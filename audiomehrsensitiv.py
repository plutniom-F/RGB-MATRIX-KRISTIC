#!/usr/bin/env python3
"""
Smoothed audiovisualiser for rpi-rgb-led-matrix with optional edge effect.

When the central shape (circle/square) is near its maximum size, the area
outside the shape will be filled with a slow pulsing edge color (configurable).
This gives a "full-screen" reaction when audio is loud.

Usage examples:
  python audiovisualiser.py
  python audiovisualiser.py --sensitivity 0.3 --shape square --edge --edge-threshold 0.8

Run as root with venv python if you need hardware pulsing:
  sudo /path/to/.venv/bin/python audiovisualiser.py
"""
from PIL import Image, ImageDraw
import time
import random
import argparse
import sys
import math

import numpy as np
import pyaudio

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except Exception:
    RGBMatrix = None
    RGBMatrixOptions = None

# ----------------------------
# CLI args
# ----------------------------
parser = argparse.ArgumentParser(description="Smoothed audiovisualiser with edge effect")
parser.add_argument("--device", type=int, default=None, help="Audio input device index (auto-select if omitted)")
parser.add_argument("--sensitivity", type=float, default=0.5, help="Lower = less sensitive (0.1..2.0). Default 0.5")
parser.add_argument("--shape", choices=("circle", "square"), default="circle", help="Shape to draw")
parser.add_argument("--buffer", type=int, default=1024, help="Audio frames per buffer")
parser.add_argument("--scale", type=float, default=0.04, help="Multiplier to map audio signal to visual size")
parser.add_argument("--smooth", type=float, default=0.7, help="Smoothing factor for visuals (0..1). Higher = smoother/laggier")
parser.add_argument("--edge", action="store_true", help="Enable edge fill effect when shape is near max")
parser.add_argument("--edge-threshold", type=float, default=0.85, help="Fraction of max size to trigger edge effect (0..1)")
parser.add_argument("--edge-speed", type=float, default=2.0, help="Speed of edge pulsing")
parser.add_argument("--edge-color", choices=("red", "blue", "white"), default="red", help="Edge pulse color")
args = parser.parse_args()

# ----------------------------
# Audio setup (auto-select input device)
# ----------------------------
p = pyaudio.PyAudio()
print("Audio devices:")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(i, dev.get('name'), "maxInputChannels=", dev.get('maxInputChannels'))

audiodevice = args.device
if audiodevice is not None:
    try:
        info = p.get_device_info_by_index(audiodevice)
        if info.get('maxInputChannels', 0) <= 0:
            print("Requested device", audiodevice, "has no input channels. Auto-selecting.")
            audiodevice = None
    except Exception:
        print("Requested device index invalid. Auto-selecting.")
        audiodevice = None

if audiodevice is None:
    audiodevice = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get('maxInputChannels', 0) > 0:
            audiodevice = i
            break
    if audiodevice is None:
        raise RuntimeError("No input-capable audio device found. Plug in a mic or fix audio drivers.")
print("Using audio device:", audiodevice, p.get_device_info_by_index(audiodevice).get('name'))

channels = 1
rate = 44100
frames_per_buffer = args.buffer

stream = p.open(format=pyaudio.paInt16,
                channels=channels,
                input=True,
                input_device_index=audiodevice,
                rate=rate,
                frames_per_buffer=frames_per_buffer)

# ----------------------------
# Matrix / PIL setup
# ----------------------------
use_matrix = False
if RGBMatrix is not None:
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'regular'
    matrix = RGBMatrix(options=options)
    use_matrix = True
else:
    print("rgbmatrix not available; running headless (no LED output).")

W, H = 64, 64
image = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(image)

# initial color for central shape
colour = (random.randrange(40, 200), random.randrange(40, 200), random.randrange(40, 200))

def colourchange(col):
    r, g, b = col
    i = random.randrange(0, 3)
    delta = random.randrange(-12, 13)
    if i == 0:
        r = min(255, max(32, r + delta))
    elif i == 1:
        g = min(255, max(32, g + delta))
    else:
        b = min(255, max(32, b + delta))
    return (r, g, b)

# ----------------------------
# Audio -> visual mapping params
# ----------------------------
sensitivity = args.sensitivity
scale = args.scale
noise_floor = 0.0
noise_decay = 0.995
noise_subtract_factor = 1.25
max_size = min(W, H) // 2 - 1
smooth_alpha = args.smooth
smoothed_cnt = 1

# Edge effect state
edge_enabled = args.edge
edge_threshold = max(0.0, min(1.0, args.edge_threshold))
edge_speed = max(0.01, args.edge_speed)
edge_color_choice = args.edge_color

def edge_color_from_choice(base_intensity, choice):
    # base_intensity: 0..255
    if choice == "red":
        return (base_intensity, int(base_intensity * 0.18), int(base_intensity * 0.18))
    if choice == "blue":
        return (int(base_intensity * 0.18), int(base_intensity * 0.18), base_intensity)
    return (base_intensity, base_intensity, base_intensity)  # white

# ----------------------------
# Main loop
# ----------------------------
try:
    while True:
        raw = stream.read(frames_per_buffer, exception_on_overflow=False)
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

        if data.size == 0:
            rms = 0.0
        else:
            rms = np.sqrt(np.mean(data * data))

        noise_floor = noise_floor * noise_decay + rms * (1.0 - noise_decay)
        signal = rms - (noise_floor * noise_subtract_factor)
        if signal < 0:
            signal = 0.0

        cnt = int(signal * sensitivity * scale * 1000.0)
        if cnt < 1:
            cnt = 1
        if cnt > max_size:
            cnt = max_size

        smoothed_cnt = int(smoothed_cnt * smooth_alpha + cnt * (1.0 - smooth_alpha))
        if smoothed_cnt < 1:
            smoothed_cnt = 1

        # slowly change main colour
        if random.random() < 0.15:
            colour = colourchange(colour)

        # Clear frame
        draw.rectangle((0, 0, W, H), fill=(0, 0, 0))

        cx, cy = W // 2, H // 2
        s = smoothed_cnt

        # Draw central shape
        if args.shape == "square":
            draw.rectangle((cx - s, cy - s, cx + s, cy + s), fill=colour)
        else:
            draw.ellipse((cx - s, cy - s, cx + s, cy + s), fill=colour)

        # Edge effect: if enabled and size is above threshold fraction of max, draw outside area
        if edge_enabled:
            threshold_size = int(edge_threshold * max_size)
            if s >= threshold_size:
                # compute how far above threshold (0..1)
                if max_size - threshold_size > 0:
                    alpha = (s - threshold_size) / (max_size - threshold_size)
                else:
                    alpha = 1.0
                alpha = max(0.0, min(1.0, alpha))

                # pulsing intensity (100..255) modulated by time and alpha
                pulse = int((math.sin(time.time() * edge_speed) + 1.0) * 0.5 * 155 + 100)
                intensity = int(pulse * alpha)
                intensity = max(0, min(255, intensity))

                ec = edge_color_from_choice(intensity, edge_color_choice)

                # draw rectangular bands outside the central bounding box
                left = max(0, cx - s)
                right = min(W, cx + s)
                top = max(0, cy - s)
                bottom = min(H, cy + s)

                # top band
                if top > 0:
                    draw.rectangle((0, 0, W, top), fill=ec)
                # bottom band
                if bottom < H:
                    draw.rectangle((0, bottom, W, H), fill=ec)
                # left band
                if left > 0:
                    draw.rectangle((0, top, left, bottom), fill=ec)
                # right band
                if right < W:
                    draw.rectangle((right, top, W, bottom), fill=ec)

        # Send to matrix (or sleep if headless)
        if use_matrix:
            try:
                matrix.SetImage(image, 0, 0)
            except TypeError:
                matrix.SetImage(image)
        else:
            # headless - you can uncomment the debug print for tuning:
            # print(f"rms:{int(rms)} noise:{int(noise_floor)} cnt:{cnt} smooth:{smoothed_cnt}")
            pass

        # small sleep to control frame rate
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    try:
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception:
        pass
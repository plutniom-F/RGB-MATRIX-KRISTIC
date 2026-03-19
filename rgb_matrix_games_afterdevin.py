# ============================================================
#  RGB MATRIX GAMES - Complete Rewrite
#  For 64x64 RGB Matrix on Raspberry Pi 4
#  Games, Clocks, Weather, Animations
#  No Spotify / No Visualizer / No Karaoke
# ============================================================

import time
import random
import sys
import tty
import termios
import threading
import math
import collections
import json
import os
import select as _select

try:
    import urllib.request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

from rgbmatrix import RGBMatrix, RGBMatrixOptions

# --- MATRIX SETUP ---
options = RGBMatrixOptions()
options.rows, options.cols = 64, 64
options.chain_length, options.parallel = 1, 1
options.hardware_mapping = 'regular'
options.gpio_slowdown = 4
options.drop_privileges = True
options.pwm_lsb_nanoseconds = 130
options.pwm_dither_bits = 1
options.show_refresh_rate = False

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# --- FONT (3x5 pixel characters) ---
CHARS = {
    '0': [1,1,1, 1,0,1, 1,0,1, 1,0,1, 1,1,1],
    '1': [0,1,0, 1,1,0, 0,1,0, 0,1,0, 1,1,1],
    '2': [1,1,1, 0,0,1, 1,1,1, 1,0,0, 1,1,1],
    '3': [1,1,1, 0,0,1, 1,1,1, 0,0,1, 1,1,1],
    '4': [1,0,1, 1,0,1, 1,1,1, 0,0,1, 0,0,1],
    '5': [1,1,1, 1,0,0, 1,1,1, 0,0,1, 1,1,1],
    '6': [1,1,1, 1,0,0, 1,1,1, 1,0,1, 1,1,1],
    '7': [1,1,1, 0,0,1, 0,1,0, 0,1,0, 0,1,0],
    '8': [1,1,1, 1,0,1, 1,1,1, 1,0,1, 1,1,1],
    '9': [1,1,1, 1,0,1, 1,1,1, 0,0,1, 1,1,1],
    'A': [1,1,1, 1,0,1, 1,1,1, 1,0,1, 1,0,1],
    'B': [1,1,0, 1,0,1, 1,1,0, 1,0,1, 1,1,0],
    'C': [1,1,1, 1,0,0, 1,0,0, 1,0,0, 1,1,1],
    'D': [1,1,0, 1,0,1, 1,0,1, 1,0,1, 1,1,0],
    'E': [1,1,1, 1,0,0, 1,1,1, 1,0,0, 1,1,1],
    'F': [1,1,1, 1,0,0, 1,1,0, 1,0,0, 1,0,0],
    'G': [1,1,1, 1,0,0, 1,0,1, 1,0,1, 1,1,1],
    'H': [1,0,1, 1,0,1, 1,1,1, 1,0,1, 1,0,1],
    'I': [1,1,1, 0,1,0, 0,1,0, 0,1,0, 1,1,1],
    'J': [0,0,1, 0,0,1, 0,0,1, 1,0,1, 1,1,1],
    'K': [1,0,1, 1,1,0, 1,0,0, 1,1,0, 1,0,1],
    'L': [1,0,0, 1,0,0, 1,0,0, 1,0,0, 1,1,1],
    'M': [1,0,1, 1,1,1, 1,0,1, 1,0,1, 1,0,1],
    'N': [1,1,1, 1,0,1, 1,0,1, 1,0,1, 1,0,1],
    'O': [1,1,1, 1,0,1, 1,0,1, 1,0,1, 1,1,1],
    'P': [1,1,1, 1,0,1, 1,1,1, 1,0,0, 1,0,0],
    'Q': [1,1,1, 1,0,1, 1,0,1, 1,1,1, 0,0,1],
    'R': [1,1,1, 1,0,1, 1,1,0, 1,0,1, 1,0,1],
    'S': [1,1,1, 1,0,0, 1,1,1, 0,0,1, 1,1,1],
    'T': [1,1,1, 0,1,0, 0,1,0, 0,1,0, 0,1,0],
    'U': [1,0,1, 1,0,1, 1,0,1, 1,0,1, 1,1,1],
    'V': [1,0,1, 1,0,1, 1,0,1, 0,1,0, 0,1,0],
    'W': [1,0,1, 1,0,1, 1,0,1, 1,1,1, 1,0,1],
    'X': [1,0,1, 1,0,1, 0,1,0, 1,0,1, 1,0,1],
    'Y': [1,0,1, 1,0,1, 0,1,0, 0,1,0, 0,1,0],
    'Z': [1,1,1, 0,0,1, 0,1,0, 1,0,0, 1,1,1],
    ' ': [0,0,0, 0,0,0, 0,0,0, 0,0,0, 0,0,0],
    '!': [0,1,0, 0,1,0, 0,1,0, 0,0,0, 0,1,0],
    ':': [0,0,0, 0,1,0, 0,0,0, 0,1,0, 0,0,0],
    '-': [0,0,0, 0,0,0, 1,1,1, 0,0,0, 0,0,0],
    '>': [1,0,0, 0,1,0, 0,0,1, 0,1,0, 1,0,0],
    '.': [0,0,0, 0,0,0, 0,0,0, 0,0,0, 0,1,0],
    '/': [0,0,1, 0,0,1, 0,1,0, 1,0,0, 1,0,0],
    '%': [1,0,1, 0,0,1, 0,1,0, 1,0,0, 1,0,1],
    '<': [0,0,1, 0,1,0, 1,0,0, 0,1,0, 0,0,1],
    '+': [0,0,0, 0,1,0, 1,1,1, 0,1,0, 0,0,0],
    '~': [0,0,0, 0,0,0, 1,0,1, 0,1,0, 0,0,0],
}

BIG_DIGITS = {
    '0': [0,1,1,1,0, 1,0,0,0,1, 1,0,0,1,1, 1,0,1,0,1, 1,1,0,0,1, 1,0,0,0,1, 0,1,1,1,0],
    '1': [0,0,1,0,0, 0,1,1,0,0, 0,0,1,0,0, 0,0,1,0,0, 0,0,1,0,0, 0,0,1,0,0, 0,1,1,1,0],
    '2': [0,1,1,1,0, 1,0,0,0,1, 0,0,0,0,1, 0,0,0,1,0, 0,0,1,0,0, 0,1,0,0,0, 1,1,1,1,1],
    '3': [0,1,1,1,0, 1,0,0,0,1, 0,0,0,0,1, 0,0,1,1,0, 0,0,0,0,1, 1,0,0,0,1, 0,1,1,1,0],
    '4': [0,0,0,1,0, 0,0,1,1,0, 0,1,0,1,0, 1,0,0,1,0, 1,1,1,1,1, 0,0,0,1,0, 0,0,0,1,0],
    '5': [1,1,1,1,1, 1,0,0,0,0, 1,1,1,1,0, 0,0,0,0,1, 0,0,0,0,1, 1,0,0,0,1, 0,1,1,1,0],
    '6': [0,1,1,1,0, 1,0,0,0,0, 1,0,0,0,0, 1,1,1,1,0, 1,0,0,0,1, 1,0,0,0,1, 0,1,1,1,0],
    '7': [1,1,1,1,1, 0,0,0,0,1, 0,0,0,1,0, 0,0,1,0,0, 0,0,1,0,0, 0,0,1,0,0, 0,0,1,0,0],
    '8': [0,1,1,1,0, 1,0,0,0,1, 1,0,0,0,1, 0,1,1,1,0, 1,0,0,0,1, 1,0,0,0,1, 0,1,1,1,0],
    '9': [0,1,1,1,0, 1,0,0,0,1, 1,0,0,0,1, 0,1,1,1,1, 0,0,0,0,1, 0,0,0,0,1, 0,1,1,1,0],
}


# ============================================================
#                    DRAWING HELPERS
# ============================================================

def draw_pixel(canvas, x, y, r, g, b):
    if 0 <= x < 64 and 0 <= y < 64:
        canvas.SetPixel(x, y, r, g, b)

def draw_text(canvas, text, x_start, y_start, r, g, b):
    x = x_start
    for ch in str(text).upper():
        glyph = CHARS.get(ch)
        if glyph:
            for row in range(5):
                for col in range(3):
                    if glyph[row * 3 + col]:
                        draw_pixel(canvas, x + col, y_start + row, r, g, b)
        x += 4

def text_width(text):
    return max(0, len(str(text)) * 4 - 1)

def draw_text_centered(canvas, text, y, r, g, b):
    w = text_width(text)
    draw_text(canvas, text, (64 - w) // 2, y, r, g, b)

def draw_block(canvas, x, y, w, h, r, g, b):
    for dx in range(w):
        for dy in range(h):
            draw_pixel(canvas, x + dx, y + dy, r, g, b)

def hsv_to_rgb(h, s, v):
    if s == 0:
        r = g = b = int(v * 255)
        return r, g, b
    h = h % 1.0
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

def draw_rect(canvas, x, y, w, h, r, g, b):
    for dx in range(w):
        for dy in range(h):
            draw_pixel(canvas, x + dx, y + dy, r, g, b)

def draw_rect_outline(canvas, x, y, w, h, r, g, b):
    for dx in range(w):
        draw_pixel(canvas, x + dx, y, r, g, b)
        draw_pixel(canvas, x + dx, y + h - 1, r, g, b)
    for dy in range(h):
        draw_pixel(canvas, x, y + dy, r, g, b)
        draw_pixel(canvas, x + w - 1, y + dy, r, g, b)

def draw_line(canvas, x0, y0, x1, y1, r, g, b):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        draw_pixel(canvas, x0, y0, r, g, b)
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 > -dy: err -= dy; x0 += sx
        if e2 < dx: err += dx; y0 += sy

def draw_circle(canvas, cx, cy, radius, r, g, b):
    x, y, d = radius, 0, 1 - radius
    while x >= y:
        for px, py in [(cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                        (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)]:
            draw_pixel(canvas, px, py, r, g, b)
        y += 1
        if d < 0: d += 2 * y + 1
        else: x -= 1; d += 2 * (y - x) + 1

def draw_filled_circle(canvas, cx, cy, radius, r, g, b):
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                draw_pixel(canvas, cx + dx, cy + dy, r, g, b)

def draw_big_digit(canvas, ch, x, y, r, g, b):
    glyph = BIG_DIGITS.get(ch)
    if not glyph: return
    for row in range(7):
        for col in range(5):
            if glyph[row * 5 + col]:
                draw_pixel(canvas, x + col, y + row, r, g, b)

def draw_big_time(canvas, time_str, x, y, r, g, b):
    cx = x
    for ch in time_str:
        if ch == ':':
            draw_pixel(canvas, cx + 1, y + 2, r, g, b)
            draw_pixel(canvas, cx + 1, y + 4, r, g, b)
            cx += 4
        elif ch == ' ':
            cx += 3
        else:
            draw_big_digit(canvas, ch, cx, y, r, g, b)
            cx += 6

def big_time_width(time_str):
    w = 0
    for ch in time_str:
        if ch == ':': w += 4
        elif ch == ' ': w += 3
        else: w += 6
    return max(0, w - 1)


# ============================================================
#                    INPUT HANDLING
# ============================================================

running = True
_key_queue = collections.deque(maxlen=16)
_input_lock = threading.Lock()

def get_input():
    global running
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while running:
            if _select.select([sys.stdin], [], [], 0.05)[0]:
                ch = sys.stdin.read(1)
                if ch == '\x03':
                    running = False
                    return
                if ch == '\x1b':
                    if _select.select([sys.stdin], [], [], 0.02)[0]:
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[':
                            ch3 = sys.stdin.read(1)
                            if ch3 == 'A':
                                with _input_lock: _key_queue.append('w')
                            elif ch3 == 'B':
                                with _input_lock: _key_queue.append('s')
                            elif ch3 == 'C':
                                with _input_lock: _key_queue.append('d')
                            elif ch3 == 'D':
                                with _input_lock: _key_queue.append('a')
                            continue
                    with _input_lock: _key_queue.append('\x1b')
                else:
                    with _input_lock: _key_queue.append(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

_input_thread = threading.Thread(target=get_input, daemon=True)
_input_thread.start()

def consume_key():
    with _input_lock:
        return _key_queue.popleft() if _key_queue else None

def consume_queue():
    with _input_lock:
        return list(_key_queue)

def peek_key():
    with _input_lock:
        return _key_queue[0] if _key_queue else None

def clear_input():
    with _input_lock:
        _key_queue.clear()


# ============================================================
#                    PARTICLE SYSTEM
# ============================================================

class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'r', 'g', 'b', 'life', 'max_life']

    def __init__(self, x, y, vx, vy, r, g, b, life):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.r, self.g, self.b = r, g, b
        self.life = life
        self.max_life = life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, canvas):
        if self.life > 0:
            f = max(0.0, self.life / self.max_life)
            draw_pixel(canvas, int(self.x), int(self.y),
                       int(self.r * f), int(self.g * f), int(self.b * f))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, r, g, b, spread=20, life=0.5):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, spread)
            self.particles.append(
                Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                         r, g, b, life * random.uniform(0.5, 1.0)))

    def emit_burst(self, x, y, count, spread=20, life=0.5):
        for i in range(count):
            h = i / count if count > 0 else 0
            r, g, b = hsv_to_rgb(h, 1.0, 1.0)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, spread)
            self.particles.append(
                Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                         r, g, b, life * random.uniform(0.5, 1.0)))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update(dt)

    def draw(self, canvas):
        for p in self.particles: p.draw(canvas)


class Starfield:
    def __init__(self, count=40):
        self.stars = []
        for _ in range(count):
            self.stars.append((random.randint(0, 63), random.randint(0, 63),
                               random.uniform(0.3, 1.0), random.uniform(1.0, 4.0)))

    def draw(self, canvas, t):
        for sx, sy, bright, freq in self.stars:
            v = int(bright * (0.3 + 0.7 * abs(math.sin(t * freq))) * 80)
            draw_pixel(canvas, sx, sy, v, v, v)


# ============================================================
#                    TIME / WEATHER
# ============================================================

def get_austria_time():
    utc = time.time()
    lt = time.localtime(utc)
    year = lt.tm_year
    march_last_sun = 31 - (int(5 * year / 4 + 4) % 7)
    oct_last_sun = 31 - (int(5 * year / 4 + 1) % 7)
    dst_start = time.mktime(time.strptime(
        f"{year}-03-{march_last_sun:02d} 01:00:00", "%Y-%m-%d %H:%M:%S"))
    dst_end = time.mktime(time.strptime(
        f"{year}-10-{oct_last_sun:02d} 01:00:00", "%Y-%m-%d %H:%M:%S"))
    offset = 2 if dst_start <= utc < dst_end else 1
    return time.gmtime(utc + offset * 3600)

class WeatherData:
    def __init__(self):
        self.temperature = None
        self.weathercode = 0
        self.last_fetch = 0
        self.fetch_interval = 600

    def get_description(self):
        wc = self.weathercode
        if wc == 0: return "KLAR"
        elif wc in (1, 2, 3): return "WOLKIG"
        elif wc in (45, 48): return "NEBEL"
        elif wc in (51, 53, 55): return "NIESEL"
        elif wc in (61, 63, 65): return "REGEN"
        elif wc in (71, 73, 75, 77): return "SCHNEE"
        elif wc in (80, 81, 82): return "SCHAUER"
        elif wc in (95, 96, 99): return "GEWITTER"
        else: return f"WC{wc}"

    def should_fetch(self):
        return time.time() - self.last_fetch > self.fetch_interval

    def fetch(self):
        if not HAS_URLLIB: return
        self.last_fetch = time.time()
        def _do():
            try:
                url = ("https://api.open-meteo.com/v1/forecast?"
                       "latitude=48.2333&longitude=16.4667"
                       "&current_weather=true&timezone=Europe/Vienna")
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'RGBMatrixGames/1.0'})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode())
                    cw = data.get("current_weather", {})
                    self.temperature = cw.get("temperature")
                    self.weathercode = cw.get("weathercode", 0)
            except Exception:
                pass
        threading.Thread(target=_do, daemon=True).start()

weather_data = WeatherData()


# ============================================================
#                    ANIMATIONS
# ============================================================

def animation_flash(duration, r, g, b):
    start = time.time()
    while time.time() - start < duration:
        t = (time.time() - start) / duration
        fade = 1.0 - t
        canvas.Clear()
        for x in range(0, 64, 2):
            for y in range(0, 64, 2):
                draw_pixel(canvas, x, y, int(r*fade), int(g*fade), int(b*fade))
        matrix.SwapOnVSync(canvas)
        time.sleep(0.02)

def animation_game_over(score, color=(255, 0, 0)):
    particles = ParticleSystem()
    particles.emit_burst(32, 25, 20, spread=30, life=1.2)
    start = time.time()
    clear_input()
    while running:
        now = time.time()
        t = now - start
        canvas.Clear()
        particles.update(0.03)
        particles.draw(canvas)
        pulse = 0.5 + 0.5 * math.sin(t * 4)
        r2 = int(color[0] * pulse)
        g2 = int(color[1] * pulse)
        b2 = int(color[2] * pulse)
        draw_text_centered(canvas, "GAME", 15, r2, g2, b2)
        draw_text_centered(canvas, "OVER", 22, r2, g2, b2)
        # rainbow line
        for x in range(10, 54):
            h = (t * 0.3 + x * 0.02) % 1.0
            rr, gg, bb = hsv_to_rgb(h, 1.0, 0.3)
            draw_pixel(canvas, x, 30, rr, gg, bb)
        draw_text_centered(canvas, f"SCORE {score}", 34, 255, 255, 255)
        if t > 1.5 and int(t * 2) % 2:
            draw_text_centered(canvas, "TASTE", 50, 80, 80, 80)
        matrix.SwapOnVSync(canvas)
        if t > 1.0 and consume_key() is not None:
            return
        time.sleep(0.03)

def animation_win(score=0, msg="GEWONNEN!"):
    particles = ParticleSystem()
    particles.emit_burst(32, 30, 25, spread=35, life=1.5)
    start = time.time()
    clear_input()
    while running:
        now = time.time()
        t = now - start
        canvas.Clear()
        particles.update(0.03)
        particles.draw(canvas)
        for x in range(64):
            h = (t * 0.5 + x * 0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 0.4)
            draw_pixel(canvas, x, 18, r, g, b)
            draw_pixel(canvas, x, 35, r, g, b)
        pulse = 0.6 + 0.4 * math.sin(t * 5)
        draw_text_centered(canvas, msg, 24, int(255*pulse), int(255*pulse), 0)
        if score > 0:
            draw_text_centered(canvas, f"SCORE {score}", 40, 200, 200, 200)
        if t > 1.5 and int(t * 2) % 2:
            draw_text_centered(canvas, "TASTE", 52, 80, 80, 80)
        matrix.SwapOnVSync(canvas)
        if t > 1.0 and consume_key() is not None:
            return
        time.sleep(0.03)

def animation_countdown():
    for num in [3, 2, 1]:
        start = time.time()
        while time.time() - start < 0.6:
            t = time.time() - start
            canvas.Clear()
            scale = min(1.0, t * 3)
            fade = 1.0 if t < 0.4 else max(0.0, 1.0 - (t - 0.4) / 0.2)
            h = (num - 1) / 3.0
            r, g, b = hsv_to_rgb(h, 1.0, fade)
            draw_text_centered(canvas, str(num), int(28 - 4 * scale), r, g, b)
            matrix.SwapOnVSync(canvas)
            time.sleep(0.02)
    # GO!
    start = time.time()
    while time.time() - start < 0.5:
        t = time.time() - start
        canvas.Clear()
        pulse = 0.5 + 0.5 * math.sin(t * 15)
        v = int(255 * pulse)
        draw_text_centered(canvas, "GO!", 26, 0, v, 0)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.02)

def animation_transition():
    for step in range(8):
        canvas.Clear()
        for y in range(64):
            progress = step / 7.0
            if y / 64.0 < progress:
                h = (y * 0.015 + step * 0.1) % 1.0
                r, g, b = hsv_to_rgb(h, 0.8, 0.15)
                for x in range(0, 64, 3):
                    draw_pixel(canvas, x, y, r, g, b)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.025)


# ============================================================
#                    SNAKE
# ============================================================

def play_snake(mode=1):
    W, H = 62, 58
    OX, OY = 1, 6
    snake = collections.deque()
    snake.append((W // 2, H // 2))
    direction = (1, 0)
    grow = 3
    score = 0
    particles = ParticleSystem()

    ultimate = (mode == 2)
    speed = 0.08 if not ultimate else 0.05
    walls = ultimate

    def spawn():
        while True:
            fx = random.randint(0, W - 1)
            fy = random.randint(0, H - 1)
            if (fx, fy) not in snake:
                return fx, fy

    food = spawn()
    bonus = None
    bonus_timer = 0

    clear_input()
    animation_countdown()
    clear_input()
    last_move = time.time()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return

        dx, dy = direction
        if k == 'w' and dy != 1: direction = (0, -1)
        elif k == 's' and dy != -1: direction = (0, 1)
        elif k == 'a' and dx != 1: direction = (-1, 0)
        elif k == 'd' and dx != -1: direction = (1, 0)

        if now - last_move >= speed:
            last_move = now
            hx, hy = snake[-1]
            nx = hx + direction[0]
            ny = hy + direction[1]

            if walls:
                if nx < 0 or nx >= W or ny < 0 or ny >= H:
                    particles.emit(hx + OX, hy + OY, 20, 255, 0, 0,
                                   spread=25, life=0.8)
                    animation_flash(0.2, 255, 0, 0)
                    animation_game_over(score, (0, 255, 0))
                    return
            else:
                nx = nx % W
                ny = ny % H

            if (nx, ny) in snake:
                particles.emit(nx + OX, ny + OY, 20, 255, 0, 0,
                               spread=25, life=0.8)
                animation_flash(0.2, 255, 0, 0)
                animation_game_over(score, (0, 255, 0))
                return

            snake.append((nx, ny))

            if (nx, ny) == food:
                score += 10
                grow += 2
                particles.emit(food[0] + OX, food[1] + OY, 8,
                               255, 50, 50, spread=15, life=0.4)
                food = spawn()
                speed = max(0.03, speed - 0.001)
                if not bonus and score > 0 and score % 50 == 0:
                    bonus = spawn()
                    bonus_timer = now
            elif bonus and (nx, ny) == bonus:
                score += 30
                particles.emit_burst(bonus[0] + OX, bonus[1] + OY,
                                     10, spread=20, life=0.6)
                bonus = None
            else:
                if grow > 0:
                    grow -= 1
                else:
                    snake.popleft()

            if bonus and now - bonus_timer > 8:
                bonus = None

        # Render
        canvas.Clear()

        # Border
        for x in range(64):
            h = (now * 0.2 + x * 0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.5, 0.15)
            draw_pixel(canvas, x, 5, r, g, b)

        # Snake body
        slist = list(snake)
        for i, (sx, sy) in enumerate(slist):
            f = (i + 1) / len(slist)
            h = (now * 0.3 + i * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 0.8, 0.3 + 0.7 * f)
            draw_pixel(canvas, sx + OX, sy + OY, r, g, b)

        # Head highlight
        hx, hy = slist[-1]
        draw_pixel(canvas, hx + OX, hy + OY, 200, 255, 200)

        # Food
        fpulse = 0.5 + 0.5 * math.sin(now * 8)
        draw_pixel(canvas, food[0] + OX, food[1] + OY,
                   int(255 * fpulse), int(50 * fpulse), int(50 * fpulse))

        # Bonus
        if bonus:
            remaining = max(0, 8 - (now - bonus_timer))
            blink = remaining < 2 and int(now * 6) % 2
            if not blink:
                bp = 0.5 + 0.5 * math.sin(now * 10)
                draw_pixel(canvas, bonus[0] + OX, bonus[1] + OY,
                           int(255 * bp), int(255 * bp), 0)

        particles.update(0.03)
        particles.draw(canvas)

        # Score
        draw_text(canvas, str(score), 2, 0, 255, 255, 0)
        mode_str = "ULT" if ultimate else "NRM"
        draw_text(canvas, mode_str, 46, 0, 80, 80, 80)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#                    TETRIS
# ============================================================

def play_tetris():
    BOARD_W, BOARD_H = 10, 20
    CELL = 3
    BX, BY = 2, 4
    SHAPES = [
        [(0,0),(1,0),(2,0),(3,0)],
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(2,0),(1,1)],
        [(0,0),(1,0),(2,0),(2,1)],
        [(0,0),(1,0),(2,0),(0,1)],
        [(0,0),(1,0),(1,1),(2,1)],
        [(1,0),(2,0),(0,1),(1,1)],
    ]
    COLORS = [
        (0,255,255),(255,255,0),(128,0,255),
        (255,128,0),(0,0,255),(0,255,0),(255,0,0),
    ]
    board = [[None]*BOARD_W for _ in range(BOARD_H)]
    score = 0
    level = 1
    lines_cleared = 0

    def nxt():
        si = random.randint(0, len(SHAPES)-1)
        return list(SHAPES[si]), COLORS[si], si

    def blks(shape, ox, oy):
        result = []
        for dx, dy in shape:
            result.append((ox+dx, oy+dy))
        return result

    cur_shape, cur_color, cur_si = nxt()
    next_shape, next_color, next_si = nxt()
    cx, cy = BOARD_W//2 - 1, 0
    fall_timer = 0
    fall_speed = 0.5
    particles = ParticleSystem()

    def hit(shape, ox, oy):
        for dx, dy in shape:
            nx2, ny2 = ox+dx, oy+dy
            if nx2 < 0 or nx2 >= BOARD_W or ny2 >= BOARD_H:
                return True
            if ny2 >= 0 and board[ny2][nx2] is not None:
                return True
        return False

    def ghy(shape, ox, oy):
        ty = oy
        while not hit(shape, ox, ty+1):
            ty += 1
        return ty

    def lck(shape, ox, oy, color):
        for dx, dy in shape:
            bx2, by2 = ox+dx, oy+dy
            if 0 <= by2 < BOARD_H and 0 <= bx2 < BOARD_W:
                board[by2][bx2] = color

    def frows():
        return [r for r in range(BOARD_H) if all(c is not None for c in board[r])]

    def rrows(rows):
        nonlocal score, lines_cleared, level, fall_speed
        for r in sorted(rows):
            for px in range(BOARD_W):
                particles.emit(BX + px*CELL + 1, BY + r*CELL + 1,
                               2, *board[r][px], spread=10, life=0.4)
            del board[r]
            board.insert(0, [None]*BOARD_W)
        n = len(rows)
        score += [0, 100, 300, 500, 800][min(n, 4)] * level
        lines_cleared += n
        level = 1 + lines_cleared // 10
        fall_speed = max(0.05, 0.5 - (level-1)*0.04)

    def dcell(x, y, color, ghost=False):
        sx = BX + x * CELL
        sy = BY + y * CELL
        if ghost:
            draw_rect_outline(canvas, sx, sy, CELL, CELL,
                              color[0]//4, color[1]//4, color[2]//4)
        else:
            draw_rect(canvas, sx, sy, CELL, CELL,
                      color[0], color[1], color[2])
            draw_pixel(canvas, sx, sy,
                       min(255, int(color[0]*1.3)),
                       min(255, int(color[1]*1.3)),
                       min(255, int(color[2]*1.3)))

    def dborder():
        bx1, by1 = BX - 1, BY - 1
        bx2 = BX + BOARD_W * CELL
        by2 = BY + BOARD_H * CELL
        now = time.time()
        for y in range(by1, by2 + 1):
            h = (now * 0.2 + y * 0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.5, 0.2)
            draw_pixel(canvas, bx1, y, r, g, b)
            draw_pixel(canvas, bx2, y, r, g, b)
        for x in range(bx1, bx2 + 1):
            h = (now * 0.2 + x * 0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.5, 0.2)
            draw_pixel(canvas, x, by2, r, g, b)

    def dsidebar():
        sx = BX + BOARD_W * CELL + 3
        draw_text(canvas, "NEXT", sx, 5, 100, 100, 100)
        for dx, dy in next_shape:
            px = sx + dx * 3
            py = 12 + dy * 3
            draw_rect(canvas, px, py, 2, 2,
                      next_color[0]//2, next_color[1]//2, next_color[2]//2)
        draw_text(canvas, str(score), sx, 26, 255, 255, 0)
        draw_text(canvas, f"L{level}", sx, 34, 100, 200, 100)
        draw_text(canvas, f"{lines_cleared}L", sx, 42, 150, 150, 150)

    clear_input()
    animation_countdown()
    clear_input()
    last_time = time.time()

    while running:
        now = time.time()
        dt = now - last_time
        last_time = now
        fall_timer += dt

        k = consume_key()
        if k == '\x1b': return

        if k == 'a':
            if not hit(cur_shape, cx-1, cy): cx -= 1
        elif k == 'd':
            if not hit(cur_shape, cx+1, cy): cx += 1
        elif k == 's':
            if not hit(cur_shape, cx, cy+1): cy += 1
            fall_timer = 0
        elif k == 'w':
            rotated = [(-dy, dx) for dx, dy in cur_shape]
            min_x = min(dx for dx, dy in rotated)
            min_y = min(dy for dx, dy in rotated)
            rotated = [(dx-min_x, dy-min_y) for dx, dy in rotated]
            if not hit(rotated, cx, cy):
                cur_shape = rotated
            elif not hit(rotated, cx-1, cy):
                cur_shape = rotated; cx -= 1
            elif not hit(rotated, cx+1, cy):
                cur_shape = rotated; cx += 1
        elif k == ' ':
            cy = ghy(cur_shape, cx, cy)
            fall_timer = fall_speed

        if fall_timer >= fall_speed:
            fall_timer = 0
            if not hit(cur_shape, cx, cy+1):
                cy += 1
            else:
                lck(cur_shape, cx, cy, cur_color)
                full = frows()
                if full:
                    rrows(full)
                    animation_flash(0.08, 255, 255, 255)
                cur_shape, cur_color, cur_si = next_shape, next_color, next_si
                next_shape, next_color, next_si = nxt()
                cx, cy = BOARD_W//2 - 1, 0
                if hit(cur_shape, cx, cy):
                    animation_flash(0.2, 255, 0, 0)
                    animation_game_over(score, (0, 150, 255))
                    return

        # Render
        canvas.Clear()
        dborder()

        for y in range(BOARD_H):
            for x in range(BOARD_W):
                if board[y][x] is not None:
                    dcell(x, y, board[y][x])

        ghost_y = ghy(cur_shape, cx, cy)
        for dx, dy in cur_shape:
            dcell(cx+dx, ghost_y+dy, cur_color, ghost=True)

        for dx, dy in cur_shape:
            dcell(cx+dx, cy+dy, cur_color)

        dsidebar()
        particles.update(dt)
        particles.draw(canvas)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#                    PONG
# ============================================================

def play_pong(difficulty=2):
    if difficulty == 1:
        AI_SPEED = 0.6; BALL_SPEED = 0.8; PADDLE_W = 12
    elif difficulty == 3:
        AI_SPEED = 1.2; BALL_SPEED = 1.2; PADDLE_W = 8
    else:
        AI_SPEED = 0.9; BALL_SPEED = 1.0; PADDLE_W = 10

    PADDLE_H = 2
    player_x = 32.0 - PADDLE_W / 2
    ai_x = 32.0 - PADDLE_W / 2
    PLAYER_Y = 59
    AI_Y = 4
    ball_x, ball_y = 32.0, 32.0
    ball_vx = random.choice([-1, 1]) * BALL_SPEED
    ball_vy = BALL_SPEED
    player_score = 0
    ai_score = 0
    MAX_SCORE = 7
    particles = ParticleSystem()
    ball_trail = collections.deque(maxlen=8)
    serving = True

    clear_input()
    animation_countdown()
    clear_input()

    while running:
        now = time.time()
        dt = 0.016

        k = consume_key()
        if k == '\x1b': return

        # Player movement
        if k == 'a': player_x = max(0, player_x - 3)
        elif k == 'd': player_x = min(64 - PADDLE_W, player_x + 3)

        # AI movement
        ai_target = ball_x - PADDLE_W / 2
        ai_diff = ai_target - ai_x
        ai_move = min(abs(ai_diff), AI_SPEED * 2) * (1 if ai_diff > 0 else -1)
        ai_x = max(0, min(64 - PADDLE_W, ai_x + ai_move))

        if serving:
            ball_x = player_x + PADDLE_W / 2
            ball_y = PLAYER_Y - 2
            if k in ('w', ' '):
                serving = False
                ball_vy = -BALL_SPEED
                ball_vx = random.uniform(-0.5, 0.5)
            canvas.Clear()
            # Draw paddles
            for dx in range(PADDLE_W):
                fade = 1.0 - abs(dx - PADDLE_W/2)/(PADDLE_W/2)*0.3
                draw_pixel(canvas, int(player_x)+dx, PLAYER_Y, 0, int(200*fade), int(255*fade))
                draw_pixel(canvas, int(player_x)+dx, PLAYER_Y+1, 0, int(150*fade), int(200*fade))
            for dx in range(PADDLE_W):
                fade = 1.0 - abs(dx - PADDLE_W/2)/(PADDLE_W/2)*0.3
                draw_pixel(canvas, int(ai_x)+dx, AI_Y, int(255*fade), int(50*fade), int(50*fade))
                draw_pixel(canvas, int(ai_x)+dx, AI_Y+1, int(200*fade), int(30*fade), int(30*fade))
            draw_pixel(canvas, int(ball_x), int(ball_y), 255, 255, 255)
            if int(now*3) % 2:
                draw_text_centered(canvas, "W START", 30, 80, 80, 80)
            draw_text(canvas, str(player_score), 2, 30, 0, 200, 255)
            draw_text(canvas, str(ai_score), 56, 30, 255, 50, 50)
            particles.draw(canvas)
            matrix.SwapOnVSync(canvas)
            time.sleep(0.03)
            continue

        # Ball physics
        ball_x += ball_vx * dt * 50
        ball_y += ball_vy * dt * 50

        if ball_x <= 0: ball_x = 0; ball_vx = abs(ball_vx)
        elif ball_x >= 63: ball_x = 63; ball_vx = -abs(ball_vx)

        # Player paddle collision
        if ball_vy > 0 and PLAYER_Y - 1 <= ball_y <= PLAYER_Y + PADDLE_H:
            if player_x - 1 <= ball_x <= player_x + PADDLE_W + 1:
                hit_pos = (ball_x - player_x) / PADDLE_W
                ang = (hit_pos - 0.5) * 2.0
                spd = math.sqrt(ball_vx**2 + ball_vy**2)
                ball_vx = spd * math.sin(ang)
                ball_vy = -abs(spd * math.cos(ang))
                ball_y = PLAYER_Y - 2
                particles.emit(int(ball_x), PLAYER_Y, 4, 0, 200, 255, spread=10, life=0.3)

        # AI paddle collision
        if ball_vy < 0 and AI_Y <= ball_y <= AI_Y + PADDLE_H + 1:
            if ai_x - 1 <= ball_x <= ai_x + PADDLE_W + 1:
                hit_pos = (ball_x - ai_x) / PADDLE_W
                ang = (hit_pos - 0.5) * 2.0
                spd = math.sqrt(ball_vx**2 + ball_vy**2)
                ball_vx = spd * math.sin(ang)
                ball_vy = abs(spd * math.cos(ang))
                ball_y = AI_Y + PADDLE_H + 1
                particles.emit(int(ball_x), AI_Y + PADDLE_H, 4, 255, 50, 50, spread=10, life=0.3)

        # Scoring
        if ball_y >= 63:
            ai_score += 1
            particles.emit(int(ball_x), 63, 10, 255, 0, 0, spread=20, life=0.6)
            if ai_score >= MAX_SCORE:
                animation_flash(0.2, 255, 0, 0)
                animation_game_over(player_score, (0, 200, 255))
                return
            serving = True
            ball_trail.clear()
            continue
        if ball_y <= 0:
            player_score += 1
            particles.emit(int(ball_x), 0, 10, 0, 255, 0, spread=20, life=0.6)
            if player_score >= MAX_SCORE:
                animation_win(player_score, "GEWONNEN!")
                return
            serving = True
            ball_trail.clear()
            continue

        ball_trail.append((ball_x, ball_y))

        # Render
        canvas.Clear()

        # Center line
        for x in range(0, 64, 4):
            draw_pixel(canvas, x, 32, 20, 20, 20)

        # Trail
        for i, (tx, ty) in enumerate(ball_trail):
            f = (i + 1) / max(len(ball_trail), 1)
            v = int(60 * f)
            draw_pixel(canvas, int(tx), int(ty), v, v, v)

        # Ball glow + ball
        bxi, byi = int(ball_x), int(ball_y)
        for ddx in range(-1, 2):
            for ddy in range(-1, 2):
                if ddx == 0 and ddy == 0: continue
                draw_pixel(canvas, bxi+ddx, byi+ddy, 40, 40, 40)
        draw_pixel(canvas, bxi, byi, 255, 255, 255)

        # Paddles
        for dx in range(PADDLE_W):
            fade = 1.0 - abs(dx - PADDLE_W/2)/(PADDLE_W/2)*0.3
            draw_pixel(canvas, int(player_x)+dx, PLAYER_Y, 0, int(200*fade), int(255*fade))
            draw_pixel(canvas, int(player_x)+dx, PLAYER_Y+1, 0, int(150*fade), int(200*fade))
        for dx in range(PADDLE_W):
            fade = 1.0 - abs(dx - PADDLE_W/2)/(PADDLE_W/2)*0.3
            draw_pixel(canvas, int(ai_x)+dx, AI_Y, int(255*fade), int(50*fade), int(50*fade))
            draw_pixel(canvas, int(ai_x)+dx, AI_Y+1, int(200*fade), int(30*fade), int(30*fade))

        particles.update(dt)
        particles.draw(canvas)
        draw_text(canvas, str(player_score), 2, 30, 0, 200, 255)
        draw_text(canvas, str(ai_score), 56, 30, 255, 50, 50)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#                    DVD BOUNCE
# ============================================================

def play_dvd_bounce():
    logos = ["DVD", "MATRIX", "RGB", "PI4", "64X64", "COOL"]
    logo_idx = 0
    x, y = 20.0, 20.0
    vx, vy = 0.8, 0.6
    hue = 0.0
    trail = collections.deque(maxlen=20)
    corner_hits = 0
    particles = ParticleSystem()

    clear_input()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return
        if k == 'd':
            logo_idx = (logo_idx + 1) % len(logos)
        if k == 'w': vx *= 1.2; vy *= 1.2
        if k == 's': vx *= 0.8; vy *= 0.8

        text = logos[logo_idx]
        tw = text_width(text)
        th = 5

        x += vx
        y += vy

        bounced = False
        if x <= 0: x = 0; vx = abs(vx); bounced = True
        elif x + tw >= 63: x = 63 - tw; vx = -abs(vx); bounced = True
        if y <= 0: y = 0; vy = abs(vy); bounced = True
        elif y + th >= 63: y = 63 - th; vy = -abs(vy); bounced = True

        if bounced:
            hue = (hue + 0.15) % 1.0
            particles.emit(int(x + tw/2), int(y + th/2), 5,
                           *hsv_to_rgb(hue, 1.0, 1.0), spread=15, life=0.5)
            # corner detection
            at_left = x <= 1
            at_right = x + tw >= 62
            at_top = y <= 1
            at_bottom = y + th >= 62
            if (at_left or at_right) and (at_top or at_bottom):
                corner_hits += 1
                particles.emit_burst(int(x + tw/2), int(y + th/2),
                                     20, spread=30, life=1.0)

        trail.append((int(x), int(y), hue))

        canvas.Clear()

        # Trail
        for i, (tx, ty, th2) in enumerate(trail):
            f = (i + 1) / len(trail) * 0.3
            r, g, b = hsv_to_rgb(th2, 0.6, f)
            draw_text(canvas, text, tx, ty, r, g, b)

        # Main logo
        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        draw_text(canvas, text, int(x), int(y), r, g, b)

        particles.update(0.03)
        particles.draw(canvas)

        if corner_hits > 0:
            draw_text(canvas, f"C{corner_hits}", 2, 1, 80, 80, 0)

        # Border shimmer
        for bx in range(64):
            bh = (now * 0.3 + bx * 0.03) % 1.0
            br, bg, bb = hsv_to_rgb(bh, 0.5, 0.08)
            draw_pixel(canvas, bx, 0, br, bg, bb)
            draw_pixel(canvas, bx, 63, br, bg, bb)
        for by in range(64):
            bh = (now * 0.3 + by * 0.03) % 1.0
            br, bg, bb = hsv_to_rgb(bh, 0.5, 0.08)
            draw_pixel(canvas, 0, by, br, bg, bb)
            draw_pixel(canvas, 63, by, br, bg, bb)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)


# ============================================================
#                    ANALOG CLOCK
# ============================================================

def show_analog_clock():
    clear_input()
    particles = ParticleSystem()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return

        at = get_austria_time()
        hours, minutes, seconds = at.tm_hour, at.tm_min, at.tm_sec
        frac = now % 1.0

        canvas.Clear()

        cx, cy = 31, 33
        R = 28

        # Clock face dots
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                r_dot = R - 1
                h = (now * 0.05 + i * 0.02) % 1.0
                cr, cg, cb = hsv_to_rgb(h, 0.5, 0.4)
                x = cx + int(r_dot * math.cos(angle))
                y = cy + int(r_dot * math.sin(angle))
                draw_pixel(canvas, x, y, cr, cg, cb)
                # extra dot for hour marks
                r_dot2 = R - 2
                x2 = cx + int(r_dot2 * math.cos(angle))
                y2 = cy + int(r_dot2 * math.sin(angle))
                draw_pixel(canvas, x2, y2, cr//2, cg//2, cb//2)
            else:
                r_dot = R
                x = cx + int(r_dot * math.cos(angle))
                y = cy + int(r_dot * math.sin(angle))
                draw_pixel(canvas, x, y, 15, 15, 15)

        # Hour hand
        h_angle = math.radians((hours % 12 + minutes / 60.0) * 30 - 90)
        hx = cx + int(16 * math.cos(h_angle))
        hy = cy + int(16 * math.sin(h_angle))
        draw_line(canvas, cx, cy, hx, hy, 200, 200, 200)

        # Minute hand
        m_angle = math.radians(minutes * 6 + seconds / 10.0 - 90)
        mx = cx + int(22 * math.cos(m_angle))
        my = cy + int(22 * math.sin(m_angle))
        draw_line(canvas, cx, cy, mx, my, 100, 180, 255)

        # Second hand
        s_angle = math.radians((seconds + frac) * 6 - 90)
        sx = cx + int(24 * math.cos(s_angle))
        sy = cy + int(24 * math.sin(s_angle))
        draw_line(canvas, cx, cy, sx, sy, 255, 50, 50)

        # Center dot
        draw_pixel(canvas, cx, cy, 255, 255, 255)
        draw_pixel(canvas, cx+1, cy, 200, 200, 200)
        draw_pixel(canvas, cx, cy+1, 200, 200, 200)

        # Digital time at top
        time_str = f"{hours:02d}:{minutes:02d}"
        draw_text_centered(canvas, time_str, 1, 80, 80, 80)

        # Seconds tick particle
        if seconds != getattr(show_analog_clock, '_last_sec', -1):
            show_analog_clock._last_sec = seconds
            particles.emit(sx, sy, 2, 255, 50, 50, spread=5, life=0.3)

        particles.update(0.03)
        particles.draw(canvas)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)


# ============================================================
#                    DIGITAL CLOCK
# ============================================================

def show_digital_clock():
    clear_input()
    WOCHENTAGE = ["MO", "DI", "MI", "DO", "FR", "SA", "SO"]

    if weather_data.should_fetch():
        weather_data.fetch()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return

        at = get_austria_time()
        hours, minutes, seconds = at.tm_hour, at.tm_min, at.tm_sec
        frac = now % 1.0

        canvas.Clear()

        # Background pattern
        for gx in range(0, 64, 4):
            for gy in range(0, 64, 4):
                wave = math.sin(now * 0.2 + gx * 0.05 + gy * 0.05)
                v = int(3 + 2 * wave)
                draw_pixel(canvas, gx, gy, 0, 0, v)

        # Big time display
        h_str = f"{hours:02d}"
        m_str = f"{minutes:02d}"
        time_full = f"{hours:02d}:{minutes:02d}"
        tw = big_time_width(time_full)
        tx = (64 - tw) // 2

        # Hour color based on time of day
        if 6 <= hours < 12:
            tr, tg, tb = 255, 200, 50
        elif 12 <= hours < 18:
            tr, tg, tb = 50, 200, 255
        elif 18 <= hours < 22:
            tr, tg, tb = 255, 100, 50
        else:
            tr, tg, tb = 100, 100, 200

        draw_big_digit(canvas, h_str[0], tx, 18, tr, tg, tb)
        draw_big_digit(canvas, h_str[1], tx + 6, 18, tr, tg, tb)

        # Blinking colon
        if frac < 0.5:
            draw_pixel(canvas, tx + 13, 20, tr, tg, tb)
            draw_pixel(canvas, tx + 13, 22, tr, tg, tb)

        draw_big_digit(canvas, m_str[0], tx + 16, 18, tr, tg, tb)
        draw_big_digit(canvas, m_str[1], tx + 22, 18, tr, tg, tb)

        # Seconds
        draw_text(canvas, f"{seconds:02d}", tx + 29, 22, tr//3, tg//3, tb//3)

        # Seconds progress bar
        bar_w = int((seconds + frac) / 60.0 * 44)
        for bx in range(bar_w):
            h = (now * 0.1 + bx * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 0.7, 0.3)
            draw_pixel(canvas, 10 + bx, 28, r, g, b)

        # Date
        wday = at.tm_wday
        wday_str = WOCHENTAGE[wday] if wday < 7 else "??"
        date_str = f"{wday_str} {at.tm_mday:02d}.{at.tm_mon:02d}.{at.tm_year}"
        draw_text_centered(canvas, date_str, 32, 80, 80, 100)

        # Rainbow separator
        for x in range(10, 54):
            h = (now * 0.3 + x * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 0.6, 0.2)
            draw_pixel(canvas, x, 39, r, g, b)

        # Weather
        if weather_data.temperature is not None:
            temp = weather_data.temperature
            temp_str = f"{temp:.0f}C"
            if temp <= 0: wr, wg, wb = 100, 150, 255
            elif temp <= 20: wr, wg, wb = 0, 200, 200
            else: wr, wg, wb = 255, 200, 0
            draw_text(canvas, temp_str, 5, 43, wr, wg, wb)
            desc = weather_data.get_description()
            draw_text(canvas, desc, 24, 43, 120, 120, 120)

        if weather_data.should_fetch():
            weather_data.fetch()

        # Top decoration
        for x in range(64):
            h = (now * 0.2 + x * 0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.4, 0.1)
            draw_pixel(canvas, x, 0, r, g, b)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)


# ============================================================
#                    WEATHER DISPLAY
# ============================================================

def show_weather():
    def draw_sun(cx, cy, t):
        draw_filled_circle(canvas, cx, cy, 4, 255, 200, 0)
        for i in range(8):
            angle = math.radians(i * 45 + t * 30)
            rx = cx + int(7 * math.cos(angle))
            ry = cy + int(7 * math.sin(angle))
            draw_pixel(canvas, rx, ry, 255, 255, 100)
            rx2 = cx + int(6 * math.cos(angle))
            ry2 = cy + int(6 * math.sin(angle))
            draw_pixel(canvas, rx2, ry2, 255, 220, 50)

    def draw_cloud(cx, cy):
        for dx, dy in [(-3,0),(-2,-1),(-1,-1),(0,-1),(1,-1),(2,0),
                        (-3,1),(-2,1),(-1,1),(0,1),(1,1),(2,1),(3,0)]:
            draw_pixel(canvas, cx+dx, cy+dy, 150, 150, 160)

    def draw_rain(cx, cy, t):
        draw_cloud(cx, cy)
        for i in range(4):
            rx = cx - 3 + i * 2
            ry = cy + 3 + int((t * 8 + i * 2) % 6)
            draw_pixel(canvas, rx, ry, 50, 100, 255)
            draw_pixel(canvas, rx, ry + 1, 30, 70, 200)

    def draw_snow(cx, cy, t):
        draw_cloud(cx, cy)
        for i in range(5):
            sx = cx - 4 + i * 2 + int(math.sin(t * 2 + i) * 1.5)
            sy = cy + 3 + int((t * 3 + i * 3) % 8)
            draw_pixel(canvas, sx, sy, 200, 200, 255)

    def draw_lightning(cx, cy, t):
        draw_cloud(cx, cy)
        if int(t * 4) % 8 == 0:
            for dy in range(6):
                lx = cx + (1 if dy % 2 else -1)
                draw_pixel(canvas, lx, cy + 2 + dy, 255, 255, 100)

    def draw_fog(cx, cy, t):
        for row in range(4):
            for dx in range(-6, 7):
                offset = int(math.sin(t * 0.5 + row * 0.8) * 2)
                v = 60 + int(20 * math.sin(t + dx * 0.3))
                draw_pixel(canvas, cx + dx + offset, cy + row * 2, v, v, v + 10)

    clear_input()
    if weather_data.should_fetch():
        weather_data.fetch()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return

        canvas.Clear()

        at = get_austria_time()
        hours, minutes = at.tm_hour, at.tm_min

        # Background based on time
        if 6 <= hours < 20:
            for y in range(64):
                ratio = y / 64.0
                r = int(30 + 50 * (1 - ratio))
                g = int(60 + 100 * (1 - ratio))
                b = int(120 + 80 * (1 - ratio))
                for x in range(0, 64, 4):
                    draw_pixel(canvas, x, y, r // 4, g // 4, b // 4)
        else:
            for y in range(64):
                for x in range(0, 64, 6):
                    draw_pixel(canvas, x, y, 2, 2, 5)

        # Title
        draw_text_centered(canvas, "WETTER", 2, 200, 200, 255)
        draw_text_centered(canvas, "WIEN", 9, 120, 120, 150)

        # Rainbow separator
        for x in range(8, 56):
            h = (now * 0.3 + x * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 0.5, 0.2)
            draw_pixel(canvas, x, 15, r, g, b)

        # Weather icon
        wc = weather_data.weathercode
        t = now
        icon_cx, icon_cy = 16, 28
        if wc == 0:
            draw_sun(icon_cx, icon_cy, t)
        elif wc in (1, 2, 3):
            draw_sun(icon_cx + 4, icon_cy - 2, t)
            draw_cloud(icon_cx - 2, icon_cy + 2)
        elif wc in (45, 48):
            draw_fog(icon_cx, icon_cy, t)
        elif wc in (51, 53, 55, 61, 63, 65, 80, 81, 82):
            draw_rain(icon_cx, icon_cy, t)
        elif wc in (71, 73, 75, 77):
            draw_snow(icon_cx, icon_cy, t)
        elif wc in (95, 96, 99):
            draw_lightning(icon_cx, icon_cy, t)
        else:
            draw_cloud(icon_cx, icon_cy)

        # Temperature
        if weather_data.temperature is not None:
            temp = weather_data.temperature
            temp_str = f"{temp:.1f}"
            if temp <= 0:
                tr, tg, tb = 100, 150, 255
            elif temp <= 10:
                tr, tg, tb = 0, 200, 255
            elif temp <= 20:
                tr, tg, tb = 0, 255, 150
            elif temp <= 30:
                tr, tg, tb = 255, 200, 0
            else:
                tr, tg, tb = 255, 50, 0
            draw_text(canvas, temp_str, 32, 22, tr, tg, tb)
            draw_text(canvas, "C", 32 + text_width(temp_str) + 2, 22, tr // 2, tg // 2, tb // 2)

            desc = weather_data.get_description()
            draw_text(canvas, desc, 32, 30, 150, 150, 150)

        # Temperature bar
        if weather_data.temperature is not None:
            temp = weather_data.temperature
            bar_len = max(0, min(44, int((temp + 10) / 50.0 * 44)))
            for bx in range(bar_len):
                h = bx / 44.0 * 0.35
                r, g, b = hsv_to_rgb(0.65 - h, 0.8, 0.4)
                draw_pixel(canvas, 10 + bx, 40, r, g, b)
            draw_text(canvas, "-10", 2, 43, 60, 60, 80)
            draw_text(canvas, "40", 50, 43, 60, 60, 80)

        # Clock at bottom
        time_str = f"{hours:02d}:{minutes:02d}"
        draw_text_centered(canvas, time_str, 52, 80, 80, 80)

        # Update check
        if weather_data.should_fetch():
            weather_data.fetch()

        matrix.SwapOnVSync(canvas)
        time.sleep(0.05)


# ============================================================
#                    BREAKOUT
# ============================================================

def play_breakout(difficulty=2):
    PADDLE_W = 12 if difficulty == 1 else (8 if difficulty == 3 else 10)
    PADDLE_Y = 58
    PADDLE_H = 2
    COLS_B = 8
    ROWS_B = 5
    BRICK_W = 7
    BRICK_H = 3
    BRICK_OFFSET_X = 2
    BRICK_OFFSET_Y = 8

    start_speed = 0.8 if difficulty == 1 else (1.2 if difficulty == 3 else 1.0)

    def create_bricks():
        bricks = {}
        for col in range(COLS_B):
            for row in range(ROWS_B):
                h = (row * 0.15 + col * 0.02) % 1.0
                bricks[(col, row)] = hsv_to_rgb(h, 0.8, 0.8)
        return bricks

    bricks = create_bricks()
    paddle_x = 32.0 - PADDLE_W / 2
    ball_x, ball_y = 32.0, PADDLE_Y - 2
    ball_speed = start_speed
    ball_vx = ball_speed * random.choice([-1, 1]) * 0.5
    ball_vy = -ball_speed
    score = 0
    lives = 3
    level = 1
    serving = True
    particles = ParticleSystem()
    ball_trail = collections.deque(maxlen=6)

    clear_input()
    animation_countdown()
    clear_input()

    while running:
        now = time.time()
        dt = 0.016

        k = consume_key()
        if k == '\x1b': return
        if k == 'a': paddle_x = max(0, paddle_x - 3)
        elif k == 'd': paddle_x = min(64 - PADDLE_W, paddle_x + 3)

        if serving:
            ball_x = paddle_x + PADDLE_W / 2
            ball_y = PADDLE_Y - 2
            canvas.Clear()
            for (col, row), color in bricks.items():
                bx = BRICK_OFFSET_X + col * BRICK_W
                by = BRICK_OFFSET_Y + row * BRICK_H
                draw_rect(canvas, bx, by, BRICK_W - 1, BRICK_H - 1, *color)
                for ddx in range(BRICK_W - 1):
                    draw_pixel(canvas, bx + ddx, by,
                               min(255, int(color[0] * 1.3)),
                               min(255, int(color[1] * 1.3)),
                               min(255, int(color[2] * 1.3)))
            for ddx in range(PADDLE_W):
                fade = 1.0 - abs(ddx - PADDLE_W / 2) / (PADDLE_W / 2) * 0.3
                draw_pixel(canvas, int(paddle_x) + ddx, PADDLE_Y,
                           0, int(200 * fade), int(255 * fade))
                draw_pixel(canvas, int(paddle_x) + ddx, PADDLE_Y + 1,
                           0, int(150 * fade), int(200 * fade))
            draw_pixel(canvas, int(ball_x), int(ball_y), 255, 255, 255)
            if int(now * 3) % 2:
                draw_text_centered(canvas, "W START", 52, 80, 80, 80)
            draw_text(canvas, str(score), 2, 1, 255, 255, 0)
            for i in range(lives):
                draw_pixel(canvas, 58 - i * 3, 1, 255, 50, 50)
            draw_text(canvas, f"L{level}", 50, 1, 100, 100, 100)
            particles.draw(canvas)
            matrix.SwapOnVSync(canvas)
            if k in ('w', ' '):
                serving = False
                ball_vy = -ball_speed
                ball_vx = ball_speed * random.uniform(-0.5, 0.5)
            time.sleep(0.03)
            continue

        # Ball physics
        ball_x += ball_vx * dt * 40
        ball_y += ball_vy * dt * 40

        if ball_x <= 0: ball_x = 0; ball_vx = abs(ball_vx)
        elif ball_x >= 63: ball_x = 63; ball_vx = -abs(ball_vx)
        if ball_y <= 0: ball_y = 0; ball_vy = abs(ball_vy)

        if ball_y >= 63:
            lives -= 1
            particles.emit(int(ball_x), 63, 15, 255, 0, 0, spread=30, life=0.8)
            if lives <= 0:
                animation_flash(0.2, 255, 0, 0)
                animation_game_over(score, (255, 100, 0))
                return
            serving = True
            ball_trail.clear()
            continue

        # Paddle collision
        if ball_vy > 0 and PADDLE_Y - 1 <= ball_y <= PADDLE_Y + PADDLE_H:
            if paddle_x - 1 <= ball_x <= paddle_x + PADDLE_W + 1:
                hit_pos = (ball_x - paddle_x) / PADDLE_W
                ang = (hit_pos - 0.5) * 2.2
                spd = math.sqrt(ball_vx**2 + ball_vy**2)
                ball_vx = spd * math.sin(ang)
                ball_vy = -abs(spd * math.cos(ang))
                ball_y = PADDLE_Y - 2
                particles.emit(int(ball_x), PADDLE_Y, 4, 0, 200, 255, spread=10, life=0.3)

        # Brick collision
        brick_hit = None
        for (col, row), color in list(bricks.items()):
            bx = BRICK_OFFSET_X + col * BRICK_W
            by = BRICK_OFFSET_Y + row * BRICK_H
            if (bx - 1 <= ball_x <= bx + BRICK_W and
                    by - 1 <= ball_y <= by + BRICK_H):
                brick_hit = (col, row)
                bcx = bx + BRICK_W / 2
                bcy = by + BRICK_H / 2
                dx_b = ball_x - bcx
                dy_b = ball_y - bcy
                if abs(dx_b / BRICK_W) > abs(dy_b / BRICK_H):
                    ball_vx = -ball_vx
                else:
                    ball_vy = -ball_vy
                break

        if brick_hit:
            col, row = brick_hit
            color = bricks.pop(brick_hit)
            score += (ROWS_B - row) * 10
            bx = BRICK_OFFSET_X + col * BRICK_W
            by = BRICK_OFFSET_Y + row * BRICK_H
            particles.emit(bx + BRICK_W // 2, by + BRICK_H // 2,
                           8, *color, spread=25, life=0.5)
            if not bricks:
                level += 1
                ball_speed = min(2.5, start_speed + level * 0.15)
                animation_flash(0.15, 0, 255, 0)
                bricks = create_bricks()
                serving = True
                ball_trail.clear()
                continue

        ball_trail.append((ball_x, ball_y))

        # Render
        canvas.Clear()
        for (col, row), color in bricks.items():
            bx = BRICK_OFFSET_X + col * BRICK_W
            by = BRICK_OFFSET_Y + row * BRICK_H
            draw_rect(canvas, bx, by, BRICK_W - 1, BRICK_H - 1, *color)
            for ddx in range(BRICK_W - 1):
                draw_pixel(canvas, bx + ddx, by,
                           min(255, int(color[0] * 1.3)),
                           min(255, int(color[1] * 1.3)),
                           min(255, int(color[2] * 1.3)))

        for i, (tx, ty) in enumerate(ball_trail):
            f = (i + 1) / max(len(ball_trail), 1)
            v = int(80 * f)
            draw_pixel(canvas, int(tx), int(ty), v, v, v)

        bxi, byi = int(ball_x), int(ball_y)
        for ddx in range(-1, 2):
            for ddy in range(-1, 2):
                if ddx == 0 and ddy == 0: continue
                draw_pixel(canvas, bxi + ddx, byi + ddy, 60, 60, 60)
        draw_pixel(canvas, bxi, byi, 255, 255, 255)

        for ddx in range(PADDLE_W):
            fade = 1.0 - abs(ddx - PADDLE_W / 2) / (PADDLE_W / 2) * 0.3
            draw_pixel(canvas, int(paddle_x) + ddx, PADDLE_Y,
                       0, int(200 * fade), int(255 * fade))
            draw_pixel(canvas, int(paddle_x) + ddx, PADDLE_Y + 1,
                       0, int(150 * fade), int(200 * fade))

        particles.update(dt)
        particles.draw(canvas)
        draw_text(canvas, str(score), 2, 1, 255, 255, 0)
        for i in range(lives):
            draw_pixel(canvas, 58 - i * 3, 1, 255, 50, 50)
        draw_text(canvas, f"L{level}", 48, 1, 100, 100, 100)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#                    FLAPPY BIRD
# ============================================================

def play_flappy(difficulty=2):
    if difficulty == 1:
        GRAVITY = 0.06; FLAP_FORCE = -1.7
        GAP_H = 22; PIPE_SPEED = 0.6
    elif difficulty == 3:
        GRAVITY = 0.10; FLAP_FORCE = -1.9
        GAP_H = 14; PIPE_SPEED = 1.0
    else:
        GRAVITY = 0.08; FLAP_FORCE = -1.8
        GAP_H = 18; PIPE_SPEED = 0.8
    PIPE_W = 6
    GROUND_Y = 59
    BIRD_X = 15

    bird_y = 30.0
    bird_vy = 0.0
    bird_frame = 0
    pipes = []
    pipe_timer = 0
    PIPE_INTERVAL = 45
    score = 0
    passed_pipes = set()
    particles = ParticleSystem()
    ground_offset = 0

    clouds = [(random.randint(0, 63), random.randint(2, 20),
               random.uniform(0.1, 0.3)) for _ in range(5)]

    clear_input()
    animation_countdown()
    clear_input()
    frame = 0

    while running:
        now = time.time()
        frame += 1

        k = consume_key()
        if k == '\x1b': return

        if k in ('w', ' '):
            bird_vy = FLAP_FORCE
            bird_frame = 3
            particles.emit(BIRD_X, int(bird_y) + 2, 3,
                           255, 255, 100, spread=8, life=0.3)

        bird_vy += GRAVITY
        bird_y += bird_vy
        if bird_frame > 0: bird_frame -= 1

        if bird_y >= GROUND_Y - 3:
            animation_flash(0.15, 255, 100, 0)
            animation_game_over(score, (255, 200, 0))
            return
        if bird_y < 0:
            bird_y = 0; bird_vy = 0

        pipe_timer += 1
        if pipe_timer >= PIPE_INTERVAL:
            pipe_timer = 0
            current_gap = max(13, GAP_H - score // 5)
            gap_center = random.randint(
                12 + current_gap // 2, GROUND_Y - 8 - current_gap // 2)
            pipes.append([64.0, gap_center, current_gap])

        current_speed = PIPE_SPEED + score * 0.02
        for pipe in pipes:
            pipe[0] -= current_speed
        pipes = [p for p in pipes if p[0] > -PIPE_W - 2]

        for i, pipe in enumerate(pipes):
            if pipe[0] + PIPE_W < BIRD_X and id(pipe) not in passed_pipes:
                passed_pipes.add(id(pipe))
                score += 1
                particles.emit_burst(BIRD_X + 5, int(bird_y),
                                     5, spread=15, life=0.4)

        for pipe in pipes:
            px, gap_center, gap = pipe[0], pipe[1], pipe[2]
            if px - 1 <= BIRD_X + 3 <= px + PIPE_W + 1:
                if (bird_y - 1 < gap_center - gap // 2 or
                        bird_y + 3 > gap_center + gap // 2):
                    animation_flash(0.15, 255, 0, 0)
                    animation_game_over(score, (255, 200, 0))
                    return

        ground_offset = (ground_offset + current_speed) % 4

        # Render
        canvas.Clear()

        for y in range(GROUND_Y):
            ratio = y / GROUND_Y
            r = int(20 + 30 * ratio)
            g = int(30 + 60 * ratio)
            b = int(80 + 80 * (1 - ratio))
            if y % 5 == 0:
                for x in range(0, 64, 8):
                    draw_pixel(canvas, x, y, r, g, b)

        for ci, (cx, cy, cs) in enumerate(clouds):
            wx = (cx - frame * cs * 0.5) % 72 - 4
            draw_pixel(canvas, int(wx), cy, 40, 45, 55)
            draw_pixel(canvas, int(wx) + 1, cy, 45, 50, 60)
            draw_pixel(canvas, int(wx) + 2, cy, 40, 45, 55)
            draw_pixel(canvas, int(wx), cy + 1, 35, 40, 50)
            draw_pixel(canvas, int(wx) + 1, cy - 1, 45, 50, 60)

        for pipe in pipes:
            px, gap_center, gap = int(pipe[0]), pipe[1], pipe[2]
            gap_top = gap_center - gap // 2
            gap_bot = gap_center + gap // 2
            for x in range(PIPE_W):
                px2 = px + x
                if 0 <= px2 < 64:
                    inner = 1 if 1 <= x <= PIPE_W - 2 else 0
                    for y in range(0, gap_top):
                        if inner:
                            draw_pixel(canvas, px2, y, 40, 180, 40)
                        else:
                            draw_pixel(canvas, px2, y, 20, 120, 20)
                    if 0 <= gap_top - 1:
                        draw_pixel(canvas, px2, gap_top - 1, 60, 220, 60)
            for x in range(PIPE_W):
                px2 = px + x
                if 0 <= px2 < 64:
                    inner = 1 if 1 <= x <= PIPE_W - 2 else 0
                    for y in range(gap_bot, GROUND_Y):
                        if inner:
                            draw_pixel(canvas, px2, y, 40, 180, 40)
                        else:
                            draw_pixel(canvas, px2, y, 20, 120, 20)
                    if gap_bot < 64:
                        draw_pixel(canvas, px2, gap_bot, 60, 220, 60)

        for x in range(64):
            draw_pixel(canvas, x, GROUND_Y, 80, 60, 30)
            draw_pixel(canvas, x, GROUND_Y + 1, 100, 80, 40)
            if (x + int(ground_offset)) % 4 < 2:
                draw_pixel(canvas, x, GROUND_Y, 50, 150, 30)
            for dy in range(2, 5):
                draw_pixel(canvas, x, GROUND_Y + dy, 70 + dy * 5, 50 + dy * 3, 20)

        # Bird
        by = int(bird_y)
        draw_pixel(canvas, BIRD_X, by, 255, 220, 50)
        draw_pixel(canvas, BIRD_X + 1, by, 255, 230, 80)
        draw_pixel(canvas, BIRD_X, by + 1, 255, 200, 30)
        draw_pixel(canvas, BIRD_X + 1, by + 1, 255, 210, 50)
        draw_pixel(canvas, BIRD_X + 2, by + 1, 255, 220, 60)
        draw_pixel(canvas, BIRD_X + 2, by, 255, 255, 255)
        draw_pixel(canvas, BIRD_X + 3, by + 1, 255, 100, 0)
        if bird_frame > 1:
            draw_pixel(canvas, BIRD_X, by - 1, 200, 200, 40)
            draw_pixel(canvas, BIRD_X + 1, by - 1, 200, 200, 40)
        else:
            draw_pixel(canvas, BIRD_X - 1, by + 1, 200, 200, 40)
            draw_pixel(canvas, BIRD_X, by + 2, 180, 180, 30)
        if bird_vy > 1.5:
            draw_pixel(canvas, BIRD_X - 1, by - 1, 200, 180, 30)

        particles.update(0.03)
        particles.draw(canvas)

        score_str = str(score)
        sw = text_width(score_str)
        draw_text_centered(canvas, score_str, 3, 0, 0, 0)
        draw_text(canvas, score_str, (64 - sw) // 2 - 1, 2, 255, 255, 255)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.025)


# ============================================================
#                    CONWAY'S GAME OF LIFE
# ============================================================

def play_game_of_life():
    GRID_W, GRID_H = 64, 64
    grid = [[0] * GRID_H for _ in range(GRID_W)]
    next_grid = [[0] * GRID_H for _ in range(GRID_W)]

    def randomize(density=0.3):
        for x in range(GRID_W):
            for y in range(GRID_H):
                grid[x][y] = 1 if random.random() < density else 0

    def clear_grid():
        for x in range(GRID_W):
            for y in range(GRID_H):
                grid[x][y] = 0

    def add_glider(ox, oy):
        for dx, dy in [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]:
            grid[(ox + dx) % GRID_W][(oy + dy) % GRID_H] = 1

    def add_rpentomino(ox, oy):
        for dx, dy in [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)]:
            grid[(ox + dx) % GRID_W][(oy + dy) % GRID_H] = 1

    def add_acorn(ox, oy):
        for dx, dy in [(1, 0), (3, 1), (0, 2), (1, 2), (4, 2), (5, 2), (6, 2)]:
            grid[(ox + dx) % GRID_W][(oy + dy) % GRID_H] = 1

    def count_neighbors(x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                if grid[(x + dx) % GRID_W][(y + dy) % GRID_H] > 0:
                    count += 1
        return count

    def step():
        alive = 0
        for x in range(GRID_W):
            for y in range(GRID_H):
                n = count_neighbors(x, y)
                if grid[x][y] > 0:
                    if n == 2 or n == 3:
                        next_grid[x][y] = min(grid[x][y] + 1, 200)
                    else:
                        next_grid[x][y] = 0
                else:
                    if n == 3:
                        next_grid[x][y] = 1
                    else:
                        next_grid[x][y] = 0
                if next_grid[x][y] > 0: alive += 1
        for x in range(GRID_W):
            for y in range(GRID_H):
                grid[x][y] = next_grid[x][y]
        return alive

    # Pattern submenu
    clear_input()
    sub_sel = 0
    patterns = [
        ("ZUFALL", None),
        ("GLIDER", "glider"),
        ("R-PENTO", "rpentomino"),
        ("ACORN", "acorn"),
    ]
    starfield = Starfield(30)

    while running:
        now = time.time()
        canvas.Clear()
        starfield.draw(canvas, now)
        draw_text_centered(canvas, "GAME OF", 5, 0, 200, 100)
        draw_text_centered(canvas, "LIFE", 12, 0, 200, 100)
        for x in range(12, 52):
            h = (now * 0.3 + x * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 0.6, 0.25)
            draw_pixel(canvas, x, 19, r, g, b)
        for i, (label, _) in enumerate(patterns):
            y = 23 + i * 10
            if i == sub_sel:
                pulse = 0.6 + 0.4 * math.sin(now * 5)
                v = int(255 * pulse)
                ax = 4 + int(math.sin(now * 6) * 1.5)
                draw_text(canvas, ">", ax, y, v, v, 0)
                draw_text(canvas, label, 12, y, v, v // 2, 0)
            else:
                draw_text(canvas, label, 12, y, 60, 40, 0)
        if int(now * 1.5) % 2:
            draw_text_centered(canvas, "ESC BACK", 58, 50, 50, 50)
        matrix.SwapOnVSync(canvas)
        sk = consume_key()
        if sk == 'w': sub_sel = (sub_sel - 1) % len(patterns)
        elif sk == 's': sub_sel = (sub_sel + 1) % len(patterns)
        elif sk == '\x1b': return
        elif sk in ('\r', '\n', 'd', ' '):
            _, pattern = patterns[sub_sel]
            clear_grid()
            if pattern is None:
                randomize(0.35)
            elif pattern == "glider":
                for _ in range(8):
                    add_glider(random.randint(0, 60), random.randint(0, 60))
            elif pattern == "rpentomino":
                add_rpentomino(30, 30)
            elif pattern == "acorn":
                add_acorn(28, 30)
            break
        time.sleep(0.05)

    # Simulation
    paused = False
    speed = 0.08
    generation = 0
    clear_input()
    last_step = time.time()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return
        elif k == ' ': paused = not paused
        elif k == 'r':
            clear_grid(); randomize(0.35); generation = 0
        elif k == 'w': speed = max(0.02, speed - 0.02)
        elif k == 's': speed = min(0.5, speed + 0.02)

        if not paused and now - last_step >= speed:
            last_step = now
            alive = step()
            generation += 1
            if alive == 0:
                time.sleep(0.5)
                randomize(0.35); generation = 0

        canvas.Clear()
        for x in range(GRID_W):
            for y in range(GRID_H):
                age = grid[x][y]
                if age > 0:
                    hue = (age * 0.02 + now * 0.1) % 1.0
                    brightness = min(1.0, 0.4 + age * 0.05)
                    r, g, b = hsv_to_rgb(hue, 0.9, brightness)
                    draw_pixel(canvas, x, y, r, g, b)

        gen_str = f"G{generation}"
        draw_text(canvas, gen_str, 1, 1, 80, 80, 80)
        if paused:
            if int(now * 3) % 2:
                draw_text(canvas, "PAUSE", 38, 1, 200, 200, 0)
        sp_bar = int((1.0 - (speed - 0.02) / 0.48) * 10)
        for i in range(sp_bar):
            draw_pixel(canvas, 60, 58 - i, 0, 100 + i * 15, 0)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.02)


# ============================================================
#                    REACTION TIME GAME
# ============================================================

def play_reaction(difficulty=2):
    clear_input()
    particles = ParticleSystem()
    best_time = 9999
    times = []
    round_num = 0
    if difficulty == 1:
        TOTAL_ROUNDS = 3; wait_min, wait_max = 1.5, 3.5
    elif difficulty == 3:
        TOTAL_ROUNDS = 7; wait_min, wait_max = 1.0, 6.0
    else:
        TOTAL_ROUNDS = 5; wait_min, wait_max = 1.5, 5.0

    while running and round_num < TOTAL_ROUNDS:
        # Phase 1: Get ready
        clear_input()
        start_show = time.time()
        while time.time() - start_show < 1.5:
            now = time.time()
            canvas.Clear()
            draw_text_centered(canvas, f"RUNDE {round_num+1}", 8, 150, 150, 150)
            pulse = 0.5 + 0.5 * math.sin(now * 6)
            v = int(200 * pulse)
            draw_text_centered(canvas, "BEREIT", 26, v, v, 0)
            draw_text_centered(canvas, "WARTE AUF", 42, 80, 80, 80)
            draw_text_centered(canvas, "GRUEN!", 50, 0, 80, 0)
            matrix.SwapOnVSync(canvas)
            ck = consume_key()
            if ck == '\x1b': return
            time.sleep(0.03)

        # Phase 2: Red waiting
        wait_time = random.uniform(wait_min, wait_max)
        wait_start = time.time()
        too_early = False

        while time.time() - wait_start < wait_time:
            canvas.Clear()
            now = time.time()
            pulse = 0.8 + 0.2 * math.sin(now * 2)
            for x in range(0, 64, 2):
                for y in range(0, 64, 2):
                    draw_pixel(canvas, x, y, int(40 * pulse), 0, 0)
            draw_text_centered(canvas, "WARTE", 28, 200, 50, 50)
            matrix.SwapOnVSync(canvas)
            ck = consume_key()
            if ck == '\x1b': return
            if ck is not None:
                too_early = True; break
            time.sleep(0.02)

        if too_early:
            animation_flash(0.2, 255, 0, 0)
            show_start = time.time()
            while time.time() - show_start < 2.0:
                canvas.Clear()
                draw_text_centered(canvas, "ZU", 20, 255, 0, 0)
                draw_text_centered(canvas, "FRUEH!", 28, 255, 0, 0)
                draw_text_centered(canvas, "NOCHMAL", 44, 150, 150, 150)
                matrix.SwapOnVSync(canvas)
                if consume_key() == '\x1b': return
                time.sleep(0.05)
            continue

        # Phase 3: GREEN! Measure
        green_time = time.time()
        reacted = False

        while not reacted:
            now = time.time()
            elapsed_ms = int((now - green_time) * 1000)
            canvas.Clear()
            for x in range(0, 64, 2):
                for y in range(0, 64, 2):
                    draw_pixel(canvas, x, y, 0, 30, 0)
            draw_text_centered(canvas, "JETZT!", 20, 0, 255, 0)
            draw_text_centered(canvas, "DRUECK!", 30, 0, 255, 0)
            draw_text_centered(canvas, f"{elapsed_ms}MS", 48, 200, 200, 200)
            matrix.SwapOnVSync(canvas)
            ck = consume_key()
            if ck == '\x1b': return
            if ck is not None:
                reaction_ms = int((time.time() - green_time) * 1000)
                times.append(reaction_ms)
                if reaction_ms < best_time: best_time = reaction_ms
                reacted = True; round_num += 1
            if now - green_time > 3.0:
                times.append(3000); round_num += 1; reacted = True
            time.sleep(0.005)

        # Phase 4: Result
        reaction_ms = times[-1]
        particles.emit_burst(32, 32, 10, spread=25, life=0.8)
        if reaction_ms < 200:
            rating = "BLITZ!"; rc, gc, bc = 255, 255, 0
        elif reaction_ms < 300:
            rating = "SUPER!"; rc, gc, bc = 0, 255, 0
        elif reaction_ms < 400:
            rating = "GUT"; rc, gc, bc = 0, 200, 200
        elif reaction_ms < 600:
            rating = "OK"; rc, gc, bc = 200, 200, 0
        else:
            rating = "LANGSAM"; rc, gc, bc = 255, 100, 0

        show_start = time.time()
        while time.time() - show_start < 2.5:
            now = time.time()
            canvas.Clear()
            particles.update(0.03); particles.draw(canvas)
            draw_text_centered(canvas, f"{reaction_ms}MS", 18, 255, 255, 255)
            pulse = 0.6 + 0.4 * math.sin(now * 6)
            draw_text_centered(canvas, rating, 30,
                               int(rc * pulse), int(gc * pulse), int(bc * pulse))
            draw_text_centered(canvas, f"BEST {best_time}MS", 46, 100, 100, 150)
            draw_text_centered(canvas, f"{round_num}/{TOTAL_ROUNDS}", 56, 80, 80, 80)
            matrix.SwapOnVSync(canvas)
            if consume_key() == '\x1b': return
            time.sleep(0.03)

    # Final results
    if times:
        avg = sum(times) // len(times)
    else:
        avg = 0

    clear_input()
    particles = ParticleSystem()
    particles.emit_burst(32, 20, 15, spread=30, life=1.0)
    start = time.time()

    while running:
        now = time.time()
        canvas.Clear()
        particles.update(0.03); particles.draw(canvas)
        draw_text_centered(canvas, "ERGEBNIS", 5, 200, 200, 255)
        for x in range(10, 54):
            h = (now * 0.3 + x * 0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.7, 0.3)
            draw_pixel(canvas, x, 12, r, g, b)
        draw_text_centered(canvas, "SCHNITT", 16, 150, 150, 150)
        draw_text_centered(canvas, f"{avg}MS", 24, 0, 255, 200)
        draw_text_centered(canvas, "BESTE", 34, 150, 150, 150)
        draw_text_centered(canvas, f"{best_time}MS", 42, 255, 255, 0)
        for i, t in enumerate(times):
            tx = 5 + i * 12
            draw_text(canvas, str(t), tx, 54, 80, 80, 80)
        if now - start > 1.5 and int(now * 2) % 2:
            draw_text_centered(canvas, "ESC", 58, 60, 60, 60)
        matrix.SwapOnVSync(canvas)
        if now - start > 1.0 and consume_key() is not None: return
        time.sleep(0.03)


# ============================================================
#                    MAZE GENERATOR / RUNNER
# ============================================================

def play_maze(difficulty=2):
    CELL_SIZE = 2
    MAZE_W = 31
    MAZE_H = 31
    if difficulty == 1:
        default_sight = 8; fog_default = False
    elif difficulty == 3:
        default_sight = 4; fog_default = True
    else:
        default_sight = 6; fog_default = True

    def generate_maze():
        maze = [[1] * MAZE_H for _ in range(MAZE_W)]
        start_x, start_y = 1, 1
        maze[start_x][start_y] = 0
        stack = [(start_x, start_y)]
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        while stack:
            cx, cy = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if (0 < nx < MAZE_W and 0 < ny < MAZE_H
                        and maze[nx][ny] == 1):
                    maze[cx + dx // 2][cy + dy // 2] = 0
                    maze[nx][ny] = 0
                    stack.append((nx, ny))
                    found = True; break
            if not found:
                stack.pop()
        return maze

    level = 1
    total_steps = 0

    while running:
        maze = generate_maze()
        player_x, player_y = 1, 1
        goal_x, goal_y = MAZE_W - 2, MAZE_H - 2
        maze[goal_x][goal_y] = 0
        steps = 0
        fog = fog_default
        particles = ParticleSystem()
        SIGHT = default_sight
        clear_input()

        while running:
            now = time.time()
            k = consume_key()
            if k == '\x1b': return
            elif k == 'f': fog = not fog

            dx, dy = 0, 0
            if k == 'w': dy = -1
            elif k == 's': dy = 1
            elif k == 'a': dx = -1
            elif k == 'd': dx = 1

            nx, ny = player_x + dx, player_y + dy
            if (0 <= nx < MAZE_W and 0 <= ny < MAZE_H
                    and maze[nx][ny] == 0):
                player_x, player_y = nx, ny
                steps += 1; total_steps += 1

            if player_x == goal_x and player_y == goal_y:
                particles.emit_burst(
                    goal_x * CELL_SIZE + 1, goal_y * CELL_SIZE + 1,
                    15, spread=25, life=0.8)
                animation_flash(0.15, 255, 255, 0)
                show_start = time.time()
                while time.time() - show_start < 2.0 and running:
                    canvas.Clear()
                    particles.update(0.03); particles.draw(canvas)
                    draw_text_centered(canvas, f"LEVEL {level}!",
                                       20, 255, 255, 0)
                    draw_text_centered(canvas, f"{steps} SCHRITTE",
                                       32, 200, 200, 200)
                    matrix.SwapOnVSync(canvas)
                    if consume_key() == '\x1b': return
                    time.sleep(0.03)
                level += 1; break

            # Render
            canvas.Clear()
            cam_x = player_x * CELL_SIZE - 31
            cam_y = player_y * CELL_SIZE - 31

            for mx in range(MAZE_W):
                for my in range(MAZE_H):
                    sx = mx * CELL_SIZE - cam_x
                    sy = my * CELL_SIZE - cam_y
                    if sx < -2 or sx > 65 or sy < -2 or sy > 65:
                        continue
                    if fog:
                        dist = abs(mx - player_x) + abs(my - player_y)
                        if dist > SIGHT: continue
                        fog_fade = max(0.2, 1.0 - (dist / SIGHT) * 0.8)
                    else:
                        fog_fade = 1.0
                    if maze[mx][my] == 1:
                        h = (now * 0.1 + (mx + my) * 0.05) % 1.0
                        r, g, b = hsv_to_rgb(h, 0.3, 0.2 * fog_fade)
                        for ddx in range(CELL_SIZE):
                            for ddy in range(CELL_SIZE):
                                draw_pixel(canvas, sx + ddx, sy + ddy, r, g, b)

            # Goal
            gsx = goal_x * CELL_SIZE - cam_x
            gsy = goal_y * CELL_SIZE - cam_y
            if (not fog or
                    abs(goal_x - player_x) + abs(goal_y - player_y) <= SIGHT):
                pulse = 0.5 + 0.5 * math.sin(now * 5)
                for ddx in range(CELL_SIZE):
                    for ddy in range(CELL_SIZE):
                        draw_pixel(canvas, gsx + ddx, gsy + ddy,
                                   int(255 * pulse), int(200 * pulse), 0)

            # Player
            psx = player_x * CELL_SIZE - cam_x
            psy = player_y * CELL_SIZE - cam_y
            for ddx in range(CELL_SIZE):
                for ddy in range(CELL_SIZE):
                    draw_pixel(canvas, psx + ddx, psy + ddy, 0, 255, 0)
            for ddx in range(-1, CELL_SIZE + 1):
                for ddy in range(-1, CELL_SIZE + 1):
                    if 0 <= ddx < CELL_SIZE and 0 <= ddy < CELL_SIZE:
                        continue
                    draw_pixel(canvas, psx + ddx, psy + ddy, 0, 40, 0)

            particles.update(0.03); particles.draw(canvas)
            draw_text(canvas, f"L{level}", 1, 1, 150, 150, 0)
            draw_text(canvas, str(steps), 48, 1, 150, 150, 150)
            if fog:
                draw_pixel(canvas, 62, 1, 100, 0, 100)

            matrix.SwapOnVSync(canvas)
            time.sleep(0.05)


# ============================================================
#                    DIFFICULTY MENU
# ============================================================

def show_difficulty_menu(title, title_color, starfield, menu_start):
    """Shows difficulty submenu (EINFACH/MITTEL/SCHWER).
    Returns 1, 2 or 3, or None on ESC."""
    sub_sel = 0
    submenu = [("EINFACH", (0, 255, 0)),
               ("MITTEL", (255, 200, 0)),
               ("SCHWER", (255, 50, 50))]
    while running:
        now2 = time.time()
        canvas.Clear()
        starfield.draw(canvas, now2 - menu_start)
        draw_text_centered(canvas, title, 5,
                           title_color[0], title_color[1], title_color[2])
        for x in range(15, 49):
            h = (now2 * 0.5 + x * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 0.3)
            draw_pixel(canvas, x, 12, r, g, b)
        for i, (label, color) in enumerate(submenu):
            y = 18 + i * 15
            if i == sub_sel:
                pulse = 0.6 + 0.4 * math.sin(now2 * 5)
                r = int(color[0] * pulse)
                g = int(color[1] * pulse)
                b = int(color[2] * pulse)
                ax = 4 + int(math.sin(now2 * 6) * 1.5)
                draw_text(canvas, ">", ax, y, r, g, b)
                draw_text(canvas, f"{i+1} {label}", 12, y, r, g, b)
            else:
                draw_text(canvas, f"{i+1} {label}",
                          12, y, color[0] // 4, color[1] // 4, color[2] // 4)
        if int(now2 * 1.5) % 2:
            draw_text_centered(canvas, "ESC BACK", 58, 50, 50, 50)
        matrix.SwapOnVSync(canvas)
        sk = consume_key()
        if sk in ('w', 'W'): sub_sel = (sub_sel - 1) % 3
        elif sk in ('s', 'S'): sub_sel = (sub_sel + 1) % 3
        elif sk == '1': animation_transition(); return 1
        elif sk == '2': animation_transition(); return 2
        elif sk == '3': animation_transition(); return 3
        elif sk in ('\r', '\n', 'd', 'D'):
            animation_transition(); return sub_sel + 1
        elif sk == '\x1b': return None
        time.sleep(0.05)
    return None


# ============================================================
#                    MAIN MENU
# ============================================================

def show_main_menu():
    starfield = Starfield(50)
    selected = 0

    tab_names = ["SPIELE", "EXTRAS"]
    tab_colors = [(0, 255, 100), (100, 150, 255)]
    current_tab = 0

    tabs = [
        # SPIELE
        [
            ("SNAKE",      (0, 255, 0)),
            ("TETRIS",     (0, 150, 255)),
            ("PONG",       (255, 0, 255)),
            ("BREAKOUT",   (255, 100, 0)),
            ("FLAPPY",     (255, 220, 0)),
            ("REACTION",   (255, 50, 50)),
            ("LABYRINTH",  (0, 255, 200)),
        ],
        # EXTRAS
        [
            ("LIFE",       (200, 100, 0)),
            ("DVD",        (255, 0, 100)),
            ("ANALOG",     (100, 200, 255)),
            ("DIGITAL",    (0, 200, 200)),
            ("WETTER",     (100, 255, 100)),
        ],
    ]

    menu_items = tabs[current_tab]
    scroll_offset = 0
    VISIBLE_ITEMS = 4
    menu_start = time.time()

    # Intro animation
    intro_start = time.time()
    while time.time() - intro_start < 1.5 and running:
        t = time.time() - intro_start
        canvas.Clear()
        starfield.draw(canvas, t)
        title_y = int(-8 + t * 10)
        title_y = min(title_y, 2)
        title_text = "MATRIX"
        tx = (64 - text_width(title_text)) // 2
        for i, ch in enumerate(title_text):
            h = (t * 0.5 + i * 0.12) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 1.0)
            draw_text(canvas, ch, tx + i * 4, title_y, r, g, b)
        if t > 0.6:
            fade = min(1.0, (t - 0.6) / 0.4)
            v = int(120 * fade)
            draw_text_centered(canvas, "HUB", 9, v, v, v)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)

    clear_input()

    # Menu loop
    while running:
        now = time.time()
        t = now - menu_start

        canvas.Clear()
        starfield.draw(canvas, t)

        # Title
        title_text = "MATRIX"
        tx = (64 - text_width(title_text)) // 2
        for i, ch in enumerate(title_text):
            h = (t * 0.3 + i * 0.12) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 1.0)
            draw_text(canvas, ch, tx + i * 4, 2, r, g, b)
        draw_text_centered(canvas, "HUB", 9, 100, 100, 120)

        # Tabs
        for ti in range(len(tab_names)):
            tc = tab_colors[ti]
            tx_pos = 2 + ti * 32
            if ti == current_tab:
                pulse_tab = 0.7 + 0.3 * math.sin(t * 4)
                draw_text(canvas, tab_names[ti], tx_pos, 14,
                          int(tc[0] * pulse_tab), int(tc[1] * pulse_tab),
                          int(tc[2] * pulse_tab))
            else:
                draw_text(canvas, tab_names[ti], tx_pos, 14,
                          tc[0] // 6, tc[1] // 6, tc[2] // 6)

        menu_items = tabs[current_tab]

        # Scroll management
        if selected < scroll_offset:
            scroll_offset = selected
        elif selected >= scroll_offset + VISIBLE_ITEMS:
            scroll_offset = selected - VISIBLE_ITEMS + 1

        for vi in range(VISIBLE_ITEMS):
            idx = scroll_offset + vi
            if idx >= len(menu_items): break
            name, base_color = menu_items[idx]
            y = 21 + vi * 10
            is_selected = (idx == selected)
            if is_selected:
                pulse = 0.6 + 0.4 * math.sin(t * 5)
                r = int(base_color[0] * pulse)
                g = int(base_color[1] * pulse)
                b = int(base_color[2] * pulse)
                arrow_x = 2 + int(math.sin(t * 6) * 1.5)
                draw_text(canvas, ">", arrow_x, y, r, g, b)
                draw_text(canvas, name, 10, y, r, g, b)
                w = text_width(name)
                for ux in range(w + 2):
                    gr = int(pulse * 0.25 * base_color[0])
                    gg = int(pulse * 0.25 * base_color[1])
                    gb = int(pulse * 0.25 * base_color[2])
                    draw_pixel(canvas, 9 + ux, y + 6, gr, gg, gb)
            else:
                r = base_color[0] // 5
                g = base_color[1] // 5
                b = base_color[2] // 5
                draw_text(canvas, name, 10, y, r, g, b)

        # Scroll indicators
        if scroll_offset > 0:
            pulse_up = 0.5 + 0.5 * math.sin(t * 4)
            v = int(80 * pulse_up)
            draw_pixel(canvas, 60, 20, v, v, v)
            draw_pixel(canvas, 59, 21, v, v, v)
            draw_pixel(canvas, 61, 21, v, v, v)

        if scroll_offset + VISIBLE_ITEMS < len(menu_items):
            pulse_dn = 0.5 + 0.5 * math.sin(t * 4 + 1)
            v = int(80 * pulse_dn)
            bottom_y = 21 + VISIBLE_ITEMS * 10 - 3
            draw_pixel(canvas, 60, bottom_y + 2, v, v, v)
            draw_pixel(canvas, 59, bottom_y + 1, v, v, v)
            draw_pixel(canvas, 61, bottom_y + 1, v, v, v)

        page_str = f"{selected+1}/{len(menu_items)}"
        draw_text(canvas, page_str, 40, 58, 40, 40, 50)
        if int(t * 1.5) % 2:
            draw_text(canvas, "W/S TAB", 2, 58, 40, 40, 40)

        matrix.SwapOnVSync(canvas)

        # Input
        k = consume_key()
        if k in ('\t', 'a', 'A'):
            current_tab = (current_tab + 1) % len(tabs)
            menu_items = tabs[current_tab]
            selected = 0; scroll_offset = 0
            continue
        if k in ('w', 'W'):
            selected = (selected - 1) % len(menu_items)
        elif k in ('s', 'S'):
            selected = (selected + 1) % len(menu_items)

        # Direct numeric choice 1..9
        if k and len(k) == 1 and k.isdigit() and k != '0':
            num = int(k) - 1
            if num < len(menu_items):
                selected = num; k = '\r'

        # Confirm
        if k in ('\r', '\n', 'd', 'D'):
            animation_transition()
            clear_input()
            item_name = menu_items[selected][0]
            item_color = menu_items[selected][1]

            if item_name == "SNAKE":
                _snake_submenu(starfield, menu_start)
            elif item_name == "TETRIS":
                play_tetris()
            elif item_name == "PONG":
                d = show_difficulty_menu("PONG", item_color, starfield, menu_start)
                if d is not None: play_pong(d)
            elif item_name == "BREAKOUT":
                d = show_difficulty_menu("BREAKOUT", item_color, starfield, menu_start)
                if d is not None: play_breakout(d)
            elif item_name == "FLAPPY":
                d = show_difficulty_menu("FLAPPY", item_color, starfield, menu_start)
                if d is not None: play_flappy(d)
            elif item_name == "REACTION":
                d = show_difficulty_menu("REACTION", item_color, starfield, menu_start)
                if d is not None: play_reaction(d)
            elif item_name == "LABYRINTH":
                d = show_difficulty_menu("LABYRINTH", item_color, starfield, menu_start)
                if d is not None: play_maze(d)
            elif item_name == "LIFE":
                play_game_of_life()
            elif item_name == "DVD":
                play_dvd_bounce()
            elif item_name == "ANALOG":
                show_analog_clock()
            elif item_name == "DIGITAL":
                show_digital_clock()
            elif item_name == "WETTER":
                show_weather()

            clear_input()
            menu_start = time.time()

        time.sleep(0.05)


# ============================================================
#                    SNAKE SUBMENU HELPER
# ============================================================

def _snake_submenu(starfield, menu_start):
    sub_sel = 0
    while running:
        now2 = time.time()
        canvas.Clear()
        starfield.draw(canvas, now2 - menu_start)
        draw_text_centered(canvas, "SNAKE", 5, 0, 255, 0)
        for x in range(15, 49):
            h = (now2 * 0.5 + x * 0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 0.3)
            draw_pixel(canvas, x, 12, r, g, b)
        submenu = [("NORMAL", (0, 255, 0)),
                   ("ULTIMATE", (255, 80, 0))]
        for i, (label, color) in enumerate(submenu):
            y = 20 + i * 18
            if i == sub_sel:
                pulse = 0.6 + 0.4 * math.sin(now2 * 5)
                r = int(color[0] * pulse)
                g = int(color[1] * pulse)
                b = int(color[2] * pulse)
                ax = 4 + int(math.sin(now2 * 6) * 1.5)
                draw_text(canvas, ">", ax, y, r, g, b)
                draw_text(canvas, f"{i+1} {label}", 12, y, r, g, b)
            else:
                draw_text(canvas, f"{i+1} {label}",
                          12, y, color[0] // 4,
                          color[1] // 4, color[2] // 4)
        if int(now2 * 1.5) % 2:
            draw_text_centered(canvas, "ESC BACK", 58, 50, 50, 50)
        matrix.SwapOnVSync(canvas)
        sk = consume_key()
        if sk in ('w', 'W'):
            sub_sel = (sub_sel - 1) % 2
        elif sk in ('s', 'S'):
            sub_sel = (sub_sel + 1) % 2
        elif sk == '1':
            animation_transition(); play_snake(1); return
        elif sk == '2':
            animation_transition(); play_snake(2); return
        elif sk in ('\r', '\n', 'd', 'D'):
            animation_transition(); play_snake(sub_sel + 1); return
        elif sk == '\x1b': return
        time.sleep(0.05)


# ============================================================
#                    ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        show_main_menu()
    finally:
        running = False
        try:
            matrix.Clear()
        except Exception:
            pass

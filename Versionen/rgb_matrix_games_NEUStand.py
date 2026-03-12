# ============================================================
#  RGB MATRIX GAMES - TEIL 1 von 5
#  Imports, Setup, Fonts, Drawing, Input, Particles, Time/Weather
#  NEUE MODULE: Spotify + Audio Visualizer Klassen
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

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    HAS_SPOTIPY = True
except ImportError:
    HAS_SPOTIPY = False

try:
    from PIL import Image
    import io as _io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

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
    offset = 0
    for char in str(text).upper():
        if char in CHARS:
            pixels = CHARS[char]
            for i in range(15):
                if pixels[i]:
                    draw_pixel(canvas, x_start + offset + (i % 3), y_start + (i // 3), r, g, b)
        offset += 4

def text_width(text):
    return max(0, len(str(text)) * 4 - 1)

def draw_text_centered(canvas, text, y, r, g, b):
    w = text_width(text)
    draw_text(canvas, text, (64 - w) // 2, y, r, g, b)

def draw_block(canvas, x, y, r, g, b):
    for dx in range(2):
        for dy in range(2):
            draw_pixel(canvas, x * 2 + dx, y * 2 + dy, r, g, b)

def hsv_to_rgb(h, s, v):
    if s == 0:
        c = int(v * 255); return c, c, c
    h = h % 1.0
    i = int(h * 6); f = h * 6 - i
    p, q, t = v*(1-s), v*(1-s*f), v*(1-s*(1-f))
    if i == 0: r,g,b = v,t,p
    elif i == 1: r,g,b = q,v,p
    elif i == 2: r,g,b = p,v,t
    elif i == 3: r,g,b = p,q,v
    elif i == 4: r,g,b = t,p,v
    else: r,g,b = v,p,q
    return int(r*255), int(g*255), int(b*255)

def draw_rect(canvas, x, y, w, h, r, g, b):
    for dx in range(w):
        for dy in range(h):
            draw_pixel(canvas, x+dx, y+dy, r, g, b)

def draw_rect_outline(canvas, x, y, w, h, r, g, b):
    for dx in range(w):
        draw_pixel(canvas, x+dx, y, r, g, b)
        draw_pixel(canvas, x+dx, y+h-1, r, g, b)
    for dy in range(h):
        draw_pixel(canvas, x, y+dy, r, g, b)
        draw_pixel(canvas, x+w-1, y+dy, r, g, b)

def draw_line(canvas, x0, y0, x1, y1, r, g, b):
    dx = abs(x1-x0); dy = abs(y1-y0)
    sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        draw_pixel(canvas, x0, y0, r, g, b)
        if x0 == x1 and y0 == y1: break
        e2 = 2*err
        if e2 > -dy: err -= dy; x0 += sx
        if e2 < dx: err += dx; y0 += sy

def draw_circle(canvas, cx, cy, radius, r, g, b):
    x, y, err = radius, 0, 0
    while x >= y:
        for px, py in [(cx+x,cy+y),(cx+y,cy+x),(cx-y,cy+x),(cx-x,cy+y),
                        (cx-x,cy-y),(cx-y,cy-x),(cx+y,cy-x),(cx+x,cy-y)]:
            draw_pixel(canvas, px, py, r, g, b)
        y += 1; err += 1 + 2*y
        if 2*(err-x)+1 > 0: x -= 1; err += 1-2*x

def draw_filled_circle(canvas, cx, cy, radius, r, g, b):
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            if dx*dx + dy*dy <= radius*radius:
                draw_pixel(canvas, cx+dx, cy+dy, r, g, b)

def draw_big_digit(canvas, digit, x, y, r, g, b):
    if digit not in BIG_DIGITS: return
    pixels = BIG_DIGITS[digit]
    for i in range(35):
        if pixels[i]:
            draw_pixel(canvas, x + (i % 5), y + (i // 5), r, g, b)

def draw_big_time(canvas, text, x, y, r, g, b):
    offset = 0
    for ch in text:
        if ch in BIG_DIGITS:
            draw_big_digit(canvas, ch, x + offset, y, r, g, b)
            offset += 6
        elif ch == ':':
            draw_pixel(canvas, x + offset + 1, y + 2, r, g, b)
            draw_pixel(canvas, x + offset + 1, y + 4, r, g, b)
            offset += 4
        else:
            offset += 3

def big_time_width(text):
    w = 0
    for ch in text:
        if ch in BIG_DIGITS: w += 6
        elif ch == ':': w += 4
        else: w += 3
    return max(0, w - 1)


# ============================================================
#                    INPUT HANDLER
# ============================================================

key_pressed = None
key_queue = collections.deque(maxlen=16)
running = True
input_lock = threading.Lock()

def get_input():
    global key_pressed, running
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        while running:
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                # Pruefe ob Escape-Sequenz (Pfeiltasten) folgt
                if _select.select([sys.stdin], [], [], 0.02)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[' and _select.select([sys.stdin], [], [], 0.02)[0]:
                        ch3 = sys.stdin.read(1)
                        arrow_map = {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}
                        ch = arrow_map.get(ch3, '\x1b')
                    else:
                        ch = '\x1b'
                # else: einzelnes ESC
            with input_lock:
                key_pressed = ch
                key_queue.append(ch)
            if ch == 'q':
                running = False
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

threading.Thread(target=get_input, daemon=True).start()

def consume_key():
    global key_pressed
    with input_lock:
        k = key_pressed; key_pressed = None; return k

def consume_queue():
    with input_lock:
        return key_queue.popleft() if key_queue else None

def peek_key():
    with input_lock:
        return key_pressed

def clear_input():
    global key_pressed
    with input_lock:
        key_pressed = None; key_queue.clear()


# ============================================================
#              PARTICLE SYSTEM + STARFIELD
# ============================================================

class Particle:
    __slots__ = ['x','y','vx','vy','r','g','b','life','max_life']
    def __init__(self, x, y, vx, vy, r, g, b, life=1.0):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.r, self.g, self.b = r, g, b
        self.life = life; self.max_life = life
    def update(self, dt):
        self.x += self.vx*dt; self.y += self.vy*dt
        self.vy += 25*dt; self.life -= dt
        return self.life > 0
    def draw(self, canvas):
        f = max(0, self.life / self.max_life)
        draw_pixel(canvas, int(self.x), int(self.y),
                   int(self.r*f), int(self.g*f), int(self.b*f))

class ParticleSystem:
    def __init__(self): self.particles = []
    def emit(self, x, y, count, r, g, b, spread=30, life=0.8):
        for _ in range(count):
            self.particles.append(Particle(x, y,
                random.uniform(-spread,spread),
                random.uniform(-spread, spread*0.5), r, g, b, life))
    def emit_burst(self, x, y, count, spread=30, life=0.8):
        for i in range(count):
            h = i/count; r,g,b = hsv_to_rgb(h, 1.0, 1.0)
            self.particles.append(Particle(x, y,
                random.uniform(-spread,spread),
                random.uniform(-spread, spread*0.5), r, g, b, life))
    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
    def draw(self, canvas):
        for p in self.particles: p.draw(canvas)
    def clear(self): self.particles.clear()

class Starfield:
    def __init__(self, count=40):
        self.stars = [(random.randint(0,63), random.randint(0,63),
                       random.uniform(0.3,1.5), random.randint(40,180))
                      for _ in range(count)]
    def draw(self, canvas, t):
        for i, (x, y, speed, br) in enumerate(self.stars):
            ny = (y + speed*t*8) % 64
            tw = 0.5 + 0.5*math.sin(t*speed*3 + i)
            v = int(br * tw)
            draw_pixel(canvas, int(x), int(ny), v, v, v)


# ============================================================
#            AUSTRIA TIME HELPER + WEATHER
# ============================================================

def get_austria_time():
    now_utc = time.time()
    gm = time.gmtime(now_utc)
    year = gm.tm_year
    d = 31
    while time.gmtime(time.mktime((year,3,d,1,0,0,0,0,0))).tm_wday != 6: d -= 1
    dst_start = time.mktime((year,3,d,1,0,0,0,0,0))
    d = 31
    while time.gmtime(time.mktime((year,10,d,1,0,0,0,0,0))).tm_wday != 6: d -= 1
    dst_end = time.mktime((year,10,d,1,0,0,0,0,0))
    offset = 7200 if dst_start <= now_utc < dst_end else 3600
    return time.gmtime(now_utc + offset)

class WeatherData:
    LAT, LON = 48.2333, 16.4667
    def __init__(self):
        self.temperature = None; self.humidity = None
        self.weather_code = None; self.wind_speed = None
        self.last_fetch = 0; self.fetching = False
    def get_description(self):
        if self.weather_code is None: return "..."
        c = self.weather_code
        if c == 0: return "KLAR"
        elif c <= 3: return "WOLKIG"
        elif c <= 48: return "NEBEL"
        elif c <= 57: return "NIESEL"
        elif c <= 67: return "REGEN"
        elif c <= 77: return "SCHNEE"
        elif c <= 82: return "SCHAUER"
        elif c <= 86: return "SCHNEE"
        elif c >= 95: return "GEWITTER"
        return "?"
    def should_fetch(self):
        return time.time() - self.last_fetch > 300
    def fetch(self):
        if not HAS_URLLIB or self.fetching: return
        self.fetching = True
        def _do():
            try:
                url = (f"https://api.open-meteo.com/v1/forecast?"
                       f"latitude={self.LAT}&longitude={self.LON}"
                       f"&current=temperature_2m,relative_humidity_2m,"
                       f"weather_code,wind_speed_10m&timezone=Europe/Vienna")
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'RGBMatrixGames/1.0')
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    cur = data.get('current', {})
                    self.temperature = cur.get('temperature_2m')
                    self.humidity = cur.get('relative_humidity_2m')
                    self.weather_code = cur.get('weather_code')
                    self.wind_speed = cur.get('wind_speed_10m')
                    self.last_fetch = time.time()
            except Exception: pass
            finally: self.fetching = False
        threading.Thread(target=_do, daemon=True).start()

weather_data = WeatherData()


# ============================================================
#     NEU: SPOTIFY DISPLAY KLASSE
# ============================================================

class SpotifyDisplay:
    def __init__(self):
        self.sp = None
        self.is_playing = False
        self.track_name = ""
        self.artist_name = ""
        self.cover_pixels = None
        self.current_cover_url = None
        self.progress_ms = 0
        self.duration_ms = 1
        self.last_poll = 0
        self.poll_interval = 3.0
        self.polling = False
        self.error_msg = None
        self.lock = threading.Lock()
        self._init_spotify()

    def _init_spotify(self):
        if not HAS_SPOTIPY:
            self.error_msg = "SPOTIPY FEHLT"; return
        if not HAS_PIL:
            self.error_msg = "PIL FEHLT"; return
        cid = os.environ.get('SPOTIPY_CLIENT_ID', '')
        csec = os.environ.get('SPOTIPY_CLIENT_SECRET', '')
        ruri = os.environ.get('SPOTIPY_REDIRECT_URI',
                              'http://localhost:8888/callback')
        if not cid or not csec:
            self.error_msg = "SPOTIFY KEYS FEHLEN"; return
        try:
            auth = SpotifyOAuth(
                client_id=cid, client_secret=csec,
                redirect_uri=ruri,
                scope="user-read-playback-state user-read-currently-playing",
                cache_path=os.path.expanduser("~/.spotify_cache"))
            self.sp = spotipy.Spotify(auth_manager=auth)
            self.error_msg = None
        except Exception:
            self.error_msg = "AUTH FEHLER"

    def _poll_spotify(self):
        if self.sp is None or self.polling: return
        self.polling = True
        def _do():
            try:
                pb = self.sp.current_playback()
                with self.lock:
                    if pb and pb.get('is_playing') and pb.get('item'):
                        item = pb['item']
                        self.is_playing = True
                        self.track_name = item.get('name', '?')
                        arts = item.get('artists', [])
                        self.artist_name = arts[0].get('name','') if arts else ''
                        self.progress_ms = pb.get('progress_ms', 0)
                        self.duration_ms = max(1, item.get('duration_ms', 1))
                        imgs = item.get('album',{}).get('images',[])
                        if imgs:
                            url = imgs[-1]['url']
                            if url != self.current_cover_url:
                                self.current_cover_url = url
                                self._load_cover(url)
                    else:
                        self.is_playing = False
                self.last_poll = time.time()
            except Exception:
                with self.lock:
                    self.error_msg = "NETZWERK ERR"
            finally:
                self.polling = False
        threading.Thread(target=_do, daemon=True).start()

    def _load_cover(self, url):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'RGBMatrixGames/1.0')
            with urllib.request.urlopen(req, timeout=10) as resp:
                img_data = resp.read()
            img = Image.open(_io.BytesIO(img_data)).convert('RGB')
            img = img.resize((64, 64), Image.LANCZOS)
            pixels = []
            for y in range(64):
                row = []
                for x in range(64):
                    r, g, b = img.getpixel((x, y))
                    row.append((int(r*0.85), int(g*0.85), int(b*0.85)))
                pixels.append(row)
            with self.lock:
                self.cover_pixels = pixels
        except Exception: pass

    def should_poll(self):
        return time.time() - self.last_poll >= self.poll_interval

    def draw(self, canvas):
        now = time.time()
        if self.should_poll():
            self._poll_spotify()
        with self.lock:
            playing = self.is_playing
            track = self.track_name
            artist = self.artist_name
            cover = self.cover_pixels
            prog = self.progress_ms
            dur = self.duration_ms
            err = self.error_msg
        if err and not playing:
            for x in range(64): draw_pixel(canvas, x, 0, 0, 30, 0)
            draw_text_centered(canvas, "SPOTIFY", 2, 30, 185, 64)
            p = 0.5+0.5*math.sin(now*3); v = int(180*p)
            draw_text_centered(canvas, err[:15], 25, v, v//3, 0)
            draw_text_centered(canvas, "SETZE ENV", 40, 80, 80, 80)
            draw_text_centered(canvas, "VARIABLEN", 48, 80, 80, 80)
            return False
        if not playing:
            return False
        if cover:
            for y in range(64):
                for x in range(64):
                    r, g, b = cover[y][x]
                    canvas.SetPixel(x, y, r, g, b)
        for y in range(52, 64):
            for x in range(64):
                if cover:
                    cr,cg,cb = cover[y][x]
                    canvas.SetPixel(x, y, cr//4, cg//4, cb//4)
                else:
                    canvas.SetPixel(x, y, 5, 5, 5)
        tt = f"{track}  -  {artist}"
        tw = text_width(tt)
        if tw > 60:
            sx = int(now * 20) % (tw + 64) - 64
            draw_text(canvas, tt, -sx, 53, 255, 255, 255)
        else:
            draw_text_centered(canvas, track[:15], 53, 255, 255, 255)
        if dur > 0:
            frac = min(1.0, prog / dur)
            filled = int(64 * frac)
            for x in range(64):
                if x < filled:
                    h = (now*0.2 + x*0.02) % 1.0
                    r,g,b = hsv_to_rgb(h, 0.8, 0.7)
                    draw_pixel(canvas, x, 62, r, g, b)
                    draw_pixel(canvas, x, 63, r, g, b)
                else:
                    draw_pixel(canvas, x, 62, 20, 20, 20)
                    draw_pixel(canvas, x, 63, 15, 15, 15)
        return True


# ============================================================
#     NEU: AUDIO VISUALIZER KLASSE
# ============================================================

class AudioVisualizer:
    CHUNK = 1024
    RATE = 44100
    NUM_BARS = 64
    MAX_HEIGHT = 60

    def __init__(self):
        self.bars = [0.0] * self.NUM_BARS
        self.peaks = [0.0] * self.NUM_BARS
        self.peak_decay = [0.0] * self.NUM_BARS
        self.smoothed = [0.0] * self.NUM_BARS
        self.stream = None; self.pa = None
        self.error_msg = None
        self.lock = threading.Lock()
        self.color_mode = 0
        self.sensitivity = 1.5
        self.audio_running = False

    def start(self):
        if not HAS_NUMPY:
            self.error_msg = "NUMPY FEHLT"; return
        if not HAS_PYAUDIO:
            self.error_msg = "PYAUDIO FEHLT"; return
        self.audio_running = True
        threading.Thread(target=self._audio_loop, daemon=True).start()

    def stop(self):
        self.audio_running = False; time.sleep(0.1)
        if self.stream:
            try: self.stream.stop_stream(); self.stream.close()
            except: pass
        if self.pa:
            try: self.pa.terminate()
            except: pass
        self.stream = None; self.pa = None

    def _audio_loop(self):
        try:
            self.pa = pyaudio.PyAudio()
            dev_idx = None
            for i in range(self.pa.get_device_count()):
                dev = self.pa.get_device_info_by_index(i)
                nm = dev.get('name','').lower()
                if ('monitor' in nm or 'loopback' in nm) \
                   and dev.get('maxInputChannels',0) > 0:
                    dev_idx = i; break
            self.stream = self.pa.open(
                format=pyaudio.paInt16, channels=1,
                rate=self.RATE, input=True,
                input_device_index=dev_idx,
                frames_per_buffer=self.CHUNK)
            self.error_msg = None
            num_fft = self.CHUNK // 2 + 1
            log_min = math.log10(20); log_max = math.log10(16000)
            edges = [int(10**(log_min+(log_max-log_min)*i/self.NUM_BARS)
                         / (self.RATE/self.CHUNK))
                     for i in range(self.NUM_BARS+1)]
            window = np.hamming(self.CHUNK)
            while self.audio_running:
                try:
                    data = self.stream.read(self.CHUNK,
                                            exception_on_overflow=False)
                    samp = np.frombuffer(data, dtype=np.int16).astype(np.float64)
                    fft = np.abs(np.fft.rfft(samp * window))
                    nb = []
                    for i in range(self.NUM_BARS):
                        lo = max(0, min(edges[i], num_fft-1))
                        hi = max(lo+1, min(edges[i+1], num_fft))
                        mag = np.mean(fft[lo:hi]) if lo < hi else 0
                        norm = mag / 32768.0 * self.sensitivity
                        if norm > 0:
                            db = max(0, 20*math.log10(norm+1e-10)+60)/60.0
                        else:
                            db = 0
                        nb.append(min(1.0, db))
                    with self.lock:
                        for i in range(self.NUM_BARS):
                            if nb[i] > self.smoothed[i]:
                                self.smoothed[i] = self.smoothed[i]*0.3+nb[i]*0.7
                            else:
                                self.smoothed[i] *= 0.85
                            self.bars[i] = self.smoothed[i]
                            if self.bars[i] > self.peaks[i]:
                                self.peaks[i] = self.bars[i]
                                self.peak_decay[i] = 0
                            else:
                                self.peak_decay[i] += 0.015
                                self.peaks[i] = max(0,
                                    self.peaks[i]-self.peak_decay[i]*0.02)
                except IOError: time.sleep(0.01)
        except Exception:
            self.error_msg = "AUDIO FEHLER"

    def draw(self, canvas):
        now = time.time()
        if self.error_msg:
            canvas.Clear()
            p = 0.5+0.5*math.sin(now*3); v = int(200*p)
            draw_text_centered(canvas, "VISUALIZER", 10, v, 0, v)
            draw_text_centered(canvas, self.error_msg, 25, 200, 80, 0)
            draw_text_centered(canvas, "INSTALLIERE", 40, 80, 80, 80)
            draw_text_centered(canvas, "PYAUDIO", 48, 80, 80, 80)
            return
        with self.lock:
            bars = list(self.bars); peaks = list(self.peaks)
        canvas.Clear()
        for i in range(self.NUM_BARS):
            bh = int(bars[i] * self.MAX_HEIGHT)
            pk = int(peaks[i] * self.MAX_HEIGHT)
            if bh < 1 and pk < 1:
                v = int(10+5*math.sin(now*2+i*0.3))
                draw_pixel(canvas, i, 63, v, v, v); continue
            for y in range(bh):
                sy = 63-y; ratio = y/self.MAX_HEIGHT
                if self.color_mode == 0:
                    h = (ratio*0.4+i/self.NUM_BARS*0.6+now*0.1)%1.0
                    r,g,b = hsv_to_rgb(h, 0.9, 0.5+ratio*0.5)
                elif self.color_mode == 1:
                    if ratio<0.3: r,g,b = 200,int(50*ratio/0.3),0
                    elif ratio<0.7:
                        f=(ratio-0.3)/0.4; r,g,b = 255,int(50+200*f),0
                    else:
                        f=(ratio-0.7)/0.3; r,g,b = 255,255,int(200*f)
                elif self.color_mode == 2:
                    if ratio<0.5:
                        f=ratio/0.5; r,g,b = 0,int(80*f),int(150+105*f)
                    else:
                        f=(ratio-0.5)/0.5
                        r,g,b = int(100*f),int(200+55*f),255
                else:
                    if i%2==0:
                        r,g,b = int(255*ratio),0,int(255*(1-ratio*0.5))
                    else:
                        r,g,b = 0,int(255*ratio),int(255*(1-ratio*0.3))
                draw_pixel(canvas, i, sy, r, g, b)
            if pk > 0:
                psy = 63-pk
                draw_pixel(canvas, i, psy, 255, 255, 255)
                if psy+1 < 64:
                    draw_pixel(canvas, i, psy+1, 80, 80, 80)
        names = ["RAINBOW","FEUER","OZEAN","NEON"]
        draw_text(canvas, names[self.color_mode], 1, 1, 40, 40, 50)
        sv = int(self.sensitivity*10)
        draw_text(canvas, f"S{sv}", 50, 1, 40, 40, 50)

# Singleton-Instanz (SpotifyDisplay wird erst nach _apply_spotify_config() erstellt)
audio_visualizer = AudioVisualizer()


# ============================================================
#                      ANIMATIONS
# ============================================================

def animation_flash(duration=0.3, r=255, g=255, b=255):
    start = time.time()
    while time.time()-start < duration:
        canvas.Clear()
        fade = max(0, 1.0-(time.time()-start)/duration)
        cr,cg,cb = int(r*fade),int(g*fade),int(b*fade)
        for x in range(64):
            for y in range(64):
                canvas.SetPixel(x, y, cr, cg, cb)
        matrix.SwapOnVSync(canvas)

def animation_game_over(score, game_color=(255,0,0)):
    particles = ParticleSystem()
    for _ in range(4):
        particles.emit(random.randint(10,54), random.randint(10,54),
                       12, *game_color, spread=35, life=1.5)
    start = time.time(); last_t = start
    while time.time()-start < 3.0:
        now = time.time(); dt = min(now-last_t, 0.05); last_t = now
        canvas.Clear(); particles.update(dt); particles.draw(canvas)
        p = 0.5+0.5*math.sin((now-start)*6)
        draw_text_centered(canvas, "GAME", 20,
            int(game_color[0]*p), int(game_color[1]*p), int(game_color[2]*p))
        draw_text_centered(canvas, "OVER", 28,
            int(game_color[0]*p), int(game_color[1]*p), int(game_color[2]*p))
        draw_text_centered(canvas, "SCORE", 40, 150, 150, 150)
        draw_text_centered(canvas, str(score), 48, 255, 255, 255)
        matrix.SwapOnVSync(canvas); time.sleep(0.03)
    clear_input()
    while running:
        now = time.time(); canvas.Clear()
        p = 0.5+0.5*math.sin(now*4)
        draw_text_centered(canvas, "GAME", 20,
            int(game_color[0]*p), int(game_color[1]*p), int(game_color[2]*p))
        draw_text_centered(canvas, "OVER", 28,
            int(game_color[0]*p), int(game_color[1]*p), int(game_color[2]*p))
        draw_text_centered(canvas, "SCORE", 40, 150, 150, 150)
        draw_text_centered(canvas, str(score), 48, 255, 255, 255)
        if int(now*3)%2: draw_text_centered(canvas, "ESC", 58, 80, 80, 80)
        matrix.SwapOnVSync(canvas)
        if consume_key() is not None: break
        time.sleep(0.05)

def animation_win(text="YOU WIN", color=(0,255,0)):
    clear_input(); particles = ParticleSystem(); start = time.time()
    while running:
        now = time.time(); el = now-start; canvas.Clear()
        if el < 3.0 and random.random() < 0.3:
            particles.emit_burst(random.randint(5,58),
                                 random.randint(5,58), 3, spread=20, life=0.8)
        particles.update(0.03); particles.draw(canvas)
        p = 0.7+0.3*math.sin(el*8)
        cr,cg,cb = int(color[0]*p),int(color[1]*p),int(color[2]*p)
        if len(text) > 8:
            words = text.split(); mid = len(words)//2
            draw_text_centered(canvas, " ".join(words[:mid]), 24, cr, cg, cb)
            draw_text_centered(canvas, " ".join(words[mid:]), 32, cr, cg, cb)
        else:
            draw_text_centered(canvas, text, 28, cr, cg, cb)
        matrix.SwapOnVSync(canvas)
        if el > 1.0 and consume_key() is not None: break
        time.sleep(0.03)

def animation_countdown(count=3):
    for num in range(count, 0, -1):
        start = time.time()
        while time.time()-start < 0.6:
            canvas.Clear()
            fade = max(0, 1.0-(time.time()-start)/0.6)
            v = int(255*fade)
            draw_text_centered(canvas, str(num), 28, v, v, v)
            matrix.SwapOnVSync(canvas); time.sleep(0.03)
    start = time.time()
    while time.time()-start < 0.4:
        canvas.Clear()
        fade = max(0, 1.0-(time.time()-start)/0.4)
        draw_text_centered(canvas, "GO!", 28, 0, int(255*fade), 0)
        matrix.SwapOnVSync(canvas); time.sleep(0.03)

def animation_transition():
    for x in range(0, 64, 4):
        canvas.Clear()
        for wx in range(x):
            for y in range(64):
                h = (wx*0.02+y*0.01)%1.0; r,g,b = hsv_to_rgb(h,1.0,0.3)
                canvas.SetPixel(wx, y, r, g, b)
        matrix.SwapOnVSync(canvas); time.sleep(0.01)
    for x in range(0, 64, 4):
        canvas.Clear()
        for wx in range(x, 64):
            for y in range(64):
                h = (wx*0.02+y*0.01)%1.0
                r,g,b = hsv_to_rgb(h, 1.0, 0.3*(1.0-x/64))
                canvas.SetPixel(wx, y, r, g, b)
        matrix.SwapOnVSync(canvas); time.sleep(0.01)


# ============================================================
#  ENDE TEIL 1 - Weiter mit Teil 2: Snake, Tetris, Pong
# ============================================================
# ============================================================
#  RGB MATRIX GAMES - TEIL 2 von 5
#  Snake, Tetris, Pong (PONG BUG GEFIXT!)
# ============================================================


# ============================================================
#                       SNAKE GAME
# ============================================================

def play_snake(mode):
    GRID = 32
    if mode == 2: MN, MX = 1, 30
    else: MN, MX = 0, 31
    snake = [(16,16),(15,16),(14,16)]
    dir = (1, 0)
    obs = [(10,10),(20,20),(10,20),(20,10),(15,8),(15,24),(8,15),(24,15)] \
          if mode == 2 else []

    def spawn():
        for _ in range(500):
            p = (random.randint(MN+1, MX-1), random.randint(MN+1, MX-1))
            if p not in snake and p not in obs: return p
        for x in range(MN+1, MX):
            for y in range(MN+1, MX):
                if (x,y) not in snake and (x,y) not in obs: return (x,y)
        return (16, 16)

    food = spawn(); score = 0
    speed = 0.13 if mode == 1 else 0.10
    ps = ParticleSystem(); dq = collections.deque(maxlen=4)
    clear_input(); animation_countdown(); clear_input()
    lm = time.time(); lr = time.time()

    while running:
        now = time.time()
        while True:
            k = consume_queue()
            if k is None: break
            if k == '\x1b': return
            eff = dir
            for d in dq: eff = d
            if k == 'w' and eff != (0,1): dq.append((0,-1))
            elif k == 's' and eff != (0,-1): dq.append((0,1))
            elif k == 'a' and eff != (1,0): dq.append((-1,0))
            elif k == 'd' and eff != (-1,0): dq.append((1,0))
        if now - lm >= speed:
            lm = now
            if dq:
                nd = dq.popleft()
                if nd[0] != -dir[0] or nd[1] != -dir[1]: dir = nd
            nx, ny = snake[0][0]+dir[0], snake[0][1]+dir[1]
            if mode == 1: nx %= GRID; ny %= GRID
            elif mode == 2:
                if nx < MN or nx > MX or ny < MN or ny > MX:
                    animation_flash(0.2,255,50,0)
                    animation_game_over(score,(255,80,0)); return
            nh = (nx, ny)
            if nh in snake:
                animation_flash(0.15,255,0,0)
                animation_game_over(score,(0,255,0)); return
            if mode == 2 and nh in obs:
                animation_flash(0.15,255,50,0)
                animation_game_over(score,(255,80,0)); return
            snake.insert(0, nh)
            if nh == food:
                score += 1; speed = max(0.04, speed-0.004)
                ps.emit(food[0]*2+1, food[1]*2+1, 10, 255,50,50,
                        spread=25, life=0.6)
                food = spawn()
            else: snake.pop()
        if now - lr >= 0.016:
            lr = now; canvas.Clear(); ps.update(0.016)
            if mode == 1:
                for i in range(0,64,8):
                    for j in range(64):
                        draw_pixel(canvas,i,j,8,8,8)
                        draw_pixel(canvas,j,i,8,8,8)
            if mode == 2:
                t = now*3
                for i in range(GRID):
                    h = (t*0.1+i*0.04)%1.0; r,g,b = hsv_to_rgb(h,1.0,0.7)
                    draw_block(canvas,i,0,r,g,b)
                    draw_block(canvas,i,31,r,g,b)
                    draw_block(canvas,0,i,r,g,b)
                    draw_block(canvas,31,i,r,g,b)
                pl = 0.5+0.5*math.sin(now*4)
                for ox,oy in obs:
                    v = int(120+135*pl)
                    draw_block(canvas,ox,oy,v,v,v)
            fp = 0.5+0.5*math.sin(now*10); fr = int(200+55*fp)
            fx, fy = food[0]*2, food[1]*2
            for dx in range(-1,4):
                for dy in range(-1,4):
                    if 0<=dx<=1 and 0<=dy<=1: continue
                    draw_pixel(canvas, fx+dx, fy+dy, int(40*fp), 0, 0)
            draw_block(canvas, food[0], food[1], fr, 30, 30)
            for i,(x,y) in enumerate(snake):
                if i == 0:
                    draw_block(canvas,x,y,150,255,150)
                    hx,hy = x*2,y*2
                    if dir==(1,0):
                        draw_pixel(canvas,hx+1,hy,0,0,0)
                        draw_pixel(canvas,hx+1,hy+1,0,0,0)
                    elif dir==(-1,0):
                        draw_pixel(canvas,hx,hy,0,0,0)
                        draw_pixel(canvas,hx,hy+1,0,0,0)
                    elif dir==(0,-1):
                        draw_pixel(canvas,hx,hy,0,0,0)
                        draw_pixel(canvas,hx+1,hy,0,0,0)
                    else:
                        draw_pixel(canvas,hx,hy+1,0,0,0)
                        draw_pixel(canvas,hx+1,hy+1,0,0,0)
                else:
                    tg = i/max(len(snake),1)
                    r,g,b = hsv_to_rgb(0.30+tg*0.35, 0.85, 0.9-tg*0.35)
                    draw_block(canvas,x,y,r,g,b)
            ps.draw(canvas)
            if mode == 2:
                draw_text(canvas,str(score),4,4,255,255,255)
                draw_text(canvas,"ULT",48,4,255,100,0)
            else:
                draw_text(canvas,str(score),2,2,255,255,255)
            matrix.SwapOnVSync(canvas)
        time.sleep(0.005)


# ============================================================
#                       TETRIS GAME
# ============================================================

def play_tetris():
    COLS, ROWS, CELL = 10, 20, 3
    FX, FY = 19, 2
    SHAPES = {
        'I': {'b':[(0,1),(1,1),(2,1),(3,1)],'c':(0,255,255)},
        'O': {'b':[(0,0),(1,0),(0,1),(1,1)],'c':(255,255,0)},
        'T': {'b':[(1,0),(0,1),(1,1),(2,1)],'c':(180,0,255)},
        'S': {'b':[(1,0),(2,0),(0,1),(1,1)],'c':(0,255,0)},
        'Z': {'b':[(0,0),(1,0),(1,1),(2,1)],'c':(255,0,0)},
        'L': {'b':[(2,0),(0,1),(1,1),(2,1)],'c':(255,165,0)},
        'J': {'b':[(0,0),(0,1),(1,1),(2,1)],'c':(0,100,255)},
    }
    bag = []
    def nxt():
        nonlocal bag
        if not bag: bag = list(SHAPES.keys()); random.shuffle(bag)
        return bag.pop()
    def blks(n, r=0):
        bl = list(SHAPES[n]['b'])
        for _ in range(r%4): bl = [(-y,x) for x,y in bl]
        mx = min(x for x,y in bl); my = min(y for x,y in bl)
        return [(x-mx,y-my) for x,y in bl]
    def clr(n): return SHAPES[n]['c']
    board = {}
    cn, nn = nxt(), nxt()
    cr, cx, cy = 0, 3, 0
    sc, lv, lt = 0, 1, 0
    clr_rows = []; cas = 0; CD = 0.35

    def hit(n,r,px,py):
        for bx,by in blks(n,r):
            nx2,ny2 = px+bx, py+by
            if nx2<0 or nx2>=COLS or ny2>=ROWS: return True
            if ny2>=0 and (nx2,ny2) in board: return True
        return False
    def ghy(n,r,px,py):
        g = py
        while not hit(n,r,px,g+1): g+=1
        return g
    def lck(n,r,px,py):
        c = clr(n)
        for bx,by in blks(n,r):
            if py+by >= 0: board[(px+bx,py+by)] = c
    def frows():
        return [y for y in range(ROWS)
                if all((x,y) in board for x in range(COLS))]
    def rrows(rows):
        nonlocal board
        rs = set(rows); nb = {}
        for (bx,by),c in board.items():
            if by not in rs:
                nb[(bx, by+sum(1 for ry in rs if ry>by))] = c
        board = nb
    def dcell(col,row,r,g,b,gh=False):
        px2,py2 = FX+col*CELL, FY+row*CELL
        if gh:
            for d in range(CELL):
                draw_pixel(canvas,px2+d,py2,r,g,b)
                draw_pixel(canvas,px2+d,py2+CELL-1,r,g,b)
            for d in range(CELL):
                draw_pixel(canvas,px2,py2+d,r,g,b)
                draw_pixel(canvas,px2+CELL-1,py2+d,r,g,b)
        else:
            for dx2 in range(CELL):
                for dy2 in range(CELL):
                    if dx2==0 or dy2==0:
                        dr = min(255,int(r*1.3))
                        dg = min(255,int(g*1.3))
                        db = min(255,int(b*1.3))
                    elif dx2==CELL-1 or dy2==CELL-1:
                        dr,dg,db = int(r*0.5),int(g*0.5),int(b*0.5)
                    else:
                        dr,dg,db = r,g,b
                    draw_pixel(canvas,px2+dx2,py2+dy2,dr,dg,db)
    def dborder():
        bx2,by2 = FX-1, FY-1
        bw,bh = COLS*CELL+1, ROWS*CELL+1
        t = time.time()*2
        for i in range(bw+1):
            h = (t+i*0.03)%1.0; r,g,b = hsv_to_rgb(h,0.8,0.6)
            draw_pixel(canvas,bx2+i,by2,r,g,b)
            draw_pixel(canvas,bx2+i,by2+bh,r,g,b)
        for i in range(bh+1):
            h = (t+i*0.02+0.5)%1.0; r,g,b = hsv_to_rgb(h,0.8,0.6)
            draw_pixel(canvas,bx2,by2+i,r,g,b)
            draw_pixel(canvas,bx2+bw,by2+i,r,g,b)
    def dsidebar():
        draw_text(canvas,"NXT",1,2,120,120,120)
        bl2 = blks(nn,0); c2 = clr(nn)
        for bx,by in bl2:
            for dx2 in range(2):
                for dy2 in range(2):
                    draw_pixel(canvas,2+bx*3+dx2,9+by*3+dy2,*c2)
        draw_text(canvas,"SC",1,24,150,150,150)
        s = str(sc)
        draw_text(canvas,s[-4:] if len(s)>4 else s,1,31,255,255,0)
        draw_text(canvas,"LV",1,41,150,150,150)
        draw_text(canvas,str(lv),1,48,0,255,200)
        draw_text(canvas,"LN",1,55,150,150,150)
        draw_text(canvas,str(lt),10,55,200,200,200)

    ps = ParticleSystem()
    clear_input(); animation_countdown(); clear_input()
    ld = time.time(); di = 0.5; lkd = 0.5; lkt = 0
    ilk = False; lkm = 0
    dk = None; ds = 0; dr2 = 0

    while running:
        now = time.time()
        if clr_rows:
            el = now - cas
            if el >= CD:
                rrows(clr_rows); cnt = len(clr_rows); lt += cnt
                sc += [0,100,300,500,800][min(cnt,4)] * lv
                lv = 1 + lt//10
                di = max(0.05, 0.5-(lv-1)*0.045)
                for row in clr_rows:
                    ps.emit(FX+COLS*CELL//2, FY+row*CELL+1,
                            8, 255,255,100, spread=30, life=0.5)
                clr_rows = []
                cn = nn; nn = nxt(); cr,cx,cy = 0,3,0; ilk = False
                if hit(cn,cr,cx,cy):
                    animation_flash(0.2,0,100,255)
                    animation_game_over(sc,(0,150,255)); return
            else:
                canvas.Clear(); dborder()
                fl = int((el/0.07)%2)
                for (bx,by),c in board.items():
                    if by in clr_rows:
                        if fl: dcell(bx,by,255,255,255)
                    else: dcell(bx,by,*c)
                dsidebar(); ps.update(0.03); ps.draw(canvas)
                matrix.SwapOnVSync(canvas); time.sleep(0.03); continue

        k = consume_key()
        if k == '\x1b': return
        dx,rot,hd,sd = 0,False,False,False
        if k == 'a': dx=-1; dk='a'; ds=now; dr2=0
        elif k == 'd': dx=1; dk='d'; ds=now; dr2=0
        elif k in ('w',' '): rot=True
        elif k == 's': sd=True
        elif k == 'e': hd=True
        held = peek_key()
        if dk and held==dk:
            if now-ds>0.17 and now-dr2>0.05:
                dr2=now; dx=-1 if dk=='a' else 1
        elif k is None: dk=None
        if rot:
            nr = (cr+1)%4
            for ox in [0,-1,1,-2,2]:
                if not hit(cn,nr,cx+ox,cy):
                    cr=nr; cx+=ox
                    if ilk: lkm+=1
                    break
        if dx!=0 and not hit(cn,cr,cx+dx,cy):
            cx+=dx
            if ilk: lkm+=1; lkt=now
        if sd and not hit(cn,cr,cx,cy+1):
            cy+=1; sc+=1; ld=now; ilk=False
        if hd:
            gy2 = ghy(cn,cr,cx,cy); sc+=(gy2-cy)*2; cy=gy2
            lck(cn,cr,cx,cy)
            c = clr(cn)
            for bx,by in blks(cn,cr):
                ps.emit(FX+(cx+bx)*CELL+1, FY+(cy+by)*CELL+1,
                        3, *c, spread=15, life=0.3)
            fl = frows()
            if fl: clr_rows=fl; cas=now; ld=now; continue
            cn=nn; nn=nxt(); cr,cx,cy=0,3,0; ilk=False; ld=now
            if hit(cn,cr,cx,cy):
                animation_flash(0.2,0,100,255)
                animation_game_over(sc,(0,150,255)); return
            continue
        if now-ld >= di:
            ld = now
            if not hit(cn,cr,cx,cy+1): cy+=1; ilk=False
            else:
                if not ilk: ilk=True; lkt=now; lkm=0
                elif now-lkt>=lkd or lkm>=10:
                    lck(cn,cr,cx,cy); fl=frows()
                    if fl: clr_rows=fl; cas=now; continue
                    cn=nn; nn=nxt(); cr,cx,cy=0,3,0; ilk=False
                    if hit(cn,cr,cx,cy):
                        animation_flash(0.2,0,100,255)
                        animation_game_over(sc,(0,150,255)); return
        canvas.Clear(); dborder()
        for col in range(COLS+1):
            for row in range(ROWS):
                draw_pixel(canvas,FX+col*CELL,FY+row*CELL,15,15,15)
        for row in range(ROWS+1):
            for col in range(COLS):
                draw_pixel(canvas,FX+col*CELL,FY+row*CELL,15,15,15)
        for (bx,by),c in board.items(): dcell(bx,by,*c)
        gy2 = ghy(cn,cr,cx,cy); c = clr(cn)
        if gy2 != cy:
            for bx,by in blks(cn,cr):
                gx2,gy3 = cx+bx,gy2+by
                if gy3>=0:
                    dcell(gx2,gy3,c[0]//6,c[1]//6,c[2]//6,gh=True)
        for bx,by in blks(cn,cr):
            if cy+by>=0: dcell(cx+bx,cy+by,*c)
        dsidebar(); ps.update(0.03); ps.draw(canvas)
        matrix.SwapOnVSync(canvas); time.sleep(0.03)


# ============================================================
#                    PONG GAME 
# ============================================================

def play_pong(difficulty=2):
    # Schwierigkeitsstufen: 1=EINFACH, 2=MITTEL, 3=SCHWER
    if difficulty == 1:
        PH, PW, WIN = 12, 2, 5
        PS = 2.8; bs = 1.0
    elif difficulty == 3:
        PH, PW, WIN = 8, 2, 7
        PS = 2.2; bs = 1.6
    else:
        PH, PW, WIN = 10, 2, 7
        PS = 2.5; bs = 1.3
    p1, p2 = 27.0, 27.0
    bx, by = 32.0, 32.0
    bvx = bs*random.choice([-1,1]); bvy = random.uniform(-0.5,0.5)
    s1, s2, rl = 0, 0, 0
    trail = collections.deque(maxlen=10)
    ps = ParticleSystem()
    srv = True; st = time.time()
    clear_input(); lt = time.time()

    while running:
        now = time.time(); dt = min(now-lt, 0.05); lt = now

        # Alle Keys aus der Queue verarbeiten (Multiplayer)
        while True:
            k = consume_queue()
            if k is None: break
            if k == '\x1b': return
            # Spieler 1 (links): W/S
            if k in ('w', 'W'): p1 = max(0, p1-PS*2)
            elif k in ('s', 'S'): p1 = min(64-PH, p1+PS*2)
            # Spieler 2 (rechts): Pfeiltasten
            elif k == 'UP': p2 = max(0, p2-PS*2)
            elif k == 'DOWN': p2 = min(64-PH, p2+PS*2)

        # Gehaltene Tasten fuer sanfte Bewegung
        held = peek_key()
        if held in ('w', 'W'): p1 = max(0, p1-PS)
        elif held in ('s', 'S'): p1 = min(64-PH, p1+PS)
        elif held == 'UP': p2 = max(0, p2-PS)
        elif held == 'DOWN': p2 = min(64-PH, p2+PS)

        if srv:
            if now-st > 1.0: srv = False
        else:
            sm = 1.0+rl*0.02
            bx += bvx*sm; by += bvy*sm

            if by <= 0:
                by = 0; bvy = abs(bvy)
                ps.emit(int(bx),0,4,100,100,255,spread=15,life=0.3)
            elif by >= 63:
                by = 63; bvy = -abs(bvy)
                ps.emit(int(bx),63,4,100,100,255,spread=15,life=0.3)

            if bx <= PW+1 and bvx < 0 and p1-1 <= by <= p1+PH+1:
                hp = (by-p1)/PH; a = (hp-0.5)*2.5
                sp = math.sqrt(bvx**2+bvy**2)*1.05
                bvx = abs(sp*math.cos(a)); bvy = sp*math.sin(a)
                bx = PW+2; rl += 1
                ps.emit(int(bx),int(by),6,0,255,100,spread=20,life=0.4)

            if bx >= 64-PW-2 and bvx > 0 and p2-1 <= by <= p2+PH+1:
                hp = (by-p2)/PH; a = (hp-0.5)*2.5
                sp = math.sqrt(bvx**2+bvy**2)*1.05
                bvx = -abs(sp*math.cos(a)); bvy = sp*math.sin(a)
                bx = 64-PW-3; rl += 1
                ps.emit(int(bx),int(by),6,255,100,100,spread=20,life=0.4)

            if bx < -4:
                s2 += 1
                ps.emit(2,int(by),15,255,0,0,spread=35,life=0.8)
                bx,by = 32.0,32.0; bvx = bs
                bvy = random.uniform(-0.5,0.5)
                rl = 0; srv = True; st = now; trail.clear()
            elif bx > 68:
                s1 += 1
                ps.emit(62,int(by),15,0,255,0,spread=35,life=0.8)
                bx,by = 32.0,32.0; bvx = -bs
                bvy = random.uniform(-0.5,0.5)
                rl = 0; srv = True; st = now; trail.clear()

            if s1 >= WIN:
                animation_win("YOU WIN!",(0,255,0)); return
            elif s2 >= WIN:
                animation_game_over(s1,(255,0,0)); return

            trail.append((bx,by))

        canvas.Clear()

        # Mittellinie
        for y in range(0,64,4):
            for d in range(2):
                draw_pixel(canvas,31,y+d,30,30,30)
                draw_pixel(canvas,32,y+d,30,30,30)

        # Ball-Trail
        for i,(tx,ty) in enumerate(trail):
            f = (i+1)/max(len(trail),1); v = int(60*f)
            draw_pixel(canvas,int(tx),int(ty),v,v,v)

        # Paddles
        for i in range(PH):
            cd = abs(i-PH/2)/(PH/2); br = 1.0-cd*0.4
            for j in range(PW):
                draw_pixel(canvas, j, int(p1)+i,
                           int(50*br), int(255*br), 0)
                draw_pixel(canvas, 62+j, int(p2)+i,
                           int(255*br), 0, int(50*br))

        # Ball + Glow
        bxi,byi = int(bx),int(by)
        for ddx in range(-2,3):
            for ddy in range(-2,3):
                d = abs(ddx)+abs(ddy)
                if 0 < d <= 2:
                    draw_pixel(canvas, bxi+ddx, byi+ddy,
                               int(60/d), int(60/d), int(60/d))
        draw_pixel(canvas,bxi,byi,255,255,255)
        draw_pixel(canvas,bxi+1,byi,200,200,200)
        draw_pixel(canvas,bxi,byi+1,200,200,200)
        draw_pixel(canvas,bxi+1,byi+1,180,180,180)

        ps.update(dt); ps.draw(canvas)

        # Score Text
        draw_text(canvas,str(s1),18,2,0,255,0)
        draw_text(canvas,str(s2),42,2,255,0,0)

        # === HIER WAR DER BUG! ===
        # ALT (KAPUTT): draw_pixel(canvas,10+i*3,2,(0,200,0) if i<s1 else (30,30,30))
        # NEU (GEFIXT): Separate r,g,b Werte
        for i in range(WIN):
            if i < s1:
                draw_pixel(canvas, 10+i*3, 2, 0, 200, 0)
            else:
                draw_pixel(canvas, 10+i*3, 2, 30, 30, 30)
            if i < s2:
                draw_pixel(canvas, 64-10-i*3, 2, 200, 0, 0)
            else:
                draw_pixel(canvas, 64-10-i*3, 2, 30, 30, 30)

        # Rally Counter
        if rl > 2:
            pl = 0.5+0.5*math.sin(now*6); v = int(180*pl)
            draw_text_centered(canvas, str(rl), 58, v, v, 0)

        # Serve Countdown
        if srv:
            rem = max(0, 1.0-(now-st))
            if rem > 0:
                draw_text_centered(canvas,
                    str(min(3, int(rem*3)+1)), 28, 255, 255, 255)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#  ENDE TEIL 2 - Weiter mit Teil 3: DVD, Analog, Digital, Wetter
# ============================================================
# ============================================================
#  RGB MATRIX GAMES - TEIL 3 von 5
#  DVD Bounce, Analoge Uhr, Digitale Uhr, Wetter-Anzeige
# ============================================================


# ============================================================
#              DVD BOUNCING LOGO SCREENSAVER
# ============================================================

def play_dvd_bounce():
    LOGO_W = 13
    LOGO_H = 7
    x = random.uniform(5, 45)
    y = random.uniform(5, 45)
    vx = random.choice([-1.0, 1.0]) * 0.6
    vy = random.choice([-1.0, 1.0]) * 0.45
    hue = random.random()
    corner_count = 0
    particles = ParticleSystem()
    total_bounces = 0
    trail = collections.deque(maxlen=25)
    clear_input()
    last_time = time.time()

    while running:
        now = time.time()
        dt = min(now - last_time, 0.05)
        last_time = now

        k = consume_key()
        if k == '\x1b': return

        x += vx * dt * 28
        y += vy * dt * 28
        hit_x = False
        hit_y = False

        if x <= 0:
            x = 0; vx = abs(vx); hit_x = True
        elif x + LOGO_W >= 64:
            x = 64 - LOGO_W; vx = -abs(vx); hit_x = True
        if y <= 0:
            y = 0; vy = abs(vy); hit_y = True
        elif y + LOGO_H >= 64:
            y = 64 - LOGO_H; vy = -abs(vy); hit_y = True

        if hit_x or hit_y:
            hue = (hue + 0.15 + random.uniform(0, 0.1)) % 1.0
            total_bounces += 1
            if hit_x:
                px_hit = 0 if vx > 0 else 63
                py_hit = int(y + LOGO_H / 2)
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                particles.emit(px_hit, py_hit, 5, r, g, b,
                               spread=15, life=0.4)
            if hit_y:
                px_hit = int(x + LOGO_W / 2)
                py_hit = 0 if vy > 0 else 63
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                particles.emit(px_hit, py_hit, 5, r, g, b,
                               spread=15, life=0.4)

        if hit_x and hit_y:
            corner_count += 1
            ccx = 0 if vx > 0 else 63
            ccy = 0 if vy > 0 else 63
            particles.emit_burst(ccx, ccy, 25, spread=40, life=1.2)
            animation_flash(0.15, 255, 255, 255)

        trail.append((x + LOGO_W / 2, y + LOGO_H / 2, hue))

        canvas.Clear()

        for gx in range(0, 64, 4):
            for gy in range(0, 64, 4):
                v = int(3 + 2 * math.sin(now*0.5 + gx*0.05 + gy*0.05))
                draw_pixel(canvas, gx, gy, v, v, v)

        for i, (tx, ty, th) in enumerate(trail):
            fade = (i + 1) / len(trail)
            r, g, b = hsv_to_rgb(th, 1.0, 0.3 * fade)
            draw_pixel(canvas, int(tx), int(ty), r, g, b)
            draw_pixel(canvas, int(tx)+1, int(ty), r//2, g//2, b//2)

        particles.update(dt)
        particles.draw(canvas)

        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        ix, iy = int(x), int(y)

        for ddx in range(-1, LOGO_W + 1):
            for ddy in range(-1, LOGO_H + 1):
                draw_pixel(canvas, ix+ddx, iy+ddy, r//8, g//8, b//8)

        draw_text(canvas, "DVD", ix + 1, iy + 1, r, g, b)

        if total_bounces > 0:
            draw_text(canvas, str(total_bounces), 50, 58, 40, 40, 40)

        if corner_count > 0:
            pulse = 0.5 + 0.5 * math.sin(now * 4)
            v = int(200 * pulse)
            draw_text(canvas, str(corner_count), 2, 58, v, v, 0)
            draw_pixel(canvas,
                       2 + text_width(str(corner_count)) + 2, 59,
                       v, v, 0)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#                    ANALOGE UHR
# ============================================================

def show_analog_clock():
    CX, CY = 31, 28
    RADIUS = 26
    clear_input()

    while running:
        now = time.time()
        at = get_austria_time()
        hours = at.tm_hour
        minutes = at.tm_min
        seconds = at.tm_sec

        frac_sec = now % 1.0
        sec_angle = (seconds + frac_sec) / 60.0 * 2*math.pi - math.pi/2
        min_angle = (minutes + seconds/60.0) / 60.0 * 2*math.pi - math.pi/2
        hr12 = hours % 12
        hr_angle = (hr12 + minutes/60.0) / 12.0 * 2*math.pi - math.pi/2

        k = consume_key()
        if k == '\x1b': return

        canvas.Clear()

        # Rainbow Rand
        for i in range(60):
            angle = i / 60.0 * 2*math.pi - math.pi/2
            rx = int(CX + (RADIUS+2) * math.cos(angle))
            ry = int(CY + (RADIUS+2) * math.sin(angle))
            h = (now*0.1 + i/60.0) % 1.0
            r, g, b = hsv_to_rgb(h, 0.7, 0.25)
            draw_pixel(canvas, rx, ry, r, g, b)

        # Zifferblatt-Kreis
        draw_circle(canvas, CX, CY, RADIUS, 40, 40, 60)

        # Stunden-Markierungen
        for i in range(12):
            angle = i / 12.0 * 2*math.pi - math.pi/2
            for d in range(3):
                dist = RADIUS - 1 - d
                mx = int(CX + dist * math.cos(angle))
                my = int(CY + dist * math.sin(angle))
                if i % 3 == 0:
                    draw_pixel(canvas, mx, my, 200, 200, 255)
                else:
                    if d < 2:
                        draw_pixel(canvas, mx, my, 100, 100, 140)

        # 12, 3, 6, 9 Zahlen
        draw_text(canvas, "12", CX-3, CY-RADIUS+4, 150, 150, 200)
        draw_text(canvas, "3", CX+RADIUS-6, CY-2, 150, 150, 200)
        draw_text(canvas, "6", CX-1, CY+RADIUS-8, 150, 150, 200)
        draw_text(canvas, "9", CX-RADIUS+3, CY-2, 150, 150, 200)

        # Minute-Ticks
        for i in range(60):
            if i % 5 == 0: continue
            angle = i / 60.0 * 2*math.pi - math.pi/2
            mx = int(CX + (RADIUS-1) * math.cos(angle))
            my = int(CY + (RADIUS-1) * math.sin(angle))
            draw_pixel(canvas, mx, my, 35, 35, 50)

        # Stundenzeiger (dick, kurz)
        hr_len = RADIUS * 0.5
        hx = int(CX + hr_len * math.cos(hr_angle))
        hy = int(CY + hr_len * math.sin(hr_angle))
        draw_line(canvas, CX, CY, hx, hy, 220, 220, 255)
        hnx = -math.sin(hr_angle)
        hny = math.cos(hr_angle)
        draw_line(canvas, int(CX+hnx), int(CY+hny),
                  int(hx+hnx), int(hy+hny), 180, 180, 220)
        draw_line(canvas, int(CX-hnx), int(CY-hny),
                  int(hx-hnx), int(hy-hny), 180, 180, 220)

        # Minutenzeiger (mittel, laenger)
        min_len = RADIUS * 0.75
        mx_end = int(CX + min_len * math.cos(min_angle))
        my_end = int(CY + min_len * math.sin(min_angle))
        draw_line(canvas, CX, CY, mx_end, my_end, 180, 200, 255)
        draw_line(canvas, CX+1, CY, mx_end+1, my_end, 120, 140, 180)

        # Sekundenzeiger mit Schweif
        sec_len = RADIUS * 0.85
        for trail_i in range(5):
            trail_sec = seconds + frac_sec - trail_i * 0.3
            trail_angle = trail_sec / 60.0 * 2*math.pi - math.pi/2
            trail_len = sec_len * (1.0 - trail_i * 0.05)
            tx = int(CX + trail_len * math.cos(trail_angle))
            ty = int(CY + trail_len * math.sin(trail_angle))
            fade = int(80 * (1.0 - trail_i / 5.0))
            draw_pixel(canvas, tx, ty, fade, 0, 0)

        sx = int(CX + sec_len * math.cos(sec_angle))
        sy = int(CY + sec_len * math.sin(sec_angle))
        draw_line(canvas, CX, CY, sx, sy, 255, 50, 50)

        tail_len = RADIUS * 0.15
        tax = int(CX - tail_len * math.cos(sec_angle))
        tay = int(CY - tail_len * math.sin(sec_angle))
        draw_line(canvas, CX, CY, tax, tay, 200, 30, 30)

        # Mittelpunkt pulsierend
        pulse = 0.7 + 0.3 * math.sin(now * 4)
        v = int(255 * pulse)
        draw_filled_circle(canvas, CX, CY, 2, v, v//3, v//3)

        # Datum unten
        date_str = f"{at.tm_mday:02d}.{at.tm_mon:02d}"
        draw_text_centered(canvas, date_str, 58, 80, 80, 120)

        # 24h Anzeige oben
        time_str = f"{hours:02d}:{minutes:02d}"
        draw_text_centered(canvas, time_str, 1, 60, 60, 80)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)


# ============================================================
#                    DIGITALE UHR
# ============================================================

def show_digital_clock():
    WOCHENTAGE = ["MO", "DI", "MI", "DO", "FR", "SA", "SO"]
    clear_input()
    if weather_data.should_fetch():
        weather_data.fetch()

    while running:
        now = time.time()
        at = get_austria_time()
        hours = at.tm_hour
        minutes = at.tm_min
        seconds = at.tm_sec
        frac = now % 1.0

        k = consume_key()
        if k == '\x1b': return

        if weather_data.should_fetch():
            weather_data.fetch()

        canvas.Clear()

        # Subtiler Hintergrund
        for gx in range(0, 64, 2):
            for gy in range(0, 64, 2):
                wave = math.sin(now*0.3 + gx*0.08 + gy*0.06) * 0.5 + 0.5
                v = int(4 * wave)
                draw_pixel(canvas, gx, gy, v, v, v + 1)

        # Wochentag
        wday = at.tm_wday
        wday_str = WOCHENTAGE[wday] if wday < 7 else "??"
        draw_text_centered(canvas, wday_str, 2, 80, 80, 120)

        # Rainbow Trennlinie
        for x in range(10, 54):
            h = (now*0.3 + x*0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.8, 0.3)
            draw_pixel(canvas, x, 9, r, g, b)

        # Grosse Uhrzeit
        time_str = f"{hours:02d}:{minutes:02d}"
        tw = big_time_width(time_str)
        tx = (64 - tw) // 2

        # Stunden
        h_str = f"{hours:02d}"
        draw_big_digit(canvas, h_str[0], tx, 13, 0, 200, 255)
        draw_big_digit(canvas, h_str[1], tx + 6, 13, 0, 200, 255)

        # Blinkender Doppelpunkt
        if frac < 0.5:
            draw_pixel(canvas, tx + 13, 15, 0, 200, 255)
            draw_pixel(canvas, tx + 13, 17, 0, 200, 255)

        # Minuten
        m_str = f"{minutes:02d}"
        draw_big_digit(canvas, m_str[0], tx + 16, 13, 0, 200, 255)
        draw_big_digit(canvas, m_str[1], tx + 22, 13, 0, 200, 255)

        # Sekunden klein rechts
        s_str = f"{seconds:02d}"
        draw_text(canvas, s_str, tx + 29, 17, 100, 150, 200)

        # Sekunden-Fortschrittsbalken
        bar_y = 23
        bar_width = 44
        bar_x = 10
        progress = (seconds + frac) / 60.0
        filled = int(bar_width * progress)

        for bx in range(bar_width):
            draw_pixel(canvas, bar_x + bx, bar_y, 20, 20, 30)
        for bx in range(filled):
            h = (bx / bar_width + now * 0.2) % 1.0
            r, g, b = hsv_to_rgb(h, 0.9, 0.7)
            draw_pixel(canvas, bar_x + bx, bar_y, r, g, b)

        # Trennlinie
        for x in range(10, 54):
            h = (now*0.3 + x*0.02 + 0.5) % 1.0
            r, g, b = hsv_to_rgb(h, 0.8, 0.25)
            draw_pixel(canvas, x, 26, r, g, b)

        # Datum
        date_str = f"{at.tm_mday:02d}.{at.tm_mon:02d}.{at.tm_year}"
        draw_text_centered(canvas, date_str, 30, 120, 120, 160)

        # Wetter-Info
        if weather_data.temperature is not None:
            for x in range(10, 54):
                draw_pixel(canvas, x, 37, 30, 30, 40)

            temp = weather_data.temperature
            temp_str = f"{temp:.0f}C"
            if temp <= 0: tr, tg, tb = 100, 150, 255
            elif temp <= 10: tr, tg, tb = 0, 200, 200
            elif temp <= 20: tr, tg, tb = 0, 255, 100
            elif temp <= 30: tr, tg, tb = 255, 200, 0
            else: tr, tg, tb = 255, 50, 0
            draw_text(canvas, temp_str, 3, 40, tr, tg, tb)

            desc = weather_data.get_description()
            draw_text(canvas, desc, 24, 40, 150, 150, 150)

            if weather_data.humidity is not None:
                hum_str = f"{int(weather_data.humidity)}%"
                draw_text(canvas, hum_str, 3, 48, 80, 130, 200)
            if weather_data.wind_speed is not None:
                wind_str = f"{weather_data.wind_speed:.0f}KMH"
                draw_text(canvas, wind_str, 28, 48, 100, 180, 100)
        else:
            dots = "." * (int(now * 2) % 4)
            draw_text_centered(canvas, "WETTER" + dots, 42, 60, 60, 60)

        # STADLAU unten
        draw_text_centered(canvas, "STADLAU", 56, 50, 50, 70)

        # Eck-Dekoration
        pulse = 0.5 + 0.5 * math.sin(now * 3)
        v = int(40 * pulse)
        draw_pixel(canvas, 1, 1, v, v, v)
        draw_pixel(canvas, 62, 1, v, v, v)
        draw_pixel(canvas, 1, 62, v, v, v)
        draw_pixel(canvas, 62, 62, v, v, v)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)


# ============================================================
#               WETTER-ANZEIGE STADLAU
# ============================================================

def show_weather():
    def draw_sun(cx, cy, t, size=8):
        draw_filled_circle(canvas, cx, cy, size//3, 255, 220, 50)
        for i in range(8):
            angle = t*0.5 + i*math.pi/4
            x1 = int(cx + (size//2)*math.cos(angle))
            y1 = int(cy + (size//2)*math.sin(angle))
            x2 = int(cx + size*math.cos(angle))
            y2 = int(cy + size*math.sin(angle))
            pulse = 0.7 + 0.3*math.sin(t*3 + i)
            draw_line(canvas, x1, y1, x2, y2,
                      int(255*pulse), int(200*pulse), 0)

    def draw_cloud(cx, cy, size=6):
        draw_filled_circle(canvas, cx-size//3, cy, size//2,
                           150, 150, 170)
        draw_filled_circle(canvas, cx+size//3, cy, size//2,
                           150, 150, 170)
        draw_filled_circle(canvas, cx, cy-size//3, size//2,
                           180, 180, 200)
        draw_rect(canvas, cx-size//2, cy, size, size//3,
                  140, 140, 160)

    def draw_rain(cx, cy, t, count=5):
        for i in range(count):
            rx = cx - 4 + i*2
            ry_offset = (t*20 + i*7) % 12
            ry = int(cy + ry_offset)
            draw_pixel(canvas, rx, ry, 80, 120, 255)
            draw_pixel(canvas, rx, ry+1, 50, 80, 200)

    def draw_snow(cx, cy, t, count=6):
        for i in range(count):
            sx = cx - 5 + (i*3 + int(t*2)) % 10
            sy_offset = (t*8 + i*5) % 14
            sy = int(cy + sy_offset)
            wobble = int(math.sin(t*2 + i) * 1.5)
            draw_pixel(canvas, sx + wobble, sy, 200, 200, 255)

    def draw_lightning(cx, cy, t):
        if math.sin(t*1.5) > 0.95:
            draw_line(canvas, cx, cy, cx-2, cy+4, 255, 255, 100)
            draw_line(canvas, cx-2, cy+4, cx+1, cy+5, 255, 255, 100)
            draw_line(canvas, cx+1, cy+5, cx-1, cy+9, 255, 255, 100)
            for gx in range(64):
                for gy in range(64):
                    draw_pixel(canvas, gx, gy, 15, 15, 20)

    def draw_fog(t):
        for y in range(0, 64, 3):
            offset = int(math.sin(t*0.5 + y*0.1) * 5)
            for x in range(64):
                if (x + offset) % 6 < 3:
                    v = int(20 + 10*math.sin(t + x*0.1))
                    draw_pixel(canvas, x, y, v, v, v+5)

    clear_input()
    if weather_data.should_fetch():
        weather_data.fetch()

    while running:
        now = time.time()
        t = now

        k = consume_key()
        if k == '\x1b': return

        if weather_data.should_fetch():
            weather_data.fetch()

        canvas.Clear()

        # Header: STADLAU
        for x in range(64):
            h = (now*0.2 + x*0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.6, 0.15)
            draw_pixel(canvas, x, 0, r, g, b)
            draw_pixel(canvas, x, 7, r, g, b)
        draw_text_centered(canvas, "STADLAU", 1, 200, 200, 255)

        if weather_data.temperature is not None:
            code = weather_data.weather_code \
                   if weather_data.weather_code is not None else 0
            icon_cx, icon_cy = 16, 20

            if code == 0:
                draw_sun(icon_cx, icon_cy, t, 10)
            elif code <= 3:
                if code == 1:
                    draw_sun(icon_cx+4, icon_cy-2, t, 6)
                draw_cloud(icon_cx-2, icon_cy+2, 6)
                if code == 3:
                    draw_cloud(icon_cx+4, icon_cy, 5)
            elif code <= 48:
                draw_cloud(icon_cx, icon_cy, 5)
                draw_fog(t)
            elif code <= 67:
                draw_cloud(icon_cx, icon_cy-2, 6)
                intensity = 3 if code <= 57 else 6
                draw_rain(icon_cx, icon_cy+3, t, intensity)
            elif code <= 77:
                draw_cloud(icon_cx, icon_cy-2, 6)
                draw_snow(icon_cx, icon_cy+3, t, 8)
            elif code <= 86:
                draw_cloud(icon_cx, icon_cy-2, 7)
                draw_rain(icon_cx, icon_cy+3, t, 8)
            elif code >= 95:
                draw_cloud(icon_cx, icon_cy-2, 7)
                draw_rain(icon_cx, icon_cy+3, t, 5)
                draw_lightning(icon_cx+2, icon_cy+2, t)

            # Grosse Temperatur rechts
            temp = weather_data.temperature
            temp_str = f"{temp:.0f}"
            if temp <= -5: tr, tg, tb = 80, 100, 255
            elif temp <= 0: tr, tg, tb = 100, 150, 255
            elif temp <= 10: tr, tg, tb = 0, 200, 200
            elif temp <= 20: tr, tg, tb = 0, 255, 100
            elif temp <= 25: tr, tg, tb = 200, 255, 0
            elif temp <= 30: tr, tg, tb = 255, 200, 0
            else: tr, tg, tb = 255, 50, 0

            tx = 36
            for ch in temp_str:
                if ch == '-':
                    draw_rect(canvas, tx, 18, 4, 1, tr, tg, tb)
                    tx += 5
                elif ch in BIG_DIGITS:
                    draw_big_digit(canvas, ch, tx, 14, tr, tg, tb)
                    tx += 6

            # Grad-Symbol
            draw_pixel(canvas, tx+1, 14, tr, tg, tb)
            draw_pixel(canvas, tx+2, 13, tr, tg, tb)
            draw_pixel(canvas, tx+3, 14, tr, tg, tb)
            draw_pixel(canvas, tx+2, 15, tr, tg, tb)
            draw_text(canvas, "C", tx+5, 16, tr, tg, tb)

            # Wetter-Beschreibung
            desc = weather_data.get_description()
            draw_text_centered(canvas, desc, 30, 180, 180, 200)

            # Trennlinie
            for x in range(8, 56):
                h = (now*0.2 + x*0.03) % 1.0
                r, g, b = hsv_to_rgb(h, 0.5, 0.2)
                draw_pixel(canvas, x, 37, r, g, b)

            # Luftfeuchtigkeit
            if weather_data.humidity is not None:
                draw_pixel(canvas, 4, 41, 80, 120, 255)
                draw_pixel(canvas, 3, 42, 80, 120, 255)
                draw_pixel(canvas, 5, 42, 80, 120, 255)
                draw_pixel(canvas, 4, 43, 80, 120, 255)
                hum_str = f"{int(weather_data.humidity)}%"
                draw_text(canvas, hum_str, 8, 40, 100, 160, 255)

            # Wind
            if weather_data.wind_speed is not None:
                for i in range(4):
                    wx = 4 + i*2
                    wy = 50 + int(math.sin(now*3 + i) * 0.8)
                    draw_pixel(canvas, wx, wy, 100, 200, 100)
                wind_str = f"{weather_data.wind_speed:.0f}KMH"
                draw_text(canvas, wind_str, 14, 48, 100, 200, 100)

            # Uhrzeit unten
            at = get_austria_time()
            time_str = f"{at.tm_hour:02d}:{at.tm_min:02d}"
            draw_text_centered(canvas, time_str, 56, 80, 80, 120)

        else:
            # Lade-Animation
            draw_text_centered(canvas, "LADE", 20, 100, 100, 150)
            draw_text_centered(canvas, "WETTER", 28, 100, 100, 150)
            dots = int(now * 3) % 4
            for i in range(dots):
                draw_pixel(canvas, 28 + i*4, 38, 150, 150, 200)
            spinner_angle = now * 4
            spx = int(32 + 6*math.cos(spinner_angle))
            spy = int(48 + 6*math.sin(spinner_angle))
            draw_pixel(canvas, spx, spy, 200, 200, 255)
            draw_pixel(canvas, spx+1, spy, 150, 150, 200)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.05)


# ============================================================
#  ENDE TEIL 3 - Weiter mit Teil 4: Breakout, Flappy, Life,
#                Reaction, Maze
# ============================================================
# ============================================================
#  RGB MATRIX GAMES - TEIL 4 von 5
#  Breakout, Flappy Bird, Game of Life, Reaction Time, Maze
# ============================================================


# ============================================================
#                     BREAKOUT GAME
# ============================================================

def play_breakout(difficulty=2):
    COLS_B = 10
    ROWS_B = 6
    BRICK_W = 6
    BRICK_H = 3
    BRICK_OFFSET_X = 2
    BRICK_OFFSET_Y = 6
    # Schwierigkeitsstufen: 1=EINFACH, 2=MITTEL, 3=SCHWER
    if difficulty == 1:
        PADDLE_W = 14
        lives = 5
        start_speed = 1.0
    elif difficulty == 3:
        PADDLE_W = 8
        lives = 2
        start_speed = 1.5
    else:
        PADDLE_W = 10
        lives = 3
        start_speed = 1.2
    PADDLE_H = 2
    PADDLE_Y = 60

    ROW_COLORS = [
        (255, 50, 50),
        (255, 150, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 150, 255),
        (180, 0, 255),
    ]

    level = 1
    score = 0
    particles = ParticleSystem()

    def create_bricks():
        bricks = {}
        for row in range(ROWS_B):
            for col in range(COLS_B):
                if level > 1 and random.random() < 0.1 * (level - 1):
                    continue
                color = ROW_COLORS[row % len(ROW_COLORS)]
                bricks[(col, row)] = color
        return bricks

    bricks = create_bricks()
    ball_x, ball_y = 32.0, 55.0
    ball_speed = start_speed + level * 0.1
    angle = random.uniform(-0.8, 0.8) - math.pi / 2
    ball_vx = ball_speed * math.cos(angle)
    ball_vy = ball_speed * math.sin(angle)
    if ball_vy > -0.3:
        ball_vy = -0.8
    paddle_x = 27.0
    ball_trail = collections.deque(maxlen=8)
    serving = True

    clear_input()
    animation_countdown()
    clear_input()
    last_time = time.time()

    while running:
        now = time.time()
        dt = min(now - last_time, 0.05)
        last_time = now

        k = consume_key()
        if k == '\x1b': return

        pad_speed = 2.5
        if k == 'a':
            paddle_x = max(0, paddle_x - pad_speed * 3)
        elif k == 'd':
            paddle_x = min(64 - PADDLE_W, paddle_x + pad_speed * 3)
        held = peek_key()
        if held == 'a':
            paddle_x = max(0, paddle_x - pad_speed)
        elif held == 'd':
            paddle_x = min(64 - PADDLE_W, paddle_x + pad_speed)

        if serving:
            ball_x = paddle_x + PADDLE_W / 2
            ball_y = PADDLE_Y - 2
            if k in ('w', ' ', 's'):
                serving = False
                ball_vy = -ball_speed
                ball_vx = random.uniform(-0.5, 0.5)

            canvas.Clear()
            for (col, row), color in bricks.items():
                bx = BRICK_OFFSET_X + col * BRICK_W
                by = BRICK_OFFSET_Y + row * BRICK_H
                draw_rect(canvas, bx, by, BRICK_W-1, BRICK_H-1, *color)
                for ddx in range(BRICK_W - 1):
                    draw_pixel(canvas, bx+ddx, by,
                               min(255, int(color[0]*1.4)),
                               min(255, int(color[1]*1.4)),
                               min(255, int(color[2]*1.4)))
                for ddy in range(BRICK_H - 1):
                    draw_pixel(canvas, bx+BRICK_W-2, by+ddy,
                               int(color[0]*0.5),
                               int(color[1]*0.5),
                               int(color[2]*0.5))
            for ddx in range(PADDLE_W):
                fade = 1.0 - abs(ddx-PADDLE_W/2)/(PADDLE_W/2)*0.3
                draw_pixel(canvas, int(paddle_x)+ddx, PADDLE_Y,
                           0, int(200*fade), int(255*fade))
                draw_pixel(canvas, int(paddle_x)+ddx, PADDLE_Y+1,
                           0, int(150*fade), int(200*fade))
            draw_pixel(canvas, int(ball_x), int(ball_y), 255, 255, 255)
            if int(now*3) % 2:
                draw_text_centered(canvas, "W START", 52, 80, 80, 80)
            draw_text(canvas, str(score), 2, 1, 255, 255, 0)
            for i in range(lives):
                draw_pixel(canvas, 58-i*3, 1, 255, 50, 50)
            draw_text(canvas, f"L{level}", 50, 1, 100, 100, 100)
            particles.draw(canvas)
            matrix.SwapOnVSync(canvas)
            time.sleep(0.03)
            continue

        # Ball Physik
        ball_x += ball_vx * dt * 40
        ball_y += ball_vy * dt * 40

        if ball_x <= 0:
            ball_x = 0; ball_vx = abs(ball_vx)
        elif ball_x >= 63:
            ball_x = 63; ball_vx = -abs(ball_vx)
        if ball_y <= 0:
            ball_y = 0; ball_vy = abs(ball_vy)

        if ball_y >= 63:
            lives -= 1
            particles.emit(int(ball_x), 63, 15, 255, 0, 0,
                           spread=30, life=0.8)
            if lives <= 0:
                animation_flash(0.2, 255, 0, 0)
                animation_game_over(score, (255, 100, 0)); return
            serving = True
            ball_trail.clear(); continue

        # Paddle Kollision
        if ball_vy > 0 and PADDLE_Y-1 <= ball_y <= PADDLE_Y+PADDLE_H:
            if paddle_x-1 <= ball_x <= paddle_x+PADDLE_W+1:
                hit_pos = (ball_x - paddle_x) / PADDLE_W
                ang = (hit_pos - 0.5) * 2.2
                spd = math.sqrt(ball_vx**2 + ball_vy**2)
                ball_vx = spd * math.sin(ang)
                ball_vy = -abs(spd * math.cos(ang))
                ball_y = PADDLE_Y - 2
                particles.emit(int(ball_x), PADDLE_Y, 4,
                               0, 200, 255, spread=10, life=0.3)

        # Brick Kollision
        brick_hit = None
        for (col, row), color in list(bricks.items()):
            bx = BRICK_OFFSET_X + col * BRICK_W
            by = BRICK_OFFSET_Y + row * BRICK_H
            if (bx-1 <= ball_x <= bx+BRICK_W and
                    by-1 <= ball_y <= by+BRICK_H):
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
            particles.emit(bx+BRICK_W//2, by+BRICK_H//2,
                           8, *color, spread=25, life=0.5)
            if not bricks:
                level += 1
                ball_speed = min(2.5, start_speed + level * 0.15)
                animation_flash(0.15, 0, 255, 0)
                bricks = create_bricks()
                serving = True
                ball_trail.clear(); continue

        ball_trail.append((ball_x, ball_y))

        # Render
        canvas.Clear()
        for (col, row), color in bricks.items():
            bx = BRICK_OFFSET_X + col * BRICK_W
            by = BRICK_OFFSET_Y + row * BRICK_H
            draw_rect(canvas, bx, by, BRICK_W-1, BRICK_H-1, *color)
            for ddx in range(BRICK_W - 1):
                draw_pixel(canvas, bx+ddx, by,
                           min(255, int(color[0]*1.3)),
                           min(255, int(color[1]*1.3)),
                           min(255, int(color[2]*1.3)))

        for i, (tx, ty) in enumerate(ball_trail):
            f = (i+1) / max(len(ball_trail), 1)
            v = int(80 * f)
            draw_pixel(canvas, int(tx), int(ty), v, v, v)

        bxi, byi = int(ball_x), int(ball_y)
        for ddx in range(-1, 2):
            for ddy in range(-1, 2):
                if ddx == 0 and ddy == 0: continue
                draw_pixel(canvas, bxi+ddx, byi+ddy, 60, 60, 60)
        draw_pixel(canvas, bxi, byi, 255, 255, 255)

        for ddx in range(PADDLE_W):
            fade = 1.0 - abs(ddx-PADDLE_W/2)/(PADDLE_W/2)*0.3
            draw_pixel(canvas, int(paddle_x)+ddx, PADDLE_Y,
                       0, int(200*fade), int(255*fade))
            draw_pixel(canvas, int(paddle_x)+ddx, PADDLE_Y+1,
                       0, int(150*fade), int(200*fade))

        particles.update(dt); particles.draw(canvas)
        draw_text(canvas, str(score), 2, 1, 255, 255, 0)
        for i in range(lives):
            draw_pixel(canvas, 58-i*3, 1, 255, 50, 50)
        draw_text(canvas, f"L{level}", 48, 1, 100, 100, 100)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.016)


# ============================================================
#                    FLAPPY BIRD
# ============================================================

def play_flappy(difficulty=2):
    # Schwierigkeitsstufen: 1=EINFACH, 2=MITTEL, 3=SCHWER
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
            particles.emit(BIRD_X, int(bird_y)+2, 3,
                           255, 255, 100, spread=8, life=0.3)

        bird_vy += GRAVITY
        bird_y += bird_vy
        if bird_frame > 0: bird_frame -= 1

        if bird_y >= GROUND_Y - 3:
            animation_flash(0.15, 255, 100, 0)
            animation_game_over(score, (255, 200, 0)); return
        if bird_y < 0:
            bird_y = 0; bird_vy = 0

        pipe_timer += 1
        if pipe_timer >= PIPE_INTERVAL:
            pipe_timer = 0
            current_gap = max(13, GAP_H - score // 5)
            gap_center = random.randint(
                12 + current_gap//2, GROUND_Y - 8 - current_gap//2)
            pipes.append([64.0, gap_center, current_gap])

        current_speed = PIPE_SPEED + score * 0.02
        for pipe in pipes:
            pipe[0] -= current_speed
        pipes = [p for p in pipes if p[0] > -PIPE_W - 2]

        for i, pipe in enumerate(pipes):
            if pipe[0]+PIPE_W < BIRD_X and id(pipe) not in passed_pipes:
                passed_pipes.add(id(pipe))
                score += 1
                particles.emit_burst(BIRD_X+5, int(bird_y),
                                     5, spread=15, life=0.4)

        for pipe in pipes:
            px, gap_center, gap = pipe[0], pipe[1], pipe[2]
            if px-1 <= BIRD_X+3 <= px+PIPE_W+1:
                if (bird_y-1 < gap_center - gap//2 or
                        bird_y+3 > gap_center + gap//2):
                    animation_flash(0.15, 255, 0, 0)
                    animation_game_over(score, (255, 200, 0)); return

        ground_offset = (ground_offset + current_speed) % 4

        # Render
        canvas.Clear()

        for y in range(GROUND_Y):
            ratio = y / GROUND_Y
            r = int(20 + 30*ratio)
            g = int(30 + 60*ratio)
            b = int(80 + 80*(1-ratio))
            if y % 5 == 0:
                for x in range(0, 64, 8):
                    draw_pixel(canvas, x, y, r, g, b)

        for ci, (cx, cy, cs) in enumerate(clouds):
            wx = (cx - frame*cs*0.5) % 72 - 4
            draw_pixel(canvas, int(wx), cy, 40, 45, 55)
            draw_pixel(canvas, int(wx)+1, cy, 45, 50, 60)
            draw_pixel(canvas, int(wx)+2, cy, 40, 45, 55)
            draw_pixel(canvas, int(wx), cy+1, 35, 40, 50)
            draw_pixel(canvas, int(wx)+1, cy-1, 45, 50, 60)

        for pipe in pipes:
            px, gap_center, gap = int(pipe[0]), pipe[1], pipe[2]
            gap_top = gap_center - gap//2
            gap_bot = gap_center + gap//2
            for x in range(PIPE_W):
                px2 = px + x
                if 0 <= px2 < 64:
                    inner = 1 if 1 <= x <= PIPE_W-2 else 0
                    for y in range(0, gap_top):
                        if inner:
                            draw_pixel(canvas, px2, y, 40, 180, 40)
                        else:
                            draw_pixel(canvas, px2, y, 20, 120, 20)
                    if 0 <= gap_top-1:
                        draw_pixel(canvas, px2, gap_top-1, 60, 220, 60)
            for x in range(PIPE_W):
                px2 = px + x
                if 0 <= px2 < 64:
                    inner = 1 if 1 <= x <= PIPE_W-2 else 0
                    for y in range(gap_bot, GROUND_Y):
                        if inner:
                            draw_pixel(canvas, px2, y, 40, 180, 40)
                        else:
                            draw_pixel(canvas, px2, y, 20, 120, 20)
                    if gap_bot < 64:
                        draw_pixel(canvas, px2, gap_bot, 60, 220, 60)

        for x in range(64):
            draw_pixel(canvas, x, GROUND_Y, 80, 60, 30)
            draw_pixel(canvas, x, GROUND_Y+1, 100, 80, 40)
            if (x + int(ground_offset)) % 4 < 2:
                draw_pixel(canvas, x, GROUND_Y, 50, 150, 30)
            for dy in range(2, 5):
                draw_pixel(canvas, x, GROUND_Y+dy,
                           70+dy*5, 50+dy*3, 20)

        # Vogel
        by = int(bird_y)
        draw_pixel(canvas, BIRD_X, by, 255, 220, 50)
        draw_pixel(canvas, BIRD_X+1, by, 255, 230, 80)
        draw_pixel(canvas, BIRD_X, by+1, 255, 200, 30)
        draw_pixel(canvas, BIRD_X+1, by+1, 255, 210, 50)
        draw_pixel(canvas, BIRD_X+2, by+1, 255, 220, 60)
        draw_pixel(canvas, BIRD_X+2, by, 255, 255, 255)
        draw_pixel(canvas, BIRD_X+3, by+1, 255, 100, 0)
        if bird_frame > 1:
            draw_pixel(canvas, BIRD_X, by-1, 200, 200, 40)
            draw_pixel(canvas, BIRD_X+1, by-1, 200, 200, 40)
        else:
            draw_pixel(canvas, BIRD_X-1, by+1, 200, 200, 40)
            draw_pixel(canvas, BIRD_X, by+2, 180, 180, 30)
        if bird_vy > 1.5:
            draw_pixel(canvas, BIRD_X-1, by-1, 200, 180, 30)

        particles.update(0.03); particles.draw(canvas)

        score_str = str(score)
        sw = text_width(score_str)
        draw_text_centered(canvas, score_str, 3, 0, 0, 0)
        draw_text(canvas, score_str, (64-sw)//2 - 1, 2, 255, 255, 255)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.025)


# ============================================================
#               CONWAY'S GAME OF LIFE
# ============================================================

def play_game_of_life():
    GRID_W, GRID_H = 64, 64
    grid = [[0]*GRID_H for _ in range(GRID_W)]
    next_grid = [[0]*GRID_H for _ in range(GRID_W)]

    def randomize(density=0.3):
        for x in range(GRID_W):
            for y in range(GRID_H):
                grid[x][y] = 1 if random.random() < density else 0

    def clear_grid():
        for x in range(GRID_W):
            for y in range(GRID_H):
                grid[x][y] = 0

    def add_glider(ox, oy):
        for dx, dy in [(1,0),(2,1),(0,2),(1,2),(2,2)]:
            grid[(ox+dx)%GRID_W][(oy+dy)%GRID_H] = 1

    def add_rpentomino(ox, oy):
        for dx, dy in [(1,0),(2,0),(0,1),(1,1),(1,2)]:
            grid[(ox+dx)%GRID_W][(oy+dy)%GRID_H] = 1

    def add_acorn(ox, oy):
        for dx, dy in [(1,0),(3,1),(0,2),(1,2),(4,2),(5,2),(6,2)]:
            grid[(ox+dx)%GRID_W][(oy+dy)%GRID_H] = 1

    def count_neighbors(x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                if grid[(x+dx)%GRID_W][(y+dy)%GRID_H] > 0:
                    count += 1
        return count

    def step():
        alive = 0
        for x in range(GRID_W):
            for y in range(GRID_H):
                n = count_neighbors(x, y)
                if grid[x][y] > 0:
                    if n == 2 or n == 3:
                        next_grid[x][y] = min(grid[x][y]+1, 200)
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

    # Muster-Submenue
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
            h = (now*0.3 + x*0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 0.6, 0.25)
            draw_pixel(canvas, x, 19, r, g, b)
        for i, (label, _) in enumerate(patterns):
            y = 23 + i*10
            if i == sub_sel:
                pulse = 0.6 + 0.4*math.sin(now*5)
                v = int(255*pulse)
                ax = 4 + int(math.sin(now*6)*1.5)
                draw_text(canvas, ">", ax, y, v, v, 0)
                draw_text(canvas, label, 12, y, v, v//2, 0)
            else:
                draw_text(canvas, label, 12, y, 60, 40, 0)
        if int(now*1.5) % 2:
            draw_text_centered(canvas, "ESC BACK", 58, 50, 50, 50)
        matrix.SwapOnVSync(canvas)
        sk = consume_key()
        if sk == 'w': sub_sel = (sub_sel-1) % len(patterns)
        elif sk == 's': sub_sel = (sub_sel+1) % len(patterns)
        elif sk == '\x1b': return
        elif sk in ('\r', '\n', 'd', ' '):
            _, pattern = patterns[sub_sel]
            clear_grid()
            if pattern is None:
                randomize(0.35)
            elif pattern == "glider":
                for _ in range(8):
                    add_glider(random.randint(0,60),
                               random.randint(0,60))
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
                    hue = (age*0.02 + now*0.1) % 1.0
                    brightness = min(1.0, 0.4 + age*0.05)
                    r, g, b = hsv_to_rgb(hue, 0.9, brightness)
                    draw_pixel(canvas, x, y, r, g, b)

        gen_str = f"G{generation}"
        draw_text(canvas, gen_str, 1, 1, 80, 80, 80)
        if paused:
            if int(now*3) % 2:
                draw_text(canvas, "PAUSE", 38, 1, 200, 200, 0)
        sp_bar = int((1.0 - (speed-0.02)/0.48) * 10)
        for i in range(sp_bar):
            draw_pixel(canvas, 60, 58-i, 0, 100+i*15, 0)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.02)


# ============================================================
#                  REACTION TIME GAME
# ============================================================

def play_reaction(difficulty=2):
    clear_input()
    particles = ParticleSystem()
    best_time = 9999
    times = []
    round_num = 0
    # Schwierigkeitsstufen: 1=EINFACH, 2=MITTEL, 3=SCHWER
    if difficulty == 1:
        TOTAL_ROUNDS = 3
        wait_min, wait_max = 1.5, 3.5
    elif difficulty == 3:
        TOTAL_ROUNDS = 7
        wait_min, wait_max = 1.0, 6.0
    else:
        TOTAL_ROUNDS = 5
        wait_min, wait_max = 1.5, 5.0

    while running and round_num < TOTAL_ROUNDS:
        # Phase 1: Bereit machen
        clear_input()
        start_show = time.time()
        while time.time() - start_show < 1.5:
            now = time.time()
            canvas.Clear()
            draw_text_centered(canvas, f"RUNDE {round_num+1}",
                               8, 150, 150, 150)
            pulse = 0.5 + 0.5*math.sin(now*6)
            v = int(200*pulse)
            draw_text_centered(canvas, "BEREIT", 26, v, v, 0)
            draw_text_centered(canvas, "WARTE AUF", 42, 80, 80, 80)
            draw_text_centered(canvas, "GRUEN!", 50, 0, 80, 0)
            matrix.SwapOnVSync(canvas)
            ck = consume_key()
            if ck == '\x1b': return
            time.sleep(0.03)

        # Phase 2: Rotes Warten
        wait_time = random.uniform(wait_min, wait_max)
        wait_start = time.time()
        too_early = False

        while time.time() - wait_start < wait_time:
            canvas.Clear()
            now = time.time()
            pulse = 0.8 + 0.2*math.sin(now*2)
            for x in range(0, 64, 2):
                for y in range(0, 64, 2):
                    draw_pixel(canvas, x, y, int(40*pulse), 0, 0)
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

        # Phase 3: GRUEN! Messen
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
            draw_text_centered(canvas, f"{elapsed_ms}MS",
                               48, 200, 200, 200)
            matrix.SwapOnVSync(canvas)
            ck = consume_key()
            if ck == '\x1b': return
            if ck is not None:
                reaction_ms = int((time.time()-green_time)*1000)
                times.append(reaction_ms)
                if reaction_ms < best_time: best_time = reaction_ms
                reacted = True; round_num += 1
            if now - green_time > 3.0:
                times.append(3000); round_num += 1; reacted = True
            time.sleep(0.005)

        # Phase 4: Ergebnis
        reaction_ms = times[-1]
        particles.emit_burst(32, 32, 10, spread=25, life=0.8)
        if reaction_ms < 200:
            rating = "BLITZ!"; rc,gc,bc = 255,255,0
        elif reaction_ms < 300:
            rating = "SUPER!"; rc,gc,bc = 0,255,0
        elif reaction_ms < 400:
            rating = "GUT"; rc,gc,bc = 0,200,200
        elif reaction_ms < 600:
            rating = "OK"; rc,gc,bc = 200,200,0
        else:
            rating = "LANGSAM"; rc,gc,bc = 255,100,0

        show_start = time.time()
        while time.time() - show_start < 2.5:
            now = time.time()
            canvas.Clear()
            particles.update(0.03); particles.draw(canvas)
            draw_text_centered(canvas, f"{reaction_ms}MS",
                               18, 255, 255, 255)
            pulse = 0.6 + 0.4*math.sin(now*6)
            draw_text_centered(canvas, rating, 30,
                               int(rc*pulse), int(gc*pulse),
                               int(bc*pulse))
            draw_text_centered(canvas, f"BEST {best_time}MS",
                               46, 100, 100, 150)
            draw_text_centered(canvas, f"{round_num}/{TOTAL_ROUNDS}",
                               56, 80, 80, 80)
            matrix.SwapOnVSync(canvas)
            if consume_key() == '\x1b': return
            time.sleep(0.03)

    # Endergebnis
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
            h = (now*0.3 + x*0.02) % 1.0
            r, g, b = hsv_to_rgb(h, 0.7, 0.3)
            draw_pixel(canvas, x, 12, r, g, b)
        draw_text_centered(canvas, "SCHNITT", 16, 150, 150, 150)
        draw_text_centered(canvas, f"{avg}MS", 24, 0, 255, 200)
        draw_text_centered(canvas, "BESTE", 34, 150, 150, 150)
        draw_text_centered(canvas, f"{best_time}MS", 42, 255, 255, 0)
        for i, t in enumerate(times):
            tx = 5 + i*12
            draw_text(canvas, str(t), tx, 54, 80, 80, 80)
        if now-start > 1.5 and int(now*2) % 2:
            draw_text_centered(canvas, "ESC", 58, 60, 60, 60)
        matrix.SwapOnVSync(canvas)
        if now-start > 1.0 and consume_key() is not None: return
        time.sleep(0.03)


# ============================================================
#                 MAZE GENERATOR / RUNNER
# ============================================================

def play_maze(difficulty=2):
    CELL_SIZE = 2
    MAZE_W = 31
    MAZE_H = 31
    # Schwierigkeitsstufen: 1=EINFACH, 2=MITTEL, 3=SCHWER
    if difficulty == 1:
        default_sight = 8
        fog_default = False
    elif difficulty == 3:
        default_sight = 4
        fog_default = True
    else:
        default_sight = 6
        fog_default = True

    def generate_maze():
        maze = [[1]*MAZE_H for _ in range(MAZE_W)]
        start_x, start_y = 1, 1
        maze[start_x][start_y] = 0
        stack = [(start_x, start_y)]
        directions = [(0,-2),(0,2),(-2,0),(2,0)]
        while stack:
            cx, cy = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy in directions:
                nx, ny = cx+dx, cy+dy
                if (0 < nx < MAZE_W and 0 < ny < MAZE_H
                        and maze[nx][ny] == 1):
                    maze[cx+dx//2][cy+dy//2] = 0
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
        goal_x, goal_y = MAZE_W-2, MAZE_H-2
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

            nx, ny = player_x+dx, player_y+dy
            if (0 <= nx < MAZE_W and 0 <= ny < MAZE_H
                    and maze[nx][ny] == 0):
                player_x, player_y = nx, ny
                steps += 1; total_steps += 1

            if player_x == goal_x and player_y == goal_y:
                particles.emit_burst(
                    goal_x*CELL_SIZE+1, goal_y*CELL_SIZE+1,
                    15, spread=25, life=0.8)
                animation_flash(0.15, 255, 255, 0)
                show_start = time.time()
                while time.time()-show_start < 2.0 and running:
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
            cam_x = player_x*CELL_SIZE - 31
            cam_y = player_y*CELL_SIZE - 31

            for mx in range(MAZE_W):
                for my in range(MAZE_H):
                    sx = mx*CELL_SIZE - cam_x
                    sy = my*CELL_SIZE - cam_y
                    if sx < -2 or sx > 65 or sy < -2 or sy > 65:
                        continue
                    if fog:
                        dist = abs(mx-player_x) + abs(my-player_y)
                        if dist > SIGHT: continue
                        fog_fade = max(0.2,
                                       1.0 - (dist/SIGHT)*0.8)
                    else:
                        fog_fade = 1.0
                    if maze[mx][my] == 1:
                        h = (now*0.1 + (mx+my)*0.05) % 1.0
                        r, g, b = hsv_to_rgb(h, 0.3,
                                             0.2*fog_fade)
                        for ddx in range(CELL_SIZE):
                            for ddy in range(CELL_SIZE):
                                draw_pixel(canvas, sx+ddx,
                                           sy+ddy, r, g, b)

            # Ziel
            gsx = goal_x*CELL_SIZE - cam_x
            gsy = goal_y*CELL_SIZE - cam_y
            if (not fog or
                    abs(goal_x-player_x)+abs(goal_y-player_y) <= SIGHT):
                pulse = 0.5 + 0.5*math.sin(now*5)
                for ddx in range(CELL_SIZE):
                    for ddy in range(CELL_SIZE):
                        draw_pixel(canvas, gsx+ddx, gsy+ddy,
                                   int(255*pulse), int(200*pulse), 0)

            # Spieler
            psx = player_x*CELL_SIZE - cam_x
            psy = player_y*CELL_SIZE - cam_y
            for ddx in range(CELL_SIZE):
                for ddy in range(CELL_SIZE):
                    draw_pixel(canvas, psx+ddx, psy+ddy, 0, 255, 0)
            for ddx in range(-1, CELL_SIZE+1):
                for ddy in range(-1, CELL_SIZE+1):
                    if 0 <= ddx < CELL_SIZE and 0 <= ddy < CELL_SIZE:
                        continue
                    draw_pixel(canvas, psx+ddx, psy+ddy, 0, 40, 0)

            particles.update(0.03); particles.draw(canvas)
            draw_text(canvas, f"L{level}", 1, 1, 150, 150, 0)
            draw_text(canvas, str(steps), 48, 1, 150, 150, 150)
            if fog:
                draw_pixel(canvas, 62, 1, 100, 0, 100)

            matrix.SwapOnVSync(canvas)
            time.sleep(0.05)


# ============================================================
#  ENDE TEIL 4 - Weiter mit Teil 5: Spotify-Wrapper,
#  Visualizer-Wrapper, Hauptmenue (mit allen 14 Eintraegen)
# ============================================================
# ============================================================
#  RGB MATRIX GAMES - TEIL 5 von 5 (LETZTER TEIL)
#  Spotify-Wrapper, Visualizer-Wrapper, Hauptmenue
#  mit allen 14 Eintraegen + Konfigurations-Menue
# ============================================================


# ============================================================
#     SPOTIFY CONFIG - TRAGE HIER DEINE DATEN EIN!
# ============================================================
# Anleitung:
# 1. Gehe zu https://developer.spotify.com/dashboard
# 2. Erstelle eine neue App
# 3. Kopiere Client ID und Client Secret hierher
# 4. Redirect URI: http://localhost:8888/callback
#    (muss auch im Dashboard eingetragen sein!)
#
# ALTERNATIV: Setze Umgebungsvariablen statt hier einzutragen:
#   export SPOTIPY_CLIENT_ID="deine_id"
#   export SPOTIPY_CLIENT_SECRET="dein_secret"
#   export SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"

SPOTIFY_CLIENT_ID = ""        # <-- HIER DEINE CLIENT ID
SPOTIFY_CLIENT_SECRET = ""    # <-- HIER DEIN CLIENT SECRET
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"

# Wenn hier ausgefuellt, werden diese Werte benutzt.
# Wenn leer, wird auf Umgebungsvariablen zurueckgegriffen.
# (Das passiert automatisch in der SpotifyDisplay Klasse)

def _apply_spotify_config():
    """Setzt Umgebungsvariablen falls hier konfiguriert."""
    if SPOTIFY_CLIENT_ID:
        os.environ['SPOTIPY_CLIENT_ID'] = SPOTIFY_CLIENT_ID
    if SPOTIFY_CLIENT_SECRET:
        os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIFY_CLIENT_SECRET
    if SPOTIFY_REDIRECT_URI:
        os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIFY_REDIRECT_URI

_apply_spotify_config()

# Spotify-Display mit den gesetzten Konfigurationswerten erstellen
spotify_display = SpotifyDisplay()


# ============================================================
#     SPOTIFY ANZEIGE - WRAPPER FUNKTION
# ============================================================

def show_spotify():
    """
    Spotify Album-Cover Anzeige.
    - Zeigt Cover + Song-Info wenn Musik spielt
    - Faellt auf Digitaluhr zurueck wenn nichts spielt
    - ESC zum Beenden
    
    Steuerung:
      ESC = Zurueck zum Menue
    """
    clear_input()

    # Digitaluhr als Fallback vorbereiten
    WOCHENTAGE = ["MO", "DI", "MI", "DO", "FR", "SA", "SO"]
    if weather_data.should_fetch():
        weather_data.fetch()

    while running:
        now = time.time()
        k = consume_key()
        if k == '\x1b': return

        canvas.Clear()

        # Spotify zeichnen - gibt True zurueck wenn Cover angezeigt
        showing_spotify = spotify_display.draw(canvas)

        if not showing_spotify:
            # Fallback: Mini-Digitaluhr mit Spotify-Hinweis
            canvas.Clear()
            at = get_austria_time()
            hours = at.tm_hour
            minutes = at.tm_min
            seconds = at.tm_sec
            frac = now % 1.0

            # Subtiler Hintergrund
            for gx in range(0, 64, 3):
                for gy in range(0, 64, 3):
                    wave = math.sin(now*0.3 + gx*0.08 + gy*0.06)
                    v = int(3 + 2*wave)
                    draw_pixel(canvas, gx, gy, 0, v, 0)

            # Spotify Logo oben (gruen)
            draw_text_centered(canvas, "SPOTIFY", 2, 30, 185, 64)

            # Status
            if spotify_display.error_msg:
                draw_text_centered(canvas, spotify_display.error_msg[:15],
                                   12, 200, 60, 0)
            else:
                pulse = 0.5 + 0.5*math.sin(now*2)
                v = int(120*pulse)
                draw_text_centered(canvas, "KEINE MUSIK", 12,
                                   v, v, v)

            # Trennlinie
            for x in range(10, 54):
                h = (now*0.2 + x*0.03) % 1.0
                r, g, b = hsv_to_rgb(h, 0.5, 0.15)
                draw_pixel(canvas, x, 19, r, g, b)

            # Grosse Uhrzeit
            h_str = f"{hours:02d}"
            m_str = f"{minutes:02d}"
            tw = big_time_width(f"{hours:02d}:{minutes:02d}")
            tx = (64 - tw) // 2

            draw_big_digit(canvas, h_str[0], tx, 23, 0, 180, 230)
            draw_big_digit(canvas, h_str[1], tx+6, 23, 0, 180, 230)
            if frac < 0.5:
                draw_pixel(canvas, tx+13, 25, 0, 180, 230)
                draw_pixel(canvas, tx+13, 27, 0, 180, 230)
            draw_big_digit(canvas, m_str[0], tx+16, 23, 0, 180, 230)
            draw_big_digit(canvas, m_str[1], tx+22, 23, 0, 180, 230)

            # Sekunden
            s_str = f"{seconds:02d}"
            draw_text(canvas, s_str, tx+29, 27, 80, 120, 160)

            # Datum
            wday = at.tm_wday
            wday_str = WOCHENTAGE[wday] if wday < 7 else "??"
            date_str = f"{wday_str} {at.tm_mday:02d}.{at.tm_mon:02d}"
            draw_text_centered(canvas, date_str, 35, 80, 80, 100)

            # Wetter wenn vorhanden
            if weather_data.temperature is not None:
                temp = weather_data.temperature
                temp_str = f"{temp:.0f}C"
                if temp <= 0: tr,tg,tb = 100,150,255
                elif temp <= 20: tr,tg,tb = 0,200,200
                else: tr,tg,tb = 255,200,0
                draw_text(canvas, temp_str, 5, 45, tr, tg, tb)
                desc = weather_data.get_description()
                draw_text(canvas, desc, 24, 45, 120, 120, 120)
            if weather_data.should_fetch():
                weather_data.fetch()

            # Hinweis unten
            if int(now*1.5) % 2:
                draw_text_centered(canvas, "PLAY SPOTIFY",
                                   55, 30, 100, 30)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)


# ============================================================
#     AUDIO VISUALIZER - WRAPPER FUNKTION
# ============================================================

def show_visualizer():
    """
    Audio-Visualizer mit FFT.
    
    Steuerung:
      W/S   = Sensitivity hoch/runter
      D     = Farb-Modus wechseln
      ESC   = Zurueck zum Menue
    
    Audio-Routing Setup (einmalig auf dem Pi):
    
    1. PulseAudio Loopback einrichten:
       pactl load-module module-null-sink sink_name=vis_sink
       pactl set-default-sink vis_sink
    
    2. Dann hoert der Visualizer auf: vis_sink.monitor
    
    3. Um trotzdem Ton aus dem Lautsprecher zu hoeren:
       pactl load-module module-loopback source=vis_sink.monitor
    
    ODER einfach ein USB-Mikrofon anschliessen - das geht auch!
    """
    clear_input()

    # Visualizer starten
    audio_visualizer.start()

    try:
        while running:
            now = time.time()
            k = consume_key()
            if k == '\x1b':
                return

            # Sensitivity
            if k == 'w':
                audio_visualizer.sensitivity = min(5.0,
                    audio_visualizer.sensitivity + 0.2)
            elif k == 's':
                audio_visualizer.sensitivity = max(0.3,
                    audio_visualizer.sensitivity - 0.2)

            # Farb-Modus wechseln
            if k == 'd':
                audio_visualizer.color_mode = \
                    (audio_visualizer.color_mode + 1) % 4

            canvas.Clear()
            audio_visualizer.draw(canvas)

            # Steuerungs-Hinweis kurz einblenden
            # (nur erste 5 Sekunden)
            matrix.SwapOnVSync(canvas)
            time.sleep(0.016)
    finally:
        audio_visualizer.stop()


# ============================================================
#                    HAUPTMENUE
# ============================================================

def show_difficulty_menu(title, title_color, starfield, menu_start):
    """Zeigt ein Schwierigkeits-Submenue (EINFACH/MITTEL/SCHWER).
    Gibt 1, 2 oder 3 zurueck, oder None bei ESC."""
    sub_sel = 0
    submenu = [("EINFACH",(0,255,0)),
               ("MITTEL",(255,200,0)),
               ("SCHWER",(255,50,50))]
    while running:
        now2 = time.time()
        canvas.Clear()
        starfield.draw(canvas, now2 - menu_start)
        draw_text_centered(canvas, title, 5,
                           title_color[0], title_color[1], title_color[2])
        for x in range(15, 49):
            h = (now2*0.5 + x*0.03) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 0.3)
            draw_pixel(canvas, x, 12, r, g, b)
        for i, (label, color) in enumerate(submenu):
            y = 18 + i*15
            if i == sub_sel:
                pulse = 0.6+0.4*math.sin(now2*5)
                r = int(color[0]*pulse)
                g = int(color[1]*pulse)
                b = int(color[2]*pulse)
                ax = 4+int(math.sin(now2*6)*1.5)
                draw_text(canvas, ">", ax, y, r, g, b)
                draw_text(canvas, f"{i+1} {label}", 12, y, r, g, b)
            else:
                draw_text(canvas, f"{i+1} {label}",
                          12, y, color[0]//4, color[1]//4, color[2]//4)
        if int(now2*1.5) % 2:
            draw_text_centered(canvas, "ESC BACK", 58, 50, 50, 50)
        matrix.SwapOnVSync(canvas)
        sk = consume_key()
        if sk in ('w','W','UP'): sub_sel = (sub_sel-1) % 3
        elif sk in ('s','S','DOWN'): sub_sel = (sub_sel+1) % 3
        elif sk == '1': animation_transition(); return 1
        elif sk == '2': animation_transition(); return 2
        elif sk == '3': animation_transition(); return 3
        elif sk in ('\r','\n','d','D'):
            animation_transition(); return sub_sel+1
        elif sk == '\x1b': return None
        time.sleep(0.05)
    return None

try:
    starfield = Starfield(50)
    selected = 0

    # Tab-Kategorien: SPIELE und EXTRAS
    tab_names = ["SPIELE", "EXTRAS"]
    tab_colors = [(0, 255, 100), (100, 150, 255)]
    current_tab = 0

    tabs = [
        # Tab 0: SPIELE
        [
            ("SNAKE",      (0, 255, 0)),
            ("TETRIS",     (0, 150, 255)),
            ("PONG",       (255, 0, 255)),
            ("BREAKOUT",   (255, 100, 0)),
            ("FLAPPY",     (255, 220, 0)),
            ("REACTION",   (255, 50, 50)),
            ("LABYRINTH",  (0, 255, 200)),
        ],
        # Tab 1: EXTRAS
        [
            ("LIFE",       (200, 100, 0)),
            ("DVD",        (255, 0, 100)),
            ("ANALOG",     (100, 200, 255)),
            ("DIGITAL",    (0, 200, 200)),
            ("WETTER",     (100, 255, 100)),
            ("SPOTIFY",    (30, 185, 64)),
            ("VISUALIZER", (255, 0, 255)),
        ],
    ]

    menu_items = tabs[current_tab]

    scroll_offset = 0
    VISIBLE_ITEMS = 4
    menu_start = time.time()

    # Intro Animation
    intro_start = time.time()
    while time.time() - intro_start < 1.8 and running:
        t = time.time() - intro_start
        canvas.Clear()
        starfield.draw(canvas, t)
        title_y = int(-10 + t * 12)
        title_y = min(title_y, 2)
        title_text = "MATRIX"
        tx = (64 - text_width(title_text)) // 2
        for i, ch in enumerate(title_text):
            h = (t*0.5 + i*0.12) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 1.0)
            draw_text(canvas, ch, tx + i*4, title_y, r, g, b)
        if t > 0.8:
            fade = min(1.0, (t-0.8)/0.5)
            v = int(120*fade)
            draw_text_centered(canvas, "HUB", 9, v, v, v)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)

    clear_input()

    while running:
        now = time.time()
        t = now - menu_start

        canvas.Clear()
        starfield.draw(canvas, t)

        # Rainbow Titel
        title_text = "MATRIX"
        tx = (64 - text_width(title_text)) // 2
        for i, ch in enumerate(title_text):
            h = (t*0.3 + i*0.12) % 1.0
            r, g, b = hsv_to_rgb(h, 1.0, 1.0)
            draw_text(canvas, ch, tx + i*4, 2, r, g, b)

        draw_text_centered(canvas, "HUB", 9, 100, 100, 120)

        # Tab-Anzeige
        for ti in range(len(tab_names)):
            tc = tab_colors[ti]
            tx_pos = 2 + ti * 32
            if ti == current_tab:
                pulse_tab = 0.7 + 0.3*math.sin(t*4)
                draw_text(canvas, tab_names[ti], tx_pos, 14,
                          int(tc[0]*pulse_tab), int(tc[1]*pulse_tab),
                          int(tc[2]*pulse_tab))
            else:
                draw_text(canvas, tab_names[ti], tx_pos, 14,
                          tc[0]//6, tc[1]//6, tc[2]//6)

        # Scroll sicherstellen
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
                pulse = 0.6 + 0.4*math.sin(t*5)
                r = int(base_color[0]*pulse)
                g = int(base_color[1]*pulse)
                b = int(base_color[2]*pulse)
                arrow_x = 2 + int(math.sin(t*6)*1.5)
                draw_text(canvas, ">", arrow_x, y, r, g, b)
                draw_text(canvas, name, 10, y, r, g, b)
                w = text_width(name)
                for ux in range(w + 2):
                    gr = int(pulse*0.25*base_color[0])
                    gg = int(pulse*0.25*base_color[1])
                    gb = int(pulse*0.25*base_color[2])
                    draw_pixel(canvas, 9+ux, y+6, gr, gg, gb)
            else:
                r = base_color[0] // 5
                g = base_color[1] // 5
                b = base_color[2] // 5
                draw_text(canvas, name, 10, y, r, g, b)

        # Scroll-Indikatoren
        if scroll_offset > 0:
            pulse_up = 0.5 + 0.5*math.sin(t*4)
            v = int(80*pulse_up)
            draw_pixel(canvas, 60, 20, v, v, v)
            draw_pixel(canvas, 59, 21, v, v, v)
            draw_pixel(canvas, 61, 21, v, v, v)

        if scroll_offset + VISIBLE_ITEMS < len(menu_items):
            pulse_dn = 0.5 + 0.5*math.sin(t*4 + 1)
            v = int(80*pulse_dn)
            bottom_y = 21 + VISIBLE_ITEMS*10 - 3
            draw_pixel(canvas, 60, bottom_y+2, v, v, v)
            draw_pixel(canvas, 59, bottom_y+1, v, v, v)
            draw_pixel(canvas, 61, bottom_y+1, v, v, v)

        # Seitenzahl
        page_str = f"{selected+1}/{len(menu_items)}"
        draw_text(canvas, page_str, 40, 58, 40, 40, 50)

        # Footer
        if int(t*1.5) % 2:
            draw_text(canvas, "W/S TAB", 2, 58, 40, 40, 40)

        matrix.SwapOnVSync(canvas)

        # --- INPUT ---
        k = consume_key()

        # Tab wechseln mit Tab-Taste oder A
        if k in ('\t', 'a', 'A'):
            current_tab = (current_tab + 1) % len(tabs)
            menu_items = tabs[current_tab]
            selected = 0
            scroll_offset = 0
            continue

        if k in ('w', 'W', 'UP'):
            selected = (selected - 1) % len(menu_items)
        elif k in ('s', 'S', 'DOWN'):
            selected = (selected + 1) % len(menu_items)

        # Direktwahl 1-9
        if k and len(k) == 1 and k.isdigit() and k != '0':
            num = int(k) - 1
            if num < len(menu_items):
                selected = num
                k = '\r'

        # Enter/Bestaetigen
        if k in ('\r', '\n', 'd', 'D'):
            animation_transition()
            clear_input()

            # Aktuellen Eintragsnamen holen
            item_name = menu_items[selected][0]
            item_color = menu_items[selected][1]

            if item_name == "SNAKE":
                # Snake Submenue (NORMAL/ULTIMATE)
                sub_sel = 0
                while running:
                    now2 = time.time()
                    canvas.Clear()
                    starfield.draw(canvas, now2 - menu_start)
                    draw_text_centered(canvas, "SNAKE", 5, 0, 255, 0)
                    for x in range(15, 49):
                        h = (now2*0.5 + x*0.03) % 1.0
                        r, g, b = hsv_to_rgb(h, 1.0, 0.3)
                        draw_pixel(canvas, x, 12, r, g, b)
                    submenu = [("NORMAL",(0,255,0)),
                               ("ULTIMATE",(255,80,0))]
                    for i, (label, color) in enumerate(submenu):
                        y = 20 + i*18
                        if i == sub_sel:
                            pulse = 0.6+0.4*math.sin(now2*5)
                            r = int(color[0]*pulse)
                            g = int(color[1]*pulse)
                            b = int(color[2]*pulse)
                            ax = 4+int(math.sin(now2*6)*1.5)
                            draw_text(canvas, ">", ax, y, r, g, b)
                            draw_text(canvas, f"{i+1} {label}",
                                      12, y, r, g, b)
                        else:
                            draw_text(canvas, f"{i+1} {label}",
                                      12, y, color[0]//4,
                                      color[1]//4, color[2]//4)
                    if int(now2*1.5) % 2:
                        draw_text_centered(canvas, "ESC BACK",
                                           58, 50, 50, 50)
                    matrix.SwapOnVSync(canvas)
                    sk = consume_key()
                    if sk in ('w','W','UP'):
                        sub_sel = (sub_sel-1) % 2
                    elif sk in ('s','S','DOWN'):
                        sub_sel = (sub_sel+1) % 2
                    elif sk == '1':
                        animation_transition()
                        play_snake(1); break
                    elif sk == '2':
                        animation_transition()
                        play_snake(2); break
                    elif sk in ('\r','\n','d','D'):
                        animation_transition()
                        play_snake(sub_sel+1); break
                    elif sk == '\x1b': break
                    time.sleep(0.05)

            elif item_name == "TETRIS":
                play_tetris()
            elif item_name == "PONG":
                d = show_difficulty_menu("PONG", item_color,
                                         starfield, menu_start)
                if d is not None: play_pong(d)
            elif item_name == "BREAKOUT":
                d = show_difficulty_menu("BREAKOUT", item_color,
                                         starfield, menu_start)
                if d is not None: play_breakout(d)
            elif item_name == "FLAPPY":
                d = show_difficulty_menu("FLAPPY", item_color,
                                         starfield, menu_start)
                if d is not None: play_flappy(d)
            elif item_name == "REACTION":
                d = show_difficulty_menu("REACTION", item_color,
                                         starfield, menu_start)
                if d is not None: play_reaction(d)
            elif item_name == "LABYRINTH":
                d = show_difficulty_menu("LABYRINTH", item_color,
                                         starfield, menu_start)
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
            elif item_name == "SPOTIFY":
                show_spotify()
            elif item_name == "VISUALIZER":
                show_visualizer()

            clear_input()
            menu_start = time.time()

        time.sleep(0.05)

finally:
    # Aufraumen
    audio_visualizer.stop()
    running = False
    matrix.Clear()


# ============================================================
#  ENDE TEIL 5 - ALLE TEILE ZUSAMMEN ERGEBEN DAS KOMPLETTE
#  SKRIPT. EINFACH TEIL 1-5 NACHEINANDER IN EINE DATEI KOPIEREN.
# ============================================================
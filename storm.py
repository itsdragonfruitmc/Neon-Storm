import colorsys
import math
import random
import turtle

HUES = [0.52, 0.80, 0.72, 0.55]
STRIKES = [
    (110, 1),
    (214, 2),
    (530, 3),
    (420, 4),
    (452, 5),
    (488, 6),
    (538, 7),
    (566, 8),
]
SHEETS = [(30, 0.25), (58, 0.35), (170, 0.3), (270, 0.3)]
SPANS = [(0, 90), (90, 192), (192, 294), (294, 402), (402, 610)]

screen = turtle.Screen()
screen.setup(780, 480)
screen.bgcolor("#03030a")
screen.colormode(1.0)
screen.tracer(0)

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.penup()


def clamp(x):
  return max(0.0, min(1.0, x))


def mix(a, b, k):
  return tuple(p + (q - p) * k for p, q in zip(a, b))


def neon(h, s=0.85, v=1.0):
  return colorsys.hsv_to_rgb(h % 1, s, v)


def stroke(pts, color, width):
  t.pencolor(color)
  t.pensize(width)
  t.goto(*pts[0])
  t.pendown()
  for p in pts[1:]:
    t.goto(*p)
  t.penup()


def jag(p, q, rng, depth, spread):
  if depth == 0:
    return [p, q]
  dx = rng.uniform(-spread, spread)
  dy = rng.uniform(-spread, spread) / 3
  m = ((p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy)
  left = jag(p, m, rng, depth - 1, spread / 2)
  right = jag(m, q, rng, depth - 1, spread / 2)
  return left[:-1] + right


def make_bolt(frame, seed):
  rng = random.Random(seed * 31)
  x0 = rng.uniform(-250, 250)
  x1 = x0 + rng.uniform(-100, 100)
  main = jag((x0, 175), (x1, -150), rng, 5, 60)
  forks = []
  for k in rng.sample(range(4, len(main) - 4), 5):
    p = main[k]
    qx = p[0] + rng.uniform(-130, 130)
    qy = p[1] - rng.uniform(50, 120)
    forks.append((k, jag(p, (qx, qy), rng, 3, 24)))
  return frame, HUES[seed % 4], main, forks


BOLTS = [make_bolt(f, s) for f, s in STRIKES]


def glow_at(age):
  if age < 0:
    return 0
  if age < 0.15:
    return 0.15 * age / 0.15
  a = age - 0.15
  f = math.exp(-a * 7)
  f += 0.6 * math.exp(-((a - 0.2) * 14) ** 2)
  return min(1.0, f)


def sky(fl):
  lit = (0.55, 0.6, 0.95)
  top = mix((0.01, 0.01, 0.05), lit, fl * 0.6)
  low = mix((0.10, 0.05, 0.20), (0.05, 0.85, 1), fl * 0.7)
  for i in range(60):
    y = 236 - i * 8
    col = mix(top, low, (i / 59) ** 0.8)
    stroke([(-390, y), (390, y)], col, 10)


def clouds(tm, fl, build):
  rng = random.Random(3)
  for i in range(int(320 * build)):
    x = rng.uniform(-430, 430)
    x += 14 * math.sin(tm * 0.5 + i)
    y = rng.uniform(125, 265)
    dark = (0.03, 0.02, 0.08)
    col = mix(dark, (0.62, 0.66, 0.95), fl * 0.65)
    t.goto(x, y)
    t.dot(rng.uniform(50, 100), col)


def city(fl):
  rng = random.Random(8)
  x = -390
  while x < 390:
    w = rng.randint(30, 60)
    h = rng.randint(30, 105)
    lit = (0.25, 0.28, 0.45)
    col = mix((0.01, 0.01, 0.03), lit, fl * 0.5)
    for y in range(-240, -240 + h, 6):
      stroke([(x, y), (x + w, y)], col, 8)
    for _ in range(w // 10):
      t.goto(x + rng.randint(3, w - 3), -232 + rng.randint(6, h - 6))
      t.dot(3, (1, 0.8, 0.45))
    x += w


def rain(tm, fl, build):
  col = mix((0.25, 0.3, 0.5), (0.8, 0.85, 1), fl)
  for i in range(int(130 * build)):
    x = (i * 61) % 820 - 410
    y = 250 - (tm * 460 + i * 47) % 500
    stroke([(x, y), (x + 5, y - 18)], col, 1.2)


def draw_bolt(b, t_frame):
  frame, hue, main, forks = b
  age = (t_frame - frame) / 30
  if age < 0 or age > 1.6:
    return
  f = clamp(age / 0.16)
  fade = clamp(1 - (age - 0.16) / 1.1) ** 1.5
  n = int(f * (len(main) - 1)) + 1
  outer = neon(hue, 0.9, 0.35 * fade)
  mid = neon(hue, 0.6, 0.25 + 0.75 * fade)
  core = mix(neon(hue, 0.25, 1), (1, 1, 1), 0.3)
  core = mix(core, (0, 0, 0), 0.3 + 0.7 * fade)
  layers = [(22, outer), (10, mid), (4, core)]
  for width, col in layers:
    stroke(main[:n], col, width)
    for k, fork in forks:
      if k < n:
        stroke(fork, col, width * 0.55)
  if f == 1 and age < 0.6:
    x, y = main[-1]
    for j in range(12):
      a = 6.283 * j / 12
      r = 10 + 90 * (age - 0.16)
      ex = x + r * math.cos(a)
      ey = y + r * math.sin(a) / 2
      stroke([(x, y), (ex, ey)], neon(hue, 0.3), 1.5)


def frame(i):
  tm = i / 30
  build = min(1.0, i / 60)
  fl = 0.0
  for f, s in STRIKES:
    fl = max(fl, glow_at((i - f) / 30))
  for f0, amp in SHEETS:
    fl = max(fl, amp * glow_at((i - f0) / 30))
  t.clear()
  sky(fl)
  clouds(tm, fl, build)
  city(fl)
  rain(tm, fl, build)
  for b in BOLTS:
    draw_bolt(b, i)
  screen.update()


def play(k):
  for i in range(*SPANS[k]):
    frame(i)


def gather():
  play(0)


def first_strike():
  play(1)


def second_strike():
  play(2)


def third_strike():
  play(3)


def finale():
  play(4)


gather()
first_strike()
second_strike()
third_strike()
finale()
turtle.done()
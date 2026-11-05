#!/usr/bin/env python3
"""Draws Nimbus's large central weather pictures into res/drawable-nodpi (wxl_*.png).

All procedural (noise + blur), no photos or third-party artwork. Greyscale/white on a
transparent background so they sit on the face's black centre disk.
usage: python3 design/make_weather_art.py      (needs Pillow + numpy)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "res", "drawable-nodpi")
N = 220                      # final size in px (drawn 1:1 on the 450 px face)
SS = 2                       # supersample
W = N * SS
rng = np.random.default_rng(7)   # fixed seed: re-running gives identical PNGs


def fbm(size, octaves=5, seed=0):
    """Fractal value noise in [0,1]."""
    r = np.random.default_rng(seed)
    out = np.zeros((size, size))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        cells = 4 * 2 ** o
        grid = r.random((cells + 1, cells + 1))
        im = Image.fromarray((grid * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
        out += amp * np.asarray(im, dtype=float) / 255
        total += amp
        amp *= 0.5
    return out / total


def to_img(alpha, lum=None):
    alpha = np.clip(alpha, 0, 1)
    lum = np.ones_like(alpha) if lum is None else np.clip(lum, 0, 1)
    rgba = np.dstack([lum * 255] * 3 + [alpha * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def blob_mask(circles, blur):
    m = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(m)
    for cx, cy, r in circles:
        d.ellipse(((cx - r) * W, (cy - r) * W, (cx + r) * W, (cy + r) * W), fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(blur * W)), dtype=float) / 255


YY, XX = np.mgrid[0:W, 0:W] / W


def cloud_layer(cx=0.5, cy=0.52, k=1.0, dark=0.0, seed=1):
    circles = [(cx - 0.20 * k, cy + 0.04 * k, 0.15 * k), (cx - 0.04 * k, cy - 0.07 * k, 0.20 * k),
               (cx + 0.16 * k, cy - 0.02 * k, 0.17 * k), (cx + 0.28 * k, cy + 0.07 * k, 0.11 * k),
               (cx - 0.33 * k, cy + 0.09 * k, 0.09 * k), (cx + 0.05 * k, cy + 0.09 * k, 0.17 * k)]
    base = blob_mask(circles, 0.035)
    n = fbm(W, 6, seed)
    alpha = np.clip(base * (0.75 + 0.8 * n) - 0.05, 0, 1)
    alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * SS)),
                       dtype=float) / 255
    # lit from above: brighter top, greyer belly
    shade = 1.0 - 0.45 * np.clip((YY - (cy - 0.15 * k)) / (0.35 * k), 0, 1)
    lum = (shade * (0.8 + 0.3 * n)) * (1 - dark)
    return alpha, lum


def over(dst_a, dst_l, a, l):
    out_a = a + dst_a * (1 - a)
    out_l = np.where(out_a > 0, (l * a + dst_l * dst_a * (1 - a)) / np.maximum(out_a, 1e-6), 0)
    return out_a, out_l


def glow(cx, cy, r, spread, strength=0.6):
    d = np.hypot(XX - cx, YY - cy)
    return strength * np.exp(-np.clip(d - r, 0, None) / spread)


def sun_layer(cx=0.5, cy=0.5, r=0.22):
    d = np.hypot(XX - cx, YY - cy)
    disk = np.clip((r - d) / 0.01, 0, 1)
    a = np.maximum(disk, glow(cx, cy, r, 0.07, 0.8))
    lum = np.where(d < r, 1.0, 0.95)
    return a, lum


def moon_layer(cx=0.5, cy=0.5, r=0.24, seed=3):
    d = np.hypot(XX - cx, YY - cy)
    disk = np.clip((r - d) / 0.008, 0, 1)
    n = fbm(W, 6, seed)
    # maria: large dark patches; craters: small rings
    maria = np.clip((fbm(W, 3, seed + 10) - 0.42) * 2.5, 0, 1)
    lum = 0.92 - 0.35 * maria - 0.12 * n
    r2 = np.random.default_rng(seed)
    for _ in range(14):
        ang, rad = r2.random() * 2 * math.pi, math.sqrt(r2.random()) * r * 0.85
        ccx, ccy, cr = cx + math.cos(ang) * rad, cy + math.sin(ang) * rad, r * (0.04 + 0.1 * r2.random())
        dc = np.hypot(XX - ccx, YY - ccy)
        lum -= 0.10 * np.clip(1 - dc / cr, 0, 1) ** 0.5
    limb = 1.0
    lum = np.clip(lum * limb, 0.35, 1)
    a = np.maximum(disk, glow(cx, cy, r, 0.05, 0.55))
    lum = np.where(d < r - 0.004, lum, 0.85)
    return a, lum


def streaks(a, l, count, length, slant, top, seed, snow=False):
    m = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(m)
    r = np.random.default_rng(seed)
    for _ in range(count):
        x, y = 0.18 + 0.64 * r.random(), top + 0.25 * r.random()
        if snow:
            rr = (0.010 + 0.012 * r.random()) * W
            d.ellipse((x * W - rr, y * W - rr, x * W + rr, y * W + rr), fill=int(200 + 55 * r.random()))
        else:
            ln = length * (0.6 + 0.8 * r.random())
            d.line((x * W, y * W, (x - slant) * W, (y + ln) * W), fill=int(90 + 90 * r.random()),
                   width=max(2, int(0.008 * W)))
    sa = np.asarray(m.filter(ImageFilter.GaussianBlur((2.0 if snow else 1.4) * SS)), dtype=float) / 255
    sa = np.clip(sa * 1.6, 0, 1)
    return over(a, l, sa, np.ones_like(sa) * 0.95)


def bolt(a, l):
    m = Image.new("L", (W, W), 0)
    pts = [(0.52, 0.56), (0.42, 0.75), (0.50, 0.75), (0.43, 0.93), (0.62, 0.69), (0.53, 0.69), (0.60, 0.56)]
    ImageDraw.Draw(m).polygon([(x * W, y * W) for x, y in pts], fill=255)
    core = np.asarray(m.filter(ImageFilter.GaussianBlur(0.6 * SS)), dtype=float) / 255
    halo = np.asarray(m.filter(ImageFilter.GaussianBlur(6 * SS)), dtype=float) / 255 * 0.8
    a, l = over(a, l, halo, np.ones_like(halo))
    return over(a, l, core, np.ones_like(core))


def fog_layer(seed=5):
    n = fbm(W, 5, seed)
    bands = sum(np.exp(-((YY - y) / 0.035) ** 2) for y in (0.30, 0.42, 0.54, 0.66, 0.78))
    edge = np.clip(1 - np.abs(XX - 0.5) / 0.42, 0, 1) ** 0.6
    a = np.clip(bands * edge * (0.45 + 0.6 * n), 0, 0.9)
    return a, np.ones_like(a) * 0.85


def wind_layer():
    m = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(m)
    for y, x0, x1, curl in ((0.36, 0.14, 0.78, 1), (0.50, 0.08, 0.86, 1), (0.64, 0.20, 0.70, -1)):
        pts = [(x * W, (y + 0.03 * math.sin((x - x0) * 9)) * W) for x in np.linspace(x0, x1, 40)]
        d.line(pts, fill=230, width=int(0.022 * W), joint="curve")
        cx, cy, r = x1, y - 0.06 * curl, 0.06
        d.arc(((cx - r) * W, (cy - r) * W, (cx + r) * W, (cy + r) * W),
              90 if curl > 0 else 180, 360 if curl > 0 else 450, fill=230, width=int(0.022 * W))
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(1.5 * SS)), dtype=float) / 255
    return a, np.ones_like(a)


def empty():
    return np.zeros((W, W)), np.zeros((W, W))


def save(a, l, name):
    to_img(a, l).resize((N, N), Image.LANCZOS).save(os.path.join(OUT, name + ".png"), optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    save(*sun_layer(), "wxl_sun")
    save(*moon_layer(), "wxl_moon")
    save(*cloud_layer(seed=1), "wxl_cloud")
    a, l = sun_layer(0.64, 0.36, 0.16); a, l = over(a, l, *cloud_layer(0.46, 0.60, 0.8, seed=2))
    save(a, l, "wxl_partly_day")
    a, l = moon_layer(0.64, 0.36, 0.17, seed=4); a, l = over(a, l, *cloud_layer(0.46, 0.60, 0.8, seed=2))
    save(a, l, "wxl_partly_night")
    a, l = cloud_layer(cy=0.42, dark=0.25, seed=6); a, l = streaks(a, l, 34, 0.09, 0.035, 0.56, 11)
    save(a, l, "wxl_rain")
    a, l = cloud_layer(cy=0.42, dark=0.1, seed=7); a, l = streaks(a, l, 18, 0, 0, 0.58, 12, snow=True)
    save(a, l, "wxl_snow")
    a, l = cloud_layer(cy=0.40, dark=0.45, seed=8); a, l = bolt(a, l)
    save(a, l, "wxl_storm")
    save(*fog_layer(), "wxl_fog")
    save(*wind_layer(), "wxl_wind")
    a, l = cloud_layer(seed=9); save(a * 0.35, l, "wxl_unknown")   # faint cloud: no data yet


if __name__ == "__main__":
    main()

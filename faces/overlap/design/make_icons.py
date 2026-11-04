#!/usr/bin/env python3
"""Draws the small icons Overlap uses (heart + weather) into res/drawable-nodpi.
White-on-transparent so the face can tint them; the heart keeps its own colour.
usage: python3 design/make_icons.py     (needs Pillow)
"""
import math, os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "res", "drawable-nodpi")
SS, N = 8, 30          # supersample, final size (px)
W = N * SS
WHITE = (255, 255, 255, 255)


def canvas():
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save(im, name, size=N):
    im.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name + ".png"), optimize=True)


def s(v):
    return v * W


def cloud(d, ox=0.0, oy=0.0, k=1.0, fill=WHITE):
    for cx, cy, r in ((0.36, 0.56, 0.17), (0.56, 0.46, 0.22), (0.74, 0.60, 0.14)):
        cx, cy, r = ox + cx * k, oy + cy * k, r * k
        d.ellipse((s(cx - r), s(cy - r), s(cx + r), s(cy + r)), fill=fill)
    d.rounded_rectangle((s(ox + 0.20 * k), s(oy + 0.55 * k), s(ox + 0.88 * k), s(oy + 0.74 * k)),
                        radius=s(0.09 * k), fill=fill)


def sun(d, cx=0.5, cy=0.5, r=0.19, ray=0.13):
    d.ellipse((s(cx - r), s(cy - r), s(cx + r), s(cy + r)), fill=WHITE)
    for i in range(8):
        a = i * math.pi / 4
        x1, y1 = cx + math.cos(a) * (r + 0.07), cy + math.sin(a) * (r + 0.07)
        x2, y2 = cx + math.cos(a) * (r + 0.07 + ray), cy + math.sin(a) * (r + 0.07 + ray)
        d.line((s(x1), s(y1), s(x2), s(y2)), fill=WHITE, width=int(s(0.075)))


def drops(d, xs, y0=0.80, ln=0.14):
    for x in xs:
        d.line((s(x), s(y0), s(x - 0.05), s(y0 + ln)), fill=WHITE, width=int(s(0.07)))


def main():
    im, d = canvas(); sun(d); save(im, "wx_sun")
    im, d = canvas()
    d.ellipse((s(0.18), s(0.15), s(0.82), s(0.79)), fill=WHITE)
    d.ellipse((s(0.38), s(0.05), s(0.98), s(0.65)), fill=(0, 0, 0, 0))
    save(im, "wx_moon")
    im, d = canvas(); cloud(d, 0, 0.02); save(im, "wx_cloud")
    im, d = canvas(); sun(d, 0.36, 0.34, 0.14, 0.08); cloud(d, 0.10, 0.12, 0.92); save(im, "wx_partly")
    im, d = canvas(); cloud(d, 0, -0.12); drops(d, (0.38, 0.56, 0.74), 0.66, 0.2); save(im, "wx_rain")
    im, d = canvas(); cloud(d, 0, -0.12)
    for x in (0.36, 0.56, 0.76):
        d.ellipse((s(x - 0.05), s(0.74), s(x + 0.05), s(0.84)), fill=WHITE)
    save(im, "wx_snow")
    im, d = canvas(); cloud(d, 0, -0.12)
    d.polygon([(s(0.56), s(0.58)), (s(0.40), s(0.80)), (s(0.52), s(0.80)), (s(0.44), s(0.98)),
               (s(0.66), s(0.72)), (s(0.54), s(0.72)), (s(0.62), s(0.58))], fill=WHITE)
    save(im, "wx_storm")
    im, d = canvas()
    for y, x0, x1 in ((0.34, 0.14, 0.86), (0.52, 0.22, 0.80), (0.70, 0.14, 0.86)):
        d.line((s(x0), s(y), s(x1), s(y)), fill=WHITE, width=int(s(0.08)))
    save(im, "wx_fog")
    im, d = canvas()
    for y, x1 in ((0.36, 0.70), (0.54, 0.86), (0.72, 0.60)):
        d.line((s(0.12), s(y), s(x1), s(y)), fill=WHITE, width=int(s(0.08)))
    d.arc((s(0.58), s(0.22), s(0.86), s(0.50)), 180, 90, fill=WHITE, width=int(s(0.08)))
    save(im, "wx_wind")
    # heart (own colour, not tinted)
    im, d = canvas()
    red = (255, 90, 110, 255)
    d.ellipse((s(0.08), s(0.14), s(0.54), s(0.60)), fill=red)
    d.ellipse((s(0.46), s(0.14), s(0.92), s(0.60)), fill=red)
    d.polygon([(s(0.11), s(0.46)), (s(0.89), s(0.46)), (s(0.5), s(0.90))], fill=red)
    save(im, "ic_heart", 44)
    # setting icons for "Stress level words": a mini watch face with the chosen slot lit
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_watchface as G
    for oid, _, icon in G.LEVEL_OPTIONS:
        im, d = canvas()
        d.ellipse((s(0.06), s(0.06), s(0.94), s(0.94)), outline=(170, 170, 170, 255), width=int(s(0.05)))
        d.rounded_rectangle((s(0.38), s(0.28), s(0.62), s(0.62)), radius=s(0.08), fill=(110, 110, 110, 255))
        for sid, _, kind, cx, cy, *_ in G.SLOTS:
            x, y = 0.5 + (cx - 225) / 450 * 0.84, 0.5 + (cy - 225) / 450 * 0.84
            on = oid == f"s{sid}"
            r = 0.11 if on else 0.06
            d.ellipse((s(x - r), s(y - r), s(x + r), s(y + r)),
                      fill=(120, 205, 255, 255) if on else (110, 110, 110, 255))
        if oid == "off":
            d.line((s(0.22), s(0.78), s(0.78), s(0.22)), fill=(255, 110, 110, 255), width=int(s(0.07)))
        save(im, icon, 96)
    print("icons written to", os.path.normpath(OUT))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Draws the small icons Overlap uses (heart + weather) into res/drawable-nodpi.
White-on-transparent so the face can tint them; the heart keeps its own colour.
usage: python3 design/make_icons.py     (needs Pillow)
"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
from weather_icons import canvas, s, draw_weather, save as save_to

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "res", "drawable-nodpi")


def save(im, name, size):
    save_to(im, OUT, name, size)


def main():
    draw_weather(OUT)
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

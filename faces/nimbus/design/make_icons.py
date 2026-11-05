#!/usr/bin/env python3
"""Draws Nimbus's small icons into res/drawable-nodpi. White on transparent (tinted by the face).
The small forecast icons wx_*.png come from tools/weather_icons.py (draw_weather).
usage: python3 design/make_icons.py     (needs Pillow)
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "res", "drawable-nodpi")
SS = 8


def bolt(w=14, h=16):
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    pts = [(0.62, 0.0), (0.08, 0.58), (0.46, 0.58), (0.34, 1.0), (0.92, 0.38), (0.54, 0.38), (0.70, 0.0)]
    ImageDraw.Draw(im).polygon([(x * w * SS, y * h * SS) for x, y in pts], fill=(255, 255, 255, 255))
    im.resize((w, h), Image.LANCZOS).save(os.path.join(OUT, "ic_bolt.png"), optimize=True)


if __name__ == "__main__":
    bolt()

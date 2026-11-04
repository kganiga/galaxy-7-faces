#!/usr/bin/env python3
"""Renders the always-on (ambient) digit bitmaps for Overlap.

Ambient mode uses outline-only digits: an opaque black fill with a thin grey stroke.
The black fill hides the outline of the digit underneath where digits overlap, so the
stacked look survives while only ~5% of pixels are lit (filled digits light ~25%).

Writes res/drawable-nodpi/amb_{a,b}_{0..9}.png and prints the geometry that
gen_watchface.py must use (AMB_W, AMB_H, AMB_TOP).
usage: python3 make_ambient_digits.py   (run from anywhere)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_watchface as G

RES = os.path.join(HERE, "..", "src", "main", "res")
FONT = os.path.join(RES, "font", "fredoka_bold.ttf")
OUT = os.path.join(RES, "drawable-nodpi")
SS = 4                       # supersampling for smooth strokes
STROKE = G.AMB_STROKE
TONES = {"a": G.AMB_TONES[0], "b": G.AMB_TONES[1]}


def geometry():
    f = ImageFont.truetype(FONT, G.SIZE)
    asc, _ = f.getmetrics()
    boxes = [f.getbbox(d, anchor="ms") for d in "0123456789"]
    top = min(b[1] for b in boxes) - STROKE - 1      # relative to baseline (negative)
    bot = max(b[3] for b in boxes) + STROKE + 1
    half_w = max(max(-b[0], b[2]) for b in boxes) + STROKE + 1
    w = 2 * half_w
    h = bot - top
    return {"AMB_W": w, "AMB_H": h, "AMB_TOP": asc + top, "_baseline": -top}


def main():
    g = geometry()
    for k in ("AMB_W", "AMB_H", "AMB_TOP"):
        if getattr(G, k) != g[k]:
            sys.exit(f"gen_watchface.py has {k}={getattr(G, k)}, expected {g[k]}: update it")
    f = ImageFont.truetype(FONT, G.SIZE * SS)
    W, H, base = g["AMB_W"] * SS, g["AMB_H"] * SS, g["_baseline"] * SS
    for tone, hexcol in TONES.items():
        rgb = tuple(int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
        for d in "0123456789":
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((W / 2, base), d, font=f, anchor="ms",
                                    fill=(0, 0, 0, 255), stroke_width=STROKE * SS,
                                    stroke_fill=rgb + (255,))
            # re-fill the glyph interior black (stroke drawn centred on the outline)
            ImageDraw.Draw(im).text((W / 2, base), d, font=f, anchor="ms", fill=(0, 0, 0, 255))
            im = im.resize((g["AMB_W"], g["AMB_H"]), Image.LANCZOS)
            im.save(os.path.join(OUT, f"amb_{tone}_{d}.png"), optimize=True)
    print("ok", g)


if __name__ == "__main__":
    main()

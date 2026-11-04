#!/usr/bin/env python3
"""Approximate PIL mock-up of the Overlap face (same geometry/colours as gen_watchface.py).
Not the on-watch renderer: font placement inside WFF text boxes may differ by a few px.
usage: render_preview.py FONT.ttf OUT.png [theme_index] [ambient 0|1] [size]
"""
import math, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __import__("os").path.dirname(__file__))
import gen_watchface as G

font_path, out = sys.argv[1], sys.argv[2]
theme = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ambient = len(sys.argv) > 4 and sys.argv[4] == "1"
final = int(sys.argv[5]) if len(sys.argv) > 5 else 450
SS = 4  # supersample
W = 450 * SS
cols = [tuple(int(h[i:i + 2], 16) for i in (3, 5, 7)) for h in G.THEMES[theme][2]]

img = Image.new("RGB", (W, W), "black")
d = ImageDraw.Draw(img)

def F(sz):
    return ImageFont.truetype(font_path, int(sz * SS))

# ---- digits: glyph sits on baseline = box top + ascent (box height = line height)
digits = {"hh_10": "1", "hh_1": "0", "mm_10": "0", "mm_1": "8"}
fd = F(G.SIZE)
asc, _ = fd.getmetrics()
res = __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "src", "main", "res")
for fmt, col, row, tone in G.DIGITS:
    ch = digits[fmt]
    cx = G.COL_X[col] * SS
    top = G.ROW_Y[row] * SS
    if ambient:  # outline bitmaps, exactly as the watch uses them
        bm = Image.open(f"{res}/drawable-nodpi/amb_{'ab'[tone]}_{ch}.png").convert("RGBA")
        bm = bm.resize((G.AMB_W * SS, G.AMB_H * SS), Image.LANCZOS)
        img.paste(bm, (int(cx - G.AMB_W * SS / 2), int(top + G.AMB_TOP * SS)), bm)
        continue
    for dx, colr in ((G.SHADOW * SS, (0, 0, 0)), (0, cols[tone])):
        d.text((cx + dx, top + asc + dx), ch, font=fd, fill=colr, anchor="ms")

accent = cols[2] if not ambient else tuple(int(v * 150 / 255) for v in cols[2])

# ---- curved date (glyphs centred on radius ~ 200)
date = "WED, NOV 4"
fdate = F(30)
r = 200 * SS
widths = [fdate.getlength(ch) * 1.04 for ch in date]
total = sum(widths)
ang = -total / r / 2  # radians, 0 = 12 o'clock
for ch, w in zip(date, widths):
    a = ang + w / r / 2
    tile = Image.new("L", (60 * SS, 60 * SS), 0)
    ImageDraw.Draw(tile).text((30 * SS, 30 * SS), ch, font=fdate, fill=255, anchor="mm")
    tile = tile.rotate(-math.degrees(a), resample=Image.BICUBIC)
    x = W / 2 + r * math.sin(a) - 30 * SS
    y = W / 2 - r * math.cos(a) - 30 * SS
    img.paste(Image.new("RGB", tile.size, accent), (int(x), int(y)), tile)
    ang += w / r

if not ambient:
    # ---- side complications (rotated text)
    fs = F(30)
    for text, cx, angle in (("78%", 40, -90), ("6214", 410, 90)):
        tile = Image.new("L", (G.SIDE_W * SS, G.SIDE_H * SS), 0)
        ImageDraw.Draw(tile).text((G.SIDE_W * SS / 2, 19 * SS), text, font=fs, fill=255, anchor="mm")
        tile = tile.rotate(-angle, expand=True, resample=Image.BICUBIC)
        img.paste(Image.new("RGB", tile.size, cols[2]),
                  (int(cx * SS - tile.size[0] / 2), int(225 * SS - tile.size[1] / 2)), tile)
    # ---- bottom: built-in weather (EMPTY slot)
    bx, by = G.BOT_X * SS, G.BOT_Y * SS
    d.ellipse((bx + 41 * SS, by + 17 * SS, bx + 55 * SS, by + 31 * SS), outline=cols[1], width=3 * SS)
    d.text((bx + 62 * SS, by + 24 * SS), "21°", font=F(30), fill=cols[2], anchor="lm")

# circular mask
mask = Image.new("L", (W, W), 0)
ImageDraw.Draw(mask).ellipse((0, 0, W - 1, W - 1), fill=255)
bg = Image.new("RGB", (W, W), "black")
bg.paste(img, (0, 0), mask)
bg.resize((final, final), Image.LANCZOS).save(out)

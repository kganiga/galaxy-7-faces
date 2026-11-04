#!/usr/bin/env python3
"""Approximate PIL mock-up of the Overlap face (same geometry/colours as gen_watchface.py).
Not the on-watch renderer: font placement inside WFF text boxes may differ by a few px.
usage: render_preview.py FONT.ttf OUT.png [theme_index] [ambient 0|1] [size] [raining 0|1]
"""
import math, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __import__("os").path.dirname(__file__))
import gen_watchface as G

font_path, out = sys.argv[1], sys.argv[2]
theme = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ambient = len(sys.argv) > 4 and sys.argv[4] == "1"
final = int(sys.argv[5]) if len(sys.argv) > 5 else 450
rain = len(sys.argv) > 6 and sys.argv[6] == "1"
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

# ---- curved date, split around 12 o'clock (glyphs centred on radius ~ 200)
fdate = F(30)
r = 200 * SS


def arc_text(text, edge_deg, align):
    widths = [fdate.getlength(ch) * 1.04 for ch in text]
    total = sum(widths)
    edge = math.radians(edge_deg)
    ang = edge - total / r if align == "END" else edge
    for ch, w in zip(text, widths):
        a = ang + w / r / 2
        tile = Image.new("L", (60 * SS, 60 * SS), 0)
        ImageDraw.Draw(tile).text((30 * SS, 30 * SS), ch, font=fdate, fill=255, anchor="mm")
        tile = tile.rotate(-math.degrees(a), resample=Image.BICUBIC)
        x = W / 2 + r * math.sin(a) - 30 * SS
        y = W / 2 - r * math.cos(a) - 30 * SS
        img.paste(Image.new("RGB", tile.size, accent), (int(x), int(y)), tile)
        ang += w / r


arc_text("WED", -G.DATE_GAP, "END")
arc_text("NOV 4", G.DATE_GAP, "START")


def paste_icon(name, cx, cy, size, color=None):
    ic = Image.open(f"{res}/drawable-nodpi/{name}.png").convert("RGBA").resize((size * SS, size * SS), Image.LANCZOS)
    if color:
        solid = Image.new("RGBA", ic.size, color + (255,))
        solid.putalpha(ic.getchannel("A")); ic = solid
    img.paste(ic, (int(cx * SS - ic.size[0] / 2), int(cy * SS - ic.size[1] / 2)), ic)


if rain and not ambient:
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for k, (x, y0, ln, sec) in enumerate(G.RAIN_DROPS):
        y = (y0 + 560 * ((k * 0.37) % 1)) % 450
        ld.line((x * SS + 2 * SS, y * SS, x * SS + 2 * SS, (y + ln) * SS), fill=cols[1] + (110,), width=3 * SS)
    base = img.convert("RGBA"); base.alpha_composite(lay)
    # rain sits behind everything: redraw digits on top
    img.paste(base.convert("RGB"))
    d = ImageDraw.Draw(img)
    for fmt, col, row, tone in G.DIGITS:
        for dx, colr in ((G.SHADOW * SS, (0, 0, 0)), (0, cols[tone])):
            d.text((G.COL_X[col] * SS + dx, G.ROW_Y[row] * SS + asc + dx), digits[fmt], font=fd, fill=colr, anchor="ms")

if not ambient:
    slots = {s[0]: s for s in G.SLOTS}
    # ---- side complications (rotated text): battery as ranged value, steps as text
    for sid, text in ((0, "78%"), (1, "6214")):
        _, _, kind, cx, cy, angle, _, _ = slots[sid]
        sw, sh = G.SIZES[kind]
        tile = Image.new("L", (sw * SS, sh * SS), 0)
        td = ImageDraw.Draw(tile)
        td.text((sw * SS / 2, (18 if sid == 0 else 22) * SS), text, font=F(30), fill=255, anchor="mm")
        tile = tile.rotate(-angle, expand=True, resample=Image.BICUBIC)
        img.paste(Image.new("RGB", tile.size, cols[2]),
                  (int(cx * SS - tile.size[0] / 2), int(cy * SS - tile.size[1] / 2)), tile)
        if sid == 0:  # progress bar, rotated with the slot
            bw = 64
            bar = Image.new("RGBA", (sw * SS, sh * SS), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
            x0 = (sw - bw) / 2 * SS
            bd.rounded_rectangle((x0, 39 * SS, x0 + bw * SS, 44 * SS), radius=2.5 * SS, fill=(255, 255, 255, 51))
            bd.rounded_rectangle((x0, 39 * SS, x0 + bw * 0.78 * SS, 44 * SS), radius=2.5 * SS, fill=cols[1] + (255,))
            bar = bar.rotate(-angle, expand=True, resample=Image.BICUBIC)
            img.paste(bar, (int(cx * SS - bar.size[0] / 2), int(cy * SS - bar.size[1] / 2)), bar)
    # ---- bottom: built-in weather (EMPTY slot), icon + temperature centred
    _, _, kind, cx, cy, _, _, _ = slots[2]
    ft = F(30); label = " 21°"; tw = ft.getlength(label) / SS; total = 30 + tw
    left = cx - total / 2
    paste_icon("wx_rain" if rain else "wx_partly", left + 15, cy, 30, cols[1])
    d.text(((left + 30) * SS, cy * SS), label, font=ft, fill=cols[2], anchor="lm")
    # ---- bottom-left: heart rate (EMPTY slot) ; bottom-right: sunrise/sunset short text
    for sid in (3, 4):
        _, _, kind, cx, cy, _, _, _ = slots[sid]
        if sid == 3:
            paste_icon("ic_heart", cx, cy - 12, 22)
            d.text((cx * SS, (cy + 10) * SS), "72", font=F(17), fill=cols[2], anchor="mm")
        else:
            paste_icon("wx_sun", cx, cy - 12, 20, cols[2])
            d.text((cx * SS, (cy + 10) * SS), "6:42", font=F(17), fill=cols[2], anchor="mm")

# circular mask
mask = Image.new("L", (W, W), 0)
ImageDraw.Draw(mask).ellipse((0, 0, W - 1, W - 1), fill=255)
bg = Image.new("RGB", (W, W), "black")
bg.paste(img, (0, 0), mask)
bg.resize((final, final), Image.LANCZOS).save(out)

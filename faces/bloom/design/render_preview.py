#!/usr/bin/env python3
"""Approximate Pillow render of Bloom, for the picker preview and the docs images.

Not the real WFF renderer: it reuses gen_watchface.py's geometry and assets, so layout
changes show up here, but font hinting and vertical text placement are close, not exact.
usage: python3 design/render_preview.py   -> res/drawable-nodpi/preview.png, mipmap ic_launcher,
                                              docs/preview.png, docs/themes.png, docs/ambient.png
"""
import math, os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_watchface as g   # also puts tools/ on sys.path
import preview
from preview import col

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "src", "main", "res")
DOCS = os.path.join(ROOT, "docs")
DIGITS = os.path.join(RES, "font", g.DIGITS + ".ttf")
TEXT = os.path.join(RES, "font", g.TEXT + ".ttf")
SS = 2
N = 450 * SS


def png(res):
    return os.path.join(RES, "drawable-nodpi", res + ".png")


def text(d, x, y, w, h, t, size, color, path=TEXT):
    preview.text_box(d, path, SS, x, y, w, h, t, size, color)


def line(d, cx, cy, w, t, size, color, h=30):
    text(d, cx - w / 2, cy - h / 2, w, h, t, size, color)


def rotated_layer(w, h, angle, draw):
    """Draw into a w x h tile, rotate it like a WFF part (clockwise, about its centre)."""
    tile = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw(ImageDraw.Draw(tile))
    return tile.rotate(-angle, resample=Image.BICUBIC, expand=True)


def paste_centred(im, tile, cx, cy):
    im.alpha_composite(tile, (round(cx * SS - tile.width / 2), round(cy * SS - tile.height / 2)))


def clock(d, color, sample):
    for (fmt, cy), t in zip(g.ROWS, (sample[:2], sample[3:5])):
        size = g.DIGIT_SIZE
        top = round(cy + g.DIGIT_H * size / 2 - g.ASC * size)
        f = preview.font(DIGITS, size, SS)
        # WFF: baseline at box top + ascent
        d.text((g.CX * SS, (top + g.ASC * size) * SS), t, font=f, fill=color, anchor="ms")


def blob(im, res, tint):
    x, y = g.BLOB_C[0] - g.BLOB_IMG // 2, g.BLOB_C[1] - g.BLOB_IMG // 2
    preview.paste_icon(im, png(res), SS, x, y, g.BLOB_IMG, g.BLOB_IMG, tint)


def render(theme=0, sample="08:57", weather="wx_moon", city=("London", "4:27 PM"), frac=0.56):
    cs = [col(x) for x in g.THEMES[theme][2]]
    im = Image.new("RGBA", (N, N), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    # arc track
    r = (g.ARC_R + g.ARC_T / 2) * SS     # PIL grows the stroke inwards from the box
    box = (g.CX * SS - r, g.CY * SS - r, g.CX * SS + r, g.CY * SS + r)
    d.arc(box, g.ARC_A1 - 90, g.ARC_A0 - 90, fill=cs[2], width=g.ARC_T * SS)   # PIL 0 = 3 o'clock
    for a in (g.ARC_A1, g.ARC_A0):   # round caps
        x, y = preview_point(g.ARC_R, a)
        d.ellipse((x - g.ARC_T / 2 * SS, y - g.ARC_T / 2 * SS, x + g.ARC_T / 2 * SS, y + g.ARC_T / 2 * SS), fill=cs[2])
    # pods and edges
    for side, ((px, py), (ex, ey)) in enumerate(zip(g.POD_C, g.EAR_C)):
        sign = -1 if side == 0 else 1
        P = g.POD
        paste_centred(im, rotated_layer(P["w"], P["h"], sign * P["angle"], lambda dd: dd.rounded_rectangle(
            (0, 0, P["w"] * SS - 1, P["h"] * SS - 1), radius=P["r"] * SS, fill=cs[2])), px, py)
        E = g.EAR
        paste_centred(im, rotated_layer(E["w"], E["h"], sign * E["angle"], lambda dd: dd.ellipse(
            (0, 0, E["w"] * SS - 1, E["h"] * SS - 1), fill=cs[3])), ex, ey)
    blob(im, "scallop", cs[0])
    d = ImageDraw.Draw(im)
    clock(d, cs[1], sample)
    # pods: weather (left), date (right)
    L, R = g.POD_SLOTS
    lx, ly = L["box"][:2]
    preview.paste_icon(im, png(weather), SS, lx + L["up"][0] - 14, ly + L["up"][1] - 14, 28, 28, cs[3])
    line(d, lx + L["low"][0], ly + L["low"][1], 84, "23°", 24, cs[0])
    rx, ry = R["box"][:2]
    line(d, rx + R["up"][0], ry + R["up"][1], 84, "Fri", 24, cs[0])
    line(d, rx + R["low"][0], ry + R["low"][1], 84, "15", 24, cs[3])
    # tiles
    T = g.TILE
    x0 = g.TILE_X[0]
    d.rounded_rectangle((x0 * SS, g.TILE_Y * SS, (x0 + T) * SS - 1, (g.TILE_Y + T) * SS - 1), radius=g.TILE_R * SS, fill=cs[3])
    line(d, x0 + T / 2, g.TILE_Y + g.TITLE_CY, T - 8, "Steps", 21, cs[1])
    line(d, x0 + T / 2, g.TILE_Y + g.VALUE_CY, T - 8, "4132", 20, cs[1])
    x1 = g.TILE_X[1]
    preview.paste_icon(im, png("clover"), SS, x1, g.TILE_Y, T, T, cs[4])
    d = ImageDraw.Draw(im)
    line(d, x1 + T / 2, g.TILE_Y + g.TITLE_CY, T - 8, city[0], 21, cs[1])
    line(d, x1 + T / 2, g.TILE_Y + g.VALUE_CY, T - 8, city[1], 20, cs[1])
    # arc dot
    x, y = preview_point(g.ARC_R, g.ARC_A0 - (g.ARC_A0 - g.ARC_A1) * frac)
    rr = g.ARC_DOT / 2 * SS
    d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=cs[4])
    return preview.finish(im, SS)


def preview_point(r, a):
    return ((g.CX + r * math.sin(math.radians(a))) * SS, (g.CY - r * math.cos(math.radians(a))) * SS)


def render_ambient(sample="08:57"):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 255))
    blob(im, "scallop_line", col(g.AOD_DIM))
    d = ImageDraw.Draw(im)
    clock(d, col(g.AOD_INK), sample)
    text(d, g.CX - 80, g.AOD_DATE_Y, 160, 30, "Fri 15", 22, col(g.AOD_DIM))
    return preview.finish(im, SS)


def main():
    os.makedirs(DOCS, exist_ok=True)
    main_img = render()
    main_img.convert("RGB").save(os.path.join(RES, "drawable-nodpi", "preview.png"), optimize=True)
    main_img.resize((192, 192), Image.LANCZOS).save(os.path.join(RES, "mipmap-nodpi", "ic_launcher.png"), optimize=True)
    main_img.save(os.path.join(DOCS, "preview.png"))
    samples = ["08:57", "10:42", "11:09", "07:30", "12:15", "09:24", "06:48", "02:36", "05:51", "03:03", "04:20", "01:58"]
    preview.theme_sheet(lambda i: render(i, samples[i]), len(g.THEMES)).save(os.path.join(DOCS, "themes.png"), optimize=True)
    amb = render_ambient()
    amb.save(os.path.join(DOCS, "ambient.png"))
    print(f"ambient lit pixels: {preview.lit_fraction(amb) * 100:.1f}% of the dial")


if __name__ == "__main__":
    main()

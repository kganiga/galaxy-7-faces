"""Shared Pillow helpers for the faces' design/render_preview.py mock-ups.

Coordinates are in face pixels (450x450 canvas); ss is the supersampling factor the
caller draws at. Colours are WFF '#AARRGGBB' strings converted with col().
"""
import math
from PIL import Image, ImageDraw, ImageFont

_FONTS = {}


def col(h):
    """'#AARRGGBB' -> (r, g, b, a)."""
    h = h.lstrip("#")
    a, rgb = int(h[:2], 16), h[2:]
    return tuple(int(rgb[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def font(path, size, ss):
    key = (path, int(size * ss))
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, key[1])
    return _FONTS[key]


def text_box(d, path, ss, x, y, w, h, t, size, color, align="CENTER"):
    """Text vertically centred in the box, aligned like WFF's Text align."""
    f = font(path, size, ss)
    ax = {"CENTER": (x + w / 2, "mm"), "START": (x, "lm"), "END": (x + w, "rm")}[align]
    d.text((ax[0] * ss, (y + h / 2) * ss), t, font=f, fill=color, anchor=ax[1])


def paste_icon(im, png, ss, x, y, w, h, tint=None):
    """Paste a PNG resource scaled to the box; tint replaces its colour, keeping its alpha."""
    ic = Image.open(png).convert("RGBA").resize((round(w * ss), round(h * ss)), Image.LANCZOS)
    if tint:
        solid = Image.new("RGBA", ic.size, tint[:3] + (255,))
        solid.putalpha(ic.getchannel("A"))
        ic = solid
    im.alpha_composite(ic, (round(x * ss), round(y * ss)))


def finish(im, ss):
    """Clip to the round dial and scale back to 450 px."""
    n = 450 * ss
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, n - 1, n - 1), fill=255)
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out.resize((450, 450), Image.LANCZOS)


def lit_fraction(im):
    """Share of the round dial's pixels that are visibly lit (always-on budget is 15%)."""
    px = im.convert("L").tobytes()
    return sum(1 for p in px if p > 24) / (math.pi * 225 * 225)


def theme_sheet(render, n, cols=4, tile=220, gap=10):
    """Grid of render(i) for themes 0..n-1, on a dark background."""
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tile + gap) + gap, rows * (tile + gap) + gap), (24, 24, 24))
    for i in range(n):
        t = render(i).resize((tile, tile), Image.LANCZOS)
        sheet.paste(t, (gap + (i % cols) * (tile + gap), gap + (i // cols) * (tile + gap)), t)
    return sheet

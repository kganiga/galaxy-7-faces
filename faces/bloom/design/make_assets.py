#!/usr/bin/env python3
"""Makes Bloom's fonts and shape masks. Run from anywhere; only needed when they change.

    python3 design/make_assets.py           # shapes + weather icons (needs Pillow)
    python3 design/make_assets.py fonts     # also re-download and subset the fonts (needs fontTools)

Fonts: Google Sans Flex (SIL OFL 1.1, licenses/GoogleSansFlex-OFL.txt), two static instances
from Google Fonts, subset to what the face draws:
  gsf_digits.ttf    Rounded, Black, 144 pt optical size: the big stacked hours and minutes
  gsf_text.ttf      SemiBold: labels and complication text (Latin, Latin-1, Latin Extended-A)
Shapes are white on transparent; the face tints them with the theme colours.
"""
import math, os, sys, urllib.request
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "src", "main", "res")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
sys.path.insert(0, HERE)
import gen_watchface as g
from weather_icons import draw_weather

CSS = "https://fonts.googleapis.com/css2?family=Google+Sans+Flex:{axes}"
FONTS = {
    "gsf_digits": ("opsz,wght,ROND@144,900,100", "0123456789"),
    "gsf_text": ("wght@600", "".join(map(chr, range(0x20, 0x7F))) + "".join(map(chr, range(0xA0, 0x180))) + "–—‘’“”•…€"),
}
SS = 4


def fonts():
    from fontTools import subset
    for name, (axes, chars) in FONTS.items():
        req = urllib.request.Request(CSS.format(axes=axes), headers={"User-Agent": "Mozilla/5.0"})
        css = urllib.request.urlopen(req).read().decode()
        url = css.split("url(")[1].split(")")[0]
        raw = os.path.join(HERE, name + ".download.ttf")
        urllib.request.urlretrieve(url, raw)
        out = os.path.join(RES, "font", name + ".ttf")
        opts = subset.Options()
        opts.layout_features = ["kern", "tnum"] if name == "gsf_digits" else ["*"]
        opts.name_IDs = ["*"]          # keep the copyright and licence records
        f = subset.load_font(raw, opts)
        sub = subset.Subsetter(opts)
        sub.populate(text=chars)
        sub.subset(f)
        subset.save_font(f, out, opts)
        os.remove(raw)
        print(f"{name}.ttf: {os.path.getsize(out) // 1024} KB")


def polar_mask(size, r_of, stroke=0):
    """White shape whose edge is r_of(theta) (px, centred). stroke>0 draws only the outline."""
    n = size * SS
    pts = []
    for i in range(720):
        t = 2 * math.pi * i / 720
        r = r_of(t) * SS
        pts.append((n / 2 + r * math.sin(t), n / 2 - r * math.cos(t)))
    im = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(im)
    if stroke:
        d.line(pts + [pts[0]], fill=255, width=int(stroke * SS), joint="curve")
    else:
        d.polygon(pts, fill=255)
    out = Image.new("RGBA", (n, n), (255, 255, 255, 0))
    out.putalpha(im)
    return out.resize((size, size), Image.LANCZOS)


def save(im, name):
    im.save(os.path.join(RES, "drawable-nodpi", name + ".png"), optimize=True)


def shapes():
    R, A, N = g.BLOB_R, g.BLOB_WAVE, g.BLOB_LOBES
    size = g.BLOB_IMG
    scallop = lambda t: R + A * math.cos(N * t)
    save(polar_mask(size, scallop), "scallop")
    save(polar_mask(size, lambda t: scallop(t) - g.AOD_LINE / 2, stroke=g.AOD_LINE), "scallop_line")
    # clover: a rounded square with the middle of each side pulled in
    w = g.TILE
    base = lambda t: 1 / (abs(math.sin(t)) ** 4 + abs(math.cos(t)) ** 4) ** 0.25    # squircle
    raw = lambda t: base(t) * (1 - 0.085 * math.cos(4 * t))
    ext = max(raw(t) * max(abs(math.sin(t)), abs(math.cos(t))) for t in [i * math.pi / 720 for i in range(1440)])
    save(polar_mask(w, lambda t: raw(t) / ext * (w / 2 - 0.5)), "clover")


if __name__ == "__main__":
    if "fonts" in sys.argv[1:]:
        fonts()
    shapes()
    draw_weather(os.path.join(RES, "drawable-nodpi"))
    print("assets written to", os.path.normpath(RES))

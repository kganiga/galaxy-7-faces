#!/usr/bin/env python3
"""Approximate PIL render of Nimbus, for the picker preview and the docs images.

Not the real WFF renderer: it reuses gen_watchface.py's geometry so layout changes show
up here, but text placement on curves and font hinting are close, not exact.
usage: python3 design/render_preview.py   -> res/drawable-nodpi/preview.png, mipmap ic_launcher,
                                              docs/preview.png, docs/themes.png, docs/ambient.png
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_watchface as g

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "src", "main", "res")
DOCS = os.path.join(ROOT, "docs")
SS = 2
N = 450 * SS


def col(h):
    h = h.lstrip("#")
    a, rgb = int(h[:2], 16), h[2:]
    return tuple(int(rgb[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def F(size):
    return ImageFont.truetype(g.FONT_FILE, int(size * SS))


def ring_band(d, r, t, color):
    r0, r1 = (r + t / 2) * SS, (r - t / 2) * SS
    c = g.CX * SS
    d.ellipse((c - r0, c - r0, c + r0, c + r0), fill=color)
    d.ellipse((c - r1, c - r1, c + r1, c + r1), fill=(0, 0, 0, 255))


def curved(im, text, ring, a0, a1, size, color, align):
    if not text:
        return
    f = F(size)
    r = (ring["tr"] - ring["vs"] * 0.35) * SS
    total = math.degrees(f.getlength(text) / r)
    start = {"START": a0, "END": a1 - total, "CENTER": (a0 + a1 - total) / 2}[align]
    ang = start
    for ch in text:
        w = f.getlength(ch)
        mid = ang + math.degrees(w / 2 / r)
        tile = Image.new("RGBA", (int(w) + 4 * SS, int(size * 1.6 * SS)), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((tile.width / 2, tile.height / 2), ch, font=f, fill=color, anchor="mm")
        tile = tile.rotate(-mid, resample=Image.BICUBIC, expand=True)
        x = g.CX * SS + r * math.sin(math.radians(mid))
        y = g.CY * SS - r * math.cos(math.radians(mid))
        im.alpha_composite(tile, (int(x - tile.width / 2), int(y - tile.height / 2)))
        ang += math.degrees(w / r)


def text_box(d, x, y, w, h, t, size, color, align="CENTER"):
    f = F(size)
    ax = {"CENTER": (x + w / 2, "mm"), "START": (x, "lm"), "END": (x + w, "rm")}[align]
    d.text((ax[0] * SS, (y + h / 2) * SS), t, font=f, fill=color, anchor=ax[1])


def paste_icon(im, res, x, y, w, h, tint=None):
    ic = Image.open(os.path.join(RES, "drawable-nodpi", res + ".png")).convert("RGBA").resize((w * SS, h * SS), Image.LANCZOS)
    if tint:
        solid = Image.new("RGBA", ic.size, tint[:3] + (255,))
        solid.putalpha(ic.getchannel("A"))
        ic = solid
    im.alpha_composite(ic, (x * SS, y * SS))


def clock(d, size, groups, color, cy, sample):
    digits = iter(sample.replace(":", ""))
    for f, x, y, w, h in g.clock_boxes(size, groups, cy):
        ch = ":" if f == ":" else next(digits)
        text_box(d, x, y, w, h, ch, size, color)


def render(theme=0, art="wxl_partly_day", seconds=True, sample="10:30:00"):
    cs = [col(x) for x in g.THEMES[theme][2]]
    im = Image.new("RGBA", (N, N), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    ring_band(d, g.OUTER["r"], g.OUTER["t"], cs[0])
    ring_band(d, g.INNER["r"], g.INNER["t"], cs[1])
    for ring in (g.OUTER, g.INNER):
        for a in g.DOTS[id(ring)]:
            x = (g.CX + ring["r"] * math.sin(math.radians(a))) * SS
            y = (g.CY - ring["r"] * math.cos(math.radians(a))) * SS
            d.ellipse((x - 3 * SS, y - 3 * SS, x + 3 * SS, y + 3 * SS), outline=(255, 255, 255, 150), width=SS)
    c, r = g.CX * SS, g.DISK_R * SS
    d.ellipse((c - r, c - r, c + r, c + r), fill=(0, 0, 0, 255))
    # lower fade
    fade = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(235 * SS, N):
        t = (y / SS - 235) / 165
        a = 230 * min(t / 0.75, 1) if t < 0.75 else 230 + 25 * min((t - 0.75) / 0.25, 1)
        fd.line((0, y, N, y), fill=(0, 0, 0, int(min(a, 255))))
    for pid, _, ring, (a0, a1), default in g.POSITIONS:
        o = g.OPT[default]
        if o[0] == "none":
            continue
        split, gap = g.ring_split(ring, a0, a1, o[2], o[6])
        curved(im, o[2], ring, a0, split, ring["ls"], col(g.LABEL), "END")
        curved(im, o[6], ring, split + gap, a1, ring["vs"], col(g.WHITE), "START")
    x, y, w, h = g.ART
    paste_icon(im, art, x, y, w, h)
    im.alpha_composite(fade)
    d = ImageDraw.Draw(im)
    # pill
    x, y, w, h = g.PILL
    d.rounded_rectangle((x * SS, y * SS, (x + w) * SS, (y + h) * SS), radius=h * SS // 2,
                        fill=(0, 0, 0, 180), outline=cs[2], width=2 * SS)
    text_box(d, x + 108, y + 2, w - 122, h - 4, "28 MON", 22, (255, 255, 255, 255), "END")
    px, py, pw, ph = g.PILL_SLOT
    paste_icon(im, "wx_sun", px + 4, py + 5, 22, 22, cs[2])
    text_box(d, px + 30, py + 1, pw - 32, ph - 2, "18:49", 22, (255, 255, 255, 255), "START")
    # side complications (sample content)
    for (cx, cy), icon, txt in zip(g.SIDE_C, ("wx_cloud", "wx_wind"), ("1015", "25°")):
        W, H = g.SIDE
        paste_icon(im, icon, cx - 13, cy - H // 2 + 2, 26, 26, (255, 255, 255))
        text_box(d, cx - W // 2, cy - H // 2 + 29, W, 30, txt, 22, (255, 255, 255, 255))
    if seconds:
        clock(d, 62, g.HMS, (255, 255, 255, 255), g.TIME_CY, sample)
    else:
        clock(d, 74, g.HM, (255, 255, 255, 255), g.TIME_CY, sample[:5])
    # battery
    a = g.BATT_ARC
    rb = a["r"] * SS
    box = (c - rb, c - rb, c + rb, c + rb)
    # PIL angles: 0 = 3 o'clock; WFF 0 = 12 o'clock
    d.arc(box, a["a0"] - 90, a["a1"] - 90, fill=(255, 255, 255, 64), width=7 * SS)
    span = (a["a1"] - a["a0"]) * 0.9
    d.arc(box, a["a1"] - 90 - span, a["a1"] - 90, fill=cs[2], width=7 * SS)
    paste_icon(im, "ic_bolt", g.CX - 28, g.BATT_Y + 6, 14, 16, cs[2])
    text_box(d, g.CX - 10, g.BATT_Y, 60, 28, "90", 24, (255, 255, 255, 255), "START")
    return finish(im)


def render_ambient(sample="10:09"):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    grey, dim = col(g.AOD_GREY), col(g.AOD_DIM)
    d.rounded_rectangle((161 * SS, 101 * SS, 289 * SS, 131 * SS), radius=15 * SS, outline=dim, width=int(1.5 * SS))
    text_box(d, 160, 102, 130, 28, "28 MON", 21, grey)
    clock(d, 96, g.HM, grey, 192, sample)
    for cx, icon, temps, day in zip(g.AOD_FC_X, ("wx_sun", "wx_cloud"), ("30 18", "31 19"), ("TUE", "WED")):
        y = g.AOD_FC_Y
        paste_icon(im, icon, cx - 14, y, 28, 28, grey)
        text_box(d, cx - 45, y + 30, 90, 28, temps, 24, grey)
        d.rounded_rectangle(((cx - 27) * SS, (y + 62) * SS, (cx + 27) * SS, (y + 84) * SS), radius=11 * SS,
                            outline=dim, width=int(1.5 * SS))
        text_box(d, cx - 28, y + 62, 56, 22, day, 16, grey)
    text_box(d, g.CX - 40, 380, 80, 26, "90", 20, dim)
    return finish(im)


def finish(im):
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, N - 1, N - 1), fill=255)
    out = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out.resize((450, 450), Image.LANCZOS)


def lit_fraction(im):
    px = im.convert("L").tobytes()
    return sum(1 for p in px if p > 24) / (math.pi * 225 * 225)


def main():
    os.makedirs(DOCS, exist_ok=True)
    main_img = render()
    main_img.convert("RGB").save(os.path.join(RES, "drawable-nodpi", "preview.png"), optimize=True)
    main_img.resize((192, 192), Image.LANCZOS).save(os.path.join(RES, "mipmap-nodpi", "ic_launcher.png"), optimize=True)
    main_img.save(os.path.join(DOCS, "preview.png"))
    arts = ["wxl_cloud", "wxl_moon", "wxl_rain", "wxl_sun", "wxl_partly_night", "wxl_snow",
            "wxl_storm", "wxl_fog", "wxl_partly_day", "wxl_wind", "wxl_cloud", "wxl_moon"]
    sheet = Image.new("RGB", (4 * 230 + 10, 3 * 230 + 10), (24, 24, 24))
    for i in range(len(g.THEMES)):
        t = render(i, arts[i]).resize((220, 220), Image.LANCZOS)
        sheet.paste(t, (10 + (i % 4) * 230, 10 + (i // 4) * 230), t)
    sheet.save(os.path.join(DOCS, "themes.png"), optimize=True)
    amb = render_ambient()
    amb.save(os.path.join(DOCS, "ambient.png"))
    print(f"ambient lit pixels: {lit_fraction(amb) * 100:.1f}% of the dial")


if __name__ == "__main__":
    main()

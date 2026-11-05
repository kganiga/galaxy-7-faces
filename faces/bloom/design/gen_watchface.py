#!/usr/bin/env python3
"""Generates res/raw/watchface.xml for the "Bloom" Watch Face Format (v2) face.

Run from anywhere:
    python3 design/make_assets.py                          # only if shapes/fonts change
    python3 design/gen_watchface.py > src/main/res/raw/watchface.xml
    python3 design/render_preview.py                       # preview.png, launcher icon, docs/*.png
Layout: a scalloped clock with stacked hours over minutes, two side pods (weather, date),
two tiles (a complication and the second time zone) and a progress arc along the bottom.
Every pod, tile and the arc is a complication slot; the built-in content shows when a slot
is empty. Geometry is for the 450x450 round canvas. Angles: 0 = 12 o'clock, clockwise.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import wff
from wff import ind, tmpl, cond, image, MONO, CTEXT, CTITLE, RANGE, GOAL

c = wff.theme
DIGITS = "gsf_digits"      # Google Sans Flex Rounded Black (digits only)
TEXT = "gsf_text"          # Google Sans Flex SemiBold
CX = CY = 225

# Theme colours (WFF allows 5): [0] clock shape, [1] ink (digits, tile text), [2] pods and arc,
# [3] accent (pod edges, date, weather icon, left tile), [4] right tile and arc dot.
THEMES = [
    ("mocha",    "theme_mocha",    ["#FFF7F1CF", "#FF3B2B28", "#FF3E2B27", "#FFD69A66", "#FFF4DEDD"]),
    ("sage",     "theme_sage",     ["#FFE3F0D8", "#FF233226", "#FF2A3A2D", "#FF8DB87F", "#FFDCEBD3"]),
    ("lavender", "theme_lavender", ["#FFECE4FA", "#FF2D2440", "#FF342A4A", "#FFA08ED6", "#FFF1E3F3"]),
    ("ocean",    "theme_ocean",    ["#FFD9EEF7", "#FF15303D", "#FF1C3644", "#FF5FA8C8", "#FFDDEFF2"]),
    ("rose",     "theme_rose",     ["#FFFBE0E6", "#FF3F1F28", "#FF45232D", "#FFE07F96", "#FFFBE8DF"]),
    ("citrus",   "theme_citrus",   ["#FFFBF3C2", "#FF34300F", "#FF3A3413", "#FFE0C443", "#FFF6F0D2"]),
    ("mint",     "theme_mint",     ["#FFD8F5EA", "#FF123A2E", "#FF17402F", "#FF4FC39A", "#FFE2F4EC"]),
    ("coral",    "theme_coral",    ["#FFFFE1D3", "#FF3E2018", "#FF452519", "#FFF08A5D", "#FFFCE3DA"]),
    ("berry",    "theme_berry",    ["#FFF6DDF0", "#FF3B1736", "#FF431B3D", "#FFC2549F", "#FFF7E6F2"]),
    ("sand",     "theme_sand",     ["#FFF3E7D3", "#FF33291C", "#FF3A2E20", "#FFC9A46C", "#FFF2E9DA"]),
    ("slate",    "theme_slate",    ["#FFE6E9EE", "#FF23272E", "#FF2C3038", "#FF8C96A8", "#FFECEFF3"]),
    ("mono",     "theme_mono",     ["#FFF2F2F2", "#FF1E1E1E", "#FF2A2A2A", "#FF9A9A9A", "#FFE6E6E6"]),
]

# ---- Clock shape and digits ------------------------------------------------------------
BLOB_C = (225, 122)          # centre of the scalloped shape
BLOB_R, BLOB_WAVE, BLOB_LOBES = 103, 7, 12
BLOB_IMG = 2 * (BLOB_R + BLOB_WAVE) + 4
DIGIT_SIZE = 92
# Google Sans Flex metrics (em): ascent 0.966, descent 0.286, digit height 0.73. A box exactly
# one line high puts the baseline at top + ascent however the renderer aligns text vertically.
ASC, LINE, DIGIT_H = 0.966, 1.252, 0.73
ROWS = [("hh", 83), ("mm", 155)]         # (format, visual centre y of the digits)

# ---- Side pods (rotated capsules partly tucked under the clock shape) --------------------
POD = dict(w=136, h=96, r=44, angle=37)
POD_C = [(102, 160), (348, 160)]          # left, right
EAR = dict(w=38, h=84, angle=12)
EAR_C = [(128, 156), (322, 156)]
# Pod slots: box (x, y, w, h), and the centres of the upper and lower line inside the box.
POD_SLOTS = [
    dict(sid=0, name="slot_left",  box=(36, 124, 94, 90),  up=(60, 25), low=(42, 61)),
    dict(sid=1, name="slot_right", box=(320, 124, 94, 90), up=(34, 25), low=(52, 61)),
]

# ---- Tiles ------------------------------------------------------------------------------------
TILE = 111
TILE_Y = 240
TILE_X = [106, 233]
TILE_R = 30
TITLE_CY, VALUE_CY = 40, 74              # centres of the two text lines inside a tile

# ---- Bottom arc -------------------------------------------------------------------------------
ARC_R, ARC_T, ARC_DOT = 191, 24, 22
ARC_A0, ARC_A1 = 270, 90                  # value 0 at 9 o'clock, full at 3 o'clock
ARC_BOX = (21, 212, 408, 217)            # slot box: lower half of the dial

# ---- Second time zone ----------------------------------------------------------------------------
# (option id, setting name, label on the face, IANA time zone). Labels stay English: WFF
# templates take literal text.
ZONES = [
    ("off",  "zone_off",  "", ""),
    ("lon",  "zone_lon",  "London",    "Europe/London"),
    ("par",  "zone_par",  "Paris",     "Europe/Paris"),
    ("ist",  "zone_ist",  "Istanbul",  "Europe/Istanbul"),
    ("ruh",  "zone_ruh",  "Riyadh",    "Asia/Riyadh"),
    ("dxb",  "zone_dxb",  "Dubai",     "Asia/Dubai"),
    ("khi",  "zone_khi",  "Karachi",   "Asia/Karachi"),
    ("del",  "zone_del",  "India",     "Asia/Kolkata"),
    ("sin",  "zone_sin",  "Singapore", "Asia/Singapore"),
    ("hkg",  "zone_hkg",  "Hong Kong", "Asia/Hong_Kong"),
    ("tyo",  "zone_tyo",  "Tokyo",     "Asia/Tokyo"),
    ("syd",  "zone_syd",  "Sydney",    "Australia/Sydney"),
    ("nyc",  "zone_nyc",  "New York",  "America/New_York"),
    ("chi",  "zone_chi",  "Chicago",   "America/Chicago"),
    ("lax",  "zone_lax",  "Los Angeles", "America/Los_Angeles"),
    ("sao",  "zone_sao",  "São Paulo", "America/Sao_Paulo"),
    ("utc",  "zone_utc",  "UTC",       "UTC"),
]
ZONE_DEFAULT = "lon"

# ---- Always-on ----------------------------------------------------------------------------------
AOD_INK = "#FFB8B8B8"
AOD_DIM = "#FF6E6E6E"
AOD_LINE = 3                              # scallop outline thickness
AOD_DATE_Y = 246

WX_ICONS = {"storm": "wx_storm", "rain": "wx_rain", "snow": "wx_snow", "fog": "wx_fog", "cloud": "wx_cloud",
            "partly": "wx_partly", "wind": "wx_wind", "clear": ("wx_sun", "wx_moon")}


def wx_pick(kind):
    r = WX_ICONS[kind]
    return r if isinstance(r, tuple) else (r, r)


def text(x, y, w, h, body, size, color, align="CENTER", family=TEXT, extra=""):
    return wff.text(family, x, y, w, h, body, size, color, align, extra)


def line(cx, cy, w, body, size, color, h=30):
    """One centred line of text, w wide, centred on (cx, cy)."""
    return text(round(cx - w / 2), round(cy - h / 2), w, h, body, size, color)


# ---- Decoration -------------------------------------------------------------------------------------
def rotated(x, y, w, h, angle, shape):
    return (f'<PartDraw x="{x}" y="{y}" width="{w}" height="{h}" angle="{angle}" pivotX="0.5" pivotY="0.5">\n'
            + ind(shape, 2) + '</PartDraw>\n')


def fill(color):
    return f'  <Fill color="{color}"/>\n'


def pods():
    out = ""
    for side, ((px, py), (ex, ey)) in enumerate(zip(POD_C, EAR_C)):
        sign = -1 if side == 0 else 1
        w, h, r = POD["w"], POD["h"], POD["r"]
        out += rotated(px - w // 2, py - h // 2, w, h, sign * POD["angle"],
                       f'<RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="{r}" cornerRadiusY="{r}">\n'
                       + fill(c(2)) + '</RoundRectangle>\n')
        ew, eh = EAR["w"], EAR["h"]
        out += rotated(ex - ew // 2, ey - eh // 2, ew, eh, sign * EAR["angle"],
                       f'<Ellipse x="0" y="0" width="{ew}" height="{eh}">\n' + fill(c(3)) + '</Ellipse>\n')
    return out


def arc_track():
    d = 2 * ARC_R
    return (f'<PartDraw x="0" y="0" width="450" height="450">\n'
            f'  <Arc centerX="{CX}" centerY="{CY}" width="{d}" height="{d}" startAngle="{ARC_A1}" endAngle="{ARC_A0}">\n'
            f'    <Stroke color="{c(2)}" thickness="{ARC_T}" cap="ROUND"/>\n'
            f'  </Arc>\n'
            f'</PartDraw>\n')


def blob(res, tint):
    x, y = BLOB_C[0] - BLOB_IMG // 2, BLOB_C[1] - BLOB_IMG // 2
    return image(x, y, BLOB_IMG, BLOB_IMG, res, tint)


def clock(color):
    size = DIGIT_SIZE
    h = round(size * LINE)
    body = ""
    for fmt, cy in ROWS:
        top = round(cy + DIGIT_H * size / 2 - ASC * size)
        body += wff.time_text(fmt, CX - 100, top, 200, h, DIGITS, size, color)
    return wff.digital_clock(body)


# ---- Complication content ------------------------------------------------------------------------------
HAS_TITLE = "textLength([COMPLICATION.TITLE]) &gt; 0"


def title_or_icon(cx, cy, w, size, color, icon=26):
    """The provider's title if it sends one, else its icon."""
    return cond([("t", HAS_TITLE)], [("t", line(cx, cy, w, CTITLE, size, color))],
                image(round(cx - icon / 2), round(cy - icon / 2), icon, icon, MONO, color))


def value_line(cx, cy, w, size, color, value=None):
    if value is None:
        return line(cx, cy, w, CTEXT, size, color)
    return wff.text_or_value(TEXT, round(cx - w / 2), round(cy - 15), w, 30, size, color, value)


def content(up, low, w, color, sizes, bg="", value_color=None):
    """Two-line content for every type except EMPTY. up/low: line centres inside the slot."""
    t_size, v_size = sizes
    vc = value_color or color
    two = lambda value: bg + title_or_icon(*up, w, t_size, color) + value_line(*low, w, v_size, vc, value)
    mid = ((up[0] + low[0]) / 2, (up[1] + low[1]) / 2)
    return {
        "SHORT_TEXT": two(None),
        "RANGED_VALUE": two("[COMPLICATION.RANGED_VALUE_VALUE]"),
        "GOAL_PROGRESS": two("[COMPLICATION.GOAL_PROGRESS_VALUE]"),
        "MONOCHROMATIC_IMAGE": bg + image(round(mid[0] - 18), round(mid[1] - 18), 36, 36, MONO, color),
        "SMALL_IMAGE": bg + image(round(mid[0] - 20), round(mid[1] - 20), 40, 40, "[COMPLICATION.SMALL_IMAGE]"),
    }


TYPES = "SHORT_TEXT RANGED_VALUE GOAL_PROGRESS MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY"


def weather_pod(up, low, w):
    icon = wff.weather_switch("[WEATHER.CONDITION]", wx_pick,
                              lambda r: image(up[0] - 14, up[1] - 14, 28, 28, r, c(3)),
                              isday="[WEATHER.IS_DAY]")
    temp = line(*low, w, tmpl("%d°", ["round([WEATHER.TEMPERATURE])"]), 24, c(0))
    return cond([("wx", wff.WX_OK)], [("wx", icon + temp)], line(*low, w, "--°", 24, c(0)))


def date_pod(up, low, w):
    return (line(*up, w, tmpl("%s", ["[DAY_OF_WEEK_S]"]), 24, c(0))
            + line(*low, w, tmpl("%d", ["[DAY]"]), 24, c(3)))


def pod_slot(p, empty, provider="EMPTY", ptype="EMPTY"):
    x, y, W, H = p["box"]
    parts = content(p["up"], p["low"], W - 6, c(0), (20, 24))
    parts["EMPTY"] = empty(p["up"], p["low"], W - 6)
    return wff.slot_xml(p["sid"], p["name"], x, y, W, H, TYPES, provider, ptype, parts)


def square_bg():
    return ('<PartDraw x="0" y="0" width="{0}" height="{0}">\n'
            '  <RoundRectangle x="0" y="0" width="{0}" height="{0}" cornerRadiusX="{1}" cornerRadiusY="{1}">\n'
            '    <Fill color="{2}"/>\n'
            '  </RoundRectangle>\n'
            '</PartDraw>\n').format(TILE, TILE_R, c(3))


def clover_bg():
    return image(0, 0, TILE, TILE, "clover", c(4))


def second_time():
    """City and its time, one ListOption per city. Localization pins the time sources inside
    the PartText to that zone; 12/24 h follows the watch setting."""
    m10, m1 = "floor([MINUTE] / 10)", "[MINUTE] - floor([MINUTE] / 10) * 10"
    h12 = tmpl("%d:%d%d %s", ["[HOUR_1_12]", m10, m1, "[AMPM_STRING]"])
    h24 = tmpl("%d:%d%d", ["[HOUR_0_23]", m10, m1])
    opts = ""
    for zid, _, label, tz in ZONES:
        if zid == "off":
            body = wff.group("z_off", "", w=TILE, h=TILE)     # an option can't be empty
        else:
            loc = f'  <Localization timeZone="{tz}"/>\n'
            t = lambda b: text(4, VALUE_CY - 15, TILE - 8, 30, b, 20, c(1), extra=loc)
            body = wff.group(f"z_{zid}", clover_bg() + line(TILE / 2, TITLE_CY, TILE - 8, wff.esc(label), 21, c(1))
                             + cond([("h24", "[IS_24_HOUR_MODE]")], [("h24", t(h24))], t(h12)),
                             w=TILE, h=TILE)
        opts += f'  <ListOption id="{zid}">\n' + ind(body, 4) + '  </ListOption>\n'
    return wff.group("zone", '<ListConfiguration id="zone">\n' + opts + '</ListConfiguration>\n', w=TILE, h=TILE)


def tile_slot(sid, name, x, bg, provider, ptype, empty=""):
    up, low = (TILE / 2, TITLE_CY), (TILE / 2, VALUE_CY)
    parts = content(up, low, TILE - 8, c(1), (21, 20), bg)
    parts["EMPTY"] = empty
    return wff.slot_xml(sid, name, x, TILE_Y, TILE, TILE, TYPES, provider, ptype, parts,
                        bound=wff.round_box(TILE, TILE, TILE_R))


def arc_slot():
    x, y, W, H = ARC_BOX
    cx, cy = CX - x, CY - y

    def dot(frac):
        a = f"{ARC_A0} - {ARC_A0 - ARC_A1} * clamp({frac}, 0, 1)"
        d = 2 * ARC_R
        return (f'<PartDraw x="0" y="0" width="{W}" height="{H}">\n'
                f'  <Arc centerX="{cx}" centerY="{cy}" width="{d}" height="{d}" startAngle="{ARC_A0}" endAngle="{ARC_A0 + 1}">\n'
                f'    <Stroke color="{c(4)}" thickness="{ARC_DOT}" cap="ROUND"/>\n'
                f'    <Transform target="startAngle" value="{a}"/>\n'
                f'    <Transform target="endAngle" value="{a} + 1"/>\n'
                f'  </Arc>\n'
                f'</PartDraw>\n')
    bound = (f'<BoundingArc centerX="{cx}" centerY="{cy}" width="{2 * ARC_R}" height="{2 * ARC_R}" '
             f'thickness="{ARC_T + 16}" startAngle="{ARC_A1}" endAngle="{ARC_A0}" isRoundEdge="TRUE"/>')
    parts = {"RANGED_VALUE": dot(RANGE), "GOAL_PROGRESS": dot(GOAL), "EMPTY": ""}
    return wff.slot_xml(4, "slot_arc", x, y, W, H, "RANGED_VALUE GOAL_PROGRESS EMPTY",
                        "WATCH_BATTERY", "RANGED_VALUE", parts, bound)


# ---- Always-on ---------------------------------------------------------------------------------------------
def ambient():
    date = text(CX - 80, AOD_DATE_Y, 160, 30,
                tmpl("%s %d", ["[DAY_OF_WEEK_S]", "[DAY]"]), 22, AOD_DIM)
    return blob("scallop_line", AOD_DIM) + clock(AOD_INK) + date


# ---- Settings and scene --------------------------------------------------------------------------------------
def user_configs():
    zones = "".join(f'  <ListOption id="{z[0]}" displayName="{z[1]}"/>\n' for z in ZONES)
    return ('<UserConfigurations>\n' + ind(wff.color_config(THEMES), 2)
            + f'  <ListConfiguration id="zone" displayName="cfg_zone" defaultValue="{ZONE_DEFAULT}">\n'
            + ind(zones, 2) + '  </ListConfiguration>\n'
            '</UserConfigurations>\n')


def main():
    active = arc_track() + pods() + blob("scallop", c(0)) + clock(c(1))
    scene = (wff.active_only("active", active) + wff.ambient_only("ambient", ambient())
             + pod_slot(POD_SLOTS[0], weather_pod) + pod_slot(POD_SLOTS[1], date_pod)
             + tile_slot(2, "slot_tile_left", TILE_X[0], square_bg(), "STEP_COUNT", "SHORT_TEXT")
             + tile_slot(3, "slot_tile_right", TILE_X[1], clover_bg(), "EMPTY", "EMPTY", second_time())
             + arc_slot())
    print(wff.watchface("Bloom: scalloped stacked clock with a second time zone.", "08:57:00",
                        user_configs(), scene), end="")


if __name__ == "__main__":
    main()

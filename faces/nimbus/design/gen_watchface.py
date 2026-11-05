#!/usr/bin/env python3
"""Generates res/raw/watchface.xml for the "Nimbus" Watch Face Format (v2) face.

Run from the face folder (faces/nimbus):
    python3 design/make_weather_art.py        # only if the big weather pictures change
    python3 design/make_icons.py              # only if the small icons change
    python3 design/gen_watchface.py > src/main/res/raw/watchface.xml
    python3 design/render_preview.py          # preview.png, launcher icon, docs/*.png
Geometry is for a 450x450 round canvas. Angles: 0 = 12 o'clock, clockwise.
User-visible setting names live in src/main/res/values/strings.xml.
"""
import math, os, sys
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import wff
from wff import ind, esc, tmpl, cond, image, any_of, RAIN_CODES, SNOW_CODES, STORM, RANGE, GOAL, MONO, CTEXT
FONT = "barlow_sc_bold"
FONT_FILE = os.path.join(HERE, "..", "src", "main", "res", "font", FONT + ".ttf")
CX = CY = 225

# Theme colours: [0] outer band, [1] inner band, [2] accent (pill, battery, icons).
THEMES = [
    ("olive",    "theme_olive",    ["#FF5C6B2E", "#FF46521F", "#FFB9CC6A"]),
    ("steel",    "theme_steel",    ["#FF3E5C7A", "#FF2E4760", "#FF8FC0EE"]),
    ("rust",     "theme_rust",     ["#FF8A4A22", "#FF6B3818", "#FFF0A066"]),
    ("crimson",  "theme_crimson",  ["#FF7A2630", "#FF5E1C24", "#FFF0707E"]),
    ("violet",   "theme_violet",   ["#FF55347E", "#FF412763", "#FFB896F0"]),
    ("plum",     "theme_plum",     ["#FF6E2F62", "#FF55234B", "#FFE493D2"]),
    ("teal",     "theme_teal",     ["#FF1F6466", "#FF174D4F", "#FF6FD6D2"]),
    ("forest",   "theme_forest",   ["#FF2F5E3A", "#FF23482C", "#FF84D69A"]),
    ("navy",     "theme_navy",     ["#FF283C78", "#FF1D2D5C", "#FF8EA6F2"]),
    ("sand",     "theme_sand",     ["#FF7A6A48", "#FF5E5136", "#FFE8D3A0"]),
    ("graphite", "theme_graphite", ["#FF4A4A4E", "#FF38383B", "#FFD0D0D6"]),
    ("midnight", "theme_midnight", ["#FF1E1E26", "#FF16161C", "#FF9FA8C8"]),
]


c = wff.theme


WHITE = "#FFFFFFFF"
LABEL = "#B3FFFFFF"     # 70% white

# ---- Rings ----------------------------------------------------------------------
# (band centre radius, band thickness, text ellipse radius, label size, value size)
OUTER = dict(r=206, t=34, tr=208, ls=14, vs=23)
INNER = dict(r=170, t=30, tr=172, ls=13, vs=21)
# Text sits on an ellipse a few px outside the band centre: the WFF renderer is not
# documented on whether TextCircular text is centred on the ellipse or hangs inside
# it; this radius keeps the text inside the band either way.

S = "[STEP_COUNT]"
WX = "[WEATHER.IS_AVAILABLE]"
T, HI, LO = "[WEATHER.TEMPERATURE]", "[WEATHER.DAY_TEMPERATURE_HIGH]", "[WEATHER.DAY_TEMPERATURE_LOW]"


def tenths(expr):
    """Two params that print expr as 'a.b' with '%d.%d'."""
    return [f"floor({expr})", f"floor(({expr}) * 10) - floor({expr}) * 10"]


# Ring data choices: id, setting name, label on the face, template, params, guard, sample.
# Distance has no WFF data source, so it's estimated from steps at 0.75 m per step.
OPTIONS = [
    ("none",  "opt_none",  "",       "",         [],                                  None, ""),
    ("steps", "opt_steps", "STEPS",  "%d",       [S],                                 None, "9998"),
    ("goal",  "opt_goal",  "GOAL %", "%d",       ["[STEP_PERCENT]"],                  None, "19"),
    ("km",    "opt_km",    "KM",     "%d.%d",    tenths(f"{S} * 0.00075"),            None, "7.6"),
    ("mi",    "opt_mi",    "MI",     "%d.%d",    tenths(f"{S} * 0.000466"),           None, "4.7"),
    ("notif", "opt_notif", "NOTIFY", "%d",       ["[UNREAD_NOTIFICATION_COUNT]"],     None, "9"),
    ("hr",    "opt_hr",    "BPM",    "%d",       ["round([HEART_RATE])"],             "[HEART_RATE] &gt; 0", "83"),
    ("uv",    "opt_uv",    "UV",     "%d",       ["[WEATHER.UV_INDEX]"],              WX, "3"),
    ("temp",  "opt_temp",  "TEMP",   "%d° %d %d", [T, HI, LO],                       WX, "25° 30 18"),
    ("hilo",  "opt_hilo",  "HI LO",  "%d %d",    [HI, LO],                            WX, "30 18"),
    ("rain",  "opt_rain",  "RAIN %", "%d",       ["[WEATHER.CHANCE_OF_PRECIPITATION]"], WX, "40"),
    ("batt",  "opt_batt",  "BATT %", "%d",       ["[BATTERY_PERCENT]"],               None, "90"),
]
OPT = {o[0]: o for o in OPTIONS}

# Ring positions: config id, setting name, ring, (start, end) angles, default option.
POSITIONS = [
    ("ringO1", "pos_o1", OUTER, (-118, -72), "goal"),
    ("ringO2", "pos_o2", OUTER, (-63, -7),   "steps"),
    ("ringO3", "pos_o3", OUTER, (7, 63),     "uv"),
    ("ringO4", "pos_o4", OUTER, (72, 118),   "temp"),
    ("ringI1", "pos_i1", INNER, (-112, -68), "km"),
    ("ringI2", "pos_i2", INNER, (-59, -7),   "notif"),
    ("ringI3", "pos_i3", INNER, (7, 59),     "hr"),
    ("ringI4", "pos_i4", INNER, (68, 112),   "rain"),
]
DOTS = {id(OUTER): (-67.5, 0, 67.5), id(INNER): (-63.5, 0, 63.5)}

# ---- Centre -----------------------------------------------------------------------
DISK_R = 152
ART = (115, 62, 220, 220)          # x, y, w, h of the big weather picture
# Weather pictures per kind (wff.WEATHER_KINDS): big picture (day, night), small icon (day, night)
WEATHER = {
    "storm":  (("wxl_storm", "wxl_storm"),             ("wx_storm", "wx_storm")),
    "rain":   (("wxl_rain", "wxl_rain"),               ("wx_rain", "wx_rain")),
    "snow":   (("wxl_snow", "wxl_snow"),               ("wx_snow", "wx_snow")),
    "fog":    (("wxl_fog", "wxl_fog"),                 ("wx_fog", "wx_fog")),
    "cloud":  (("wxl_cloud", "wxl_cloud"),             ("wx_cloud", "wx_cloud")),
    "partly": (("wxl_partly_day", "wxl_partly_night"), ("wx_partly", "wx_partly")),
    "wind":   (("wxl_wind", "wxl_wind"),               ("wx_wind", "wx_wind")),
    "clear":  (("wxl_sun", "wxl_moon"),                ("wx_sun", "wx_moon")),
}


def weather_cases(src, isday=None, big=False):
    """[(expression, resource)] for a condition source. isday=None means daytime only."""
    return wff.weather_cases(src, lambda k: WEATHER[k][0 if big else 1], isday)


# Lower block
PILL = (118, 284, 214, 34)          # x, y, w, h
SIDE = (76, 64)                     # side complication size
SIDE_C = [(70, 300), (380, 300)]    # centres
PILL_SLOT = (122, 285, 102, 32)
TIME_CY = 352                       # visual centre of the digits
BATT_Y = 388
BATT_ARC = dict(r=202, a0=154, a1=206)

# Rain/snow motion (optional, off by default)
DROPS = [(150, 0.9), (172, 1.1), (196, 0.8), (218, 1.0), (240, 0.95), (262, 1.15), (284, 0.85), (306, 1.05)]


def font(size, color, body, extra=""):
    return wff.font(FONT, size, color, body, extra)


def text(x, y, w, h, body, size, color=WHITE, align="CENTER"):
    return wff.text(FONT, x, y, w, h, body, size, color, align)


def ctext(ring, a0, a1, body, size, color, align):
    d = 2 * ring["tr"]
    return (f'<PartText x="0" y="0" width="450" height="450">\n'
            f'  <TextCircular centerX="{CX}" centerY="{CY}" width="{d}" height="{d}" '
            f'startAngle="{a0:.1f}" endAngle="{a1:.1f}" direction="CLOCKWISE" align="{align}">\n'
            f'    {font(size, color, body)}\n'
            f'  </TextCircular>\n'
            f'</PartText>\n')


def outline_pill(x, y, w, h, color, thickness=1.5, fill=None):
    r = h / 2 - 1
    f = f'\n    <Fill color="{fill}"/>' if fill else ""
    return (f'<PartDraw x="{x}" y="{y}" width="{w}" height="{h}">\n'
            f'  <RoundRectangle x="1" y="1" width="{w - 2}" height="{h - 2}" cornerRadiusX="{r}" cornerRadiusY="{r}">{f}\n'
            f'    <Stroke color="{color}" thickness="{thickness}"/>\n'
            f'  </RoundRectangle>\n'
            f'</PartDraw>\n')


# ---- Ring text --------------------------------------------------------------------
_F = {}


def width(t, size):
    if size not in _F:
        _F[size] = ImageFont.truetype(FONT_FILE, size)
    return _F[size].getlength(t)


def ring_split(ring, a0, a1, label, sample):
    """Label ends at `split`, value starts at `split + gap`, so label+sample value is centred."""
    r = ring["tr"] - ring["vs"] * 0.35           # roughly where the glyph middles sit
    deg = lambda px: math.degrees(px / r)
    gap = deg(5)
    wl, wv = deg(width(label, ring["ls"])), deg(width(sample, ring["vs"]))
    return (a0 + a1) / 2 - (wl + gap + wv) / 2 + wl, gap


def ring_item(ring, a0, a1, opt):
    oid, _, label, template, params, guard, sample = opt
    if oid == "none":
        return ""
    split, gap = ring_split(ring, a0, a1, label, sample)
    lab = ctext(ring, a0, split, esc(label), ring["ls"], LABEL, "END")
    val = ctext(ring, split + gap, a1, tmpl(template, params), ring["vs"], WHITE, "START")
    if guard:
        dash = ctext(ring, split + gap, a1, "--", ring["vs"], WHITE, "START")
        val = cond([("ok", guard)], [("ok", val)], dash)
    return lab + val


def ring_position(pid, ring, angles, _default):
    opts = "".join(f'  <ListOption id="{o[0]}">\n'
                   + ind(f'<Group name="{pid}_{o[0]}" x="0" y="0" width="450" height="450">\n'
                         + ind(ring_item(ring, *angles, o), 2) + '</Group>\n', 4)
                   + '  </ListOption>\n' for o in OPTIONS)
    return f'<ListConfiguration id="{pid}">\n' + opts + '</ListConfiguration>\n'


def bands():
    out = ""
    for ring in (OUTER, INNER):
        d = 2 * ring["r"]
        col = c(0) if ring is OUTER else c(1)
        out += (f'<PartDraw x="0" y="0" width="450" height="450">\n'
                f'  <Arc centerX="{CX}" centerY="{CY}" width="{d}" height="{d}" startAngle="0" endAngle="360">\n'
                f'    <Stroke color="{col}" thickness="{ring["t"]}"/>\n'
                f'  </Arc>\n'
                f'</PartDraw>\n')
        dots = ""
        for a in DOTS[id(ring)]:
            x = CX + ring["r"] * math.sin(math.radians(a))
            y = CY - ring["r"] * math.cos(math.radians(a))
            dots += (f'  <Ellipse x="{x - 3:.1f}" y="{y - 3:.1f}" width="6" height="6">\n'
                     f'    <Stroke color="#99FFFFFF" thickness="1.5"/>\n'
                     f'  </Ellipse>\n')
        out += f'<PartDraw x="0" y="0" width="450" height="450">\n{dots}</PartDraw>\n'
    # centre disk, and a fade to black over the lower part so the time reads cleanly
    out += (f'<PartDraw x="0" y="0" width="450" height="450">\n'
            f'  <Ellipse x="{CX - DISK_R}" y="{CY - DISK_R}" width="{2 * DISK_R}" height="{2 * DISK_R}">\n'
            f'    <Fill color="#FF000000"/>\n'
            f'  </Ellipse>\n'
            f'  <Rectangle x="0" y="235" width="450" height="215">\n'
            f'    <Fill color="#00000000">\n'
            f'      <LinearGradient startX="0" startY="235" endX="0" endY="400" '
            f'colors="#00000000 #E6000000 #FF000000" positions="0 0.75 1"/>\n'
            f'    </Fill>\n'
            f'  </Rectangle>\n'
            f'</PartDraw>\n')
    return out


def weather_art():
    x, y, w, h = ART
    arts = weather_cases("[WEATHER.CONDITION]", "[WEATHER.IS_DAY]", big=True)
    cases = [(f"a{i}", image(x, y, w, h, res)) for i, (_, res) in enumerate(arts)]
    inner = cond([(f"a{i}", e) for i, (e, _) in enumerate(arts)], cases, image(x, y, w, h, "wxl_unknown"))
    return cond([("wx", wff.WX_OK)], [("wx", inner)],
                image(x, y, w, h, "wxl_unknown"))


def motion():
    """Falling rain / snow over the picture. Only when enabled and it is raining/snowing."""
    def layer(snow):
        parts = ""
        for i, (x, sec) in enumerate(DROPS):
            y0 = 168 + (i * 23) % 40
            sec = sec * (2.2 if snow else 1)
            if snow:
                shape = '  <Ellipse x="0" y="0" width="5" height="5"><Fill color="#CCFFFFFF"/></Ellipse>\n'
                w, h = 5, 5
            else:
                shape = ('  <Line startX="2" startY="0" endX="0" endY="14">\n'
                         '    <Stroke color="#99FFFFFF" thickness="2" cap="ROUND"/>\n  </Line>\n')
                w, h = 4, 14
            parts += (f'<PartDraw x="{x}" y="{y0}" width="{w}" height="{h}">\n{shape}'
                      f'  <Transform target="y" value="{y0 + 70}">'
                      f'<Animation interpolation="LINEAR" duration="{sec:.2f}" repeat="-1" fps="12"/></Transform>\n'
                      f'</PartDraw>\n')
        return f'<Group name="{"snow" if snow else "rain"}" x="0" y="0" width="450" height="450">\n' + ind(parts, 2) + '</Group>\n'
    rain = any_of("[WEATHER.CONDITION]", RAIN_CODES + (STORM,))
    snow = any_of("[WEATHER.CONDITION]", SNOW_CODES)
    body = cond([("r", f"{WX} &amp;&amp; {rain}"), ("s", f"{WX} &amp;&amp; {snow}")],
                [("r", layer(False)), ("s", layer(True))])
    return ('<BooleanConfiguration id="motion">\n  <BooleanOption id="TRUE">\n'
            + ind(body, 4) + '  </BooleanOption>\n</BooleanConfiguration>\n')


DATE = '<Upper>' + tmpl("%d %s", ["[DAY]", "[DAY_OF_WEEK_S]"]) + '</Upper>'


def pill():
    x, y, w, h = PILL
    return (outline_pill(x, y, w, h, c(2), 2, "#B3000000")
            + text(x + 108, y + 2, w - 122, h - 4, DATE, 22, WHITE, "END"))


DIGIT = 0.53    # digit box width in em (monospaced boxes stop the time jiggling each second)
COLON = 0.26


def clock_boxes(size, fmt_groups, cy):
    """[(format or ":", x, y, w, h)] in fixed boxes (monospaced, so the time doesn't jiggle).
    fmt_groups: e.g. [("hh_10","hh_1"), ("mm_10","mm_1"), ("ss_10","ss_1")]"""
    dw, cw = round(size * DIGIT), round(size * COLON)
    total = len(fmt_groups) * 2 * dw + (len(fmt_groups) - 1) * cw
    x = round(CX - total / 2)
    top = round(cy - 0.65 * size)   # Barlow digits: cap middle ~0.65 em below the box top
    h = round(size * 1.2)
    out = []
    for gi, g in enumerate(fmt_groups):
        if gi:
            out.append((":", x, top, cw, h))
            x += cw
        for fmt in g:
            out.append((fmt, x, top, dw, h))
            x += dw
    return out


def clock(size, fmt_groups, color, cy):
    boxes = clock_boxes(size, fmt_groups, cy)
    colons = "".join(text(x, y, w, h, ":", size, color) for f, x, y, w, h in boxes if f == ":")
    digits = "".join(wff.time_text(f, x, y, w, h, FONT, size, color) for f, x, y, w, h in boxes if f != ":")
    return colons + wff.digital_clock(digits)


HM = [("hh_10", "hh_1"), ("mm_10", "mm_1")]
HMS = HM + [("ss_10", "ss_1")]


def time_block():
    return ('<BooleanConfiguration id="seconds">\n'
            '  <BooleanOption id="TRUE">\n'
            + ind('<Group name="hms" x="0" y="0" width="450" height="450">\n' + ind(clock(62, HMS, WHITE, TIME_CY), 2) + '</Group>\n', 4) +
            '  </BooleanOption>\n'
            '  <BooleanOption id="FALSE">\n'
            + ind('<Group name="hm" x="0" y="0" width="450" height="450">\n' + ind(clock(74, HM, WHITE, TIME_CY), 2) + '</Group>\n', 4) +
            '  </BooleanOption>\n'
            '</BooleanConfiguration>\n')


def battery():
    a = BATT_ARC
    d = 2 * a["r"]
    span = a["a1"] - a["a0"]
    # fills right-to-left along the bottom (clockwise from a0)
    arc = (f'<PartDraw x="0" y="0" width="450" height="450">\n'
           f'  <Arc centerX="{CX}" centerY="{CY}" width="{d}" height="{d}" startAngle="{a["a0"]}" endAngle="{a["a1"]}">\n'
           f'    <Stroke color="#40FFFFFF" thickness="7" cap="ROUND"/>\n'
           f'  </Arc>\n'
           f'  <Arc centerX="{CX}" centerY="{CY}" width="{d}" height="{d}" startAngle="{a["a1"]}" endAngle="{a["a1"]}" direction="COUNTER_CLOCKWISE">\n'
           f'    <Stroke color="{c(2)}" thickness="7" cap="ROUND"/>\n'
           f'    <Transform target="endAngle" value="{a["a1"]} - {span} * [BATTERY_PERCENT] / 100"/>\n'
           f'  </Arc>\n'
           f'</PartDraw>\n')
    num = text(CX - 10, BATT_Y, 60, 28, tmpl("%d", ["[BATTERY_PERCENT]"]), 24, WHITE, "START")
    bolt = image(CX - 28, BATT_Y + 6, 14, 16, "ic_bolt", c(2))
    return arc + bolt + num


# ---- Complications --------------------------------------------------------------------
def text_or_value(x, y, w, h, size, value):
    return wff.text_or_value(FONT, x, y, w, h, size, WHITE, value)


def bar(x, y, w, frac):
    return (f'<PartDraw x="{x}" y="{y}" width="{w}" height="4">\n'
            f'  <RoundRectangle x="0" y="0" width="{w}" height="4" cornerRadiusX="2" cornerRadiusY="2"><Fill color="#40FFFFFF"/></RoundRectangle>\n'
            f'  <RoundRectangle x="0" y="0" width="{w}" height="4" cornerRadiusX="2" cornerRadiusY="2"><Fill color="{c(2)}"/>\n'
            f'    <Transform target="width" value="{w} * clamp({frac}, 0, 1)"/>\n'
            f'  </RoundRectangle>\n'
            f'</PartDraw>\n')


def side_slot(sid, name, cx, cy, provider, ptype):
    W, H = SIDE
    types = "SHORT_TEXT RANGED_VALUE GOAL_PROGRESS MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY"
    icon = image((W - 26) // 2, 2, 26, 26, MONO, WHITE)
    parts = {
        "SHORT_TEXT": icon + text(0, 29, W, 30, CTEXT, 22),
        "RANGED_VALUE": icon + text_or_value(0, 27, W, 28, 21, "[COMPLICATION.RANGED_VALUE_VALUE]") + bar(14, 58, W - 28, RANGE),
        "GOAL_PROGRESS": icon + text_or_value(0, 27, W, 28, 21, "[COMPLICATION.GOAL_PROGRESS_VALUE]") + bar(14, 58, W - 28, GOAL),
        "MONOCHROMATIC_IMAGE": image((W - 34) // 2, (H - 34) // 2, 34, 34, MONO, WHITE),
        "SMALL_IMAGE": image((W - 38) // 2, (H - 38) // 2, 38, 38, "[COMPLICATION.SMALL_IMAGE]"),
        "EMPTY": "",
    }
    return wff.slot_xml(sid, name, cx - W // 2, cy - H // 2, W, H, types, provider, ptype, parts)


def pill_slot(sid, name, provider, ptype):
    x, y, W, H = PILL_SLOT
    types = "SHORT_TEXT RANGED_VALUE MONOCHROMATIC_IMAGE EMPTY"
    icon = image(4, 5, 22, 22, MONO, c(2))
    parts = {
        "SHORT_TEXT": icon + text(30, 1, W - 32, H - 2, CTEXT, 22, WHITE, "START"),
        "RANGED_VALUE": icon + text(30, 1, W - 32, H - 2, CTEXT, 22, WHITE, "START"),
        "MONOCHROMATIC_IMAGE": image(4, 5, 22, 22, MONO, c(2)),
        "EMPTY": "",
    }
    return wff.slot_xml(sid, name, x, y, W, H, types, provider, ptype, parts)


# ---- Always-on ---------------------------------------------------------------------------
AOD_GREY = "#FFB4B4B4"
AOD_DIM = "#FF7A7A7A"
DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]   # WFF DAY_OF_WEEK: 1 = Sunday


def forecast_block(cx, y, cond_expr, isday, hi_tmpl, hi_params, label_body, avail):
    ic = wff.weather_switch(cond_expr, lambda k: WEATHER[k][1], lambda r: image(cx - 14, y, 28, 28, r, AOD_GREY),
                            isday=isday)
    temps = text(cx - 45, y + 30, 90, 28, tmpl(hi_tmpl, hi_params), 24, AOD_GREY)
    lab = (outline_pill(cx - 28, y + 61, 56, 24, AOD_DIM)
           + (text(cx - 28, y + 62, 56, 22, label_body, 16, AOD_GREY) if label_body else ""))
    return cond([("ok", avail)], [("ok", ic + temps + lab)])


def day_name_text(cx, y, k):
    exprs = [(f"d{d}", f"[DAY_OF_WEEK] + {k} == {d} || [DAY_OF_WEEK] + {k} == {d + 7}") for d in range(1, 8)]
    return cond(exprs, [(f"d{d}", text(cx - 28, y, 56, 22, DAYS[d - 1], 16, AOD_GREY)) for d in range(1, 8)])


AOD_FC_Y = 262
AOD_FC_X = (180, 270)


def ambient():
    # date pill
    out = outline_pill(160, 100, 130, 32, AOD_DIM) + text(160, 102, 130, 28, DATE, 21, AOD_GREY)
    out += clock(96, HM, AOD_GREY, 192)
    # forecast: daily (tomorrow, day after) from 07:00, hourly (+3h, +6h) overnight
    daily = ""
    for k, cx in zip((1, 2), AOD_FC_X):
        blk = forecast_block(cx, AOD_FC_Y, f"[WEATHER.DAYS.{k}.CONDITION_DAY]", None, "%d %d",
                             [f"[WEATHER.DAYS.{k}.TEMPERATURE_HIGH]", f"[WEATHER.DAYS.{k}.TEMPERATURE_LOW]"],
                             "", f"[WEATHER.DAYS.{k}.IS_AVAILABLE]")
        daily += blk + cond([("ok", f"[WEATHER.DAYS.{k}.IS_AVAILABLE]")], [("ok", day_name_text(cx, AOD_FC_Y + 62, k))])
    hourly = ""
    for h, cx in zip((3, 6), AOD_FC_X):
        hourly += forecast_block(cx, AOD_FC_Y, f"[WEATHER.HOURS.{h}.CONDITION]", f"[WEATHER.HOURS.{h}.IS_DAY]",
                                 "%d°", [f"[WEATHER.HOURS.{h}.TEMPERATURE]"], f"+{h}H",
                                 f"[WEATHER.HOURS.{h}.IS_AVAILABLE]")
    out += cond([("night", "[HOUR_0_23] &lt; 7")], [("night", hourly)], daily)
    out += text(CX - 40, 380, 80, 26, tmpl("%d", ["[BATTERY_PERCENT]"]), 20, AOD_DIM)
    return out


# ---- Settings ------------------------------------------------------------------------------
def user_configs():
    lists = ""
    for pid, name, _, _, default in POSITIONS:
        opts = "".join(f'  <ListOption id="{o[0]}" displayName="{o[1]}"/>\n' for o in OPTIONS)
        lists += f'<ListConfiguration id="{pid}" displayName="{name}" defaultValue="{default}">\n{opts}</ListConfiguration>\n'
    return ('<UserConfigurations>\n' + ind(wff.color_config(THEMES), 2) +
            '  <BooleanConfiguration id="seconds" displayName="cfg_seconds" defaultValue="FALSE"/>\n'
            '  <BooleanConfiguration id="motion" displayName="cfg_motion" defaultValue="FALSE"/>\n'
            + ind(lists, 2) +
            '</UserConfigurations>\n')


SLOTS_SIDE = [(0, "slot_left", *SIDE_C[0], "NEXT_EVENT", "SHORT_TEXT"),
              (1, "slot_right", *SIDE_C[1], "WORLD_CLOCK", "SHORT_TEXT")]
SLOT_PILL = (2, "slot_pill", "SUNRISE_SUNSET", "SHORT_TEXT")


def main():
    active = (bands()
              + "".join(ring_position(p[0], p[2], p[3], p[4]) for p in POSITIONS)
              + weather_art() + motion() + pill() + time_block() + battery())
    scene = (wff.active_only("active", active) + wff.ambient_only("ambient", ambient())
             + "".join(side_slot(*s) for s in SLOTS_SIDE) + pill_slot(*SLOT_PILL))
    xml = wff.watchface("Nimbus: weather rings digital face.", "10:30:00", user_configs(), scene)
    print(xml, end="")


if __name__ == "__main__":
    main()

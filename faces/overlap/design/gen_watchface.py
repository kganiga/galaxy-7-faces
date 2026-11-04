#!/usr/bin/env python3
"""Generates res/raw/watchface.xml for the "Overlap" Watch Face Format (v2) face.

Run from the face folder (faces/overlap):
    python3 design/make_ambient_digits.py     # only if digit size/stroke/tones change
    python3 design/make_icons.py              # only if icons change
    python3 design/gen_watchface.py > src/main/res/raw/watchface.xml
All geometry is for a 450x450 round canvas (Galaxy Watch 7 renders WFF at 450).
User-visible names live in src/main/res/values/strings.xml and are referenced by name.
"""

FONT = "fredoka_bold"

# Theme colours: [0] digit A, [1] digit B, [2] accent text.  (id, string resource, colours)
THEMES = [
    ("oat",     "theme_oat",     ["#FFF2E8D5", "#FFC9AA80", "#FFE6D6BC"]),
    ("sage",    "theme_sage",    ["#FFE4F0DC", "#FF8FBF7E", "#FFCDE3C2"]),
    ("coral",   "theme_coral",   ["#FFFFE3D8", "#FFF2815F", "#FFFFD0BF"]),
    ("glacier", "theme_glacier", ["#FFE2F0FA", "#FF74AEDD", "#FFCDE5F6"]),
    ("lilac",   "theme_lilac",   ["#FFEFE6FB", "#FFAA92DE", "#FFDFD2F6"]),
    ("mono",    "theme_mono",    ["#FFF5F5F5", "#FF9A9A9A", "#FFE2E2E2"]),
    ("mint",    "theme_mint",    ["#FFDDF7EC", "#FF45C59A", "#FFC6EEDC"]),
    ("amber",   "theme_amber",   ["#FFFFF0D2", "#FFF0A532", "#FFFFE2AE"]),
    ("rose",    "theme_rose",    ["#FFFFE1EA", "#FFE86E8F", "#FFFFCCDA"]),
    ("ocean",   "theme_ocean",   ["#FFD8F2F6", "#FF2DA3B5", "#FFBDE6EE"]),
    ("lemon",   "theme_lemon",   ["#FFFBF6CF", "#FFD6C32A", "#FFF2EAA6"]),
    ("berry",   "theme_berry",   ["#FFF4DDF1", "#FFB24E9C", "#FFEBC6E4"]),
]


def c(i):
    return f"[CONFIGURATION.theme.{i}]"


# ---- Digit geometry -------------------------------------------------------
SIZE = 215          # Fredoka Bold: ~156 px digit height, ~120 px digit width at 215
BOX_W, BOX_H = 150, 262   # box height = font line height so the glyph sits at a fixed baseline
COL_X = [173, 277]  # centres of tens / units columns (overlap ~16 px)
ROW_Y = [20, 164]   # box tops: hours, minutes (rows overlap ~12 px)
SHADOW = 6          # black offset copy drawn under every digit -> carved overlap edge

# (format, column, row, tone) -- checkerboard: H-tens A, H-units B, M-tens B, M-units A
DIGITS = [
    ("hh_10", 0, 0, 0),
    ("hh_1",  1, 0, 1),
    ("mm_10", 0, 1, 1),
    ("mm_1",  1, 1, 0),
]

# ---- Always-on digits (battery) --------------------------------------------
# Outline-only bitmap digits rendered by make_ambient_digits.py: black fill + thin
# neutral-grey stroke, so ~7% of pixels are lit instead of ~30% with filled digits.
AMB_STROKE = 3
AMB_TONES = ("#C4C4C4", "#7E7E7E")   # tone A, tone B (fixed greys, theme-independent)
AMB_W, AMB_H, AMB_TOP = 130, 165, 54  # must match make_ambient_digits.py (it checks)

# ---- Date ------------------------------------------------------------------
# Split around 12 o'clock: Wear OS draws the charging / status icons there.
DATE_R = 376          # TextCircular ellipse size
DATE_GAP = 9          # degrees left free either side of 12 o'clock
DATE_SPAN = 62        # outer end of each half, degrees from 12 o'clock

# ---- Weather / animation ------------------------------------------------------
# WEATHER.CONDITION values (developer.android.com/reference/wear-os/wff/.../source-type)
RAINY = (4, 6, 9, 10, 12)       # heavy rain, rain, thunderstorm, sleet, light rain
WEATHER_ICONS = [               # (expression, icon resource) -- first match wins
    ("[WEATHER.CONDITION] == 9", "wx_storm"),
    ("[WEATHER.CONDITION] == 4 || [WEATHER.CONDITION] == 6 || [WEATHER.CONDITION] == 12 || [WEATHER.CONDITION] == 10", "wx_rain"),
    ("[WEATHER.CONDITION] == 5 || [WEATHER.CONDITION] == 7 || [WEATHER.CONDITION] == 11", "wx_snow"),
    ("[WEATHER.CONDITION] == 3 || [WEATHER.CONDITION] == 13", "wx_fog"),
    ("[WEATHER.CONDITION] == 2", "wx_cloud"),
    ("[WEATHER.CONDITION] == 14", "wx_partly"),
    ("[WEATHER.CONDITION] == 15", "wx_wind"),
    ("([WEATHER.CONDITION] == 1 || [WEATHER.CONDITION] == 8) &amp;&amp; ![WEATHER.IS_DAY]", "wx_moon"),
    ("[WEATHER.CONDITION] == 1 || [WEATHER.CONDITION] == 8", "wx_sun"),
]
RAIN_DROPS = [  # (x, start y, length, fall seconds) -- looping streaks behind the digits
    (48, -40, 22, 1.30), (82, -200, 18, 1.10), (118, -90, 26, 1.45), (150, -300, 20, 1.20),
    (184, -150, 24, 1.35), (212, -20, 18, 1.05), (246, -260, 26, 1.40), (276, -110, 20, 1.15),
    (308, -330, 24, 1.30), (338, -60, 18, 1.10), (368, -220, 26, 1.45), (398, -140, 20, 1.25),
    (98, -380, 20, 1.20), (230, -420, 22, 1.30), (322, -460, 18, 1.15), (166, -480, 24, 1.40),
]

# ---- Complication slots -------------------------------------------------------
# kind: "side" (rotated pill), "bottom" (pill), "round" (small circle)
SLOTS = [
    # id, name string, kind, centre x, centre y, angle, default provider, default type
    (0, "slot_left",         "side",   40, 225, -90, "WATCH_BATTERY", "RANGED_VALUE"),
    (1, "slot_right",        "side",  410, 225,  90, "STEP_COUNT",    "SHORT_TEXT"),
    (2, "slot_bottom",       "bottom", 225, 402,   0, "EMPTY",         "EMPTY"),       # empty = weather
    (3, "slot_bottom_left",  "round",  91, 357,   0, "EMPTY",         "EMPTY"),       # empty = heart rate
    (4, "slot_bottom_right", "round", 359, 357,   0, "SUNRISE_SUNSET", "SHORT_TEXT"),
]
SIZES = {"side": (124, 46), "bottom": (170, 48), "round": (60, 60)}
# Listed in order of preference: the watch picks the first type a provider offers,
# so ranged providers (battery, stress) deliver a value we can turn into Low/Medium/High.
TYPES = {
    "side":   "RANGED_VALUE GOAL_PROGRESS SHORT_TEXT MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY",
    "bottom": "RANGED_VALUE GOAL_PROGRESS SHORT_TEXT LONG_TEXT MONOCHROMATIC_IMAGE EMPTY",
    "round":  "RANGED_VALUE GOAL_PROGRESS SHORT_TEXT MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY",
}
TEXT_SIZE = {"side": 30, "bottom": 30, "round": 14}
WORD_SIZE = {"side": 24, "bottom": 28, "round": 12}   # level words are longer than numbers

# "Stress level words" setting: which slot turns its min-max value into Samsung-style
# stress words. Samsung shows four levels: Relaxed, Low, Medium, High. The bands below are
# even quarters of the range (our assumption, Samsung doesn't publish its cut-offs).
LEVEL_OPTIONS = [("off", "level_off", "lvl_off")] + [(f"s{s[0]}", s[1], f"lvl_s{s[0]}") for s in SLOTS]
LEVELS = [(0.75, "level_high"), (0.50, "level_medium"), (0.25, "level_low")]   # else Relaxed

RANGE = "([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN])"
GOAL = "[COMPLICATION.GOAL_PROGRESS_VALUE] / [COMPLICATION.GOAL_PROGRESS_TARGET_VALUE]"

# Words shown on the face itself (not settings). Kept English: WFF Templates take literals.
WORDS = {"level_high": "HIGH", "level_medium": "MEDIUM", "level_low": "LOW", "level_relaxed": "RELAXED"}


def ind(s, n):
    pad = " " * n
    return "".join(pad + line if line.strip() else line for line in s.splitlines(True))


def text_part(x, y, w, h, template, size, color=None, align="CENTER", params=()):
    color = color or c(2)
    p = "".join(f'<Parameter expression="{e}"/>' for e in params)
    body = f'<Template>{template}{p}</Template>' if params else template   # literal text needs no Template
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}">\n'
            f'  <Text align="{align}" ellipsis="TRUE">\n'
            f'    <Font family="{FONT}" size="{size}" color="{color}">{body}</Font>\n'
            f'  </Text>\n'
            f'</PartText>\n')


def value_text(kind, x, y, w, h, frac_expr, value_expr):
    """Complication text, or the value itself when the provider sends no text."""
    sz = TEXT_SIZE[kind]
    return (
        '<Condition>\n'
        '  <Expressions>\n'
        '    <Expression name="hasText">textLength([COMPLICATION.TEXT]) &gt; 0</Expression>\n'
        '  </Expressions>\n'
        '  <Compare expression="hasText">\n'
        + ind(text_part(x, y, w, h, "%s", sz, params=["[COMPLICATION.TEXT]"]), 4) +
        '  </Compare>\n'
        '  <Default>\n'
        + ind(text_part(x, y, w, h, "%d", sz, params=[f"round({value_expr})"]), 4) +
        '  </Default>\n'
        '</Condition>\n')


def level_text(kind, x, y, w, h, frac_expr):
    sz = WORD_SIZE[kind]
    exprs = "".join(f'    <Expression name="lv{i}">{frac_expr} &gt;= {t}</Expression>\n'
                    for i, (t, _) in enumerate(LEVELS))
    cmps = "".join('  <Compare expression="lv%d">\n' % i
                   + ind(text_part(x, y, w, h, WORDS[word], sz), 4) + '  </Compare>\n'
                   for i, (_, word) in enumerate(LEVELS))
    return ('<Condition>\n  <Expressions>\n' + exprs + '  </Expressions>\n' + cmps +
            '  <Default>\n' + ind(text_part(x, y, w, h, WORDS["level_relaxed"], sz), 4) +
            '  </Default>\n</Condition>\n')


def ranged_text(slot_id, kind, x, y, w, h, frac_expr, value_expr):
    """Number by default; Low/Medium/High when the user picked this slot in settings."""
    opts = []
    for oid, _, _ in LEVEL_OPTIONS:
        body = (level_text(kind, x, y, w, h, frac_expr) if oid == f"s{slot_id}"
                else value_text(kind, x, y, w, h, frac_expr, value_expr))
        opts.append(f'  <ListOption id="{oid}">\n' + ind(body, 4) + '  </ListOption>\n')
    return ('<Group name="levelText" x="0" y="0" width="%d" height="%d">\n' % (SIZES[kind])
            + '  <ListConfiguration id="levelSlot">\n' + ind("".join(opts), 2)
            + '  </ListConfiguration>\n</Group>\n')


def bar(x, y, w, h, frac_expr):
    r = h / 2
    return (f'<PartDraw x="{x}" y="{y}" width="{w}" height="{h}">\n'
            f'  <RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="{r}" cornerRadiusY="{r}">\n'
            f'    <Fill color="#33FFFFFF"/>\n'
            f'  </RoundRectangle>\n'
            f'  <RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="{r}" cornerRadiusY="{r}">\n'
            f'    <Fill color="{c(1)}"/>\n'
            f'    <Transform target="width" value="{w} * clamp({frac_expr}, 0, 1)"/>\n'
            f'  </RoundRectangle>\n'
            f'</PartDraw>\n')


def ring(size, frac_expr):
    m, t = 3, 4
    d = size - 2 * m
    return (f'<PartDraw x="0" y="0" width="{size}" height="{size}">\n'
            f'  <Arc centerX="{size / 2}" centerY="{size / 2}" width="{d}" height="{d}" startAngle="0" endAngle="360">\n'
            f'    <Stroke color="#33FFFFFF" thickness="{t}"/>\n'
            f'  </Arc>\n'
            f'  <Arc centerX="{size / 2}" centerY="{size / 2}" width="{d}" height="{d}" startAngle="0" endAngle="0">\n'
            f'    <Stroke color="{c(1)}" thickness="{t}" cap="ROUND"/>\n'
            f'    <Transform target="endAngle" value="360 * clamp({frac_expr}, 0, 1)"/>\n'
            f'  </Arc>\n'
            f'</PartDraw>\n')


def image(x, y, w, h, src, tint=True):
    t = f' tintColor="{c(2)}"' if tint else ""
    return (f'<PartImage x="{x}" y="{y}" width="{w}" height="{h}"{t}>\n'
            f'  <Image resource="{src}"/>\n'
            f'</PartImage>\n')


def progress_content(slot_id, kind, frac_expr, value_expr):
    W, H = SIZES[kind]
    if kind == "round":
        return ring(W, frac_expr) + ranged_text(slot_id, kind, 4, 19, W - 8, 22, frac_expr, value_expr)
    bw = 64 if kind == "side" else W - 60
    return (ranged_text(slot_id, kind, 0, 0, W, 36, frac_expr, value_expr)
            + bar((W - bw) // 2, 39, bw, 5, frac_expr))


def short_content(kind):
    W, H = SIZES[kind]
    sz = TEXT_SIZE[kind]
    if kind == "round":
        return (image((W - 20) // 2, 9, 20, 20, "[COMPLICATION.MONOCHROMATIC_IMAGE]")
                + text_part(4, 29, W - 8, 22, "%s", sz, params=["[COMPLICATION.TEXT]"]))
    return text_part(0, 4, W, 40, "%s", sz, params=["[COMPLICATION.TEXT]"])


def weather_content(W, H):
    """Bottom slot when empty: built-in weather (WFF v2), icon + temperature, centred."""
    icons = "".join(f'    <Expression name="w{i}">{e}</Expression>\n' for i, (e, _) in enumerate(WEATHER_ICONS))
    def line(icon):
        img = f'<InlineImage resource="{icon}" width="30" height="30" color="{c(1)}"/>' if icon else ""
        return (f'<PartText x="0" y="4" width="{W}" height="40">\n'
                f'  <Text align="CENTER">\n'
                f'    <Font family="{FONT}" size="30" color="{c(2)}">{img}<Template> %d°'
                f'<Parameter expression="round([WEATHER.TEMPERATURE])"/></Template></Font>\n'
                f'  </Text>\n'
                f'</PartText>\n')
    cmps = "".join(f'    <Compare expression="w{i}">\n' + ind(line(ic), 6) + '    </Compare>\n'
                   for i, (_, ic) in enumerate(WEATHER_ICONS))
    return ('<Condition>\n'
            '  <Expressions>\n'
            '    <Expression name="hasWeather">[WEATHER.IS_AVAILABLE] &amp;&amp; !([WEATHER.IS_ERROR])</Expression>\n'
            '  </Expressions>\n'
            '  <Compare expression="hasWeather">\n'
            '    <Condition>\n'
            '      <Expressions>\n' + ind(icons, 4) + '      </Expressions>\n'
            + ind(cmps, 2) +
            '      <Default>\n' + ind(line(None), 8) + '      </Default>\n'
            '    </Condition>\n'
            '  </Compare>\n'
            '</Condition>\n')


def heart_content(W, H):
    """Small slot when empty: built-in heart rate with an optional beating heart."""
    def heart(animated):
        tr = ""
        if animated:
            anim = '<Animation interpolation="EASE_OUT" duration="0.9" repeat="-1" fps="15"/>'
            tr = (f'  <Transform target="scaleX" value="0.72">{anim}</Transform>\n'
                  f'  <Transform target="scaleY" value="0.72">{anim}</Transform>\n')
        return (f'<PartImage x="{(W - 22) // 2}" y="7" width="22" height="22" pivotX="0.5" pivotY="0.5">\n'
                f'  <Image resource="ic_heart"/>\n{tr}</PartImage>\n')
    bpm = ('<Condition>\n'
           '  <Expressions>\n'
           '    <Expression name="hasHr">[HEART_RATE] &gt; 0</Expression>\n'
           '  </Expressions>\n'
           '  <Compare expression="hasHr">\n'
           + ind(text_part(4, 29, W - 8, 22, "%d", 17, params=["round([HEART_RATE])"]), 4) +
           '  </Compare>\n'
           '  <Default>\n' + ind(text_part(4, 29, W - 8, 22, "--", 17), 4) + '  </Default>\n'
           '</Condition>\n')
    return (f'<Group name="heart" x="0" y="0" width="{W}" height="{H}">\n'
            '<BooleanConfiguration id="heartbeat">\n'
            '  <BooleanOption id="TRUE">\n'
            f'    <Group name="heartOn" x="0" y="0" width="{W}" height="{H}">\n'
            + ind(heart(True) + bpm, 6) +
            '    </Group>\n'
            '  </BooleanOption>\n'
            '  <BooleanOption id="FALSE">\n'
            f'    <Group name="heartOff" x="0" y="0" width="{W}" height="{H}">\n'
            + ind(heart(False) + bpm, 6) +
            '    </Group>\n'
            '  </BooleanOption>\n'
            '</BooleanConfiguration>\n'
            '</Group>\n')


def slot(sid, name, kind, cx, cy, angle, provider, ptype):
    W, H = SIZES[kind]
    x, y = cx - W // 2, cy - H // 2
    if kind == "round":
        bound = f'<BoundingOval x="0" y="0" width="{W}" height="{H}"/>'
    else:
        bound = f'<BoundingRoundBox x="0" y="0" width="{W}" height="{H}" cornerRadius="{H // 2}"/>'
    sz = 34 if kind != "round" else 30
    mono = image((W - sz) // 2, (H - sz) // 2, sz, sz, "[COMPLICATION.MONOCHROMATIC_IMAGE]")
    small = image((W - sz) // 2, (H - sz) // 2, sz, sz, "[COMPLICATION.SMALL_IMAGE]", tint=False)
    parts = {
        "RANGED_VALUE": progress_content(sid, kind, RANGE, "[COMPLICATION.RANGED_VALUE_VALUE]"),
        "GOAL_PROGRESS": progress_content(sid, kind, GOAL, "[COMPLICATION.GOAL_PROGRESS_VALUE]"),
        "SHORT_TEXT": short_content(kind),
        "LONG_TEXT": text_part(0, 6, W, 36, "%s", 24, params=["[COMPLICATION.TEXT]"]),
        "MONOCHROMATIC_IMAGE": mono,
        "SMALL_IMAGE": small,
        "EMPTY": (weather_content(W, H) if sid == 2 else heart_content(W, H) if sid == 3 else ""),
    }
    angle_attr = f' angle="{angle}"' if angle else ""
    out = (f'<ComplicationSlot slotId="{sid}" displayName="{name}" x="{x}" y="{y}" width="{W}" height="{H}"'
           f'{angle_attr} isCustomizable="TRUE" supportedTypes="{TYPES[kind]}">\n'
           f'  <DefaultProviderPolicy defaultSystemProvider="{provider}" defaultSystemProviderType="{ptype}"/>\n'
           f'  {bound}\n'
           f'  <Variant mode="AMBIENT" target="alpha" value="0"/>\n')
    for t in TYPES[kind].split():
        body = parts[t]
        out += (f'  <Complication type="{t}">\n' + ind(body, 4) + '  </Complication>\n') if body \
            else f'  <Complication type="{t}"/>\n'
    return out + '</ComplicationSlot>\n'


# ---- Scene pieces ---------------------------------------------------------------------
def time_text(fmt, x, y, color):
    return (f'<TimeText format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="CENTER" '
            f'x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}">\n'
            f'  <Font family="{FONT}" size="{SIZE}" color="{color}"/>\n'
            f'</TimeText>\n')


def digit_clock():
    body = ""
    for fmt, col, row, tone in DIGITS:
        x, y = COL_X[col] - BOX_W // 2, ROW_Y[row]
        body += time_text(fmt, x + SHADOW, y + SHADOW, "#FF000000")   # carved shadow
        body += time_text(fmt, x, y, c(tone))
    return '<DigitalClock x="0" y="0" width="450" height="450">\n' + ind(body, 2) + '</DigitalClock>\n'


def ambient_clock():
    body = ""
    for fmt, col, row, tone in DIGITS:
        x, y = COL_X[col] - AMB_W // 2, ROW_Y[row] + AMB_TOP
        body += (f'<TimeText format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="CENTER" '
                 f'x="{x}" y="{y}" width="{AMB_W}" height="{AMB_H}">\n'
                 f'  <BitmapFont family="amb_{"ab"[tone]}" size="{AMB_H}"/>\n'
                 f'</TimeText>\n')
    return '<DigitalClock x="0" y="0" width="450" height="450">\n' + ind(body, 2) + '</DigitalClock>\n'


def bitmap_fonts():
    fonts = ""
    for t in "ab":
        chars = "".join(f'  <Character name="{d}" resource="amb_{t}_{d}" width="{AMB_W}" height="{AMB_H}"/>\n'
                        for d in "0123456789")
        fonts += f'<BitmapFont name="amb_{t}">\n{chars}</BitmapFont>\n'
    return '<BitmapFonts>\n' + ind(fonts, 2) + '</BitmapFonts>\n'


def date_arc():
    def half(start, end, align, template, params):
        p = "".join(f'<Parameter expression="{e}"/>' for e in params)
        return (f'<PartText x="0" y="0" width="450" height="450">\n'
                f'  <Variant mode="AMBIENT" target="alpha" value="150"/>\n'
                f'  <TextCircular centerX="225" centerY="225" width="{DATE_R}" height="{DATE_R}" '
                f'startAngle="{start}" endAngle="{end}" direction="CLOCKWISE" align="{align}">\n'
                f'    <Font family="{FONT}" size="30" color="{c(2)}" letterSpacing="0.04">'
                f'<Upper><Template>{template}{p}</Template></Upper></Font>\n'
                f'  </TextCircular>\n'
                f'</PartText>\n')
    both = (half(-DATE_SPAN, -DATE_GAP, "END", "%s", ["[DAY_OF_WEEK_S]"])
            + half(DATE_GAP, DATE_SPAN, "START", "%s %s", ["[MONTH_S]", "[DAY]"]))
    return ('<BooleanConfiguration id="showDate">\n'
            '  <BooleanOption id="TRUE">\n'
            '    <Group name="date" x="0" y="0" width="450" height="450">\n'
            + ind(both, 6) +
            '    </Group>\n'
            '  </BooleanOption>\n'
            '</BooleanConfiguration>\n')


def rain_layer():
    """Falling streaks, only while it is raining, only in interactive mode, only if enabled."""
    drops = ""
    for x, y0, ln, sec in RAIN_DROPS:
        drops += (f'<PartDraw x="{x}" y="{y0}" width="4" height="{ln}" alpha="110">\n'
                  f'  <Line startX="2" startY="0" endX="2" endY="{ln}">\n'
                  f'    <Stroke color="{c(1)}" thickness="3" cap="ROUND"/>\n'
                  f'  </Line>\n'
                  f'  <Transform target="y" value="{y0 + 560}">'
                  f'<Animation interpolation="LINEAR" duration="{sec}" repeat="-1" fps="15"/></Transform>\n'
                  f'</PartDraw>\n')
    cond = " || ".join(f"[WEATHER.CONDITION] == {v}" for v in RAINY)
    return ('<BooleanConfiguration id="rainFx">\n'
            '  <BooleanOption id="TRUE">\n'
            '    <Group name="rain" x="0" y="0" width="450" height="450">\n'
            '      <Variant mode="AMBIENT" target="alpha" value="0"/>\n'
            '      <Condition>\n'
            '        <Expressions>\n'
            f'          <Expression name="raining">[WEATHER.IS_AVAILABLE] &amp;&amp; ({cond})</Expression>\n'
            '        </Expressions>\n'
            '        <Compare expression="raining">\n'
            '          <Group name="drops" x="0" y="0" width="450" height="450">\n'
            + ind(drops, 12) +
            '          </Group>\n'
            '        </Compare>\n'
            '      </Condition>\n'
            '    </Group>\n'
            '  </BooleanOption>\n'
            '</BooleanConfiguration>\n')


def user_configs():
    colors = "".join(f'<ColorOption id="{i}" displayName="{name}" colors="{" ".join(cols)}"/>\n'
                     for i, (_, name, cols) in enumerate(THEMES))
    levels = "".join(f'<ListOption id="{oid}" displayName="{name}" icon="{icon}"/>\n'
                     for oid, name, icon in LEVEL_OPTIONS)
    return ('<UserConfigurations>\n'
            '  <ColorConfiguration id="theme" displayName="cfg_theme" defaultValue="0">\n'
            + ind(colors, 4) +
            '  </ColorConfiguration>\n'
            '  <BooleanConfiguration id="showDate" displayName="cfg_date" defaultValue="TRUE"/>\n'
            '  <BooleanConfiguration id="heartbeat" displayName="cfg_heartbeat" defaultValue="TRUE"/>\n'
            '  <BooleanConfiguration id="rainFx" displayName="cfg_rain" defaultValue="TRUE"/>\n'
            '  <ListConfiguration id="levelSlot" displayName="cfg_levels" defaultValue="off">\n'
            + ind(levels, 4) +
            '  </ListConfiguration>\n'
            '</UserConfigurations>\n')


def main():
    scene = (rain_layer()
             + date_arc()
             + '<Group name="digitsActive" x="0" y="0" width="450" height="450" alpha="255">\n'
             '  <Variant mode="AMBIENT" target="alpha" value="0"/>\n'
             + ind(digit_clock(), 2) + '</Group>\n'
             + '<Group name="digitsAmbient" x="0" y="0" width="450" height="450" alpha="0">\n'
             '  <Variant mode="AMBIENT" target="alpha" value="255"/>\n'
             + ind(ambient_clock(), 2) + '</Group>\n'
             + "".join(slot(*s) for s in SLOTS))
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<!-- Overlap: stacked two-tone digital watch face. Watch Face Format v2. '
           'GENERATED by design/gen_watchface.py, do not edit by hand. -->\n'
           '<WatchFace width="450" height="450" clipShape="CIRCLE">\n'
           '  <Metadata key="CLOCK_TYPE" value="DIGITAL"/>\n'
           '  <Metadata key="PREVIEW_TIME" value="10:08:32"/>\n'
           + ind(user_configs(), 2) + ind(bitmap_fonts(), 2)
           + '  <Scene backgroundColor="#FF000000">\n' + ind(scene, 4) + '  </Scene>\n'
           '</WatchFace>\n')
    print(xml, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generates res/raw/watchface.xml for the "Overlap" Watch Face Format (v2) face.

Run from the face folder (faces/overlap):
    python3 design/make_ambient_digits.py
    python3 design/gen_watchface.py > src/main/res/raw/watchface.xml
All geometry is for a 450x450 round canvas (Galaxy Watch 7 renders WFF at 450).
"""

FONT = "fredoka_bold"

# Theme colours: [0] digit A, [1] digit B, [2] accent text
THEMES = [
    ("oat",     "Oat",     ["#FFF2E8D5", "#FFC9AA80", "#FFE6D6BC"]),
    ("sage",    "Sage",    ["#FFE4F0DC", "#FF8FBF7E", "#FFCDE3C2"]),
    ("coral",   "Coral",   ["#FFFFE3D8", "#FFF2815F", "#FFFFD0BF"]),
    ("glacier", "Glacier", ["#FFE2F0FA", "#FF74AEDD", "#FFCDE5F6"]),
    ("lilac",   "Lilac",   ["#FFEFE6FB", "#FFAA92DE", "#FFDFD2F6"]),
    ("mono",    "Mono",    ["#FFF5F5F5", "#FF9A9A9A", "#FFE2E2E2"]),
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
# neutral-grey stroke, so ~5% of pixels are lit instead of ~25% with filled digits.
AMB_STROKE = 3
AMB_TONES = ("#C4C4C4", "#7E7E7E")   # tone A, tone B (fixed greys, theme-independent)
AMB_W, AMB_H, AMB_TOP = 130, 165, 54  # must match make_ambient_digits.py (it checks)


def time_text(fmt, x, y, color):
    return (f'      <TimeText format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="CENTER" '
            f'x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}">\n'
            f'        <Font family="{FONT}" size="{SIZE}" color="{color}"/>\n'
            f'      </TimeText>\n')


def digit_clock():
    out = []
    for fmt, col, row, tone in DIGITS:
        x = COL_X[col] - BOX_W // 2
        y = ROW_Y[row]
        # shadow first, then the digit itself
        out.append(time_text(fmt, x + SHADOW, y + SHADOW, "#FF000000"))
        out.append(time_text(fmt, x, y, c(tone)))
    body = "".join(out)
    return (f'    <DigitalClock x="0" y="0" width="450" height="450">\n{body}    </DigitalClock>\n')


def ambient_clock():
    out = []
    for fmt, col, row, tone in DIGITS:
        x = COL_X[col] - AMB_W // 2
        y = ROW_Y[row] + AMB_TOP
        fam = "amb_" + "ab"[tone]
        out.append(f'      <TimeText format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="CENTER" '
                   f'x="{x}" y="{y}" width="{AMB_W}" height="{AMB_H}">\n'
                   f'        <BitmapFont family="{fam}" size="{AMB_H}"/>\n'
                   f'      </TimeText>\n')
    body = "".join(out)
    return (f'    <DigitalClock x="0" y="0" width="450" height="450">\n{body}    </DigitalClock>\n')


def bitmap_fonts():
    fonts = []
    for t in "ab":
        chars = "".join(
            f'      <Character name="{d}" resource="amb_{t}_{d}" width="{AMB_W}" height="{AMB_H}"/>\n'
            for d in "0123456789")
        fonts.append(f'    <BitmapFont name="amb_{t}">\n{chars}    </BitmapFont>\n')
    return '  <BitmapFonts>\n' + "".join(fonts) + '  </BitmapFonts>\n'


# ---- Complications --------------------------------------------------------
SIDE_W, SIDE_H = 124, 46


def side_slot(slot_id, name, cx, angle, provider, ptype):
    x = cx - SIDE_W // 2
    y = 225 - SIDE_H // 2
    bar_w = 64
    bar_x = (SIDE_W - bar_w) // 2
    text = (f'          <PartText x="0" y="2" width="{SIDE_W}" height="34">\n'
            f'            <Text align="CENTER" ellipsis="TRUE">\n'
            f'              <Font family="{FONT}" size="30" color="{c(2)}">'
            f'<Template>%s<Parameter expression="[COMPLICATION.TEXT]"/></Template></Font>\n'
            f'            </Text>\n'
            f'          </PartText>\n')
    ranged_text = text.replace('y="2"', 'y="0"')
    ranged_bar = (
        f'          <PartDraw x="{bar_x}" y="38" width="{bar_w}" height="5">\n'
        f'            <RoundRectangle x="0" y="0" width="{bar_w}" height="5" cornerRadiusX="2.5" cornerRadiusY="2.5">\n'
        f'              <Fill color="#33FFFFFF"/>\n'
        f'            </RoundRectangle>\n'
        f'            <RoundRectangle x="0" y="0" width="{bar_w}" height="5" cornerRadiusX="2.5" cornerRadiusY="2.5">\n'
        f'              <Fill color="{c(1)}"/>\n'
        f'              <Transform target="width" value="{bar_w} * clamp(([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN]), 0, 1)"/>\n'
        f'            </RoundRectangle>\n'
        f'          </PartDraw>\n')
    icon = (f'          <PartImage x="{(SIDE_W - 34) // 2}" y="6" width="34" height="34" tintColor="{c(2)}">\n'
            f'            <Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/>\n'
            f'          </PartImage>\n')
    small = (f'          <PartImage x="{(SIDE_W - 36) // 2}" y="5" width="36" height="36">\n'
             f'            <Image resource="[COMPLICATION.SMALL_IMAGE]"/>\n'
             f'          </PartImage>\n')
    return (
        f'    <ComplicationSlot slotId="{slot_id}" displayName="{name}" x="{x}" y="{y}" '
        f'width="{SIDE_W}" height="{SIDE_H}" angle="{angle}" isCustomizable="TRUE" '
        f'supportedTypes="SHORT_TEXT RANGED_VALUE MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY">\n'
        f'      <DefaultProviderPolicy defaultSystemProvider="{provider}" defaultSystemProviderType="{ptype}"/>\n'
        f'      <BoundingRoundBox x="0" y="0" width="{SIDE_W}" height="{SIDE_H}" cornerRadius="23"/>\n'
        f'      <Variant mode="AMBIENT" target="alpha" value="0"/>\n'
        f'      <Complication type="SHORT_TEXT">\n{text}      </Complication>\n'
        f'      <Complication type="RANGED_VALUE">\n{ranged_text}{ranged_bar}      </Complication>\n'
        f'      <Complication type="MONOCHROMATIC_IMAGE">\n{icon}      </Complication>\n'
        f'      <Complication type="SMALL_IMAGE">\n{small}      </Complication>\n'
        f'      <Complication type="EMPTY"/>\n'
        f'    </ComplicationSlot>\n')


BOT_W, BOT_H = 160, 48
BOT_X, BOT_Y = 225 - BOT_W // 2, 378


def bottom_slot():
    W, H = BOT_W, BOT_H
    short = (
        f'          <PartImage x="6" y="{(H - 28) // 2}" width="28" height="28" tintColor="{c(2)}">\n'
        f'            <Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/>\n'
        f'          </PartImage>\n'
        f'          <PartText x="36" y="4" width="{W - 42}" height="40">\n'
        f'            <Text align="START" ellipsis="TRUE">\n'
        f'              <Font family="{FONT}" size="30" color="{c(2)}">'
        f'<Template>%s<Parameter expression="[COMPLICATION.TEXT]"/></Template></Font>\n'
        f'            </Text>\n'
        f'          </PartText>\n')
    ranged = short + (
        f'          <PartDraw x="36" y="42" width="{W - 52}" height="4">\n'
        f'            <RoundRectangle x="0" y="0" width="{W - 52}" height="4" cornerRadiusX="2" cornerRadiusY="2">\n'
        f'              <Fill color="#33FFFFFF"/>\n'
        f'            </RoundRectangle>\n'
        f'            <RoundRectangle x="0" y="0" width="{W - 52}" height="4" cornerRadiusX="2" cornerRadiusY="2">\n'
        f'              <Fill color="{c(1)}"/>\n'
        f'              <Transform target="width" value="{W - 52} * clamp(([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN]), 0, 1)"/>\n'
        f'            </RoundRectangle>\n'
        f'          </PartDraw>\n')
    longt = (
        f'          <PartText x="0" y="4" width="{W}" height="40">\n'
        f'            <Text align="CENTER" ellipsis="TRUE">\n'
        f'              <Font family="{FONT}" size="24" color="{c(2)}">'
        f'<Template>%s<Parameter expression="[COMPLICATION.TEXT]"/></Template></Font>\n'
        f'            </Text>\n'
        f'          </PartText>\n')
    mono = (f'          <PartImage x="{(W - 36) // 2}" y="6" width="36" height="36" tintColor="{c(2)}">\n'
            f'            <Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/>\n'
            f'          </PartImage>\n')
    # EMPTY: built-in weather (WFF v2 WEATHER.* data) so the slot shows temperature out of the box
    weather = (
        f'          <Condition>\n'
        f'            <Expressions>\n'
        f'              <Expression name="hasWeather">[WEATHER.IS_AVAILABLE] &amp;&amp; !([WEATHER.IS_ERROR])</Expression>\n'
        f'            </Expressions>\n'
        f'            <Compare expression="hasWeather">\n'
        f'              <PartDraw x="36" y="12" width="24" height="24">\n'
        f'                <Ellipse x="5" y="5" width="14" height="14">\n'
        f'                  <Stroke color="{c(1)}" thickness="3"/>\n'
        f'                </Ellipse>\n'
        f'              </PartDraw>\n'
        f'              <PartText x="62" y="4" width="{W - 66}" height="40">\n'
        f'                <Text align="START">\n'
        f'                  <Font family="{FONT}" size="30" color="{c(2)}">'
        f'<Template>%d°<Parameter expression="round([WEATHER.TEMPERATURE])"/></Template></Font>\n'
        f'                </Text>\n'
        f'              </PartText>\n'
        f'            </Compare>\n'
        f'          </Condition>\n')
    return (
        f'    <ComplicationSlot slotId="2" displayName="Bottom" x="{BOT_X}" y="{BOT_Y}" '
        f'width="{W}" height="{H}" isCustomizable="TRUE" '
        f'supportedTypes="SHORT_TEXT RANGED_VALUE LONG_TEXT MONOCHROMATIC_IMAGE EMPTY">\n'
        f'      <DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY"/>\n'
        f'      <BoundingRoundBox x="0" y="0" width="{W}" height="{H}" cornerRadius="24"/>\n'
        f'      <Variant mode="AMBIENT" target="alpha" value="0"/>\n'
        f'      <Complication type="SHORT_TEXT">\n{short}      </Complication>\n'
        f'      <Complication type="RANGED_VALUE">\n{ranged}      </Complication>\n'
        f'      <Complication type="LONG_TEXT">\n{longt}      </Complication>\n'
        f'      <Complication type="MONOCHROMATIC_IMAGE">\n{mono}      </Complication>\n'
        f'      <Complication type="EMPTY">\n{weather}      </Complication>\n'
        f'    </ComplicationSlot>\n')


def date_arc():
    # Curved date along the top edge, e.g. "WED, NOV 4"
    return (
        '    <BooleanConfiguration id="showDate">\n'
        '      <BooleanOption id="TRUE">\n'
        '        <PartText x="0" y="0" width="450" height="450">\n'
        '          <Variant mode="AMBIENT" target="alpha" value="150"/>\n'
        '          <TextCircular centerX="225" centerY="225" width="376" height="376" '
        'startAngle="-60" endAngle="60" direction="CLOCKWISE" align="CENTER">\n'
        f'            <Font family="{FONT}" size="30" color="{c(2)}" letterSpacing="0.04">'
        '<Upper><Template>%s, %s %s'
        '<Parameter expression="[DAY_OF_WEEK_S]"/>'
        '<Parameter expression="[MONTH_S]"/>'
        '<Parameter expression="[DAY]"/>'
        '</Template></Upper></Font>\n'
        '          </TextCircular>\n'
        '        </PartText>\n'
        '      </BooleanOption>\n'
        '    </BooleanConfiguration>\n')


def user_configs():
    opts = "".join(
        f'      <ColorOption id="{i}" displayName="{label}" colors="{" ".join(cols)}"/>\n'
        for i, (_, label, cols) in enumerate(THEMES))
    return (
        '  <UserConfigurations>\n'
        '    <ColorConfiguration id="theme" displayName="Color theme" defaultValue="0">\n'
        f'{opts}'
        '    </ColorConfiguration>\n'
        '    <BooleanConfiguration id="showDate" displayName="Show date" defaultValue="TRUE"/>\n'
        '  </UserConfigurations>\n')


def main():
    active = digit_clock()
    ambient = ambient_clock()
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!-- Overlap: stacked two-tone digital watch face. Watch Face Format v2, generated by gen_watchface.py -->\n'
        '<WatchFace width="450" height="450" clipShape="CIRCLE">\n'
        '  <Metadata key="CLOCK_TYPE" value="DIGITAL"/>\n'
        '  <Metadata key="PREVIEW_TIME" value="10:08:32"/>\n'
        f'{user_configs()}'
        f'{bitmap_fonts()}'
        '  <Scene backgroundColor="#FF000000">\n'
        f'{date_arc()}'
        '    <Group name="digitsActive" x="0" y="0" width="450" height="450" alpha="255">\n'
        '      <Variant mode="AMBIENT" target="alpha" value="0"/>\n'
        f'{indent(active, 2)}'
        '    </Group>\n'
        '    <Group name="digitsAmbient" x="0" y="0" width="450" height="450" alpha="0">\n'
        '      <Variant mode="AMBIENT" target="alpha" value="255"/>\n'
        f'{indent(ambient, 2)}'
        '    </Group>\n'
        f'{side_slot(0, "Left", 40, -90, "WATCH_BATTERY", "SHORT_TEXT")}'
        f'{side_slot(1, "Right", 410, 90, "STEP_COUNT", "SHORT_TEXT")}'
        f'{bottom_slot()}'
        '  </Scene>\n'
        '</WatchFace>\n')
    print(xml, end="")


def indent(s, n):
    pad = " " * n
    return "".join(pad + line if line.strip() else line for line in s.splitlines(True))


if __name__ == "__main__":
    main()

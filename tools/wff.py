"""Shared Watch Face Format (v2) XML helpers for the face generators in faces/*/design/.

Each face's gen_watchface.py imports this module:
    sys.path.insert(0, os.path.join(<repo>, "tools")); import wff
Everything here returns XML text. Geometry is for the 450x450 round canvas.
Angles: 0 = 12 o'clock, clockwise.
"""

CANVAS = 450

# ---- Text ---------------------------------------------------------------------------


def ind(s, n):
    """Indent every non-blank line of s by n spaces."""
    pad = " " * n
    return "".join(pad + line if line.strip() else line for line in s.splitlines(True))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")


def theme(i, cfg="theme"):
    """Reference to colour i of a ColorConfiguration."""
    return f"[CONFIGURATION.{cfg}.{i}]"


def tmpl(template, params):
    """Literal text, or a <Template> with one <Parameter> per expression."""
    if not params:
        return esc(template)
    p = "".join(f'<Parameter expression="{e}"/>' for e in params)
    return f"<Template>{esc(template)}{p}</Template>"


def font(family, size, color, body, extra=""):
    return f'<Font family="{family}" size="{size}" color="{color}"{extra}>{body}</Font>'


def text(family, x, y, w, h, body, size, color, align="CENTER", extra=""):
    """Single-line PartText. `extra` goes inside <PartText> before <Text> (e.g. a Localization)."""
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}">\n{extra}'
            f'  <Text align="{align}" ellipsis="TRUE">{font(family, size, color, body)}</Text>\n'
            f'</PartText>\n')


def cond(exprs, cases, default=""):
    """<Condition>. exprs: [(name, expression)], cases: [(name, xml)], default: xml."""
    e = "".join(f'    <Expression name="{n}">{x}</Expression>\n' for n, x in exprs)
    cs = "".join(f'  <Compare expression="{n}">\n' + ind(b, 4) + '  </Compare>\n' for n, b in cases)
    d = ('  <Default>\n' + ind(default, 4) + '  </Default>\n') if default else ""
    return '<Condition>\n  <Expressions>\n' + e + '  </Expressions>\n' + cs + d + '</Condition>\n'


def group(name, body, x=0, y=0, w=CANVAS, h=CANVAS, attrs=""):
    return (f'<Group name="{name}" x="{x}" y="{y}" width="{w}" height="{h}"{attrs}>\n'
            + ind(body, 2) + '</Group>\n')


def image(x, y, w, h, res, tint=None, extra=""):
    t = f' tintColor="{tint}"' if tint else ""
    return (f'<PartImage x="{x}" y="{y}" width="{w}" height="{h}"{t}{extra}>\n'
            f'  <Image resource="{res}"/>\n'
            f'</PartImage>\n')


# ---- Clock --------------------------------------------------------------------------


def time_text(fmt, x, y, w, h, family, size, color, align="CENTER"):
    return (f'<TimeText format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="{align}" '
            f'x="{x}" y="{y}" width="{w}" height="{h}">\n'
            f'  <Font family="{family}" size="{size}" color="{color}"/>\n'
            f'</TimeText>\n')


def digital_clock(body):
    """One DigitalClock around all TimeTexts: one time binding instead of one per digit."""
    return f'<DigitalClock x="0" y="0" width="{CANVAS}" height="{CANVAS}">\n' + ind(body, 2) + '</DigitalClock>\n'


# ---- Always-on ------------------------------------------------------------------------


def active_only(name, body, attrs=""):
    """Group drawn in interactive mode, hidden in always-on."""
    return group(name, '<Variant mode="AMBIENT" target="alpha" value="0"/>\n' + body, attrs=attrs)


def ambient_only(name, body):
    """Group hidden in interactive mode, drawn in always-on."""
    return group(name, '<Variant mode="AMBIENT" target="alpha" value="255"/>\n' + body, attrs=' alpha="0"')


# ---- Weather --------------------------------------------------------------------------
# WEATHER.CONDITION values 0..15 (developer.android.com/reference/wear-os/wff/common/
# attributes/source-type). First match wins; 0 (unknown) and anything unmatched fall
# through to the caller's default.
RAIN_CODES, SNOW_CODES, STORM = (4, 6, 10, 12), (5, 7, 11), 9
WEATHER_KINDS = [
    ((STORM,),   "storm"),
    (RAIN_CODES, "rain"),
    (SNOW_CODES, "snow"),
    ((3, 13),    "fog"),
    ((2,),       "cloud"),
    ((14,),      "partly"),
    ((15,),      "wind"),
    ((1, 8),     "clear"),
]
WX_OK = "[WEATHER.IS_AVAILABLE] &amp;&amp; !([WEATHER.IS_ERROR])"


def any_of(src, codes):
    e = " || ".join(f"{src} == {v}" for v in codes)
    return f"({e})" if len(codes) > 1 else e


def weather_cases(src, pick, isday=None):
    """[(expression, resource)] for a condition source.
    pick(kind) -> (day resource, night resource). isday=None means daytime only."""
    out = []
    for codes, kind in WEATHER_KINDS:
        day, night = pick(kind)
        e = any_of(src, codes)
        if isday and day != night:
            out.append((f"{e} &amp;&amp; {isday}", day))
            out.append((e, night))
        else:
            out.append((e, day))
    return out


def weather_switch(src, pick, draw, default="", isday=None):
    """Condition that draws draw(resource) for the matching weather kind."""
    cases = weather_cases(src, pick, isday)
    return cond([(f"i{i}", e) for i, (e, _) in enumerate(cases)],
                [(f"i{i}", draw(r)) for i, (_, r) in enumerate(cases)], default)


# ---- Complications ----------------------------------------------------------------------
RANGE = "([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN])"
GOAL = "[COMPLICATION.GOAL_PROGRESS_VALUE] / [COMPLICATION.GOAL_PROGRESS_TARGET_VALUE]"
MONO = "[COMPLICATION.MONOCHROMATIC_IMAGE]"
CTEXT = tmpl("%s", ["[COMPLICATION.TEXT]"])
CTITLE = tmpl("%s", ["[COMPLICATION.TITLE]"])


def text_or_value(family, x, y, w, h, size, color, value):
    """Complication text, or the rounded value when the provider sends no text."""
    return cond([("t", "textLength([COMPLICATION.TEXT]) &gt; 0")], [("t", text(family, x, y, w, h, CTEXT, size, color))],
                text(family, x, y, w, h, tmpl("%d", [f"round({value})"]), size, color))


def round_box(W, H, r=None):
    return f'<BoundingRoundBox x="0" y="0" width="{W}" height="{H}" cornerRadius="{min(W, H) // 2 if r is None else r}"/>'


def slot_xml(sid, name, x, y, W, H, types, provider, ptype, parts, bound=None, angle=0):
    """ComplicationSlot, hidden in always-on. parts: {type: xml}; an empty string draws nothing.
    types: space-separated, in order of preference (the watch picks the first a provider offers)."""
    bound = bound or round_box(W, H)
    angle_attr = f' angle="{angle}"' if angle else ""
    out = (f'<ComplicationSlot slotId="{sid}" displayName="{name}" x="{x}" y="{y}" width="{W}" height="{H}"'
           f'{angle_attr} isCustomizable="TRUE" supportedTypes="{types}">\n'
           f'  <DefaultProviderPolicy defaultSystemProvider="{provider}" defaultSystemProviderType="{ptype}"/>\n'
           f'  {bound}\n'
           f'  <Variant mode="AMBIENT" target="alpha" value="0"/>\n')
    for t in types.split():
        b = parts[t]
        out += (f'  <Complication type="{t}">\n' + ind(b, 4) + '  </Complication>\n') if b else f'  <Complication type="{t}"/>\n'
    return out + '</ComplicationSlot>\n'


# ---- Settings and document ----------------------------------------------------------------


def color_config(themes, cfg="theme", name="cfg_theme"):
    """themes: [(id, string resource, [colours])]; option ids are the list indexes."""
    colors = "".join(f'<ColorOption id="{i}" displayName="{n}" colors="{" ".join(cs)}"/>\n'
                     for i, (_, n, cs) in enumerate(themes))
    return (f'<ColorConfiguration id="{cfg}" displayName="{name}" defaultValue="0">\n' + ind(colors, 2)
            + '</ColorConfiguration>\n')


def watchface(comment, preview_time, configs, scene, extra=""):
    """The whole document. configs: <UserConfigurations> xml; extra: e.g. <BitmapFonts>."""
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            f'<!-- {comment} Watch Face Format v2. '
            'GENERATED by design/gen_watchface.py, do not edit by hand. -->\n'
            f'<WatchFace width="{CANVAS}" height="{CANVAS}" clipShape="CIRCLE">\n'
            '  <Metadata key="CLOCK_TYPE" value="DIGITAL"/>\n'
            f'  <Metadata key="PREVIEW_TIME" value="{preview_time}"/>\n'
            + ind(configs, 2) + ind(extra, 2)
            + '  <Scene backgroundColor="#FF000000">\n' + ind(scene, 4) + '  </Scene>\n'
            '</WatchFace>\n')

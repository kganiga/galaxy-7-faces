# Overlap

Stacked two-tone digits: hours on top, minutes below, a checkerboard of two theme colours
with a carved shadow where the digits overlap. The date curves along the top, and there are
three complication slots.

<img src="docs/themes.png" width="640">

## Customize (long-press the face > Customize)

| Setting | Options | Default |
|---|---|---|
| Color theme | Oat, Sage, Coral, Glacier, Lilac, Mono | Oat |
| Show date | on / off | on |
| Left slot (vertical) | short text, ranged value, icon, small image | Watch battery |
| Right slot (vertical) | same | Step count |
| Bottom slot | short text, ranged value, long text, icon | Empty, which shows the built-in weather temperature |

Ranged-value complications get a thin progress bar. 12/24-hour follows the watch setting.

## Always-on mode (battery)

Always-on mode switches to outline-only digits (pre-rendered bitmaps, `amb_*.png`): a black fill
with a 3 px grey stroke. The black fill still hides the digit behind it, so the stacked look stays.
Complications are hidden, and the date dims to about 60%.

| Mock-up measurement | Lit pixels | Average brightness |
|---|---|---|
| Filled dim digits (v1.0) | 29.5% | 9.2% |
| Outline digits (v1.1) | about 7% | about 3% |

## Editing the design

Geometry, colours and themes live in `design/gen_watchface.py`. From `faces/overlap`:

```sh
python3 design/make_ambient_digits.py                            # only if size/stroke/tones changed (needs Pillow)
python3 design/gen_watchface.py > src/main/res/raw/watchface.xml
python3 design/render_preview.py src/main/res/font/fredoka_bold.ttf docs/preview.png 0 0 900
```

CI fails if `watchface.xml` doesn't match the generator output.

## Status

The XML passes the official WFF v2 schema check. The preview images are a Pillow mock-up, not
captures from a real watch, so the digits and the date may sit a few pixels differently on the watch.

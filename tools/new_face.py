#!/usr/bin/env python3
"""Scaffolds a new watch face module under faces/<name>.

usage: python3 tools/new_face.py <name> "<Title>" [package]
  e.g. python3 tools/new_face.py orbit "Orbit"
The new face builds and validates immediately (a plain digital clock); then replace
src/main/res/raw/watchface.xml and src/main/res/drawable-nodpi/preview.png with the design.
"""
import os, re, struct, sys, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def black_png(path, size):
    # minimal all-black RGB PNG, no third-party deps
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * size for _ in range(size))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    name, title = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        sys.exit("name must be lowercase letters, digits or _ (it becomes the module and file name)")
    pkg = sys.argv[3] if len(sys.argv) > 3 else f"com.kganiga.{name}.watchface"
    face = os.path.join(ROOT, "faces", name)
    if os.path.exists(face):
        sys.exit(f"{face} already exists")
    res = os.path.join(face, "src/main/res")

    write(os.path.join(face, "face.properties"),
          f"# Read by the root build.gradle.kts, tools/build_without_gradle.sh and CI.\n"
          f"package={pkg}\nversionName=1.0\ntitle={title}\n")
    write(os.path.join(face, "build.gradle.kts"),
          "// Package, SDK levels, signing and version come from face.properties\n"
          "// and the root build.gradle.kts.\nplugins {\n    id(\"com.android.application\")\n}\n")
    write(os.path.join(face, "src/main/AndroidManifest.xml"), """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-feature android:name="android.hardware.type.watch" />

    <application
        android:hasCode="false"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <meta-data
            android:name="com.google.android.wearable.standalone"
            android:value="true" />

        <property
            android:name="com.google.wear.watchface.format.version"
            android:value="2" />
        <property
            android:name="com.google.wear.watchface.format.publisher"
            android:value="kganiga" />
    </application>
</manifest>
""")
    write(os.path.join(res, "values/strings.xml"),
          f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="app_name">{title}</string>\n</resources>\n')
    write(os.path.join(res, "xml/watch_face_info.xml"), """<?xml version="1.0" encoding="utf-8"?>
<WatchFaceInfo>
    <Preview value="@drawable/preview" />
    <Category value="CATEGORY_EMPTY" />
    <AvailableInRetail value="true" />
    <MultipleInstancesAllowed value="true" />
    <Editable value="true" />
</WatchFaceInfo>
""")
    write(os.path.join(res, "raw/watchface.xml"), f"""<?xml version="1.0" encoding="utf-8"?>
<!-- {title}: starter face from tools/new_face.py -->
<WatchFace width="450" height="450" clipShape="CIRCLE">
  <Metadata key="CLOCK_TYPE" value="DIGITAL"/>
  <Metadata key="PREVIEW_TIME" value="10:08:32"/>
  <Scene backgroundColor="#FF000000">
    <DigitalClock x="0" y="0" width="450" height="450">
      <Variant mode="AMBIENT" target="alpha" value="160"/>
      <TimeText format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER" x="25" y="165" width="400" height="120">
        <Font family="SYNC_TO_DEVICE" size="96" color="#FFFFFFFF" weight="BOLD"/>
      </TimeText>
    </DigitalClock>
  </Scene>
</WatchFace>
""")
    os.makedirs(os.path.join(res, "drawable-nodpi"), exist_ok=True)
    os.makedirs(os.path.join(res, "mipmap-nodpi"), exist_ok=True)
    black_png(os.path.join(res, "drawable-nodpi/preview.png"), 450)
    black_png(os.path.join(res, "mipmap-nodpi/ic_launcher.png"), 192)
    print(f"created faces/{name} ({pkg}). Build: ./gradlew :faces:{name}:assembleRelease")


if __name__ == "__main__":
    main()

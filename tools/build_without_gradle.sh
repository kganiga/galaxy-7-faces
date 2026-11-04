#!/usr/bin/env bash
# Builds watch face APKs with plain aapt2 + zipalign + apksigner (no Gradle/AGP needed).
#   usage: tools/build_without_gradle.sh [face ...]     (default: every face) -> dist/<face>-<version>.apk
# Needs aapt2, zipalign, apksigner and an android.jar (any API level >= 23):
#   Ubuntu/Debian: sudo apt install aapt apksigner zipalign android-sdk-platform-23
#   Android SDK:   ANDROID_JAR=$ANDROID_HOME/platforms/android-35/android.jar
set -euo pipefail
cd "$(dirname "$0")/.."
ANDROID_JAR=${ANDROID_JAR:-/usr/lib/android-sdk/platforms/android-23/android.jar}
KS=${SIGNING_KEYSTORE_PATH:-signing/sideload.keystore}
VERSION_CODE=${GITHUB_RUN_NUMBER:-1}
mkdir -p dist

faces=("$@")
if [ ${#faces[@]} -eq 0 ]; then
  for d in faces/*/face.properties; do faces+=("$(basename "$(dirname "$d")")"); done
fi

prop() { grep -E "^$2=" "faces/$1/face.properties" | cut -d= -f2-; }

for face in "${faces[@]}"; do
  src="faces/$face/src/main"
  pkg=$(prop "$face" package); ver=$(prop "$face" versionName)
  tmp=$(mktemp -d)
  # AGP injects package/version from face.properties; for plain aapt2 we add them here.
  sed "s#<manifest #<manifest package=\"$pkg\" android:versionCode=\"$VERSION_CODE\" android:versionName=\"$ver\" #" \
      "$src/AndroidManifest.xml" > "$tmp/AndroidManifest.xml"
  aapt2 compile --dir "$src/res" -o "$tmp/res.zip"
  aapt2 link -o "$tmp/unaligned.apk" -I "$ANDROID_JAR" --manifest "$tmp/AndroidManifest.xml" \
      --min-sdk-version 34 --target-sdk-version 34 "$tmp/res.zip"
  zipalign -f -p 4 "$tmp/unaligned.apk" "$tmp/aligned.apk"
  out="dist/$face-$ver.apk"
  apksigner sign --ks "$KS" --ks-pass "pass:${SIGNING_STORE_PASSWORD:-android}" \
      --ks-key-alias "${SIGNING_KEY_ALIAS:-debug}" --key-pass "pass:${SIGNING_KEY_PASSWORD:-android}" \
      --min-sdk-version 34 --out "$out" "$tmp/aligned.apk"
  apksigner verify --min-sdk-version 34 "$out"
  rm -rf "$tmp" "$out.idsig"
  echo "built $out"
done

#!/usr/bin/env python3
"""Validates every face's res/raw/watchface.xml against the official Watch Face Format XSD.

The XSD (from github.com/google/watchface) is downloaded once into .xsd-cache/.
The WFF version is read from each face's AndroidManifest.xml.
usage: python3 tools/validate_wff.py [face ...]      (needs: pip install xmlschema)
"""
import os, posixpath, re, sys, urllib.request
import xmlschema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".xsd-cache")
BASE = "https://raw.githubusercontent.com/google/watchface/main/third_party/wff/specification/documents/{v}/"


def fetch_xsd(version):
    root = os.path.join(CACHE, str(version))
    queue, seen = ["watchface.xsd"], set()
    while queue:
        rel = posixpath.normpath(queue.pop())
        if rel in seen:
            continue
        seen.add(rel)
        local = os.path.join(root, rel)
        if not os.path.exists(local):
            os.makedirs(os.path.dirname(local), exist_ok=True)
            with urllib.request.urlopen(BASE.format(v=version) + rel) as r:
                data = r.read()
            with open(local, "wb") as f:
                f.write(data)
        text = open(local, encoding="utf-8").read()
        queue += [posixpath.join(posixpath.dirname(rel), loc)
                  for loc in re.findall(r'schemaLocation="([^"]+)"', text)]
    return os.path.join(root, "watchface.xsd")


def wff_version(face_dir):
    manifest = open(os.path.join(face_dir, "src/main/AndroidManifest.xml"), encoding="utf-8").read()
    m = re.search(r'com\.google\.wear\.watchface\.format\.version"\s+android:value="(\d+)"', manifest)
    if not m:
        sys.exit(f"{face_dir}: no com.google.wear.watchface.format.version property in manifest")
    return int(m.group(1))


def main():
    faces_dir = os.path.join(ROOT, "faces")
    faces = sys.argv[1:] or sorted(d for d in os.listdir(faces_dir)
                                   if os.path.exists(os.path.join(faces_dir, d, "face.properties")))
    schemas, failed = {}, 0
    for face in faces:
        face_dir = os.path.join(faces_dir, face)
        v = wff_version(face_dir)
        if v not in schemas:
            schemas[v] = xmlschema.XMLSchema11(fetch_xsd(v))
        xml = os.path.join(face_dir, "src/main/res/raw/watchface.xml")
        errors = list(schemas[v].iter_errors(xml))
        status = "OK" if not errors else f"{len(errors)} error(s)"
        print(f"{face}: WFF v{v}: {status}")
        for e in errors[:20]:
            print(f"  - {e.reason} @ {e.path}")
        failed += bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

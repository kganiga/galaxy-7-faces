#!/usr/bin/env python3
"""Lit-pixel ratio and average brightness of round preview PNGs: measure_pixels.py a.png [b.png ...]"""
import sys
from PIL import Image
for f in sys.argv[1:]:
    im=Image.open(f).convert("L"); px=list(im.get_flattened_data() if hasattr(im,"get_flattened_data") else im.getdata()); n=len(px)*0.785
    lit=sum(1 for v in px if v>16)/n; apl=sum(px)/255/n
    print(f"{f.split('/')[-1]}: lit {lit*100:.1f}%  avg-luminance {apl*100:.1f}%")

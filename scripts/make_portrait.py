#!/usr/bin/env python3
"""One-off: turn assets/portrait-source.png into assets/portrait.txt (ASCII art lines).

Needs Pillow (pip install pillow). The output is committed, so the daily workflow
does not need to run this.  Usage: python scripts/make_portrait.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "assets", "portrait-source.png")
OUT = os.path.join(ROOT, "assets", "portrait.txt")

COLS = 150
CELL_W, CELL_H = 2.27, 4.0          # glyph cell used by the card renderer (keeps the aspect right)
RAMP = " .'`^:;-~=+*xoO#%@"        # light -> dark (drawn as ink on paper)

im = Image.open(SRC).convert("RGB").crop((170, 100, 1060, 1130))
rows = round(COLS * (im.height / im.width) * (CELL_W / CELL_H))
im = im.resize((COLS, rows), Image.LANCZOS)

# cut out the cream background by flood-filling from the corners
m = im.copy()
for pt in [(0, 0), (COLS - 1, 0), (0, rows - 1), (COLS - 1, rows - 1)]:
    ImageDraw.floodfill(m, pt, (255, 0, 255), thresh=30)
mask = Image.new("L", im.size, 255)
mp, px = mask.load(), m.load()
for y in range(rows):
    for x in range(COLS):
        if px[x, y] == (255, 0, 255):
            mp[x, y] = 0

g = ImageOps.autocontrast(im.convert("L"), cutoff=1)
g = g.filter(ImageFilter.GaussianBlur(0.5))
gp, mp = g.load(), mask.load()

lines = []
for y in range(rows):
    row = []
    for x in range(COLS):
        if mp[x, y] < 128:
            row.append(" ")
            continue
        dark = 1 - gp[x, y] / 255                       # 0 light .. 1 dark
        dark = max(0.0, (dark - 0.30) / 0.70)           # skin tones -> blank, features/hair -> ink
        row.append(RAMP[min(len(RAMP) - 1, int(dark ** 0.8 * len(RAMP)))])
    lines.append("".join(row).rstrip())

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"wrote {OUT}: {COLS}x{rows}")

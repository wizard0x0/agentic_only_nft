#!/usr/bin/env python3
"""Generate Club of Agent logo — pixel art robot agent face."""

from PIL import Image
import os

# 32x32 grid, each cell = 12px → final 384x384 (also save 64x64 for favicon)
SCALE = 12
SIZE  = 32

# Palette
_ = (0, 0, 0, 0)          # transparent
B = (8,  10,  20,  255)   # near-black bg
D = (15, 20,  40,  255)   # dark panel
P = (124, 58, 237, 255)   # purple
L = (167, 139, 250, 255)  # light purple
C = (6,  182, 212, 255)   # cyan
E = (103, 232, 249, 255)  # light cyan
W = (226, 232, 240, 255)  # white
G = (71,  85,  105, 255)  # muted grey
S = (30,  41,  59,  255)  # dark slate
T = (51,  65,  85,  255)  # mid slate
H = (251, 191, 36,  255)  # gold highlight
R = (248, 113, 113, 255)  # red accent

# 32×32 pixel art — robot agent face with circuit crown
grid = [
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,P,P,_,_,P,P,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,P,H,P,P,H,P,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,P,P,P,P,P,P,P,P,P,P,P,P,P,P,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,P,L,P,L,P,L,P,L,P,L,P,L,P,L,P,L,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,P,P,P,P,P,P,P,P,P,P,P,P,P,P,P,P,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,T,T,T,T,T,T,T,T,T,T,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,T,T,T,T,T,T,T,T,T,T,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,C,C,C,T,T,T,T,T,T,C,C,C,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,C,E,C,T,T,T,T,T,T,C,E,C,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,C,C,C,T,T,T,T,T,T,C,C,C,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,T,T,T,T,T,T,T,T,T,T,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,T,T,T,T,T,T,T,T,T,T,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,G,G,G,G,G,G,G,G,G,G,G,G,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,G,P,G,G,G,G,G,G,G,G,P,G,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,G,G,G,G,G,G,G,G,G,G,G,G,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,T,T,T,T,T,T,T,T,T,T,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,C,T,T,T,C,C,T,T,T,C,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,C,C,T,T,C,C,T,T,C,C,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,T,T,T,T,T,T,T,T,T,T,T,T,T,T,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,S,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,D,S,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,S,S,S,S,S,S,S,S,S,S,S,S,S,S,S,S,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,P,P,P,P,P,P,P,P,P,P,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,P,C,C,C,C,C,C,C,C,C,C,P,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,P,P,P,P,P,P,P,P,P,P,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
for y, row in enumerate(grid):
    for x, color in enumerate(row):
        img.putpixel((x, y), color)

out_dir = "/Users/yunanli/Desktop/AW_NFT/website"

# Large logo — 384×384 (32×12)
logo = img.resize((SIZE * SCALE, SIZE * SCALE), Image.Resampling.NEAREST)
logo.save(f"{out_dir}/logo.png")
print(f"Saved logo.png ({SIZE*SCALE}x{SIZE*SCALE})")

# Favicon — 32×32 (kept at pixel scale)
fav = img.resize((32, 32), Image.Resampling.NEAREST)
fav.save(f"{out_dir}/favicon.png")
print("Saved favicon.png (32x32)")

# Also save a 64px version for apple-touch-icon
touch = img.resize((180, 180), Image.Resampling.NEAREST)
touch.save(f"{out_dir}/apple-touch-icon.png")
print("Saved apple-touch-icon.png (180x180)")

"""
AgenticNFT Art Style Generator — 10 examples across 4 styles with rarity tiers
Common / Rare (Gold) / Legendary (Diamond)
Each drawn at 24x24, scaled 12x → 288x288
"""
from PIL import Image, ImageDraw
import os

OUT = os.path.join(os.path.dirname(__file__), "styles")
SCALE = 12
SIZE = 24

def save(img, name):
    big = img.resize((SIZE * SCALE, SIZE * SCALE), Image.Resampling.NEAREST)
    big.save(os.path.join(OUT, name))
    print(f"  {name}")

def px(draw, x, y, c):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        draw.rectangle([x, y, x, y], fill=c)

def sparkle(d, positions, c=(255,255,255)):
    """Draw diamond sparkle at given (cx,cy) positions"""
    for cx, cy in positions:
        px(d, cx, cy, c)
        px(d, cx-1, cy, c)
        px(d, cx+1, cy, c)
        px(d, cx, cy-1, c)
        px(d, cx, cy+1, c)


# ══════════════════════════════════════════════════════════
# STYLE A — CIRCUIT PUNK
# ══════════════════════════════════════════════════════════

def _draw_circuit_punk(img, skin, eye, hair, accent, jacket, circuit):
    d = ImageDraw.Draw(img)
    dark  = tuple(max(0, c - 80) for c in skin)
    mouth = (180, 50, 50)

    # Antenna
    for y in range(1, 4): px(d, 12, y, accent)
    px(d, 11, 4, accent); px(d, 13, 4, accent)

    # Mohawk
    for x in range(9, 16):  px(d, x, 4, hair)
    for x in range(10, 15): px(d, x, 5, hair)
    for x in range(11, 14): px(d, x, 6, hair)

    # Head
    for y in range(6, 16):
        for x in range(8, 17): px(d, x, y, skin)
    for y in range(7, 15):
        px(d, 8, y, dark); px(d, 16, y, dark)

    # Circuit lines
    for x in range(9, 16, 3): px(d, x, 9, circuit)
    for y in range(11, 14, 2): px(d, 14, y, circuit)

    # Eyes
    px(d, 10, 9, eye); px(d, 11, 9, eye)
    px(d, 13, 9, eye); px(d, 14, 9, eye)

    # Nose
    px(d, 12, 11, dark)

    # Mouth
    for x in range(10, 15): px(d, x, 13, mouth)
    px(d, 10, 13, dark); px(d, 14, 13, dark)

    # Neck
    for y in range(15, 18):
        for x in range(11, 14): px(d, x, y, skin)

    # Jacket
    for y in range(17, 24):
        for x in range(7, 18): px(d, x, y, jacket)
    for y in range(17, 20):
        px(d, 10, y, accent); px(d, 14, y, accent)
    for x in range(8, 17, 2): px(d, x, 20, circuit)
    for y in range(18, 23, 2): px(d, 17, y, circuit)

    return d

def style_a_common():
    img = Image.new("RGB", (SIZE, SIZE), (15, 10, 30))
    _draw_circuit_punk(img,
        skin=(0,230,180), eye=(255,255,80), hair=(80,0,160),
        accent=(0,255,200), jacket=(30,0,80), circuit=(0,200,160))
    save(img, "01_circuit_punk_common.png")

def style_a_gold():
    img = Image.new("RGB", (SIZE, SIZE), (20, 14, 0))
    d = _draw_circuit_punk(img,
        skin=(210,160,0), eye=(255,240,50), hair=(180,80,0),
        accent=(255,200,0), jacket=(80,40,0), circuit=(255,180,0))
    # Gold crown
    for x in range(9,16): px(d, x, 3, (255,200,0))
    px(d, 9,2,(255,220,50)); px(d, 12,1,(255,240,80)); px(d, 15,2,(255,220,50))
    # Gem on crown
    px(d, 12, 2, (255,80,80))
    save(img, "02_circuit_punk_gold.png")

def style_a_diamond():
    img = Image.new("RGB", (SIZE, SIZE), (5, 10, 25))
    d = _draw_circuit_punk(img,
        skin=(180,220,255), eye=(255,255,255), hair=(100,180,255),
        accent=(200,240,255), jacket=(20,50,120), circuit=(150,220,255))
    # Diamond sparkles
    sparkle(d, [(6,6),(18,8),(5,14),(19,12)], (220,245,255))
    # Crystal forehead gem
    px(d, 12, 7, (255,255,255))
    px(d, 11, 7, (180,230,255)); px(d, 13, 7, (180,230,255))
    save(img, "03_circuit_punk_diamond.png")


# ══════════════════════════════════════════════════════════
# STYLE B — STEEL AGENT
# ══════════════════════════════════════════════════════════

def _draw_steel_agent(img, metal, light, dark, visor, glow, chest_light):
    d = ImageDraw.Draw(img)
    black = (5, 5, 8)

    # Head box
    for y in range(4, 18):
        for x in range(7, 18): px(d, x, y, metal)
    for x in range(7, 18): px(d, x, 4, light); px(d, x, 17, dark)
    for y in range(4, 18): px(d, 7, y, light);  px(d, 17, y, dark)

    # Visor
    for x in range(8, 17):
        px(d, x, 9, black); px(d, x, 10, black)
    for x in range(9, 16): px(d, x, 9, visor)
    px(d, 12, 9, glow)

    # Mouth grille
    for x in range(9, 16, 2): px(d, x, 14, black)
    for x in range(9, 16): px(d, x, 15, dark)

    # Panel lines
    px(d, 12, 6, dark); px(d, 12, 7, dark)
    px(d, 8, 12, dark); px(d, 16, 12, dark)

    # Antenna bolts
    px(d, 9, 3, metal); px(d, 12, 2, light); px(d, 15, 3, metal)

    # Neck
    for y in range(18, 21):
        for x in range(10, 15): px(d, x, y, dark)
    for y in range(18, 21):
        px(d, 10, y, metal); px(d, 14, y, metal)

    # Chest
    for y in range(20, 24):
        for x in range(6, 19): px(d, x, y, dark)
    for x in range(7, 18): px(d, x, 20, metal)
    px(d, 12, 22, chest_light)
    px(d, 11, 22, glow); px(d, 13, 22, glow)

    return d

def style_b_common():
    img = Image.new("RGB", (SIZE, SIZE), (8, 8, 12))
    _draw_steel_agent(img,
        metal=(100,110,130), light=(170,180,200), dark=(50,55,70),
        visor=(255,40,40), glow=(255,160,0), chest_light=(255,40,40))
    save(img, "04_steel_agent_common.png")

def style_b_gold():
    img = Image.new("RGB", (SIZE, SIZE), (15, 10, 0))
    d = _draw_steel_agent(img,
        metal=(180,140,0), light=(255,210,50), dark=(100,70,0),
        visor=(255,220,0), glow=(255,255,100), chest_light=(255,200,0))
    # Gold laurel / crown on top
    for x in range(8, 17): px(d, x, 3, (200,150,0))
    for x in range(9, 16): px(d, x, 2, (255,200,0))
    px(d, 12, 1, (255,230,80))
    # Gold shoulder pads
    for x in range(4, 8):  px(d, x, 21, (180,140,0))
    for x in range(17, 21): px(d, x, 21, (180,140,0))
    save(img, "05_steel_agent_gold.png")

def style_b_diamond():
    img = Image.new("RGB", (SIZE, SIZE), (5, 8, 20))
    d = _draw_steel_agent(img,
        metal=(160,200,240), light=(220,240,255), dark=(80,120,180),
        visor=(100,220,255), glow=(255,255,255), chest_light=(180,240,255))
    # Diamond facets on head
    for x in range(8, 17, 2): px(d, x, 5, (255,255,255))
    for x in range(8, 17, 2): px(d, x, 16, (200,230,255))
    # Sparkles
    sparkle(d, [(4,6),(20,7),(4,16),(20,15),(12,1)], (220,245,255))
    save(img, "06_steel_agent_diamond.png")


# ══════════════════════════════════════════════════════════
# STYLE C — NEON GHOST
# ══════════════════════════════════════════════════════════

def _draw_neon_ghost(img, body, outline1, outline2, eye, data, symbol):
    d = ImageDraw.Draw(img)
    white = (230, 220, 255)
    glow  = tuple(max(0,c-60) for c in outline1)

    # Head
    for y in range(5, 17):
        for x in range(8, 17): px(d, x, y, body)

    # Neon outline
    for x in range(8, 17):
        px(d, x, 5, outline1); px(d, x, 16, outline2)
    for y in range(5, 17):
        px(d, 8, y, outline1); px(d, 16, y, outline2)
    for c in [(8,5),(16,5),(8,16),(16,16)]: px(d, c[0], c[1], white)

    # Eyes
    for x in range(9, 12): px(d, x, 9, eye)
    for x in range(13, 16): px(d, x, 9, eye)
    for x in range(9, 12): px(d, x, 10, data)
    for x in range(13, 16): px(d, x, 10, data)

    px(d, 12, 11, glow)

    # Mouth
    for x in range(10, 15): px(d, x, 13, outline2)
    px(d, 10, 13, white); px(d, 14, 13, white)

    # Data streams
    for y in range(6, 16, 3): px(d, 6, y, data)
    for y in range(7, 16, 3): px(d, 5, y, glow)
    for y in range(6, 16, 3): px(d, 18, y, data)

    # Hood
    for x in range(7, 18): px(d, x, 4, outline1)
    for x in range(6, 19): px(d, x, 3, glow)
    for x in range(8, 17): px(d, x, 3, body)
    px(d, 12, 2, outline1)

    # Body
    for y in range(17, 24):
        for x in range(9, 16): px(d, x, y, body)
    for y in range(17, 24):
        px(d, 9, y, outline1); px(d, 15, y, outline2)

    # Chest symbol
    px(d, 12, 20, symbol)
    px(d, 11, 21, symbol); px(d, 13, 21, symbol)
    px(d, 10, 22, symbol); px(d, 14, 22, symbol)

    return d

def style_c_common():
    img = Image.new("RGB", (SIZE, SIZE), (5, 0, 15))
    _draw_neon_ghost(img,
        body=(20,5,40), outline1=(200,0,255), outline2=(255,0,180),
        eye=(0,240,255), data=(0,180,200), symbol=(0,240,255))
    save(img, "07_neon_ghost_common.png")

def style_c_gold():
    img = Image.new("RGB", (SIZE, SIZE), (15, 8, 0))
    d = _draw_neon_ghost(img,
        body=(40,20,0), outline1=(255,180,0), outline2=(255,120,0),
        eye=(255,240,80), data=(220,160,0), symbol=(255,200,0))
    # Halo
    for x in range(9, 16): px(d, x, 1, (255,200,0))
    px(d, 8, 2, (255,180,0)); px(d, 16, 2, (255,180,0))
    save(img, "08_neon_ghost_gold.png")


# ══════════════════════════════════════════════════════════
# STYLE D — RETRO TERMINAL
# ══════════════════════════════════════════════════════════

def _draw_retro_terminal(img, green, dgreen, bright, cursor, bg):
    d = ImageDraw.Draw(img)
    black = bg

    # Monitor
    for y in range(4, 18):
        for x in range(7, 18): px(d, x, y, dgreen)
    for x in range(7, 18):
        px(d, x, 4, green); px(d, x, 17, green)
    for y in range(4, 18):
        px(d, 7, y, green); px(d, 17, y, green)

    # Screen
    for y in range(6, 16):
        for x in range(9, 16): px(d, x, y, black)

    # Face
    for x in range(10, 12): px(d, x, 8, green)
    for x in range(13, 15): px(d, x, 8, green)
    px(d, 11, 8, bright); px(d, 14, 8, bright)
    px(d, 12, 10, dgreen)
    for x in range(10, 15): px(d, x, 12, green)
    px(d, 14, 12, cursor)

    # Scanlines
    for x in range(9, 16):
        for sy in [7,9,11,13,15]: px(d, x, sy, dgreen)

    # Stand
    for y in range(18, 21):
        for x in range(11, 14): px(d, x, y, green)
    for x in range(9, 16): px(d, x, 20, green)
    for x in range(9, 16): px(d, x, 21, dgreen)

    # Floating bits
    for bx,by,bc in [(3,8,dgreen),(3,10,green),(3,12,dgreen),(4,9,green),
                     (20,7,dgreen),(20,9,green),(20,11,dgreen),(19,8,green)]:
        px(d, bx, by, bc)

    return d

def style_d_common():
    img = Image.new("RGB", (SIZE, SIZE), (0, 8, 0))
    _draw_retro_terminal(img,
        green=(0,220,50), dgreen=(0,120,20), bright=(100,255,120),
        cursor=(255,180,0), bg=(0,8,0))
    save(img, "09_retro_terminal_common.png")

def style_d_diamond():
    img = Image.new("RGB", (SIZE, SIZE), (2, 5, 20))
    d = _draw_retro_terminal(img,
        green=(100,200,255), dgreen=(40,100,200), bright=(255,255,255),
        cursor=(180,240,255), bg=(2,5,20))
    # Diamond facets on monitor corners
    sparkle(d, [(7,4),(17,4),(7,17),(17,17)], (255,255,255))
    # Prismatic lines
    for x in range(9,16): px(d, x, 5, (220,240,255))
    # Ice crystals
    for cx,cy in [(3,5),(21,5),(3,18),(21,18)]:
        px(d, cx, cy, (200,230,255))
        px(d, cx, cy-1, (255,255,255))
    save(img, "10_retro_terminal_diamond.png")


if __name__ == "__main__":
    print("Generating 10 style samples...\n")
    print("─── Circuit Punk ───")
    style_a_common()
    style_a_gold()
    style_a_diamond()
    print("─── Steel Agent ────")
    style_b_common()
    style_b_gold()
    style_b_diamond()
    print("─── Neon Ghost ─────")
    style_c_common()
    style_c_gold()
    print("─── Retro Terminal ─")
    style_d_common()
    style_d_diamond()
    print("\nDone! Check nft-art/styles/")
    print("\nRarity guide:")
    print("  Common    → 01, 04, 07, 09")
    print("  Gold Rare → 02, 05, 08")
    print("  Diamond   → 03, 06, 10")

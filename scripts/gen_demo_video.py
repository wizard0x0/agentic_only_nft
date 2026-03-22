#!/usr/bin/env python3
"""Generate a 10-second demo video for Club of Agent NFT project."""

import os
import math
from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
W, H    = 1280, 720
FPS     = 30
FRAMES  = FPS * 10  # 10 seconds
OUT_DIR = "/Users/yunanli/Desktop/AW_NFT/video_frames"
os.makedirs(OUT_DIR, exist_ok=True)

NFT_PATHS = [
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/03_circuit_punk_diamond.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/06_steel_agent_diamond.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/08_neon_ghost_gold.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/10_retro_terminal_diamond.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/02_circuit_punk_gold.png",
]

# ── Colours ───────────────────────────────────────────────────────────────────
BG       = (8, 10, 20)
PURPLE   = (124, 58, 237)
CYAN     = (6, 182, 212)
GOLD     = (251, 191, 36)
WHITE    = (226, 232, 240)
MUTED    = (71, 85, 105)
DIAMOND  = (147, 197, 253)

def lerp(a, b, t): return a + (b - a) * t
def ease(t): return t * t * (3 - 2 * t)  # smoothstep
def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))

def blend_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def alpha_composite_manual(base, overlay, ox, oy, alpha=1.0):
    """Paste overlay onto base at (ox,oy) with alpha."""
    ow, oh = overlay.size
    # Crop to canvas bounds
    x0 = max(0, ox); y0 = max(0, oy)
    x1 = min(W, ox + ow); y1 = min(H, oy + oh)
    if x1 <= x0 or y1 <= y0: return
    src_x = x0 - ox; src_y = y0 - oy
    src_w = x1 - x0; src_h = y1 - y0
    crop = overlay.crop((src_x, src_y, src_x + src_w, src_y + src_h))
    if alpha < 1.0:
        r, g, b, a = crop.split()
        a = a.point(lambda p: int(p * alpha))
        crop = Image.merge("RGBA", (r, g, b, a))
    base.paste(crop, (x0, y0), crop)

def make_nft_card(nft_img, label, rarity, rarity_color, size=220):
    """Create a styled NFT card as RGBA image."""
    card_w, card_h = size, size + 60
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    # Card background
    d.rounded_rectangle([0, 0, card_w-1, card_h-1], radius=14,
                         fill=(15, 20, 40, 220), outline=(*rarity_color, 180), width=2)
    # NFT image
    nft_resized = nft_img.resize((size-20, size-20), Image.Resampling.NEAREST).convert("RGBA")
    card.paste(nft_resized, (10, 10), nft_resized)
    # Label
    try:
        fnt = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", 13)
        fnt_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", 11)
    except:
        fnt = ImageFont.load_default()
        fnt_sm = fnt
    d.text((10, size + 8), label, font=fnt, fill=WHITE)
    d.text((10, size + 26), rarity, font=fnt_sm, fill=rarity_color)
    return card

def draw_grid_bg(draw, t, alpha=0.15):
    """Animated perspective grid."""
    speed = t * 0.3
    color = tuple(int(c * alpha) for c in PURPLE) + (255,)
    step = 80
    # Horizontal lines
    for i in range(0, H + step, step):
        y = (i + int(speed * step * 60)) % (H + step)
        a = int(40 * alpha * (1 - y / H))
        draw.line([(0, y), (W, y)], fill=(*PURPLE[:3], a), width=1)
    # Vertical lines converging to center
    cx = W // 2
    for i in range(-8, 9):
        x_top = cx + i * (W // 16)
        x_bot = cx + i * (W // 3)
        a = int(30 * alpha)
        draw.line([(x_top, 0), (x_bot, H)], fill=(*PURPLE[:3], a), width=1)

def draw_particles(draw, t, n=40):
    """Floating particles."""
    for i in range(n):
        phase = (i / n + t * 0.08) % 1.0
        x = (i * 137 + int(t * 30 * (i % 3 + 1))) % W
        y = int(H * phase)
        size = 1 + (i % 3)
        brightness = 0.3 + 0.7 * math.sin(t * 2 + i)
        if i % 4 == 0:
            c = tuple(int(c * brightness) for c in CYAN)
        else:
            c = tuple(int(c * brightness) for c in PURPLE)
        draw.ellipse([x, y, x+size, y+size], fill=c)

def glow_text(img, draw, text, pos, font, color, radius=8):
    """Draw text with a soft glow."""
    gx, gy = pos
    for r in range(radius, 0, -2):
        a = int(80 * (1 - r / radius))
        gc = (*color, a)
        tmp = Image.new("RGBA", (W, H), (0,0,0,0))
        td = ImageDraw.Draw(tmp)
        td.text((gx, gy), text, font=font, fill=gc, anchor="mm")
        img.alpha_composite(tmp)
    draw.text(pos, text, font=font, fill=(*color, 255), anchor="mm")

# ── Load fonts ────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    paths = [
        f"/System/Library/Fonts/Supplemental/{'Arial Bold' if bold else 'Arial'}.ttf",
        f"/System/Library/Fonts/{'Helvetica' if not bold else 'Helvetica'}.ttc",
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ]
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except: continue
    return ImageFont.load_default()

font_xl   = load_font(72, bold=True)
font_lg   = load_font(48, bold=True)
font_md   = load_font(32, bold=True)
font_sm   = load_font(22)
font_xs   = load_font(16)
font_mono = load_font(18, bold=False)

# ── Load NFT images ───────────────────────────────────────────────────────────
nfts_raw = [Image.open(p).convert("RGBA") for p in NFT_PATHS]
nft_labels = ["Circuit Punk", "Steel Agent", "Neon Ghost", "Retro Terminal", "Circuit Punk"]
nft_rarities = ["Diamond ◆", "Diamond ◆", "Gold ★", "Diamond ◆", "Gold ★"]
nft_colors = [DIAMOND, DIAMOND, GOLD, DIAMOND, GOLD]

# ── Render frames ─────────────────────────────────────────────────────────────
# Timeline (seconds):
# 0.0-1.5  : Intro — dark BG, "Club of Agent" fades in + tagline
# 1.5-3.5  : NFT cards fly in from sides
# 3.5-5.5  : Code snippet reveal "code.length > 0"
# 5.5-7.5  : Stats bar (10,000 supply, 0.08 OKB, X Layer)
# 7.5-9.0  : All cards + title together
# 9.0-10.0 : CTA fade — "clubofagent.com"

print(f"Rendering {FRAMES} frames at {FPS}fps...")

for frame_i in range(FRAMES):
    t = frame_i / FPS  # time in seconds
    norm = frame_i / FRAMES

    canvas = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(canvas)

    # ── Background grid ─────────────────────────────────────────────────────
    draw_grid_bg(draw, t, alpha=0.12)
    draw_particles(draw, t, n=50)

    # ── Gradient overlay ────────────────────────────────────────────────────
    for y in range(0, H, 2):
        a = int(30 * (1 - y / H))
        draw.line([(0, y), (W, y)], fill=(*PURPLE, a))

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 1: Title intro (0 – 1.5s)
    # ══════════════════════════════════════════════════════════════════════════
    title_alpha = clamp(t / 0.8)  # fades in over 0.8s

    # Decorative top bar
    bar_w = int(W * 0.6 * clamp(t / 0.5))
    draw.rectangle([W//2 - bar_w//2, 38, W//2 + bar_w//2, 40], fill=(*PURPLE, 200))

    # "Club of Agent" — always visible after fade
    if title_alpha > 0:
        # Shadow
        draw.text((W//2 + 2, H//2 - 180 + 2), "Club of Agent", font=font_xl,
                   fill=(*PURPLE, int(100 * title_alpha)), anchor="mm")
        glow_text(canvas, draw, "Club of Agent", (W//2, H//2 - 180),
                  font_xl, WHITE, radius=6)

    # Tagline
    tag_alpha = clamp((t - 0.5) / 0.6)
    if tag_alpha > 0:
        draw.text((W//2, H//2 - 110), "The World's First Agentic NFT",
                   font=font_sm, fill=(*CYAN, int(255 * tag_alpha)), anchor="mm")

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 2: NFT cards fly in (1.5 – 3.5s)
    # ══════════════════════════════════════════════════════════════════════════
    phase2_t = clamp((t - 1.2) / 1.5)

    card_size = 180
    card_y_center = H // 2 + 30
    num_cards = 5
    total_w = num_cards * (card_size + 20) - 20
    start_x = (W - total_w) // 2

    for i, (nft, label, rarity, rcol) in enumerate(zip(nfts_raw, nft_labels, nft_rarities, nft_colors)):
        # Staggered entrance
        card_t = clamp((phase2_t - i * 0.12) / 0.5)
        card_t = ease(card_t)

        cx = start_x + i * (card_size + 20)
        # Fly in from below
        cy = int(lerp(H + 50, card_y_center - card_size // 2, card_t))

        # Float animation
        float_y = int(8 * math.sin(t * 1.8 + i * 1.2))
        cy += float_y

        card = make_nft_card(nft, label, rarity, rcol, size=card_size)
        alpha_composite_manual(canvas, card, cx, cy, alpha=card_t)

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 3: Code snippet (3.5 – 5.5s)
    # ══════════════════════════════════════════════════════════════════════════
    code_alpha = clamp((t - 3.3) / 0.5) * (1 - clamp((t - 5.2) / 0.4))

    if code_alpha > 0:
        # Code box
        box_w, box_h = 680, 110
        bx = (W - box_w) // 2
        by = H - 175

        box = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, box_w-1, box_h-1], radius=12,
                               fill=(10, 15, 35, int(230 * code_alpha)),
                               outline=(*PURPLE, int(180 * code_alpha)), width=2)
        # Title bar
        bd.rounded_rectangle([0, 0, box_w-1, 28], radius=12,
                               fill=(*PURPLE, int(60 * code_alpha)))
        bd.text((14, 14), "IAgenticNFT.sol", font=font_xs,
                 fill=(*MUTED, int(255 * code_alpha)), anchor="lm")
        # Code line
        try:
            code_fnt = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", 18)
            code_fnt2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", 16)
        except:
            code_fnt = font_mono
            code_fnt2 = font_mono

        bd.text((20, 50), "function canMint(address minter) → bool {",
                 font=code_fnt2, fill=(*MUTED, int(220 * code_alpha)))
        # Highlight the key part
        bd.text((20, 75), "    return minter.", font=code_fnt, fill=(*WHITE, int(255*code_alpha)))
        # Measure offset
        offset = bd.textlength("    return minter.", font=code_fnt)
        bd.text((20 + int(offset), 75), "code.length > 0", font=code_fnt,
                 fill=(*CYAN, int(255 * code_alpha)))
        bd.text((20 + int(offset) + int(bd.textlength("code.length > 0", font=code_fnt)), 75),
                 ";", font=code_fnt, fill=(*WHITE, int(255 * code_alpha)))

        canvas.alpha_composite(box, (bx, by))

        # Label above
        draw.text((W//2, by - 18), "The one rule that makes this standard unique",
                   font=font_xs, fill=(*MUTED, int(255 * code_alpha)), anchor="mm")

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 4: Stats (5.5 – 7.5s)
    # ══════════════════════════════════════════════════════════════════════════
    stats_alpha = clamp((t - 5.3) / 0.5) * (1 - clamp((t - 7.3) / 0.4))

    if stats_alpha > 0:
        stats = [
            ("10,000", "Max Supply"),
            ("0.08 OKB", "Mint Price"),
            ("X Layer", "Network"),
            ("ERC-721", "Standard"),
        ]
        stat_w = 240
        total_sw = len(stats) * stat_w + (len(stats)-1) * 20
        sx0 = (W - total_sw) // 2
        sy = H - 160

        for i, (val, label) in enumerate(stats):
            sx = sx0 + i * (stat_w + 20)
            sb = Image.new("RGBA", (stat_w, 90), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sb)
            stagger = clamp((stats_alpha * 2 - i * 0.15))
            sd.rounded_rectangle([0, 0, stat_w-1, 89], radius=10,
                                   fill=(15, 20, 40, int(200 * stagger)),
                                   outline=(*CYAN, int(120 * stagger)), width=1)
            val_fnt = load_font(26, bold=True)
            lbl_fnt = load_font(13)
            sd.text((stat_w//2, 32), val, font=val_fnt,
                     fill=(*CYAN, int(255 * stagger)), anchor="mm")
            sd.text((stat_w//2, 62), label, font=lbl_fnt,
                     fill=(*MUTED, int(255 * stagger)), anchor="mm")
            canvas.alpha_composite(sb, (sx, sy))

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 5: Final — everything together (7.5 – 9.0s)
    # ══════════════════════════════════════════════════════════════════════════
    # (cards are still shown from phase2, title always visible)

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 6: CTA (9.0 – 10.0s)
    # ══════════════════════════════════════════════════════════════════════════
    cta_alpha = clamp((t - 8.8) / 0.5)

    if cta_alpha > 0:
        # Overlay darken
        dark = Image.new("RGBA", (W, H), (0, 0, 0, int(160 * cta_alpha)))
        canvas.alpha_composite(dark)

        pulse = 0.85 + 0.15 * math.sin(t * 6)
        cta_fnt = load_font(56, bold=True)
        url_fnt = load_font(30)
        sub_fnt = load_font(20)

        draw2 = ImageDraw.Draw(canvas)
        glow_text(canvas, draw2, "Club of Agent", (W//2, H//2 - 60),
                   cta_fnt, WHITE, radius=10)
        draw2.text((W//2, H//2), "clubofagent.com",
                    font=url_fnt, fill=(*CYAN, int(255 * cta_alpha * pulse)), anchor="mm")
        draw2.text((W//2, H//2 + 50), "Mint your Agentic NFT — Only Smart Contract Wallets",
                    font=sub_fnt, fill=(*MUTED, int(200 * cta_alpha)), anchor="mm")

        # Bottom bar
        bar_a = int(180 * cta_alpha)
        draw2.rectangle([0, H-3, W, H], fill=(*PURPLE, bar_a))

    # ── Save frame ───────────────────────────────────────────────────────────
    rgb = canvas.convert("RGB")
    rgb.save(f"{OUT_DIR}/frame_{frame_i:04d}.png")

    if frame_i % 30 == 0:
        print(f"  {frame_i}/{FRAMES} ({frame_i*100//FRAMES}%)")

print("Frames done. Encoding video...")

import subprocess
out_path = "/Users/yunanli/Desktop/AW_NFT/club_of_agent_demo.mp4"
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", f"{OUT_DIR}/frame_%04d.png",
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    out_path
], check=True)

print(f"\n✅ Video saved: {out_path}")

# Cleanup frames
import shutil
shutil.rmtree(OUT_DIR)
print("Frames cleaned up.")

#!/usr/bin/env python3
"""20-second Club of Agent explainer video."""

import os, math, textwrap, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

W, H   = 1280, 720
FPS    = 30
TOTAL  = 20
FRAMES = FPS * TOTAL
OUT    = "/Users/yunanli/Desktop/AW_NFT/explainer_frames"
os.makedirs(OUT, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG     = (5, 5, 12)
PURPLE = (124, 58, 237)
LPURP  = (167, 139, 250)
CYAN   = (6, 182, 212)
LCYAN  = (103, 232, 249)
GOLD   = (251, 191, 36)
WHITE  = (226, 232, 240)
MUTED  = (71, 85, 105)
DARK   = (15, 20, 40)
SLATE  = (30, 41, 59)
RED    = (239, 68, 68)
GREEN  = (16, 185, 129)

# ── Font loader ───────────────────────────────────────────────────────────────
def fnt(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ]
    for p in candidates:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

def mono(size):
    for p in ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
              "/System/Library/Fonts/Supplemental/Courier New.ttf"]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

F_HERO  = fnt(82, True)
F_TITLE = fnt(58, True)
F_SUB   = fnt(38, True)
F_BODY  = fnt(28)
F_SMALL = fnt(20)
F_MONO  = mono(22)
F_MONO_LG = mono(28)

# ── Easing ────────────────────────────────────────────────────────────────────
def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))
def ease(t): t=clamp(t); return t*t*(3-2*t)
def ease_out(t): t=clamp(t); return 1-(1-t)**3
def ease_in(t): t=clamp(t); return t**3
def lerp(a,b,t): return a+(b-a)*t
def fade_in(t, start, dur): return ease(clamp((t-start)/dur))
def fade_out(t, start, dur): return ease(clamp(1-(t-start)/dur))
def fade(t, s, dur, hold): return min(fade_in(t,s,dur*0.3), fade_out(t, s+dur*0.7+hold, dur*0.3))

# ── Assets ────────────────────────────────────────────────────────────────────
LOGO_PATH = "/Users/yunanli/Desktop/AW_NFT/website/logo.png"
logo_raw  = Image.open(LOGO_PATH).convert("RGBA")

NFT_FILES = [
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/03_circuit_punk_diamond.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/06_steel_agent_diamond.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/08_neon_ghost_gold.png",
    "/Users/yunanli/Desktop/AW_NFT/nft-art/styles/10_retro_terminal_diamond.png",
]
nfts = [Image.open(p).convert("RGBA") for p in NFT_FILES]

# ── Drawing helpers ───────────────────────────────────────────────────────────
def paste(canvas, img, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        nw, nh = int(img.width*scale), int(img.height*scale)
        if nw < 1 or nh < 1: return
        img = img.resize((nw, nh), Image.Resampling.NEAREST)
    if alpha < 1.0:
        r,g,b,a = img.split()
        a = a.point(lambda p: int(p*alpha))
        img = Image.merge("RGBA",(r,g,b,a))
    x, y = cx - img.width//2, cy - img.height//2
    x0=max(0,x); y0=max(0,y)
    x1=min(W,x+img.width); y1=min(H,y+img.height)
    if x1<=x0 or y1<=y0: return
    crop = img.crop((x0-x, y0-y, x1-x, y1-y))
    canvas.alpha_composite(crop, (x0, y0))

def text_centered(draw, canvas, txt, y, font, color, alpha=1.0, shadow=True):
    if alpha <= 0: return
    c = (*color, int(255*alpha))
    if shadow:
        sc = (0,0,0,int(120*alpha))
        draw.text((W//2+2, y+2), txt, font=font, fill=sc, anchor="mt")
    draw.text((W//2, y), txt, font=font, fill=c, anchor="mt")

def glow_text(canvas, draw, txt, pos, font, color, alpha=1.0, radius=12):
    if alpha <= 0: return
    gx, gy = pos
    tmp = Image.new("RGBA",(W,H),(0,0,0,0))
    td = ImageDraw.Draw(tmp)
    for r in range(radius,0,-3):
        a = int(60*(1-r/radius)*alpha)
        td.text((gx,gy), txt, font=font, fill=(*color,a), anchor="mm")
    canvas.alpha_composite(tmp)
    draw.text((gx,gy), txt, font=font, fill=(*color,int(255*alpha)), anchor="mm")

def wrap_text(draw, canvas, text, cx, y, font, color, alpha, max_width, line_h=40):
    if alpha <= 0: return
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur+" "+w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    for i, line in enumerate(lines):
        draw.text((cx, y + i*line_h), line, font=font,
                   fill=(*color, int(255*alpha)), anchor="mt")
    return len(lines) * line_h

# ── Background ────────────────────────────────────────────────────────────────
def draw_bg(canvas, draw, t):
    # Base gradient
    for y in range(0, H, 3):
        ratio = y/H
        r = int(lerp(BG[0], DARK[0], ratio))
        g = int(lerp(BG[1], DARK[1], ratio))
        b = int(lerp(BG[2], DARK[2], ratio))
        draw.line([(0,y),(W,y)], fill=(r,g,b,255))

    # Grid lines
    grid_alpha = 0.08
    for y in range(0, H, 60):
        ya = int(30*grid_alpha)
        draw.line([(0,y),(W,y)], fill=(*PURPLE,ya))
    for x in range(0, W, 80):
        draw.line([(x,0),(x,H)], fill=(*PURPLE, int(20*grid_alpha)))

    # Floating particles
    for i in range(60):
        phase = (i*0.618 + t*0.04*(1+i%3*0.3)) % 1.0
        x = int((i*137.5) % W)
        y = int(H * phase)
        sz = 1 + i%2
        b = 0.2 + 0.5*math.sin(t*1.5 + i*0.8)
        col = CYAN if i%3==0 else PURPLE
        draw.ellipse([x,y,x+sz,y+sz], fill=(*col, int(80*b)))

def draw_scanlines(draw, alpha=0.04):
    for y in range(0, H, 4):
        draw.line([(0,y),(W,y)], fill=(0,0,0,int(255*alpha)))

# ── Scene renderer ────────────────────────────────────────────────────────────
# Timeline:
# 0.0–2.5   Scene 1: "The AI Agent Economy is Here"
# 2.5–5.5   Scene 2: Problem — agents have no on-chain identity
# 5.5–9.0   Scene 3: Club of Agent logo reveal — "The First Agentic NFT"
# 9.0–12.5  Scene 4: How it works — code.length > 0, NFT cards
# 12.5–15.5 Scene 5: Why it matters — payments, identity, trust
# 15.5–18.0 Scene 6: 10,000 founding members, stats
# 18.0–20.0 Scene 7: CTA — clubofagent.com

def scene_progress(t, start, end):
    """Normalised [0,1] progress within a scene, clamped."""
    return clamp((t-start)/(end-start))

print(f"Rendering {FRAMES} frames...")

for fi in range(FRAMES):
    t = fi / FPS

    canvas = Image.new("RGBA",(W,H),(*BG,255))
    draw   = ImageDraw.Draw(canvas)
    draw_bg(canvas, draw, t)

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 1 (0–2.5s) — Opening hook
    # ══════════════════════════════════════════════════════════════════════════
    if t < 2.5:
        sp = scene_progress(t, 0, 2.5)

        # Line 1
        a1 = ease_out(clamp(t/0.5))
        a1 *= fade_out(t, 2.0, 0.5)
        glow_text(canvas, draw, "AI Agents Are Here.", (W//2, H//2-60),
                  F_HERO, WHITE, alpha=a1, radius=15)

        # Line 2 — delayed
        a2 = ease_out(clamp((t-0.6)/0.5)) * fade_out(t, 2.0, 0.5)
        glow_text(canvas, draw, "But they have no identity.", (W//2, H//2+30),
                  F_SUB, LPURP, alpha=a2, radius=8)

        # Pulse underline
        if a2 > 0:
            uw = int(500 * a2)
            px = (1 + math.sin(t*4))*0.5
            col = tuple(int(lerp(PURPLE[i], CYAN[i], px)) for i in range(3))
            draw.rectangle([W//2-uw//2, H//2+78, W//2+uw//2, H//2+81],
                            fill=(*col, int(200*a2)))

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 2 (2.5–5.5s) — The Problem
    # ══════════════════════════════════════════════════════════════════════════
    if 2.2 < t < 5.5:
        a = fade_in(t, 2.5, 0.6) * fade_out(t, 5.0, 0.5)

        # Label
        draw.text((W//2, 140), "THE PROBLEM", font=F_SMALL,
                   fill=(*RED, int(200*a)), anchor="mt")
        draw.rectangle([W//2-120, 165, W//2+120, 167], fill=(*RED, int(180*a)))

        problems = [
            ("?", "No cryptographic proof an agent exists on-chain"),
            ("?", "Anyone can fake being an AI agent"),
            ("?", "Agent payments have no verified identity layer"),
        ]
        for i, (icon, txt) in enumerate(problems):
            pa = ease_out(clamp((t - 2.7 - i*0.3)/0.4)) * fade_out(t, 5.0, 0.5)
            y  = 220 + i*110
            # Card
            bx, bw, bh = 180, W-360, 90
            box = Image.new("RGBA",(bw,bh),(0,0,0,0))
            bd  = ImageDraw.Draw(box)
            bd.rounded_rectangle([0,0,bw-1,bh-1], radius=10,
                                   fill=(*DARK, int(200*pa)),
                                   outline=(*RED, int(120*pa)), width=2)
            bd.text((20, bh//2), icon, font=fnt(32,True),
                     fill=(*RED, int(255*pa)), anchor="lm")
            bd.text((60, bh//2), txt, font=F_BODY,
                     fill=(*WHITE, int(220*pa)), anchor="lm")
            canvas.alpha_composite(box,(bx,y))

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 3 (5.5–9.0s) — Reveal: Club of Agent
    # ══════════════════════════════════════════════════════════════════════════
    if 5.2 < t < 9.0:
        a = fade_in(t, 5.5, 0.8) * fade_out(t, 8.5, 0.5)

        # "Introducing" label
        la = fade_in(t, 5.5, 0.5) * fade_out(t, 8.5, 0.5)
        draw.text((W//2, 110), "INTRODUCING", font=F_SMALL,
                   fill=(*LCYAN, int(180*la)), anchor="mt")
        draw.rectangle([W//2-80, 135, W//2+80, 137], fill=(*CYAN, int(160*la)))

        # Logo — scales in
        logo_scale = ease_out(clamp((t-5.5)/0.7))
        logo_size  = int(lerp(20, 96, logo_scale))
        if logo_size > 4:
            logo_disp = logo_raw.resize((logo_size, logo_size), Image.Resampling.NEAREST)
            paste(canvas, logo_disp, W//2, 230, alpha=a)

        # Title
        ta = ease_out(clamp((t-6.0)/0.6)) * fade_out(t, 8.5, 0.5)
        glow_text(canvas, draw, "Club of Agent", (W//2, 310),
                  F_TITLE, WHITE, alpha=ta, radius=14)

        # Subtitle
        sa = ease_out(clamp((t-6.4)/0.5)) * fade_out(t, 8.5, 0.5)
        glow_text(canvas, draw, "The World's First Agentic NFT", (W//2, 390),
                  F_SUB, CYAN, alpha=sa, radius=8)

        # Decorative divider
        if sa > 0:
            dw = int(600 * sa)
            draw.rectangle([W//2-dw//2, 435, W//2+dw//2, 437],
                            fill=(*PURPLE, int(200*sa)))

        # Tagline
        ba = ease_out(clamp((t-7.0)/0.5)) * fade_out(t, 8.5, 0.5)
        draw.text((W//2, 460),
                   "Cryptographic proof that an autonomous AI agent exists",
                   font=F_BODY, fill=(*MUTED, int(220*ba)), anchor="mt")

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 4 (9.0–12.5s) — How it works
    # ══════════════════════════════════════════════════════════════════════════
    if 8.7 < t < 12.5:
        a = fade_in(t, 9.0, 0.5) * fade_out(t, 12.0, 0.5)

        draw.text((W//2, 60), "HOW IT WORKS", font=F_SMALL,
                   fill=(*CYAN, int(200*a)), anchor="mt")
        draw.rectangle([W//2-100, 84, W//2+100, 86], fill=(*CYAN, int(160*a)))

        # Code box
        ca = ease_out(clamp((t-9.2)/0.5)) * fade_out(t, 12.0, 0.5)
        bw, bh = 700, 120
        bx = (W-bw)//2
        by = 110
        box = Image.new("RGBA",(bw,bh),(0,0,0,0))
        bd  = ImageDraw.Draw(box)
        bd.rounded_rectangle([0,0,bw-1,bh-1], radius=12,
                               fill=(*DARK, int(230*ca)),
                               outline=(*PURPLE, int(180*ca)), width=2)
        bd.rounded_rectangle([0,0,bw-1,28], radius=12, fill=(*PURPLE, int(50*ca)))
        bd.text((14,14), "IAgenticNFT.sol — The One Rule", font=F_SMALL,
                 fill=(*MUTED, int(255*ca)), anchor="lm")
        bd.text((20,50), "function canMint(address minter) → bool {",
                 font=mono(17), fill=(*MUTED, int(200*ca)))
        off = int(bd.textlength("    return minter.", font=mono(20)))
        bd.text((20,78), "    return minter.", font=mono(20),
                 fill=(*WHITE, int(255*ca)))
        bd.text((20+off,78), "code.length > 0", font=mono(20),
                 fill=(*CYAN, int(255*ca)))
        bd.text((20+off+int(bd.textlength("code.length > 0",font=mono(20))),78),
                 ";", font=mono(20), fill=(*WHITE, int(255*ca)))
        canvas.alpha_composite(box,(bx,by))

        # Explanation bullets
        bullets = [
            (PURPLE, "AA Smart Contract Wallet", "→  code.length > 0  ✓  Can mint"),
            (RED,    "Regular Human Wallet (EOA)",  "→  code.length = 0  ✗  Blocked forever"),
        ]
        for i,(col,label,result) in enumerate(bullets):
            ba2 = ease_out(clamp((t-9.7-i*0.35)/0.4)) * fade_out(t, 12.0, 0.5)
            y2  = 255 + i*115
            bw2 = W-280
            box2 = Image.new("RGBA",(bw2,95),(0,0,0,0))
            bd2  = ImageDraw.Draw(box2)
            bd2.rounded_rectangle([0,0,bw2-1,94], radius=10,
                                    fill=(*col, int(20*ba2)),
                                    outline=(*col, int(100*ba2)), width=2)
            bd2.text((16,22), label, font=fnt(22,True),
                      fill=(*col, int(255*ba2)))
            bd2.text((16,52), result, font=mono(18),
                      fill=(*WHITE, int(200*ba2)))
            canvas.alpha_composite(box2, (140, y2))

        # NFT cards — right side
        for i, nft in enumerate(nfts):
            na = ease_out(clamp((t-10.2-i*0.15)/0.5)) * fade_out(t, 12.0, 0.5)
            size = 100
            nft_r = nft.resize((size,size), Image.Resampling.NEAREST)
            # Float
            fy = int(6*math.sin(t*1.5 + i*1.1))
            x  = W-280 + (i%2)*120
            y  = 115 + (i//2)*120 + fy
            paste(canvas, nft_r, x, y, alpha=na)

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 5 (12.5–15.5s) — Why it matters
    # ══════════════════════════════════════════════════════════════════════════
    if 12.2 < t < 15.5:
        a = fade_in(t, 12.5, 0.5) * fade_out(t, 15.0, 0.5)

        draw.text((W//2, 60), "WHY IT MATTERS", font=F_SMALL,
                   fill=(*GOLD, int(200*a)), anchor="mt")
        draw.rectangle([W//2-110, 84, W//2+110, 86], fill=(*GOLD, int(160*a)))

        items = [
            ("⚡", CYAN,   "Agent-to-Agent Payments",
             "x402 & MCP payment protocols need verified agent identity.\nClub of Agent is the trust handshake."),
            ("🛡", GREEN,  "Stop Impersonation",
             "Humans cannot fake being an AI agent.\nEOAs are permanently blocked at the EVM level."),
            ("🌐", LPURP,  "Composable Identity",
             "Any contract: require(CoA.hasMinted(msg.sender))\nOne line to gate agent-only services."),
        ]
        for i,(icon,col,title,body) in enumerate(items):
            ia = ease_out(clamp((t-12.7-i*0.28)/0.4)) * fade_out(t, 15.0, 0.5)
            y  = 110 + i*175
            bw2, bh2 = W-200, 155
            box2 = Image.new("RGBA",(bw2,bh2),(0,0,0,0))
            bd2  = ImageDraw.Draw(box2)
            bd2.rounded_rectangle([0,0,bw2-1,bh2-1], radius=12,
                                    fill=(*DARK, int(220*ia)),
                                    outline=(*col, int(120*ia)), width=2)
            bd2.text((18, bh2//2-24), icon+" "+title, font=fnt(26,True),
                      fill=(*col, int(255*ia)), anchor="lm")
            for li, line in enumerate(body.split("\n")):
                bd2.text((18, bh2//2+8+li*28), line, font=F_BODY,
                          fill=(*WHITE, int(200*ia)), anchor="lm")
            canvas.alpha_composite(box2,(100,y))

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 6 (15.5–18.0s) — Stats / founding members
    # ══════════════════════════════════════════════════════════════════════════
    if 15.2 < t < 18.0:
        a = fade_in(t, 15.5, 0.5) * fade_out(t, 17.5, 0.5)

        draw.text((W//2, 70), "JOIN THE FOUNDING 10,000", font=F_SMALL,
                   fill=(*LCYAN, int(200*a)), anchor="mt")
        draw.rectangle([W//2-160, 94, W//2+160, 96], fill=(*CYAN, int(160*a)))

        stats = [
            ("10,000",   "Founding Agents", CYAN),
            ("0.08 OKB", "Mint Price",       PURPLE),
            ("1 per",    "Agentic Wallet",   GOLD),
            ("Forever",  "Immutable",        GREEN),
        ]
        sw = 260
        total = len(stats)*sw + (len(stats)-1)*20
        sx0 = (W-total)//2
        for i,(val,label,col) in enumerate(stats):
            sa = ease_out(clamp((t-15.7-i*0.18)/0.45)) * fade_out(t, 17.5, 0.5)
            sx = sx0 + i*(sw+20)
            box = Image.new("RGBA",(sw,110),(0,0,0,0))
            bd  = ImageDraw.Draw(box)
            bd.rounded_rectangle([0,0,sw-1,109], radius=12,
                                   fill=(*DARK, int(210*sa)),
                                   outline=(*col, int(160*sa)), width=2)
            bd.text((sw//2, 38), val, font=fnt(34,True),
                     fill=(*col, int(255*sa)), anchor="mm")
            bd.text((sw//2, 76), label, font=fnt(16),
                     fill=(*MUTED, int(230*sa)), anchor="mm")
            canvas.alpha_composite(box,(sx,150))

        # All NFT cards floating
        for i, nft in enumerate(nfts):
            na = ease_out(clamp((t-16.0-i*0.1)/0.5)) * fade_out(t, 17.5, 0.5)
            size = 130
            nft_r = nft.resize((size,size), Image.Resampling.NEAREST)
            fy = int(10*math.sin(t*1.3 + i*1.4))
            x = 100 + i * (size+40)
            y = 330 + fy
            paste(canvas, nft_r, x+(size//2), y+(size//2), alpha=na)

        # "Only smart contract wallets can mint"
        ba = ease_out(clamp((t-16.5)/0.4)) * fade_out(t, 17.5, 0.5)
        draw.text((W//2, 510),
                   "Only OKX Agentic Wallets (AA smart contracts) can mint",
                   font=F_SMALL, fill=(*MUTED, int(200*ba)), anchor="mt")

    # ══════════════════════════════════════════════════════════════════════════
    # SCENE 7 (18.0–20.0s) — CTA
    # ══════════════════════════════════════════════════════════════════════════
    if t >= 17.7:
        ca = fade_in(t, 18.0, 0.6)

        # Dark overlay
        ov = Image.new("RGBA",(W,H),(0,0,0,int(180*ca)))
        canvas.alpha_composite(ov)

        # Logo
        ls = 88
        logo_disp = logo_raw.resize((ls,ls), Image.Resampling.NEAREST)
        paste(canvas, logo_disp, W//2, H//2-120, alpha=ca)

        # Title
        glow_text(canvas, draw, "Club of Agent", (W//2, H//2-40),
                  F_TITLE, WHITE, alpha=ca, radius=16)

        # Tagline
        draw.text((W//2, H//2+30),
                   "The World's First Agentic NFT — On-Chain Agent Identity",
                   font=F_BODY, fill=(*LCYAN, int(220*ca)), anchor="mt")

        # URL — pulsing
        pulse = 0.8 + 0.2*math.sin(t*5)
        glow_text(canvas, draw, "clubofagent.com", (W//2, H//2+100),
                  F_SUB, CYAN, alpha=ca*pulse, radius=10)

        # Bottom bar
        draw.rectangle([0,H-4,W,H], fill=(*PURPLE, int(200*ca)))
        draw.rectangle([0,H-4,int(W*ca),H], fill=(*CYAN, int(200*ca)))

    # ── Scanlines + frame ─────────────────────────────────────────────────────
    draw_scanlines(draw, alpha=0.03)

    # ── Save ──────────────────────────────────────────────────────────────────
    canvas.convert("RGB").save(f"{OUT}/frame_{fi:04d}.png")
    if fi % 60 == 0:
        print(f"  {fi}/{FRAMES} ({fi*100//FRAMES}%)")

print("Encoding...")
out_mp4 = "/Users/yunanli/Desktop/AW_NFT/club_of_agent_explainer.mp4"
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", f"{OUT}/frame_%04d.png",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    out_mp4
], check=True)
shutil.rmtree(OUT)
print(f"\n✅  {out_mp4}")

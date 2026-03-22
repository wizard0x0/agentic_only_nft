#!/usr/bin/env python3
"""Generate robotic/synthwave soundtrack for the 20s Club of Agent explainer."""

import numpy as np
from scipy.io import wavfile

SR   = 44100   # sample rate
DUR  = 20.0    # seconds
N    = int(SR * DUR)
t    = np.linspace(0, DUR, N, endpoint=False)

def silence(n=N): return np.zeros(n)
def s(start, end): return slice(int(start*SR), int(end*SR))
def env(start, end, attack=0.05, release=0.08):
    """Simple envelope over the full buffer."""
    e = np.zeros(N)
    a = int(attack*SR); r = int(release*SR)
    i0 = int(start*SR); i1 = int(end*SR)
    length = i1 - i0
    e[i0:i0+min(a,length)] = np.linspace(0,1,min(a,length))
    e[i0+min(a,length):i1-min(r,length)] = 1.0
    e[i1-min(r,length):i1] = np.linspace(1,0,min(r,length))
    return e

def sine(freq, amp=1.0): return amp * np.sin(2*np.pi*freq*t)
def saw(freq, amp=1.0):
    return amp * (2*(t*freq - np.floor(t*freq+0.5)))
def square(freq, amp=1.0):
    return amp * np.sign(np.sin(2*np.pi*freq*t))
def noise(amp=1.0): return amp * np.random.uniform(-1,1,N)

# ── Layer 1: Deep robotic drone (throughout) ──────────────────────────────────
drone = (
    sine(55,  0.18) +
    sine(55*2, 0.10) +
    saw(55,   0.06) +
    sine(110, 0.05)
)
drone *= env(0, 20, attack=1.5, release=2.0)

# ── Layer 2: Pulse/heartbeat (robotic LFO rhythm) ────────────────────────────
# 2 beats per second pulse
lfo = (np.sin(2*np.pi*2*t) > 0.6).astype(float)
lfo_smooth = np.convolve(lfo, np.ones(int(SR*0.02))/int(SR*0.02), mode='same')
pulse_tone = sine(220, 0.22) * lfo_smooth
pulse_tone *= env(0, 20, attack=0.5, release=1.5)

# ── Layer 3: Robotic arpeggiated melody ──────────────────────────────────────
# Notes: minor pentatonic-ish, robotic saw wave
arp = silence()
melody = [
    # (start, dur, freq)
    (0.5, 0.12, 440), (0.7, 0.12, 330), (0.9, 0.12, 440), (1.1, 0.12, 262),
    (2.6, 0.10, 523), (2.8, 0.10, 440), (3.0, 0.10, 392), (3.2, 0.10, 330),
    (3.4, 0.10, 392), (3.6, 0.10, 440),
    (5.5, 0.15, 659), (5.75,0.15, 587), (6.0, 0.25, 523), (6.4, 0.15, 440),
    (6.7, 0.15, 392), (7.0, 0.30, 523), (7.5, 0.20, 440), (7.9, 0.20, 392),
    (9.0, 0.10, 440), (9.15,0.10, 523), (9.3, 0.10, 587), (9.5, 0.10, 659),
    (9.7, 0.10, 523), (9.9, 0.10, 440),
    (10.5,0.10, 330),(10.7,0.10, 392),(10.9,0.10, 440),(11.1,0.10, 523),
    (12.5,0.15, 659),(12.75,0.15,587),(13.0,0.25,523),(13.4,0.15,440),
    (13.7,0.15,392),(14.0,0.30,659),(14.5,0.20,587),(14.9,0.20,523),
    (15.5,0.12,440),(15.7,0.12,523),(15.9,0.12,587),(16.1,0.12,659),
    (16.4,0.12,587),(16.6,0.12,523),(16.8,0.12,440),(17.0,0.12,392),
    (18.0,0.20,523),(18.3,0.20,659),(18.6,0.20,784),(18.9,0.40,1047),
    (19.5,0.40,784),
]
for (st, dur, freq) in melody:
    i0 = int(st*SR)
    i1 = min(N, int((st+dur)*SR))
    ln = i1-i0
    tt = np.arange(ln)/SR
    note = 0.18*np.sign(np.sin(2*np.pi*freq*tt))  # square = robotic
    # Quick envelope per note
    att = min(int(0.01*SR), ln//3)
    rel = min(int(0.03*SR), ln//3)
    e   = np.ones(ln)
    e[:att] = np.linspace(0,1,att)
    e[ln-rel:] = np.linspace(1,0,rel)
    arp[i0:i1] += note*e

# ── Layer 4: Scene transition whooshes ───────────────────────────────────────
whoosh = silence()
transitions = [2.5, 5.5, 9.0, 12.5, 15.5, 18.0]
for ts in transitions:
    i0 = int(ts*SR)
    dur_s = int(0.35*SR)
    if i0+dur_s > N: continue
    tt  = np.linspace(0,1,dur_s)
    # Rising frequency sweep (robotic whoosh)
    freq_sweep = 200 + 1800*tt
    phase = 2*np.pi*np.cumsum(freq_sweep)/SR
    sweep = 0.3*np.sin(phase)
    # Fade in/out
    e = np.hanning(dur_s)
    whoosh[i0:i0+dur_s] += sweep*e

# ── Layer 5: Robotic glitch/click accents ────────────────────────────────────
glitch = silence()
clicks = [0.5, 0.7, 0.9, 1.1, 6.0, 7.0, 9.0, 10.5, 12.5, 13.0, 15.5, 16.0, 18.0, 18.3, 18.6]
for ck in clicks:
    i0 = int(ck*SR)
    ln = int(0.025*SR)
    if i0+ln > N: continue
    tt2 = np.arange(ln)/SR
    click = 0.25*np.sin(2*np.pi*4000*tt2) * np.hanning(ln)
    glitch[i0:i0+ln] += click

# ── Layer 6: CTA build-up (18–20s) ───────────────────────────────────────────
buildup = silence()
i0 = int(18.0*SR)
ln = N - i0
tt3 = np.arange(ln)/SR
t_seg = tt3  # local time axis for this segment
# Rising saw chord using local time
seg = (
    0.08*(2*(t_seg*523 - np.floor(t_seg*523+0.5))) +
    0.06*(2*(t_seg*659 - np.floor(t_seg*659+0.5))) +
    0.05*(2*(t_seg*784 - np.floor(t_seg*784+0.5)))
) * np.linspace(0, 1, ln)
buildup[i0:] = seg

# ── Layer 7: Sub-bass kick (every beat) ──────────────────────────────────────
kick = silence()
bpm  = 120
beat = SR * 60 / bpm
for b in range(int(DUR * bpm / 60)):
    i0 = int(b * beat)
    ln = min(int(0.15*SR), N-i0)
    if i0+ln > N: break
    tt4 = np.arange(ln)/SR
    freq_kick = 80*np.exp(-30*tt4)
    sub = 0.30*np.sin(2*np.pi*np.cumsum(freq_kick)/SR) * np.exp(-20*tt4)
    kick[i0:i0+ln] += sub

# ── Mix everything ────────────────────────────────────────────────────────────
mix = (
    drone   * 1.0 +
    pulse_tone * 0.8 +
    arp     * 1.0 +
    whoosh  * 1.2 +
    glitch  * 0.9 +
    buildup * 1.0 +
    kick    * 0.7
)

# Normalize + soft limiter
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.85
mix = np.tanh(mix * 1.5) / 1.5   # soft clip

# Convert to 16-bit
out = (mix * 32767).astype(np.int16)
wavfile.write("/Users/yunanli/Desktop/AW_NFT/soundtrack.wav", SR, out)
print("✅  soundtrack.wav written")

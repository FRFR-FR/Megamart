#!/usr/bin/env python3
"""Synthesize music + SFX for 'The Bridge That Wobbled' (30 s, 48 kHz mono) and mix with the voice, music ducked under speech."""
import numpy as np, soundfile as sf, subprocess
SR = 48000; N = SR * 30; D = 'shorts/millennium'
rng = np.random.default_rng(3)
def env(n, a=.005, r=.25): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / r)
def tone(f, d, r=.25, harm=(1, .35, .15)): t = np.arange(int(d * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (i + 1) * t) for i, h in enumerate(harm)) * env(len(t), .004, r)
def put(buf, x, at, g=1.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i] * g
# music: bouncy 108 bpm pluck arpeggio + bass, C - Am - F - G, in a light "brass band" feel
mus = np.zeros(N); beat = 60 / 108; chords = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
for bar in range(int(30 / (beat * 4)) + 1):
    c = chords[bar % 4]; t0 = bar * beat * 4
    for k in range(8): put(mus, tone(c[k % 3] * 2, .3, .16), t0 + k * beat / 2, .16)
    put(mus, tone(c[0] / 2, .45, .3, (1, .5)), t0, .3); put(mus, tone(c[0] / 2 * 1.5, .45, .3, (1, .5)), t0 + beat * 2, .26)
    for k in (1, 3): put(mus, np.concatenate([rng.normal(0, 1, int(.05 * SR))]) * env(int(.05 * SR), .001, .02), t0 + k * beat, .05)   # soft snare tick
mus *= np.minimum(1, np.arange(N) / (SR * .5)) * np.minimum(1, (N - np.arange(N)) / (SR * 1.5))
# SFX
sfx = np.zeros(N)
t = np.arange(int(.6 * SR)) / SR; thud = (np.sin(2 * np.pi * 70 * np.exp(-t * 6) * t * 3) + .4 * rng.normal(0, 1, len(t)) * np.exp(-t * 30)) * np.exp(-t * 7); put(sfx, thud, 12.35, .9); put(sfx, thud * .8, 12.45, .6)   # barriers land
t = np.arange(int(.45 * SR)) / SR; sq = np.sin(2 * np.pi * (1800 - 900 * t / .45) * t) * np.exp(-t * 3) * (.5 + .5 * np.sin(2 * np.pi * 40 * t)); put(sfx, sq, 18.2, .22)                         # bus brakes
for i in range(24): put(sfx, tone(900 + 35 * i, .09, .03, (1, .3)), 22.75 + i * .06, .35)                                                                                                    # dampers click on
for k in range(0, 14): put(sfx, tone(110 + 8 * (k % 3), .25, .12, (1, .6)), 2.4 + k * .55, .06 * (1 if 2.4 + k * .55 < 24 else 0))                                                              # deck creak/sway pulse
sf.write('/tmp/music.wav', mus / np.abs(mus).max() * .5, SR); sf.write('/tmp/sfx.wav', sfx / max(1e-6, np.abs(sfx).max()) * .7, SR)
# mix: voice unchanged, music ducked under speech (sidechain), sfx on top; length exactly 30 s
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{D}/voice/voice.wav', '-i', '/tmp/music.wav', '-i', '/tmp/sfx.wav', '-filter_complex',
  '[0:a]apad=whole_dur=30,asplit=2[v][vs];[1:a]volume=0.55[m];[m][vs]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=250[md];[2:a]volume=0.8[s];'
  '[v][md][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95,atrim=0:30[out]', '-map', '[out]', '-ar', '48000', '-ac', '1', f'{D}/audio_mix.wav'], check=True)
print('mix ok')

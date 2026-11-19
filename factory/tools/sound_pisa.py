#!/usr/bin/env python3
"""Synthesize music + SFX for 'The Queue' (30 s, 48 kHz mono) and mix with the voice, music ducked under speech."""
import numpy as np, soundfile as sf, subprocess
SR = 48000; N = int(SR * 30.0); D = 'shorts/pisa'
rng = np.random.default_rng(3)
def env(n, a=.005, r=.25): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / r)
def tone(f, d, r=.25, harm=(1, .35, .15)): t = np.arange(int(d * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (i + 1) * t) for i, h in enumerate(harm)) * env(len(t), .004, r)
def put(buf, x, at, g=1.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i] * g
# music: bouncy 108 bpm pluck arpeggio + bass, C - Am - F - G, in a light "brass band" feel
mus = np.zeros(N); beat = 60 / 108; chords = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
for bar in range(int(30.0 / (beat * 4)) + 1):
    c = chords[bar % 4]; t0 = bar * beat * 4
    for k in range(8): put(mus, tone(c[k % 3] * 2, .3, .16), t0 + k * beat / 2, .16)
    put(mus, tone(c[0] / 2, .45, .3, (1, .5)), t0, .3); put(mus, tone(c[0] / 2 * 1.5, .45, .3, (1, .5)), t0 + beat * 2, .26)
    for k in (1, 3): put(mus, np.concatenate([rng.normal(0, 1, int(.05 * SR))]) * env(int(.05 * SR), .001, .02), t0 + k * beat, .05)   # soft snare tick
mus *= np.minimum(1, np.arange(N) / (SR * .5)) * np.minimum(1, (N - np.arange(N)) / (SR * 1.5))
# SFX
sfx = np.zeros(N)
def thud(t, f=90, a=1): tt = np.arange(int(.35 * SR)) / SR; put(sfx, (np.sin(2 * np.pi * f * tt * np.exp(-tt * 6)) + .3 * rng.normal(0, 1, len(tt)) * np.exp(-tt * 40)) * np.exp(-tt * 9), t, .6 * a)
for t in (.3, 1.4): thud(t, 110, .6)                                                                                     # first stones go down
for t in (10.4, 10.9, 11.4, 11.9, 12.4, 12.9): thud(t, 100, .8)                                                          # builders return: floors stack up fast
tt = np.arange(int(.5 * SR)) / SR; put(sfx, rng.normal(0, 1, len(tt)) * np.exp(-tt * 9) * np.minimum(1, tt / .02), 13.55, .5)   # gasp on "Wait"
for i in range(4): thud(18.0 + i * .5, 140, .7)                                                                          # books land on the sofa
for i in range(5): put(sfx, rng.normal(0, 1, int(.18 * SR)) * np.exp(-np.arange(int(.18 * SR)) / SR * 22), 20.9 + i * .9, .35)    # soil scooped out
for i, x in enumerate([523, 659, 784, 1047]): put(sfx, tone(x, .5, .3, (1, .3)), 25.9 + i * .1, .3)                      # tourists strike the pose
put(sfx, tone(330, .35, .2, (1, .5)), 28.6, .3); put(sfx, tone(262, .5, .3, (1, .5)), 28.95, .3)                           # wah-wah ending
sf.write('/tmp/music.wav', mus / np.abs(mus).max() * .5, SR); sf.write('/tmp/sfx.wav', sfx / max(1e-6, np.abs(sfx).max()) * .7, SR)
# mix: voice unchanged, music ducked under speech (sidechain), sfx on top; length 30.8 s
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{D}/voice/voice.wav', '-i', '/tmp/music.wav', '-i', '/tmp/sfx.wav', '-filter_complex',
  '[0:a]apad=whole_dur=30.0,asplit=2[v][vs];[1:a]volume=0.55[m];[m][vs]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=250[md];[2:a]volume=0.8[s];'
  '[v][md][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95,atrim=0:30.0[out]', '-map', '[out]', '-ar', '48000', '-ac', '1', f'{D}/audio_mix.wav'], check=True)
print('mix ok')

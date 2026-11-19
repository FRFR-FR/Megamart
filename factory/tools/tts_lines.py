#!/usr/bin/env python3
"""Synthesize SCRIPT.md line by line with kokoro-onnx (British voice). Per-line synthesis => exact line timings.
usage: tts_lines.py SCRIPT.md outdir [--voice bm_george] [--speed 1.15] [--gap 0.10]
writes outdir/voice.wav (48 kHz mono), lines.json [{text,start,end}], words.json [{word,start,end}] (words spread by character count)."""
import json, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
a = sys.argv; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
script, out = a[1], a[2]; voice = opt('--voice', 'bm_george'); speed = float(opt('--speed', 1.15)); gap = float(opt('--gap', .10))
lines = []; head = True
for ln in open(script, encoding='utf-8').read().splitlines():
    if head:
        if not ln.strip() and any(h for h in lines) : head = False
        elif ln.strip() and not ln.startswith(('#', 'Format:', 'Facts:')): head = False; lines.append(ln.strip())
        continue
    if ln.strip() and not ln.startswith(('#', '>')): lines.append(ln.strip())
k = Kokoro(f'{out}/kokoro-v1.0.onnx', f'{out}/voices-v1.0.bin'); SR = 24000
audio, L, W, t = [], [], [], 0.0
for txt in lines:
    s, sr = k.create(txt, voice=voice, speed=speed, lang='en-gb'); assert sr == SR
    # trim leading/trailing silence of each take
    m = np.abs(s) > 0.01; i, j = (np.argmax(m), len(m) - np.argmax(m[::-1])) if m.any() else (0, len(s)); s = s[max(0, i - 120):min(len(s), j + 240)]
    d = len(s) / SR; L.append({'text': txt, 'start': round(t, 3), 'end': round(t + d, 3)})
    ws = re.findall(r"\S+", txt); ch = sum(len(w) for w in ws); x = t
    for w in ws: dw = d * len(w) / ch; W.append({'word': w, 'start': round(x, 3), 'end': round(x + dw, 3)}); x += dw
    audio += [s, np.zeros(int(gap * SR), dtype=s.dtype)]; t += d + gap
y = np.concatenate(audio); y = y / max(1e-6, np.abs(y).max()) * 0.92
import subprocess, tempfile, os
tmp = out + '/_v24.wav'; sf.write(tmp, y, SR); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-ar', '48000', '-ac', '1', out + '/voice.wav'], check=True); os.remove(tmp)
json.dump(L, open(out + '/lines.json', 'w'), indent=1); json.dump(W, open(out + '/words.json', 'w'), indent=1)
print(f'{len(lines)} lines, {len(W)} words, {t:.2f} s, {len(W)/t:.2f} words/s')
for l in L: print(f"{l['start']:6.2f}-{l['end']:6.2f}  {l['text'][:60]}")

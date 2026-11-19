#!/usr/bin/env python3
"""Check voice word timings (words.json) against the measured narrator profile.

Usage: python check_timings.py words.json [--fps 30]

Accepts a list of {word|text, start|s|t0, end|e|t1} in seconds (whisper-style word timestamps).
Measured reference profile: 3.5-4.1 words/s, voice starts within frame 1-4,
total gaps > 0.25 s under ~1 s per video, length 31-78 s (ours 55-70 s).
"""
import json
import sys


def pick(d, *keys):
    for k in keys:
        if k in d:
            return d[k]
    raise KeyError(f"none of {keys} in {list(d)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    fps = 30
    if "--fps" in sys.argv:
        fps = int(sys.argv[sys.argv.index("--fps") + 1])
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("words") or data.get("segments") or []
    ws = [(str(pick(w, "word", "text")).strip(), float(pick(w, "start", "s", "t0")), float(pick(w, "end", "e", "t1"))) for w in data]
    if not ws:
        print("FAIL no words")
        return 1
    start, end = ws[0][1], ws[-1][2]
    dur = end - start
    wps = len(ws) / dur
    gaps = [b[1] - a[2] for a, b in zip(ws, ws[1:]) if b[1] - a[2] > 0.25]
    bad = False
    print(f"INFO {len(ws)} words, {dur:.1f} s, {wps:.2f} words/s, first word at frame {round(start * fps)}")
    if not 3.5 <= wps <= 4.1:
        print(f"WARN speed {wps:.2f} words/s is outside the reference 3.5-4.1")
    if round(start * fps) > 4:
        print(f"FAIL voice starts at frame {round(start * fps)}; reference starts at frame 1-4 (trim leading silence)")
        bad = True
    if sum(gaps) > 1.0:
        print(f"WARN pauses >0.25 s total {sum(gaps):.2f} s (reference < 1 s): tighten the voice take")
    if not 55 <= dur <= 70:
        print(f"FAIL duration {dur:.1f} s outside 55-70 s")
        bad = True
    # words per frame-boundary helper for story.ts: every visual reaction lands 0-3 frames BEFORE its word
    print("INFO word -> frame table (first 12):", ", ".join(f"{w}@{max(0, round(s * fps) - 2)}" for w, s, _ in ws[:12]))
    print("RESULT", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

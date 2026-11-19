#!/usr/bin/env python3
"""Lint a SCRIPT.md against the measured script formula (cartoon-3d-short STYLE_BIBLE.md).

Usage: python lint_script.py SCRIPT.md [--dur 25-35] [--allow-cta] [--ban "word" ...]

SCRIPT.md layout (same as templates/SCRIPT_example.md):
  # "Title"
  Format: ...
  Facts: ... (Source)          <- header block, ends at the first blank line
  <blank line>
  one spoken sentence-group per line   <- the narration

Exit code 0 = pass (warnings allowed), 1 = at least one hard failure.
"""
import re
import statistics
import sys

WPS = 3.7                      # median narrator speed measured on 20 reference shorts
DUR_MIN, DUR_MAX = 55, 70      # seconds
HOOK_MIN, HOOK_MAX = 8, 16     # words, hook = sentence 1
SENT_MED_MIN, SENT_MED_MAX = 10, 17  # median sentence length (reference ~13.5)
ANALOGY = re.compile(r"\b(ever\b|think about|picture|imagine|just like|like a)\b", re.I)
PIVOT = re.compile(r"\byou see,", re.I)


def parse(path):
    raw = open(path, encoding="utf-8").read().splitlines()
    head, body, in_head = [], [], True
    for ln in raw:
        if in_head:
            if ln.strip() == "" and any(h.strip() and not h.startswith("#") for h in head):
                in_head = False
                continue
            head.append(ln)
        elif ln.strip() and not ln.startswith(("#", ">")):
            body.append(ln.strip())
    return head, body


def sentences(lines):
    text = " ".join(lines)
    parts = re.split(r"(?<=[.?!])\s+", text)
    return [p for p in parts if p.strip()]


def wc(s):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", s))


def main():
    global DUR_MIN, DUR_MAX
    if "--dur" in sys.argv:
        a, b = sys.argv[sys.argv.index("--dur") + 1].split("-"); DUR_MIN, DUR_MAX = float(a), float(b)
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    bans = [sys.argv[i + 1].lower() for i, a in enumerate(sys.argv) if a == "--ban" and i + 1 < len(sys.argv)]
    head, body = parse(path)
    sents = sentences(body)
    fails, warns, notes = [], [], []

    head_txt = " ".join(head)
    if "facts:" not in head_txt.lower():
        fails.append("No 'Facts:' line in the header. Write the true facts with their source at the top (pipeline step 1).")
    elif not re.search(r"\([^)]{4,}\)", head_txt.split("Facts:", 1)[-1] if "Facts:" in head_txt else head_txt):
        fails.append("Facts line has no source in parentheses, e.g. (Wikipedia, Broughton Suspension Bridge).")

    if not sents:
        fails.append("No narration found below the header block.")
        print("\n".join("FAIL " + f for f in fails))
        return 1

    words = sum(wc(s) for s in sents)
    dur = words / WPS
    notes.append(f"{words} words -> {dur:.1f} s at {WPS} words/s ({len(sents)} sentences)")
    if not DUR_MIN <= dur <= DUR_MAX:
        lo, hi = int(DUR_MIN * WPS), int(DUR_MAX * WPS)
        fails.append(f"Length {dur:.1f} s is outside {DUR_MIN}-{DUR_MAX} s. Aim for {lo}-{hi} words.")

    hook = sents[0]
    hw = wc(hook)
    notes.append(f"hook ({hw} words): {hook}")
    if not HOOK_MIN <= hw <= HOOK_MAX:
        fails.append(f"Hook is {hw} words; the formula wants one sentence of ~{HOOK_MIN}-{HOOK_MAX} words, stated as fact, no setup.")
    if hook.rstrip().endswith("?"):
        warns.append("Hook is a question. The formula states the paradox as a fact.")

    lens = [wc(s) for s in sents]
    med = statistics.median(lens)
    notes.append(f"median sentence {med:.1f} words (reference ~13.5), longest {max(lens)}")
    if not SENT_MED_MIN <= med <= SENT_MED_MAX:
        warns.append(f"Median sentence length {med:.1f} is outside {SENT_MED_MIN}-{SENT_MED_MAX}. Keep plain, spoken, contractions OK.")
    if max(lens) > 30:
        warns.append(f"A sentence runs {max(lens)} words; split it, the narrator never pauses to breathe.")

    full = " ".join(sents)
    npiv = len(PIVOT.findall(full))
    if npiv != 1:
        fails.append(f"Found {npiv} pivots 'You see,'. Use it exactly once to switch from story to mechanism (14 of 20 reference shorts do).")
    else:
        pi = next(i for i, s in enumerate(sents) if PIVOT.search(s))
        if pi < len(sents) * 0.4:
            warns.append("The 'You see,' pivot comes early; the escalation should fill the first ~half.")
        esc = pi - 2  # sentences between hook+setting and pivot
        if esc < 3:
            fails.append(f"Only {max(esc,0)} escalation beats before the pivot; the formula has 3-6.")
        if len(sents) - pi - 1 < 2:
            warns.append("Almost nothing after the pivot; need mechanism + ironic payoff (last 1-2 sentences).")

    if not re.search(r"\?|\bwait,", full, re.I):
        warns.append("No mystery beat (a question or 'Wait, ...?'); the reference has about one per video.")
    if not ANALOGY.search(full):
        warns.append("No everyday analogy found (Ever ...? / think about ... / picture ... / like a ...).")
    if not re.search(r"\b\w+'(s|t|re|ve|ll|d)\b", full):
        warns.append("No contractions; narration should read as spoken English.")
    if not re.search(r"\d|seventeen|nineteen|eighteen|hundred|thousand|\b(first|second|third)\b", " ".join(sents[:3]), re.I):
        warns.append("Setting (lines 2-3) has no concrete number/year; the formula wants numbers and a named everyman.")

    if len(sents) >= 2:
        last2 = sents[-2:]
        if wc(last2[-1]) > 22:
            warns.append("Final sentence is long; the ironic payoff should be short and end the video on its last word.")
    if "--allow-cta" not in sys.argv and re.search(r"\b(subscribe|follow|like and|part 2|link in)\b", full, re.I):
        fails.append("CTA wording found; the format has no intro, logo, outro or CTA.")
    if re.search(r"\[(caption|text|title)", " ".join(body), re.I):
        fails.append("Caption/label markers found; our rule is no captions or labels in the video.")
    for b in bans:
        if b in full.lower():
            fails.append(f"Banned word in narration: '{b}' (e.g. never say the reference channel's name).")

    if re.search(r"\bLuckily\b", full) and re.search(r"\bUnluckily\b", full):
        notes.append("deadpan double line (Luckily/Unluckily) present")

    for n in notes:
        print("INFO ", n)
    for w in warns:
        print("WARN ", w)
    for f in fails:
        print("FAIL ", f)
    print("RESULT", "PASS" if not fails else "FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())

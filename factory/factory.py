#!/usr/bin/env python3
"""shorts-factory: one CLI that drives the cartoon-3d-short pipeline (three.js + Remotion) end to end,
with an optional Blender branch for realistic shots. Every stage is a gate: it refuses to continue
when the previous stage's measurable rules fail.

  python factory.py setup  <remotion_project_dir>        install deps + copy skill templates
  python factory.py new    <name> [--topic "..."]        create shorts/<name>/ with SCRIPT.md skeleton
  python factory.py lint   <name>                        gate 1: script formula
  python factory.py voice  <name> [--wav f --model m]    gate 2: voice -> words.json -> timing check
  python factory.py scaffold <name>                      copy templates/bridge -> src/videos/<name>
  python factory.py stills <name> <frames,...> [scale]   look checks at scale 0.5
  python factory.py sheets <name> --ours a.jpg --ref b.jpg   side-by-side for the verifier
  python factory.py sound  <name>                        build mix.wav from audio templates
  python factory.py render <name>                        final 2K render + mux voice/mix
  python factory.py qa     <name>                        frame-by-frame QA (black/white/frozen/pop, loudness)
  python factory.py blender-init                         link the realistic Blender skills

Environment: SKILL_DIR (default ~/.claude/skills/cartoon-3d-short), REMOTION_PROJECT, REMOTION_TMP.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = Path(os.environ.get("SKILL_DIR", Path.home() / ".claude/skills/cartoon-3d-short"))
BLENDER_SKILLS = Path.home() / ".claude/skills/claude-blender-skills"
SHORTS = ROOT / "shorts"
CONFIG = ROOT / ".factory.json"


def cfg():
    return json.loads(CONFIG.read_text()) if CONFIG.exists() else {}


def sh(cmd, cwd=None, env=None, check=True):
    print("$", " ".join(map(str, cmd)))
    e = dict(os.environ, **(env or {}))
    r = subprocess.run(list(map(str, cmd)), cwd=cwd, env=e)
    if check and r.returncode:
        sys.exit(r.returncode)
    return r.returncode


def proj():
    p = os.environ.get("REMOTION_PROJECT") or cfg().get("project")
    if not p:
        sys.exit("No Remotion project. Run: python factory.py setup <dir>")
    return Path(p)


def tmpdir():
    t = os.environ.get("REMOTION_TMP") or cfg().get("tmp")
    if not t:
        sys.exit("Set REMOTION_TMP to a folder on a big drive (each Remotion bundle copies public/, ~1.3 GB).")
    Path(t).mkdir(parents=True, exist_ok=True)
    return t


def need_gate(name, gate):
    g = SHORTS / name / ".gates.json"
    done = json.loads(g.read_text()) if g.exists() else {}
    if not done.get(gate):
        sys.exit(f"Gate '{gate}' has not passed for {name}. Run it first.")


def pass_gate(name, gate):
    g = SHORTS / name / ".gates.json"
    done = json.loads(g.read_text()) if g.exists() else {}
    done[gate] = True
    g.write_text(json.dumps(done))


SCRIPT_SKELETON = '''# "{title}" — original script v1
Format: vertical story short (~55-70 s, ~3.7 words/s), one steady male narrator, our own story and characters.
Facts: <one surprising TRUE story with a physical cause and effect; list each fact> (<source, e.g. Wikipedia, Article>)

<HOOK: the absurd fact as one plain sentence, 8-16 words, no setup.>
<SETTING: year, place, a named everyman, one number.>
<ESCALATION 1: others doubt or laugh, short in-character line.>
<ESCALATION 2: stakes climb.>
<ESCALATION 3: a little bigger again; one researched real-fact joke.>
<MYSTERY: a question or "Wait, ...?">
<SNAP: the moment it breaks.>
<DEADPAN DOUBLE LINE (optional): "Luckily, ..." / "Unluckily, ...">
You see, <the one real mechanism in plain words>.
<EVERYDAY ANALOGY: "Ever ...?" / "Think about the last time ...">
<CONSEQUENCE: the rule or change it created.>
<CALLBACK TWIST: short ironic payoff; the video ends on its last word.>
'''


def cmd_setup(a):
    target = Path(a[0]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    if not (target / "package.json").exists():
        (target / "package.json").write_text(json.dumps({
            "name": "shorts-project", "private": True, "type": "module",
            "dependencies": {
                "remotion": "4.0.290", "@remotion/cli": "4.0.290", "@remotion/bundler": "4.0.290",
                "@remotion/renderer": "4.0.290", "@remotion/three": "4.0.290",
                "three": "0.175.0", "@react-three/fiber": "9.1.2",
                "@react-three/postprocessing": "3.0.4", "postprocessing": "6.37.2",
                "react": "19.0.0", "react-dom": "19.0.0",
            },
            "devDependencies": {"typescript": "5.8.3", "@types/react": "19.0.0", "@types/three": "0.175.0"},
        }, indent=2))
    sh(["npm", "install"], cwd=target)
    (target / "scripts").mkdir(exist_ok=True)
    for f in (SKILL / "templates/scripts").iterdir():
        shutil.copy(f, target / "scripts" / f.name)
    # the shipped stills script has a Windows Chrome path and the BridgeShort id hardcoded: make both configurable
    s = target / "scripts/bridge-stills.mjs"
    t = s.read_text()
    t = t.replace('"C:/Program Files/Google/Chrome/Application/chrome.exe"', 'process.env.CHROME_BIN || undefined')
    t = t.replace('id: "BridgeShort"', 'id: process.env.COMP_ID || "BridgeShort"')
    s.write_text(t)
    (target / "public").mkdir(exist_ok=True)
    CONFIG.write_text(json.dumps({"project": str(target), "tmp": os.environ.get("REMOTION_TMP", str(target.parent / "remotion-tmp"))}))
    print(f"""
Project ready: {target}
Still needed by hand (not downloadable from the sandbox):
  - Kenney CC0 kits (kenney.nl) as GLBs in {target}/public/bridge/kenney/<name>.glb  (the loader falls back to null if missing)
  - src/index.ts + src/Root.tsx registering the composition (see `scaffold`)
  - Chrome/Chromium for Remotion (set CHROME_BIN) and a GPU or SwiftShader for WebGL
""")


def cmd_new(a):
    name = a[0]
    d = SHORTS / name
    if d.exists():
        sys.exit(f"{d} exists")
    for sub in ("voice", "audio", "out", "notes"):
        (d / sub).mkdir(parents=True)
    topic = a[a.index("--topic") + 1] if "--topic" in a else name
    (d / "SCRIPT.md").write_text(SCRIPT_SKELETON.format(title=topic))
    (d / "NOTES.md").write_text("Rules in force: no captions/labels, English only, one steady voice tone, jokes are researched real facts,\n"
                                "mix: music +3 dB, SFX -6 dB, voice unchanged, final 1440x2560 (--scale 1.3333), save after every step.\n"
                                "Never copy reference scripts/characters/shots; never name the reference channel in voice-over or description.\n")
    print("created", d)


def cmd_lint(a):
    d = SHORTS / a[0]
    ban = []
    for b in cfg().get("ban", []):
        ban += ["--ban", b]
    rc = sh([sys.executable, ROOT / "tools/lint_script.py", d / "SCRIPT.md", *ban], check=False)
    if rc == 0:
        pass_gate(a[0], "script")
    else:
        sys.exit(rc)


def cmd_voice(a):
    name = a[0]
    need_gate(name, "script")
    d = SHORTS / name / "voice"
    wav = Path(a[a.index("--wav") + 1]) if "--wav" in a else d / "voice.wav"
    if not wav.exists():
        sys.exit(f"{wav} missing. Record or generate the narration (one steady male tone) and save it there.")
    words = d / "words.json"
    if not words.exists():
        try:
            import whisper  # openai-whisper
        except ImportError:
            sys.exit("No words.json and openai-whisper not installed. `pip install openai-whisper` or provide words.json "
                     "([{word,start,end}] in seconds), then hand-fix timings; everything is timed to words.json.")
        model = a[a.index("--model") + 1] if "--model" in a else "small.en"
        r = whisper.load_model(model).transcribe(str(wav), word_timestamps=True, language="en")
        out = [{"word": w["word"].strip(), "start": w["start"], "end": w["end"]} for s in r["segments"] for w in s["words"]]
        words.write_text(json.dumps(out, indent=1))
        print("wrote", words, "- now hand-fix the word timings")
    rc = sh([sys.executable, ROOT / "tools/check_timings.py", words], check=False)
    if rc == 0:
        pass_gate(name, "voice")
    else:
        sys.exit(rc)


def cmd_scaffold(a):
    name = a[0]
    need_gate(name, "voice")
    p = proj()
    dst = p / "src/videos" / name
    if dst.exists():
        sys.exit(f"{dst} exists")
    shutil.copytree(SKILL / "templates/bridge", dst)
    shutil.copy(SHORTS / name / "voice/words.json", dst / "words.json")
    print(f"""copied the final bridge source to {dst}
Now edit, in this order (pipeline step 4-7; each file has one job):
  story.ts   SHOTS/XFADE/FLASH_AT/CAMS/KICKS/DOF/FOREGROUND timed to words.json (reaction lands 0-3 frames BEFORE its word)
  build.ts   town/props for YOUR story    cast.ts / toon.ts   YOUR characters (never the reference's)
  lights.ts  day / golden presets         Bridge.tsx          composer order: ink -> lens pre -> lens main -> bloom -> NEUTRAL -> grade
Register the composition next to BridgeShort in src/Root.tsx and rename it (id used below as COMP_ID).""")
    pass_gate(name, "scaffold")


def cmd_stills(a):
    name, frames = a[0], a[1]
    scale = a[2] if len(a) > 2 else "0.5"
    p = proj()
    out = p / "out" / name
    out.mkdir(parents=True, exist_ok=True)
    sh(["node", "scripts/bridge-stills.mjs", f"out/{name}/x_", frames, scale], cwd=p,
       env={"REMOTION_TMP": tmpdir(), "COMP_ID": name})


def cmd_sheets(a):
    p = proj()
    sh([sys.executable, "scripts/sbs_sheet.py", *a[1:]] if a[0].startswith("--") else [sys.executable, "scripts/sbs_sheet.py", *a], cwd=p)


def cmd_sound(a):
    name = a[0]
    d = SHORTS / name / "audio"
    for f in (SKILL / "templates/audio").iterdir():
        if not (d / f.name).exists():
            shutil.copy(f, d / f.name)
    print(f"""audio templates copied to {d}.
1) lock the picture's time constants FIRST (any later timing change means re-running sound)
2) edit timeline.py (event table from words.json + story.ts), then:  python sfx_gen.py && python music.py && python mix.py
   -> mix.wav (48 kHz, exact length), stems, cues.md.   Mix: music +3 dB, SFX -6 dB, voice unchanged, ducked under voice.""")


def cmd_render(a):
    name = a[0]
    need_gate(name, "scaffold")
    p = proj()
    out = p / "out" / name
    out.mkdir(parents=True, exist_ok=True)
    env = {"TEMP": tmpdir(), "TMP": tmpdir()}
    sh(["npx", "remotion", "render", "src/index.ts", name, f"out/{name}/video.mp4", "--codec", "h264", "--crf", "16", "--scale", "1.3333"], cwd=p, env=env)
    mix = SHORTS / name / "audio/mix.wav"
    final = out / "final.mp4"
    if mix.exists():
        # Remotion writes a silent audio track: take video from 0, audio from our mix
        sh(["ffmpeg", "-y", "-i", out / "video.mp4", "-i", mix, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", final])
    else:
        print("no audio/mix.wav yet; run `sound` first. Silent video at", out / "video.mp4")
    pass_gate(name, "render")


def cmd_qa(a):
    name = a[0]
    need_gate(name, "render")
    p = proj()
    shots = SHORTS / name / "shots.json"
    sh([sys.executable, "scripts/short_qa.py", f"out/{name}/final.mp4", f"out/{name}/qa", *( [shots] if shots.exists() else [])], cwd=p)


def cmd_blender_init(a):
    if not BLENDER_SKILLS.exists():
        sys.exit("Clone https://github.com/mromidev/claude-blender-skills into ~/.claude/skills/claude-blender-skills first.")
    (ROOT / "blender").mkdir(exist_ok=True)
    for sk in BLENDER_SKILLS.glob("skills/*"):
        link = ROOT / "blender" / sk.name
        if not link.exists():
            link.symlink_to(sk)
    print("linked:", ", ".join(p.name for p in (ROOT / "blender").iterdir()))
    print("Use blender-film for realistic cinematic shots (storyboard -> physics path -> night lighting -> sound from motion -> overnight render -> clay build-up).")
    print("Needs Blender 4.4+ with a GPU, ffmpeg, numpy/scipy. Not available in the cloud sandbox: run on your own PC.")


CMDS = {"setup": cmd_setup, "new": cmd_new, "lint": cmd_lint, "voice": cmd_voice, "scaffold": cmd_scaffold, "stills": cmd_stills,
        "sheets": cmd_sheets, "sound": cmd_sound, "render": cmd_render, "qa": cmd_qa, "blender-init": cmd_blender_init}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(2)
    CMDS[sys.argv[1]](sys.argv[2:])

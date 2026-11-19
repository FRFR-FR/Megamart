# shorts-factory

A gated pipeline around the free `mromidev/claude-animated-shorts` skill (installed at `~/.claude/skills/cartoon-3d-short/`)
for mass-producing 55-70 s vertical cartoon-3D story shorts (three.js + Remotion), with the Blender realistic branch from
`mromidev/claude-blender-skills` linked in.

    python factory.py setup ~/shorts-project      # npm install, copy QA/stills scripts (patched for Linux + any composition id)
    python factory.py new bridge2 --topic "..."   # shorts/bridge2/ with the script skeleton
    python factory.py lint bridge2                # GATE 1 script formula (tools/lint_script.py)
    python factory.py voice bridge2               # GATE 2 words.json + speed/start/pause checks (tools/check_timings.py)
    python factory.py scaffold bridge2            # copy the proven source into src/videos/bridge2
    python factory.py stills bridge2 100,400      # look checks, then sheets against references/frames
    python factory.py sound bridge2               # audio templates -> mix.wav
    python factory.py render bridge2              # 2K render + mux
    python factory.py qa bridge2                  # frame-by-frame QA

Each stage refuses to run until the previous gate passed. All rules are in `docs/RULES.md`.

Verified here: linter (passes the proven bridge script, fails a bad one), gates, `setup` (npm install), and `tsc --noEmit` on
the template source. Not verified here: rendering (needs a GPU/Chrome with WebGL, Kenney GLB assets, `src/index.ts` + `Root.tsx`,
voice audio) and Blender (not installed in the sandbox).

## Chat mode (new)
`render/` is a standalone three.js renderer (no Remotion, no Kenney assets, no GPU): `cd render && npm i && node render.mjs story.example.json out.mp4`.
See docs/CHAT_MODE.md for the cheap in-chat workflow and the known gaps against the reference look.

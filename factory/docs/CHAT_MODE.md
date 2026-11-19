# Running the whole factory inside chat (no PC, no Remotion, no downloads)

Measured in the sandbox: software WebGL2 works; the standalone renderer does ~0.17 s/frame at 540x960
(67 s short = ~2000 frames = ~6 min). 2 CPU cores, 7 GB RAM. Hugging Face is blocked; npm, pip and GitHub work.

Cheap order of operations (each step is one tool call, so it costs as little chat as possible):
1. Write SCRIPT.md, then `python3 tools/lint_script.py SCRIPT.md`            (seconds)
2. Voice: user records/uploads voice.wav + words.json (no TTS model is downloadable here; try a GitHub-hosted
   kokoro-onnx model if you want synthetic voice), then `python3 tools/check_timings.py words.json`
3. Write story.json (world, actors, shots, kicks) timed to words.json: reaction lands 0-3 frames BEFORE its word.
4. Look check, cheap: `cd render && node render.mjs story.json /tmp/t.mp4 --from 10 --to 12` then view a still.
5. Final: `node render.mjs story.json out.mp4 --w 1080 --h 1920 --audio mix.wav` (4x pixels; expect ~25 min,
   or render 540x960 and upscale: `ffmpeg -i out.mp4 -vf scale=1440:2560:flags=lanczos`).

Credit-saving rules: render stills at small sizes and look at 2-3 frames per check, never whole videos in context;
batch edits; keep every check to one command; do not re-read files already in context.

Rig + physics (render/index.html):
- Characters are articulated rigs: pelvis, bean torso, head with blink decal, hat, two-bone arms (shoulder+elbow, ink-dot hands),
  two-bone legs solved with IK against planted feet (stride locked to distance travelled, so no foot sliding), torso lean into speed,
  turn-around squash when direction flips.
- Physics is cannon-es at a fixed 1/240 s: every prop's collider is built from the same numbers as its mesh (houses, trunks, deck,
  ramps, parapets, crates, balls); characters are 3-sphere capsules that steer along their keyed path, so blocked paths lag instead of
  passing through. Crates and balls are dynamic and get shoved/tipped.
- Built-in audit printed after every render: `PHYSICS AUDIT` with an independent geometric overlap check (visiblePenCm), solver contact
  depth, falls through floor, and camInside (camera inside a solid prop). Use `--nophys 1` for a negative control.
- Limits: collision is per body capsule and per prop, NOT per limb (an arm can still poke into a crate or rail); the camera is only
  audited, not auto-avoided; characters are not yet colliding with the river (it is a visual plane).

Known gaps vs the reference look (see docs/RULES.md section 5): no lens blur or bloom pass yet, procedural
props instead of Kenney assets, no synthesized SFX/music, no voice.

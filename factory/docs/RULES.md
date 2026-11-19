# The laws of the workflow (from the Mr omi video, the cartoon-3d-short skill and its style reports)

Source of truth: `~/.claude/skills/cartoon-3d-short/` (SKILL.md, references/STYLE_BIBLE.md, references/reports/*.md).
This file is the checklist form. `tools/lint_script.py` and `tools/check_timings.py` enforce the measurable ones.

## 0. Ground rules
1. No AI video generator. Everything is rendered in code: three.js inside Remotion (@remotion/three).
2. Story, characters and voice are ALWAYS our own. The reference shorts are study material for the look only:
   never copy their scripts, characters or shots, never upload/publish them, never name their channel in voice-over or description.
3. No captions or labels in the video. English only. One steady voice tone.
4. Jokes are researched real facts. Every fact has a source at the top of SCRIPT.md.
5. Save after every step. "Just do it" once the script is approved.
6. Standard mix: music +3 dB, SFX -6 dB, voice unchanged. Final export 2K vertical 1440x2560 (`--scale 1.3333`), 30 fps.

## 1. Format (measured on 20 shorts, 32,000+ frames at 30 fps)
Vertical 1080x1920, 55-70 s for us, voice starts at frame 1-4, no intro, logo, outro or CTA.
Narrator 3.5-4.1 words/s (median 3.7), gaps >0.25 s total under 1 s. About -14 LUFS, heavily compressed.

## 2. Script formula (gate 1: `factory.py lint`)
1. Topic: one surprising TRUE story with a physical cause and effect, plus an everyday analogy that explains it.
2. Hook: the absurd fact as one plain sentence (8-16 words), no setup.
3. Setting: 1-2 lines, present tense, year/place/named everyman/number.
4. Escalation: 3-6 beats, each a little bigger; doubt or mockery in short dialogue; 1-2 exaggeration jokes.
5. Mystery beat: a question or "Wait, ...?" (about one per video).
6. Snap: the moment it breaks. Optional deadpan double line ("Luckily ... / Unluckily ...").
7. Pivot "You see," exactly once, then the real mechanism via an everyday analogy ("Ever ...?").
8. Consequence (the rule it created), then callback twist: short, ironic, the video ends on its last word.
9. Never describe on screen what the viewer already sees. Plain spoken English, ~13.5 words per sentence, contractions.

## 3. Voice (gate 2: `factory.py voice`)
Record/generate voice.wav, produce words.json (speech-to-text with word times), hand-fix the timings.
Everything is timed to words.json. Every visual reaction lands 0-3 frames BEFORE its word.

## 4. Shot plan (`story.ts`)
SHOTS (id, a/b frames, light day|golden, crowd mode, tau), XFADE (6-8 frame dissolves at place/time changes),
FLASH_AT (white flash after the hook), CAMS (per shot keys {f, dur?, cut?, s}), KICKS (impact flip-shakes),
DOF/dofAt (lens blur per beat), FOREGROUND (near framing props in ~1/3 of shots).

## 5. Look targets (numbers, not adjectives)
- Camera: hard cuts only on big jumps; everything else a smootherstep glide of 18-40 f (peak <= 25 px/f at 720p).
  Every hold creeps in 0.15-0.35 %/f (0.6 %/f on punch words); no static hold >= 4 f (QA flags frozen spans >= 12 f).
  Rolls 4-5 degrees; no hand-held float; impact shakes flip sign every frame and decay over 7 f.
- Ink: world lines about 3 px at 1080 (bridge final: 5.1 px near -> 3.3 px far), #030303-#0b0a0c, silhouettes + depth jumps
  + normal creases only; no line on wall/floor joins or horizon. Character cards carry their own plum ink (#201628-#2f1d28,
  thicker on the shadow side) and sit on the NOINK layer.
- Colour: day median luma ~.57, non-ink p5 ~.23 (no crushed blacks), lit chroma C* p90 ~55; day sky top ~#5e93d9, horizon 1.28x
  brighter; golden = peach horizon #ffd08a, violet-blue shadows (never brown), backlit sun. Fog = horizon colour.
  Never lemon, never lavender lit faces. Cool tint ONLY in shade. Film grain OFF (reference has none, file size x4).
- Depth: lens blur on ~1/3 of screen time (CU, MS, inserts), cInf 10-16 px at 1080, focus on the eyes; wides stay sharp.
  Bloom only on HDR emissives, threshold 1.0.
- Characters: flat bean-head cards (h/w ~.93), ~3.5 head-heights, stick limbs ~.055 head width, ink-dot hands, no blush,
  no eye highlights, faces ~.93 brightness, walk bob 3-7 %, lean 1-7 deg, planted feet, blinks every 0.5-2.3 s for 4 f.
  Cards are lit by the scene (no emissive), cast contact shadows.
- Composer order: ink -> lens pre -> lens main -> bloom -> NEUTRAL tone map -> grade, MSAA 4. Every pixel parameter scales
  with output height / 1920.

## 6. Sound
Synthesized SFX + an original score ducked under the voice: event table -> mix.wav (48 kHz, exact length), stems, cues.md.
Lock the picture's time constants BEFORE making sound; any later timing change means re-running it.

## 7. Look-match loop (use for any "make it look like X")
1. Measure the reference first: one analysis agent per topic (motion, depth, textures, characters, lighting, outlines, grade),
   each writing NUMBERS to references/reports/<topic>.md.
2. Sandboxes, one owner per file: cam=story.ts; world=world.ts,lights.ts,shade.ts,grade.ts; mat=paint.ts,build.ts;
   char=toon.ts,cast.ts,cardshade.ts; post=ink.ts,Bridge.tsx,lensblur.ts.
3. Merge with bridge_merge.py, `tsc --noEmit`, re-sync every sandbox from main.
4. Verify with a fresh verifier agent: side-by-side sheets, score each area /10, numbered fix list with frame numbers;
   send each fix to its file owner. Contracts live in exported constants (NOINK, dofAt, FOREGROUND, LIGHTS/LOOK).

## 8. Final render and QA
`npx remotion render ... --codec h264 --crf 16 --scale 1.3333`, mux with `-map 0:v:0 -map 1:a:0` (Remotion's audio is silent).
`short_qa.py` checks every frame for black/white/frozen/pop frames, loudness and contact sheets. Fix, then a deep audit.

## 9. Gotchas that cost the author hours
- Disk: every Remotion bundle copies public/ (~1.3 GB) into the temp dir and never deletes it. Always set REMOTION_TMP/TEMP/TMP
  to a big drive; ask before deleting old bundles.
- Ink in the same pass as DOF gets overwritten: ink is its own pass before the blur.
- Kenney nature-kit materials are teal: recolour by material name. Cameras end up inside houses: sight-line culling.
- Readability traps: a swing drawn as one rope reads as a hanging (two ropes); props <2 m from a lens become blobs;
  period-correct flags; painted signs need unlit faces; golden rim = inner only; rails at chest height through characters.
- Sub-agents can't write report files in some harnesses: ask for a <=150-word final message and save it yourself.
- 2K renders run ~4 fps (~10 min for 67 s). Stills at 0.5 take 3-8 s after a ~40 s bundle.

## 10. Realistic branch (Blender, own PC)
`claude-blender-skills/skills/blender-film`: storyboard first -> city layout -> physics-driven path -> pivot the hero if it looks
wrong -> realism pass -> night lighting from practical lights -> operator-style camera -> sound designed from motion data ->
safe overnight render (test stills first, absolute paths, resumable) -> clay build-up reveal.

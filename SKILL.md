---
name: cartoon-short-factory
description: Make vertical 30-70 s cartoon-3D story shorts end to end (script, British voice, rigged characters, UK or any world, physics, sound, render, QA) in the "2D-style characters in a colourful inked 3D world" look. Use for "make a short/animation like the bridge video", history/science/cybersecurity story shorts, or any request to reuse the character, prop and place library.
---

# Cartoon short factory

One skill with everything: the style rules (from the free `mromidev/claude-animated-shorts` skill), a chat-friendly renderer that needs no GPU, a rigged character kit, a prop/building library, a script linter, voice and sound tools, and three finished example videos.

```
SKILL.md                this file
factory/                the toolkit (copy it to a working folder, see Setup)
  render/               standalone three.js + cannon-es renderer (headless Chrome, SwiftShader) -> ffmpeg
    index.html          scene, rig posing, IK, physics, cameras, builders
    lib/characters.js   character kit: build(def) -> rig
    lib/props.js        ~65 props, vehicles, animals, buildings, interiors, Pisa landmarks
    render.mjs          story.json -> mp4 (+ PHYSICS AUDIT)
  library/cast.py       25 named character presets + crowd generators
  tools/                lint_script.py, tts_lines.py, check_timings.py, sound_*.py, make_story_*.py (examples)
  docs/                 RULES.md (checklist form of the laws), CHAT_MODE.md
  factory.py            gated orchestrator for the original Remotion route
references/             STYLE_BIBLE.md, reports/ (measured numbers), frames/, sheets/ (reference look), ORIGINAL_REMOTION_SKILL.md
templates/              original Remotion bridge source (the high-end route)
examples/               SCRIPT.md + story.json for: millennium (Millennium Bridge), queue (original fiction), pisa (Leaning Tower)
```

## Two routes
1. **Chat route (default, free, ~3-5 min per 30 s video at 540x960).** `factory/render`. Everything below.
2. **Remotion route (2K, bloom, lens blur, Kenney assets).** `templates/bridge/` + `references/ORIGINAL_REMOTION_SKILL.md`. Needs a PC with a GPU. Use only when the user asks for top quality and has the machine.

## Ground rules (from the reference workflow; keep them)
- No AI video generator: everything is code-rendered. Story, characters and voice are always our own; the reference channel is study material only (never copy its scripts/characters/shots, never name it in a voice-over or description).
- No captions or labels in the video, except what the user explicitly asks for (a Like/Subscribe or book call-to-action). Pass `--allow-cta` to the linter in that case.
- Facts are real and sourced: put them with a source in parentheses at the top of SCRIPT.md. Verify on Wikipedia/primary pages, not from memory.
- One steady narrator, English. Narration starts within frames 1-4. No intro, logo or outro unless asked.
- Save after every step. Once the script is approved, just do it.

## Setup (once per session)
```bash
cp -r factory ~/shorts-factory && cd ~/shorts-factory/render && npm i      # playwright-core, three, cannon-es
pip install --break-system-packages kokoro-onnx soundfile numpy              # voice + sound
# voice model (Hugging Face may be blocked; use GitHub release files)
#   kokoro-v1.0.onnx and voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases -> shorts/<name>/voice/
```
Chrome/Chromium must exist at /usr/bin/google-chrome or /usr/bin/chromium; no GPU needed. ffmpeg required.

## Pipeline (each step = one command; check stills, never watch whole videos in context)
1. **Topic + facts.** One surprising TRUE story with a visible physical cause and effect and an everyday analogy. Good picks: engineering failures, odd history, "how did that even happen" hacks.
2. **Script** in `shorts/<name>/SCRIPT.md` (header block with `Facts: ... (source)`, blank line, one spoken line per row). Formula:
   hook 8-16 words stated as fact -> setting with numbers -> 3-6 escalating beats -> `Wait, ...?` mystery -> exactly one `You see,` pivot -> `Ever ...?` everyday analogy -> consequence -> short ironic callback. ~3.7 words/s. 30 s short = ~105-115 words.
   `python tools/lint_script.py shorts/<name>/SCRIPT.md --dur 25-35 [--allow-cta]`
3. **Voice.** `python tools/tts_lines.py SCRIPT.md voice --speed 1.35` (British `bm_george`, per-line synthesis gives exact line timings in `voice/lines.json`, plus `words.json`). Kokoro speed is non-linear: try 1.3 / 1.35 / 1.4 and keep the one that lands the target length.
4. **Story** `shorts/<name>/story.json` via a small Python generator (copy `tools/make_story_pisa.py`): world items, actors, shots, kicks. Cut times = midpoints between voice lines. A reaction lands 0-3 frames before its word.
5. **Look check.** `cd render && node render.mjs ../shorts/<name>/story.json ../shorts/<name>/out/still --stills 1.5,5,9,...` then montage 4-9 stills with ffmpeg hstack and look at one image. Fix cameras, then render.
6. **Sound.** Copy `tools/sound_pisa.py`; edit the SFX block (event times from the story) -> `audio_mix.wav` (voice + ducked music + SFX).
7. **Render in two halves in parallel** (2 cores):
   `node render.mjs story.json out/p1.mp4 --from 0 --to 15 &` and `--from 15 --to 30`, then
   `ffmpeg -f concat -i list.txt -i audio_mix.wav -c:v copy -c:a aac -b:a 256k -shortest final.mp4`
8. **QA.** Read the `PHYSICS AUDIT` line in each log (want over2cm 0 or tiny, fell 0, camInside 0, actorOverlap 0, visiblePenCm < 1). Decode at 270x480 gray and check: no black (<8), no white (>247), no frozen runs, jumps only at cuts. View 5-10 frames.
9. **Deliver** with SendUserFile (display render), one-paragraph summary with honest limits.

## story.json reference
```
{ duration, world:[items], actors:[defs], shots:[...], kicks:[{t,amp}], sway:[{t,a}], swayMax, dampersAt }
```
- Ground top is y = .8 (`land`). Give every actor `y0: .85` or it spawns inside the ground (buried, invisible).
- **Any world item** may carry `at` / `until` (seconds) to appear/disappear (eras, time-lapse). Dynamic items (`crate`, `ball`) with `at` spawn then.
- **Actor** = character def (below) + `keys:[{t,x,z}]` (+ `lin:true` for straight lerp), optional `show:[t0,t1]` (visible window; hidden actors still collide, so park them away from live paths), `emote:[{t,e}]`, `armsUp:[{t,v}]` with `armSide` (0/1, omit = both) and `armAngle`, `noWalk`.
- **Shot** = `{a, b, light:'day'|'golden', from:[x,y,z], to:[...], look:[...]|lookActor:i, lookOff:[...], followActor:i, fov, roll}`. Cameras glide smootherstep from->to over the shot. Roll 2-4 deg alternating sign. Keep cameras >=5 m from foreground actors/props (anything nearer becomes a huge blob), never inside a prop, and check lamp posts/bins near lenses.
- Hero ideas that work: a looping pacing crowd that stays in frame (`circuit()` in make_story_pisa.py), a stack of crates dropping on a sofa, a tower that grows floor by floor, a tourist pretending to hold a tower.

## Character kit (`render/lib/characters.js`, presets in `library/cast.py`)
`cast('derek', hat='#335', skin='#f6d9c6', keys=[...])` returns an actor dict. Fields:
`skin eye build(slim|normal|stocky) hair hairStyle(short quiff long bob ponytail bun curly wisp bald fringe pigtails) beard(none moustache beard stubble) glasses lashes blush hat hatStyle(flatcap bowler tophat bobby hardhat beanie bobble baseball sunhat chef beret crown bonnet tricorn) outfit(tee jumper jacket suit hivis dress coat apron robe hoodie blazer) shirt accent pants shoe shoeStyle(shoe boot trainer) legs(long shorts skirt) sleeves scarf tie backpack chain badge belt stripes collar face(happy neutral worried surprised sad smug angry talk) s headScale`.
Presets: derek nan granddad bobby vicar mayor postie builder engineer baker schoolkid toddler teen office_woman scientist tourist tourist_f peasant mason foreman soldier king victorian_gent victorian_lady sailor. `crowd(n, seed, kind)` kinds: everyday tourists workers medieval. Skin defaults to pale; pass any hex (`SKINS` has a spread). Characters are ~3 units tall; a bus is 6.4 long.
Rig: bean torso, head with face decal (emotes + blink), two-bone arms, IK legs with stride locked to distance, lean, turn squash, spread/arms-up poses. Collision is a 3-sphere capsule per actor (not per limb).

## Props / world builders (`type` values)
Core (index.html): `land pave riverx terrace stpauls tate phonebox pillarbox lamp flag cloud bus box crate ball swayBridge tree road house`.
Library (props.js; params `x z y rot s color col`; `col:false` disables the collider, `col:[w,h,d]` overrides it; animals/vehicles take `keys` to move and face their direction):
- Street: bench bin bollard hydrant cone barrier signpost trafficlight busstop sandwichboard bunting balloons fountain statue streetlamp_victorian bike
- Vehicles (face +x): car taxi van tractor traincar boat
- Nature/animals: oak pine cypress bush flowers rock haystack hay_ball hedge fence stonewall hill pond sheep cow dog cat duck chicken
- Buildings: cottage shop pub church clocktower windmill lighthouse station castle tower_block barn shed school stall duomo baptistery pisa(`appear:[t...] lean:[{t,a}] bend`)
- Interior: room table chair sofa bed tv shelf rug mug teapot cake crate_box suitcase lamp_table
Only the ones used in the example videos are visually proven; render a quick still before relying on any other.
Places (recipes, built from the above): UK high street = `land` + `pave` strips + two `terrace` rows + lamps/pillarbox/phonebox/bus; village green = green + pub + church + cottages + oak + bench; countryside = hills + sheep + fences + barn + windmill; Pisa piazza = lawn + `pisa` + `duomo` + `baptistery` + cypress.

## Physics and honesty
cannon-es at 1/240 s; colliders use the same numbers as meshes; actors steer by P-controller so blocked paths lag instead of passing through. `PHYSICS AUDIT` prints penetration, falls and camera-inside checks. Say plainly what is not covered: per-limb collisions, low resolution (540x960; upscale with lanczos if asked), no lens blur/bloom, word timings estimated, tower lean angles exaggerated for readability.

## Call-to-action videos (user-requested)
The reference format has no CTA; when the user asks for "Like and subscribe" or a book/product plug, put the like/subscribe line near the middle (after the `Wait,` question works well, it adds tension) and the plug at the end; lint with `--allow-cta`; show the user's own cover image as a texture on a 3D prop (copy the image into `render/assets/`, load with `THREE.TextureLoader`, serve through `render.mjs`).

## Gotchas learned the hard way
- `lint`/`voice` must exit non-zero on failure; check exit codes in scripts.
- A Python patch with several `assert`s aborts on the first failure and applies nothing: grep exact text first.
- ExtrudeGeometry torso had no front face: use a flattened sphere.
- Ink hull thickness in world units per axis; a camera inside a tree/lamp hides the shot (audit `camInside`).
- Hugging Face is blocked in the sandbox; GitHub releases, npm and pip work. espeak is not installable: use kokoro-onnx.
- YouTube is unreachable: you cannot download or watch the reference channel; rely on references/.
- Sound scripts: guard `put()` against writing past the buffer end.
- Free plan: no browser/computer control, no scheduled tasks.

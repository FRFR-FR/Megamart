// Character kit: builds one articulated cartoon person from a plain JSON definition.
// Same rig contract as before (root/flip/pelvis/torso/head/face, arm[{sh,up,fo}], leg[{hip,th,sn}], shoe = sn.children[1]) so walk/IK/pose code is unchanged.
//
// def fields (all optional):
//   skin, eye                       colours
//   build      'slim'|'normal'|'stocky'
//   hair       colour;  hairStyle 'short'|'quiff'|'long'|'bob'|'ponytail'|'bun'|'curly'|'wisp'|'bald'|'fringe'|'pigtails'
//   beard      'none'|'moustache'|'beard'|'stubble'   (uses hair colour unless beardColor)
//   glasses    colour or false;   lashes true;   blush true
//   hat        colour;  hatStyle 'flatcap'|'bowler'|'tophat'|'bobby'|'hardhat'|'beanie'|'bobble'|'baseball'|'sunhat'|'chef'|'beret'|'crown'|'bonnet'|'tricorn'
//   outfit     'tee'|'jumper'|'jacket'|'suit'|'hivis'|'dress'|'coat'|'apron'|'robe'|'hoodie'|'blazer'
//   shirt (main colour), accent (2nd colour: jacket/coat/apron/tie/trim), pants, shoe, shoeStyle 'shoe'|'boot'|'trainer'
//   legs       'long'|'shorts'|'skirt';   sleeves 'long'|'short'
//   scarf, tie, backpack, chain (colours / true), badge
//   face       default emotion 'happy'|'neutral'|'worried'|'surprised'|'sad'|'smug'|'angry'|'talk'
//   s          overall scale (1 = adult, .75 child, .55 toddler);  headScale
export function makeKit({ THREE, mat, inked, PLUM }) {
  const SP = new THREE.SphereGeometry(1, 28, 20);
  const CYL = new THREE.CylinderGeometry(1, 1, 1, 24);
  const HEMI = new THREE.SphereGeometry(1, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2);
  const ell = (g, c, sx, sy, sz, x, y, z, o = {}) => {
    const m = new THREE.Mesh(o.geo || SP, mat(c)); m.scale.set(sx, sy, sz); m.position.set(x, y, z); if (o.rot) m.rotation.set(...o.rot);
    m.castShadow = true; if (o.ink !== 0) inked(m, o.ink ?? .045); g.add(m); return m; };
  const BODY = { slim: { tw: .3, tz: .12, lr: .085 }, normal: { tw: .33, tz: .13, lr: .095 }, stocky: { tw: .4, tz: .16, lr: .11 } };

  /* ---------- faces ---------- */
  const faceCache = {};
  function faceTex(emo, blink, def) {
    const key = [emo, blink, def.eye || '', !!def.lashes, def.blush !== false, def.glasses ? 1 : 0].join('|'); if (faceCache[key]) return faceCache[key];
    const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'); g.lineCap = g.lineJoin = 'round'; const ink = PLUM, ex = [80, 176], ey = emo === 'surprised' ? 112 : 120;
    const E = { happy: [1, 1], neutral: [1, 1], worried: [1, 1], surprised: [1.25, 1.25], sad: [1, .95], smug: [1, .55], angry: [1, .85], talk: [1, 1] }[emo] || [1, 1];
    if (def.blush !== false && emo !== 'angry') { g.fillStyle = 'rgba(240,120,120,.32)'; [[60, 164], [196, 164]].forEach(([x, y]) => { g.beginPath(); g.ellipse(x, y, 16, 10, 0, 0, 6.3); g.fill(); }); }
    ex.forEach((x, i) => {
      if (blink) { g.strokeStyle = ink; g.lineWidth = 7; g.beginPath(); g.arc(x, ey - 6, 20, .15 * Math.PI, .85 * Math.PI); g.stroke(); }
      else {
        g.fillStyle = '#fff'; g.strokeStyle = ink; g.lineWidth = 5; g.beginPath(); g.ellipse(x, ey, 25 * E[0], 31 * E[1], 0, 0, 6.3); g.fill(); g.stroke();
        const px = x + (i ? -3 : 3) * (emo === 'worried' ? 1.6 : 1), py = ey + (emo === 'sad' ? 6 : emo === 'smug' ? 2 : 2);
        g.fillStyle = def.eye || ink; g.beginPath(); g.ellipse(px, py, 14 * E[0], 19 * E[1], 0, 0, 6.3); g.fill(); g.fillStyle = ink; g.beginPath(); g.ellipse(px, py + 1, 8.5, 12.5, 0, 0, 6.3); g.fill();
        g.fillStyle = '#fff'; g.beginPath(); g.arc(px - 5, py - 8, 5, 0, 6.3); g.fill();
        if (emo === 'smug') { g.fillStyle = '#f1c9ad'; g.fillStyle = def.skinLid || '#e9b89a'; g.beginPath(); g.rect(x - 22, ey - 28, 44, 28); g.fill(); g.strokeStyle = ink; g.lineWidth = 6; g.beginPath(); g.moveTo(x - 20, ey - 1); g.lineTo(x + 20, ey - 1); g.stroke(); }
      }
      if (def.lashes) { g.strokeStyle = ink; g.lineWidth = 4; for (let k = 0; k < 3; k++) { const a = (i ? -1 : 1) * (-.2 - k * .45) - Math.PI / 2 - (i ? 0 : 0); g.beginPath(); g.moveTo(x + (i ? 1 : -1) * 15 + Math.cos(a) * 10 * 0, ey - 18 + k * 4); g.lineTo(x + (i ? 1 : -1) * (22 + k * 3), ey - 24 + k * 5); g.stroke(); } }
      g.strokeStyle = ink; g.lineWidth = 9; g.beginPath();                                                              // brows
      const bx = x, by = ey - 50, s = i ? -1 : 1;
      if (emo === 'worried' || emo === 'sad') { g.moveTo(bx - 18 * s, by + 4); g.lineTo(bx + 14 * s, by - 8); }
      else if (emo === 'angry') { g.moveTo(bx - 18 * s, by - 8); g.lineTo(bx + 16 * s, by + 8); }
      else if (emo === 'surprised') { g.arc(bx, by - 14, 18, 1.15 * Math.PI, 1.85 * Math.PI); }
      else if (emo === 'smug') { g.moveTo(bx - 18, by + (i ? 4 : -3)); g.quadraticCurveTo(bx, by - 8 + (i ? 4 : -3), bx + 18, by + (i ? 4 : -3)); }
      else { g.arc(bx, by + 20, 20, 1.2 * Math.PI, 1.8 * Math.PI); }
      g.stroke(); });
    if (def.glasses) { g.strokeStyle = typeof def.glasses === 'string' ? def.glasses : '#2a2430'; g.lineWidth = 7; ex.forEach(x => { g.beginPath(); g.ellipse(x, ey, 37, 37, 0, 0, 6.3); g.stroke(); }); g.beginPath(); g.moveTo(ex[0] + 37, ey - 4); g.lineTo(ex[1] - 37, ey - 4); g.stroke(); }
    g.strokeStyle = 'rgba(70,35,25,.55)'; g.lineWidth = 5; g.beginPath(); g.moveTo(128, 138); g.quadraticCurveTo(138, 150, 126, 154); g.stroke();   // nose hint
    g.strokeStyle = ink; g.fillStyle = ink; g.lineWidth = 8; g.beginPath();
    if (emo === 'talk') { g.ellipse(128, 194, 28, 20, 0, 0, 6.3); g.fill(); g.fillStyle = '#e8727a'; g.beginPath(); g.ellipse(128, 205, 13, 7, 0, 0, 6.3); g.fill(); }
    else if (emo === 'surprised') { g.ellipse(128, 198, 13, 18, 0, 0, 6.3); g.fill(); }
    else if (emo === 'worried') { g.moveTo(104, 198); g.quadraticCurveTo(116, 188, 128, 198); g.quadraticCurveTo(140, 208, 152, 198); g.stroke(); }
    else if (emo === 'sad') { g.arc(128, 214, 24, 1.2 * Math.PI, 1.8 * Math.PI); g.stroke(); }
    else if (emo === 'angry') { g.moveTo(106, 202); g.lineTo(150, 198); g.stroke(); }
    else if (emo === 'smug') { g.moveTo(104, 196); g.quadraticCurveTo(132, 208, 156, 186); g.stroke(); }
    else if (emo === 'neutral') { g.moveTo(108, 198); g.lineTo(148, 198); g.stroke(); }
    else { g.arc(128, 176, 36, .16 * Math.PI, .84 * Math.PI); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return faceCache[key] = t; }

  /* ---------- pieces ---------- */
  function limb(len, rad, color, zs = .6) { const pv = new THREE.Group(); const m = new THREE.Mesh(new THREE.CapsuleGeometry(rad, Math.max(.01, len - 2 * rad), 6, 12), mat(color));
    m.position.y = -len / 2; m.scale.z = zs; m.castShadow = true; inked(m, .045); pv.add(m); return pv; }
  const LEN = { thigh: .68, shin: .68, upper: .52, fore: .5 };

  function hairBuild(h, st, col, headScale, hat) {
    const shell = (sx = .5, sy = .53, sz = .19, y = .38, th = 1.22) => { if (hat) return null; const m = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 14, 0, 6.2832, 0, th), mat(col)); m.scale.set(sx, sy, sz); m.position.set(0, y, 0); m.castShadow = true; inked(m, .05); h.add(m); return m; };
    const fringe = (y = .66) => hat ? null : ell(h, col, .4, .11, .17, .02, y, .05, { rot: [.25, 0, -.12], ink: .035 });
    const side = () => [-1, 1].forEach(s => ell(h, col, .06, .15, .12, s * .455, .52, -.02, { ink: .03 }));
    if (st === 'bald') return;
    if (st === 'short') { shell(); side(); fringe(.7); }
    else if (st === 'fringe') { shell(.51, .54, .2, .38, 1.25); fringe(.68); ell(h, col, .22, .08, .15, -.2, .67, .08, { rot: [.3, 0, .4], ink: .03 }); side(); }
    else if (st === 'quiff') { shell(); side(); if (!hat) ell(h, col, .3, .17, .17, .03, .88, .06, { rot: [-.2, 0, -.15] }); }
    else if (st === 'long') { shell(.52, .54, .2, .38, 1.3); ell(h, col, .52, .72, .11, 0, .0, -.1); [-1, 1].forEach(s => ell(h, col, .09, .42, .14, s * .45, .18, -.02, { ink: .03 })); fringe(.69); }
    else if (st === 'bob') { shell(.52, .54, .2, .38, 1.3); ell(h, col, .54, .45, .12, 0, .22, -.08); [-1, 1].forEach(s => ell(h, col, .1, .3, .15, s * .46, .24, .0, { ink: .03 })); fringe(.69); }
    else if (st === 'ponytail') { shell(.51, .54, .2, .38, 1.25); side(); fringe(.7); ell(h, col, .1, .1, .09, 0, .62, -.2, { ink: .03 }); ell(h, col, .13, .36, .1, 0, .3, -.32, { rot: [.2, 0, 0] }); }
    else if (st === 'pigtails') { shell(.51, .54, .2, .38, 1.25); fringe(.7); [-1, 1].forEach(s => { ell(h, col, .08, .08, .08, s * .46, .5, -.04, { ink: .03 }); ell(h, col, .12, .32, .11, s * .55, .22, -.04, { rot: [0, 0, s * .15] }); }); }
    else if (st === 'bun') { shell(); side(); fringe(.7); if (!hat) ell(h, col, .2, .2, .17, 0, .98, -.04); }
    else if (st === 'curly') { shell(.5, .5, .19, .38, 1.1); if (!hat) for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ell(h, col, .16, .16, .14, Math.sin(a) * .42, .62 + Math.cos(a) * .12 + (i % 3) * .06, Math.cos(a) * .06, { ink: .03 }); } if (!hat) ell(h, col, .22, .2, .15, 0, .93, 0, { ink: .03 }); }
    else if (st === 'wisp') { shell(.5, .52, .19, .38, .9); [-1, 1].forEach(s => ell(h, col, .07, .16, .11, s * .45, .45, 0, { ink: .03 })); if (!hat) ell(h, col, .08, .06, .06, .1, .9, .1, { ink: .02 }); } }

  function hatBuild(h, st, col, def) {
    const dome = (sx, sy, sz, y, th = 1.5708) => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 14, 0, 6.2832, 0, th), mat(col)); m.scale.set(sx, sy, sz); m.position.set(0, y, 0); m.castShadow = true; inked(m, .05); h.add(m); return m; };
    const acc = def.accent || '#c9c9d0', tr = def.trim || '#ffffff';
    if (st === 'flatcap') { dome(.53, .24, .22, .6); ell(h, col, .33, .045, .17, .02, .62, .23, { rot: [.15, 0, 0] }); ell(h, col, .56, .05, .22, 0, .6, 0, { ink: .04 }); }
    else if (st === 'baseball') { dome(.5, .36, .2, .58); ell(h, col, .3, .04, .22, .05, .6, .3, { rot: [.1, 0, 0] }); }
    else if (st === 'bowler') { dome(.5, .46, .2, .6); ell(h, col, .64, .05, .26, 0, .6, 0); ell(h, acc, .5, .06, .2, 0, .64, 0, { ink: 0 }); }
    else if (st === 'tophat') { const c = new THREE.Mesh(CYL, mat(col)); c.scale.set(.33, .7, .15); c.position.set(0, 1.0, 0); c.castShadow = true; inked(c, .05); h.add(c); ell(h, col, .62, .05, .27, 0, .66, 0); ell(h, acc, .335, .09, .155, 0, .75, 0, { geo: CYL, ink: 0 }); }
    else if (st === 'bobby') { dome(.47, .62, .2, .56); ell(h, col, .52, .05, .22, 0, .58, .0); ell(h, col, .36, .05, .24, .02, .64, .2, { rot: [.2, 0, 0] }); ell(h, acc, .08, .08, .07, 0, 1.18, 0, { ink: .03 }); ell(h, acc, .09, .11, .03, 0, .9, .2, { ink: .03 }); ell(h, acc, .045, 0.5, .02, 0, 1.0, 0, { ink: 0 }); }
    else if (st === 'hardhat') { dome(.53, .38, .22, .58); ell(h, col, .6, .05, .25, 0, .58, .0); ell(h, col, .1, .06, .24, 0, .86, 0, { ink: .03 }); ell(h, col, .4, .06, .26, .02, .6, .13); }
    else if (st === 'beanie' || st === 'bobble') { dome(.5, .42, .2, .54); const cuff = ell(h, acc, .515, .09, .205, 0, .6, 0, { geo: CYL, ink: .04 }); if (st === 'bobble') ell(h, acc, .13, .13, .12, 0, 1.0, 0, { ink: .035 }); }
    else if (st === 'sunhat') { dome(.45, .3, .19, .64); ell(h, col, .95, .05, .55, 0, .64, 0, { ink: .05 }); ell(h, acc, .46, .06, .2, 0, .66, 0, { ink: 0, geo: CYL }); }
    else if (st === 'chef') { const c = new THREE.Mesh(CYL, mat(col)); c.scale.set(.42, .26, .17); c.position.set(0, .8, 0); inked(c, .045); h.add(c); ell(h, col, .52, .3, .21, 0, 1.12, 0); }
    else if (st === 'beret') { ell(h, col, .56, .15, .24, .06, .7, 0); ell(h, col, .05, .08, .05, .06, .88, 0, { ink: .02 }); }
    else if (st === 'tricorn') { dome(.5, .3, .2, .6); [0, 1, 2].forEach(i => { const a = i * Math.PI * 2 / 3 + Math.PI; ell(h, col, .36, .05, .22, Math.sin(a) * .36, .72, Math.cos(a) * .12, { rot: [0, a, .3], ink: .04 }); }); }
    else if (st === 'bonnet') { dome(.52, .4, .22, .52); ell(h, col, .56, .12, .26, 0, .5, .05); ell(h, acc, .1, .1, .1, .0, .84, .12, { ink: .02 }); }
    else if (st === 'crown') { const c = new THREE.Mesh(CYL, mat('#e5b93a')); c.scale.set(.4, .17, .17); c.position.set(0, .78, 0); inked(c, .045); h.add(c); for (let i = 0; i < 5; i++) { const a = (i - 2) * .55; const k = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 4), mat('#e5b93a')); k.scale.set(.07, .22, .07); k.position.set(Math.sin(a) * .4, .98, Math.cos(a) * .15 * Math.cos(a)); inked(k, .03); h.add(k); ell(h, '#d83a3a', .035, .035, .035, Math.sin(a) * .4, 1.12, Math.cos(a) * .12, { ink: 0 }); } } }

  /* ---------- the build ---------- */
  function build(def) {
    const B = BODY[def.build || 'normal']; const R = { root: new THREE.Group(), flip: new THREE.Group(), pelvis: new THREE.Group(), def }; R.root.add(R.flip); R.flip.add(R.pelvis);
    const skin = def.skin || '#f6d9c6', main = def.shirt || '#d9534f', acc = def.accent || '#2c3a55', pants = def.pants || '#3b3a5a', outfit = def.outfit || 'tee';
    const jacketLike = ['jacket', 'suit', 'blazer', 'coat', 'robe', 'hoodie'].includes(outfit); const sleeveCol = jacketLike || outfit === 'hivis' ? acc : main;
    const longSleeve = (def.sleeves || (['tee', 'dress', 'apron'].includes(outfit) ? 'short' : 'long')) === 'long';
    /* torso */
    R.torso = new THREE.Group(); R.pelvis.add(R.torso);
    const tw = B.tw, tz = B.tz, k = y => Math.sqrt(Math.max(0, 1 - ((y - .4) / .45) ** 2));
    const band = (g, y, h, col, grow = .012) => ell(g, col, tw * k(y) + grow, h / 2, tz * k(y) + grow, 0, y, 0, { ink: 0 });
    ell(R.torso, outfit === 'hivis' ? '#2c3a55' : (jacketLike ? main : main), tw, .45, tz, 0, .4, 0, { ink: .05 });
    if (jacketLike) { ell(R.torso, acc, tw * 1.045, .462, tz * 1.05, 0, .4, -.004, { ink: .05 }); if (outfit !== 'hoodie') ell(R.torso, main, .06, .28, tz * 1.1, 0, .44, .0, { ink: 0 });
      if (outfit !== 'hoodie') [-1, 1].forEach(s => ell(R.torso, acc, .075, .15, .03, s * .08, .69, tz * .86, { rot: [0, 0, s * .45], ink: .025 }));
      if (outfit === 'hoodie') { ell(R.torso, acc, tw * .9, .1, tz * 1.2, 0, .8, -.04, { ink: .04 }); ell(R.torso, '#00000022'.slice(0, 7) === '#000000' ? '#222' : '#e8e8ee', .015, .13, .015, .045, .55, tz * 1.1, { ink: 0 }); ell(R.torso, '#e8e8ee', .015, .13, .015, -.045, .55, tz * 1.1, { ink: 0 }); }
      if (outfit === 'robe') { band(R.torso, .05, .1, def.trim || '#f0ead8', .03); band(R.torso, .55, .1, def.trim || '#f0ead8', .03); } }
    if (outfit === 'hivis') { ell(R.torso, '#f2d21b', tw * 1.05, .452, tz * 1.06, 0, .4, 0, { ink: .05 }); ell(R.torso, '#2c3a55', .04, .3, tz * 1.12, 0, .4, 0, { ink: 0 }); band(R.torso, .3, .07, '#e4e6ea', .03); band(R.torso, .55, .07, '#e4e6ea', .03); }
    if (outfit === 'jumper') { band(R.torso, .0, .12, acc, .03); band(R.torso, .8, .09, acc, .03); if (def.stripes) for (let i = 0; i < 3; i++) band(R.torso, .25 + i * .2, .06, def.stripes, .014); }
    if (outfit === 'tee' && def.stripes) for (let i = 0; i < 4; i++) band(R.torso, .15 + i * .17, .07, def.stripes, .012);
    if (outfit === 'apron') { ell(R.torso, acc, tw * .8, .42, tz * 1.12, 0, .36, .005, { ink: .04 }); band(R.torso, .1, .05, acc, .02); }
    if (outfit === 'suit' || def.tie) { const tc = def.tie || '#b3262e'; ell(R.torso, tc, .045, .2, .02, 0, .56, tz * 1.1, { ink: .02 }); ell(R.torso, tc, .06, .06, .025, 0, .76, tz * 1.0, { ink: .02 }); }
    if (def.scarf) { band(R.torso, .82, .13, def.scarf, .04); ell(R.torso, def.scarf, .07, .22, .03, .12, .62, tz * 1.0, { ink: .03 }); }
    if (def.chain) ell(R.torso, '#e5b93a', .2, .015, .15, 0, .74, .03, { geo: new THREE.TorusGeometry(1, .06, 6, 24), rot: [Math.PI / 2, 0, 0], ink: .02 });
    if (def.collar) ell(R.torso, def.collar, .12, .04, .08, 0, .84, tz * .7, { ink: .02 });
    if (def.badge) ell(R.torso, '#e8e8ee', .05, .06, .02, .14, .6, tz * 1.1, { ink: .02 });
    if (def.backpack) { const bp = ell(R.torso, def.backpack, .22, .3, .1, 0, .42, -tz - .1, { ink: .05 }); [-1, 1].forEach(s => ell(R.torso, def.backpack, .025, .28, .02, s * .14, .5, tz * .9, { ink: 0 })); }
    /* head */
    const hs = def.headScale || 1; R.head = new THREE.Group(); R.head.position.y = .84; R.head.scale.setScalar(hs); R.torso.add(R.head);
    ell(R.head, skin, .47, .5, .17, 0, .38, 0, { ink: .055 });
    [-1, 1].forEach(s => ell(R.head, skin, .07, .1, .045, s * .465, .36, 0, { ink: .03 }));
    ell(R.head, skin, .06, .05, .04, .03, .33, .17, { ink: .02 });
    R.face = new THREE.Mesh(new THREE.PlaneGeometry(.8, .8), new THREE.MeshBasicMaterial({ map: faceTex(def.face || 'happy', false, def), transparent: true })); R.face.position.set(.0, .38, .2); R.face.renderOrder = 2; R.head.add(R.face);
    const hairCol = def.hair || '#5a3a22'; const beard = def.beard || 'none', bc = def.beardColor || hairCol;
    if (beard === 'moustache' || beard === 'beard') ell(R.head, bc, .2, .06, .06, .0, .275, .17, { ink: .025 });
    if (beard === 'beard') { ell(R.head, bc, .38, .25, .15, 0, .1, .03, { ink: .04 }); }
    if (beard === 'stubble') ell(R.head, def.stubble || '#a8907c', .4, .22, .15, 0, .1, .03, { ink: 0 });
    hairBuild(R.head, def.hairStyle || 'short', hairCol, hs, !!def.hat);
    if (def.hat) hatBuild(R.head, def.hatStyle || 'flatcap', def.hat, def);
    /* arms */
    const lr = B.lr;
    R.arm = [0, 1].map(i => { const sh = new THREE.Group(); sh.position.set((i ? -1 : 1) * (tw * .92), .72, (i ? -.13 : .13) * B.tz / .13); const up = limb(LEN.upper, lr * .8, longSleeve || outfit === 'dress' ? sleeveCol : (def.sleeves === 'short' ? main : sleeveCol));
      const fo = limb(LEN.fore, lr * .7, longSleeve ? sleeveCol : skin); fo.position.y = -LEN.upper;
      if (longSleeve) ell(fo, outfit === 'jumper' ? acc : (jacketLike ? main : sleeveCol), lr * .8, .045, lr * .55, 0, -LEN.fore + .1, 0, { ink: .02 });
      const gl = def.gloves || skin; const hand = new THREE.Group(); hand.position.y = -LEN.fore + .01; fo.add(hand);
      ell(hand, gl, .1, .12, .075, 0, -.06, 0, { ink: .035 }); ell(hand, gl, .04, .075, .04, i ? -.09 : .09, -.04, .03, { rot: [0, 0, i ? .5 : -.5], ink: .025 });
      up.add(fo); sh.add(up); R.torso.add(sh); return { sh, up, fo }; });
    /* lower body */
    const legMode = def.legs || (outfit === 'dress' ? 'skirt' : 'long'); const shoeCol = def.shoe || '#2a2430', st = def.shoeStyle || 'shoe';
    R.leg = [0, 1].map(i => { const hip = new THREE.Group(); hip.position.set(i ? -.17 : .17, 0, i ? -.05 : .05);
      const th = limb(LEN.thigh, lr, legMode === 'skirt' ? skin : pants), sn = limb(LEN.shin, lr * .85, legMode === 'long' ? pants : skin);
      sn.position.y = -LEN.thigh;
      const shoe = new THREE.Group(); shoe.position.set(.0, -LEN.shin + .11, 0); sn.add(shoe);
      if (legMode !== 'long') ell(shoe, '#f4f4f0', lr * .95, .06, lr * .6, 0, .24, 0, { ink: .02, geo: CYL });                    // socks
      ell(shoe, shoeCol, .22, .1, .115, .07, 0, 0, { ink: .04 }); ell(shoe, st === 'trainer' ? '#f4f4f0' : '#15141a', .22, .035, .12, .07, -.07, 0, { ink: .02 });
      if (st === 'boot') ell(shoe, shoeCol, .12, .24, .1, -.01, .15, 0, { ink: .035 });
      th.add(sn); hip.add(th); R.pelvis.add(hip); return { hip, th, sn }; });
    if (outfit === 'dress' || legMode === 'skirt' || outfit === 'coat' || outfit === 'robe') {
      const long = outfit === 'coat' || outfit === 'robe', h = long ? .95 : .6, col = outfit === 'dress' ? main : (long ? acc : (def.skirt || acc));
      const sk = new THREE.Mesh(new THREE.CylinderGeometry(tw * .9, tw * (long ? 1.45 : 1.6), h, 28, 1, true), new THREE.MeshStandardMaterial({ color: col, roughness: .85, side: THREE.DoubleSide })); sk.scale.z = .62; sk.position.y = -h / 2 + .08; sk.castShadow = true; inked(sk, .045); R.pelvis.add(sk);
      if (outfit === 'robe') { const tr = new THREE.Mesh(new THREE.CylinderGeometry(tw * 1.46, tw * 1.46, .12, 28, 1, true), new THREE.MeshStandardMaterial({ color: def.trim || '#f0ead8', side: THREE.DoubleSide })); tr.scale.z = .62; tr.position.y = -h + .1; R.pelvis.add(tr); } }
    else ell(R.pelvis, outfit === 'dress' ? main : pants, tw * .82, .1, tz * 1.1, 0, .05, 0, { ink: .04 });
    if (def.belt) band(R.torso, .02, .06, def.belt, .02);
    /* face state */
    R.setFace = (emo, blink) => { R.face.material.map = faceTex(emo || def.face || 'happy', !!blink, def); };
    return R; }
  return { build, LEN, faceTex };
}

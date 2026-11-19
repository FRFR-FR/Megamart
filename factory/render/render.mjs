#!/usr/bin/env node
// Standalone renderer: story.json -> headless Chrome (software WebGL) -> ffmpeg. No Remotion, no GPU, no downloads.
// usage: node render.mjs story.json out.mp4 [--w 540 --h 960 --fps 30 --from 0 --to 5 --audio mix.wav --frames dir]
import { chromium } from 'playwright-core';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { spawn } from 'child_process';
const A = process.argv.slice(2); const opt = (k, d) => { const i = A.indexOf('--' + k); return i < 0 ? d : A[i + 1]; };
const [storyFile, out] = A; const W = +opt('w', 540), H = +opt('h', 960), FPS = +opt('fps', 30);
const story = JSON.parse(fs.readFileSync(storyFile, 'utf8')); const t0 = +opt('from', 0), t1 = +opt('to', story.duration);
const root = path.dirname(new URL(import.meta.url).pathname);
const srv = http.createServer((q, s) => { const u = q.url.split('?')[0]; const f = u === '/story.json' ? path.resolve(storyFile) : path.join(root, u === '/' ? 'index.html' : u);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); } else { s.writeHead(200, { 'content-type': f.endsWith('.js') || f.endsWith('.mjs') ? 'text/javascript' : f.endsWith('.json') ? 'application/json' : 'text/html' }); s.end(d); } }); }).listen(0);
const port = srv.address().port;
const exe = ['/usr/bin/google-chrome', '/usr/bin/chromium'].find(fs.existsSync);
const b = await chromium.launch({ executablePath: exe, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: W, height: H } }); p.on('pageerror', e => console.error('page error', e.message)); p.on('console', m => m.type() === 'error' && console.error(m.text()));
await p.goto(`http://localhost:${port}/?w=${W}&h=${H}${opt('nophys',0)==='1'?'&nophys=1':''}`); await p.waitForFunction('window.READY', null, { timeout: 60000 });
const stills = opt('stills', null);
if (stills) { const ts = stills.split(',').map(Number).sort((a, b) => a - b); for (const t of ts) { await p.evaluate(x => window.renderFrame(x), t); fs.writeFileSync(`${out}_${t}.jpg`, await p.locator('canvas').screenshot({ type: 'jpeg', quality: 92 })); }
  console.error('PHYSICS AUDIT', JSON.stringify(await p.evaluate(() => window.audit()))); await b.close(); srv.close(); process.exit(0); }
const n = Math.round((t1 - t0) * FPS); const audio = opt('audio', null);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', ...(audio ? ['-i', audio] : []),
  '-c:v', 'libx264', '-crf', '16', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', ...(audio ? ['-c:a', 'aac', '-b:a', '256k', '-shortest'] : []), out], { stdio: ['pipe', 'inherit', 'inherit'] });
const start = Date.now();
for (let i = 0; i < n; i++) {
  await p.evaluate(t => window.renderFrame(t), t0 + i / FPS);
  const buf = await p.locator('canvas').screenshot({ type: 'jpeg', quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 30 === 0) console.error(`frame ${i}/${n}  ${((Date.now() - start) / 1000 / (i || 1)).toFixed(2)} s/frame`);
}
const aud = await p.evaluate(() => window.audit?.()); console.error('PHYSICS AUDIT', JSON.stringify(aud));
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); srv.close();
console.error(`done ${n} frames in ${((Date.now() - start) / 1000).toFixed(0)} s -> ${out}`);

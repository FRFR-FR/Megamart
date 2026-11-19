#!/usr/bin/env python3
"""story.json for 'The Tower That Was Saved By War' (Leaning Tower of Pisa). Uses the library: cast.py presets + props.js builders."""
import json, math, random, sys
sys.path.insert(0, 'library'); from cast import cast, crowd
D = 'shorts/pisa'; L = json.load(open(f'{D}/voice/lines.json')); DUR = 30.0
B = [0.0] + [round((L[i]['end'] + L[i + 1]['start']) / 2, 2) for i in range(len(L) - 1)] + [DUR]
TX, TZ = 10, -6                                              # tower
actors = []
def stand(x, z, t0=0): return [{'t': t0, 'x': x, 'z': z}, {'t': 40, 'x': x, 'z': z}]
def circuit(pts, speed, phase_len, t_end, t0=0):
    per = sum(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))); s = phase_len % per; keys = []; t = t0
    def at(sd):
        sd %= per
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]; d = math.dist(a, b)
            if sd <= d: u = sd / d; return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
            sd -= d
    while t <= t_end + 1e-6:
        x, z = at(s + (t - t0) * speed); keys.append({'t': round(t, 2), 'x': round(x, 3), 'z': round(z, 3)}); t += .5
    return keys
LOOP = [(-1, 7), (4.6, -.4), (6.6, .5), (.8, 7.9)]
PER = sum(math.dist(LOOP[i], LOOP[(i + 1) % 4]) for i in range(4))
# ---- era 1: medieval builders (t < 9.6) ----
fm = cast('foreman', keys=stand(4.8, 2.4), emote=[{'t': 0, 'e': 'worried'}, {'t': 13.5, 'e': 'surprised'}], show=[0, 15.1]); actors.append(fm)
for i, d in enumerate(crowd(6, 3, 'medieval')):
    k = circuit(LOOP, 1.8, i * PER / 6, 6.0); last = k[-1]
    k += [{'t': 9.0, 'x': 34, 'z': 3 + i * 1.4}, {'t': 40, 'x': 34, 'z': 3 + i * 1.4}]
    actors.append(dict(d, keys=k, lin=True, show=[0, 9.5]))
# ---- soldiers march across the foreground during the war ----
for i in range(3):
    actors.append(cast('soldier', keys=[{'t': 0, 'x': -22 - i * 2.2, 'z': 14}, {'t': 6.1, 'x': -9 - i * 2.2, 'z': 14}, {'t': 10.3, 'x': 21 - i * 2.2, 'z': 14}, {'t': 40, 'x': 21 - i * 2.2, 'z': 14}], lin=True, show=[6.2, 10.6]))
# ---- era 1b: builders return (9.9 - 20) ----
for i, d in enumerate(crowd(6, 9, 'medieval')):
    k = [{'t': 0, 'x': 26 + i * 1.5, 'z': 3.2}, {'t': 8.0, 'x': 26 + i * 1.5, 'z': 3.2}, {'t': 14.5, 'x': 7.4, 'z': 2.0 + i * .2}]
    # then join the same loop
    for j in range(1, 14): t = 14.5 + j * .5; pass
    k2 = circuit(LOOP, 1.8, i * PER / 6, 20.0, 14.5)
    for kk in k2: kk['t'] = round(kk['t'], 2)
    k = k[:2] + [{'t': 14.4, 'x': k2[0]['x'], 'z': k2[0]['z']}] + k2[1:]
    actors.append(dict(d, keys=k, lin=True, show=[9.9, 20.0]))
# ---- era 2: engineers + tourists (20 - 30) ----
for i, (x, z) in enumerate([(17.5, -2.5), (18.5, -8), (16, -11.5), (19.5, -5)]):
    d = cast('engineer' if i % 2 else 'builder', show=[20.0, 31], keys=stand(x, z))
    if i < 2: d['keys'] = [{'t': 0, 'x': x, 'z': z}, {'t': 22.5, 'x': x, 'z': z}, {'t': 23.5, 'x': x + 3, 'z': z + 1}, {'t': 25, 'x': x, 'z': z}, {'t': 40, 'x': x, 'z': z}]
    actors.append(d)
TP = [(8.4, 21.6), (12.6, 21.2), (10.4, 16.4), (4.5, 17.0), (17.5, 16.5), (1.5, 19.0)]
for i, (x, z) in enumerate(TP):
    d = cast('tourist' if i % 2 == 0 else 'tourist_f', shirt=['#e07b39', '#d9689a', '#2b8f93', '#e5c04a', '#7a4f9a', '#3e8f5a'][i], keys=stand(x, z), show=[20.0, 31])
    if i < 3: d['armsUp'] = [{'t': 0, 'v': 0}, {'t': 25.5 + i * .25, 'v': 0}, {'t': 26.1 + i * .25, 'v': 1}]; d['armSide'] = 0 if i != 1 else None; d['armAngle'] = 2.3; d['emote'] = [{'t': 0, 'e': 'happy'}, {'t': 26, 'e': 'smug'}]
    actors.append(d)
for i, d in enumerate(crowd(3, 5, 'tourists')):
    z = 26 + i * 1.5; actors.append(dict(d, keys=[{'t': 0, 'x': -6, 'z': z}, {'t': 20, 'x': -6, 'z': z}, {'t': 30, 'x': 26, 'z': z}], lin=True, show=[20.0, 31]))
# the schoolkid watching the books on the sofa (room at x=60)
actors.append(cast('schoolkid', keys=stand(64.2, -8.2), show=[17.5, 21], emote=[{'t': 0, 'e': 'surprised'}]))
actors.append(cast('nan', keys=stand(56.2, -8.8), show=[17.5, 21], emote=[{'t': 0, 'e': 'happy'}]))
# ---- world ----
ap = [-1, 1.4, 10.4, 10.9, 11.4, 11.9, 12.4, 12.9]
lean = [{'t': 0, 'a': 0}, {'t': 3.5, 'a': 3.4}, {'t': 10.0, 'a': 3.8}, {'t': 13.2, 'a': 7.6}, {'t': 20.8, 'a': 7.6}, {'t': 24.6, 'a': 6.2}, {'t': 40, 'a': 6.2}]
world = [{'type': 'land', 'x0': -140, 'x1': 140, 'z0': -110, 'z1': 110, 'color': 0x7fc24f},
 {'type': 'pave', 'x0': -60, 'x1': 60, 'z0': 11.5, 'z1': 14.5, 'y': .806, 'color': 0xdccfb2}, {'type': 'pave', 'x0': 6, 'x1': 14, 'z0': -2.5, 'z1': 11.6, 'y': .807, 'color': 0xdccfb2},
 {'type': 'pisa', 'x': TX, 'z': TZ, 'appear': ap, 'lean': lean, 'bend': 1.3},
 {'type': 'duomo', 'x': -6, 'z': -21}, {'type': 'baptistery', 'x': -26, 'z': -3},
 {'type': 'hill', 'x': 20, 'z': -80, 'r': 60, 'h': 14, 'color': 0x6fae4a}, {'type': 'hill', 'x': -50, 'z': -70, 'r': 44, 'h': 11, 'color': 0x78b650}]
for x, z in [(-30, -20), (-34, 8), (24, -22), (30, -4), (-14, 16), (28, 20)]: world.append({'type': 'cypress', 'x': x, 'z': z, 'size': 1.15})
for x, z, s in [(-44, -12, 1.2), (36, -14, 1.1), (-20, 30, 1.1), (40, 30, 1.0)]: world.append({'type': 'oak', 'x': x, 'z': z, 'size': s})
# medieval dressing (until the modern cut at 20)
for x, z in [(-1.6, 8.8), (0, 9.2), (-.4, 10.2), (-2.4, 7.9)]: world.append({'type': 'crate_box', 'x': x, 'z': z, 'size': .8, 'color': 0xb9b1a0, 'until': 20.0})
world += [{'type': 'haystack', 'x': -12, 'z': 6, 'until': 20.0}, {'type': 'sheep', 'x': -18, 'z': 22, 'until': 20.0, 'keys': [{'t': 0, 'x': -18, 'z': 22}, {'t': 10, 'x': -10, 'z': 25}, {'t': 20, 'x': -16, 'z': 21}]}, {'type': 'sheep', 'x': -22, 'z': 24, 'until': 20.0, 'keys': [{'t': 0, 'x': -22, 'z': 24}, {'t': 12, 'x': -14, 'z': 27}, {'t': 20, 'x': -21, 'z': 25}]}]
# time passes: flowers/bushes grow round the base while the war goes on
for i, (x, z) in enumerate([(2.5, -1), (16, -2), (3, -12), (17.5, -9)]): world.append({'type': 'bush', 'x': x, 'z': z, 'at': 6.8 + i * 1.0, 'until': 9.9, 'berries': '#d32a2a'})
for i, (x, z) in enumerate([(5.5, 4.0), (14.5, 2.5)]): world.append({'type': 'flowers', 'x': x, 'z': z, 'at': 7.0 + i * 1.1, 'until': 9.9, 'w': 2.4, 'd': 1})
# modern dressing (from 20)
world += [{'type': 'bench', 'x': -8, 'z': 10.2, 'at': 20.0}, {'type': 'bench', 'x': 22, 'z': 10.4, 'at': 20.0}, {'type': 'bin', 'x': -3, 'z': 12.6, 'at': 20.0}, {'type': 'stall', 'x': 26, 'z': 12, 'at': 20.0, 'goods': ['#e03a2a', '#f2c22c', '#f4f4f0']},
          {'type': 'bike', 'x': -2.5, 'z': 17.8, 'at': 20.0, 'rot': .5}, {'type': 'balloons', 'x': 27, 'z': 9.8, 'at': 20.0}, {'type': 'barrier', 'x': 18.5, 'z': -.8, 'at': 20.0, 'rot': 1.2}, {'type': 'cone', 'x': 16.2, 'z': 1.2, 'at': 20.0}, {'type': 'cone', 'x': 20.6, 'z': -3.6, 'at': 20.0}]
for i, (x, z) in enumerate([(15.5, -4.5), (17.2, -5.6), (15.8, -7.0), (17.6, -8.4), (16.2, -9.6)]): world.append({'type': 'rock', 'x': x + 3.6, 'z': z - 1.2, 'size': .45, 'color': 0x7a5a3a, 'at': 20.9 + i * .9, 'col': False})
# the sofa vignette (a different place, a cartoon cut-away)
world += [{'type': 'room', 'x': 60, 'z': -10, 'w': 14, 'd': 11, 'h': 7, 'wall': 0xe8d8c0}, {'type': 'rug', 'x': 60, 'z': -6, 'r': 3.4}, {'type': 'sofa', 'x': 60, 'z': -12.4, 'col': [2.7, .8, 1.1], 'color': 0x8a3a4a},
          {'type': 'shelf', 'x': 65.5, 'z': -14.3}, {'type': 'lamp_table', 'x': 56.8, 'z': -13.8}, {'type': 'mug', 'x': 58.3, 'z': -5.2}, {'type': 'tv', 'x': 55.4, 'z': -14.4}]
for i, c in enumerate([0xd32a2a, 0x2f5f9e, 0xe5c04a, 0x3e8f5a]):
    world.append({'type': 'crate', 'x': 60 + (i % 2) * .08, 'y': 2.6 + i * .8, 'z': -12.2, 's': .78, 'mass': 1, 'color': c, 'at': 18.0 + i * .5})
for x, y, z, s in [(-30, 40, 40, 1.3), (30, 44, 20, 1.5), (0, 52, -60, 1.7), (-55, 42, -40, 1.4), (60, 46, -50, 1.5), (-10, 38, 70, 1.2)]: world.append({'type': 'cloud', 'x': x, 'y': y, 'z': z, 's': s})
S = lambda i: (B[i], B[i + 1])
def shot(i, light='day', **kw): return dict(zip(('a', 'b'), S(i)), light=light, **kw)
shots = [
 shot(0, **{'from': [-6, 2.4, 17], 'to': [-1, 3.2, 15.5], 'look': [9, 6.5, -6], 'fov': 46, 'roll': 2}),
 shot(1, **{'from': [17, 2.2, 7], 'to': [15, 2.6, 5], 'look': [9.5, 3.4, -5], 'fov': 44, 'roll': -2}),
 shot(2, 'golden', **{'from': [-3, 2.3, 21], 'to': [2, 2.5, 20], 'look': [8, 4.0, 2], 'fov': 46, 'roll': 2}),
 shot(3, **{'from': [3, 2.4, 22], 'to': [5, 3.6, 24], 'look': [10, 13, -6], 'fov': 50, 'roll': -2}),
 shot(4, lookActor=0, lookOff=[0, 1.9, 0], **{'from': [8.6, 2.3, 7.2], 'to': [8.2, 2.4, 6.5], 'fov': 30, 'roll': 3}),
 shot(5, 'golden', **{'from': [10, 1.4, 9], 'to': [11, 9, 13], 'look': [10, 8, -6], 'fov': 46, 'roll': 0}),
 shot(6, **{'from': [57, 3.4, 0], 'to': [59, 3.1, -1.4], 'look': [60, 2.2, -12], 'fov': 40, 'roll': -2}),
 shot(7, **{'from': [26, 3.6, 12], 'to': [22, 4.6, 9], 'look': [12, 7, -6], 'fov': 46, 'roll': 0}),
 shot(8, 'golden', **{'from': [10.6, 1.7, 34], 'to': [10.4, 2.0, 32.5], 'look': [10.4, 9.5, -6], 'fov': 46, 'roll': -2}),
]
story = {'duration': DUR, 'world': world, 'actors': actors, 'shots': shots, 'kicks': [{'t': 13.55, 'amp': .25}, {'t': 15.1, 'amp': .2}], 'sway': [{'t': 0, 'a': 0}], 'swayMax': 0, 'dampersAt': 999}
json.dump(story, open(f'{D}/story.json', 'w')); print(len(actors), 'actors', len(world), 'world items', [(s['a'], s['b']) for s in shots])

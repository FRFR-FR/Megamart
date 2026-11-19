#!/usr/bin/env python3
"""Build story.json for 'The Bridge That Wobbled' from lines.json (voice timings). Original story, original cast."""
import json, math, random, sys
R = random.Random(7)
D = 'shorts/millennium'
L = json.load(open(f'{D}/voice/lines.json')); DUR = 30.0
# shot boundaries = midpoints of the gaps between voice lines (cuts land on the first word)
B = [0.0] + [round((L[i]['end'] + L[i + 1]['start']) / 2 - 0.03, 2) for i in range(len(L) - 1)] + [DUR]

SKIN = ['#f6d9c6', '#f2cfb8', '#fbe3d3', '#efc9b0', '#f8dcc9']          # all white / pale skin tones
HAIR = ['#5a3a22', '#d9b36b', '#c2561e', '#2b211c', '#b8b8b8', '#8b5a2b']
SHIRT = ['#c8382f', '#2f5f9e', '#3e8f5a', '#e5c04a', '#7a4f9a', '#e9e9ee', '#e07b39', '#2b8f93']
PANTS = ['#3b3a5a', '#2d3a4a', '#4a4036', '#3a3a3a', '#5a4a3a', '#2f4a3a']
def person(**kw):
    d = {'skin': R.choice(SKIN), 'shirt': R.choice(SHIRT), 'pants': R.choice(PANTS), 's': round(R.uniform(.9, 1.05), 2), 'y0': .85}
    r = R.random()
    if r < .28: d.update(hat=R.choice(['#6e6a5e', '#4b5a48', '#7a6a50']), hatStyle='cap')
    elif r < .4: d.update(hat='#222228')
    else: d['hair'] = R.choice(HAIR)
    d.update(kw); return d

actors = []
V = 2.0; ZN = 8.2; XL, XR = -.65, .65
LOOP = [(XL, -ZN), (XL, ZN), (XR, ZN), (XR, -ZN)]          # north on the left lane, shuffle across, south on the right lane, shuffle back
SEG = [math.dist(LOOP[i], LOOP[(i + 1) % 4]) for i in range(4)]; LP = sum(SEG)
def pace_keys(s0):
    s = s0 % LP; i = 0
    while s >= SEG[i]: s -= SEG[i]; i += 1
    a, b = LOOP[i], LOOP[(i + 1) % 4]; f = s / SEG[i]
    keys = [{'t': 0, 'x': a[0] + (b[0] - a[0]) * f, 'z': a[1] + (b[1] - a[1]) * f}]; t = (SEG[i] - s) / V
    while t < DUR + 2:
        i = (i + 1) % 4; q = LOOP[i]; keys.append({'t': round(t, 3), 'x': q[0], 'z': q[1]}); t += SEG[i] / V
    keys.insert(1, {'t': round((SEG[(i - 0) % 4] and 0) + keys[1]['t'] - 1e-3, 3), 'x': keys[1]['x'], 'z': keys[1]['z']}) if False else None
    return keys
NP = 14
for k in range(NP):
    a = person(keys=pace_keys(k * LP / NP), lin=True)
    if k == 0: a.update(shirt='#2f5f9e', hat='#6e6a5e', hatStyle='cap', skin='#f5d5c0', s=1.0); a.pop('hair', None)       # hero
    if k in (5, 6): a.update(shirt='#f2d21b', hat='#f4f4f0', pants='#2d3a4a'); a.pop('hatStyle', None); a.pop('hair', None)  # hi-vis engineers
    actors.append(a)
for x, z in [(-5.5, 11), (-7, 12.5), (5.5, 10.5), (7, 12), (-5.5, -11), (6, -12)]:                      # onlookers on the banks
    actors.append(person(keys=[{'t': 0, 'x': x, 'z': z}, {'t': 30, 'x': x, 'z': z}]))
BUS = [(0, -60), (16.4, -14), (18.2, -3.2), (18.6, -.6), (18.95, 0), (30, 0)]
LEAN = [{'t': 18.4, 'v': 0}, {'t': 18.7, 'v': .5}, {'t': 19.1, 'v': .6}, {'t': 19.6, 'v': .1}, {'t': 20.2, 'v': 0}]
for ox, dz in [(-1.5, -.35), (.1, .3), (1.5, -.25)]:
    actors.append(person(keys=[{'t': t, 'x': x + ox, 'z': -32 + dz} for t, x in BUS], lin=True, noWalk=True, yOff=.7, s=.85, lean=LEAN))

world = [
  {'type': 'land', 'x0': -200, 'x1': 200, 'z0': -200, 'z1': -7}, {'type': 'land', 'x0': -200, 'x1': 200, 'z0': 7, 'z1': 200},
  {'type': 'riverx', 'w': 14, 'y': .3},
  {'type': 'pave', 'x0': -200, 'x1': 200, 'z0': -200, 'z1': -9.2, 'y': .803, 'color': 0x72b84a}, {'type': 'pave', 'x0': -200, 'x1': 200, 'z0': 9.2, 'z1': 200, 'y': .803, 'color': 0x72b84a},
  {'type': 'pave', 'x0': -14, 'x1': 14, 'z0': -28, 'z1': -9.2, 'y': .808, 'color': 0xd7c9aa}, {'type': 'pave', 'x0': -14, 'x1': 14, 'z0': 9.2, 'z1': 34, 'y': .808, 'color': 0xd7c9aa},
  {'type': 'pave', 'x0': -200, 'x1': 200, 'z0': -35, 'z1': -29, 'y': .806, 'color': 0x4a4d55}, {'type': 'pave', 'x0': -200, 'x1': 200, 'z0': 36, 'z1': 42, 'y': .806, 'color': 0x4a4d55},
  {'type': 'swayBridge', 'len': 18, 'w': 3.4, 'y': .8, 'n': 12},
  {'type': 'tate', 'x': -4, 'z': -44}, {'type': 'stpauls', 'x': 0, 'z': 105, 's': 1.3},
  {'type': 'terrace', 'x': -40, 'z': 50, 'n': 8}, {'type': 'terrace', 'x': 8, 'z': 50, 'n': 8},
  {'type': 'terrace', 'x': -36, 'z': 18, 'n': 3}, {'type': 'terrace', 'x': 26, 'z': 20, 'n': 3}, {'type': 'terrace', 'x': -40, 'z': -18, 'n': 3}, {'type': 'terrace', 'x': 28, 'z': -20, 'n': 3},
  {'type': 'bus', 'keys': [{'t': t, 'x': x, 'z': -32} for t, x in BUS]},
  {'type': 'phonebox', 'x': 9, 'z': -14}, {'type': 'phonebox', 'x': -9, 'z': 14}, {'type': 'pillarbox', 'x': 8, 'z': -19},
  {'type': 'flag', 'x': -3.2, 'z': -10.5}, {'type': 'flag', 'x': 3.2, 'z': -10.5}, {'type': 'flag', 'x': -3.2, 'z': 10.5}, {'type': 'flag', 'x': 3.2, 'z': 10.5},
  {'type': 'box', 'w': 4.4, 'h': 1.2, 'd': .3, 'x': 0, 'y': 3, 'z': -12.9, 'color': 0xd32a2a, 'mass': 40, 'at': 12.0},
  {'type': 'box', 'w': 4.4, 'h': 1.2, 'd': .3, 'x': 0, 'y': 3, 'z': 12.9, 'color': 0xd32a2a, 'mass': 40, 'at': 12.0},
]
for x, z, sc in [(-10, -14, 1.1), (10, -22, 1.2), (-11, -22, 1.1), (10, 15, 1.1), (-11, 25, 1.2), (11, 25, 1.1), (-10, 15, 1.0)]: world.append({'type': 'tree', 'x': x, 'z': z, 'y': .8, 's': sc})
for x in (-9, 9):
    for z in (-12, 12, -20, 20): world.append({'type': 'lamp', 'x': x, 'z': z})
for x, y, z, s in [(-30, 34, 60, 1.2), (28, 40, 50, 1.4), (0, 48, 95, 1.6), (-45, 36, -70, 1.3), (35, 38, -60, 1.2), (8, 46, -95, 1.6), (70, 38, 5, 1.4), (-70, 40, -5, 1.3), (-15, 42, 20, 1.0), (22, 36, -20, 1.0)]:
    world.append({'type': 'cloud', 'x': x, 'y': y, 'z': z, 's': s})

S = lambda i: (B[i], B[i + 1])
shots = [
 dict(zip(('a', 'b'), S(0)), light='day', **{'from': [-4, 5.0, -29], 'to': [-1.5, 4.2, -23], 'look': [0, 5, 30], 'fov': 40, 'roll': 2}),
 dict(zip(('a', 'b'), S(1)), light='day', **{'from': [6.5, 8.5, -8], 'to': [5, 7.5, -3], 'look': [0, 1.5, 2.5], 'fov': 42, 'roll': -2}),
 dict(zip(('a', 'b'), S(2)), light='day', followActor=0, swayRoll=.1, **{'from': [-7.5, 2.8, -2.5], 'to': [-7.0, 2.6, -.5], 'lookActor': 0, 'lookOff': [0, 1.4, .4], 'fov': 34, 'roll': 3}),
 dict(zip(('a', 'b'), S(3)), light='day', swayRoll=.12, **{'from': [0, 7.0, -26], 'to': [0, 6.0, -20], 'look': [0, 2, 9], 'fov': 34, 'roll': 0}),
 dict(zip(('a', 'b'), S(4)), light='day', **{'from': [6, 3.6, -22], 'to': [5.5, 3.4, -21], 'look': [0, 1.4, -12.9], 'fov': 38, 'roll': 2}),
 dict(zip(('a', 'b'), S(5)), light='day', swayRoll=.08, **{'from': [5.2, 3.6, -6], 'to': [4.6, 3.2, -2], 'look': [-.2, 2.0, 2.5], 'fov': 40, 'roll': 2}),
 dict(zip(('a', 'b'), S(6)), light='day', **{'from': [3.8, 3.4, -11], 'to': [3.4, 3.2, -11.5], 'look': [.3, 2.3, -32], 'fov': 34, 'roll': 0}),
 dict(zip(('a', 'b'), S(7)), light='day', swayRoll=.14, **{'from': [0, 5.4, 20], 'to': [0, 4.8, 17], 'look': [0, 1.6, -2], 'fov': 36, 'roll': 0}),
 dict(zip(('a', 'b'), S(8)), light='day', **{'from': [-8.5, 2.2, 4.2], 'to': [-7.5, 2.0, 2.0], 'look': [0, 1.0, .5], 'fov': 38, 'roll': -2}),
 dict(zip(('a', 'b'), S(9)), light='golden', swayRoll=.06, **{'from': [-9, 4.8, 27], 'to': [-5, 4.2, 21], 'look': [0, 2.5, -8], 'fov': 38, 'roll': 2}),
]
sway = [(0, .1), (2.5, .3), (3.9, .4), (6.9, .45), (9.5, .65), (12, .75), (17, .8), (22.6, .8), (24.4, .05), (25.6, 0), (27.6, 0), (28.4, .12), (30, .15)]
story = {'duration': DUR, 'world': world, 'actors': actors, 'shots': shots, 'kicks': [{'t': 12.2, 'amp': .3}, {'t': 18.55, 'amp': .25}],
         'sway': [{'t': t, 'a': a} for t, a in sway], 'swayMax': .8, 'dampersAt': 22.75}
json.dump(story, open(f'{D}/story.json', 'w'))
print('shots', [(s['a'], s['b']) for s in shots]); print(len(actors), 'actors,', len(world), 'world items')

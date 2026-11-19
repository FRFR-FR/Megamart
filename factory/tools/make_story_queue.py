#!/usr/bin/env python3
"""story.json for 'The Queue Nobody Joined On Purpose' (original fiction, Little Wumbleton, UK high street). All-white cast."""
import json, math, random
R = random.Random(11); D = 'shorts/queue'
L = json.load(open(f'{D}/voice/lines.json')); DUR = 30.8
B = [0.0] + [round((L[i]['end'] + L[i + 1]['start']) / 2 - 0.03, 2) for i in range(len(L) - 1)] + [DUR]
SKIN = ['#f6d9c6', '#f2cfb8', '#fbe3d3', '#efc9b0', '#f8dcc9']
HAIR = ['#5a3a22', '#d9b36b', '#c2561e', '#2b211c', '#b8b8b8', '#8b5a2b']
SHIRT = ['#c8382f', '#2f5f9e', '#3e8f5a', '#e5c04a', '#7a4f9a', '#e9e9ee', '#e07b39', '#2b8f93']
PANTS = ['#3b3a5a', '#2d3a4a', '#4a4036', '#3a3a3a', '#5a4a3a', '#2f4a3a']
def person(**kw):
    d = {'skin': R.choice(SKIN), 'shirt': R.choice(SHIRT), 'pants': R.choice(PANTS), 's': round(R.uniform(.9, 1.05), 2), 'y0': .85}
    r = R.random()
    if r < .25: d.update(hat=R.choice(['#6e6a5e', '#4b5a48', '#7a6a50']), hatStyle='cap')
    elif r < .35: d.update(hat='#222228')
    else: d['hair'] = R.choice(HAIR)
    d.update(kw); return d
QZ, LZ, X0, SP, V = -5.3, -4.2, -6.0, .8, 2.2      # queue row, approach lane, front slot x, slot spacing, walk speed
def walker(k, T):
    xk = X0 + SP * k; xs = xk + 2.0 + V * (T - 1.2)
    return [{'t': 0, 'x': round(xs, 3), 'z': LZ}, {'t': round(T - 1.2, 3), 'x': round(xk + 2.0, 3), 'z': LZ}, {'t': round(T - .15, 3), 'x': round(xk + .3, 3), 'z': QZ}, {'t': round(T + .1, 3), 'x': round(xk, 3), 'z': QZ}, {'t': 40, 'x': round(xk, 3), 'z': QZ}]
actors = []; NQ = 31
for k in range(NQ):
    T = 2.4 if k == 0 else 4.6 + .6 * (k - 1)
    a = person(keys=walker(k, T), lin=True)
    if k == 0:
        a.update(shirt='#2f5f9e', hat='#6e6a5e', hatStyle='cap', skin='#f5d5c0', s=1.0); a.pop('hair', None)       # Derek
        a['keys'] = a['keys'][:4] + [{'t': 28.0, 'x': X0, 'z': QZ}, {'t': 29.2, 'x': X0 - 2.2, 'z': LZ}, {'t': 31, 'x': X0 - 6.4, 'z': LZ - .1}]
    if 10 <= k <= 13: a.update(shirt='#b3202a', hat='#222228', pants='#1f1f26'); a.pop('hatStyle', None); a.pop('hair', None)   # brass band
    if k == 24: a.update(shirt='#1d1d22', pants='#1d1d22', hair='#b8b8b8'); a.pop('hat', None); a.pop('hatStyle', None)       # the vicar
    actors.append(a)
for x in (-14, -1, 9, 16):                                  # villagers on the far pavement, watching
    actors.append(person(keys=[{'t': 0, 'x': x, 'z': 4.7}, {'t': 40, 'x': x, 'z': 4.7}]))
world = [{'type': 'land', 'x0': -250, 'x1': 250, 'z0': -250, 'z1': 250, 'color': 0x72b84a},
  {'type': 'pave', 'x0': -250, 'x1': 250, 'z0': -3.5, 'z1': 3.5, 'y': .806, 'color': 0x4a4d55},
  {'type': 'pave', 'x0': -250, 'x1': 250, 'z0': -6, 'z1': -3.5, 'y': .808, 'color': 0xd7c9aa}, {'type': 'pave', 'x0': -250, 'x1': 250, 'z0': 3.5, 'z1': 6, 'y': .808, 'color': 0xd7c9aa},
  {'type': 'terrace', 'x': -50, 'z': -9, 'n': 28}, {'type': 'terrace', 'x': 52, 'z': -9, 'n': 14}, {'type': 'terrace', 'x': -50, 'z': 9, 'n': 28}, {'type': 'terrace', 'x': 52, 'z': 9, 'n': 14},
  {'type': 'bus', 'keys': [{'t': 0, 'x': -90, 'z': 0}, {'t': 20.2, 'x': -34, 'z': 0}, {'t': 24.4, 'x': 38, 'z': 0}, {'t': 40, 'x': 200, 'z': 0}]},
  {'type': 'box', 'w': .12, 'h': 2.4, 'd': .12, 'x': -7.3, 'y': .8, 'z': -5.7, 'color': 0x2a2a30}, {'type': 'box', 'w': .7, 'h': .7, 'd': .08, 'x': -7.3, 'y': 3.0, 'z': -5.7, 'color': 0xf2c22c},
  {'type': 'phonebox', 'x': -12, 'z': -5.1}, {'type': 'pillarbox', 'x': -9.6, 'z': -5.4}, {'type': 'flag', 'x': -10.8, 'z': -3.9}]
for x in (24, 36): world.append({'type': 'lamp', 'x': x, 'z': -3.45})
for x in (16, 28): world.append({'type': 'lamp', 'x': x, 'z': 3.45})
for x, s in [(-18, 1.1), (-4, 1.2), (12, 1.1), (22, 1.0)]: world.append({'type': 'tree', 'x': x, 'z': 5.1, 'y': .8, 's': s})
for x, y, z, s in [(-30, 34, 60, 1.2), (28, 40, 50, 1.4), (0, 48, 95, 1.6), (-45, 36, -70, 1.3), (35, 38, -60, 1.2), (8, 46, -95, 1.6), (70, 38, 5, 1.4), (-70, 40, -5, 1.3), (-15, 42, 20, 1.0), (22, 36, -20, 1.0)]:
    world.append({'type': 'cloud', 'x': x, 'y': y, 'z': z, 's': s})
S = lambda i: (B[i], B[i + 1])
def shot(i, light='day', **kw): return dict(zip(('a', 'b'), S(i)), light=light, **kw)
shots = [
 shot(0, **{'from': [-13, 3.4, 3.6], 'to': [-10.5, 3.1, 2.4], 'look': [-3, 1.6, -5], 'fov': 40, 'roll': 2}),
 shot(1, lookActor=0, lookOff=[0, 1.3, 0], **{'from': [-3.2, 2.0, -1.4], 'to': [-3.9, 1.9, -1.9], 'fov': 34, 'roll': -2}),
 shot(2, **{'from': [-10.5, 2.8, 0.6], 'to': [-8, 2.7, 0.8], 'look': [14, 1.4, -5.3], 'fov': 38, 'roll': 2}),
 shot(3, **{'from': [9.5, 2.7, 0.4], 'to': [7.5, 2.5, 0.2], 'look': [3.6, 1.4, -5.3], 'fov': 38, 'roll': -2}),
 shot(4, **{'from': [-9.6, 2.4, -1.2], 'to': [-8.3, 2.3, -1.4], 'look': [-2, 1.4, -5.3], 'fov': 34, 'roll': 3}),
 shot(5, **{'from': [2, 9, 6], 'to': [4.5, 8.4, 4], 'look': [6, 1, -5], 'fov': 44, 'roll': 0}),
 shot(6, lookActor=0, lookOff=[0, 1.0, 0], **{'from': [-9.8, 1.7, -1.6], 'to': [-9.0, 1.6, -2.0], 'fov': 34, 'roll': 2}),
 shot(7, **{'from': [3.5, 2.7, 3.3], 'to': [6.5, 2.6, 3.0], 'look': [9, 1.6, -5.2], 'fov': 40, 'roll': -2}),
 shot(8, 'golden', **{'from': [-14, 9, 6], 'to': [-4, 8, 5], 'look': [8, 1, -5], 'fov': 44, 'roll': 0}),
 shot(9, 'golden', lookActor=0, lookOff=[0, 1.3, 0], **{'from': [-18, 1.7, -2.7], 'to': [-17, 1.6, -2.9], 'fov': 36, 'roll': -2}),
]
story = {'duration': DUR, 'world': world, 'actors': actors, 'shots': shots, 'kicks': [{'t': 12.2, 'amp': .2}, {'t': 16.85, 'amp': .25}],
         'sway': [{'t': 0, 'a': 0}], 'swayMax': 0, 'dampersAt': 999}
json.dump(story, open(f'{D}/story.json', 'w')); print(len(actors), 'actors', len(world), 'world', [(s['a'], s['b']) for s in shots])

"""Character library: named presets + randomised crowd generators. Every function returns a plain dict that goes straight into story.json 'actors'
(add 'keys' for movement, 'y0': .85 on a ground whose top is .8). Fields are documented at the top of render/lib/characters.js.
All presets default to pale skin; pass skin='#hex' to change (SKINS has a spread of tones)."""
import random
SKINS = {'pale': '#f6d9c6', 'fair': '#f2cfb8', 'light': '#fbe3d3', 'tan': '#e3b48f', 'brown': '#a8764f', 'dark': '#6f4a32', 'deep': '#4a3023'}
PALE = [SKINS['pale'], SKINS['fair'], SKINS['light'], '#efc9b0', '#f8dcc9']
HAIR = ['#5a3a22', '#d9b36b', '#c2561e', '#2b211c', '#b8b8b8', '#8b5a2b', '#e8d29a']
TEE = ['#c8382f', '#2f5f9e', '#3e8f5a', '#e5c04a', '#7a4f9a', '#e9e9ee', '#e07b39', '#2b8f93', '#d9689a']
PANTS = ['#3b3a5a', '#2d3a4a', '#4a4036', '#3a3a3a', '#5a4a3a', '#2f4a3a']
P = {
 # ---- everyday UK ----
 'derek':      dict(outfit='jumper', shirt='#2f5f9e', accent='#2f5f9e', hat='#6e6a5e', hatStyle='flatcap', pants='#5a4a3a', build='stocky', beard='stubble', hair='#5a3a22'),
 'nan':        dict(outfit='dress', shirt='#8a5fb0', hair='#b8b8b8', hairStyle='bun', glasses='#555555', shoe='#6b3b3b'),
 'granddad':   dict(outfit='jacket', shirt='#e9e9ee', accent='#7a6a50', hat='#6e6a5e', hatStyle='flatcap', beard='moustache', hair='#b8b8b8', pants='#4a4036', build='stocky'),
 'bobby':      dict(outfit='suit', shirt='#e9e9ee', accent='#1d1d22', hat='#1d1d22', hatStyle='bobby', pants='#1d1d22', tie='#1d1d22', badge=True, beard='moustache', hair='#2b211c'),
 'vicar':      dict(outfit='coat', shirt='#1d1d22', accent='#1d1d22', collar='#f4f4f0', hair='#b8b8b8', hairStyle='wisp', glasses='#333333', pants='#1d1d22'),
 'mayor':      dict(outfit='suit', shirt='#e9e9ee', accent='#7a1f2a', chain=True, hat='#1d1d22', hatStyle='bowler', pants='#1d1d22', tie='#e5c04a', build='stocky', beard='moustache', hair='#8b5a2b'),
 'postie':     dict(outfit='jacket', shirt='#e9e9ee', accent='#d32a2a', hat='#d32a2a', hatStyle='baseball', legs='shorts', backpack='#d32a2a', shoeStyle='trainer', hair='#5a3a22'),
 'builder':    dict(outfit='hivis', hat='#f2d21b', hatStyle='hardhat', pants='#2d3a4a', shoeStyle='boot', beard='beard', hair='#8b5a2b', build='stocky'),
 'engineer':   dict(outfit='hivis', hat='#f4f4f0', hatStyle='hardhat', pants='#2d3a4a', shoeStyle='boot', glasses='#333333', hair='#2b211c'),
 'baker':      dict(outfit='apron', shirt='#f4f4f0', accent='#f4f4f0', hat='#f4f4f0', hatStyle='chef', pants='#3a3a3a', build='stocky', beard='moustache', hair='#8b5a2b'),
 'schoolkid':  dict(outfit='blazer', shirt='#e9e9ee', accent='#2a3a6a', tie='#b3262e', legs='shorts', hair='#c2561e', hairStyle='fringe', s=.75, build='slim'),
 'toddler':    dict(outfit='hoodie', shirt='#e9a83a', accent='#e9a83a', hair='#e8d29a', hairStyle='curly', s=.55, headScale=1.12, legs='shorts'),
 'teen':       dict(outfit='hoodie', shirt='#e5c04a', accent='#2b8f93', hair='#c2561e', hairStyle='ponytail', pants='#3a3a3a', shoeStyle='trainer', lashes=True, build='slim'),
 'office_woman': dict(outfit='suit', shirt='#e9e9ee', accent='#2a3a5a', legs='skirt', skirt='#2a3a5a', hair='#2b211c', hairStyle='bob', lashes=True, build='slim'),
 'scientist':  dict(outfit='coat', shirt='#e9e9ee', accent='#f4f4f0', glasses='#333333', hair='#b8b8b8', hairStyle='curly', pants='#3a3a3a'),
 'tourist':    dict(outfit='tee', shirt='#e07b39', hat='#e8d29a', hatStyle='sunhat', legs='shorts', backpack='#2f5f9e', shoeStyle='trainer', glasses='#333333', hair='#5a3a22'),
 'tourist_f':  dict(outfit='tee', shirt='#d9689a', hat='#f4f4f0', hatStyle='baseball', legs='shorts', backpack='#3e8f5a', shoeStyle='trainer', hair='#e8d29a', hairStyle='ponytail', lashes=True),
 # ---- history ----
 'peasant':    dict(outfit='jumper', shirt='#8a6a3a', accent='#5a4a2a', pants='#5a4a3a', shoeStyle='boot', hat='#7a6a50', hatStyle='flatcap', hair='#5a3a22'),
 'mason':      dict(outfit='apron', shirt='#b8a888', accent='#6b4a2a', pants='#5a4a3a', shoeStyle='boot', hat='#b8a888', hatStyle='beret', beard='beard', hair='#5a3a22', build='stocky'),
 'foreman':    dict(outfit='jumper', shirt='#7a2f2f', accent='#5a2a2a', pants='#3a3a3a', shoeStyle='boot', hat='#4a2a2a', hatStyle='beret', beard='beard', hair='#2b211c', build='stocky', face='worried'),
 'soldier':    dict(outfit='jacket', shirt='#d8d8e0', accent='#a8302a', hat='#8a8f98', hatStyle='bowler', pants='#4a4a55', shoeStyle='boot', hair='#2b211c', belt='#6b4a2a'),
 'king':       dict(outfit='robe', shirt='#e9e9ee', accent='#6a2a8a', trim='#f4efe2', hat='#e5b93a', hatStyle='crown', beard='beard', hair='#b8b8b8', chain=True, build='stocky'),
 'victorian_gent': dict(outfit='coat', shirt='#e9e9ee', accent='#2a2a30', hat='#1d1d22', hatStyle='tophat', beard='moustache', hair='#2b211c', pants='#2a2a30', tie='#7a1f2a', shoeStyle='boot'),
 'victorian_lady': dict(outfit='dress', shirt='#4a78b8', hat='#f4f4f0', hatStyle='bonnet', hair='#8b5a2b', hairStyle='bun', lashes=True, shoeStyle='boot'),
 'sailor':     dict(outfit='tee', shirt='#e9e9ee', stripes='#2a3a6a', hat='#2a3a6a', hatStyle='beanie', pants='#2a3a6a', beard='beard', hair='#8b5a2b', build='stocky'),
}
def cast(name, **ov):
    d = dict(P[name]); d.setdefault('skin', random.choice(PALE)); d.update(ov); d.setdefault('y0', .85); return d
def crowd(n, seed=1, kind='everyday', skins=None):
    """n varied passers-by. kind: everyday | tourists | workers | medieval"""
    R = random.Random(seed); out = []
    for _ in range(n):
        sk = R.choice(skins or PALE)
        if kind == 'tourists': d = dict(P['tourist' if R.random() < .5 else 'tourist_f'], shirt=R.choice(TEE), backpack=R.choice(TEE), hair=R.choice(HAIR), s=round(R.uniform(.92, 1.04), 2))
        elif kind == 'workers': d = dict(P['builder' if R.random() < .6 else 'engineer'], hair=R.choice(HAIR), s=round(R.uniform(.94, 1.05), 2))
        elif kind == 'medieval': d = dict(P[R.choice(['peasant', 'mason', 'peasant'])], shirt=R.choice(['#8a6a3a', '#7a6a50', '#6a7a4a', '#9a5a3a', '#6a5a7a']), hair=R.choice(HAIR), s=round(R.uniform(.92, 1.05), 2))
        else:
            d = dict(skin=sk, shirt=R.choice(TEE), accent=R.choice(TEE), pants=R.choice(PANTS), outfit=R.choice(['tee', 'jumper', 'jacket', 'hoodie', 'dress', 'tee']), hair=R.choice(HAIR),
                     hairStyle=R.choice(['short', 'short', 'fringe', 'quiff', 'long', 'bob', 'ponytail', 'bun', 'curly', 'wisp', 'bald']), build=R.choice(['slim', 'normal', 'normal', 'stocky']), s=round(R.uniform(.9, 1.05), 2),
                     lashes=R.random() < .3, glasses=('#333333' if R.random() < .15 else False), beard=R.choice(['none'] * 5 + ['moustache', 'beard', 'stubble']), shoeStyle=R.choice(['shoe', 'trainer', 'boot']))
            if R.random() < .3: d.update(hat=R.choice(TEE), hatStyle=R.choice(['flatcap', 'beanie', 'baseball', 'bobble']))
            if d['outfit'] == 'dress': d['beard'] = 'none'
        d['skin'] = sk; d['y0'] = .85; out.append(d)
    return out

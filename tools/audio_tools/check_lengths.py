# -*- coding: utf-8 -*-
"""How does each English clip's length compare to the 3DS slot it must fit?"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

import mca
from dgs2tool.arc import parse_arc
from encode_shouts import steam_english, decode_wav

ARCDIR = os.path.join(ROOT, 'basegame', 'rom', 'archive')
SEP = chr(92)

seen = {}
for f in sorted(os.listdir(ARCDIR)):
    if not f.endswith('.arc'):
        continue
    arc = parse_arc(open(os.path.join(ARCDIR, f), 'rb').read())
    for e in arc['entries']:
        norm = e.name.replace(SEP, '/')
        if '_v_' not in e.name or '/wav/' not in norm or e.data[:4] != b'MADP':
            continue
        n = norm.split('/')[-1].rsplit('.', 1)[0]
        if n in seen:
            continue
        src = steam_english(e.name)
        h = mca.parse_bytes(e.data)
        eng = decode_wav(src, h['rate'])
        seen[n] = (h['samples'], len(eng), h['rate'])

over = [(k, v) for k, v in seen.items() if v[1] > v[0]]
print('%d of %d unique shouts are LONGER in English' % (len(over), len(seen)))
if over:
    ex = sorted((v[1] - v[0]) / v[2] for _, v in over)
    print('overflow: min %.3fs  median %.3fs  max %.3fs'
          % (ex[0], ex[len(ex) // 2], ex[-1]))
    print('\nworst 8:')
    for k, v in sorted(over, key=lambda x: -(x[1][1] - x[1][0]))[:8]:
        print('  %-36s slot %.2fs  eng %.2fs  (+%.2fs)'
              % (k, v[0] / v[2], v[1] / v[2], (v[1] - v[0]) / v[2]))
    kinds = {}
    for k, _ in over:
        t = k.split('_v_')[1].replace('_jpn', '')
        kinds[t] = kinds.get(t, 0) + 1
    print('\nby type:', kinds)

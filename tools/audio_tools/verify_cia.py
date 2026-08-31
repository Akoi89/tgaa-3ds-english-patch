# -*- coding: utf-8 -*-
"""Final check: pull the shouts back out of the finished CIA and prove they are
the English audio, not the Japanese, by correlating against both sources."""
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

SHIPPED = os.path.join(ROOT, 'base_v12', 'vc13', 'dir', 'archive')
ORIG = os.path.join(ROOT, 'basegame', 'rom', 'archive')
SEP = chr(92)


def env(x, n=40):
    """Coarse RMS envelope -- compares shape without needing sample alignment."""
    x = x.astype(np.float64)
    if len(x) < n:
        return np.zeros(n)
    parts = np.array_split(x, n)
    e = np.array([np.sqrt((p ** 2).mean()) for p in parts])
    return e / (e.max() or 1.0)


def corr(a, b):
    a, b = a - a.mean(), b - b.mean()
    d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float((a * b).sum() / d) if d else 0.0


rows = []
for f in sorted(os.listdir(SHIPPED)):
    if not f.endswith('.arc') or not os.path.exists(os.path.join(ORIG, f)):
        continue
    new = parse_arc(open(os.path.join(SHIPPED, f), 'rb').read())
    old = {e.name: e.data for e in
           parse_arc(open(os.path.join(ORIG, f), 'rb').read())['entries']}
    for e in new['entries']:
        if '_v_' not in e.name or '/wav/' not in e.name.replace(SEP, '/'):
            continue
        if e.data[:4] != b'MADP':
            continue
        h = mca.parse_bytes(e.data)
        got = mca.decode(h)
        jp = mca.decode(mca.parse_bytes(old[e.name]))
        en = decode_wav(steam_english(e.name), h['rate'])
        rows.append((e.name.replace(SEP, '/').split('/')[-1].rsplit('.', 1)[0],
                     corr(env(got), env(en)), corr(env(got), env(jp))))

eng_wins = sum(1 for _, ce, cj in rows if ce > cj)
print('%d shouts pulled back out of the finished CIA' % len(rows))
print('closer to the ENGLISH source: %d' % eng_wins)
print('closer to the Japanese original: %d' % (len(rows) - eng_wins))
me = np.mean([c for _, c, _ in rows])
mj = np.mean([c for _, _, c in rows])
print('mean envelope correlation:  english %.3f   japanese %.3f' % (me, mj))
print()
for n, ce, cj in rows[:6]:
    print('  %-34s eng %.3f  jp %.3f' % (n, ce, cj))
print('\n%s' % ('OK' if eng_wins == len(rows) else 'CHECK THE MISMATCHES'))

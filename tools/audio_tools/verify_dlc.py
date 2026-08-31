# -*- coding: utf-8 -*-
"""Pull the gallery voices back out of the finished DLC CIA and prove they are
English, by correlating RMS envelopes against both the English source and the
Japanese original that shipped in v32."""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

import mca
from dlc_voices import english_for
from encode_shouts import decode_wav

SHIPPED = os.path.join(ROOT, 'dlc_v33')


def env(x, n=40):
    x = x.astype(np.float64)
    parts = np.array_split(x, n)
    e = np.array([np.sqrt((p ** 2).mean()) for p in parts])
    return e / (e.max() or 1.0)


def corr(a, b):
    a, b = a - a.mean(), b - b.mean()
    d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float((a * b).sum() / d) if d else 0.0


rows = []
for new_p in sorted(glob.glob(os.path.join(SHIPPED, 'v*_dir', 'sound', '*_v_*.mca'))):
    idx = os.path.basename(os.path.dirname(os.path.dirname(new_p)))[1:].split('_')[0]
    old_p = os.path.join(SHIPPED, 'idx%s_dir' % idx, 'sound', os.path.basename(new_p))
    # idx*_dir was edited in place, so read the Japanese from the v32 split instead
    h = mca.parse(new_p)
    got = mca.decode(h)
    en = decode_wav(english_for(new_p), h['rate'])
    jp_src = os.path.join(ROOT, 'video_inject', 'work',
                          'f%s_dir' % idx, 'sound', os.path.basename(new_p))
    if not os.path.exists(jp_src):
        jp_src = os.path.join(ROOT, 'video_inject', 'work',
                              'o%s_dir' % idx, 'sound', os.path.basename(new_p))
    jp = mca.decode(mca.parse(jp_src)) if os.path.exists(jp_src) else None
    ce = corr(env(got), env(en))
    cj = corr(env(got), env(jp)) if jp is not None else float('nan')
    rows.append((idx, os.path.basename(new_p), h['rate'], ce, cj))

print('%-5s %-22s %7s %8s %8s' % ('idx', 'track', 'Hz', 'eng', 'jp'))
for idx, n, r, ce, cj in rows:
    print('%-5s %-22s %7d %8.3f %8.3f' % (idx, n, r, ce, cj))
wins = sum(1 for *_, ce, cj in rows if not (cj == cj) or ce > cj)
print('\n%d/%d closer to the English source' % (wins, len(rows)))
print('OK' if wins == len(rows) else 'CHECK')

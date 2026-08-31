# -*- coding: utf-8 -*-
"""Check every rebuilt archive: entries intact, shouts decode, nothing else moved."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

import mca
from dgs2tool.arc import parse_arc

ARCDIR = os.path.join(ROOT, 'basegame', 'rom', 'archive')
OUTDIR = os.path.join(HERE, 'out')
SEP = chr(92)

bad = 0
shouts = 0
files = sorted(os.listdir(OUTDIR))
for f in files:
    old = parse_arc(open(os.path.join(ARCDIR, f), 'rb').read())
    new = parse_arc(open(os.path.join(OUTDIR, f), 'rb').read())
    o = {e.name: e.data for e in old['entries']}
    n = {e.name: e.data for e in new['entries']}
    if set(o) != set(n):
        print('  !! %s entry set changed' % f)
        bad += 1
        continue
    for name in o:
        is_shout = ('_v_' in name and '/wav/' in name.replace(SEP, '/')
                    and o[name][:4] == b'MADP')
        if is_shout:
            shouts += 1
            h = mca.parse_bytes(n[name])
            pcm = mca.decode(h)
            peak = int(np.abs(pcm).max())
            zc = float(np.mean(np.diff(np.signbit(pcm.astype(np.float64))) != 0))
            ok = (n[name][:4] == b'MADP' and h['rate'] == mca.parse_bytes(o[name])['rate']
                  and h['samples'] > 1000 and peak > 3000 and zc < 0.45)
            if not ok:
                print('  !! %s :: %s  rate=%d samples=%d peak=%d zc=%.2f'
                      % (f, name.split('/')[-1], h['rate'], h['samples'], peak, zc))
                bad += 1
        elif o[name] != n[name]:
            print('  !! %s :: %s changed but is not a shout' % (f, name))
            bad += 1

print('\n%d archives, %d shouts checked, %d problems' % (len(files), shouts, bad))
print('OK' if bad == 0 else 'FAILED')
sys.exit(1 if bad else 0)

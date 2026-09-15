# -*- coding: utf-8 -*-
"""Checks from relabelling_method.md, run on final/ against orig/ at the native 512x256.

  1. nothing outside the visible window (x 24..424, y 8..248) may change;
  2. changed-pixel bounding box per page (report; big boxes get a look);
  3. ground drift: median of the four visible-corner 12x12 patches, before vs after, unless a
     corner is inside a text area;
  4. panel-edge survival on see-through pages: horizontal edge strength along the top row of the
     marked box, after / before (the method calls < 0.45 damaged).
Writes review/verify_pages.txt.
"""
import io
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
boxes = json.load(open(os.path.join(HERE, 'boxes_medium.json')))


def load(d, p):
    return np.asarray(Image.open(os.path.join(HERE, d, p + '.png')).convert('RGB')).astype(int)


lines, fails = [], []
DIR = os.environ.get('VERIFY_DIR', 'final')
for f in sorted(os.listdir(os.path.join(HERE, DIR))):
    p = f[:-4]
    a, b = load('orig', p), load(DIR, p)
    ch = np.abs(a - b).max(axis=-1) > 0
    out = ch.copy(); out[VIS[1]:VIS[3], VIS[0]:VIS[2]] = False
    ys, xs = np.nonzero(ch)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None
    corners = []
    for cx, cy in ((VIS[0], VIS[1]), (VIS[2] - 12, VIS[1]), (VIS[0], VIS[3] - 12), (VIS[2] - 12, VIS[3] - 12)):
        pa = np.median(a[cy:cy + 12, cx:cx + 12].reshape(-1, 3), axis=0); pb = np.median(b[cy:cy + 12, cx:cx + 12].reshape(-1, 3), axis=0)
        corners.append(int(np.abs(pa - pb).max()))
    edge = ''
    if p in boxes and boxes[p]['mode'] == 'overlay':
        x0, y0, x1, y1 = boxes[p]['boxes'][0]
        def strength(img):
            g = img @ np.array([0.299, 0.587, 0.114])
            return float(np.abs(g[y0 - 2, x0:x1] - g[y0 + 2, x0:x1]).mean())
        sa, sb = strength(a), strength(b)
        edge = 'panel edge %.2f' % (sb / sa if sa > 1 else 1.0)
        if sa > 1 and sb / sa < 0.45:
            fails.append('%s panel edge %.2f' % (p, sb / sa))
    if out.any():
        fails.append('%s changed %d px outside the visible window' % (p, int(out.sum())))
    lines.append('%-16s changed %6d px  bbox %s  outside-window %d  corner drift %s  %s' % (
        p, int(ch.sum()), bbox, int(out.sum()), corners, edge))
report = '\n'.join(lines) + '\n\nFAILS:\n' + ('\n'.join(fails) if fails else 'none') + '\n'
io.open(os.path.join(HERE, 'review', 'verify_pages%s.txt' % ('' if DIR == 'final' else '_' + DIR)), 'w', encoding='utf-8').write(report)
print(report[-3000:])

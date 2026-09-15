# -*- coding: utf-8 -*-
"""Gate from wash_addendum.md: on the see-through pages, pixels that were never ink in either language
must come through unchanged. sel = marked text rectangle & not Japanese glyphs (median-9 residual > 16,
dilated 5x5, on the original) & not English glyphs (residual > 12, dilated 3x3, on the output).
Reports MAE of output vs original on sel for each page folder given; target < 0.5.

    python gate_mae.py final final_nowash final_lama final_lama2
Writes review/gate_mae.txt.
"""
import io
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
LIMIT = 0.5


def dark(img, thr):
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return (cv2.medianBlur(g, 9).astype(int) - g.astype(int)) > thr


def main():
    dirs = sys.argv[1:] or ['final']
    boxes = json.load(open(os.path.join(HERE, 'boxes_medium.json')))
    pages = open(os.path.join(HERE, '_overlay_pages.txt')).read().strip().split(',')
    rows = []
    for p in pages:
        o = np.asarray(Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB'))
        bs = boxes[p]['boxes']
        rect = np.zeros(o.shape[:2], bool)
        rect[min(b[1] for b in bs):max(b[3] for b in bs), min(b[0] for b in bs):max(b[2] for b in bs)] = True
        jp = cv2.dilate(dark(o, 16).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        r = []
        for d in dirs:
            v = np.asarray(Image.open(os.path.join(HERE, d, p + '.png')).convert('RGB'))
            en = cv2.dilate(dark(v, 12).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            sel = rect & ~jp & ~en
            r.append(float(np.abs(v[sel].astype(int) - o[sel].astype(int)).mean()))
        rows.append((p, r))
    head = '%-16s' % 'page' + ''.join('%14s' % d for d in dirs)
    lines = [head] + ['%-16s' % p + ''.join('%14.2f' % x for x in r) for p, r in rows]
    arr = np.array([r for _, r in rows])
    lines.append('%-16s' % 'median' + ''.join('%14.2f' % x for x in np.median(arr, 0)))
    lines.append('%-16s' % 'max' + ''.join('%14.2f' % x for x in arr.max(0)))
    lines.append('%-16s' % ('pass < %.1f' % LIMIT) + ''.join('%11d/%d' % ((arr[:, i] < LIMIT).sum(), len(rows)) for i in range(len(dirs))))
    rep = '\n'.join(lines) + '\n'
    io.open(os.path.join(HERE, 'review', 'gate_mae.txt'), 'w', encoding='utf-8').write(
        'MAE vs original on never-ink pixels in the text rectangle (wash_addendum.md gate)\n' + rep)
    print(rep)


if __name__ == '__main__':
    main()

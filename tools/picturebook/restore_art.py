# -*- coding: utf-8 -*-
"""Give back art that the plain-page typesetter (typeset.py) blanked (user, 2026-09-15: Eggert's coat,
cats' feet and similar were cut off).

typeset.py fills each PLAIN block's box (+2 px) with the background colour. Where artwork reaches into
that box from outside, the fill cut it off. Here, per block: non-background shapes in the ORIGINAL that
continue outside the filled rectangle are art; their pixels inside the rectangle are restored wherever
the typeset page still shows the bare fill colour there (never over the English ink).

    python restore_art.py [src=typeset_bahn] [dst=typeset_bahn2]
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
BG = np.array((255, 247, 223))


def restore(p, src):
    orig = np.asarray(Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB')).astype(int)
    page = np.asarray(Image.open(os.path.join(HERE, src, p + '.png')).convert('RGB')).copy()
    blocks = [b['box'] for b in json.load(open(os.path.join(HERE, 'blocks.json')))[p] if b['kind'] == 'PLAIN']
    nonbg = (np.abs(orig - BG).max(-1) > 10).astype(np.uint8)
    bare = (np.abs(page.astype(int) - BG).max(-1) == 0)
    total = 0
    for x0, y0, x1, y1 in blocks:
        rx0, ry0 = max(VIS[0], x0 - 2), max(VIS[1], y0 - 2)
        rx1, ry1 = min(VIS[2], x1 + 2), min(VIS[3], y1 + 2)
        rect = np.zeros_like(nonbg); rect[ry0:ry1, rx0:rx1] = 1
        win = np.zeros_like(nonbg); win[max(0, ry0 - 10):ry1 + 10, max(0, rx0 - 10):rx1 + 10] = 1
        n, lab = cv2.connectedComponents(nonbg & win, connectivity=8)
        ids = np.unique(lab[(rect == 0) & (win == 1) & (nonbg == 1)])
        art = np.zeros_like(bare)
        for i in ids[ids > 0]:
            inside = (lab == i) & (rect == 1)
            ys = np.nonzero(inside)[0]
            # art tips reach a few px into the rectangle (paws, hems); a shape reaching deeper is a
            # glyph fused with art (Mael page: the heading's last characters touch the collar)
            if len(ys) and ys.max() - ys.min() <= 10:
                art |= inside & bare
        page[art] = orig[art]
        total += int(art.sum())
    return page, total


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'typeset_bahn'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'typeset_bahn2'
    os.makedirs(os.path.join(HERE, dst), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(HERE, src))):
        if not f.endswith('.png') or f.startswith('_'):
            continue
        p = f[:-4]
        page, n = restore(p, src)
        Image.fromarray(page.astype(np.uint8)).save(os.path.join(HERE, dst, f))
        print('%-16s %5d art px restored' % (p, n))


if __name__ == '__main__':
    main()

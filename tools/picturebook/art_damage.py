# -*- coding: utf-8 -*-
"""Sweep for artwork the erase changed (user review 2026-09-15 found cut shoes, hats, coat corners).

Per page, damage = pixels whose value changed clearly (> 40 on some channel) versus the original, that were
NOT Japanese ink in the original (median-9 residual > 14 or near-ink colour, grown 2 px) and are NOT English
ink now (near the text ink colour). Such pixels are artwork or background that was repainted. Writes
review/art_damage.txt (count + bounding box per page) and review/art_damage_N.png sheets (original |
page with damage in red) for the pages over the threshold.

    python art_damage.py [folder=final_v3] [threshold=25]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
INK = np.array((48, 40, 16), float)


def damage(p, folder):
    o = np.asarray(Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB')).astype(int)
    f = np.asarray(Image.open(os.path.join(HERE, folder, p + '.png')).convert('RGB')).astype(int)
    g = cv2.cvtColor(o.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(int)
    jp = (cv2.medianBlur(g.astype(np.uint8), 9).astype(int) - g) > 14
    jp |= (np.linalg.norm(o - INK, axis=-1) < 50)
    jp = cv2.dilate(jp.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    en = cv2.dilate((np.linalg.norm(f - INK, axis=-1) < 70).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ch = np.abs(f - o).max(-1) > 40
    d = ch & ~jp & ~en
    d[:VIS[1]] = d[VIS[3]:] = False; d[:, :VIS[0]] = d[:, VIS[2]:] = False
    # ignore isolated single pixels
    d = cv2.morphologyEx(d.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    return d, o, f


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else 'final_v3'
    thr = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    F = ImageFont.truetype('segoeui.ttf', 14)
    lines, tiles = [], []
    for fn in sorted(os.listdir(os.path.join(HERE, folder))):
        if not fn.endswith('.png'):
            continue
        p = fn[:-4]
        d, o, f = damage(p, folder)
        n = int(d.sum())
        ys, xs = np.nonzero(d)
        bb = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if n else None
        lines.append('%-16s %5d px  %s' % (p, n, bb))
        if n >= thr:
            vis = f.astype(np.uint8).copy(); vis[d] = (255, 0, 0)
            a = Image.fromarray(o.astype(np.uint8)).crop(VIS); b = Image.fromarray(vis).crop(VIS)
            t = Image.new('RGB', (810, 262), (30, 30, 30)); t.paste(a, (0, 20)); t.paste(b, (410, 20))
            ImageDraw.Draw(t).text((2, 2), '%s  %d px repainted outside Japanese/English ink (red)' % (p, n), fill=(255, 220, 120), font=F)
            tiles.append(t)
    open(os.path.join(HERE, 'review', 'art_damage.txt'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    for k in range(0, len(tiles), 4):
        part = tiles[k:k + 4]
        s = Image.new('RGB', (810, 266 * len(part)), (30, 30, 30))
        for i, t in enumerate(part):
            s.paste(t, (0, i * 266))
        s.save(os.path.join(HERE, 'review', 'art_damage_%d.png' % (k // 4 + 1)))
    print('%d pages over %d px -> %d sheets' % (len(tiles), thr, (len(tiles) + 3) // 4))


if __name__ == '__main__':
    main()

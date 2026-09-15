# -*- coding: utf-8 -*-
"""Find the typed Japanese commentary blocks on each Picture Book page and classify them.

Measured 2026-09-14: the page background is exactly (255,247,223) and the typed ink is (48,40,16);
anti-aliased glyph edges are blends of the two, i.e. colours on the straight line between them.
A pixel is 'ink-like' if it sits within DIST of that line and at least T_MIN of the way to the ink.
Ink-like pixels are merged into lines and lines into blocks. A block is PLAIN when every pixel of
its padded box is either background or ink-like (so erasing it cannot damage art); otherwise ART.

    python detect_text.py            -> blocks.json + debug/detect_NN.png (green PLAIN, red ART)
"""
import json
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BG = np.array([255, 247, 223], float)
INK = np.array([48, 40, 16], float)
DIST, T_MIN = 14.0, 0.18
VIS = (24, 8, 424, 248)


def inklike(a):
    d = INK - BG
    t = ((a - BG) @ d) / (d @ d)
    proj = BG + np.clip(t, 0, 1)[..., None] * d
    off = np.linalg.norm(a - proj, axis=-1)
    return (off < DIST) & (t > T_MIN), (np.linalg.norm(a - BG, axis=-1) < 6)


def blocks_of(page):
    a = np.asarray(Image.open(os.path.join(HERE, 'orig', page + '.png')).convert('RGB')).astype(float)
    ink, bg = inklike(a)
    vis = np.zeros(ink.shape, bool)
    vis[VIS[1]:VIS[3], VIS[0]:VIS[2]] = True
    ink &= vis
    # glyph-scale components only: drop big ink blobs (lines of art) and specks
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        x, y, w, h, area = st[i]
        keep[i] = h <= 14 and w <= 80 and area >= 2   # height, not width: a line's fringes fuse sideways
    glyph = keep[lab]
    lab_g = np.where(glyph, lab, 0)
    # merge glyphs into lines, then lines into blocks
    line = cv2.dilate(glyph.astype(np.uint8), np.ones((3, 9), np.uint8))
    blk = cv2.dilate(line, np.ones((7, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(blk, 8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        m = (lab == i) & glyph
        gy, gx = np.nonzero(m)
        if len(gx) < 30 or w < 16 or h < 6:
            continue
        x0, y0, x1, y1 = int(gx.min()), int(gy.min()), int(gx.max()) + 1, int(gy.max()) + 1
        ncomp = len(np.unique(lab_g[m]))
        main = len(gx) >= 250 and (x1 - x0) >= 50 and ncomp >= 8
        prof = m[y0:y1, x0:x1].any(axis=1)
        runs = int(np.sum(prof[1:] & ~prof[:-1]) + prof[0])
        px0, py0, px1, py1 = max(VIS[0], x0 - 3), max(VIS[1], y0 - 3), min(VIS[2], x1 + 3), min(VIS[3], y1 + 3)
        # PLAIN test: inside the padded box, every non-background pixel belongs to a glyph-sized speck
        # (a line's glyph fringes touch, so judge shapes by HEIGHT: text lines stay under 16 px tall,
        #  art does not; and the pixels must be ink-coloured, i.e. on the background-to-ink line)
        sub = a[py0:py1, px0:px1]
        nonbg = (np.linalg.norm(sub - BG, axis=-1) > 8)
        d = INK - BG
        tt = ((sub - BG) @ d) / (d @ d)
        off = np.linalg.norm(sub - (BG + np.clip(tt, 0, 1)[..., None] * d), axis=-1)
        k, lb, s2, _ = cv2.connectedComponentsWithStats(nonbg.astype(np.uint8), 8)
        tall = np.zeros(k, bool)
        for j in range(1, k):
            tall[j] = s2[j, 3] > 15
        bad = nonbg & (tall[lb] | (off > 24))
        clean = 1.0 - bad.sum() / float(max(1, int(nonbg.sum())))
        out.append(dict(box=[x0, y0, x1, y1], lines=runs, glyph_px=int(len(gx)), clean=round(clean, 4),
                        kind='PLAIN' if clean >= 0.99 else 'ART', role='main' if main else 'small'))
    out.sort(key=lambda b: (b['box'][1], b['box'][0]))
    # a small PLAIN block within 30 px above/below a main PLAIN block and overlapping it sideways is part of it
    mains = [b for b in out if b['role'] == 'main' and b['kind'] == 'PLAIN']
    for b in out:
        if b['role'] != 'small' or b['kind'] != 'PLAIN':
            continue
        for m in mains:
            vgap = max(m['box'][1] - b['box'][3], b['box'][1] - m['box'][3], 0)
            hover = min(m['box'][2], b['box'][2]) - max(m['box'][0], b['box'][0])
            if vgap <= 30 and hover > 0:
                b['role'] = 'attached'
    return [b for b in out if b['role'] != 'small']


def main():
    pages = sorted(f[:-4] for f in os.listdir(os.path.join(HERE, 'orig')) if '_design_' in f)
    res = {p: blocks_of(p) for p in pages}
    json.dump(res, open(os.path.join(HERE, 'blocks.json'), 'w'), indent=1)
    os.makedirs(os.path.join(HERE, 'debug'), exist_ok=True)
    per = 9
    for s in range(0, len(pages), per):
        chunk = pages[s:s + per]
        sheet = Image.new('RGB', (3 * 400, 3 * 256), (0, 0, 0))
        for i, p in enumerate(chunk):
            im = Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB')
            d = ImageDraw.Draw(im)
            for b in res[p]:
                d.rectangle(b['box'], outline=(0, 200, 0) if b['kind'] == 'PLAIN' else (230, 0, 0), width=2)
            d.text((VIS[0] + 2, VIS[1] + 1), p, fill=(0, 0, 255))
            sheet.paste(im.crop(VIS), ((i % 3) * 400, (i // 3) * 256))
        sheet.save(os.path.join(HERE, 'debug', 'detect_%02d.png' % (s // per + 1)))
    plain = sum(1 for p in pages if res[p] and all(b['kind'] == 'PLAIN' for b in res[p]))
    none = [p for p in pages if not res[p]]
    print('%d pages: %d all-PLAIN, %d with an ART block, %d with nothing found %s' % (
        len(pages), plain, len(pages) - plain - len(none), len(none), none))


if __name__ == '__main__':
    main()

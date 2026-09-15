# -*- coding: utf-8 -*-
"""Gap between each see-through panel's top edge and the English first line.

On the ORIGINAL page, the panel top is the row with the strongest step to lighter across columns where
there is art above (lum < 200), searched in the 14 rows above the English text top. The English text top
is the first row of the typeset area holding >= 3 ink-coloured pixels in the given page folder.
Writes panel_top.json {page: {panel_top, text_top, gap}} and review/panel_top_check_N.png
(red = panel top, green = text top).

    python panel_top.py [folder=final]
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
boxes = json.load(open(os.path.join(HERE, 'boxes_medium.json')))
pages = [p for p in sorted(boxes) if boxes[p]['mode'] == 'overlay']
INK = np.array((48, 40, 16), float)


def lum(img):
    return img.astype(float) @ np.array([0.299, 0.587, 0.114])


def measure(p, folder):
    o = np.asarray(Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB'))
    f = np.asarray(Image.open(os.path.join(HERE, folder, p + '.png')).convert('RGB'))
    bs = boxes[p]['boxes']
    x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs); x1 = max(b[2] for b in bs); y1 = max(b[3] for b in bs)
    ink = (np.linalg.norm(f.astype(float) - INK, axis=-1) < 60) & (np.abs(f.astype(int) - o.astype(int)).max(-1) > 20)
    rows = np.nonzero(ink[y0 - 6:y1, x0:x1].sum(1) >= 3)[0]
    tt = int(rows[0]) + y0 - 6
    L = lum(o)
    best = (0.0, None)
    for y in range(max(9, tt - 14), tt + 1):
        up, dn = L[y - 1, x0:x1], L[y, x0:x1]
        sc = float(np.clip(dn - up, 0, None)[up < 200].sum())
        if sc > best[0]:
            best = (sc, y)
    return best[1], tt, (x0, y0, x1)


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else 'final'
    F = ImageFont.truetype('segoeui.ttf', 14)
    res, tiles = {}, []
    for p in pages:
        pt, tt, (x0, y0, x1) = measure(p, folder)
        res[p] = {'panel_top': pt, 'text_top': tt, 'gap': tt - pt}
        print('%-16s panel top %3d  text top %3d  gap %d' % (p, pt, tt, tt - pt))
        fin = Image.open(os.path.join(HERE, folder, p + '.png')).convert('RGB')
        crop = (x0, max(8, tt - 20), min(424, x0 + 200), tt + 12)
        im = fin.crop(crop).resize(((crop[2] - crop[0]) * 3, (crop[3] - crop[1]) * 3), Image.NEAREST)
        d = ImageDraw.Draw(im)
        d.line([(0, (pt - crop[1]) * 3), (30, (pt - crop[1]) * 3)], fill=(255, 0, 0), width=2)
        d.line([(0, (tt - crop[1]) * 3), (30, (tt - crop[1]) * 3)], fill=(0, 200, 0), width=2)
        t = Image.new('RGB', (im.width, im.height + 18), (30, 30, 30)); t.paste(im, (0, 18))
        ImageDraw.Draw(t).text((2, 1), '%s  panel %d  text %d  gap %d' % (p, pt, tt, tt - pt), fill=(255, 220, 120), font=F)
        tiles.append(t)
    json.dump(res, open(os.path.join(HERE, 'panel_top.json'), 'w'), indent=1)
    for k in range(0, len(tiles), 8):
        part = tiles[k:k + 8]
        W = max(t.width for t in part); h = max(t.height for t in part)
        s = Image.new('RGB', (2 * W + 10, 4 * (h + 8)), (30, 30, 30))
        for i, t in enumerate(part):
            s.paste(t, ((i % 2) * (W + 10), (i // 2) * (h + 8)))
        s.save(os.path.join(HERE, 'review', 'panel_top_check_%d.png' % (k // 8 + 1)))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Find leftover Japanese ink on the translated pages: pixels that were Japanese glyph ink in the original
(median-9 residual > 16, neutral grey: saturation < 20) and are STILL dark neutral grey in the page
(lum < 130, saturation < 20). The English ink is warm (48,40,16), saturation 32, so it never counts.
    python jp_leftover.py [folder=final_v5]
"""
import os, sys, json
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
folder = sys.argv[1] if len(sys.argv) > 1 else 'final_v5'
F = ImageFont.truetype('segoeui.ttf', 14)
tiles, rows = [], []
for f in sorted(os.listdir(os.path.join(HERE, folder))):
    p = f[:-4]
    o = np.asarray(Image.open(os.path.join(HERE, 'orig', f)).convert('RGB')).astype(int)
    v = np.asarray(Image.open(os.path.join(HERE, folder, f)).convert('RGB')).astype(int)
    g = cv2.cvtColor(o.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(int)
    jp = ((cv2.medianBlur(g.astype(np.uint8), 9).astype(int) - g) > 16) & ((o.max(-1) - o.min(-1)) < 20)
    lum = v @ np.array([0.299, 0.587, 0.114]); sat = v.max(-1) - v.min(-1)
    still = jp & (lum < 130) & (sat < 20) & (np.abs(v - o).max(-1) <= 12)
    still[:VIS[1]] = still[VIS[3]:] = False; still[:, :VIS[0]] = still[:, VIS[2]:] = False
    # only where the page was changed nearby (text areas), so untouched art with grey lines is ignored
    changed = cv2.dilate((np.abs(v - o).max(-1) > 20).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    still &= changed
    n = int(still.sum())
    rows.append((n, p))
    if n >= 15:
        vis = v.astype(np.uint8).copy(); vis[cv2.dilate(still.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)] = (255, 0, 0)
        t = Image.new('RGB', (400, 260), (30, 30, 30)); t.paste(Image.fromarray(vis).crop(VIS), (0, 20))
        ImageDraw.Draw(t).text((2, 2), '%s %d px' % (p, n), fill=(255, 220, 120), font=F); tiles.append(t)
for n, p in sorted(rows, reverse=True)[:25]:
    print('%5d %s' % (n, p))
for k in range(0, len(tiles), 6):
    part = tiles[k:k + 6]; s = Image.new('RGB', (2 * 406, 3 * 266), (30, 30, 30))
    for i, t in enumerate(part): s.paste(t, ((i % 2) * 406, (i // 2) * 266))
    s.save(os.path.join(HERE, 'review', 'jp_leftover_%d.png' % (k // 6 + 1)))
print(len(tiles), 'pages flagged')

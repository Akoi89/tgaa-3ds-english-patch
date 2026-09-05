"""Compose the English HOME-banner logo texture for TGAA1 / TGAA2.

    python compose_logo.py <orig_tex.png> <logo.webp> <out.png> [--scale S] [--dy N]

The Japanese logo's alpha bounding box is measured from orig_tex.png; the English
logo (RGBA, official art) is cropped to its own alpha, scaled to the same WIDTH
(times --scale, default 1.0, aspect kept), and centred in that box (+--dy rows).
Everything outside the box is cleared to transparent white like the original.
Prints the placement numbers.
"""
import sys
import numpy as np
from PIL import Image

args = sys.argv[1:]
scale = 1.0; dy = 0; stretch = 1.0
if '--scale' in args:
    i = args.index('--scale'); scale = float(args[i + 1]); del args[i:i + 2]
if '--stretch' in args:
    i = args.index('--stretch'); stretch = float(args[i + 1]); del args[i:i + 2]
if '--dy' in args:
    i = args.index('--dy'); dy = int(args[i + 1]); del args[i:i + 2]
orig, logo, out = args[:3]

o = np.asarray(Image.open(orig).convert('RGBA'))
H, W = o.shape[:2]
ys, xs = np.nonzero(o[..., 3] > 16)
bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
print('JP logo box x %d..%d y %d..%d (%dx%d) in %dx%d' % (bx0, bx1 - 1, by0, by1 - 1, bx1 - bx0, by1 - by0, W, H))

L = Image.open(logo).convert('RGBA'); a = np.asarray(L)
ys, xs = np.nonzero(a[..., 3] > 8)
L = L.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
tw = int(round((bx1 - bx0) * scale)); th = max(1, int(round(L.height * tw / L.width * stretch)))
if th > H:
    th = H; tw = int(round(L.width * th / L.height))
Ls = L.resize((tw, th), Image.LANCZOS)
ox = bx0 + ((bx1 - bx0) - tw) // 2; oy = by0 + ((by1 - by0) - th) // 2 + dy
ox = max(0, min(W - tw, ox)); oy = max(0, min(H - th, oy))
canvas = Image.new('RGBA', (W, H), (255, 255, 255, 0))
canvas.alpha_composite(Ls, (ox, oy))
canvas.save(out)
print('English logo %dx%d source -> %dx%d placed at (%d,%d), box y %d..%d; wrote %s' % (L.width, L.height, tw, th, ox, oy, oy, oy + th - 1, out))

# -*- coding: utf-8 -*-
"""Drop the externally-supplied banner artwork into the three DLC textures.

The .tex is 512x256 but only x24..423, y8..247 (400x240) is opaque -- that
rectangle is what the game draws. Inside it each banner has an outer margin
and then the card itself; we keep the original margin pixels and scale the
supplied image's card into the original's card box, so in-game framing is
byte-for-byte where Capcom put it.

    python banner_swap.py preview   -> *_swap.png for review
    python banner_swap.py apply     -> rewrites the .tex files
"""
import os, sys

import numpy as np
from PIL import Image

from banner_translate import load, save_tex

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('BANNER_OUT', HERE)
# folder of replacement banner art; override with BANNER_ART
SRC = os.environ.get('BANNER_ART', 'banner_art')

VIS = (24, 8, 424, 248)          # opaque rectangle of every banner texture

JOBS = [
    # name, supplied image, texture in, texture out, card box in visible area
    ('sc00', 'Gemini_Generated_Image_f9jggpf9jggpf9jg.jpg',
     'idx2_v6_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex',
     'idx2_v7_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex', (6, 6, 400, 240)),
    ('sc01', 'Gemini_Generated_Image_t6bpubt6bpubt6bp.jpg',
     'idx2_v6_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex',
     'idx2_v7_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex', (6, 5, 400, 240)),
    ('cost', 'Gemini_Generated_Image_tusq6tusq6tusq6t.jpg',
     'idx1_dir/dlc_costumepack_BM_NOMIP_HQ.tex',
     'idx1_v7_dir/dlc_costumepack_BM_NOMIP_HQ.tex', (0, 11, 400, 240)),
]


def card_box(img, thresh=60, frac=0.15):
    """bbox of the card inside a supplied image (outer flat margin removed)"""
    a = np.asarray(img.convert('RGB')).astype(int)
    corner = a[5:25, 5:25].reshape(-1, 3).mean(axis=0)
    d = np.abs(a - corner).sum(axis=2)
    xs = np.where((d > thresh).mean(axis=0) > frac)[0]
    ys = np.where((d > thresh).mean(axis=1) > frac)[0]
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def run(apply):
    for name, src, tex_in, tex_out, box in JOBS:
        header, rgb, alpha = load(os.path.join(HERE, tex_in))
        img = Image.open(os.path.join(SRC, src)).convert('RGB')
        cb = card_box(img)
        x0, y0, x1, y1 = box
        sx = (cb[2] - cb[0]) / float(x1 - x0)
        sy = (cb[3] - cb[1]) / float(y1 - y0)
        vx0, vy0 = VIS[0], VIS[1]
        out = rgb.copy()
        if name == 'cost':
            # their margin is black: keep ours, but repaint the maroon band
            # rows first (the JP title tops poke into them on the original)
            for y in range(8, 21):
                seg = np.concatenate([rgb[y, 44:68], rgb[y, 400:424]], axis=0)
                med = np.median(seg, axis=0).astype(np.uint8)
                out[y, 24:424] = med
            card = img.crop(cb).resize((x1 - x0, y1 - y0), Image.LANCZOS)
            out[vy0 + y0:vy0 + y1, vx0 + x0:vx0 + x1] = np.asarray(card)
        else:
            # map their WHOLE image (ribbon tails included) over the whole
            # visible area, anchored so their card lands on the original's
            # card box
            sx0 = cb[0] - x0 * sx
            sy0 = cb[1] - y0 * sy
            sx1 = cb[2] + (400 - x1) * sx
            sy1 = cb[3] + (240 - y1) * sy
            crop = img.crop((int(round(sx0)), int(round(sy0)),
                             int(round(sx1)), int(round(sy1))))
            full = crop.resize((400, 240), Image.LANCZOS)
            out[vy0:vy0 + 240, vx0:vx0 + 400] = np.asarray(full)
        Image.fromarray(out).save(os.path.join(OUT, name + '_swap.png'))
        Image.fromarray(out[VIS[1]:VIS[3], VIS[0]:VIS[2]]).save(
            os.path.join(OUT, name + '_swap_view.png'))
        if apply:
            save_tex(os.path.join(HERE, tex_out), header, out, alpha)
        print('%s: card %s -> %s%s' % (name, cb, box, '  APPLIED' if apply else ''))


if __name__ == '__main__':
    run('apply' in sys.argv)

# -*- coding: utf-8 -*-
"""Rebuild TGAA2's three DLC banners, stamping the version on the costume pack only.

    python stamp_dlc_banners.py <banner_src_dir> <out_dir> "DLC 1.0.5" [--stamp-on cost]

<banner_src_dir> is dlc_story_audit/tgaa2/dlc, which holds the finished,
UNSTAMPED banners banner_swap.py produced from the user's Gemini art:
    idx2_v7_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex   story card, content 2
    idx2_v7_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex   story card, content 2
    idx1_v7_dir/dlc_costumepack_BM_NOMIP_HQ.tex         costume pack, content 1
Verified: outside the stamp box they match the shipped 1.0.4 textures to 0.000,
so they are the shipped art minus the stamp. RGB AND ALPHA both come from these
-- never from a shipped texture, whose alpha carries the old stamp's silhouette
(that mistake put a dark ghost of "DLC 1.0.4" on five TGAA1 pages).

MEASURED off the shipped costume banner, not guessed:
    ink bbox   x 358..416, y 233..244  (59x12 incl. a 1 px outline)
    fill       (235, 233, 229)   outline (20, 15, 10)
    font       Segoe UI 14 px -> 58x10 glyph box, the same family as TGAA1's stamp
The drawable area of every banner is x 24..423, y 8..247; the stamp sits in its
bottom-right corner.
"""
import os
import argparse
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from tex_rgba8 import decode_rgba8, encode_rgba8      # noqa: E402

FONT = os.environ.get('STAMP_FONT', 'C:/Windows/Fonts/segoeui.ttf')
SIZE = 14
FILL = (235, 233, 229, 255)
OUTLINE = (20, 15, 10, 255)
TARGET = (358, 233)               # where the ink's top-left must land
BANNERS = {
    'sc00': ('idx2_v7_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex', 'UI/tex'),
    'sc01': ('idx2_v7_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex', 'UI/tex'),
    'cost': ('idx1_v7_dir/dlc_costumepack_BM_NOMIP_HQ.tex', ''),
}


def stamp(rgba, text):
    """Draw, measure where the ink landed, and nudge so it lands on TARGET."""
    f = ImageFont.truetype(FONT, SIZE)

    def render(origin):
        im = Image.fromarray(rgba.copy(), 'RGBA')
        d = ImageDraw.Draw(im)
        x, y = origin
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    d.text((x + dx, y + dy), text, font=f, fill=OUTLINE)
        d.text((x, y), text, font=f, fill=FILL)
        return np.asarray(im)

    origin = TARGET
    for _ in range(3):                      # converge on the measured box
        out = render(origin)
        diff = np.abs(out[:, :, :3].astype(int) - rgba[:, :, :3].astype(int)).max(axis=2)
        ys, xs = np.nonzero(diff > 24)
        dx, dy = TARGET[0] - xs.min(), TARGET[1] - ys.min()
        if dx == 0 and dy == 0:
            break
        origin = (origin[0] + dx, origin[1] + dy)
    return out, (xs.min(), xs.max(), ys.min(), ys.max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out')
    ap.add_argument('version')
    ap.add_argument('--stamp-on', default='cost', choices=sorted(BANNERS))
    a = ap.parse_args()
    for key, (rel, sub) in BANNERS.items():
        blob = open(os.path.join(a.src, *rel.split('/')), 'rb').read()
        rgb, alpha = decode_rgba8(blob)
        rgba = np.dstack([rgb, alpha])
        tag = 'clean'
        if key == a.stamp_on:
            rgba, box = stamp(rgba, a.version)
            tag = 'STAMPED "%s" at x %d..%d y %d..%d' % ((a.version,) + box)
        od = os.path.join(a.out, key, *([sub] if sub else []))
        os.makedirs(od, exist_ok=True)
        op = os.path.join(od, os.path.basename(rel))
        open(op, 'wb').write(encode_rgba8(blob, rgba[:, :, :3], rgba[:, :, 3]))
        print('  %-4s -> %-42s %s' % (key, os.path.relpath(op, a.out), tag))


if __name__ == '__main__':
    main()

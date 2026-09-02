# -*- coding: utf-8 -*-
"""Rebuild TGAA1's DLC magazine covers, stamping the version on ONE of them.

    python stamp_dlc_covers.py <cover_build_dir> <donor_tree> <out_dir> "DLC 1.0.7"
    python stamp_dlc_covers.py ... --stamp-on 0        # which issue carries it

WHY THIS EXISTS
All 14 magazine covers carried a painted-on `DLC 1.0.4`. Bumping the version
therefore meant editing 14 textures and rebuilding ~10 encrypted DLC contents
every release -- so in practice it never got bumped, and the number on screen
drifted away from the filename until it was actively misleading.

The fix is to stamp ONE cover, Episode 0, which is the issue the DLC page opens
on. The other 13 are rebuilt clean from `cover_build/`'s PNGs, which are the
original art with no stamp (verified: outside the stamp corner they match the
shipped textures to within 0.017 of a grey level).

MEASURED CONSTANTS, taken off the shipped aoc00 rather than guessed:
    ink bounding box  x 34..94, y 13..25   -> 61 x 13 px for a 9-character string
    fill              (239, 235, 229)      warm off-white
    outline           (15, 10, 8)          1 px, all eight directions
    font              Segoe UI 15 px       renders 60 x 11, plus outline = 61 x 13
    background under  (20, 33, 43)         dark blue-grey

The alpha channel MUST be carried through. texture_sweep's decoder drops it, and
writing 255 everywhere turns transparent pixels opaque -- see tex_rgba8.py, whose
round-trip is byte-exact on all 14 covers and is the gate for this script.
"""
import os
import argparse
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from tex_rgba8 import decode_rgba8, encode_rgba8      # noqa: E402

ANCHOR = (34, 8)                  # PIL text origin; ink then lands at y 13..25
FONT = os.environ.get('STAMP_FONT', 'C:/Windows/Fonts/segoeui.ttf')
SIZE = 15
FILL = (239, 235, 229)
OUTLINE = (15, 10, 8)
COVERS = 14
TEX = 'aoc%02d_magazine_BM_NOMIP_HQ.tex'


def source_png(cover_dir, n):
    # ph_out is ALREADY CLEAN. An earlier version of this file preferred an
    # inpainted 'ph_clean' because the corner measured std 47 and that was
    # read as a version stamp. It is the magazine's own title, 'THE RANDST'.
    # The inpaint clipped the top of that title and fixed nothing. Dump the
    # covers and LOOK before concluding anything about them: dump_covers.py
    for sub in ('simple_out', 'ph_out'):
        p = os.path.join(cover_dir, sub, 'aoc%02d.png' % n)
        if os.path.exists(p):
            return p
    return None


def draw_stamp(rgb, text):
    im = Image.fromarray(rgb.copy())
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, SIZE)
    x, y = ANCHOR
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                d.text((x + dx, y + dy), text, font=f, fill=OUTLINE)
    d.text((x, y), text, font=f, fill=FILL)
    return np.asarray(im)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('covers')
    ap.add_argument('donors', help='tree of extracted DLC contents (x_cNN/tex/...)')
    ap.add_argument('out')
    ap.add_argument('version', help='e.g. "DLC 1.0.7"')
    ap.add_argument('--stamp-on', type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    made = 0
    for n in range(COVERS):
        png = source_png(a.covers, n)
        donor = os.path.join(a.donors, 'x_c%02d' % (n + 2), 'tex', TEX % n)
        if not (png and os.path.exists(donor)):
            print('  aoc%02d SKIPPED (%s missing)'
                  % (n, 'png' if not png else 'donor')); continue
        blob = open(donor, 'rb').read()
        _, alpha = decode_rgba8(blob)          # keep Capcom's alpha
        rgb = np.asarray(Image.open(png).convert('RGB'))
        tag = 'clean'
        if n == a.stamp_on:
            rgb = draw_stamp(rgb, a.version)
            tag = 'STAMPED "%s"' % a.version
        out = os.path.join(a.out, TEX % n)
        open(out, 'wb').write(encode_rgba8(blob, rgb, alpha))
        made += 1
        print('  aoc%02d -> %s  %s' % (n, os.path.basename(out), tag))
    print('  wrote %d textures to %s' % (made, a.out))


if __name__ == '__main__':
    main()

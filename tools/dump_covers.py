# -*- coding: utf-8 -*-
"""Dump the DLC magazine covers out of a CIA as PNGs, plus a corner contact sheet.

    python dump_covers.py <dlc.cia> <out_dir>

WHY THIS EXISTS
Two wrong conclusions were reached about these covers by measuring pixel
statistics instead of looking at them:

  * "the placeholder art has a version stamp baked in" -- it does not. The ink
    in that corner is the magazine's own title, "THE RANDST". A standard
    deviation of 47 says "something is there", not "a stamp is there".
  * an inpaint sized from Episode 0's stamp box was applied to a different
    plate, where it erased the title instead.

Both were obvious in a two-second glance at the image. Neither was obvious in
any number I computed. So: dump first, look, then edit.

The contact sheet stacks the top-left corner of all 14 covers, 4x, in issue
order, so "which of these carry a stamp" is answerable by eye in one image.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from cia import Cia                                    # noqa: E402
from tex_rgba8 import decode_rgba8                     # noqa: E402

TEX = 'tex/aoc%02d_magazine_BM_NOMIP_HQ.tex'
CORNER = (0, 44, 0, 200)          # y0, y1, x0, x1 - generous, includes the title
SCALE = 3


def covers_from(cia_path, work):
    """-> {issue: rgb array}, extracting each content's romfs with 3dstool."""
    import subprocess
    tool = os.environ.get('THREEDSTOOL',
                          os.environ.get('THREEDSTOOL', '3dstool.exe'))
    os.makedirs(work, exist_ok=True)
    c = Cia(cia_path)
    out = {}
    for n in range(14):
        idx = n + 2
        if idx >= c.count:
            break
        cfa = os.path.join(work, 'c%02d.cfa' % idx)
        open(cfa, 'wb').write(c.contents[idx])
        rom = os.path.join(work, 'c%02d.romfs' % idx)
        d = os.path.join(work, 'x_c%02d' % idx)
        subprocess.run([tool, '-xtf', 'cfa', cfa, '--romfs', rom],
                       capture_output=True)
        subprocess.run([tool, '-xtf', 'romfs', rom, '--romfs-dir', d],
                       capture_output=True)
        p = os.path.join(d, *(TEX % n).split('/'))
        if os.path.exists(p):
            out[n] = decode_rgba8(open(p, 'rb').read())[0]
    return out


def main():
    cia, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    work = os.path.join(outdir, '_work')
    covers = covers_from(cia, work)
    print('  decoded %d covers' % len(covers))
    y0, y1, x0, x1 = CORNER
    tiles = []
    for n in sorted(covers):
        img = covers[n]
        Image.fromarray(img).save(os.path.join(outdir, 'aoc%02d.png' % n))
        tiles.append((n, img[y0:y1, x0:x1]))
    if tiles:
        h = (y1 - y0) * SCALE
        w = (x1 - x0) * SCALE
        sheet = Image.new('RGB', (w, h * len(tiles)), (0, 0, 0))
        for i, (n, t) in enumerate(tiles):
            sheet.paste(Image.fromarray(t).resize((w, h), Image.NEAREST),
                        (0, i * h))
        sheet.save(os.path.join(outdir, 'corners_contact_sheet.png'))
        print('  contact sheet: %s  (issues %s top to bottom)'
              % (os.path.join(outdir, 'corners_contact_sheet.png'),
                 ', '.join(str(n) for n, _ in tiles)))


if __name__ == '__main__':
    main()

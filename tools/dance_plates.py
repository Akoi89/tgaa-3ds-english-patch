# -*- coding: utf-8 -*-
"""Re-render the Dance of Deduction topic/name plates from Capcom's Chronicles strings.

The 3DS bakes each Dance topic into a 128x128 ETC1A4 plate
(UI/3_mg/30_together/tex/txt/*.tex). senyarom's plates are his own wording; Capcom's
official wording exists in Chronicles (GO/msg/pair_reasoning_*_eng.gmd,
BB/msg/pair_reasoning_*_eng.gmd, *_evidence_name_eng.gmd, *_cast_name_eng.gmd),
keyed by the plate name for the first game.

Layout (measured from senyarom's plates, which the game draws as one ribbon):
the string is centred in a 384 px strip that is sliced into three 128 px rows,
rows centred at y 25.5 / 57.5 / 89.5. White text, antialiased, no outline.

    python dance_plates.py render <name> "<text>" <out.tex> <donor.tex>
"""
import os
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etc1a4

FONT = os.environ.get('TGAA_PLATE_FONT', r'C:\Windows\Fonts\georgia.ttf')
STRIP_W, ROW_H, ROWS = 384, 32, 3
ROW_CENTRES = (25.5, 57.5, 89.5)
TARGET_TRUNK_W = 84          # senyarom's 'trunk' ink width: calibrates the size once


def _font():
    best = None
    for size in range(24, 40):
        f = ImageFont.truetype(FONT, size); d = ImageDraw.Draw(Image.new('L', (8, 8)))
        bb = d.textbbox((0, 0), 'trunk', font=f); w = bb[2] - bb[0]
        if best is None or abs(w - TARGET_TRUNK_W) < abs(best[1] - TARGET_TRUNK_W):
            best = (size, w)
    return ImageFont.truetype(FONT, best[0]), best


def render_mask(text, font=None, shrink=True):
    font = font or _font()[0]
    d = ImageDraw.Draw(Image.new('L', (8, 8)))
    f = font
    bb = d.textbbox((0, 0), text, font=f)
    if shrink and bb[2] - bb[0] > STRIP_W - 8:          # long names: step the size down until it fits
        size = f.size
        while bb[2] - bb[0] > STRIP_W - 8 and size > 16:
            size -= 1; f = ImageFont.truetype(FONT, size); bb = d.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    strip = Image.new('L', (STRIP_W, ROW_H), 0)
    # vertical: centre the x-height band like the originals (measured centre of 'trunk' ink = row centre)
    ref = d.textbbox((0, 0), 'trunk', font=f); ink_c = (ref[1] + ref[3]) / 2
    ImageDraw.Draw(strip).text(((STRIP_W - tw) / 2 - bb[0], ROW_H / 2 - ink_c), text, font=f, fill=255)
    s = np.asarray(strip)
    plate = np.zeros((128, 128), np.uint8)
    for r in range(ROWS):
        y0 = int(round(ROW_CENTRES[r] - ROW_H / 2))
        plate[y0:y0 + ROW_H, :] = s[:, r * 128:(r + 1) * 128]
    return plate, f.size


def render_plate(text, donor):
    mask, size = render_mask(text)
    w = 128; h = 128
    new = donor[:20] + etc1a4.encode_solid((255, 255, 255), mask, b'\0' * (w * h), w, h)
    return new, mask, size


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        _, name, text, out, donor = sys.argv[1:6]
        new, mask, size = render_plate(text, open(donor, 'rb').read())
        open(out, 'wb').write(new); print('  %s: %r at %dpx -> %s' % (name, text, size, out))
    elif sys.argv[1] == 'calib':
        f, best = _font(); print('Georgia size %d gives trunk width %d (target %d)' % (best[0], best[1], TARGET_TRUNK_W))

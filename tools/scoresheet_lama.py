# -*- coding: utf-8 -*-
"""LaMa paper for the TGAA2 DLC score sheets (2026-09-15, user OK), keeping the SHIPPED lettering.

The shipped composites were made by absorption, out = plate * (1 - a * (1 - k)), so the lettering is a
per-pixel multiplicative factor r = composite / plate. scoresheet_compose.py has changed since those
composites shipped (re-running it no longer reproduces them), so instead of re-composing, this moves the
shipped lettering onto a new plate:  new = lama_plate * (shipped_composite / old_plate).

lama_plate: the same ink mask as strip_scoresheet_ink.py (per-job threshold/dilation below; the half-size
sheets need a lower threshold and wider dilation or LaMa keeps stroke fragments sharp), filled by LaMa
(dlc_picturebook/lama_inpaint.py). Pixels outside the mask are the original photo, as before.

Inputs : _event_png/<name>.png (trimmed original), _plate_bak_pre_lama/<name>_plate.png (shipped plate),
         _composite_bak_pre_lama/<name>_english.png (shipped composite; verified == shipped texture pixels)
Output : _event_png/_plate_lama/<name>_plate.png, _event_png/_composite_lama/<name>_english.png,
         review/scoresheet_lama_<name>.png
    python dlc_story_audit/scoresheet_lama.py
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'dlc_story_audit'))
sys.path.insert(0, os.path.join(R, 'dlc_picturebook'))
import strip_scoresheet_ink as SS   # noqa: E402
import lama_inpaint as LI           # noqa: E402

E = os.path.join(R, 'dlc_story_audit', 'tgaa2', 'dlc', '_event_png')
MASK = {'EVENT8_05_01_big': (14, 3), 'EVENT8_05_01': (5, 7), 'EVENT8_05_02': (10, 6)}
REVIEW = os.path.join(R, 'dlc_picturebook', 'review')


def lama_plate(name):
    kw = SS.JOBS[name]
    thr, dil = MASK[name]
    img = cv2.imread(os.path.join(SS.SRC, name + '.png'), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bands = [(a, b, min(t, thr) if t <= kw['thresh'] else t) for a, b, t in kw['bands']]
    mask, _, _ = SS.ink_mask(gray, kw['radius'], thr, dil, bands, kw['quad'])
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ys, xs = np.nonzero(mask)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    return rgb, LI.inpaint(rgb, (mask > 0).astype(np.uint8), box, scale=2 if img.shape[1] <= 512 else 1), int((mask > 0).sum())


def main():
    F = ImageFont.truetype('segoeui.ttf', 18)
    for d in ('_plate_lama', '_composite_lama'):
        os.makedirs(os.path.join(E, d), exist_ok=True)
    for name in MASK:
        orig, plate, npx = lama_plate(name)
        old_plate = np.asarray(Image.open(os.path.join(E, '_plate_bak_pre_lama', name + '_plate.png')).convert('RGB')).astype(np.float64)
        comp = np.asarray(Image.open(os.path.join(E, '_composite_bak_pre_lama', name + '_english.png')).convert('RGB')).astype(np.float64)
        r = comp / np.maximum(old_plate, 1.0)
        new = np.clip(np.round(plate.astype(np.float64) * r), 0, 255).astype(np.uint8)
        Image.fromarray(plate).save(os.path.join(E, '_plate_lama', name + '_plate.png'))
        Image.fromarray(new).save(os.path.join(E, '_composite_lama', name + '_english.png'))
        h, w = new.shape[:2]
        s = 1.0 if w > 512 else 2.0
        ims = [Image.fromarray(x.astype(np.uint8)).resize((int(w * s), int(h * s)), Image.LANCZOS) for x in (orig, comp, new)]
        row = Image.new('RGB', (3 * (ims[0].width + 8), ims[0].height + 24), (30, 30, 30))
        for i, (im, lab) in enumerate(zip(ims, ('Japanese', 'shipped English', 'LaMa paper, same lettering'))):
            row.paste(im, (i * (im.width + 8), 24))
            ImageDraw.Draw(row).text((i * (im.width + 8) + 4, 2), '%s  %s' % (name, lab), fill=(255, 220, 120), font=F)
        row.save(os.path.join(REVIEW, 'scoresheet_lama_%s.png' % name))
        print('%-18s mask %6d px  -> _composite_lama' % (name, npx))


if __name__ == '__main__':
    main()

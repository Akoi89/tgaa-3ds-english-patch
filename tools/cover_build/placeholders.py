# -*- coding: utf-8 -*-
"""Translate the placeholder covers for DLC issues 9-13.

Issues 9-13 DO appear in the in-game DLC list (user-confirmed), each
showing a Capcom placeholder cover: one shared plate of Ryunosuke and
Susato with only the issue number swapped -- the sole region differing
between issue 9 and 13 is x 78..165, y 129..167. The number reads
「N号」 (= "issue no. N"), so it is rendered here as "No. N" to match
the badge the game draws top-right.

These have no official PC banner (Chronicles never shipped them), so
unlike issues 0-8 the 3DS texture itself is edited: mask the glyphs and
their dark outline, inpaint, and redraw. Style sampled off the plate --
cream #faf1e6 core, #423834 outline, 35px cap height, baseline 163.
"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = 'C:/Windows/Fonts/Candarab.ttf'
SS = 4
CREAM = (250, 241, 230)
INK = (66, 56, 52)
BAND = (70, 122, 180, 172)          # x0, y0, x1, y1 around the number
BASELINE, SIZE = 150, 40            # number sits higher to make room below
SUB_BASELINE, SUB_SIZE = 172, 15

# Issue 13 is Capcom's playable sample -- ~11,300 characters across five
# script files (Episode 1's opening, the Court Record tutorial and a
# cross-examination), ending "This is the end of the sample." Issues
# 9-12 are ~40-character stubs that just exit. Nothing on the covers
# distinguished them, so each is labelled: the CONTRAST is what tells
# you which one is worth opening, so the empty ones are labelled too.
SUBTITLE = {9: '(Empty)', 10: '(Empty)', 11: '(Empty)', 12: '(Empty)',
            13: 'Playable Sample'}


def retitle(tex_png, issue):
    a = np.array(Image.open(tex_png).convert('RGBA'))
    rgb = a[:, :, :3].copy()
    x0, y0, x1, y1 = BAND
    sub = rgb[y0:y1, x0:x1].astype(int)
    lum = sub @ np.array([0.299, 0.587, 0.114])
    sat = sub.max(2) - sub.min(2)
    glyph = (lum > 195) & (sat < 45)
    # take the dark outline with the glyphs
    halo = cv2.dilate(glyph.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    m = np.zeros(rgb.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = (glyph | (halo & (lum < 110))).astype(np.uint8)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    rgb = cv2.inpaint(rgb, m, 6, cv2.INPAINT_TELEA)
    out = a.copy(); out[:, :, :3] = rgb
    base = Image.fromarray(out, 'RGBA')

    big = base.resize((512 * SS, 256 * SS), Image.LANCZOS)
    layer = Image.new('RGBA', big.size, (0, 0, 0, 0))
    shadow = Image.new('RGBA', big.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer); sd = ImageDraw.Draw(shadow)
    def put(txt, px, bx, by):
        f = ImageFont.truetype(F, px * SS)
        sd.text((bx * SS + 3 * SS, by * SS + 3 * SS), txt, font=f,
                fill=(0, 0, 0, 150), anchor='ls')
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy:
                    d.text((bx * SS + dx * SS, by * SS + dy * SS), txt,
                           font=f, fill=INK + (255,), anchor='ls')
        d.text((bx * SS, by * SS), txt, font=f, fill=CREAM + (255,), anchor='ls')

    put('No. %d' % issue, SIZE, 77, BASELINE)
    sub = SUBTITLE.get(issue)
    if sub:
        put(sub, SUB_SIZE, 79, SUB_BASELINE)
    big.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2.0 * SS)))
    big.alpha_composite(layer)
    return big.resize((512, 256), Image.LANCZOS)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for issue in range(9, 14):
        p = os.path.join(src, 'jp_placeholder_%02d.png' % issue)
        if not os.path.exists(p):
            print('  missing', p); continue
        retitle(p, issue).save(os.path.join(dst, 'aoc%02d.png' % issue))
        print('  issue %d -> "No. %d"  %s' % (issue, issue, SUBTITLE.get(issue, '')))

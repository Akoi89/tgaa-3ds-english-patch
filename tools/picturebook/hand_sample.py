# -*- coding: utf-8 -*-
"""Sample renders for the handwritten elements, in two handwriting fonts, for the user's choice.

Elements (canvas coords, measured on enlarged crops):
  aoc08_editor_00  header 編集後記 (59,27)-(129,42) -> "Editor's Notes" (Georgia, like the serif header);
                   body (109,58)-(329,198) -> the English in the handwriting font; signature kept.
  aoc01_design_07  labels 服のボタン (104,88)-(155,103), 校章 (110,137)-(146,155).
  aoc01_design_00  brush tag 龍ノ介 (37,16)-(91,41) -> "Ryunosuke"; the swash and date stay.
Erase: pixels >= 40 darker than a 9x9 median inside the element box (all shapes), grown 1 px,
OpenCV Telea inpaint. Output: review/hand_fonts.png (original | Ink Free | Segoe Print).
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = r'C:\Windows\Fonts'
HANDS = {'Ink Free': 'Inkfree.ttf', 'Segoe Print': 'segoepr.ttf'}
EDITOR_EN = ["Nineteenth-century London...", "How did you enjoy your great journey?",
             "The whole team looks forward", "to the day we meet you again", "in Ryunosuke's next adventure."]


def erase(a, box, dark=40, grow=1, k=9):
    x0, y0, x1, y1 = box
    lum = a.astype(float) @ np.array([0.299, 0.587, 0.114])
    med = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), k).astype(float)
    m = np.zeros(lum.shape, np.uint8)
    m[y0:y1, x0:x1] = (med - lum)[y0:y1, x0:x1] > dark
    m = cv2.dilate(m, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))
    out = cv2.inpaint(cv2.cvtColor(a, cv2.COLOR_RGB2BGR), m * 255, 4 if k == 9 else 7, cv2.INPAINT_TELEA)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


def ink_of(a, box):
    x0, y0, x1, y1 = box
    px = a[y0:y1, x0:x1].reshape(-1, 3).astype(float)
    lum = px.mean(axis=1)
    return tuple(int(v) for v in px[lum <= np.percentile(lum, 3)].mean(axis=0))


def draw_text(img, xy, lines, fontfile, px, colour, lh=1.25, S=4):
    """Supersampled text, composited onto img (PIL RGB) at xy (top-left)."""
    f = ImageFont.truetype(fontfile, px * S)
    w = int(max(f.getlength(l) for l in lines)) + 8 * S
    h = int(len(lines) * px * lh * S) + 8 * S
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    for i, l in enumerate(lines):
        d.text((0, int(i * px * lh * S)), l, font=f, fill=255)
    m = m.resize((w // S, h // S), Image.LANCZOS)
    col = Image.new('RGB', m.size, colour)
    img.paste(col, xy, m)
    return m.size


def build(hand):
    out = {}
    # Editor's Notes page 1
    a = np.asarray(Image.open(os.path.join(HERE, 'orig', 'aoc08_editor_00.png')).convert('RGB'))
    hdr_col, body_col = ink_of(a, (59, 27, 129, 42)), ink_of(a, (109, 58, 329, 198))
    a = erase(a, (57, 25, 131, 44), dark=30)
    a = erase(a, (107, 56, 331, 200), dark=30)
    im = Image.fromarray(a)
    draw_text(im, (60, 27), ["Editor's Notes"], os.path.join(F, 'georgia.ttf'), 12, hdr_col)
    draw_text(im, (92, 62), EDITOR_EN, os.path.join(F, HANDS[hand]), 14 if hand == 'Ink Free' else 12, body_col, lh=1.55)
    out['aoc08_editor_00'] = im
    # labels on the sword page (start from the typeset commentary version)
    base = os.path.join(HERE, 'final', 'aoc01_design_07.png')
    a = np.asarray(Image.open(base).convert('RGB'))
    col = ink_of(a, (104, 88, 155, 103))
    a = erase(a, (103, 86, 157, 105), grow=2); a = erase(a, (108, 135, 148, 157), grow=2)
    im = Image.fromarray(a)
    draw_text(im, (104, 84), ['Uniform', 'button'], os.path.join(F, HANDS[hand]), 11 if hand == 'Ink Free' else 9, col, lh=1.05)
    draw_text(im, (110, 139), ['School crest'], os.path.join(F, HANDS[hand]), 11 if hand == 'Ink Free' else 9, col)
    out['aoc01_design_07'] = im
    # brush name tag
    a = np.asarray(Image.open(os.path.join(HERE, 'final', 'aoc01_design_00.png')).convert('RGB'))
    a = erase(a, (36, 14, 93, 38), dark=45, grow=1, k=31)
    im = Image.fromarray(a)
    draw_text(im, (34, 15), ['Ryunosuke'], os.path.join(F, HANDS[hand]), 17 if hand == 'Ink Free' else 14, (20, 16, 14))
    out['aoc01_design_00'] = im
    return out


def main():
    crops = {'aoc08_editor_00': (24, 8, 424, 248), 'aoc01_design_07': (60, 60, 240, 170), 'aoc01_design_00': (24, 8, 150, 60)}
    zoom = {'aoc08_editor_00': 1.6, 'aoc01_design_07': 3, 'aoc01_design_00': 4}
    res = {h: build(h) for h in HANDS}
    rows = []
    for p, c in crops.items():
        cells = [Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB').crop(c)] + [res[h][p].crop(c) for h in HANDS]
        z = zoom[p]
        cells = [x.resize((int(x.size[0] * z), int(x.size[1] * z)), Image.LANCZOS) for x in cells]
        w, h = cells[0].size
        row = Image.new('RGB', (3 * (w + 8), h + 18), (20, 20, 20)); d = ImageDraw.Draw(row)
        for i, (x, lab) in enumerate(zip(cells, ['original'] + list(HANDS))):
            row.paste(x, (i * (w + 8), 18)); d.text((i * (w + 8) + 4, 3), '%s  %s' % (p, lab), fill=(255, 255, 0))
        rows.append(row)
    S = Image.new('RGB', (max(r.size[0] for r in rows), sum(r.size[1] for r in rows)), (20, 20, 20)); y = 0
    for r in rows:
        S.paste(r, (0, y)); y += r.size[1]
    os.makedirs(os.path.join(HERE, 'review'), exist_ok=True)
    S.save(os.path.join(HERE, 'review', 'hand_fonts.png'))
    for h in HANDS:
        for p, im in res[h].items():
            im.save(os.path.join(HERE, 'review', '_hand_%s_%s.png' % (h.replace(' ', ''), p)))
    print(S.size)


if __name__ == '__main__':
    main()

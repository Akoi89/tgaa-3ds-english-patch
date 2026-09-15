# -*- coding: utf-8 -*-
"""English for the legible handwritten labels and both Editor's Notes pages (decided 2026-09-15:
handwriting font Ink Free; brush name tags stay Japanese; tiny production scribbles stay).

Each item: page, erase box (canvas coords, measured on 2x ruler renders), erase mode, English lines,
anchor (top-left), size in px, font. Colour is sampled from the ink that was erased.
  dark : pixels >= 30 darker than a 9x9 median in the box (pencil, pen, marker)
  red  : pixels with R - max(G, B) > 40 in the box (red and pink ink)
  lumNNN: pixels darker than luminance NNN (pen over a highlighter), dilated 3x3 not 5x5
Fill: LaMa (lama_inpaint.py) by default, OpenCV Telea for modes ending in -telea or LABEL_ERASE=telea;
'rowfill' rebuilds rows from the paper beside the note.
Base image: final/<page>.png if it exists (commentary already typeset), else orig/. Result is written
back to final/<page>.png; every run starts from typeset_*/ or orig/, never from final/.
"""
import os
import shutil

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = r'C:\Windows\Fonts'
HAND = os.path.join(F, 'Inkfree.ttf')
SERIF = os.path.join(F, 'georgia.ttf')

ITEMS = [
    # the sword page
    ('aoc01_design_07', (103, 86, 157, 105), 'dark', ['Uniform', 'button'], (104, 84), 11, HAND),
    ('aoc01_design_07', (108, 135, 148, 157), 'dark', ['School crest'], (110, 139), 11, HAND),
    # red note on the animation sheet
    ('aoc02_design_07', (186, 10, 297, 52), 'red-rowfill', ['For the front angle, please', 'turn the hair silhouette', 'this way.'], (190, 12), 10, HAND),
    # Iris's inventions: pink labels and the pen note
    ('aoc04_design_03', (127, 20, 186, 33), 'red', ["Iris's magic flask"], (129, 21), 8, HAND),
    ('aoc04_design_03', (139, 114, 193, 126), 'red', ["Iris's calling card"], (141, 115), 8, HAND),
    ('aoc04_design_03', (234, 8, 281, 18), 'red', ["Iris's backpack"], (236, 8), 8, HAND),
    ('aoc04_design_03', (284, 41, 331, 69), 'dark', ['Mascot hangs', 'on the left'], (283, 43), 9, HAND),
    # lucky charms page
    ('aoc04_design_04', (52, 28, 101, 58), 'red', ["Iris's lucky", 'charm', 'mascots'], (55, 28), 9, HAND),
    ('aoc04_design_04', (317, 137, 339, 151), 'red', ['Buttons'], (316, 139), 8, HAND),
    # early Iris
    # pen over green highlighter: erase only the pen (luminance < N), keep the highlighter (2026-09-15)
    ('aoc04_design_05', (184, 47, 224, 66), 'lum190', ['First', 'appearance'], (186, 45), 9, HAND),
    ('aoc04_design_05', (264, 37, 306, 53), 'lum200-telea', ['Change of', 'outfit'], (266, 38), 9, HAND),
    # early van Zieks
    ('aoc06_design_06', (249, 12, 304, 44), 'dark', ['Russian?', 'England?'], (250, 14), 10, HAND),
    ('aoc06_design_06', (279, 65, 316, 80), 'dark', ['Hood'], (282, 66), 11, HAND),
    # Editor's Notes
    ('aoc08_editor_00', (57, 25, 131, 44), 'dark', ["Editor's Notes"], (60, 27), 12, SERIF),
    ('aoc08_editor_00', (107, 56, 331, 200), 'dark', ["Nineteenth-century London...", "How did you enjoy your great journey?",
                                                     "The whole team looks forward", "to the day we meet you again",
                                                     "in Ryunosuke's next adventure."], (92, 62), 14, HAND),
    ('aoc08_editor_01', (59, 25, 128, 44), 'dark', ["Editor's Notes"], (60, 27), 12, SERIF),
]


def erase_mask(a, box, mode):
    x0, y0, x1, y1 = box
    m = np.zeros(a.shape[:2], np.uint8)
    af = a.astype(float)
    if mode.startswith('red'):
        sel = (af[..., 0] - np.maximum(af[..., 1], af[..., 2])) > 25
    elif mode.startswith('lum'):
        sel = (af @ np.array([0.299, 0.587, 0.114])) < int(mode[3:6])
    else:
        lum = af @ np.array([0.299, 0.587, 0.114])
        med = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 9).astype(float)
        sel = (med - lum) > 22
    m[y0:y1, x0:x1] = sel[y0:y1, x0:x1]
    return m


def colour_of(a, m, mode):
    px = a[m.astype(bool)].astype(float)
    if not len(px):
        return (60, 50, 40)
    if mode.startswith('red'):
        sat = px[:, 0] - np.maximum(px[:, 1], px[:, 2])
        return tuple(int(v) for v in px[sat >= np.percentile(sat, 90)].mean(axis=0))
    lum = px.mean(axis=1)
    return tuple(int(v * 0.9) for v in px[lum <= np.percentile(lum, 8)].mean(axis=0))


def draw(img, xy, lines, fontfile, px, colour, lh=None, S=4):
    lh = lh or (1.55 if len(lines) >= 5 else 1.08)
    f = ImageFont.truetype(fontfile, px * S)
    w = int(max(f.getlength(l) for l in lines)) + 8 * S
    h = int(len(lines) * px * lh * S) + 8 * S
    mk = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mk)
    for i, l in enumerate(lines):
        d.text((0, int(i * px * lh * S)), l, font=f, fill=255)
    mk = mk.resize((w // S, h // S), Image.LANCZOS)
    img.paste(Image.new('RGB', mk.size, colour), xy, mk)
    return (xy[0], xy[1], xy[0] + mk.size[0], xy[1] + mk.size[1])


def main():
    pages = []
    for it in ITEMS:
        if it[0] not in pages:
            pages.append(it[0])
    for p in pages:
        # deterministic start: the typeset version of the page if there is one, else Capcom's original
        base = next((os.path.join(HERE, d, p + '.png') for d in os.environ.get('LABEL_BASES', 'typeset_bahn,typeset_medium,typeset_themes,orig').split(',')
                     if os.path.exists(os.path.join(HERE, d, p + '.png'))))
        a = np.asarray(Image.open(base).convert('RGB')).copy()
        todo = [it for it in ITEMS if it[0] == p]
        cols = []
        for _, box, mode, lines, xy, px, font in todo:
            m = erase_mask(a, box, mode)
            cols.append(colour_of(a, m, mode))
            m = cv2.dilate(m, np.ones((3, 3) if mode.startswith('lum') else (5, 5), np.uint8))
            if mode.endswith('rowfill'):
                # the note straddles the dark border and the paper's top edge, both horizontal bands:
                # rebuild each masked pixel from the median of the same row just right of the box
                ref = a[:, box[2] + 2:box[2] + 26].astype(float)
                med = np.median(ref, axis=1)
                ys, xs = np.nonzero(m)
                a[ys, xs] = med[ys].astype(np.uint8)
            elif os.environ.get('LABEL_ERASE', 'lama') == 'lama' and not mode.endswith('telea'):
                import lama_inpaint as LI      # AI fill on the same mask; only masked pixels change
                a = LI.inpaint(a, m, box, scale=2)
            else:
                a = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(a, cv2.COLOR_RGB2BGR), m * 255, 3 if mode.startswith('lum') else 4, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
        im = Image.fromarray(a)
        for (_, box, mode, lines, xy, px, font), col in zip(todo, cols):
            r = draw(im, xy, lines, font, px, col)
            print('%-16s %-28s %2d px  colour %s  drawn %s' % (p, ' / '.join(lines)[:28], px, col, r))
        orig = np.asarray(Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB'))
        res = np.asarray(im).copy(); keep = np.ones(res.shape[:2], bool); keep[8:248, 24:424] = False
        res[keep] = orig[keep]            # nothing outside the visible window may change
        Image.fromarray(res).save(os.path.join(HERE, os.environ.get('LABEL_OUT', 'final'), p + '.png'))
    print('%d pages written to %s/' % (len(pages), os.environ.get('LABEL_OUT', 'final')))


if __name__ == '__main__':
    main()

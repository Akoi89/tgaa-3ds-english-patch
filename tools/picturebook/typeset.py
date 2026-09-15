# -*- coding: utf-8 -*-
"""Typeset the English commentary onto PLAIN Picture Book pages (text on the flat cream background).

    python typeset.py [--font segoeui] [--pages p1,p2] [--sample]

For each page whose commentary blocks detect_text.py classified PLAIN:
  1. erase: every padded PLAIN box is filled with the background colour (the box holds only
     background and glyphs, measured, so no art is touched);
  2. area: the union of those boxes, grown right/left/down/up while the new strip is pure background
     with a 4 px margin from any art, inside the visible 400x240 window;
  3. fit: the full English (never shortened) wrapped into that area at the largest size from 12 px
     down to MIN_PX that fits; rendered at 4x and downsampled, composited as ink over background;
  4. write typeset/<page>.png (512x256 canvas) and typeset/_cmp_<page>.png (before | after, 2x).
Pages that do not fit at MIN_PX are reported and left alone.
"""
import argparse
import io
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BG = (255, 247, 223)
INK = (48, 40, 16)
VIS = (24, 8, 424, 248)
MIN_PX, MAX_PX = 9, 12
FONTS = {'segoeui': ('segoeui.ttf', None), 'segoeui-sb': ('seguisb.ttf', None), 'calibri': ('calibri.ttf', None),
         'calibri-b': ('calibrib.ttf', None), 'candara': ('Candara.ttf', None), 'bahn-sc': ('bahnschrift.ttf', b'SemiCondensed'),
         'bahn-sb-sc': ('bahnschrift.ttf', b'SemiBold SemiCondensed'), 'bahn-c': ('bahnschrift.ttf', b'Condensed')}
# commentary blocks per page: detect_text.py PLAIN blocks, minus nothing; pages listed here are the
# high-confidence set (every commentary block on the page is PLAIN)
HIGH = ['aoc01_design_01', 'aoc01_design_02', 'aoc01_design_04', 'aoc01_design_07', 'aoc02_design_01', 'aoc02_design_02',
        'aoc02_design_03', 'aoc02_design_04', 'aoc02_design_06', 'aoc03_design_01', 'aoc03_design_03', 'aoc04_design_02',
        'aoc04_design_04', 'aoc04_design_05', 'aoc05_design_01', 'aoc05_design_02', 'aoc06_design_02', 'aoc07_design_00',
        'aoc07_design_01', 'aoc07_design_03', 'aoc07_design_06', 'aoc08_design_02', 'aoc08_design_06']


def is_bg(a):
    return np.abs(a.astype(int) - np.array(BG)).max(axis=-1) <= 3


def grow_order(bgmask, box, order, margin=3):
    """Grow box one side at a time in the given order (each side as far as it goes), then repeat."""
    x0, y0, x1, y1 = box

    def clear(xa, ya, xb, yb):
        xa, ya, xb, yb = max(VIS[0], xa), max(VIS[1], ya), min(VIS[2], xb), min(VIS[3], yb)
        if xa >= xb or ya >= yb:
            return False
        return bool(bgmask[ya:yb, xa:xb].all())
    for _ in range(2):
        for side in order:
            while True:
                if side == 'R' and x1 + 1 + margin <= VIS[2] - 2 and clear(x1, y0 - margin, x1 + 1 + margin, y1 + margin):
                    x1 += 1
                elif side == 'D' and y1 + 1 + margin <= VIS[3] - 2 and clear(x0 - margin, y1, x1 + margin, y1 + 1 + margin):
                    y1 += 1
                elif side == 'L' and x0 - 1 - margin >= VIS[0] + 2 and clear(x0 - 1 - margin, y0 - margin, x0, y1 + margin):
                    x0 -= 1
                elif side == 'U' and y0 - 1 - margin >= VIS[1] + 2 and clear(x0 - margin, y0 - 1 - margin, x1 + margin, y0):
                    y0 -= 1
                else:
                    break
    return [x0, y0, x1, y1]


ORDERS = ['RDLU', 'DRLU', 'DLRU', 'LDRU', 'URDL', 'ULDR', 'RULD', 'LURD']


def grow(bgmask, box, margin=4):
    """Grow box while the strip just outside it (plus margin) is all background."""
    x0, y0, x1, y1 = box
    H, W = bgmask.shape

    def clear(xa, ya, xb, yb):
        xa, ya, xb, yb = max(VIS[0], xa), max(VIS[1], ya), min(VIS[2], xb), min(VIS[3], yb)
        if xa >= xb or ya >= yb:
            return False
        return bool(bgmask[ya:yb, xa:xb].all())
    moved = True
    while moved:
        moved = False
        if x1 + 1 + margin <= VIS[2] - 2 and clear(x1, y0 - margin, x1 + 1 + margin, y1 + margin):
            x1 += 1; moved = True
        if y1 + 1 + margin <= VIS[3] - 2 and clear(x0 - margin, y1, x1 + margin, y1 + 1 + margin):
            y1 += 1; moved = True
        if x0 - 1 - margin >= VIS[0] + 2 and clear(x0 - 1 - margin, y0 - margin, x0, y1 + margin):
            x0 -= 1; moved = True
        if y0 - 1 - margin >= VIS[1] + 2 and clear(x0 - margin, y0 - 1 - margin, x1 + margin, y0):
            y0 -= 1; moved = True
    return [x0, y0, x1, y1]


def layout(text, font, width):
    """Greedy word wrap; paragraphs split on blank lines. Returns list of lines ('' = paragraph gap)."""
    out = []
    for pi, para in enumerate(text.split('\n\n')):
        if pi:
            out.append('')
        for src_line in para.split('\n'):
            line = ''
            for w in src_line.split(' '):
                cand = (line + ' ' + w).strip()
                if font.getlength(cand) <= width or not line:
                    line = cand
                else:
                    out.append(line); line = w
            out.append(line)
    return out


def render(text, box, fontfile, px, lhf=1.22):
    """Return (alpha 2D array for box size, fits flag). Rendered at 4x then reduced."""
    S = 4
    w, h = box[2] - box[0], box[3] - box[1]
    f = ImageFont.truetype(fontfile[0], px * S)
    if fontfile[1]:
        f.set_variation_by_name(fontfile[1])
    lines = layout(text, f, w * S)
    lh = round(px * lhf) * S
    gap = lh // 2
    total = sum(gap if l == '' else lh for l in lines)
    if total > h * S or any(f.getlength(l) > w * S for l in lines):
        return None, lines
    im = Image.new('L', (w * S, h * S), 0)
    d = ImageDraw.Draw(im)
    y = 0
    asc = f.getmetrics()[0]
    for l in lines:
        if l == '':
            y += gap; continue
        d.text((0, y + (lh - px * S) // 2 - (asc - px * S * 0.78)), l, font=f, fill=255)
        y += lh
    return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(float) / 255.0, lines


def do_page(page, blocks, en, fontfile):
    a = np.asarray(Image.open(os.path.join(HERE, 'orig', page + '.png')).convert('RGB')).copy()
    plain = [b['box'] for b in blocks if b['kind'] == 'PLAIN']
    for x0, y0, x1, y1 in plain:
        a[max(VIS[1], y0 - 2):min(VIS[3], y1 + 2), max(VIS[0], x0 - 2):min(VIS[2], x1 + 2)] = BG
    ux0, uy0 = min(b[0] for b in plain), min(b[1] for b in plain)
    ux1, uy1 = max(b[2] for b in plain), max(b[3] for b in plain)
    bgm = is_bg(a)
    # candidate areas: the even grow plus every one-side-at-a-time order; keep the one that
    # allows the largest size, ties to the smallest shift from where the Japanese sat
    cands = [grow(bgm, [ux0, uy0, ux1, uy1])] + [grow_order(bgm, [ux0, uy0, ux1, uy1], o) for o in ORDERS]
    best = None
    for area in cands:
        for px in range(MAX_PX, MIN_PX - 1, -1):
            alpha, lines = render(en, area, fontfile, px)
            if alpha is not None:
                shift = abs(area[0] - ux0) + abs(area[1] - uy0)
                if best is None or px > best[0] or (px == best[0] and shift < best[1]):
                    best = (px, shift, area, alpha, lines)
                break
    if best is not None:
        px, _, area, alpha, lines = best
        if True:
            x0, y0, x1, y1 = area
            reg = a[y0:y1, x0:x1].astype(float)
            ink = np.array(INK, float)
            a[y0:y1, x0:x1] = np.clip(reg * (1 - alpha[..., None]) + ink * alpha[..., None], 0, 255).astype(np.uint8)
            return Image.fromarray(a), px, area, len([l for l in lines if l])
    return None, None, area, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--font', default='segoeui')
    ap.add_argument('--pages', default='')
    ap.add_argument('--out', default='typeset')
    a = ap.parse_args()
    fontfile = (os.path.join(r'C:\Windows\Fonts', FONTS[a.font][0]), FONTS[a.font][1])
    blocks = json.load(open(os.path.join(HERE, 'blocks.json')))
    en = {json.loads(l)['page']: json.loads(l)['en'] for l in io.open(os.path.join(HERE, 'translations.jsonl'), encoding='utf-8') if l.strip()}
    pages = a.pages.split(',') if a.pages else HIGH
    out = os.path.join(HERE, a.out)
    os.makedirs(out, exist_ok=True)
    ok, bad = 0, []
    for p in pages:
        im, px, area, nl = do_page(p, blocks[p], en[p], fontfile)
        if im is None:
            bad.append((p, area)); print('NO FIT  %-16s area %s' % (p, area)); continue
        im.save(os.path.join(out, p + '.png'))
        before = Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB').crop(VIS).resize((800, 480), Image.LANCZOS)
        after = im.crop(VIS).resize((800, 480), Image.LANCZOS)
        c = Image.new('RGB', (1610, 480), (0, 0, 0)); c.paste(before, (0, 0)); c.paste(after, (810, 0))
        c.save(os.path.join(out, '_cmp_' + p + '.png'))
        print('OK      %-16s %2d px, %2d lines, area %s' % (p, px, nl, area)); ok += 1
    print('%d typeset, %d did not fit at %d px' % (ok, len(bad), MIN_PX))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Rebuild the TGAA1 DLC-list icon sheet (UI/4_menu/43_extra/tex/dlc_menuicon_BM_HQ_NOMIP.tex in
archive/extra_jpn.arc) from Capcom's Japanese plate, 2026-09-15 (user: the shipped English sheet has
artifacts and cuts off artwork).

Measured on the shipped sheet: its label erase changed every pixel of rows 45..66 of each tile, which
reached into the bottom of the art on all 18 tiles (gramophone feet, 3DS bottom edge, microphone base,
photo corner, scroll foot, reel rim).

Here: per tile, dark shapes (darker than a 9x9 median of the parchment) are labelled; a shape is a
Japanese glyph only if it lies wholly inside the label strip (below ART_BOTTOM) and away from the tile's
frame lines. Only those shapes (grown 2 px, never into a 2 px guard round art and frame) are erased, in two
passes, and filled with Telea (LaMa, ICON_FILL=lama, invented dark dots under the art on this smooth parchment). Art and frame pixels are never in the mask. Then the English labels are drawn as before: Blackford,
12.75 px (51 at 4x), mixed case, antialiased, centred on the tile, baselines 68/147/228, colour sampled
from the Japanese ink.

    python dlc_story_audit/menuicon_rebuild.py            -> review PNGs + _menuicon/dlc_menuicon_new.png
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'dlc_icons', 'tgaa2-en-patch'))
sys.path.insert(0, os.path.join(R, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(R, 'dlc_picturebook'))
from dgs2tool.arc import parse_arc   # noqa: E402
import tex_rgba8                     # noqa: E402

JP_ARC = os.path.join(R, 'dlc_story_audit', 'basegame', 'rom', 'archive', 'extra_jpn.arc')
SHIP_ARC = os.path.join(R, 'dlc_ai_voice', '_shipped', 'TGAA1-base-3.2.3', 'content0', 'archive', 'extra_jpn.arc')
MEMBER = 'UI/4_menu/43_extra/tex/dlc_menuicon_BM_HQ_NOMIP.tex'
OUT = os.path.join(R, 'dlc_story_audit', '_menuicon')
REVIEW = os.path.join(R, 'dlc_picturebook', 'review')
FONT = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts', 'Blackford.ttf')
XS = (5, 85, 165, 245, 325, 405)
YS = (5, 85, 165)
T = 76                      # tile size
BASE = (68, 147, 228)       # label baselines (sheet rows), from the shipped build
LABELS = [['Short Story', 'Short Story', 'Music', 'Music', 'Movie', 'Movie'],
          ['Picture Book', 'Picture Book', "Editor's Notes", "Editor's Notes", 'Illustration', 'Illustration'],
          ['Theme', 'Theme', 'Audio', 'Audio', 'Movie 2', 'Movie 2']]
CX = 34.5                   # label centre in the tile: the shipped labels sit 3.5 px left of the box centre
                            # (best-fit shift per tile, correlation 0.88..0.97 with the same font and size)
INK = (58, 52, 39)          # the shipped labels' ink (darkest 20% of their strokes)
STRIP_TOP = 47              # tile row where a glyph may start; anything reaching above it is art
FRAME = 7                   # tile columns this close to the edge are frame lines


def member(path):
    for e in parse_arc(open(path, 'rb').read())['entries']:
        if e.name.replace('\\', '/').endswith(MEMBER.split('/')[-1]):
            return e.data
    raise SystemExit('member not found in ' + path)


def glyph_mask(rgb, grow=5):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(int)
    dark = ((cv2.medianBlur(g.astype(np.uint8), 9).astype(int) - g) > 18).astype(np.uint8)
    mask = np.zeros(g.shape, np.uint8)
    keep = np.zeros(g.shape, np.uint8)      # art and frame: never erased, with a 2 px guard band
    for y in YS:
        for x in XS:
            sub = dark[y:y + T, x:x + T].copy()
            n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
            for i in range(1, n):
                x0, y0, w, h, a = st[i]
                frame = (x0 < FRAME or x0 + w > T - FRAME) and h > 14          # tall thin frame lines only
                art = y0 < STRIP_TOP or frame or y0 + h > T - 6
                line = w > 40 and h <= 3                       # a rule under the pressed-state tile
                corner = x0 > T - 16 and y0 > T - 16            # the frame's cut corner
                tgt = keep if (art or line or corner) else mask
                tgt[y:y + T, x:x + T][lab == i] = 1
    # the glyphs carry a pale emboss ring: grow the mask to take it, but never into art or frame
    core = mask.copy()
    ring = cv2.dilate(mask, np.ones((grow, grow), np.uint8))
    guard = cv2.dilate(keep, np.ones((3, 3), np.uint8))
    black = (g < 40).astype(np.uint8)                  # the sheet's black surround and the tiles' cut corners
    guard |= cv2.dilate(black, np.ones((7, 7), np.uint8))
    # the glyph itself always goes; only the widened ring stops at art, frame and the black surround
    return (core | (ring & (1 - guard))).astype(np.uint8)


def ink_colour(rgb, mask):
    px = rgb[mask.astype(bool)].astype(float)
    lum = px.mean(1)
    return tuple(int(v) for v in px[lum <= np.percentile(lum, 10)].mean(0))


def draw_labels(img, colour):
    S = 4
    f = ImageFont.truetype(FONT, 51)
    big = Image.new('L', (img.width * S, img.height * S), 0)
    d = ImageDraw.Draw(big)
    for r, y in enumerate(YS):
        for c, x in enumerate(XS):
            t = LABELS[r][c]
            w = d.textlength(t, font=f)
            d.text(((x + CX) * S - w / 2, BASE[r] * S), t, font=f, fill=255, anchor='ls')
    a = np.asarray(big.resize(img.size, Image.LANCZOS)).astype(float)[:, :, None] / 255
    base = np.asarray(img).astype(float)
    out = base * (1 - a) + np.array(colour, float)[None, None, :] * a
    return np.clip(np.round(out), 0, 255).astype(np.uint8), a[:, :, 0]


def main():
    import lama_inpaint as LI
    os.makedirs(OUT, exist_ok=True)
    jp_blob = member(JP_ARC)
    jp, alpha = tex_rgba8.decode_rgba8(jp_blob)
    jp = np.asarray(jp)[:, :, :3].copy()
    alpha = np.asarray(alpha)
    ship = np.asarray(tex_rgba8.decode_rgba8(member(SHIP_ARC))[0])[:, :, :3]
    m = glyph_mask(jp)
    col = ink_colour(jp, m)
    clean = jp.copy()
    total = np.zeros_like(m)
    for rnd in range(2):          # second pass takes stroke fragments the first mask missed
        mm = m if rnd == 0 else glyph_mask(clean, grow=3)
        total |= mm
        for y in YS:
            for x in XS:
                tm = np.zeros_like(mm)
                tm[y:y + T, x:x + T] = mm[y:y + T, x:x + T]
                if tm.any():
                    if os.environ.get('ICON_FILL') == 'lama':   # tried 2026-09-15: invents dark dots under the art
                        clean = LI.inpaint(clean, tm, (x, y, x + T, y + T), scale=4, clip=(x, y + STRIP_TOP - 3, x + T, y + T))
                    else:                                        # Telea: cleanest on this smooth parchment
                        # fill on a copy where the art above the strip is plain parchment, so Telea cannot
                        # drag the art's shadow down into the strip; paste back only the erased pixels
                        work = clean.copy()
                        strip = work[y + STRIP_TOP:y + T - 8, x + FRAME:x + T - FRAME].reshape(-1, 3)
                        sm = tm[y + STRIP_TOP:y + T - 8, x + FRAME:x + T - FRAME].reshape(-1) == 0
                        par = np.median(strip[sm & (strip.mean(1) > 150)], axis=0).astype(np.uint8)
                        work[y + FRAME:y + STRIP_TOP - 1, x + FRAME:x + T - FRAME] = par
                        res = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(work, cv2.COLOR_RGB2BGR), tm * 255, 3, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
                        clean[tm.astype(bool)] = res[tm.astype(bool)]
        print('pass %d erased %d px' % (rnd + 1, int(mm.sum())))
    m = total
    new, a = draw_labels(Image.fromarray(clean), INK)
    # nothing outside the erased glyphs and the new label ink may differ from Capcom's plate
    touched = m.astype(bool) | (a > 0)
    assert not (np.abs(new.astype(int) - jp.astype(int)).max(-1) > 0)[~touched].any()
    Image.fromarray(np.dstack([new, alpha])).save(os.path.join(OUT, 'dlc_menuicon_new.png'))
    Image.fromarray(np.dstack([clean, alpha])).save(os.path.join(OUT, 'dlc_menuicon_clean.png'))
    # label placement check against the shipped English: ink IoU per tile
    sd = (cv2.medianBlur(cv2.cvtColor(ship, cv2.COLOR_RGB2GRAY), 9).astype(int) - cv2.cvtColor(ship, cv2.COLOR_RGB2GRAY).astype(int)) > 30
    nd = a > 0.5
    ious = []
    for y in YS:
        for x in XS:
            s_ = sd[y + 45:y + 70, x:x + T]; n_ = nd[y + 45:y + 70, x:x + T]
            ious.append((s_ & n_).sum() / max(1, (s_ | n_).sum()))
    print('ink colour', col, ' label ink IoU vs shipped: min %.2f median %.2f' % (min(ious), float(np.median(ious))))
    # review: per tile Japanese | shipped | new, 3x
    F = ImageFont.truetype('segoeui.ttf', 14)
    tiles = []
    for r, y in enumerate(YS):
        for c, x in enumerate(XS[::2]):
            ims = [Image.fromarray(v[y:y + T, x:x + T]).resize((228, 228), Image.NEAREST) for v in (jp, ship, new)]
            t = Image.new('RGB', (3 * 232, 248), (30, 30, 30))
            for i, im in enumerate(ims):
                t.paste(im, (i * 232, 20))
            ImageDraw.Draw(t).text((2, 2), 'Japanese | shipped English | rebuilt', fill=(255, 220, 120), font=F)
            tiles.append(t)
    s = Image.new('RGB', (3 * 700, 3 * 252), (30, 30, 30))
    for i, t in enumerate(tiles):
        s.paste(t, ((i % 3) * 700, (i // 3) * 252))
    s.save(os.path.join(REVIEW, 'menuicon_rebuild.png'))
    mk = jp.copy(); mk[m.astype(bool)] = (255, 0, 0)
    Image.fromarray(mk).crop((0, 0, 490, 250)).resize((980, 500), Image.NEAREST).save(os.path.join(REVIEW, 'menuicon_mask.png'))
    print('written', os.path.join(OUT, 'dlc_menuicon_new.png'))


if __name__ == '__main__':
    main()

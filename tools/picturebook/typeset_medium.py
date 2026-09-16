# -*- coding: utf-8 -*-
"""Typeset the English onto the medium pages: commentary over art, in see-through boxes, or on a
flat panel. Boxes are hand-marked in boxes_medium.json (canvas coords) after reading each page.

Per page:
  1. glyph mask inside each box: pixels at least DARK darker (luminance) than a 9x9 local median,
     in connected shapes no taller than 14 px (text strokes; long art strokes are taller), grown 1 px
     to take the anti-aliased fringe;
  2. those pixels are rebuilt from their surroundings (OpenCV Telea inpainting, radius 3);
  3. the full English is fitted, 12 down to 9 px, font A (Bahnschrift SemiBold SemiCondensed), into
     the union of the boxes (inset 2 px), left-aligned from the top like the Japanese;
  4. pages that do not fit are listed, not forced.
Writes typeset_medium/<page>.png and _cmp_<page>.png.
"""
import io
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import typeset as T   # noqa: E402

VIS = (24, 8, 424, 248)
DARK = 26
FONT = (os.path.join(r'C:\Windows\Fonts', 'bahnschrift.ttf'), b'SemiBold SemiCondensed')
INK = np.array(T.INK, float)


def save(im, path, tries=8):
    """G: sometimes refuses a write for a moment (Errno 22); retry instead of losing the run."""
    import time
    for k in range(tries):
        try:
            im.save(path); return
        except OSError:
            if k == tries - 1: raise
            time.sleep(0.5)


def glyph_mask(a, box, overlay=False):
    x0, y0, x1, y1 = box
    lum = a[..., :3].astype(float) @ np.array([0.299, 0.587, 0.114])
    med = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 9).astype(float)
    dark = np.zeros(lum.shape, np.uint8)
    dark[y0:y1, x0:x1] = ((med - lum)[y0:y1, x0:x1] > DARK)
    n, lab, st, _ = cv2.connectedComponentsWithStats(dark, 8)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        keep[i] = st[i, 3] <= 14
    m = keep[lab].astype(np.uint8)
    if overlay:
        # inside a see-through box the art is washed light, so anything close to the ink colour
        # is text, whatever its shape (strokes that crossed pencil lines fuse into tall shapes)
        near_ink = (np.linalg.norm(a[..., :3].astype(float) - INK, axis=-1) < 45) & (lum < 110)
        box_m = np.zeros_like(m); box_m[y0:y1, x0:x1] = 1
        m |= (near_ink & (box_m == 1)).astype(np.uint8)
    return cv2.dilate(m, np.ones((5, 5), np.uint8))


def ink_grey(a):
    """Pixels in the Japanese text's colour range: neutral grey, lum 35..150 (measured 2026-09-15: JP ink
    (57,54,48)..(83,80,70); shoes, dark coats and the art above the panels are darker or coloured)."""
    c = a[..., :3].astype(int)
    lum = c @ np.array([0.299, 0.587, 0.114])
    return (lum >= 35) & (lum <= 150) & ((c.max(-1) - c.min(-1)) <= 30)


def art_entering(g, box, thr=12, reach=6, pad=8):
    """Art that enters the text box from outside (2026-09-15, user: shoe, hat, hair tops, backpack bottom,
    sword edge were eaten): dark-stroke components (median-9 residual > thr) that continue more than 1 px
    outside the marked box are art, not Japanese. Returns their pixels inside the box within `reach` px of
    the outside, which the erase must leave alone."""
    x0, y0, x1, y1 = box
    H, W = g.shape
    wx0, wy0, wx1, wy1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    sub = g[wy0:wy1, wx0:wx1].astype(np.uint8)
    dark = ((cv2.medianBlur(sub, 9).astype(int) - sub.astype(int)) > thr).astype(np.uint8)
    inside = np.zeros_like(dark); inside[y0 - wy0:y1 - wy0, x0 - wx0:x1 - wx0] = 1
    outside = 1 - cv2.dilate(inside, np.ones((3, 3), np.uint8))
    n, lab = cv2.connectedComponents(dark, connectivity=8)
    art_ids = np.unique(lab[(outside == 1) & (dark == 1)])
    art = np.isin(lab, art_ids[art_ids > 0]) & (inside == 1)
    near = cv2.distanceTransform(inside, cv2.DIST_L2, 3) <= reach
    out = np.zeros(g.shape, np.uint8)
    out[wy0:wy1, wx0:wx1] = (art & near).astype(np.uint8)
    return cv2.dilate(out, np.ones((3, 3), np.uint8))


def art_through(g, box, pad=10, thr=12, min_h=18, min_str=20):
    """Art that runs through a see-through text box (Iris's legs, a cane, a coat edge): dark-stroke
    components that reach outside the box, stand at least min_h tall, are taller than they are wide and are
    drawn firmly. Japanese glyphs are at most 14 px tall and sit wholly inside the box, so they never match.
    Returns those pixels inside the box, which the erase must leave alone."""
    x0, y0, x1, y1 = box
    H, W = g.shape
    wx0, wy0, wx1, wy1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    sub = g[wy0:wy1, wx0:wx1].astype(np.uint8)
    res = cv2.medianBlur(sub, 9).astype(int) - sub.astype(int)
    dark = (res > thr).astype(np.uint8)
    inside = np.zeros_like(dark)
    inside[y0 - wy0:y1 - wy0, x0 - wx0:x1 - wx0] = 1
    n, lab, st, _ = cv2.connectedComponentsWithStats(dark, 8)
    out_ids = set(np.unique(lab[(inside == 0) & (dark == 1)]).tolist())
    keep = np.zeros(n, bool)
    for i in range(1, n):
        keep[i] = (i in out_ids and st[i, 3] >= min_h and st[i, 3] >= 1.2 * st[i, 2]
                   and res[lab == i].mean() >= min_str)
    o = np.zeros(g.shape, np.uint8)
    o[wy0:wy1, wx0:wx1] = (keep[lab] & (inside == 1)).astype(np.uint8)
    o = cv2.dilate(o, np.ones((3, 3), np.uint8))
    nk, lk, stk, _ = cv2.connectedComponentsWithStats(o, 8)
    return np.isin(lk, [i for i in range(1, nk) if stk[i, 3] >= 12]).astype(np.uint8)


LHF = [1.22]


def do_page(page, spec, en):
    LHF[0] = 1.22
    a = np.asarray(Image.open(os.path.join(HERE, 'orig', page + '.png')).convert('RGB')).copy()
    mask = np.zeros(a.shape[:2], np.uint8)
    for b in spec['boxes']:
        mask |= glyph_mask(a, b, spec['mode'] == 'overlay')
    bgr = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    clean = cv2.cvtColor(cv2.inpaint(bgr, mask * 255, 4, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    if os.environ.get('ERASE') == 'lama' and spec['mode'] != 'panel':
        # LaMa (big-lama) at 2x on the same masks, one call per box; only masked pixels change
        import lama_inpaint as LI
        clean = a.copy()
        for b in spec['boxes']:
            bm = np.zeros_like(mask); x0, y0, x1, y1 = b
            bm[max(0, y0 - 3):y1 + 3, max(0, x0 - 3):x1 + 3] = mask[max(0, y0 - 3):y1 + 3, max(0, x0 - 3):x1 + 3]
            clean = LI.inpaint(clean, bm, b, scale=2)
    if os.environ.get('ERASE') == 'lama2' and spec['mode'] == 'overlay':
        # LaMa on the thin two-pass mask of relabelling_method.md (16 then 12, 13x1 seams kept, dilate 3x3),
        # so panel border lines and dark art that never held text are passed through untouched
        import lama_inpaint as LI
        clean = a.copy()
        for thr in (16, 12):
            g = cv2.cvtColor(clean, cv2.COLOR_RGB2GRAY)
            flat = cv2.medianBlur(g, 7)
            for b in spec['boxes']:
                # the hand-marked boxes sit on the glyph bodies; the tops of the first line and the tails of the
                # last reach 3-4 px beyond them and were left as dashes (user, 2026-09-15): erase a wider band
                bx0, by0, bx1, by1 = b
                x0, y0, x1, y1 = bx0, max(VIS[1], by0 - 4), bx1, min(VIS[3], by1 + 3, spec.get('panel_bottom', 999))
                res = ((flat.astype(int) - g.astype(int)) > thr).astype(np.uint8)
                m2 = np.zeros(g.shape, np.uint8)
                m2[by0:by1, bx0:bx1] = res[by0:by1, bx0:bx1]
                # in the extra strip, only strokes joined to a glyph inside the box and close to the ink colour
                # (glyph tops/tails); hems, hair and small production notes there stay
                ext = np.zeros_like(m2); ext[y0:y1, x0:x1] = res[y0:y1, x0:x1]
                nl_, lab_ = cv2.connectedComponents(ext, connectivity=8)
                ids = np.unique(lab_[m2 == 1]); ids = ids[ids > 0]
                inkish = (np.linalg.norm(clean.astype(float) - INK, axis=-1) < 70)
                strip = np.isin(lab_, ids) & (m2 == 0) & inkish
                # and their soft edges: anything faintly darker (> 5) right next to those strokes, inside the strip
                # the Japanese carries a pale outline too: take everything within 2 px of those strokes
                soft = cv2.dilate(strip.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
                band_ = np.zeros(g.shape, bool); band_[y0:y1, x0:x1] = True; band_[by0:by1, bx0:bx1] = False
                m2 |= (strip | (soft & band_)).astype(np.uint8)
                b = (x0, y0, x1, y1)
                seams = cv2.morphologyEx(m2, cv2.MORPH_OPEN, np.ones((13, 1), np.uint8))
                m2 = m2 & (1 - cv2.dilate(seams, np.ones((3, 3), np.uint8)))
                protect = art_entering(g, b) & (~ink_grey(clean)).astype(np.uint8) if os.environ.get('ART_PROTECT', '0') == '1' else np.zeros_like(m2)   # off: kept glyph tops (ink cores are saturated)
                # 5x5: the Japanese has a pale outline that a 3x3 grow leaves as ghost shapes; with the English
                # now starting lower, those showed above the first line (user, 2026-09-15)
                m2 = cv2.dilate(m2 & (1 - protect), np.ones((5, 5), np.uint8)) & (1 - protect)
                if m2.any():
                    clip = None if os.environ.get('LAMA_CLIP', '1') == '0' else (max(VIS[0], x0 - 2), y0, min(VIS[2], x1 + 2), min(VIS[3], y1, spec.get('panel_bottom', 999)))
                    clean = LI.inpaint(clean, m2, b, scale=2, clip=clip)
                    g = cv2.cvtColor(clean, cv2.COLOR_RGB2GRAY); flat = cv2.medianBlur(g, 7)
    if os.environ.get('ERASE') == 'lama2' and spec['mode'] == 'cream':
        # plain background: Japanese = dark shapes wholly inside the box (art entering from outside is
        # protected), filled flat with the page's own background colour; Telea smeared shoes, hats and
        # frame edges here (user, 2026-09-15)
        from collections import Counter
        clean = a.copy()
        g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
        for b in spec['boxes']:
            x0, y0, x1, y1 = b
            H_, W_ = g.shape
            wx0, wy0, wx1, wy1 = max(0, x0 - 8), max(0, y0 - 8), min(W_, x1 + 8), min(H_, y1 + 8)
            dark = ((cv2.medianBlur(g, 9).astype(int) - g.astype(int)) > 16).astype(np.uint8)
            nonbg = (np.abs(a.astype(int) - np.array(T.BG)).max(-1) > 10).astype(np.uint8)
            cand = np.zeros_like(dark); cand[wy0:wy1, wx0:wx1] = (dark | nonbg)[wy0:wy1, wx0:wx1]
            inbox = np.zeros_like(cand); inbox[max(0, y0 - 1):y1 + 1, max(0, x0 - 1):x1 + 1] = 1
            n, lab = cv2.connectedComponents(cand, connectivity=8)
            protect = art_entering(g, b) if spec.get('erase_fused') else np.zeros_like(cand)
            glyph = np.zeros_like(cand)
            for i_ in range(1, n):
                comp = lab == i_
                ys = np.nonzero(comp)[0]
                # a Japanese glyph lies wholly inside the box (1 px slack); anything continuing outside is art
                out_px = int((comp & (inbox == 0)).sum())
                # mostly inside = a glyph that pokes past the hand-drawn box (punctuation, brackets);
                # art entering the box has most of its body outside
                if out_px == 0 or (out_px < 0.5 * comp.sum() and ys.max() - ys.min() <= 18):
                    if ys.max() - ys.min() <= 16:
                        glyph[comp] = 1
                else:
                    # art fused with a glyph (a hair strand touching a character): erase the part inside the
                    # box, except the art's last 6 px where it enters (art_entering keeps those). This does
                    # cost the tips of the pencil hair on aoc06_design_04, which share pixels with the
                    # writing; rules that kept them (near a recognised glyph, or by stroke strength: the
                    # Japanese averages a residual of 86 there and the hair 50, but the two overlap) each
                    # left readable kana behind, so the tips stay clipped (user review, 2026-09-15).
                    if spec.get('erase_fused'):
                        glyph[comp & (inbox == 1) & ink_grey(a)] = 1
            # punctuation the hand-drawn box just missed: small shapes lying wholly within 6 px outside
            # the box (full stops, corner brackets), not connected to anything else
            near = np.zeros_like(cand); near[max(0, y0 - 6):y1 + 6, max(0, x0 - 6):x1 + 6] = 1
            for i in range(1, n):
                comp = lab == i
                if glyph[comp].any():
                    continue
                ys, xs = np.nonzero(comp)
                if (not (comp & (near == 0)).any() and ys.max() - ys.min() <= 12 and xs.max() - xs.min() <= 12
                        and ink_grey(a)[comp].mean() > 0.3):
                    glyph[comp] = 1
            m = cv2.dilate(glyph, np.ones((3, 3), np.uint8)) & (1 - protect)
            bgc = np.array(T.BG, np.uint8)
            clean[m.astype(bool)] = bgc
            mask |= m
    if os.environ.get('ERASE') == 'v2' and spec['mode'] == 'overlay':
        # relabelling_method.md class B, at native size: median 11 -> 7, seam 25 -> 13, two passes 16 then 12,
        # Telea r3, vertical art lines protected; starts again from the untouched page
        clean = a.copy()
        for thr in (16, 12):
            g = cv2.cvtColor(clean, cv2.COLOR_RGB2GRAY)
            flat = cv2.medianBlur(g, 7)
            m2 = np.zeros(g.shape, np.uint8)
            for b in spec['boxes']:
                x0, y0, x1, y1 = b
                m2[y0:y1, x0:x1] = ((flat.astype(int) - g.astype(int)) > thr)[y0:y1, x0:x1]
            seams = cv2.morphologyEx(m2, cv2.MORPH_OPEN, np.ones((13, 1), np.uint8))
            m2 = m2 & (1 - cv2.dilate(seams, np.ones((3, 3), np.uint8)))
            m2 = cv2.dilate(m2, np.ones((3, 3), np.uint8))
            clean = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(clean, cv2.COLOR_RGB2BGR), m2 * 255, 3, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    if os.environ.get('ERASE') == 'see' and spec['mode'] == 'overlay':
        # Keep the see-through panel. Nothing in the box is repainted and nothing is invented, so nothing
        # can smear: the Japanese is simply lifted out of it. The ink is whatever is darker than its own
        # surroundings, so a per-channel median-7 of the page is what the panel looks like without it;
        # each pixel is blended towards that estimate in proportion to how much darker than it the pixel
        # is. Two passes, the second gentler, so the glyphs' pale outline goes as well. Flat art keeps its
        # colour (its inside is not darker than its surroundings) and art that runs through the box is
        # protected outright. Replaces ERASE=lama2, whose 5x5 mask covered 74% of a box and made LaMa
        # repaint the whole panel (user, 2026-09-15: blurred band, smeared legs, grey lumps).
        clean = a.copy()
        sel = np.zeros(a.shape[:2], np.float32)
        protect = np.zeros(a.shape[:2], np.uint8)
        g0 = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
        for b in spec['boxes']:
            bx0, by0, bx1, by1 = b
            # Never reach above the panel's own top edge, measured on the page (erase_top). The four
            # rows above the marked box exist for glyph tops that poke out of it, but on most pages
            # they sit on full-strength artwork instead, and lifting there smudged it (user, three
            # rounds of this). Above the panel there is no Japanese to remove.
            ty0 = max(VIS[1], by0 - 4, spec.get('erase_top', 0))
            # erase_bottom bounds the ERASE only. panel_bottom also bounds where the text may sit, and
            # using it to keep the erase off aoc02_design_07's dark bottom band cost that page two
            # pixels of type size.
            ty1 = min(VIS[3], by1 + 3, spec.get('erase_bottom', spec.get('panel_bottom', 999)))
            top = max(by0, ty0)          # the full lift starts at the panel, not at the marked box
            sel[top:ty1, bx0:bx1] = 1.0
            # Above the marked box, only the tops of the first line's strokes may be lifted. Taking the whole
            # strip faded the drawing out over those rows wherever it is grey, which the colour ramp cannot
            # catch (aoc05_design_06's pencil sketch). A glyph top is joined to a stroke inside the box.
            if top > ty0:
                cand = (((cv2.medianBlur(g0, 9).astype(int) - g0.astype(int)) > 12) & ink_grey(a)).astype(np.uint8)
                win = np.zeros(g0.shape, np.uint8)
                win[ty0:top + 3, bx0:bx1] = 1
                # Grow up from the ink inside the box a step at a time, never past the strip, instead of
                # taking whole components: a pencil line that crosses a glyph top is one component with it,
                # and taking the whole thing smudged the sketch above the first line (user, 2026-09-15).
                cand = (cand * win).astype(np.uint8)
                tops = np.zeros(g0.shape, np.uint8)
                tops[top:top + 2, bx0:bx1] = cand[top:top + 2, bx0:bx1]
                for _ in range(top - ty0):
                    tops = cv2.dilate(tops, np.ones((3, 3), np.uint8)) & cand
                tops = cv2.dilate(tops, np.ones((3, 3), np.uint8))
                # accumulate: where a page's box is split, the lower half's strip sits inside the
                # upper half's box, and a plain assignment wiped out the full lift asked for there
                # (aoc07_design_07 left a whole line of Japanese standing)
                sel[ty0:top, bx0:bx1] = np.maximum(sel[ty0:top, bx0:bx1], tops[ty0:top, bx0:bx1])
            # SEE_KEEP=1 also protects art that runs through the box. It is OFF: the lift already leaves
            # broad art alone (the inside of a dark shape is not darker than its surroundings), and the
            # protection kept specks of Japanese fused to thin strokes (aoc02_design_07, aoc05_design_07)
            if os.environ.get('SEE_KEEP', '0') == '1':
                protect |= art_through(g0, (bx0, ty0, bx1, ty1))
        # Japanese that fuses with a firm stroke behind it makes a tall narrow component too and was
        # being protected as art (aoc05_design_07 kept a whole word): nothing in the ink's own neutral
        # grey is ever protected
        protect = (protect & (~ink_grey(a)).astype(np.uint8))
        protect = cv2.morphologyEx(protect, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        nk, lk, stk, _ = cv2.connectedComponentsWithStats(protect, 8)
        protect = np.isin(lk, [i for i in range(1, nk) if stk[i, 3] >= 12]).astype(np.uint8)
        sig = float(os.environ.get('SEE_SIG', '3.5'))
        for t0, t1 in ((float(os.environ.get("SEE_T0", "2.0")), float(os.environ.get("SEE_T1", "11.0"))),):
            g = cv2.cvtColor(clean, cv2.COLOR_RGB2GRAY)
            # a median-7 of a dense line of Japanese is itself darkened by the ink, which left speckles of
            # the heaviest glyphs behind; estimate the panel from the pixels that are NOT ink instead
            # (normalised convolution), so the estimate does not know about the strokes at all
            rough = (cv2.medianBlur(g, 9).astype(np.float32) - g.astype(np.float32)) > 2.5
            w = (~rough).astype(np.float32)
            num = cv2.GaussianBlur(clean.astype(np.float32) * w[..., None], (0, 0), sig)
            den = cv2.GaussianBlur(w, (0, 0), sig)[..., None]
            bg = num / np.maximum(den, 1e-3)
            res = (bg @ np.array([0.299, 0.587, 0.114], np.float32)) - g.astype(np.float32)
            # Where nearly everything nearby is ink-dark the estimate has almost nothing to work from and
            # comes out far too light: on aoc02_design_07 that wiped the dark band along the bottom of the
            # box, 150 grey levels across its whole width. Fade the lift out with the estimate's support.
            support = np.clip((den[..., 0] - 0.20) / 0.30, 0, 1)
            # Only the ink's own colour family may be lifted. Without this the estimate, which is pulled
            # bright by the panel just below, fades the coloured art out over the last rows before the
            # panel begins: that is the blurred band along the panel's top edge (user, 2026-09-15).
            # A hard neutral-grey test leaves crumbs where the art tints the ink, so ramp it: fully neutral
            # ink lifts completely, and anything as colourful as the coats and uniforms not at all.
            c = a[..., :3].astype(np.int16)
            sat = (c.max(-1) - c.min(-1)).astype(np.float32)
            grey = np.clip((float(os.environ.get('SEE_SAT', '58')) - sat) / 26.0, 0, 1)
            grey = cv2.dilate(grey, np.ones((3, 3), np.uint8))
            alpha = np.clip((res - t0) / (t1 - t0), 0, 1) * sel * (1 - protect) * support * grey
            clean = (clean.astype(np.float32) * (1 - alpha[..., None])
                     + bg * alpha[..., None]).clip(0, 255).astype(np.uint8)
    if spec['mode'] == 'panel':
        # a flat panel: fill with its own most common colour, never with the art beside it
        from collections import Counter
        x0, y0, x1, y1 = spec['boxes'][0]
        sub = a[y0:y1, x0:x1][mask[y0:y1, x0:x1] == 0]
        col = Counter(map(tuple, sub)).most_common(1)[0][0]
        clean = a.copy(); clean[mask.astype(bool)] = col
    ux0 = min(b[0] for b in spec['boxes']) + 2; uy0 = min(b[1] for b in spec['boxes']) + 2
    ux1 = max(b[2] for b in spec['boxes']) - 2; uy1 = max(b[3] for b in spec['boxes']) - 2
    wash = float(os.environ.get('WASH', '0.35'))
    grow_up = 0
    base = [ux0, uy0, ux1, uy1]
    if spec['mode'] in ('cream', 'panel') and T.render(en, base, FONT, T.MIN_PX)[0] is None:
        # plain background first: grow over clear background in every order, keep the biggest fit
        bgcol = np.median(clean[uy0:uy1, ux0:ux1].reshape(-1, 3), axis=0)
        bgm = np.abs(clean.astype(int) - bgcol.astype(int)).max(axis=-1) <= 8
        best = None
        for order in T.ORDERS:
            cand = T.grow_order(bgm, list(base), order)
            for px in range(T.MAX_PX, T.MIN_PX - 1, -1):
                for lhf in (1.22, 1.12):
                    if T.render(en, cand, FONT, px, lhf)[0] is not None:
                        if best is None or (px, lhf) > (best[0], best[2]): best = (px, cand, lhf)
                        break
                else:
                    continue
                break
        if best:
            ux0, uy0, ux1, uy1 = best[1]
            LHF[0] = best[2]
    if os.environ.get('ERASE') in ('lama2', 'see') and spec['mode'] == 'overlay':
        # English capitals are denser than the thin tops of Japanese strokes, so starting where the Japanese
        # started reads as pressed against the panel's top edge (user, 2026-09-15): start TOP_PAD rows lower.
        # Over art, tighter line spacing beats growing into the picture; if it still does not fit, give back
        # the pad a row at a time before the upward-growth fallback is allowed.
        pad0 = int(os.environ.get('TOP_PAD', '3'))
        if 'area_top' in spec:          # measured panel top: place the text directly, no pad
            uy0, pad0 = spec['area_top'], 0
        last = spec.get('panel_bottom', VIS[3]) - 1     # text area must end inside the panel
        uy1 = min(uy1, last)
        # next, let the area reach up to 3 rows lower, never past the last visible row
        done = False
        for pad in range(pad0, -1, -1):
            for down in range(0, 4):
                bot = min(uy1 + down, last)
                hit = next((l for l in (LHF[0], 1.12, 1.05) if T.render(en, [ux0, uy0 + pad, ux1, bot], FONT, T.MIN_PX, l)[0] is not None), None)
                if hit:
                    uy0 += pad
                    uy1 = bot
                    LHF[0] = hit
                    done = True
                    break
            if done:
                break
    for grow_up in range(0, 44, 4):
        area = [ux0, uy0 - grow_up, ux1, uy1]
        if T.render(en, area, FONT, T.MIN_PX, LHF[0])[0] is not None:
            break
    if os.environ.get('ERASE') in ('lama', 'lama2', 'see'):
        wash = 0.35 if grow_up else 0.0     # LaMa needs no wash; an upward extension over art still gets one
    if wash > 0 and (spec['mode'] == 'overlay' or grow_up):
        # a light cream wash over the text area, feathered over 5 px, to even out fill blotches;
        # the art still shows through, like the original see-through boxes
        fm = np.zeros(a.shape[:2], np.float32)
        fm[ux0 - 2:ux1 + 2, :] = 0
        fm[uy0 - grow_up - 2:uy1 + 2, ux0 - 2:ux1 + 2] = 1.0
        fm = cv2.GaussianBlur(fm, (0, 0), 2.5) * wash
        cream = np.array([255, 250, 236], float)
        clean = np.clip(clean.astype(float) * (1 - fm[..., None]) + cream * fm[..., None], 0, 255).astype(np.uint8)
    for px in range(T.MAX_PX, T.MIN_PX - 1, -1):
        alpha, lines = T.render(en, area, FONT, px, LHF[0])
        if alpha is not None:
            x0, y0, x1, y1 = area
            reg = clean[y0:y1, x0:x1].astype(float)
            clean[y0:y1, x0:x1] = np.clip(reg * (1 - alpha[..., None]) + INK * alpha[..., None], 0, 255).astype(np.uint8)
            keep = np.ones(clean.shape[:2], bool); keep[VIS[1]:VIS[3], VIS[0]:VIS[2]] = False
            clean[keep] = a[keep]          # nothing outside the visible window may change
            return Image.fromarray(clean), px, area, int(mask.sum())
    return Image.fromarray(clean), None, area, int(mask.sum())


def main():
    boxes = json.load(open(os.path.join(HERE, 'boxes_medium.json')))
    en = {json.loads(l)['page']: json.loads(l)['en'] for l in io.open(os.path.join(HERE, 'translations.jsonl'), encoding='utf-8') if l.strip()}
    only = sys.argv[1].split(',') if len(sys.argv) > 1 else sorted(boxes)
    out = os.path.join(HERE, os.environ.get('OUTDIR', 'typeset_medium'))
    os.makedirs(out, exist_ok=True)
    nofit = []
    for p in only:
        im, px, area, npx = do_page(p, boxes[p], en[p])
        tag = '%2d px' % px if px else 'NO FIT'
        if px is None:
            nofit.append(p)
            save(im, os.path.join(out, '_erased_' + p + '.png'))
        else:
            save(im, os.path.join(out, p + '.png'))
            b = Image.open(os.path.join(HERE, 'orig', p + '.png')).convert('RGB').crop(VIS).resize((800, 480), Image.LANCZOS)
            c = im.crop(VIS).resize((800, 480), Image.LANCZOS)
            cm = Image.new('RGB', (1610, 480)); cm.paste(b, (0, 0)); cm.paste(c, (810, 0)); save(cm, os.path.join(out, '_cmp_' + p + '.png'))
        print('%-16s %-7s %-8s area %s, %d px erased' % (p, boxes[p]['mode'], tag, area, npx))
    print('%d pages, %d did not fit: %s' % (len(only), len(nofit), ', '.join(nofit)))


if __name__ == '__main__':
    main()

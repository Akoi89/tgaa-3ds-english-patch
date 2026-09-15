# -*- coding: utf-8 -*-
"""Replace the Japanese title on the 8 theme preview pages with English.

Measured 2026-09-14 on the theme pages: the top divider (row 28) and bottom divider (row 229) are the
same design, and the band around the title repeats exactly 201 rows lower (mean abs diff ~1/255 where
nothing covers it). The whole background is mirror-symmetric about x = AXIS (diff 0.00). So the title
band is rebuilt from the bottom band, using the mirrored column where the lower-screen mock-up covers
the bottom band on the right. Then the English title is drawn like the Japanese one: a dark glow that
hides the divider line under the text, a dark outline, and a pale fill (colours sampled per page).

    python theme_titles.py [--font georgiab] [--out typeset_themes]
"""
import argparse
import io
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
OFF = 201
BAND = (10, 48)          # rows holding the title
FONTS = {'georgiab': ('georgiab.ttf', None), 'segoeui-b': ('segoeuib.ttf', None), 'bahn-sb': ('bahnschrift.ttf', b'SemiBold'),
         'candarab': ('Candarab.ttf', None)}


def mirror_axis(a):
    best = None
    for c2 in range(436, 460):
        left = a[12:44, 30:100]
        right = a[12:44, c2 - 99:c2 - 29][:, ::-1]
        e = np.abs(left - right).mean()
        if best is None or e < best[0]:
            best = (e, c2)
    return best[1], best[0]


def rebuild_band(a):
    c2, err = mirror_axis(a)
    y0, y1 = BAND
    out = a.copy()
    # which bottom-band columns are clean: compare with the top band far from the title, per column,
    # using the mirror: a column is usable when bottom(x) matches bottom(mirror x) outside the title rows
    # the background is exactly mirror-symmetric (diff 0.00) and the bottom band's left half is clean,
    # so: left half from the bottom band as is, right half from the bottom band mirrored. No per-column
    # switching (an earlier per-column test left a one-column seam at x 382 on aoc07).
    for x in range(VIS[0], VIS[2]):
        src = x if x <= (c2 - 1) / 2.0 else c2 - 1 - x
        out[y0:y1, x] = a[y0 + OFF:y1 + OFF, src]
    return out, c2 / 2.0, err


def title_colours(a, clean):
    band = a[BAND[0]:BAND[1], VIS[0]:VIS[2]]
    bg = clean[BAND[0]:BAND[1], VIS[0]:VIS[2]]
    diff = np.abs(band - bg).sum(axis=-1) > 60
    px = band[diff]
    lum = px.mean(axis=1)
    fill = px[lum >= np.percentile(lum, 85)].mean(axis=0)
    dark = px[lum <= np.percentile(lum, 10)].mean(axis=0)
    ys, xs = np.nonzero(diff)
    return fill, dark, (int(xs.min()) + VIS[0], int(ys.min()) + BAND[0], int(xs.max()) + VIS[0] + 1, int(ys.max()) + BAND[0] + 1)


def draw_title(clean, text, fill, dark, jp_box, fontspec, axis):
    S = 4
    H = 26
    for px in range(20, 11, -1):
        f = ImageFont.truetype(fontspec[0], px * S)
        if fontspec[1]:
            f.set_variation_by_name(fontspec[1])
        w = f.getlength(text)
        if w <= 330 * S:
            break
    W = int(w) + 16 * S
    PAD = 12                    # rows of canvas above and below the text so the glow fades out instead of
                                # being cut flat at the canvas edge (user, 2026-09-15: title tops looked clipped)
    cy = (jp_box[1] + jp_box[3]) / 2.0
    x0 = int(round(axis - W / (2.0 * S)))
    y0 = int(round(cy - H / 2.0)) - PAD
    HH = H + 2 * PAD
    mask = Image.new('L', (W, HH * S), 0)
    d = ImageDraw.Draw(mask)
    asc, desc = f.getmetrics()
    ty = PAD * S + (H * S - (asc + desc)) // 2
    d.text((8 * S, ty), text, font=f, fill=255)
    glyph = np.asarray(mask.resize((W // S, HH), Image.LANCZOS)).astype(float) / 255
    outline = np.asarray(mask.filter(ImageFilter.MaxFilter(2 * S + 1)).resize((W // S, HH), Image.LANCZOS)).astype(float) / 255
    glow = np.asarray(mask.filter(ImageFilter.MaxFilter(3 * S + 1)).filter(ImageFilter.GaussianBlur(2 * S)).resize((W // S, HH), Image.LANCZOS)).astype(float) / 255
    out = clean.copy().astype(float)
    reg = out[y0:y0 + HH, x0:x0 + W // S]
    # glow kept close to the Japanese title's: a soft shadow, not a dark cloud over the band (user, 2026-09-15)
    for alpha, col in ((np.clip(glow * 0.9, 0, 0.6), dark * 0.7), (outline, dark), (glyph, fill)):
        reg[:] = reg * (1 - alpha[..., None]) + np.array(col)[None, None, :] * alpha[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--font', default='georgiab')
    ap.add_argument('--out', default='typeset_themes')
    a_ = ap.parse_args()
    spec = (os.path.join(r'C:\Windows\Fonts', FONTS[a_.font][0]), FONTS[a_.font][1])
    en = {json.loads(l)['page']: json.loads(l)['en'] for l in io.open(os.path.join(HERE, 'translations.jsonl'), encoding='utf-8') if l.strip()}
    out = os.path.join(HERE, a_.out)
    os.makedirs(out, exist_ok=True)
    for n in range(1, 9):
        page = 'aoc%02d_theme' % n
        a = np.asarray(Image.open(os.path.join(HERE, 'orig', page + '.png')).convert('RGB')).astype(int)
        clean, axis, err = rebuild_band(a)
        fill, dark, jp_box = title_colours(a, clean)
        title = '\u201c%s\u201d' % en[page]
        res, px = draw_title(clean, title, fill, dark, jp_box, spec, axis)
        Image.fromarray(res).save(os.path.join(out, page + '.png'))
        b = Image.fromarray(a.astype(np.uint8)).crop(VIS).resize((800, 480), Image.LANCZOS)
        c = Image.fromarray(res).crop(VIS).resize((800, 480), Image.LANCZOS)
        cmp_ = Image.new('RGB', (1610, 480)); cmp_.paste(b, (0, 0)); cmp_.paste(c, (810, 0))
        cmp_.save(os.path.join(out, '_cmp_' + page + '.png'))
        print('%-12s axis %.1f (mirror err %.2f)  JP title box %s  fill %s dark %s  -> %d px "%s"' % (
            page, axis, err, jp_box, fill.astype(int).tolist(), dark.astype(int).tolist(), px, en[page]))


if __name__ == '__main__':
    main()

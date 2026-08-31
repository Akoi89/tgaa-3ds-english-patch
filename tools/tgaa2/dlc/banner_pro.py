# -*- coding: utf-8 -*-
"""Professional-grade English rebuild of the three TGAA2 DLC banners.

Principles:
  * character art / silhouettes keep their ORIGINAL pixels (per-row art
    boundary detection keeps every mask out of the art)
  * all typography is rendered at 4x and Lanczos-downsampled, so the glyph
    edges are supersampled instead of PIL's 1x hinting
  * body text is wrapped per-line against the art boundary, so it fills the
    plate the way a typeset page would
  * fully English: title, body, ribbon, scroll

    python banner_pro.py preview   -> *_pro.png (+ *_pro_view.png at 400x240)
    python banner_pro.py apply     -> writes the .tex files
"""
import os, sys

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

from banner_translate import load, save_tex, font, art_left

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('BANNER_OUT', HERE)
SS = 4                       # supersample factor for all text
VIS = (24, 8, 424, 248)


def f4(name, size):
    return font(name, size * SS)


def text_layer():
    lay = Image.new('RGBA', (512 * SS, 256 * SS), (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay)


def compose(bg_rgb, lay):
    lay = lay.resize((512, 256), Image.LANCZOS)
    im = Image.fromarray(bg_rgb).convert('RGBA')
    im.alpha_composite(lay)
    return np.asarray(im.convert('RGB')).copy()


def wrap_to_widths(words, widths, meas):
    """greedy wrap; returns None if the paragraph does not fit"""
    lines, cur, li = [], '', 0
    for w in words:
        cand = (cur + ' ' + w).strip()
        if li >= len(widths):
            return None
        if meas(cand) <= widths[li]:
            cur = cand
        else:
            if not cur:
                return None
            lines.append(cur)
            li += 1
            if li >= len(widths):
                return None
            cur = w
            if meas(cur) > widths[li]:
                return None
    lines.append(cur)
    return lines


# ------------------------------------------------------------------ scenario
def scenario(name, title, body_para, title_x1, out_png, tex_in, tex_out, apply):
    header, rgb, alpha = load(tex_in)

    # ---- clean background (identical recipe to the shipped v9 pass) ----
    def ink_mask(box, thresh):
        x0, y0, x1, y1 = box
        z = rgb[y0:y1, x0:x1].astype(int)
        lum = z.mean(axis=2)
        sat = z.max(axis=2) - z.min(axis=2)
        m = np.zeros(rgb.shape[:2], np.uint8)
        m[y0:y1, x0:x1] = ((lum < thresh) & (sat < 45)).astype(np.uint8) * 255
        return m
    mask = ink_mask((40, 44, title_x1 + 14, 92), 150)
    mask |= ink_mask((36, 96, 246, 232), 150)
    lims = art_left(rgb, 40, 236, 270)
    xs = np.arange(rgb.shape[1])[None, :]
    mask[(xs >= lims[:, None] - 2)] = 0
    # ribbon text comes off too (redrawn in English)
    rz = rgb[0:52, 8:170].astype(int)
    rl = rz.mean(axis=2)
    mask[0:52, 8:170] |= (rl < 140).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((2, 2), np.uint8))
    ribbon_px = mask[0:52, 8:170] > 0
    bg = cv2.inpaint(rgb, mask, 3, cv2.INPAINT_TELEA)
    # ribbon band: solid fill beats inpaint mush on the flat mauve band
    zone = bg[0:52, 8:170]
    donors = zone[~ribbon_px]
    dl = donors.astype(int).mean(axis=1)
    med = np.median(donors[(dl > 110) & (dl < 205)], axis=0).astype(np.uint8)
    zone[ribbon_px] = med
    bg[0:52, 8:170] = cv2.GaussianBlur(zone, (3, 3), 0)
    # true art boundary, measured on the CLEANED plate (no JP ink left)
    lims = art_left(bg, 44, 236, 270)

    # ---- typography at 4x ----
    lay, d = text_layer()
    ox, oy = VIS[0] * SS, 0   # texture coords already include the offset

    # title: single line if it can be >=21px, else two lines
    words = title.split()
    for size in range(27, 15, -1):
        ft = f4('georgiab.ttf', size)
        if d.textlength(title, font=ft) <= (title_x1 - 42) * SS:
            break
    two = size < 19 and len(words) >= 3
    ink = (52, 38, 30)
    halo = (232, 220, 192)
    if not two:
        cx = (42 + title_x1) // 2 * SS
        y = 64 * SS
        d.text((cx, y), title, font=ft, fill=ink, anchor='mm',
               stroke_width=SS, stroke_fill=halo)
        # thin rule with a diamond, under the title
        ry = 85 * SS
        rx0, rx1 = 46 * SS, (title_x1 - 6) * SS
        rcx = (rx0 + rx1) // 2
        rule = (110, 82, 60)
        d.line([(rx0, ry), (rcx - 7 * SS, ry)], fill=rule, width=SS)
        d.line([(rcx + 7 * SS, ry), (rx1, ry)], fill=rule, width=SS)
        d.polygon([(rcx, ry - 4 * SS), (rcx + 5 * SS, ry),
                   (rcx, ry + 4 * SS), (rcx - 5 * SS, ry)], fill=rule)
    else:
        half = (len(words) + 1) // 2
        l1, l2 = ' '.join(words[:half]), ' '.join(words[half:])
        for size in range(30, 15, -1):
            ft = f4('georgiab.ttf', size)
            if max(d.textlength(t, font=ft) for t in (l1, l2)) \
                    <= (title_x1 - 44) * SS:
                break
        cx = (42 + title_x1) // 2 * SS
        for t, y in ((l1, 58), (l2, 82)):
            d.text((cx, y * SS), t, font=ft, fill=ink, anchor='mm',
                   stroke_width=SS, stroke_fill=halo)

    # body: per-line widths follow the art boundary
    for size, lead in ((15, 18), (14, 17), (13, 16)):
        fb = f4('georgia.ttf', size)
        nmax = (234 - 96) // lead
        widths = []
        for i in range(nmax):
            y0, y1 = 96 + i * lead, 96 + i * lead + size + 2
            lim = min(lims[y0:y1 + 1]) if y1 + 1 <= 236 else min(lims[y0:236])
            widths.append((min(lim - 8, 242) - 40) * SS)
        lines = wrap_to_widths(body_para.split(), widths,
                               lambda s: d.textlength(s, font=fb))
        if lines:
            break
    assert lines, (name, 'body does not fit')
    for i, line in enumerate(lines):
        d.text((40 * SS, (98 + i * lead) * SS), line, font=fb,
               fill=(58, 48, 40))

    # ribbon: rotated English on the original band
    band = Image.new('RGBA', (170 * SS, 30 * SS), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    fr = f4('georgiab.ttf', 12)
    bd.text((85 * SS, 15 * SS), 'Ace Attorney Stories', font=fr,
            fill=(66, 28, 38), anchor='mm')
    band = band.rotate(9, expand=True, resample=Image.BICUBIC)
    lay.alpha_composite(band, (6 * SS, 1 * SS))

    out = compose(bg, lay)
    Image.fromarray(out).save(os.path.join(OUT, name + '_pro.png'))
    Image.fromarray(out[VIS[1]:VIS[3], VIS[0]:VIS[2]]).save(
        os.path.join(OUT, name + '_pro_view.png'))
    if apply:
        save_tex(tex_out, header, out, alpha)
    print('scenario %s -> %d body lines, title %s' %
          (name, len(lines), 'two-line' if two else 'one-line'))


# ------------------------------------------------------------------- costume
def costume(out_png_base, tex_in, tex_out, apply):
    header, rgb, alpha = load(tex_in)
    lum_all = rgb.astype(int).mean(axis=2)

    def not_gold(box):
        zx0, zy0, zx1, zy1 = box
        z = rgb[zy0:zy1, zx0:zx1].astype(int)
        l = z.mean(axis=2)
        r, g, b = z[:, :, 0], z[:, :, 1], z[:, :, 2]
        m = np.zeros(rgb.shape[:2], np.uint8)
        m[zy0:zy1, zx0:zx1] = (~((r - b > 40) & (r > 140) & (g > 120) &
                                 (l > 120) & (r - g < 60))
                               ).astype(np.uint8) * 255
        return m

    # coat-flap pocket: a JP glyph bridges both flaps there; it is neutral
    # grey while the flaps are warm, so kill it early by colour and fill
    # each row from its own horizontal neighbours
    gx0, gy0, gx1, gy1 = 130, 184, 174, 228
    pz = rgb[gy0:gy1, gx0:gx1].astype(int)
    pl = pz.mean(axis=2)
    pm = ((pz[:, :, 0] - pz[:, :, 1] < 16) & (pl < 115))
    pm = cv2.dilate(pm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    for j in range(pm.shape[0]):
        badx = np.where(pm[j])[0]
        goodx = np.where(~pm[j])[0]
        if len(badx) and len(goodx) >= 2:
            for c in range(3):
                rgb[gy0 + j, gx0 + badx, c] = np.interp(
                    badx, goodx, rgb[gy0 + j, gx0 + goodx, c])
    lum_all = rgb.astype(int).mean(axis=2)

    band = not_gold((92, 6, 392, 62)) | not_gold((118, 98, 345, 230))
    dark = (lum_all < 105).astype(np.uint8)
    dark[:8, :] = 0
    dark[234:, :] = 0
    er = cv2.erode(dark, np.ones((3, 3), np.uint8))
    n, lab = cv2.connectedComponents(er)
    edge = set(np.unique(lab[8:234, :116])) | set(np.unique(lab[8:234, 347:]))
    edge.discard(0)
    core = np.isin(lab, list(edge)).astype(np.uint8)
    protect = (cv2.dilate(core, np.ones((7, 7), np.uint8)) > 0) & (lum_all < 135)
    protect[:32, 100:392] = False
    band[protect] = 0
    band = cv2.dilate(band, np.ones((2, 2), np.uint8))
    band[protect] = 0
    band[:17, 68:392] = 255
    band[17:42, 68:392] |= ((lum_all[17:42, 68:392] < 148).astype(np.uint8) * 255)

    sx0, sy0, sx1, sy1 = 137, 63, 310, 95
    z = rgb[sy0:sy1, sx0:sx1].astype(int)
    lz = z.mean(axis=2)
    rr, gg, bb = z[:, :, 0], z[:, :, 1], z[:, :, 2]
    goldtxt = (rr > 150) & (gg > 110) & (bb < 120) & (rr - bb > 60)
    scroll = np.zeros(rgb.shape[:2], np.uint8)
    scroll[sy0:sy1, sx0:sx1] = ((lz < 130) | goldtxt).astype(np.uint8) * 255
    scroll = cv2.dilate(scroll, np.ones((2, 2), np.uint8))
    scroll[protect] = 0

    for y in range(6, 17):        # maroon band + gold rule: solid row medians
        seg = np.concatenate([rgb[y, 44:68], rgb[y, 400:470]], axis=0)
        med = np.median(seg, axis=0).astype(np.uint8)
        xs_bad = np.where(band[y, 68:392] > 0)[0] + 68
        rgb[y, xs_bad] = med
        band[y, xs_bad] = 0

    bad = band > 0                # rays: windowed per-column interpolation
    for w0, w1 in ((17, 96), (96, 232)):
        for x in range(512):
            rows = np.arange(w0, w1)
            cb = rows[bad[w0:w1, x]]
            if len(cb) == 0:
                continue
            cg = rows[~bad[w0:w1, x]]
            if len(cg) == 0:
                continue
            for c in range(3):
                rgb[cb, x, c] = np.interp(cb, cg, rgb[cg, x, c])
    soft = cv2.GaussianBlur(rgb, (1, 7), 0)
    rgb[bad] = soft[bad]

    # residual sweep: small dark blobs clear of the silhouettes
    lum2 = rgb.astype(int).mean(axis=2)
    dark2 = np.zeros(rgb.shape[:2], np.uint8)
    dark2[6:62, 92:392] = (lum2[6:62, 92:392] < 125).astype(np.uint8)
    dark2[98:230, 118:345] = (lum2[98:230, 118:345] < 125).astype(np.uint8)
    dist = cv2.distanceTransform((core == 0).astype(np.uint8), cv2.DIST_L2, 3)
    dark2[dist <= 3] = 0
    n2, lab2 = cv2.connectedComponents(dark2)
    sizes = np.bincount(lab2.ravel())
    resid = np.zeros(rgb.shape[:2], np.uint8)
    for i in range(1, n2):
        if sizes[i] < 2000:
            resid[lab2 == i] = 255
    resid = cv2.dilate(resid, np.ones((3, 3), np.uint8))
    rgb = cv2.inpaint(rgb, resid, 4, cv2.INPAINT_TELEA)

    # glyph bits ON the silhouettes -> nearest silhouette colour
    lum3 = rgb.astype(int).mean(axis=2)
    box = np.zeros(rgb.shape[:2], bool)
    box[6:62, 56:392] = True
    box[96:232, 100:352] = True
    d2, lbl = cv2.distanceTransformWithLabels(
        (core == 0).astype(np.uint8), cv2.DIST_L2, 3,
        labelType=cv2.DIST_LABEL_PIXEL)
    ys_c, xs_c = np.where(core > 0)
    coreidx = np.zeros(lbl.max() + 1, np.int64)
    coreidx[lbl[ys_c, xs_c]] = ys_c * 512 + xs_c
    bits = box & (lum3 < 85) & (d2 <= 14)
    byx = np.where(bits)
    rgb[byx] = rgb.reshape(-1, 3)[coreidx[lbl[byx]]]
    smooth = cv2.GaussianBlur(rgb, (5, 5), 0)
    rgb[bits] = smooth[bits]

    bg = cv2.inpaint(rgb, scroll, 3, cv2.INPAINT_NS)

    # ---- typography at 4x ----
    lay, d = text_layer()
    s = 'SPECIAL COSTUMES'
    ft = f4('Candarab.ttf', 38)
    total = sum(d.textlength(c, font=ft) for c in s)
    x = 224 * SS - total / 2
    for c in s:
        w = d.textlength(c, font=ft)
        t = (x + w / 2 - 224 * SS) / (140.0 * SS)
        y = (26 + 10 * (t * t) - 4) * SS
        gsz = 72 * SS
        glyph = Image.new('RGBA', (gsz, gsz), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        # dark red drop shadow, then cream-outlined red fill
        gd.text((gsz // 2, gsz // 2 + 3 * SS), c, font=ft,
                fill=(126, 28, 34), anchor='mm',
                stroke_width=2 * SS, stroke_fill=(126, 28, 34))
        gd.text((gsz // 2, gsz // 2), c, font=ft, fill=(186, 41, 47),
                anchor='mm', stroke_width=2 * SS, stroke_fill=(255, 250, 238))
        glyph = glyph.rotate(-t * 9, resample=Image.BICUBIC)
        lay.alpha_composite(glyph, (int(x + w / 2 - gsz // 2),
                                    int(y - gsz // 2 + 28 * SS)))
        x += w
    fr = f4('Candarab.ttf', 17)
    d.text((224 * SS, 78 * SS), '3-Costume Pack', font=fr,
           fill=(207, 184, 43), anchor='mm',
           stroke_width=2 * SS, stroke_fill=(63, 39, 34))
    fb = f4('Candarab.ttf', 14)
    body = ['Naruhodo, Sholmes and Susato',
            'transform in style with these',
            'special outfits!! Don brand-new',
            'costumes drawn by Art Director',
            'Kazuya Nuri and play through',
            'the main story!!']
    for i, line in enumerate(body):
        d.text((224 * SS, (108 + i * 19) * SS), line, font=fb,
               fill=(77, 50, 20), anchor='mm',
               stroke_width=2 * SS, stroke_fill=(252, 246, 225))

    out = compose(bg, lay)
    Image.fromarray(out).save(os.path.join(OUT, out_png_base + '_pro.png'))
    Image.fromarray(out[VIS[1]:VIS[3], VIS[0]:VIS[2]]).save(
        os.path.join(OUT, out_png_base + '_pro_view.png'))
    if apply:
        save_tex(tex_out, header, out, alpha)
    print('costume done')


if __name__ == '__main__':
    apply = 'apply' in sys.argv
    scenario('sc00', 'The Empire of Japan',
             'Ryunosuke Naruhodo and his best friend Kazuma Asogi are busy '
             'preparing to set sail to study in the British Empire. '
             'Prosecutor Taketsuchi Auchi, meanwhile, stakes his prestige '
             'on one last, careful gambit...',
             246,
             os.path.join(OUT, 'sc00_pro.png'),
             os.path.join(HERE, 'idx2_v6_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex'),
             os.path.join(HERE, 'idx2_v7_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex'),
             apply)
    scenario('sc01', 'The British Empire',
             "As Ryunosuke Naruhodo serves out his suspension in Britain, "
             "the Reaper's shadow falls on a poor young genius. To protect "
             "his little partner, the greatest 'lawyer' in the world and "
             "his assistant head to court...",
             206,
             os.path.join(OUT, 'sc01_pro.png'),
             os.path.join(HERE, 'idx2_v6_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex'),
             os.path.join(HERE, 'idx2_v7_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex'),
             apply)
    costume('cost',
            os.path.join(HERE, 'idx1_dir/dlc_costumepack_BM_NOMIP_HQ.tex'),
            os.path.join(HERE, 'idx1_v7_dir/dlc_costumepack_BM_NOMIP_HQ.tex'),
            apply)

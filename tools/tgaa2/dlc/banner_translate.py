# -*- coding: utf-8 -*-
"""Translate the three TGAA2 DLC banner textures (512x256 RGBA8 ABGR, Morton).

Same recipe as TGAA1's issue 9-13 placeholder covers: mask the Japanese glyph
strokes by colour inside each text zone, cv2 inpaint the background, and
redraw the English with PIL. Character art is never touched (per-row
parchment-gap detection keeps the mask out of the art).

    python banner_translate.py preview   -> writes *_en.png for review
    python banner_translate.py apply     -> also re-encodes the .tex files
"""
import os, struct, sys

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('BANNER_OUT', HERE)
FDIRS = [os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts') + os.sep,
         os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts') + os.sep]

def font(name, size):
    for d in FDIRS:
        if os.path.exists(d + name):
            return ImageFont.truetype(d + name, size)
    raise IOError(name)

def detile(payload, w=512, h=256):
    raw = np.frombuffer(payload, np.uint8).reshape(-1, 4)
    out = np.zeros((h, w, 4), np.uint8)
    idx = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = ((i & 1)) | ((i & 4) >> 1) | ((i & 16) >> 2)
                y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                out[ty + y, tx + x] = raw[idx]; idx += 1
    return out

def retile(img):
    h, w, _ = img.shape
    raw = np.zeros((h * w, 4), np.uint8)
    idx = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = ((i & 1)) | ((i & 4) >> 1) | ((i & 16) >> 2)
                y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                raw[idx] = img[ty + y, tx + x]; idx += 1
    return raw.tobytes()

def load(path):
    d = open(path, 'rb').read()
    img = detile(d[20:])
    rgb = img[:, :, [3, 2, 1]].copy()      # ABGR -> RGB
    return d[:20], rgb, img[:, :, 0].copy()  # header, rgb, alpha

def save_tex(path, header, rgb, alpha):
    img = np.zeros((256, 512, 4), np.uint8)
    img[:, :, 0] = alpha
    img[:, :, 1] = rgb[:, :, 2]
    img[:, :, 2] = rgb[:, :, 1]
    img[:, :, 3] = rgb[:, :, 0]
    open(path, 'wb').write(header + retile(img))

def text(draw, xy, s, fnt, fill, outline=None, ow=0, anchor=None):
    if outline and ow:
        draw.text(xy, s, font=fnt, fill=fill, anchor=anchor,
                  stroke_width=ow, stroke_fill=outline)
    else:
        draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)

# per-row art boundary: walk from x_probe toward the text until a run of
# background pixels appears; never let the inpaint mask cross into the art.
def art_left(rgb, y0, y1, x_probe, bg=160, run=4):
    lum = rgb.astype(int).mean(axis=2)
    lims = np.full(rgb.shape[0], x_probe, int)
    for y in range(y0, y1):
        cnt = 0
        hit = False
        for x in range(x_probe, 36, -1):
            cnt = cnt + 1 if lum[y, x] > bg else 0
            if cnt >= run:
                lims[y] = x + run
                hit = True
                break
        if not hit:
            lims[y] = 36
    return lims

# ------------------------------------------------------------- scenario pair
def scenario(name, title_lines, body_lines, title_x1, out_png, tex_in, tex_out,
             apply, body_x1=232, body_size=14):
    header, rgb, alpha = load(tex_in)
    # low-saturation dark strokes only: never eats the saturated character art
    def ink_mask(box, thresh):
        x0, y0, x1, y1 = box
        z = rgb[y0:y1, x0:x1].astype(int)
        lum = z.mean(axis=2)
        sat = z.max(axis=2) - z.min(axis=2)
        m = np.zeros(rgb.shape[:2], np.uint8)
        m[y0:y1, x0:x1] = ((lum < thresh) & (sat < 45)).astype(np.uint8) * 255
        return m
    mask = ink_mask((40, 44, title_x1 + 14, 92), 150)   # title glyphs
    mask |= ink_mask((36, 96, 246, 232), 150)           # body glyphs
    # never cross into the character art (parchment-gap detection per row)
    lims = art_left(rgb, 40, 236, 270)
    xs = np.arange(rgb.shape[1])[None, :]
    mask[(xs >= lims[:, None] - 2)] = 0
    mask = cv2.dilate(mask, np.ones((2, 2), np.uint8))
    rgb = cv2.inpaint(rgb, mask, 3, cv2.INPAINT_TELEA)

    im = Image.fromarray(rgb)
    d = ImageDraw.Draw(im)
    # title: Blackford, two lines, centred in the plate, auto-shrunk
    cx = (40 + title_x1) // 2 + 10
    maxw = title_x1 - 58
    for size in range(40, 18, -1):
        ft = font('Blackford.ttf', size)
        wmax = max(d.textlength(t, font=ft) for t in title_lines)
        if wmax <= maxw:
            break
    cx = min(cx, int(title_x1 - 2 - wmax / 2))   # keep clear of the art
    ys = [57, 82] if len(title_lines) == 2 else [68]
    for t, y in zip(title_lines, ys):
        text(d, (cx + 1, y + 1), t, ft, (210, 195, 160), anchor='mm')
        text(d, (cx, y), t, ft, (48, 38, 32), anchor='mm')
    # body (assert every line clears the art)
    fb = font('georgia.ttf', body_size)
    for i, line in enumerate(body_lines):
        w = d.textlength(line, font=fb)
        assert 40 + w <= body_x1, (name, i, line, w)
        text(d, (40, 97 + i * 18), line, fb, (52, 44, 38))
    # ribbon stays Japanese (untouched) by request
    im.save(out_png)
    if apply:
        save_tex(tex_out, header, np.array(im), alpha)
    print('scenario %s -> %s' % (name, out_png))

# ---------------------------------------------------------------- costume
def costume(out_png, tex_in, tex_out, apply):
    """Keep the original banner; only the scroll text becomes English."""
    header, rgb, alpha = load(tex_in)
    sx0, sy0, sx1, sy1 = 137, 63, 310, 95
    z = rgb[sy0:sy1, sx0:sx1].astype(int)
    lz = z.mean(axis=2)
    rz, gz, bz = z[:, :, 0], z[:, :, 1], z[:, :, 2]
    gold = (rz > 150) & (gz > 110) & (bz < 120) & (rz - bz > 60)
    mask = np.zeros(rgb.shape[:2], np.uint8)
    mask[sy0:sy1, sx0:sx1] = ((lz < 110) | gold).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((2, 2), np.uint8))
    rgb = cv2.inpaint(rgb, mask, 3, cv2.INPAINT_NS)

    im = Image.fromarray(rgb)
    d = ImageDraw.Draw(im)
    fr = font('Candarab.ttf', 18)
    text(d, (224, 78), '3-Costume Pack', fr, (207, 184, 43),
         outline=(63, 39, 34), ow=2, anchor='mm')
    im.save(out_png)
    if apply:
        save_tex(tex_out, header, np.array(im), alpha)
    print('costume -> %s' % out_png)


if __name__ == '__main__':
    apply = 'apply' in sys.argv
    scenario('sc00', ['The Empire', 'of Japan'],
             ['Ryunosuke Naruhodo and his',
              'best friend Kazuma Asogi are',
              'busy preparing to set sail to',
              'study in the British Empire.',
              'Prosecutor Taketsuchi Auchi,',
              'meanwhile, stakes his prestige',
              'on one last, careful gambit...'],
             246,
             os.path.join(OUT, 'sc00_en.png'),
             os.path.join(HERE, 'idx2_v6_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex'),
             os.path.join(HERE, 'idx2_v7_dir/UI/tex/dlc_scenario00_BM_NOMIP_HQ.tex'), apply)
    scenario('sc01', ['The British', 'Empire'],
             ['As Ryunosuke Naruhodo serves',
              'out his suspension in Britain,',
              "the Reaper's shadow falls on a",
              'poor young genius. To protect',
              'his little partner, the greatest',
              "'lawyer' in the world and his",
              'assistant head to court...'],
             206,
             os.path.join(OUT, 'sc01_en.png'),
             os.path.join(HERE, 'idx2_v6_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex'),
             os.path.join(HERE, 'idx2_v7_dir/UI/tex/dlc_scenario01_BM_NOMIP_HQ.tex'), apply, body_x1=238, body_size=14)
    costume(os.path.join(OUT, 'cost_en.png'),
            os.path.join(HERE, 'idx1_dir/dlc_costumepack_BM_NOMIP_HQ.tex'),
            os.path.join(HERE, 'idx1_v7_dir/dlc_costumepack_BM_NOMIP_HQ.tex'), apply)

# -*- coding: utf-8 -*-
"""Paint the project version onto TGAA2's title screen.

WHY THIS EXISTS
The second game displays no version of its own. Its executable contains no
version-like string at all (searched: Capcom's code.bin and Scarlet Study's
v2.1.0 -- zero hits), so unlike the first game there is nothing to patch.
The first game's "ENG x.y.z" lives in code.bin, injected years ago by Scarlet
Study; adding the same to the second would mean writing new ARM code into the
title-screen flow.

Instead the version is PAINTED INTO THE TITLE-LOGO TEXTURE. That texture is
RGBA8 and this project already overrides it, so the edit is lossless and needs
no encoder for a compressed format.

    UI/4_menu/40_title/tex/title_jpn_01_BM_NOMIP_HQ.tex   512x512, TEX format 3

The version sprite is drawn by the game in the screen's TOP-RIGHT corner, and
is a SEPARATE sprite from the logo -- which is why text placed here appears in
the corner rather than beside the logo.

MEASURED CONSTANTS (do not guess these again)
    anchor          (318, 175)      PIL text() origin
    font            Segoe UI 18 px  regular
    fill            (214, 212, 206, 233)   warm off-white, matches the plate
    outline         (73, 73, 71, 233)      1 px, all eight directions
    resulting ink   x 319..393, y 182..194 for a 9-character string

    SPRITE BOUNDARY: the sprite's top edge is ~y=174. Drawing at y=170 CLIPS
    the text; y=176 and below renders whole. Do not move it higher.

ALWAYS DRAW FROM THE CLEAN UPSTREAM TEXTURE, never from a build that already
carries a stamp -- otherwise the old digits show through underneath the new
ones. The clean plate is senyarom's, with nothing in the version area.

The backgrounds (title_scenario_00..05) are ETC1/ETC1A4, lossy, and would need
an encoder this project does not have. Do not use them as the canvas.

Usage:
    python stamp_version.py <clean.tex> "ENG 1.0.3" <out.tex>
"""
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HDR = 20
ANCHOR = (318, 175)
FONT = 'C:/Windows/Fonts/segoeui.ttf'
SIZE = 18
FILL = (214, 212, 206, 233)
OUTLINE = (73, 73, 71, 233)
SAFE_TOP = 176          # anything above this is clipped by the sprite edge


def morton(x, y):
    return (((x & 1) << 0) | ((y & 1) << 1) | ((x & 2) << 1) |
            ((y & 2) << 2) | ((x & 4) << 2) | ((y & 4) << 3))


def dims(blob):
    v = struct.unpack('<I', blob[8:12])[0]
    bits = [i for i in range(32) if v >> i & 1]
    wb = [i for i in bits if 6 <= i <= 16]
    hb = [i for i in bits if 19 <= i <= 29]
    return (1 << (wb[0] - 6), 1 << (hb[0] - 19))


def decode(blob, w, h):
    """TEX format 3: 8x8 Morton tiles, bytes stored A,B,G,R."""
    pay = np.frombuffer(blob[HDR:HDR + w * h * 4], np.uint8).reshape(-1, 4)
    ys, xs = np.mgrid[0:h, 0:w]
    idx = ((ys // 8) * (w // 8) + (xs // 8)) * 64 + morton(xs & 7, ys & 7)
    px = pay[idx]
    return Image.fromarray(np.stack([px[..., 3], px[..., 2],
                                     px[..., 1], px[..., 0]], -1), 'RGBA')


def encode(im, header):
    """Inverse of decode(). Null-tested: decode->encode is byte-identical."""
    w, h = im.size
    a = np.array(im.convert('RGBA'), np.uint8)
    ys, xs = np.mgrid[0:h, 0:w]
    idx = ((ys // 8) * (w // 8) + (xs // 8)) * 64 + morton(xs & 7, ys & 7)
    pay = np.zeros((w * h, 4), np.uint8)
    px = a[ys, xs]
    pay[idx] = np.stack([px[..., 3], px[..., 2], px[..., 1], px[..., 0]], -1)
    return header + pay.tobytes()


def stamp(clean_tex, text, out_tex):
    blob = open(clean_tex, 'rb').read()
    w, h = dims(blob)
    if blob[13] != 3:
        raise SystemExit('not TEX format 3 (RGBA8): got %d' % blob[13])

    im = decode(blob, w, h)
    before = np.array(im)

    # Refuse to stamp a plate that already carries one: the old digits would
    # remain underneath and the result reads as a smear.
    box = before[176:200, 300:400]
    if int((box[..., 3] > 0).sum()) > 0:
        raise SystemExit('version area is not empty -- pass the CLEAN upstream '
                         'texture, not a build that is already stamped')

    if ANCHOR[1] < SAFE_TOP - 6:
        raise SystemExit('anchor above the sprite edge; text would be clipped')

    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, SIZE)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                d.text((ANCHOR[0] + dx, ANCHOR[1] + dy), text, font=f, fill=OUTLINE)
    d.text(ANCHOR, text, font=f, fill=FILL)

    after = np.array(im)
    vis = (after[..., 3] > 0) & np.any(after != before, axis=-1)
    ys, xs = np.nonzero(vis)
    if not len(ys):
        raise SystemExit('nothing was drawn')
    if ys.min() < SAFE_TOP - 1:
        raise SystemExit('ink at y=%d is above the sprite edge and will clip' % ys.min())
    print('  ink: x %d..%d  y %d..%d  (%d px)'
          % (xs.min(), xs.max(), ys.min(), ys.max(), len(ys)))

    out = encode(im, blob[:HDR])
    if len(out) != len(blob):
        raise SystemExit('size changed: %d -> %d' % (len(blob), len(out)))
    open(out_tex, 'wb').write(out)
    print('  wrote %s (%d bytes, unchanged size)' % (out_tex, len(out)))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    stamp(sys.argv[1], sys.argv[2], sys.argv[3])

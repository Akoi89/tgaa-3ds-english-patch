# -*- coding: utf-8 -*-
"""Best-effort RGBA preview of any 3DS or Chronicles .tex (for LOOKING, not re-encoding).

3DS: fmt 3 RGBA8 / 0x11 RGB8 via tex_rgba8, fmt 12 LA44 (8x8 Morton tiles, high
nibble L, low nibble A), everything else via texture_sweep.decode_any.
PC ('TEX\0' with BC payload): pctex_rgba.
"""
import os
import struct, sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import tex_rgba8, pctex_rgba


def dims3ds(b):
    v = struct.unpack_from('<I', b, 8)[0]
    bits = [i for i in range(32) if v >> i & 1]
    return 1 << ([i for i in bits if 6 <= i <= 18][0] - 6), 1 << ([i for i in bits if 19 <= i <= 31][0] - 19)


def _morton_grey(px, w, h):
    img = np.zeros((h, w), px.dtype); idx = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            blk = px[idx:idx + 64]; idx += 64
            for i in range(len(blk)):
                x = (i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2); y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                img[ty + y, tx + x] = blk[i]
    return img


def preview(b, over=(40, 40, 40)):
    if b[:4] == b'TEX\0' and b[4] in (0xA3, 0x9D, 0x9E) and len(b) > 24 and struct.unpack_from('<I', b, 4)[0] >> 24 == 0x20 or (b[:4] == b'TEX\0' and b[13] in pctex_rgba.BC):
        return pctex_rgba.decode(b)
    fmt = b[13]
    if fmt == 3:
        rgb, a = tex_rgba8.decode_rgba8(b); return Image.fromarray(np.dstack([rgb, a]))
    if fmt == 0x11:
        return Image.fromarray(tex_rgba8.decode_rgb8(b)).convert('RGBA')
    if fmt == 12:
        w, h = dims3ds(b); px = np.frombuffer(b[20:20 + w * h], np.uint8); g = _morton_grey(px, w, h)
        L = (g >> 4) * 17; A = (g & 15) * 17
        return Image.fromarray(np.dstack([L, L, L, A]).astype(np.uint8))
    import texture_sweep as ts
    im, _ = ts.decode_any(b)
    return im.convert('RGBA') if im is not None else None


def flat(im, over=(40, 40, 40)):
    bg = Image.new('RGBA', im.size, over + (255,)); bg.alpha_composite(im); return bg

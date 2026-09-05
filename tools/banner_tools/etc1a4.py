# -*- coding: utf-8 -*-
"""3DS ETC1 / ETC1A4 (MT Framework .tex fmt 12 = ETC1A4, 1 byte/px; fmt 11? = ETC1, 0.5 byte/px).

Layout: 8x8 tiles in row-major tile order; inside a tile, four 4x4 blocks in
Z-order (TL, TR, BL, BR). ETC1A4 block = 8 bytes alpha (4 bpp, column-major: byte
x holds column x, low nibble = row 0..) + 8 bytes ETC1 (big-endian u64).
Decoder covers both modes; the encoder writes SOLID-COLOUR blocks (individual
mode, table 0, all pixels 'lowest' modifier) with an arbitrary 4-bit alpha mask -
exactly what a flat text label needs.
"""
import struct
import numpy as np

MOD = [[2, 8], [5, 17], [9, 29], [13, 42], [18, 60], [24, 80], [33, 106], [47, 183]]


def _decode_etc1_block(hi, lo):
    """hi = first 4 bytes (as u32 BE), lo = last 4 bytes. Returns 4x4x3 uint8 (rows, cols)."""
    diff = (hi >> 1) & 1; flip = hi & 1
    t0 = (hi >> 5) & 7; t1 = (hi >> 2) & 7
    if diff:
        r = (hi >> 27) & 31; g = (hi >> 19) & 31; b = (hi >> 11) & 31
        dr = (hi >> 24) & 7; dg = (hi >> 16) & 7; db = (hi >> 8) & 7
        dr = dr - 8 if dr > 3 else dr; dg = dg - 8 if dg > 3 else dg; db = db - 8 if db > 3 else db
        c0 = [(r << 3) | (r >> 2), (g << 3) | (g >> 2), (b << 3) | (b >> 2)]
        r2, g2, b2 = r + dr, g + dg, b + db
        c1 = [(r2 << 3) | (r2 >> 2), (g2 << 3) | (g2 >> 2), (b2 << 3) | (b2 >> 2)]
    else:
        c0 = [((hi >> 28) & 15) * 17, ((hi >> 20) & 15) * 17, ((hi >> 12) & 15) * 17]
        c1 = [((hi >> 24) & 15) * 17, ((hi >> 16) & 15) * 17, ((hi >> 8) & 15) * 17]
    out = np.zeros((4, 4, 3), np.int32)
    for i in range(16):                      # i = x*4 + y (column-major)
        x, y = i // 4, i % 4
        sub = (y >= 2) if flip else (x >= 2)   # flip=0: left/right halves; flip=1: top/bottom
        base = c1 if sub else c0; tbl = MOD[t1 if sub else t0]
        msb = (lo >> (i + 16)) & 1; lsb = (lo >> i) & 1
        m = (-tbl[1], -tbl[0], tbl[0], tbl[1])[(msb << 1) | lsb] if True else 0
        # index mapping: 0 -> +a, 1 -> +b, 2 -> -a, 3 -> -b
        idx = (msb << 1) | lsb; m = (tbl[0], tbl[1], -tbl[0], -tbl[1])[idx]
        out[y, x] = [min(255, max(0, c + m)) for c in base]
    return out


def decode(data, w, h, alpha=True):
    bs = 16 if alpha else 8
    rgb = np.zeros((h, w, 3), np.uint8); a = np.full((h, w), 255, np.uint8); p = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                blk = data[p:p + bs]; p += bs
                if alpha:
                    av = struct.unpack('<Q', blk[:8])[0]; q = struct.unpack('<Q', blk[8:16])[0]
                    for x in range(4):
                        for y in range(4):
                            a[ty + by + y, tx + bx + x] = ((av >> (4 * (x * 4 + y))) & 15) * 17
                else:
                    q = struct.unpack('<Q', blk[:8])[0]
                hi, lo = q >> 32, q & 0xFFFFFFFF          # 3DS stores the ETC1 block as a little-endian u64
                rgb[ty + by:ty + by + 4, tx + bx:tx + bx + 4] = _decode_etc1_block(hi, lo)
    return rgb, a


def encode_solid(colour, alpha_mask, base_data, w, h):
    """Re-encode: every block gets solid `colour` (individual mode, table 0, index 0 => +2) and the
    4-bit alpha from alpha_mask (h x w uint8). Blocks whose mask is all-zero are copied from base_data
    untouched so the rest of the atlas is byte-identical."""
    r, g, b = colour
    def q(c): return max(0, min(15, round((c - 2) / 17)))   # index 0 adds +2 (table 0 low)
    hi = (q(r) << 28) | (q(r) << 24) | (q(g) << 20) | (q(g) << 16) | (q(b) << 12) | (q(b) << 8)  # tables 0, diff 0, flip 0
    lo = 0
    out = bytearray(base_data); p = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                m = alpha_mask[ty + by:ty + by + 4, tx + bx:tx + bx + 4]
                if m.any():
                    av = 0
                    for x in range(4):
                        for y in range(4):
                            av |= (int(m[y, x]) >> 4) << (4 * (x * 4 + y))
                    out[p:p + 16] = struct.pack('<Q', av) + struct.pack('<Q', (hi << 32) | lo)
                p += 16
    return bytes(out)

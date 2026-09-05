# -*- coding: utf-8 -*-
"""Small general ETC1 / ETC1A4 encoder (individual mode, per-subblock base colour,
brute-force table and modifier index, both flip orientations). Meant for a few
blocks of two-tone UI text, not for whole textures. Layout as in etc1a4.py."""
import struct
import numpy as np
from etc1a4 import MOD


def _enc_block(rgb):
    best = None
    for flip in (0, 1):
        if flip == 0:
            subs = (rgb[:, :2], rgb[:, 2:])
        else:
            subs = (rgb[:2, :], rgb[2:, :])
        bases, tables, idxs, err_total = [], [], [], 0
        for sub in subs:
            px = sub.reshape(-1, 3)
            base = np.clip(np.round(px.mean(axis=0) / 17), 0, 15).astype(int)
            b255 = base * 17
            bt, be, bi = None, None, None
            for t in range(8):
                a_, b_ = MOD[t]
                mods = (a_, b_, -a_, -b_)
                cand = np.stack([np.clip(b255 + m, 0, 255) for m in mods])        # 4 x 3
                errs = ((cand[None, :, :] - px[:, None, :]) ** 2).sum(axis=2)       # n x 4
                ids = errs.argmin(axis=1); e = errs[np.arange(len(px)), ids].sum()
                if be is None or e < be:
                    bt, be, bi = t, e, ids
            bases.append(base); tables.append(bt); idxs.append(bi); err_total += be
        if best is None or err_total < best[0]:
            best = (err_total, flip, bases, tables, idxs)
    _, flip, bases, tables, idxs = best
    bases = [[int(v) for v in b] for b in bases]; tables = [int(t) for t in tables]   # numpy ints overflow on << 32
    hi = ((bases[0][0] << 28) | (bases[1][0] << 24) | (bases[0][1] << 20) | (bases[1][1] << 16)
          | (bases[0][2] << 12) | (bases[1][2] << 8) | (tables[0] << 5) | (tables[1] << 2) | flip)
    lo = 0
    for i in range(16):                      # i = x*4 + y (column-major pixel index)
        x, y = i // 4, i % 4
        if flip == 0:
            si = 0 if x < 2 else 1; j = y * 2 + (x % 2)          # row-major within the 4x2 slice
        else:
            si = 0 if y < 2 else 1; j = (y % 2) * 4 + x          # row-major within the 2x4 slice
        k = int(idxs[si][j])
        lo |= ((k >> 1) & 1) << (i + 16)
        lo |= (k & 1) << i
    return hi, lo


def encode_rgba(rgba, base_data, w, h, touch_mask=None):
    """Encode h x w x 4 into ETC1A4, replacing only blocks where touch_mask is set
    (default: any alpha > 0); other blocks are copied from base_data unchanged."""
    out = bytearray(base_data); p = 0
    if touch_mask is None:
        touch_mask = rgba[..., 3] > 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                m = touch_mask[ty + by:ty + by + 4, tx + bx:tx + bx + 4]
                if m.any():
                    blk = rgba[ty + by:ty + by + 4, tx + bx:tx + bx + 4].astype(np.float32)
                    hi, lo = _enc_block(blk[..., :3])
                    av = 0
                    for x in range(4):
                        for y in range(4):
                            av |= (int(blk[y, x, 3]) >> 4) << (4 * (x * 4 + y))
                    out[p:p + 16] = struct.pack('<Q', av) + struct.pack('<Q', (hi << 32) | lo)
                p += 16
    return bytes(out)


if __name__ == '__main__':
    import etc1a4
    img = np.zeros((8, 8, 4), np.uint8); img[..., :3] = (15, 10, 8); img[2:6, 1:7, :3] = (239, 235, 229); img[..., 3] = 255
    data = encode_rgba(img, bytes(16 * 4), 8, 8); rgb, a = etc1a4.decode(data, 8, 8)
    d = np.abs(rgb.astype(int) - img[..., :3].astype(int))
    print('two-tone round trip: mean abs err %.1f, max %d' % (d.mean(), d.max()))

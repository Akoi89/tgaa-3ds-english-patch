"""Decode MT Framework TEX format 3 = RGBA8, 8x8 Morton tiles (bytes stored ABGR)."""
import struct
import numpy as np
from PIL import Image


def morton(x, y):
    return (((x & 1) << 0) | ((y & 1) << 1) | ((x & 2) << 1) |
            ((y & 2) << 2) | ((x & 4) << 2) | ((y & 4) << 3))


def dims(blob):
    v = struct.unpack('<I', blob[8:12])[0]
    bits = [i for i in range(32) if v >> i & 1]
    wb = [i for i in bits if 6 <= i <= 16]
    hb = [i for i in bits if 19 <= i <= 29]
    return (1 << (wb[0] - 6), 1 << (hb[0] - 19))


def decode_rgba8(blob, w, h, hdr=20):
    pay = np.frombuffer(blob[hdr:hdr + w * h * 4], np.uint8).reshape(-1, 4)
    ys, xs = np.mgrid[0:h, 0:w]
    tile = (ys // 8) * (w // 8) + (xs // 8)
    idx = tile * 64 + morton(xs & 7, ys & 7)
    px = pay[idx]                       # stored A,B,G,R
    out = np.stack([px[..., 3], px[..., 2], px[..., 1], px[..., 0]], -1)
    return Image.fromarray(out, 'RGBA')


if __name__ == '__main__':
    import sys
    d = open(sys.argv[1], 'rb').read()
    w, h = dims(d)
    print('%dx%d format=%d' % (w, h, d[13]))
    decode_rgba8(d, w, h).save(sys.argv[2])

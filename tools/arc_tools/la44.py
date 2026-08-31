"""Decode MT Framework TEX format 12 = LA44 (4-bit luma + 4-bit alpha), 8x8 Morton."""
import numpy as np
from PIL import Image
from rgba8 import morton, dims


def decode_la44(blob, w, h, hdr=20, lum_high=True):
    pay = np.frombuffer(blob[hdr:hdr + w * h], np.uint8)
    ys, xs = np.mgrid[0:h, 0:w]
    tile = (ys // 8) * (w // 8) + (xs // 8)
    idx = tile * 64 + morton(xs & 7, ys & 7)
    b = pay[idx]
    hi, lo = (b >> 4) * 17, (b & 15) * 17
    l, a = (hi, lo) if lum_high else (lo, hi)
    return Image.fromarray(np.stack([l, l, l, a], -1).astype(np.uint8), 'RGBA')


if __name__ == '__main__':
    import sys
    d = open(sys.argv[1], 'rb').read()
    w, h = dims(d)
    print('%dx%d format=%d' % (w, h, d[13]))
    decode_la44(d, w, h, lum_high=True).save(sys.argv[2])
    decode_la44(d, w, h, lum_high=False).save(sys.argv[2].replace('.png', '_alt.png'))

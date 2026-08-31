"""Decode MT Framework TEX format 14 = A4 (4-bit alpha), 8x8 Morton tiles."""
import numpy as np
from PIL import Image

def morton(x, y):
    return (((x & 1) << 0) | ((y & 1) << 1) | ((x & 2) << 1) |
            ((y & 2) << 2) | ((x & 4) << 2) | ((y & 4) << 3))

def decode_a4(blob, w, h, hdr=20):
    pay = np.frombuffer(blob[hdr:], np.uint8)
    assert w * h // 2 == len(pay), (w, h, len(pay))
    ys, xs = np.mgrid[0:h, 0:w]
    tile = (ys // 8) * (w // 8) + (xs // 8)
    idx = tile * 64 + morton(xs & 7, ys & 7)
    byte = pay[idx // 2]
    nib = np.where(idx % 2 == 0, byte & 0x0F, byte >> 4)
    return Image.fromarray((nib * 17).astype(np.uint8), 'L')

def dims(blob):
    import struct
    v = struct.unpack('<I', blob[8:12])[0]
    bits = [i for i in range(32) if v >> i & 1]
    wb = [i for i in bits if 6 <= i <= 16]; hb = [i for i in bits if 19 <= i <= 29]
    return (1 << (wb[0] - 6), 1 << (hb[0] - 19))

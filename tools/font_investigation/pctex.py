# -*- coding: utf-8 -*-
"""Decode Chronicles (PC) .tex font atlases.

They are **BC7** (format byte 42) with a 24-byte header, and the glyph coverage
lives in the **GREEN** channel -- red and blue are a flat 122-124 and alpha is a
flat 254-255, so decoding "the alpha channel" like a normal font atlas gives
nothing. Dimensions are log2-packed in the u32 at byte 8, same convention as the
3DS files: width bit = log2(w)+6, height bit = log2(h)+19.

Pillow >= 11 decodes BC7 through a DDS wrapper with a DX10 header
(DXGI_FORMAT_BC7_UNORM = 98).
"""
import io
import struct

import numpy as np
from PIL import Image


def dims(blob):
    v = struct.unpack_from('<I', blob, 8)[0]
    bits = [i for i in range(32) if v >> i & 1]
    wb = [i for i in bits if 6 <= i <= 16]
    hb = [i for i in bits if 19 <= i <= 29]
    return 1 << (wb[0] - 6), 1 << (hb[0] - 19)


def _dds(pay, w, h, dxgi=98):
    d = b'DDS ' + struct.pack('<I', 124)
    d += struct.pack('<I', 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000)
    d += struct.pack('<II', h, w) + struct.pack('<I', len(pay)) + struct.pack('<I', 0)
    d += struct.pack('<I', 1) + b'\x00' * 44
    d += struct.pack('<I', 32) + struct.pack('<I', 0x4) + b'DX10'
    d += struct.pack('<IIIII', 0, 0, 0, 0, 0)
    d += struct.pack('<I', 0x1000) + b'\x00' * 16
    d += struct.pack('<IIIII', dxgi, 3, 0, 1, 0)
    return d + pay


def decode(blob, hdr=24):
    """PC font .tex -> single-channel coverage image (L)."""
    w, h = dims(blob)
    im = Image.open(io.BytesIO(_dds(blob[hdr:], w, h))).convert('RGBA')
    return Image.fromarray(np.array(im)[..., 1], 'L')


if __name__ == '__main__':
    import sys
    d = open(sys.argv[1], 'rb').read()
    print('%dx%d format=%d' % (*dims(d), d[13]))
    decode(d).save(sys.argv[2])

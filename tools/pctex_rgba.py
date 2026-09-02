# -*- coding: utf-8 -*-
"""Decode a Chronicles (PC, MT Framework DX11) .tex to RGBA.

Header: 'TEX\0', then bitfields; the u32 at +8 packs width/height the same
way the 3DS header does (width = 1 << (bit-6) for a bit in 6..18, height =
1 << (bit-19) for a bit in 19..31), the byte at +13 is the DXGI-ish format
(0x2A = BC7 for every UI texture checked), payload from +24. Wrapped in a DDS
DX10 header so Pillow's DDS reader does the block decoding.
"""
import io, struct
import numpy as np
from PIL import Image

BC = {0x2A: 98, 0x13: 71, 0x17: 77}      # BC7, BC1, BC3 -> DXGI ids


def dims(blob):
    v = struct.unpack_from('<I', blob, 8)[0]
    bits = [i for i in range(32) if v >> i & 1]
    w = [i for i in bits if 6 <= i <= 18]; h = [i for i in bits if 19 <= i <= 31]
    return (1 << (w[0] - 6)) if w else 0, (1 << (h[0] - 19)) if h else 0


def decode(blob, hdr=24):
    w, h = dims(blob)
    fmt = blob[13]
    dxgi = BC.get(fmt, 98)
    pay = blob[hdr:]
    d = b'DDS ' + struct.pack('<I', 124) + struct.pack('<I', 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000)
    d += struct.pack('<II', h, w) + struct.pack('<I', len(pay)) + struct.pack('<I', 0)
    d += struct.pack('<I', 1) + b'\x00' * 44 + struct.pack('<I', 32) + struct.pack('<I', 0x4) + b'DX10'
    d += struct.pack('<IIIII', 0, 0, 0, 0, 0) + struct.pack('<I', 0x1000) + b'\x00' * 16
    d += struct.pack('<IIIII', dxgi, 3, 0, 1, 0)
    return Image.open(io.BytesIO(d + pay)).convert('RGBA')

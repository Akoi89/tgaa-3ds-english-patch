"""3DS texture codec for this game's two containers.

CTPK entries (fmt as in the CTPK table) and Sega's COMP members (LZ11 stream
whose payload is a 16-byte header + raw texture; header u16[2] low byte is the
same format code, u16[3] = width, u16[4] = height).

    decode(data, w, h, fmt) -> PIL RGBA image
    encode(img, fmt, base=None) -> bytes      (base = original data, needed for ETC1A4)
    comp_decode(blob) -> (img, fmt, header16)
    comp_encode(img, fmt, header16, base_blob) -> COMP blob

Pixel order is the 8x8 Morton tile order with no flips (proven byte-exact on
CTPK RGBA4/RGBA8/RGB565 round trips in this project).
"""
import os
import struct, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.environ.get('TGAA_ROOT', os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2')), r'testimony_pipeline'))
import etc1a4, etc1_enc
import comp

RGBA8, RGB8, RGBA5551, RGB565, RGBA4, LA8, HILO8, L8, A8, LA4, L4, A4, ETC1, ETC1A4 = range(14)
BPP = {RGBA8: 4, RGB8: 3, RGBA5551: 2, RGB565: 2, RGBA4: 2, LA8: 2, HILO8: 2, L8: 1, A8: 1, LA4: 1, ETC1A4: None, ETC1: None}
NAMES = {0: 'RGBA8', 1: 'RGB8', 2: 'RGBA5551', 3: 'RGB565', 4: 'RGBA4', 5: 'LA8', 6: 'HILO8', 7: 'L8', 8: 'A8', 9: 'LA4', 10: 'L4', 11: 'A4', 12: 'ETC1', 13: 'ETC1A4'}


def _morton():
    out = []
    for i in range(64):
        x = ((i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2))
        y = (((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3))
        out.append((x, y))
    return out


MORTON = _morton()


def _order(w, h):
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for mx, my in MORTON:
                yield tx + mx, ty + my


def decode(data, w, h, fmt):
    if fmt in (ETC1, ETC1A4):
        rgb, a = etc1a4.decode(data, w, h, alpha=(fmt == ETC1A4))
        return Image.fromarray(np.dstack([rgb, a]), 'RGBA')
    img = Image.new('RGBA', (w, h)); px = img.load()
    bpp = BPP.get(fmt)
    if fmt in (L4, A4):
        for k, (x, y) in enumerate(_order(w, h)):
            v = (data[k >> 1] >> (4 * (k & 1))) & 0xF
            px[x, y] = (v * 17, v * 17, v * 17, 255) if fmt == L4 else (255, 255, 255, v * 17)
        return img
    for k, (x, y) in enumerate(_order(w, h)):
        o = k * bpp
        if fmt == RGBA8:
            a, b, g, r = data[o:o + 4]; px[x, y] = (r, g, b, a)
        elif fmt == RGB8:
            b, g, r = data[o:o + 3]; px[x, y] = (r, g, b, 255)
        elif fmt == RGBA5551:
            v = struct.unpack_from('<H', data, o)[0]
            px[x, y] = (((v >> 11) & 31) * 255 // 31, ((v >> 6) & 31) * 255 // 31, ((v >> 1) & 31) * 255 // 31, (v & 1) * 255)
        elif fmt == RGB565:
            v = struct.unpack_from('<H', data, o)[0]
            px[x, y] = (((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31, 255)
        elif fmt == RGBA4:
            v = struct.unpack_from('<H', data, o)[0]
            px[x, y] = ((v >> 12) * 17, ((v >> 8) & 0xF) * 17, ((v >> 4) & 0xF) * 17, (v & 0xF) * 17)
        elif fmt == LA8:
            a, l = data[o], data[o + 1]; px[x, y] = (l, l, l, a)
        elif fmt == HILO8:
            g, r = data[o], data[o + 1]; px[x, y] = (r, g, 0, 255)
        elif fmt == L8:
            l = data[o]; px[x, y] = (l, l, l, 255)
        elif fmt == A8:
            px[x, y] = (255, 255, 255, data[o])
        elif fmt == LA4:
            v = data[o]; px[x, y] = ((v >> 4) * 17, (v >> 4) * 17, (v >> 4) * 17, (v & 0xF) * 17)
    return img


def encode(img, fmt, base=None):
    w, h = img.size
    if fmt in (ETC1, ETC1A4):
        if fmt == ETC1:
            raise NotImplementedError('ETC1 without alpha')
        rgba = np.array(img.convert('RGBA'))
        return etc1_enc.encode_rgba(rgba, base, w, h, touch_mask=np.ones((h, w), bool))
    px = img.load(); out = bytearray()
    for x, y in _order(w, h):
        r, g, b, a = px[x, y]
        if fmt == RGBA8:
            out += bytes((a, b, g, r))
        elif fmt == RGB8:
            out += bytes((b, g, r))
        elif fmt == RGBA5551:
            out += struct.pack('<H', ((r >> 3) << 11) | ((g >> 3) << 6) | ((b >> 3) << 1) | (1 if a >= 128 else 0))
        elif fmt == RGB565:
            out += struct.pack('<H', ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3))
        elif fmt == RGBA4:
            out += struct.pack('<H', ((r >> 4) << 12) | ((g >> 4) << 8) | ((b >> 4) << 4) | (a >> 4))
        elif fmt == LA8:
            out += bytes((a, r))
        elif fmt == L8:
            out.append(r)
        elif fmt == A8:
            out.append(a)
        elif fmt == LA4:
            out.append(((r >> 4) << 4) | (a >> 4))
        else:
            raise NotImplementedError(NAMES.get(fmt, fmt))
    return bytes(out)


def comp_decode(blob):
    d = comp.decode(blob)
    hdr = d[:16]
    h16 = struct.unpack('<8H', hdr)
    fmt, w, h = h16[2] & 0xFF, h16[3], h16[4]
    return decode(d[16:], w, h, fmt), fmt, hdr


def comp_encode(img, fmt, hdr, base_blob=None):
    base = comp.decode(base_blob)[16:] if base_blob is not None else None
    return comp.encode(hdr + encode(img, fmt, base))

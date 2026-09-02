# -*- coding: utf-8 -*-
"""Encode an RGBA8 (format 3) 3DS .tex, the inverse of texture_sweep's decoder.

The project has only ever DECODED these. To restamp a DLC magazine cover we have
to write one back, so this is the missing half.

Layout, as read off the real files:
    +0x00  8 bytes   header preamble, copied verbatim from the donor
    +0x08  u32       dimension bits: width  = 1 << (bit_index - 6)  for bits 6..18
                                     height = 1 << (bit_index - 19) for bits 19..31
    +0x0D  u8        format (3 = RGBA8)
    +0x14  payload   8x8 Morton-tiled, 4 bytes per pixel, stored ABGR

Pixel order inside a tile is the standard 3DS swizzle:
    x = (i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2)
    y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)

Everything before the payload is taken from the donor texture unchanged, so the
dimension bits and every unknown field stay exactly as Capcom wrote them. Only
the pixels change.
"""
import numpy as np

HDR = 20


def tile_bytes(img):
    """(h, w, n) uint8 -> Morton-tiled payload bytes."""
    h, w, n = img.shape
    out = np.zeros((h * w, n), np.uint8)
    idx = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = (i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2)
                y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                out[idx] = img[ty + y, tx + x]
                idx += 1
    return out.tobytes()


def encode_rgba8(donor_blob, rgb, alpha=None):
    """A new .tex carrying `rgb`, keeping every donor header byte.

    texture_sweep decodes format 3 as img[:, :, [3,2,1]] from an ABGR buffer,
    so channel 0 is alpha and 1..3 are B, G, R. We invert exactly that.
    """
    if donor_blob[13] != 3:
        raise ValueError('donor is format %d, not RGBA8' % donor_blob[13])
    rgb = np.asarray(rgb, np.uint8)
    h, w = rgb.shape[:2]
    if alpha is None:
        alpha = np.full((h, w), 255, np.uint8)
    abgr = np.dstack([alpha, rgb[:, :, 2], rgb[:, :, 1], rgb[:, :, 0]])
    return donor_blob[:HDR] + tile_bytes(abgr)


def detile(payload, w, h, n=4):
    raw = np.frombuffer(payload[:w * h * n], np.uint8).reshape(-1, n)
    out = np.zeros((h, w, n), np.uint8)
    idx = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = (i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2)
                y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                out[ty + y, tx + x] = raw[idx]
                idx += 1
    return out


def decode_rgba8(blob):
    """-> (rgb, alpha). texture_sweep drops alpha; a restamp must keep it,
    otherwise every transparent pixel becomes opaque and the plate turns into a
    solid rectangle over the art."""
    import struct
    v = struct.unpack_from('<I', blob, 8)[0]
    bits = [i for i in range(32) if v >> i & 1]
    w = 1 << ([i for i in bits if 6 <= i <= 18][0] - 6)
    h = 1 << ([i for i in bits if 19 <= i <= 31][0] - 19)
    abgr = detile(blob[HDR:], w, h)
    return abgr[:, :, [3, 2, 1]].copy(), abgr[:, :, 0].copy()

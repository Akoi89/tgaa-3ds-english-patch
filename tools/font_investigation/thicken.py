# -*- coding: utf-8 -*-
"""Repair font03's Latin glyphs so they survive the engine's downscale.

The patch rasterised font03's Latin set into 15-pixel cells but declares
the font size as 12.0, so the 3DS point-samples it down by 0.8 -- and a
point-sampled shrink can drop a source row outright. Every one-pixel
horizontal feature is therefore at risk, which is exactly what shows in
game: H loses its crossbar and reads "II", m loses an arch join and
reads "rn", 2's thin diagonal breaks up.

Fix: find horizontal strokes that are only one pixel tall and thicken
them to two, so no single dropped row can erase them. Only runs of >=3
columns are touched, so this hits crossbars and arch joins and leaves
serifs, dots and diagonals alone. Every glyph is verified by simulating
the 0.8 point-sample before and after.
"""
import struct
import numpy as np
from PIL import Image

BASE, NGLYPH = 0x53, 219
SCALE = 0.8


def records(gfd):
    out = {}
    for i in range(NGLYPH):
        o = BASE + i * 16
        cp = struct.unpack_from('<I', gfd, o)[0]
        v1 = struct.unpack_from('<I', gfd, o + 4)[0]
        v2 = struct.unpack_from('<I', gfd, o + 8)[0]
        out[cp] = ((v1 >> 8) & 0xFFF, (v1 >> 20) & 0xFFF,
                   (v2 >> 8) & 0xFFF, (v2 >> 20) & 0xFFF)
    return out


def shrink(g):
    h, w = g.shape
    return np.array(Image.fromarray(g).resize(
        (max(1, int(round(w * SCALE))), max(1, int(round(h * SCALE)))),
        Image.NEAREST))


def components(g, thr=40):
    """Count 8-connected ink blobs -- a stroke vanishing usually splits one."""
    import cv2
    n, _ = cv2.connectedComponents((g > thr).astype(np.uint8), connectivity=8)
    return n - 1


def thicken(g, thr=40, minrun=3):
    out = g.copy()
    h, w = g.shape
    ink = g > thr
    for r in range(h):
        cols = [c for c in range(w) if ink[r, c]
                and (r == 0 or not ink[r - 1, c])
                and (r == h - 1 or not ink[r + 1, c])]
        # keep only stretches of >= minrun adjacent columns
        run = []
        for c in cols + [None]:
            if run and c is not None and c == run[-1] + 1:
                run.append(c); continue
            if len(run) >= minrun:
                tgt = r + 1 if r + 1 < h else r - 1
                for cc in run:
                    if out[tgt, cc] < g[r, cc]:
                        out[tgt, cc] = g[r, cc]
            run = [c] if c is not None else []
    return out

# -*- coding: utf-8 -*-
"""Fix font03's Latin glyphs WITHOUT touching a single metric.

The bug: the atlas holds Latin in 15 px cells while the GFD declares 12.00, so
the console point-samples every glyph by 12/15 and drops whole pixel rows --
`H` loses its crossbar, `e` and `D` lose strokes.

The naive fix (redraw into 12 px cells, declare 12) breaks the spacing: the
console scales advances by declared/cell too, so shrinking the cell loosens
every word. Probe 1 proved that -- scaling advances AND the declared size
together mashed words into each other.

So instead: **pre-compensate**. Nearest-neighbour downsampling is exactly
invertible. The console keeps source row `floor(j*15/12)` for destination row
j, which uses rows 0,1,2,3,5,6,7,8,10,11,12,13 and never reads 4, 9 or 14. So
render the glyph cleanly at 12 px from Capcom's own high-resolution serif, then
scatter those pixels into exactly the rows and columns the console samples.
What lands on screen is the clean 12 px glyph, and the GFD is not modified at
all -- same cell sizes, same advances, same declared size, so the v14 caption
wrapping stays valid to the pixel.

The never-sampled rows are filled with their neighbour so the glyph still reads
correctly if the sampling rule turns out to differ slightly.

    python rebuild_font03.py <romfs_dir> [--apply]
"""
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from a4 import decode_a4, dims, morton
from pctex import decode as pc_decode
from dgs2tool.arc import parse_arc, build_arc_bytes

FONT_ARC = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'archive', 'font_eng.arc')
PC_GFD = 'UI/0_system/00_font/font00_eng.gfd'
PC_TEX = 'UI/0_system/00_font/font00_eng_00_ID_HQ.tex'
DS_GFD = 'UI/0_system/00_font/font03_jpn.gfd'
DS_TEX = 'UI/0_system/00_font/font03_jpn_00_AM_NOMIP.tex'
PC_LINE = 57.75
GAMMA = 0.50


def pc_glyphs(gfd):
    n = struct.unpack_from('<I', gfd, 0x1C)[0]
    plen = struct.unpack_from('<I', gfd, 0x44)[0]
    base = 0x48 + plen + 1
    out = {}
    for i in range(n):
        o = base + i * 36
        if o + 36 > len(gfd):
            break
        cp = struct.unpack_from('<I', gfd, o)[0]
        w, h, bx, by, adv = struct.unpack_from('<5f', gfd, o + 4)
        v = struct.unpack_from('<I', gfd, o + 28)[0]
        out[cp] = dict(x=(v >> 8) & 0xFFF, y=(v >> 20) & 0xFFF,
                       w=w, h=h, bx=bx, by=by, adv=adv)
    return out


def ds_glyphs(gfd):
    n = struct.unpack_from('<I', gfd, 28)[0]
    out = {}
    for i in range(n):
        o = 0x53 + i * 16
        if o + 16 > len(gfd):
            break
        cp = struct.unpack_from('<I', gfd, o)[0]
        v1 = struct.unpack_from('<I', gfd, o + 4)[0]
        v2 = struct.unpack_from('<I', gfd, o + 8)[0]
        out[cp] = dict(off=o, x=(v1 >> 8) & 0xFFF, y=(v1 >> 20) & 0xFFF,
                       w=(v2 >> 8) & 0xFFF, h=(v2 >> 20) & 0xFFF, adv=gfd[o + 12])
    return out


def encode_a4(img, w, h, hdr):
    """L image -> A4 4bpp 8x8 Morton payload (exact inverse of a4.decode_a4)."""
    a = np.asarray(img, np.uint8)
    ys, xs = np.mgrid[0:h, 0:w]
    idx = ((ys // 8) * (w // 8) + (xs // 8)) * 64 + morton(xs & 7, ys & 7)
    nib = np.zeros(w * h, np.uint8)
    # int32, not uint8: 255 + 8 wraps to 7 and every bright pixel encodes as 0
    nib[idx.ravel()] = np.minimum((a.ravel().astype(np.int32) + 8) // 17, 15)
    return hdr + (nib[0::2] | (nib[1::2] << 4)).astype(np.uint8).tobytes()


def precompensate(clean, cell_w, cell_h, dst_w, dst_h):
    """Scatter a clean dst-sized glyph into the source pixels the console reads."""
    out = np.zeros((cell_h, cell_w), np.uint8)
    c = np.asarray(clean, np.uint8)
    rows = [min(cell_h - 1, int(j * cell_h / dst_h)) for j in range(dst_h)]
    cols = [min(cell_w - 1, int(i * cell_w / dst_w)) for i in range(dst_w)]
    for j, sy in enumerate(rows):
        for i, sx in enumerate(cols):
            out[sy, sx] = c[j, i]
    # rows/cols the sampler never reads: copy the nearest one it does, so the
    # glyph still reads correctly if the rule is not exactly floor()
    used_r, used_c = set(rows), set(cols)
    for y in range(cell_h):
        if y not in used_r:
            src = min(used_r, key=lambda r: abs(r - y))
            out[y] = out[src]
    for x in range(cell_w):
        if x not in used_c:
            src = min(used_c, key=lambda c2: abs(c2 - x))
            out[:, x] = out[:, src]
    return Image.fromarray(out, 'L')


def main(romfs, apply=False):
    pc = parse_arc(open(FONT_ARC, 'rb').read())
    pe = {e.name: e.data for e in pc['entries']}
    src = pc_decode(pe[PC_TEX])
    pg = pc_glyphs(pe[PC_GFD])

    ui_path = os.path.join(romfs, 'archive', 'UI_cmn_jpn.arc')
    ui = parse_arc(open(ui_path, 'rb').read())
    ue = {e.name: e.data for e in ui['entries']}
    gfd = ue[DS_GFD]
    declared = struct.unpack_from('<f', gfd, 36)[0]
    tex = ue[DS_TEX]
    tw, th = dims(tex)
    atlas = decode_a4(tex, tw, th).copy()
    dg = ds_glyphs(gfd)

    cell_h = max(d['h'] for c, d in dg.items() if 0x20 <= c < 0x7F)
    ratio = declared / cell_h
    print('cells are %d px, GFD declares %.2f -> console samples at %.3f'
          % (cell_h, declared, ratio))

    done = 0
    for cp in sorted(dg):
        if not (0x20 <= cp < 0x7F) or cp not in pg:
            continue
        d, p = dg[cp], pg[cp]
        if d['w'] == 0 or d['h'] == 0 or p['w'] < 1 or p['h'] < 1:
            continue
        dst_w = max(1, int(round(d['w'] * ratio)))
        dst_h = max(1, int(round(d['h'] * ratio)))
        s = dst_h / PC_LINE

        iw, ih = max(1, int(round(p['w']))), max(1, int(round(p['h'])))
        ink = src.crop((p['x'], p['y'], p['x'] + iw, p['y'] + ih))
        nw, nh = max(1, int(round(p['w'] * s))), max(1, int(round(p['h'] * s)))
        ink = ink.resize((nw, nh), Image.LANCZOS)
        # a clean downsample lands far lighter than the atlas it replaces;
        # renormalise per glyph and lift midtones to keep the original weight
        a = np.asarray(ink, np.float64)
        if a.max() > 0:
            a *= 255.0 / a.max()
        a = 255.0 * np.clip(a / 255.0, 0.0, 1.0) ** GAMMA
        ink = Image.fromarray(np.minimum(a, 255).astype(np.uint8), 'L')

        clean = Image.new('L', (dst_w, dst_h), 0)
        ox = max(0, min(int(round(p['bx'] * s)), dst_w - nw))
        oy = max(0, min(int(round(p['by'] * s)), dst_h - nh))
        clean.paste(ink.crop((0, 0, min(nw, dst_w), min(nh, dst_h))), (ox, oy))

        atlas.paste(precompensate(clean, d['w'], d['h'], dst_w, dst_h),
                    (d['x'], d['y']))
        done += 1

    print('%d Latin glyphs pre-compensated; GFD untouched' % done)
    if not apply:
        atlas.save(os.path.join(HERE, 'font03_rebuilt_preview.png'))
        print('preview -> font_investigation/font03_rebuilt_preview.png  (dry run)')
        return 0

    new_tex = encode_a4(atlas, tw, th, tex[:20])
    assert len(new_tex) == len(tex)
    open(ui_path, 'wb').write(build_arc_bytes(ui, {DS_TEX: new_tex}))
    back = {e.name: e.data for e in parse_arc(open(ui_path, 'rb').read())['entries']}
    chk = decode_a4(back[DS_TEX], tw, th)
    err = np.abs(np.asarray(chk, np.int16) - np.asarray(atlas, np.int16)).max()
    print('atlas round-trip max error: %d (16-level quantisation floor is 8)' % err)
    print('GFD byte-identical:', back[DS_GFD] == gfd)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--apply' in sys.argv))

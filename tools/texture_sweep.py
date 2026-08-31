# -*- coding: utf-8 -*-
"""Decode every non-overridden text-suspect texture in both games and build
contact sheets for eyeballing. Formats: 3=RGBA8, 11=ETC1, 12=LA44, 17=ETC1A4;
14/16/1 are attempted as 16bpp guesses and labelled.
"""
import json, struct, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.arc import parse_arc
import os

MOD = [[2,8,-2,-8],[5,17,-5,-17],[9,29,-9,-29],[13,42,-13,-42],
       [18,60,-18,-60],[24,80,-24,-80],[33,106,-33,-106],[47,183,-47,-183]]

def dims_of(blob):
    v = struct.unpack_from('<I', blob, 8)[0]
    bits = [i for i in range(32) if v >> i & 1]
    wb = [i for i in bits if 6 <= i <= 18]
    hb = [i for i in bits if 19 <= i <= 31]
    if wb and hb:
        return 1 << (wb[0]-6), 1 << (hb[0]-19)
    return None, None

def etc1_block(data, out, ox, oy):
    v = int.from_bytes(data, 'little')
    pix = v & 0xFFFFFFFF
    b4 = (v >> 32) & 0xFF; b5 = (v >> 40) & 0xFF
    b6 = (v >> 48) & 0xFF; b7 = (v >> 56) & 0xFF
    diff = (b4 >> 1) & 1; flip = b4 & 1
    t1 = (b4 >> 5) & 7; t2 = (b4 >> 2) & 7
    if diff:
        def x5(x): return (x << 3) | (x >> 2)
        r5 = b7 >> 3; g5 = b6 >> 3; bl5 = b5 >> 3
        def sd(x):
            x &= 7
            return x - 8 if x & 4 else x
        c1 = (x5(r5), x5(g5), x5(bl5))
        c2 = (x5((r5+sd(b7)) & 31), x5((g5+sd(b6)) & 31), x5((bl5+sd(b5)) & 31))
    else:
        def x4(x): return x * 17
        c1 = (x4(b7 >> 4), x4(b6 >> 4), x4(b5 >> 4))
        c2 = (x4(b7 & 15), x4(b6 & 15), x4(b5 & 15))
    for x in range(4):
        for y in range(4):
            bit = x * 4 + y
            lsb = (pix >> bit) & 1
            msb = (pix >> (bit + 16)) & 1
            idx = msb * 2 + lsb
            sb2 = (x >= 2) if not flip else (y >= 2)
            base = c2 if sb2 else c1
            t = t2 if sb2 else t1
            m = MOD[t][idx]
            out[oy+y, ox+x] = [max(0, min(255, c + m)) for c in base]

def decode_etc1(payload, w, h, alpha4=False):
    out = np.zeros((h, w, 3), np.uint8)
    step = 16 if alpha4 else 8
    pos = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0,0),(0,4),(4,0),(4,4)):
                blk = payload[pos:pos+step]; pos += step
                col = blk[8:] if alpha4 else blk
                if len(col) < 8: return out
                etc1_block(col, out, tx+bx, ty+by)
    return out

def detile_bytes(payload, w, h, bpp):
    n = bpp
    raw = np.frombuffer(payload[:w*h*n], np.uint8).reshape(-1, n)
    out = np.zeros((h, w, n), np.uint8)
    idx = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for i in range(64):
                x = ((i & 1)) | ((i & 4) >> 1) | ((i & 16) >> 2)
                y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                if idx < len(raw):
                    out[ty+y, tx+x] = raw[idx]
                idx += 1
    return out

def decode_any(blob):
    fmt = blob[13]
    w, h = dims_of(blob)
    pay = blob[20:]
    if not w:
        return None, 'nodims f%d' % fmt
    try:
        if fmt == 3:
            img = detile_bytes(pay, w, h, 4)          # ABGR
            return Image.fromarray(img[:, :, [3,2,1]]), 'RGBA8'
        if fmt == 0x11:
            img = detile_bytes(pay, w, h, 3)          # BGR
            return Image.fromarray(img[:, :, ::-1]), 'RGB8'
        if fmt == 12:
            img = detile_bytes(pay, w, h, 1)[:, :, 0]
            lum = ((img >> 4) * 17).astype(np.uint8)
            return Image.fromarray(lum).convert('RGB'), 'LA44'
        if fmt == 11:
            return Image.fromarray(decode_etc1(pay, w, h, False)), 'ETC1'
        if fmt == 17:
            return Image.fromarray(decode_etc1(pay, w, h, True)), 'ETC1A4'
        if fmt in (14, 16, 1):
            a = np.frombuffer(pay[:w*h*2], '<u2')
            if len(a) < w*h: return None, 'short f%d' % fmt
            img2 = np.zeros((h, w), '<u2')
            idx = 0
            flat = a
            for ty in range(0, h, 8):
                for tx in range(0, w, 8):
                    for i in range(64):
                        x = ((i & 1)) | ((i & 4) >> 1) | ((i & 16) >> 2)
                        y = ((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3)
                        img2[ty+y, tx+x] = flat[idx]; idx += 1
            v = img2.astype(np.uint32)
            r = ((v >> 11) & 31) * 255 // 31
            g = ((v >> 5) & 63) * 255 // 63
            b = (v & 31) * 255 // 31
            return Image.fromarray(np.dstack([r, g, b]).astype(np.uint8)), 'f%d as 565' % fmt
    except Exception as ex:
        return None, 'err f%d %s' % (fmt, ex)
    return None, 'unk f%d' % fmt

def main():
    plan = json.load(open('texture_sweep_effective.json'))
    jobs = []
    roots = {'t1': Path('basegame/rom'), 't2': Path('dgs2_base_romfs')}
    for game in ('t1', 't2'):
        for rel, fmt, size in plan[game+'_loose']:
            jobs.append((game, rel, roots[game] / rel, None))
        for rel, fmt, size in plan[game+'_arc']:
            arcrel, member = rel.split(' :: ')
            jobs.append((game, rel, roots[game] / arcrel, member))
    thumbs = []
    arc_cache = {}
    for game, rel, path, member in jobs:
        if member is None:
            blob = path.read_bytes()
        else:
            if path not in arc_cache:
                arc_cache[path] = {e.name: e.data for e in parse_arc(path.read_bytes())['entries']}
            blob = arc_cache[path][member]
        im, how = decode_any(blob)
        label = '%s %s [%s]' % (game.upper(), rel.split('/')[-1][:38], how)
        if im is None:
            im = Image.new('RGB', (128, 96), (120, 0, 0))
        im.thumbnail((176, 132))
        thumbs.append((label, im))
    cols, cell_w, cell_h = 6, 180, 152
    per = 30
    import tempfile
    out = Path(os.environ.get('SWEEP_OUT', tempfile.gettempdir()))
    for s in range(0, len(thumbs), per):
        batch = thumbs[s:s+per]
        rows = (len(batch)+cols-1)//cols
        sheet = Image.new('RGB', (cols*cell_w, rows*cell_h), (24, 24, 28))
        d = ImageDraw.Draw(sheet)
        for i, (label, im) in enumerate(batch):
            x = (i % cols) * cell_w; y = (i // cols) * cell_h
            sheet.paste(im, (x + (cell_w-im.width)//2, y + (cell_h-16-im.height)//2))
            d.text((x+2, y+cell_h-14), label[:34], fill=(200, 200, 100))
        sheet.save(out / ('texsweep_%02d.png' % (s//per)))
    print('%d textures -> %d sheets' % (len(thumbs), (len(thumbs)+per-1)//per))

if __name__ == '__main__':
    main()

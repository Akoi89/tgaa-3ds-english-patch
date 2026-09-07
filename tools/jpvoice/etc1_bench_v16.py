# -*- coding: utf-8 -*-
"""Bench: for each ETC1 texture ported in v1.6, encode the SAME touched blocks with plain etcpak (what v1.6
shipped) and with etc1_enc.encode_rgba_search (peer session's searched encoder), and report PSNR against the
PC source pixels over the touched blocks only. Read-only: nothing in the trees or releases changes."""
import os, sys, io, struct, time, json
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
import numpy as np
from PIL import Image
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch')); sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline')); sys.path.insert(0, os.path.join(ROOT, 'jpvoice'))
from dgs2tool.arc import parse_arc
import tex_view, pctex_rgba, etc1a4, etc1_enc, etcpak
PC = os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64', 'archive'); TREES = os.path.join(ROOT, 'jpvoice', '_trees')
# import the target table without running the port script body
src = open(os.path.join(ROOT, 'jpvoice', 'port_eng_textures.py'), encoding='utf-8').read()
T = eval(src[src.index('T = [') + 4: src.index(']\n', src.index('T = [')) + 1])

def pc_tex(arc, member):
    a = parse_arc(open(os.path.join(PC, arc.replace('/', os.sep)), 'rb').read()); return [bytes(e.data) for e in a['entries'] if e.name == member][0]

def psnr(a, b, m):
    d = (a.astype(float) - b.astype(float))[m]; mse = (d ** 2).mean(); return 10 * np.log10(255 ** 2 / mse) if mse else 99.0

rows = []
for game, loc, parc, pmem, method in T:
    if method != 'etc1': continue
    rel, member = loc.split('::')
    a_jp = parse_arc(open(os.path.join(TREES, game + '_jp_cart', 'c0', rel.replace('/', os.sep)), 'rb').read())
    jp = [bytes(e.data) for e in a_jp['entries'] if e.name == member][0]
    w, h = tex_view.dims3ds(jp); rgb_jp, _ = etc1a4.decode(jp[20:], w, h, alpha=False)
    rgba = np.asarray(pctex_rgba.decode(pc_tex(parc, pmem)).resize((w, h), Image.LANCZOS)).astype(np.float32); rgb_pc = rgba[..., :3]
    diff = np.abs(rgb_pc - rgb_jp.astype(np.float32)).mean(axis=2); bdiff = diff.reshape(h // 4, 4, w // 4, 4).mean(axis=(1, 3)); mask = bdiff > 20
    m2 = mask.copy(); m2[1:] |= mask[:-1]; m2[:-1] |= mask[1:]; m2[:, 1:] |= mask[:, :-1]; m2[:, :-1] |= mask[:, 1:]
    pix = np.kron(m2, np.ones((4, 4), bool))
    src_rgba = np.dstack([np.clip(rgb_pc, 0, 255).astype(np.uint8), np.full((h, w), 255, np.uint8)])
    # both encoders write ETC1A4 (16-byte blocks); take the colour u64 of each block for the ETC1 texture
    def colour_only(a4):
        out = bytearray()
        for i in range(0, len(a4), 16): out += a4[i + 8:i + 16]
        return bytes(out)
    t = time.time(); e1 = colour_only(etc1_enc.encode_rgba_etcpak(src_rgba, bytes(w * h), w, h, touch_mask=pix)); t1 = time.time() - t
    t = time.time(); e2 = colour_only(etc1_enc.encode_rgba_search(src_rgba, bytes(w * h), w, h, touch_mask=pix)); t2 = time.time() - t
    d1, _ = etc1a4.decode(e1, w, h, alpha=False); d2, _ = etc1a4.decode(e2, w, h, alpha=False)
    p1, p2 = psnr(d1, rgb_pc, pix), psnr(d2, rgb_pc, pix)
    rows.append((game, member.split('/')[-1], int(m2.sum()), p1, p2, t1, t2))
    print('%s %-34s blocks %5d  etcpak %.2f dB (%.0fs)  search %.2f dB (%.0fs)  gain %+.2f' % (game, member.split('/')[-1][:34], m2.sum(), p1, t1, p2, t2, p2 - p1), flush=True)
json.dump(rows, open(os.path.join(ROOT, 'jpvoice', 'etc1_bench_v16.json'), 'w'), indent=1)

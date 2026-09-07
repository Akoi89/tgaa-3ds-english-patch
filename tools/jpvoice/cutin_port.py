# -*- coding: utf-8 -*-
"""Port Capcom's Chronicles English cut-in (shout) atlases to the 3DS.

3DS: UI/1_ig/12_cutin/tex/bigfont_*_GSM_NOMIP.tex, 512x512, fmt 0x10 = 8bpp grey, 8x8 Morton tiles,
20-byte header (Capcom's Japanese files). The shipped translated set is fmt 0x0c (LA44) with two of
the UK atlases' second variant still Japanese. Chronicles: UI_cmn_eng.arc members
bigfont_*_BM_NOMIP_eng.tex, 1024x1024, BC-compressed mask; same layout, 2:1.

Calibration: bigfont_shutup and bigfont_hukidasi have the SAME content in JP 3DS and PC eng, so the
PC channel and the downscale filter are chosen by best match against Capcom's own 3DS pixels.
Null test: re-encoding the decoded JP texture reproduces the JP file byte for byte.

Output: jpvoice/_cutin/new/bigfont_*_GSM_NOMIP.tex (8 files) + previews + jpvoice/_cutin/compare_ours_vs_capcom.png
"""
import os, sys, io, struct
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
import numpy as np
from PIL import Image
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch')); sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline')); sys.path.insert(0, os.path.join(ROOT, 'dlc_story_audit'))
from dgs2tool.arc import parse_arc
import tex_view, pctex_rgba
C = os.path.join(ROOT, 'jpvoice', '_cutin'); NEW = os.path.join(C, 'new'); os.makedirs(NEW, exist_ok=True)
JP = os.path.join(ROOT, 'jpvoice', '_trees', 'TGAA1_jp_cart', 'c0', 'UI', '1_ig', '12_cutin', 'tex')
OURS = os.path.join(ROOT, 'jpvoice', '_trees', 'TGAA1_ours_upd', 'c0', 'UI', '1_ig', '12_cutin', 'tex')
NAMES = ['default', 'gift', 'hay', 'here', 'say', 'uk_default', 'uk_wait', 'wait']


def dec_grey(b):
    assert b[13] == 0x10, 'not fmt16: %02x' % b[13]
    w, h = tex_view.dims3ds(b)
    return tex_view._morton_grey(np.frombuffer(b[20:20 + w * h], np.uint8), w, h)


def enc_grey(img, header):
    h, w = img.shape; out = bytearray(w * h); idx = 0
    xs = np.array([(i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2) for i in range(64)])
    ys = np.array([((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3) for i in range(64)])
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            out[idx:idx + 64] = bytes(img[ty + ys, tx + xs].astype(np.uint8)); idx += 64
    return bytes(header) + bytes(out)


pc = {}
a = parse_arc(open(os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64', 'archive', 'UI_cmn_eng.arc'), 'rb').read())
for e in a['entries']:
    if 'bigfont_' in e.name and e.name.endswith('.tex'):
        pc[e.name.split('/')[-1].replace('bigfont_', '').replace('_BM_NOMIP_eng.tex', '')] = np.asarray(pctex_rgba.decode(e.data)).astype(np.float32)

# null test on a JP file
jp0 = open(os.path.join(JP, 'bigfont_default_GSM_NOMIP.tex'), 'rb').read()
assert enc_grey(dec_grey(jp0), jp0[:20]) == jp0, 'encoder null test failed'
print('encoder null test: re-encoded JP default == original')

# 3DS byte = L4A4: high nibble luminance, low nibble alpha (0xF0 = white transparent, 0xFF = white
# opaque, 0x60 / 0x90 = the grey tint of a quadrant's background). PC: grey in RGB, coverage in A.
# The tint greys drifted between platforms (PC 110/122/155 where the 3DS has 96/96/144), so per
# quadrant the PC tint level is snapped to the 3DS quadrant's tint level, with antialiased pixels
# between tint and white interpolated.
Q = {'TL': (slice(0, 256), slice(0, 256)), 'TR': (slice(0, 256), slice(256, 512)), 'BL': (slice(256, 512), slice(0, 256)), 'BR': (slice(256, 512), slice(256, 512))}


def tint_level(vals, lo, hi):
    v = vals[(vals >= lo) & (vals <= hi)]
    if v.size < 500:
        return None
    u, c = np.unique(v, return_counts=True); return int(u[np.argmax(c)])


def to3ds(im, jp_grey):
    """im: PC RGBA 1024x1024 float; jp_grey: the JP 3DS 512x512 bytes (for the per-quadrant tint)."""
    g = im[..., 1]; a = im[..., 3]
    g = np.asarray(Image.fromarray(g.clip(0, 255).astype(np.uint8)).resize((512, 512), Image.BOX)).astype(np.float32)
    a = np.asarray(Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((512, 512), Image.BOX)).astype(np.float32)
    out = np.zeros((512, 512), np.float32)
    for q, (ys, xs) in Q.items():
        gq = g[ys, xs]; aq = a[ys, xs]; jq = jp_grey[ys, xs]
        pc_t = tint_level(gq[aq < 8], 60, 200)
        jp_t = tint_level((jq[(jq & 15) == 0] >> 4), 3, 12)      # 3DS tint L (A == 0 pixels)
        L = gq / 17.0
        if pc_t is not None and jp_t is not None:
            lo = np.minimum(gq, pc_t) / pc_t * jp_t                     # 0..pc_t -> 0..jp_t
            hi = jp_t + (np.maximum(gq, pc_t) - pc_t) / (255 - pc_t) * (15 - jp_t)  # pc_t..255 -> jp_t..15
            Lt = np.where(gq <= pc_t, lo, hi)
            L = np.where(aq < 8, Lt, L)                                # only transparent pixels carry tint
        A = aq / 17.0
        out[ys, xs] = np.clip(np.rint(L), 0, 15) * 16 + np.clip(np.rint(A), 0, 15)
    return out.astype(np.uint8)


# validation on the balloon atlas, whose content is the same on both platforms
jp_h = dec_grey(open(os.path.join(JP, 'bigfont_hukidasi_GSM_NOMIP.tex'), 'rb').read())
got = to3ds(pc['hukidasi'], jp_h)
d = np.abs(got.astype(int) - jp_h.astype(int))
print('hukidasi: mean abs err %.2f, exact %.1f%%, within 17 (one nibble step) %.1f%%' % (d.mean(), (d == 0).mean() * 100, (d <= 17).mean() * 100))


tiles = []
for n in NAMES:
    jpb = open(os.path.join(JP, 'bigfont_%s_GSM_NOMIP.tex' % n), 'rb').read()
    new = to3ds(pc[n], dec_grey(jpb)); blob = enc_grey(new, jpb[:20])
    assert len(blob) == len(jpb) and dec_grey(blob).tobytes() == new.astype(np.uint8).tobytes()
    open(os.path.join(NEW, 'bigfont_%s_GSM_NOMIP.tex' % n), 'wb').write(blob)
    la = lambda arr: tex_view.flat(Image.fromarray(np.dstack([(arr >> 4) * 17] * 3 + [(arr & 15) * 17]).astype(np.uint8))).convert('L')
    Image.fromarray(new).save(os.path.join(NEW, '%s_raw.png' % n)); la(new).save(os.path.join(NEW, '%s.png' % n))
    ours = tex_view.flat(tex_view.preview(open(os.path.join(OURS, 'bigfont_%s_GSM_NOMIP.tex' % n), 'rb').read())).convert('L')
    tiles.append((n, ours, la(new)))
    print('wrote', n, len(blob), 'bytes')
W = 256; sheet = Image.new('L', (W * 8, W * 2), 0)
for i, (n, o, nw) in enumerate(tiles):
    sheet.paste(o.resize((W, W)), (i * W, 0)); sheet.paste(nw.resize((W, W)), (i * W, W))
sheet.save(os.path.join(C, 'compare_ours_vs_capcom.png')); print('sheet: top = shipped (senyarom set), bottom = Capcom Chronicles ported')

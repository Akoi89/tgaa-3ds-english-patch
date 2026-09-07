# -*- coding: utf-8 -*-
"""v1.6: port the remaining Capcom-English textures from Chronicles into the v1.6 romfs trees.

Targets (from jpvoice/eng_texture_crossref.txt, minus the credits, the 40 handwriting textures whose
alpha nibble carries stroke timing, and names that only matched by stem):
  opTitle4                the second game's last chapter card, 3DS RGBA8: keep the 3DS plate colours,
                          alpha = Capcom's English mask (G*A), exactly how the other cards were ported
  ETC1 model/place tex    re-encode ONLY the 4x4 blocks where Capcom's English art differs from the
                          3DS Japanese art (text regions), with etcpak (pip package; differential mode
                          and full search, unlike the small in-house etc1_enc); other blocks stay Capcom's bytes
  LA44 item textures      L = luminance/17, A = alpha/17 of the PC art, Morton 8x8
Each 3DS texture keeps its 20-byte header. Archive members are replaced with build_arc_bytes and the
archive is read back to prove only that member changed. Writes into jpvoice/_v16/<game>/c0.
Output: jpvoice/_v16/port_report.json and jpvoice/_notported/port_preview_<game>.png (before/after).
"""
import os, sys, io, json, struct, hashlib
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
import numpy as np
from PIL import Image, ImageDraw
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch')); sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
from dgs2tool.arc import parse_arc, build_arc_bytes
import tex_view, pctex_rgba, tex_rgba8, etc1a4, etc1_enc
PC = os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64', 'archive')
TREES = os.path.join(ROOT, 'jpvoice', '_trees'); V16 = os.path.join(ROOT, 'jpvoice', '_v16')

# (game, 3DS relpath [::member], PC arc, PC member, method)
T = [
    ('TGAA2', 'archive/UI_opdemo04_jpn.arc::UI/2_doc/26_op/4/tex/opTitle4_BM_NOMIP_HQ.tex', 'BB/UI_opdemo04_eng.arc', 'UI/2_doc/26_op_BB/4/tex/opTitle4_BM_NOMIP_HQ_eng.tex', 'card'),
    ('TGAA2', 'archive/chr151_jpn.arc::obj/chr/chr151/model/chr151_hand_BM_NOMIP.tex', 'BB/chr151_eng.arc', 'BB/obj/chr/chr151/model/chr151_hand_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA2', 'archive/chr230_jpn.arc::obj/chr/chr230/model/chr230_body_BM_NOMIP.tex', 'BB/chr230_eng.arc', 'BB/obj/chr/chr230/model/chr230_body_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA2', 'archive/chr574_jpn.arc::obj/chr/chr574/model/p1101_09_BM_NOMIP.tex', 'BB/chr574_eng.arc', 'BB/obj/chr/chr574/model/p1101_09_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA2', 'archive/chr280_jpn.arc::obj/chr/chr280/model/chr230_body_BM_NOMIP.tex', 'BB/chr280_eng.arc', 'BB/obj/chr/chr280/model/chr230_body_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA2', 'archive/chr303_jpn.arc::obj/chr/chr303/model/chr303_rArm_BM_NOMIP.tex', 'BB/chr303_eng.arc', 'BB/obj/chr/chr303/model/chr303_rarm_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA2', 'archive/place1201_jpn.arc::place/p1201/p1201_11_BM_NOMIP.tex', 'BB/place1201_eng.arc', 'BB/place/p1201/p1201_11_BM_NOMIP_eng.tex', 'etc1'),
    ('TGAA2', 'archive/place1201_jpn.arc::place/p1201/p1201_60_BM_NOMIP.tex', 'BB/place1201_eng.arc', 'BB/place/p1201/p1201_60_BM_NOMIP_eng.tex', 'etc1'),
    ('TGAA2', 'archive/evi3d_1_02_01_jpn.arc::item/item1_02_01/model/item1_02_01_0_BM_NOMIP.tex', 'BB/evi3d_1_02_01_eng.arc', 'BB/item/item1_02_01/model/item1_02_01_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA1', 'archive/chr022_jpn.arc::obj/chr/chr022/model/chr022_body_BM_NOMIP.tex', 'GO/chr022_eng.arc', 'GO/obj/chr/chr022/model/chr022_body_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA1', 'archive/chr220_jpn.arc::obj/chr/chr220/model/chr220_body_BM_NOMIP.tex', 'GO/chr220_eng.arc', 'GO/obj/chr/chr220/model/chr220_body_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA1', 'archive/evi3d_3_17_00_jpn.arc::item/item3_17_00/model/item3_17_00_0_BM_NOMIP.tex', 'GO/evi3d_3_17_00_eng.arc', 'GO/item/item3_17_00/model/item3_17_00_0_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA1', 'archive/evi3d_5_16_00_jpn.arc::item/item5_16_00/model/item5_16_00_0_BM_NOMIP.tex', 'GO/evi3d_5_16_00_eng.arc', 'GO/item/item5_16_00/model/item5_16_00_0_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA1', 'archive/evi3d_5_34_00_jpn.arc::item/item5_34_00/model/item5_34_00B_BM_NOMIP.tex', 'GO/evi3d_5_34_00_eng.arc', 'GO/item/item5_34_00/model/item5_34_00B_eng_BM_NOMIP.tex', 'etc1'),
    ('TGAA1', 'archive/place0101_jpn.arc::place/p0101/p0101_10_BM_NOMIP.tex', 'GO/place0101_eng.arc', 'GO/place/p0101/p0101_10_BM_NOMIP_eng.tex', 'etc1'),
]


def pc_tex(arc, member):
    a = parse_arc(open(os.path.join(PC, arc.replace('/', os.sep)), 'rb').read())
    return [bytes(e.data) for e in a['entries'] if e.name == member][0]


def pc_rgba(blob, w, h):
    im = pctex_rgba.decode(blob)
    return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32)


def la44_pack(L, A, header):
    g = (np.clip(np.rint(L), 0, 15).astype(np.uint8) << 4) | np.clip(np.rint(A), 0, 15).astype(np.uint8)
    h, w = g.shape; out = bytearray(w * h); idx = 0
    xs = np.array([(i & 1) | ((i & 4) >> 1) | ((i & 16) >> 2) for i in range(64)]); ys = np.array([((i & 2) >> 1) | ((i & 8) >> 2) | ((i & 32) >> 3) for i in range(64)])
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            out[idx:idx + 64] = bytes(g[ty + ys, tx + xs]); idx += 64
    return bytes(header) + bytes(out)


def la44_unpack(blob):
    w, h = tex_view.dims3ds(blob); g = tex_view._morton_grey(np.frombuffer(blob[20:20 + w * h], np.uint8), w, h)
    return (g >> 4).astype(np.float32) * 17, (g & 15).astype(np.float32) * 17


def etc1_port(jp, pcb, thresh=20):
    """Re-encode only the 4x4 blocks where the English art differs from the Japanese art."""
    w, h = tex_view.dims3ds(jp); pay = jp[20:]
    rgb_jp, _ = etc1a4.decode(pay, w, h, alpha=False)
    rgba = pc_rgba(pcb, w, h); rgb_pc = rgba[..., :3]
    diff = np.abs(rgb_pc - rgb_jp.astype(np.float32)).mean(axis=2)
    bh, bw = h // 4, w // 4
    bdiff = diff.reshape(bh, 4, bw, 4).mean(axis=(1, 3))
    mask = bdiff > thresh
    # dilate one block so antialiased edges of the text are inside the re-encoded region
    m2 = mask.copy(); m2[1:] |= mask[:-1]; m2[:-1] |= mask[1:]; m2[:, 1:] |= mask[:, :-1]; m2[:, :-1] |= mask[:, 1:]
    # etcpak (differential mode, full search) encodes the whole PC image in linear 4x4 block order,
    # standard big-endian blocks; the 3DS wants 8x8 tiles of four blocks, each a little-endian u64
    import etcpak
    rgba = np.dstack([np.clip(rgb_pc, 0, 255).astype(np.uint8), np.full((h, w), 255, np.uint8)])
    lin = etcpak.compress_etc1_rgb(rgba.tobytes(), w, h); bw = w // 4
    out = bytearray(pay); p = 0; n = 0
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            for by, bx in ((0, 0), (0, 4), (4, 0), (4, 4)):
                if m2[(ty + by) // 4, (tx + bx) // 4]:
                    i = ((ty + by) // 4) * bw + (tx + bx) // 4
                    out[p:p + 8] = lin[i * 8:i * 8 + 8][::-1]; n += 1
                p += 8
    new = jp[:20] + bytes(out)
    rgb_new, _ = etc1a4.decode(bytes(out), w, h, alpha=False)
    return new, rgb_jp, rgb_new, n, int(m2.sum())


def card_port(jp, pcb):
    rgb, al = tex_rgba8.decode_rgba8(jp); h, w = rgb.shape[:2]
    a = np.asarray(pctex_rgba.decode(pcb)).astype(np.float32)
    L = a[..., 1] * a[..., 3] / 255.0
    lo, hi = np.percentile(L[a[..., 3] > 4], [0.5, 99.5]); Ln = np.clip((L - lo) / max(1, hi - lo), 0, 1)
    al_new = np.asarray(Image.fromarray((Ln * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS))
    return tex_rgba8.encode_rgba8(jp, rgb, al_new), (rgb, al), (rgb, al_new)


def la44_port(jp, pcb):
    w, h = tex_view.dims3ds(jp); rgba = pc_rgba(pcb, w, h)
    lum = rgba[..., :3].mean(axis=2); A = rgba[..., 3]
    Lj, Aj = la44_unpack(jp)
    new = la44_pack(lum / 17.0, A / 17.0, jp[:20])
    Ln, An = la44_unpack(new)
    return new, (Lj, Aj), (Ln, An)


def flat_rgba(rgb, al):
    im = Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), 'RGBA'); return tex_view.flat(im).convert('RGB')


report = []; previews = {'TGAA1': [], 'TGAA2': []}
for game, loc, parc, pmem, method in T:
    rel, member = (loc.split('::') + [None])[:2]
    src_tree = os.path.join(TREES, game + '_jp_cart', 'c0'); dst_tree = os.path.join(V16, game, 'c0')
    if member:
        a_jp = parse_arc(open(os.path.join(src_tree, rel.replace('/', os.sep)), 'rb').read())
        jp = [bytes(e.data) for e in a_jp['entries'] if e.name == member][0]
    else:
        jp = open(os.path.join(src_tree, rel.replace('/', os.sep)), 'rb').read()
    pcb = pc_tex(parc, pmem)
    if method == 'etc1':
        new, before, after, nblk, nmask = etc1_port(jp, pcb)
        bim = Image.fromarray(before); aim = Image.fromarray(after); note = '%d/%d blocks re-encoded' % (nblk, (before.shape[0] // 4) * (before.shape[1] // 4))
    elif method == 'card':
        new, (rgb, al), (rgb2, al2) = card_port(jp, pcb); bim = flat_rgba(rgb, al); aim = flat_rgba(rgb2, al2); note = 'alpha from Capcom mask, plate colours kept'
    else:
        new, (Lj, Aj), (Ln, An) = la44_port(jp, pcb); bim = flat_rgba(np.dstack([Lj] * 3), Aj); aim = flat_rgba(np.dstack([Ln] * 3), An); note = 'L4A4 from PC luminance/alpha'
    assert len(new) == len(jp) and new[:20] == jp[:20]
    # write into the v1.6 tree
    dst = os.path.join(dst_tree, rel.replace('/', os.sep))
    if not os.path.exists(dst):
        # the update never carried this file: it comes from the cartridge, and the update romfs is a
        # file-level overlay, so adding Capcom's copy with one member replaced is the right shape
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'wb').write(open(os.path.join(src_tree, rel.replace('/', os.sep)), 'rb').read())
        added = True
    else:
        added = False
    if member:
        a_ours = parse_arc(open(dst, 'rb').read())
        out_arc = build_arc_bytes(a_ours, {member: new})
        chk = parse_arc(out_arc)
        assert [e.name for e in chk['entries']] == [e.name for e in a_ours['entries']]
        for eo, en in zip(a_ours['entries'], chk['entries']):
            assert bytes(en.data) == (new if en.name == member else bytes(eo.data)), en.name
        open(dst, 'wb').write(out_arc)
    else:
        open(dst, 'wb').write(new)
    report.append(dict(game=game, loc=loc, pc=parc + '::' + pmem, method=method, note=note, added_to_update=added, new_sha256=hashlib.sha256(new).hexdigest()))
    previews[game].append((loc.split('/')[-1].replace('_BM_NOMIP', ''), bim, aim, note))
    print('%s %-60s %s%s' % (game, loc.split('::')[-1].split('/')[-1], note, '  [file added to the update]' if added else ''))
json.dump(report, io.open(os.path.join(V16, 'port_report.json'), 'w', encoding='utf-8'), indent=1)
for game, tiles in previews.items():
    if not tiles: continue
    W = 256; sheet = Image.new('RGB', (W * len(tiles), 2 * W + 40), (0, 0, 0)); dr = ImageDraw.Draw(sheet)
    for i, (n, b, a, note) in enumerate(tiles):
        b = b.copy(); a = a.copy(); b.thumbnail((W, W)); a.thumbnail((W, W))
        dr.text((i * W + 2, 2), n[:36], fill=(255, 255, 0)); dr.text((i * W + 2, 14), note[:36], fill=(180, 180, 180))
        sheet.paste(b, (i * W, 40)); sheet.paste(a, (i * W, 40 + W))
    sheet.save(os.path.join(ROOT, 'jpvoice', '_notported', 'port_preview_%s.png' % game)); print(game, 'preview', sheet.size)

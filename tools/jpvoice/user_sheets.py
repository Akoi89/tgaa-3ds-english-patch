# -*- coding: utf-8 -*-
"""Two review sheets for the user (who has not played the games): what v1.6 ported (3DS Japanese
before / ported after) and what was left out (3DS Japanese / what Capcom's English would have been).
Textures with readable story text are blurred and labelled."""
import os, sys, io, numpy as np
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
from PIL import Image, ImageDraw, ImageFilter
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch')); sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline')); sys.path.insert(0, os.path.join(ROOT, 'dlc_story_audit'))
from dgs2tool.arc import parse_arc
import tex_view, pctex_rgba, tex_rgba8, etc1a4
PC = os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64', 'archive'); TREES = os.path.join(ROOT, 'jpvoice', '_trees'); V16 = os.path.join(ROOT, 'jpvoice', '_v16'); OUT = os.path.join(ROOT, 'jpvoice', '_notported')


def member(path, name):
    return [bytes(e.data) for e in parse_arc(open(path, 'rb').read())['entries'] if e.name == name][0]


def show3ds(b):
    fmt = b[13]; w, h = tex_view.dims3ds(b)
    if fmt == 0x0b:
        rgb, _ = etc1a4.decode(b[20:], w, h, alpha=False); return Image.fromarray(rgb)
    if fmt in (0x0c, 0x10):
        g = tex_view._morton_grey(np.frombuffer(b[20:20 + w * h], np.uint8), w, h)
        return tex_view.flat(Image.fromarray(np.dstack([(g >> 4) * 17] * 3 + [(g & 15) * 17]).astype(np.uint8), 'RGBA')).convert('RGB')
    im = tex_view.preview(b); return tex_view.flat(im).convert('RGB')


def showpc(b):
    im = pctex_rgba.decode(b); bg = Image.new('RGBA', im.size, (40, 40, 40, 255)); bg.alpha_composite(im); return bg.convert('RGB')


def sheet(rows, path, cols):
    W = 220; H = W * 2 + 44
    im = Image.new('RGB', (W * len(rows), H), (10, 10, 10)); dr = ImageDraw.Draw(im)
    for i, (label, a, b, blur, note) in enumerate(rows):
        for j, t in enumerate((a, b)):
            t = t.copy(); t.thumbnail((W - 8, W - 8))
            if blur and j == 1:
                t = t.filter(ImageFilter.GaussianBlur(7))
            im.paste(t, (i * W + 4, 44 + j * W + (W - 8 - t.size[1]) // 2))
        dr.text((i * W + 4, 2), label[:34], fill=(255, 255, 0)); dr.text((i * W + 4, 14), cols, fill=(160, 160, 160)); dr.text((i * W + 4, 26), note[:36], fill=(255, 120, 120) if blur else (160, 200, 160))
    im.save(path); print(path, im.size)


P = []  # ported: (label, before 3DS JP, after new, blur, note)
def ported(game, arc, name, label, blur=False, note='', loose=False):
    if loose:
        jp = open(os.path.join(TREES, game + '_jp_cart', 'c0', name), 'rb').read(); new = open(os.path.join(V16, game, 'c0', name), 'rb').read()
    else:
        jp = member(os.path.join(TREES, game + '_jp_cart', 'c0', 'archive', arc), name); new = member(os.path.join(V16, game, 'c0', 'archive', arc), name)
    P.append((label, show3ds(jp), show3ds(new), blur, note))


ported('TGAA1', '', r'UI\1_ig\12_cutin\tex\bigfont_uk_wait_GSM_NOMIP.tex'.replace('\\', os.sep), 'shout atlas (1 of 8)', note='rotated variant was Japanese', loose=True)
ported('TGAA2', 'UI_opdemo04_jpn.arc', 'UI/2_doc/26_op/4/tex/opTitle4_BM_NOMIP_HQ.tex', 'TGAA2 last chapter card', note='card art kept, text from Capcom')
ported('TGAA2', 'chr230_jpn.arc', 'obj/chr/chr230/model/chr230_body_BM_NOMIP.tex', 'TGAA2 costume label', note='text on a costume')
ported('TGAA2', 'chr303_jpn.arc', 'obj/chr/chr303/model/chr303_rArm_BM_NOMIP.tex', 'TGAA2 writing on an arm', note='')
ported('TGAA2', 'chr151_jpn.arc', 'obj/chr/chr151/model/chr151_hand_BM_NOMIP.tex', 'TGAA2 paper held in hand', note='')
ported('TGAA2', 'chr574_jpn.arc', 'obj/chr/chr574/model/p1101_09_BM_NOMIP.tex', 'TGAA2 prop labels', note='small labels')
ported('TGAA2', 'place1201_jpn.arc', 'place/p1201/p1201_60_BM_NOMIP.tex', 'TGAA2 background sign', note='')
ported('TGAA2', 'evi3d_1_02_01_jpn.arc', 'item/item1_02_01/model/item1_02_01_0_BM_NOMIP.tex', 'TGAA2 newspaper item (3D)', note='the Court Record model')
ported('TGAA1', 'chr220_jpn.arc', 'obj/chr/chr220/model/chr220_body_BM_NOMIP.tex', 'TGAA1 initials on a prop', note='')
ported('TGAA1', 'chr022_jpn.arc', 'obj/chr/chr022/model/chr022_body_BM_NOMIP.tex', 'TGAA1 costume detail', note='')
ported('TGAA1', 'place0101_jpn.arc', 'place/p0101/p0101_10_BM_NOMIP.tex', 'TGAA1 book cover', note='')
ported('TGAA1', 'evi3d_3_17_00_jpn.arc', 'item/item3_17_00/model/item3_17_00_0_BM_NOMIP.tex', 'TGAA1 card with handwriting', blur=True, note='blurred: readable story text')
ported('TGAA1', 'evi3d_5_16_00_jpn.arc', 'item/item5_16_00/model/item5_16_00_0_BM_NOMIP.tex', 'TGAA1 letter', blur=True, note='blurred: readable story text')
ported('TGAA1', 'evi3d_5_34_00_jpn.arc', 'item/item5_34_00/model/item5_34_00B_BM_NOMIP.tex', 'TGAA1 labelled object', blur=True, note='blurred: readable story text')
sheet(P, os.path.join(OUT, 'user_sheet_ported.png'), 'top: 3DS today   bottom: v1.6')

L = []  # left out: (label, 3DS JP, Capcom English (PC), blur, note)
def leftout(game, arc, name, pcarc, pcname, label, blur=False, note=''):
    jp = member(os.path.join(TREES, game + '_jp_cart', 'c0', 'archive', arc), name); pc = member(os.path.join(PC, pcarc), pcname)
    L.append((label, show3ds(jp), showpc(pc), blur, note))


leftout('TGAA2', 'UI_opdemo01_jpn.arc', 'UI/2_doc/26_op/1/tex/freeHand0105_BM_NOMIP.tex', r'BB\UI_opdemo01_eng.arc', 'UI/2_doc/26_op_BB/1/tex/freeHand0105_BM_NOMIP_HQ_eng.tex', 'opening handwriting (1 of 40)', blur=True, note='blurred: narration text; alpha = timing')
leftout('TGAA2', 'evi3d_1_04_01_jpn.arc', 'item/item1_04_01/model/item1_04_01_0_BM_NOMIP.tex', r'BB\evi3d_1_04_01_eng.arc', 'BB/item/item1_04_01/model/item1_04_01_eng_BM_NOMIP.tex', 'TGAA2 evidence (odd PC format)', note='PC decode unreliable')
leftout('TGAA1', 'evi3d_5_06_10_jpn.arc', 'item/item5_06_10/model/item5_06_10_0_BM_NOMIP.tex', r'GO\evi3d_5_06_10_eng.arc', 'GO/item/item5_06_10/model/item5_06_10_0_eng_BM_NOMIP.tex', 'TGAA1 evidence (odd PC format)', blur=True, note='blurred; PC decode unreliable')
leftout('TGAA1', 'evi3d_1_03_00_jpn.arc', 'item/item1_03_00/model/item1_03_00_0_BM_NOMIP.tex', r'GO\evi3d_1_03_00_eng.arc', 'GO/item/item1_03_00/model/item1_03_00_0_eng_BM_NOMIP.tex', 'TGAA1 newspaper, Russian both', note='no translation gain')
sheet(L, os.path.join(OUT, 'user_sheet_leftout.png'), 'top: 3DS today   bottom: Capcom EN')

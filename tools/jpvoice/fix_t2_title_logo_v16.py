# -*- coding: utf-8 -*-
"""Restore Capcom's official colour title logo in the TGAA2 v1.6 update.

Cause: 1.0.15 restamped the loose title atlas from dlc_story_audit/tgaa2/v233_dir (the fan-logo
plate), so the official logo that shipped in 1.0.14 was lost; 1.0.16 inherited that atlas
(1.0.16 atlas == v233 plate everywhere except the stamp rectangle, measured).

Fix: take the shipped 1.0.14 atlas (official logo, colour + cream sprites), repaint the stamp
rectangle with the current version text, splice that one file into the shipped 1.0.16 CIA
(same TMD 3.1.0, same stamp, so the v1.6 assets can be replaced in place), and prove from a
re-extraction of the built CIA that exactly one romfs file changed.

    python fix_t2_title_logo_v16.py            (builds jpvoice/_v17/TGAA2-base-1.0.16.cia)
"""
import os, sys, io, shutil, subprocess, hashlib, filecmp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import numpy as np
from PIL import Image, ImageDraw
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
from cia import Cia
import stamp_title_versions as stv
import tex_view, tex_rgba8

TOOL = os.path.join(ROOT, '3dstool', '3dstool.exe')
SHELL = os.path.join(ROOT, 'Final', '_CURRENT', 'TGAA2-base-1.0.16.cia')
SHELL_SHA = 'd6e450b199c03ecfc290cf5b419d1667ad4997ba2759c91cf556749e6f76983c'
ATLAS_REL = os.path.join('UI', '4_menu', '40_title', 'tex', 'title_jpn_01_BM_NOMIP_HQ.tex')
PLATE_1014 = os.path.join(ROOT, 'dlc_ai_voice', '_shipped', 'TGAA2-base-1.0.14', 'content0', ATLAS_REL)
STAMP = 'ENG 1.0.16'
VERSION = '3.1.0'
WORK = os.path.join(ROOT, 'jpvoice', '_v17')
OUT = os.path.join(WORK, 'TGAA2-base-1.0.16.cia')
PREV = os.path.join(ROOT, 'jpvoice', '_notported')


def extract(cia_path, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    c = Cia(cia_path)
    n = os.path.join(dst, 'c0.ncch'); rom = os.path.join(dst, 'c0.romfs'); h = os.path.join(dst, 'c0.hdr')
    open(n, 'wb').write(c.contents[0])
    r = subprocess.run([TOOL, '-xtf', 'cxi', n, '--header', h, '--romfs', rom], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('cxi extract failed: ' + r.stdout + r.stderr)
    tree = os.path.join(dst, 'tree'); os.makedirs(tree)
    r = subprocess.run([TOOL, '-xtf', 'romfs', rom, '--romfs-dir', tree], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('romfs extract failed: ' + r.stdout + r.stderr)
    os.remove(n); os.remove(rom)
    return tree, c


def tree_files(t):
    out = {}
    for dp, dn, fn in os.walk(t):
        for f in fn:
            p = os.path.join(dp, f); out[os.path.relpath(p, t)] = p
    return out


def tree_diff(a, b):
    fa, fb = tree_files(a), tree_files(b)
    diffs = [k for k in sorted(set(fa) | set(fb))
             if k not in fa or k not in fb or not filecmp.cmp(fa[k], fb[k], shallow=False)]
    return diffs, len(fa), len(fb)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    os.makedirs(WORK, exist_ok=True)
    assert sha(SHELL) == SHELL_SHA, 'shell is not the released 1.0.16 (sha256 mismatch)'
    print('shell', os.path.basename(SHELL), 'sha256 OK')

    # 1. fresh extraction of the shipped 1.0.16
    tree16, c16 = extract(SHELL, os.path.join(WORK, 'x_1016'))
    print('shipped 1.0.16 declares %d.%d.%d, %d content(s)' % (*c16.version(), c16.count))

    # 2. the new atlas: 1.0.14 plate + current stamp
    plate = open(PLATE_1014, 'rb').read()
    new_tex, a8 = stv.stamp_tex(plate, STAMP)
    assert len(new_tex) == len(plate) == os.path.getsize(os.path.join(tree16, ATLAS_REL))
    # everything outside the stamp rectangle must equal the 1.0.14 plate
    rgb0, al0 = tex_rgba8.decode_rgba8(plate); p0 = np.dstack([rgb0, al0]).astype(int)
    x0, y0, x1, y1 = stv.STAMP_REGION
    m = np.ones(p0.shape[:2], bool); m[y0:y1, x0:x1] = False
    nd = (np.abs(p0 - a8.astype(int)).sum(-1) > 0)
    assert not (nd & m).any(), 'atlas differs from the 1.0.14 plate outside the stamp rectangle'
    print('new atlas: %d px repainted, all inside the stamp rectangle %s' % (int(nd.sum()), stv.STAMP_REGION))

    # 3. work tree = shipped 1.0.16 + the new atlas
    tree17 = os.path.join(WORK, 'tree17')
    if os.path.isdir(tree17):
        shutil.rmtree(tree17)
    shutil.copytree(tree16, tree17)
    open(os.path.join(tree17, ATLAS_REL), 'wb').write(new_tex)
    open(os.path.join(WORK, 'title_jpn_01_BM_NOMIP_HQ_fixed.tex'), 'wb').write(new_tex)

    # 4. build (plaintext romfs splice, build.py)
    if os.path.exists(OUT):
        os.remove(OUT)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'testimony_pipeline', 'build.py'),
                        SHELL, OUT, VERSION, '0=' + tree17], capture_output=True, text=True)
    print(r.stdout.strip()); print(r.stderr.strip())
    if r.returncode or not os.path.exists(OUT):
        raise SystemExit('build failed')

    # 5. verify from the built file
    treeB, cB = extract(OUT, os.path.join(WORK, 'x_built'))
    print('built declares %d.%d.%d, %d content(s)' % (*cB.version(), cB.count))
    diffs, na, nb = tree_diff(tree16, treeB)
    print('built vs shipped 1.0.16: %d/%d files, differing: %s' % (nb, na, diffs))
    assert diffs == [ATLAS_REL], 'expected exactly the atlas to differ'
    assert open(os.path.join(treeB, ATLAS_REL), 'rb').read() == new_tex, 'built atlas != stamped atlas'
    d2, _, _ = tree_diff(tree17, treeB)
    assert d2 == [], 'built tree != work tree: %s' % d2
    print('built atlas reads back byte-identical; built tree == work tree')

    # 6. renders for the user
    ims = []
    for lab, p in (('shipped 1.0.14', PLATE_1014), ('released 1.0.16 (wrong plate)', os.path.join(tree16, ATLAS_REL)),
                   ('fixed 1.0.16', os.path.join(treeB, ATLAS_REL))):
        ims.append((lab, tex_view.preview(open(p, 'rb').read()).convert('RGB')))
    W = Image.new('RGB', (512 * 3 + 20, 540), (30, 30, 30)); d = ImageDraw.Draw(W)
    for i, (lab, im) in enumerate(ims):
        W.paste(im, (i * 522, 28)); d.text((i * 522 + 4, 6), lab, fill=(255, 255, 0))
    W.save(os.path.join(PREV, 'title_logo_fix_compare.png'))
    ims[2][1].save(os.path.join(PREV, 'title_logo_fixed_atlas.png'))
    print('sha256 %s  %d bytes' % (sha(OUT), os.path.getsize(OUT)))
    shutil.rmtree(os.path.join(WORK, 'x_built'), ignore_errors=True)


if __name__ == '__main__':
    main()

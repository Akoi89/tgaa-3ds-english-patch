# -*- coding: utf-8 -*-
"""TGAA1-DLC-1.0.11 = released 1.0.10 + the English Picture Book / Editor's Notes / theme pages.

    python build_dlc_1011.py

1. every final/<page>.png (512x256) is written into its content's tex/ with tex_rgba8.encode_rgb8,
   using the shipped texture as the header donor (round trip of an unedited page is byte-exact);
2. the Episode 0 cover carries the version stamp: first prove stamp_dlc_covers' method reproduces
   the shipped 1.0.10 cover byte for byte, then stamp "DLC 1.0.11" on the LaMa-erased cover source
   (cover_build/simple_out_lama/aoc00.png); issues 9-13 covers from cover_build/ph_out_lama (LaMa);
3. build.py rebuilds only the changed contents (encrypted CFA route) with TMD version 3.0.11
   (the project rule: DLC TMDs are major 3; 1.0.10 shipped as 3.0.10);
4. verification: the built CIA is re-extracted and compared file by file with the 1.0.10 extraction;
   exactly the page textures and the stamped cover may differ, and each must equal what we wrote.
"""
import csv
import hashlib
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_ai_voice'))
import tex_rgba8                 # noqa: E402
import stamp_dlc_covers as SC    # noqa: E402

SRC = os.path.join(ROOT, 'dlc_ai_voice', '_shipped', 'TGAA1-DLC-1.0.10')
SHELL = os.path.join(ROOT, 'Final', '_CURRENT', 'TGAA1-DLC-1.0.10.cia')
OUT = os.path.join(ROOT, 'Final', '_new', 'TGAA1-DLC-1.0.11.cia')
WORK = os.path.join(HERE, '_build')
COVERS = os.path.join(ROOT, 'dlc_story_audit', 'cover_build')


def stamped_cover(version, src=None):
    donor = os.path.join(SRC, 'content2', 'tex', SC.TEX % 0)
    blob = open(donor, 'rb').read()
    rgba = np.asarray(Image.open(src or SC.source_png(COVERS, 0)).convert('RGBA'))
    rgba = SC.draw_stamp(rgba, version)
    return SC.encode_rgba8(blob, rgba[:, :, :3], rgba[:, :, 3])


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'manifest.tsv')), delimiter='\t'))
    where = {r['name']: r['content'] for r in rows}
    pages = sorted(f[:-4] for f in os.listdir(os.path.join(HERE, 'final')) if f.endswith('.png'))
    contents = sorted({where[p] for p in pages} | {'content2'} | {'content%d' % (i + 2) for i in range(9, 14)}, key=lambda c: int(c[7:]))
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    for c in contents:
        shutil.copytree(os.path.join(SRC, c), os.path.join(WORK, c))
    written = {}
    for p in pages:
        rel = os.path.join(where[p], 'tex', p + '_BM_NOMIP_HQ.tex')
        blob = open(os.path.join(SRC, rel), 'rb').read()
        rgb = np.asarray(Image.open(os.path.join(HERE, 'final', p + '.png')).convert('RGB'))
        assert rgb.shape == (256, 512, 3), (p, rgb.shape)
        if blob[13] == 3:     # RGBA8 (4 pages): keep the page's own alpha
            _, alpha = tex_rgba8.decode_rgba8(blob)
            new = tex_rgba8.encode_rgba8(blob, rgb, alpha)
            dec = tex_rgba8.decode_rgba8(new)[0]
        else:
            new = tex_rgba8.encode_rgb8(blob, rgb)
            dec = tex_rgba8.decode_rgb8(new); dec = dec[0] if isinstance(dec, tuple) else dec
        assert len(new) == len(blob) and new[:20] == blob[:20], p
        assert np.array_equal(np.asarray(dec)[:, :, :3], rgb), 'decode mismatch ' + p
        open(os.path.join(WORK, rel), 'wb').write(new)
        written[rel.replace(os.sep, '/')] = hashlib.sha256(new).hexdigest()
    print('%d page textures encoded into %s' % (len(pages), ', '.join(contents)))
    # issues 9-13 placeholder covers: LaMa-erased (placeholders.py PH_ERASE=lama, user OK 2026-09-15);
    # the Telea versions in ph_out/ reproduce the shipped 1.0.10 textures byte for byte
    for issue in range(9, 14):
        rel = 'content%d/tex/' % (issue + 2) + SC.TEX % issue
        blob = open(os.path.join(SRC, rel.replace('/', os.sep)), 'rb').read()
        rgba = np.asarray(Image.open(os.path.join(COVERS, 'ph_out_lama', 'aoc%02d.png' % issue)).convert('RGBA'))
        old_rgba = np.asarray(Image.open(os.path.join(COVERS, 'ph_out', 'aoc%02d.png' % issue)).convert('RGBA'))
        assert SC.encode_rgba8(blob, old_rgba[:, :, :3], old_rgba[:, :, 3]) == blob, 'ph_out does not reproduce ' + rel
        new = SC.encode_rgba8(blob, rgba[:, :, :3], rgba[:, :, 3])
        assert len(new) == len(blob)
        open(os.path.join(WORK, rel.replace('/', os.sep)), 'wb').write(new)
        written[rel] = hashlib.sha256(new).hexdigest()
    print('5 placeholder covers (issues 9-13) encoded; the Telea sources reproduce the shipped ones')
    # stamp: prove the method, then stamp 1.0.11
    shipped = open(os.path.join(SRC, 'content2', 'tex', SC.TEX % 0), 'rb').read()
    again = stamped_cover('DLC 1.0.10')
    print('stamp method reproduces the shipped 1.0.10 cover byte for byte:', again == shipped)
    assert again == shipped, 'stamp method does not reproduce the shipped cover; stop'
    cover_rel = 'content2/tex/' + SC.TEX % 0
    # 1.0.11 cover: the LaMa-erased Episode 0 source (simple.py COVER_ERASE=lama, user OK 2026-09-15)
    new_cover = stamped_cover('DLC 1.0.11', os.path.join(COVERS, 'simple_out_lama', 'aoc00.png'))
    open(os.path.join(WORK, cover_rel.replace('/', os.sep)), 'wb').write(new_cover)
    written[cover_rel] = hashlib.sha256(new_cover).hexdigest()
    # build
    args = [sys.executable, os.path.join(ROOT, 'testimony_pipeline', 'build.py'), SHELL, OUT, '3.0.11']   # TMD major 3 like every DLC build (1.0.10 = 3.0.10); stamp/filename 1.0.11
    args += ['%d=%s' % (int(c[7:]), os.path.join(WORK, c)) for c in contents]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    r = subprocess.run(args, capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-1500:])
    if r.returncode:
        raise SystemExit('build.py failed')
    # verify by re-extraction
    import extract_shipped as es
    name = 'TGAA1-DLC-1.0.11-candidate'
    dest = os.path.join(es.OUT, name)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    es.extract(name, OUT)
    diff, missing = [], []
    for dp, _, fs in os.walk(SRC):
        for fn in fs:
            a = os.path.join(dp, fn)
            rel = os.path.relpath(a, SRC).replace(os.sep, '/')
            b = os.path.join(dest, rel.replace('/', os.sep))
            if not os.path.exists(b):
                missing.append(rel); continue
            if open(a, 'rb').read() != open(b, 'rb').read():
                diff.append(rel)
    bad = [d for d in diff if d not in written]
    wrong = [k for k, h in written.items() if hashlib.sha256(open(os.path.join(dest, k.replace('/', os.sep)), 'rb').read()).hexdigest() != h]
    print('re-extracted: %d files differ from 1.0.10 (expected %d), unexpected %d, missing %d, written-but-wrong %d'
          % (len(diff), len(written), len(bad), len(missing), len(wrong)))
    assert not bad and not missing and not wrong, (bad[:5], missing[:5], wrong[:5])
    h = hashlib.sha256(open(OUT, 'rb').read()).hexdigest()
    print('OK %s  sha256 %s  %d bytes' % (OUT, h, os.path.getsize(OUT)))


if __name__ == '__main__':
    main()

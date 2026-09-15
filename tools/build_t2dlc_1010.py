# -*- coding: utf-8 -*-
"""TGAA2-DLC-1.0.10 = released 1.0.9 + LaMa paper under the score sheets (user OK 2026-09-15).

    python dlc_story_audit/build_t2dlc_1010.py

1. score sheets (content 2, UI/evt/EVENT8_05_01, _01_big, _02): first prove that pasting the SHIPPED
   composites (_event_png/_composite_bak_pre_lama) into the decoded shipped texture and re-encoding gives
   the shipped file byte for byte, then encode the LaMa composites (_event_png/_composite_lama, made by
   scoresheet_lama.py) the same way;
2. costume banner (content 1): prove stamp_dlc_banners.stamp on the unstamped idx1_v7_dir source with
   "DLC 1.0.9" reproduces the shipped texture byte for byte, then stamp "DLC 1.0.10";
3. build.py from the shipped 1.0.9 CIA, only contents 1 and 2, TMD 1.0.10 (TGAA2's DLC declares 1.0.x:
   the shipped 1.0.9 declares 1.0.9);
4. re-extract the built CIA and diff against the 1.0.9 extraction: exactly the 4 written files may
   differ, and each must equal what was written.
"""
import hashlib
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(R, 'dlc_ai_voice'))
import tex_rgba8                    # noqa: E402
import stamp_dlc_banners as SB      # noqa: E402

SRC = os.path.join(R, 'dlc_ai_voice', '_shipped', 'TGAA2-DLC-1.0.9-pad32')
SHELL = os.path.join(R, 'Final', '_CURRENT', 'TGAA2-DLC-1.0.9.cia')
OUT = os.path.join(R, 'Final', '_new', 'TGAA2-DLC-1.0.10.cia')
WORK = os.path.join(R, 'dlc_story_audit', 'tgaa2', 'dlc', '_build_1010')
EV = os.path.join(R, 'dlc_story_audit', 'tgaa2', 'dlc', '_event_png')
BN = os.path.join(R, 'dlc_story_audit', 'tgaa2', 'dlc')
SHEETS = ('EVENT8_05_01_big', 'EVENT8_05_01', 'EVENT8_05_02')
COST = 'content1/dlc_costumepack_BM_NOMIP_HQ.tex'


def rgb(path):
    return np.asarray(Image.open(path).convert('RGB'))


def sheet_tex(donor, comp):
    full = tex_rgba8.decode_rgb8(donor).copy()
    h, w = comp.shape[:2]
    full[0:h, 0:w] = comp
    out = tex_rgba8.encode_rgb8(donor, full)
    assert len(out) == len(donor) and out[:20] == donor[:20]
    assert tex_rgba8.decode_rgb8(out).tobytes() == full.tobytes()
    return out


def cost_tex(version):
    blob = open(os.path.join(BN, *SB.BANNERS['cost'][0].split('/')), 'rb').read()
    c, a = tex_rgba8.decode_rgba8(blob)
    # the stamper pins the ink's LEFT edge at x 358; a longer version string would run off the drawable
    # area (x <= 423), so keep the RIGHT edge where the 1.0.9 stamp's was (x 416)
    from PIL import ImageFont
    f = ImageFont.truetype(SB.FONT, SB.SIZE)
    keep = SB.TARGET
    SB.TARGET = (keep[0] - int(round(f.getlength(version) - f.getlength('DLC 1.0.9'))), keep[1])
    try:
        rgba, box = SB.stamp(np.dstack([np.asarray(c)[:, :, :3], np.asarray(a)]), version)
    finally:
        SB.TARGET = keep
    print('  stamp "%s" ink x %d..%d y %d..%d' % ((version,) + tuple(int(v) for v in box)))
    return tex_rgba8.encode_rgba8(blob, rgba[:, :, :3], rgba[:, :, 3])


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    for c in ('content1', 'content2'):
        shutil.copytree(os.path.join(SRC, c), os.path.join(WORK, c))
    written = {}
    for n in SHEETS:
        rel = 'content2/UI/evt/%s_BM_NOMIP_HQ.tex' % n
        donor = open(os.path.join(SRC, *rel.split('/')), 'rb').read()
        again = sheet_tex(donor, rgb(os.path.join(EV, '_composite_bak_pre_lama', n + '_english.png')))
        print('%-18s shipped composite re-encodes to the shipped texture: %s' % (n, again == donor))
        assert again == donor, 'score sheet method does not reproduce the shipped texture; stop'
        new = sheet_tex(donor, rgb(os.path.join(EV, '_composite_lama', n + '_english.png')))
        open(os.path.join(WORK, *rel.split('/')), 'wb').write(new)
        written[rel] = hashlib.sha256(new).hexdigest()
    shipped = open(os.path.join(SRC, *COST.split('/')), 'rb').read()
    again = cost_tex('DLC 1.0.9')
    print('costume stamp method reproduces the shipped 1.0.9 banner byte for byte:', again == shipped)
    assert again == shipped, 'stamp method does not reproduce the shipped banner; stop'
    new = cost_tex('DLC 1.0.10')
    open(os.path.join(WORK, *COST.split('/')), 'wb').write(new)
    written[COST] = hashlib.sha256(new).hexdigest()
    args = [sys.executable, os.path.join(R, 'testimony_pipeline', 'build.py'), SHELL, OUT, '1.0.10',
            '1=%s' % os.path.join(WORK, 'content1'), '2=%s' % os.path.join(WORK, 'content2')]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    r = subprocess.run(args, capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-1500:])
    if r.returncode:
        raise SystemExit('build.py failed')
    import extract_shipped as es
    name = 'TGAA2-DLC-1.0.10-candidate'
    dest = os.path.join(es.OUT, name)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    es.extract(name, OUT)
    diff, missing = [], []
    for dp, _, fs in os.walk(SRC):
        for fn in fs:
            a = os.path.join(dp, fn)
            rel = os.path.relpath(a, SRC).replace(os.sep, '/')
            b = os.path.join(dest, *rel.split('/'))
            if not os.path.exists(b):
                missing.append(rel)
                continue
            if open(a, 'rb').read() != open(b, 'rb').read():
                diff.append(rel)
    bad = [d for d in diff if d not in written]
    wrong = [k for k, h in written.items() if hashlib.sha256(open(os.path.join(dest, *k.split('/')), 'rb').read()).hexdigest() != h]
    print('re-extracted: %d files differ from 1.0.9 (expected %d), unexpected %d, missing %d, written-but-wrong %d'
          % (len(diff), len(written), len(bad), len(missing), len(wrong)))
    assert not bad and not missing and not wrong, (bad[:5], missing[:5], wrong[:5])
    h = hashlib.sha256(open(OUT, 'rb').read()).hexdigest()
    print('OK %s  sha256 %s  %d bytes' % (OUT, h, os.path.getsize(OUT)))


if __name__ == '__main__':
    main()

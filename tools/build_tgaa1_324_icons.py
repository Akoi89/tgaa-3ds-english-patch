# -*- coding: utf-8 -*-
"""TGAA1-base-3.2.4 (unreleased) + the rebuilt DLC-list icon sheet (user, 2026-09-15: the shipped sheet
had artifacts and cut off the bottom of the artwork).

    python testimony_pipeline/build_tgaa1_324_icons.py

Input : dlc_story_audit/_menuicon/TGAA1-base-3.2.4-bounce-only.cia (build_tgaa1_324_bounce.py: 3.2.3 + bounce fix) and its extraction
        dlc_ai_voice/_shipped/TGAA1-base-3.2.4-staged/content0;
        dlc_story_audit/_menuicon/dlc_menuicon_new.png from dlc_story_audit/menuicon_rebuild.py.
Change: archive/extra_jpn.arc member UI/4_menu/43_extra/tex/dlc_menuicon_BM_HQ_NOMIP.tex only.
Checks: the archive rebuild with no replacement reproduces the shipped archive byte for byte; the new
member round-trips; the rebuilt archive differs from the old in that member only; build.py (NoCrypto
splice) keeps TMD 3.2.4; the built CIA is re-extracted and exactly one romfs file differs from the staged
3.2.4, equal to what was written; the ExeFS .code is byte-identical to the staged 3.2.4 (bounce fix and
"ENG 3.2.4" stamp kept).
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
sys.path.insert(0, os.path.join(R, 'dlc_icons', 'tgaa2-en-patch'))
import tex_rgba8                                   # noqa: E402
from cia import Cia                                # noqa: E402
from build_tgaa1_324_bounce import code_of         # noqa: E402
from dgs2tool.arc import parse_arc, build_arc_bytes  # noqa: E402

SHELL = os.path.join(R, 'dlc_story_audit', '_menuicon', 'TGAA1-base-3.2.4-bounce-only.cia')   # build_tgaa1_324_bounce.py output, sha256 12bcfa17...
SRC = os.path.join(R, 'dlc_ai_voice', '_shipped', 'TGAA1-base-3.2.4-staged', 'content0')
OUT = os.path.join(R, 'Final', '_new', 'TGAA1-base-3.2.4.cia')
WORK = os.path.join(R, 'dlc_story_audit', '_menuicon', '_tree324')
PNG = os.path.join(R, 'dlc_story_audit', '_menuicon', 'dlc_menuicon_new.png')
ARC_REL = 'archive/extra_jpn.arc'
MEMBER = 'dlc_menuicon_BM_HQ_NOMIP'


def main():
    arc_path = os.path.join(SRC, *ARC_REL.split('/'))
    old_arc = open(arc_path, 'rb').read()
    a = parse_arc(old_arc)
    assert build_arc_bytes(a) == old_arc, 'archive null rebuild is not byte-identical; stop'
    ent = [e for e in a['entries'] if MEMBER in e.name]
    assert len(ent) == 1, [e.name for e in ent]
    ent = ent[0]
    donor = ent.data
    _, alpha = tex_rgba8.decode_rgba8(donor)
    rgba = np.asarray(Image.open(PNG).convert('RGBA'))
    assert np.array_equal(rgba[:, :, 3], np.asarray(alpha)), 'alpha differs from the shipped member'
    new_tex = tex_rgba8.encode_rgba8(donor, rgba[:, :, :3], rgba[:, :, 3])
    assert len(new_tex) == len(donor) and new_tex[:20] == donor[:20]
    back = np.asarray(tex_rgba8.decode_rgba8(new_tex)[0])[:, :, :3]
    assert np.array_equal(back, rgba[:, :, :3]), 'member does not round-trip'
    new_arc = build_arc_bytes(a, {ent.name: new_tex})
    b = parse_arc(new_arc)
    changed = [e.name for e, f in zip(a['entries'], b['entries']) if e.name != f.name or e.data != f.data]
    assert changed == [ent.name], changed
    print('%s: member %s replaced, %d bytes -> archive %d -> %d bytes' % (ARC_REL, ent.name, len(new_tex), len(old_arc), len(new_arc)))
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    shutil.copytree(SRC, WORK)
    open(os.path.join(WORK, *ARC_REL.split('/')), 'wb').write(new_arc)
    want = hashlib.sha256(new_arc).hexdigest()

    r = subprocess.run([sys.executable, os.path.join(R, 'testimony_pipeline', 'build.py'), SHELL, OUT, '3.2.4', '0=%s' % WORK],
                       capture_output=True, text=True)
    print(r.stdout[-1200:], r.stderr[-1200:])
    if r.returncode:
        raise SystemExit('build.py failed')
    import extract_shipped as es
    name = 'TGAA1-base-3.2.4-icons-candidate'
    dest = os.path.join(es.OUT, name)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    es.extract(name, OUT)
    dest0 = os.path.join(dest, 'content0')
    diff, missing, extra = [], [], []
    for dp, _, fs in os.walk(SRC):
        for fn in fs:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, SRC).replace(os.sep, '/')
            q = os.path.join(dest0, *rel.split('/'))
            if not os.path.exists(q):
                missing.append(rel)
            elif open(p, 'rb').read() != open(q, 'rb').read():
                diff.append(rel)
    n_src = sum(len(fs) for _, _, fs in os.walk(SRC))
    n_dst = sum(len(fs) for _, _, fs in os.walk(dest0))
    print('re-extracted: %d files (staged %d); differ %s; missing %d' % (n_dst, n_src, diff, len(missing)))
    assert diff == [ARC_REL] and not missing and n_dst == n_src, 'unexpected romfs difference'
    assert hashlib.sha256(open(os.path.join(dest0, *ARC_REL.split('/')), 'rb').read()).hexdigest() == want
    s, o = Cia(SHELL), Cia(OUT)
    assert o.version() == (3, 2, 4), o.version()
    assert code_of(s.contents[0]) == code_of(o.contents[0]), '.code changed'
    h = hashlib.sha256(open(OUT, 'rb').read()).hexdigest()
    print('OK %s  version 3.2.4, .code identical to the staged 3.2.4, one romfs file changed; sha256 %s  %d bytes'
          % (OUT, h, os.path.getsize(OUT)))


if __name__ == '__main__':
    main()

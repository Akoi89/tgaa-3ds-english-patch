# -*- coding: utf-8 -*-
"""Read the 21 cues back OUT of a built CIA and prove what shipped.

Working trees have misled this project before, so the gate is the built file:
extract its romfs, compare each cue against Capcom's Japanese original, and
check every .stqr row inside the CIA against the file it names.

    python verify_built.py <built.cia> TGAA1|TGAA2
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))

import mca
import stqr
from cia import Cia
from import_21 import CROWD, DANCE, find_one

TOOL = os.path.join(ROOT, '3dstool', '3dstool.exe')
JP = {'TGAA1': os.path.join(ROOT, 'dlc_story_audit', 'basegame', 'rom'),
      'TGAA2': os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs')}


def main(cia_path, game):
    c = Cia(cia_path)
    print('%s declares %d.%d.%d, %d content(s)'
          % (os.path.basename(cia_path), *c.version(), c.count))
    tmp = tempfile.mkdtemp(prefix='verify21')
    try:
        tree = os.path.join(tmp, 'tree')
        os.makedirs(tree)
        for i, blob in enumerate(c.contents):
            n = os.path.join(tmp, 'c%d.ncch' % i)
            r = os.path.join(tmp, 'c%d.romfs' % i)
            h = os.path.join(tmp, 'c%d.hdr' % i)
            open(n, 'wb').write(blob)
            for kind in ('cxi', 'cfa'):
                subprocess.run([TOOL, '-xtf', kind, n, '--header', h, '--romfs', r],
                               capture_output=True)
                if os.path.exists(r) and os.path.getsize(r):
                    break
            else:
                continue
            subprocess.run([TOOL, '-xtf', 'romfs', r, '--romfs-dir', tree],
                           capture_output=True)

        eng = jp = absent = 0
        for name in CROWD + DANCE:
            got = find_one(tree, name + '.mca')
            orig = find_one(JP[game], name + '.mca')
            if not got:
                absent += 1
                continue
            if open(got, 'rb').read() == open(orig, 'rb').read():
                jp += 1
                print('   still Japanese: %s' % name)
            else:
                eng += 1
        print('%d cues English in the built CIA, %d still Japanese, %d not carried'
              % (eng, jp, absent))

        stale = rows = 0
        for dirpath, _, files in os.walk(tree):
            for fn in files:
                if not fn.endswith('.stqr'):
                    continue
                _, _, ents = stqr.parse(open(os.path.join(dirpath, fn), 'rb').read())
                snd = os.path.join(dirpath, 'wav')
                for e in ents:
                    base = e['name'].replace('\\', '/').split('/')[-1]
                    if not base.endswith('.mca'):
                        base += '.mca'
                    p = os.path.join(snd, base)
                    if not os.path.exists(p):
                        continue
                    rows += 1
                    hh = mca.parse(p)
                    if (e['size'], e['samples'], e['rate']) != (
                            os.path.getsize(p), hh['samples'], hh['rate']):
                        stale += 1
                        print('   STALE ROW %s / %s' % (fn, base))
        print('%d index rows inside the CIA name a local file, %d stale' % (rows, stale))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

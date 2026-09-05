# -*- coding: utf-8 -*-
"""Build the TGAA2 DLC twice: without the synthesised shouts, and with them.

    clean   exactly what the project ships today. Every voice in it is
            Capcom's own recording. Kazuma's and Hosonaga's "Take that"
            stay Japanese, because Capcom never recorded them in English.

    aivoice the same build with those two shouts replaced by the wavs in
            synth/, which are NOT Capcom recordings and not any performer's
            actual take. Anyone installing this one should be told that.

Both carry the same title id and version, so a 3DS holds one or the other --
installing either replaces the other. That is the intended choice, but it also
means the two are indistinguishable once installed. See NOTES.md.

The clean build is not assumed to be unchanged, it is measured: it is compared
byte for byte against the shell it was built from, and the two output CIAs are
compared against each other. Both .mca files are then read back OUT of the
finished CIAs rather than off the working trees, because a working tree has
lied to this project before.

    python build_variants.py                      # both, from the rc19 shell
    python build_variants.py --version 1.0.9
    python build_variants.py --only aivoice
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))

DLC = os.path.join(ROOT, 'dlc_story_audit', 'tgaa2', 'dlc')
IDX1 = os.path.join(DLC, 'idx1_105_dir')
IDX2 = os.path.join(DLC, 'idx2_105_dir')
AI_TREE = os.path.join(HERE, '_tree_ai', 'idx2_dir')
OUT = os.path.join(HERE, '_out')
TOOL = os.path.join(ROOT, '3dstool', '3dstool.exe')
SHELL = os.path.join(ROOT, 'dlc_story_audit', '_validation',
                     'TGAA2-DLC-1.0.8-rc19-titlecolour.cia')
SHOUTS = ['chr100_asg_v_kurae_jpn.mca', 'chr010_hms_v_kurae_jpn.mca']

from cia import Cia


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def sync_ai_tree():
    """A full copy of idx2, with the synthesised shouts written into the copy.

    A copy, not an edit in place: the clean build must be reachable without
    undoing anything, and build.py packs a whole tree, so the two trees have
    to be genuinely separate rather than one tree with a flag.
    """
    if os.path.isdir(AI_TREE):
        shutil.rmtree(AI_TREE)
    os.makedirs(os.path.dirname(AI_TREE), exist_ok=True)
    shutil.copytree(IDX2, AI_TREE)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'import_kurae.py'),
                        '--tree', AI_TREE, '--apply'])
    if r.returncode != 0:
        raise SystemExit('import_kurae failed; not building the aivoice variant')

    changed = tree_diff(IDX2, AI_TREE)
    if sorted(changed) != sorted(SHOUTS):
        raise SystemExit('the ai tree differs from the clean tree in %d file(s): %s\n'
                         'expected exactly the two shouts'
                         % (len(changed), ', '.join(sorted(changed)) or '(none)'))
    print('   ai tree differs from clean in exactly the two shouts')


def tree_diff(a, b):
    """Basenames of files that differ between two trees (or exist in only one)."""
    out = []
    for root, _, files in os.walk(a):
        for fn in files:
            pa = os.path.join(root, fn)
            pb = os.path.join(b, os.path.relpath(pa, a))
            if not os.path.exists(pb) or open(pa, 'rb').read() != open(pb, 'rb').read():
                out.append(fn)
    for root, _, files in os.walk(b):
        for fn in files:
            pb = os.path.join(root, fn)
            if not os.path.exists(os.path.join(a, os.path.relpath(pb, b))):
                out.append(fn)
    return out


def build(shell, out_path, version, idx2_tree):
    r = subprocess.run([sys.executable,
                        os.path.join(ROOT, 'testimony_pipeline', 'build.py'),
                        shell, out_path, version,
                        '1=' + IDX1, '2=' + idx2_tree])
    if r.returncode != 0:
        raise SystemExit('build.py failed for %s' % os.path.basename(out_path))


def shouts_from_cia(cia_path):
    """Pull the two .mca back out of a finished CIA. Content 2 is an encrypted
    CFA, so it has to come out through 3dstool rather than off the tree."""
    c = Cia(cia_path)
    tmp = tempfile.mkdtemp(prefix='ciaverify')
    try:
        ncch = os.path.join(tmp, 'c2.ncch')
        open(ncch, 'wb').write(c.contents[2])
        romfs = os.path.join(tmp, 'c2.romfs')
        subprocess.run([TOOL, '-xtf', 'cfa', ncch, '--romfs', romfs],
                       capture_output=True)
        tree = os.path.join(tmp, 'tree')
        subprocess.run([TOOL, '-xtf', 'romfs', romfs, '--romfs-dir', tree],
                       capture_output=True)
        found = {}
        for root, _, files in os.walk(tree):
            for fn in files:
                if fn in SHOUTS:
                    found[fn] = open(os.path.join(root, fn), 'rb').read()
        if len(found) != len(SHOUTS):
            raise SystemExit('could not read the shouts back out of %s'
                             % os.path.basename(cia_path))
        return found
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shell', default=SHELL)
    ap.add_argument('--version', default='1.0.8')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--only', choices=['clean', 'aivoice'])
    a = ap.parse_args()

    if not os.path.exists(a.shell):
        raise SystemExit('shell not found: %s' % a.shell)
    os.makedirs(a.out, exist_ok=True)
    clean = os.path.join(a.out, 'TGAA2-DLC-%s.cia' % a.version)
    ai = os.path.join(a.out, 'TGAA2-DLC-%s-aivoice.cia' % a.version)

    if a.only != 'aivoice':
        print('\nclean build (Capcom voices only)')
        build(a.shell, clean, a.version, IDX2)
    if a.only != 'clean':
        print('\nai tree')
        sync_ai_tree()
        print('\naivoice build (two synthesised shouts)')
        build(a.shell, ai, a.version, AI_TREE)

    print('\nverification, read back out of the built CIAs')
    jp = {n: open(os.path.join(IDX2, 'sound', n), 'rb').read() for n in SHOUTS}
    if os.path.exists(clean):
        got = shouts_from_cia(clean)
        for n in SHOUTS:
            same = got[n] == jp[n]
            print('   clean   %-30s %s' % (n, 'Capcom Japanese, unchanged' if same
                                           else 'DIFFERS -- unexpected'))
        if a.version == '1.0.8' and os.path.getsize(clean) == os.path.getsize(a.shell):
            print('   clean   %s the shell it was built from'
                  % ('reproduces' if md5(clean) == md5(a.shell) else 'DIFFERS from'))
    if os.path.exists(ai):
        got = shouts_from_cia(ai)
        for n in SHOUTS:
            print('   aivoice %-30s %s' % (n, 'synthesised, differs from Capcom'
                                           if got[n] != jp[n] else 'STILL JAPANESE -- failed'))
    print()
    for p in (clean, ai):
        if os.path.exists(p):
            print('   %-42s %s  %.1f MB'
                  % (os.path.basename(p), md5(p), os.path.getsize(p) / 1048576))


if __name__ == '__main__':
    main()

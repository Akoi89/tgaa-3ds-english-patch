# -*- coding: utf-8 -*-
"""Extract the romfs of every shipped CIA, so an audit reads the BUILD.

This project has been bitten by auditing a working tree that had drifted from
the build (see the memory note, and the rc19 drift found this week). Anything
that claims a clip is or is not shipped has to read the CIA.

Base-game updates are NoCrypto NCCH -- the romfs sits in the clear and 3dstool
takes it straight off with -xtf cxi. DLC contents are encrypted CFA and need
the -xtf cfa path first, exactly as build.py does in reverse.

    python extract_shipped.py            extract all four, skipping any done
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))

from cia import Cia

TOOL = os.path.join(ROOT, '3dstool', '3dstool.exe')
OUT = os.path.join(HERE, '_shipped')
BUILDS = [
    ('TGAA1-base-1.0.19', 'Final/_new/TGAA1-base-1.0.19.cia'),
    ('TGAA2-base-1.0.13', 'Final/_new/TGAA2-base-1.0.13.cia'),
    ('TGAA1-DLC-1.0.9', 'Final/_new/TGAA1-DLC-1.0.9.cia'),
    ('TGAA2-DLC-1.0.7', 'Final/_new/TGAA2-DLC-1.0.7.cia'),
]


def run(*args):
    return subprocess.run([TOOL] + list(args), capture_output=True, text=True)


def extract(name, cia_path):
    dest = os.path.join(OUT, name)
    if os.path.isdir(dest) and os.listdir(dest):
        print('%-20s already extracted' % name)
        return
    c = Cia(cia_path)
    print('%-20s %d contents' % (name, c.count))
    for i, blob in enumerate(c.contents):
        tmp = os.path.join(OUT, '_tmp_%s_%d.ncch' % (name, i))
        romfs = os.path.join(OUT, '_tmp_%s_%d.romfs' % (name, i))
        tree = os.path.join(dest, 'content%d' % i)
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        open(tmp, 'wb').write(blob)
        # 3dstool needs somewhere to put the header or it extracts nothing --
        # silently, with exit 0, which is why this looked like empty content.
        hdr = os.path.join(OUT, '_tmp_%s_%d.hdr' % (name, i))
        ok = False
        for kind in ('cfa', 'cxi'):
            run('-xtf', kind, tmp, '--header', hdr, '--romfs', romfs)
            if os.path.exists(romfs) and os.path.getsize(romfs):
                ok = True
                break
        if not ok:
            print('   content %-2d no romfs (code-only or unreadable)' % i)
            for p in (tmp, romfs, hdr):
                if os.path.exists(p):
                    os.remove(p)
            continue
        # 3dstool will not create the output directory itself; it exits 0
        # and writes nothing, which is how this first looked like empty content.
        os.makedirs(tree, exist_ok=True)
        run('-xtf', 'romfs', romfs, '--romfs-dir', tree)
        n = sum(len(f) for _, _, f in os.walk(tree))
        print('   content %-2d %6d files -> %s'
              % (i, n, os.path.relpath(tree, HERE)))
        for p in (tmp, romfs, hdr):
            if os.path.exists(p):
                os.remove(p)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, rel in BUILDS:
        p = os.path.join(ROOT, *rel.split('/'))
        if not os.path.exists(p):
            print('%-20s MISSING %s' % (name, rel))
            continue
        extract(name, p)


if __name__ == '__main__':
    main()

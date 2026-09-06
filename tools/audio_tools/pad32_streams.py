# -*- coding: utf-8 -*-
"""Append Capcom's zero trailer to every replaced voice stream so the file is a 32-byte multiple.

Found 2026-09-06 from the user's own 3DS recording: the click sits exactly at the end of our
stream. Every Capcom .mca (234 checked, DLC and base) ends in a zero trailer that pads the
total length to a multiple of 32 bytes (104-byte header + 64-aligned data + 24). Every stream
we or senyarom wrote is 8 mod 32 with no trailer. A console reading in 32-byte units takes
24 bytes of whatever follows the file and decodes them as the last frames. Azahar reads exact
sizes and never hears it. This tool changes NOTHING but the trailer: header, sample count,
data bytes are untouched.

    python pad32_streams.py <src_tree> <work_tree> [<jp_tree>]
        copies src_tree to work_tree; every MADP stream (loose .mca or archive entry) that is
        not 32-aligned gets zero bytes appended up to the next multiple of 32. If jp_tree is
        given, streams byte-identical to their Japanese counterpart are reported, not touched
        (they are already aligned anyway).
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', os.path.join(ROOT, '..', 'dlc_icons', 'tgaa2-en-patch')))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.arc import parse_arc, build_arc_bytes


def pad32(d):
    return d + bytes((-len(d)) % 32)


def main():
    src, work = sys.argv[1], sys.argv[2]
    jp = sys.argv[3] if len(sys.argv) > 3 else None
    if os.path.isdir(work):
        shutil.rmtree(work)
    shutil.copytree(src, work)
    jpmd5 = {}
    if jp:
        for dp, _, fs in os.walk(jp):
            for fn in fs:
                p = os.path.join(dp, fn)
                if fn.endswith('.mca'):
                    jpmd5['LOOSE ' + fn] = hashlib.md5(open(p, 'rb').read()).digest()
                elif fn.endswith('.arc'):
                    try:
                        for e in parse_arc(open(p, 'rb').read())['entries']:
                            if e.data[:4] == b'MADP':
                                jpmd5[fn + '::' + e.name] = hashlib.md5(e.data).digest()
                    except Exception:
                        pass
    n_pad = n_same = n_ok = 0
    for dp, _, fs in os.walk(work):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            if fn.endswith('.mca'):
                d = open(p, 'rb').read()
                if d[:4] != b'MADP':
                    continue
                if jpmd5.get('LOOSE ' + fn) == hashlib.md5(d).digest():
                    n_same += 1
                    continue
                if len(d) % 32 == 0:
                    n_ok += 1
                    continue
                open(p, 'wb').write(pad32(d))
                n_pad += 1
                print('  padded %-70s %6d -> %6d' % (os.path.relpath(p, work), len(d), len(pad32(d))))
            elif fn.endswith('.arc'):
                blob = open(p, 'rb').read()
                try:
                    a = parse_arc(blob)
                except Exception:
                    continue
                assert build_arc_bytes(a) == blob, 'arc null test failed ' + p
                repl = {}
                for e in a['entries']:
                    if e.data[:4] != b'MADP':
                        continue
                    if jpmd5.get(fn + '::' + e.name) == hashlib.md5(e.data).digest():
                        n_same += 1
                        continue
                    if len(e.data) % 32 == 0:
                        n_ok += 1
                        continue
                    repl[e.name] = pad32(e.data)
                    n_pad += 1
                if repl:
                    open(p, 'wb').write(build_arc_bytes(a, repl))
                    print('  padded %-70s %d entries' % (os.path.relpath(p, work), len(repl)))
    print('%d streams padded, %d already aligned, %d identical to Capcom (untouched)' % (n_pad, n_ok, n_same))


if __name__ == '__main__':
    main()

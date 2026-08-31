# -*- coding: utf-8 -*-
"""Keep the DLC's .stqr sound tables in step with rebuilt .mca files.

An .stqr duplicates each stream's size and sample count. Replacing a .mca
without updating its entry leaves the game asking for the old byte count, and
the track plays as silence -- which is exactly what happened in DLC v33.

Layout, read off aoc00_voice.stqr and checked against every other one:
    0x00 'STQR'  0x04 u32 version(4)  0x08 u32 count  0x0C u32 count
    0x10 u32 entry table offset (0x18)  0x14 u32 ...
    entries of 36 bytes from the table offset:
        +0x00 u32 name offset (NUL-terminated string later in the file)
        +0x04 u32 file size          <- must match the .mca on disk
        +0x08 u32 sample count       <- must match the .mca header
        +0x0C u32 channels
        +0x10 u32 sample rate
        +0x14 u32 loop start   +0x18 u32 loop end
        +0x1C u32 name hash    +0x20 u32 flags
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import mca

ENTRY = 36


def parse(blob):
    assert blob[:4] == b'STQR', blob[:4]
    ver, count = struct.unpack_from('<II', blob, 4)
    table = struct.unpack_from('<I', blob, 0x10)[0]
    out = []
    for i in range(count):
        o = table + i * ENTRY
        noff, size, samples, ch, rate = struct.unpack_from('<5I', blob, o)
        end = blob.index(b'\x00', noff)
        name = blob[noff:end].decode('ascii', 'replace')
        out.append({'off': o, 'name': name, 'size': size,
                    'samples': samples, 'channels': ch, 'rate': rate})
    return ver, count, out


def sync(stqr_path, sound_dir, apply=False):
    blob = bytearray(open(stqr_path, 'rb').read())
    ver, count, entries = parse(bytes(blob))
    changed = 0
    for e in entries:
        base = e['name'].replace('\\', '/').split('/')[-1]
        mpath = os.path.join(sound_dir, base + '.mca')
        if not os.path.exists(mpath):
            continue
        h = mca.parse(mpath)
        actual = os.path.getsize(mpath)
        if e['size'] == actual and e['samples'] == h['samples']:
            continue
        print('    %-22s size %d->%d  samples %d->%d'
              % (base, e['size'], actual, e['samples'], h['samples']))
        if h['rate'] != e['rate']:
            print('      !! rate mismatch %d vs %d' % (h['rate'], e['rate']))
        struct.pack_into('<I', blob, e['off'] + 0x04, actual)
        struct.pack_into('<I', blob, e['off'] + 0x08, h['samples'])
        changed += 1
    if changed and apply:
        open(stqr_path, 'wb').write(bytes(blob))
        # read back and prove every entry now matches the file on disk
        _, _, back = parse(open(stqr_path, 'rb').read())
        for e in back:
            base = e['name'].replace('\\', '/').split('/')[-1]
            mpath = os.path.join(sound_dir, base + '.mca')
            if os.path.exists(mpath):
                h = mca.parse(mpath)
                assert e['size'] == os.path.getsize(mpath), base
                assert e['samples'] == h['samples'], base
    return changed


def main(root, apply=False):
    total = 0
    for dp, dn, fn in os.walk(root):
        for f in sorted(fn):
            if not f.endswith('.stqr'):
                continue
            p = os.path.join(dp, f)
            n = sync(p, dp, apply)
            if n:
                print('  %s: %d entries updated' % (os.path.relpath(p, root), n))
                total += n
    print('\n%d entries updated%s'
          % (total, '' if apply else '  (dry run -- pass --apply)'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--apply' in sys.argv))

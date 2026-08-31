# -*- coding: utf-8 -*-
"""Swap one DLC content into Azahar's installed title and fix the TMD.

Testing a DLC change by rebuilding and reinstalling a 311 MB CIA costs minutes
per attempt; swapping the single .app costs seconds. Azahar validates the
content against the installed TMD, so a content whose SIZE changed needs the
chunk record and both hash-chain hashes rewritten -- otherwise the title stops
loading and it looks like the audio change broke the game.

    python swap_content.py <title_id_low> <content_id_hex> <new.ncch>
    python swap_content.py 0014ad00 00000013 bounce/rev/f04.ncch

Keeps a .bak of whatever it replaces, next to the file.
"""
import hashlib
import os
import shutil
import struct
import sys

SD = os.path.join(os.environ['APPDATA'], 'AzaharPlus', 'sdmc', 'Nintendo 3DS',
                  '0' * 32, '0' * 32, 'title', '0004008c')


def main(title_low, cid, src):
    content_dir = os.path.join(SD, title_low, 'content')
    if not os.path.isdir(content_dir):
        sys.exit('no installed content at %s' % content_dir)

    tmd_path = next(os.path.join(content_dir, f)
                    for f in sorted(os.listdir(content_dir)) if f.endswith('.tmd'))
    app_path = os.path.join(content_dir, '%s.app' % cid)
    blob = open(src, 'rb').read()
    want = int(cid, 16)

    d = bytearray(open(tmd_path, 'rb').read())
    info, outer, chunks = 0x204, 0x1E4, 0xB04
    count = struct.unpack_from('>H', d, info + 2)[0]

    for i in range(count):
        r = chunks + i * 0x30
        if struct.unpack_from('>I', d, r)[0] != want:
            continue
        old = struct.unpack_from('>Q', d, r + 8)[0]
        struct.pack_into('>Q', d, r + 8, len(blob))
        d[r + 16:r + 48] = hashlib.sha256(blob).digest()
        print('content %s: %d -> %d bytes' % (cid, old, len(blob)))
        break
    else:
        sys.exit('content id %s not in the installed TMD' % cid)

    d[info + 4:info + 36] = hashlib.sha256(bytes(d[chunks:chunks + count * 0x30])).digest()
    d[outer:outer + 32] = hashlib.sha256(bytes(d[info:info + 64 * 36])).digest()

    for p in (app_path, tmd_path):
        if os.path.exists(p) and not os.path.exists(p + '.bak'):
            shutil.copy2(p, p + '.bak')
            print('backed up %s' % os.path.basename(p))

    shutil.copy2(src, app_path)
    open(tmd_path, 'wb').write(bytes(d))
    print('installed %s and updated %s' % (os.path.basename(app_path),
                                           os.path.basename(tmd_path)))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])

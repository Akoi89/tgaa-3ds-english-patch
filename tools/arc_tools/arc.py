# -*- coding: utf-8 -*-
"""Minimal MT-Framework .arc reader (3DS, little-endian).

Layout: 'ARC\0' | u16 version | u16 count | u32 pad
        then `count` entries of 80 bytes:
          char[64] name (no extension)
          u32 ext_hash
          u32 comp_size
          u32 decomp_size_and_flags   (low 29 bits = size)
          u32 offset
        payloads are zlib streams.
"""
import struct, zlib, os, sys

def entries(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'ARC\x00', 'not an arc: %r' % d[:4]
    ver, count = struct.unpack_from('<HH', d, 4)
    HDR = 12
    out = []
    for i in range(count):
        o = HDR + i * 80
        name = d[o:o+64].split(b'\x00')[0].decode('ascii', 'replace')
        ehash, csize, dsize, off = struct.unpack_from('<IIII', d, o+64)
        out.append({'i': i, 'name': name, 'hash': ehash,
                    'csize': csize, 'dsize': dsize & 0x1FFFFFFF,
                    'off': off, 'raw': d[off:off+csize]})
    return ver, count, out, d

def decomp(e):
    try:
        return zlib.decompress(e['raw'])
    except Exception:
        return e['raw']

if __name__ == '__main__':
    p = sys.argv[1]
    ver, count, es, _ = entries(p)
    print('%s  version=%d  entries=%d' % (os.path.basename(p), ver, count))
    for e in es:
        print(('  %-52s %8d -> %8d  hash=%08x' % (e['name'], e['csize'], e['dsize'], e['hash'])).encode('ascii','replace').decode())


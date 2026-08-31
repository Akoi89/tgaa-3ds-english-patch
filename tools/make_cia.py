# -*- coding: utf-8 -*-
"""Wrap a patched .cxi (our .app files) back into an installable CIA.

Takes an existing CIA of the SAME title as a shell, replaces its single
content with the new .cxi, and rebuilds the TMD hash chain so the 3DS and
Azahar both accept it. Handles a content that changed size.

    python make_cia.py <shell.cia> <new.cxi> <out.cia>

Hash chain, for reference:
    chunk record i : tmd+0xB04 + i*0x30   -> +4 id(u16BE) +8 size(u64BE) +16 sha256
    content info   : tmd+0x204            -> +2 count(u16BE) +4 sha256 over chunks
    outer hash     : tmd+0x1E4            -> sha256 over 64*0x36 bytes of info
    CIA header     : +24 total content size (u64LE)
"""
import hashlib
import struct
import sys
from pathlib import Path


def align64(x):
    return (x + 63) // 64 * 64


def build(shell_path, cxi_path, out_path):
    d = bytearray(Path(shell_path).read_bytes())
    new = Path(cxi_path).read_bytes()

    hdr, cert, tik, tmd, meta = (
        struct.unpack_from('<I', d, o)[0] for o in (0, 8, 12, 16, 20)
    )
    old_total = struct.unpack_from('<Q', d, 24)[0]
    tmd_off = align64(hdr) + align64(cert) + align64(tik)
    coff = tmd_off + align64(tmd)
    info = tmd_off + 0x204
    outer = tmd_off + 0x1E4
    chunks = tmd_off + 0xB04
    count = struct.unpack('>H', d[info + 2:info + 4])[0]
    if count != 1:
        raise SystemExit('shell has %d contents; this helper handles single-content titles' % count)

    old_size = struct.unpack('>Q', d[chunks + 8:chunks + 16])[0]
    content_end = coff + old_size
    trailer = bytes(d[content_end:])          # meta region, carried verbatim
    if len(trailer) != meta:
        raise SystemExit('meta region is %d bytes, header says %d' % (len(trailer), meta))

    # chunk record: size + sha256 of the new content
    struct.pack_into('>Q', d, chunks + 8, len(new))
    d[chunks + 16:chunks + 48] = hashlib.sha256(new).digest()
    # content-info record hashes the chunk table, outer hash covers the info block
    d[info + 4:info + 36] = hashlib.sha256(bytes(d[chunks:chunks + count * 0x30])).digest()
    d[outer:outer + 32] = hashlib.sha256(bytes(d[info:info + 64 * 36])).digest()
    # CIA header carries the total content size
    struct.pack_into('<Q', d, 24, old_total - old_size + len(new))

    out = bytes(d[:coff]) + new + trailer
    Path(out_path).write_bytes(out)

    # verify what we just wrote, rather than trusting the arithmetic
    v = Path(out_path).read_bytes()
    size = struct.unpack('>Q', v[chunks + 8:chunks + 16])[0]
    checks = {
        'content bytes': v[coff:coff + len(new)] == new,
        'content size': size == len(new),
        'content hash': hashlib.sha256(v[coff:coff + size]).digest() == v[chunks + 16:chunks + 48],
        'chunk-group hash': v[info + 4:info + 36] == hashlib.sha256(v[chunks:chunks + count * 0x30]).digest(),
        'outer hash': v[outer:outer + 32] == hashlib.sha256(v[info:info + 64 * 36]).digest(),
        'header size field': struct.unpack('<Q', v[24:32])[0] == old_total - old_size + len(new),
        'meta carried': v[coff + size:] == trailer,
    }
    for k, ok in checks.items():
        print('    %-18s %s' % (k, 'OK' if ok else 'FAILED'))
    if not all(checks.values()):
        raise SystemExit('verification failed; output not trustworthy')
    print('    wrote %s (%d bytes)' % (out_path, len(v)))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    build(*sys.argv[1:])

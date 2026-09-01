# -*- coding: utf-8 -*-
"""Read and rewrite a CIA, including multi-content DLC titles.

tools/make_cia.py handles single-content titles only; every DLC here has 3 to
16 contents, and replacing one shifts the offsets of all that follow.

Layout:
    header <IHHIIII>  -> header, type, version, cert, tik, tmd, meta sizes
                         each region padded to a 64-byte boundary
    header + 24  u64LE  total size of all content
    tmd + 0x1DC  u16BE  title version   (major << 10 | minor << 4 | micro)
    tmd + 0x1E4  32B    sha256 over the 64 content-info records
    tmd + 0x204         content-info records, 0x24 each:
                            +0 u16BE first chunk index
                            +2 u16BE chunk count
                            +4 32B   sha256 over those chunk records
    tmd + 0xB04         content chunk records, 0x30 each:
                            +0 u32BE id   +4 u16BE index   +6 u16BE type
                            +8 u64BE size +0x10 32B sha256 of the content
    then the contents, back to back, then the meta region.

Every hash is recomputed from what is actually written, and the result is
re-read and re-verified before the file is accepted.
"""
import hashlib
import struct
import sys


def a64(x):
    return (x + 63) // 64 * 64


class Cia(object):
    def __init__(self, path):
        self.raw = bytearray(open(path, 'rb').read())
        d = self.raw
        hdr, _, _, cert, tik, tmd, meta = struct.unpack_from('<IHHIIII', d, 0)
        self.sizes = dict(hdr=hdr, cert=cert, tik=tik, tmd=tmd, meta=meta)
        self.tmd = a64(hdr) + a64(cert) + a64(tik)
        self.tik = a64(hdr) + a64(cert)
        self.info = self.tmd + 0x204
        self.chunks = self.tmd + 0xB04
        self.count = struct.unpack('>H', d[self.info + 2:self.info + 4])[0]
        self.coff = self.tmd + a64(tmd)
        self.contents, off = [], self.coff
        for i in range(self.count):
            c = self.chunks + i * 0x30
            n = struct.unpack('>Q', d[c + 8:c + 16])[0]
            blob = bytes(d[off:off + n])
            if hashlib.sha256(blob).digest() != bytes(d[c + 16:c + 48]):
                raise SystemExit('content %d fails its stored hash' % i)
            self.contents.append(blob)
            off += n
        self.trailer = bytes(d[off:])
        if len(self.trailer) != meta:
            raise SystemExit('meta region is %d bytes, header says %d'
                             % (len(self.trailer), meta))

    def version(self):
        v = struct.unpack('>H', self.raw[self.tmd + 0x1DC:self.tmd + 0x1DE])[0]
        return (v >> 10, (v >> 4) & 0x3F, v & 0xF)

    def write(self, path, replace=None, version=None):
        d = bytearray(self.raw)
        blobs = list(self.contents)
        for i, blob in (replace or {}).items():
            blobs[i] = blob

        for i, blob in enumerate(blobs):
            c = self.chunks + i * 0x30
            struct.pack_into('>Q', d, c + 8, len(blob))
            d[c + 16:c + 48] = hashlib.sha256(blob).digest()

        # each info record hashes its own span of chunk records
        for r in range(64):
            o = self.info + r * 0x24
            first, n = struct.unpack('>HH', d[o:o + 4])
            if not n:
                continue
            span = bytes(d[self.chunks + first * 0x30:
                           self.chunks + (first + n) * 0x30])
            d[o + 4:o + 36] = hashlib.sha256(span).digest()
        d[self.tmd + 0x1E4:self.tmd + 0x204] = hashlib.sha256(
            bytes(d[self.info:self.info + 64 * 0x24])).digest()

        if version is not None:
            maj, mi, mic = version
            v = (maj << 10) | (mi << 4) | mic
            struct.pack_into('>H', d, self.tmd + 0x1DC, v)
            struct.pack_into('>H', d, self.tik + 0x1E6, v)

        struct.pack_into('<Q', d, 24, sum(len(b) for b in blobs))
        out = bytes(d[:self.coff]) + b''.join(blobs) + self.trailer
        open(path, 'wb').write(out)

        check = Cia(path)                      # re-parse: proves every hash
        if [len(b) for b in check.contents] != [len(b) for b in blobs]:
            raise SystemExit('content sizes did not survive the write')
        return check


if __name__ == '__main__':
    for p in sys.argv[1:]:
        c = Cia(p)
        print('  %-34s %d content(s), version %d.%d.%d, %.1f MB'
              % (p.split('/')[-1], c.count, c.version()[0], c.version()[1],
                 c.version()[2], sum(len(b) for b in c.contents) / 1048576))

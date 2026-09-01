# -*- coding: utf-8 -*-
"""Splice a rebuilt romfs into an NCCH (CXI or CFA) and fix its hash chain.

NEVER rebuild a CXI with `3dstool -c -t cxi`. It does not reproduce Nintendo's
layout and the result does not boot. Replace the romfs region in place and
repair only the fields that describe it.

NCCH header fields this touches (all little-endian, offsets from NCCH start):
    0x104  u32  content size            , in media units (1 unit = 0x200)
    0x18F  u8   flags[7]                , bit 2 = NoCrypto
    0x1B0  u32  romfs offset            , media units
    0x1B4  u32  romfs size              , media units
    0x1B8  u32  romfs hash region size  , media units
    0x1E0  32B  sha256 over the first <hash region size> of the romfs

The superblock hash covers only the LEADING hash region, not the whole romfs,
which is what makes an in-place splice possible at all.

Run this module directly to null-test the hash maths against an untouched
NCCH: if the hash computed here does not reproduce the one already stored, the
offsets are wrong and nothing downstream can be trusted.
"""
import hashlib
import struct
import sys

MU = 0x200


def fields(d):
    g = lambda o: struct.unpack_from('<I', d, o)[0]
    return dict(content_size=g(0x104), romfs_off=g(0x1B0), romfs_size=g(0x1B4),
                hash_region=g(0x1B8), stored_hash=bytes(d[0x1E0:0x200]),
                nocrypto=bool(d[0x18F] & 0x04))


def verify(d):
    """Does the stored superblock hash match the romfs actually present?"""
    f = fields(d)
    if not f['romfs_off']:
        return None
    start = f['romfs_off'] * MU
    region = d[start:start + f['hash_region'] * MU]
    return hashlib.sha256(region).digest() == f['stored_hash'], f


def splice(ncch, new_romfs):
    """Return a new NCCH carrying new_romfs, with its hash chain repaired."""
    d = bytearray(ncch)
    f = fields(d)
    if not f['romfs_off']:
        raise SystemExit('this NCCH has no romfs')
    start = f['romfs_off'] * MU
    tail_start = start + f['romfs_size'] * MU
    tail = bytes(d[tail_start:])            # anything after the romfs, kept

    body = bytearray(new_romfs)
    if len(body) % MU:
        body += b'\0' * (MU - len(body) % MU)

    out = bytearray(d[:start]) + body + tail
    size_mu = len(body) // MU
    struct.pack_into('<I', out, 0x1B4, size_mu)
    struct.pack_into('<I', out, 0x104,
                     f['content_size'] - f['romfs_size'] + size_mu)
    region = bytes(out[start:start + f['hash_region'] * MU])
    out[0x1E0:0x200] = hashlib.sha256(region).digest()

    ok, _ = verify(bytes(out))
    if not ok:
        raise SystemExit('spliced NCCH fails its own hash check')
    return bytes(out)


if __name__ == '__main__':
    for path in sys.argv[1:]:
        d = open(path, 'rb').read()
        r = verify(d)
        if r is None:
            print('  %-30s no romfs' % path)
            continue
        ok, f = r
        print('  %-30s hash %s | romfs %d MU at %d | hash region %d MU | nocrypto %s'
              % (path.split('/')[-1], 'MATCHES' if ok else 'MISMATCH',
                 f['romfs_size'], f['romfs_off'], f['hash_region'], f['nocrypto']))

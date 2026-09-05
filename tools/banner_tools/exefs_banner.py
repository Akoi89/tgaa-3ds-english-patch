"""Replace the ExeFS banner inside partition 0 of a decrypted CCI, keeping the
ExeFS region the same size so nothing else in the NCCH or CCI moves.

ExeFS: 0x200 header = 10 entries (name[8], u32 offset, u32 size) + 10 SHA-256
hashes stored in REVERSE order at 0xC0 (entry i at 0xC0 + (9-i)*0x20); file
data starts at header + 0x200. NCCH: exefs offset 0x1A0, size 0x1A4, hash
region 0x1A8 (media units of 0x200); exefs superblock hash at 0x1C0 = sha256
of the first <hash region> of the ExeFS.

    python exefs_banner.py <in.cci> <banner.bin> <out.cci>
"""
import hashlib, struct, sys

MU = 0x200
P0 = 0x4000            # partition 0 offset in the CCI (checked against the NCSD table)


def main(src, banner, out):
    d = bytearray(open(src, 'rb').read()); ban = open(banner, 'rb').read()
    p0 = struct.unpack_from('<I', d, 0x120)[0] * MU; assert p0 == P0, hex(p0)
    g = lambda o: struct.unpack_from('<I', d, P0 + o)[0]
    ex_off, ex_size, ex_hreg = g(0x1A0) * MU, g(0x1A4) * MU, g(0x1A8) * MU
    base = P0 + ex_off
    ents = []
    for i in range(10):
        name = bytes(d[base + i * 16:base + i * 16 + 8]).rstrip(b'\0'); off, size = struct.unpack_from('<II', d, base + i * 16 + 8)
        if name: ents.append([i, name, off, size])
    files = {n: bytes(d[base + 0x200 + o:base + 0x200 + o + s]) for i, n, o, s in ents}
    old = files[b'banner']; files[b'banner'] = ban
    # repack in the original order, each file 0x200-aligned as the original was
    pos = 0; region = bytearray(); new_ents = []
    for i, n, o, s in ents:
        f = files[n]; new_ents.append((i, n, pos, len(f))); region += f; pad = (-len(f)) % MU; region += b'\0' * pad; pos += len(f) + pad
    assert 0x200 + len(region) <= ex_size, ('ExeFS would grow: %d > %d' % (0x200 + len(region), ex_size))
    hdr = bytearray(0x200)
    for i, n, o, s in new_ents:
        hdr[i * 16:i * 16 + 8] = n.ljust(8, b'\0'); struct.pack_into('<II', hdr, i * 16 + 8, o, s)
        hdr[0xC0 + (9 - i) * 0x20:0xC0 + (9 - i) * 0x20 + 32] = hashlib.sha256(files[n]).digest()
    region = bytes(hdr) + bytes(region); region += b'\0' * (ex_size - len(region))
    d[base:base + ex_size] = region
    d[P0 + 0x1C0:P0 + 0x1E0] = hashlib.sha256(region[:ex_hreg]).digest()
    open(out, 'wb').write(d)
    # verify
    chk = hashlib.sha256(bytes(d[base:base + ex_hreg])).digest() == bytes(d[P0 + 0x1C0:P0 + 0x1E0])
    print('banner %d -> %d bytes; ExeFS size kept at %d; superblock hash re-verifies: %s; wrote %s' % (len(old), len(ban), ex_size, chk, out))


if __name__ == '__main__':
    main(*sys.argv[1:4])

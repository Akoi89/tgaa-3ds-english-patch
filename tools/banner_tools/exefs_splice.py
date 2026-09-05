"""Generalised exefs_banner.py: replace any ExeFS files inside partition 0 of a
decrypted CCI, keeping the ExeFS region the same size so nothing else moves.

    python exefs_splice.py <in.cci> <out.cci> banner=<file> [icon=<file>] ...

Repairs the ExeFS header (entries + reverse-order file hashes at 0xC0) and the
NCCH ExeFS superblock hash at 0x1C0. Refuses if the files would not fit.
"""
import hashlib, struct, sys

MU = 0x200
P0 = 0x4000


def main(src, out, repl):
    d = bytearray(open(src, 'rb').read())
    p0 = struct.unpack_from('<I', d, 0x120)[0] * MU; assert p0 == P0, hex(p0)
    g = lambda o: struct.unpack_from('<I', d, P0 + o)[0]
    ex_off, ex_size, ex_hreg = g(0x1A0) * MU, g(0x1A4) * MU, g(0x1A8) * MU
    base = P0 + ex_off
    ents = []
    for i in range(10):
        name = bytes(d[base + i * 16:base + i * 16 + 8]).rstrip(b'\0'); off, size = struct.unpack_from('<II', d, base + i * 16 + 8)
        if name: ents.append([i, name, off, size])
    files = {n: bytes(d[base + 0x200 + o:base + 0x200 + o + s]) for i, n, o, s in ents}
    for n, path in repl.items():
        assert n in files, 'no ExeFS file %r (have %s)' % (n, list(files))
        new = open(path, 'rb').read(); print('%s: %d -> %d bytes' % (n.decode(), len(files[n]), len(new))); files[n] = new
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
    chk = hashlib.sha256(bytes(d[base:base + ex_hreg])).digest() == bytes(d[P0 + 0x1C0:P0 + 0x1E0])
    print('ExeFS size kept at %d; superblock hash re-verifies: %s; wrote %s' % (ex_size, chk, out))


if __name__ == '__main__':
    repl = {}
    for a in sys.argv[3:]:
        k, v = a.split('=', 1); repl[k.encode()] = v
    main(sys.argv[1], sys.argv[2], repl)

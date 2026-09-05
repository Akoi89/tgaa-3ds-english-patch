# -*- coding: utf-8 -*-
"""Put the cartridge's HOME menu icon picture into an update CIA, keeping the update's
English titles.

    python swap_home_icon.py <cartridge.cci> <update.cia> <out.cia>

The icon (SMDH) lives twice: in content 0's ExeFS (what the console and Azahar show
once installed) and in the CIA's meta block (what installers show). Both get the
cartridge's 24x24 and 48x48 pictures; the 16 title records and the settings block
stay the update's own. Hash chain repaired: ExeFS per-file hash in the ExeFS header,
NCCH ExeFS superblock hash at 0x1C0 over the header's hash region, then the CIA/TMD
chain via cia.Cia.write. The result is re-read and checked before it is accepted.
"""
import hashlib
import os
import struct
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cia import Cia   # noqa: E402

MU = 0x200
SMALL, SMALL_LEN = 0x2040, 24 * 24 * 2
LARGE, LARGE_LEN = 0x24C0, 48 * 48 * 2


def cci_exefs_icon(path):
    d = open(path, 'rb').read()
    poff = struct.unpack_from('<I', d, 0x120)[0] * MU
    ncch = d[poff:poff + MU]
    assert ncch[0x100:0x104] == b'NCCH' and ncch[0x18F] & 4, 'cartridge partition 0 is not NoCrypto'
    exo = struct.unpack_from('<I', ncch, 0x1A0)[0] * MU
    ex = d[poff + exo:poff + exo + 0x200]
    for i in range(10):
        name = ex[i * 16:i * 16 + 8].split(b'\0')[0]
        o, s = struct.unpack_from('<II', ex, i * 16 + 8)
        if name == b'icon':
            return d[poff + exo + 0x200 + o:poff + exo + 0x200 + o + s]
    raise SystemExit('no icon in cartridge ExeFS')


def patch_smdh(smdh, pictures):
    s = bytearray(smdh)
    assert s[:4] == b'SMDH'
    s[SMALL:SMALL + SMALL_LEN] = pictures[SMALL:SMALL + SMALL_LEN]
    s[LARGE:LARGE + LARGE_LEN] = pictures[LARGE:LARGE + LARGE_LEN]
    return bytes(s)


def patch_ncch_icon(ncch, pictures):
    d = bytearray(ncch)
    assert d[0x100:0x104] == b'NCCH' and d[0x18F] & 4, 'update content is not NoCrypto'
    exo = struct.unpack_from('<I', d, 0x1A0)[0] * MU
    hreg = struct.unpack_from('<I', d, 0x1A8)[0] * MU
    hdr = d[exo:exo + 0x200]
    for i in range(10):
        name = hdr[i * 16:i * 16 + 8].split(b'\0')[0]
        o, s = struct.unpack_from('<II', hdr, i * 16 + 8)
        if name == b'icon':
            start = exo + 0x200 + o
            new = patch_smdh(bytes(d[start:start + s]), pictures)
            d[start:start + s] = new
            # per-file hashes sit at the END of the header, file 0 last: 0x200 - (i+1)*0x20
            hpos = exo + 0x200 - (i + 1) * 0x20
            d[hpos:hpos + 0x20] = hashlib.sha256(new).digest()
            break
    else:
        raise SystemExit('no icon in update ExeFS')
    d[0x1C0:0x1E0] = hashlib.sha256(bytes(d[exo:exo + hreg])).digest()
    return bytes(d)


def read_icon(ncch):
    exo = struct.unpack_from('<I', ncch, 0x1A0)[0] * MU
    hdr = ncch[exo:exo + 0x200]
    for i in range(10):
        name = hdr[i * 16:i * 16 + 8].split(b'\0')[0]
        o, s = struct.unpack_from('<II', hdr, i * 16 + 8)
        if name == b'icon':
            blob = ncch[exo + 0x200 + o:exo + 0x200 + o + s]
            ok_file = hashlib.sha256(blob).digest() == hdr[0x200 - (i + 1) * 0x20:0x200 - i * 0x20]
            hreg = struct.unpack_from('<I', ncch, 0x1A8)[0] * MU
            ok_sb = hashlib.sha256(ncch[exo:exo + hreg]).digest() == ncch[0x1C0:0x1E0]
            return blob, ok_file, ok_sb


def main():
    cci, src, out = sys.argv[1:4]
    pictures = cci_exefs_icon(cci)
    c = Cia(src)
    new0 = patch_ncch_icon(c.contents[0], pictures)
    # meta block: SMDH sits after the 0x400-byte meta header
    raw = bytearray(c.raw)
    mo = len(raw) - len(c.trailer)
    i = c.trailer.find(b'SMDH')
    if i >= 0:
        raw[mo + i:mo + i + len(c.trailer) - i] = patch_smdh(c.trailer[i:], pictures)
        c.raw = bytes(raw)
    c.write(out, replace={0: new0})

    v = Cia(out)
    blob, ok_file, ok_sb = read_icon(v.contents[0])
    same_pic = blob[LARGE:LARGE + LARGE_LEN] == pictures[LARGE:LARGE + LARGE_LEN]
    title_en = blob[8 + 0x200 + 0x80:8 + 0x200 + 0x180].decode('utf-16le', 'replace').rstrip('\0')
    print('%s: version %s, exefs file hash %s, exefs superblock hash %s, picture is the cartridge one: %s'
          % (os.path.basename(out), v.version(), 'OK' if ok_file else 'BAD', 'OK' if ok_sb else 'BAD', same_pic))
    print('English long title kept: %r' % title_en.replace('\n', ' / '))
    if not (ok_file and ok_sb and same_pic):
        os.remove(out)
        raise SystemExit('verification failed, output removed')


if __name__ == '__main__':
    main()

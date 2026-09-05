"""Copy the 12 SMDH title/description/publisher slots from one SMDH (our update's
CIA meta or icon.bin) into a base icon.bin, keeping the base's settings and
pictures byte-identical. Output is the same 14016-byte SMDH.

    python patch_icon_strings.py <base icon.bin> <source: .cia or icon.bin> <out icon.bin>
"""
import struct, sys


def smdh_from(path):
    d = open(path, 'rb').read()
    if d[:4] == b'SMDH':
        return d
    hdr, typ, ver, cert, tik, tmd, meta = struct.unpack_from('<IHHIIII', d, 0)
    assert meta, 'CIA has no meta region'
    s = d[len(d) - meta + 0x400:]
    assert s[:4] == b'SMDH'
    return s[:14016]


def main(base, src, out):
    b = bytearray(open(base, 'rb').read()); s = smdh_from(src)
    assert b[:4] == b'SMDH' and len(b) == 14016
    b[8:8 + 12 * 0x200] = s[8:8 + 12 * 0x200]
    open(out, 'wb').write(b)
    langs = ['JP', 'EN', 'FR', 'DE', 'IT', 'ES', 'ZH', 'KO', 'NL', 'PT', 'RU', 'TW']
    for i in (0, 1):
        o = 8 + i * 0x200
        print(langs[i], repr(b[o:o + 0x80].decode('utf-16-le').rstrip('\0')), '|', repr(b[o + 0x80:o + 0x180].decode('utf-16-le').rstrip('\0')), '|', repr(b[o + 0x180:o + 0x200].decode('utf-16-le').rstrip('\0')))
    filled = sum(1 for i in range(12) if b[8 + i * 0x200:8 + i * 0x200 + 2] != b'\0\0')
    print('filled slots %d/12; settings+pictures unchanged: %s; wrote %s' % (filled, b[0x1808:] == bytearray(open(base, 'rb').read())[0x1808:], out))


if __name__ == '__main__':
    main(*sys.argv[1:4])

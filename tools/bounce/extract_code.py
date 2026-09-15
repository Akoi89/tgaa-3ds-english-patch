# -*- coding: utf-8 -*-
"""Pull the decompressed .code out of a decrypted (NoCrypto) update CIA.

    python extract_code.py <cia> <out.bin>

CIA -> first content (the update NCCH) -> ExeFS -> .code, then BLZ-decompressed in Python
(3dstool's cxi extraction timed out on this file in earlier sessions).
"""
import struct
import sys


def a64(x):
    return (x + 63) & ~63


def blz_decompress(data):
    """Nintendo bottom-LZ ('BLZ') used for 3DS .code: decompresses backwards from the end."""
    buf_top, header_len = struct.unpack_from('<I', data, len(data) - 8)[0], data[len(data) - 5]
    enc_len = buf_top & 0x00FFFFFF
    inc = struct.unpack_from('<I', data, len(data) - 4)[0]
    header_len = data[len(data) - 5]
    out = bytearray(data) + bytearray(inc)
    src = len(data) - header_len
    dst = len(out)
    stop = len(data) - enc_len
    while src > stop:
        src -= 1
        flags = data[src]
        for _ in range(8):
            if src <= stop:
                break
            if flags & 0x80:
                src -= 2
                pair = data[src] | (data[src + 1] << 8)
                length = (pair >> 12) + 3
                disp = (pair & 0x0FFF) + 3
                for _ in range(length):
                    dst -= 1
                    out[dst] = out[dst + disp]
            else:
                src -= 1
                dst -= 1
                out[dst] = data[src]
            flags = (flags << 1) & 0xFF
    return bytes(out)


def main():
    cia, outp = sys.argv[1], sys.argv[2]
    d = open(cia, 'rb').read()
    hdr, typ, ver, cert, tik, tmd, meta = struct.unpack_from('<IHHIIII', d, 0)
    content_off = a64(hdr) + a64(cert) + a64(tik) + a64(tmd)
    n = d[content_off:]
    assert n[0x100:0x104] == b'NCCH', n[0x100:0x104]
    flags7 = n[0x18F]
    print('NCCH flags7 0x%02x (NoCrypto=%s)' % (flags7, bool(flags7 & 4)))
    exefs_off = struct.unpack_from('<I', n, 0x1A0)[0] * 0x200
    ex = n[exefs_off:]
    for i in range(10):
        name = ex[i * 16:i * 16 + 8].rstrip(b'\0')
        off, sz = struct.unpack_from('<II', ex, i * 16 + 8)
        if name == b'.code':
            raw = ex[0x200 + off:0x200 + off + sz]
            code = blz_decompress(raw)
            open(outp, 'wb').write(code)
            print('.code compressed %d -> %d bytes -> %s' % (sz, len(code), outp))
            return
    raise SystemExit('no .code')


if __name__ == '__main__':
    main()

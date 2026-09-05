"""Sega's COMP container = 'COMP' + a Nintendo LZ11 stream (type byte 0x11).

    decode(blob) -> bytes        raise if the stream is malformed
    encode(data)  -> COMP blob   greedy LZ11, byte-exact re-decode guaranteed
"""
import struct


def lz11_decode(d, off=0):
    if d[off] != 0x11:
        raise ValueError('not LZ11')
    size = struct.unpack_from('<I', d, off)[0] >> 8
    out = bytearray()
    i = off + 4
    while len(out) < size:
        flags = d[i]; i += 1
        for bit in range(7, -1, -1):
            if len(out) >= size:
                break
            if not (flags >> bit) & 1:
                out.append(d[i]); i += 1
                continue
            b0 = d[i]
            ind = b0 >> 4
            if ind == 0:
                ln = (((b0 & 0xF) << 4) | (d[i + 1] >> 4)) + 0x11
                disp = (((d[i + 1] & 0xF) << 8) | d[i + 2]) + 1
                i += 3
            elif ind == 1:
                ln = (((b0 & 0xF) << 12) | (d[i + 1] << 4) | (d[i + 2] >> 4)) + 0x111
                disp = (((d[i + 2] & 0xF) << 8) | d[i + 3]) + 1
                i += 4
            else:
                ln = ind + 1
                disp = (((b0 & 0xF) << 8) | d[i + 1]) + 1
                i += 2
            for _ in range(ln):
                out.append(out[-disp])
    return bytes(out), i


def lz11_encode(data):
    n = len(data)
    out = bytearray(struct.pack('<I', 0x11 | (n << 8)))
    i = 0
    while i < n:
        flags = 0; chunk = bytearray()
        for bit in range(7, -1, -1):
            if i >= n:
                break
            best_len, best_disp = 0, 0
            start = max(0, i - 0x1000)
            # longest match search, bounded for speed
            j = data.rfind(data[i:i + 3], start, i + 2) if i + 3 <= n else -1
            while j != -1 and j >= start:
                ln = 0
                while i + ln < n and ln < 0x10110 and data[j + ln] == data[i + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_disp = ln, i - j
                    if ln >= 0x10110:
                        break
                j = data.rfind(data[i:i + 3], start, j + 2) if j > start else -1
            if best_len >= 3:
                flags |= 1 << bit
                d = best_disp - 1
                if best_len <= 0x10:
                    chunk += bytes((((best_len - 1) << 4) | (d >> 8), d & 0xFF))
                elif best_len <= 0x110:
                    l = best_len - 0x11
                    chunk += bytes(((l >> 4), ((l & 0xF) << 4) | (d >> 8), d & 0xFF))
                else:
                    l = best_len - 0x111
                    chunk += bytes((0x10 | (l >> 12), (l >> 4) & 0xFF, ((l & 0xF) << 4) | (d >> 8), d & 0xFF))
                i += best_len
            else:
                chunk.append(data[i]); i += 1
        out.append(flags); out += chunk
    return bytes(out)


def decode(blob):
    if blob[:4] != b'COMP':
        raise ValueError('not COMP')
    data, end = lz11_decode(blob, 4)
    return data


def encode(data):
    blob = b'COMP' + lz11_encode(data)
    assert decode(blob) == data
    return blob


if __name__ == '__main__':
    import sys, narc
    for p in sys.argv[1:]:
        m = narc.read(p)
        for i, b in enumerate(m['members']):
            if b[:4] == b'COMP':
                d = decode(b)
                print('%s member %d: %d -> %d bytes, starts %s' % (p, i, len(b), len(d), d[:16].hex()))

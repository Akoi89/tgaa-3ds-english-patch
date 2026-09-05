"""Rebuild a 3DS HOME-menu banner (ExeFS banner.bin, CBMD container) with a new
texture in every region's CGFX model.

CBMD: 'CBMD' + u32 0 + 14 x u32 offsets of LZ11-compressed CGFX blobs (index 0
common, then one per region/language; 0 = absent) + u32 CWAV offset at 0x84,
header 0x88 bytes. Inside each CGFX the texture object 'TXOB' stores height
and width at +0x14/+0x18, the PICA format code 11 words after the magic, the
data size 15 words after, and the data pointer 16 words after (relative to
that pointer's own position). The CWAV must start 0x20-aligned or the HOME
menu plays garbage.

    python banner_build.py <orig banner.bin> <texture.png> <out banner.bin>

The PNG must be the same size as the model's texture (find it with
banner_extract.py). Any PICA format is re-encoded as the original's format.
"""
import re, struct, sys
import comp, tex
from PIL import Image


def txob(d, size):
    for o in [m.start() for m in re.finditer(b'TXOB', d)]:
        h, w = struct.unpack_from('<II', d, o + 0x14)
        if (w, h) == size:
            fmt = struct.unpack_from('<I', d, o + 4 + 11 * 4)[0]; n = struct.unpack_from('<I', d, o + 4 + 15 * 4)[0]
            data = o + 4 + 16 * 4 + struct.unpack_from('<I', d, o + 4 + 16 * 4)[0]
            return o, fmt, n, data
    return None


def unlz(raw):
    d = comp.lz11_decode(raw, 0)
    return d[0] if isinstance(d, tuple) else d


def main(src, png, out):
    b = open(src, 'rb').read(); assert b[:4] == b'CBMD'
    offs = list(struct.unpack_from('<14I', b, 8)); cw = struct.unpack_from('<I', b, 0x84)[0]
    img = Image.open(png).convert('RGBA')
    ends = [o for o in offs if o] + [cw]
    chunks = []; k = 0; fmt_used = None
    for i, off in enumerate(offs):
        if not off:
            chunks.append(None); continue
        raw = b[off:ends[k + 1]]; k += 1
        d = bytearray(unlz(raw)); t = txob(d, img.size)
        if t:
            o, fmt, n, data = t; fmt_used = fmt
            enc = tex.encode(img, fmt); assert len(enc) == n, ('encoded size %d != texture size %d' % (len(enc), n))
            d[data:data + n] = enc; chunks.append(comp.lz11_encode(bytes(d)))
        else:
            chunks.append(raw)
    hdr = bytearray(b[:0x88]); pos = 0x88; body = b''
    for i, c in enumerate(chunks):
        if c is None:
            offs[i] = 0; continue
        offs[i] = pos; body += c; pos += len(c)
    pad = (-pos) % 0x20; body += bytes(pad); pos += pad
    struct.pack_into('<14I', hdr, 8, *offs); struct.pack_into('<I', hdr, 0x84, pos)
    new = bytes(hdr) + body + b[cw:]
    open(out, 'wb').write(new)
    ok = 0
    for i, off in enumerate(offs):
        if not off: continue
        nxt = min([o for o in offs if o > off] + [pos]); d = unlz(new[off:nxt]); t = txob(d, img.size)
        if t:
            o, fmt, n, data = t
            ok += tex.decode(d[data:data + n], img.width, img.height, fmt).convert('RGBA').tobytes() == tex.decode(tex.encode(img, fmt), img.width, img.height, fmt).convert('RGBA').tobytes()
    print('wrote %s: %d bytes (was %d), %d models carry the new %dx%d texture (format %s), CWAV at 0x%X (%d bytes, untouched)'
          % (out, len(new), len(b), ok, img.width, img.height, fmt_used, pos, len(b) - cw))


if __name__ == '__main__':
    main(*sys.argv[1:4])

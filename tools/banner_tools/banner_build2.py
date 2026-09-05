"""TGAA variant of banner_build.py: the model has TWO 256x256 textures (ETC1 and
ETC1A4); pick the one with the given format code, and re-encode only the 4x4
blocks whose pixels differ from the original decode so untouched ETC1 bytes stay
byte-identical (keeps the LZ11 size close to the original; the ExeFS has 0 slack).

    python banner_build2.py <orig banner.bin> <texture.png> <out banner.bin> [fmt=13]
"""
import re, struct, sys
import numpy as np
import comp, tex, etc1_enc
from PIL import Image


def txob(d, size, want_fmt):
    for o in [m.start() for m in re.finditer(b'TXOB', d)]:
        h, w = struct.unpack_from('<II', d, o + 0x14)
        if (w, h) == size:
            fmt = struct.unpack_from('<I', d, o + 4 + 11 * 4)[0]
            if fmt != want_fmt: continue
            n = struct.unpack_from('<I', d, o + 4 + 15 * 4)[0]
            data = o + 4 + 16 * 4 + struct.unpack_from('<I', d, o + 4 + 16 * 4)[0]
            return o, fmt, n, data
    return None


def unlz(raw):
    d = comp.lz11_decode(raw, 0)
    return d[0] if isinstance(d, tuple) else d


def main(src, png, out, want_fmt=13):
    b = open(src, 'rb').read(); assert b[:4] == b'CBMD'
    offs = list(struct.unpack_from('<14I', b, 8)); cw = struct.unpack_from('<I', b, 0x84)[0]
    img = Image.open(png).convert('RGBA'); W, H = img.size; new = np.asarray(img)
    ends = [o for o in offs if o] + [cw]
    chunks = []; k = 0; touched = 0
    for i, off in enumerate(offs):
        if not off:
            chunks.append(None); continue
        raw = b[off:ends[k + 1]]; k += 1
        d = bytearray(unlz(raw)); t = txob(d, img.size, want_fmt)
        if t:
            o, fmt, n, data = t
            old = np.asarray(tex.decode(d[data:data + n], W, H, fmt).convert('RGBA'))
            diff = (old != new).any(axis=2)
            # block-level mask (4x4)
            mask = np.zeros((H, W), bool)
            for y in range(0, H, 4):
                for x in range(0, W, 4):
                    if diff[y:y + 4, x:x + 4].any(): mask[y:y + 4, x:x + 4] = True
            touched = int(mask[::4, ::4].sum())
            enc = etc1_enc.encode_rgba(new, bytes(d[data:data + n]), W, H, touch_mask=mask)
            assert len(enc) == n
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
    newb = bytes(hdr) + body + b[cw:]
    open(out, 'wb').write(newb)
    # verify: decode back and compare to what a fresh encode gives
    d = unlz(newb[offs[0]:pos]); o, fmt, n, data = txob(d, img.size, want_fmt)
    back = tex.decode(d[data:data + n], W, H, fmt).convert('RGBA')
    back.save(out + '.decoded.png')
    a = np.asarray(back).astype(int); c_ = new.astype(int)
    print('wrote %s: %d bytes (was %d, model chunk %d -> %d), %d/%d blocks re-encoded, CWAV at 0x%X (mod32=%d); decoded-vs-target mean abs diff RGBA %s'
          % (out, len(newb), len(b), ends[1] - 0x88, offs[0] and (pos - pad - 0x88), touched, (W // 4) * (H // 4), pos, pos % 32,
             [round(float(abs(a[..., i] - c_[..., i]).mean()), 2) for i in range(4)]))


if __name__ == '__main__':
    main(*sys.argv[1:4], *([int(sys.argv[4])] if len(sys.argv) > 4 else []))

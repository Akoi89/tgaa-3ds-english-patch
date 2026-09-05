"""Dump every texture of every model in a CBMD banner.bin, plus CWAV facts.

    python banner_dump_all.py <banner.bin> <outdir>
"""
import os, re, struct, sys
import comp, tex, csar


def unlz(raw):
    d = comp.lz11_decode(raw, 0)
    return d[0] if isinstance(d, tuple) else d


def main(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    b = open(path, 'rb').read(); assert b[:4] == b'CBMD'
    offs = struct.unpack_from('<14I', b, 8); cw = struct.unpack_from('<I', b, 0x84)[0]
    print('file %d bytes, model offsets %s, cwav at 0x%X (mod32=%d)' % (len(b), [hex(o) for o in offs], cw, cw % 32))
    ends = [o for o in offs if o] + [cw]; k = 0
    for i, off in enumerate(offs):
        if not off: continue
        d = unlz(b[off:ends[k + 1]]); k += 1
        open(os.path.join(outdir, 'model%d.cgfx' % i), 'wb').write(d)
        print('model %d: compressed %d -> %d bytes' % (i, ends[k] - off, len(d)))
        for o in [m.start() for m in re.finditer(b'TXOB', d)]:
            h, w = struct.unpack_from('<II', d, o + 0x14)
            if not (8 <= w <= 1024 and 8 <= h <= 1024): continue
            fmt = struct.unpack_from('<I', d, o + 4 + 11 * 4)[0]; n = struct.unpack_from('<I', d, o + 4 + 15 * 4)[0]
            data = o + 4 + 16 * 4 + struct.unpack_from('<I', d, o + 4 + 16 * 4)[0]
            # name: TXOB +0xC? try the name pointer at +0x10 (relative)
            try:
                np_ = o + 0x10 + struct.unpack_from('<I', d, o + 0x10)[0]
                name = d[np_:d.index(b'\0', np_)].decode('ascii', 'replace')
            except Exception:
                name = '?'
            print('  TXOB @0x%X name=%r %dx%d fmt %d (%s) %d bytes, data @0x%X' % (o, name, w, h, fmt, tex.NAMES.get(fmt, '?'), n, data))
            try:
                tex.decode(d[data:data + n], w, h, fmt).convert('RGBA').save(os.path.join(outdir, 'model%d_%s_%dx%d_f%d.png' % (i, re.sub(r'[^\w]', '_', name), w, h, fmt)))
            except Exception as e:
                print('    decode failed:', e)
    w = b[cw:]; info = csar.cwav_info(w)
    io_, isz = info['secs'][0x7000]; nch = struct.unpack_from('<I', w, io_ + 8 + 0x14)[0]
    print('CWAV: enc %d (0=PCM8 1=PCM16 2=ADPCM), %d ch, %d Hz, %.2f s, %d bytes' % (info['enc'], nch, info['rate'], info['samples'] / info['rate'], len(w)))
    open(os.path.join(outdir, 'banner.bcwav'), 'wb').write(w)


if __name__ == '__main__':
    main(*sys.argv[1:3])

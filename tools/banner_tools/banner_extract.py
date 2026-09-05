"""Step 1: get the banner out of a CIA and its texture out of the banner.

    python banner_extract.py <game.cia> <outdir>

Writes <outdir>/banner.bin, icon.bin (ExeFS files, via ctrtool), then
<outdir>/banner_tex.png (the texture of the first region model, decoded) and
prints every model's texture size/format, the CWAV format, and the SMDH
titles. Edit banner_tex.png (same size), then run banner_build.py.
Needs ctrtool.exe next to this script or in the parent folder.
"""
import os, re, struct, subprocess, sys
import comp, tex, csar

here = os.path.dirname(os.path.abspath(__file__))
CTRTOOL = next(p for p in (os.path.join(here, 'ctrtool.exe'), os.path.join(here, '..', 'ctrtool.exe')) if os.path.exists(p))


def unlz(raw):
    d = comp.lz11_decode(raw, 0)
    return d[0] if isinstance(d, tuple) else d


def main(cia, outdir):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run([CTRTOOL, '--contents=' + os.path.join(outdir, 'content'), cia], capture_output=True)
    c0 = sorted(f for f in os.listdir(outdir) if f.startswith('content.0000'))[0]
    subprocess.run([CTRTOOL, '--exefsdir=' + os.path.join(outdir, 'exefs'), os.path.join(outdir, c0)], capture_output=True)
    for f in ('banner.bin', 'icon.bin'):
        os.replace(os.path.join(outdir, 'exefs', f), os.path.join(outdir, f))
    b = open(os.path.join(outdir, 'banner.bin'), 'rb').read(); assert b[:4] == b'CBMD'
    offs = struct.unpack_from('<14I', b, 8); cw = struct.unpack_from('<I', b, 0x84)[0]
    ends = [o for o in offs if o] + [cw]; k = 0; found = []
    for i, off in enumerate(offs):
        if not off: continue
        d = unlz(b[off:ends[k + 1]]); k += 1
        for o in [m.start() for m in re.finditer(b'TXOB', d)]:
            h, w = struct.unpack_from('<II', d, o + 0x14)
            if not (8 <= w <= 1024 and 8 <= h <= 1024): continue
            fmt = struct.unpack_from('<I', d, o + 4 + 11 * 4)[0]; n = struct.unpack_from('<I', d, o + 4 + 15 * 4)[0]
            data = o + 4 + 16 * 4 + struct.unpack_from('<I', d, o + 4 + 16 * 4)[0]
            print('model %2d (chunk offset 0x%X): texture %dx%d format %d (%s), %d bytes' % (i, off, w, h, fmt, tex.NAMES.get(fmt, '?'), n))
            found.append(((w, h), fmt, d[data:data + n]))
    # the region models share one texture size; the common model (index 0) may hold a small one. Save the size that occurs most.
    from collections import Counter
    size = Counter(f[0] for f in found).most_common(1)[0][0]
    (w, h), fmt, blob = next(f for f in found if f[0] == size)
    tex.decode(blob, w, h, fmt).convert('RGBA').save(os.path.join(outdir, 'banner_tex.png'))
    print('region texture: %dx%d format %d, shared by %d models' % (w, h, fmt, sum(1 for f in found if f[0] == size)))
    w = b[cw:]; info = csar.cwav_info(w)
    io_, isz = info['secs'][0x7000]; nch = struct.unpack_from('<I', w, io_ + 8 + 0x14)[0]
    print('CWAV: encoding %d (0=PCM8 1=PCM16 2=DSP-ADPCM), %d channel(s), %d Hz, %.2f s, %d bytes at 0x%X (mod 32 = %d)'
          % (info['enc'], nch, info['rate'], info['samples'] / info['rate'], len(w), cw, cw % 32))
    s = open(os.path.join(outdir, 'icon.bin'), 'rb').read()
    for i, lang in enumerate(['JP', 'EN', 'FR', 'DE', 'IT', 'ES', 'ZH', 'KO', 'NL', 'PT', 'RU', 'TW']):
        o = 8 + i * 0x200; short = s[o:o + 0x80].decode('utf-16-le').rstrip('\0')
        if short: print('SMDH %s: %r' % (lang, short))
    print('texture written to', os.path.join(outdir, 'banner_tex.png'))


if __name__ == '__main__':
    main(*sys.argv[1:3])

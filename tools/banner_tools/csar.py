"""CSAR / CWAR / CWAV reading and rebuilding for the in-battle voice banks.

    python csar.py nulltest      rebuild tenp.bcsar with every bank unchanged -> byte-identical?

CSAR: sections STRG, INFO, FILE. INFO holds a file table; internal files are
records {u16 0x1F00, u16 pad, u32 offset, u32 size} with offset relative to
FILE+8, laid out contiguously in table order at 0x20 alignment.
CWAR: 0x40 header, INFO (0x6800: count + {0x1F00, off, size} refs relative to
FILE+8), FILE (0x6801). CWAV: 0x40 header, INFO (0x7000), DATA (0x7001).
"""
import struct, sys, os


def _refs(d, at, count_at, n):
    return [struct.unpack_from('<HHII', d, at + i * 12) for i in range(n)]


class Csar:
    def __init__(self, path):
        d = bytearray(open(path, 'rb').read())
        assert d[:4] == b'CSAR'
        self.d = d
        nsec = struct.unpack_from('<H', d, 0x10)[0]
        self.secs = {t: (o, s) for t, _, o, s in (struct.unpack_from('<HHII', d, 0x14 + i * 12) for i in range(nsec))}
        info, _ = self.secs[0x2001]
        base = info + 8
        refs = {}
        for i in range(8):
            t, _, off = struct.unpack_from('<HHI', d, base + i * 8)
            refs[t] = base + off
        ft = refs[0x2106]
        n = struct.unpack_from('<I', d, ft)[0]
        self.file_off = self.secs[0x2002][0]
        self.records = []              # (record position, offset, size) for internal files, table order
        for i in range(n):
            t, _, off = struct.unpack_from('<HHI', d, ft + 4 + i * 8)
            fi = ft + off
            it, _, ioff = struct.unpack_from('<HHI', d, fi)
            if it == 0x220C:
                rec = fi + ioff
                rt, _, roff, rsize = struct.unpack_from('<HHII', d, rec)
                self.records.append((rec, roff, rsize))
        self.blobs = [bytes(d[self.file_off + 8 + o: self.file_off + 8 + o + s]) for _, o, s in self.records]

    def build(self, replace=None):
        """Return CSAR bytes with internal file i replaced by replace[i] (bytes)."""
        blobs = list(self.blobs)
        for i, b in (replace or {}).items():
            blobs[i] = b
        d = bytearray(self.d[:self.file_off])
        body = bytearray()
        offs = []
        for b in blobs:
            # keep absolute 0x20 alignment: body starts at file_off + 8
            pad = (-(self.file_off + 8 + len(body))) % 0x20
            body += bytes(pad)
            offs.append(len(body))
            body += b
        for (rec, _, _), o, b in zip(self.records, offs, blobs):
            struct.pack_into('<HHII', d, rec, 0x1F00, 0, o, len(b))
        fsec = b'FILE' + struct.pack('<I', 8 + len(body)) + bytes(body)
        out = d + fsec
        # header: total size and the FILE section size
        struct.pack_into('<I', out, 0x0C, len(out))
        nsec = struct.unpack_from('<H', out, 0x10)[0]
        for i in range(nsec):
            t = struct.unpack_from('<H', out, 0x14 + i * 12)[0]
            if t == 0x2002:
                struct.pack_into('<HHII', out, 0x14 + i * 12, t, 0, self.file_off, len(fsec))
        return bytes(out)


class Cwar:
    def __init__(self, blob):
        assert blob[:4] == b'CWAR'
        self.raw = blob
        nsec = struct.unpack_from('<H', blob, 0x10)[0]
        secs = {t: (o, s) for t, _, o, s in (struct.unpack_from('<HHII', blob, 0x14 + i * 12) for i in range(nsec))}
        self.info, self.filesec = secs[0x6800][0], secs[0x6801][0]
        n = struct.unpack_from('<I', blob, self.info + 8)[0]
        self.entries = [struct.unpack_from('<HHII', blob, self.info + 12 + i * 12) for i in range(n)]
        self.waves = [bytes(blob[self.filesec + 8 + o: self.filesec + 8 + o + s]) for _, _, o, s in self.entries]

    def build(self, waves=None):
        waves = waves or self.waves
        head = bytearray(self.raw[:self.filesec])
        body = bytearray()
        offs = []
        for w in waves:
            pad = (-(self.filesec + 8 + len(body))) % 0x20
            body += bytes(pad)
            offs.append(len(body))
            body += w
        for i, (o, w) in enumerate(zip(offs, waves)):
            struct.pack_into('<HHII', head, self.info + 12 + i * 12, 0x1F00, 0, o, len(w))
        fsec = b'FILE' + struct.pack('<I', 8 + len(body)) + bytes(body)
        out = head + fsec
        struct.pack_into('<I', out, 0x0C, len(out))
        nsec = struct.unpack_from('<H', out, 0x10)[0]
        for i in range(nsec):
            t = struct.unpack_from('<H', out, 0x14 + i * 12)[0]
            if t == 0x6801:
                struct.pack_into('<HHII', out, 0x14 + i * 12, t, 0, self.filesec, len(fsec))
        return bytes(out)


def cwav_info(w):
    nsec = struct.unpack_from('<H', w, 0x10)[0]
    secs = {t: (o, s) for t, _, o, s in (struct.unpack_from('<HHII', w, 0x14 + i * 12) for i in range(nsec))}
    wi = secs[0x7000][0]
    enc, loop, _, _, rate, ls, le = struct.unpack_from('<BBBBIII', w, wi + 8)
    return dict(secs=secs, info=wi, enc=enc, loop=loop, rate=rate, loop_start=ls, samples=le)


def build_cwav(pcm, coefs, template, adpcm=None):
    """Mono non-looping DSP-ADPCM CWAV, INFO copied from the template and patched."""
    import dsp
    t = cwav_info(template)
    adpcm = dsp.encode(pcm, coefs) if adpcm is None else adpcm
    wi = t['info']
    io_, isz = t['secs'][0x7000]
    info = bytearray(template[io_:io_ + isz])
    struct.pack_into('<III', info, 8 + 4, t['rate'], 0, len(pcm))
    # channel info -> adpcm info: find the 16 coefficients by locating the 0x0300 ref
    # layout (from the game's files): channel table at info+8+0x14 ...; simplest is to
    # patch by searching for the original coefficient block
    orig = cwav_info(template)
    ct = 8 + 0x14
    n = struct.unpack_from('<I', info, ct)[0]
    ro = struct.unpack_from('<HHI', info, ct + 4)[2]
    cinfo = ct + ro
    ao = struct.unpack_from('<HHI', info, cinfo + 8)[2] if struct.unpack_from('<H', info, cinfo + 8)[0] == 0x0300 else struct.unpack_from('<HHI', info, cinfo)[2]
    adp = cinfo + ao
    struct.pack_into('<16h', info, adp, *coefs)
    ps = adpcm[0] if adpcm else 0
    struct.pack_into('<HhhHhh', info, adp + 32, ps, 0, 0, ps, 0, 0)     # Sega mirrors ps into the loop ps
    body = bytearray(adpcm)                       # whole 8-byte frames; 0x20 alignment is the CWAR's job
    data = b'DATA' + struct.pack('<I', 8 + 0x18 + len(body)) + bytes(0x18) + bytes(body)
    head = bytearray(template[:0x40])
    off_info = 0x40
    off_data = off_info + len(info)
    struct.pack_into('<I', head, 0x0C, off_data + len(data))
    struct.pack_into('<HHII', head, 0x14, 0x7000, 0, off_info, len(info))
    struct.pack_into('<HHII', head, 0x20, 0x7001, 0, off_data, len(data))
    return bytes(head) + bytes(info) + data


if __name__ == '__main__':
    if sys.argv[1] == 'nulltest':
        for p in ('jp_orig/sound/tenp.bcsar', 'tr_envoice/sound/tenp.bcsar'):
            c = Csar(p)
            out = c.build()
            print('%-32s %d internal files; rebuilt unchanged byte-identical: %s (%d vs %d bytes)'
                  % (p, len(c.blobs), out == bytes(c.d), len(out), len(c.d)))
            if out != bytes(c.d):
                diff = next(i for i in range(min(len(out), len(c.d))) if out[i] != c.d[i])
                print('   first difference at 0x%X' % diff)
            # CWAR null test on bank 9 and 10
            for k in (9, 10):
                blob = c.blobs[[i for i, b in enumerate(c.blobs) if b[:4] == b'CWAR'][k]]
                w = Cwar(blob)
                print('   CWAR[%d]: %d waves; rebuilt unchanged byte-identical: %s' % (k, len(w.waves), w.build() == blob))

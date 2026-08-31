# -*- coding: utf-8 -*-
"""Reader for Capcom's 3DS .mca ("MADP") audio = Nintendo DSP-ADPCM.

Header, verified against TGAA/DGS files:
    0x00 'MADP'      0x04 u32 version (5)
    0x08 u8  channels
    0x0C u32 sample count
    0x10 u32 sample rate
    0x14 u32 loop start      0x18 u32 loop end
    0x1C u32 data offset     0x20 u32 data size
    0x24 f32 volume?
    0x38 16x s16 DSP coefficients (8 predictor pairs)
    0x58 s16 gain, s16 initial ps, s16 hist1, s16 hist2
Sanity check that pins it: ceil(samples/14)*8 == the ADPCM byte count.
"""
import struct
import numpy as np


def parse(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'MADP', d[:4]
    h = {}
    h['version'] = struct.unpack_from('<I', d, 4)[0]
    h['channels'] = d[8]
    h['samples'], h['rate'] = struct.unpack_from('<II', d, 0x0C)
    h['loop_start'], h['loop_end'] = struct.unpack_from('<II', d, 0x14)
    h['data_off'], h['data_size'] = struct.unpack_from('<II', d, 0x1C)
    h['coef'] = list(struct.unpack_from('<16h', d, 0x38))
    h['gain'], h['ps'], h['h1'], h['h2'] = struct.unpack_from('<4h', d, 0x58)
    h['raw'] = d
    h['adpcm'] = d[h['data_off']:h['data_off'] + h['data_size']]
    return h


def decode(h):
    """DSP-ADPCM -> int16 PCM."""
    coef, data, n = h['coef'], h['adpcm'], h['samples']
    out = np.zeros(n, np.int32)
    h1, h2 = h['h1'], h['h2']
    i = 0
    for f in range(0, len(data), 8):
        if i >= n:
            break
        ps = data[f]
        scale = 1 << (ps & 0x0F)
        p = (ps >> 4) & 0x07
        c1, c2 = coef[p * 2], coef[p * 2 + 1]
        for k in range(14):
            if i >= n:
                break
            b = data[f + 1 + k // 2]
            nib = (b >> 4) if k % 2 == 0 else (b & 0x0F)
            if nib >= 8:
                nib -= 16
            s = (nib * scale * 2048 + c1 * h1 + c2 * h2 + 1024) >> 11
            s = max(-32768, min(32767, s))
            out[i] = s
            h2, h1 = h1, s
            i += 1
    return out.astype(np.int16)



def parse_bytes(d):
    """Same as parse() but from an in-memory blob (e.g. an .arc entry)."""
    import struct
    assert d[:4] == b'MADP', d[:4]
    h = {}
    h['version'] = struct.unpack_from('<I', d, 4)[0]
    h['channels'] = d[8]
    h['samples'], h['rate'] = struct.unpack_from('<II', d, 0x0C)
    h['loop_start'], h['loop_end'] = struct.unpack_from('<II', d, 0x14)
    h['data_off'], h['data_size'] = struct.unpack_from('<II', d, 0x1C)
    h['coef'] = list(struct.unpack_from('<16h', d, 0x38))
    h['gain'], h['ps'], h['h1'], h['h2'] = struct.unpack_from('<4h', d, 0x58)
    h['raw'] = d
    h['adpcm'] = d[h['data_off']:h['data_off'] + h['data_size']]
    return h


if __name__ == '__main__':
    import sys, wave
    h = parse(sys.argv[1])
    print({k: v for k, v in h.items() if k not in ('raw', 'adpcm', 'coef')})
    print('coef', h['coef'])
    frames = -(-h['samples'] // 14) * 8
    print('expected adpcm bytes %d, have %d' % (frames, len(h['adpcm'])))
    pcm = decode(h)
    w = wave.open(sys.argv[2], 'wb')
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(h['rate'])
    w.writeframes(pcm.tobytes()); w.close()
    print('wrote', sys.argv[2], 'peak', int(np.abs(pcm).max()))

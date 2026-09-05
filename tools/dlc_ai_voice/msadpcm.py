# -*- coding: utf-8 -*-
"""Decoder for Chronicles' .xsew shout files, so this folder needs no ffmpeg.

An .xsew is a plain RIFF/WAVE whose 'fmt ' tag is 2 -- MS-ADPCM -- which
Python's own `wave` module refuses. The rest of the project shells out to
ffmpeg for this; ffmpeg is not installed on this machine, and the format is
small enough to decode directly.

    chr100_asg_v_matta_eng.xsew  ->  mono int16 @ 47890 Hz

Block layout, per channel, blockAlign bytes:
    u8  predictor index      s16 initial delta
    s16 sample2              s16 sample1
    then one 4-bit nibble per following sample, high nibble first.
"""
import struct

import numpy as np

ADAPT = [230, 230, 230, 230, 307, 409, 512, 614,
         768, 614, 512, 409, 307, 230, 230, 230]
COEF1 = [256, 512, 0, 192, 240, 460, 392]
COEF2 = [0, -256, 0, 64, 0, -208, -232]


def _chunks(d):
    assert d[:4] == b'RIFF' and d[8:12] == b'WAVE', 'not a RIFF/WAVE'
    o = 12
    while o + 8 <= len(d):
        cid = d[o:o + 4]
        sz = struct.unpack_from('<I', d, o + 4)[0]
        yield cid, d[o + 8:o + 8 + sz]
        o += 8 + sz + (sz & 1)


def decode(path):
    """.xsew (or any mono MS-ADPCM wav) -> (int16 numpy array, sample rate)."""
    d = open(path, 'rb').read()
    fmt = data = None
    for cid, body in _chunks(d):
        if cid == b'fmt ':
            fmt = body
        elif cid == b'data':
            data = body
    if fmt is None or data is None:
        raise ValueError('%s: missing fmt or data chunk' % path)
    tag, ch, rate, _bps, align, _bits = struct.unpack_from('<HHIIHH', fmt, 0)
    if tag != 2:
        raise ValueError('%s: format tag %d, expected 2 (MS-ADPCM)' % (path, tag))
    if ch != 1:
        raise ValueError('%s: %d channels, this decoder is mono-only' % (path, ch))
    # The coefficient table lives in the fmt extension; Capcom ships the
    # standard 7 pairs, but read them rather than assume.
    ncoef = struct.unpack_from('<H', fmt, 20)[0] if len(fmt) >= 22 else 7
    if len(fmt) >= 22 + ncoef * 4:
        pairs = struct.unpack_from('<%dh' % (ncoef * 2), fmt, 22)
        c1 = list(pairs[0::2])
        c2 = list(pairs[1::2])
    else:
        c1, c2 = COEF1, COEF2

    out = []
    for b in range(0, len(data) - align + 1, align):
        blk = data[b:b + align]
        pred = blk[0]
        delta, s2, s1 = struct.unpack_from('<hhh', blk, 1)
        if pred >= len(c1):
            raise ValueError('%s: predictor %d out of range' % (path, pred))
        a1, a2 = c1[pred], c2[pred]
        out.append(s2)
        out.append(s1)
        for byte in blk[7:]:
            for nib in ((byte >> 4) & 0xF, byte & 0xF):
                n = nib - 16 if nib >= 8 else nib
                s = (s1 * a1 + s2 * a2) // 256 + n * delta
                s = max(-32768, min(32767, s))
                out.append(s)
                s2, s1 = s1, s
                delta = max(16, (ADAPT[nib] * delta) // 256)
    return np.array(out, dtype=np.int16), rate


def write_wav(path, pcm, rate):
    """Plain 16-bit PCM mono wav, for anything that wants to read it back."""
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(np.asarray(pcm, dtype='<i2').tobytes())


if __name__ == '__main__':
    import sys
    for p in sys.argv[1:]:
        pcm, rate = decode(p)
        print('%s  %d samples  %d Hz  %.3fs  peak %d'
              % (p, len(pcm), rate, len(pcm) / rate, int(abs(pcm).max())))

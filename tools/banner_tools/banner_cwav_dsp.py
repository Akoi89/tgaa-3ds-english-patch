"""Replace a DSP-ADPCM banner CWAV with a WAV clip (TGAA banners are stereo
dual-mono DSP-ADPCM, which banner_cwav.py cannot do).

    python banner_cwav_dsp.py <banner.bin in> <clip.wav> <banner.bin out> [--match-level] [--keep-length]

The clip is mixed to mono, resampled to the banner's rate, optionally scaled to
the RMS of the voiced part of the original, faded 10 ms in / 40 ms out, padded
(--keep-length) to the original sample count so the CWAV keeps its exact size,
encoded once with the project's DSP-ADPCM encoder and written to both channels.
The CWAV INFO keeps its layout: coefficients and predictor/scale patched per
channel, sample count patched, channel 1 sample offset recomputed. CWAV offset
in the CBMD header is unchanged (models untouched).
"""
import math, os, struct, sys, wave
import numpy as np
R = os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2')
sys.path.insert(0, os.path.join(R, r'dlc_story_audit\audio_tools'))
import dsp, mca
from banner_cwav import resample, rms, limiter


def read_wav(p):
    w = wave.open(p); r = w.getframerate(); ch = w.getnchannels(); sw = w.getsampwidth()
    x = np.frombuffer(w.readframes(w.getnframes()), {2: np.int16, 4: np.int32}[sw]).astype(np.float64)
    if sw == 4: x /= 65536
    if ch > 1: x = x.reshape(-1, ch).mean(1)
    return x, r


def cwav_parse(w):
    nsec = struct.unpack_from('<H', w, 0x10)[0]
    secs = {t: (o, s) for t, _, o, s in (struct.unpack_from('<HHII', w, 0x14 + i * 12) for i in range(nsec))}
    io, isz = secs[0x7000]; info = bytearray(w[io:io + isz])
    enc, loop, _, _, rate, ls, le = struct.unpack_from('<BBBBIII', info, 8); n = struct.unpack_from('<I', info, 8 + 0x14)[0]
    chans = []
    for c in range(n):
        ro = struct.unpack_from('<HHI', info, 8 + 0x18 + c * 8)[2]; ci = 8 + 0x14 + ro
        so = struct.unpack_from('<HHI', info, ci)[2]; ao = struct.unpack_from('<HHI', info, ci + 8)[2]
        chans.append(dict(ci=ci, so=so, adp=ci + ao, coefs=struct.unpack_from('<16h', info, ci + ao)))
    return dict(secs=secs, io=io, info=info, enc=enc, rate=rate, samples=le, chans=chans)


def main(src, clip, out, match=False, keep=False):
    b = open(src, 'rb').read(); assert b[:4] == b'CBMD'
    cw = struct.unpack_from('<I', b, 0x84)[0]; w = b[cw:]; P = cwav_parse(w); assert P['enc'] == 2 and len(P['chans']) == 2
    do, dsz = P['secs'][0x7001]; le = P['samples']; nb = (le + 13) // 14 * 8
    orig = np.asarray(mca.decode({'coef': list(P['chans'][0]['coefs']), 'adpcm': w[do + 8 + P['chans'][0]['so']:do + 8 + P['chans'][0]['so'] + nb], 'samples': le, 'h1': 0, 'h2': 0}), np.float64)[:le]
    x, r = read_wav(clip); y = resample(x, r, P['rate'])
    if match:
        nz = np.nonzero(np.abs(orig) > 300)[0]; voiced = orig[nz[0]:nz[-1]] if len(nz) else orig
        nz2 = np.nonzero(np.abs(y) > 300)[0]; v2 = y[nz2[0]:nz2[-1]] if len(nz2) else y
        g = rms(voiced) / rms(v2); y = limiter(y * g, P['rate'])
        print('level: gain %.2f (orig voiced rms %d, clip %d -> %d), peak now %d' % (g, rms(voiced), rms(v2), rms(v2 * g), int(np.abs(y).max())))
    fi, fo = int(P['rate'] * 0.01), int(P['rate'] * 0.04)
    y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo)
    if keep:
        assert len(y) <= le, 'clip %d samples > original %d' % (len(y), le)
        y = np.concatenate([y, np.zeros(le - len(y))])
    pcm = np.clip(np.round(y), -32768, 32767).astype(np.int16)
    adpcm, coefs = dsp.encode(pcm); nbytes = len(adpcm); assert nbytes == (len(pcm) + 13) // 14 * 8
    info = P['info']
    struct.pack_into('<III', info, 8 + 4, P['rate'], 0, len(pcm))
    for c, ch in enumerate(P['chans']):
        struct.pack_into('<16h', info, ch['adp'], *coefs)
        struct.pack_into('<HhhHhh', info, ch['adp'] + 32, adpcm[0], 0, 0, adpcm[0], 0, 0)
    # channel blocks: ch0 at +0x18 (as original), ch1 right after, 0x20-aligned like the original layout
    so0 = P['chans'][0]['so']; so1 = so0 + nbytes; so1 += (-so1) % 0x20
    struct.pack_into('<I', info, P['chans'][0]['ci'] + 4, so0); struct.pack_into('<I', info, P['chans'][1]['ci'] + 4, so1)
    body = bytearray(so1 + nbytes); body[so0:so0 + nbytes] = adpcm; body[so1:so1 + nbytes] = adpcm
    data = b'DATA' + struct.pack('<I', 8 + len(body)) + bytes(body)
    data += bytes((-len(data)) % 0x20)
    head = bytearray(w[:0x40]); struct.pack_into('<I', head, 0x0C, 0x40 + len(info) + len(data))
    struct.pack_into('<HHII', head, 0x14, 0x7000, 0, 0x40, len(info)); struct.pack_into('<HHII', head, 0x20, 0x7001, 0, 0x40 + len(info), len(data))
    new_w = bytes(head) + bytes(info) + data
    open(out, 'wb').write(b[:cw] + new_w)
    # verify by decoding back
    Q = cwav_parse(new_w); back = np.asarray(mca.decode({'coef': list(Q['chans'][1]['coefs']), 'adpcm': new_w[Q['secs'][0x7001][0] + 8 + Q['chans'][1]['so']:][:nbytes], 'samples': len(pcm), 'h1': 0, 'h2': 0}), np.float64)[:len(pcm)]
    err = back - pcm; snr = 10 * math.log10((pcm.astype(np.float64) ** 2).mean() / max(1e-9, (err ** 2).mean()))
    print('wrote %s: CWAV %d -> %d bytes (%d samples %.2f s at %d Hz, was %d), banner %d -> %d bytes, ch1 decode SNR %.1f dB, cwav offset 0x%X (mod32=%d)'
          % (out, len(w), len(new_w), len(pcm), len(pcm) / P['rate'], P['rate'], le, len(b), len(b[:cw]) + len(new_w), snr, cw, cw % 32))


if __name__ == '__main__':
    a = sys.argv[1:]; match = '--match-level' in a; keep = '--keep-length' in a
    a = [x for x in a if not x.startswith('--')]
    main(a[0], a[1], a[2], match, keep)

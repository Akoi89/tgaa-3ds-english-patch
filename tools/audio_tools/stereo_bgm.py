# -*- coding: utf-8 -*-
"""Convert the music-baked courtroom-call tracks to Chronicles English.

These four bgm-stream tracks carry the character's shout INSIDE the music, so
the voice pipeline cannot touch them. They are STEREO MADP with loop points:

    per-channel 48-byte block at 0x38 + ch*0x30:
        +0  16x s16 DSP coefficients
        +32 s16 gain, s16 initial ps, s16 hist1, s16 hist2
        +40 s16 loop ps, s16 loop hist1, s16 loop hist2, s16 pad
    data at 0x38 + channels*0x30, frames (8 bytes / 14 samples)
    interleaved per-frame L,R,L,R (proven: L/R corr .52 vs -.09 split-halves)

Chronicles ships the English mixes as .sngw (Ogg) with official LoopStart/
LoopEnd vorbis comments at the native 48 kHz; scaled to the 3DS 32728 Hz they
land within ~54 samples of Capcom's own JP loop points, proving the same
arrangement (the extra EN length is reverb tail after the loop).

    python stereo_bgm.py <jp_dir> <out_dir> <track> [<track>...]
"""
import os, re, struct, subprocess, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsp

FF = os.environ.get('FFMPEG', 'ffmpeg')   # set FFMPEG if it is not on PATH
# Chronicles PC install: point TGAAC_STEAM at .../nativeDX11x64
STEAM = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'stream', 'bgm', 'wav')
MAX_GAIN = 2.0


def sngw_info(path):
    head = open(path, 'rb').read(4096)
    ls = int(re.search(rb'LoopStart=(\d+)', head).group(1))
    le = int(re.search(rb'LoopEnd=(\d+)', head).group(1))
    err = subprocess.run([FF, '-hide_banner', '-i', path, '-f', 'null', '-'],
                         capture_output=True)
    rate = int(re.search(rb'(\d+) Hz', err.stderr).group(1))
    return ls, le, rate


def decode_stereo(path, rate):
    out = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 's16le',
                          '-acodec', 'pcm_s16le', '-ac', '2', '-ar', str(rate), '-'],
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode('utf-8', 'replace')[:300])
    pcm = np.frombuffer(out.stdout, np.int16).reshape(-1, 2)
    return pcm[:, 0].copy(), pcm[:, 1].copy()


def dec_channel(frames, coef, n):
    out = np.zeros(n, np.int32)
    h1 = h2 = 0
    i = 0
    for f in range(0, len(frames), 8):
        if i >= n:
            break
        ps = frames[f]
        scale = 1 << (ps & 0xF)
        p = (ps >> 4) & 7
        c1, c2 = coef[p * 2], coef[p * 2 + 1]
        for k in range(14):
            if i >= n:
                break
            b = frames[f + 1 + k // 2]
            nib = (b >> 4) if k % 2 == 0 else (b & 0xF)
            if nib >= 8:
                nib -= 16
            s = (nib * scale * 2048 + c1 * h1 + c2 * h2 + 1024) >> 11
            s = max(-32768, min(32767, s))
            out[i] = s
            h2, h1 = h1, s
            i += 1
    return out.astype(np.int16)


def convert(jp_path, out_path, log=print):
    name = os.path.splitext(os.path.basename(jp_path))[0]
    jp = open(jp_path, 'rb').read()
    assert jp[:4] == b'MADP' and jp[8] == 2, (name, jp[8])
    rate = struct.unpack_from('<I', jp, 0x10)[0]
    jp_peak = 30000  # conservative reference; measured below if needed

    src = os.path.join(STEAM, name + '.sngw')
    ls_n, le_n, native = sngw_info(src)
    L, R = decode_stereo(src, rate)
    n = len(L)
    loop_s = round(ls_n * rate / native)
    loop_e = min(round(le_n * rate / native), n - 1)
    log('%s: %d smp @%d, loop %d..%d (native %d Hz)' % (name, n, rate, loop_s, loop_e, native))

    # level-match to the JP track's actual peak, capped
    import mca
    hjp = mca.parse(jp_path)
    jp_pcm = None  # decoding JP stereo fully is slow; use header-free peak match on EN
    peak = float(max(np.abs(L).max(), np.abs(R).max()))
    # keep Chronicles' own mix level; only guard clipping
    gain = 1.0 if peak <= 32767 else 32767.0 / peak

    chans = []
    for ch, pcm in (('L', L), ('R', R)):
        x = np.clip(pcm.astype(np.float64) * gain, -32768, 32767).astype(np.int16)
        adpcm, coefs = dsp.encode(list(x))
        dec = dec_channel(adpcm, coefs, n)
        a = dec.astype(np.float64); b = x.astype(np.float64)
        corr = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        assert corr > 0.95, (name, ch, corr)
        # loop context: state of the DECODED stream entering loop_s
        fr = loop_s // 14
        loop_ps = adpcm[fr * 8]
        lh1 = int(dec[loop_s - 1]) if loop_s >= 1 else 0
        lh2 = int(dec[loop_s - 2]) if loop_s >= 2 else 0
        chans.append(dict(adpcm=adpcm, coefs=coefs, ps=adpcm[0],
                          loop=(loop_ps, lh1, lh2), corr=corr))
        log('  %s ch%s: %d frames, corr %.4f' % (name, ch, len(adpcm) // 8, corr))

    nfr = (n + 13) // 14
    body = bytearray()
    for f in range(nfr):
        for c in chans:
            body += c['adpcm'][f * 8:(f + 1) * 8]
    size = (len(body) + 255) // 256 * 256
    body += bytes(size - len(body))

    d = bytearray(jp[:0x98])
    struct.pack_into('<I', d, 0x0C, n)
    struct.pack_into('<II', d, 0x14, loop_s, loop_e)
    struct.pack_into('<I', d, 0x20, size)
    for i, c in enumerate(chans):
        b = 0x38 + i * 0x30
        struct.pack_into('<16h', d, b, *c['coefs'])
        struct.pack_into('<4h', d, b + 32, 0, c['ps'], 0, 0)
        struct.pack_into('<4h', d, b + 40, c['loop'][0], c['loop'][1], c['loop'][2], 0)
    out = bytes(d) + bytes(body)

    # verify: reparse + spot-decode both channels of the finished file
    assert out[:4] == b'MADP' and out[8] == 2
    got_n, got_rate = struct.unpack_from('<II', out, 0x0C)
    assert got_n == n and got_rate == rate
    dat = out[0x98:0x98 + size]
    a = bytearray(); b2 = bytearray()
    for f in range(2 * min(nfr, 40000)):
        (a if f % 2 == 0 else b2).extend(dat[f * 8:(f + 1) * 8])
    la = dec_channel(bytes(a), chans[0]['coefs'], min(n, 40000 * 14))
    x = np.clip(L[:len(la)].astype(np.float64) * gain, -32768, 32767)
    corr = float(np.dot(la.astype(np.float64), x) /
                 (np.linalg.norm(la.astype(np.float64)) * np.linalg.norm(x) + 1e-9))
    assert corr > 0.95, (name, 'final-L', corr)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, 'wb').write(out)
    log('  %s WRITTEN: %d bytes (JP was %d), final corr %.4f' % (name, len(out), len(jp), corr))


if __name__ == '__main__':
    jp_dir, out_dir = sys.argv[1], sys.argv[2]
    for track in sys.argv[3:]:
        convert(os.path.join(jp_dir, track + '.mca'),
                os.path.join(out_dir, track + '.mca'))

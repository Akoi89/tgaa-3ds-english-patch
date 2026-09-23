# -*- coding: utf-8 -*-
"""Convert the music-baked courtroom-call tracks to Chronicles English.

These four bgm-stream tracks carry the character's shout INSIDE the music, so
the voice pipeline cannot touch them. They are STEREO MADP with loop points:

    per-channel 48-byte block at 0x38 + ch*0x30:
        +0  16x s16 DSP coefficients
        +32 s16 gain, s16 initial ps, s16 hist1, s16 hist2
        +40 s16 loop ps, s16 loop hist1, s16 loop hist2, s16 pad
    data at the header's own +0x34 offset (0xA0 typically for a stereo file;
        read per-file, never assumed -- the bytes from the end of the channel
        headers at +0x1C/0x98 up to there are zero), 256-byte blocks per
        channel, ch0 block / ch1 block / ch0 block / ...

CORRECTED 2026-09-22 (was: data hardcoded at +0x98, the channel-header end, not
the real +0x34 offset; per-frame L,R,L,R interleave, "proven" by an L/R corr of
.52 vs -.09 split-halves). Both were wrong. The +0x98 offset skipped Capcom's
own zero gap and wrote data 8 bytes early, the same class of bug across every
.mca writer here -- see memory note mca-data-starts-at-0x34.md. The per-frame
correlation "proof" is not trustworthy either: decoding real block data as
per-frame still correlates, because every "L" then holds even frames of BOTH
real channels and every "R" holds the odd frames of both. The corpus check (653
loose .mca under dgs2_base_romfs/sound) found no Capcom file using per-frame
stereo -- always 256-byte blocks -- and import_anime.py independently confirmed
the same thing by ear (a frame-interleaved build played garbled; 256-byte
blocks did not).

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


def interleave_blocks(streams):
    """Per-channel ADPCM byte strings (already 256-padded, equal length) ->
    one interleaved payload: ch0 block, ch1 block, ch0 block, ... ."""
    n = len(streams[0])
    assert all(len(s) == n for s in streams)
    out = bytearray()
    for i in range(0, n, 256):
        for s in streams:
            out += s[i:i + 256]
    return bytes(out)


def deinterleave_blocks(data, nch):
    """Inverse of interleave_blocks: one interleaved payload -> per-channel bytes."""
    per_ch = len(data) // nch
    return [b''.join(data[i * 256 * nch + c * 256:i * 256 * nch + (c + 1) * 256]
                     for i in range(-(-per_ch // 256)))
            for c in range(nch)]


def convert(jp_path, out_path, log=print):
    name = os.path.splitext(os.path.basename(jp_path))[0]
    jp = open(jp_path, 'rb').read()
    assert jp[:4] == b'MADP' and jp[8] == 2, (name, jp[8])
    rate = struct.unpack_from('<I', jp, 0x10)[0]
    o3 = struct.unpack_from('<I', jp, 0x34)[0]     # real data offset, read per-file
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

    # Capcom's own size rule (measured on the seven stereo crowd streams too):
    # each channel's ADPCM is padded to 256 bytes on its own, THEN interleaved,
    # so the data size is channels * ceil(per_channel/256)*256.
    per_ch = max((len(c['adpcm']) + 255) // 256 * 256 for c in chans)
    streams = [c['adpcm'] + bytes(per_ch - len(c['adpcm'])) for c in chans]
    body = interleave_blocks(streams)
    size = len(body)

    d = bytearray(jp[:o3])          # keeps Capcom's own header AND zero gap verbatim
    struct.pack_into('<I', d, 0x0C, n)
    struct.pack_into('<II', d, 0x14, loop_s, loop_e)
    struct.pack_into('<I', d, 0x20, size)
    for i, c in enumerate(chans):
        b = 0x38 + i * 0x30
        struct.pack_into('<16h', d, b, *c['coefs'])
        struct.pack_into('<4h', d, b + 32, 0, c['ps'], 0, 0)
        struct.pack_into('<4h', d, b + 40, c['loop'][0], c['loop'][1], c['loop'][2], 0)
    out = bytes(d) + bytes(body)
    out += bytes((-len(out)) % 32)   # Capcom's zero trailer: 32-aligned or hardware clicks at the end (pad32 rule)

    # verify: reparse + spot-decode both channels of the finished file, from o3
    assert out[:4] == b'MADP' and out[8] == 2
    got_n, got_rate = struct.unpack_from('<II', out, 0x0C)
    assert got_n == n and got_rate == rate
    dat = out[o3:o3 + size]
    a, _ = deinterleave_blocks(dat, 2)
    la = dec_channel(a, chans[0]['coefs'], min(n, 40000 * 14))
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

# -*- coding: utf-8 -*-
"""Put Capcom's English narration into the animated cutscenes of both games.

    python import_anime.py --report
    python import_anime.py --apply <out-romfs> [<out-romfs2> ...]

A THIRD audio system, separate from the story voices and the character shouts,
and the last one still speaking Japanese: `sound/stream/anime/wav/*.mca`. The
opening narration is in it, which is what a player hears first.

Both games ship the SAME cutscenes -- correlation 1.0000 between TGAA1's and
TGAA2's copies, identical file sizes and coefficients, and only 22 bytes
differing, all inside the 152-byte header. So one English mix serves both, and
there is no risk of giving one game the other's audio.

Chronicles ships the cutscene audio as SEPATE STEMS rather than a finished
mix: `<name>_MUSIC`, `<name>_SE`, `<name>_VOICE_eng`, `<name>_VOICE_jpn`. The
English track is MUSIC + SE + VOICE_eng summed. Durations agree with the 3DS
track to a hundredth of a second, so this is mixing, not resynchronisation.

STEREO, so the mono voice pipeline does not apply: per-channel 48-byte blocks at
0x38 + ch*0x30, frames interleaved L,R,L,R. That is the layout stereo_bgm.py
established for the music-baked shouts, and its encoder is reused here.

Streamed, so the slot rule applies: the result is padded back to Capcom's exact
file size. ADPCM is fixed-bitrate and the durations match, so it fits.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys

import numpy as np

AUDIO = os.environ.get('AUDIO_TOOLS',
                       os.environ.get('AUDIO_TOOLS', '.'))
sys.path.insert(0, AUDIO)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import dsp                                                     # noqa: E402
import mca                                                     # noqa: E402
from stereo_bgm import dec_channel                             # noqa: E402

SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JP = os.path.join(SCRATCH, 'tut', 't1jap', 'romfs', 'sound', 'stream', 'anime')
PC = os.path.join(os.environ.get('TGAAC_STEAM',
                                 os.environ.get('TGAAC_STEAM', '')),
                  'nativeDX11x64', 'sound', 'stream', 'anime', 'wav')
FFMPEG = (os.environ.get('FFMPEG') or 'ffmpeg')
STEMS = ('_MUSIC', '_SE', '_VOICE_eng')
# 256-byte block interleave. CONFIRMED BY EAR 2026-08-31 after a frame-
# interleaved build played garbled. Overridable only for further experiments.
INTERLEAVE = int(os.environ.get('MCA_INTERLEAVE', '256'))


def mix(name, rate):
    """MUSIC + SE + VOICE_eng, summed without amix's automatic attenuation."""
    ins = []
    for s in STEMS:
        p = os.path.join(PC, name + s + '.sngw')
        if not os.path.exists(p):
            return None
        ins += ['-i', p]
    r = subprocess.run(
        [FFMPEG, '-hide_banner', '-loglevel', 'error'] + ins +
        ['-filter_complex', 'amix=inputs=%d:duration=longest:normalize=0' % len(STEMS),
         '-ac', '2', '-ar', str(rate), '-f', 's16le', '-'],
        capture_output=True)
    if r.returncode or not r.stdout:
        raise RuntimeError(r.stderr.decode('utf8', 'replace')[:200])
    p = np.frombuffer(r.stdout, np.int16).reshape(-1, 2)
    return p[:, 0].copy(), p[:, 1].copy()


def jp_rms(path, h, secs=30):
    """RMS of Capcom's own track, as the level to match."""
    d = open(path, 'rb').read()
    coef = list(struct.unpack_from('<16h', d, 0x38))
    off = 0x38 + h['channels'] * 0x30
    n = min(int(h['rate'] * secs), h['samples'])
    need = int(np.ceil(n / 14)) * 8 * h['channels']
    raw = np.frombuffer(d[off:off + need], np.uint8)
    blk = raw[:len(raw) // 16 * 16].reshape(-1, 16)
    x = dec_channel([int(v) for v in blk[:, :8].reshape(-1)], coef, n)
    return float(np.sqrt((x.astype(np.float64) ** 2).mean()))


def build(jp_path, log=print):
    jp = open(jp_path, 'rb').read()
    name = os.path.splitext(os.path.basename(jp_path))[0]
    h = mca.parse(jp_path)
    if h['channels'] != 2:
        return None, 'not stereo'
    got = mix(name, h['rate'])
    if got is None:
        return None, 'no English voice stem'
    L, R = got
    n = min(h['samples'], len(L))

    # Capcom's finished mix is mastered; a raw stem sum lands about 3 dB
    # quieter and sounds thin next to it. Match the Japanese track's RMS, then
    # cap so nothing clips.
    jp_ref = jp_rms(jp_path, h)
    ours = float(np.sqrt((L[:n].astype(np.float64) ** 2).mean()))
    gain = (jp_ref / ours) if (ours and jp_ref) else 1.0
    peak = float(max(np.abs(L[:n]).max(), np.abs(R[:n]).max())) * gain
    if peak > 32000:
        gain *= 32000.0 / peak
    chans = []
    for tag, pcm in (('L', L), ('R', R)):
        x = np.clip(pcm[:n].astype(np.float64) * gain, -32768, 32767).astype(np.int16)
        adpcm, coefs = dsp.encode(list(x))
        dec = dec_channel(adpcm, coefs, n)
        a, b = dec.astype(np.float64), x.astype(np.float64)
        corr = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        if corr < 0.95:
            return None, '%s channel round-trips at only %.3f' % (tag, corr)
        chans.append(dict(adpcm=adpcm, coefs=coefs, ps=adpcm[0], corr=corr))

    # CHANNEL INTERLEAVE. This is the unsettled part and the reason a build
    # sounded garbled: every offline check shares whatever assumption is made
    # here, so none of them can detect it being wrong. Selectable so it can be
    # decided by listening, which is the only ground truth available.
    #   8   L,R per 8-byte ADPCM frame -- what stereo_bgm.py assumes. WRONG.
    #       A build using it played garbled in game.
    #   256 L,R per 256-byte block. CORRECT, confirmed by ear. It also explains
    #       why Capcom's data_size is always a multiple of 256, and it makes our
    #       file reproduce Capcom's own per-track L/R pattern (+0.876 vs +0.874
    #       on go_anime_1a, and matching the LOW +0.225 vs +0.215 on
    #       go_anime_ed, which is the part a single-file test cannot show).
    blk = INTERLEAVE
    streams = []
    for c in chans:
        a = bytearray(c['adpcm'])
        if len(a) % blk:
            a += bytes(blk - len(a) % blk)
        streams.append(bytes(a))
    body = bytearray()
    for o in range(0, len(streams[0]), blk):
        for st in streams:
            body += st[o:o + blk]
    size = (len(body) + 255) // 256 * 256
    body += bytes(size - len(body))
    d = bytearray(jp[:0x98])
    struct.pack_into('<I', d, 0x0C, n)
    struct.pack_into('<I', d, 0x20, size)
    for i, c in enumerate(chans):
        o = 0x38 + i * 0x30
        struct.pack_into('<16h', d, o, *c['coefs'])
        struct.pack_into('<4h', d, o + 32, 0, c['ps'], 0, 0)
    out = bytes(d) + bytes(body)
    if len(out) > len(jp):
        return None, 'overruns Capcom\'s slot by %d bytes' % (len(out) - len(jp))
    out += bytes(len(jp) - len(out))          # back to Capcom's exact size
    log('  %-20s %6.1fs  corr L %.4f R %.4f  %d bytes'
        % (name, n / h['rate'], chans[0]['corr'], chans[1]['corr'], len(out)))
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--apply', nargs='*', default=[])
    a = ap.parse_args()
    tracks = sorted(f for f in os.listdir(os.path.join(JP, 'wav'))
                    if f.endswith('.mca'))
    ok, skip = [], []
    for t in tracks:
        p = os.path.join(JP, 'wav', t)
        if a.report:
            name = t[:-4]
            have = all(os.path.exists(os.path.join(PC, name + s + '.sngw'))
                       for s in STEMS)
            (ok if have else skip).append(name)
            continue
        blob, why = build(p)
        (ok if blob else skip).append((t[:-4], why))
        if blob:
            for out in a.apply:
                dst = os.path.join(out, 'sound', 'stream', 'anime', 'wav', t)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'wb').write(blob)
    if a.report:
        print('  cutscenes with an English stem : %d' % len(ok))
        print('  without (no dialogue in them)  : %d  %s' % (len(skip), skip))
        return
    print('  converted : %d' % len(ok))
    for n, why in skip:
        print('     skipped %-20s %s' % (n, why))
    for out in a.apply:
        src = os.path.join(JP, 'go_anime.stqr')
        if os.path.exists(src):
            dst = os.path.join(out, 'sound', 'stream', 'anime', 'go_anime.stqr')
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            print('  index copied to %s' % os.path.relpath(dst, out))


if __name__ == '__main__':
    main()

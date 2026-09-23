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
0x38 + ch*0x30, data at the header's own +0x34 offset (not the +0x1C/0x98
channel-header end -- see the CHANNEL INTERLEAVE note below and memory note
mca-data-starts-at-0x34.md), 256-byte blocks per channel. That is the layout
this project confirmed by ear for stereo .mca; stereo_bgm.py's encoder is
reused here (and was itself corrected to the same offset and layout 2026-09-22).

Streamed, so the slot rule applies: the result is padded back to Capcom's exact
file size. ADPCM is fixed-bitrate and the durations match, so it fits.
"""
import os
import argparse
import collections
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
from stereo_bgm import dec_channel, deinterleave_blocks        # noqa: E402

SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Capcom's untouched Japanese tree, the donor whose header and slot size every
# built file keeps. Overridable because the original path was a scratch folder
# that no longer exists, which left this script unrunnable; the live copy is
# dlc_story_audit\basegame\rom\sound\stream\anime.
JP = os.environ.get('ANIME_JP') or os.path.join(
    SCRATCH, 'tut', 't1jap', 'romfs', 'sound', 'stream', 'anime')
PC = os.path.join(os.environ.get('TGAAC_STEAM',
                                 os.environ.get('TGAAC_STEAM', '')),
                  'nativeDX11x64', 'sound', 'stream', 'anime', 'wav')
FFMPEG = (os.environ.get('FFMPEG') or 'ffmpeg')
STEMS = ('_MUSIC', '_SE', '_VOICE_eng')
# 256-byte block interleave. CONFIRMED BY EAR 2026-08-31 after a frame-
# interleaved build played garbled. Overridable only for further experiments.
INTERLEAVE = int(os.environ.get('MCA_INTERLEAVE', '256'))

# KEEP THE SHIPPED LOUDNESS. jp_rms() was corrected 2026-09-22 to read from the
# real +0x34 offset in 256-byte blocks (it is right to be honest about what a
# fresh measurement of Capcom's track now shows), but feeding that corrected
# number into v18a_level() would move the release's level by up to +0.70 /
# -0.61 dB per track and fail verify_anime_fix.py's 0.25 dB check -- an
# audible, unintended change nobody asked for. These seven values are v1.8a's
# actual calibration target: jp_rms() computed with the PRE-2026-09-22 reader
# (off = 0x38 + channels*0x30, per-8-byte-frame split -- the same +0x1C-class
# bug the rest of this job fixed). They are kept here deliberately so already
# shipped levels do not move; changing them is a sound decision for the user,
# not a bug fix. See memory note mca-data-starts-at-0x34.md.
V18A_JP_REF = {
    'go_anime_1a': 8388.033621012835,
    'go_anime_1b': 7241.6101531427685,
    'go_anime_2a': 4898.441154948754,
    'go_anime_2b': 8599.641204089896,
    'go_anime_3': 3793.8505860462483,
    'go_anime_5': 6450.742263059082,
    'go_anime_ed': 6078.321175070444,
}


def mix(name, rate):
    """MUSIC + SE + VOICE_eng, summed without amix's automatic attenuation.

    FLOAT, and that is the whole of the crackle fix. This asked ffmpeg for
    `-f s16le` until 2026-09-20, which meant ffmpeg hard clipped the sum on
    the way out: the three stems together run up to +5.2 dB past full scale,
    each one of them under it on its own. build() then measured the peak of
    what came back, which can never read over full scale, and scaled the
    track DOWN to match the Japanese RMS, so nothing downstream could see it.
    That is 615 chopped samples in 126 separate bursts in the opening alone,
    and a hardware tester heard every one of them.
    """
    ins = []
    for s in STEMS:
        p = os.path.join(PC, name + s + '.sngw')
        if not os.path.exists(p):
            return None
        ins += ['-i', p]
    r = subprocess.run(
        [FFMPEG, '-hide_banner', '-loglevel', 'error'] + ins +
        ['-filter_complex', 'amix=inputs=%d:duration=longest:normalize=0' % len(STEMS),
         '-ac', '2', '-ar', str(rate), '-f', 'f32le', '-'],
        capture_output=True)
    if r.returncode or not r.stdout:
        raise RuntimeError(r.stderr.decode('utf8', 'replace')[:200])
    p = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).astype(np.float64) * 32768.0
    return p[:, 0].copy(), p[:, 1].copy()


def limit(x, ceiling, rate, look=0.003, release=0.060):
    """Hold |x| under `ceiling` by riding the gain instead of chopping peaks.

    Instant attack with a 3 ms lookahead so the gain is already down before
    the peak arrives, and a 60 ms release so it comes back slowly enough not
    to be heard. Returns the limited signal and the gain curve.
    """
    need = np.minimum(1.0, ceiling / np.maximum(np.abs(x).max(axis=1), 1e-9))
    L = max(1, int(look * rate))
    # running minimum over the lookahead window, monotonic deque
    pad = np.concatenate([need, np.ones(L)])
    run = np.empty(len(need))
    dq = collections.deque()
    for i in range(len(pad)):
        while dq and pad[dq[-1]] >= pad[i]:
            dq.pop()
        dq.append(i)
        j = i - L
        if j >= 0:
            while dq[0] < j:
                dq.popleft()
            run[j] = pad[dq[0]]
    a = np.exp(-1.0 / (release * rate))
    g = np.empty(len(run))
    cur = 1.0
    for i, v in enumerate(run):
        cur = v if v < cur else a * cur + (1 - a) * v
        g[i] = cur
    return x * g[:, None], g


def v18a_level(clean, jp_ref):
    """The loudness the clipped builds landed on, reproduced without clipping.

    Up to v1.8a the level was an accident: ffmpeg chopped the peaks, which
    raised the RMS, then the RMS match and the peak cap set the gain from
    that. Aiming the limiter at the same number keeps every release sounding
    the same as the one before it, which is the point. Matching Capcom's RMS
    outright would need 45% of samples pulled down by up to 9 dB and is a
    different decision about how the patch sounds.
    """
    clipped = np.clip(clean, -32768, 32767)
    g = jp_ref / float(np.sqrt((clipped[:, 0] ** 2).mean()))
    peak = float(np.abs(clipped).max()) * g
    if peak > 32000:
        g *= 32000.0 / peak
    return float(np.sqrt(((clipped[:, 0] * g) ** 2).mean()))


def jp_rms(path, h, secs=30):
    """RMS of Capcom's own track, as the level to match.

    CORRECTED 2026-09-22 (was: read from off = 0x38 + channels*0x30 == 0x98,
    the channel-header end, and split per-8-byte-frame -- the same +0x1C-class
    bug as the writers, plus the per-frame assumption this project has since
    shown is wrong for every Capcom .mca). Now reads from the header's own
    +0x34 offset and deinterleaves 256-byte blocks, the way the game does.
    """
    d = open(path, 'rb').read()
    coef = list(struct.unpack_from('<16h', d, 0x38))
    off = h['data_off']            # +0x34, not the +0x1C/0x98 channel-header end
    n = min(int(h['rate'] * secs), h['samples'])
    nblocks = -(-(int(np.ceil(n / 14)) * 8) // 256)     # ceil to whole 256-byte blocks
    need = nblocks * 256 * h['channels']
    raw = d[off:off + need]
    ch0 = deinterleave_blocks(raw, h['channels'])[0]
    x = dec_channel(ch0, coef, n)
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
    # quieter and sounds thin next to it. Capcom's own English mix is no help
    # here, go_anime_1a.sngw correlates 0.9903 with MUSIC + SE + VOICE_jpn, so
    # it is the Japanese master. Aim at the loudness the earlier builds
    # reached and get there by limiting the peaks rather than losing them.
    # Calibration target: v1.8a's own reference (V18A_JP_REF), not a fresh
    # jp_rms() -- see the comment on V18A_JP_REF. jp_rms() (corrected, honest)
    # is only the fallback for a track that has no recorded v1.8a reference.
    jp_ref = V18A_JP_REF.get(name)
    if jp_ref is None:
        jp_ref = jp_rms(jp_path, h)
    clean = np.stack([L[:n], R[:n]], axis=1)
    target = v18a_level(clean, jp_ref) if jp_ref else float(np.sqrt((L[:n] ** 2).mean()))
    ours = float(np.sqrt((clean[:, 0] ** 2).mean()))
    y, gred = limit(clean * ((target / ours) if ours else 1.0), 32000.0, h['rate'])
    got_rms = float(np.sqrt((y[:, 0] ** 2).mean()))
    if got_rms:
        y *= target / got_rms                  # give back what the limiter shaved
    if np.abs(y).max() > 32000:                # and hold the ceiling anyway
        y, g2 = limit(y, 32000.0, h['rate'])
        gred = gred * g2
    assert np.abs(y).max() <= 32767, 'limiter let a sample past full scale'
    chans = []
    for tag, pcm in (('L', y[:, 0]), ('R', y[:, 1])):
        x = np.clip(pcm[:n], -32768, 32767).astype(np.int16)
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
    #   8   L,R per 8-byte ADPCM frame -- what stereo_bgm.py assumed before it
    #       was corrected 2026-09-22. WRONG. A build using it played garbled.
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
    d = bytearray(jp[:h['data_off']])   # Capcom's own header AND zero gap, verbatim (+0x34, not +0x1C/0x98)
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
    log('  %-20s %6.1fs  corr L %.4f R %.4f  limiter %4.1f%% of samples, most'
        ' %.2f dB  %d bytes'
        % (name, n / h['rate'], chans[0]['corr'], chans[1]['corr'],
           100.0 * float((gred < 0.9944).mean()), -20 * np.log10(float(gred.min())),
           len(out)))
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

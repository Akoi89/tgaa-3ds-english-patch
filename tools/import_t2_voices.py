# -*- coding: utf-8 -*-
"""Import Capcom's English story voices into TGAA2's base game.

    python import_t2_voices.py --report
    python import_t2_voices.py --apply <out-romfs>

TGAA2 shipped with only TEN English voice clips -- Naruhodo's and Susato's
courtroom shouts, which live in the two `sound/se` banks. Every one of the 555
STORY voice streams under `sound/stream/voice/wav` is still Japanese, which is
why Ryutaro reads English text in a Japanese voice. TGAA1 got 81 of these; TGAA2
got none of them.

252 of the 555 have an exact-name English recording in Chronicles. The rest are
overwhelmingly music, not voice (`09_tsuisou_1`, `10_asougi_theme`,
`12_naruhodo_igiari` -- the last of those is a shout baked into a BGM track and
needs a stereo encoder this project does not have).

THE SLOT RULE, which is why this is not just a file copy: these are STREAMED,
and a stream larger than Capcom's original is cut off in-game at an
unpredictable point. So every rebuilt clip is padded back to Capcom's EXACT file
size, and where the English take is longer than the Japanese one the sample rate
comes down just far enough to fit the complete take. Never trim words. In
practice Capcom recorded both languages to the same timing, so most clips need a
rate change of well under a tenth of a percent.

The .stqr index carries each stream's size, sample count and rate. It must be
updated to agree with the rebuilt header or the stream will not play -- that
mismatch is what made an earlier build silent.
"""
import os
import argparse
import re
import shutil
import struct
import subprocess
import sys

import numpy as np

BS = chr(92)

AUDIO = os.environ.get('AUDIO_TOOLS', '.')
sys.path.insert(0, AUDIO)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import dsp                                                    # noqa: E402
import mca                                                    # noqa: E402

SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# --game picks the base romfs; both games use the identical layout and the same
# Chronicles voice folder, so one tool serves both.
GAME_ROOT = {'t2': ('tut', 'dgs2base', 'romfs'), 't1': ('tut', 't1jap', 'romfs')}
JP = None
PC = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'nativeDX11x64', 'sound', 'stream', 'voice', 'wav')
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')

QUIET = 150                   # below this counts as silence at a clip's edges
SAMPLES_PER_FRAME = 14        # DSP-ADPCM: 8 bytes carry 14 samples
BYTES_PER_FRAME = 8
STQR_REC = None               # discovered from the file, see stqr_layout()


def decode(path, rate):
    """Any ffmpeg-readable file -> mono int16 PCM at `rate`."""
    r = subprocess.run(
        [FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', path,
         '-ac', '1', '-ar', str(rate), '-f', 's16le', '-'],
        capture_output=True)
    if r.returncode or not r.stdout:
        raise RuntimeError('ffmpeg failed on %s: %s'
                           % (path, r.stderr.decode('utf8', 'replace')[:200]))
    return np.frombuffer(r.stdout, dtype='<i2')


def trim_edges(pcm):
    """Drop leading and trailing silence, never a pause inside the line.

    Capcom's English masters carry more edge padding than the 3DS slots do, and
    that padding alone is what pushes most clips over. Trimming it buys the room
    honestly; lowering the rate is the fallback, not the first move."""
    nz = np.nonzero(np.abs(np.asarray(pcm)) > QUIET)[0]
    return np.asarray(pcm)[nz[0]:nz[-1] + 1] if len(nz) else np.asarray(pcm)


def capacity_samples(data_size):
    return (data_size // BYTES_PER_FRAME) * SAMPLES_PER_FRAME


def plan_one(name):
    """What rate this clip needs to fit Capcom's slot with the whole take."""
    cap_path = os.path.join(JP, 'wav', name + '.mca')
    eng = os.path.join(PC, name + '_eng.sngw')
    if not (os.path.exists(cap_path) and os.path.exists(eng)):
        return None
    h = mca.parse(cap_path)
    cap = capacity_samples(h['data_size'])
    # measure the English take at Capcom's own rate first
    pcm = trim_edges(decode(eng, h['rate']))
    rate = h['rate']
    if len(pcm) > cap:
        # lower the rate just enough for the COMPLETE take to fit
        rate = int(h['rate'] * cap / len(pcm)) - 1
        pcm = trim_edges(decode(eng, rate))
        while len(pcm) > cap and rate > 8000:
            rate -= 200
            pcm = trim_edges(decode(eng, rate))
    return dict(name=name, cap_path=cap_path, hdr=h, cap=cap,
                pcm=pcm, rate=rate, orig_rate=h['rate'])


def rebuild(job):
    """A new .mca at Capcom's EXACT file size, carrying the English take."""
    cap = open(job['cap_path'], 'rb').read()
    h = job['hdr']
    pcm = np.asarray(job['pcm'][:job['cap']], dtype=np.int16)
    adpcm, coefs = dsp.encode(pcm)
    size = (len(adpcm) + 63) // 64 * 64
    if h['data_off'] + size > len(cap):
        raise AssertionError('%s overruns its slot' % job['name'])
    d = bytearray(cap[:h['data_off']])
    struct.pack_into('<I', d, 0x0C, len(pcm))          # sample count
    struct.pack_into('<I', d, 0x10, job['rate'])       # sample rate
    struct.pack_into('<I', d, 0x20, size)              # data size
    struct.pack_into('<16h', d, 0x38, *coefs)
    struct.pack_into('<4h', d, 0x58, h['gain'], h['ps'], 0, 0)
    d += adpcm + bytes(size - len(adpcm))
    d += bytes(len(cap) - len(d))                      # back to Capcom's size
    assert len(d) == len(cap), (len(d), len(cap))
    return bytes(d), len(pcm), size


# .stqr layout, read off the file rather than assumed:
#   0x00 'STQR', u32 version(4), u32 count, u32 count, ...
#   0x1C  records begin, STRIDE 36 bytes:
#         +0  u32 total FILE size of the .mca (data_off + data_size)
#         +4  u32 sample count
#         +12 u32 sample rate
#   then a table of names, 'sound\stream\voice\wav\<clip>' with NO extension.
# The index must agree with the .mca header or the stream does not play. Because
# every rebuild is padded back to Capcom's exact file size, the size field never
# changes -- only samples and rate do.
STQR_BASE = 0x1C
STQR_STRIDE = 36


def stqr_names(blob):
    pat = ('sound' + BS + 'stream' + BS + 'voice' + BS + 'wav' + BS).encode()
    return [m.group(0).decode().split(BS)[-1]
            for m in re.finditer(re.escape(pat) + rb'[ -~]+', blob)]


def sync_stqr(path, updates):
    b = bytearray(open(path, 'rb').read())
    names = stqr_names(bytes(b))
    done = 0
    for i, nm in enumerate(names):
        if nm not in updates:
            continue
        o = STQR_BASE + i * STQR_STRIDE
        size, samples, rate = updates[nm]
        old_size, old_samples, old_rate = updates[nm + '__old']
        # prove we are looking at the right record before writing to it
        if struct.unpack_from('<I', b, o + 4)[0] != old_samples:
            raise AssertionError('%s: record %d does not hold the expected '
                                 'sample count (%d, wanted %d)'
                                 % (os.path.basename(path), i,
                                    struct.unpack_from('<I', b, o + 4)[0], old_samples))
        struct.pack_into('<I', b, o + 4, samples)
        struct.pack_into('<I', b, o + 12, rate)
        done += 1
    if done:
        open(path, 'wb').write(bytes(b))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--apply')
    ap.add_argument('--only', default='')
    ap.add_argument('--limit', type=int, default=0)
    # QUALITY FLOOR. A clip that will not fit above this fraction of Capcom's
    # own rate is LEFT JAPANESE. A badly degraded English line is worse than the
    # Japanese one it replaces, and the project rule is never to cut words to
    # make something fit.
    ap.add_argument('--floor', type=float, default=0.75)
    ap.add_argument('--game', default='t2', choices=('t1', 't2'))
    a = ap.parse_args()
    globals()['JP'] = os.path.join(SCRATCH, *GAME_ROOT[a.game],
                                   'sound', 'stream', 'voice')

    names = sorted(f[:-4] for f in os.listdir(os.path.join(JP, 'wav'))
                   if f.endswith('.mca')
                   and os.path.exists(os.path.join(PC, f[:-4] + '_eng.sngw')))
    if a.only:
        names = [n for n in names if n.endswith('_' + a.only)]
    if a.limit:
        names = names[:a.limit]
    print('  clips with an English recording: %d' % len(names))

    jobs, full, lowered, failed, skipped = [], 0, [], [], []
    for n in names:
        try:
            j = plan_one(n)
        except Exception as e:
            failed.append((n, str(e)[:60])); continue
        if j is None:
            continue
        if j['rate'] < j['orig_rate'] * a.floor:
            skipped.append((n, j['orig_rate'], j['rate']))
            continue
        jobs.append(j)
        if j['rate'] == j['orig_rate']:
            full += 1
        else:
            lowered.append((n, j['orig_rate'], j['rate']))
    print('  fit at Capcom\'s own rate      : %d' % full)
    print('  needed a lower rate           : %d' % len(lowered))
    if lowered:
        worst = min(r for _, _, r in lowered)
        drops = sorted(((o - r) / o, n, o, r) for n, o, r in lowered)
        print('     lowest rate used           : %d Hz' % worst)
        print('     biggest reduction          : %.1f%% (%s %d -> %d)'
              % (drops[-1][0] * 100, drops[-1][1], drops[-1][2], drops[-1][3]))
        big = [d for d in drops if d[0] > 0.02]
        print('     reductions over 2%%         : %d' % len(big))
        for d in big[-6:]:
            print('        %-22s %5d -> %5d Hz  (-%.1f%%)' % (d[1], d[2], d[3], d[0] * 100))
    print('  left Japanese (below the %.0f%% floor): %d' % (a.floor * 100, len(skipped)))
    for n, e in failed[:5]:
        print('     FAILED %s: %s' % (n, e))

    if not a.apply:
        return

    out = a.apply
    wav_out = os.path.join(out, 'sound', 'stream', 'voice', 'wav')
    os.makedirs(wav_out, exist_ok=True)
    updates = {}
    for j in jobs:
        blob, samples, size = rebuild(j)
        open(os.path.join(wav_out, j['name'] + '.mca'), 'wb').write(blob)
        updates[j['name']] = (size, samples, j['rate'])
        updates[j['name'] + '__old'] = (j['hdr']['data_size'], j['hdr']['samples'],
                                        j['hdr']['rate'])
    print('  wrote %d .mca into %s' % (len(jobs), wav_out))

    # DISCOVER the index files; do not hardcode their names. TGAA2 uses
    # bb_voice_jpn / bb_demo_vo_jpn, TGAA1 uses go_nrt_voice / go_trial_voice,
    # and assuming TGAA2's pair silently synced nothing for TGAA1 -- which is
    # the exact condition that makes a stream play as silence.
    synced = 0
    stqrs = [f for f in os.listdir(JP) if f.endswith('.stqr')]
    if not stqrs:
        raise SystemExit('no .stqr found in %s' % JP)
    for st in stqrs:
        src = os.path.join(JP, st)
        dst = os.path.join(out, 'sound', 'stream', 'voice', st)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        synced += sync_stqr(dst, updates)
    if synced != len(jobs):
        raise SystemExit('synced %d index records for %d rebuilt clips -- the '
                         'index and the headers must agree or the streams are '
                         'silent' % (synced, len(jobs)))
    print('  stqr index records updated    : %d' % synced)


if __name__ == '__main__':
    main()

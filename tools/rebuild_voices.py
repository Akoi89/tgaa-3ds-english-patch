# -*- coding: utf-8 -*-
"""Re-import the English story voices using reclaimed pause time.

    python rebuild_voices.py <romfs-tree> <t1|t2> [--apply]

Every clip in the shipped patch that had to drop its sample rate to fit Capcom's
slot is a candidate to be rebuilt at a HIGHER rate, by shortening the silence
between phrases instead of degrading every sample. See gaptrim.py for why the
pauses are found with an energy envelope rather than an amplitude threshold.

MINIMUM GAIN RULE (1000 Hz). Trimming an actor's delivery is only worth it if
the fidelity actually improves. One clip in the sample set, DEMO_03010_0060_dbb,
could be "restored" from 32698 Hz to 32728 -- thirty hertz, inaudible -- at the
cost of a 100 ms pause cap that swallowed the breath markers in a rapid-fire
delivery and made the read sound spliced. Confirmed by ear. So a rebuild that
buys less than 1000 Hz is skipped and the clip is left exactly as it shipped.

The slot rule still governs: the result is padded back to Capcom's EXACT file
size, and the .stqr index is updated to agree with the new header or the stream
plays as silence.
"""
import os
import argparse
import re
import struct
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('AUDIO_TOOLS',
                                  os.environ.get('AUDIO_TOOLS', '.')))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import dsp                                                      # noqa: E402
import mca                                                      # noqa: E402
import gaptrim                                                  # noqa: E402

BS = chr(92)
PC = os.path.join(os.environ.get('TGAAC_STEAM', os.environ.get('TGAAC_STEAM', '')),
                  'nativeDX11x64', 'sound', 'stream', 'voice', 'wav')
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')
FULL = 32728
MIN_GAIN = 1000
QUIET = 150
STQR_BASE, STQR_STRIDE = 0x1C, 36


def decode(path, rate):
    r = subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', path,
                        '-ac', '1', '-ar', str(rate), '-f', 's16le', '-'],
                       capture_output=True)
    if not r.stdout:
        raise RuntimeError('ffmpeg failed on %s' % path)
    return np.frombuffer(r.stdout, dtype='<i2')


def edge(pcm):
    nz = np.nonzero(np.abs(pcm) > QUIET)[0]
    return pcm[nz[0]:nz[-1] + 1] if len(nz) else pcm


def stqr_names(blob):
    pat = ('sound' + BS + 'stream' + BS + 'voice' + BS + 'wav' + BS).encode()
    return [m.group(0).decode().split(BS)[-1]
            for m in re.finditer(re.escape(pat) + rb'[ -~]+', blob)]


def plan(name, slot_bytes, data_off, cur_rate):
    """-> (pcm, rate, floor) at the best rate that fits, or None to skip."""
    eng = os.path.join(PC, name + '_eng.sngw')
    if not os.path.exists(eng):
        return None
    # The encoded stream is padded up to a 64-byte boundary, so capacity has
    # to be figured from the largest whole 64-byte block that fits, not from
    # the raw byte count -- otherwise a clip that fits by samples overruns
    # once it is aligned.
    room = ((slot_bytes - data_off) // 64) * 64
    cap = (room // 8) * 14
    pcm = edge(decode(eng, FULL))
    out, floor = gaptrim.fit(pcm, FULL, cap)
    rate = FULL
    if len(out) > cap:
        rate = int(FULL * cap / len(out)) - 1
        out, floor = gaptrim.fit(edge(decode(eng, rate)), rate, cap)
        while len(out) > cap and rate > 8000:
            rate -= 200
            out, floor = gaptrim.fit(edge(decode(eng, rate)), rate, cap)
    if len(out) > cap:
        return None
    if rate - cur_rate < MIN_GAIN:
        return None
    return out, rate, floor


def build(donor_path, pcm, rate):
    donor = open(donor_path, 'rb').read()
    h = mca.parse(donor_path)
    adpcm, coefs = dsp.encode(np.asarray(pcm, dtype=np.int16))
    size = (len(adpcm) + 63) // 64 * 64
    if h['data_off'] + size > len(donor):
        raise AssertionError('overruns the slot')
    d = bytearray(donor[:h['data_off']])
    struct.pack_into('<I', d, 0x0C, len(pcm))
    struct.pack_into('<I', d, 0x10, rate)
    struct.pack_into('<I', d, 0x20, size)
    struct.pack_into('<16h', d, 0x38, *coefs)
    struct.pack_into('<4h', d, 0x58, h['gain'], h['ps'], 0, 0)
    d += adpcm + bytes(size - len(adpcm))
    d += bytes(len(donor) - len(d))
    assert len(d) == len(donor)
    return bytes(d), len(pcm), size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree')
    ap.add_argument('game', choices=('t1', 't2'))
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    vd = os.path.join(a.tree, 'sound', 'stream', 'voice')
    wav = os.path.join(vd, 'wav')

    done, skipped, updates = [], 0, {}
    for f in sorted(os.listdir(wav)):
        if not f.endswith('.mca'):
            continue
        name = f[:-4]
        if name.endswith('_nrt'):          # narration is page-timed; leave it
            skipped += 1
            continue
        p = os.path.join(wav, f)
        h = mca.parse(p)
        got = plan(name, os.path.getsize(p), h['data_off'], h['rate'])
        if not got:
            skipped += 1
            continue
        pcm, rate, floor = got
        blob, samples, size = build(p, pcm, rate)
        done.append((name, h['rate'], rate, floor))
        updates[name] = (size, samples, rate, h['samples'])
        if a.apply:
            open(p, 'wb').write(blob)

    print('  %s: rebuilt %d, left alone %d' % (a.game, len(done), skipped))
    for n, old, new, fl in sorted(done, key=lambda x: x[1])[:12]:
        print('     %-26s %5d -> %5d Hz  (+%4d, pauses capped at %dms)'
              % (n, old, new, new - old, int(fl * 1000) if fl else 0))
    if not a.apply:
        return

    synced = 0
    for st in [f for f in os.listdir(vd) if f.endswith('.stqr')]:
        path = os.path.join(vd, st)
        b = bytearray(open(path, 'rb').read())
        for i, nm in enumerate(stqr_names(bytes(b))):
            if nm not in updates:
                continue
            size, samples, rate, old_samples = updates[nm]
            o = STQR_BASE + i * STQR_STRIDE
            if struct.unpack_from('<I', b, o + 4)[0] != old_samples:
                raise AssertionError('%s record %d does not hold the expected '
                                     'sample count' % (st, i))
            struct.pack_into('<I', b, o + 4, samples)
            struct.pack_into('<I', b, o + 12, rate)
            synced += 1
        open(path, 'wb').write(bytes(b))
    if synced != len(done):
        raise SystemExit('synced %d index records for %d rebuilt clips -- these '
                         'must agree or the streams play silent'
                         % (synced, len(done)))
    print('  stqr index records updated: %d' % synced)


if __name__ == '__main__':
    main()

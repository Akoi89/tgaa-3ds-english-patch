# -*- coding: utf-8 -*-
"""Make every DLC voice stream fit Capcom's original byte slot.

WHY (measured in-game, not inferred):

  A stream larger than Capcom's original allocation is cut off at an
  unpredictable point. Measured on the emulator with azrig/playtime.ps1:

    file 4.10s, slot 3.81s (over by 0.29s)  -> played 0.98s
    file 4.47s, slot 3.91s (over by 0.56s)  -> played 1.86s
    file 5.44s, slot 3.32s (over by 2.12s)  -> played 2.77s
    file 9.04s, slot 9.18s (fits)           -> played 8.92s   <- full
    file 4.60s, slot 4.69s (fits)           -> played 4.52s   <- full

  So it is not "plays up to the slot length" -- exceeding the slot AT ALL
  corrupts playback. The rule is binary: fit, or be cut.

HOW: keep the whole English take and buy the space instead of cutting words.

  1. trim only true leading/trailing silence (never internal pauses -- those
     are the performance)
  2. if it now fits at 32728 Hz, keep full quality
  3. otherwise lower the sample rate just enough that the complete take fits

  The rate lives in both the .mca header and the .stqr record, and the game
  honours it: the 20 kHz test clip played 5.42s of a 5.44s take at correct
  pitch. Lower rate costs treble, not words.

Never sources audio by name alone. A candidate replacement must correlate with
what is already shipped, because reading a correlation backwards is how
Japanese audio once got published as a fix.

    python fit_slots.py --report     what would change, nothing written
    python fit_slots.py --apply      rewrite the .mca files and their indexes
"""
import os
import re
import struct
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

import dsp
import mca
from encode_shouts import decode_wav
from gallery_map import build as build_map

# Chronicles PC install: point TGAAC_STEAM at .../nativeDX11x64
SPECIAL = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'stream', 'special', 'wav')
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')   # set FFMPEG if it is not on PATH
OURS, CAPCOM = os.path.join(ROOT, 'bounce', 'rev'), os.path.join(ROOT, 'bounce', 'engd')
BS = chr(92)
REC, STRIDE = 0x1C, 0x24
BASE_RATE = 32728
QUIET = 150          # below this counts as silence for edge trimming


def corr(a, b):
    n = min(len(a), len(b))
    if n < 1000:
        return 0.0
    a = np.asarray(a[:n], float); b = np.asarray(b[:n], float)
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a ** 2).sum()) * np.sqrt((b ** 2).sum())
    return float((a * b).sum() / d) if d else 0.0


def resample(pcm, src_rate, dst_rate):
    """Proper resample through ffmpeg -- linear interpolation would alias."""
    if src_rate == dst_rate:
        return np.asarray(pcm, dtype=np.int16)
    fd, wav = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    fd, out = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    try:
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(src_rate)
            w.writeframes(np.asarray(pcm, dtype=np.int16).tobytes())
        subprocess.run([FFMPEG, '-y', '-i', wav, '-ar', str(dst_rate), out],
                       capture_output=True, check=True)
        with wave.open(out, 'rb') as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    finally:
        for p in (wav, out):
            try: os.remove(p)
            except OSError: pass


def trim_edges(pcm):
    nz = np.nonzero(np.abs(np.asarray(pcm)) > QUIET)[0]
    return np.asarray(pcm)[nz[0]:nz[-1] + 1] if len(nz) else np.asarray(pcm)


def source_pcm(name, ours_pcm, mapping):
    """Prefer Capcom's PC master; fall back to what we already ship.

    The PC file is only used if it is demonstrably the SAME recording we are
    already shipping -- that check is what stops a language swap."""
    m = mapping.get(name)
    if m:
        p = os.path.join(SPECIAL, m + '.sngw')
        if os.path.exists(p):
            cand = decode_wav(p, BASE_RATE)
            if corr(cand, ours_pcm) > 0.9:
                return np.asarray(cand, dtype=np.int16), 'PC master'
    return np.asarray(ours_pcm, dtype=np.int16), 'shipped audio'


def plan():
    mapping = build_map(quiet=True) if 'quiet' in build_map.__code__.co_varnames else build_map()
    jobs = []
    for dirpath, _, files in os.walk(OURS):
        for fn in sorted(files):
            if not fn.endswith('.mca'):
                continue
            ours_p = os.path.join(dirpath, fn)
            cap_p = ours_p.replace(os.sep + 'rev' + os.sep, os.sep + 'engd' + os.sep)
            if not os.path.exists(cap_p):
                continue
            if os.path.getsize(ours_p) <= os.path.getsize(cap_p):
                continue                                    # already fits
            oh = mca.parse_bytes(open(ours_p, 'rb').read())
            chh = mca.parse_bytes(open(cap_p, 'rb').read())
            ours_pcm = mca.decode(oh)
            pcm, origin = source_pcm(fn[:-4], ours_pcm, mapping)
            pcm = trim_edges(pcm)
            room = chh['data_size'] // 64 * 64
            capacity = room // 8 * 14
            rate = BASE_RATE if len(pcm) <= capacity else int(capacity / (len(pcm) / BASE_RATE))
            jobs.append(dict(name=fn[:-4], ours=ours_p, cap=cap_p, pcm=pcm, rate=rate,
                             capacity=capacity, origin=origin, cap_hdr=chh,
                             was=len(ours_pcm) / oh['rate'], keeps=len(pcm) / BASE_RATE))
    return jobs


def rebuild(job):
    cap = open(job['cap'], 'rb').read()
    ch = job['cap_hdr']
    pcm = resample(job['pcm'], BASE_RATE, job['rate'])[:job['capacity']]
    adpcm, coefs = dsp.encode(pcm)
    size = (len(adpcm) + 63) // 64 * 64
    if ch['data_off'] + size > len(cap):
        raise AssertionError('%s still overruns the slot' % job['name'])
    d = bytearray(cap[:ch['data_off']])
    struct.pack_into('<I', d, 0x0C, len(pcm))
    struct.pack_into('<I', d, 0x10, job['rate'])
    struct.pack_into('<I', d, 0x20, size)
    struct.pack_into('<16h', d, 0x38, *coefs)
    struct.pack_into('<4h', d, 0x58, ch['gain'], ch['ps'], 0, 0)
    d += adpcm + bytes(size - len(adpcm))
    d += bytes(len(cap) - len(d))                # pad back to Capcom's exact size
    return bytes(d), len(pcm)


def sync_index(sound_dir, name, size, samples, rate):
    """The index must agree with the header or the stream will not play."""
    hits = 0
    for fn in sorted(os.listdir(sound_dir)):
        if not fn.endswith('.stqr'):
            continue
        p = os.path.join(sound_dir, fn)
        b = bytearray(open(p, 'rb').read())
        names = [m.group(0).decode() for m in re.finditer(rb'AddOnContents[ -~]+', bytes(b))]
        touched = False
        for i, nm in enumerate(names):
            if nm.replace('/', BS).split(BS)[-1] != name:
                continue
            o = REC + i * STRIDE
            struct.pack_into('<II', b, o, size, samples)
            struct.pack_into('<I', b, o + 0x0C, rate)
            touched = True; hits += 1
        if touched:
            open(p, 'wb').write(bytes(b))
    return hits


def main():
    jobs = plan()
    if not jobs:
        print('every stream already fits its slot -- nothing to do')
        return
    apply_ = '--apply' in sys.argv
    print('%d streams exceed Capcom\'s slot\n' % len(jobs))
    print('%-26s %8s %8s %7s  %s' % ('clip', 'keeps', 'rate', 'quality', 'source'))
    for j in sorted(jobs, key=lambda x: x['rate']):
        print('%-26s %7.2fs %8d %6.0f%%  %s'
              % (j['name'], j['keeps'], j['rate'], j['rate'] * 100.0 / BASE_RATE, j['origin']))
    if not apply_:
        print('\n--report only; run with --apply to write')
        return
    print()
    for j in jobs:
        blob, n = rebuild(j)
        assert len(blob) == os.path.getsize(j['cap'])
        open(j['ours'], 'wb').write(blob)
        hits = sync_index(os.path.dirname(j['ours']), j['name'], len(blob), n, j['rate'])
        print('%-26s %d bytes, %d samples @ %d Hz, %d index entr%s'
              % (j['name'], len(blob), n, j['rate'], hits, 'y' if hits == 1 else 'ies'))
    print('\n%d streams rewritten' % len(jobs))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Which stereo layout do the crowd streams really use, and are the loops sane?

This project has two contradictory notes on record: stereo_bgm.py proved
per-FRAME L,R interleave for music (L/R corr .52 vs -.09 the other way), while
import_t2dlc_shouts.py found 256-BYTE BLOCKS per channel for DLC clips and says
a frame-interleaved build "played audibly garbled". import_21.py used per-frame.
Its round-trip check decoded with the same assumption it encoded with, which
proves nothing. This decodes CAPCOM'S originals both ways and lets the
left/right correlation say which layout is real, then decodes OUR built file
under that layout against Capcom's English master.

    python check_stereo.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))

import mca
from import_21 import CROWD, dec_channel, decode_english, english_source, find_one, corr
from resample import resample

JP = os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs')
OURS = os.path.join(HERE, '_tree21', 'TGAA2')
N = 120000          # samples per channel to decode; enough to judge, quick enough


def split(h, mode):
    """Return (L, R) ADPCM byte strings under one interleave hypothesis."""
    d = h['adpcm']
    if mode == 'frame':
        L = b''.join(d[i:i + 8] for i in range(0, len(d) - 7, 16))
        R = b''.join(d[i + 8:i + 16] for i in range(0, len(d) - 15, 16))
    else:
        L = b''.join(d[i:i + 256] for i in range(0, len(d) - 255, 512))
        R = b''.join(d[i + 256:i + 512] for i in range(0, len(d) - 511, 512))
    return L, R


def coefs(h, ch):
    import struct
    return list(struct.unpack_from('<16h', h['raw'], 0x38 + ch * 0x30))


def lr(h, mode, n):
    L, R = split(h, mode)
    a = dec_channel(L, coefs(h, 0), n).astype(np.float64)
    b = dec_channel(R, coefs(h, 1), n).astype(np.float64)
    return a, b


print('%-22s %8s %8s  %s' % ('Capcom original', 'frame', 'block', 'verdict'))
winner = {}
for name in CROWD:
    p = find_one(JP, name + '.mca')
    if not p:
        continue
    h = mca.parse(p)
    if h['channels'] != 2:
        print('%-22s mono, skipped' % name)
        continue
    n = min(N, h['samples'])
    cf = corr(*lr(h, 'frame', n))
    cb = corr(*lr(h, 'block', n))
    # wrong deinterleave hands the decoder a stream whose predictor state is
    # scrambled every frame: low or negative L/R correlation and blown peaks
    w = 'frame' if cf > cb else 'block'
    winner[name] = w
    print('%-22s %+8.3f %+8.3f  %s' % (name, cf, cb, w))

print('\nloop points (Capcom -> ours) and our file decoded under the WINNING layout '
      'against Capcom\'s English master:')
for name in CROWD:
    p = find_one(JP, name + '.mca'); q = find_one(OURS, name + '.mca')
    if not p or not q or name not in winner:
        continue
    hj, ho = mca.parse(p), mca.parse(q)
    src = english_source(name)
    chans, erate = decode_english(src, 2)
    ref = resample(chans[0], erate, ho['rate']).astype(np.float64)
    n = min(N, ho['samples'])
    ours_L, _ = lr(ho, winner[name], n)
    # our file may be edge-trimmed; align by best lag over a small window
    best = max(corr(ours_L, ref[k:k + n]) for k in range(0, min(len(ref) - n, 4000), 200)) \
        if len(ref) > n else corr(ours_L, ref)
    print('   %-22s loop %d..%d -> %d..%d   ours-vs-master corr %+.3f  (%s)'
          % (name, hj['loop_start'], hj['loop_end'], ho['loop_start'], ho['loop_end'],
             best, winner[name]))

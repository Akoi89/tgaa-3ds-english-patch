# -*- coding: utf-8 -*-
"""Are the crowd streams' stereo loops sane, decoded the way the game reads them?

SUPERSEDED 2026-09-22: this used to decode Capcom's originals two ways (per-frame
and per-256-byte-block) and let L/R correlation pick a "winner" per file, because
two notes on record disagreed (stereo_bgm.py's frame claim vs
import_t2dlc_shouts.py's block finding). That correlation test cannot actually
tell them apart: decoding real block data as per-frame still correlates, because
every "L" then holds even frames of BOTH real channels and every "R" holds the
odd frames of both. The corpus check (653 loose .mca under dgs2_base_romfs/sound;
see memory note mca-data-starts-at-0x34.md) found no Capcom file using per-frame
stereo -- always 256-byte blocks -- and import_anime.py independently confirmed
the same thing by ear. So this now just decodes the way the game does: data at
the header's own +0x34 offset (mca.parse already returns adpcm sliced from
there), 256-byte blocks per channel, no hypothesis test.

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
from import_21 import CROWD, dec_channel, deinterleave, decode_english, english_source, find_one, corr
from resample import resample

JP = os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs')
OURS = os.path.join(HERE, '_tree21', 'TGAA2')
N = 120000          # samples per channel to decode; enough to judge, quick enough


def coefs(h, ch):
    import struct
    return list(struct.unpack_from('<16h', h['raw'], 0x38 + ch * 0x30))


def lr(h, n):
    """(L, R) PCM, decoded from +0x34 in 256-byte blocks -- the way the game reads it."""
    L, R = deinterleave(h['adpcm'], 2, 'block')
    a = dec_channel(L, coefs(h, 0), n).astype(np.float64)
    b = dec_channel(R, coefs(h, 1), n).astype(np.float64)
    return a, b


print('%-22s %8s  %s' % ('Capcom original', 'block', 'notes'))
present = {}
for name in CROWD:
    p = find_one(JP, name + '.mca')
    if not p:
        continue
    h = mca.parse(p)
    if h['channels'] != 2:
        print('%-22s mono, skipped' % name)
        continue
    n = min(N, h['samples'])
    cb = corr(*lr(h, n))
    present[name] = True
    print('%-22s %+8.3f  L/R correlation, decoded from +0x34 in 256-byte blocks' % (name, cb))

print('\nloop points (Capcom -> ours) and our file decoded from +0x34 in 256-byte blocks '
      'against Capcom\'s English master:')
for name in CROWD:
    p = find_one(JP, name + '.mca'); q = find_one(OURS, name + '.mca')
    if not p or not q or name not in present:
        continue
    hj, ho = mca.parse(p), mca.parse(q)
    src = english_source(name)
    chans, erate = decode_english(src, 2)
    ref = resample(chans[0], erate, ho['rate']).astype(np.float64)
    n = min(N, ho['samples'])
    ours_L, _ = lr(ho, n)
    # our file may be edge-trimmed; align by best lag over a small window
    best = max(corr(ours_L, ref[k:k + n]) for k in range(0, min(len(ref) - n, 4000), 200)) \
        if len(ref) > n else corr(ours_L, ref)
    print('   %-22s loop %d..%d -> %d..%d   ours-vs-master corr %+.3f'
          % (name, hj['loop_start'], hj['loop_end'], ho['loop_start'], ho['loop_end'], best))

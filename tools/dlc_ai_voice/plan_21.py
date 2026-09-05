# -*- coding: utf-8 -*-
"""Feasibility for the 21 English recordings audit_526.py found unported.

For each one: locate Capcom's Japanese slot in the 3DS base romfs, decode
Capcom's English master, and work out whether the English fits the slot at
Capcom's own sample rate. Nothing is written -- this only measures.

Two families, and they are not the same problem:

  stream/se/wav/*_st.mca   STREAMED, named by sound/stream/se/bb_se.stqr.
                           The slot rule applies (fit_slots.py) and the index
                           must be updated with it or the cue plays silence.
  se/bb_se_ep03_dm_*/wav/  SE bank entries, named by .sbkr/.srqr, not .stqr.
                           Same class as the DLC's loose shouts: no stream
                           index, so the proven failure mode does not apply,
                           but growth has never been tested either.

    python plan_21.py
"""
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))

import mca
import msadpcm

STEAM = os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64')
JP_TREES = [('TGAA1', os.path.join(ROOT, 'dlc_story_audit', 'basegame', 'rom')),
            ('TGAA2', os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs'))]

CROWD = ['bb_benron_kaishi_st', 'bb_ronkoku_st', 'bsi_zawameki_st',
         'ks_complete_st', 'ks_failed_st', 'sprechchor_01_st', 'sprechchor_02_st']
DANCE = ['v_asg_cloak', 'v_asg_katana', 'v_asg_surprise_eye', 'v_asg_surprise_mask',
         'v_asg_umeki', 'v_dbb_cage', 'v_dbb_excite', 'v_dbb_lever', 'v_dbb_panic',
         'v_dbb_skip', 'v_nhd_surprise', 'v_nhd_surprise2', 'v_sst_run',
         'v_sst_surprise']


def find_one(root, name):
    for dirpath, _, files in os.walk(root):
        if name in files:
            return os.path.join(dirpath, name)
    return None


def english_source(name):
    """Capcom's English master for this cue, whichever container it uses."""
    for suffix in ('_eng.sngw', '_eng.xsew'):
        p = find_one(os.path.join(STEAM, 'sound'), name + suffix)
        if p:
            return p
    return None


def decode_english(path):
    """-> (channels, samples per channel, rate). PyAV handles the Ogg."""
    if path.endswith('.xsew'):
        pcm, rate = msadpcm.decode(path)
        return 1, len(pcm), rate
    import av
    c = av.open(path)
    s = c.streams.audio[0]
    rate = s.codec_context.sample_rate
    n = 0
    ch = s.codec_context.channels
    for f in c.decode(audio=0):
        n += f.to_ndarray().shape[1]
    return ch, n, rate


def adpcm_bytes(samples, channels):
    """DSP-ADPCM packs 14 samples into 8 bytes, per channel, padded to 64."""
    per = math.ceil(samples / 14) * 8
    return (per * channels + 63) // 64 * 64


def main():
    print('%-22s %-6s %4s %8s %8s %9s %9s  %s'
          % ('cue', 'game', 'ch', 'jp', 'english', 'slot', 'needed', 'verdict'))
    fits = grows = 0
    for group, names in (('stream (.stqr)', CROWD), ('SE bank (.sbkr)', DANCE)):
        print('\n-- %s --' % group)
        for name in names:
            src = english_source(name)
            if not src:
                print('%-22s no English master found' % name)
                continue
            ech, en, erate = decode_english(src)
            for game, tree in JP_TREES:
                jp = find_one(tree, name + '.mca')
                if not jp:
                    continue
                h = mca.parse(jp)
                slot = os.path.getsize(jp)
                # resampled to Capcom's rate, at Capcom's channel count
                samples = int(round(en / erate * h['rate']))
                need = h['data_off'] + adpcm_bytes(samples, h['channels'])
                ok = need <= slot
                fits += ok
                grows += not ok
                print('%-22s %-6s %4d %7.2fs %7.2fs %8d %8d  %s'
                      % (name, game, h['channels'], h['samples'] / h['rate'],
                         en / erate, slot, need,
                         'fits' if ok else 'OVER by %d bytes' % (need - slot)))
    print('\n%d slots fit at Capcom\'s own rate, %d would grow' % (fits, grows))


if __name__ == '__main__':
    main()

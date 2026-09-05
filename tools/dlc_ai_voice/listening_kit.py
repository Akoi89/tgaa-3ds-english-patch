# -*- coding: utf-8 -*-
"""A/B reference for the ear test: each crowd cue, Capcom's Japanese vs English.

Crowd murmur is nearly language-neutral by ear, so "is it English?" needs
something to compare against. This writes plain 16-bit WAVs of Capcom's own
Japanese 3DS original (decoded from the .mca in its true stereo layout) and
Capcom's English master (from Chronicles' .sngw), side by side.

    python listening_kit.py        -> _out/listen/<cue>_JP.wav, <cue>_EN.wav
"""
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))
import mca
from import_21 import CROWD, dec_channel, deinterleave, donor_layout, decode_english, english_source, find_one
import struct

GAME = sys.argv[1] if len(sys.argv) > 1 else 'TGAA1'
JP = {'TGAA1': os.path.join(ROOT, 'dlc_story_audit', 'basegame', 'rom'),
      'TGAA2': os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs')}[GAME]
OUT = os.path.join(HERE, '_out', 'listen', GAME)


def write(path, chans, rate):
    x = np.stack([np.asarray(c, dtype=np.int16) for c in chans], axis=1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(len(chans)); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(x.astype('<i2').tobytes())


os.makedirs(OUT, exist_ok=True)
for name in CROWD:
    jp = find_one(JP, name + '.mca')
    if not jp:
        continue
    h = mca.parse(jp)
    lay = donor_layout(h)
    streams = deinterleave(h['adpcm'], h['channels'], lay) if h['channels'] > 1 else [h['adpcm']]
    chans = [dec_channel(s, list(struct.unpack_from('<16h', h['raw'], 0x38 + i * 0x30)), h['samples'])
             for i, s in enumerate(streams)]
    write(os.path.join(OUT, name + '_JP.wav'), chans, h['rate'])
    en, erate = decode_english(english_source(name), 2)
    write(os.path.join(OUT, name + '_EN.wav'), en, erate)
    print('%-22s JP %5.2fs (%s)   EN %5.2fs' % (name, h['samples'] / h['rate'], lay, len(en[0]) / erate))
print('->', OUT)

# -*- coding: utf-8 -*-
"""Convert the 8 voice tracks that live in the MUSIC (bgm) stream tables.

dlc_all_voices.py collected its work list from *voice*.stqr only, so the one
interview track each issue keeps in its MUSIC gallery stayed Japanese -- the
user caught it in game. The mapping comes from Chronicles' own paired
special_bgm_{jpn,eng}.stqr: the 8 voice rows differ between the two files
(07_dlc_cv_200_sst -> dlc_music_01_07_v_sst_eng) while every real music row is
identical in both -- which is also the guard: ONLY rows whose English name
differs are converted, so music is never touched.

    python bgm_voices.py <root with idxN_dir trees> [--apply]
"""
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import mca
import stqr
from encode_shouts import decode_wav, rebuild_mca, MAX_GAIN

SPECIAL = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'stream', 'special')
SEP = chr(92)


def bgm_map():
    def names(p):
        d = open(p, 'rb').read()
        return [m.decode().split(SEP)[-1] for m in re.findall(rb'[ -~]{6,}', d)
                if b'wav' + SEP.encode() in m]
    jp = names(os.path.join(SPECIAL, 'special_bgm_jpn.stqr'))
    en = names(os.path.join(SPECIAL, 'special_bgm_eng.stqr'))
    assert len(jp) == len(en), (len(jp), len(en))
    return {a: b for a, b in zip(jp, en) if a != b}      # the differing 8 only


def main(root, apply=False):
    m = bgm_map()
    print('bgm-table voice rows with a differing English name: %d' % len(m))
    done = 0
    for sound_dir in sorted(glob.glob(os.path.join(root, 'idx*_dir', 'sound'))):
        idx = os.path.basename(os.path.dirname(sound_dir))
        for base, eng in sorted(m.items()):
            p = os.path.join(sound_dir, base + '.mca')
            if not os.path.exists(p):
                continue
            src = os.path.join(SPECIAL, 'wav', eng + '.sngw')
            h = mca.parse(p)
            ref = mca.decode(h)
            new = decode_wav(src, h['rate'])
            x = new.astype(np.float64)
            peak, refpeak = np.abs(x).max(), float(np.abs(ref).max())
            if peak > 0 and refpeak > 0:
                x *= min(refpeak / peak, MAX_GAIN)
            pcm = np.clip(x, -32768, 32767).astype(np.int16)
            print('  %-9s %-20s %6.2fs -> %6.2fs  <- %s'
                  % (idx, base, h['samples'] / h['rate'], len(pcm) / h['rate'], eng))
            if apply:
                data = rebuild_mca(h['raw'], pcm)   # encode BEFORE opening: open('wb')
                open(p, 'wb').write(data)           # truncates even if encoding then fails
                chk = mca.parse(p)
                got = mca.decode(chk)
                assert chk['rate'] == h['rate'] and len(got) == len(pcm)
                assert int(np.abs(got).max()) > 2000, base
            done += 1
    print('\n%d converted%s' % (done, '' if apply else '  (dry run -- pass --apply)'))
    if apply:
        print('\nsyncing every stream table...')
        stqr.main(root, True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--apply' in sys.argv))

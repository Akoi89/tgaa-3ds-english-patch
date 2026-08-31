# -*- coding: utf-8 -*-
"""Swap the DLC Audio-gallery voice tracks to Chronicles' English recordings.

The DLC's only voice files are gallery items, loose .mca under each content's
sound/ dir, named by gallery slot rather than by character:
    idx2  01_nhd_v_igiari, 02_nhd_v_matta      idx6  01_irs_v_igiari
    idx3  01_nhd_v_igiari                      idx7  01_asg_v_igiari
    idx4  01_sst_v_matta                       idx8  01_rkj_v_igiari
    idx5  01_hms_v_igiari
They are the SAME takes as the in-game shouts (durations match exactly,
including Iris's odd 1.29 s) but at 32728 Hz instead of 22050 -- the "Voice
Collection" is the hi-fi version. So the same Chronicles _eng source applies;
only the sample rate differs.

The character is identified by the 3-letter code in the middle of the name,
which is matched against Chronicles' own folders rather than hard-coded.

    python dlc_voices.py <romfs_root_dir> [--apply]
where romfs_root_dir holds idxN_dir/ trees extracted from the DLC.
"""
import glob
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import dsp
import mca
from encode_shouts import decode_wav, rebuild_mca, MAX_GAIN

STEAM = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'se')


def english_for(fname):
    """'01_nhd_v_igiari' -> the Chronicles _eng.xsew that holds the same take."""
    stem = os.path.splitext(os.path.basename(fname))[0]
    parts = stem.split('_')
    if len(parts) < 4 or parts[2] != 'v':
        return None
    code, kind = parts[1], '_'.join(parts[3:])
    hits = glob.glob(os.path.join(STEAM, '*', 'wav',
                                  '*_%s_v_%s_eng.xsew' % (code, kind)))
    return hits[0] if len(hits) == 1 else (hits[0] if hits else None)


def main(root, apply=False):
    targets = sorted(glob.glob(os.path.join(root, '*_dir', 'sound', '*_v_*.mca')))
    print('%d gallery voice tracks found' % len(targets))
    done = 0
    for p in targets:
        src = english_for(p)
        idx = os.path.basename(os.path.dirname(os.path.dirname(p)))
        name = os.path.basename(p)
        if not src:
            print('  -- no English source for %s' % name)
            continue
        h = mca.parse(p)
        ref = mca.decode(h)
        eng = decode_wav(src, h['rate'])
        x = eng.astype(np.float64)
        peak = np.abs(x).max()
        refpeak = float(np.abs(ref).max())
        if peak > 0 and refpeak > 0:
            x *= min(refpeak / peak, MAX_GAIN)
        pcm = np.clip(x, -32768, 32767).astype(np.int16)
        print('  %-10s %-20s %.2fs -> %.2fs  @%d Hz  <- %s'
              % (idx, name, h['samples'] / h['rate'], len(pcm) / h['rate'],
                 h['rate'], os.path.basename(src)))
        if apply:
            out = rebuild_mca(h['raw'], pcm)
            open(p, 'wb').write(out)
            chk = mca.parse(p)
            got = mca.decode(chk)
            assert chk['rate'] == h['rate'] and len(got) == len(pcm)
            assert int(np.abs(got).max()) > 3000, name
        done += 1
    print('\n%d converted%s' % (done, '' if apply else '  (dry run -- pass --apply)'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--apply' in sys.argv))

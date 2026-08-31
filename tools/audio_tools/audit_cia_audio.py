# -*- coding: utf-8 -*-
"""Full audio audit of a built DLC CIA -- the strongest offline check we have.

For every content: every .mca must parse, decode to AUDIBLE audio (peak and
RMS above silence), and every .stqr row that names a local file must carry that
file's exact size and sample count. The stale-table case is precisely the bug
that made v33 play silence, so this audit is the regression gate for it.

    python audit_cia_audio.py <split_root with idxN_dir trees>
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import mca
import stqr

SEP = chr(92)


def main(root):
    bad = 0
    files = 0
    for d in sorted(glob.glob(os.path.join(root, 'idx*_dir'))):
        idx = os.path.basename(d)
        sound = os.path.join(d, 'sound')
        if not os.path.isdir(sound):
            continue
        sizes = {}
        for p in sorted(glob.glob(os.path.join(sound, '*.mca'))):
            files += 1
            base = os.path.basename(p)[:-4]
            try:
                h = mca.parse(p)
                pcm = mca.decode(h).astype(np.float64)
            except Exception as ex:
                print('  !! %-10s %-24s does not decode: %s' % (idx, base, ex))
                bad += 1
                continue
            peak = int(np.abs(pcm).max())
            rms = float(np.sqrt((pcm ** 2).mean()))
            sizes[base] = (os.path.getsize(p), h['samples'])
            if peak < 1500 or rms < 100:
                print('  !! %-10s %-24s near-silent: peak %d rms %.0f' % (idx, base, peak, rms))
                bad += 1
        for st in sorted(glob.glob(os.path.join(sound, '*.stqr'))):
            _, _, es = stqr.parse(open(st, 'rb').read())
            for e2 in es:
                base = e2['name'].replace(SEP, '/').split('/')[-1]
                if base not in sizes:
                    continue          # streamed from the base game
                fs, smp = sizes[base]
                if e2['size'] != fs or e2['samples'] != smp:
                    print('  !! %-10s %-24s TABLE STALE: stqr %d/%d vs file %d/%d  (%s)'
                          % (idx, base, e2['size'], e2['samples'], fs, smp,
                             os.path.basename(st)))
                    bad += 1
    print('\n%d audio files audited, %d problems' % (files, bad))
    print('OK' if bad == 0 else 'FAILED')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

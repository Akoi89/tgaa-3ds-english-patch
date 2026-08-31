# -*- coding: utf-8 -*-
"""Swap EVERY DLC Audio-gallery voice track to Capcom's English recording.

Supersedes dlc_voices.py, which only handled the six shout tracks. The other
tracks are character lines too ("The quintessential look...", "This is an
outrage!"), and Capcom DID re-record them for Chronicles -- under new names, so
the mapping comes from pairing their own per-language .stqr tables rather than
from the filenames. See gallery_map.py.

Two sources of English audio:
  gallery lines  sound/stream/special/wav/dlc_voice_NN_MM_v_XXX_eng.sngw (Ogg)
  shouts         the same _eng.xsew used for the in-game shouts

After rewriting the .mca files this MUST be followed by stqr.py, because the
stream table repeats each file's size and sample count -- that is what made
v33 play silence.

    python dlc_all_voices.py <root with idxN_dir trees> [--apply]
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import mca
import stqr
from encode_shouts import decode_wav, rebuild_mca, steam_english, MAX_GAIN
from gallery_map import build as build_map, english_path

SEP = chr(92)


def source_for(basename):
    """3DS gallery track name -> path of Capcom's English recording."""
    eng = MAP.get(basename)
    if eng:
        p = english_path(eng)
        if p:
            return p, eng
    p = steam_english(basename)          # base-game-style chrNNN_..._jpn names
    if p:
        return p, os.path.basename(p)
    return None, None


MAP = build_map()


def main(root, apply=False):
    done = skipped = 0
    for sound_dir in sorted(glob.glob(os.path.join(root, 'idx*_dir', 'sound'))):
        idx = os.path.basename(os.path.dirname(sound_dir))
        tables = glob.glob(os.path.join(sound_dir, '*voice*.stqr'))
        wanted = set()
        for t in tables:
            _, _, es = stqr.parse(open(t, 'rb').read())
            for e in es:
                wanted.add(e['name'].replace(SEP, '/').split('/')[-1])
        for base in sorted(wanted):
            mpath = os.path.join(sound_dir, base + '.mca')
            if not os.path.exists(mpath):
                continue                      # streamed from the base game
            src, engname = source_for(base)
            if not src:
                print('  %-8s %-24s -- no English source' % (idx, base))
                skipped += 1
                continue
            h = mca.parse(mpath)
            ref = mca.decode(h)
            eng = decode_wav(src, h['rate'])
            x = eng.astype(np.float64)
            peak, refpeak = np.abs(x).max(), float(np.abs(ref).max())
            if peak > 0 and refpeak > 0:
                x *= min(refpeak / peak, MAX_GAIN)
            pcm = np.clip(x, -32768, 32767).astype(np.int16)
            print('  %-8s %-24s %5.2fs -> %5.2fs  <- %s'
                  % (idx, base, h['samples'] / h['rate'],
                     len(pcm) / h['rate'], engname))
            if apply:
                data = rebuild_mca(h['raw'], pcm)
                open(mpath, 'wb').write(data)
                chk = mca.parse(mpath)
                got = mca.decode(chk)
                assert chk['rate'] == h['rate'] and len(got) == len(pcm)
                assert int(np.abs(got).max()) > 2000, base
            done += 1
    print('\n%d converted, %d skipped%s'
          % (done, skipped, '' if apply else '  (dry run -- pass --apply)'))
    if apply:
        print('\nnow syncing the stream tables...')
        stqr.main(root, True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--apply' in sys.argv))

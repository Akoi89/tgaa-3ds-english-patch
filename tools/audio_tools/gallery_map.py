# -*- coding: utf-8 -*-
"""Work out which Chronicles English file replaces each 3DS DLC gallery track.

Capcom renamed the English re-recordings, so the names cannot be derived --
`02_dlc_cv_420_rkj` becomes `dlc_voice_06_02_v_rkj_eng`. But Chronicles ships a
Japanese AND an English .stqr for each of the six galleries, listing the same
tracks in the same order, so pairing them positionally gives Capcom's own
mapping.

The 3DS DLC's own voice tables list exactly the Japanese names in exactly the
same order, so the JP name is the join key.
"""
import glob
import os
import re
import sys

SPECIAL = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'stream', 'special')
SEP = chr(92)


def names(path):
    """Ordered wav basenames referenced by an .stqr."""
    d = open(path, 'rb').read()
    out = []
    for m in re.findall(rb'[ -~]{6,}', d):
        s = m.decode('ascii')
        if 'wav' + SEP in s:
            out.append(s.split(SEP)[-1])
    return out


def build():
    """{japanese basename: english basename}"""
    m = {}
    for jp in sorted(glob.glob(os.path.join(SPECIAL, 'special_voice_*_jpn.stqr'))):
        en = jp[:-len('_jpn.stqr')] + '_eng.stqr'
        if not os.path.exists(en):
            continue
        a, b = names(jp), names(en)
        if len(a) != len(b):
            print('  !! %s: %d jp vs %d eng entries, skipping'
                  % (os.path.basename(jp), len(a), len(b)))
            continue
        for x, y in zip(a, b):
            if x in m and m[x] != y:
                print('  !! %s maps to both %s and %s' % (x, m[x], y))
            m[x] = y
    return m


def english_path(eng_base):
    p = os.path.join(SPECIAL, 'wav', eng_base + '.sngw')
    return p if os.path.exists(p) else None


if __name__ == '__main__':
    m = build()
    print('%d japanese -> english pairs from Capcom\'s own tables\n' % len(m))
    missing = [k for k, v in m.items() if not english_path(v)]
    for k in sorted(m):
        mark = '' if english_path(m[k]) else '   <-- no file'
        print('  %-26s -> %s%s' % (k, m[k], mark))
    if missing:
        print('\n%d have no English file on disk' % len(missing))

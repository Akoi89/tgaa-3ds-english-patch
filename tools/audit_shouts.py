# -*- coding: utf-8 -*-
"""Which character shouts are still Japanese, and can they be fixed.

    python audit_shouts.py

A shout is an archived .mca whose member name contains '_v_' and ends '_jpn':
    sound/se/bb_se_chr040/wav/chr040_irs_v_igiari_jpn
Its English master sits in Chronicles at
    <steam>/nativeDX11x64/sound/se/<same folder>/wav/<same base>_eng.xsew
NOTE the path is sound/se, NOT sound/stream/se -- the streamed story voices live
under stream/, the shouts do not, and mixing the two reports zero matches.
"""
import os
import glob
import hashlib
import sys

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.arc import parse_arc

BS = chr(92)
PCSE = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'nativeDX11x64', 'sound', 'se')


def shouts(root):
    out = {}
    for ap in glob.glob(os.path.join(root, '**', '*.arc'), recursive=True):
        try:
            a = parse_arc(open(ap, 'rb').read())
        except Exception:
            continue
        for m in a['entries']:
            if m.data[:4] != b'MADP':
                continue
            n = m.name.replace(BS, '/')
            base = n.split('/')[-1].split('.')[0]
            if '_v_' in base and base.endswith('_jpn'):
                out[base] = (os.path.basename(ap), n, hashlib.md5(m.data).hexdigest())
    return out


def english_for(member):
    parts = member.replace(BS, '/').split('/')
    folder = next((p for p in parts if p.startswith(('go_se_', 'bb_se_'))), None)
    base = parts[-1].split('.')[0]
    if not (folder and base.endswith('_jpn')):
        return None
    for ext in ('.xsew', '.sngw'):
        p = os.path.join(PCSE, folder, 'wav', base[:-4] + '_eng' + ext)
        if os.path.exists(p):
            return p
    return None


for tag, ours, jp in (('TGAA1', 'build/vf/t1/romfs00', 'tut/t1jap/romfs'),
                      ('TGAA2', 'build/vf/t2/romfs00', 'tut/dgs2base/romfs')):
    O, J = shouts(ours), shouts(jp)
    swapped = [k for k in J if k in O and O[k][2] != J[k][2]]
    same = [k for k in J if k in O and O[k][2] == J[k][2]]
    absent = [k for k in J if k not in O]
    todo = same + absent
    fixable = [k for k in todo if english_for(J[k][1])]
    print('%s  %d shout clips in Capcom JP' % (tag, len(J)))
    print('    already English in our build : %d' % len(swapped))
    print('    still Japanese               : %d' % len(todo))
    print('    of those, English available  : %d' % len(fixable))
    for k in fixable[:8]:
        print('        %s' % k)
    if len(fixable) > 8:
        print('        ... and %d more' % (len(fixable) - 8))

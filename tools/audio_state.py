# -*- coding: utf-8 -*-
"""What is still Japanese after all the audio work, and why.

Counts every VOICE clip in each title and sorts it into: English now, or still
Japanese with the reason. Voice only -- BGM and sound effects are excluded, so
`sound/stream/bgm` and non `_v_` archive members do not inflate the totals.
"""
import glob, hashlib, os, sys
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.arc import parse_arc

BS = chr(92)
PCSE = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'nativeDX11x64', 'sound', 'se')
PCVO = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'nativeDX11x64', 'sound', 'stream', 'voice', 'wav')


def eng_shout(member):
    p = member.replace(BS, '/').split('/')
    f = next((x for x in p if x.startswith(('go_se_', 'bb_se_'))), None)
    b = p[-1].split('.')[0]
    if not (f and b.endswith('_jpn')):
        return None
    for e in ('.xsew', '.sngw'):
        q = os.path.join(PCSE, f, 'wav', b[:-4] + '_eng' + e)
        if os.path.exists(q):
            return q


def arch_shouts(root):
    d = {}
    for ap in glob.glob(os.path.join(root, '**', '*.arc'), recursive=True):
        try:
            a = parse_arc(open(ap, 'rb').read())
        except Exception:
            continue
        for m in a['entries']:
            if m.data[:4] != b'MADP':
                continue
            b = m.name.replace(BS, '/').split('/')[-1].split('.')[0]
            if '_v_' in b and b.endswith('_jpn'):
                d[b] = (hashlib.md5(m.data).hexdigest(), m.name)
    return d


def report(tag, ours, base, voice_dir=None):
    O, J = arch_shouts(ours), arch_shouts(base)
    eng = [k for k in J if k in O and O[k][0] != J[k][0]]
    jp = [k for k in J if k not in O or O[k][0] == J[k][0]]
    jp_fix = [k for k in jp if eng_shout(J[k][1])]
    print('%s' % tag)
    print('   shouts        : %3d total | %3d English | %3d Japanese (%d have an English master)'
          % (len(J), len(eng), len(jp), len(jp_fix)))
    if voice_dir:
        jv = sorted(glob.glob(os.path.join(base, voice_dir, '*.mca')))
        ov = {os.path.basename(p) for p in glob.glob(os.path.join(ours, voice_dir, '*.mca'))}
        done = [p for p in jv if os.path.basename(p) in ov]
        left = [p for p in jv if os.path.basename(p) not in ov]
        havee = [p for p in left
                 if os.path.exists(os.path.join(PCVO, os.path.basename(p)[:-4] + '_eng.sngw'))]
        print('   story voices  : %3d total | %3d English | %3d Japanese (%d have an English master)'
              % (len(jv), len(done), len(left), len(havee)))


report('TGAA1 base', 'build/vf/t1/romfs00', 'tut/t1jap/romfs')
report('TGAA2 base', 'build/vf/t2b7/romfs00', 'tut/dgs2base/romfs',
       'sound/stream/voice/wav')
report('TGAA1 DLC ', 'build/verify/t1d', 'dlccheck/t1dlc_up')
report('TGAA2 DLC ', 'build/verify/t2d', 'dlccheck/t2dlc_up')

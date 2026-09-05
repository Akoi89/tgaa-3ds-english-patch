"""Compare every shout clip (MADP entries) between Capcom's Japanese DLC tree and
our shipped tree: duration, first/last sample level, peak. Prints one row per entry."""
import os, sys, struct
ROOT = 'G:/Claude/TGAA 1-2/dlc_story_audit'
sys.path.insert(0, ROOT + '/arc_tools')
sys.path.insert(0, ROOT + '/audio_tools')
import arc, mca
import numpy as np

PAIRS = [('tgaa2/dlc/jp_idx1_dir', 'tgaa2/dlc/idx1_105_dir'),
         ('tgaa2/dlc/jp_idx2_dir', 'tgaa2/dlc/idx2_105_dir')]

def shouts(tree):
    out = {}
    for dp, _, fs in os.walk(os.path.join(ROOT, tree)):
        for fn in fs:
            if not fn.endswith('.arc'):
                continue
            p = os.path.join(dp, fn)
            try:
                _, _, es, _ = arc.entries(p)
            except AssertionError:
                continue
            for e in es:
                d = arc.decomp(e)
                if d[:4] != b'MADP':
                    continue
                h = mca.parse_bytes(d)
                pcm = np.asarray(mca.decode(h), dtype=np.int32)
                if pcm.ndim > 1:
                    pcm = pcm[:, 0]
                pk = max(1, int(np.abs(pcm).max()))
                out[(fn, e['name'])] = dict(dur=h['samples'] / h['rate'], rate=h['rate'],
                    size=len(d), first=abs(int(pcm[0])) * 100.0 / pk,
                    last=abs(int(pcm[-1])) * 100.0 / pk,
                    tail=float(np.abs(pcm[-50:]).max()) * 100.0 / pk, peak=pk)
    return out

for jp_t, en_t in PAIRS:
    if not os.path.isdir(os.path.join(ROOT, jp_t)):
        print('missing', jp_t); continue
    jp, en = shouts(jp_t), shouts(en_t)
    print('\n== %s vs %s: %d JP entries, %d EN entries' % (jp_t, en_t, len(jp), len(en)))
    print('%-14s %-34s %6s %6s %5s | %6s %6s %5s %5s %5s' % ('arc', 'entry', 'JPdur', 'ENdur', 'diff', 'rateEN', 'first%', 'last%', 'tail%', 'same'))
    for k in sorted(en):
        a, b = jp.get(k), en[k]
        same = 'JP' if a and a['size'] == b['size'] and abs(a['dur'] - b['dur']) < 1e-6 else 'EN'
        print('%-14s %-34s %6.2f %6.2f %+5.2f | %6d %6.1f %6.1f %5.1f %5s' % (
            k[0][:14], k[1].split('/')[-1][:34], a['dur'] if a else -1, b['dur'],
            (b['dur'] - a['dur']) if a else 0, b['rate'], b['first'], b['last'], b['tail'], same))

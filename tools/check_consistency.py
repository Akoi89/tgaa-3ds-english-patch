# -*- coding: utf-8 -*-
"""No two entries may show different wording for the same original line.

    python check_consistency.py <work-romfs> <shipped-romfs>

Catches the failure mode where a statement is reworded but its _MSG twin is
not, so the same testimony reads two ways depending on how the player reaches it.
"""
import os
import sys, os, glob, re, collections

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes

WRK, SHIP = sys.argv[1], sys.argv[2]
TAG = re.compile(r'<[^>]*>')


def vis(t):
    return ' '.join(TAG.sub('', t).split())


bad = []
for wp in sorted(glob.glob(os.path.join(WRK, '**', '*.gmd'), recursive=True)):
    rel = os.path.relpath(wp, WRK)
    sp = os.path.join(SHIP, rel)
    if not os.path.exists(sp):
        continue
    w = {(e['label'] or ''): e['text'] for e in parse_gmd_bytes(open(wp, 'rb').read())['entries']}
    s = {(e['label'] or ''): e['text'] for e in parse_gmd_bytes(open(sp, 'rb').read())['entries']}
    groups = collections.defaultdict(set)
    for lab, t in w.items():
        if lab not in s:
            continue
        wp_ = t.split('<PAGE>')
        sp_ = s[lab].split('<PAGE>')
        for i in range(min(len(wp_), len(sp_))):
            if vis(sp_[i]):
                groups[vis(sp_[i])].add(vis(wp_[i]))
    for old, news in groups.items():
        if len(news) > 1:
            bad.append((rel, old, sorted(news)))

print('  originals now rendered inconsistently : %d' % len(bad))
for rel, old, news in bad[:10]:
    print('     %s' % rel)
    print('        was : %s' % old[:100])
    for n in news:
        print('        now : %s' % n[:100])
sys.exit(1 if bad else 0)

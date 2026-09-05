# -*- coding: utf-8 -*-
"""How wide are TGAA2's conversation lines, measured the game's way?

Five clipped lines from a 2026-09-04 rig session are all ordinary <E041>
dialogue pages. pxwidth.py carries upstream's rule that such pages render at
~1.25x and get a 265-unit budget, while testimony/widgets get 365 (arrow 345).
This measures every visible line of every script page in the SHIPPED TGAA2
update against the font00 the console loads, classified by upstream's own
segment classifier, and reports the distribution -- so the fix is sized from
numbers, not from five screenshots.

    python sweep_dialogue.py [tree]     default: _shipped/TGAA2-base-1.0.13/content0
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
import pxwidth
from dgs2tool.gmd import parse_gmd_bytes

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
TREE = args[0] if args else os.path.join(HERE, '_shipped', 'TGAA2-base-1.0.13', 'content0')
BASE = os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs')
NEEDLES = ['flicker and falter', 'Court Record with the touch',
           'never be forgotten in the courtrooms', 'visiting student from the Empire',
           'indelibly associated']


def find(root, name):
    for dp, _, fs in os.walk(root):
        if name in fs:
            return os.path.join(dp, name)


if 'gfd' in opt:
    gfd = opt['gfd']; src = gfd
else:
    arc = find(TREE, 'UI_cmn_jpn.arc') or find(BASE, 'UI_cmn_jpn.arc')
    gfd = os.path.join(HERE, '_out', '_font00_%s.gfd' % os.path.basename(os.path.normpath(TREE)))
    pxwidth.font_from_arc(arc, gfd); src = arc
adv = pxwidth.advances(gfd)
print('font00 from %s  (%d glyph advances)' % (os.path.relpath(src, ROOT), len(adv)))

rows = []            # (px, budget, kind, file, label, page_idx, line)
five = []
for dp, _, fs in [t for sub in ('script', 'msg') for t in os.walk(os.path.join(TREE, sub))]:
    for fn in fs:
        if not fn.endswith('.gmd'):
            continue
        p = os.path.join(dp, fn)
        try:
            g = parse_gmd_bytes(open(p, 'rb').read())
        except Exception:
            continue
        rel = os.path.relpath(p, TREE).replace(os.sep, '/')
        for e in g['entries']:
            for i, page in enumerate(e['text'].split('<PAGE>')):
                if pxwidth.hand_laid_out(page):
                    continue
                budget = pxwidth.budget_for(page)
                kind = 'dialogue' if budget == pxwidth.DIALOGUE else 'widget'
                for line in pxwidth.lines(page):
                    w = pxwidth.px(line, adv)
                    rows.append((w, budget, kind, rel, e['label'], i, line))
                    if any(n in line for n in NEEDLES):
                        five.append((w, budget, kind, line))

print('\nthe five screenshot lines (all clipped on the rig):')
for w, b, k, line in five:
    print('   %4d px  budget %d (%s)  %s' % (w, b, k, line[:60]))

dl = [r for r in rows if r[2] == 'dialogue']
wd = [r for r in rows if r[2] == 'widget']
print('\n%d visible lines: %d on conversation pages, %d on widget/testimony pages'
      % (len(rows), len(dl), len(wd)))


def hist(rs, edges):
    c = collections.Counter()
    for r in rs:
        for lo, hi in edges:
            if lo <= r[0] < hi:
                c[(lo, hi)] += 1
    return c


edges = [(0, 200), (200, 265), (265, 300), (300, 345), (345, 365), (365, 400), (400, 9999)]
print('\nconversation-page line widths (px units):')
h = hist(dl, edges)
for lo, hi in edges:
    print('   %3d..%-4s %6d' % (lo, hi if hi < 9999 else 'inf', h[(lo, hi)]))
over265 = [r for r in dl if r[0] > 265]
over345 = [r for r in dl if r[0] > 345]
print('\nconversation lines over 265: %d   over 345: %d   (widest %d)'
      % (len(over265), len(over345), max(r[0] for r in dl) if dl else 0))
print('widget/testimony lines over 345: %d   over 365: %d'
      % (sum(r[0] > 345 for r in wd), sum(r[0] > 365 for r in wd)))
files = collections.Counter(r[3] for r in over265)
print('\nconversation lines over 265, by file (top 12 of %d files):' % len(files))
for f, n in files.most_common(12):
    print('   %5d  %s' % (n, f))

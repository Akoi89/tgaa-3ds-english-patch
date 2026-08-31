# -*- coding: utf-8 -*-
"""Build the review document for the 72 condensed captions.

For every caption: the official text, the condensed text, both widths, and a
preview of how the condensed version wraps in the Court Record's 4 x 199 px
box at full size. Duplicated texts (same wording under several labels) are
shown once with all their labels.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'audio_tools'))

from caption_width import arc, advances
from caption_fit import wrap
from condensed import CONDENSED

K = 'UI/0_system/00_font/font03_jpn.gfd'
adv, _ = advances(arc(os.path.join(HERE, '..', 'base_v12', 'romfs_dir',
                                   'archive', 'UI_cmn_jpn.arc'))[K])
W = lambda s: sum(adv.get(ord(c), 7) for c in s)
B = 796
LINE = 199

rows = json.load(open(os.path.join(HERE, 'over_budget.json'), encoding='utf-8'))

# group labels that share an original text
groups = {}
for r in rows:
    groups.setdefault(r['text'], []).append(r['label'])

out = []
out.append('# Condensed captions for review')
out.append('')
out.append('72 captions (63 unique texts) that exceed the Court Record\'s full-size budget of')
out.append('796 px, condensed so they render at full size. Names, first person and jokes are')
out.append('kept; only filler is cut. Veto anything you dislike and it stays as the official text.')
out.append('')
out.append('Each entry: labels, then OFFICIAL (width) / CONDENSED (width), then how the')
out.append('condensed version wraps in the 4-line box.')
out.append('')

n = 0
for text, labels in sorted(groups.items(), key=lambda kv: kv[1][0]):
    n += 1
    cond = CONDENSED[labels[0]]
    for lab in labels[1:]:
        assert CONDENSED[lab] == cond, (labels, 'inconsistent rewrite')
    wo, wc = W(text), W(cond)
    lines = wrap(cond, W, LINE)
    kind = 'profile' if labels[0].startswith('cast') else 'evidence'
    out.append('## %d. %s  [%s]' % (n, ', '.join(labels), kind))
    out.append('')
    out.append('**OFFICIAL** (%d px, shrunk to %.2f):' % (wo, B / wo))
    out.append('> %s' % text)
    out.append('')
    out.append('**CONDENSED** (%d px, %d lines, full size):' % (wc, len(lines)))
    out.append('> %s' % cond)
    out.append('')
    out.append('```')
    for l in lines:
        out.append('%-42s|' % l)
    out.append('```')
    out.append('')

path = os.path.join(HERE, 'CAPTION_REVIEW.md')
open(path, 'w', encoding='utf-8').write('\n'.join(out))
print('wrote %s  (%d unique captions)' % (path, n))

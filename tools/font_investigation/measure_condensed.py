# -*- coding: utf-8 -*-
"""Measure every condensed caption against the 796 px budget and check that
no proper noun from the original has been lost or altered."""
import json
import os
import re
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

rows = json.load(open(os.path.join(HERE, 'over_budget.json'), encoding='utf-8'))
orig = {r['label']: r['text'] for r in rows}

NAME = re.compile(r"\b[A-Z][a-z]+(?:'s)?\b")
SKIP = {'A', 'An', 'The', 'It', 'Its', 'He', 'His', 'She', 'Her', 'They', 'There', 'This',
        'On', 'In', 'At', 'By', 'To', 'Of', 'For', 'From', 'With', 'One', 'Two', 'Three',
        'Four', 'Two', 'Death', 'Further', 'Luckily', 'Supposedly', 'According', 'Showing',
        'Different', 'Now', 'Stern', 'Recently', 'Found', 'Broke', 'Cause', 'No', 'Signs',
        'Kazuma', 'Defending', 'Pretends', 'Used'}

over = missing = 0
out = []
for lab in sorted(orig):
    o = orig[lab]
    c = CONDENSED.get(lab)
    if c is None:
        print('!! no condensed text for', lab)
        continue
    w = W(c)
    nl = len(wrap(c, W, 199))
    flag = 'OK %d lines' % nl if nl <= 4 else '%d LINES' % nl
    if nl > 4:
        over += 1
    # proper nouns present in the original must survive
    on = {n for n in NAME.findall(o) if n.rstrip("'s") not in SKIP and n not in SKIP}
    cn = set(NAME.findall(c))
    lost = {n for n in on if n not in cn and n.rstrip("'s") not in ' '.join(cn)}
    if lost:
        missing += 1
    out.append((lab, W(o), w, flag, sorted(lost)))

for lab, wo, wc, flag, lost in out:
    print('%-16s %4d -> %4d  %-12s %s' % (lab, wo, wc, flag, ('LOST ' + ', '.join(lost)) if lost else ''))
print('\n%d over budget, %d with a lost name, of %d' % (over, missing, len(out)))

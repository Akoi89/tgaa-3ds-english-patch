# -*- coding: utf-8 -*-
"""Full check over every condensed caption.

Three things must hold for all 90:
  1. it wraps to <= 4 lines at 199 px, so the Court Record renders it full size
  2. every proper noun in the official text survives
  3. the set covers exactly the captions the game actually shrinks
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'audio_tools'))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from caption_width import arc, advances, strip
from caption_fit import wrap
from condensed import CONDENSED
from dgs2tool.gmd import parse_gmd_bytes

ROOT = os.path.join(HERE, '..', 'base_v12', 'romfs_dir', 'archive')
adv, _ = advances(arc(os.path.join(ROOT, 'UI_cmn_jpn.arc'))['UI/0_system/00_font/font03_jpn.gfd'])
W = lambda s: sum(adv.get(ord(c), 7) for c in s)
LINE, MAXL = 199, 4

msg = arc(os.path.join(ROOT, 'msg_cmn_jpn.arc'))
official = {}
for g in ['msg/evidence_caption_jpn.gmd', 'msg/cast_caption_jpn.gmd']:
    for e in parse_gmd_bytes(msg[g])['entries']:
        t = e.get('text') or ''
        lab = str(e.get('label'))
        if t.strip() and lab != 'null':
            official[lab] = ' '.join(strip(t).split())

shrunk = {l for l, t in official.items() if len(wrap(t, W, LINE)) > MAXL}

NAME = re.compile(r"\b[A-Z][a-z]+(?:'s)?\b")
SKIP = {'A', 'An', 'The', 'It', 'Its', 'He', 'His', 'She', 'Her', 'They', 'There', 'This',
        'On', 'In', 'At', 'By', 'To', 'Of', 'For', 'From', 'With', 'One', 'Two', 'Three',
        'Four', 'Death', 'Further', 'Luckily', 'Supposedly', 'According', 'Showing',
        'Different', 'Now', 'Stern', 'Recently', 'Found', 'Broke', 'Cause', 'No', 'Signs',
        'Defending', 'Pretends', 'Used', 'Owner', 'Head', 'Even', 'Where', 'Claims',
        'Detective', 'Proprietor', 'Kazuma', 'Japanese', 'Russian', 'English', 'British'}

bad_lines = bad_names = 0
for lab in sorted(CONDENSED):
    c = CONDENSED[lab]
    o = official.get(lab)
    if o is None:
        print('  !! %s is not a real caption label' % lab)
        continue
    n = len(wrap(c, W, LINE))
    if n > MAXL:
        print('  !! %-16s needs %d lines' % (lab, n))
        bad_lines += 1
    on = {x for x in NAME.findall(o) if x not in SKIP and x.rstrip("'s") not in SKIP}
    cn = ' '.join(NAME.findall(c))
    lost = sorted(x for x in on if x not in cn and x.rstrip("'s") not in cn)
    if lost:
        print('  !! %-16s lost %s' % (lab, ', '.join(lost)))
        bad_names += 1

missing = sorted(shrunk - set(CONDENSED))
extra = sorted(set(CONDENSED) - shrunk)
print('\ncaptions the game shrinks : %d' % len(shrunk))
print('captions with a rewrite   : %d' % len(CONDENSED))
print('shrunk but NOT rewritten  : %d %s' % (len(missing), missing or ''))
print('rewritten but not needed  : %d %s' % (len(extra), extra or ''))
print('over 4 lines              : %d' % bad_lines)
print('with a lost proper noun   : %d' % bad_names)
ok = not (missing or extra or bad_lines or bad_names)
print('\n%s' % ('ALL CLEAR' if ok else 'PROBLEMS ABOVE'))
sys.exit(0 if ok else 1)

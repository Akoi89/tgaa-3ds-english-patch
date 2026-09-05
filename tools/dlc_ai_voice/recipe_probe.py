# -*- coding: utf-8 -*-
"""Extract rc21's page-split recipe from the files, and show the target page raw.

rc21 split DLC `_sce08_c000_0010` `L_START_3` page 23 and it was verified on
the rig. The pre-split backup and the shipped file are both on disk, so the
diff between them is the recipe -- read it from bytes rather than from notes.
"""
import os
import re
import sys

ROOT = os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2')
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from dgs2tool.gmd import parse_gmd_bytes

PRE = os.path.join(ROOT, 'dlc_story_audit', 'tgaa2', 'dlc', '_orig_backup_ellipsis_20260903',
                   '_sce08_c000_0010_jpn.gmd.pre_pagesplit')
POST = os.path.join(ROOT, 'dlc_story_audit', 'tgaa2', 'dlc', 'idx2_105_dir', 'script',
                    '_sce08_c000_0010_jpn.gmd')


def entry(path, label):
    g = parse_gmd_bytes(open(path, 'rb').read())
    return next(e['text'] for e in g['entries'] if e['label'] == label)


if os.path.exists(PRE) and os.path.exists(POST):
    a = entry(PRE, 'L_START_3').split('<PAGE>')
    b = entry(POST, 'L_START_3').split('<PAGE>')
    print('rc21 L_START_3: %d pages -> %d pages' % (len(a), len(b)))
    # find the first page index where they diverge
    i = next(k for k in range(min(len(a), len(b))) if a[k] != b[k])
    print('\n--- BEFORE page %d ---' % i)
    print(repr(a[i]))
    print('\n--- AFTER page %d (A) ---' % i)
    print(repr(b[i]))
    print('\n--- AFTER page %d (B, new) ---' % (i + 1))
    print(repr(b[i + 1]))
    print('\n--- page %d before == page %d after? %s' % (i + 1, i + 2, a[i + 1] == b[i + 2]))
else:
    print('rc21 files not found:', PRE, POST)

print('\n==================== TARGET: TGAA2 _sce00_c001_0000 L_START_2 p6 (and p5, p7) ====================')
T = os.path.join(ROOT, 'dlc_ai_voice', '_tree21', 'TGAA2', 'script', '_output', '_sce00_c001_0000_jpn.gmd')
pages = entry(T, 'L_START_2').split('<PAGE>')
for k in (5, 6, 7):
    print('\n--- p%d ---' % k)
    print(repr(pages[k]))

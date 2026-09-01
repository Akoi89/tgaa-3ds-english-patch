# -*- coding: utf-8 -*-
"""Keep only the testimony fixes; put every other page back as shipped.

    python revert_nontestimony.py <work-romfs> <shipped-romfs>

WHY. The engine auto-paginates: an ordinary dialogue page authored with three
lines shows two, waits for A, then shows the rest. It also re-wraps a too-wide
authored line at its own break point. So on ORDINARY dialogue neither "3 lines"
nor "line too wide" is a defect, and rewording Capcom's text there is churn --
an earlier pass on this project already made that mistake once.

The exception, and the whole reason this work exists: a CROSS-EXAMINATION
STATEMENT is a rigid 2-page unit (page 0 opens <E008>, page 1 closes <E001>),
and the ceonstrained arrows step between STATEMENTS, not pages -- so its
continuation page is UNREACHABLE and any third line is lost. That is the bug
the user photographed, and it is the only one worth touching text for.

A statement is identified structurally, not by label: 2 pages, <E008> on page 0.
"""
import sys, os, glob, shutil

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

WRK, SHIP = sys.argv[1], sys.argv[2]


def ents(p):
    return parse_gmd_bytes(open(p, 'rb').read())


def is_statement(text):
    pages = text.split('<PAGE>')
    return len(pages) == 2 and '<E008>' in pages[0]


kept = reverted = 0
files = 0
for wp in sorted(glob.glob(os.path.join(WRK, '**', '*.gmd'), recursive=True)):
    rel = os.path.relpath(wp, WRK)
    sp = os.path.join(SHIP, rel)
    if not os.path.exists(sp) or open(wp, 'rb').read() == open(sp, 'rb').read():
        continue
    g = ents(wp)
    s = {(e['label'] or ''): e['text'] for e in ents(sp)['entries']}
    touched = False
    for e in g['entries']:
        lab = e['label'] or ''
        if lab not in s or s[lab] == e['text']:
            continue
        # judge by what the SHIPPED entry was, so a page we damaged is still
        # classified by its original structure
        if is_statement(s[lab]):
            kept += 1
        else:
            e['text'] = s[lab]
            reverted += 1
            touched = True
    if touched:
        open(wp, 'wb').write(build_gmd_bytes(g))
        files += 1

print('  testimony statements kept changed : %d' % kept)
print('  other entries put back as shipped : %d' % reverted)
print('  files rewritten                   : %d' % files)

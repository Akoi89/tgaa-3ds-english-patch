# -*- coding: utf-8 -*-
"""Collect every dialogue page that cannot fit the box, with references.

  python gather.py <ship-romfs> <font00.gfd> <out.json> [upstream] [scarlet] [jp]

TWO THINGS THAT WERE WRONG BEFORE, both of which shipped bugs:

  1. MEASURE IN PIXELS, NOT MODEL UNITS. textwidth.width() is a Helvetica-ratio
     model with a per-game calibration constant. TGAA1, TGAA2 and the TGAA2 DLC
     ship different font00 advances, so its cap does not transfer -- it passed a
     tree that still had 28 lines over the real budget. pxwidth reads the GFD
     the console loads. Budget is 365 px (senyarom's own reflow constant;
     independently confirmed by senyarom's DLC script topping out at exactly
     365 with zero lines over).

  2. FILTER ON THE BEST TWO-LINE SPLIT, NOT THE TOTAL. A page fits iff some word
     boundary gives max(line1, line2) <= budget. Filtering on total > 2*budget
     misses every statement whose words split unevenly -- that gap hid eight
     statements on the first pass.

Pages whose best split already fits need only a RE-WRAP (mechanical, no wording
change); the rest need condensing and are the ones that need drafts.
"""
import sys, os, glob, json, io

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.gmd import parse_gmd_bytes
from pxwidth import advances, px, lines, best_two_line, BUDGET

SHIP, GFD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
REFS = [('upstream', sys.argv[4] if len(sys.argv) > 4 else None),
        ('scarlet',  sys.argv[5] if len(sys.argv) > 5 else None),
        ('jp',       sys.argv[6] if len(sys.argv) > 6 else None)]
ADV = advances(GFD)


def ents(p):
    try:
        return {e['label']: e['text'] for e in parse_gmd_bytes(open(p, 'rb').read())['entries']
                if e['label']}
    except Exception:
        return {}


def page_text(root, rel, label, page):
    if not root:
        return None
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        c = glob.glob(os.path.join(root, '**', os.path.basename(rel)), recursive=True)
        if not c:
            return None
        p = c[0]
    t = ents(p).get(label)
    if t is None:
        return None
    pgs = t.split('<PAGE>')
    if page >= len(pgs):
        return None
    return ' '.join(' '.join(lines(pgs[page])).split()) or None


rows, seen = [], set()
for sp in sorted(glob.glob(os.path.join(SHIP, '**', '*.gmd'), recursive=True)):
    rel = os.path.relpath(sp, SHIP)
    for label, t in ents(sp).items():
        if not label.startswith('L_'):
            continue
        for i, pg in enumerate(t.split('<PAGE>')):
            ls = lines(pg)
            if not ls:
                continue
            now = max(px(l, ADV) for l in ls)
            body = ' '.join(' '.join(ls).split())
            best = best_two_line(body, ADV)
            if now <= BUDGET and len(ls) <= 2:
                continue
            key = (os.path.basename(rel), label, i)
            if key in seen:
                continue
            seen.add(key)
            r = dict(file=os.path.basename(rel), rel=rel, label=label, page=i,
                     official=body, now_px=now, best_px=best, over=best - BUDGET,
                     nlines=len(ls), kind='rewrap' if best <= BUDGET else 'condense')
            for tag, root in REFS:
                r[tag] = page_text(root, rel, label, i)
            rows.append(r)

with io.open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=1, ensure_ascii=False)

nc = [r for r in rows if r['kind'] == 'condense']
print('  budget            : %d px' % BUDGET)
print('  pages flagged     : %d   (rewrap %d, condense %d)'
      % (len(rows), len(rows) - len(nc), len(nc)))
print('  unique statements needing new wording : %d'
      % len({r['official'] for r in nc}))
if nc:
    print('  overage range     : %d .. %d px' % (min(r['over'] for r in nc),
                                                 max(r['over'] for r in nc)))

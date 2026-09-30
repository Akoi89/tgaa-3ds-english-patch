# -*- coding: utf-8 -*-
"""Issue #1 (2026-09-29): thoughts that run across a page break. Read-only.

Capcom (JP and Chronicles English) never ends a page with a thought bracket
still open. This lists every page in a tree where one does, carrying the
bracket depth across the pages of an entry, and measures what the Capcom-style
fix would cost: ')' appended to the last line of page A, '(' prepended to the
first line of page B.

    python bracket_audit.py <tree> <font00.gfd> <out.tsv> [--limit 345]
"""
import argparse, glob, os, re, sys
ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the project folder')
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pxwidth as P
from dgs2tool.gmd import parse_gmd_bytes

TAG = re.compile(r'<[^>]*>')


def vis_lines(page):
    return [l.strip() for l in TAG.sub('', page).replace('\r', '').split('\n') if l.strip()]


def depth_after(text, d):
    for ch in text:
        if ch == '(':
            d += 1
        elif ch == ')':
            d = max(0, d - 1)
    return d


ap = argparse.ArgumentParser()
ap.add_argument('tree'); ap.add_argument('gfd'); ap.add_argument('out')
ap.add_argument('--limit', type=int, default=345)
a = ap.parse_args()
adv = P.advances(a.gfd)
rows = []
for f in sorted(glob.glob(os.path.join(a.tree, '**', '*.gmd'), recursive=True)):
    try:
        g = parse_gmd_bytes(open(f, 'rb').read())
    except Exception:
        continue
    rel = os.path.relpath(f, a.tree)
    for e in g['entries']:
        pages = [p for p in re.split(r'(?=<E041)', e['text']) if '<E041' in p]
        d = 0
        for i, pg in enumerate(pages):
            lines = vis_lines(pg)
            if not lines:
                continue
            start = d
            body = TAG.sub('', pg)
            end = depth_after(body, d)
            b_side = start > 0 and not lines[0].startswith('(')
            a_side = end > 0
            if a_side or b_side:
                first_w = P.px(lines[0], adv)
                last_w = P.px(lines[-1], adv)
                new_first = P.px('(' + lines[0], adv) if b_side else first_w
                new_last = P.px(lines[-1] + ')', adv) if a_side else last_w
                if len(lines) == 1:
                    new_first = new_last = P.px(('(' if b_side else '') + lines[0] + (')' if a_side else ''), adv)
                worst_before = max(P.px(l, adv) for l in lines)
                worst_after = max([new_first, new_last] + [P.px(l, adv) for l in lines[1:-1]])
                rows.append(dict(file=rel, label=e['label'], page=i,
                                 side=('A' if a_side else '') + ('B' if b_side else ''),
                                 before=worst_before, after=worst_after,
                                 first=lines[0][:60], last=lines[-1][-60:]))
            d = end

with open(a.out, 'w', encoding='utf-8', newline='\n') as o:
    o.write('file\tlabel\tpage\tside\tworst_px_before\tworst_px_after\tfirst_line\tlast_line\n')
    for r in rows:
        o.write('%(file)s\t%(label)s\t%(page)d\t%(side)s\t%(before)d\t%(after)d\t%(first)s\t%(last)s\n' % r)
nA = sum('A' in r['side'] for r in rows)
nB = sum('B' in r['side'] for r in rows)
over_new = [r for r in rows if r['after'] > a.limit and r['before'] <= a.limit]
over_old = [r for r in rows if r['before'] > a.limit]
print('%s: pages touched %d (end inside a thought %d, continue a thought without "(" %d); '
      'would newly pass %d px: %d; already over before: %d'
      % (os.path.basename(a.tree.rstrip('/\\')), len(rows), nA, nB, a.limit, len(over_new), len(over_old)))

# -*- coding: utf-8 -*-
"""Plan (and, only when told, apply) rc21-style page splits for every
conversation page that cannot be re-split within two lines of <= LIMIT.

Runs the SAME planner and the SAME proofs as split_page.py on every page, and
adds the one check a batch needs that a single page did not: a split may not
leave a paired tag open across the new <PAGE> boundary. Report mode writes the
complete dry-run listing -- every split point, every re-stated tag -- to a file
for review. Nothing is written to a GMD without --apply.

    python split_pages_batch.py <tree> [--limit 345] [--report FILE] [--apply]
"""
import argparse
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pxwidth as P
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from fix_dlc_overflow import split_body, rewrap
from fix_dialogue_overflow import words_of
from split_page import plan_split, proofs, E800

# tags that open something a later tag closes; a split between them is refused
PAIRS = [(re.compile(r'<COL [0-9a-fA-F]+>'), '</COL>'),
         (re.compile(r'<RUBY>'), '</RUBY>'),
         (re.compile(r'<RB>'), '</RB>'),
         (re.compile(r'<RT>'), '</RT>')]


def unbalanced(page):
    for opener, closer in PAIRS:
        if len(opener.findall(page)) != page.count(closer):
            return True
    return False


def fits_two_lines(page, adv, limit):
    lines = P.lines(page)
    if max(P.px(l, adv) for l in lines) <= limit:
        return True
    words = words_of(split_body(page)[1])
    if len(words) < 2:
        return True                      # a single unbreakable word: not ours
    c = rewrap(words, adv, limit, 2)
    return c is not None and c[1] <= limit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree')
    ap.add_argument('--limit', type=int, default=345)
    ap.add_argument('--gfd', default=os.path.join(HERE, '_out', '_tgaa2_font00.gfd'))
    ap.add_argument('--report', default=os.path.join(HERE, '_out', 'split_plan.txt'))
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--include-widgets', action='store_true', help='also split hand-laid/widget pages (TGAA1 widget-overflow pass, 2026-09-05)')
    a = ap.parse_args()
    adv = P.advances(a.gfd)

    counts = collections.Counter()
    rows = []
    files = sorted(glob.glob(os.path.join(a.tree, 'script', '**', '*.gmd'), recursive=True))
    for f in files:
        raw = open(f, 'rb').read()
        try:
            g = parse_gmd_bytes(raw)
        except Exception as ex:
            counts['GMD did not parse -- NOT covered'] += 1
            print('   UNPARSED %s (%s)' % (os.path.relpath(f, a.tree), str(ex)[:60]))
            continue
        touched = False
        for e in g['entries']:
            txt = e['text'] or ''
            if P.is_statement(txt):
                continue
            pages = txt.split('<PAGE>')
            out = []
            for pi, page in enumerate(pages):
                lines = P.lines(page)
                if (not lines or max(P.px(l, adv) for l in lines) <= a.limit
                        or (not a.include_widgets and (P.hand_laid_out(page) or P.budget_for(page) != P.DIALOGUE))
                        or fits_two_lines(page, adv, a.limit)):
                    out.append(page)
                    continue
                counts['candidates'] += 1
                got = plan_split(page, adv, a.limit)
                if got is None:
                    counts['no split possible'] += 1
                    out.append(page)
                    continue
                pa, pb, wa, wb, lp, trailer_a = got
                why = proofs(page, pa, pb, lp, trailer_a)     # the same proofs as split_page.py
                if why:
                    why = 'proof: ' + why
                    counts[why] += 1
                    if counts[why] <= 3:
                        print('   %-48s %s %s p%d' % (why, os.path.basename(f), e['label'], pi))
                    out.append(page)
                    continue
                if unbalanced(pa) or unbalanced(pb):
                    counts['paired tag would straddle the split'] += 1
                    out.append(page)
                    continue
                counts['planned'] += 1
                rows.append((os.path.relpath(f, a.tree).replace(os.sep, '/'), e['label'], pi,
                             [(P.px(l, adv), l) for l in P.lines(pa)],
                             [(P.px(l, adv), l) for l in P.lines(pb)], lp))
                out.extend([pa, pb])
                touched = True
            if touched:
                e['text'] = '<PAGE>'.join(out)
        if touched:
            counts['files'] += 1
            if a.apply:
                open(f, 'wb').write(build_gmd_bytes(g))

    with open(a.report, 'w', encoding='utf-8') as w:
        w.write('page-split plan, limit %d, %s\n\n' % (a.limit, 'APPLIED' if a.apply else 'dry run'))
        for k, v in counts.most_common():
            w.write('%6d  %s\n' % (v, k))
        w.write('\n')
        for f, label, pi, la, lb, lp in rows:
            w.write('%s | %s | p%d | restates %s\n' % (f, label, pi, lp or '(nothing)'))
            for px, l in la:
                w.write('   A %3d  %s\n' % (px, l))
            for px, l in lb:
                w.write('   B %3d  %s\n' % (px, l))
    for k, v in counts.most_common():
        print('%6d  %s' % (v, k))
    print('listing -> %s' % a.report)
    if not a.apply:
        print('dry run; nothing written to any GMD')


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Re-split TGAA1 hand-laid and widget pages that overrun the 365-unit box.

Why this exists: the 2026-09-03 hardware playtest of the TGAA2 DLC showed text running
off the page on FOUR lines, and two of them sat on pages classified "hand-laid"
(<CNTR>, <SIZE, ruby) which every fitter skipped. The memory note's rule since then:
skip hand-laid pages for REFLOW decisions, never for the FIT CHECK, and treat the
365 widget budget as a few units too generous (366 and 368 clipped). TGAA1's base
game shipped 25 hand-laid pages over 365 (up to 404) and 4 widget pages over 365;
nobody had measured them because the conversation fitter skips them by design.

What it does: for every page that is NOT a cross-examination statement and NOT
standard dialogue (i.e. hand-laid or widget), whose widest line exceeds --limit,
re-break the words onto the same number of lines, or one more up to TWO lines,
so every line is <= --limit. Words and tags are never changed; a page is written
only if the tag-stripped word sequence is identical. Pages that cannot be made to
fit are reported, never touched.

    python fix_widget_overflow.py <tree> --gfd <font00.gfd> [--limit 355] [--apply] [--verbose]
"""
import argparse
import glob
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pxwidth as P                                             # noqa: E402
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes        # noqa: E402
from fix_dlc_overflow import split_body, rewrap                  # noqa: E402
from fix_dialogue_overflow import words_of                       # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree')
    ap.add_argument('--gfd', required=True)
    ap.add_argument('--limit', type=int, default=355)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    adv = P.advances(a.gfd)

    files = sorted(glob.glob(os.path.join(a.tree, 'script', '**', '*.gmd'), recursive=True))
    over = fixed = grew = unfixed = conv = 0
    kinds = {}
    for f in files:
        g = parse_gmd_bytes(open(f, 'rb').read())
        touched = False
        for e in g['entries']:
            txt = e['text'] or ''
            if P.is_statement(txt):
                continue
            pages = txt.split('<PAGE>')
            for pi, page in enumerate(pages):
                lines = P.lines(page)
                if not lines or max(P.px(l, adv) for l in lines) <= a.limit:
                    continue
                if not P.hand_laid_out(page) and P.budget_for(page) == P.DIALOGUE:
                    conv += 1          # conversation pages belong to fix_dialogue_overflow
                    continue
                over += 1
                kind = 'hand-laid' if P.hand_laid_out(page) else 'widget'
                prefix, body, suffix = split_body(page)
                words = words_of(body)
                got = None
                for n in (len(lines), len(lines) + 1):
                    if n < 2 or n > 2 or len(words) < n:
                        continue
                    cand = rewrap(words, adv, a.limit, n)
                    if cand and cand[1] <= a.limit:
                        got = (cand, n)
                        break
                seq = P.TAG.sub('', body.replace('\r\n', ' ')).split()
                tag = '%-9s %-26s %-18s p%-3d %3d' % (kind, os.path.basename(f)[:26], e['label'][:18], pi,
                                                     max(P.px(l, adv) for l in lines))
                if got is None:
                    unfixed += 1
                    kinds[(kind, 'unfixed')] = kinds.get((kind, 'unfixed'), 0) + 1
                    if a.verbose:
                        print('  UNFIXED %s  (%d lines, %d words)' % (tag, len(lines), len(words)))
                    continue
                new_body = '\r\n'.join(got[0][0])
                if P.TAG.sub('', new_body.replace('\r\n', ' ')).split() != seq:
                    unfixed += 1
                    if a.verbose:
                        print('  WORDSEQ CHANGED, skipped %s' % tag)
                    continue
                fixed += 1
                if got[1] > len(lines):
                    grew += 1
                kinds[(kind, 'fixed')] = kinds.get((kind, 'fixed'), 0) + 1
                if a.verbose:
                    print('  %s -> %3d  %d->%d lines' % (tag, got[0][1], len(lines), got[1]))
                pages[pi] = prefix + new_body + suffix
                touched = True
            if touched:
                e['text'] = '<PAGE>'.join(pages)
                e.pop('text_hex', None)
        if touched and a.apply:
            open(f, 'wb').write(build_gmd_bytes(g))
    print('hand-laid/widget pages over %d: %d   re-split: %d (%d grew 1->2 lines)   unfixed: %d   conversation pages over the limit (not mine): %d%s'
          % (a.limit, over, fixed, grew, unfixed, conv, '   (WRITTEN)' if a.apply else '   (dry run)'))
    for k in sorted(kinds):
        print('   %-9s %-8s %d' % (k[0], k[1], kinds[k]))


if __name__ == '__main__':
    main()

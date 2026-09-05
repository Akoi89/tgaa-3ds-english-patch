# -*- coding: utf-8 -*-
"""How under-filled is the TGAA2 DLC dialogue, and how much could be recovered?

    python measure_dlc_fill.py <dlc-romfs> <font00.gfd>

Reports, for every <PAGE> in every script entry:
  * line-width histogram against the 345 arrow limit
  * pages whose first line could take at least one more word (within-page refill)
  * consecutive page pairs that could be merged into one two-line page with no
    tag sitting on the boundary (suffix of page i and prefix of page i+1 both empty)
Read-only. Numbers only; no text is printed beyond first words for spot checks.
"""
import glob
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.environ.get('TGAA_ROOT', os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2')), r'dlc_icons\tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes            # noqa: E402
import pxwidth as P                                  # noqa: E402
from fix_dlc_overflow import split_body, words_of, rewrap   # noqa: E402

LIMIT = 345


def main():
    root, gfd = sys.argv[1], sys.argv[2]
    adv = P.advances(gfd)
    hist = {'0-200': 0, '200-265': 0, '265-345': 0, '345+': 0}
    pages = one = two = refill = 0
    merge_pairs = 0
    merge_chain_saved = 0
    entries = 0
    examples = []
    for f in sorted(glob.glob(os.path.join(root, 'script', '*.gmd'))):
        g = parse_gmd_bytes(open(f, 'rb').read())
        for e in g['entries']:
            txt = e['text'] or ''
            if '<PAGE>' not in txt and not P.lines(txt):
                continue
            entries += 1
            pg = txt.split('<PAGE>')
            parsed = []
            for page in pg:
                lines = P.lines(page)
                if not lines:
                    parsed.append(None)
                    continue
                pages += 1
                ws = [P.px(l, adv) for l in lines]
                for w in ws:
                    k = '0-200' if w < 200 else '200-265' if w < 265 else '265-345' if w <= 345 else '345+'
                    hist[k] += 1
                if len(lines) == 1:
                    one += 1
                elif len(lines) == 2:
                    two += 1
                prefix, body, suffix = split_body(page)
                words = words_of(body)
                # could line 1 take the first word of line 2?
                if len(lines) >= 2:
                    l2w = words_of(lines[1])
                    if l2w and P.px(P.TAG.sub('', lines[0] + ' ' + l2w[0]), adv) <= LIMIT:
                        refill += 1
                parsed.append((prefix, words, suffix, lines))
            # merge pairs: greedy chain, so the count is "pages saved", not pairs
            i = 0
            while i < len(parsed) - 1:
                a, b = parsed[i], parsed[i + 1]
                if a is None or b is None:
                    i += 1
                    continue
                clean = P.TAG.sub('', a[2]).strip() == '' and not P.TAG.search(a[2]) \
                    and not P.TAG.search(b[0]) and P.TAG.sub('', b[0]).strip() == ''
                if clean:
                    joined = a[1] + b[1]
                    cand = rewrap(joined, adv, LIMIT, 2) if len(joined) >= 2 else None
                    if cand and cand[1] <= LIMIT:
                        merge_pairs += 1
                        merge_chain_saved += 1
                        if len(examples) < 4:
                            examples.append((os.path.basename(f)[:20], e['label'][:18], i,
                                             ' '.join(P.TAG.sub('', w) for w in a[1])[:40]))
                        i += 2
                        continue
                i += 1
    print('entries %d   pages %d   1-line %d   2-line %d' % (entries, pages, one, two))
    print('line widths:', hist)
    print('pages whose line 1 could take one more word: %d' % refill)
    print('adjacent clean page pairs that fit one 2-line page at <=%d: %d  (pages saved if merged: %d, %.0f%% of pages)'
          % (LIMIT, merge_pairs, merge_chain_saved, 100.0 * merge_chain_saved / max(1, pages)))
    for x in examples:
        print('   e.g. %s %s p%d  "%s..."' % x)


if __name__ == '__main__':
    main()

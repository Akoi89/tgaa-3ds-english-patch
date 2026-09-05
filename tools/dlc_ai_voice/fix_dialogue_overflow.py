# -*- coding: utf-8 -*-
"""Re-split TGAA2 base-game CONVERSATION lines that overrun the page-advance arrow.

Found 2026-09-04 from five rig screenshots, then measured across the shipped
update: the base game was wrapped to the 365 widget budget on every page, and
7,530 conversation lines sit in the 345..365 band where the arrow clips them.
The five screenshots measure 356, 363, 363, 364, 365. Nothing shorter than 345
was seen clipping; the DLC width probe put the arrow at 345 and the box edge at
365, which is the same geometry.

This reuses testimony_pipeline/fix_dlc_overflow.py's machinery unchanged --
words are never altered, a page keeps its line count or grows by one (the
engine paginates a third line), and a page is rewritten only if every line ends
up <= LIMIT with the tag-stripped word sequence identical. Differences from the
DLC tool: it walks script/_output/, and it touches ONLY pages upstream's own
classifier calls standard dialogue (or interactive tutorial), never testimony,
never hand-laid-out pages, never rigid cross-examination statements. Those were
not what clipped, and this project has twice "fixed" clipping that was not
happening.

    python fix_dialogue_overflow.py <tree> [--limit 345] [--apply]
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

import pxwidth as P
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from fix_dlc_overflow import split_body, rewrap
import re

_TOK = re.compile(r'<[^>]*>|[^\s<]+|\s+')


def words_of(body):
    """Tokens a line break may fall between -- and ONLY those.

    The DLC tool's tokenizer treats a tag as a word boundary. The base game puts
    timing tags INSIDE words with no whitespace on either side:
        charring...<E003 14><E025 1.5><E346>must
    The engine sees one word there. Splitting it lets the re-splitter put a
    line break where no space exists, which the word-sequence check then
    rightly refuses -- 942 of 7,358 pages on the first pass. So: a tag run is
    glue unless whitespace separates it from the visible text on BOTH sides.
    Breaks land on real spaces, nowhere else.
    """
    toks = _TOK.findall(body.replace('\r\n', ' '))
    out = []
    prev_space = True
    for x in toks:
        if x.isspace():
            prev_space = True
            continue
        if out and not prev_space:
            out[-1] += x            # no whitespace before it: same word
        else:
            out.append(x)
        prev_space = False
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree')
    ap.add_argument('--limit', type=int, default=345)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--gfd', default=None, help='font00 .gfd to measure with (default: the TGAA2 base font)')
    ap.add_argument('--no-grow', action='store_true',
                    help='never add a line. A 3-line CONVERSATION page is NOT '
                         'paginated by the engine -- the third line draws below '
                         'the box and is clipped (seen on screen 2026-09-04, '
                         'TGAA2 Ep1 L_START_2 p6). The auto-paginate note was '
                         'proven on cross-examination pages only.')
    a = ap.parse_args()

    gfd = a.gfd or os.path.join(HERE, '_out', '_tgaa2_font00.gfd')
    if not os.path.exists(gfd):
        arc = None
        for dp, _, fs in os.walk(a.tree):
            if 'UI_cmn_jpn.arc' in fs:
                arc = os.path.join(dp, 'UI_cmn_jpn.arc')
        P.font_from_arc(arc, gfd)
    adv = P.advances(gfd)

    pat = os.path.join(a.tree, 'script', '**', '*.gmd')
    files = sorted(glob.glob(pat, recursive=True))
    over = fixed = grew = unfixed = skipped_kind = 0
    touched_files = 0
    unparsed = []
    for f in files:
        raw = open(f, 'rb').read()
        try:
            g = parse_gmd_bytes(raw)
        except Exception as ex:
            # a file that does not parse is a file this pass did not cover;
            # say so, never let the summary read as complete coverage
            unparsed.append((os.path.relpath(f, a.tree), str(ex)[:60]))
            continue
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
                if P.hand_laid_out(page) or P.budget_for(page) != P.DIALOGUE:
                    skipped_kind += 1
                    continue
                over += 1
                prefix, body, suffix = split_body(page)
                words = words_of(body)
                got = None
                # --no-grow means: never exceed TWO lines. Growing a single
                # line to two is a normal page; growing two to three is the
                # clipped third line. So allow n = 2 always, n = 3 never.
                options = (len(lines), len(lines) + 1)
                for n in options:
                    if n < 2 or n > (2 if a.no_grow else 3) or len(words) < n:
                        continue
                    cand = rewrap(words, adv, a.limit, n)
                    if cand and cand[1] <= a.limit:
                        got = (cand, n)
                        break
                seq = P.TAG.sub('', body.replace('\r\n', ' ')).split()
                if got is None:
                    unfixed += 1
                    if a.verbose:
                        print('  UNFIXED %-28s %-20s p%-3d %s'
                              % (os.path.basename(f)[:28], e['label'][:20], pi, lines[0][:50]))
                    continue
                (parts, width), n = got
                new_body = '\r\n'.join(parts)
                if P.TAG.sub('', new_body.replace('\r\n', ' ')).split() != seq:
                    unfixed += 1
                    continue
                fixed += 1
                grew += n > len(lines)
                pages[pi] = prefix + new_body + suffix
                touched = True
            if touched:
                e['text'] = '<PAGE>'.join(pages)
        if touched:
            touched_files += 1
            if a.apply:
                open(f, 'wb').write(build_gmd_bytes(g))

    print('conversation pages over %d: %d' % (a.limit, over))
    print('   re-split within the same line count: %d' % (fixed - grew))
    print('   re-split by adding a line (engine paginates): %d' % grew)
    print('   could not be brought under the limit: %d' % unfixed)
    print('non-conversation pages over the limit, deliberately left alone: %d' % skipped_kind)
    if unparsed:
        print('WARNING: %d GMD file(s) did not parse and were NOT covered:' % len(unparsed))
        for rel, why in unparsed:
            print('   %s  (%s)' % (rel, why))
    print('%d files %s' % (touched_files, 'rewritten' if a.apply else 'would change (report only)'))


if __name__ == '__main__':
    main()

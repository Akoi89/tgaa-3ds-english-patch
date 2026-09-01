"""
Project-wide consistency audit against the dialogue-box rules.

Scans every .gmd under one or more directories and reports, per file:
  - pages with more than 2 physical lines (clipped off the bottom)
  - lines wider than the box (clipped at the right edge)
  - ellipsis runs that are not 3/6/9 dots
  - ',...' and '...,' sequences

Width is only meaningful for Latin text -- Japanese uses fullwidth
glyphs that textwidth.py does not model -- so --no-width skips it and
checks structure only. Line COUNT is language-independent and is always
checked: it is a property of the box, not of the script.

Usage:
    python audit_all.py [--no-width] [--label NAME] <dir> [<dir>...]
"""
import os
import sys, os, re, glob, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from check_fit import pages_of, MAX_LINES_PER_PAGE, HARD_W, CNTR_HARD_W
from textwidth import width

TAG = re.compile(r'<[^>]*>')
DOTS = re.compile(r'\.{2,}')
BAD_PUNCT = re.compile(r',\.\.\.|\.\.\.,|[,]{2,}')
LATIN = re.compile(r'[A-Za-z]')


def audit(dirs, check_width=True, label=''):
    tall = []
    wide = []
    dot_bad = []
    punct_bad = []
    pages = lines = files = 0
    dot_hist = collections.Counter()

    for d in dirs:
        for fn in sorted(glob.glob(os.path.join(d, '**', '*.gmd'), recursive=True)):
            try:
                doc = parse_gmd_bytes(open(fn, 'rb').read())
            except Exception:
                continue
            files += 1
            short = os.path.relpath(fn, d)
            for e in doc['entries']:
                for is_cntr, ls in pages_of(e['text']):
                    if not ls:
                        continue
                    pages += 1
                    lines += len(ls)
                    if len(ls) > MAX_LINES_PER_PAGE:
                        tall.append((short, e['label'], ls))
                    if check_width:
                        cap = CNTR_HARD_W if is_cntr else HARD_W
                        for l in ls:
                            if LATIN.search(l) and width(l) > cap:
                                wide.append((short, e['label'], width(l), l))
                plain = TAG.sub('', e['text'])
                if check_width:      # Latin-script conventions only
                    for m in DOTS.finditer(plain):
                        n = len(m.group(0))
                        dot_hist[n] += 1
                        if n not in (3, 6, 9):
                            dot_bad.append((short, e['label'], n,
                                            plain[max(0, m.start()-30):m.end()+15]))
                    for m in BAD_PUNCT.finditer(plain):
                        punct_bad.append((short, e['label'], m.group(0),
                                          plain[max(0, m.start()-30):m.end()+15]))

    print(f'===== {label or dirs[0]} =====')
    print(f'{files} files, {pages} pages, {lines} lines')
    print(f'  pages over {MAX_LINES_PER_PAGE} lines : {len(tall)}')
    if check_width:
        print(f'  lines wider than box     : {len(wide)}')
        print(f'  odd ellipsis runs        : {len(dot_bad)}   (hist {dict(sorted(dot_hist.items()))})')
        print(f'  bad comma/ellipsis pairs : {len(punct_bad)}')
    for f, lab, ls in tall[:15]:
        print(f'   !! {len(ls)} LINES {f} :: {lab}')
        for l in ls:
            print(f'        {width(l):6d} | {l!r}')
    for f, lab, w, l in wide[:15]:
        print(f'   !! WIDE {w} {f} :: {lab}')
        print(f'        {l!r}')
    for f, lab, n, ctx in dot_bad[:10]:
        print(f'   ?  {n} dots {f} :: {lab}  {ctx!r}')
    for f, lab, g, ctx in punct_bad[:10]:
        print(f'   ?  {g!r} {f} :: {lab}  {ctx!r}')
    print()
    return len(tall), len(wide), len(dot_bad), len(punct_bad)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    check_width = '--no-width' not in args
    args = [a for a in args if a != '--no-width']
    label = ''
    if '--label' in args:
        i = args.index('--label')
        label = args[i+1]
        args = args[:i] + args[i+2:]
    audit(args, check_width, label)

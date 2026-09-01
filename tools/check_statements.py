# -*- coding: utf-8 -*-
"""The check that matters: no cross-examination statement may exceed 2 lines.

    python check_statements.py <romfs> [<baseline-romfs>]

A statement is a 2-page unit whose page 0 opens <E008>. Its page 1 is the
<E001> close. The arrows in cross-examination step between STATEMENTS, so a
third line -- which the engine would push to a continuation page -- is
UNREACHABLE and simply lost. Ordinary dialogue is exempt: there the engine
paginates and the player advances with A, so 3 lines is normal.
"""
import sys, os, glob, re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.gmd import parse_gmd_bytes

ROOT = sys.argv[1]
BASE = sys.argv[2] if len(sys.argv) > 2 else None


def lines(pg):
    return [l.strip() for l in re.sub(r'<[^>]*>', '', pg).replace('\r', '').split('\n') if l.strip()]


def statements(root):
    out = {}
    for p in sorted(glob.glob(os.path.join(root, '**', '*.gmd'), recursive=True)):
        try:
            g = parse_gmd_bytes(open(p, 'rb').read())
        except Exception:
            continue
        for e in g['entries']:
            pages = e['text'].split('<PAGE>')
            if len(pages) == 2 and '<E008>' in pages[0]:
                out[(os.path.relpath(p, root), e['label'] or '')] = pages
    return out


cur = statements(ROOT)
bad = [(k, lines(v[0])) for k, v in cur.items() if len(lines(v[0])) > 2]
print('  testimony statements found : %d' % len(cur))
print('  statements over 2 lines    : %d' % len(bad))
for k, ls in bad[:15]:
    print('     %s %s -> %d lines' % (k[0], k[1], len(ls)))
    for l in ls:
        print('        %s' % l)
if BASE:
    old = statements(BASE)
    was = sum(1 for k, v in old.items() if len(lines(v[0])) > 2)
    lost = [k for k in old if k not in cur]
    print('  baseline had over 2 lines  : %d' % was)
    print('  statements lost vs baseline: %d' % len(lost))
sys.exit(1 if bad else 0)

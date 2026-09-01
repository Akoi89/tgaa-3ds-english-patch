# -*- coding: utf-8 -*-
"""Overflow audit with the CORRECT per-segment budget.

    python audit.py <romfs> <font00.gfd> [label]

Classifies every page the way upstream's reflow does -- E041 conversation at
265, specialised widgets (testimony, narration) at 365, hand-laid-out <CNTR>/
<SIZE>/<RUBY> pages left alone -- then reports what overflows and whether a
re-wrap would fix it or the wording has to change.
"""
import os
import sys, os, glob

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.gmd import parse_gmd_bytes
from pxwidth import advances, px, lines, best_two_line, budget_for, hand_laid_out


def audit(root, gfd):
    adv = advances(gfd)
    rewrap, condense, three, skipped = [], [], [], 0
    for p in sorted(glob.glob(os.path.join(root, '**', '*.gmd'), recursive=True)):
        try:
            g = parse_gmd_bytes(open(p, 'rb').read())
        except Exception:
            continue
        for e in g['entries']:
            lab = e['label'] or ''
            if not lab.startswith('L_'):
                continue
            for i, pg in enumerate(e['text'].split('<PAGE>')):
                ls = lines(pg)
                if not ls:
                    continue
                if hand_laid_out(pg):
                    skipped += 1
                    continue
                cap = budget_for(pg)
                if len(ls) > 2:
                    three.append((os.path.basename(p), lab, i, len(ls)))
                now = max(px(l, adv) for l in ls)
                if now <= cap:
                    continue
                body = ' '.join(' '.join(ls).split())
                b = best_two_line(body, adv)
                rec = dict(now=now, best=b, cap=cap, file=os.path.basename(p),
                           rel=os.path.relpath(p, root), label=lab, page=i, text=body)
                (rewrap if b <= cap else condense).append(rec)
    return rewrap, condense, three, skipped


if __name__ == '__main__':
    rw, cd, th, sk = audit(sys.argv[1], sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else sys.argv[1]
    print('%-32s rewrap %3d   condense %3d   3-line %2d   hand-laid skipped %d'
          % (tag, len(rw), len(cd), len(th), sk))

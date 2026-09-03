# -*- coding: utf-8 -*-
"""Gate a condensed TGAA build before it is packed into a CIA.

  python verify.py <work-romfs> <shipped-romfs> <upstream-romfs> <CAP>

Four checks, all of which have caught a real shipped bug:

  1. LINES OVER CAP        horizontal clipping, measured in the game's own GFD
                           advances (pxwidth), NOT the Helvetica model -- the
                           three fonts in play differ by ~9% on common
                           lowercase so a model-unit cap does not transfer.
                           The absolute clip width is NOT settled: upstream's
                           265 flags thousands of pages in a build confirmed
                           good in-game. Pass a cap only when you have
                           calibrated one from a screenshot; left off, this
                           check is skipped and the structural checks below --
                           which are exact -- still run.
  2. STATEMENTS OVER 2     ONLY cross-examination statements are checked, and
                           this is the check that matters. The engine
                           auto-paginates: an ordinary dialogue page authored
                           with three lines shows two, waits for A, and shows
                           the rest -- not a defect, and an earlier pass on
                           this project wasted a build "fixing" 25 of them. A
                           STATEMENT is different: a rigid 2-page unit, page 0
                           opening <E008>, and the cross-examination arrows
                           step between STATEMENTS, so its continuation page
                           is unreachable and a third line is lost outright.
                           Ordinary 3-line pages are counted for information
                           only and never fail the gate.
  3. PAGE-COUNT DRIFT      two baselines, because they answer different things.
                           3a vs UPSTREAM, judged STRUCTURALLY: a
                           testimony STATEMENT is a rigid 2-page unit -- page 0
                           opens the green <E008>, page 1 closes it. An extra
                           page makes that text UNREACHABLE, because the
                           cross-examination arrows step between STATEMENTS, not
                           pages. This is what broke base 1.0.3.
                           3b vs SHIPPED, every L_EXAM label: catches a
                           regression introduced by THIS pass. The _TOITSU_OK
                           (Press) labels legitimately differ from upstream --
                           they are ordinary A-to-advance conversations and our
                           reflow already re-paginated them -- so they are only
                           checked against what we last shipped.
  4. GREEN TAG INTACT      no entry may end up with FEWER <E008> pages than the
                           build we shipped, or testimony renders in ordinary
                           white. Counted per entry, and compared against
                           SHIPPED rather than upstream: comparing page indices
                           against upstream reports 18 phantom losses, because
                           earlier passes merged two green pages into one and
                           every later index is then off by one.
"""
import os
import sys, os, glob, re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.environ.get('TGAA_TOOLS', '.'))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dgs2tool.gmd import parse_gmd_bytes
from pxwidth import advances, px, hand_laid_out, STATEMENT as STATEMENT_CAP

WRK, SHIP, UP, GFD = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
ADV = advances(GFD)
CAP = int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 9   # width gate optional


def lines(pg):
    return [l.strip() for l in re.sub(r'<[^>]*>', '', pg).replace('\r', '').split('\n') if l.strip()]


def ents(p):
    try:
        return {(e['label'] or ''): e['text']
                for e in parse_gmd_bytes(open(p, 'rb').read())['entries']}
    except Exception:
        return {}


def tree(root):
    """Every .gmd under root. Do NOT restrict to script/ -- the DLC keeps its
    scripts elsewhere, and a tree that globs to nothing makes every check below
    report a triumphant zero."""
    t = {os.path.relpath(p, root): p
         for p in glob.glob(os.path.join(root, '**', '*.gmd'), recursive=True)}
    if not t:
        raise SystemExit('no .gmd found under %s -- wrong path?' % root)
    return t


w_over, three_ours, three_theirs, drift, drift_ship, ungreen, changed = [], [], [], [], [], [], 0
info_three = 0
W, S, U = tree(WRK), tree(SHIP), tree(UP)
STATEMENT = re.compile(r'^L_EXAM_\d+$')
CAPTION = re.compile(r'(evidence|cast)_caption')     # Court Record widget: 4 lines


def is_statement(text):
    pages = text.split('<PAGE>')
    return len(pages) == 2 and '<E008>' in pages[0]

for rel, p in sorted(W.items()):
    wb = open(p, 'rb').read()
    if rel in S and open(S[rel], 'rb').read() != wb:
        changed += 1
    we, ue = ents(p), ents(U[rel]) if rel in U else {}
    se = ents(S[rel]) if rel in S else {}
    for label, t in we.items():
        label = label or ''
        pages = t.split('<PAGE>')
        up_text = ue.get(label)
        up_pages = up_text.split('<PAGE>') if up_text is not None else None
        for i, pg in enumerate(pages):
            ls = lines(pg)
            if not ls:
                continue
            if not hand_laid_out(pg):
                # Statements have their own, narrower, in-game-calibrated budget
                # (pxwidth.STATEMENT); everything else is judged at the passed CAP.
                cap = min(CAP, STATEMENT_CAP) if is_statement(t) else CAP
                for l in ls:
                    if px(l, ADV) > cap:
                        w_over.append((rel, label, i, px(l, ADV) - cap, l))
            if len(ls) > 2:
                if is_statement(t):
                    up = lines(up_pages[i]) if up_pages and i < len(up_pages) else []
                    (three_theirs if len(up) > 2 else three_ours).append((rel, label, i, ls))
                else:
                    info_three += 1
        # No label filter here. Statements are judged by SHAPE, because the
        # label tells you nothing: _sce03_c103_0070 L_TF_START is a genuine
        # 2-page <E008> unit carrying a present-evidence gate, and the old
        # ^L_EXAM_\d+$ rule walked straight past it while it sat split across
        # three pages in two shipped builds.
        if up_pages is None:
            continue
        # Judge by SHAPE, not by label. _sce03_c103_0070 L_TF_START is a real
        # 2-page <E008> statement carrying a present-evidence gate, and a
        # label-based rule (^L_EXAM_\d+$) walked straight past it while it sat
        # split across three pages in two shipped builds.
        if is_statement(up_text) and not is_statement(t):
            drift.append((rel, label, len(up_pages), len(pages)))
        # Moving BACK to upstream's page count is a repair, not a regression,
        # so 3b only fires when the result matches neither what we shipped nor
        # what upstream has.
        if label in se and (is_statement(se[label]) or is_statement(t)):
            n = len(se[label].split('<PAGE>'))
            if n != len(pages) and len(pages) != len(up_pages):
                drift_ship.append((rel, label, n, len(pages)))
        if label in se:
            was = sum(1 for p in se[label].split('<PAGE>') if '<E008>' in p)
            now = sum(1 for p in pages if '<E008>' in p)
            ups = sum(1 for p in up_pages if '<E008>' in p)
            # dropping to upstream's count is a repair: a page we had split
            # reopened <E008> on the continuation, and merging it back removes
            # that second opener, which is exactly what upstream has.
            if now < was and now != ups:
                ungreen.append((rel, label, '%d -> %d green pages' % (was, now)))

print('  TGAA BUILD GATE   cap %d units (statements %d)' % (CAP, min(CAP, STATEMENT_CAP)))
print('    1. lines over cap             : %d' % len(w_over))
print('    2. STATEMENTS over 2 lines    : %d' % len(three_ours))
print('       upstream already had       : %d  (pre-existing, untouched)' % len(three_theirs))
print('       ordinary 3-line pages      : %d  (fine - the engine paginates these)' % info_three)
print('    3a. statement drift vs upstream: %d' % len(drift))
print('    3b. statement drift vs shipped : %d' % len(drift_ship))
print('    4. pages that lost green <E008>: %d' % len(ungreen))
print('       files changed vs shipped   : %d' % changed)
for tag, rows in (('OVER CAP', w_over), ('STATEMENT >2 LINES', three_ours),
                  ('DRIFT vs UP', drift), ('DRIFT vs SHIP', drift_ship),
                  ('LOST GREEN', ungreen)):
    for r in rows[:12]:
        print('    %-15s %s' % (tag, r))
bad = len(w_over) + len(three_ours) + len(drift) + len(drift_ship) + len(ungreen)
print('\n  %s' % ('PASS' if not bad else 'FAIL - %d problem(s)' % bad))
sys.exit(1 if bad else 0)

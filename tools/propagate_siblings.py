# -*- coding: utf-8 -*-
"""Keep a statement's _MSG / _UPDATE twins reading the same as the statement.

    python propagate_siblings.py <work-romfs> <shipped-romfs>

A cross-examination statement usually has siblings in the same file carrying
the IDENTICAL wording -- L_EXAM_03_MSG, L_EXAM_03_UPDATE, L_EXAM_03_MSG_UPDATE
-- shown when the statement is pressed or revisited. They are not themselves
2-page <E008> units, so the "must fit 2 lines" rule does not apply to them and
they are exempt from condensing. But if the statement is reworded and they are
not, the player sees two different sentences for the same testimony.

So: match on the SHIPPED visible wording, not on the label. Any sibling whose
shipped text equalled the statement's shipped text inherits the new wording.
Line breaks are re-flowed at the same point; those boxes auto-paginate, so the
split is cosmetic there.
"""
import os
import sys, os, glob, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

WRK, SHIP = sys.argv[1], sys.argv[2]
TAG = re.compile(r'<[^>]*>')


def vis(t):
    return ' '.join(TAG.sub('', t).split())


def rewrap_like(pg, new_words, ref_lines):
    """Replace the page's words, splitting into the same number of lines."""
    m = re.match(r'^((?:<[^>]*>|\s)*)', pg)
    pre = m.group(1)
    rest = pg[len(pre):]
    t = re.search(r'((?:<[^>]*>|\s)*)$', rest)
    suf = t.group(1)
    body = rest[:len(rest) - len(suf)]
    if TAG.search(body):
        return None
    w = new_words.split()
    n = max(1, min(ref_lines, len(w)))
    per = (len(w) + n - 1) // n
    out = [' '.join(w[i:i + per]) for i in range(0, len(w), per)]
    return pre + '\r\n'.join(out) + suf


changed = 0
files = 0
for wp in sorted(glob.glob(os.path.join(WRK, '**', '*.gmd'), recursive=True)):
    rel = os.path.relpath(wp, WRK)
    sp = os.path.join(SHIP, rel)
    if not os.path.exists(sp):
        continue
    g = parse_gmd_bytes(open(wp, 'rb').read())
    s = {(e['label'] or ''): e['text'] for e in parse_gmd_bytes(open(sp, 'rb').read())['entries']}
    # statements in this file whose page-0 wording we changed
    newby = {}
    for e in g['entries']:
        lab = e['label'] or ''
        pages = e['text'].split('<PAGE>')
        if len(pages) != 2 or '<E008>' not in pages[0] or lab not in s:
            continue
        old0 = s[lab].split('<PAGE>')[0]
        if vis(old0) != vis(pages[0]):
            newby[vis(old0)] = vis(pages[0])
    if not newby:
        continue
    touched = False
    for e in g['entries']:
        lab = e['label'] or ''
        if lab not in s:
            continue
        pages = e['text'].split('<PAGE>')
        if len(pages) == 2 and '<E008>' in pages[0]:
            continue                                   # the statement itself
        for i, pg in enumerate(pages):
            old = vis(pg)
            if old not in newby:
                continue
            nl = len([l for l in TAG.sub('', pg).replace('\r', '').split('\n') if l.strip()])
            np = rewrap_like(pg, newby[old], nl)
            if np is None or np == pg:
                continue
            pages[i] = np
            changed += 1
            touched = True
        if touched:
            e['text'] = '<PAGE>'.join(pages)
    if touched:
        open(wp, 'wb').write(build_gmd_bytes(g))
        files += 1

print('  sibling pages brought into line : %d' % changed)
print('  files rewritten                 : %d' % files)

# -*- coding: utf-8 -*-
"""Apply condensed / re-wrapped dialogue to a romfs tree.

    python apply.py <work-romfs> <targets.json> <font00.gfd>

Two kinds of row, both handled here:
  kind=rewrap    the wording already fits two lines, it is just split at the
                 wrong point -- re-split it, change no words.
  kind=condense  no split fits; substitute the drafted wording, then split.

Control tags are preserved: the page's leading tags (which carry <E008>, the
green cross-examination colour) and its trailing tags are kept verbatim, and a
page with tags EMBEDDED in the body is refused rather than mangled.

Never adds a page. A testimony statement is a rigid 2-page unit -- page 0 opens
<E008>, page 1 closes it -- and the cross-examination arrows step between
STATEMENTS, not pages, so a third page is unreachable. That is what broke
TGAA2 base 1.0.3.
"""
import os
import sys, os, glob, re, json, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from pxwidth import advances, split_two, BUDGET
from drafts import DRAFTS
from drafts_px import DRAFTS_PX

WRK = sys.argv[1]
TARGETS = json.load(io.open(sys.argv[2], encoding='utf-8'))
ADV = advances(sys.argv[3])
ALL = dict(DRAFTS); ALL.update(DRAFTS_PX)
TAG = re.compile(r'<[^>]*>')


def rebuild_page(pg, new_text):
    m = re.match(r'^((?:<[^>]*>|\s)*)', pg)
    prefix = m.group(1)
    rest = pg[len(prefix):]
    t = re.search(r'((?:<[^>]*>|\s)*)$', rest)
    suffix = t.group(1)
    body = rest[:len(rest) - len(suffix)]
    if TAG.search(body):
        return None
    mw, a, b = split_two(new_text, ADV)
    if mw > BUDGET:
        return None
    return prefix + a + '\r\n' + b + suffix


changed_files, rewrapped, condensed, skipped = set(), 0, 0, []
for r in TARGETS:
    new = ALL.get(r['official'], r['official'] if r['kind'] == 'rewrap' else None)
    if new is None:
        skipped.append((r['file'], r['label'], 'no draft')); continue
    cand = glob.glob(os.path.join(WRK, '**', os.path.basename(r['rel'])), recursive=True)
    if not cand:
        skipped.append((r['file'], r['label'], 'file missing')); continue
    p = cand[0]
    g = parse_gmd_bytes(open(p, 'rb').read())
    hit = False
    for e in g['entries']:
        if e['label'] != r['label']:
            continue
        pages = e['text'].split('<PAGE>')
        if r['page'] >= len(pages):
            continue
        np = rebuild_page(pages[r['page']], new)
        if np is None:
            skipped.append((r['file'], r['label'], 'embedded tags / no split fits')); continue
        if np != pages[r['page']]:
            pages[r['page']] = np
            e['text'] = '<PAGE>'.join(pages)
            hit = True
    if hit:
        open(p, 'wb').write(build_gmd_bytes(g))
        changed_files.add(p)
        if r['kind'] == 'rewrap':
            rewrapped += 1
        else:
            condensed += 1
    elif not any(s[:2] == (r['file'], r['label']) for s in skipped):
        skipped.append((r['file'], r['label'], 'label not found / already correct'))

print('  pages re-wrapped     : %d' % rewrapped)
print('  pages re-worded      : %d' % condensed)
print('  files written        : %d' % len(changed_files))
print('  skipped              : %d' % len(skipped))
for s in skipped:
    print('     %-30s %-24s %s' % s)

# -*- coding: utf-8 -*-
"""Re-split statement pages whose body carries INLINE tags (pause <E003 n>, mid-line
<E008>, <E049>, <E025 x>), which apply.py refuses rather than mangle.

    python rewrap_tagged.py <work-romfs> <targets.json> <font00.gfd>

Only kind=rewrap rows: the words stay exactly as shipped, every tag stays attached to
the word it follows, and only the position of the single \\r\\n changes. The split is
chosen on the tag-stripped widths (pxwidth), the same fit test as everywhere else.
Rows that still cannot fit two lines at the row's budget are reported, not written.
"""
import os
import sys, os, glob, re, json, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from pxwidth import advances, px, BUDGET

WRK = sys.argv[1]
TARGETS = json.load(io.open(sys.argv[2], encoding='utf-8'))
ADV = advances(sys.argv[3])
TAG = re.compile(r'<[^>]*>')
TOKEN = re.compile(r'<[^>]*>|[^\s<]+|\s+')


def resplit(pg, budget):
    m = re.match(r'^((?:<[^>]*>|\s)*)', pg)
    prefix = m.group(1); rest = pg[len(prefix):]
    t = re.search(r'((?:<[^>]*>|\s)*)$', rest)
    suffix = t.group(1); body = rest[:len(rest) - len(suffix)]
    # words = runs of non-space text with their trailing tags glued on
    toks = [x for x in TOKEN.findall(body.replace('\r\n', ' ')) if not x.isspace()]
    words = []
    for x in toks:
        if TAG.fullmatch(x) and words:
            words[-1] += x
        else:
            words.append(x)
    if len(words) < 2:
        return None, px(TAG.sub('', body), ADV)
    best = None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        mw = max(px(TAG.sub('', a), ADV), px(TAG.sub('', b), ADV))
        if best is None or mw < best[0]:
            best = (mw, a, b)
    mw, a, b = best
    if mw > budget:
        return None, mw
    return prefix + a + '\r\n' + b + suffix, mw


done, still = [], []
for r in TARGETS:
    if r['kind'] != 'rewrap':
        continue
    cand = glob.glob(os.path.join(WRK, '**', os.path.basename(r['rel'])), recursive=True)
    if not cand:
        continue
    p = cand[0]
    g = parse_gmd_bytes(open(p, 'rb').read()); hit = False
    for e in g['entries']:
        if e['label'] != r['label']:
            continue
        pages = e['text'].split('<PAGE>')
        pg = pages[r['page']]
        body_has_tags = bool(TAG.search(re.sub(r'^((?:<[^>]*>|\s)*)', '', re.sub(r'((?:<[^>]*>|\s)*)$', '', pg))))
        if not body_has_tags:
            continue                      # apply.py handled it
        new, mw = resplit(pg, r.get('budget', BUDGET))
        if new is None:
            still.append((r['file'], r['label'], mw)); continue
        if new != pg:
            pages[r['page']] = new; e['text'] = '<PAGE>'.join(pages); hit = True
            done.append((r['file'], r['label'], mw))
    if hit:
        open(p, 'wb').write(build_gmd_bytes(g))
print('  tagged pages re-split : %d' % len(done))
for d in done: print('     %-30s %-24s -> %d px' % d)
print('  still over budget     : %d' % len(still))
for s in still: print('     %-30s %-24s best %d px' % s)

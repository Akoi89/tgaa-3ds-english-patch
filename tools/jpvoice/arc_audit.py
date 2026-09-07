# -*- coding: utf-8 -*-
"""Member-level diff of every changed .arc between our shipped romfs and the Japanese counterpart.

For the two update titles (archive/*.arc vs JP update, else cartridge) and the TGAA2 DLC content 2
(root *.arc vs JP DLC content 2). For each changed arc: which members differ, added, removed, and
the extension of each. Output jpvoice/arc_audit.json and a summary on stdout: per arc the counts of
differing members by extension, so the revert rule (whole-arc vs member-level) can be decided.
"""
import os, sys, io, json, hashlib, collections
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from dgs2tool.arc import parse_arc
HERE = os.path.join(ROOT, 'jpvoice'); TREES = os.path.join(HERE, '_trees')
rows = json.load(io.open(os.path.join(HERE, 'inventory.json'), encoding='utf-8'))


def members(p):
    a = parse_arc(open(p, 'rb').read())
    out = {}
    for e in a['entries']:
        ext = getattr(e, 'extension', None) or getattr(e, 'ext', None) or ''
        out[e.name] = (hashlib.md5(e.data).hexdigest(), str(ext), len(e.data))
    return out


def jp_path(title, ci, rel):
    g = title.split('_')[0]
    if title.endswith('_upd'):
        for lab in (g + '_jp_upd', g + '_jp_cart'):
            p = os.path.join(TREES, lab, 'c0', rel.replace('/', os.sep))
            if os.path.exists(p):
                return p
        return None
    p = os.path.join(TREES, g + '_jp_dlc', 'c%d' % ci, rel.replace('/', os.sep))
    return p if os.path.exists(p) else None


result = []
for r in rows:
    if r['bucket'] != 'changed' or not r['rel'].endswith('.arc'):
        continue
    ours = os.path.join(TREES, r['title'].split('_')[0] + '_ours_' + r['title'].split('_')[1], 'c%d' % r['content'], r['rel'].replace('/', os.sep))
    jp = jp_path(r['title'], r['content'], r['rel'])
    if jp is None:
        result.append(dict(title=r['title'], content=r['content'], rel=r['rel'], error='no JP counterpart')); continue
    try:
        mo, mj = members(ours), members(jp)
    except Exception as e:
        result.append(dict(title=r['title'], content=r['content'], rel=r['rel'], error=str(e))); continue
    diff = [n for n in mo if n in mj and mo[n][0] != mj[n][0]]
    added = [n for n in mo if n not in mj]
    removed = [n for n in mj if n not in mo]
    result.append(dict(title=r['title'], content=r['content'], rel=r['rel'], members_ours=len(mo), members_jp=len(mj),
                       diff=[(n, mo[n][1]) for n in diff], added=[(n, mo[n][1]) for n in added], removed=[(n, mj[n][1]) for n in removed]))
json.dump(result, io.open(os.path.join(HERE, 'arc_audit.json'), 'w', encoding='utf-8'), indent=0)
for x in result:
    if 'error' in x:
        print('%-10s c%d %-40s ERROR %s' % (x['title'], x['content'], x['rel'], x['error'])); continue
    c = collections.Counter(e for _, e in x['diff'])
    print('%-10s c%d %-40s members %4d/%4d  diff %s  added %d removed %d' % (x['title'], x['content'], x['rel'], x['members_ours'], x['members_jp'], dict(c) or '{}', len(x['added']), len(x['removed'])))
    if x['added'] or x['removed']:
        print('      added:', x['added'][:8], ' removed:', x['removed'][:8])
# one sample member name so the extension convention is visible
for x in result:
    if 'diff' in x and x['diff']:
        print('sample differing member names:', x['diff'][:3]); break

# -*- coding: utf-8 -*-
"""Prove an archive rebuild changed ONLY what it meant to.

    python audit_archives.py <ours-romfs> <baseline-romfs>

build_arc_bytes() recomputes every entry offset, so a rebuild touches the whole
file. Verifying the members you replaced says nothing about the hundreds you did
not: a textures-and-models archive that silently lost a member still parses, and
the loss only shows up as a missing character on screen.

So: every member of every rebuilt archive is compared against the baseline, and
anything that changed which is NOT an audio clip we intended to replace is a
failure.
"""
import glob
import hashlib
import os
import sys

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.arc import parse_arc

# An archive we ADD to the update exists in ours and not in the baseline. Those
# are precisely the ones a rebuild touches, so falling through on "not in the
# baseline" audits nothing -- compare them against Capcom's original instead.
OURS, BASE = sys.argv[1], sys.argv[2]
ORIGIN = sys.argv[3] if len(sys.argv) > 3 else None
ALLOW = set(sys.argv[4].split(',')) if len(sys.argv) > 4 else set()
BS = chr(92)


def members(p):
    try:
        a = parse_arc(open(p, 'rb').read())
    except Exception as e:
        return None, str(e)
    return {m.name: hashlib.md5(m.data).hexdigest() for m in a['entries']}, None


rebuilt = unreadable = 0
lost, added, changed_audio, changed_other = [], [], [], []
for op in sorted(glob.glob(os.path.join(OURS, '**', '*.arc'), recursive=True)):
    rel = os.path.relpath(op, OURS)
    bp = os.path.join(BASE, rel)
    kind = 'vs shipped'
    if not os.path.exists(bp):
        if not ORIGIN:
            continue
        bp = os.path.join(ORIGIN, rel)
        kind = 'newly added'
        if not os.path.exists(bp):
            added.append((rel, '<no origin to compare>')); continue
    if open(op, 'rb').read() == open(bp, 'rb').read():
        continue
    rebuilt += 1
    O, e1 = members(op)
    B, e2 = members(bp)
    if O is None or B is None:
        unreadable += 1
        print('  UNREADABLE %s: %s' % (rel, e1 or e2))
        continue
    lost += [(rel, k) for k in B if k not in O]
    added += [(rel, k) for k in O if k not in B]
    for k in set(O) & set(B):
        if O[k] == B[k]:
            continue
        base = k.replace(BS, '/').split('/')[-1].split('.')[0]
        if '_v_' in base and base.endswith('_jpn'):
            changed_audio.append((rel, base))
        elif k not in ALLOW:
            changed_other.append((rel, k))

print('  archives rebuilt vs baseline   : %d' % rebuilt)
print('  unreadable after rebuild       : %d' % unreadable)
print('  members LOST                   : %d' % len(lost))
print('  members ADDED                  : %d' % len(added))
print('  audio members changed (wanted) : %d' % len(changed_audio))
print('  OTHER members changed          : %d' % len(changed_other))
for r, k in (lost + added + changed_other)[:10]:
    print('     %-26s %s' % (r, k))
bad = unreadable + len(lost) + len(added) + len(changed_other)
print('\n  %s' % ('PASS' if not bad else 'FAIL - %d problem(s)' % bad))
sys.exit(1 if bad else 0)

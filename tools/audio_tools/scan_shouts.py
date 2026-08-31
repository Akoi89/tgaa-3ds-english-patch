# -*- coding: utf-8 -*-
"""Enumerate the 3DS shout voice entries and check Chronicles coverage."""
import os, sys, re, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'arc_tools'))
from arc import entries

ROOT = 'basegame/rom'
STEAM = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'se')
SEP = chr(92)

found = {}
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if not f.endswith('.arc'):
            continue
        p = os.path.join(dp, f)
        try:
            _, _, es, _ = entries(p)
        except Exception:
            continue
        for e in es:
            n = e['name']
            if '_v_' in n and (SEP + 'wav' + SEP) in n:
                found.setdefault(n.split(SEP)[-1], set()).add(f)

arcs = {a for v in found.values() for a in v}
print('3DS: %d unique shout names across %d character archives' % (len(found), len(arcs)))
have, missing = 0, []
for name in sorted(found):
    eng = name.replace('_jpn', '_eng') + '.xsew'
    if glob.glob(os.path.join(STEAM, '*', 'wav', eng)):
        have += 1
    else:
        missing.append(name)
print('English counterpart in Chronicles: %d / %d' % (have, len(found)))
if missing:
    print('missing (%d):' % len(missing))
    for m in missing:
        print('   ', m)
print()
kinds = {}
for n in found:
    k = re.sub(r'^chr\d+_[a-z]+_v_', '', n).replace('_jpn', '')
    kinds[k] = kinds.get(k, 0) + 1
for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
    print('  %-18s %d' % (k, v))
tot = sum(os.path.getsize(os.path.join(ROOT, 'archive', a)) for a in arcs)
print('\ncombined size of the %d archives that would ship in the overlay: %.1f MB'
      % (len(arcs), tot / 1024 / 1024))

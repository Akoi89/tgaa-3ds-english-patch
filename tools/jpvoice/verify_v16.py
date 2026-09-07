# -*- coding: utf-8 -*-
"""Gate for the v1.6 updates: extract each new update CIA and the released v1.5 one, and prove that
every file that differs is intended: the 8 shout atlases (hash-matched to jpvoice/_cutin/new), the
version stamp (TGAA2 title atlas; TGAA1's stamp is in the code, outside the romfs), and the ported
texture archives, each differing only in .tex members named in jpvoice/_v16/port_report.json.
Exit 1 on anything else. Usage: python jpvoice\verify_v16.py"""
import os, sys, io, json, hashlib, shutil
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline')); sys.path.insert(0, os.path.join(ROOT, 'jpvoice')); sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from cia import Cia
from inventory import romfs_of_ncch, extract_romfs, walk, h
from dgs2tool.arc import parse_arc
rep = json.load(open(os.path.join(ROOT, 'jpvoice', '_v16', 'port_report.json'), encoding='utf-8'))
allowed = {}
for r in rep:
    arc, member = (r['loc'].split('::') + [None])[:2]
    allowed.setdefault((r['game'], arc), set()).add(member)
NEWTEX = {hashlib.sha256(open(os.path.join(ROOT, 'jpvoice', '_cutin', 'new', 'bigfont_%s_GSM_NOMIP.tex' % n), 'rb').read()).hexdigest()
          for n in ['default', 'gift', 'hay', 'here', 'say', 'uk_default', 'uk_wait', 'wait']}
ok_all = True
for g, old, new, ver in (('TGAA1', r'Final\_CURRENT\TGAA1-base-3.2.2.cia', r'jpvoice\_v16\TGAA1-base-3.2.3.cia', (3, 2, 3)),
                         ('TGAA2', r'Final\_CURRENT\TGAA2-base-1.0.15.cia', r'jpvoice\_v16\TGAA2-base-1.0.16.cia', (3, 1, 0))):
    n = Cia(os.path.join(ROOT, new)); o = Cia(os.path.join(ROOT, old))
    problems = []
    if n.version() != ver: problems.append('version %s' % (n.version(),))
    d15 = os.path.join(ROOT, 'jpvoice', '_v15tree_' + g.lower()); d16 = os.path.join(ROOT, 'jpvoice', '_verify16', g)
    if not os.path.isdir(d15): extract_romfs(romfs_of_ncch(o.contents[0]), d15)
    shutil.rmtree(d16, ignore_errors=True); extract_romfs(romfs_of_ncch(n.contents[0]), d16)
    t15, t16 = walk(d15), walk(d16); tc = walk(os.path.join(ROOT, 'jpvoice', '_trees', g + '_jp_cart', 'c0'))
    for rel in sorted(set(t15) - set(t16)): problems.append('MISSING ' + rel)
    lines = []
    for rel in sorted(set(t16)):
        if rel in t15 and h(t16[rel]) == h(t15[rel]): continue
        tag = 'added' if rel not in t15 else 'changed'
        if h(t16[rel]) in NEWTEX: lines.append('  %-7s %-56s shout atlas' % (tag, rel)); continue
        if rel == 'UI/4_menu/40_title/tex/title_jpn_01_BM_NOMIP_HQ.tex' and g == 'TGAA2': lines.append('  %-7s %-56s version stamp' % (tag, rel)); continue
        if rel.endswith('.arc') and (g, rel) in allowed:
            base = t15.get(rel) or tc.get(rel)
            m0 = {e.name: bytes(e.data) for e in parse_arc(open(base, 'rb').read())['entries']}
            m1 = {e.name: bytes(e.data) for e in parse_arc(open(t16[rel], 'rb').read())['entries']}
            diff = {k for k in m1 if m0.get(k) != m1[k]}
            if set(m0) == set(m1) and diff and diff <= allowed[(g, rel)]:
                lines.append('  %-7s %-56s members: %s' % (tag, rel, ', '.join(sorted(k.split('/')[-1] for k in diff)))); continue
            problems.append('%s: unexpected member diff %s' % (rel, sorted(diff ^ allowed[(g, rel)])))
            continue
        problems.append('%s %s UNEXPECTED' % (tag, rel))
    print('== %s %s: %s' % (g, os.path.basename(new), 'PASS' if not problems else 'FAIL'))
    for l in lines: print(l)
    for p in problems: print('  PROBLEM', p)
    print('  sha256 %s  %d bytes' % (h(os.path.join(ROOT, new)), os.path.getsize(os.path.join(ROOT, new))))
    ok_all &= not problems
sys.exit(0 if ok_all else 1)

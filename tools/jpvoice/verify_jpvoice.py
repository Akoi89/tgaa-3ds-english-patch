# -*- coding: utf-8 -*-
"""Step 3: prove each -jpvoice CIA differs from the English build ONLY in audio, and that every
audio file it carries is Capcom's Japanese byte for byte.

Independent of build_jpvoice.py: re-extracts the built CIA's romfs, walks every file and compares
against (a) our shipped English romfs and (b) the Japanese sources. Rules checked:
  - every file present in ours and not in jpvoice was a sound/ or movie/ file whose cartridge copy
    exists (a deliberate deletion), and nothing else went missing
  - no file was added
  - every file that differs from ours is under sound/, movie/, or is an .arc, and equals the JP file
    (JP update first, then cartridge; DLC: same content in the JP DLC)
  - every unchanged file is byte-identical to ours
  - for .arc files that differ: whole file equals the JP archive
  - TMD title version equals the English build's; content count equals
Writes jpvoice/_out/VERIFY_<title>.txt and prints PASS/FAIL per title.
"""
import os, sys, io, json, struct, shutil
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline')); sys.path.insert(0, os.path.join(ROOT, 'jpvoice')); sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from cia import Cia
from inventory import SRC, TREES, extract_romfs, romfs_of_ncch, walk, h
from build_jpvoice import OUT_NAME, REVERT_DIRS
HERE = os.path.join(ROOT, 'jpvoice'); OUT = os.path.join(HERE, '_out')


def jp_file(g, kind, ci, rel):
    if kind == 'upd':
        for lab in (g + '_jp_upd', g + '_jp_cart'):
            p = os.path.join(TREES, lab, 'c0', rel.replace('/', os.sep))
            if os.path.exists(p):
                return p, lab
        return None, None
    p = os.path.join(TREES, g + '_jp_dlc', 'c%d' % ci, rel.replace('/', os.sep))
    return (p, 'jp_dlc') if os.path.exists(p) else (None, None)


def verify(title):
    g, kind = title.split('_')
    eng = Cia(SRC[g]['ours_upd' if kind == 'upd' else 'ours_dlc'])
    out = os.path.join(OUT, OUT_NAME[title]); jp = Cia(out)
    problems = []; notes = []
    if jp.version() != eng.version(): problems.append('version %s != %s' % (jp.version(), eng.version()))
    if jp.count != eng.count: problems.append('content count %d != %d' % (jp.count, eng.count))
    stats = dict(identical=0, reverted=0, deleted=0)
    for ci in range(min(jp.count, eng.count)):
        rj = romfs_of_ncch(jp.contents[ci]); re_ = romfs_of_ncch(eng.contents[ci])
        if rj is None and re_ is None:
            continue
        if (rj is None) != (re_ is None):
            problems.append('c%d romfs presence differs' % ci); continue
        if rj == re_:
            # untouched content: still count its files as identical
            stats['identical'] += len(walk(os.path.join(TREES, g + '_ours_' + kind, 'c%d' % ci))); continue
        d = os.path.join(HERE, '_verify', title, 'c%d' % ci)
        if os.path.isdir(d): shutil.rmtree(d)
        extract_romfs(rj, d)
        tj = walk(d); te = walk(os.path.join(TREES, g + '_ours_' + kind, 'c%d' % ci))
        for rel in sorted(set(te) - set(tj)):
            top = rel.split('/')[0]
            p, lab = jp_file(g, kind, ci, rel)
            if kind == 'upd' and top in REVERT_DIRS[title] and lab is not None and lab.endswith('jp_cart'):
                stats['deleted'] += 1
            else:
                problems.append('c%d MISSING %s' % (ci, rel))
        for rel in sorted(set(tj) - set(te)):
            problems.append('c%d ADDED %s' % (ci, rel))
        for rel in sorted(set(tj) & set(te)):
            hj, he = h(tj[rel]), h(te[rel])
            if hj == he:
                stats['identical'] += 1; continue
            top = rel.split('/')[0] if '/' in rel else '(root)'
            if not (top in REVERT_DIRS[title] or rel.endswith('.arc')):
                problems.append('c%d CHANGED outside audio: %s' % (ci, rel)); continue
            p, lab = jp_file(g, kind, ci, rel)
            if p is not None and h(p) == hj:
                stats['reverted'] += 1; continue
            if rel.endswith('.arc') and p is not None:
                # member-level revert: every voice member (type 79C47B59) must equal the JP archive's,
                # every other member must equal our English build's
                from dgs2tool.arc import parse_arc
                mj = {e.name: bytes(e.data) for e in parse_arc(open(tj[rel], 'rb').read())['entries']}
                me = {e.name: bytes(e.data) for e in parse_arc(open(te[rel], 'rb').read())['entries']}
                mp = {e.name: bytes(e.data) for e in parse_arc(open(p, 'rb').read())['entries']}
                ok = set(mj) == set(me) == set(mp) and all(mj[k] == (mp[k] if k.endswith('79C47B59') else me[k]) for k in mj)
                if ok:
                    stats['reverted'] += 1; stats['arcs with voice members reverted, other members ours'] = stats.get('arcs with voice members reverted, other members ours', 0) + 1; continue
            problems.append('c%d differs from ours but is NOT the JP file: %s' % (ci, rel)); continue
    lines = ['%s: %s' % (title, 'PASS' if not problems else 'FAIL'), '  file %s' % os.path.basename(out),
             '  sha256 %s' % h(out), '  version %d.%d.%d, contents %d' % (jp.version() + (jp.count,)),
             '  files identical to the English build: %d' % stats['identical'],
             '  files reverted to the Japanese original: %d' % stats['reverted'],
             '  files deleted so the cartridge copy plays: %d' % stats['deleted'],
             '  archives with voice members reverted and our textures kept: %d' % stats.get('arcs with voice members reverted, other members ours', 0)]
    lines += ['  PROBLEM ' + p for p in problems]
    io.open(os.path.join(OUT, 'VERIFY_%s.txt' % title), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return not problems


if __name__ == '__main__':
    want = sys.argv[1:] or ['TGAA1_upd', 'TGAA2_upd', 'TGAA1_dlc', 'TGAA2_dlc']
    ok = all([verify(t) for t in want])
    sys.exit(0 if ok else 1)

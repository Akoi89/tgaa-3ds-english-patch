# -*- coding: utf-8 -*-
"""End-to-end audit of a patched tree against the build it derives from.

    python final_audit.py <work-romfs> <shipped-romfs>

Checks nothing else in this pipeline checks:
  A  file inventory      no file added, lost, or emptied
  B  parser round-trip   parse->build is byte-identical on UNTOUCHED files, so
                         a difference elsewhere is a real edit and not the
                         writer corrupting something on the way through
  C  tag sequence        every changed entry keeps the exact same control tags
                         in the same order (upstream asserts this too)
  D  entry inventory     no label added or dropped inside a file
  E  edit locality       what actually changed, by directory and label kind
  F  statement shape     every 2-page <E008> unit still has page 1 closing
                         <E001>, and page 0 at 2 lines or fewer
"""
import sys, os, glob, re, collections

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

WRK, SHIP = sys.argv[1], sys.argv[2]
TAG = re.compile(r'<[^>]*>')
fail = []


def rel_set(root):
    return {os.path.relpath(p, root).replace(os.sep, '/')
            for p in glob.glob(os.path.join(root, '**', '*'), recursive=True)
            if os.path.isfile(p)}


w_files, s_files = rel_set(WRK), rel_set(SHIP)
added, lost = w_files - s_files, s_files - w_files
empty = [f for f in w_files if os.path.getsize(os.path.join(WRK, f)) == 0]
print('A  files: work %d, shipped %d | added %d, lost %d, empty %d'
      % (len(w_files), len(s_files), len(added), len(lost), len(empty)))
for tag, v in (('added', added), ('lost', lost), ('empty', empty)):
    if v:
        fail.append('%s files: %s' % (tag, sorted(v)[:5]))

roundtrip_bad, tagseq_bad, entry_bad, changed = [], [], [], []
kinds = collections.Counter()
dirs = collections.Counter()

for f in sorted(w_files & s_files):
    if not f.endswith('.gmd'):
        continue
    wp, sp = os.path.join(WRK, f), os.path.join(SHIP, f)
    wb, sb = open(wp, 'rb').read(), open(sp, 'rb').read()
    if wb == sb:
        try:
            if build_gmd_bytes(parse_gmd_bytes(wb)) != wb:
                roundtrip_bad.append(f)
        except Exception as e:
            roundtrip_bad.append('%s (%s)' % (f, e))
        continue
    changed.append(f)
    dirs[os.path.dirname(f)] += 1
    we = {(e['label'] or ''): e['text'] for e in parse_gmd_bytes(wb)['entries']}
    se = {(e['label'] or ''): e['text'] for e in parse_gmd_bytes(sb)['entries']}
    if set(we) != set(se):
        entry_bad.append((f, sorted(set(we) ^ set(se))[:4]))
    for lab in set(we) & set(se):
        if we[lab] == se[lab]:
            continue
        if TAG.findall(we[lab]) != TAG.findall(se[lab]):
            tagseq_bad.append((f, lab))
        pages = se[lab].split('<PAGE>')
        kinds['statement' if (len(pages) == 2 and '<E008>' in pages[0])
              else 'other'] += 1

print('B  parser round-trip on untouched files : %d bad' % len(roundtrip_bad))
print('C  changed entries with altered tag seq : %d' % len(tagseq_bad))
print('D  files with added/dropped labels      : %d' % len(entry_bad))
print('E  files changed: %d  | entries changed: statements %d, other %d'
      % (len(changed), kinds['statement'], kinds['other']))
for d, n in dirs.most_common():
    print('       %-28s %d file(s)' % (d or '.', n))
for name, v in (('round-trip', roundtrip_bad), ('tag seq', tagseq_bad), ('labels', entry_bad)):
    if v:
        fail.append('%s: %s' % (name, v[:5]))

shape_bad = []
for f in sorted(w_files):
    if not f.endswith('.gmd'):
        continue
    try:
        g = parse_gmd_bytes(open(os.path.join(WRK, f), 'rb').read())
    except Exception:
        continue
    for e in g['entries']:
        pages = e['text'].split('<PAGE>')
        if not (len(pages) == 2 and '<E008>' in pages[0]):
            continue
        body = [l for l in TAG.sub('', pages[0]).replace('\r', '').split('\n') if l.strip()]
        if len(body) > 2 or '<E001>' not in pages[1]:
            shape_bad.append((f, e['label'], len(body), '<E001>' in pages[1]))
print('F  malformed statements                 : %d' % len(shape_bad))
for s in shape_bad[:6]:
    print('       %s' % (s,))
if shape_bad:
    fail.append('statement shape: %s' % shape_bad[:5])

print()
if fail:
    print('  FAIL')
    for f in fail:
        print('    %s' % f)
    sys.exit(1)
print('  PASS - all five structural checks clean')

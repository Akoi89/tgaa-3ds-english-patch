# -*- coding: utf-8 -*-
"""Release gate: no visible line may fall off-centre on a centred page.

Rule, proven on the rig 2026-09-27 (model_tests/_v19h_cntr_rig and _rig2): a line is centred when it carries
<CNTR> ANYWHERE in it (start, middle or after its text); a line with visible text and no <CNTR> at all falls back
to the LEFT, even when the page's other lines are centred (TGAA1 Ep5 opening "London passed by in a flash.").
Defect = a page with at least one <CNTR> after its last <E041>, and a visible line in that span with no <CNTR>.
Same logic as _gaps/cntr_lines.py (the finder), taking trees as arguments.

The one documented exclusion: TGAA1 DLC sce07_c006_0000 L_EVENT_1 p14 ("Ugh. As they say..."): the Japanese page
(E800 468) also leaves line 1 uncentred and centres only the chant line. By design.

    python check_cntr_lines.py <tree> [<tree> ...]
exit 0 = clean (the exclusion may be present), 1 = any other uncentred line or any script gmd that did not parse.
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'dlc_icons', 'tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes   # noqa: E402

VIS = re.compile(r'[^<>\s](?![^<]*>)')
TAG = re.compile(r'<[^>]*>')
EXCLUDE = {('sce07_c006_0000_jpn.gmd', 'L_EVENT_1', 14, 'Ugh. As they say...')}


def scan(tree):
    rows, unparsed, pages = [], [], 0
    for f in sorted(glob.glob(os.path.join(tree, '**', 'script', '**', '*.gmd'), recursive=True)):
        try:
            entries = parse_gmd_bytes(open(f, 'rb').read())['entries']
        except Exception as ex:
            unparsed.append((os.path.relpath(f, tree), str(ex)[:60]))
            continue
        for e in entries:
            for i, p in enumerate((e['text'] or '').split('<PAGE>')):
                ms = list(re.finditer(r'<E041 [^>]*>', p))
                seg = p[ms[-1].end():] if ms else p
                if '<CNTR>' not in seg:
                    continue
                pages += 1
                for ln in seg.split('\r\n'):
                    if VIS.search(ln) and '<CNTR>' not in ln:
                        rows.append((os.path.relpath(f, tree), e['label'], i, TAG.sub('', ln).strip()))
    return rows, unparsed, pages


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    bad_total = 0
    for tree in sys.argv[1:]:
        if not os.path.isdir(tree):
            raise SystemExit('not a directory: %s' % tree)
        rows, unparsed, pages = scan(tree)
        excl = [r for r in rows if (os.path.basename(r[0]), r[1], r[2], r[3]) in EXCLUDE]
        bad = [r for r in rows if r not in excl]
        print('%s: centred pages %d, uncentred lines %d (documented exclusion %d), unparsed script gmds %d'
              % (tree, pages, len(bad), len(excl), len(unparsed)))
        for r in bad:
            print('  UNCENTRED %s\t%s\tp%d\t%s' % r)
        for u in unparsed:
            print('  UNPARSED %s (%s)' % u)
        bad_total += len(bad) + len(unparsed)
    print('GATE %s' % ('PASS' if not bad_total else 'FAIL (%d)' % bad_total))
    sys.exit(1 if bad_total else 0)


if __name__ == '__main__':
    main()

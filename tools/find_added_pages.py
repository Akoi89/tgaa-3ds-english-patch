# -*- coding: utf-8 -*-
"""Which TGAA2 DLC pages did the translator ADD beyond Capcom's Japanese pagination,
and how many of them could be re-joined now that the box is known to be 345 wide?

    python find_added_pages.py <en-romfs> <jp-romfs> <font00.gfd> [--show]

Alignment is by the tag skeleton of each page (every <...> tag, text stripped),
matched JP vs EN with difflib. An EN page that matches no JP page is "added".
For each added page, try joining it with the page before it (the usual split
direction) into ONE page whose lines all fit <= 345; the boundary tags between
them are kept inline. Prints numbers only unless --show.
"""
import difflib
import glob
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.environ.get('TGAA_ROOT', os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2')), r'dlc_icons\tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import parse_gmd_bytes            # noqa: E402
import pxwidth as P                                  # noqa: E402
from fix_dlc_overflow import split_body, words_of, rewrap   # noqa: E402

LIMIT = 345


def sig(page):
    # tag NAMES only: the translator retimed <E025 x> waits, which must not break alignment
    return tuple(t.split(' ')[0].strip('<>') for t in P.TAG.findall(page))


def main():
    en_root, jp_root, gfd = sys.argv[1:4]
    show = '--show' in sys.argv
    global LIMIT
    for a in sys.argv:
        if a.startswith('--limit='):
            LIMIT = int(a[8:])
    apply = '--apply' in sys.argv
    written = 0
    adv = P.advances(gfd)
    entries_more = added = joinable = joinable_1line = unjoinable = 0
    boundary_kinds = {}
    rows = []
    surplus = [0]; simple_join = [0]; simple_nofit = [0]
    for f in sorted(glob.glob(os.path.join(en_root, 'script', '**', '*.gmd'), recursive=True)):
        jf = os.path.join(jp_root, os.path.relpath(f, en_root))
        if not os.path.exists(jf):
            continue
        jp = {e['label']: e['text'] or '' for e in
              parse_gmd_bytes(open(jf, 'rb').read())['entries']}
        g = parse_gmd_bytes(open(f, 'rb').read())
        touched = False
        for e in g['entries']:
            t = e['text'] or ''
            if e['label'] not in jp:
                continue
            joins = []
            pe, pj = t.split('<PAGE>'), jp[e['label']].split('<PAGE>')
            if len(pe) <= len(pj):
                continue
            entries_more += 1
            surplus[0] += len(pe) - len(pj)
            se, sj = [sig(p) for p in pe], [sig(p) for p in pj]
            sm = difflib.SequenceMatcher(a=sj, b=se, autojunk=False)
            matched = set()
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == 'equal':
                    matched.update(range(j1, j2))
            for k, p in enumerate(pe):
                if k in matched or not P.lines(p):
                    continue
                added += 1
                if k == 0 or not P.lines(pe[k - 1]):
                    unjoinable += 1
                    continue
                pa, ba, sa = split_body(pe[k - 1])
                pb, bb, sb = split_body(p)
                mid = (sa + pb).replace('\r\n', '').replace('\n', '')
                boundary_kinds[re.sub(r'[\d.\- ]+', 'N', mid)] = boundary_kinds.get(re.sub(r'[\d.\- ]+', 'N', mid), 0) + 1
                simple = len(P.TAG.findall(mid)) <= 3
                words = words_of(ba)
                wb = words_of(bb)
                if words and mid:
                    words[-1] += mid          # glue boundary tags to the last word before them
                joined = words + wb
                one = P.px(P.TAG.sub('', ' '.join(joined)), adv)
                cand = rewrap(joined, adv, LIMIT, 2) if len(joined) >= 2 else None
                if one <= LIMIT:
                    joinable += 1; joinable_1line += 1; simple_join[0] += simple
                    rows.append((os.path.basename(f)[:22], e['label'][:14], k, 'ONE LINE', one))
                elif cand and cand[1] <= LIMIT:
                    joinable += 1; simple_join[0] += simple
                    names = re.findall(r'<(E\d+)', mid)
                    if simple and names == ['E023', 'E041', 'E025'] and sa.strip() == '<E023>':
                        joins.append((k, pa + (chr(13) + chr(10)).join(cand[0]).replace(mid, '') + sb))
                    rows.append((os.path.basename(f)[:22], e['label'][:14], k, 'two lines', cand[1]))
                    if simple and names == ['E023', 'E041', 'E025'] and sa.strip() == '<E023>':
                        rows[-1] = rows[-1][:3] + ('EXACT',) + rows[-1][4:]
                else:
                    unjoinable += 1; simple_nofit[0] += simple
                    rows.append((os.path.basename(f)[:22], e['label'][:14], k, 'NO FIT', cand[1] if cand else one))
            if apply and joins:
                for k, newpage in sorted(joins, reverse=True):
                    pe[k - 1:k + 1] = [newpage]
                    written += 1
                e['text'] = '<PAGE>'.join(pe)
                e.pop('text_hex', None)
                touched = True
        if apply and touched:
            from dgs2tool.gmd import build_gmd_bytes
            open(f, 'wb').write(build_gmd_bytes(g))
    if apply:
        print('joined pages written: %d' % written)
    print('entries with more EN pages than JP: %d, total surplus pages: %d' % (entries_more, surplus[0]))
    print('EN pages that match no JP page (translator-added): %d' % added)
    print('  re-joinable into the previous page at <=%d: %d  (%d of those fit on ONE line)' % (LIMIT, joinable, joinable_1line))
    print('  not joinable: %d' % unjoinable)
    print('splits with a plain 3-tag boundary (the translator pattern): joinable %d, no fit %d' % (simple_join[0], simple_nofit[0]))
    print('boundary tag patterns at the added splits:')
    for k, v in sorted(boundary_kinds.items(), key=lambda x: -x[1])[:8]:
        print('  %4d  %s' % (v, k[:90]))
    if show:
        for r in rows:
            print('  %-22s %-14s p%-3d %-9s widest %d' % r)


if __name__ == '__main__':
    main()

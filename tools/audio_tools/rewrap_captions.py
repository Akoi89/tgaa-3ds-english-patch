# -*- coding: utf-8 -*-
"""Re-wrap the evidence/profile captions so the "added to the Court Record"
banner stops clipping them.

Established by probe (TGAA1-LINECOUNT-PROBE):
  * the banner shows **6 full lines** at the stock font size -- a 7th bleeds
    past the box edge. It is NOT limited to three lines as Capcom's Japanese
    suggested, so no font change is needed.
  * the banner is ~209 px wide (a 230 px line lost "the", ~21 px), slightly
    WIDER than the Court Record's ~200 px wrap point.
  * only the banner honours the stored \\r\\n breaks -- the Court Record and the
    People screen re-wrap on their own, so changing the breaks cannot affect
    them.

The port wrapped these at ~300 px, which is why every line overflowed. This
re-wraps each caption at the narrowest width in WIDTHS that keeps it within
6 lines, and asserts the word sequence is unchanged: the wording is Capcom's
official English and must not be edited, only re-broken.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from caption_width import advances, strip
from caption_fit import wrap
from dgs2tool.arc import parse_arc, build_arc_bytes
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

GMDS = ['msg/evidence_caption_jpn.gmd', 'msg/cast_caption_jpn.gmd']
WIDTHS = list(range(196, 209))     # narrowest first, never past the ~209 box
MAX_LINES = 6


def main(romfs, apply=False):
    ui_path = os.path.join(romfs, 'archive', 'UI_cmn_jpn.arc')
    msg_path = os.path.join(romfs, 'archive', 'msg_cmn_jpn.arc')
    ui = {e.name: e.data for e in parse_arc(open(ui_path, 'rb').read())['entries']}
    adv, _ = advances(ui['UI/0_system/00_font/font03_jpn.gfd'])
    w = lambda s: sum(adv.get(ord(c), 7) for c in s)

    msg = parse_arc(open(msg_path, 'rb').read())
    ment = {e.name: e.data for e in msg['entries']}
    repl = {}
    changed = wide = over = 0
    widths_used = {}

    for g in GMDS:
        doc = parse_gmd_bytes(ment[g])
        for e in doc['entries']:
            t = e.get('text') or ''
            # entries labelled 'null' are unused placeholders holding runs of
            # 'xxxxxxxx'; they are not shown, and their single 232 px token
            # cannot be broken anyway
            if not t.strip() or str(e.get('label')) == 'null':
                continue
            flat = ' '.join(strip(t).split())
            chosen, lines = None, None
            for width in WIDTHS:
                cand = wrap(flat, w, width)
                if len(cand) <= MAX_LINES:
                    chosen, lines = width, cand
                    break
            if chosen is None:
                chosen = WIDTHS[-1]
                lines = wrap(flat, w, chosen)
                over += 1
                print('  !! %-16s still needs %d lines' % (e.get('label'), len(lines)))
            widths_used[chosen] = widths_used.get(chosen, 0) + 1
            if chosen > 200:
                wide += 1
            new = '\r\n'.join(lines)
            # the wording is Capcom's; only the breaks may move
            assert ' '.join(new.split()) == flat, e.get('label')
            assert all(w(l) <= chosen for l in lines), e.get('label')
            if new != t:
                e['text'] = new
                changed += 1
        if apply:
            repl[g] = build_gmd_bytes(doc)

    print('\n%d captions re-wrapped' % changed)
    print('widths used: %s' % dict(sorted(widths_used.items())))
    print('%d needed more than 200 px, %d still exceed %d lines' % (wide, over, MAX_LINES))

    if apply:
        open(msg_path, 'wb').write(build_arc_bytes(msg, repl))
        back = {e.name: e.data for e in parse_arc(open(msg_path, 'rb').read())['entries']}
        bad = 0
        for g in GMDS:
            for e in parse_gmd_bytes(back[g])['entries']:
                t = e.get('text') or ''
                if not t.strip():
                    continue
                ls = t.split('\r\n')
                if len(ls) > MAX_LINES or any(w(l) > 208 for l in ls):
                    print('  !! %s survived badly' % e.get('label'))
                    bad += 1
        print('re-read from the archive: %d problems' % bad)
        return 1 if bad else 0
    print('(dry run -- pass --apply)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '--apply' in sys.argv))

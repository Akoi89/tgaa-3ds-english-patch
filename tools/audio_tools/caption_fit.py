# -*- coding: utf-8 -*-
"""How many captions can be made to fit the banner by re-wrapping alone?

Established by measurement:
  * the banner honours the caption's own \\r\\n breaks and CLIPS the overflow;
    the Court Record ignores them and re-wraps, which is why the full text is
    always readable there and only the banner looks broken
  * the wrap width is ~200 px -- the Court Record fitted 199 px and broke
    before a word that would have made 204, and Scarlet's independent English
    tops out at 197
  * Capcom's Japanese uses exactly 3 lines for every caption, never more

So the budget is 3 x 200 px. This greedily re-wraps each caption at that width
and reports which ones still do not fit -- those need the text condensed, not
just re-broken.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from caption_width import arc, advances, strip
from dgs2tool.gmd import parse_gmd_bytes

WIDTH = 200
LINES = 3
GMDS = ['msg/evidence_caption_jpn.gmd', 'msg/cast_caption_jpn.gmd']


def wrap(text, w, width):
    out, cur = [], ''
    for word in text.split():
        trial = word if not cur else cur + ' ' + word
        if w(trial) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def main(root='base_v12/romfs_dir/archive'):
    ui = arc(os.path.join(root, 'UI_cmn_jpn.arc'))
    msg = arc(os.path.join(root, 'msg_cmn_jpn.arc'))
    adv, _ = advances(ui['UI/0_system/00_font/font03_jpn.gfd'])
    w = lambda s: sum(adv.get(ord(c), 7) for c in s)

    fits, needs = [], []
    for g in GMDS:
        doc = parse_gmd_bytes(msg[g])
        for e in doc['entries']:
            t = e.get('text') or ''
            if not t.strip():
                continue
            flat = ' '.join(strip(t).split())
            lines = wrap(flat, w, WIDTH)
            rec = (len(lines), w(flat), g.split('/')[-1], str(e.get('label')), lines)
            (fits if len(lines) <= LINES else needs).append(rec)

    total = len(fits) + len(needs)
    print('budget: %d lines x %d px = %d px of text\n' % (LINES, WIDTH, LINES * WIDTH))
    print('%3d of %d captions fit in %d lines just by re-wrapping' % (len(fits), total, LINES))
    print('%3d of %d need the wording condensed as well\n' % (len(needs), total))

    needs.sort(reverse=True)
    print('worst offenders (lines needed at %d px, total text width):' % WIDTH)
    for n, tw, g, lab, lines in needs[:12]:
        print('  %d lines  %4d px  %-26s %s' % (n, tw, g, lab))
        for l in lines:
            print('        %s' % l)
    over = sum(1 for n, tw, *_ in needs if tw > LINES * WIDTH)
    print('\n%d captions have more text than the box can physically hold' % over)
    return fits, needs


if __name__ == '__main__':
    main()

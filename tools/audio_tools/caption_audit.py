# -*- coding: utf-8 -*-
"""Find evidence/profile captions whose lines overflow the top-screen banner.

The Court Record re-wraps a caption to fit, but the banner that pops up when a
piece of evidence is added honours the string's own \\r\\n breaks and simply
clips whatever does not fit. So an over-long line is invisible in the Court
Record and broken on the banner -- exactly what happened to item0_01_00_c
("...shows the / ...from the fro / ...subsequently die").

Widths are measured with the CAPTION FONT'S OWN advance table (font03's GFD),
not an approximation, so the numbers are the real pixel advances the 3DS uses.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from dgs2tool.arc import parse_arc
from dgs2tool.gmd import parse_gmd_bytes

UI_ARC = os.path.join(ROOT, 'base_v12', 'romfs_dir', 'archive', 'UI_cmn_jpn.arc')
MSG_ARC = os.path.join(ROOT, 'base_v12', 'romfs_dir', 'archive', 'msg_cmn_jpn.arc')
GMDS = ['msg/evidence_caption_jpn.gmd', 'msg/cast_caption_jpn.gmd']


def advances(gfd):
    """codepoint -> advance width, straight from the font descriptor."""
    n = struct.unpack_from('<I', gfd, 28)[0]
    out = {}
    for i in range(n):
        o = 0x53 + i * 16
        if o + 16 > len(gfd):
            break
        cp = struct.unpack_from('<I', gfd, o)[0]
        out[cp] = gfd[o + 12]
    return out


def load():
    ui = {e.name: e.data for e in parse_arc(open(UI_ARC, 'rb').read())['entries']}
    adv = advances(ui['UI/0_system/00_font/font03_jpn.gfd'])
    msg = {e.name: e.data for e in parse_arc(open(MSG_ARC, 'rb').read())['entries']}
    return adv, msg


def width(text, adv, default=7):
    return sum(adv.get(ord(c), default) for c in text)


def main(limit=None):
    adv, msg = load()
    rows = []
    for g in GMDS:
        doc = parse_gmd_bytes(msg[g])
        for e in doc['entries']:
            t = e.get('text') or ''
            if not t.strip():
                continue
            for i, line in enumerate(t.replace('\r\n', '\n').split('\n')):
                rows.append((width(line, adv), g.split('/')[-1],
                             e.get('label'), i, line))
    rows.sort(reverse=True)

    known_bad = [r for r in rows if r[2] == 'item0_01_00_c']
    print('the reported case, item0_01_00_c:')
    for w, _, lab, i, line in known_bad:
        print('   %4d  line %d  %r' % (w, i, line))
    thresh = min(r[0] for r in known_bad) if known_bad else 0
    print('\nits narrowest overflowing line is %d units -> anything >= that is suspect\n'
          % thresh)

    over = [r for r in rows if r[0] >= thresh]
    print('%d lines at or above that width, across %d captions:'
          % (len(over), len({(r[1], r[2]) for r in over})))
    for w, g, lab, i, line in over[:limit or len(over)]:
        print('  %4d  %-26s %-18s L%d  %s' % (w, g, lab, i, line))

    print('\nwidth distribution of all %d lines:' % len(rows))
    ws = [r[0] for r in rows]
    ws.sort()
    for q in (50, 75, 90, 95, 99, 100):
        print('   p%-3d %d' % (q, ws[min(len(ws) - 1, q * len(ws) // 100)]))
    return over


if __name__ == '__main__':
    main()

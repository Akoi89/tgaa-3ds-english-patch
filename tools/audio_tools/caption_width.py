# -*- coding: utf-8 -*-
"""Calibrate the evidence/profile banner width from Capcom's own Japanese.

The banner honours a caption's own \\r\\n breaks and clips anything past the
box, while the Court Record re-wraps and therefore always looks fine. So the
question is: how wide can ONE LINE be?

Capcom authored the Japanese captions to fit that banner, so the widest
Japanese line is the design width. Japanese is measured as fullwidth = the font
size, halfwidth = half -- ruby annotations sit above the line and markup is not
drawn, so both are stripped first.
"""
import os
import re
import struct
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from dgs2tool.arc import parse_arc
from dgs2tool.gmd import parse_gmd_bytes

GMDS = ['msg/evidence_caption_jpn.gmd', 'msg/cast_caption_jpn.gmd']
TAG = re.compile(r'<[^>]*>')
RUBY = re.compile(r'<RUBY>\s*<RB>(.*?)</RB>\s*<RT>.*?</RT>\s*</RUBY>', re.S)


def arc(p):
    return {e.name: e.data for e in parse_arc(open(p, 'rb').read())['entries']}


def advances(gfd):
    n = struct.unpack_from('<I', gfd, 28)[0]
    size = struct.unpack_from('<f', gfd, 36)[0]
    out = {}
    for i in range(n):
        o = 0x53 + i * 16
        if o + 16 > len(gfd):
            break
        out[struct.unpack_from('<I', gfd, o)[0]] = gfd[o + 12]
    return out, size


def strip(text):
    """Drop ruby annotations and every other tag; keep only drawn characters."""
    return TAG.sub('', RUBY.sub(lambda m: m.group(1), text))


def jp_width(line, size):
    w = 0.0
    for ch in line:
        ea = unicodedata.east_asian_width(ch)
        w += size if ea in ('W', 'F', 'A') else size / 2.0
    return w


def lines_of(doc):
    for e in doc['entries']:
        t = e.get('text') or ''
        if not t.strip():
            continue
        for i, line in enumerate(strip(t).replace('\r\n', '\n').split('\n')):
            if line.strip():
                yield e.get('label'), i, line


def main():
    jui = arc(os.path.join(ROOT, 'basegame', 'rom', 'archive', 'UI_cmn_jpn.arc'))
    jmsg = arc(os.path.join(ROOT, 'basegame', 'rom', 'archive', 'msg_cmn_jpn.arc'))
    _, jsize = advances(jui['UI/0_system/00_font/font03_jpn.gfd'])

    print('Capcom Japanese, font size %.2f px:' % jsize)
    design = 0
    for g in GMDS:
        doc = parse_gmd_bytes(jmsg[g])
        ws = sorted(((jp_width(l, jsize), lab, i, l)
                     for lab, i, l in lines_of(doc)), reverse=True)
        design = max(design, ws[0][0])
        print('  %-26s %3d lines, widest %.0f px' % (g.split('/')[-1], len(ws), ws[0][0]))
        for w, lab, i, l in ws[:3]:
            print('      %5.0f  %-16s L%d  %s' % (w, lab, i, l))
    print('\n=> banner design width ~= %.0f px\n' % design)

    eui = arc(os.path.join(ROOT, 'base_v12', 'romfs_dir', 'archive', 'UI_cmn_jpn.arc'))
    emsg = arc(os.path.join(ROOT, 'base_v12', 'romfs_dir', 'archive', 'msg_cmn_jpn.arc'))
    eadv, esize = advances(eui['UI/0_system/00_font/font03_jpn.gfd'])
    # the atlas is rasterised bigger than the declared size and point-sampled
    # down, and the advances are in ATLAS pixels, so scale them the same way
    cell = 15.0
    scale = esize / cell
    print('English font03: declared %.2f, atlas cell %.0f -> advances x%.3f'
          % (esize, cell, scale))

    rows = []
    for g in GMDS:
        doc = parse_gmd_bytes(emsg[g])
        for lab, i, l in lines_of(doc):
            w = sum(eadv.get(ord(c), 7) for c in l) * scale
            rows.append((w, g.split('/')[-1], lab, i, l))
    rows.sort(reverse=True)

    over = [r for r in rows if r[0] > design]
    print('\n%d of %d English lines exceed %.0f px  (%d captions affected)'
          % (len(over), len(rows), design, len({(r[1], r[2]) for r in over})))
    for w, g, lab, i, l in over[:40]:
        print('  %5.1f  %-26s %-16s L%d  %s' % (w, g, lab, i, l))
    ref = [r for r in rows if r[2] == 'item0_01_00_c']
    print('\nthe reported case:')
    for w, g, lab, i, l in ref:
        print('  %5.1f  L%d  %s' % (w, i, l))
    return over, design


if __name__ == '__main__':
    main()

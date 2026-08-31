# -*- coding: utf-8 -*-
"""Throwaway probe: does the caption banner REFLOW when the font gets smaller?

That single unknown decides whether shrinking font03 is worth doing properly.
At 0.74 scale the captions fit in 4 lines -- but only if the box grows a fourth
line as the line height drops. If the layout pins it at 3, the whole idea dies.

Two changes, both deliberately crude because this build is disposable:

1. font03 scaled to 0.74 -- declared size 12.00 -> 8.88 and every advance
   multiplied by 0.74. The glyphs will look rough (they are being point-sampled
   even harder than usual); that is expected and is NOT what we are judging.

2. item0_01_00_c -- "Photograph of Victim", the first piece of evidence in
   episode 1 -- rewritten as FIVE short explicit lines, the last two marked, so
   the number of lines the banner can show is unmistakable.

Read the result as: how many lines are visible on the banner?
    3  -> box is pinned, drop the idea
    4  -> a proper re-rasterisation at 0.74 fits 146 of 149 captions
    5  -> even better
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

from dgs2tool.arc import parse_arc, build_arc_bytes
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

SCALE = float(os.environ.get('PROBE_SCALE', '0.74'))
GFD = 'UI/0_system/00_font/font03_jpn.gfd'
CAPTION = 'msg/evidence_caption_jpn.gmd'
LABEL = 'item0_01_00_c'
# Probe 2 showed FIVE lines, so the box is not pinned at three. Probe 3 plants
# eight to find the actual ceiling, with the number FIRST on each line so the
# count is readable even if the right-hand side clips.
PROBE_TEXT = ('L1 A photographic print\r\n'
              'L2 shows the victim. He\r\n'
              'L3 was shot from the\r\n'
              'L4 front in the chest and\r\n'
              'L5 subsequently died.\r\n'
              'L6 extra line six\r\n'
              'L7 extra line seven\r\n'
              'L8 extra line eight')
# NO angle brackets. "<" opens a control tag and an unterminated one hangs the
# parser -- probe 1 froze the game on exactly that. The tell I should have
# checked first: not one caption in the whole game contains a bare "<".


def scale_gfd(blob, s):
    d = bytearray(blob)
    n = struct.unpack_from('<I', d, 28)[0]
    old = struct.unpack_from('<f', d, 36)[0]
    struct.pack_into('<f', d, 36, old * s)
    touched = 0
    for i in range(n):
        o = 0x53 + i * 16
        if o + 16 > len(d):
            break
        cp = struct.unpack_from('<I', d, o)[0]
        a = d[o + 12]
        if a and cp != 32:      # hold the space at 3: scaling rounds it to 2,
            d[o + 12] = max(1, min(255, int(round(a * s))))   # a 33% cut that
            touched += 1        # mashed words together in probe 1
    print('  font03: size %.2f -> %.2f, %d advances scaled' % (old, old * s, touched))
    return bytes(d)


def main(romfs):
    ui_path = os.path.join(romfs, 'archive', 'UI_cmn_jpn.arc')
    ui = parse_arc(open(ui_path, 'rb').read())
    ent = {e.name: e.data for e in ui['entries']}
    if abs(SCALE - 1.0) < 1e-9:
        print('  font03: LEFT ALONE (scale 1.0)')
    else:
        new_gfd = scale_gfd(ent[GFD], SCALE)
        open(ui_path, 'wb').write(build_arc_bytes(ui, {GFD: new_gfd}))

    msg_path = os.path.join(romfs, 'archive', 'msg_cmn_jpn.arc')
    msg = parse_arc(open(msg_path, 'rb').read())
    ment = {e.name: e.data for e in msg['entries']}
    doc = parse_gmd_bytes(ment[CAPTION])
    hit = False
    for e in doc['entries']:
        if e.get('label') == LABEL:
            print('  %s:\n     old %r\n     new %r' % (LABEL, e['text'], PROBE_TEXT))
            e['text'] = PROBE_TEXT
            hit = True
    if not hit:
        print('  !! %s not found' % LABEL)
        return 1
    open(msg_path, 'wb').write(build_arc_bytes(msg, {CAPTION: build_gmd_bytes(doc)}))

    # prove both edits survive a re-read
    ui2 = {e.name: e.data for e in parse_arc(open(ui_path, 'rb').read())['entries']}
    got = struct.unpack_from('<f', ui2[GFD], 36)[0]
    assert abs(got - 12.0 * SCALE) < 0.1, got
    m2 = {e.name: e.data for e in parse_arc(open(msg_path, 'rb').read())['entries']}
    d2 = parse_gmd_bytes(m2[CAPTION])
    assert any(e.get('label') == LABEL and e['text'] == PROBE_TEXT
               for e in d2['entries'])
    print('  verified in the repacked archives')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

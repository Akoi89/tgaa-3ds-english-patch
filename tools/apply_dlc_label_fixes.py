# -*- coding: utf-8 -*-
"""Two fixes to the DLC menu labels in msg/system_title_jpn.gmd.

1. DLC_M_PREV -- "Previous Issue" is 38.8% wider than "Next Issue" opposite
   it, and the left plate draws the L button glyph BEFORE the text while the
   right plate draws R after it. Left-aligned text therefore starts under the
   glyph and the P is hidden, so the button reads "Lrevious Issue".

   Fix: shorten to "Back Issue" (the magazine term, and the same width class
   as "Next Issue") and prepend 3 spaces. A space is 278 font units and the
   hidden P is 667, so 834 units clears the glyph with ~2px to spare. The
   whole label ends up 833 units NARROWER than what ships today, so its right
   edge moves inward -- it cannot overrun the plate more than the current one
   already does.

2. DLC_S_PURCHASE / DLC_S_BOSS carry <FONT 2> while every other label on the
   DLC screens is <FONT 0>. That single tag is why "Purchase DLC" and
   "SpotPass" look like a different typeface from "DLC List", "Picture Book"
   and the rest. Retagged to FONT 0.
"""
import os
import sys
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.arc import parse_arc, build_arc_bytes
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

ARC = 'base_v12/romfs_dir/archive/msg_cmn_jpn.arc'
GMD = 'msg/system_title_jpn.gmd'

EDITS = {
    'DLC_M_PREV':     ('<FONT 0>Previous Issue', '<FONT 0>   Back Issue'),
    'DLC_S_PURCHASE': ('<FONT 2>Purchase DLC',   '<FONT 0>Purchase DLC'),
    'DLC_S_BOSS':     ('<FONT 2>SpotPass',       '<FONT 0>SpotPass'),
}


def main(apply=False):
    arc = parse_arc(open(ARC, 'rb').read())
    ent = {e.name: e for e in arc['entries']}
    assert GMD in ent, sorted(ent)[:5]
    doc = parse_gmd_bytes(ent[GMD].data)

    done = 0
    for e in doc['entries']:
        lab = e.get('label')
        if lab in EDITS:
            old, new = EDITS[lab]
            if e['text'] != old:
                print('  !! %-16s expected %r, found %r' % (lab, old, e['text']))
                continue
            e['text'] = new
            print('  %-16s %r -> %r' % (lab, old, new))
            done += 1
    if done != len(EDITS):
        print('\n%d/%d applied -- aborting' % (done, len(EDITS)))
        return 1

    new_gmd = build_gmd_bytes(doc)
    # re-parse to prove the rebuild is readable and carries the edits
    chk = parse_gmd_bytes(new_gmd)
    got = {e['label']: e['text'] for e in chk['entries'] if e.get('label') in EDITS}
    assert all(got[k] == v[1] for k, v in EDITS.items()), got
    print('\nGMD %d -> %d bytes, re-parsed OK' % (len(ent[GMD].data), len(new_gmd)))

    if apply:
        out = build_arc_bytes(arc, {GMD: new_gmd})
        open(ARC, 'wb').write(out)
        print('arc rewritten: %d bytes' % len(out))
        # verify from disk
        back = parse_arc(open(ARC, 'rb').read())
        b = {e.name: e for e in back['entries']}
        assert len(b) == len(ent), (len(b), len(ent))
        d2 = parse_gmd_bytes(b[GMD].data)
        g2 = {e['label']: e['text'] for e in d2['entries'] if e.get('label') in EDITS}
        assert all(g2[k] == v[1] for k, v in EDITS.items()), g2
        for n in ent:
            if n != GMD and b[n].data != ent[n].data:
                print('  !! %s changed unexpectedly' % n)
        print('verified: %d entries, only %s modified' % (len(b), GMD))
    else:
        print('(dry run -- pass --apply)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--apply' in sys.argv))

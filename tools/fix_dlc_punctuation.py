# -*- coding: utf-8 -*-
"""Punctuation corrections to text WE translated in the TGAA1 DLC.

    python fix_dlc_punctuation.py <dlc-romfs> <font00.gfd>

These pages are our own prose -- the community DLC patch left them in Japanese
and we translated them -- so unlike Capcom's text they carry no authority and
plain errors should simply be fixed.

Each is a place where the Japanese punctuation was carried over literally:
Japanese uses a full stop where English wants a comma, and marks the topic with
a comma where English wants none. Everything here is a real error, not a matter
of taste. Deliberate sentence-initial "Because..." fragments are LEFT ALONE --
they answer a question, they match the Japanese, and they are ordinary Ace
Attorney voice.

Long runs of dots are also left alone: they are Capcom's own convention for a
long silence (their English reaches 18, 27, even 60 and 90 dots) and every run
in our text is a multiple of three, exactly as theirs are.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.gmd import build_gmd_bytes, parse_gmd_bytes
from pxwidth import advances, px

TAG = re.compile(r'<[^>]*>')

# Matched WITH their surrounding tags, because in most of these the offending
# punctuation sits right on top of an <E003 N> delivery pause: the comma was an
# attempt to write a beat the engine already performs. Removing the comma keeps
# the beat -- the pause tag stays exactly where it was.
FIXES = [
    ('sce07_c002_0000_jpn.gmd', 'L_EVENT_2_1', 17,
     'The first,<E003 8>', 'The first<E003 8>',
     'comma between subject and verb, doubling the <E003 8> pause'),

    ('sce07_c013_0000_jpn.gmd', 'L_START', 68,
     'restaurant,<E003 4>', 'restaurant<E003 4>',
     'comma before a restrictive "like this", doubling the <E003 4> pause'),

    # Capcom put this silence on its OWN page and we kept it -- the next page is
    # "(.........)". These dots leaked in when we merged pages, so the beat plays
    # twice. Only the characters go; the style/speed tags are Capcom's and stay.
    ('sce07_c013_0002_jpn.gmd', 'L_START', 9,
     '<E025 8>...<E025 3>', '<E025 8><E025 3>',
     'silence beat duplicated -- the following page already carries it'),

    ('sce07_c013_0002_jpn.gmd', 'L_CHOICE_ME', 25,
     'the defendant is innocent,', 'the defendant is innocent',
     'Japanese topic comma splitting subject from verb'),

    ('sce07_c013_0002_jpn.gmd', 'L_CHOICE_ME', 43,
     'that the most,<E003 6><E025 4><E341> is myself though)',
     'that the most<E003 6><E025 4><E341> is myself, though.)',
     'comma on the wrong side of "though"; no terminal stop'),

    ('sce07_c013_0002_jpn.gmd', 'L_CHOICE_SEE_HOW', 1,
     "(If I say 'I am' here.<E003 8>\r\nIt would mean telling a lie)",
     "(If I say 'I am' here,<E003 8>\r\nit would mean telling a lie.)",
     'full stop orphaning the "If" clause; no terminal stop'),
]


def main(root, gfd):
    adv = advances(gfd)
    done = 0
    for fn, label, page, old, new, why in FIXES:
        cand = glob.glob(os.path.join(root, '**', fn), recursive=True)
        if not cand:
            print('  MISSING FILE %s' % fn)
            continue
        p = cand[0]
        g = parse_gmd_bytes(open(p, 'rb').read())
        hit = False
        for e in g['entries']:
            if (e['label'] or '') != label:
                continue
            pages = e['text'].split('<PAGE>')
            if page >= len(pages):
                continue
            if old not in pages[page]:
                if new in pages[page]:
                    print('  %-26s %-18s p%-3d  already applied' % (fn, label, page))
                    hit = None
                continue
            if pages[page].count(old) != 1:
                print('  AMBIGUOUS  %s %s p%d' % (fn, label, page))
                continue
            pages[page] = pages[page].replace(old, new)
            e['text'] = '<PAGE>'.join(pages)
            hit = True
            widest = max((px(l.strip(), adv)
                          for l in TAG.sub('', pages[page]).replace('\r', '').split('\n')
                          if l.strip()), default=0)
            print('  %-26s %-18s p%-3d  %s' % (fn, label, page, why))
            print('       -> %s   (widest line now %d units)'
                  % (' / '.join(new.split('\r\n')), widest))
        if hit:
            open(p, 'wb').write(build_gmd_bytes(g))
            done += 1
        elif hit is None:
            done += 1
        else:
            print('  NOT FOUND  %s %s p%d : %r' % (fn, label, page, old[:40]))
    print('\n  %d of %d fixes applied' % (done, len(FIXES)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

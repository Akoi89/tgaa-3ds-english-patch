# -*- coding: utf-8 -*-
"""Prove the re-split changed line breaks and nothing else.

For every script GMD that differs between the shipped update and the staged
tree: same entry count, same labels in order, same page count per entry, same
tag sequence per page, same tag-stripped word sequence per page. The only
permitted difference is where CRLF falls inside a page.

    python verify_resplit.py <shipped tree> <staged tree>
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from dgs2tool.gmd import parse_gmd_bytes

TAG = re.compile(r'<[^>]*>')


def shape(text):
    pages = text.split('<PAGE>')
    return [(TAG.findall(p), TAG.sub('', p.replace('\r\n', ' ')).split()) for p in pages]


def main(a, b):
    files = changed = bad = 0
    pages_grown = 0
    for dp, _, fs in os.walk(os.path.join(a, 'script')):
        for fn in fs:
            if not fn.endswith('.gmd'):
                continue
            pa = os.path.join(dp, fn)
            pb = os.path.join(b, os.path.relpath(pa, a))
            files += 1
            ra, rb = open(pa, 'rb').read(), open(pb, 'rb').read()
            if ra == rb:
                continue
            changed += 1
            ga, gb = parse_gmd_bytes(ra), parse_gmd_bytes(rb)
            if [e['label'] for e in ga['entries']] != [e['label'] for e in gb['entries']]:
                bad += 1
                print('   LABELS DIFFER  %s' % fn)
                continue
            for ea, eb in zip(ga['entries'], gb['entries']):
                sa, sb = shape(ea['text'] or ''), shape(eb['text'] or '')
                if len(sa) != len(sb):
                    bad += 1
                    print('   PAGE COUNT     %s %s %d -> %d' % (fn, ea['label'], len(sa), len(sb)))
                    continue
                for i, ((ta, wa), (tb, wb)) in enumerate(zip(sa, sb)):
                    if ta != tb:
                        bad += 1
                        print('   TAGS DIFFER    %s %s p%d' % (fn, ea['label'], i))
                    if wa != wb:
                        bad += 1
                        print('   WORDS DIFFER   %s %s p%d' % (fn, ea['label'], i))
                    la = (ea['text'] or '').split('<PAGE>')[i].count('\r\n')
                    lb = (eb['text'] or '').split('<PAGE>')[i].count('\r\n')
                    pages_grown += lb > la
    print('%d script files, %d changed, %d pages gained a line, %d violations'
          % (files, changed, pages_grown, bad))
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1], sys.argv[2]) else 0)

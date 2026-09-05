# -*- coding: utf-8 -*-
"""Split ONE conversation page into two, rc21's way, and prove it before writing.

A conversation page whose words cannot sit in two lines of <= 345 px cannot be
re-split; it needs a second page. The engine does NOT paginate a three-line
conversation page (seen on screen twice on 2026-09-04), so the split has to be
authored. rc21 did exactly one of these for DLC `L_START_3` page 23, it was
verified on the rig, and its pre/post files are the recipe:

    page A = original prefix (every <E800 n>, animation cues, the <E041> box)
             + the first words, as two lines <= LIMIT
             + the original trailing tags (ending on the wait marker <E023>)
    page B = CRLF + ONLY the tags after the last <E800 n> in the prefix
             (the speaker/layout state: <E041 X Y>, <E042>, <CNTR>, <E025 N>)
             + the remaining words + the same trailing tags

No <E800> is invented or duplicated: those number voice/event streams and are
dense and ascending through an entry, so B re-states layout only. Tags that sit
inside the text with no whitespace around them travel with their word.

    python split_page.py <gmd> <label> <page> [--limit 345] [--apply]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pxwidth as P
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from fix_dlc_overflow import split_body, rewrap
from fix_dialogue_overflow import words_of

E800 = re.compile(r'<E800 \d+>')
SENT_END = re.compile(r'[.!?…]["\')]*(<[^>]*>)*$')


LAYOUT = re.compile(r'<(E041 \d+ \d+|E042|CNTR|E025 [0-9.]+)>')
# what page A may keep from the original trailer: timed waits, text speed,
# alignment, and the wait marker itself. Anything else stays on page B only.
A_TRAILER = re.compile(r'<(E003 \d+|E025 [0-9.]+|E042|CNTR|E023|E024)>')


def layout_prefix(prefix):
    """The LAYOUT tags after the last <E800 n>: what page B must re-state.

    Whitelist, not 'everything after the last E800'. The batch dry run showed
    108 pages whose prefix tail also carried <E330>, <E333>, <E007>, <E239>,
    <E346>, <E341> -- animation/emote cues, not state. Re-stating one on page
    B fires it a second time. rc21 re-stated only the speaker box, the
    alignment and the text speed; so does this."""
    tags = P.TAG.findall(prefix)
    last = max((i for i, t in enumerate(tags) if E800.match(t)), default=-1)
    keep = [t for t in tags[last + 1:] if LAYOUT.fullmatch(t)]
    return ''.join(keep)


def plan_split(page, adv, limit):
    prefix, body, suffix = split_body(page)
    words = words_of(body)
    if len(words) < 3:
        return None
    best = None
    for i in range(2, len(words) - 0):
        a, b = words[:i], words[i:]
        if not b:
            continue
        # page A, like B, takes one line when one line fits -- a short clause
        # split into "(Now that I'm / standing in his shoes," reads worse than
        # the same words on one line
        one_a = ' '.join(a)
        w1a = P.px(P.TAG.sub('', one_a), adv)
        ra = ([one_a], w1a) if w1a <= limit else (rewrap(a, adv, limit, 2) if len(a) >= 2 else None)
        if ra is None:
            continue
        # page B takes as few lines as it needs: one if the remainder fits
        one = ' '.join(b)
        w1 = P.px(P.TAG.sub('', one), adv)
        rb = ([one], w1) if w1 <= limit else (rewrap(b, adv, limit, 2) if len(b) >= 2 else None)
        if ra is None or rb is None or ra[1] > limit or rb[1] > limit:
            continue
        # Where page A ends decides how the split READS. The first plan filled
        # A greedily and left 473 of 773 page Bs a single word ("...with
        # flying" / "colours."). Priority: end A on a sentence; else on a
        # clause boundary; else mid-phrase but with at least three words on
        # B when any such split fits. Within a class, the latest split wins.
        last = P.TAG.sub('', a[-1]).rstrip()
        if SENT_END.search(a[-1]):
            cls = 3
        elif last.endswith((',', ';', ':', '–', '—', '-', '...', '…')):
            cls = 2
        else:
            cls = 1 if len(b) >= 3 else 0
        score = (cls, i)
        if best is None or score > best[0]:
            best = (score, ra, rb)
    if best is None:
        return None
    _, ra, rb = best
    if not suffix.strip():
        return None                      # no wait marker to end page A on
    # A trailing tag belongs after the LAST word of the passage, so page B keeps
    # the original trailer whole. Page A keeps only wait/timing/layout tags
    # before its wait marker. rc21 copied the trailer onto both halves, which
    # was harmless for its page (waits and alignment only); the batch showed 20
    # pages whose trailer carried <E085 X Y>, an event tag that would then fire
    # twice -- the same mistake as re-stating emote cues, one tag later.
    trailer_a = ''.join(t for t in P.TAG.findall(suffix) if A_TRAILER.fullmatch(t))
    if not trailer_a.rstrip().endswith(('<E023>', '<E024>')):
        return None
    page_a = prefix + '\r\n'.join(ra[0]) + trailer_a
    body_b = '\r\n'.join(rb[0])
    # do not re-state a layout tag the remainder already opens with
    # (e.g. ` <E025 2.5>This is,` -- the tag travelled with its word)
    lp = layout_prefix(prefix)
    while True:
        m = re.search(r'(<[^>]*>)$', lp)
        if m and body_b.startswith(m.group(1)):
            lp = lp[:-len(m.group(1))]
        else:
            break
    page_b = '\r\n' + lp + body_b + suffix
    return page_a, page_b, ra[1], rb[1], lp, trailer_a


def proofs(page, pa, pb, lp, trailer_a):
    """Everything a split must preserve. Returns None, or the reason it fails."""
    if (P.TAG.sub('', page.replace('\r\n', ' ')).split()
            != P.TAG.sub('', (pa + ' ' + pb).replace('\r\n', ' ')).split()):
        return 'words changed'
    # tags: the original set, plus the layout B re-states, plus what A kept of
    # the trailer (waits/layout only) -- nothing else may appear or vanish
    extra = P.TAG.findall(lp) + P.TAG.findall(trailer_a)
    if sorted(P.TAG.findall(pa) + P.TAG.findall(pb)) != sorted(P.TAG.findall(page) + extra):
        return 'tags changed beyond restated layout / kept trailer'
    # <E800> markers number voice/event streams: same ones, same order, once
    if E800.findall(pa) + E800.findall(pb) != E800.findall(page):
        return 'E800 sequence changed'
    # ORDER, not just multiset. The construction is A = prefix + bodyA + kept
    # trailer, B = CRLF + re-stated layout + bodyB + original trailer. Strip
    # exactly those two affixes and the tag sequence must be the original's,
    # in order. A multiset check would pass a reordering.
    if not pa.endswith(trailer_a) or not pb.startswith('\r\n' + lp):
        return 'page affixes are not where the recipe puts them'
    ta = P.TAG.findall(pa[:len(pa) - len(trailer_a)] if trailer_a else pa)
    tb = P.TAG.findall(pb[len('\r\n' + lp):])
    if ta + tb != P.TAG.findall(page):
        return 'tag order changed'
    if not pa.rstrip().endswith(('<E023>', '<E024>')):
        return 'A does not end on a wait marker'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('gmd'); ap.add_argument('label'); ap.add_argument('page', type=int)
    ap.add_argument('--limit', type=int, default=345)
    ap.add_argument('--gfd', default=os.path.join(HERE, '_out', '_tgaa2_font00.gfd'))
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    adv = P.advances(a.gfd)

    raw = open(a.gmd, 'rb').read()
    g = parse_gmd_bytes(raw)
    e = next(x for x in g['entries'] if x['label'] == a.label)
    pages = e['text'].split('<PAGE>')
    page = pages[a.page]
    lines = P.lines(page)
    print('original page %d: %d lines, widths %s' % (a.page, len(lines), [P.px(l, adv) for l in lines]))

    got = plan_split(page, adv, a.limit)
    if got is None:
        raise SystemExit('no split satisfies the limit on both pages')
    pa, pb, wa, wb, restated_lp, trailer_a = got
    print('\nPAGE A (max %d px):' % wa)
    for l in P.lines(pa):
        print('   %3d  %s' % (P.px(l, adv), l))
    print('   raw: %r' % pa)
    print('\nPAGE B (max %d px):' % wb)
    for l in P.lines(pb):
        print('   %3d  %s' % (P.px(l, adv), l))
    print('   raw: %r' % pb)

    why = proofs(page, pa, pb, restated_lp, trailer_a)
    assert why is None, why
    print('\nproofs: words identical; tags identical except the restated layout (%s) and what A kept of '
          'the trailer (%s); <E800> sequence identical; A ends on a wait marker'
          % (restated_lp or '(nothing)', trailer_a))

    if not a.apply:
        print('\n--report only; --apply to write')
        return
    pages[a.page:a.page + 1] = [pa, pb]
    e['text'] = '<PAGE>'.join(pages)
    open(a.gmd, 'wb').write(build_gmd_bytes(g))
    print('written: %s %s now %d pages' % (os.path.basename(a.gmd), a.label, len(pages)))


if __name__ == '__main__':
    main()

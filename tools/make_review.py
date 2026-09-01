# -*- coding: utf-8 -*-
"""Every wording change this project made, with all available references.

    python make_review.py <out.txt>

Walks each of our four builds against the upstream build it derives from and
emits one record per CHANGED PASSAGE -- not per entry. A script entry can run
to a hundred pages; dumping the whole thing to show a two-word trim buries the
edit. Where the page count matches, the differing page is shown; where we
re-paginated, a word-level diff finds the changed span and shows it with a
little context.

Pure re-wrapping (identical words, different line breaks) is counted per
section but never listed -- no wording changed.
"""
import os
import difflib
import io
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gmdwalk import gmds, visible

CONTEXT = 10           # words of context either side of a changed span

# Read from the trees extracted BACK OUT of the finished CIAs, not from the
# working trees. A working tree can drift from what actually shipped:
# scratchpad/fix/romfs was used here as "TGAA2 base" and turned out to differ
# from the shipped 1.0.4 in three files, so an earlier run of this report
# described a build that does not exist.
BUILDS = [
    ('TGAA1 - base game 1.0.5', 'build/verify/t1b/romfs00', 'tut/t1theirs/romfs',
     'tut/t1jap/romfs', 'tut/scarlet/romfs'),
    ('TGAA2 - base game 1.0.5', 'build/verify/t2b/romfs00', 'tut/theirs/romfs',
     'tut/dgs2base/romfs', 'scarlet2/romfs00'),
    ('TGAA1 - DLC 1.0.7', 'build/verify/t1d', 'dlccheck/t1dlc_up', None, None),
    ('TGAA2 - DLC 1.0.4', 'build/verify/t2d', 'dlccheck/t2dlc_up',
     'dlccheck/t2dlc_jp', None),
]

KINDS = [('evidence_caption', 'Court Record - evidence captions'),
         ('cast_caption', 'Court Record - character profiles'),
         ('system_title', 'Episode and system titles'),
         ('title_', 'Episode and system titles'),
         ('system_', 'System and menu text'),
         ('choice_', 'Dialogue choices'),
         ('topic_', 'Conversation topics'),
         ('Caption_', 'Scene captions'),
         ('movie_subtitle', 'Movie subtitles')]

TESTIMONY = 'Cross-examination testimony statements'


def kind_of(key, ours_text):
    pages = ours_text.split('<PAGE>')
    if len(pages) == 2 and '<E008>' in pages[0]:
        return TESTIMONY
    base = key.split('::')[-1]
    for frag, name in KINDS:
        if frag in base:
            return name
    return 'Other script text'


def window(words, lo, hi):
    lead = '...' if lo else ''
    tail = '...' if hi < len(words) else ''
    return lead + ' '.join(words[lo:hi]) + tail


def passages(new_text, old_text):
    """[(page_or_None, old_passage, new_passage)] for what actually changed."""
    np, op = new_text.split('<PAGE>'), old_text.split('<PAGE>')
    if len(np) == len(op):
        out = []
        for i, (a, b) in enumerate(zip(np, op)):
            va, vb = visible(a), visible(b)
            if va != vb and (va or vb):
                out.append((i, vb, va))
        if out:
            return out
    a, b = visible(new_text).split(), visible(old_text).split()
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, b, a).get_opcodes():
        if tag == 'equal':
            continue
        out.append((None,
                    window(b, max(0, i1 - CONTEXT), min(len(b), i2 + CONTEXT)),
                    window(a, max(0, j1 - CONTEXT), min(len(a), j2 + CONTEXT))))
    return out or [(None, visible(old_text), visible(new_text))]


def find(tree, key, label):
    if not tree:
        return None
    d = tree.get(key)
    if d is None:
        base = key.split('::')[-1].split('/')[-1]
        for k, v in tree.items():
            if k.split('::')[-1].split('/')[-1] == base and label in v:
                d = v
                break
    return (d or {}).get(label)


MAX_REF = 400          # a whole-entry reference longer than this is noise


def ref(text, page, passage):
    """The reference for one passage, never a whole conversation.

    Page indices only line up when the reference tree paginates the entry the
    same way. When they don't, fall back to the whole entry -- but only if it
    is short enough to be a useful comparison rather than a wall of text."""
    if not text:
        return None
    if page is not None:
        pgs = text.split('<PAGE>')
        if page < len(pgs):
            return visible(pgs[page]) or None
        return None
    v = visible(text)
    if not v:
        return None
    if len(v) > max(MAX_REF, len(passage) * 3):
        return None
    return v


def is_japanese(s):
    """Text still in Japanese = we translated it, we did not condense it."""
    cjk = sum(1 for c in s if '぀' <= c <= 'ヿ' or '一' <= c <= '鿿'
              or '＀' <= c <= '￯')
    return cjk > len(s) * 0.2


HEADER = """
Context for a reviewer
----------------------
These are English fan-translation patches for the two 3DS "Great Ace Attorney"
games, which Capcom released in Japan only. The English text comes from
Capcom's own later PC release (The Great Ace Attorney Chronicles), ported onto
the 3DS ROM by senyarom -- so "STARTED FROM" is Capcom's official English
wherever Capcom localised that string, and the community DLC patch for DLC
entries.

Why anything was changed: the 3DS text boxes are narrower than the PC ones, so
some official lines do not fit. The aim of every edit was the SMALLEST trim
that makes a line fit while keeping the speaker's voice and everything the
Japanese actually says. Each was checked against the Japanese original, and
against Scarlet Study's independent fan translation where one exists (a second
opinion, never our baseline).

The tightest constraint is a cross-examination TESTIMONY STATEMENT: it is a
rigid two-page unit, and in cross-examination the player's arrows move between
statements rather than pages, so a third line is unreachable and its text is
lost outright. Those had to fit two lines no matter what.

  JAPANESE     - Capcom's original 3DS Japanese (ruby readings folded in)
  SCARLET      - Scarlet Study's independent English fan translation
  STARTED FROM - the text we began with
  OURS         - what we changed it to

Where a passage is bracketed by "..." it is a window around the changed span,
not the whole entry.

What a reviewer would most usefully judge: does OURS still say what JAPANESE
says, does it keep the register of STARTED FROM, and is anything lost that
mattered?
"""


def main(path):
    out = io.open(path, 'w', encoding='utf-8')
    w = out.write
    w('EVERY WORDING CHANGE IN THIS PATCH SET\n' + '=' * 78 + '\n')
    w(HEADER)
    grand = 0
    for tag, wr, ur, jr, sr in BUILDS:
        if not (os.path.isdir(wr) and os.path.isdir(ur)):
            continue
        wt, ut = gmds(wr), gmds(ur)
        jt = gmds(jr) if jr and os.path.isdir(jr) else None
        st = gmds(sr) if sr and os.path.isdir(sr) else None
        recs, reflow = [], 0
        for k in sorted(set(wt) & set(ut)):
            for lab in sorted(set(wt[k]) & set(ut[k])):
                a, b = wt[k][lab], ut[k][lab]
                if a == b:
                    continue
                if visible(a) == visible(b):
                    reflow += 1
                    continue
                jp_t, sc_t = find(jt, k, lab), find(st, k, lab)
                for pi, old, new in passages(a, b):
                    kind = ('Newly translated from Japanese (not condensing)'
                            if is_japanese(old) else kind_of(k, a))
                    recs.append((kind, k, lab, pi, old, new,
                                 ref(jp_t, pi, old), ref(sc_t, pi, old)))
        w('\n\n' + '#' * 78 + '\n')
        w('## %s -- %d changed passages (%d further pages re-wrapped only)\n'
          % (tag, len(recs), reflow))
        w('#' * 78 + '\n')
        if not st:
            w('\n(No Scarlet Study version exists for this content.)\n')
        if not jt:
            w('\n(The Japanese original for this content was not available offline.)\n')
        order = {TESTIMONY: 0, 'Newly translated from Japanese (not condensing)': 9}
        for kind in sorted({r[0] for r in recs},
                           key=lambda x: (order.get(x, 5), x)):
            rows = [r for r in recs if r[0] == kind]
            w('\n\n--- %s (%d) ---\n' % (kind.upper(), len(rows)))
            for _, k, lab, pi, old, new, jp, sc in rows:
                grand += 1
                w('\n[%d] %s | %s%s\n'
                  % (grand, k.split('::')[-1], lab,
                     '' if pi is None else ' | page %d' % pi))
                if jp:
                    w('  JAPANESE     : %s\n' % jp)
                if sc:
                    w('  SCARLET      : %s\n' % sc)
                w('  STARTED FROM : %s\n' % old)
                w('  OURS         : %s\n' % new)
    out.close()
    print('  %d changed passages written' % grand)


if __name__ == '__main__':
    main(sys.argv[1])

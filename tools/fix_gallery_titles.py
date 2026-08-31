"""
Un-breaks the six gallery track titles that were authored as two lines.

The music/voice list button and the top-screen title plate are ONE line
tall. Unlike the dialogue box, they do not auto-paginate: a hard CRLF
does not push the remainder to a second screen, it draws it outside the
widget, where the next list entry paints over it. The user's screenshot
of Issue No. 8 shows exactly that -- "Ryunosuke Naruhodo -" with
"Overture to Adventures" struck through beneath it, and the same in the
title plate above.

Six titles in the community DLC patch (v1.0.5) carry that CRLF; they are
inherited, not introduced by this project. Each is rewritten to a single
line using the convention the surrounding entries already follow -- an
(Unused) variant drops everything after the dash:

    Susato Mikotoba - A New Bloom in the New World
    Susato Mikotoba (Unused)
    Ryunosuke Naruhodo - Overture to Adventures
    Overture to Adventures (Unused)

and aoc01 establishes "GAA" as the accepted short form of the series
name ("GAA - Court is Now in Session").

Width budget: measured off the screenshot, the button's text column runs
from the left padding to the speaker icon, about 16300 units. "The Great
Ace Attorney - Adjudication" (16841) is the first list entry there and
its final glyph sits under the icon, which fixes the boundary. Every
replacement below is under 15000.

Usage:
    python fix_gallery_titles.py <dlc_root_containing_eng_aocNN_full> [--apply]
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from textwidth import width

CRLF = chr(13) + chr(10)
CAP = 16300

# (issue, label, new single-line title)
EDITS = [
    (1, 'BGM4_TITLE', 'The Great Beginning (Unused)'),
    (2, 'BGM1_TITLE', 'Susato Mikotoba - A New Bloom'),
    (2, 'BGM4_TITLE', 'Reminiscences (Unused)'),
    (5, 'BGM6_TITLE', 'Dance of Deduction (Unused)'),
    (8, 'BGM2_TITLE', 'GAA - Adjudication (Unused)'),
    (8, 'BGM3_TITLE', 'Overture to Adventures'),
]


def main():
    root = sys.argv[1]
    apply = '--apply' in sys.argv
    done = bad = 0
    for issue, label, new in EDITS:
        path = os.path.join(root, 'eng_aoc%02d_full' % issue,
                            'msg', 'aoc%02d_jpn.gmd' % issue)
        doc = parse_gmd_bytes(open(path, 'rb').read())
        ent = {e['label']: e for e in doc['entries']}
        e = ent.get(label)
        if e is None or CRLF not in e['text']:
            print('!! aoc%02d %s -- not a two-line title' % (issue, label))
            bad += 1
            continue
        w = width(new)
        if w > CAP or CRLF in new:
            print('!! aoc%02d %s -- replacement is %d units' % (issue, label, w))
            bad += 1
            continue
        print('aoc%02d %-12s %r\n%18s-> %r  (%d units)'
              % (issue, label, e['text'], '', new, w))
        e['text'] = new
        done += 1
        if apply:
            open(path, 'wb').write(build_gmd_bytes(doc))

    print('\nrewritten %d, refused %d' % (done, bad))

    # nothing multi-line may survive in any gallery title
    left = 0
    for i in range(14):
        fn = os.path.join(root, 'eng_aoc%02d_full' % i,
                          'msg', 'aoc%02d_jpn.gmd' % i)
        if not os.path.exists(fn):
            continue
        for e in parse_gmd_bytes(open(fn, 'rb').read())['entries']:
            if e['label'].endswith('_TITLE') and e['label'] != 'TITLE' \
                    and CRLF in e['text']:
                left += 1
                print('   REMAINS aoc%02d %s %r' % (i, e['label'], e['text']))
    print('two-line gallery titles remaining: %d' % left)
    if not apply:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()

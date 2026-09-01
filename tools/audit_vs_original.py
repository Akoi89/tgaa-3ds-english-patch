"""
Compares an English build against the Japanese original, per label.

Why per-label and not a fixed rule: the 2-line limit belongs to the
DIALOGUE box, not to every widget. The Japanese original itself has
pages of 5 lines (location descriptions) and even 37 (special
full-screen entries), so "flag anything over 2 lines" produces a pile of
false positives. But Capcom's own text is by definition laid out to fit
whatever widget each entry uses -- so the reliable question is not "how
many lines is this?" but "does the English use MORE lines than the
Japanese did for this same label?". If it does, the English has grown
past what that widget was built to show, and the overflow is clipped.

This is what found the real defects: 71 dialogue pages in the community
English base-game patch render 3 lines where Capcom's Japanese uses 2,
plus 14 movie-subtitle pages at 4 lines where the original uses 2.

Usage:
    python audit_vs_original.py <jp_romfs_dir> <en_romfs_dir> [--limit N]
"""
import os
import sys, os, glob, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from check_fit import pages_of
from textwidth import width


def page_line_counts(text):
    return [len(ls) for _, ls in pages_of(text) if ls]


def main():
    jp_root, en_root = sys.argv[1], sys.argv[2]
    limit = 20
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])

    findings = []
    files_compared = labels_compared = 0
    missing = 0

    for en_fn in sorted(glob.glob(os.path.join(en_root, '**', '*.gmd'),
                                  recursive=True)):
        rel = os.path.relpath(en_fn, en_root)
        jp_fn = os.path.join(jp_root, rel)
        if not os.path.exists(jp_fn):
            missing += 1
            continue
        try:
            en_doc = parse_gmd_bytes(open(en_fn, 'rb').read())
            jp_doc = parse_gmd_bytes(open(jp_fn, 'rb').read())
        except Exception:
            continue
        files_compared += 1
        jp_by_label = {e['label']: e for e in jp_doc['entries']}
        file_capacity = max(
            (max(page_line_counts(x['text']), default=0)
             for x in jp_doc['entries']), default=0)
        for e in en_doc['entries']:
            jp_e = jp_by_label.get(e['label'])
            if jp_e is None:
                continue
            labels_compared += 1
            en_counts = page_line_counts(e['text'])
            jp_counts = page_line_counts(jp_e['text'])
            if not en_counts or not jp_counts:
                continue
            en_max, jp_max = max(en_counts), max(jp_counts)

            # How many lines is this entry's widget actually able to show?
            #
            # For a msg/ file every entry feeds the same widget, so the
            # tallest page Capcom ever puts in that file is a fair measure
            # of its capacity -- the location-description panel holds 5
            # lines, and an English entry growing from 2 to 3 there is
            # harmless.
            #
            # A script/ file is not uniform: it mixes dialogue with
            # occasional full-screen entries running to dozens of lines,
            # so a file-wide maximum would excuse real dialogue overflow.
            # There the Japanese entry itself is the measure, floored at 2
            # because the dialogue box demonstrably shows two lines.
            if rel.replace('\\', '/').startswith('msg/'):
                capacity = max(file_capacity, 2)
            else:
                capacity = max(jp_max, 2)

            if en_max > capacity:
                worst = max((ls for _, ls in pages_of(e['text']) if ls),
                            key=len)
                findings.append((rel, e['label'], jp_max, en_max, capacity,
                                 worst))

    print(f'Compared {files_compared} files, {labels_compared} labels '
          f'({missing} English files had no Japanese counterpart).')
    print(f'Labels where English uses MORE lines than the original: '
          f'{len(findings)}')
    print()
    by_file = collections.Counter(f for f, *_ in findings)
    for f, n in by_file.most_common():
        print(f'   {n:4d}  {f}')
    print()
    for rel, label, jpm, enm, cap, lines in findings[:limit]:
        print(f'-- {rel} :: {label}   JP {jpm} -> EN {enm} lines '
              f'(widget holds {cap})')
        for l in lines:
            print(f'     {width(l):6d} | {l}')
    if len(findings) > limit:
        print(f'... and {len(findings)-limit} more')


if __name__ == '__main__':
    main()

"""
Checks for a specific, concrete translation bug: two adjacent text runs
getting visually joined into one word because neither side added the
space English needs at that boundary.

Why this happens: JP doesn't use spaces between words/clauses -- commas
and control tags (pauses, etc.) provide all the separation the original
needs. When a run boundary falls where JP relied on that natural
lack-of-space (or a tag-only pause) instead of an actual space
character, and the English translation is done run-by-run, it's easy
for neither adjacent run to include the space English requires there --
producing a real on-screen join like "gallery" + "is limited..." ->
"galleryis limited...". This is unrelated to line length; it happens
regardless of whether the page fits on screen.

Method: walk the FULL token stream (tags included). Track the most
recent text run's content, but reset that tracking to "no risk" any
time a <PAGE> tag is crossed -- runs on separate screens can never
visually join, no matter what their text looks like. Whitespace-only
text runs (a bare '\r\n' token, common in this format) are NOT filtered
out before comparing -- they naturally provide the separation, so
walking through them keeps both the run before and the run after
correctly un-flagged. Only two CONTENT-bearing runs with nothing but
tags and/or non-whitespace between them, where neither side's text
supplies the space English needs, get flagged.

This can't see multi-run boundaries where a translator already added
the needed space on either side (the normal, correct case) or where a
literal newline/page-break already separates them, so it should have a
low false-positive rate.

Usage:
    python check_run_spacing.py <translated_gmd>
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize

NO_SPACE_NEEDED_END = set(' \n\r\t-[')            # whitespace, hyphen, opening bracket.
                                                    # Straight quotes (' and ") are
                                                    # deliberately NOT here -- this game's
                                                    # font has no curly-quote glyphs, so
                                                    # everything uses straight quotes,
                                                    # which are direction-ambiguous. The
                                                    # real build (tag_align.rebuild)
                                                    # resolves that ambiguity with parity
                                                    # tracking (1st occurrence = opening,
                                                    # 2nd = closing, ...); this standalone
                                                    # checker can't replicate that
                                                    # stateful logic, so it just doesn't
                                                    # flag quote-adjacent boundaries at
                                                    # all rather than risk false alarms.
NO_SPACE_NEEDED_START = set(' \n\r\t.,!?;:)　]')  # whitespace, closing punct, closing bracket
QUOTE_CHARS = ("'", '"')


def main():
    gmd_path = sys.argv[1]
    doc = parse_gmd_bytes(open(gmd_path, 'rb').read())

    flagged = 0
    checked = 0
    for e in doc['entries']:
        label = e['label']
        tokens = tokenize(e['text'])
        prev_idx = None
        prev_text = None  # most recent text-run's content since the last <PAGE> reset
        for i, tok in enumerate(tokens):
            kind, s = tok
            if kind == 'tag':
                if s == '<PAGE>':
                    prev_idx = None
                    prev_text = None  # new screen -- no join risk across this boundary
                continue
            if s == '':
                continue
            if prev_text is not None:
                checked += 1
                end_ok = prev_text[-1] in NO_SPACE_NEEDED_END or prev_text[-1] in QUOTE_CHARS
                start_ok = s[0] in NO_SPACE_NEEDED_START or s[0] in QUOTE_CHARS
                if not end_ok and not start_ok:
                    flagged += 1
                    print(f'!! {label}  [{prev_idx}]...[{i}]')
                    print(f'     [{prev_idx}] ends:   ...{prev_text[-25:]!r}')
                    print(f'     [{i}] starts: {s[:25]!r}...')
                    print(f'     => would render as: ...{prev_text[-15:]}{s[:15]}...')
            prev_idx = i
            prev_text = s

    print()
    print(f'Checked {checked} adjacent run boundaries.')
    print(f'Flagged {flagged} likely missing-space joins.')
    if flagged == 0:
        print('RESULT: clean -- no missing-space run joins detected.')


if __name__ == '__main__':
    main()

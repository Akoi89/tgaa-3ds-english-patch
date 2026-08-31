"""
Checks that a translated GMD's actual tag sequence (as any real parser --
including the game itself -- would read it) still exactly matches the
original JP source's tag sequence.

Why this exists, and why it's different from tag_align.verify_tags_unchanged:
that check confirms rebuild() didn't accidentally overwrite a tag SLOT in
the token list -- which is necessary but not sufficient. It can't see a
separate real bug: if a translated text run's own content contains a
literal '<' or '>' character (e.g. an ASCII-bracket style choice like
'<Supreme Court>') that ends up sitting directly adjacent to a REAL tag
with nothing between them, the two can merge into one malformed tag when
the assembled bytes are re-parsed downstream (confirmed: '<' + '<E006>'
-> '<<E006>' merges into a single bogus token). The game's own parser
has to re-read these final bytes the same way, so this is a genuine
functional risk, not just a cosmetic one.

Method: re-tokenize the BUILT file's text and compare its tag sequence
directly against the ORIGINAL source's tag sequence. Any mismatch means
something in the translated text is interfering with real tag
boundaries.

One kind of difference is legitimate and expected: autowrap.py inserts
CONTINUATION PAGES when English runs longer than the 2-line box, using
the same recipe the official localization uses --
'<E023><PAGE>' followed by a repeat of the page's own '<E041>'/'<E025>'.
So the comparison skips over insertions that match exactly that shape and
still fails on anything else, which keeps the real check (a translated
'<' merging into an adjacent tag) fully intact.

Usage:
    python check_tag_integrity.py <source_jp_gmd> <translated_gmd>
"""
import sys, io, difflib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize


def _is_continuation_shape(block):
    """True if `block` reads exactly as '<E023>' '<PAGE>' then optionally
    '<E041 ...>' and '<E025 ...>'."""
    if len(block) < 2 or block[0] != '<E023>' or block[1] != '<PAGE>':
        return False
    rest = block[2:]
    if rest and rest[0].startswith('<E041'):
        rest = rest[1:]
    if rest and rest[0].startswith('<E025'):
        rest = rest[1:]
    return not rest


def _is_continuation_group(block):
    """True if `block` is one inserted continuation page, in any rotation.

    Rotations have to be accepted because the surrounding stream already
    contains the same '<E041 ...><E025 ...>' pair that the insertion
    repeats. When identical tags sit on both sides of an insertion point,
    there is more than one equally minimal way to align the edit, and
    SequenceMatcher may legitimately report the block starting at the
    '<E041>' instead of at the '<E023>'. Both describe the very same
    inserted page, so judging the shape alone would reject a correct
    build; the structural check in verify_page_structure() is what
    actually guarantees the result is well formed."""
    n = len(block)
    return any(_is_continuation_shape(block[r:] + block[:r]) for r in range(n))


# Measured across Capcom's whole Japanese base game (32247 page breaks),
# which is a far broader sample than the DLC episodes alone: a <PAGE> is
# preceded by <E023> 30658x, <E024> 1378x, <E104> 83x, <E590> 83x,
# <E206> 23x and <E196> 22x -- and by nothing else, ever. An earlier
# version of this set was derived from the DLC only, listed just <E023>
# and <E024>, and so reported the base game's own untouched <E590><PAGE>
# structures as corruption.
PAGE_PRECEDERS = {'<E023>', '<E024>', '<E104>', '<E590>', '<E206>', '<E196>'}


def verify_page_structure(tr_tags):
    """Every '<PAGE>' must be immediately preceded by a wait-for-input
    marker. That invariant holds in all 2163 official pages, and it is
    the property an inserted page could plausibly break. Checked
    independently of the diff, so a well-formed edit still gets
    validated even when the differ aligns the insertion oddly."""
    problems = []
    for i, t in enumerate(tr_tags):
        if t == '<PAGE>' and (i == 0 or tr_tags[i-1] not in PAGE_PRECEDERS):
            prev = tr_tags[i-1] if i else None
            problems.append(
                f'<PAGE> at #{i} not preceded by a wait marker (got {prev!r})')
    return problems


def diff_tags(src_tags, tr_tags):
    """Compare the two tag sequences, tolerating ONLY whole inserted
    continuation-page groups. Returns a list of human-readable problems
    (empty means clean).

    A hand-rolled walker is not good enough here: an inserted
    '<E023><PAGE>' is byte-identical to the '<E023><PAGE>' that already
    ends the page being split, so a greedy left-to-right match happily
    consumes the wrong one and then reports a bogus divergence hundreds
    of tags later. SequenceMatcher finds the actual minimal edit script,
    so each inserted block can be checked for being a legal group."""
    problems = []
    sm = difflib.SequenceMatcher(a=src_tags, b=tr_tags, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if op == 'insert':
            block = tr_tags[j1:j2]
            if not _is_continuation_group(block):
                problems.append(f'unexpected inserted tags at #{j1}: {block!r}')
            continue
        if op == 'delete':
            problems.append(f'tags MISSING at source #{i1}: {src_tags[i1:i2]!r}')
            continue
        problems.append(
            f'tags CHANGED at source #{i1}: {src_tags[i1:i2]!r} -> {tr_tags[j1:j2]!r}')
    return problems


def main():
    src_path, translated_path = sys.argv[1], sys.argv[2]
    doc_src = parse_gmd_bytes(open(src_path, 'rb').read())
    doc_tr = parse_gmd_bytes(open(translated_path, 'rb').read())
    src_by_label = {e['label']: e for e in doc_src['entries']}

    flagged = 0
    checked = 0
    inserted_pages = 0
    for e in doc_tr['entries']:
        label = e['label']
        src_e = src_by_label.get(label)
        if src_e is None:
            continue
        src_tags = [s for k, s in tokenize(src_e['text']) if k == 'tag']
        tr_tags = [s for k, s in tokenize(e['text']) if k == 'tag']
        checked += 1
        problems = diff_tags(src_tags, tr_tags) + verify_page_structure(tr_tags)
        inserted_pages += sum(
            1 for op, i1, i2, j1, j2 in difflib.SequenceMatcher(
                a=src_tags, b=tr_tags, autojunk=False).get_opcodes()
            if op == 'insert' and _is_continuation_group(tr_tags[j1:j2]))
        if problems:
            flagged += 1
            print(f'!! TAG SEQUENCE MISMATCH in {label}')
            for p in problems:
                print(f'   {p}')

    print()
    print(f'Checked {checked} entries.')
    print(f'Flagged {flagged} with tag sequence mismatches.')
    print(f'{inserted_pages} legitimate continuation page(s) inserted by autowrap.')
    if flagged == 0:
        print('RESULT: clean -- every tag matches source; only continuation pages added.')


if __name__ == '__main__':
    main()

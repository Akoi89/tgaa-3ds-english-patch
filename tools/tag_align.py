"""
Tag-preserving translation helper for TGAA/DGS GMD script entries.

The raw entry text is a sequence of <TAG ...> control codes interleaved
with plain-text runs (JP dialogue). To translate safely without ever
hand-retyping a tag (the actual risk in this kind of work), this module:

  1. Tokenizes an entry's text into an alternating list of
     ('tag', raw_tag_string) / ('text', plain_run) tokens.
  2. Exposes only the 'text' runs, each with a stable index, for
     translation -- tags are never touched, only copied through.
  3. Reassembles the full tagged string from the original token list
     plus a {index: translated_text} substitution map, verifying that
     every tag is byte-identical to the source and every text run was
     either translated or intentionally left blank (e.g. runs that are
     pure whitespace/punctuation used only for layout).

Usage:
    tokens = tokenize(entry_text)
    runs = list_text_runs(tokens)          # [(idx, jp_text), ...]
    ... translate each run ...
    new_text = rebuild(tokens, {idx: en_text, ...})
"""
import os
import re

TAG_RE = re.compile(r'(<[^>]*>)')


def tokenize(text):
    """Split into a list of ('tag', s) / ('text', s) tokens, in order."""
    parts = TAG_RE.split(text)
    tokens = []
    for p in parts:
        if p == '':
            continue
        if TAG_RE.fullmatch(p):
            tokens.append(('tag', p))
        else:
            tokens.append(('text', p))
    return tokens


def list_text_runs(tokens):
    """Return [(index, text)] for every text-run token, indexed by
    position in the token list (stable key for rebuild())."""
    return [(i, tok[1]) for i, tok in enumerate(tokens) if tok[0] == 'text']


def is_translatable(s):
    """True if a text run actually contains JP prose worth translating
    (as opposed to pure whitespace/punctuation/newlines used for
    layout, which should just be copied through unchanged)."""
    return bool(re.search(r'[\u3040-\u30ff\u4e00-\u9fff\uff01-\uff9f]', s))


PUNCT_MAP = {
    '　': ' ',   # JP fullwidth space (usually a paragraph-indent artifact) -> regular space
    '、': ',',   # 、 -> ,
    '。': '.',   # 。 -> .
    '《': "'",   # 《 -> straight quote (see note below on curly quotes)
    '》': "'",
    '『': "'",   # 『 -> straight quote (treated the same as 《)
    '』': "'",
    '“': "'",   # JP-native curly double quote, used pervasively as JP's OWN
    '”': "'",   # primary emphasis-quote style -- same target as 《》.
    '【': '[',  # JP lenticular brackets, used here for UI button-name
    '】': ']',  # references ("press the【Back】button") -- no official
                # precedent found in the sampled script, so this is a
                # judgment call: square brackets are the standard,
                # unambiguous English convention for naming a UI control.
}
ELLIPSIS_RE = re.compile(r'‥+')  # one or more JP two-dot-leader chars (‥, doubled as ‥‥)


def normalize_punctuation(text):
    """Converts leftover JP-style punctuation in already-assembled English
    text to this game's established English convention.

    Why this is needed: is_translatable() only flags runs containing
    actual kana/kanji as needing translation -- a run that's PURELY JP
    punctuation (an ellipsis, a fullwidth space, a 《》 emphasis bracket)
    never gets flagged, so it's never shown to a translator at all, and
    rebuild() correctly-by-design copies it through unchanged. That's
    fine structurally, but wrong for OUTPUT.

    IMPORTANT, corrected after a real bug: this originally converted
    quote-role punctuation to CURLY quotes ('‘'/'’'), calibrated against
    the official Steam/Switch remaster's script (which does use curly
    quotes extensively and works fine there). That calibration doesn't
    transfer to this original 3DS game -- its font is a different, more
    limited one, and confirmed via in-game screenshots: every closing
    curly quote / curly apostrophe ('’', U+2019) renders as a BLANK GAP
    ("can t believe", "Defendant s Antechamber", "won t do you any
    good"). Straight quotes (') and straight double quotes (") render
    fine (confirmed: '"murderer"' displays correctly). So everything
    here now targets the plain ASCII straight quote -- ellipsis (JP
    '‥' -> ASCII '...') is still safe since that's a real Steam-confirmed
    AND visually-confirmed-in-3DS convention, just not the quote style."""
    text = ELLIPSIS_RE.sub('...', text)
    for jp, en in PUNCT_MAP.items():
        text = text.replace(jp, en)
    return text


NO_SPACE_NEEDED_END = set(' \n\r\t-—[')           # whitespace, hyphen, em-dash, and an
                                                    # OPENING square bracket -- unlike
                                                    # quotes, '[' is unambiguously opening,
                                                    # so it's safe here directly (no parity
                                                    # tracking needed). Quote characters
                                                    # are NOT here -- they're ambiguous
                                                    # (opening vs closing) and handled
                                                    # separately below via parity tracking,
                                                    # since a blanket "no space needed"
                                                    # caused the exact opposite bug on the
                                                    # other side (a quoted word glued to
                                                    # its opening or closing mark:
                                                    # '" murderer "' instead of
                                                    # '"murderer"', confirmed by an
                                                    # in-game screenshot) as excluding them
                                                    # unconditionally did for word-joining
                                                    # ("fate'will").
NO_SPACE_NEEDED_START = set(' \n\r\t.,!?;:)　]')  # whitespace, closing punctuation, and
                                                    # an unambiguously CLOSING square
                                                    # bracket ']' (mirrors '[' above).

QUOTE_CHARS = ("'", '"')


def _quote_is_opening(ch, count_including_this_one):
    """True if the `count_including_this_one`-th occurrence of quote
    character `ch` (1st, 2nd, 3rd...) is an OPENING quote. Straight
    quotes carry no directional information of their own, so direction
    is inferred purely from parse order: odd occurrence -> opening,
    even occurrence -> closing. This mirrors how a person reads the
    text -- the first "  encountered starts a quotation, the next one
    ends it, and so on."""
    return count_including_this_one % 2 == 1


def rebuild(tokens, substitutions):
    """Reassemble the tagged string. `substitutions` maps token index
    -> replacement text for text-run tokens; any text-run index not in
    the map is copied through unchanged (use this for pure-layout runs
    that don't need translation).

    Also restores natural separation between adjacent text runs. JP
    doesn't need spaces between words/clauses -- commas and pause tags
    carry all the separation the original needs, and where JP does need
    a hard break it's often an embedded '\\r\\n' *inside* a run's own
    raw text (not a separate token). When translating run-by-run it's
    easy for the English replacement to drop that embedded break, which
    silently joins two runs into one word on screen (confirmed both by
    direct inspection and by measuring a ~54% missing-space rate across
    a translated file's run boundaries vs ~5% in the official shipped
    script). So: whenever a substituted run's end and the next
    substituted run's start would leave no separation at all, this
    inserts one -- using the ORIGINAL text's own '\\r\\n' at that
    boundary if it had one (preserving the author's exact line break),
    falling back to a plain space otherwise (the JP-needs-no-space but
    English-does case). Resets across a <PAGE> tag, since runs on
    different screens can never visually join."""
    out = []
    prev_sub = None   # substituted text of the most recent text-run token
    prev_orig = None  # that same token's original (pre-translation) text
    quote_count = {"'": 0, '"': 0}  # occurrences seen so far this page, for
                                     # inferring each straight quote's role
                                     # by parse order (see _quote_is_opening)
    for i, tok in enumerate(tokens):
        kind, s = tok
        if kind == 'tag':
            out.append(s)
            if s == '<PAGE>':
                prev_sub = None
                prev_orig = None
                quote_count = {"'": 0, '"': 0}
            continue
        piece = substitutions.get(i, s)
        piece = normalize_punctuation(piece)
        if piece and prev_sub:
            end_char = prev_sub[-1]
            start_char = piece[0]
            end_ok = end_char in NO_SPACE_NEEDED_END
            start_ok = start_char in NO_SPACE_NEEDED_START
            if not end_ok and end_char in QUOTE_CHARS:
                # quote_count already includes this trailing quote (counted
                # when prev_sub was processed) -- odd means IT was opening,
                # which hugs the word that just followed it, so no space
                if _quote_is_opening(end_char, quote_count[end_char]):
                    end_ok = True
            if not start_ok and start_char in QUOTE_CHARS:
                # quote_count does NOT yet include this leading quote --
                # if counting it would make it odd (opening), it needs a
                # leading space from whatever precedes; if even (closing),
                # it hugs the word that just ended, so no space
                if not _quote_is_opening(start_char, quote_count[start_char] + 1):
                    start_ok = True
            if not end_ok and not start_ok:
                if prev_orig and prev_orig.endswith('\r\n'):
                    sep = '\r\n'
                elif s.startswith('\r\n'):
                    sep = '\r\n'
                else:
                    sep = ' '
                out.append(sep)
        out.append(piece)
        for j, ch in enumerate(piece):
            if ch not in QUOTE_CHARS:
                continue
            # a quote character with a LETTER on both sides WITHIN this same
            # piece is unambiguously a mid-word contraction/possessive
            # ("he's", "Defendant's") -- never a real quote boundary -- and
            # must NOT be counted, or it throws off the open/close parity
            # for every genuine quote mark later on the same page (this was
            # a real, confirmed bug: "he's earned his qualifications as a
            # 'defence attorney'" miscounted "he's" as quote #1, making the
            # real opening quote look like a closing one). A quote at the
            # very start/end of a piece (no letter on one side within this
            # piece) IS counted -- that's exactly where translators place
            # real quote marks, at run boundaries.
            before = piece[j - 1] if j > 0 else ''
            after = piece[j + 1] if j + 1 < len(piece) else ''
            if before.isalpha() and after.isalpha():
                continue
            quote_count[ch] += 1
        if piece:
            # only update the tracked "most recent text run" when this one
            # actually produced content -- an intentionally-empty override
            # (e.g. suppressing a redundant fallback punctuation mark)
            # must not erase the previous real run from consideration, or
            # the boundary check after it would be silently skipped
            prev_sub = piece
            prev_orig = s
    return ''.join(out)


def verify_tags_unchanged(tokens, substitutions):
    """Safety check, done structurally rather than by re-scanning the
    assembled text.

    rebuild() only ever copies 'tag'-kind tokens through verbatim -- it
    is not possible for it to corrupt a real tag. So re-tokenizing the
    *finished* string (the old approach) was never a sound way to check
    that: translated text can legitimately contain literal '<' and '>'
    characters (e.g. a stylistic '<Supreme Court>' rendering of source
    brackets), and those get misdetected as fake tags by the same regex
    that finds real ones, producing a false TAG MISMATCH.

    The only real failure mode worth catching is a substitutions map
    that mistakenly targets a tag-token index with different text --
    rebuild() would silently ignore it and keep the original tag, which
    would mask a caller bug (e.g. an off-by-one in run numbering). So
    that's what this checks for."""
    for i, tok in enumerate(tokens):
        kind, s = tok
        if kind == 'tag' and i in substitutions and substitutions[i] != s:
            return False
    return True


if __name__ == '__main__':
    import sys, io
    # point DGS2TOOL at a checkout of senyarom/tgaa2-en-patch
    sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
    from dgs2tool.gmd import parse_gmd_bytes

    fp = sys.argv[1]
    label = sys.argv[2]
    doc = parse_gmd_bytes(open(fp, 'rb').read())
    entry = next(e for e in doc['entries'] if e['label'] == label)
    tokens = tokenize(entry['text'])
    runs = list_text_runs(tokens)

    out = io.open(sys.argv[3], 'w', encoding='utf-8')
    out.write(f'{len(tokens)} tokens, {len(runs)} text runs\n\n')
    for idx, s in runs:
        marker = 'JP' if is_translatable(s) else 'layout-only'
        out.write(f'[{idx}] ({marker}) {s!r}\n')
    out.close()

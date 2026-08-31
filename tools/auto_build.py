"""
Builds a translated .gmd file directly from your edited runs_XXXX.txt file --
no manual copy-pasting into a translations dict needed.

It expects the same format extract_runs.py produces, after you've replaced
the Japanese text with your English translations:

    ##### LABEL_NAME (386 tokens, 34 JP runs) #####
    [15] Same day, 9:00 a.m.
    [18] Supreme Court of Judicature, Courtroom No. 2
    [116] The most authoritative

    seat of judgment in this entire nation.

A run's text is everything between its [N] marker and the next [N] marker
or ##### header -- so multi-line translations (including ones with a blank
line in the middle, like [116] above) are captured correctly as one piece.
Any "<== likely sentence/thought END" marker text is stripped automatically.

Usage:
    python auto_build.py <runs_file.txt> <source_gmd> <output_gmd>

Example:
    python auto_build.py runs_0002.txt eng_aoc13_full\\script\\sce07_c013_0002_jpn.gmd sce07_c013_0002_TRANSLATED.gmd
"""
import sys, re, io

sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from tag_align import tokenize, rebuild, verify_tags_unchanged

# <RUBY><RB>base</RB><RT>reading</RT></RUBY>, optionally bracketed by the
# <E516 n>/<E519> pair that reserves room for it.
RUBY_RE = re.compile(
    r'(?:<E516 \d+>)?<RUBY><RB>(.*?)</RB><RT>(?:<COL [0-9a-fA-F]+>)?'
    r'(.*?)(?:</COL>)?</RT></RUBY>(?:<E519>)?', re.S)


def strip_ruby(text):
    """Fold ruby annotations back into the line.

    Ruby is furigana: small text set ABOVE the base word, so the engine
    reserves a whole row of vertical space for it -- which is why a line
    carrying one sits with a conspicuous gap above it.

    It exists to gloss kanji, and English has no kanji to gloss. Capcom's
    Japanese uses 3273 ruby spans; the English base game uses exactly
    zero, so dropping them is the game's own established convention and
    not a liberty taken here. Keeping them also meant inventing text for
    the reading slot -- 仕業/しわざ ("deed", read "shiwaza") had become
    base "doing" with a floating "at all" above it.

    Base and reading are concatenated: every case in this script reads
    naturally that way ("act of" + " outrage" -> "act of outrage")."""
    return RUBY_RE.sub(lambda m: m.group(1) + m.group(2), text)
from autowrap import rewrap_entry

HEADER_RE = re.compile(r'^#####\s+(\S+)\s+\(.*\)\s*(?:#####)?\s*$')
RUN_RE = re.compile(r'^\[(\d+)\]\s?(.*)$')
# markers added by chunk_runs.py -- the chunk marker actually carries the
# label too (chunk_runs.py doesn't repeat the ##### header separately), so
# it needs to be treated like a header for label-tracking purposes, not
# just skipped. The checkpoint marker carries no label info and really is
# pure navigation, so that one just gets skipped like a blank line.
CHUNK_MARKER_RE = re.compile(r'^-+\s*chunk\s+\d+\s*--\s*(\S+)\s*\(.*\)\s*-+\s*$', re.IGNORECASE)
CHECKPOINT_MARKER_RE = re.compile(r'^=+\s*REVIEW CHECKPOINT.*=+\s*$', re.IGNORECASE)


def parse_runs_file(path):
    """Returns {label: {run_index: translated_text}}."""
    translations = {}
    current_label = None
    current_idx = None
    current_lines = []

    def flush():
        if current_label is not None and current_idx is not None:
            # '\r\n', not '\n' -- this game's own line-break convention is
            # CRLF (confirmed by every JP source and official-script sample
            # examined all session; bare LF never appears). A multi-line
            # chunks entry always represents a genuine intended in-game
            # line break, so joining with plain '\n' silently embeds a
            # character the game doesn't recognize as a break at all --
            # confirmed by check_line_fit2.py: it only ever split on
            # literal '\r\n', so every multi-physical-line chunks entry
            # built through this path was invisible to line-length
            # checking and, more importantly, likely wasn't a real
            # on-screen break in the actual game either.
            text = '\r\n'.join(current_lines).rstrip()
            translations.setdefault(current_label, {})[current_idx] = text

    with io.open(path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            header_match = HEADER_RE.match(line)
            if header_match:
                flush()
                current_label = header_match.group(1)
                current_idx = None
                current_lines = []
                continue
            chunk_match = CHUNK_MARKER_RE.match(line)
            if chunk_match:
                flush()
                current_label = chunk_match.group(1)
                current_idx = None
                current_lines = []
                continue
            if CHECKPOINT_MARKER_RE.match(line):
                # pure navigation, carries no label info -- skip like blank
                continue
            run_match = RUN_RE.match(line)
            if run_match:
                flush()
                current_idx = int(run_match.group(1))
                text = run_match.group(2)
                # strip the sentence-end marker if present
                text = re.sub(r'\s*<==\s*likely sentence/thought END\s*$', '', text)
                current_lines = [text]
                continue
            # blank lines and chunk_runs.py markers are navigation aids,
            # not content -- skip them the same way
            if line.strip() == '':
                continue
            if CHUNK_MARKER_RE.match(line) or CHECKPOINT_MARKER_RE.match(line):
                continue
            # anything else is a continuation of the current run's text
            # (this is what captures multi-line / "gap" translations)
            if current_idx is not None:
                current_lines.append(line)
    flush()
    return translations


def main():
    runs_file, src_gmd, out_gmd = sys.argv[1], sys.argv[2], sys.argv[3]
    translations = parse_runs_file(runs_file)

    total_runs = sum(len(v) for v in translations.values())
    print(f'Parsed {len(translations)} labels, {total_runs} translated runs from {runs_file}')

    doc = parse_gmd_bytes(open(src_gmd, 'rb').read())
    changed = 0
    overfull_total = 0
    for e in doc['entries']:
        if e['label'] not in translations:
            continue
        tokens = tokenize(e['text'])
        if not verify_tags_unchanged(tokens, translations[e['label']]):
            print(f'!! TAG MISMATCH in {e["label"]} -- NOT applying this one, check your edits')
            continue
        text = strip_ruby(rebuild(tokens, translations[e['label']]))
        # Line breaks are a property of the box, not of the translation, so
        # they're placed here rather than by hand in the chunks file -- see
        # autowrap.py. Anything that genuinely cannot fit the 2-line box is
        # reported instead of being silently clipped on screen.
        text, overfull = rewrap_entry(text, e['label'])
        for page in overfull:
            overfull_total += 1
            print(f'!! OVERFULL {e["label"]}: needs shortening, cannot fit 2 lines')
            print(f'     {page!r}')
        e['text'] = text
        changed += 1

    blob = build_gmd_bytes(doc)
    open(out_gmd, 'wb').write(blob)
    print(f'Built {out_gmd} -- {changed} entries updated, {len(blob)} bytes')

    reparsed = parse_gmd_bytes(blob)
    print(f'Re-parsed OK, {len(reparsed["entries"])} entries')


if __name__ == '__main__':
    main()

"""
The real dialogue-box fit checker. Replaces check_line_fit2.py and
check_cntr_fit.py, both of which enforced only half the constraint and
used the wrong width metric.

Two independent constraints, both measured from the 8 officially
localized 3DS episodes rather than guessed:

1. LINES PER PAGE: at most 2.
   Measured across 2163 real pages: 40.6% are 1 line, 59.4% are 2 lines,
   and NOTHING is 3 or more. Not one exception. The box simply is two
   lines tall -- a third line is drawn clipped off the bottom edge
   (confirmed by in-game screenshots showing a half-cut third line).
   This is the constraint that a previous pass violated: fixing
   too-wide lines by inserting line breaks pushed pages to 3 and 4
   lines, trading a horizontal overflow for a worse vertical one.

2. LINE WIDTH: measured in proportional font units, not characters.
   See textwidth.py for why character count is not a usable proxy
   (a 45-char all-caps line overflowed while a 46-char mixed-case line
   fit). Real observed maxima: 19835 units for normal dialogue lines
   (n=3402), 23233 for the wider <CNTR> caption box (n=46).

Usage:
    python check_fit.py <translated_gmd> [more_gmds...]
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize
from textwidth import width

MAX_LINES_PER_PAGE = 2

# normal dialogue box
SAFE_W = 19000
HARD_W = 19976   # exact maximum in the pristine official v1.0.5 release
# wider centred-caption box
CNTR_SAFE_W = 21700
CNTR_HARD_W = 23233


def pages_of(entry_text):
    """Yield (is_cntr, [physical_line, ...]) for each <PAGE>-bounded screen."""
    toks = tokenize(entry_text)
    buf, cur, is_cntr = [], [], False
    for kind, s in toks:
        if kind == 'tag':
            if s == '<CNTR>':
                is_cntr = True
            if s == '<PAGE>':
                cur.append(''.join(buf))
                yield is_cntr, [l for l in cur if l.strip()]
                buf, cur, is_cntr = [], [], False
            continue
        if '\r\n' in s:
            parts = s.split('\r\n')
            buf.append(parts[0])
            cur.append(''.join(buf))
            for mid in parts[1:-1]:
                cur.append(mid)
            buf = [parts[-1]]
        else:
            buf.append(s)
    cur.append(''.join(buf))
    yield is_cntr, [l for l in cur if l.strip()]


def main():
    total_flagged = 0
    for gmd_path in sys.argv[1:]:
        print(f'########## {gmd_path} ##########')
        doc = parse_gmd_bytes(open(gmd_path, 'rb').read())
        pages = lines_checked = flagged = 0
        for e in doc['entries']:
            for is_cntr, lines in pages_of(e['text']):
                if not lines:
                    continue
                pages += 1
                safe_w = CNTR_SAFE_W if is_cntr else SAFE_W
                hard_w = CNTR_HARD_W if is_cntr else HARD_W
                tag = 'CNTR' if is_cntr else 'dlg'

                if len(lines) > MAX_LINES_PER_PAGE:
                    flagged += 1
                    print(f'!! {len(lines)} LINES  {e["label"]} [{tag}] '
                          f'(box holds {MAX_LINES_PER_PAGE})')
                    for l in lines:
                        print(f'     {width(l):6d}  {l!r}')

                for l in lines:
                    lines_checked += 1
                    w = width(l)
                    if w > hard_w:
                        flagged += 1
                        print(f'!! TOO WIDE  {e["label"]} [{tag}] '
                              f'w={w} (max {hard_w})')
                        print(f'     {l!r}')
                    elif w > safe_w:
                        flagged += 1
                        print(f'?  CLOSE     {e["label"]} [{tag}] '
                              f'w={w} (safe {safe_w})')
                        print(f'     {l!r}')

        print(f'-- {pages} pages, {lines_checked} lines, {flagged} flagged')
        print()
        total_flagged += flagged

    print(f'TOTAL FLAGGED: {total_flagged}')
    if total_flagged == 0:
        print('RESULT: clean -- every page fits the real 2-line box at real widths.')


if __name__ == '__main__':
    main()

"""
Checks whether translated English text is likely to overflow the game's
on-screen dialogue textbox.

Calibration note (important -- supersedes an earlier, wrong assumption):
this courtroom dialogue box DOES auto-wrap text by pixel width. That was
confirmed empirically by pulling the game's own OFFICIAL English script
(the Steam release, TGAAC, sce07 c001-c008 -- the officially localized
main-story episodes) and measuring real on-screen page lengths: a single
<PAGE>-bounded screen commonly renders 60-100+ characters of English
text wrapped across multiple visual lines, up to a measured max of 122
across a sample of 1656 real official pages. So the meaningful unit to
check is TOTAL characters per <PAGE> (per screen), not per raw '\\r\\n'
line -- a raw \\r\\n segment in the script is not one visual line, the
engine re-wraps it.

(An earlier, unrelated finding -- that a specific TGAA2 confirm-dialog
widget does NOT respect the <CNTR> tag and needed manual rewrapping --
does not apply to this courtroom dialogue box; that was a different,
narrower widget.)

Thresholds below are set directly from that real official-script sample:
  SAFE  <= 100   (well within normal official usage)
  CLOSE 100-122  (upper end of what's actually shipped -- worth a glance)
  OVER  > 122    (exceeds every officially shipped page in the sample)

This is still a heuristic based on character count, not a pixel-perfect
font-metric simulation -- treat "OVER" as "likely needs a look", not as
proof of an actual clip. For anything flagged, an in-emulator visual
check is the real confirmation.

Usage:
    python check_line_fit.py <translated_gmd> [safe_len] [hard_len]

Defaults: safe_len=100, hard_len=122
"""
import sys, re, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize

PAGE_RE = re.compile(r'<PAGE>')


def rendered_length(page_text):
    """Total rendered character count of a <PAGE>-bounded screen (tags
    excluded, all '\\r\\n'-separated raw lines within it summed together
    since the engine re-wraps them by pixel width, not by the raw
    line breaks)."""
    tokens = tokenize(page_text)
    return sum(len(s) for k, s in tokens if k == 'text')


def main():
    gmd_path = sys.argv[1]
    safe_len = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    hard_len = int(sys.argv[3]) if len(sys.argv) > 3 else 122

    doc = parse_gmd_bytes(open(gmd_path, 'rb').read())

    flagged = 0
    checked = 0
    for e in doc['entries']:
        label = e['label']
        pages = PAGE_RE.split(e['text'])
        for page_i, page in enumerate(pages):
            length = rendered_length(page)
            if length == 0:
                continue
            checked += 1
            if length > hard_len:
                flagged += 1
                preview = re.sub(r'\s+', ' ', ''.join(s for k, s in tokenize(page) if k == 'text')).strip()
                print(f'!! OVER   {label} page{page_i}  len={length}')
                print(f'     {preview!r}')
            elif length > safe_len:
                flagged += 1
                preview = re.sub(r'\s+', ' ', ''.join(s for k, s in tokenize(page) if k == 'text')).strip()
                print(f'?  CLOSE  {label} page{page_i}  len={length}')
                print(f'     {preview!r}')

    print()
    print(f'Checked {checked} pages/screens across {len(doc["entries"])} entries.')
    print(f'Flagged {flagged} (thresholds calibrated from 1656 real official-script pages: safe<={safe_len}, hard<={hard_len}).')
    if flagged == 0:
        print('RESULT: clean -- nothing exceeds what the official localization itself ships.')
    else:
        print('RESULT: see flagged lines above. "!! OVER" = longer than any officially shipped page in the sample, worth tightening or verifying in-emulator. "? CLOSE" = within the upper range of official usage, probably fine.')


if __name__ == '__main__':
    main()

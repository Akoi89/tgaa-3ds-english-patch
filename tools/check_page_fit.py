"""
Checks total rendered character count per <PAGE>-bounded screen for the
REGULAR (non-CNTR) dialogue textbox -- calibrated from real, decrypted
3DS retail data, not the Steam/Switch remaster.

Why this replaces the earlier Steam-based calibration: that one used the
officially localized Steam/Switch script (1656 pages, up to 122 chars,
95th percentile 108) as its reference, reasoning the two releases share
the same story text. They don't share the same TEXTBOX -- confirmed
directly by extracting the actual decrypted 3DS DLC's own English script
across all 8 officially localized episodes (1942 real pages): max 100
characters, 95th percentile just 80, median 48. The Steam calibration
was measuring a wider/different box the whole time.

Thresholds: safe<=80 (95th-percentile line for real 3DS content),
hard<=95 (a small margin under the observed real max of 100).

This is still a heuristic -- character count, not pixel width -- but
it's grounded in real shipped 3DS text now, not a different platform.

Usage:
    python check_page_fit.py <translated_gmd> [safe_len] [hard_len]
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes

PAGE_RE = re.compile(r'<PAGE>')
TAG_RE = re.compile(r'<[^>]*>')


def main():
    gmd_path = sys.argv[1]
    safe_len = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    hard_len = int(sys.argv[3]) if len(sys.argv) > 3 else 95

    doc = parse_gmd_bytes(open(gmd_path, 'rb').read())

    flagged = 0
    checked = 0
    for e in doc['entries']:
        label = e['label']
        pages = PAGE_RE.split(e['text'])
        for page_i, page in enumerate(pages):
            clean_display = TAG_RE.sub('', page)
            length = len(clean_display.replace('\r', '').replace('\n', ''))
            if length == 0:
                continue
            checked += 1
            display = clean_display.replace('\r\n', ' / ')
            if length > hard_len:
                flagged += 1
                print(f'!! OVER   {label} page{page_i}  len={length}')
                print(f'     {display!r}')
            elif length > safe_len:
                flagged += 1
                print(f'?  CLOSE  {label} page{page_i}  len={length}')
                print(f'     {display!r}')

    print()
    print(f'Checked {checked} pages/screens across {len(doc["entries"])} entries.')
    print(f'Flagged {flagged} (thresholds from 1942 real decrypted-3DS pages: safe<={safe_len}, hard<={hard_len}).')
    if flagged == 0:
        print('RESULT: clean -- nothing exceeds real 3DS-observed page lengths.')


if __name__ == '__main__':
    main()

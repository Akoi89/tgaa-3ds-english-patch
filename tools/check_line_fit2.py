"""
Checks EVERY physical line (split on '\\r\\n' within a <PAGE>-bounded
screen) against a per-line character limit -- not the page's aggregate
total. This replaces check_page_fit.py, which measured the WRONG thing:
it summed all text within a page across however many physical lines it
had, which is only meaningful if the box's real constraint is "total
capacity across N lines" -- it isn't. Confirmed wrong by an in-game
screenshot: a fix that combined a 34-char line and a 59-char line (page
total 90, under the old 95 "safe" threshold) still overflowed on screen,
because the SECOND line alone (59 chars) exceeds the real per-line
limit.

Real calibration: measured every physical line across all 8 officially
localized 3DS DLC episodes' real script (3152 lines): median 31, 95th
percentile 41, max 52. That max lines up almost exactly with the CNTR
caption box's own measured max (52) -- strong evidence the regular
dialogue box and the CNTR box share the same effective line width, and
that "up to 100 characters" from the old page-aggregate measurement was
never a real single-line capacity.

Thresholds: safe<=41 (real 95th percentile), hard<=48 (small margin
under the observed real max of 52).

Usage:
    python check_line_fit2.py <translated_gmd> [safe_len] [hard_len]
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize


def main():
    gmd_path = sys.argv[1]
    safe_len = int(sys.argv[2]) if len(sys.argv) > 2 else 41
    hard_len = int(sys.argv[3]) if len(sys.argv) > 3 else 48

    doc = parse_gmd_bytes(open(gmd_path, 'rb').read())

    flagged = 0
    checked = 0

    def check_line(label, text):
        nonlocal flagged, checked
        if not text.strip():
            return
        length = len(text)
        checked += 1
        if length > hard_len:
            flagged += 1
            print(f'!! OVER  {label}  len={length}')
            print(f'     {text!r}')
        elif length > safe_len:
            flagged += 1
            print(f'?  CLOSE {label}  len={length}')
            print(f'     {text!r}')

    for e in doc['entries']:
        label = e['label']
        tokens = tokenize(e['text'])
        buf = []
        for kind, s in tokens:
            if kind == 'tag':
                if s == '<PAGE>':
                    check_line(label, ''.join(buf))
                    buf = []
                continue
            if not s:
                continue
            if '\r\n' in s:
                parts = s.split('\r\n')
                buf.append(parts[0])
                check_line(label, ''.join(buf))
                for mid in parts[1:-1]:
                    check_line(label, mid)
                buf = [parts[-1]]
            else:
                buf.append(s)
        check_line(label, ''.join(buf))

    print()
    print(f'Checked {checked} physical lines.')
    print(f'Flagged {flagged} (thresholds from 3152 real decrypted-3DS lines: safe<={safe_len}, hard<={hard_len}).')
    if flagged == 0:
        print('RESULT: clean -- nothing exceeds real 3DS-observed line lengths.')


if __name__ == '__main__':
    main()

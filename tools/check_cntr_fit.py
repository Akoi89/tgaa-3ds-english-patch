"""
Checks CNTR-tagged text for textbox overflow -- a DIFFERENT, much narrower
UI widget than the regular auto-wrapping dialogue box, confirmed broken by
direct in-game screenshots (both the "Presentation" debug-note box and the
date/location caption box cut text off mid-word instead of wrapping).

Why <CNTR> specifically: every confirmed-overflowing line in-game traces
back to a <CNTR> tag governing that physical line -- the date/location
caption, and the "(...my 'fate' will be decided...)" internal monologue
both use it. Regular testimony dialogue (no <CNTR>) is NOT known to have
this problem.

State model: a <CNTR> tag turns on CNTR-governed mode for the rest of the
entry until a <PAGE> tag ends it (confirmed from the source: CNTR is
re-stated redundantly at the start of each physical line within a block,
but never appears again once the block's <PAGE> is reached). Every '\\r\\n'
encountered while CNTR-governed ends the current physical line and starts
a new one; the closing <PAGE> flushes whatever's left, regardless of
whether a '\\r\\n' happened to fall right before it.

For every CNTR-governed physical line, this sums its rendered text length
and compares against a threshold calibrated from REAL, decrypted 3DS
retail data -- not a screenshot guess, not the Steam/Switch remaster
(both of those turned out to be wrong in earlier passes: the Steam
script's own wording for this exact box, "...Antechamber 5" WITH "of
Judicature", turned out to be 14 characters longer than what the actual
3DS DLC ships, "Supreme Court, Defendants' Antechamber 5" -- 40 chars).
Extracted and measured all CNTR lines across all 8 officially localized
DLC episodes' actual 3DS script files (42 real lines): max 52 characters,
several confirmed lines in the high 40s. So safe<=46, hard<=52 reflects
the real ceiling with a small margin, not a guess.

This is still a heuristic (character count, not pixel width), but it's
now grounded in real shipped 3DS text rather than a different platform's
script or a single screenshot's visible cutoff point.

Usage:
    python check_cntr_fit.py <translated_gmd> [safe_len] [hard_len]
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize


def main():
    gmd_path = sys.argv[1]
    safe_len = int(sys.argv[2]) if len(sys.argv) > 2 else 46
    hard_len = int(sys.argv[3]) if len(sys.argv) > 3 else 52

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
        in_cntr = False
        line_buf = []

        for kind, s in tokens:
            if kind == 'tag':
                if s == '<CNTR>':
                    in_cntr = True
                elif s == '<PAGE>':
                    if in_cntr:
                        check_line(label, ''.join(line_buf))
                    in_cntr = False
                    line_buf = []
                continue
            if not s or not in_cntr:
                continue
            if '\r\n' in s:
                parts = s.split('\r\n')
                line_buf.append(parts[0])
                check_line(label, ''.join(line_buf))
                for mid in parts[1:-1]:
                    check_line(label, mid)
                line_buf = [parts[-1]]
            else:
                line_buf.append(s)

        # entry ended without a trailing <PAGE> -- flush any remainder
        if in_cntr:
            check_line(label, ''.join(line_buf))

    print()
    print(f'Checked {checked} CNTR-governed physical lines.')
    print(f'Flagged {flagged} (thresholds calibrated from confirmed in-game screenshots: safe<={safe_len}, hard<={hard_len}).')
    if flagged == 0:
        print('RESULT: clean -- no CNTR line overflow detected.')


if __name__ == '__main__':
    main()

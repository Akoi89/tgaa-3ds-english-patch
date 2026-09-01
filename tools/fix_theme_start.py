"""Restores THEME_START, which senyarom's port flattens into plain text.

Every DLC issue ships a 3DS HOME-menu theme, and pressing "Theme" on the
issue's detail screen shows an acknowledgement telling you where to apply
it. Capcom's message carries a choice control:

    <CHOI 1><CLS>専用のテーマが追加されています！...

`scripts/port_tgaa1_dlc_official.py` overwrites it unconditionally:

    for label in ("THEME_START", "OMNIBUS2_START", ...):
        _set_plain(entries[label], "Invalid Message")

`_set_plain` writes a bare string, so the <CHOI 1> goes with it. The
screen opens expecting a choice widget, finds none, and falls back to the
menu -- the reported bounce.

"Invalid Message" is Capcom's own placeholder for genuinely unused slots
(OMNIBUS3/4_START are already that in the Japanese), so the string is not
the problem; using it on a slot that IS in use, and dropping the control
tag with it, is.

Only THEME_START is restored. MOVIE2_START is set conditionally upstream
and is correct, and OMNIBUS2_START really is unused in issues 0-8.

Usage:
    python fix_theme_start.py <dlc_romfs_root> [--apply]
"""
import os
import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

# Mirrors Capcom's own wording and its <CHOI 1> single-acknowledgement
# form; the Japanese trails a (仮) "provisional" dev marker, dropped here.
THEME_TEXT = ('<CHOI 1><CLS>A special theme has been added!\r\n'
              'You can apply it from "Theme Settings"\r\n'
              'in the HOME Menu settings.')


def main():
    root = sys.argv[1]
    apply = '--apply' in sys.argv
    fixed = 0
    for fn in sorted(glob.glob(os.path.join(root, '**', 'msg', 'aoc*.gmd'),
                               recursive=True)):
        doc = parse_gmd_bytes(open(fn, 'rb').read())
        hit = False
        for e in doc['entries']:
            if e['label'] == 'THEME_START' and e['text'] == 'Invalid Message':
                e['text'] = THEME_TEXT
                hit = True
        if hit:
            fixed += 1
            print(f'  restored THEME_START in {os.path.basename(fn)}')
            if apply:
                open(fn, 'wb').write(build_gmd_bytes(doc))
    print(f'\n{fixed} DLC issues fixed')
    if not apply:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()

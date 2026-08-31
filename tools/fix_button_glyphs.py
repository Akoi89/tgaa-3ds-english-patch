"""
Replaces the port's invented button-icon tags with words.

The 3DS patch writes control references as tags -- <E683>..<E686>,
<E691>..<E702> -- that no engine implements. Capcom never uses them,
Scarlet Study never uses them, and they do not appear in the official PC
script either; they are written by hand in the port's own build script
(scripts/build_3ds_official_layout.py). The 3DS renders an unknown tag as
nothing, so the player reads "with a press of ." and "(I need to use , ,
and ...".

The replacement wording follows Capcom's own Japanese, which describes a
touch UI and names the on-screen control rather than a hardware button:

    【法廷記録】を"タッチ"      touch the Court Record
    【もどる】といい           touch back
    【つきつける】にタッチ      touch Present
    【調べる】をタッチ          touch Examine
    下画面の、２つの《ダイヤル》 the two dials on the bottom screen
    《操作盤タッチパネル》       the touch panel

Scarlet Study independently arrived at the same solution ("Go ahead and
tap the Court Record button in the top-right corner of the bottom
screen"), which is good evidence it reads naturally in English too.

Each replacement keeps the surrounding tags -- the <E436>/<FONT 2>
highlighting on control names, the <E003> pauses -- and only rewrites the
words around the dead tag.

Usage:
    python fix_button_glyphs.py <romfs_dir> [--apply]
"""
import sys, os, re, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

DIALS = ('<E701><E003 1><E086 0 0><E692><E003 1><E086 0 0>'
         '<E702><E003 1><E086 0 0><E700>')
PANEL = ('<E003 1><E086 0 0><E691><E003 1><E086 0 0>'
         '<E699><E003 1><E086 0 0><E697>')
DIALS2 = ('<E701><E003 2><E086 0 0><E692><E003 2><E086 0 0>'
          '<E702><E003 2><E086 0 0><E700>')
PANEL2 = ('<E003 2><E086 0 0><E691><E003 2><E086 0 0>'
          '<E699><E003 2><E086 0 0><E697>')

# (file, label, old, new)
EDITS = [
    ('_sce00_c001_0002', 'L_FLASH_END_00_00',
     '<E005> with a press of <E086 0 0><E683>.',
     '<E005> by touching it.'),
    ('_sce00_c001_0002', 'L_FLASH_END_00_00',
     '(Press <E005><E683><E007> for the ',
     '(Touch the '),
    ('_sce00_c001_0002', 'L_FLASH_END_00_00',
     "<E005>' with <E086 0 0><E683>.",
     "<E005>' by touching it."),
    ('_sce00_c001_0002', 'L_FLASH_END_00_00',
     ' press <E684> to go <E014><E436><FONT 2>back<E437></FONT><E005>.',
     ' touch <E014><E436><FONT 2>back<E437></FONT><E005> to return.'),

    ('_sce00_c001_0002', 'L_TF_START_0',
     " then press\r\n<E685> to '",
     " then touch\r\n'"),

    ('_sce00_c004_0002', 'L_FOLLOW_0',
     'giving testimony by pressing <E683>.',
     'giving testimony by touching it.'),
    ('_sce00_c004_0002', 'L_FOLLOW_0',
     ' your evidence with\r\n<E685>,',
     ' your evidence by\r\ntouching it,'),

    ('_sce00_c005_0001', 'L_FOLLOW_1',
     'Press <E686>,', 'Touch it,'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     'Use ' + DIALS + '...', 'Use the two dials...'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     'By using ' + PANEL + '...', 'By using the touch panel...'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     'press <E686> to <E014>', 'touch <E014>'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     '<E005>' + DIALS2 + '<E007>', '<E005>the two dials<E007>'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     '<E005>' + PANEL2 + '<E007>', '<E005>the touch panel<E007>'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     'and <E005><E686><E007>', 'and <E005>Examine<E007>'),

    ('_sce00_c013_0001', 'L_MIMWASU_TUTORIAL',
     'right with <E086 0 0><E694><E003 1><E086 0 0>, ',
     'right on the bottom screen, '),
    ('_sce00_c013_0001', 'L_MIMWASU_TUTORIAL',
     "<E005>' them with <E686>.", "<E005>' them by touching."),
    ('_sce00_c013_0001', 'L_MIMWASU_TUTORIAL',
     ' across with<E023><PAGE>\r\n<E041 1 0><E025 2.5>'
     '<E086 0 0><E694><E003 1><E086 0 0>,',
     ' across,<E023><PAGE>\r\n<E041 1 0><E025 2.5>'),
    ('_sce00_c013_0001', 'L_MIMWASU_TUTORIAL',
     ' him with <E686>,', ' him,'),

    ('_sce01_bg1100_3d_check_0', 'L_BG1100_CAMERA_TUTORIAL_0',
     'all around using<E358><E003 1> <E086 0 1><E694><E003 2><E086 0 1>,',
     'all around,'),

    ('_sce01_c001_0000', 'L_START',
     'If you press <E686> on people when', 'If you touch people when'),
]

# A second pass, tidying the seams the replacements left behind: a
# preposition that no longer has an icon to govern, and the double spaces
# and orphan leading spaces where a tag used to sit between punctuation.
POLISH = [
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     '...touch <E014><E436><FONT 2>Investigate<E437></FONT><E005> further.',
     '...touch <E014><E436><FONT 2>Investigate<E437></FONT><E005>.'),
    ('_sce00_c005_0001', 'L_FOLLOW_1',
     '(I need to use <E005>the two dials<E007>,<E003 8> '
     '<E086 0 0><E005>the touch panel<E007>,<E003 8> '
     'and <E005>Examine<E007>...<E003 10><E341>to\r\n'
     'inspect any areas of the',
     '(I need to use the dials,<E003 8> the touch\r\n'
     'panel<E007>,<E003 8> and <E005>Examine<E007>'
     '...<E003 10><E341>to inspect the'),
    ('_sce00_c013_0001', 'L_MIMWASU_TUTORIAL',
     'right on the bottom screen, <E358><E003 12> <E333>you can ',
     'right on the bottom screen,<E358><E003 12> <E333>you can '),
    ('_sce00_c013_0001', 'L_MIMWASU_TUTORIAL',
     '<E041 1 0><E025 2.5><E358><E003 8> and focus on the detective.',
     '<E041 1 0><E025 2.5><E358><E003 8>and focus on the detective.'),
]
EDITS = EDITS + POLISH

BROKEN = re.compile(r'<E(?:68[3-6]|69[1279]|70[012]|694)>')


def main():
    root = sys.argv[1]
    apply = '--apply' in sys.argv
    by_file = {}
    for f, lab, old, new in EDITS:
        by_file.setdefault(f, []).append((lab, old, new))

    applied = missed = 0
    for f, edits in by_file.items():
        path = os.path.join(root, 'script', '_output', f + '_jpn.gmd')
        doc = parse_gmd_bytes(open(path, 'rb').read())
        entries = {e['label']: e for e in doc['entries']}
        for lab, old, new in edits:
            e = entries.get(lab)
            if e is None or old not in e['text']:
                print(f'!! NOT FOUND {f} :: {lab} -> {old[:48]!r}')
                missed += 1
                continue
            e['text'] = e['text'].replace(old, new)
            applied += 1
        if apply:
            open(path, 'wb').write(build_gmd_bytes(doc))

    print(f'\napplied {applied} replacements, {missed} not found')

    # nothing broken may survive anywhere
    left = 0
    for fn in glob.glob(os.path.join(root, '**', '*.gmd'), recursive=True):
        try:
            doc = parse_gmd_bytes(open(fn, 'rb').read())
        except Exception:
            continue
        for e in doc['entries']:
            for m in BROKEN.finditer(e['text']):
                left += 1
                print(f'   REMAINS {os.path.basename(fn)} :: {e["label"]} '
                      f'{m.group(0)}')
    print(f'broken glyph tags remaining: {left}')
    if not apply:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()

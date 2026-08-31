"""Fixes ellipsis typos in the base game.

Capcom's English convention is runs of 3, 6 or 9 dots only (verified across
every shipped page). Five runs in the port break it -- 2, 4 and 11 dots --
which read as stray or missing punctuation rather than a pause.
"""
import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

# (file, label, old, new) -- exact strings, so nothing else can match
EDITS = [
    ('_sce00_c004_0003', 'L_START',     'that....',      'that...'),
    ('_sce00_c005_0004', 'L_TF_OK_0',   'Wha...?',       'Wha...?'),   # fine
    ('_sce00_c005_0004', 'L_TF_OK_0',   'were..?',       'were...?'),
    ('_sce03_chr205_00', 'L_TOPIC_1_07','situation..',   'situation...'),
    ('_sce04_c202_0004', 'L_TF_OK_1',   '...........',   '.........'),
    ('_sce04_chr030_00', 'L_TUKI_1_02', 'so I....',      'so I...'),
]

def main():
    root = sys.argv[1]
    apply = '--apply' in sys.argv
    n = 0
    for f, lab, old, new in EDITS:
        if old == new:
            continue
        p = os.path.join(root, 'script', '_output', f + '_jpn.gmd')
        doc = parse_gmd_bytes(open(p, 'rb').read())
        hit = False
        for e in doc['entries']:
            if e['label'] == lab and old in (e['text'] or ''):
                e['text'] = e['text'].replace(old, new)
                hit = True
        if hit:
            n += 1
            print(f'  {f} :: {lab}   {old!r} -> {new!r}')
            if apply:
                open(p, 'wb').write(build_gmd_bytes(doc))
        else:
            print(f'  !! NOT FOUND {f} :: {lab} {old!r}')
    print(f'\n{n} fixed')
    if not apply:
        print('(dry run)')

if __name__ == '__main__':
    main()

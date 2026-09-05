# -*- coding: utf-8 -*-
"""Parity manifest: every English audio file Chronicles ships, against our builds.

The existing `audit_all_audio.py` answers a different and harder question --
is a clip we ship actually the English recording -- by correlating decoded audio
against Chronicles. It needs ffmpeg, which is not installed on this machine, and
it only walks the story-voice index.

This is the accounting question instead, over ALL SIX places Chronicles keeps
English audio: for each of its English files, does a 3DS counterpart exist, and
does our patch ship a file for it?

    A  SHIPPED    our trees carry a file of that name
    B  UNSHIPPED  the 3DS has that slot, our trees do not touch it
    C  NO SLOT    no 3DS file of that name exists in either game

C is expected and is not a gap: Chronicles is a PC build of both games and
carries assets the 3DS releases never had. Counting it as a miss would
manufacture false alarms, which is the failure mode three earlier detectors in
this project had.

    python audit_526.py            summary
    python audit_526.py --list B   name every clip in a category
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from dgs2tool.arc import parse_arc

STEAM = os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64')
AUDIT = os.path.join(ROOT, 'dlc_story_audit')

# Where Chronicles keeps English audio, and what each set is.
SOURCES = [
    ('story voices', 'sound/stream/voice/wav', '_eng.sngw'),
    ('DLC gallery', 'sound/stream/special/wav', '_eng.sngw'),
    ('jury / crowd', 'sound/stream/se/wav', '_eng.sngw'),
    ('cutscene stems', 'sound/stream/anime/wav', '_eng.sngw'),
    ('title logo', 'sound/stream/mp/wav', '_eng.sngw'),
    ('shouts', 'sound/se', '_eng.xsew'),
]

# What we actually SHIP: the romfs of the four current CIAs, extracted by
# extract_shipped.py. Deliberately NOT the working trees -- this project has
# twice been misled by a tree that had drifted from the build it claimed to be.
SHIPPED = os.path.join(HERE, '_shipped')
JAPANESE = [
    ('TGAA1 base', 'basegame/rom'),
    ('TGAA1 DLC', 'bounce/engd'),
    ('TGAA2 DLC', 'tgaa2/dlc/jp_idx2_dir'),
]
# TGAA2's base romfs is not extracted here; its file listing is.
JP_LISTING = os.path.join(AUDIT, 'dgs2_base_romfs_list.txt')


def stem(name):
    """A comparable key: drop the extension and any language suffix."""
    base = name.rsplit('.', 1)[0]
    for suf in ('_eng', '_jpn'):
        if base.endswith(suf):
            base = base[:-len(suf)]
    return base


def names_in_tree(root):
    """Every audio name in a tree, loose or inside an .arc."""
    out = set()
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.endswith(('.mca', '.sngw', '.xsew')):
                out.add(stem(fn))
            elif fn.endswith('.arc'):
                try:
                    arc = parse_arc(open(os.path.join(dirpath, fn), 'rb').read())
                except Exception:
                    continue
                for e in arc['entries']:
                    if e.data[:4] in (b'MADP', b'RIFF', b'OggS'):
                        out.add(stem(e.name.replace('\\', '/').split('/')[-1]))
    return out


def main():
    chronicles = []
    for label, rel, suffix in SOURCES:
        base = os.path.join(STEAM, *rel.split('/'))
        for dirpath, _, files in os.walk(base):
            for fn in sorted(files):
                if fn.endswith(suffix):
                    chronicles.append((label, fn, stem(fn)))
    print('Chronicles English audio: %d files' % len(chronicles))
    for label, n in collections.Counter(c[0] for c in chronicles).most_common():
        print('   %-16s %d' % (label, n))

    ours = set()
    print('\nwhat the four shipped CIAs actually contain')
    if not os.path.isdir(SHIPPED):
        raise SystemExit('run extract_shipped.py first')
    for build in sorted(os.listdir(SHIPPED)):
        p = os.path.join(SHIPPED, build)
        if not os.path.isdir(p):
            continue
        got = names_in_tree(p)
        ours |= got
        print('   %-34s %d audio names' % (build, len(got)))

    jp = set()
    for label, rel in JAPANESE:
        p = os.path.join(AUDIT, *rel.split('/'))
        if os.path.isdir(p):
            jp |= names_in_tree(p)
    if os.path.exists(JP_LISTING):
        for line in open(JP_LISTING, encoding='utf-8', errors='replace'):
            t = line.strip()
            if t.endswith(('.mca', '.sngw', '.xsew')):
                jp.add(stem(t))
    print('   %-20s %-34s %d audio names' % ('3DS Japanese', '(base + DLC)', len(jp)))

    cat = collections.defaultdict(list)
    for label, fn, key in chronicles:
        if key in ours:
            cat['A'].append((label, fn))
        elif key in jp:
            cat['B'].append((label, fn))
        else:
            cat['C'].append((label, fn))

    print('\n%-3s %-38s %s' % ('', 'category', 'count'))
    for k, desc in (('A', 'SHIPPED   our trees carry it'),
                    ('B', 'UNSHIPPED 3DS slot exists, untouched'),
                    ('C', 'NO SLOT   no 3DS counterpart exists')):
        print('%-3s %-38s %d' % (k, desc, len(cat[k])))
    print('%-3s %-38s %d' % ('', 'total', sum(len(v) for v in cat.values())))

    for k in ('B', 'C'):
        by = collections.Counter(l for l, _ in cat[k])
        if by:
            print('\ncategory %s by set: %s'
                  % (k, ', '.join('%s %d' % (a, b) for a, b in by.most_common())))

    if '--list' in sys.argv:
        want = sys.argv[sys.argv.index('--list') + 1].upper()
        print('\ncategory %s, in full:' % want)
        for label, fn in sorted(cat[want]):
            print('   %-16s %s' % (label, fn))


if __name__ == '__main__':
    main()

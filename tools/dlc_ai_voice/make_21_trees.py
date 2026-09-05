# -*- coding: utf-8 -*-
"""Stage the 21 cues into copies of the two shipped base-update romfs trees.

An update romfs is an overlay: it carries only the files that changed. None of
these cues has ever been in one, so each has to be brought in from the Japanese
base first, replaced, and -- for the streamed cues -- accompanied by
`sound/stream/se/bb_se.stqr`, because an index left behind in the base would
still describe Capcom's file and the cue would play silence.

That is the same pattern the shipped updates already use for voice and anime:
TGAA1's update carries go_nrt_voice.stqr and go_trial_voice.stqr, TGAA2's
carries bb_voice_jpn.stqr, each alongside the streams it changed.

    python make_21_trees.py            build both trees under _tree21/
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

from import_21 import CROWD, DANCE, find_one

SHIPPED = os.path.join(HERE, '_shipped')
OUT = os.path.join(HERE, '_tree21')
GAMES = [
    ('TGAA1', 'TGAA1-base-1.0.19', os.path.join(ROOT, 'dlc_story_audit', 'basegame', 'rom')),
    ('TGAA2', 'TGAA2-base-1.0.13', os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs')),
]
# The two games do not name this index the same thing: TGAA2 has bb_se.stqr,
# TGAA1 has go_se.stqr. Discover it rather than hardcode either.
INDEX_DIR = os.path.join('sound', 'stream', 'se')


def stage(game, build, jp_root):
    src = os.path.join(SHIPPED, build, 'content0')
    if not os.path.isdir(src):
        raise SystemExit('%s not extracted; run extract_shipped.py' % build)
    dest = os.path.join(OUT, game)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    print('%s: copying the shipped update tree' % game)
    shutil.copytree(src, dest)

    brought = 0
    for name in CROWD + DANCE:
        jp = find_one(jp_root, name + '.mca')
        if not jp:
            continue
        rel = os.path.relpath(jp, jp_root)
        dst = os.path.join(dest, rel)
        if os.path.exists(dst):
            continue                      # already carried by the update
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(jp, dst)
        brought += 1
    # the stream index has to travel with the streams
    jp_dir = os.path.join(jp_root, INDEX_DIR)
    found = [f for f in os.listdir(jp_dir) if f.endswith('.stqr')] \
        if os.path.isdir(jp_dir) else []
    if not found:
        raise SystemExit('%s: no .stqr in %s -- the streamed cues would go stale'
                         % (game, INDEX_DIR))
    for fn in found:
        dst = os.path.join(dest, INDEX_DIR, fn)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copyfile(os.path.join(jp_dir, fn), dst)
            print('   brought in %s from the Japanese base' % fn)
    print('   %d Capcom originals brought in from the base romfs' % brought)

    r = subprocess.run([sys.executable, os.path.join(HERE, 'import_21.py'),
                        '--tree', dest, '--game', game, '--fit', '--apply'])
    if r.returncode != 0:
        raise SystemExit('import_21 failed for %s' % game)

    # A cue import_21 refused (sprechchor_02_st in TGAA2) would otherwise be
    # left behind as an unchanged Japanese copy. An update romfs should carry
    # only what actually changed, so drop anything identical to the base.
    dropped = 0
    for name in CROWD + DANCE:
        jp = find_one(jp_root, name + '.mca')
        if not jp:
            continue
        p = os.path.join(dest, os.path.relpath(jp, jp_root))
        if os.path.exists(p) and open(p, 'rb').read() == open(jp, 'rb').read():
            os.remove(p)
            dropped += 1
    if dropped:
        print('   dropped %d unchanged cue(s) from the overlay' % dropped)
    return dest


def main():
    os.makedirs(OUT, exist_ok=True)
    for game, build, jp in GAMES:
        dest = stage(game, build, jp)
        n = sum(len(f) for _, _, f in os.walk(dest))
        print('   %s tree ready: %d files\n' % (game, n))


if __name__ == '__main__':
    main()

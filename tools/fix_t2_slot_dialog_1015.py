# -*- coding: utf-8 -*-
"""TGAA2 base 1.0.15: three string fixes from issue #1 report 4 (Gemini verdicts A / A / A).

Source tree is the SHIPPED 1.0.14 romfs (extracted from Final/_CURRENT by extract_shipped),
never a working tree. Only archive/msg_cmn_jpn.arc and the title atlas change.

    system_jpn.gmd  RETURN_CONF_01              3 lines (189/323/332) -> 4 lines (max 246)
                    GAMEOVER_RETURN_TITLE_CONF  2 lines (218/332)     -> 3 lines (max 218)
    title_jpn.gmd   SCE_TITLE00                 <SIZE 12> -> <SIZE 11> (274 units in a ~265 slot)
                    CHAP_MODE_*                 prepend <SIZE 12>, append a space (experiment:
                                                does the size carry into the appended place name?)

Every arc/gmd rebuild is null-tested (rebuild with no change == original bytes) before use.

    python fix_t2_slot_dialog_1015.py            dry run, prints the diff
    python fix_t2_slot_dialog_1015.py --build    patch tree, stamp, build the CIA, verify
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch')))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dgs2tool.arc import parse_arc, build_arc_bytes
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from cia import Cia

SHIPPED = os.path.join(ROOT, 'dlc_ai_voice', '_shipped', 'TGAA2-base-1.0.14', 'content0')
SHELL = os.path.join(ROOT, 'Final', '_CURRENT', 'TGAA2-base-1.0.14.cia')
WORK = os.path.join(ROOT, 'dlc_story_audit', 'tgaa2', 'v1015_dir')
OUT = os.path.join(ROOT, 'dlc_story_audit', '_validation', 'TGAA2-base-1.0.15-rc1.cia')
CLEAN_PLATE = os.path.join(ROOT, 'dlc_story_audit', 'tgaa2', 'v233_dir',
                           'UI', '4_menu', '40_title', 'tex', 'title_jpn_01_BM_NOMIP_HQ.tex')
ATLAS_REL = os.path.join('UI', '4_menu', '40_title', 'tex', 'title_jpn_01_BM_NOMIP_HQ.tex')
ARC_REL = os.path.join('archive', 'msg_cmn_jpn.arc')
VERSION = '1.0.15'
STAMP = 'ENG 1.0.15'
TOOL = os.path.join(ROOT, '3dstool', '3dstool.exe')

CRLF = '\r\n'
EDITS = {
    'msg/system_jpn.gmd': {
        'RETURN_CONF_01': '<CHOI 2 1 1><CLS>' + CRLF.join([
            "You haven't saved your game.",
            'Any progress since your previous save',
            'will be lost. Are you sure you want',
            'to return to the Title screen?']),
        'GAMEOVER_RETURN_TITLE_CONF': '<CHOI 2 1 1>' + CRLF.join([
            'Any unsaved progress will be lost.',
            'Are you sure you want to return',
            'to the Title screen?']),
    },
    'msg/title_jpn.gmd': {
        'SCE_TITLE00': '<FONT 0><SIZE 11>The Adventure of the Blossoming Attorney',
    },
}
# rc2 (user's suggestion on the rig, 2026-09-05): shrink the "Ep. N:" prefix instead of the
# title, so every title stays at SIZE 12. rc1's SIZE 11 title rendered thin and broken.
# The chapter row at SIZE 12 was no longer squashed but too small and lost its spaces; rc2
# probes SIZE 15 to find the row's real budget. Engine inserts ": " between the two strings.
VARIANT = 'rc2' if '--rc2' in sys.argv else 'rc1'
if VARIANT == 'rc2':
    EDITS['msg/title_jpn.gmd'] = {
        'SCE_TITLE00': '<FONT 0><SIZE 12>The Adventure of the Blossoming Attorney',
        'SCE_NUM00': '<FONT 2><SIZE 12>Ep. 1:',
        'SCE_NUM01': '<FONT 2><SIZE 12>Ep. 2:',
        'SCE_NUM02': '<FONT 2><SIZE 12>Ep. 3:',
        'SCE_NUM03': '<FONT 2><SIZE 12>Ep. 4:',
        'SCE_NUM04': '<FONT 2><SIZE 12>Final:',
    }
    OUT = OUT.replace('rc1', 'rc2')
    WORK = WORK.replace('v1015_dir', 'v1015rc2_dir')
# rc3: rc2 showed the title's x origin is FIXED (a smaller prefix left the title where it
# was, still clipped), and the SIZE 12 prefix rendered broken. So carry the title inside the
# prefix string, which starts ~50 screen px further left, and empty the title string.
# Other four episodes: stock-shaped prefix, SIZE 12 title (they fit). Chapter row SIZE 15.
if '--rc3' in sys.argv:
    VARIANT = 'rc3'
    EDITS['msg/title_jpn.gmd'] = {
        'SCE_NUM00': '<FONT 2>Ep. 1: <FONT 0><SIZE 12>The Adventure of the Blossoming Attorney',
        'SCE_TITLE00': ' ',
    }
    OUT = OUT.replace('rc1', 'rc3')
    WORK = WORK.replace('v1015_dir', 'v1015rc3_dir')
# rc4: rc3 showed the merged string starts the title exactly where the separate title did
# (the old anchor sat at the prefix's end), so nothing moved. Shrinking the prefix INSIDE the
# merged string does move the title left (prefix full size is FONT 2 at 20 px; SIZE 15 saves
# about 12 screen px, the clipped letter needs about 5). Same form on all five for consistency.
if '--rc4' in sys.argv:
    VARIANT = 'rc4'
    _T = ['The Adventure of the Blossoming Attorney', 'The Memoirs of the Clouded Kokoro',
          'The Return of the Great Departed Soul', 'Twisted Karma and His Last Bow',
          'The Resolve of Ryunosuke Naruhodo']
    _P = ['Ep. 1:', 'Ep. 2:', 'Ep. 3:', 'Ep. 4:', 'Final:']
    EDITS['msg/title_jpn.gmd'] = {}
    for _i in range(5):
        EDITS['msg/title_jpn.gmd']['SCE_NUM0%d' % _i] = '<FONT 2><SIZE 15>%s <FONT 0><SIZE 12>%s' % (_P[_i], _T[_i])
        EDITS['msg/title_jpn.gmd']['SCE_TITLE0%d' % _i] = ' '
    OUT = OUT.replace('rc1', 'rc4')
    WORK = WORK.replace('v1015_dir', 'v1015rc4_dir')
# rc5: SIZE 15 on the FONT 2 prefix rendered identical to stock (so 15 is at or above its
# native size there) and the title still lost its last letter by ~5 px. SIZE 13 prefix and
# the space moved into the FONT 0 span (FONT 2's space is wide).
if '--rc5' in sys.argv:
    VARIANT = 'rc5'
    for _i in range(5):
        EDITS['msg/title_jpn.gmd']['SCE_NUM0%d' % _i] = '<FONT 2><SIZE 13>%s<FONT 0><SIZE 12> %s' % (_P[_i], _T[_i])
    OUT = OUT.replace('rc4', 'rc5')
    WORK = WORK.replace('v1015rc4_dir', 'v1015rc5_dir')
CHAP_SIZE = 15 if VARIANT in ('rc2', 'rc3', 'rc4', 'rc5') else 12
CHAP_MODE = re.compile(r'^CHAP_MODE_\d\d$')


def chap_mode_edit(text):
    """'<FONT 0>Trial, Part 1' -> '<FONT 0><SIZE n>Trial, Part 1'; 'Epilogue' -> '<SIZE n>Epilogue'.
    (rc1 also appended a space; the engine inserts ': ' itself, so rc2 drops it.)"""
    if '<SIZE' in text:
        return text
    tail = ' ' if VARIANT == 'rc1' else ''
    tag = '<SIZE %d>' % CHAP_SIZE
    if text.startswith('<FONT 0>'):
        return '<FONT 0>' + tag + text[len('<FONT 0>'):] + tail
    return tag + text + tail


def patch_arc(blob):
    arc = parse_arc(blob)
    assert build_arc_bytes(arc) == blob, 'arc null test failed'
    repl, log = {}, []
    for e in arc['entries']:
        if e.name not in EDITS and e.name != 'msg/title_jpn.gmd':
            continue
        doc = parse_gmd_bytes(e.data)
        assert build_gmd_bytes(doc) == e.data, 'gmd null test failed for ' + e.name
        changed = False
        for en in doc['entries']:
            lab = en.get('label')
            new = None
            if lab in EDITS.get(e.name, {}):
                new = EDITS[e.name][lab]
            elif e.name == 'msg/title_jpn.gmd' and lab and CHAP_MODE.match(lab):
                new = chap_mode_edit(en['text'])
            if new is not None and new != en['text']:
                log.append((e.name, lab, en['text'], new))
                en['text'] = new
                changed = True
        if changed:
            repl[e.name] = build_gmd_bytes(doc)
    return build_arc_bytes(arc, repl), log


def read_back(blob):
    arc = parse_arc(blob)
    out = {}
    for e in arc['entries']:
        if e.name in ('msg/system_jpn.gmd', 'msg/title_jpn.gmd'):
            for en in parse_gmd_bytes(e.data)['entries']:
                out[(e.name, en.get('label'))] = en['text']
    return out


def tree_diff(a, b):
    diffs = []
    for dp, _, fs in os.walk(a):
        for fn in fs:
            pa = os.path.join(dp, fn)
            pb = os.path.join(b, os.path.relpath(pa, a))
            if not os.path.exists(pb) or open(pa, 'rb').read() != open(pb, 'rb').read():
                diffs.append(os.path.relpath(pa, a))
    na = sum(len(f) for _, _, f in os.walk(a))
    nb = sum(len(f) for _, _, f in os.walk(b))
    return diffs, na, nb


def main():
    build = '--build' in sys.argv
    src_arc = open(os.path.join(SHIPPED, ARC_REL), 'rb').read()
    new_arc, log = patch_arc(src_arc)
    print('%d string edits in %s:' % (len(log), ARC_REL))
    for name, lab, old, new in log:
        print('  %s [%s]\n     was %r\n     now %r' % (name, lab, old, new))
    # every edited entry reads back exactly
    rb = read_back(new_arc)
    for name, lab, old, new in log:
        assert rb[(name, lab)] == new, 'read-back mismatch ' + lab
    # nothing else in the arc moved
    before, after = read_back(src_arc), rb
    touched = {(n, l) for n, l, _, _ in log}
    for k in before:
        if k not in touched:
            assert before[k] == after[k], 'untouched entry changed: %r' % (k,)
    print('read-back OK, %d untouched entries identical' % (len(before) - len(touched)))
    if not build:
        print('dry run; add --build to write the tree and the CIA')
        return

    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    shutil.copytree(SHIPPED, WORK)
    open(os.path.join(WORK, ARC_REL), 'wb').write(new_arc)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'stamp_title_versions.py'), 'tex',
                        CLEAN_PLATE, os.path.join(WORK, ATLAS_REL), STAMP],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        raise SystemExit('stamp failed')
    diffs, na, nb = tree_diff(SHIPPED, WORK)
    print('work tree vs shipped 1.0.14: %d/%d files, differing: %s' % (nb, na, diffs))
    assert sorted(diffs) == sorted([ARC_REL, ATLAS_REL]), 'unexpected files changed'

    r = subprocess.run([sys.executable, os.path.join(HERE, 'build.py'), SHELL, OUT, VERSION, '0=' + WORK],
                       capture_output=True, text=True)
    print(r.stdout.strip()); print(r.stderr.strip())
    if r.returncode:
        raise SystemExit('build failed')

    # verify from the BUILT file: extract content 0 and diff against the work tree
    c = Cia(OUT)
    print('%s declares %d.%d.%d, %d content(s)' % (os.path.basename(OUT), *c.version(), c.count))
    tmp = os.path.join(ROOT, 'dlc_story_audit', '_validation', '_tmp_1015_verify')
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    n = os.path.join(tmp, 'c0.ncch'); rom = os.path.join(tmp, 'c0.romfs'); h = os.path.join(tmp, 'c0.hdr')
    open(n, 'wb').write(c.contents[0])
    subprocess.run([TOOL, '-xtf', 'cxi', n, '--header', h, '--romfs', rom], capture_output=True)
    tree = os.path.join(tmp, 'tree'); os.makedirs(tree)
    subprocess.run([TOOL, '-xtf', 'romfs', rom, '--romfs-dir', tree], capture_output=True)
    diffs, na, nb = tree_diff(WORK, tree)
    print('built CIA content0 vs work tree: %d/%d files, %d differ %s' % (nb, na, len(diffs), diffs[:5]))
    diffs2, _, _ = tree_diff(SHIPPED, tree)
    print('built CIA content0 vs shipped 1.0.14: differing files: %s' % diffs2)
    built_rb = read_back(open(os.path.join(tree, ARC_REL), 'rb').read())
    for name, lab, old, new in log:
        assert built_rb[(name, lab)] == new, 'built CIA read-back mismatch ' + lab
    print('all %d edits read back from the built CIA' % len(log))
    shutil.rmtree(tmp, ignore_errors=True)
    import hashlib
    print('md5', hashlib.md5(open(OUT, 'rb').read()).hexdigest(), os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()

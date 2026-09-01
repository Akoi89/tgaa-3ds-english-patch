"""
Repairs line-count overflow in the community English base-game patch.

The defect: 71 pages render more lines than the widget can show, so the
last line is clipped off the bottom. Established by comparing each label
against Capcom's Japanese original -- where Capcom fits a page in 2
lines and the English uses 3, the English has outgrown the box.

Two different repairs, because two different structures are involved:

  * Entries Capcom lays out across SEVERAL pages (conversation runs:
    L_YUSA, L_UPDATE, L_1_*, L_2_*) can take one more page. Paging is
    already normal there -- the English patch itself adds pages to 12
    such entries -- so the overflow is absorbed by spilling onto a
    continuation page, exactly as autowrap does for the DLC.

  * Entries Capcom keeps to a SINGLE page are left alone here and must
    be shortened by hand instead. All 142 of Capcom's plain testimony
    statements (L_EXAM_<n>) are one page, without exception; a testimony
    statement is a gameplay unit the player presses, and inventing a
    second page for one is a structure the game is never seen to use.
    This script refuses to touch them so that decision stays explicit.

Only pages that actually overflow are rewritten. Everything else is
copied through byte for byte, so a diff of the output shows precisely
the repairs and nothing else.

Usage:
    python fix_base_overflow.py <jp_romfs> <en_romfs> <out_dir> [--apply]
"""
import os
import sys, os, re, glob, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from tag_align import tokenize
from check_fit import pages_of
from autowrap import rewrap_entry

def capacity_of(jp_text, rel):
    counts = [len(ls) for _, ls in pages_of(jp_text) if ls]
    return max(2, max(counts) if counts else 2)


def page_count(text):
    return sum(1 for k, s in tokenize(text) if k == 'tag' and s == '<PAGE>')


def main():
    jp_root, en_root, out_root = sys.argv[1], sys.argv[2], sys.argv[3]
    apply = '--apply' in sys.argv

    fixed = skipped = failed = 0
    touched_files = []

    for en_fn in sorted(glob.glob(os.path.join(en_root, '**', '*.gmd'),
                                  recursive=True)):
        rel = os.path.relpath(en_fn, en_root)
        jp_fn = os.path.join(jp_root, rel)
        if not os.path.exists(jp_fn):
            continue
        try:
            en_doc = parse_gmd_bytes(open(en_fn, 'rb').read())
            jp_doc = parse_gmd_bytes(open(jp_fn, 'rb').read())
        except Exception:
            continue
        jp_by_label = {e['label']: e for e in jp_doc['entries']}

        file_changed = False
        for e in en_doc['entries']:
            jp_e = jp_by_label.get(e['label'])
            if jp_e is None:
                continue
            cap = capacity_of(jp_e['text'], rel)
            over = [ls for _, ls in pages_of(e['text']) if ls and len(ls) > cap]
            if not over:
                continue

            # The structural test, not a name test: if Capcom keeps this
            # entry to one page, adding a second is inventing a layout the
            # game is never observed to use for it. Matching on the label
            # name instead would wrongly protect the L_EXAM_*_TOITSU_OK
            # conversation runs, which Capcom does spread over many pages.
            if page_count(jp_e['text']) <= 1:
                skipped += 1
                print(f'SKIP (single-page structure) {rel} :: {e["label"]} '
                      f'{len(over[0])} lines > {cap}')
                continue

            new_text, overfull = rewrap_entry(e['text'], e['label'],
                                              max_lines=cap, fix_width=False)
            if overfull:
                failed += 1
                print(f'FAIL {rel} :: {e["label"]} -- cannot lay out')
                continue
            still = [ls for _, ls in pages_of(new_text) if ls and len(ls) > cap]
            if still:
                failed += 1
                print(f'FAIL {rel} :: {e["label"]} -- still over after rewrap')
                continue
            e['text'] = new_text
            fixed += 1
            file_changed = True
            print(f'FIX  {rel} :: {e["label"]}  '
                  f'{max(len(x) for x in over)} lines -> {cap} + continuation')

        if file_changed:
            touched_files.append(rel)
            if apply:
                dst = os.path.join(out_root, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'wb').write(build_gmd_bytes(en_doc))

    print()
    print(f'fixed {fixed} pages across {len(touched_files)} files; '
          f'skipped {skipped} single-page entries; {failed} failures')
    if not apply:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()

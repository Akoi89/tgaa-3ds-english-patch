"""
Merges page breaks the 3DS port added that split text needlessly.

The port re-paginated the official PC script for a smaller box and, in
1865 places, put a break where the text would have sat on one screen
anyway -- so the player presses twice to read one short sentence:

    "The court therefore wishes for a speedy" -> "resolution to this matter."

A pair is merged only when ALL of these hold:

  * the entry has MORE pages than Capcom's Japanese, so the break is
    translation drift rather than the author's own pacing;
  * the two pages' text fits the 2-line box together;
  * the second page carries no <E800> -- that marks a voice line or
    scripted beat, and removing its break would desynchronise the scene.

Runs are accumulated, not tested pairwise: A+B and B+C can each fit while
A+B+C does not, and merging the whole run would then overflow.

Usage:
    python merge_needless.py <jp_romfs> <en_romfs> [--apply] [--show N]
"""
import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from attribute_pages import page_groups, visible, squash, prefix_tags
from remove_added_pages import merge_at
from autowrap import rewrap_entry, _wrap_words, SAFE_W, CNTR_SAFE_W, MAX_LINES
from check_fit import pages_of


def main():
    jp_root, en_root = sys.argv[1], sys.argv[2]
    apply = '--apply' in sys.argv
    show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 0

    merged_total = files_changed = skipped = 0
    samples = []

    for en_fn in sorted(glob.glob(os.path.join(en_root, '**', '*.gmd'),
                                  recursive=True)):
        rel = os.path.relpath(en_fn, en_root)
        jp_fn = os.path.join(jp_root, rel)
        if not os.path.exists(jp_fn):
            continue
        try:
            en = parse_gmd_bytes(open(en_fn, 'rb').read())
            jp = {e['label']: e for e in
                  parse_gmd_bytes(open(jp_fn, 'rb').read())['entries']}
        except Exception:
            continue

        changed = False
        for e in en['entries']:
            groups = page_groups(e['text'])
            jp_e = jp.get(e['label'])
            if jp_e is None or len(groups) <= len(page_groups(jp_e['text'])):
                continue

            merge_idx = set()
            run_text = None
            for i, g in enumerate(groups[:-1]):
                nxt = groups[i + 1]
                ta, tb = visible(g).strip(), visible(nxt).strip()
                if run_text is None:
                    run_text = ta
                if not ta or not tb or any(
                        t.startswith('<E800') for t in prefix_tags(nxt)):
                    run_text = tb
                    continue
                is_cntr = any(s == '<CNTR>' for k, s in g if k == 'tag')
                max_w = CNTR_SAFE_W if is_cntr else SAFE_W
                combined = (run_text + ' ' + tb).split()
                if _wrap_words(combined, max_w, MAX_LINES) is None:
                    run_text = tb
                    continue
                merge_idx.add(i)
                run_text = ' '.join(combined)

            if not merge_idx:
                continue

            before_pages = [l for _, l in pages_of(e['text']) if l]
            before_words = squash(''.join(visible(g) for g in groups))
            new_text, merged_pages = merge_at(groups, merge_idx)
            new_text, overfull = rewrap_entry(new_text, e['label'],
                                              only_pages=merged_pages)
            after_words = squash(''.join(
                visible(g) for g in page_groups(new_text)))
            got, want = len(page_groups(new_text)), len(groups) - len(merge_idx)
            if overfull or before_words != after_words or got != want:
                skipped += 1
                continue

            if show and len(samples) < show:
                after_pages = [l for _, l in pages_of(new_text) if l]
                samples.append((rel, e['label'], before_pages, after_pages,
                                len(merge_idx)))
            e['text'] = new_text
            merged_total += len(merge_idx)
            changed = True

        if changed:
            files_changed += 1
            if apply:
                open(en_fn, 'wb').write(build_gmd_bytes(en))

    for rel, lab, before, after, n in samples:
        print(f'===== {os.path.basename(rel)} :: {lab}   (-{n} page(s))')
        # only print the region that actually differs
        for tag, pages in (('BEFORE', before), ('AFTER ', after)):
            print(f'  {tag}:')
            for p in pages[:14]:
                print('     [' + ' / '.join(p) + ']')
            if len(pages) > 14:
                print(f'     ... {len(pages)-14} more pages')
        print()

    print(f'merged {merged_total} needless breaks across {files_changed} files '
          f'({skipped} entries skipped as unsafe)')
    if not apply:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()

"""
Removes page breaks this project added to the DLC that were never needed.

An earlier "formatting/pagination" pass inserted 39 page breaks into DLC
episodes 1-8. 37 of them split text that fits on a single screen, which
chopped sentences across two and even three presses:

    "This is a most" -> "extraordinary case of murder. Counsels, I"
                     -> "assume I may proceed?"

Only breaks that are BOTH absent from the community v1.0.5 baseline (so
demonstrably ours) AND needless (the two pages' text fits the 2-line box,
and the second page carries no <E800> event marker) are removed. Breaks
the translators or Capcom put there are left untouched.

Merging drops the boundary's wait marker, its <PAGE>, the '\\r\\n' that
follows, and the <E041>/<E025> the continuation page repeats -- but only
when those repeat a value already in force, since an <E041> that actually
changes the speaker is carrying information. The merged page is then
re-flowed to two lines.

Usage:
    python remove_added_pages.py <baseline_romfs> <our_romfs> [--apply]
"""
import os
import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from attribute_pages import page_groups, visible, squash, break_offsets, prefix_tags
from autowrap import rewrap_entry, _wrap_words, SAFE_W, CNTR_SAFE_W, MAX_LINES

CRLF = chr(13) + chr(10)

WAIT_MARKERS = {'<E023>', '<E024>', '<E104>', '<E590>', '<E206>', '<E196>'}


def merge_at(groups, merge_idx):
    """Rebuild a token list, merging the page boundaries in merge_idx.
    Returns (text, merged_page_indices) where the indices are positions in
    the RESULTING page list, so the caller can re-flow just those."""
    out = []
    out_page = 0
    merged_pages = set()
    # Every group taking part in a merge -- the page being extended and
    # the page folded into it. Their internal line breaks are dissolved
    # so the combined text is re-wrapped as one unit; keeping page A's
    # old break would leave "Kindly state before / the court the name of
    # the victim in this case." with a stub first line.
    involved = set(merge_idx) | {i + 1 for i in merge_idx}
    cur_e041 = cur_e025 = None
    for i, g in enumerate(groups):
        drop_prefix = (i - 1) in merge_idx
        if drop_prefix:
            merged_pages.add(out_page)
        elif i > 0:
            out_page += 1
        seen_text = False
        for j, (kind, s) in enumerate(g):
            if kind == 'tag':
                if s.startswith('<E041'):
                    if drop_prefix and not seen_text and s == cur_e041:
                        continue
                    cur_e041 = s
                elif s.startswith('<E025'):
                    if drop_prefix and not seen_text and s == cur_e025:
                        continue
                    cur_e025 = s
                # the boundary's own wait marker + PAGE
                if i in merge_idx and s == '<PAGE>':
                    continue
                if i in merge_idx and s in WAIT_MARKERS and j + 1 < len(g) \
                        and g[j + 1] == ('tag', '<PAGE>'):
                    continue
                out.append((kind, s))
            else:
                if drop_prefix and not seen_text:
                    # Only supply a separator if there is not already one.
                    # The previous page may end with a space and this page
                    # may open with one, and emitting a third produces
                    # "the name of  the victim".
                    tail = ''.join(x for k2, x in out if k2 == 'text')
                    need_sep = not (tail.endswith((chr(32), CRLF, chr(10)))
                                    or s[:1].isspace())
                    # The continuation page opens with the '\r\n' that
                    # followed its <PAGE>. That break is going away, but it
                    # was also the only thing separating the previous
                    # page's last word from this page's first -- drop it
                    # outright and they weld together ("decorated from" +
                    # "top to bottom" -> "decorated fromtop"). Comparing
                    # whitespace-stripped text cannot detect that, so the
                    # separator is replaced rather than deleted.
                    if need_sep:
                        out.append(('text', ' '))
                    if not s.strip():
                        continue
                if s.strip():
                    seen_text = True
                if i in involved and seen_text and CRLF in s:
                    s = s.replace(CRLF, ' ')
                out.append((kind, s))
    return ''.join(s for _, s in out), merged_pages


def main():
    base_root, our_root = sys.argv[1], sys.argv[2]
    apply = '--apply' in sys.argv
    removed = files_changed = 0

    for our_fn in sorted(glob.glob(os.path.join(our_root, '**', '*.gmd'),
                                   recursive=True)):
        rel = os.path.relpath(our_fn, our_root)
        base_fn = os.path.join(base_root, rel)
        if not os.path.exists(base_fn):
            continue
        try:
            ours = parse_gmd_bytes(open(our_fn, 'rb').read())
            base = {e['label']: e for e in
                    parse_gmd_bytes(open(base_fn, 'rb').read())['entries']}
        except Exception:
            continue

        changed = False
        for e in ours['entries']:
            groups = page_groups(e['text'])
            if len(groups) < 2:
                continue
            b = base.get(e['label'])
            if b is None:
                continue
            offs = break_offsets(b['text'])

            # Accumulate across a RUN of merges rather than testing each
            # boundary on its own. Three pages can pass pairwise -- A+B
            # fits, B+C fits -- while A+B+C does not, and merging the
            # whole run then overflows and gets re-split into a fresh
            # page, which is the very thing being removed.
            merge_idx, acc = set(), 0
            run_text = None
            for i, g in enumerate(groups[:-1]):
                acc += len(squash(visible(g)))
                nxt = groups[i + 1]
                ta, tb = visible(g).strip(), visible(nxt).strip()
                if run_text is None:
                    run_text = ta
                if not ta or not tb or acc in offs:
                    run_text = tb
                    continue
                if any(t.startswith('<E800') for t in prefix_tags(nxt)):
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

            before_text = squash(''.join(visible(g) for g in groups))
            merged, merged_pages = merge_at(groups, merge_idx)
            merged, overfull = rewrap_entry(merged, e['label'],
                                            only_pages=merged_pages)
            after_text = squash(''.join(
                visible(g) for g in page_groups(merged)))
            # Verify the merge actually took. rewrap_entry re-flows the
            # merged page, and if the result still will not sit on two
            # lines it splits it again -- silently undoing the merge and
            # leaving the page count unchanged. Count the pages rather
            # than trusting the intent.
            got = len(page_groups(merged))
            want = len(groups) - len(merge_idx)
            if overfull or before_text != after_text or got != want:
                why = ('text would change' if before_text != after_text
                       else 'could not lay out' if overfull
                       else f'merge did not take ({got} pages, wanted {want})')
                print(f'SKIP {os.path.basename(rel)} :: {e["label"]} -- {why}')
                continue
            e['text'] = merged
            removed += len(merge_idx)
            changed = True
            print(f'MERGE {os.path.basename(rel)} :: {e["label"]}  '
                  f'-{len(merge_idx)} page(s)')

        if changed:
            files_changed += 1
            if apply:
                open(our_fn, 'wb').write(build_gmd_bytes(ours))

    print()
    print(f'removed {removed} needless page breaks across {files_changed} files')
    if not apply:
        print('(dry run -- pass --apply to write)')


if __name__ == '__main__':
    main()

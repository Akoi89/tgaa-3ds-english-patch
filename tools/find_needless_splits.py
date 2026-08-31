"""
Finds page breaks that did not need to exist.

The community English patch adds 6587 pages compared to Capcom's
Japanese. Much of that is unavoidable -- English is wordier, and text
that filled two Japanese lines often genuinely needs a second page. But
some of it is gratuitous: a sentence is cut across two screens when it
would have sat comfortably on one, so the player clicks twice to read
"The court therefore wishes for a speedy / resolution to this matter."

A pair of adjacent pages is reported as a needless split when BOTH:

  * their combined text fits the 2-line box, and
  * the second page is a PURE CONTINUATION -- its tag prefix carries no
    <E800>. <E800> numbers a voice/event stream, so a page that starts
    with one is a distinct scripted beat (a new line of VO, a camera
    move) and merging it would desynchronise the scene. Only pages whose
    prefix is just the repeated <E041>/<E025> are safe to rejoin.

That second condition is what keeps this honest: Capcom uses one-line
pages 884 times deliberately, for timing, and this must not "optimise"
away a dramatic pause.

Usage:
    python find_needless_splits.py <jp_romfs> <en_romfs> [--limit N]
"""
import sys, os, glob, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize
from autowrap import _wrap_words, SAFE_W, CNTR_SAFE_W, MAX_LINES
from textwidth import width


def page_groups(text):
    """[(tokens_of_page, is_cntr)] split on <PAGE>."""
    toks = tokenize(text)
    groups, cur = [], []
    for kind, s in toks:
        cur.append((kind, s))
        if kind == 'tag' and s == '<PAGE>':
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def visible(group):
    return ''.join(s for k, s in group if k == 'text')


def prefix_tags(group):
    """Tags before this page's first visible text."""
    out = []
    for k, s in group:
        if k == 'text' and s.strip():
            break
        if k == 'tag':
            out.append(s)
    return out


def is_pure_continuation(group):
    return not any(t.startswith('<E800') for t in prefix_tags(group))


def main():
    jp_root, en_root = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 12

    total = 0
    by_file = collections.Counter()
    samples = []

    for en_fn in sorted(glob.glob(os.path.join(en_root, '**', '*.gmd'),
                                  recursive=True)):
        rel = os.path.relpath(en_fn, en_root)
        try:
            en = parse_gmd_bytes(open(en_fn, 'rb').read())
        except Exception:
            continue
        jp_fn = os.path.join(jp_root, rel)
        jp_by_label = {}
        if os.path.exists(jp_fn):
            try:
                jp_by_label = {x['label']: x for x in
                               parse_gmd_bytes(open(jp_fn, 'rb').read())['entries']}
            except Exception:
                jp_by_label = {}
        for e in en['entries']:
            # Only consider entries the English has ADDED pages to. If
            # Capcom used just as many pages, the break is the original
            # author's pacing, not translation drift, and rejoining it
            # would be rewriting the scene rather than repairing it.
            jp_e = jp_by_label.get(e['label'])
            if jp_e is None:
                continue
            if len(page_groups(e['text'])) <= len(page_groups(jp_e['text'])):
                continue
            groups = page_groups(e['text'])
            for i in range(len(groups) - 1):
                a, b = groups[i], groups[i + 1]
                ta, tb = visible(a).strip(), visible(b).strip()
                if not ta or not tb:
                    continue
                if not is_pure_continuation(b):
                    continue
                is_cntr = any(s == '<CNTR>' for k, s in a if k == 'tag')
                max_w = CNTR_SAFE_W if is_cntr else SAFE_W
                words = (ta + ' ' + tb).split()
                if _wrap_words(words, max_w, MAX_LINES) is None:
                    continue
                total += 1
                by_file[rel] += 1
                if len(samples) < limit:
                    samples.append((rel, e['label'], ta, tb))

    print(f'Needlessly split page pairs: {total} across {len(by_file)} files')
    print()
    for f, n in by_file.most_common(10):
        print(f'   {n:4d}  {os.path.basename(f)}')
    print()
    for rel, lab, ta, tb in samples:
        merged = ' '.join((ta + ' ' + tb).split())
        print(f'-- {os.path.basename(rel)} :: {lab}')
        print(f'     page A: {ta!r}')
        print(f'     page B: {tb!r}')
        print(f'     merged: {merged!r}  (w={width(merged)})')


if __name__ == '__main__':
    main()

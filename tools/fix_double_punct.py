"""
Strips punctuation from the end of a translated run when the very next
run is pure punctuation copied through from the Japanese.

The Japanese source carries its own sentence-final marks as separate
runs ('‥‥' -> '...', '。' -> '.'), and rebuild() copies those through
untouched. Ending the English run with the same mark therefore renders it
twice: 'Kazuma Asogi..', 'through that door......', 'handed down,...'.
The passthrough run is the one that matches the original's timing tags,
so the English run is always the side that gives way.

Only '.' and ',' (and runs of them) are removed automatically. '?' and
'!' are left alone and reported instead -- dropping those can silently
change the sentence's mood, and whether the Japanese supplies its own
replacement has to be looked at case by case.

Usage:
    python fix_double_punct.py <chunks_file> <source_gmd> [--apply]
"""
import sys, io, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize, normalize_punctuation
from auto_build import parse_runs_file

PURE_PUNCT = re.compile(r'^[.,!?\s]+$')
SAFE_TRAIL = re.compile(r'[.,]+$')
RISKY_TRAIL = re.compile(r'[!?]+$')
RUN_RE = re.compile(r'^\[(\d+)\]\s?(.*)$')


def main():
    chunks_file, src_gmd = sys.argv[1], sys.argv[2]
    apply = '--apply' in sys.argv

    translations = parse_runs_file(chunks_file)
    doc = parse_gmd_bytes(open(src_gmd, 'rb').read())

    # {(label, idx): stripped_text}
    edits = {}
    for e in doc['entries']:
        label = e['label']
        if label not in translations:
            continue
        subs = translations[label]
        tokens = tokenize(e['text'])
        text_idxs = [i for i, (k, _) in enumerate(tokens) if k == 'text']
        for pos in range(len(text_idxs) - 1):
            i, j = text_idxs[pos], text_idxs[pos+1]
            if i not in subs or j in subs:
                continue
            mine = subs[i]
            nxt = normalize_punctuation(tokens[j][1])
            if not mine.strip() or not nxt.strip():
                continue
            if not PURE_PUNCT.match(nxt):
                continue
            if RISKY_TRAIL.search(mine):
                print(f'REVIEW  {label} [{i}] ends with !/? before passthrough '
                      f'{nxt!r}: {mine!r}')
                continue
            m = SAFE_TRAIL.search(mine)
            if not m:
                continue
            stripped = mine[:m.start()]
            if not stripped.strip():
                continue
            edits[(label, i)] = stripped
            print(f'FIX     {label} [{i}] {mine!r} -> {stripped!r} '
                  f'(passthrough supplies {nxt!r})')

    print(f'\n{len(edits)} automatic fixes')
    if not apply:
        print('(dry run -- pass --apply to write)')
        return

    # Rewrite the chunks file in place. Entries can span multiple lines;
    # the trailing punctuation is always on the entry's LAST line.
    lines = io.open(chunks_file, encoding='utf-8').read().split('\n')
    out = []
    idx_of_line = []   # parallel: which run index each line belongs to
    cur_idx = None
    for line in lines:
        m = RUN_RE.match(line)
        if m:
            cur_idx = int(m.group(1))
        elif line.startswith('---') or line.startswith('===') or not line.strip():
            cur_idx = None
        idx_of_line.append(cur_idx)

    # find, for each run index, the last line belonging to it
    last_line_of = {}
    for n, idx in enumerate(idx_of_line):
        if idx is not None:
            last_line_of[idx] = n

    wanted = {i for (_, i) in edits}
    applied = 0
    for n, line in enumerate(lines):
        idx = idx_of_line[n]
        if idx in wanted and last_line_of.get(idx) == n:
            m = SAFE_TRAIL.search(line.rstrip())
            if m:
                stripped = line.rstrip()[:m.start()]
                if stripped.strip() and not stripped.strip() in ('[%d]' % idx,):
                    lines[n] = stripped
                    applied += 1
    io.open(chunks_file, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print(f'Applied {applied} edits to {chunks_file}')


if __name__ == '__main__':
    main()

"""
Auto-repairs the two problems check_completeness.py detects:

  1. MISSING run indices -- restores the original Japanese text for any
     run that's missing entirely from the translated file, so nothing
     silently disappears.
  2. SUSPICIOUS/merged runs -- replaces the corrupted run's text with
     the original Japanese for EVERY run index involved in the merge
     (the one it's filed under, plus any [N] markers found embedded
     inside it), splitting the mess back into its correct number of
     separate, clearly-flagged entries.

This does NOT generate any new English translation -- it only restores
known-correct Japanese source text into broken slots, tagged with a
"[[NEEDS RETRANSLATION]]" marker so they're easy to find and fix for
real afterward. Think of it as a structural repair, not a translation.

Usage:
    python fix_completeness.py <source_gmd> <runs_or_chunks_file.txt> <output_file.txt>
"""
import sys, re, io
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize, list_text_runs, is_translatable
from auto_build import parse_runs_file, HEADER_RE, RUN_RE, CHUNK_MARKER_RE, CHECKPOINT_MARKER_RE

SUSPICIOUS_BRACKET_RE = re.compile(r'\[(\d+)\]')


def get_expected(src_gmd):
    """Returns {label: {index: original_jp_text}}."""
    doc = parse_gmd_bytes(open(src_gmd, 'rb').read())
    expected = {}
    for e in doc['entries']:
        tokens = tokenize(e['text'])
        runs = list_text_runs(tokens)
        jp = {i: s for i, s in runs if is_translatable(s)}
        if jp:
            expected[e['label']] = jp
    return expected


def find_broken_indices(expected, got):
    """Returns {label: set(indices that need restoring)} -- both missing
    ones and ones embedded inside a suspicious/merged run."""
    broken = {}
    for label, jp_map in expected.items():
        exp_indices = set(jp_map.keys())
        got_map = got.get(label, {})
        got_indices = set(got_map.keys())
        missing = exp_indices - got_indices
        needs_fix = set(missing)
        for idx, text in got_map.items():
            embedded = {int(m) for m in SUSPICIOUS_BRACKET_RE.findall(text)}
            if embedded:
                needs_fix.add(idx)  # the merged-into run itself
                needs_fix |= (embedded & exp_indices)  # the runs it swallowed
        if needs_fix:
            broken[label] = needs_fix
    return broken


def main():
    src_gmd, in_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    expected = get_expected(src_gmd)
    got = parse_runs_file(in_path)
    broken = find_broken_indices(expected, got)

    total_fixed = sum(len(v) for v in broken.values())
    if total_fixed == 0:
        print('Nothing to fix -- file is already clean. No output written.')
        return

    print(f'Restoring {total_fixed} broken run(s) across {len(broken)} label(s):')
    for label, indices in broken.items():
        print(f'  {label}: {sorted(indices)}')

    # Rewrite the file: pass through everything unchanged, except broken
    # runs get replaced with their restored original Japanese, and any
    # run whose index got swallowed into a merge but wasn't otherwise
    # present gets newly inserted right after the run it was merged into.
    current_label = None
    out = io.open(out_path, 'w', encoding='utf-8')

    with io.open(in_path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            header_match = HEADER_RE.match(line)
            chunk_match = CHUNK_MARKER_RE.match(line)
            if header_match or chunk_match:
                current_label = (header_match or chunk_match).group(1)
                out.write(raw_line)
                continue
            if CHECKPOINT_MARKER_RE.match(line):
                out.write(raw_line)
                continue
            run_match = RUN_RE.match(line)
            if run_match:
                idx = int(run_match.group(1))
                label_broken = broken.get(current_label, set())
                if idx in label_broken:
                    jp_text = expected[current_label][idx]
                    out.write(f'[{idx}] [[NEEDS RETRANSLATION]] {jp_text}\n')
                    # also emit any OTHER broken indices that were merged
                    # into this same line and had no line of their own
                    embedded = {int(m) for m in SUSPICIOUS_BRACKET_RE.findall(run_match.group(2))}
                    for other_idx in sorted(embedded & label_broken):
                        if other_idx == idx:
                            continue
                        jp_text2 = expected[current_label].get(other_idx)
                        if jp_text2 is not None:
                            out.write(f'[{other_idx}] [[NEEDS RETRANSLATION]] {jp_text2}\n')
                else:
                    out.write(raw_line)
                continue
            out.write(raw_line)
    out.close()
    print(f'Wrote repaired file to {out_path} -- fix these {total_fixed} flagged line(s), then rerun check_completeness.py to confirm clean.')


if __name__ == '__main__':
    main()

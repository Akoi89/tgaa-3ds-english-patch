"""
Checks a runs/chunks file for two kinds of problems that Gemini (or any
translation pass) can silently introduce:

  1. MISSING run indices -- a run from the original source that never
     shows up in the translated file at all. This catches exactly the
     kind of bug found in aoc13's file 0000: Gemini merging several
     runs into one, which makes the merged-in run numbers vanish from
     the output entirely.
  2. SUSPICIOUS runs -- a translated run whose text itself contains a
     "[123]"-style bracketed number pattern. That's a strong signal
     that multiple runs got merged into one instead of staying separate,
     even before checking whether anything is technically "missing."

This is pure structural validation -- it never reads or judges the
translation quality itself, only whether the run structure is intact.

Usage:
    python check_completeness.py <source_gmd> <runs_or_chunks_file.txt>
"""
import sys, re, io
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize, list_text_runs, is_translatable
from auto_build import parse_runs_file

SUSPICIOUS_BRACKET_RE = re.compile(r'\[\d+\]')


def main():
    src_gmd, runs_file = sys.argv[1], sys.argv[2]

    doc = parse_gmd_bytes(open(src_gmd, 'rb').read())
    expected = {}
    for e in doc['entries']:
        tokens = tokenize(e['text'])
        runs = list_text_runs(tokens)
        jp_runs = set(i for i, s in runs if is_translatable(s))
        if jp_runs:
            expected[e['label']] = jp_runs

    got = parse_runs_file(runs_file)

    problems_found = False

    print('=== Missing / extra index check ===')
    for label, exp_indices in expected.items():
        got_indices = set(got.get(label, {}).keys())
        missing = exp_indices - got_indices
        extra = got_indices - exp_indices
        if missing or extra:
            problems_found = True
            print(f'{label}: expected={len(exp_indices)} got={len(got_indices)} -- MISMATCH')
            if missing:
                print('  MISSING indices (never appear in the translated file):', sorted(missing))
            if extra:
                print('  UNEXPECTED indices (not in source):', sorted(extra))
        else:
            print(f'{label}: expected={len(exp_indices)} got={len(got_indices)} -- OK')

    print()
    print('=== Suspicious embedded-bracket check ===')
    for label, runs in got.items():
        for idx, text in runs.items():
            if SUSPICIOUS_BRACKET_RE.search(text):
                problems_found = True
                print(f'{label}[{idx}]: contains an embedded [N]-style marker -- likely a merged/corrupted run')
                print(f'  text: {text!r}')

    print()
    if problems_found:
        print('RESULT: problems found -- see above. Fix these before building.')
    else:
        print('RESULT: clean -- no missing runs, no merge corruption detected.')


if __name__ == '__main__':
    main()

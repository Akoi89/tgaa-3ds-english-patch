"""
Like extract_runs.py, but shows EVERY text run for one entry -- including
punctuation-only ones (like a run of pure ellipsis dots) that the normal
extraction filters out because they have no actual kana/kanji to translate.

Usage:
    python show_all_runs.py <gmd_file> <entry_label> <output_file>

Example:
    python show_all_runs.py eng_aoc13_full\\script\\sce07_c013_0002_jpn.gmd L_START all_runs_0002_LSTART.txt
"""
import sys, io
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize, list_text_runs

fp = sys.argv[1]
label = sys.argv[2]
out_fp = sys.argv[3]

doc = parse_gmd_bytes(open(fp, 'rb').read())
entry = next(e for e in doc['entries'] if e['label'] == label)
tokens = tokenize(entry['text'])
runs = list_text_runs(tokens)

out = io.open(out_fp, 'w', encoding='utf-8')
for idx, s in runs:
    # show every run, flag whether it's pure punctuation/whitespace
    is_punct_only = not any(c.isalnum() for c in s) and s.strip() != ''
    tag = ' <-- PUNCTUATION-ONLY' if is_punct_only else ''
    out.write(f'[{idx}] {s!r}{tag}\n')
out.close()
print('done')

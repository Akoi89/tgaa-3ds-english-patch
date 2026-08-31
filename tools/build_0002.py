"""
Fill in your translations below, then run:
    python build_0002.py

For each entry label you want to translate, add a dict mapping
run-index -> your English text. Run indexes come from runs_0002.txt
(the [N] numbers). You don't need every entry or every run filled in --
anything you leave out just stays as the original Japanese for now,
so you can build incrementally.
"""
import sys
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes
from tag_align import tokenize, rebuild, verify_tags_unchanged

SRC = r'eng_aoc13_full\script\sce07_c013_0002_jpn.gmd'
OUT = r'sce07_c013_0002_TRANSLATED.gmd'

# ---- EDIT THIS PART ----
# One dict per entry label. Example (delete/replace with real ones):
translations = {
    # 'L_START': {
    #     3: "Example English text for run 3",
    #     7: "Example English text for run 7",
    # },
}
# ---- END EDIT ----

doc = parse_gmd_bytes(open(SRC, 'rb').read())

changed = 0
for e in doc['entries']:
    if e['label'] not in translations:
        continue
    tokens = tokenize(e['text'])
    if not verify_tags_unchanged(tokens, translations[e['label']]):
        print(f'!! TAG MISMATCH in {e["label"]} -- NOT applying this one, check your edits')
        continue
    e['text'] = rebuild(tokens, translations[e['label']])
    changed += 1

blob = build_gmd_bytes(doc)
open(OUT, 'wb').write(blob)
print(f'Built {OUT} -- {changed} entries updated, {len(blob)} bytes')

# quick sanity re-parse
reparsed = parse_gmd_bytes(blob)
print(f'Re-parsed OK, {len(reparsed["entries"])} entries')

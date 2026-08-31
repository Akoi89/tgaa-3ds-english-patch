import sys, io
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize, list_text_runs, is_translatable

# Japanese sentence-ending punctuation. You don't need to read Japanese to
# use this -- these are just shapes to recognize visually, the same way
# you'd recognize a period or question mark in English:
#   。  <- looks like a small circle, this is a period
#   ！  <- exclamation mark (fullwidth, looks like a tall !)
#   ？  <- question mark (fullwidth, looks like a tall ?)
#   」  <- closing quote mark
#   ）  <- closing parenthesis
SENTENCE_ENDERS = '。！？」）'

fp = sys.argv[1]
out_fp = sys.argv[2]
doc = parse_gmd_bytes(open(fp, 'rb').read())
out = io.open(out_fp, 'w', encoding='utf-8')
for e in doc['entries']:
    tokens = tokenize(e['text'])
    runs = list_text_runs(tokens)
    jp_runs = [(i, s) for i, s in runs if is_translatable(s)]
    out.write(f'##### {e["label"]} ({len(tokens)} tokens, {len(jp_runs)} JP runs) #####\n')
    for idx, s in jp_runs:
        # flag runs that END with a sentence-ending mark -- a good signal
        # that this is a natural stopping point for a batch, even without
        # reading the Japanese itself
        stripped = s.rstrip('\r\n 　')
        marker = '  <== likely sentence/thought END' if stripped and stripped[-1] in SENTENCE_ENDERS else ''
        out.write(f'[{idx}] {s}{marker}\n')
    out.write('\n')
out.close()
print('done')

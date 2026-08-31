"""
Combined work-list for the remaining hand-fixable problems.

Reports two things auto-wrapping cannot fix on its own:

  OVERFULL -- a page whose words cannot be fitted into the 2-line box at
  any break placement. The wording itself has to be tightened. Shows the
  current width against the box's real capacity so it's clear how much
  has to come out.

  DOUBLE PUNCT -- a translated run ending in punctuation immediately
  followed by a run that is pure punctuation copied through from the
  Japanese. The Japanese already supplies that mark (JP '‥‥' -> '...',
  '。' -> '.'), so writing one at the end of the English run too renders
  it twice: 'Kazuma Asogi..', 'door......', 'style?...?'. The fix is
  always to drop it from the English run, never to edit the passthrough.

Usage:
    python report_issues.py <chunks_file> <source_gmd> [...]
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize, rebuild, normalize_punctuation
from auto_build import parse_runs_file
from autowrap import rewrap_entry, SAFE_W, CNTR_SAFE_W, MAX_LINES
from textwidth import width

TRAIL_PUNCT = re.compile(r'[.,!?]+$')
PURE_PUNCT = re.compile(r'^[.,!?\s]+$')


def main():
    args = sys.argv[1:]
    for k in range(0, len(args), 2):
        chunks_file, src_gmd = args[k], args[k+1]
        print(f'########## {chunks_file} ##########')
        translations = parse_runs_file(chunks_file)
        doc = parse_gmd_bytes(open(src_gmd, 'rb').read())

        for e in doc['entries']:
            label = e['label']
            if label not in translations:
                continue
            subs = translations[label]
            tokens = tokenize(e['text'])

            # --- double punctuation at my-run / passthrough-run junctions ---
            text_idxs = [i for i, (kind, _) in enumerate(tokens) if kind == 'text']
            for pos in range(len(text_idxs) - 1):
                i, j = text_idxs[pos], text_idxs[pos+1]
                if i not in subs:
                    continue          # only my own runs can be edited
                if j in subs:
                    continue          # next run is mine too -- not a passthrough
                mine = normalize_punctuation(subs[i])
                nxt = normalize_punctuation(tokens[j][1])
                if not mine.strip() or not nxt.strip():
                    continue
                if not PURE_PUNCT.match(nxt):
                    continue
                m = TRAIL_PUNCT.search(mine)
                if not m:
                    continue
                print(f'DOUBLE PUNCT  {label}  [{i}] ends {m.group(0)!r} '
                      f'+ passthrough [{j}]={nxt!r}  -> renders '
                      f'{mine[-12:] + nxt!r}')
                print(f'    [{i}] = {subs[i]!r}')

            # --- pages that cannot fit ---
            text = rebuild(tokens, subs)
            _, overfull = rewrap_entry(text, label)
            for page in overfull:
                budget = SAFE_W * MAX_LINES
                print(f'OVERFULL  {label}  width={width(page)} '
                      f'budget={budget} (over by {width(page)-budget})')
                print(f'    {page!r}')
        print()


if __name__ == '__main__':
    main()

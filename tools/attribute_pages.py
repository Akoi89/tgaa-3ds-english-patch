"""
Attributes every explicit page break to whoever introduced it, and says
whether it was needed.

Three versions of the same script exist, so a break can be dated:

  JP   Capcom's Japanese original      -- the author's own pacing
  EN0  the community English patch     -- translator's choices
  ENC  our build on top of it          -- edits made in this project

A break present in ENC but not in EN0 was added by us. A break in EN0 but
not in JP was added by the translators. Comparison is done on the text
with all whitespace stripped, so that re-wrapping a line (which changes
where '\\r\\n' sits, but not the words) does not masquerade as a moved
page break.

Necessity is then judged for each break:

  STORY    the following page begins with an <E800> event marker -- a new
           voice line or scripted beat. Removing it would desynchronise
           the scene, so it belongs there regardless of length.
  OVERFLOW the two pages' combined text genuinely cannot fit the 2-line
           box, so a break is required somewhere.
  NEEDLESS neither applies: the text would sit on one screen, and the
           break only costs the player an extra click.

Usage:
    python attribute_pages.py <jp_romfs> <en_baseline_romfs> <our_romfs>
"""
import os
import sys, os, glob, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'..\dlc_icons\tgaa2-en-patch')
sys.path.insert(0, '.')
from dgs2tool.gmd import parse_gmd_bytes
from tag_align import tokenize
from autowrap import _wrap_words, SAFE_W, CNTR_SAFE_W, MAX_LINES


def page_groups(text):
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


def squash(s):
    return ''.join(s.split())


def break_offsets(text):
    """Character offsets (in whitespace-stripped text) where a page ends."""
    offs, acc = set(), 0
    groups = page_groups(text)
    for g in groups[:-1]:
        acc += len(squash(visible(g)))
        offs.add(acc)
    return offs


def prefix_tags(group):
    out = []
    for k, s in group:
        if k == 'text' and s.strip():
            break
        if k == 'tag':
            out.append(s)
    return out


def main():
    jp_root, en0_root, enc_root = sys.argv[1], sys.argv[2], sys.argv[3]
    stats = collections.Counter()
    examples = collections.defaultdict(list)

    for enc_fn in sorted(glob.glob(os.path.join(enc_root, '**', '*.gmd'),
                                   recursive=True)):
        rel = os.path.relpath(enc_fn, enc_root)
        jp_fn = os.path.join(jp_root, rel)
        en0_fn = os.path.join(en0_root, rel)
        try:
            enc = parse_gmd_bytes(open(enc_fn, 'rb').read())
        except Exception:
            continue
        jp = {}
        en0 = {}
        if os.path.exists(jp_fn):
            try:
                jp = {e['label']: e for e in
                      parse_gmd_bytes(open(jp_fn, 'rb').read())['entries']}
            except Exception:
                pass
        if os.path.exists(en0_fn):
            try:
                en0 = {e['label']: e for e in
                       parse_gmd_bytes(open(en0_fn, 'rb').read())['entries']}
            except Exception:
                pass

        for e in enc['entries']:
            groups = page_groups(e['text'])
            if len(groups) < 2:
                continue
            jp_e, en0_e = jp.get(e['label']), en0.get(e['label'])
            jp_offs = break_offsets(jp_e['text']) if jp_e else None
            en0_offs = break_offsets(en0_e['text']) if en0_e else None

            acc = 0
            for i, g in enumerate(groups[:-1]):
                acc += len(squash(visible(g)))
                nxt = groups[i + 1]
                ta, tb = visible(g).strip(), visible(nxt).strip()
                if not ta or not tb:
                    continue

                # Who introduced it. Only the English-to-English
                # comparison is sound: offsets are counted in characters
                # of the stripped text, and Japanese and English simply
                # do not share a character count, so an offset can never
                # be matched across the two. Attribution is therefore
                # "ours vs already in the English baseline"; how the
                # baseline itself compares to Capcom is reported
                # separately as an aggregate page-count delta.
                if en0_offs is None:
                    origin = 'no English baseline'
                elif acc not in en0_offs:
                    origin = 'ADDED BY US'
                else:
                    origin = 'already in EN baseline'

                # why it might be needed
                if any(t.startswith('<E800') for t in prefix_tags(nxt)):
                    need = 'STORY/event'
                else:
                    is_cntr = any(s == '<CNTR>' for k, s in g if k == 'tag')
                    max_w = CNTR_SAFE_W if is_cntr else SAFE_W
                    words = (ta + ' ' + tb).split()
                    need = ('OVERFLOW' if _wrap_words(words, max_w, MAX_LINES) is None
                            else 'NEEDLESS')

                stats[(origin, need)] += 1
                if need == 'NEEDLESS' and len(examples[origin]) < 4:
                    examples[origin].append((os.path.basename(rel), e['label'], ta, tb))

    origins = ['already in EN baseline', 'ADDED BY US', 'no English baseline']
    needs = ['STORY/event', 'OVERFLOW', 'NEEDLESS']
    print(f'{"":24s} ' + ''.join(f'{n:>14s}' for n in needs) + f'{"TOTAL":>10s}')
    for o in origins:
        row = [stats[(o, n)] for n in needs]
        if not any(row):
            continue
        print(f'{o:24s} ' + ''.join(f'{v:14d}' for v in row) + f'{sum(row):10d}')
    tot = [sum(stats[(o, n)] for o in origins) for n in needs]
    print(f'{"TOTAL":24s} ' + ''.join(f'{v:14d}' for v in tot) + f'{sum(tot):10d}')
    print()
    for o in origins:
        if examples[o]:
            print(f'--- NEEDLESS examples, {o} ---')
            for f, lab, ta, tb in examples[o]:
                print(f'  {f} :: {lab}')
                print(f'     A: {ta!r}')
                print(f'     B: {tb!r}')


if __name__ == '__main__':
    main()

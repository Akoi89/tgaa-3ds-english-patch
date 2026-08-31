# -*- coding: utf-8 -*-
"""Give TGAA2's UI strings the font tags TGAA1's already have.

The second game's Yes/No buttons render in a decorative script that is hard to
read. The cause is not the font files: TGAA1's button strings begin with
`<FONT 0>` and TGAA2's begin with nothing, so they fall through to the
decorative default. 38 shared labels are in that state, including Examine,
Move, Converse, Present, OK, Cancel, Delete and every game-over option.

WHAT THIS COPIES, AND WHAT IT DELIBERATELY DOES NOT. Only the leading
`<FONT n>` is copied. TGAA1 also carries `<SIZE 16>` and `<CNTR>` on some of
these, and those are NOT copied: TGAA2's font00 was widened during earlier work
on this project, so imposing TGAA1's point size risks overflowing buttons that
currently fit. Font choice is the readability problem; size and centring are
not, and TGAA2 already centres these.

Proof that FONT 0 is the readable face in TGAA2, rather than an assumption
carried over from the first game: TGAA2's own `EX_SUB_PASS` is
`<FONT 0>Transmission received`, and it renders plainly on the DLC page in the
same screenshot where the untagged Yes/No render decoratively.

Also corrects three character names that contradict TGAA2's own cast list,
which reads "Herlock Sholmes" and "Ryunosuke Naruhodo".

NOT changed: the title-screen subtitle. It romanizes the Japanese as
"Ryuunosuke Naruhodou" on purpose, and the first game does the same.

    python fix_t2_ui_text.py <tgaa1_romfs> <tgaa2_romfs_to_edit> [--apply]
"""
import os
import re
import sys

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.arc import parse_arc, build_arc_bytes
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

FONT = re.compile(r'^<FONT \d+>')
TAGS = re.compile(r'^((?:<[^>]+>)*)')

# only where TGAA2 contradicts its own cast list
NAMES = [
    (r'\bHolmes\b', 'Sholmes'),
    (r'\bNaruhodou\b', 'Naruhodo'),
]
# labels never touched, whatever they contain
SKIP_LABELS = {'SCE_NUM04_T', 'SCE_NUM00_T', 'SCE_NUM01_T', 'SCE_NUM02_T',
               'SCE_NUM03_T', 'SCE_NUM05_T'}
# the DLC page's SpotPass toggle: the first game labels this "SpotPass"
RELABEL = {('UI_jpn.gmd', 'EX_SUB_PASS'): '<FONT 0>SpotPass'}


def gmds(root):
    """{(arcpath, gmdname): {label: text}}"""
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith('.arc'):
                continue
            p = os.path.join(dirpath, fn)
            try:
                ents = parse_arc(open(p, 'rb').read())['entries']
            except Exception:
                continue
            for e in ents:
                if not e.name.endswith('.gmd'):
                    continue
                try:
                    doc = parse_gmd_bytes(e.data)
                except Exception:
                    continue
                d = {}
                for en in doc['entries']:
                    if en.get('label'):
                        d[en['label']] = en.get('text') or ''
                out[(p, e.name)] = d
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    ref_root, tgt_root = sys.argv[1], sys.argv[2]
    apply_ = '--apply' in sys.argv

    ref = {}
    for (_, nm), d in gmds(ref_root).items():
        ref.setdefault(nm.split('/')[-1], {}).update(d)

    edits = []          # (arcpath, gmdname, label, old, new, why)
    for (p, nm), d in sorted(gmds(tgt_root).items()):
        short = nm.split('/')[-1]
        for lab, txt in sorted(d.items()):
            if lab in SKIP_LABELS:
                continue
            new, why = txt, None
            key = (short, lab)
            if key in RELABEL and txt != RELABEL[key]:
                new, why = RELABEL[key], 'label'
            else:
                if not TAGS.match(txt).group(1) and txt.strip():
                    r = ref.get(short, {}).get(lab)
                    if r:
                        m = FONT.match(r)
                        # ONLY force FONT 0, the plain face. The tag does not
                        # decide the typeface on its own -- the widget does, and
                        # TGAA2's untagged "Start playing from here?" already
                        # renders plainly while its untagged Yes/No do not. So
                        # forcing the plain font can only ever match what is
                        # already correct or fix what is not. Copying TGAA1's
                        # <FONT 2> would do the opposite: it would impose the
                        # decorative face on text that currently reads fine
                        # (SCE_NUM04, INTERVAL_CONT, INTERVAL_END).
                        if m and m.group(0) == '<FONT 0>':
                            new, why = m.group(0) + txt, 'font'
                if why is None:
                    for pat, right in NAMES:
                        if re.search(pat, new):
                            new, why = re.sub(pat, right, new), 'name'
            if why:
                edits.append((p, nm, lab, txt, new, why))

    by = {}
    for e in edits:
        by[e[5]] = by.get(e[5], 0) + 1
    print('%d edits: %s\n' % (len(edits), ', '.join('%s %d' % (k, v) for k, v in sorted(by.items()))))
    for p, nm, lab, old, new, why in edits:
        print('   %-5s %-22s %-26s %r -> %r'
              % (why, nm.split('/')[-1][:22], lab[:26], old[:26], new[:34]))
    if not apply_:
        print('\n--report only; pass --apply to write')
        return

    # group by archive, rebuild each .gmd, then each .arc
    per_arc = {}
    for p, nm, lab, old, new, why in edits:
        per_arc.setdefault(p, {}).setdefault(nm, {})[lab] = new
    print()
    for p, gmd_edits in sorted(per_arc.items()):
        arc = parse_arc(open(p, 'rb').read())
        repl = {}
        for e in arc['entries']:
            if e.name not in gmd_edits:
                continue
            doc = parse_gmd_bytes(e.data)
            hits = 0
            for en in doc['entries']:
                if en.get('label') in gmd_edits[e.name]:
                    en['text'] = gmd_edits[e.name][en['label']]
                    hits += 1
            assert hits == len(gmd_edits[e.name]), \
                '%s: wrote %d of %d' % (e.name, hits, len(gmd_edits[e.name]))
            repl[e.name] = build_gmd_bytes(doc)
        open(p, 'wb').write(build_arc_bytes(arc, repl))
        print('   %-34s %d gmd, %d strings'
              % (os.path.basename(p), len(repl), sum(len(v) for v in gmd_edits.values())))
    print('\n%d strings rewritten' % len(edits))


if __name__ == '__main__':
    main()

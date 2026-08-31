# -*- coding: utf-8 -*-
"""Cross-game UI text audit: font tags and character names.

Found by the user, by eye, on a screenshot: the second game's Yes/No buttons
render in a decorative script that is hard to read, while the first game's are
plain. The cause is not a font file -- it is that TGAA1's strings carry
`<FONT 0><SIZE 16><CNTR>` and TGAA2's carry no tags at all, so they fall through
to the decorative default.

That is a whole class of defect, not one string, and nothing in this project
looked for it: every audit so far checked audio, textures or line lengths.
This one compares the two games' shared UI strings by label.

  FONT TAG   a label that carries <FONT n> in one game and nothing in the other
             renders in a different typeface between the two games
  NAME       a character name that does not match Capcom's official English
             ("Sholmes", not "Holmes"; "Naruhodo", not "Naruhodou")

GMD text in TGAA2 is XOR-encrypted, which is why a plain grep of the romfs finds
none of this -- the labels are readable but the strings are ciphertext.

    python audit_ui_text.py <tgaa1_romfs> <tgaa2_romfs>
"""
import os
import re
import sys

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.arc import parse_arc
from dgs2tool.gmd import parse_gmd_bytes

# Capcom's official English spellings, and what tends to appear instead
OFFICIAL = {
    'Holmes': 'Sholmes',
    'Naruhodou': 'Naruhodo',
    'Naruhodoh': 'Naruhodo',
    'Naruhodo Ryunosuke': 'Ryunosuke Naruhodo',
    'Mikotoba Susato': 'Susato Mikotoba',
    'Asougi': 'Asogi',
    'Watson': 'Wilson',
}
TAG = re.compile(r'^((?:<[^>]+>)*)')


def strings(root):
    """{(gmd, label): text} for every message entry under `root`."""
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith('.arc'):
                continue
            try:
                ents = parse_arc(open(os.path.join(dirpath, fn), 'rb').read())['entries']
            except Exception:
                continue
            for e in ents:
                if not e.name.endswith('.gmd'):
                    continue
                try:
                    doc = parse_gmd_bytes(e.data)
                except Exception:
                    continue
                g = e.name.split('/')[-1]
                for en in doc['entries']:
                    lab = en.get('label')
                    if lab:
                        out[(g, lab)] = en.get('text') or ''
    return out


def tags_of(text):
    m = TAG.match(text)
    return m.group(1) if m else ''


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    one, two = strings(sys.argv[1]), strings(sys.argv[2])
    shared = sorted(set(one) & set(two))
    print('TGAA1 %d strings, TGAA2 %d, %d share a label\n' % (len(one), len(two), len(shared)))

    missing = []
    for k in shared:
        t1, t2 = tags_of(one[k]), tags_of(two[k])
        if t1 and not t2 and one[k].strip() and two[k].strip():
            missing.append((k, t1, two[k]))
    print('FONT TAG -- TGAA1 sets a tag, TGAA2 sets none (%d)' % len(missing))
    for (g, lab), t1, txt in missing[:30]:
        print('   %-24s %-22s TGAA1 %-28s TGAA2 %r' % (g[:24], lab[:22], t1[:28], txt[:24]))
    if len(missing) > 30:
        print('   ... %d more' % (len(missing) - 30))

    print()
    names = []
    for src, lab_ in ((one, 'TGAA1'), (two, 'TGAA2')):
        for (g, lab), txt in sorted(src.items()):
            for wrong, right in OFFICIAL.items():
                # \b alone is not enough: "Naruhodo" is a substring of the wrong
                # spelling "Naruhodou", so an `right not in txt` guard silently
                # suppresses exactly the case being looked for
                if not re.search(r'\b%s\b' % re.escape(wrong), txt):
                    continue
                without = re.sub(r'\b%s\b' % re.escape(wrong), '', txt)
                if right in without:
                    continue                      # correct form used elsewhere in the same string
                names.append((lab_, g, lab, wrong, right, txt[:40]))
    print('NAME -- not Capcom\'s official English (%d)' % len(names))
    for game, g, lab, wrong, right, txt in names[:30]:
        print('   %-6s %-22s %-26s %-10s -> %-10s %r' % (game, g[:22], lab[:26], wrong, right, txt))
    if len(names) > 30:
        print('   ... %d more' % (len(names) - 30))
    return len(missing) + len(names)


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 0)

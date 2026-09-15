# -*- coding: utf-8 -*-
"""Render translations.jsonl into TRANSLATIONS.md (one section per page, Japanese beside English)."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ISSUE_TITLE = {0: 'Special issue (Episode 0)', 1: 'No.1 Ryunosuke Naruhodo', 2: 'No.2 Susato Mikotoba', 3: 'No.3 Herlock Sholmes',
               4: 'No.4 Iris Wilson', 5: 'No.5 Kazuma Asogi', 6: 'No.6 Barok van Zieks', 7: 'No.7 Empire of Japan special',
               8: 'No.8 British Empire special', 13: 'Event art'}
HINTS = {'aoc05_design_07', 'aoc07_design_04', 'aoc07_design_05', 'aoc08_design_06', 'aoc08_design_07'}

rows = [json.loads(l) for l in io.open(os.path.join(HERE, 'translations.jsonl'), encoding='utf-8') if l.strip()]
kind_order = {'design': 0, 'editor': 1, 'theme': 2, 'event': 3}
rows.sort(key=lambda r: (kind_order[r['page'].split('_')[1]], r['issue'], r['page']))
seen = set()
out = ['# TGAA1 DLC Picture Book, Editor\'s Notes and theme pages: translations', '',
       'Source: the shipped DLC 1.0.10 (Final/_CURRENT/TGAA1-DLC-1.0.10.cia). %d pages: 66 Picture Book pages, 2 Editor\'s Notes pages, 8 theme previews, 1 event picture with no text.' % len(rows), '',
       'Every Picture Book page is a single picture with the commentary painted into it; none of this text lives in the game\'s message files, so each page has to be redrawn as an image.', '',
       'Commentary is by Kazuya Nuri (art director and character designer). The Editor\'s Notes are Shu Takumi\'s handwriting. Names follow the English games: Herlock Sholmes, Iris Wilson, Barok van Zieks, Mael Stronghart, Nikolina Pavlova, the Beates.', '',
       'Pages marked **hint** mention story details (a character\'s importance, a role, a gag). Nothing states a culprit or an ending.', '',
       '## How to edit', '',
       '- Edit the files in `orig/` (512 x 256 PNG). Keep the size and the file name. Those are what I import back, losslessly (checked: an unedited PNG re-encodes to the original texture byte for byte).',
       '- Only the rectangle outlined in red in `guide/` is ever on screen: x 24 to 424, y 8 to 248 (400 x 240). Anything outside it can stay as it is.',
       '- `screen/` holds just the visible part, for reading. `sheets/` are contact sheets.',
       '- Alpha is ignored; these textures are plain RGB.', '']
for r in rows:
    if r['issue'] not in seen:
        seen.add(r['issue'])
        out += ['## %s' % ISSUE_TITLE.get(r['issue'], 'Issue %d' % r['issue']), '']
    out.append('### %s%s' % (r['page'], '  (hint)' if r['page'] in HINTS else ''))
    out.append('')
    if not r['jp'] and not r['en']:
        out += ['No text.', '']
        continue
    out += ['Japanese:', '', '> ' + r['jp'].replace('\n', '\n> '), '', 'English:', '', '> ' + r['en'].replace('\n', '\n> '), '']
    if r.get('art_text'):
        out += ['Text in the artwork: ' + r['art_text'], '']
    if r.get('notes'):
        out += ['Note: ' + r['notes'], '']
text = '\n'.join(out) + '\n'
bad = [c for c in text if c in '—–']
assert not bad, 'dash characters present'
io.open(os.path.join(HERE, 'TRANSLATIONS.md'), 'w', encoding='utf-8').write(text)
print('TRANSLATIONS.md: %d pages, %d words of English' % (len(rows), sum(len(r['en'].split()) for r in rows)))

# -*- coding: utf-8 -*-
"""Per-issue content for the nine Randst Magazine covers.

Every proper noun below was checked against the OFFICIAL English text
shipped in the base game (senyarom's port of the Chronicles script), not
translated freehand. That check turned up four errors in the previous
English art, all corrected here:

  Ep 3  "At the British Supreme Court"  -> the Japanese is 首席判事執務室,
        and the official location caption is "Lord Chief Justice's Office"
  Ep 6  "Mr Natsume's Room"             -> official is "Soseki Natsume" (32x)
  Ep 7  "Takeshi Anai"                  -> official is "Taketsuchi Auchi" (4x)
  Ep 8  "In the Bailey"                 -> official caption is "The Old Bailey"

UPDATE: the official PC (Chronicles) escapade banners surfaced later and
carry Capcom's own English episode titles. Those override the caption-
based guesses above: "In the Defendants' Antechamber", "At the British
Supreme Court", "In Sholmes's Suite", "At Naruhodo's Legal Consultancy",
"In Mr Natsume's Room", "In the Bailey". Ep 0 has no English banner.
"""

STRAP = 'SHORT STORY'          # ショート・ショート -- the DLC List calls it this

# Rows are (slot, kind, [items], more?) where slot is the vertical
# position 0-3. Capcom does not always use one slot per category: Ep 7's
# movie entry runs onto a second line and Ep 8's art entry does, so those
# covers use a 'cont' row to hold the overflow exactly where the Japanese
# put it. Getting this wrong leaves an erased empty slot on the plate.
COVERS = {
 0: dict(title='Episode 0: At the Supreme Court', rows=[
        (0, 'art',   ['Main', 'Design Art'], False),
        (1, 'music', ['Ryunosuke Naruhodo - Objection!'], True),
        (2, 'audio', ['Naruhodo Voice Collection'], False),
        (3, 'movie', ['Prototype Commentary', 'Theme Intro'], False)]),
 1: dict(title="Episode 1: In the Defendants' Antechamber", theme='Ryunosuke Naruhodo', rows=[
        (0, 'art',   ['Ryunosuke Naruhodo'], False),
        (1, 'music', ['GAA - Court is Now in Session'], True),
        (2, 'audio', ['Naruhodo Voice Collection'], False),
        (3, 'movie', ['The Great Special Trial 2014'], False)]),
 2: dict(title='Episode 2: In a First-Class Cabin', theme='Sholmes & Iris', rows=[
        (0, 'art',   ['Susato Mikotoba'], False),
        (1, 'music', ['Susato Mikotoba - A New Bloom'], True),
        (2, 'audio', ['Susato Voice Collection'], False),
        (3, 'movie', ['Jump Festa Exhibition Video'], False)]),
 3: dict(title='Episode 3: At the British Supreme Court', theme='Susato Mikotoba', rows=[
        (0, 'art',   ['Herlock Sholmes'], False),
        (1, 'music', ['The Truth Revealed (Adventures)'], True),
        (2, 'audio', ['Sholmes Voice Collection'], False),
        (3, 'movie', ['Episode 1 Commentary'], False)]),
 4: dict(title="Episode 4: In Sholmes's Suite", theme='Barok van Zieks', rows=[
        (0, 'art',   ['Iris Wilson'], False),
        (1, 'music', ['Iris Wilson'], True),
        (2, 'audio', ['Iris Voice Collection'], False),
        (3, 'movie', ['Episode 2 Commentary'], False)]),
 5: dict(title="Episode 5: At Naruhodo's Legal Consultancy", theme='Sholmes & Iris II', rows=[
        (0, 'art',   ['Kazuma Asogi'], False),
        (1, 'music', ['Kazuma Asogi - Samurai of Destiny'], True),
        (2, 'audio', ['Asogi Voice Collection'], False),
        (3, 'movie', ['Episode 3 Commentary'], False)]),
 6: dict(title="Episode 6: In Mr Natsume's Room", theme='Soseki Natsume & Wagahai', rows=[
        (0, 'art',   ['Barok van Zieks'], False),
        (1, 'music', ['Lord Chief Justice Stronghart'], True),
        (2, 'audio', ['van Zieks Voice Collection'], False),
        (3, 'movie', ['Episode 4 Commentary'], False)]),
 7: dict(title='Episode 7: On Briar Road', theme='Taketsuchi Auchi', rows=[
        (0, 'art',   ['Taketsuchi Auchi', 'Satoru Hosonaga'], True),
        (1, 'music', ['Gina Lestrade'], True),
        (2, 'movie', ['Episode 5 Commentary'], False),
        (3, 'cont',  ['Special Video: Music'], False)]),
 8: dict(title='Episode 8: In the Bailey', theme='Kazuma Asogi', rows=[
        (0, 'art',   ['Gina Lestrade'], False),
        (1, 'cont',  ['Tobias Gregson'], True),
        (2, 'music', ['The Great Ace Attorney - Adjudication'], True),
        (3, 'movie', ['Special Video: Sound Effects'], False)]),
}

LABEL = {'art': 'ART', 'music': 'MUSIC', 'audio': 'AUDIO', 'movie': 'MOVIE'}
LABEL_LONG = {'art': 'PICTURE BOOK', 'music': 'MUSIC',
              'audio': 'AUDIO', 'movie': 'MOVIE'}
THEME_LABEL = 'THEME'

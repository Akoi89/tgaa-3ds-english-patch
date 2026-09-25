# Release Notes

This project brings Capcom's official English text, voices and art from the Chronicles
release onto the Japanese 3DS versions of The Great Ace Attorney 1 and 2, including both
games' DLC. It builds on senyarom's earlier fan patch and ships a base patch and a DLC
patch for each game.

## What this build fixes

- Lowercase t and e. On the DLC menu headings they came out broken, so "Picture Book"
  read "Picturc Book", and v1.9b's fix pushed them a pixel below the line so the e grew a
  tail. Now only their crossbars get a light extra row, and i, j and l, which read a
  shade heavier than the rest, are slightly lighter. Both games, checked on the emulator.
- The first game's DLC. Picture Book commentary is usually two sizes bigger on 51 of its
  76 pages, with the see-through panel behind it extended to fit, and the faint Japanese
  behind the English on several pages is gone. The menu icons, which had slipped back to
  an older sheet with smudges under the pictures in v1.8b, are the clean v1.7 ones again.
  The galleries for the never-released issues 9 to 13 show Capcom's placeholder text in
  English.
- The title screen. The DLC card read "D L C" on four diamonds and went dark when
  pressed; it now reads "Extras" sideways like its neighbours and turns white when
  pressed, in both games. A line in the first game's second Dance of Deduction that ran
  onto the box frame is re-broken.
  Four "Bonus voice recital" tracks play Capcom's English, gallery titles fit their
  plates, and characters no font in the game can draw were swapped for ones it can.
- The grain over the first game's animated cutscenes. Not a format limit after all: my
  tools wrote every English sound track a few bytes out of position, so the console read
  each one slightly late, and that misread was the grain. Checked by recording the
  emulator before and after; not yet heard on a 3DS.
- Courtroom crowd sounds that came out scrambled, two in each game: the same misalignment
  plus a wrong channel layout. Every replaced sound in both games and their DLC is back
  in position, which also fixes at the root the click that v1.5 covered with silence.
  Crowd noise that went quiet and jumped back in now loops where Capcom's English
  recordings say to.
- Voice lines cut off, made duller or left in Japanese because the English take ran
  longer than the Japanese one. Same bug. Every replaced voice in both games and their
  DLC is at full quality and full length, the second-game lines with pauses cut from the
  middle are whole again, and the story lines that stayed Japanese for length, plus the
  second game's last Japanese crowd chant, play Capcom's English. Every DLC line was
  heard playing in full in an emulator; the story lines and the chant were mostly checked against the
  recordings offline. Gasps and cries in the second game's Dance of Deduction, distorted
  by a decoding mistake of mine, are clean too (checked by decoding only).
- The first game's parchment narration at the start of Episode 2 had been sped up, by
  up to about a third, to finish before each page turned. v1.9 put it back to natural
  pace but left the second half of each page waiting on a cue set for the Japanese
  take, so five pages paused for half a second or more, three of them mid-sentence or
  mid-word, and two felt rushed. From v1.9a each page reads straight through, the way
  Capcom's PC release times this scene, with the page turns on Capcom's original
  timing, and the three places where a page's two halves met in the middle of a word
  now meet in a pause in the actor's delivery. Heard in-game.
- Text in the first game: pop-up document and report pages that ran off the right edge
  are re-broken, not a word changed; Court Record captions the game had been shrinking
  small and soft draw at full size, a few with a word or comma trimmed.

## Version history

Newest first. A version's changes are listed here and nowhere else.

- v1.9c: v1.9b's t and e fix redone so the letters sit on the line, i, j and l a touch
  lighter, in both games; bigger commentary on 51 Picture Book pages with the leftover
  Japanese gone; the clean v1.7 DLC menu icons back; an "Extras" title card in both
  games; decorative-font lines re-broken; issues 9 to 13 gallery text in English. Every
  update and DLC changed.
- v1.9b: the broken t and e on the DLC menu headings, in both games; the second game's
  title screen and DLC banner show their real version numbers again. Every update
  changed, and the second game's DLC.
- v1.9a: the first game's Episode 2 opening narration reads straight through on each
  page instead of pausing mid-sentence, and no longer splits a word in three places.
  First game's update only.
- v1.9: the cutscene grain, scrambled crowd sounds, crowd loops, the old click's root
  cause; every voice at full quality and length, the "too long" lines and the last crowd
  chant in English, pauses restored; Episode 2 narration at natural speed; pop-up pages
  and captions; Dance reactions; DLC gallery titles, Picture Book text, four recitals,
  blank characters. Every patch changed.
- v1.8b: the crackle over the first game's cutscenes. First game's update only.
- v1.8a: no game change; the xdelta patches apply to cartridge dumps too.
- v1.8: the blurred DLC art book pages from v1.7. First game's DLC only.
- v1.7: the first game's DLC art book, theme gallery and editor's notes in English; DLC
  icons redrawn; a smudged score sheet in the second game's DLC. Both first-game files and
  the second game's DLC.
- v1.6: Capcom's own shout graphics and more of its textures; the second game's official
  logo. Both updates.
- v1.5: the click at the end of replaced voice lines; two cramped second-game menus; the
  second game's patch outranks Capcom's update. All four files.
- v1.4: the first hardware playthrough of the DLC stories; second-game dialogue no longer
  cut off under the page arrow; more English voices; English HOME icon and banner. All
  four files.
- v1.3: the v1.2 fix for the second game and its DLC; over-long evidence pop-ups
  shortened. Second game only.
- v1.2: first-game cross-examination statements no longer run into the box edge; typos.
  First game's update only.
- v1.1: Capcom's real logos, evidence card names, deduction plates and ending card; real
  version numbers; spellings. Both updates and the first game's DLC.
- v1.0: first public release: Capcom's English text on both games and their DLC over
  senyarom's patch, plus English DLC voice clips, subtitled commentary videos, magazine
  covers, refitted captions and readable second-game menus.

## Known problems

- Some lines are still spoken in Japanese because Capcom never recorded English for
  them: four courtroom shouts, two "Take that!" shouts in the second game's DLC and a
  run of narration lines.
- The second game's end credits are Japanese on purpose; a misspelled credit is worse
  than an untranslated one.
- Some text still runs past its box: a few dozen second-game dialogue pages end under
  the page arrow, four first-game widget pages sit on the edge, and two lines in the
  fancier face end slightly under the arrow.
- Japanese remains in the first game's DLC Picture Book (name tags, production
  scribbles).
- Nobody has played either main game through on a console yet. The English lines added
  to the second game's last two episodes, and the crowd loops, were checked offline only.

## Files

Per game, on the release page:

- `TGAA1-base-3.3.5.cia` / `TGAA2-base-1.0.19.cia`: the update.
- `TGAA1-DLC-1.0.17.cia` / `TGAA2-DLC-1.0.13.cia`: the DLC. `TGAA1-EN-DLC-v1.9c.cia` /
  `TGAA2-EN-DLC-v1.9c.cia`: the same DLC decrypted inside, for emulators. One or the
  other, not both.
- `TGAA1-3DS-English-v1.9c-xdelta.zip` / `TGAA2-3DS-English-v1.9c-xdelta.zip`: both as
  xdelta patches against your own decrypted dump, with the HOME banner patch
  (`TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta`, also posted on its own)
  and a readme (`TGAA1-README-v1.9c.txt` / `TGAA2-README-v1.9c.txt`, also posted on their
  own).
- `TGAA1-3DS-English-JPvoice-v1.9c-xdelta.zip` / `TGAA2-3DS-English-JPvoice-v1.9c-xdelta.zip`:
  the Japanese-voice edition, same text and art, all audio Capcom's Japanese.
- `HASHES_v1.9c.txt`: size, CRC32 and sha256 of every source dump, patch and result, so
  you can check a file before and after patching.

Sizes, hashes, apply steps and troubleshooting are in the README.

## Credits

senyarom did the hard part: their layout pipeline, font handling and port of Capcom's
script onto the 3DS builds are what everything here sits on, building on Scarlet Study
and Fan Translators International's earlier English builds. The logos, evidence cards,
shout lettering and voices are Capcom's, from Chronicles. Full credits are in the README.

The Great Ace Attorney and Chronicles are (c) Capcom.

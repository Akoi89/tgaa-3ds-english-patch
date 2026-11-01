# Release Notes

This project brings Capcom's official English text, voices and art from the Chronicles
release onto the Japanese 3DS versions of The Great Ace Attorney 1 and 2, including both
games' DLC. It builds on senyarom's earlier fan patch and ships an installable update and
DLC for each game, plus optional xdelta patch zips for your own dumps.

## What this build fixes

- **The second game's Case 5 suitcase lock.** The clue asked for a seven-digit code, but the
  Japanese 3DS lock has six wheels, so it couldn't be entered. It has seven wheels now, as in
  Capcom's version, and the tattoo has seven characters again. It needed a
  change to the game's program.
- **Dance of Deduction.** The word that flies across the top screen was cut into three
  pieces stepping down; it's one straight line now, and in the second game g, y and p are no
  longer cut off at the bottom. Note-card titles and conclusions show Capcom's English lettering; they had a stray letter and a blank.
- **Letters and spacing.** The e, t, i, j and l are back to the earlier fan translation's shapes,
  broken letters like "Picturc" are fixed, and stray spaces are gone.
- **Pictures.** Pictures that looked rough or pasted over are redone, and Van Zieks's
  "Objection!" bubble shows the whole word. I redrew the first game's Waiter's Business Card
  and Medical Report Card cover with an image generator; Chronicles has no English version
  of them.
- **An English manual.** The HOME menu manual is English, Scarlet Study's translation
  revised to match the game, with main screenshots retaken in the patched game.
  On Azahar the Manual is read from the base game, so the optional base patch carries it too.
- **Chapter names and headings.** The start-a-chapter box centres the chapter name, and the
  second game's episode heading is two centred lines.
- **Sound.** Cutscene grain, scrambled crowd sounds and the voice-line click are
  fixed, replaced voices play at full length, and the metallic "shing" is back under English shouts.
- **Text that ran past its box.** Speech bubbles, location cards, documents, juror boxes and
  the Move list have new line breaks or shorter wording to fit their boxes, and a split thought no longer moves the speaker's
  mouth.

## Version history

- v1.9s: the optional base patch now puts the English manual into the base game as well as the banner, so the HOME menu Manual is English on Azahar.
- v1.9r: second-game suitcase lock gets seven wheels, with the clue and tattoo to match; flying words keep the tails of g, y and p.
- v1.9q: clue and tattoo changed to match the six-wheel lock (reversed in v1.9r); flying words line up; e, t, i, j and l restored; manual screenshots retaken.
- v1.9p: two first-game evidence pictures redrawn; capital H, E and F keep their crossbar; chapter names centred.
- v1.9o: an English manual.
- v1.9n: Present and Examine questions fit; the "shing" back under English shouts.
- v1.9m: Van Zieks's "Objection!" bubble whole; first-game Dance labels keep their g, p and y tails; staff credits; "Mr Sholmes".
- v1.9l: Move list names whole; juror boxes and autopsy pages fit; "Invalid Message" gone; pictures redone.
- v1.9k: stray spaces and typos removed.
- v1.9j: a thought over two pages no longer moves the speaker's mouth.
- v1.9i: no extra space after a lowercase w in the second game.
- v1.9h: centred pages keep their centring; a DLC headline types at the right speed.
- v1.9g: a split page keeps its colour, red highlight and typing speed.
- v1.9f: location cards and second-game documents re-broken; tighter letter gaps; a clearer lowercase t in first-game DLC headings.
- v1.9e: long speech-bubble lines no longer cut off.
- v1.9d: English on the Dance of Deduction note cards.
- v1.9c: DLC letters redone; bigger Picture Book commentary; clean DLC icons; "Extras" title card.
- v1.9b: broken t and e on DLC headings fixed; real version numbers on the second game.
- v1.9a: the first game's Episode 2 opening narration reads straight through.
- v1.9: cutscene grain, crowd sounds and voice click fixed; full-quality voices; too-long story lines in English.
- v1.8b: the cutscene crackle fixed.
- v1.8a: no game change; the xdelta patches also work on cartridge dumps.
- v1.8: blurred DLC art book pages fixed.
- v1.7: first-game DLC art book, themes and editor's notes in English; DLC icons redrawn.
- v1.6: Capcom's own shout graphics and more textures; the second game's logo.
- v1.5: voice-line click covered with silence; two cramped second-game menus; the second-game patch outranks Capcom's update.
- v1.4: first DLC playthrough on a 3DS; second-game dialogue mostly clear of the page arrow; more English voices; HOME icon.
- v1.3: cross-examination fix carried to the second game and DLC; long evidence pop-ups shortened.
- v1.2: first-game cross-examination statements fit the box; typos fixed.
- v1.1: Capcom's real logos, evidence card names, deduction plates and ending card; real version numbers.
- v1.0: first public release: Capcom's English text on both games and DLC over senyarom's patch, with DLC voice clips and commentary videos.

## Known problems

- Some shouts and story lines are still spoken in Japanese because Capcom never recorded English for them.
- The second game's end credits are Japanese on purpose.
- Some text still runs past its box: second-game dialogue pages under the page arrow, a few first-game pages, and two lines in the fancier font.
- The manual's logo, headings and diagrams are partly the older fan translation's, so a few show older names.
- Japanese remains in the first game's DLC Picture Book (name tags, production scribbles).
- The seven-wheel lock's cyan cursor is clipped slightly at the frame's edge on the first and last wheel. It's cosmetic.

Testing: earlier versions of both games install and start on a 3DS, and a tester played the second game's DLC stories through on an original 3DS. The v1.9p, v1.9q, v1.9r and v1.9s changes haven't been tried on a 3DS; the v1.9s base patch was seen on the Azahar desktop app only, the seven-wheel lock opens in the Azahar emulator, but some other changes were checked only in the game's files, and the add-on below hasn't been tried with Luma or on a console. Nobody has played either main game through on a console. [TESTING.md](TESTING.md) has the detail; if anything looks wrong, [issue #1](../../issues/1) is the place.

## Files

Per game, on the release page:

- `TGAA1-base-3.4.2.cia` / `TGAA2-base-1.0.32.cia`: the update, with the English manual in it. In v1.9r only the second game's changed; it keeps its name and its `ENG 1.0.32` stamp, and the README gives the sha256 that tells it from v1.9q's. v1.9s leaves both updates as they were.
- `TGAA1-DLC-1.0.23.cia` / `TGAA2-DLC-1.0.19.cia`: the DLC, unchanged in v1.9r and v1.9s. `TGAA1-EN-DLC-v1.9m.cia` / `TGAA2-EN-DLC-v1.9q.cia`: the same DLC decrypted inside, for emulators. One or the other, not both.
- `TGAA1-3DS-English-v1.9s-xdelta.zip` / `TGAA2-3DS-English-v1.9s-xdelta.zip`: xdelta patches against your own decrypted dump, with the banner and manual patch and a readme inside, both also posted on their own.
- `TGAA1-3DS-English-JPvoice-v1.9r-xdelta.zip` / `TGAA2-3DS-English-JPvoice-v1.9r-xdelta.zip`: the Japanese-voice edition, same text and art, all audio Capcom's Japanese. Still the v1.9r files, unchanged in v1.9s.
- `HASHES_v1.9s.txt`: size, CRC32 and sha256 of the English xdelta sources, patches and results. Your own source dump won't hash-match mine, and that's expected.

The install steps are in the README. The release page also has an optional second-game add-on, `TGAA2-SevenWheelLock-LayeredFS-v1.9r.zip` (still the v1.9r file): the seven-wheel lock as loose files for Luma3DS or Azahar. Skip it if you're just installing the update. It's mainly for people porting the lock to another language: its scripts and tattoo are English, and its readme says which builds it fits. `LOCK_PATCH_NOTES.md` has the notes.

## Credits

senyarom's layout pipeline, font handling and port of Capcom's script onto the 3DS builds are what this patch starts from, building on Scarlet Study and Fan Translators International's earlier English builds. The English manual is Scarlet Study's, with the text revised for this patch. The logos, evidence cards, shout lettering and voices are Capcom's, from Chronicles, apart from two first-game evidence pictures I redrew for this patch (an image generator, finished by me). Full credits are in the README.

The Great Ace Attorney and Chronicles are (c) Capcom.

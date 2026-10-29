# Release Notes

This project brings Capcom's official English text, voices and art from the Chronicles
release onto the Japanese 3DS versions of The Great Ace Attorney 1 and 2, including both
games' DLC. It builds on senyarom's earlier fan patch and ships an installable update and
DLC for each game, plus optional xdelta patch zips for your own dumps.

## What this build fixes

- **An English manual.** The manual you open from the HOME menu was Japanese in both games.
  The update now carries an English one: Scarlet Study's fan translation of it, with the
  wording revised so names and terms match the game and Capcom's release, and a page about
  this patch. Its screenshots and some of its headings are still the older translation's.
- **The Dance of Deduction note cards.** The card that sums up each topic showed a single
  stray letter for its title and a blank conclusion, because its fonts had no English
  letters. Both fonts now draw Capcom's own English lettering, in every Dance of Deduction
  in both games. The cyan labels the first game shows when the crosshair is on an object
  no longer have the tails of g, p and y cut flat. In both games, the "Hold it, Mr
  Holmes!" and "Deduction Failed" lines now read "Hold it, Mr Sholmes!" and "I can see
  nothing.", as in Capcom's version.
- **Broken letters, cramped names and stray spaces.** DLC menu headings no longer show
  broken letters (like "Picturc Book"), the t in the first game's Picture Book commentary has a proper
  crossbar, the gap after a capital T, V or W is tighter, the second game's Court
  Record no longer crams evidence and profile names together, and a lowercase w in the
  second game no longer leaves a sliver of extra space before the next letter. Lines no
  longer have stray spaces or odd punctuation where Capcom's script has none ("student ,
  currently", "touch ' Present '"), and a handful of small slips are fixed.
- **Pictures that looked patched, wrong names in pictures, and the first game's DLC Picture Book.** Commentary is
  bigger on most pages, with the faint leftover Japanese behind it gone. The smudged menu
  icons are clean again, and the galleries for issues that were never released show
  Capcom's English placeholder text. Pictures that looked patched rather than made are
  redone in both games: picture book pages, maps, pawn tickets, a newspaper and the second
  game's HOME menu banner, where the "2" was cut off. A second full look at every picture
  fixed Van Zieks's "Objection!" bubble, which was chopped off after the "n" with no "!"
  in both games, the first game's staff credits (spellings and job titles now follow
  Capcom's own English credits), a medical report card that said John Watson instead of
  Wilson, a tutorial picture that spelt Yujin and Yumei with a double u, a washed-out
  bookcase, and a DLC design page whose text crowded a sketch.
- **The title screen's DLC card.** It read "D L C" on four diamonds and went dark when
  pressed; it now reads "Extras" sideways like its neighbours and turns white when
  pressed, in both games.
- **Grain over the first game's cutscenes, and scrambled courtroom crowd sounds.** My tools
  wrote every replaced sound slightly out of position, so it played with a grain, and a
  few crowd sounds also had the wrong channel layout. Every sound is back in position, the
  click at the end of replaced voice lines is gone at the root, and crowd noise loops
  where Capcom's recording says to.
- **Voice lines cut short, dulled, left in Japanese, or missing the "shing".** Every
  replaced voice now plays at full quality and length, and the second game's lines with
  pauses cut from the middle are whole again. Story lines that had stayed Japanese because
  the English ran long now play Capcom's English recording, as do four bonus recital tracks
  in the first game's DLC and the second game's last crowd chant, and the second game's
  Dance of Deduction gasps and cries aren't distorted any more. Capcom mixes a metallic
  "shing" into its Japanese shout clips, and the English recordings didn't have it. It's
  mixed back in under the English "Hold it!", "Objection!" and "Take that!", in both games
  and the second game's DLC, set so the louder shouts don't distort.
- **The first game's Episode 2 opening narration.** It had been sped up to finish before
  each page turned. It now reads straight through at a natural pace, with the page turns
  on Capcom's own timing.
- **Text that ran past its box.** The partner's speech bubble on the bottom screen cut
  long lines off, often mid-word, and location cards, the second game's autopsy reports
  and case documents, and the first game's pop-up pages ran off the edge. They're all
  re-broken; only a few location descriptions, captions, evidence names, questions and one
  remark were lightly trimmed. A line split onto a second page now keeps its thought
  color, red highlight and typing speed, and a thought that runs onto a second page closes
  its bracket at the break and opens a new one on the next, so the speaker's mouth stays
  still while they're only thinking. A line further down a centred page now keeps
  its centring instead of landing against the left edge. The Move list no longer hides the
  start of a place name under the "You" tag or cuts long ones off, the juror boxes in the
  Summation Examination no longer chop lines at the edge, autopsy reports and other
  evidence pages fit their frame, and "Invalid Message" no longer shows under two cutscene
  subtitles in the first game. The question shown with the Present and Examine buttons
  runs further right than the speech bubble does, and a few of them were chopped off
  partway through a word on the lower screen; they're re-broken now, and the longest
  continue on a second page.

## Version history

- v1.9o: the update carries an English manual (Scarlet Study's text, revised so names and
  terms match the game), opened from the HOME menu.
- v1.9n: the question beside the Present and Examine buttons is no longer chopped off
  partway through a word; the metallic "shing" is back under the English shouts.
- v1.9m: Van Zieks's "Objection!" bubble shows the whole word and the "!"; the first
  game's Dance of Deduction labels keep the tails of g, p and y; its staff credits follow
  Capcom's English credits; "Hold it, Mr Sholmes!" and a few names in pictures corrected.
- v1.9l: the Move list shows whole place names; juror boxes and autopsy pages no longer
  cut off or run into their frame; "Invalid Message" gone from two cutscene subtitles; a
  round of pictures redone, including the second game's HOME menu banner.
- v1.9k: stray spaces in the text ("student , currently") and a few small typos are gone,
  matching Capcom's script.
- v1.9j: a thought that runs onto a second page no longer makes the speaker's mouth move.
- v1.9i: a lowercase w in the second game no longer leaves an extra sliver of space
  before the next letter.
- v1.9h: a line further down a centred page keeps its centring instead of landing against
  the left edge; a DLC newspaper headline types at the right speed all the way through.
- v1.9g: a line split onto a second page keeps its color, red highlight and typing speed.
- v1.9f: location cards, second-game autopsy reports and case documents, and other
  overflowing lines re-broken or lightly trimmed; a tighter letter gap; the second game's
  Court Record names no longer crammed; a clearer lowercase t in the first game's DLC
  menu headings and Picture Book.
- v1.9e: long lines in the bottom-screen speech bubble no longer get cut off.
- v1.9d: English text on the Dance of Deduction note cards.
- v1.9c: the DLC letter fix redone; bigger Picture Book commentary with the leftover
  Japanese gone; the clean DLC menu icons back; an "Extras" title card; decorative-font
  lines re-broken.
- v1.9b: the broken t and e on the DLC menu headings fixed; the second game's title
  screen and DLC banner show their real version numbers again.
- v1.9a: the first game's Episode 2 opening narration reads straight through instead of
  pausing mid-sentence.
- v1.9: cutscene grain, scrambled crowd sounds, crowd loops and the click's root cause
  fixed; every voice at full quality and length, second-game pauses restored, the too-long
  story lines and the last crowd chant in English; clean Dance of Deduction gasps;
  Episode 2 narration at natural speed; pop-up pages, captions, blank quote marks and
  punctuation, four recitals, and DLC gallery and Picture Book text.
- v1.8b: the crackle over the first game's cutscenes fixed.
- v1.8a: no game change; the xdelta patches apply to cartridge dumps too.
- v1.8: the blurred DLC art book pages from v1.7 fixed.
- v1.7: the first game's DLC art book, theme gallery and editor's notes in English; DLC
  icons redrawn; a smudged second-game DLC score sheet fixed.
- v1.6: Capcom's own shout graphics and more of its textures; the second game's official
  logo.
- v1.5: the click at the end of replaced voice lines covered with silence; two cramped
  second-game
  menus; the second game's patch now outranks Capcom's own update.
- v1.4: first hardware playthrough of the DLC stories; second-game dialogue no longer
  cut off under the page arrow; more English voices; English HOME icon and banner.
- v1.3: the v1.2 fix carried to the second game and its DLC; over-long evidence pop-ups
  shortened.
- v1.2: first-game cross-examination statements no longer run into the box edge; typos
  fixed.
- v1.1: Capcom's real logos, evidence card names, deduction plates and ending card; real
  version numbers; spellings.
- v1.0: first public release: Capcom's English text on both games and their DLC over
  senyarom's patch, plus English DLC voice clips, subtitled commentary videos, magazine
  covers, refitted captions and readable second-game menus.

## Known problems

- Some lines are still spoken in Japanese because Capcom never recorded English for them:
  four courtroom shouts, two "Take that!" shouts in the second game's DLC and a run of
  story lines.
- The second game's end credits are Japanese on purpose; a misspelled credit is worse than
  an untranslated one.
- Some text still runs past its box: a few dozen second-game dialogue pages end under the
  page arrow, one first-game single-word page and three widget pages sit on the edge, and
  two lines in the fancier
  face end slightly under the arrow.
- The English manual's screenshots and some of its headings are still the older fan
  translation's, so a few show older names and menu words.
- Japanese remains in the first game's DLC Picture Book (name tags, production scribbles).
- Nobody has played either main game through on a console yet. The cutscene grain fix
  hasn't been heard on a 3DS, and the English lines added to the second game's last two
  episodes, and the crowd loops, were checked offline only. The first game's new staff
  credits are at the end of the game and haven't been seen on screen yet. The "shing" mixed
  back under the English shouts hasn't been heard on a 3DS, and the re-broken Present and
  Examine questions haven't been seen on screen. The English manual hasn't been opened on a 3DS.

The full account of what has and hasn't been checked is in TESTING.md.

## Files

Per game, on the release page:

- `TGAA1-base-3.4.0.cia` / `TGAA2-base-1.0.30.cia`: the update, with the English manual in it.
- `TGAA1-DLC-1.0.23.cia` / `TGAA2-DLC-1.0.17.cia`: the DLC. `TGAA1-EN-DLC-v1.9m.cia` /
  `TGAA2-EN-DLC-v1.9n.cia`: the same DLC decrypted inside, for emulators. One or the
  other, not both. Neither game's DLC changed in v1.9o, so they keep their names.
- `TGAA1-3DS-English-v1.9o-xdelta.zip` / `TGAA2-3DS-English-v1.9o-xdelta.zip`: both as
  xdelta patches against your own decrypted dump, with the banner patch inside the zip
  (`TGAA1-v1.9o-base.xdelta` / `TGAA2-v1.9o-base.xdelta`, the same file as the posted
  `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta`) and a readme (`README.txt`
  inside the zip, also posted on its own as `TGAA1-README-v1.9o.txt` /
  `TGAA2-README-v1.9o.txt`).
- `TGAA1-3DS-English-JPvoice-v1.9o-xdelta.zip` / `TGAA2-3DS-English-JPvoice-v1.9o-xdelta.zip`:
  the Japanese-voice edition, same text and art, all audio Capcom's Japanese.
- `HASHES_v1.9o.txt`: size, CRC32 and sha256 of the English xdelta sources, patches and
  results.

The result hashes are in `HASHES_v1.9o.txt` and in the readme inside each zip. Your own
source dump won't hash-match mine, and that's expected.

## Credits

senyarom's layout pipeline, font handling and port of Capcom's script onto the 3DS builds
are what this patch starts from, building on Scarlet Study and Fan Translators
International's earlier English builds. The English manual's text is Scarlet Study's,
revised for this patch. The logos, evidence cards,
shout lettering and voices are Capcom's, from Chronicles. Full credits are in the README.

The Great Ace Attorney and Chronicles are (c) Capcom.

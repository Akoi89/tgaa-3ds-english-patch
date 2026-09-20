# The Great Ace Attorney 3DS patch: the detail

Everything the README used to carry inline, plus the reasoning and the sources behind every
figure in it.

---

## Something looks wrong. Is it known?

Start here. This is everything I know about that you might actually notice while playing,
sorted by what it looks like on screen rather than by which job it came out of. The rest of
this document is a record of the work, which is a different thing and not much use for
looking something up.

If what you're seeing isn't on this list, please tell me about it in
[issue #1](../../issues/1). If it is on this list, I still don't mind hearing about it, and
I'd much rather have a duplicate than miss something.

| What you're seeing or hearing | Where | What it is |
|---|---|---|
| A line is spoken in Japanese while the text is English | both games, story scenes | 54 lines have no English recording at all. Capcom never made one, and that was checked exhaustively rather than assumed |
| The same, on a line that feels like it should exist | both games, story scenes | 18 more have an English take that runs 1.4x to 3x longer than the slot the 3DS streams it from. Fitting it would mean a rushed delivery or cut words, and neither is worth it |
| An *Objection!* or *Hold it!* comes out in Japanese | second game, two minor characters | 4 shouts Capcom never re-recorded, for `chr104_mrs` and `chr210_mmm`. Their archives were checked member by member: 100 of the 104 shouts have an English master, these four don't |
| A gallery chant is in Japanese | second game | 1 chant whose English is 8.9 seconds against a 5.05 second slot, which would need the rate cut to 57% |
| No narration plays over an episode opening | second game, two pages | The display window on those two pages is shorter than Capcom's own audio, so the Japanese never played there either |
| Narration cuts mid-word with a short fade | second game, three splits | The English takes span two pages each and had to be split. A clean break exists for all three but only at around 65% quality, which is more noticeable than the seam |
| One voice clip sounds duller than the rest | first game's DLC | Deliberate. The rate was lowered so the complete take would fit rather than losing the end of the line |
| The last word or two of a page sits under the page arrow | second game, 38 pages | 13 are a single scream that overflows in Japanese too, and 25 end without a wait marker, so they can't be split without inventing a pause Capcom didn't write |
| A centred banner or heading looks tight against the box edge | first game, 4 pages | One single-word page at 357 units and three identical widget pages at exactly 365. The widget box's own width was never confirmed on screen, so these may not be overflowing at all |
| A line in the fancier, more decorative face runs past the box | first game | The wrapper measures those lines with the other font's metrics, so it wraps them too late. This is [senyarom issue #7](https://github.com/senyarom/tgaa2-en-patch/issues/7), it is still open, and it is not fixed here either |
| The end credits are entirely in Japanese | second game, all 75 cards | Deliberate. The PC release lays them out differently and can't be ported, and a misspelled credit is worse than an untranslated one |
| Japanese writing on the artwork inside the Picture Book | first game's DLC | Brush-written name tags and small production scribbles on the design sheets were left as they are |
| The tips of the pencil hair look clipped on a sketches page | first game's DLC, issue 6 | They share pixels with the Japanese writing. Every rule that kept the hair also left readable Japanese, so the tips stay clipped |
| The title card reads "D L C", one letter per slot | first game | Cosmetic, and it used to be blank |
| A Court Record profile or caption is drawn small and soft, and thin strokes drop out | both games | The panel shrinks the type rather than clipping it when a caption is too long, so this is what a caption that doesn't fit looks like. A lot of them were rewritten to fit at full size, but that work was done caption by caption and it is NOT a guarantee that none are left. If you're looking at one now, I want to know which character |
| A full-screen document or report page has text running off the edge | first game | Reported on hardware in September 2026 and being looked at now. It is a different text box from ordinary dialogue and it was never measured on screen, so I don't yet know how many pages are affected. Not fixed, and worth reporting with a photo if you hit one |
| A crackle or buzz over the voice in the opening video | first game | Reported on hardware and UNEXPLAINED. The movie file is the same one three separate builds ship and it carries no audio track at all, so the noise is coming from somewhere else and I have not found it. A phone recording of it is the most useful thing anyone could send me |

**Not on this list and worth knowing:** nobody has played either main game the whole way
through on a console. 32 of the first game's shouts, the jury verdicts and the pressing
voices, have never been heard by anyone in any build on any platform. If you play the first
game, a verdict or a press that stops part way is the single most useful thing to listen
for. The full picture is in the testing status table further down.

---

The first game's number jumped from `1.0.19` to `3.2.1` in v1.4. That is not nineteen
missed releases. The 3DS stores a title version in a field whose last part cannot go
above 15, so `1.0.16` and up were never real versions: the files were named `1.0.x`
while the console was told something else, and the two had drifted apart. From v1.4
the first game's number on the screen, in the filename and in the console are the same
number. The second game keeps `1.0.x` on screen and in the filename, but from v1.5 the
console is told `3.x`, for the reason in the box above: Capcom's own update for it is
`1.3.0`, and a lower number is what made consoles offer that update over the patch. v1.5
was `3.0.15` to the console; v1.6 is `3.1.0`, because the last part cannot go above 15.

Both title screens now show Capcom's own *Adventures* and *Resolve* logos instead of the
fan-drawn ones, so the logo alone tells you the update took. If you want a text check as
well: in the first game's opening cross-examination the first statement should read *"I
was ingesting regulation beef steak at the restaurant in tactical discussion with the old
man."* on **two** lines. Three lines with the third cut off means the update did not
install.

---

## What this adds on top of senyarom's patch

**What is theirs:** the layout pipeline, the font handling, and the carry of Capcom's
official *script* onto the Japanese 3DS builds. That is the foundation, and it is the hard
part of the problem. Nothing here replaces any of it.

**What is here:** senyarom's patch brings Capcom's text across. This brings across the
rest of what Capcom made, the parts that are not text at all: the English voice acting,
the videos, and the art. On top of that, the DLC that nothing had ever translated, and the
layout bugs that only turn up by playing.

### 1. The DLC, which no English release had ever covered

Every previous effort stops at the base games. Scarlet Study's translation and senyarom's
patch both leave the DLC in Japanese. Even the mod that ports the 3DS DLC across to the
Steam release says in its own readme that the mini-cases are untranslated, and that no
text will be displayed during them at all.

So this is the part that did not exist anywhere before:

| | |
|---|---|
| **2** | mini-episodes in the second game, fully translated and playable |
| **46** | gallery voice clips in the first game's DLC, in Capcom's English rather than Japanese |
| **34** | shouts in those mini-episodes, which had been speaking Japanese over English text |
| **11** | commentary videos in the first game's DLC, subtitled and re-encoded to Capcom's own container spec |
| **14** | magazine covers in the first game's DLC: 9 rebuilt from the official *Chronicles* banner art, 5 relabelled so you can tell the empty issues from the playable one |
| **3** | DLC banners and the icon labels redrawn; the two story banners re-titled on new artwork (v1.4) |
| **4** | event pictures in the second game's DLC that were still Japanese: the opening "work of fiction" card and a handwritten score sheet in three views, re-typeset in English at the photograph's own angle and focus (v1.4); the score sheet's paper cleaned of a dark band and leftover brush specks (v1.7) |
| **76** | pages in the first game's DLC that were still Japanese images: 66 Picture Book pages of the art director's commentary with the handwritten notes on the design sheets, 8 theme preview titles and 2 Editor's Notes pages, all now in English (v1.7, see below) |
| **29** | of those Picture Book pages where the commentary sits on a see-through panel over the artwork, redone so the artwork under and around the panel is Capcom's own rather than a blurred repaint (v1.8, see below) |
| **1** | DLC list icon sheet redrawn from Capcom's Japanese plate, because the earlier English sheet cut off the bottom of all 18 icons; the Episode 0 cover and the five empty-issue covers got a cleaner fill behind their titles (v1.7) |

**The playable sample was translated by hand.** The first game's DLC magazine carries a
playable demo as issue No. 13: Episode 1's opening, the Court Record tutorial and a
cross-examination, around **11,300 characters across five script files**. No patch had
translated it. It was done from the Japanese by hand for this release, and it is the one
part of this project that is an original translation rather than a port of Capcom's work.
Issues 9 to 12 turned out to be empty stubs that open and immediately exit, so their
covers are now labelled as such and No. 13 is labelled as the playable one.

**The Picture Book, theme titles and Editor's Notes are new translations too (v1.7).** Their
buttons used to throw you back to the title, so nobody had seen them in English; once they
opened, every page turned out to be a Japanese image. *Chronicles* has no Picture Book, so
there was nothing of Capcom's to port. The English was translated from the Japanese with
Claude's help, reviewed against a second model, and every character name checked against
Capcom's spelling. The commentary is set in one condensed sans serif, the handwritten notes
in a handwriting face, the theme titles in the serif of the Japanese titles. On the 29
pages where the Japanese sat on a see-through panel over the artwork, the covered part of
the art was filled in with an image inpainting model (LaMa) and only those pixels were
changed; everywhere else the page is Capcom's image untouched. Brush-written name tags and
tiny production scribbles on the sketches were left in Japanese.

**Those 29 pages were redone in v1.8, and no model paints them any more.** The mask grown
around each Japanese character ended up covering about three quarters of the panel, because
the characters sit two to four pixels apart and the mask closed the gaps between them, so
the inpainting model was repainting the whole panel and inventing the picture behind it.
That showed as a smeared band along the top of each panel and as characters' legs turned
into pale smudges. Nothing is repainted now. What the panel looks like without the writing
is estimated from the pixels that are not writing, and each pixel is faded towards that
estimate in proportion to how much darker than it it is, so the ink lifts out and the
drawing stays. The English also sits on the row Capcom's Japanese started on rather than a
few rows lower, which is what left the pale band. Every row above the first line of text on
those pages is now byte-identical to Capcom's own page. One page is still not right: on the
rough sketches page in issue 6 the tips of the pencil hair share pixels with the writing,
and every rule that kept the hair also left readable Japanese, so the tips stay clipped.

**Why the buttons bounced.** The DLC screen checks a DLC status byte before it opens the
Picture Book, Theme or Editor's Notes, and turns back to the title if the byte isn't zero.
Traced live in an emulator, the byte read 5, set by a background DLC request that comes back
with an error code. senyarom's offline DLC patch skips that check in the two places the rest
of the DLC list goes through; the same check sits in three more places, and those are the
ones these three screens use. v1.7 skips it there the same way: three branch instructions
in the update's code, nothing else. Capcom's Japanese update has the same code in this
area, so the check itself is Capcom's; as far as I can tell it only trips when the DLC
runs without Nintendo's servers behind it.

**And where Capcom localised a piece of the DLC, this matches Capcom word for word.** One
scene exists in *Chronicles* as official English, which makes an exact check possible:
comparing box by box, **140 of 190 are byte-identical**, and every remaining difference is
either a line wrapped to fit the narrower 3DS box or a curly quote the 3DS font does not
carry. Not a paraphrase of the official text. The official text.

### 2. English voices, in both base games as well as the DLC

Capcom re-recorded the whole cast for *Chronicles*. senyarom's patch is a text port, so
none of those recordings came across: both games still shouted in Japanese over English
text, all the way through the main story.

| | |
|---|---|
| **81** | courtroom shouts in the first game, now Capcom's English, across 41 replaced character archives |
| **25** | story voice clips in the first game |
| **85** | courtroom shouts in the second game |
| **235** | story voice clips in the second game |
| **46** | gallery voice clips in the first game's DLC |
| **34** | shouts in the second game's DLC mini-episodes |
| **7** | animated cutscenes in the first game |
| **20** | narration slots across the first game's episode openings |
| **20** | courtroom crowd and reaction voices in the second game that Capcom recorded in English and no build had ever used: six streamed gallery and courtroom cues, and fourteen gasps, efforts and cries during the third episode's Dance of Deduction (v1.4) |
| **6** | the same six courtroom cues in the first game (v1.4) |

Those 26 had been invisible to every earlier audit for a reason worth writing down:
Capcom tags only the English file (`_eng`) and leaves the Japanese one untagged, so a
search for a Japanese twin found nothing and concluded the English was an orphan. A
whole-install count of all 526 English audio files in *Chronicles* against the four
builds is what found them.

**Pauses, not fidelity, pay for the fit.** A streamed clip has to fit Capcom's slot in
bytes, and bytes scale with duration times sample rate. Where an English take runs long,
the silence *between phrases* is shortened rather than the sample rate lowered, so the
speech itself is untouched. 24 clips that previously had to drop as low as 75% of full
rate now play at a higher one, 17 of them at full, and 3 lines that were left in
Japanese are now English. Pauses are never cut below 150 ms: shorter than that swallows
the breath marks in a fast delivery and the read sounds spliced, which was confirmed by
listening rather than assumed.

**The second game was the gap, and it is now closed.** It shipped with ten English clips
covering two characters, while every other voice in it, shouts and story lines alike,
stayed Japanese over English text. There were two separate systems to fix and finding the
second one took someone playing the game and asking why a character sounded wrong.

What is still Japanese, and why:

| | |
|---|---|
| **54** | Capcom never recorded an English take. Verified exhaustively rather than assumed: *Chronicles* ships 288 English voice files and every one of them matches a 3DS clip name, with none left over, so there is no alternate naming convention hiding a recording. |
| **18** | An English take exists but runs 1.4x to 3x longer than the 3DS slot. Shortening the pauses and lowering the rate together cannot close that without the delivery sounding rushed, and a mangled English line is worse than a clean Japanese one. Words were never cut to make something fit. |
| **4** | Courtroom shouts for two minor characters, an *Objection!* and a *Hold it!* each, that Capcom never re-recorded in English. Their archives were checked member by member: 104 shouts live inside the character archives, 100 have a *Chronicles* master, these four do not. |
| **1** | A second gallery chant in the second game. Capcom's English is 8.9 seconds of speech against a 5.05 second slot, which would need the rate cut to 57%, far below the 75% floor. It stays Japanese (v1.4). |


The episode openings needed their own approach. Capcom re-recorded the narration for
English in ten takes where the Japanese has twenty lines, so one English take spans two
of the game's pages, and each page has a fixed display window that cuts anything longer.
Lowering the sample rate shrinks a file without shortening it, so the takes are split at
the sentence break and time-compressed with the pitch preserved. Two pages turn out to
have a window shorter than Capcom's own audio, which is why their Japanese never plays
either.

Three splits land mid-word and carry a short fade. A clean break exists for each, but
only by pushing a half to around 65% of full quality, which is more noticeable than the
seam it would fix.

If you play the second game and hear Japanese where you expected English, that is this,
and it is expected rather than a broken install.

Getting the DLC's clips to play was the harder half. They came out silent or truncated,
and the reason was not obvious:

**A voice stream larger than Capcom's original is cut off in-game, and not at the
original's length.** It stops at an unpredictable point, and how far it overshoots does not
predict where it stops. Measured by metering the speaker, not by reading the file:

| our clip | Capcom's slot | actually played |
|---|---|---|
| 4.10s | 3.81s, over by 0.29s | **0.98s** |
| 4.47s | 3.91s, over by 0.56s | **1.86s** |
| 5.44s | 3.32s, over by 2.12s | **2.77s** |
| 9.04s | 9.18s, fits | full |
| 4.60s | 4.69s, fits | full |

Eighteen streams were oversized, because Capcom's English performances simply run longer
than the Japanese ones they replace. Trimming to fit would have cut words, over two seconds
off one line. Instead the space was bought: edge silence trimmed but never the pauses
inside a line, and where that was not enough, the sample rate lowered just far enough for
the **complete** take to fit. The game honours the rate field, so pitch and timing are
unchanged and the cost is treble rather than words.

Eleven of seventeen kept 90% or more of full rate. **One clip is noticeably duller.** That
is deliberate, and it is the alternative to losing the end of the line.

**The pop at the end of shouts (found v1.4, fixed v1.5).** The hardware tester heard a
click at the end of some shouts in the second game's DLC. v1.4 gave every imported clip
a fade and a silent tail like Capcom's, which was correct but was not the cause: the
tester still heard it. A recording of the click, made on a second console and lined up
against the clip, put it about ten milliseconds after the clip's last sample, and the
one structural difference left was this: every voice file Capcom ships ends in a zero
trailer that rounds its length to a multiple of 32 bytes, and every clip this project or
senyarom had written was 8 bytes past that boundary with no trailer. A console reads the
last 32-byte unit past the end of the file and plays whatever it finds there. An
emulator reads exact sizes and never hears it. The trailer is now on every replaced
stream: 89 in the second game's DLC, 130 in the second game and 123 in the first, which
means the base games had been clicking on hardware since the first release and nobody
had played them there to know. The first game's DLC was already aligned. A second
recording on the same console, same shout, same spot, shows nothing at the clip's end.
The recording also showed which file the DLC's scripted shouts play: the base game's
copy, not the DLC's own, which is why fixing the DLC alone had changed nothing.

### 3. Text that fits the box, and a font that behaves

Most of the work after the DLC was layout, and most of it is in the **story text**, not
the Court Record: dialogue running past the edge of its box, glyphs colliding, captions
rendering soft, menus in the wrong face.

| | |
|---|---|
| **164** | Court Record captions across both games (68 and 96) rewritten to fit at full size. The panel silently shrinks its font rather than clipping, so long captions rendered small and soft instead of looking broken |
| **1,438** | pages of story dialogue re-broken at the corrected font metrics, which added 124 pages of pagination. Includes the centred pages that overran the box, some running clean off the screen |
| **43** | glyph advances corrected in the second game's dialogue font, including a tuck for overhanging T, Y and L. This affects every line of text in the game, not one screen |
| **0** | end-credit cards in the second game. 15 were briefly English; they were reverted so all 75 are Japanese, because a translated block sitting inside an untranslated roll reads as a bug. See known issues |
| **42** | menu strings in the second game that fell through to a decorative script and were genuinely hard to read: Yes/No, OK, Cancel, Examine, Move, Converse, Present, every game-over option |
| **19** | voice clips in the first game's DLC cut off mid-word, per the section above |
| **202** | cross-examination statements re-laid to the statement box's real width: 65 in the first game (v1.2), 133 in the second and 4 in its DLC (v1.3). That box is narrower than the dialogue box, because the arrows that step between statements sit inside it, and every earlier build had laid statements out against the wider measurement, so the longest lines ended on the border with their last character cut. 17 only needed a new line break; 48 were shortened by the smallest edit that fits, checked against the Japanese. Found by watching Episode 1 played on the patched build, screen by screen; the second game's box was measured in-game with its own font before anything was changed |
| **16** | evidence and profile descriptions in the second game that the evidence pop-up card drew oversize and cut off. They carried a size tag the Court Record panel honours and the pop-up does not; shortened to fit at normal size in both (v1.3) |
| **1** | save/load screen drawing the timestamp straight through the episode title |
| **1** | pagination regression that had inflated the script by 6,855 pages |
| **1,635** | page breaks the translators had added that Capcom's Japanese does not have, joined back into one page now that the real box width is known (v1.4): 26 in the second game's DLC, 114 in the first game's DLC, 1,493 in the first game, 2 in the second. A break was only undone where nothing but the standard page tags sat on it and the joined words fit two lines with room to spare; the rest, where the English is genuinely too long for one page, stay split |
| **62** | of the 66 centred banners, sized text and other widget pages in the first game that ran past the box edge, up to 404 units against a 365 box: 43 re-broken, 19 split into two pages (v1.4). The 4 left alone are one single-word page measuring 357 units (`_sce01_c005_0007`, L_3D_SEARCH_0_PRES page 22) and three identical widget pages measuring exactly 365 (`_sce03_c004_0004` L_2_START and L_2_REPEAT_1, `_sce03_c004_0007` L_UPDATE_1, page 6 of each). The widget box's own width was never confirmed on screen, so those three may not be running past anything; none of the four has been seen clipping on a console |
| **9** | lines in the second game's DLC that ran off the page, found by the hardware tester, re-split or re-wrapped without changing a word, one of them a case document taken from 384 to 336 units; plus three hand-placed breaks Capcom had put inside a decorative script restored, and one page that had grown to three lines split in two (v1.4) |
| **1** | profile caption in the second game's DLC that was five lines in a four-line box, so the game shrank it and thin strokes dropped out; condensed to four (v1.4) |
| **1** | save-slot title in the second game, Episode 1's, the longest of the five, that ran off the slot's right edge on a console; the "Ep. 1:" label is now drawn a step smaller so the title fits at its normal size, and the chapter line under it, which the game was squeezing to fit, now renders one size down and unsquashed. Seen on screen (v1.5) |
| **2** | system messages in the second game, the return-to-title confirmation and its game-over twin, whose longest lines were the two widest of any dialog in the game, so the box squeezed the whole message sideways until the apostrophe vanished; re-broken onto four and three lines, no words changed. Not yet seen on screen, see the status table (v1.5) |
| **7,320** | of the 7,358 pages of ordinary dialogue in the second game that ran under the page-advance arrow (v1.4). The whole game had been wrapped to the edge of the box, 365 units, when the arrow that ends every line sits at 345, so the last word of every long line was drawn under it. Measured on the game's own font and calibrated on screen before anything moved: 344 units touches the arrow, 351 passes it. 5,828 pages only needed their line break moved, 716 single lines became two, and 776 pages that cannot fit two lines at all were split into two pages the way Capcom's own continuation pages are built. Words were never changed, and every event and animation marker in all 8,117 script entries is proven to be in its original place. 38 pages are left alone: 13 are a single scream that overflows in Japanese too, and 25 end without a wait marker, so they cannot be split without inventing a pause Capcom did not write |

The scale of that is easy to understate. Diffing these builds against senyarom's release
file by file, **854 script files differ across the four builds**: 363 in the first game,
431 in the second, 60 across the two DLCs. That is not 854 separate translations, and it
should not be read as one. It is the font-metric and reflow work rewriting line breaks
through nearly every script in both games, which is why it had to be null-tested rather
than eyeballed.

Every one of these was found by a person looking at a screen or listening to a speaker.
**None were found by an offline check**. The automated audit passed a build in which one
line was silent and another was cut in half, and it did so because a path comparison
silently matched nothing. That is why this release asks for playtesters rather than for
more tooling, and why the testing status below is written the way it is.

### 4. Capcom's art where the patch had redrawn its own

The *Chronicles* release carries English versions of most of the textures that have words
on them, and where one exists it now replaces the fan-drawn one, so what is painted on
screen agrees with what the dialogue says.

| | |
|---|---|
| **2** | title logos, Capcom's official *Adventures* and *Resolve* marks in colour, replacing hand-drawn ones that still read "Ryuunosuke Naruhodou" |
| **9** | evidence cards (maps, pawn tickets, a contract; 12 textures counting the large variants) that carried fan-translation names such as "Hatch's Pawnbrokers" and "The Ragged Reader" while the text said Windibank's and Bourbon Books. Now Capcom's cards, with the red map markers restored from the Japanese originals |
| **1** | end card in the first game, which was still Japanese: now Capcom's "The Great Ace Attorney, Adventures, FIN" |
| **168** | Dance of Deduction topic plates re-rendered with Capcom's wording (74 in the first game, 94 of 104 in the second, matched through the game's own hit tables). Two plates in the second game had never been translated at all and were still Japanese; one whole stamp atlas the fan patch had missed now has English stamps |
| **1** | evidence card for Madame Tusspells, which carried a different name |
| **2** | title screens showing their real version number, and a "D L C" label on the title card that was blank |
| **1** | Japanese anti-piracy notice on the first game's boot, now blank exactly as the second game already shipped |
| **1** | HOME menu icon for the first game, which showed the Scarlet Study pipe logo; now the cartridge's own picture, with the English title text kept (v1.4) |
| **8** | shout atlases, the big lettering that flashes on a shout, now Capcom's *Chronicles* atlases converted to the exact format of Capcom's Japanese 3DS files, in both games. The fan set both games had shipped left the rotated second variant of the two British-court atlases in Japanese, and the first game draws that variant. Two words change to Capcom's wording with it: "Yes!" for "Sir!", "'Scuse me!" for "Hang on!" (v1.6) |
| **15** | textures Capcom localised for *Chronicles* that no 3DS patch had used: the second game's last chapter title card, and text painted onto character costumes, evidence objects and two backgrounds in both games (6 in the first, 9 in the second). Found by cross-referencing every English texture in *Chronicles* against the two cartridges; each was ported in its 3DS format with only the changed blocks re-encoded, with a base-colour-searching ETC1 encoder, the rest of every texture staying Capcom's own bytes. Still unported, on purpose: the handwritten narration strokes in the episode openings (40 textures whose alpha carries stroke timing the PC files lack), two evidence textures whose PC format does not decode reliably, and one item that is Russian on both platforms (v1.6) |

These were found by decoding every texture Capcom localised for *Chronicles* and looking
at each one next to the 3DS build, rather than trusting filenames.

### 5. What was sent back upstream

**Both bugs that other people had reported on senyarom's tracker are fixed here:**

- **[#1](https://github.com/senyarom/tgaa2-en-patch/issues/1)**: text stretching outside
  the box and off the screen in the first game's Episode 4. Traced to a centred page in
  `_sce03_c000_0003`, and fixed by the reflow work above.
- **[#2](https://github.com/senyarom/tgaa2-en-patch/issues/2)**: the second game's DLC
  episodes showing blank character names, with every dialogue choice reading as invalid.

Two pull requests went back to senyarom rather than being kept here:
**[#3](https://github.com/senyarom/tgaa2-en-patch/pull/3)** reflows centred pages that
overflow the box, and **[#4](https://github.com/senyarom/tgaa2-en-patch/pull/4)** stops
adapted advances running into the next glyph.

Three further issues were filed there. **[#6](https://github.com/senyarom/tgaa2-en-patch/issues/6)**
(the first game's DLC Picture Book and Theme buttons bouncing to the title) is fixed here
from v1.7, as described above. Two **remain unfixed**, in this build and upstream:
**[#5](https://github.com/senyarom/tgaa2-en-patch/issues/5)** (the second game's Japanese
end credits) and **[#7](https://github.com/senyarom/tgaa2-en-patch/issues/7)** (40 lines in
the first game set in the serif face that overrun the box, because the wrapper measures
them with the other font's metrics). The first appears in the known issues below. They are
listed here because a contribution section that only lists wins is not worth much.

---

## Testing status

Moved to its own page: [TESTING.md](TESTING.md) says what has been played, watched and
listened to, and what has only been checked in the files.

---

## Patch files

From v1.5 each release also carries one zip per game, `TGAA1-3DS-English-v1.8a-xdelta.zip`
and `TGAA2-3DS-English-v1.8a-xdelta.zip`, holding three xdelta3 patches that apply to files
you make from your own Japanese dumps with Batch CIA 3DS Decryptor:

| patch | applies to | produces |
|---|---|---|
| `-update.xdelta` | your decrypted game `.cci` | the update CIA, byte for byte the one in rows 2 above |
| `-DLC.xdelta` | your decrypted DLC `.cia` | the DLC CIA, same contents as row 3, stored unencrypted |
| `-base.xdelta` | your decrypted game `.cci` | the same game with the English HOME banner, as above |

The zip has xdelta3.exe and a readme with the exact commands, the sizes to expect and the
output hashes. The decryptor writes a few random bytes into every file it makes, so your
source will not hash-match the readme's and the patches are built so that does not
matter; the outputs must match exactly. The update patch is 27 to 35 MB because most of
the update is files that already exist in the game image; the first game's DLC patch is
about 180 MB because the subtitled videos are genuinely new data. The patches were proven
on the `.cci` the decryptor writes from a CIA of the game; a raw `.3ds` cartridge dump has
not been tested. Same install order afterwards: base, update, DLC.

The same readme text is also on the release on its own, as `TGAA1-README-v1.8.txt` and
`TGAA2-README-v1.8.txt`, because romhacking.net wants the readme as a separate link rather
than only inside the zip.

The CIAs stay on the release because they are what the hardware testing was done on, and
because a patch against a file most people dump differently is a support thread waiting
to happen.

## Japanese voice edition

Some people want Capcom's English text over the original Japanese cast. From v1.5 the
release also carries `TGAA1-3DS-English-JPvoice-v1.8a-xdelta.zip` and
`TGAA2-3DS-English-JPvoice-v1.8a-xdelta.zip`: the same three patches as the zips above,
producing the same update and DLC with one difference. Every audio file is Capcom's
Japanese original, taken from the cartridge and the Japanese DLC: the courtroom shouts,
the story lines, the narration, the crowd cues and the DLC voices. Text, art and layout are
byte for byte the main release, and that was checked file by file rather than assumed:
everything outside the sound files and the character archives is identical, and every
reverted file equals the Japanese one. The first game's banner patch in that zip also keeps
the Japanese HOME menu jingle, which the main release's banner replaces.

The edition declares the same title versions as the main release, so install one or the
other, not both; the title screens read the same `ENG` stamps. Both games and their DLC were
installed and run before posting. The build and its check are `jpvoice/` in the tools.

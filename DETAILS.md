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
| The same, on a line that feels like it should exist | both games, story scenes | FIXED in v1.9. 18 lines had been left in Japanese because Capcom's English take was longer than the Japanese one and a longer clip was believed to get cut off. That cut-off was the misplacement bug described under the cutscene grain: a clip written where the game actually reads it plays to the end whatever its length. All 18 now play Capcom's English. One line in each game was heard in-game; the rest were checked against the recordings offline, and the ones in the second game's last two episodes have not been reached on a console |
| An *Objection!* or *Hold it!* comes out in Japanese | second game, two minor characters | 4 shouts Capcom never re-recorded, for `chr104_mrs` and `chr210_mmm`. Their archives were checked member by member: 100 of the 104 shouts have an English master, these four don't |
| A gallery chant is in Japanese | second game | FIXED in v1.9. The one chant that had stayed Japanese, in Episode 5, was held back because Capcom's English is much longer than the Japanese and a longer clip was believed to get cut off. That was the misplacement bug, not a size limit, so it plays Capcom's English now, at full length and looped where Capcom's recording says. Checked on the PC only; the test save doesn't reach it, so a report from anyone who hears it in-game would help |
| No narration plays on two pages of an episode opening | first game, Episode 2 | FIXED in v1.9. Those two English lines used to be cut to fit a timer set for the Japanese takes; they play in full now. Heard in-game |
| Narration cuts mid-word with a short fade | first game, Episode 2 opening, three places | FIXED in v1.9a. Each page's English plays as two halves, and three of the splits fell inside a word because the clean break used to cost about a third of the audio quality to fit a size limit that turned out to be my own bug. All three now split in a real pause, at full quality. Heard in-game |
| A DLC voice clip sounds duller than the rest, or stops before the line is finished | first game's DLC | FIXED in v1.9. The quality had been lowered on 16 lines, and 3 more trimmed, to keep each clip inside the space Capcom's Japanese clip took, because a bigger clip was cut off in-game. The cut-off was the misplacement bug, not a size rule, so all 19 are re-encoded at full quality and full length. Every one was heard playing to the end on a console |
| A voice line in the second game sounds hurried, with the breath between phrases missing | second game, story scenes | FIXED in v1.9. 27 lines had pauses cut out of the middle to make them fit the space, a workaround for the same misplacement bug. The pauses are back, and every second-game voice that had been stored at reduced quality for the same reason is at full quality again: a scan of the finished build found no replaced voice below Capcom's sample rate in either game or either DLC |
| The parchment narration at the start of Episode 2 sounds rushed, or pauses in the middle of a sentence | first game | FIXED in v1.9 and v1.9a. Each page of that opening had been timed for the Japanese takes, and the longer English takes had been sped up, by up to about a third, to finish in time. v1.9 restored the natural pace, but each page's English is in two pieces and the second piece still waited on the cue for the Japanese second line, which left pauses of half a second to over a second on five pages, three of them mid-sentence or mid-word, while two pages felt rushed. v1.9a times each page the way Capcom's PC release does: one continuous read per page, the second piece following the first after the recording's own pause, with the page turns, art and music on Capcom's original timing. Heard in-game: nothing is cut off and nothing overlaps |
| A gasp, effort or cry during the third episode's Dance of Deduction sounds distorted | second game | FIXED in v1.9. Those 14 reactions went through a converter of mine that read part of the source format wrong. Fixed at source; they now decode exactly like the reference decoder. Checked by decoding, not yet heard in the scene |
| A DLC Music and Sound gallery title runs past its plate | first game's DLC, issues 1 to 8 | FIXED in v1.9 |
| A "Bonus voice recital" track in the DLC Music gallery plays in Japanese | first game's DLC | FIXED in v1.9 for four of the eight. Capcom's English recordings exist for them and are in now, checked on the rig |
| A lowercase t looks broken, or "Picture" reads "Picturc", on a DLC menu heading | first game's DLC menus (the same letters in the second game) | FIXED in v1.9b, redone in v1.9c. The headings use the fan patch's menu font, whose t and e crossbars are one pixel thin; the game draws the headings slightly shrunk and smoothed, and the thin bars vanished. v1.9b thickened both letters but pushed their bottoms a pixel below the line, so the e grew a small tail in lists and dialogue. From v1.9c only the crossbars get a light extra row, and the i, j and l, which read a shade heavier than their neighbours, are slightly lighter. Nothing else in the font moved. Checked on the emulator in the Sound gallery, the DLC headings and the music notes |
| A closing quote mark or a punctuation mark shows as a blank space | first game and its DLC | FIXED in v1.9. A handful of characters, mostly curly closing quotes in the DLC gallery text plus a few punctuation marks in the first game's own text, aren't in any of the game's fonts. Replaced with characters the fonts do carry |
| A "Take that!" comes out in Japanese | second game's DLC, two shouts | No English recording exists for these two. Same class as the four base-game shouts above |
| The gallery text for DLC issues 9 to 13 is Japanese | first game's DLC | Capcom's own placeholder wording, as far as I can tell; the retail Japanese game shows the same. Whether to translate it is undecided |
| The last word or two of a page sits under the page arrow | second game, 38 pages | 13 are a single scream that overflows in Japanese too, and 25 end without a wait marker, so they can't be split without inventing a pause Capcom didn't write |
| A centred banner or heading looks tight against the box edge | first game, 4 pages | One single-word page at 357 units and three identical widget pages at exactly 365. The widget box's own width was never confirmed on screen, so these may not be overflowing at all |
| A line in the fancier, more decorative face runs past the box | first game | The wrapper measures those lines with the other font's metrics, so it wraps them too late. This is [senyarom issue #7](https://github.com/senyarom/tgaa2-en-patch/issues/7), it is still open, and it is not fixed here either |
| The end credits are entirely in Japanese | second game, all 75 cards | Deliberate. The PC release lays them out differently and can't be ported, and a misspelled credit is worse than an untranslated one |
| The DLC menu icons have smudges under the pictures | first game's DLC list | FIXED in v1.9c. The clean icon sheet from v1.7 was replaced by the older one again in v1.8b, because that update was built from a copy of the game files that still held it. The v1.7 sheet is back |
| Picture Book commentary is hard to read at its size | first game's DLC | FIXED in v1.9c on 51 of the 76 pages: the text is usually two sizes bigger, with the see-through panel behind it extended to fit, and faint Japanese that showed behind the English on several pages is gone. The other pages were already as large as their space allows |
| Japanese writing on the artwork inside the Picture Book | first game's DLC | Brush-written name tags and small production scribbles on the design sheets were left as they are |
| The tips of the pencil hair look clipped on a sketches page | first game's DLC, issue 6 | They share pixels with the Japanese writing. Every rule that kept the hair also left readable Japanese, so the tips stay clipped |
| The title card reads "D L C", one letter per slot | first game | Cosmetic, and it used to be blank |
| A Court Record profile or caption is drawn small and soft, and thin strokes drop out | both games | The panel shrinks the type rather than clipping it when a caption is too long, so this is what a caption that doesn't fit looks like. FIXED in v1.9 for the first game: every one of its captions was re-measured in the font the panel actually uses, which is not the dialogue font, and the ones over the line were re-wrapped or given a small wording trim, so they all fit at full size now. The second game's captions haven't had that pass yet. If you're looking at a shrunk one, in either game, I want to know which character |
| A full-screen document or report page has text running off the edge | first game | FIXED in v1.9. Sixteen pop-up pages had a line too long for the box; re-wrapped, not a word changed, and checked on the rig. If you hit another one, a photo would help |
| A crackle over the voice in the animated cutscenes | first game, all seven cutscenes | FIXED in v1.8b. Capcom ships the cutscene sound as three separate pieces, the music, the effects and the voice, and my build adds them together. The total came out louder than the file can hold, so the loudest instants had their tops chopped flat: 126 times in the 61 second opening, and in all seven cutscenes. Found in September 2026 from a phone recording made on a console, after three offline checks had passed the broken build |
| A fine grain, like faint static, over the animated cutscenes | first game, all seven cutscenes | FIXED in v1.9. This was written down here as an unfixable format limit, and that was wrong. My own audio tools were writing every English track into the file a few bytes out of position, so the console read each one slightly late, and the grain was the sound of that misread. The tracks now start where Capcom's do. Confirmed by recording the opening on a console before and after; the second recording has no grain. Same root cause as the crowd sounds, the voice-line click and the cut-off voice lines below, and nothing to do with the crackle fixed in v1.8b, which was a separate bug |
| A courtroom crowd sound, like the murmur around the closing arguments, plays back scrambled | both games | FIXED in v1.9. Same misalignment as the cutscene grain, and two crowd sounds in each game were also stored in the wrong channel layout, which is what made those ones scramble rather than just hiss. Every replaced sound in both games and their DLC has been moved back into position |
| A crowd chant or the courtroom murmur goes quiet for a stretch, then jumps back in as it repeats | both games | FIXED in v1.9. Two looping crowd sounds in each game had their loop points set wrong since earlier releases, so each repeat played a silent stretch and then jumped; the chant also had a couple of tiny clipped peaks. Both now loop where Capcom's English recordings say to, and so does the second game's Episode 5 chant, which is new in this release. The murmur dips a little at the start of each cycle; that is in Capcom's recording, not a defect. Checked by decoding, not yet heard in-game |
| A faint click at the end of a replaced voice line | both games and their DLC | FIXED at the root in v1.9. v1.5 stopped the click by giving every replaced clip a silent tail, which worked, but the real reason the console was reading past the end of the clip was that the clip had been written a few bytes early. The clips are written where Capcom writes them now |

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

v1.9 reverses this. The "fit" was never real: a clip written where the game reads it
plays in full at any size. The 27 second-game lines whose pauses had been shortened have
their pauses back, and the lines that had been stored at reduced quality are at full
quality again.

**The second game was the gap, and it is now closed.** It shipped with ten English clips
covering two characters, while every other voice in it, shouts and story lines alike,
stayed Japanese over English text. There were two separate systems to fix and finding the
second one took someone playing the game and asking why a character sounded wrong.

What is still Japanese, and why:

| | |
|---|---|
| **54** | Capcom never recorded an English take. Verified exhaustively rather than assumed: *Chronicles* ships 288 English voice files and every one of them matches a 3DS clip name, with none left over, so there is no alternate naming convention hiding a recording. |
| **18** | Were left Japanese through v1.8b because the English take runs 1.4x to 3x longer than the Japanese one and a longer clip was believed to get cut off in-game. English since v1.9: the cut-off was my file misplacement bug, not a size limit. |
| **4** | Courtroom shouts for two minor characters, an *Objection!* and a *Hold it!* each, that Capcom never re-recorded in English. Their archives were checked member by member: 104 shouts live inside the character archives, 100 have a *Chronicles* master, these four do not. |
| **1** | A second gallery chant in the second game, left Japanese through v1.8b because Capcom's English runs far longer than the Japanese and a longer clip was believed to get cut off. English since v1.9: the cut-off was my file misplacement bug, not a size limit. Checked offline only. |


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

v1.9 changed this for the first game's Episode 2 opening. Instead of squeezing the takes,
the halves played at natural speed and full quality. That fixed the rush and introduced a
smaller problem: each page's English is in two halves, and the second half was still
started by the cue the game uses for the Japanese second line. The Japanese lines don't
break where the English sentences do, so on five pages the second half sat waiting for
half a second to over a second, three times in the middle of a sentence or a word, and two
pages felt rushed for the same reason.

Capcom's PC release has its own English timing for this scene: the same page timing as the
Japanese, with one continuous read per page. v1.9a follows it. Each page's second half now
follows the first after the recording's own natural pause, and the page turns, art and
music are back on Capcom's original timing. The old and new timing were compared by ear
before this went in, and it was then recorded in-game: nothing is cut off and nothing
overlaps. The other episode openings in both games play one piece per page and already
match the PC timing, so they didn't need this. The Japanese-voice edition keeps the
Japanese timing on purpose, because it plays the Japanese recordings.

If you play the second game and hear Japanese where you expected English, that is this,
and it is expected rather than a broken install.

Getting the DLC's clips to play was the harder half. They came out silent or truncated,
and the reason was not obvious:

**A voice stream larger than Capcom's original is cut off in-game, and not at the
original's length.** It stops at an unpredictable point, and how far it overshoots does not
predict where it stops. Measured by metering the speaker, not by reading the file:

| my clip | Capcom's slot | actually played |
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

v1.9 retracts the rule above. The cut-off was real, but its cause was the misplacement
bug described under the cutscene grain, not the clip's size: the tools wrote every clip a
few bytes before where the game reads, and how far into the clip the read went wrong
depended on the audio, which is why the cut point looked unpredictable. A clip written at
Capcom's position plays to the end at any size; one 61% larger than Capcom's was played
three times on a console and was complete each time. All 16 rate-reduced clips and the 3
trimmed ones are back at full quality and full length.

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

v1.9 found why the clips were past the boundary in the first place: the tools were writing
every imported stream a few bytes early in the file, so the console's read ran past the
true end. The streams are written at Capcom's position now, and the silent tail stays as a
belt and braces.

v1.9 also fixed where three crowd sounds loop: the courtroom murmur and a long crowd chant in
both games, plus the second game's Episode 5 chant, which is English for the first time. The
old import took each loop point from the Japanese recording and stretched it to the English
one's length, so every repeat ran into a stretch of silence and then jumped back in. The loop
points now come straight from Capcom's English recordings, and each stream ends where Capcom
ends its own. The murmur is also about 1 dB louder than before, back at the level of Capcom's
English file, and the long chant lost a couple of tiny clipped peaks. Capcom's English murmur
starts its loop inside a short fade-in, so it dips a little each time round; that's in the
original recording. These were checked by decoding them on a PC. The loops haven't been heard
on a console yet, and the Episode 5 chant can't be reached on the test save.

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

From v1.5 each release also carries one zip per game, `TGAA1-3DS-English-v1.9c-xdelta.zip`
and `TGAA2-3DS-English-v1.9c-xdelta.zip`, holding three xdelta3 patches that apply to files
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

The same readme text is also on the release on its own, as `TGAA1-README-v1.9c.txt` and
`TGAA2-README-v1.9c.txt`, because romhacking.net wants the readme as a separate link rather
than only inside the zip. `HASHES_v1.9c.txt` on the release lists the size, CRC32 and sha256
of every source dump, patch and result for both games.

The CIAs stay on the release because they are what the hardware testing was done on, and
because a patch against a file most people dump differently is a support thread waiting
to happen.

## Japanese voice edition

Some people want Capcom's English text over the original Japanese cast. From v1.5 the
release also carries `TGAA1-3DS-English-JPvoice-v1.9c-xdelta.zip` and
`TGAA2-3DS-English-JPvoice-v1.9c-xdelta.zip`: the same three patches as the zips above,
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

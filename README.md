# The Great Ace Attorney 1 & 2: 3DS English patch

**Capcom's official English text, from *The Great Ace Attorney Chronicles*, carried onto
the Japanese 3DS releases, including all the DLC.**

*Dai Gyakuten Saiban* (2015) and *Resolve* (2017) never got an English 3DS release.
Capcom localized both for *Chronicles* (2021) on PC and console, but never brought that
text back to the handheld. **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**
does exactly that, with a real layout pipeline rather than hand-edited scripts.

This builds on their work. It finishes the DLC, which no previous patch had
translated, brings across Capcom's own voices and art, and fixes what playing the
result turned up.

> ### Playtesters wanted
>
> **Both games install and boot on real 3DS hardware**, confirmed 30 August 2026. That
> was the largest unknown in this release, and it is closed. Everything else was tested
> in an emulator, which is more permissive than a console in at least one known way.
>
> What is still untested is *playing* it on hardware. 32 of the first game's shouts,
> the jury verdicts and the pressing voices, have never been heard by anyone, in any
> build, on any platform.
>
> **[Report anything wrong in issue #1](../../issues/1)**. The episode and chapter is
> enough, and a photo of the screen beats a description. Every real defect this project
> has had was found by a person looking or listening, and none by an offline check.

**Every figure below is reproducible.** The audio counts come from
`audit_all_audio.py`, which compares each file against Capcom's own recording rather
than against a threshold; the caption and layout figures come from the upstream
pipeline. Where something has not been verified, this README says so.

> **You need the Japanese base games.** They are not distributed here, upstream, or
> anywhere else in this project. Cartridge or your own dump.

---

## What you need

| | |
|---|---|
| **Dai Gyakuten Saiban** and/or **Resolve** | The Japanese 3DS releases. Cartridge or your own dump |
| **A 3DS that can install CIAs**, or Azahar/Citra | The builds are CIAs. QR codes are not provided |

You do **not** need senyarom's release installed first. These builds supersede it.

## Install

Download from [Releases](../../releases). **Order matters.**

| order | file | what it is |
|---|---|---|
| 1 | *the Japanese base game* | not distributed, bring your own |
| 2 | `TGAA1-base-1.0.18.cia` / `TGAA2-base-1.0.12.cia` | the update |
| 3 | `TGAA1-DLC-1.0.9.cia` / `TGAA2-DLC-1.0.5.cia` | the DLC |

There is no longer a separate no-credits build. The second game's end credits now run
entirely in Japanese, exactly as Capcom shipped them, so the rollback it existed for is
the normal build.

### Checking the install took

From v1.1 on, the versions on screen are the real ones and match the filenames:

| | reads |
|---|---|
| TGAA1 title screen, top right | `ENG 1.0.18` |
| TGAA1 DLC, Episode 0 magazine cover | `DLC 1.0.9`, top left |
| TGAA2 title screen, top right | `ENG 1.0.12` |
| TGAA2 DLC, costume pack banner | `DLC 1.0.5`, bottom right |

An older number on a title screen (`ENG 1.0.2` or `ENG 1.0.4`) means the v1.0 update is
still installed. An older number on a DLC page means the old DLC is still installed.

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
| **3** | DLC banners and the icon labels redrawn |

**The playable sample was translated by hand.** The first game's DLC magazine carries a
playable demo as issue No. 13: Episode 1's opening, the Court Record tutorial and a
cross-examination, around **11,300 characters across five script files**. No patch had
translated it. It was done from the Japanese by hand for this release, and it is the one
part of this project that is an original translation rather than a port of Capcom's work.
Issues 9 to 12 turned out to be empty stubs that open and immediately exit, so their
covers are now labelled as such and No. 13 is labelled as the playable one.

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
| **1** | save/load screen drawing the timestamp straight through the episode title |
| **1** | pagination regression that had inflated the script by 6,855 pages |

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

Two further issues were filed there and **remain unfixed**, in this build and upstream:
**[#5](https://github.com/senyarom/tgaa2-en-patch/issues/5)** (the second game's Japanese
end credits) and **[#6](https://github.com/senyarom/tgaa2-en-patch/issues/6)** (the first
game's DLC Picture Book and Theme buttons bouncing to the title). Both appear in the known
issues below. They are listed here because a contribution section that only lists wins is
not worth much.

---

## Known, and not worth reporting

- **The second game's end credits are in Japanese.** All 75 cards, deliberately. The PC
  release lays them out differently and cannot be ported, so translating them is a
  typesetting job requiring every staff name romanised correctly -- and a misspelled
  credit is worse than an untranslated one. 15 cards were briefly English; they were
  reverted for consistency. This is the largest known gap and is reported upstream.
- **Some voice lines sound slightly duller than others.** Deliberate, see above.
- **Some English lines are shorter than the Japanese ones were.** The English
  performance is simply shorter. A line that ends cleanly is complete.
- **The DLC card on the title screen reads "D L C" one letter per slot.** That card's label is four single-character cells the game stacks, so a full word cannot go there. Cosmetic.
- **"Editor's Notes" behaves like the Picture Book and Theme buttons** in the first
  game's DLC. A known bug affecting all three.

## What is worth reporting

- **Any voice that is silent, cut off mid-word, or in Japanese.**
- **Anything that fails to load**: a scene, a movie, the credits.
- **Text that overflows, clips, or renders at the wrong size**, especially in the second
  game's menus. 42 UI strings were re-tagged; if anything now looks the wrong *size*,
  that is a consequence of it.
- **Anything at all on real hardware**, good or bad.

## Testing status, honestly

| | |
|---|---|
| DLC voice galleries, first game | measured in-game, and confirmed by ear |
| DLC mini-episode shouts, second game | confirmed in play |
| In-game shouts, both games | correct as files, **never heard in context** |
| The second game's credits sequence | **never run by anyone**, but now uses Capcom's own untouched archives |
| Installing and booting on a 3DS | **confirmed on hardware**, both games |
| Playing through on a 3DS | not yet |

The 32 unheard shouts are expected to be fine. They load by a different route than the
clips that had the slot bug, and Capcom ships entries five times larger in the same
archives. But that is reasoning, not listening. **If you play the first game, a jury
verdict or a press that stops part-way is the single most useful thing to listen for.**

---

## Credits

**senyarom** did the hard part:

> **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**

This is built entirely on top of their work: their layout pipeline, their font
handling, their port of Capcom's script onto the 3DS builds. Without it there is nothing
here. Where Capcom localized the DLC, the text in these builds **is** senyarom's carry
of Capcom's English, word for word; that was verified by comparing against the
*Chronicles* release directly.

**Scarlet Study** made the first playable English 3DS build, years earlier, and it was
used as a reference point throughout.

*The Great Ace Attorney* and *Chronicles* are © Capcom.

## Licence

This project is **GPL-3.0-or-later** ([`LICENSE`](LICENSE)), inherited from
[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch), which is licensed
the same way and whose modules 48 of our scripts import directly.

The corresponding source for every build on the releases page is in
**[`tools/`](tools/)**: the audio fitters, the text and archive patchers, the cover and
banner builders, and the emulator driving rig. It is research code rather than a polished
toolkit, and it ships with no game data.

The GPL covers this project's own work. It does not cover Capcom's content, which is not
ours to license. See below.

## Legal

**The Japanese base games are not distributed here**, the same line upstream draws. You
supply your own.

The update and DLC packages are installable CIAs containing Capcom's content with
English assets substituted, which is the same class of artifact
[senyarom's releases](https://github.com/senyarom/tgaa2-en-patch/releases) carry.

**If you want Capcom's translation, buy *The Great Ace Attorney Chronicles*.** It is
very good, it is on every current platform, and it is the reason this project can exist
at all.

### Why these are CIAs and not patch files

A delta against senyarom's release would be the tidier thing to ship, and for three of
the four builds it works. Those patches are attached to the release as an optional path
for anyone who already has their CIAs. Only one of the three saves much, though: the
second game's update comes to 2 MB against a 32 MB download, but the first game's is 29
against 62, and the second game's DLC is 29 against 38. Take the CIAs unless bandwidth
is genuinely tight.

It does not work for the first game's DLC. Its contents are encrypted, and the audio
work shifted every offset inside them, so the delta comes to **310 MB against a 326 MB
target**. It shares almost nothing with the source. That is not a patch; it is the
whole DLC with extra steps. Since the DLC extras are where most of this work lives, and
testers who cannot reach them cannot report on them, the CIA ships instead.

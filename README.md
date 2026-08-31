# The Great Ace Attorney 1 & 2: 3DS English patch

**Capcom's official English text, from *The Great Ace Attorney Chronicles*, carried onto
the Japanese 3DS releases, including all the DLC.**

*Dai Gyakuten Saiban* (2015) and *Resolve* (2017) never got an English 3DS release.
Capcom localized both for *Chronicles* (2021) on PC and console, but never brought that
text back to the handheld. **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**
does exactly that, with a real layout pipeline rather than hand-edited scripts.

This builds on their work. It finishes the DLC, which no previous patch had
translated, and fixes what playing the result turned up.

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
| 2 | `TGAA1-base-1.0.2.cia` / `TGAA2-base-1.0.2.cia` | the update |
| 3 | `TGAA1-DLC-1.0.4.cia` / `TGAA2-DLC-1.0.3.cia` | the DLC |

`TGAA2-base-1.0.1-no-credits.cia` is a **rollback**, not an upgrade. It is the same build
without the 15 English credit cards. Install it only if the credits sequence misbehaves,
and note it predates the UI readability fix.

### Checking the install took

Both games display their version on screen, and the filename, the version the console
reads, and the version painted in-game all agree.

| | reads |
|---|---|
| TGAA1 title screen | `ENG 1.0.2` |
| TGAA1 DLC magazine page | `DLC 1.0.4`, top left |
| TGAA2 title screen | `ENG 1.0.2` |
| TGAA2 DLC page | `DLC 1.0.3`, bottom right of the banner |

**If a version on screen does not match the file you installed, the install did not
take.** That is a real bug. Please report it.

---

## What this adds on top of senyarom's patch

**What is theirs:** the layout pipeline, the font handling, and the carry of Capcom's
official script onto the Japanese 3DS builds. That is the foundation, and it is the hard
part of the problem. Nothing here replaces any of it.

**What is here** is three things: the DLC, audio that plays to the end, and the class of
bug you only find by playing.

### 1. The DLC, which no English release had ever covered

Every previous effort stops at the base games. Scarlet Study's translation and senyarom's
patch both leave the DLC in Japanese. Even the mod that ports the 3DS DLC across to the
Steam release says in its own readme that the mini-cases are untranslated, and that no
text will be displayed during them at all.

So this is the part that did not exist anywhere before:

| | |
|---|---|
| **2** | mini-episodes, fully translated and playable |
| **46** | gallery voice clips, in Capcom's English rather than Japanese |
| **34** | mini-episode shouts in the second game, which had been speaking Japanese over English text |
| **11** | commentary videos, subtitled and re-encoded to Capcom's own container spec |
| **9** | magazine covers rebuilt from the official *Chronicles* banner art |
| **3** | DLC banners and the icon labels redrawn |

**And where Capcom localised a piece of the DLC, this matches Capcom word for word.** One
scene exists in *Chronicles* as official English, which makes an exact check possible:
comparing box by box, **140 of 190 are byte-identical**, and every remaining difference is
either a line wrapped to fit the narrower 3DS box or a curly quote the 3DS font does not
carry. Not a paraphrase of the official text. The official text.

### 2. Audio that plays to the end of the line

The DLC's English voice clips were silent, truncated, or still Japanese. Fixing that meant
finding out why, and the answer was not obvious:

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

### 3. The bugs you only find by playing

| | |
|---|---|
| **164** | Court Record captions rewritten to fit at full size. The panel silently shrinks its font rather than clipping, so long captions rendered small and soft instead of looking broken |
| **43** | glyph advances corrected in the dialogue font, including a tuck for overhanging T, Y and L |
| **42** | menu strings in the second game that fell through to a decorative script and were genuinely hard to read: Yes/No, OK, Cancel, Examine, Move, Converse, Present, every game-over option |
| **19** | voice clips cut off mid-word, per the section above |
| **1** | save/load screen drawing the timestamp straight through the episode title |
| **1** | pagination regression that had inflated the script by 6,855 pages |

Every one of these was found by a person looking at a screen or listening to a speaker.
**None were found by an offline check**. The automated audit passed a build in which one
line was silent and another was cut in half, and it did so because a path comparison
silently matched nothing. That is why this release asks for playtesters rather than for
more tooling, and why the testing status below is written the way it is.

---

## Known, and not worth reporting

- **The second game's end credits are in Japanese.** 75 cards. 15 are English; the rest
  cannot be ported, because the PC release lays them out differently. They are a
  typesetting job, not a copy. This is the largest known gap.
- **Some voice lines sound slightly duller than others.** Deliberate, see above.
- **Some English lines are shorter than the Japanese ones were.** The English
  performance is simply shorter. A line that ends cleanly is complete.
- **A DLC card on the title screen is blank** in both games. Cosmetic.
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
| The second game's credits sequence | **never run by anyone** |
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

# The Great Ace Attorney 1 & 2: 3DS English patch

**Capcom's official English text, voices and art from *The Great Ace Attorney Chronicles*,
carried onto the Japanese 3DS releases, DLC included.**

Neither *Dai Gyakuten Saiban* (2015) nor *Resolve* (2017) got an English 3DS release.
Capcom localized both for *Chronicles* in 2021 on PC and console but never brought that
text back to the handheld. **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**
brought that text to the 3DS builds first, with a real layout pipeline rather than
hand-edited scripts, and this patch starts from it.

This builds on it and adds Capcom's English voice acting, the videos and the art, the DLC
that nothing had ever translated, and a lot of layout work of its own. You don't need
senyarom's release installed first, these builds supersede it.

Every figure in [DETAILS.md](DETAILS.md) is reproducible. The audio counts come from
`audit_all_audio.py`, which compares each file against Capcom's own recording rather than
against a threshold. Where something hasn't been verified, it says so.

> ### Playtesters wanted
>
> Both games install and boot on real hardware, and a tester has played both of the second
> game's DLC stories start to finish on an original 3DS, twice. **Nobody has played either
> main game through on a console.** 32 of the first game's shouts, the jury verdicts and
> the pressing voices, have never been heard by anyone, in any build, on any platform.
>
> **[Report anything wrong in issue #1](../../issues/1).** The episode and chapter is
> enough, and a photo of the screen beats a description. Every real defect this project
> has had was found by a person looking or listening, and none by an offline check.

> **You need the Japanese base games.** They aren't distributed here, upstream, or anywhere
> else in this project. Cartridge or your own dump.

---

## Install

Download from [Releases](../../releases). **Order matters.**

| order | file | what it is |
|---|---|---|
| 1 | *the Japanese base game* | not distributed, bring your own |
| 2 | `TGAA1-base-3.4.2.cia` / `TGAA2-base-1.0.32.cia` | the update, which carries the English manual (v1.9r changed the second game's only) |
| 3 | `TGAA1-DLC-1.0.23.cia` / `TGAA2-DLC-1.0.19.cia` | the DLC (the first game's is unchanged since v1.9m; the second game's is unchanged since v1.9q, when it became 1.0.19) |
| 4 | `TGAA1-3DS-English-v1.9r-xdelta.zip` / `TGAA2-3DS-English-v1.9r-xdelta.zip` | optional: rows 2 and 3 as xdelta patches against your own decrypted dump, plus the HOME banner patch and a readme |
| 5 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional, the English HOME menu banner on its own |

The row-3 DLC CIAs are 326,388,736 bytes (`TGAA1-DLC-1.0.23.cia`, sha256
`3c1d503be27b4195df2baf6fc651f3b390edcee0b7b8e68165e36e3e50b04e86`) and 40,249,728 bytes
(`TGAA2-DLC-1.0.19.cia`, sha256
`e6f6d18345fdaa5ed326ecb1247707be82bb0d8d4f74117123ed730aff736c2d`). The release page shows
a sha256 for every posted file, so any of them can be checked the same way.

**Updating from v1.9q.** Only the second game's update changed in v1.9r. The first game's
update and DLC, the second game's DLC and both banner patches are the same files as in v1.9q,
so there is nothing to redo for the first game. The xdelta zips carry the new version in their
names, and the first game's patches inside them are the v1.9q ones.

You need a 3DS that can install CIAs, or Azahar/Citra. No QR codes.

**On an emulator, take the plain DLC instead.** If the DLC card shows a padlock and the game
returns to the title, or your emulator refuses to install the DLC at all, use
`TGAA1-EN-DLC-v1.9m.cia` or `TGAA2-EN-DLC-v1.9q.cia` in place of row 3. Same DLC, same version,
same size, with Capcom's encryption taken off the filesystem inside, so the emulator doesn't need
AES keys of its own to read it. A console reads either form. Install one or the other, not both.

`TGAA1-README-v1.9r.txt` and `TGAA2-README-v1.9r.txt` on the release page are the readmes from
inside the xdelta zips, there so you can read the commands and the hashes without downloading
the zip first.

**If you're using the xdelta zips**, the patches apply to the files Batch CIA 3DS Decryptor
writes from your own Japanese dumps, and they're strict about it.

> **Dump the title as an encrypted CIA and decrypt it on the PC.** In GodMode9, dump the title
> to CIA with no decrypt and no trim option, copy that to your computer, and run Batch CIA 3DS
> Decryptor on it there. GodMode9's own decrypt gives you a file of the **right size** that is
> not the same bytes, and the patch will refuse it; running the PC decryptor on that file
> afterwards does not fix it either. That has caught a few people, so a size that matches the
> table below is not proof the file is right. A raw `.3ds` cartridge image is a different file
> again.

Check the sizes before you spend time on it:

| | title ID | decrypted size |
|---|---|---:|
| TGAA1 game `.cci` | `000400000014AD00` | 689,790,976 |
| TGAA1 DLC `.cia` | `0004008C0014AD00` | 335,531,008 |
| TGAA2 game `.cci` | `00040000001AE200` | 844,902,400 |
| TGAA2 DLC `.cia` | `0004008C001AE200` | 39,676,288 |

Your files won't match my hashes, and that's fine: the decryptor writes random bytes into the
card header and the ticket. The patches are built so those bytes don't matter. Everything else
has to match, so a checksum error means the source is the wrong file, not the wrong
luck. The wording xdelta3 gives you is `target window checksum mismatch`. If you see it,
redump the title encrypted and check the source against `HASHES_v1.9r.txt` before trying
again.

**Check it took:**

| | reads |
|---|---|
| TGAA1 title screen, top right | `ENG 3.4.2` |
| TGAA1 DLC, Episode 0 magazine cover | `DLC 1.0.23`, top left |
| TGAA2 title screen, top right | `ENG 1.0.32` |
| TGAA2 DLC, costume pack banner | `DLC 1.0.19`, bottom right |

An older number means an older update is still installed; delete it and install again. Both
title screens should also
show Capcom's own *Adventures* and *Resolve* logos rather than fan-drawn ones.

**v1.9r and v1.9q look the same on the title screen.** The second game's update is still named
`TGAA2-base-1.0.32.cia` and still reads `ENG 1.0.32`, so the stamp can't tell the two apart. The
file is 88,699,904 bytes in both. v1.9r's sha256 is
`84c6b79034118e3f17a4987df1c5bfc26bb5ffa7cbb17dfad43cf0e0ddca2e7e` and v1.9q's was
`0e28c869969d1def939eb4b022cdb33fe775fc1f3e25875e129011effba6e631`. In the game, the Case 5
suitcase lock on the SS Grouse has seven wheels in v1.9r and six in v1.9q. I installed v1.9r over
v1.9q on the Azahar emulator and it replaced it; I haven't tried that on a 3DS.

**The manual.** From v1.9o the update has an English manual in it. Highlight the game on the
HOME menu and tap Manual. The text is English, and from v1.9q the main screenshots in it were
retaken in the patched game. The logo, a few headings and some diagrams are still the older fan
translation's, so a few show names like Naruhodou or Holmes, and the first game's Summation
Examination page has no jury picture. I haven't opened it from the update on a 3DS myself yet.

**Back up your saves first.** The second game throws a corrupted save prompt if it sees
data it doesn't expect, and confirming it wipes your slots. Decline it and report it.

**If your console is online and offers you an update for the second game, decline it.**
That's Capcom's own Japanese update. From v1.5 the patch outranks it and the offer stops.

The optional HOME banner, the xdelta patch files and the Japanese voice edition are all
covered in [DETAILS.md](DETAILS.md). Install one edition or the other, not both.

## What's in it

Capcom's English shouts and story voices in both games, the cutscenes and the episode
narration, where before this both games shouted Japanese over English text. Both of the
second game's mini-episodes and the first game's DLC magazine, including the playable demo
it carries, which was translated from the Japanese by hand, and its Picture Book, theme
titles and Editor's Notes, which open now and are in English. Capcom's own title logos,
evidence cards and shout lettering in place of the fan-drawn art. And a lot of layout work:
dialogue re-broken at corrected font metrics, captions rewritten to fit, glyph advances
fixed. From v1.9o the update also carries an English eManual, the one you open from the HOME
menu. Its text is Scarlet Study's fan translation of the manual, which I revised so that the
names and terms match the game and Capcom's English release. From v1.9q its main screenshots
are retaken in the patched game. And from v1.9p, two of the
first game's Episode 1 evidence pictures, the Waiter's Business Card and the Medical Report
Card cover, are redrawn to match the dialogue, which they didn't before. Also from v1.9p, the
box that asks whether to start a chapter shows the chapter name centred in both games, and in
the second game the episode heading there is two centred lines, with the saved-game list set a
little lower to match. And from v1.9r the second game's Case 5 suitcase lock has seven wheels, as in
Capcom's version, which meant changing the game's program as well as its data, and the topic names
that fly across the screen in that game's Dance of Deduction keep the tails of g, y and p.

Counts, sources and the reasoning for every one of those are in [DETAILS.md](DETAILS.md),
along with what stays Japanese and why. [RELEASE_NOTES.md](RELEASE_NOTES.md) has a short
entry for each version, newest first, if you want to know what changed and when.

## If something looks or sounds wrong

Tell me, even if you're sure I already know. **[Report it in issue #1](../../issues/1).**
The episode and chapter is enough to go on, and a photo of the screen beats any description
I could ask you for. A duplicate costs me nothing. A report somebody talked themselves out
of costs me a defect, and that has already happened once.

[DETAILS.md](DETAILS.md) opens with a list of everything I know about, sorted by what it
looks like on screen rather than by what I did about it. It's there if you're curious about
something specific. It isn't a checklist you have to clear before you're allowed to tell me
something.

These are the ones you're most likely to meet:

- **Some lines are still spoken in Japanese.** Capcom never recorded an English take for
  54 of them. Four courtroom shouts belong to two minor characters Capcom skipped, and
  two "Take that!" shouts in the second game's DLC have no English recording either.
  DETAILS has each group and the reasoning.
- **The second game's end credits are in Japanese.** All 75 cards, deliberately. The PC
  release lays them out differently and can't be ported, and a misspelled credit is worse
  than an untranslated one. This is the largest known gap and it's reported upstream.
- **Some text still runs past its box.** 38 dialogue pages in the second game end under the
  page arrow. One single-word page and three widget pages in the first game sit right on the
  edge. And two lines in
  the first game's second Dance of Deduction, set in the fancier face, end slightly under
  the page arrow.
- **Some of the manual's pictures are still the older fan translation's.** The text is
  revised and the main screenshots were retaken in v1.9q, but the logo, a few headings and some
  diagrams are Scarlet Study's originals, so a few show older names and menu words. The first
  game's Summation Examination page has no jury picture. I plan to redo them later.
- **The seven-wheel lock's cursor is clipped a little.** On the second game's Case 5 suitcase
  lock, the cyan cursor is cut off by the frame's edge on the first and last wheel. It's cosmetic,
  and the lock works.
- **There's still Japanese inside the first game's DLC Picture Book.** The brush-written
  name tags and the small production scribbles on the design sheets were left alone on
  purpose. On the rough sketches page in issue 6, the tips of the pencil hair are clipped,
  because every rule that kept them also left readable Japanese behind.

Nobody has played either main game the whole way through on a console yet, so the later
chapters of both are the least tested thing here. The English voice lines added to the
second game's last two episodes in v1.9 were checked against the recordings offline, not
heard in-game, and the "shing" sound mixed back under the English shouts in v1.9n hasn't been
heard on a 3DS yet. The English manual added in v1.9o, with its pictures retaken in v1.9q, hasn't been opened
from the update on a 3DS either. Nothing in v1.9p, v1.9q or v1.9r has been tried on a 3DS; what I could look at, I looked at on the Azahar
emulator. The redrawn Medical Report Card's small list icon hasn't been seen on screen at all,
and neither have the second game's saved-game rows for Episode 1, Episode 4 and Final, because
I had no such saves. The seven-wheel lock in v1.9r changes the second game's program itself, not only
its data, and that has only run in an emulator.
[TESTING.md](TESTING.md) is the full
account of what has been played, watched and listened to, and what has only been checked in
the files.

## Credits

**senyarom**: **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**.
Their layout pipeline, their font handling and their port of Capcom's script onto the 3DS
builds are what this patch starts from.

**Scarlet Study / Fan Translators International**, as senyarom's README credits them, are
further back down the same chain, and not just as a reference point. They made the first
playable English 3DS builds years earlier, along with the font, rendering and reverse
engineering work those builds rest on. senyarom's README says their project builds on that
work, and their importer takes the Scarlet Study TGAA1 v2.4.1 and TGAA2 v2.1.0 CIAs as
build inputs, so it is structurally underneath this patch too.

The English eManual in v1.9o is Scarlet Study's. Their fan translation of the manual is where
its text, its logo and the headings and diagrams I haven't redone come from, and I revised
the wording for this patch. The main screenshots in it were retaken in the patched game for v1.9q.

The title logos, evidence cards, end card, Dance of Deduction wording and the lettering on its note cards are Capcom's own
artwork and text from *Chronicles*, carried over rather than redrawn, except the first game's Waiter's Business Card and
Medical Report Card cover (and their small list icons). Those two I redrew for v1.9p,
because *Chronicles* has no English version of either, so they are not Capcom's artwork.
The three banners in
the second game's DLC are adapted from Capcom's own artwork.

The tooling was written with LLM assistance (Claude, through Claude Code). That's stated
here rather than buried. Most of what ships is Capcom's own files and senyarom's carry of
their script. Two things in the first game's DLC aren't, because Capcom never made them in
English: the Picture Book commentary, sketch notes, theme titles and Editor's Notes were
translated with Claude's help, checked against a second model and against Capcom's
spelling of every name; and where that Japanese sat over artwork, the covered part of the
art was filled in with an image inpainting model (LaMa). The two Episode 1 pictures redrawn in v1.9p were made with an image generator
and finished by me. No generated audio ships.
`tools/` is there so you can check all of it rather than take it from me.

*The Great Ace Attorney* and *Chronicles* are © Capcom.

## Licence

**GPL-3.0-or-later** ([`LICENSE`](LICENSE)), inherited from senyarom's project, which is
licensed the same way and whose modules 89 of these scripts import directly. The
corresponding source for every build on the releases page is in [`tools/`](tools/). It's
research code rather than a polished toolkit and it ships with no game data.

The GPL covers this project's own work. It doesn't cover Capcom's content, which isn't
mine to license.

## Legal

**The Japanese base games are not distributed here**, the same line upstream draws. You
supply your own. The update and DLC packages are installable CIAs containing Capcom's
content with English assets substituted, the same class of artifact
[senyarom's releases](https://github.com/senyarom/tgaa2-en-patch/releases) carry.

**If you want Capcom's translation, buy *The Great Ace Attorney Chronicles*.** It's very
good, it's on every current platform, and it's the reason this project can exist at all.

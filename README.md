# The Great Ace Attorney 1 & 2: 3DS English patch

**Capcom's official English text, voices and art from *The Great Ace Attorney Chronicles*,
carried onto the Japanese 3DS releases, DLC included.**

Neither *Dai Gyakuten Saiban* (2015) nor *Resolve* (2017) got an English 3DS release.
Capcom localized both for *Chronicles* in 2021 on PC and console but never brought that
text back to the handheld. **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**
does exactly that, with a real layout pipeline rather than hand-edited scripts. That's the
hard part and it's theirs.

This builds on it and adds everything that isn't text: Capcom's English voice acting, the
videos, the art, and the DLC that nothing had ever translated. You don't need senyarom's
release installed first, these builds supersede it.

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
| 2 | `TGAA1-base-3.2.3.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia` | the DLC |
| 4 | `TGAA1-3DS-English-v1.6-xdelta.zip` / `TGAA2-3DS-English-v1.6-xdelta.zip` | optional: rows 2 and 3 as xdelta patches against your own decrypted dump, plus the HOME banner patch and a readme |
| 5 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional, the English HOME menu banner on its own |

You need a 3DS that can install CIAs, or Azahar/Citra. No QR codes.

**Check it took:**

| | reads |
|---|---|
| TGAA1 title screen, top right | `ENG 3.2.3` |
| TGAA1 DLC, Episode 0 magazine cover | `DLC 1.0.10`, top left |
| TGAA2 title screen, top right | `ENG 1.0.16` |
| TGAA2 DLC, costume pack banner | `DLC 1.0.9`, bottom right |

An older number means an older update is still installed. Both title screens should also
show Capcom's own *Adventures* and *Resolve* logos rather than fan-drawn ones.

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
it carries, which was translated from the Japanese by hand. Capcom's own title logos,
evidence cards and shout lettering in place of the fan-drawn art. And a lot of layout work:
dialogue re-broken at corrected font metrics, captions rewritten to fit, glyph advances
fixed.

Counts, sources and the reasoning for every one of those are in [DETAILS.md](DETAILS.md),
along with what stays Japanese and why.

## Known, and not worth reporting

- **The second game's end credits are in Japanese.** All 75 cards, deliberately. The PC
  release lays them out differently and can't be ported, and a misspelled credit is worse
  than an untranslated one. This is the largest known gap and it's reported upstream.
- **Some voice lines sound slightly duller than others.** Deliberate, see DETAILS.
- **Some English lines are shorter than the Japanese were.** The performance is shorter.
  A line that ends cleanly is complete.
- **The DLC card on the title screen reads "D L C"**, one letter per slot. Cosmetic.
- **"Editor's Notes" bounces to the title** in the first game's DLC, along with the Picture
  Book and Theme buttons. Known upstream bug.
- **Two shouts in the second game's DLC stay Japanese.** Capcom never recorded them.
- **38 dialogue pages in the second game still run under the arrow**, and four pages in the
  first game are still wider than the box. Both listed in DETAILS.

## What is worth reporting

- Any voice that's silent, cut off mid-word, or in Japanese.
- Anything that fails to load: a scene, a movie, the credits.
- Text that overflows, clips, or renders at the wrong size.
- **Anything at all on real hardware**, good or bad.

The full testing status, written honestly, is in [DETAILS.md](DETAILS.md).

## Credits

**senyarom** did the hard part: **[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch)**.
Their layout pipeline, their font handling, their port of Capcom's script onto the 3DS
builds. Without it there's nothing here.

**Scarlet Study** made the first playable English 3DS build years earlier, and it was used
as a reference point throughout.

The title logos, evidence cards, end card and Dance of Deduction wording are Capcom's own
artwork and text from *Chronicles*, carried over rather than redrawn. The three banners in
the second game's DLC are new artwork made for this patch and aren't Capcom's.

The tooling was written with LLM assistance (Claude, through Claude Code). That's stated
here rather than buried. No generated text or audio ships in the patch: what's in it is
Capcom's own files and senyarom's carry of their script, and `tools/` is there so you can
check that rather than take it from me.

*The Great Ace Attorney* and *Chronicles* are © Capcom.

## Licence

**GPL-3.0-or-later** ([`LICENSE`](LICENSE)), inherited from senyarom's project, which is
licensed the same way and whose modules 48 of these scripts import directly. The
corresponding source for every build on the releases page is in [`tools/`](tools/). It's
research code rather than a polished toolkit and it ships with no game data.

The GPL covers this project's own work. It doesn't cover Capcom's content, which isn't
ours to license.

## Legal

**The Japanese base games are not distributed here**, the same line upstream draws. You
supply your own. The update and DLC packages are installable CIAs containing Capcom's
content with English assets substituted, the same class of artifact
[senyarom's releases](https://github.com/senyarom/tgaa2-en-patch/releases) carry.

**If you want Capcom's translation, buy *The Great Ace Attorney Chronicles*.** It's very
good, it's on every current platform, and it's the reason this project can exist at all.

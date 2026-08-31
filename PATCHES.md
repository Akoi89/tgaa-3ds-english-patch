# The Great Ace Attorney 1 & 2: 3DS English patch

Capcom's official English text, from the *Chronicles* PC release, carried onto
the Japanese 3DS builds, layered on top of
[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch).

These are **patches, not builds.** They contain none of senyarom's work and none
of Capcom's. They require both. Everything here is spoiler-free.

## What you need first

1. **The Japanese base game**, both titles. Cartridge or your own dump.
2. **senyarom's English patch**, already installed. These patches apply *on top
   of* their release; they cannot reproduce it.

| you need | sha256 begins |
|---|---|
| `TGAA1-Official-English-v2.8.6.cia` | `428781d2a20518cb` |
| `DGS2-Official-English-v2.3.3.cia` | `aaed9c8d110a5d10` |
| `DGS2-English-DLC-v1.0.1.cia` | `12ad9207f5aab004` |

If your file's hash differs, the patch will not apply. Say so rather than
forcing it.

## Applying

`xdelta3.exe` is included. From this folder:

```bash
xdelta3.exe -d -s "TGAA1-Official-English-v2.8.6.cia" "TGAA1-update-1.0.2.xdelta" "TGAA1-base-1.0.2.cia"
```

```bash
xdelta3.exe -d -s "DGS2-Official-English-v2.3.3.cia" "TGAA2-update-1.0.2.xdelta" "TGAA2-base-1.0.2.cia"
```

```bash
xdelta3.exe -d -s "DGS2-English-DLC-v1.0.1.cia" "TGAA2-DLC-1.0.3.xdelta" "TGAA2-DLC-1.0.3.cia"
```

Then install the CIAs you just built. **Order matters**: base game first, then
the update, then the DLC.

Each patch was verified by decoding it back and comparing, not assumed. What you
should get:

| file | sha256 |
|---|---|
| `TGAA1-base-1.0.2.cia` | `ad4f9594506c07d3e81771f6c115f8b197149d23edd5680f84cbafe89fcaa976` |
| `TGAA2-base-1.0.2.cia` | `c035dba58e50768c42ebd00145989e4e470364118da16a3b0af5b9b36a9021cb` |
| `TGAA2-DLC-1.0.3.cia` | `4c75de0cad748a7666ef169d1a8b08fe152d9d7c131eef7d31342249a4ec0f42` |

If a hash does not match, stop and report it. Do not play a build that came out
wrong.

## The first game's DLC is not here

There is no `TGAA1-DLC` patch, and the reason is worth stating plainly rather
than hiding.

The DLC contents are encrypted, and the audio work shifted every offset inside
them, so a delta against senyarom's DLC release comes out at **310 MB against a
326 MB target**. It shares almost nothing. That is not a patch; it is the entire
DLC with extra steps, and shipping it would mean distributing Capcom's DLC
wholesale.

So the first game's DLC extras, the voice galleries, magazine covers, subtitled
commentary videos and mini-episodes, are not included in this package. The base
game and its update are complete and unaffected.

## How to tell what you are running

Both games display their version, and the filename, the version the console
reads, and the version painted on screen all agree.

- **TGAA1 title screen** reads `ENG 1.0.2`
- **TGAA2 title screen** reads `ENG 1.0.2`
- **TGAA2 DLC page** reads `DLC 1.0.3`, bottom right of the banner

If a version on screen does not match what you installed, the install did not
take. That is a real bug. Please report it.

## Known, and not worth reporting

- **The second game's end credits are in Japanese.** 75 cards. 15 are English;
  the rest cannot be ported, because the PC release lays them out differently.
  This is the largest known gap.
- **Some voice lines sound slightly duller than others.** Deliberate. Capcom's
  English takes run longer than the Japanese ones they replace, and a clip larger
  than its original slot is cut off mid-word in game. Rather than cut words, those
  clips run at a lower sample rate: correct pitch and timing, less treble.
- **Some English lines are shorter than the Japanese ones were.** The English
  performance is simply shorter. A line that ends cleanly is complete.
- **A DLC card on the title screen is blank** in both games. Cosmetic.
- **"Editor's Notes" behaves like the Picture Book and Theme buttons** in the
  first game's DLC. A known bug affecting all three.

## Fixed in TGAA2 base 1.0.2

- **Unreadable buttons.** 42 UI strings carried no font tag and fell through to
  a decorative script. Yes, No, OK, Cancel, Delete, Examine, Move, Converse,
  Present, the game-over options and the chapter labels were all affected.
- **The save/load screen.** Each slot drew the timestamp straight through the
  episode title. The title now sits on one line at a smaller size and the date
  is clear.
- **The DLC SpotPass toggle** read "Transmission received"; it now reads
  "SpotPass", matching the first game.
- **Three costume labels** said "Holmes" and "Naruhodou" where the game's own
  cast list says "Sholmes" and "Naruhodo".

If anything in the second game's menus now looks the wrong size or overflows,
that is a consequence of these and worth reporting.

## Worth reporting

- **Any voice that is silent, cut off mid-word, or in Japanese.**
- **Anything that fails to load**: a scene, a movie, the credits.
- **Text that overflows, clips, or renders at the wrong size**, especially in
  the second game's menus. See the section above.
- **Anything at all on real hardware.**

Episode and chapter is enough detail. A photo of the screen beats a description.

## The known blind spot

**32 shouts in the first game, the jury verdicts ("Not guilty!" / "Guilty!") and
the pressing voices, are larger than Capcom's originals and have never been
heard by anyone.** They are expected to be fine: they load by a different route
than the clips that had the size bug, and Capcom ships entries five times larger
in the same archives. But that is reasoning, not listening.

If you play the first game, that is the single most useful thing to listen for: a
jury verdict or a press that stops part-way.

## Testing status, honestly

| | |
|---|---|
| DLC voice galleries, first game | measured, and confirmed by ear |
| DLC mini-episode shouts, second game | confirmed in play |
| In-game shouts, both games | correct as files, **never heard in context** |
| Second game's credits sequence | **never run by anyone** |
| Installing and booting on a 3DS | **confirmed on hardware**, both games |
| Playing through on a 3DS | not yet |

Both games install and boot on a real 3DS, confirmed 30 August 2026. Everything
else was tested in an emulator, which is more permissive than a console in at
least one known way -- and nobody has yet played through on hardware.

## Credit

The English text is Capcom's, from *The Great Ace Attorney Chronicles*. The
groundwork is senyarom's. This requires their patch and does not replace it.
Scarlet Study's earlier translation was the first playable English 3DS build and
was used as a reference point throughout.

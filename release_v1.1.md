Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and now Capcom's art as well.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games. They aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-1.0.18.cia` / `TGAA2-base-1.0.12.cia` | the update |
| 3 | `TGAA1-DLC-1.0.9.cia` / `TGAA2-DLC-1.0.5.cia` | the DLC |

**Coming from v1.0?** Install both updates and the first game's DLC again. `TGAA2-DLC-1.0.5.cia` is the same file as before; it's attached here so the set is complete.

## How to tell it took

The version numbers on screen are real from this release on. The title screens read `ENG 1.0.18` and `ENG 1.0.12` in the top right, the first game's Episode 0 magazine cover reads `DLC 1.0.9`, the second game's costume pack banner reads `DLC 1.0.5`. If a title screen still says `ENG 1.0.2` or `ENG 1.0.4`, the old update is still installed.

You'll also notice the title logos: both are now Capcom's own *Adventures* and *Resolve* marks rather than the hand-drawn ones.

## What's new in v1.1

Everything here came out of decoding the textures Capcom localised for *Chronicles* and putting each one next to the 3DS build.

- **Capcom's title logos** on both title screens.
- **12 evidence cards** (the maps, the pawn tickets, a contract) that still carried fan-translation names like "Hatch's Pawnbrokers" and "The Ragged Reader" while the dialogue said Windibank's and Bourbon Books. They're Capcom's cards now, with the red map markers kept from the Japanese originals.
- **The first game's end card** was still Japanese. It's Capcom's "FIN" card now.
- **168 Dance of Deduction plates** re-rendered with Capcom's wording: all 74 in the first game and 94 of 104 in the second. Two plates in the second game had never been translated and were still in Japanese, and one stamp atlas the fan patch had missed now has English stamps.
- **Madame Tusspells' card** now carries her name.
- **Real version numbers** on both title screens, a "D L C" label on the title card that used to be blank, and the first game's Japanese boot notice blanked the way the second game already was.
- The second game's episode select plates are set in the serif face and no longer cramped, and its last episode has its official Chronicles card.

Nothing about the text changed except a handful of strings brought in line with Chronicles spellings (two "Naruhodou" in the first game, a mixed "Ryuunosuke / Naruhodo's" and an episode plate in the second). The cross-examination check still applies: the first statement of the first game should sit on two lines.

## Still true from v1.0

- Both games install and boot on a real 3DS. Nobody has played all the way through on hardware yet.
- 76 voice clips stay Japanese, for the reasons in the README.
- The second game's end credits are Japanese, as Capcom shipped them.
- Picture Book, Theme and Editor's Notes in the first game's DLC still bounce back to the menu. Reported upstream as senyarom/tgaa2-en-patch#6.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt, which switching builds can trigger. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.

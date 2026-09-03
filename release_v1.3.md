Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games. They aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-1.0.19.cia` / `TGAA2-base-1.0.13.cia` | the update |
| 3 | `TGAA1-DLC-1.0.9.cia` / `TGAA2-DLC-1.0.7.cia` | the DLC |

**Coming from v1.2?** Only the second game changed. Install `TGAA2-base-1.0.13.cia` and `TGAA2-DLC-1.0.7.cia` over the old ones; the first game's two files are the same as v1.2 and are attached here so the set is complete.

## How to tell it took

The second game's title screen reads `ENG 1.0.13` in the top right and its costume pack banner reads `DLC 1.0.7`. `ENG 1.0.12` means v1.2 is still installed. The first game still reads `ENG 1.0.19` and `DLC 1.0.9`.

## What's new in v1.3

The second game gets the same cross-examination fix the first game got in v1.2, plus one more thing that turned up while checking it.

- **Cross-examination statements no longer run into the edge of the text box.** The statement box is narrower than the ordinary dialogue box, and every earlier build had laid statements out against the wider measurement. Checked in-game with the second game's own font before changing anything. **133 statements** re-laid: 92 only needed their line break moved, 41 were shortened by the smallest edit that fits, keeping the witness's voice and checked against the Japanese. Where a statement is repeated when you press it, the repeat matches. The DLC episodes had 4 of these too; fixed in `TGAA2-DLC-1.0.7.cia`. (The DLC file was `1.0.6` for the first hour of this release; `1.0.7` rewords one of those four lines closer to Capcom's original and is otherwise identical.)
- **Evidence cards no longer overflow when they pop up.** When a piece of evidence is added, the card that appears on the top screen was drawing 16 of the longer descriptions oversize and cutting them off at the edge. Those descriptions carried a size tag that the Court Record panel understands and the pop-up card does not. They are shortened to fit at the normal size, in both places.

Nothing else changed: same art, same voices, same first game.

## Still true from v1.2

- Both games install and boot on a real 3DS. Nobody has played all the way through on hardware yet.
- 76 voice clips stay Japanese, for the reasons in the README.
- The second game's end credits are Japanese, as Capcom shipped them.
- Picture Book, Theme and Editor's Notes in the first game's DLC still bounce back to the menu. Reported upstream as senyarom/tgaa2-en-patch#6.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt, which switching builds can trigger. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games. They aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-1.0.19.cia` / `TGAA2-base-1.0.12.cia` | the update |
| 3 | `TGAA1-DLC-1.0.9.cia` / `TGAA2-DLC-1.0.5.cia` | the DLC |

**Coming from v1.1?** Only the first game's update changed. Install `TGAA1-base-1.0.19.cia` over the old one and you're done; the other three files are the same as v1.1 and are attached here so the set is complete.

## How to tell it took

The first game's title screen reads `ENG 1.0.19` in the top right. `ENG 1.0.18` means v1.1 is still installed; `ENG 1.0.2` means v1.0. The second game still reads `ENG 1.0.12`, the DLC pages `DLC 1.0.8` and `DLC 1.0.5`.

## What's new in v1.2

One fix, in the first game only: **cross-examination statements no longer run into the edge of the text box.**

The statement box is narrower than the ordinary dialogue box, because the ◄ ► arrows that step between statements sit inside it. Every earlier build laid statements out against the wider measurement, so the longest lines in each cross-examination ended on the gold border, or under the arrow, with their last character cut. It was found by watching Episode 1 played on the patched build, screen by screen, and measured from those screenshots.

- **65 statements** across all five episodes re-laid to the real width. 17 only needed their line break moved. 48 were a few words too long for any break to fix and were shortened, each by the smallest edit that fits, keeping the witness's voice and checked against the Japanese. Where a statement is repeated when you press it, the repeat was updated to match.
- Eight words that had a stray space after a hyphen ("Anglo- Japanese", "shifty- looking") are joined.
- One grammatical slip in Capcom's own text ("can been") is corrected.

Nothing else changed: same art, same voices, same second game, same DLC.

## Still true from v1.1

- Both games install and boot on a real 3DS. Nobody has played all the way through on hardware yet.
- 76 voice clips stay Japanese, for the reasons in the README.
- The second game's end credits are Japanese, as Capcom shipped them.
- Picture Book, Theme and Editor's Notes in the first game's DLC still bounce back to the menu. Reported upstream as senyarom/tgaa2-en-patch#6.
- The second game's cross-examinations have not had this width fix yet. They were laid out with the same wide measurement, so expect the same clipped last characters there until the next release.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt, which switching builds can trigger. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.

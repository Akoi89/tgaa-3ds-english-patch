Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games. They aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.1.cia` / `TGAA2-base-1.0.14.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.8.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

**Coming from v1.3?** All four files changed this time. Install all four over the old ones.

## How to tell it took

The first game's title screen reads `ENG 3.2.1` in the top right, the second game's reads `ENG 1.0.14`. The second game's DLC costume banner reads `DLC 1.0.8`. The first game's DLC cover still reads `DLC 1.0.8`; it was not re-stamped for 1.0.10. `ENG 1.0.19` or `ENG 1.0.13` means v1.3 is still installed.

Yes, the first game's number jumped from 1.0.19 to 3.2.1. It is the same patch line. The console stores a version in a field whose last part cannot go above 15, so `1.0.16` and up were never real versions: the file said one thing and the console was told another, and the two had drifted apart. From this release the number on the screen, in the filename and in the console are the same number, and it is higher than every build before it, so it installs over any of them.

## What's new in v1.4

**The first hardware playthrough of the DLC, and what it found.** One tester played both of the second game's DLC stories start to finish on an original 3DS and reported in [issue #1](../../issues/1). Everything they found is fixed here: nine lines that ran off the page, an opening card and a handwritten score sheet that were still Japanese, a profile caption the game had to shrink because it was five lines in a four-line box, and a pop at the end of some shouts. The pop's cause isn't proven, but every shout this project had imported was cut hard at both ends with no fade, unlike Capcom's own, and all 76 of them across both DLCs now end in silence the way Capcom's do. On an emulator they're clean; the tester's next run is the real test.

**Fewer page breaks.** Where the translators had split one of Capcom's pages into two because the English didn't fit at the width they were working to, and the real width turns out to hold it, the page is one again: 26 in the second game's DLC, 114 in the first game's DLC, 1,493 in the first game and 2 in the second. Only breaks with nothing but the standard page tags on them were undone, and only where the joined words fit with room to spare. The ones where the English is genuinely too long for a page stay split.

**The second game's dialogue no longer runs under the page arrow.** Every long line of ordinary conversation was cut at its last word, because the whole game had been wrapped to the edge of the text box when the arrow that ends each line sits inside it. 7,320 pages changed: 5,828 only needed their line break moved, 716 single lines became two, and 776 pages that cannot fit two lines were split into two pages the way Capcom builds a continuation page. Words were never changed. 38 pages are left as they were, on purpose.

**The first game's wide pages.** 66 centred banners, sized text and other widget pages ran past the box edge, some by a lot; 62 are fixed, 4 are left and listed in the README.

**26 more English voices.** Capcom recorded these for *Chronicles* and no build had ever used them: six courtroom and gallery cues in each game, and fourteen reactions during the second game's third-episode Dance of Deduction. The courtroom cues have now been heard in English in both games. The fourteen reactions still haven't; they need that scene played.

**Cosmetic.** The first game's HOME menu icon is the cartridge art instead of a pipe logo. The two optional `.xdelta` files put an English banner and title on the HOME menu itself, by patching your own cartridge dump; the README has the steps and the exact dump sizes it needs.

## Still true from v1.3

- Both games install and boot on a real 3DS. The base games have not been played through on hardware yet; the second game's DLC has.
- Two shouts in the second game's DLC stay Japanese because Capcom never recorded them in English. 77 voice clips stay Japanese in the base games, for the reasons in the README.
- The second game's end credits are Japanese, as Capcom shipped them.
- Picture Book, Theme and Editor's Notes in the first game's DLC still bounce back to the menu. Reported upstream as senyarom/tgaa2-en-patch#6.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt, which switching builds can trigger. Decline it and report it. The tester's switch from v1.2 to this build is the first time that path gets tried on hardware, so if you see the prompt, say so.

**[Report anything wrong in issue #1](../../issues/1)**.

**Superseded by [v1.6](../../releases/tag/v1.6).** Every voice clip in this build clicks at its end on a real console (found and fixed in v1.5), so install v1.6 instead.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.1.cia` / `TGAA2-base-1.0.14.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.8.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

Coming from v1.3, all four files changed. The first game's title screen reads `ENG 3.2.1`, the second game's `ENG 1.0.14`; `ENG 1.0.19` or `ENG 1.0.13` means v1.3 is still installed. The first game's number jumped from 1.0.19 to 3.2.1 because the console stores a version whose last part can't go above 15, so `1.0.16` and up were never real versions; from here the screen, the filename and the console agree.

## What's new in v1.4

The first hardware playthrough of the DLC. One tester played both of the second game's DLC stories start to finish on an original 3DS and reported in [issue #1](../../issues/1). Everything they found is fixed here: nine lines that ran off the page, an opening card and a handwritten score sheet that were still Japanese, a profile caption the game had to shrink, and a pop at the end of some shouts. The pop's cause wasn't proven at this point; every imported shout was given a fade and a silent tail, which turned out not to be it (see v1.5).

Fewer page breaks. Where the translators had split one of Capcom's pages in two because the English didn't fit at the width they were working to, and the real width holds it, the page is one again: 26 in the second game's DLC, 114 in the first game's DLC, 1,493 in the first game and 2 in the second. Only breaks with nothing but the standard page tags were undone, and only where the joined words fit with room to spare.

The second game's dialogue no longer runs under the page arrow. Every long line of ordinary conversation was cut at its last word, because the whole game had been wrapped to the box edge when the arrow sits inside it. 7,320 pages changed: 5,828 only needed their line break moved, 716 single lines became two, and 776 pages that can't fit two lines were split into two pages the way Capcom builds a continuation page. Words were never changed. 38 pages are left as they were, on purpose.

The first game's wide pages: 66 centred banners, sized text and other widget pages ran past the box edge; 62 are fixed, 4 are left and listed in the README.

26 more English voices that Capcom recorded for *Chronicles* and no build had used: six courtroom and gallery cues in each game, and fourteen reactions during the second game's third-episode Dance of Deduction. The courtroom cues have been heard in English in both games; the fourteen reactions haven't, they need that scene played.

Cosmetic: the first game's HOME menu icon is the cartridge art instead of a pipe logo, and the two optional `.xdelta` files put an English banner and title on the HOME menu by patching your own cartridge dump; the README has the steps.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt, which switching builds can trigger. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.

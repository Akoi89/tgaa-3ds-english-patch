Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games. They aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.2.cia` / `TGAA2-base-1.0.15.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

**Prefer patch files?** `TGAA1-3DS-English-v1.5-xdelta.zip` and `TGAA2-3DS-English-v1.5-xdelta.zip` hold rows 2 and 3 as xdelta patches against your own decrypted Japanese dump, plus the HOME banner patch, with a readme that has the commands and hashes. Same result, same install order. Added 6th Sept.

**Coming from v1.4?** All four changed. The first game's DLC keeps its name and version but its cover now reads the real number, `DLC 1.0.10` instead of `DLC 1.0.8`, so it is a different file. Install all four over the old ones.

## How to tell it took

The first game's title screen reads `ENG 3.2.2`, the second game's `ENG 1.0.15`. The DLC pages read `DLC 1.0.10` on the first game's cover and `DLC 1.0.9` on the second game's costume banner. `ENG 3.2.0` or `ENG 1.0.14` means v1.4 is still installed.

If your console is online and offers an update for the second game, decline it. That's Capcom's Japanese update. Consoles offered it because it carried a higher version number than this patch did; from this release the patch outranks it and the offer stops.

## What's new in v1.5

**The pop is found and fixed.** The tester heard a click at the end of shouts in the second game's DLC through two builds, including the one where I'd given every clip a proper fade and silent tail. That wasn't it. A recording of the click made on a second console, lined up against the clip sample by sample, put it a few milliseconds after the clip's last sample, and there was exactly one structural difference left between our files and Capcom's: every voice file Capcom ships ends in a zero trailer that rounds it to a multiple of 32 bytes, and every clip this project or senyarom ever wrote was 8 bytes past that boundary with no trailer. A console reads the last 32 bytes past the end of the file and plays what it finds there. An emulator reads exact sizes and never hears it.

That means the base games had been clicking on real hardware since the first release, on every English shout and voice line that wasn't Capcom's, and nobody had played them there to know. The trailer is now on every replaced stream: 89 in the second game's DLC, 130 in the second game, 123 in the first. The first game's DLC was already aligned. A second recording of the same shout on the same console shows nothing at the clip's end. The recording also settled which file the DLC's scripted shouts play, the base game's copy rather than the DLC's own, which is why fixing the DLC alone had changed nothing.

**Two text fixes from the tester's fourth report**, both in the second game's menus. Episode 1's save-slot title, the longest of the five, ran off the slot's right edge on a console; the "Ep. 1:" label is now drawn a step smaller so the title fits at its normal size, and the chapter line under it no longer gets squeezed. The return-to-title confirmation held the two widest lines of any dialog in the game, so the box squeezed the whole message until the apostrophe vanished; it's re-broken onto four lines, no words changed, and so is its game-over twin. The slot fix was checked on screen. The dialog wasn't, because the long form of that message never came up in testing; if it looks wrong, say so.

**The first game's title screen now says `3.2.1`'s successor, `3.2.2`.** v1.4's first game showed `ENG 3.2.0` although the file was named 3.2.1. Fixed here, and the first game's DLC cover now reads its real number, `DLC 1.0.10`.

**The update offer.** The second game now tells the console it is version 3.0.15, which outranks Capcom's official 1.3.0 update. On v1.4 and earlier an online console would offer that update, and accepting it replaces the English update with the Japanese one.

## Still true from v1.4

- Both games install and boot on a real 3DS. The second game's DLC has been played through on hardware twice; the base games have not.
- Two shouts in the second game's DLC stay Japanese because Capcom never recorded them in English. 77 voice clips stay Japanese in the base games, for the reasons in the README.
- The second game's end credits are Japanese, as Capcom shipped them.
- Picture Book, Theme and Editor's Notes in the first game's DLC still bounce back to the menu. Reported upstream as senyarom/tgaa2-en-patch#6.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it. Installing v1.4 over v1.2 with existing files did not raise it on the tester's console.

**[Report anything wrong in issue #1](../../issues/1)**.

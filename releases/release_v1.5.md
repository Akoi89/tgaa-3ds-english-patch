**Superseded by [v1.6](../../releases/tag/v1.6)**, which changes the two update CIAs only. The files here still install and work.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.2.cia` / `TGAA2-base-1.0.15.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

The `-xdelta.zip` files hold rows 2 and 3 as patches against your own decrypted Japanese dump, and the `JPvoice` zips are the same with Capcom's Japanese audio put back; the README explains both. Coming from v1.4, all four files changed. The first game's title screen reads `ENG 3.2.2`, the second game's `ENG 1.0.15`; `ENG 3.2.0` or `ENG 1.0.14` means v1.4 is still installed.

If your console offers an update for the second game, decline it. That's Capcom's Japanese update; from this release the patch outranks it and the offer stops.

## What's new in v1.5

The pop at the end of shouts is found and fixed. A recording of the click on a second console, lined up against the clip sample by sample, put it a few milliseconds after the clip's last sample. Every voice file Capcom ships ends in a zero trailer that rounds it to a multiple of 32 bytes, and every clip this project or senyarom ever wrote was 8 bytes past that boundary with no trailer, so a console read past the end of the file and played what it found. An emulator reads exact sizes and never hears it. That means the base games had been clicking on real hardware since the first release on every replaced voice line. The trailer is now on all of them: 89 in the second game's DLC, 130 in the second game, 123 in the first. A second recording of the same shout shows nothing at the clip's end.

Two menu fixes in the second game from the tester's fourth report. Episode 1's save-slot title ran off the slot's right edge on a console; its label is drawn a step smaller so the title fits. The return-to-title confirmation was squeezed until its apostrophe vanished; it's re-broken onto four lines, no words changed, and so is its game-over twin. The slot fix was checked on screen, the dialog wasn't, so if it looks wrong, say so.

The first game's title screen now reads `3.2.2` (v1.4 showed `ENG 3.2.0` although the file was named 3.2.1), and its DLC cover reads its real number, `DLC 1.0.10`. The second game now tells the console it is version 3.0.15, which outranks Capcom's official update.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.


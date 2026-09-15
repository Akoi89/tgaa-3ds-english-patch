**Superseded by [v1.7](../../releases/tag/v1.7)**, which changes the first game's update and both DLC files; the second game's update is the same file. The files here still install and work.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.3.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia` | the DLC, unchanged from v1.5 |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

Prefer patch files? `TGAA1-3DS-English-v1.6-xdelta.zip` and `TGAA2-3DS-English-v1.6-xdelta.zip` hold rows 2 and 3 as xdelta patches against your own decrypted Japanese dump, plus the HOME banner patch, with a readme that has the commands and hashes. Same result, same install order.

Japanese voices? `TGAA1-3DS-English-JPvoice-v1.6-xdelta.zip` and `TGAA2-3DS-English-JPvoice-v1.6-xdelta.zip` are the same patches with every audio file put back to Capcom's Japanese, text and art unchanged. Same title versions as the main files, so install one edition or the other. See the README.

Coming from v1.5? Only the two update CIAs changed. The DLC files are the same as v1.5; if you have them installed, leave them.

## How to tell it took

The first game's title screen reads `ENG 3.2.3`, the second game's `ENG 1.0.16`. The DLC pages still read `DLC 1.0.10` and `DLC 1.0.9`. `ENG 3.2.2` or `ENG 1.0.15` means v1.5 is still installed.

## What's new in v1.6

The shout lettering is Capcom's own in both games. The "Objection!" style words that flash on a shout come from eight texture atlases, and both games had been shipping one hand-translated set that left a rotated variant in Japanese, which the first game draws. All eight are now Capcom's Chronicles atlases converted to the 3DS format, every variant English. Two words follow Capcom's wording with it: "Sir!" is "Yes!" and "Hang on!" is "'Scuse me!". The DLC episodes draw from the same files, so they get it too.

Fifteen more of Capcom's English textures are in: the second game's last chapter title card, and text painted onto costumes, evidence objects and two backgrounds, six in the first game and nine in the second. Each is ported in its 3DS format with only the changed blocks re-encoded, so the rest of every texture stays Capcom's bytes. Left alone on purpose: the handwritten narration strokes in the episode openings, two evidence textures whose PC format doesn't decode reliably, and a newspaper that's Russian on both platforms. The full-screen event pictures have no English version anywhere; Chronicles shows them in Japanese too.

The second game's title logo was restored on 7 September. The first `TGAA2-base-1.0.16.cia` uploaded here, and v1.5 before it, drew the fan-made logo instead of Capcom's colour *Resolve* logo that v1.4 had. The update CIA, its xdelta zip and both Japanese-voice zips were replaced in place with that one texture corrected, version numbers unchanged. The Japanese-voice zips from that first fix were built from a stale copy and still carried the old logo, and the first game's zip had the wrong banner patch; both were replaced again early on 8 September (UTC). If your second game's title screen shows a plain cream logo with a long Japanese-style subtitle, or you took a Japanese-voice zip on 7 September, download again. The Japanese-voice edition of v1.6 hasn't been run on a console.

The patch files were replaced on 11 September. The patches inside the four xdelta zips lost a small header that named folders on my PC; they produce exactly the same files, so if you already have them there's nothing to redo. The two loose banner patches are different: the old ones only applied to my own dump and failed on anyone else's with a checksum error. The replacements apply to any decrypted dump. The same two files were replaced on v1.4 and v1.5 as well.

Version bookkeeping: the second game's console-facing version moves from 3.0.15 to 3.1.0, because that field's last part can't go above 15; the screen and filename say 1.0.16. The first game is 3.2.3 everywhere.

## What's known and what's been tested

This build was installed and launched on a New 3DS XL and on an original 3DS, and the patch route in the zips was walked on a New 3DS from a clean install. The second game's DLC has been played through on hardware twice; the base games haven't. What stays Japanese on purpose (two DLC shouts Capcom never recorded, 77 base-game voice clips, the second game's end credits) and the first game's DLC Picture Book bug are listed in the README under "Known, and not worth reporting". The full account of what this patch adds is `DETAILS.md`.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.

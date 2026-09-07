Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games. They aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.3.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia` | the DLC, unchanged from v1.5 |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

**Prefer patch files?** `TGAA1-3DS-English-v1.6-xdelta.zip` and `TGAA2-3DS-English-v1.6-xdelta.zip` hold rows 2 and 3 as xdelta patches against your own decrypted Japanese dump, plus the HOME banner patch, with a readme that has the commands and hashes. Same result, same install order.

**Japanese voices?** `TGAA1-3DS-English-JPvoice-v1.6-xdelta.zip` and `TGAA2-3DS-English-JPvoice-v1.6-xdelta.zip` are the same patches with every audio file put back to Capcom's Japanese, text and art unchanged. Same title versions as the main files, so install one edition or the other. See the README.

**Coming from v1.5?** Only the two update CIAs changed. The DLC files are the same as v1.5; if you have them installed, leave them.

## How to tell it took

The first game's title screen reads `ENG 3.2.3`, the second game's `ENG 1.0.16`. The DLC pages still read `DLC 1.0.10` and `DLC 1.0.9`. `ENG 3.2.2` or `ENG 1.0.15` means v1.5 is still installed.

## What's new in v1.6

**The shout lettering is Capcom's own, in both games.** The big "Objection!" style lettering that flashes when someone shouts comes from eight texture atlases, and both games had been shipping the same set, translated by hand for the fan patch. Two of those atlases hold a second, rotated variant of the word that the set never translated, and the first game draws that variant, so a shout in the first game could still flash Japanese. All eight are now Capcom's Chronicles atlases, converted to the exact 3DS format Capcom's Japanese files use, every variant English. Two of the words change with it to Capcom's official wording: "Sir!" becomes "Yes!" and "Hang on!" becomes "'Scuse me!". Nothing else in either game changed, and the DLC episodes draw their shouts from these same files, so they get it too.

**Fifteen more of Capcom's English textures.** Cross-referencing every texture Capcom made English for Chronicles against the two cartridges turned up a set neither patch had used: the second game's last chapter title card, and text painted onto character costumes, evidence objects and two backgrounds, six in the first game and nine in the second. Each is ported in its 3DS format with only the changed blocks re-encoded, with a base-colour-searching ETC1 encoder, so the rest of every texture stays Capcom's own bytes. Left alone on purpose: the handwritten narration strokes in the episode openings, whose 3DS files carry stroke timing the PC files don't, two evidence textures whose PC format doesn't decode reliably, and a newspaper item that's Russian on both platforms. The event-cut pictures the story shows full screen, newspapers included, have no English version anywhere; Chronicles shows them in Japanese too.

**Version bookkeeping.** The second game's console-facing version moves from 3.0.15 to 3.1.0, because that field's last part cannot go above 15; the screen and filename say 1.0.16. The first game is 3.2.3 everywhere.

## Still true from v1.5

- Both games install and boot on a real 3DS. This build was installed and launched on a New 3DS XL and on an original 3DS, and the patch route in the zips was walked on a New 3DS from a clean install. The second game's DLC has been played through on hardware twice; the base games have not.
- Two shouts in the second game's DLC stay Japanese because Capcom never recorded them in English. 77 voice clips stay Japanese in the base games, for the reasons in the README.
- The second game's end credits are Japanese, as Capcom shipped them.
- Picture Book, Theme and Editor's Notes in the first game's DLC still bounce back to the menu. Reported upstream as senyarom/tgaa2-en-patch#6.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**.

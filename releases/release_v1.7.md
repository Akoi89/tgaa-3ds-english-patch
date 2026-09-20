**Superseded by [v1.8](../../releases/tag/v1.8).** The see-through pages of the first game's DLC Picture Book were repainted by a model in this release and came out blurred; v1.8 redoes them. Only the first game's DLC changed, so if you are on v1.7 you only need `TGAA1-DLC-1.0.12.cia`.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.4.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.11.cia` / `TGAA2-DLC-1.0.10.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

Prefer patch files? `TGAA1-3DS-English-v1.7-xdelta.zip` and `TGAA2-3DS-English-v1.7-xdelta.zip` hold rows 2 and 3 as xdelta patches against your own decrypted Japanese dump, plus the HOME banner patch, with a readme that has the commands and hashes. Same result, same install order.

Japanese voices? `TGAA1-3DS-English-JPvoice-v1.7-xdelta.zip` and `TGAA2-3DS-English-JPvoice-v1.7-xdelta.zip` are the same patches with every audio file put back to Capcom's Japanese, text and art unchanged. Same title versions as the main files, so install one edition or the other. See the README.

Coming from v1.6? In the first game both the update and the DLC changed. In the second game only the DLC changed; `TGAA2-base-1.0.16.cia` is the same file as v1.6, so leave it installed.

## How to tell it took

The first game's title screen reads `ENG 3.2.4`, the second game's `ENG 1.0.16`. The DLC pages read `DLC 1.0.11` and `DLC 1.0.10`. `ENG 3.2.3`, `DLC 1.0.10` on the first game's magazine or `DLC 1.0.9` on the second game's costume banner means part of v1.6 is still installed.

## What's new in v1.7

The first game's DLC Picture Book, Theme and Editor's Notes buttons work. Until now they loaded for a moment and dropped you back at the title screen, in every earlier release and in senyarom's patch. The cause was in the update's code: a DLC status check that senyarom's offline DLC patch already skips in two places was still live in three more, and those three are the ones these screens go through. Those three branches now skip it the same way. Nothing else in the code changed, and Music, Movie and the rest of the DLC list behave as before.

With those screens reachable, what's on them is in English: all 66 Picture Book pages of the art director's commentary, the handwritten notes on the design sheets, the eight theme preview titles and both Editor's Notes pages. There's no official English for any of it (Chronicles has no Picture Book), so this is a new translation from the Japanese, and every name in it follows Capcom's spelling. Where the Japanese sat on a see-through panel over the artwork, the art under it was filled back in rather than blurred over. Brush-written name tags and the tiny production scribbles on the sketches stay Japanese on purpose.

The DLC list icons were redrawn from Capcom's Japanese plate. The old English sheet cut off the bottom of every icon's art, the gramophone's feet and the 3DS's bottom edge among them. The covers for the empty issues 9 to 13 and the Episode 0 cover got the same cleaner fill behind the number and title.

In the second game's DLC, the candidate score sheet's paper was cleaned up: a dark band along its bottom edge and specks left from the Japanese brush strokes are gone. The English lettering on it is exactly as before.

## What's known and what's been tested

Everything new in the first game was installed and checked in Azahar: all 66 Picture Book pages, the eight theme previews and both Editor's Notes pages opened and were read on screen, along with the new covers and icons. None of it has been on a 3DS yet. The second game's score sheet sits deep in the DLC story and was checked in the files only. The Japanese-voice edition of v1.7 hasn't been run on a console. What stays Japanese on purpose is in the README under "Known, and not worth reporting", and the full account of what this patch adds is `DETAILS.md`.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**, especially anything in the Picture Book on real hardware.



Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.4.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.12.cia` / `TGAA2-DLC-1.0.10.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

Prefer patch files? `TGAA1-3DS-English-v1.8-xdelta.zip` and `TGAA2-3DS-English-v1.8-xdelta.zip` hold rows 2 and 3 as xdelta patches against your own decrypted Japanese dump, plus the HOME banner patch, with a readme that has the commands and hashes. Same result, same install order.

Japanese voices? `TGAA1-3DS-English-JPvoice-v1.8-xdelta.zip` and `TGAA2-3DS-English-JPvoice-v1.8-xdelta.zip` are the same patches with every audio file put back to Capcom's Japanese, text and art unchanged. Same title versions as the main files, so install one edition or the other. See the README.

Coming from v1.7? Only the first game's DLC changed. `TGAA1-base-3.2.4.cia`, `TGAA2-base-1.0.16.cia` and `TGAA2-DLC-1.0.10.cia` are the same files as v1.7, so leave those installed.

## How to tell it took

The first game's title screen reads `ENG 3.2.4`, the second game's `ENG 1.0.16`. The DLC pages read `DLC 1.0.12` and `DLC 1.0.10`. `DLC 1.0.11` on the first game's magazine means v1.7's DLC is still installed.

## What's new in v1.8

The see-through pages of the first game's DLC Picture Book look right now. On 29 of the 66 pages the art director's commentary sits on a translucent panel laid over the artwork, and in v1.7 the artwork under and around those panels came out blurred: a smeared band along the top of each panel, characters' legs turned into pale smudges, a grey lump under one page's text. This release redoes all 29.

The cause was in how the Japanese was removed. The mask I grew around each character ended up covering about three quarters of the panel, because Japanese characters sit two to four pixels apart and the mask closed the gaps between them, so the model filling the hole was repainting the whole panel and inventing the picture behind it. The new method never repaints anything. It works out what the panel looks like without the writing, from the pixels that aren't writing, and fades each pixel towards that in proportion to how much darker than it that pixel is. Nothing is invented, so nothing can smear. The text also sits where Capcom's Japanese sat, rather than a few rows lower, which is what left the pale band along the top.

Every row above the first line of text on those 29 pages is now byte-identical to Capcom's own page.

Nothing else changed. The other 47 pages, the theme titles, the Editor's Notes, the covers, the DLC list icons and everything in the second game are the same files as v1.7.

## What's known and what's been tested

All 66 Picture Book pages were opened and read on screen in Azahar on this build, and the DLC list stamp reads `DLC 1.0.12`. None of it has been on a 3DS yet. The theme previews, Editor's Notes and covers weren't re-checked on screen for this release because they are byte-identical to v1.7, where they were. The second game's score sheet sits deep in the DLC story and has only ever been checked in the files. The Japanese-voice edition of v1.8 hasn't been run on a console.

One page still isn't right and I'd rather say so: on the rough sketches page in issue 6, the tips of the pencil hair share pixels with the Japanese writing, and every rule I tried that kept the hair also left readable Japanese behind. The tips stay clipped, the same as in v1.7.

What stays Japanese on purpose is in the README under "Known, and not worth reporting", and the full account of what this patch adds is `DETAILS.md`.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**, especially anything in the Picture Book on real hardware.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

**If you already installed v1.8, you don't need this.** The games are identical. v1.8a exists only because the xdelta patches refused a dump made from a game cartridge, and now they don't.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.4.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.12.cia` / `TGAA2-DLC-1.0.10.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner, see the README |

Prefer patch files? `TGAA1-3DS-English-v1.8a-xdelta.zip` and `TGAA2-3DS-English-v1.8a-xdelta.zip` hold rows 2 and 3 as xdelta patches against your own decrypted Japanese dump, plus the HOME banner patch, with a readme that has the commands and hashes. Same result, same install order.

Japanese voices? `TGAA1-3DS-English-JPvoice-v1.8a-xdelta.zip` and `TGAA2-3DS-English-JPvoice-v1.8a-xdelta.zip` are the same patches with every audio file put back to Capcom's Japanese, text and art unchanged. Same title versions as the main files, so install one edition or the other. See the README.

## On an emulator, use the plain DLC files

If the DLC card shows a padlock and the game returns to the title, or your emulator refuses to install the DLC at all, take `TGAA1-EN-DLC-v1.8a.cia` or `TGAA2-EN-DLC-v1.8a.cia` in place of row 3. Same DLC, same version, same size, with Capcom's encryption taken off the filesystem inside, so the emulator doesn't need AES keys of its own to read it. A console reads either one. The xdelta zips already produce these exact files; these are just the ready made copies. Install one form or the other, not both.

## How to tell it took

The first game's title screen reads `ENG 3.2.4`, the second game's `ENG 1.0.16`. The DLC pages read `DLC 1.0.12` and `DLC 1.0.10`. These are the same numbers as v1.8, because nothing in the games changed.

## What's fixed in v1.8a

If you own the cartridge rather than a digital copy, you can dump the card to `.3ds` and convert it with GodMode9's NCSD image options, Build CIA from file. Until now the update and DLC patches refused the result with `target window checksum mismatch`, and the readme told you that route was untested. Both patches now take it.

Someone hit this, sent me their dump, and it turned out to be my fault rather than theirs. Their decrypted image differs from mine in 2,708 bytes out of 689,790,976, and all of it is header: the card info block in the NCSD header, the game partition's NCCH header and the start of its exheader, and the manual partition's NCCH header. Not one byte of game code or game data is different. GodMode9 just writes those fields differently when it converts a card image, and my patches were being strict about bytes they had no reason to care about. They already ignored a 44 byte random block in the first header for exactly this reason; the window simply wasn't wide enough.

The patch files are between 337 bytes smaller and 714 bytes larger than v1.8's. That's the whole cost.

One thing is deliberately not fixed. The optional HOME banner patch is still strict, and wants a CIA dump of an installed title. Its output is your own game image with the icon swapped, so making it tolerant would mean writing my headers into your file instead of yours, and I'm not shipping that without testing it on a console first. The readme in each zip says so.

## What's been tested

Every patch in this release reproduces its target from my own dump and from two sources with those regions randomised. The first game's two update patches were additionally checked against the reporter's real cartridge-sourced image, and both produce the release file byte for byte. The second game has no cartridge-sourced dump I can test against, so its patches are tolerant by construction rather than by demonstration; if you patch the second game from a card dump, I'd like to hear how it went.

The games themselves are the v1.8 builds and carry v1.8's testing, which is written up in that release.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**, especially anything on real hardware.

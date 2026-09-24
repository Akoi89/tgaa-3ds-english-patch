**Superseded by [v1.8b](../../releases/tag/v1.8b).** v1.8b fixes a crackle in the first game's animated cutscenes. Only the first game's update changed.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**, and Capcom's art. Built on [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they aren't distributed here.

**If you already installed v1.8, you don't need this.** The games are identical.

- **The patches now accept a cartridge dump.** If you own the card rather than a digital copy, you can dump it to `.3ds` and convert it with GodMode9. Until now the update and DLC patches refused the result with `target window checksum mismatch`.
- **That was my fault, not yours.** Someone sent me their dump: it differs from mine in 2,708 bytes out of 689,790,976, and every one of them is header. GodMode9 just writes those fields differently when it converts a card image. Not one byte of game code or game data differs. My patches were being strict about bytes they had no reason to care about.
- **Nothing in the games changed.** The patch files are between 337 bytes smaller and 714 bytes larger, and that's the whole cost.
- **The optional HOME banner patch is still strict** and still wants a CIA dump of an installed title. Its output is your own game image with the icon swapped, so making it tolerant would mean writing my headers into your file instead of yours, and I won't ship that untested on a console.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-3.2.4.cia` / `TGAA2-base-1.0.16.cia` | the update |
| 3 | `TGAA1-DLC-1.0.12.cia` / `TGAA2-DLC-1.0.10.cia` | the DLC |
| 4 | `TGAA1-Base-enbanner.xdelta` / `TGAA2-Base-enbanner.xdelta` | optional HOME menu banner |

- **Prefer patch files?** The `-xdelta.zip` downloads hold rows 2 and 3 as patches against your own decrypted Japanese dump, plus the banner patch, with the commands and hashes in a readme. Same result, same order.
- **Want Japanese voices?** The `-JPvoice-` zips are the same patches with every audio file put back to Capcom's Japanese. Text and art unchanged. Install one edition or the other.
- **On an emulator, if the DLC shows a padlock** or won't install, use `TGAA1-EN-DLC-v1.8a.cia` or `TGAA2-EN-DLC-v1.8a.cia` in place of row 3. Same DLC, with Capcom's encryption taken off the filesystem inside so the emulator doesn't need its own AES keys. A console reads either. Install one form, not both.
- **To check it took:** the title screens read `ENG 3.2.4` and `ENG 1.0.16`, the DLC pages `DLC 1.0.12` and `DLC 1.0.10`. Same numbers as v1.8, because nothing in the games changed.

Every patch here reproduces its target from my own dump and from two sources with those header regions randomised. The first game's update patches were also checked against the reporter's real cartridge image and match byte for byte. The second game has no cartridge dump I can test against, so if you patch it from a card dump, I'd like to hear how it went.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt. Decline it and report it.

**[Report anything wrong in issue #1](../../issues/1)**, especially on real hardware.

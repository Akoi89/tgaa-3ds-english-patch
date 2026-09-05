# English HOME menu banner: how it was done on Puyo Puyo Tetris, for TGAA

Written 2026-09-05 from the Puyo project. Everything here was verified on Puyo
(banner extracted back out of the built CIA byte-identical; picture and sound
confirmed in Azahar by the user). Nothing has been tried on TGAA yet.

## What the banner is

- The HOME menu banner is `banner.bin` in the ExeFS of content 0 (the CXI). It is
  a `CBMD` container: 0x88 header = magic, u32 0, 14 x u32 offsets of
  LZ11-compressed CGFX models (index 0 common, then one per region/language, 0
  when absent), u32 CWAV offset at 0x84. The CWAV (the HOME menu sound) sits at
  the end.
- Every region model carries the same texture (Puyo: 256x128 RGB565, format 3).
  The texture object is `TXOB`: height/width at +0x14/+0x18, PICA format code
  11 words after the magic, data size 15 words after, data pointer 16 words
  after (relative to the pointer's own position).
- The CWAV is usually PCM16 (Puyo: stereo 48 kHz, 2.5 s). Offsets inside its
  INFO section are from the INFO start: rate +0xC, loop end = sample count
  +0x14; each channel's sample block offset is relative to DATA+8.

## Rules that cost a rebuild each

1. The CWAV offset must be 0x20-aligned. The first Puyo build was one byte off
   and the HOME menu played garbage. `banner_build.py` pads for this.
2. The ExeFS is size-locked in the CIA build: `exefs_banner.py` rewrites the
   ExeFS in place (header, file hashes at 0xC0 in reverse entry order, and the
   NCCH superblock hash at 0x1C0) and refuses if the files would not fit. Puyo
   had 1,170 bytes of slack; a smaller banner is fine, a bigger one is not
   unless you shrink something else. Never rebuild the CXI with 3dstool.
3. Keep the original texture format. A third-party banner the user found had
   re-encoded the texture as ETC1A4 from a soft source and looked blurry.
   Sega's own texture was RGB565; swapping only the logo region on Sega's
   texture and re-encoding as RGB565 was visibly sharper.
4. Use the highest-resolution official logo you have (Puyo: Steam's
   `title_e.narc` English logo at 4x), downscale with Lanczos into the slot the
   Japanese logo occupied, keep everything else in the texture untouched.
5. Editing scripts through a bash heredoc turned a `\0` into a real NUL byte
   once. Write scripts with the Write/Edit tools.

## Recipe

```
python banner_extract.py <current game.cia> work_banner
      -> work_banner/banner.bin, icon.bin, banner_tex.png, plus a printout of
         every model's texture size/format, the CWAV format, the SMDH titles
edit work_banner/banner_tex.png (same size) -> banner_new_tex.png
python banner_build.py work_banner/banner.bin banner_new_tex.png banner_new.bin
python banner_cwav.py banner_new.bin english_call.wav banner_new.bin --match-level
      (only if the banner has a sound worth replacing; PCM16 banners only)
python exefs_banner.py <decrypted.cci> banner_new.bin cci_banner.cci
      (partition 0 of a decrypted CCI; keeps the ExeFS size)
then build the CIA from cci_banner.cci exactly as the project does now
      (Puyo: build_cia.py <shell.cia> cci_banner.cci <romfs> <out.cia> <ver>)
verify: extract the banner back out of the built CIA with ctrtool and cmp it
      against banner_new.bin
```

`exefs_banner.py` assumes partition 0 at 0x4000 and asserts it from the NCSD
table; the ExeFS files are re-laid 0x200-aligned in their original order.

## What else changed on Puyo alongside this

- The SMDH icon already had an English short title, so `icon.bin` was left
  alone. If TGAA's is Japanese, the SMDH title strings are UTF-16LE at
  8 + lang*0x200 (short 0x80 bytes, long 0x100, publisher 0x80); the ExeFS
  splicer will carry a changed icon.bin the same way (add it to the files dict).
- LayeredFS cannot change a banner, so this only exists in a built CIA; Puyo
  ships it publicly only as an xdelta against the user's own decrypted dump.

## Files in this folder

banner_extract.py, banner_build.py, banner_cwav.py, exefs_banner.py, and the
codecs they need: comp.py (LZ11), tex.py + etc1a4.py + etc1_enc.py (PICA
texture formats, Morton swizzle), csar.py (CWAV header parsing). ctrtool.exe
is picked up from this folder or the project root.

## TGAA: what was different from Puyo (done 2026-09-05, see `_out\README.md`)

- One model only (index 0, 14 region slots otherwise 0), FOUR textures: 256x256
  ETC1A4 = the logo (transparent plane), 256x256 ETC1 = character atlas, 128x64
  ETC1 and 64x32 ETC1A4 = stand/props. `banner_build.py` matches a TXOB by size
  alone and would hit whichever 256x256 comes first; `banner_build2.py` matches
  size AND format code and re-encodes only the 4x4 blocks that changed.
- Sound is DSP-ADPCM (TGAA1 1.34 s, TGAA2 3.00 s, 32728 Hz stereo); the PCM16
  CWAV swap does not apply and the jingle has no words, so it stays.
- ExeFS slack is 0 bytes in both cartridges: the rebuilt banner must be <= the
  original size rounded up to 0x200. Our LZ11 packs the untouched model 18 bytes
  smaller than Capcom's; the English logo has less detail so the model chunk
  shrank ~7 KB (TGAA1) / ~9.4 KB (TGAA2).
- The base CIAs in `Final\_CURRENT` are title-key encrypted, so `cia.Cia` cannot
  be used as a shell (hash check fails). `cci_to_cia.py` slices the CCI
  partitions and runs `makerom -f cia -ignoresign -ver <ref TMD version>`;
  without -ignoresign makerom reports "Content 0 Is Corrupt".
- The HOME title text comes from the base icon.bin (measured 2026-09-02), so
  `patch_icon_strings.py` copies the 12 SMDH slots from our update's meta SMDH
  into it; `exefs_splice.py` carries banner and icon in one pass.
- Plane aspect: the Japanese glyphs are undistorted in the texture, so texels are
  square on the plane; the English logo is fitted to the same WIDTH (255 px) and
  centred in the old logo's box (TGAA1 255x68 at y 94, TGAA2 254x72 at y 78).
  Not yet seen on hardware.

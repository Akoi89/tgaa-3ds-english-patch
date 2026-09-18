# -*- coding: utf-8 -*-
"""Pack the romhacking.net zips for the v1.5 three-patch shape: one zip per game with the
base, update and DLC xdeltas, xdelta3.exe and a README.txt filled from HASHES_<tag>.txt
(written by build_rhdn_patches_v15.py).

Usage: python make_zips_v15.py [--tag v1.5] [--out _out15]
"""
import argparse
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, '..')
XD = os.path.join(R, 'patches', 'xdelta3.exe')

META = {
    'TGAA1': dict(jp='Dai Gyakuten Saiban: Naruhodou Ryuunosuke no Bouken', en='The Great Ace Attorney: Adventures',
                  tid='0014AD00', ver='ENG 3.2.4', upd='TGAA1-base-3.2.4.cia',
                  dlc_where='the Episode 0 magazine cover, top left', dlc_stamp='DLC 1.0.12',
                  dlc_note="The first game's DLC is a big one: it holds the voice galleries, eleven subtitled commentary videos, the rebuilt magazine covers and a playable extra episode. The videos had to be re-encoded with English subtitles, which is why this DLC patch is about 170 MB: that part is genuinely new data, not a repack."),
    'TGAA2': dict(jp='Dai Gyakuten Saiban 2: Naruhodou Ryuunosuke no Kakugo', en='The Great Ace Attorney 2: Resolve',
                  tid='001AE200', ver='ENG 1.0.16', upd='TGAA2-base-1.0.16.cia',
                  dlc_where='the costume pack banner, bottom right', dlc_stamp='DLC 1.0.10',
                  dlc_note="The second game's DLC holds the two mini episodes and the costumes. Both episodes are fully in English, including their voiced shouts."),
}

README = """{en} ({jp}), Nintendo 3DS
English patch {tag}, as xdelta patches for your own Japanese dump
https://github.com/Akoi89/tgaa-3ds-english-patch

WHAT THIS IS

Capcom's own English localisation from The Great Ace Attorney Chronicles (PC,
2021), carried onto the Japanese 3DS game: text, voices and art, plus the DLC,
which no English release ever had. It builds on senyarom's fan patch
(https://github.com/senyarom/tgaa2-en-patch), which brought Capcom's script
across; this adds the English voices, the DLC, the art and a long list of layout
fixes. The full change list, the known issues and the testing status are in the
README on the GitHub page. This file only covers patching.

Three patches are in this zip, and all three apply to files you make from your
own dumps:

  {g}-{tag}-base.xdelta     your game image       ->  the same game with an English
                             HOME menu banner and title. Code and data untouched.
  {g}-{tag}-update.xdelta   your game image       ->  the English update, as a .cia
                             you install. This is the actual patch.
  {g}-{tag}-DLC.xdelta      your Japanese DLC     ->  the English DLC, as a .cia

The base patch is cosmetic and optional. The update and DLC patches are the
translation. The layout matches how the game is built for the 3DS: a base title,
an update title on top, and a DLC title; installing an update over the Japanese
game is exactly what Capcom's own patch did.

WHAT YOU NEED

1. Your own dump of the Japanese game (title ID 00040000{tid}) as a .cia, and
   your own dump of its Japanese DLC (title ID 0004008C{tid}) as a .cia.
   Dump each title to CIA in GodMode9 with NO decrypt and NO trim option, so
   what you copy to your PC is still encrypted. The DLC was a free eShop
   download; if it is installed on your console, GodMode9 dumps it too.

   THIS IS WHERE PEOPLE GET STUCK. GodMode9 will also hand you a dump it has
   decrypted or trimmed for you, and that file comes out the RIGHT SIZE but is
   not the same bytes. The patch refuses it, and running the decryptor on it
   afterwards does not rescue it. So a size matching the list further down is
   NOT proof your file is the right one. If a patch is refused, redump the title
   encrypted before you change anything else.

   If you own the cartridge rather than a digital copy, you can dump the card to
   .3ds instead and convert it with GodMode9's NCSD image options, Build CIA
   from file. That route works from v1.8a on. A file made that way differs from
   a CIA dump of an installed title in about 2,700 bytes of header and in no
   game data at all, and the update and DLC patches now ignore those bytes. The
   optional base patch does not, and still wants a CIA dump of an installed
   title.

2. "Batch CIA 3DS Decryptor" (matif's batch script around decrypt.exe and
   makerom). Put the encrypted dumps in its folder and run the .bat. The game
   comes out as "<name>-decrypted.cci", the DLC as "<name> (DLC)-decrypted.cia".
   THOSE two files are what the patches apply to. Which build of the decryptor
   you use makes no difference; what matters is that its input was encrypted.

3. xdelta3. xdelta3.exe (3.2.0, Windows) is in this zip; any xdelta3 build works.

APPLY

  xdelta3.exe -d -s "<your game>-decrypted.cci" {g}-{tag}-update.xdelta {upd}

  xdelta3.exe -d -s "<your DLC> (DLC)-decrypted.cia" {g}-{tag}-DLC.xdelta {g}-EN-DLC-{tag}.cia

  optional, for the English HOME menu banner (this one needs a CIA dump of an
  installed title; it will not take a converted cartridge image):
  xdelta3.exe -d -s "<your game>-decrypted.cci" {g}-{tag}-base.xdelta {g}-EN-base-{tag}.cci

Yes, the update patch reads your whole game image and writes a 40 to 90 MB
.cia. Most of the update is files that already exist in the game image, so the
patch itself stays small; the output is the same file the GitHub release ships.

WHAT YOU SHOULD HAVE, AND WHAT I HAD

  your decrypted game .cci  {src_game_size} bytes
  your decrypted DLC .cia   {src_dlc_size} bytes

  The decryptor writes 44 random bytes into the card header of every .cci it
  makes (offsets 0x1010 to 0x103B, a card seed the console never checks on a
  CIA or in an emulator), and clock-seeded ticket bytes into every .cia, so your
  files will not hash-match mine. That is expected. The patches are built so
  those bytes do not matter; everything else has to match. For the record:
    game .cci  sha256 {src_game_sha}
    DLC .cia   sha256 {src_dlc_sha}

  Results, which DO have to match exactly:
    {upd}  {res_upd_size} bytes  sha256 {res_upd_sha}
    {g}-EN-DLC-{tag}.cia  {res_dlc_size} bytes  sha256 {res_dlc_sha}
    {g}-EN-base-{tag}.cci  {res_base_size} bytes  sha256 {res_base_sha}

  If xdelta3 stops with a checksum error, the source is not the decryptor's
  output of a clean dump. Do not force it and do not play a file that came out
  wrong; say so on the issue tracker instead.

INSTALL

Console (CFW): install {upd} and then {g}-EN-DLC-{tag}.cia with FBI, over the
Japanese game you already have. Base first, then update, then DLC. Your saves
stay; they belong to the base title. For the English HOME banner, convert
{g}-EN-base-{tag}.cci to a CIA in GodMode9 (NCSD image options, Build CIA from
file) and install it; it replaces the Japanese base in place and the update and
DLC on top are untouched. If the tile still shows the Japanese name afterwards,
that is the HOME menu's icon cache; a reboot rebuilds it. This whole route, the
GodMode9 conversion included, was walked on a New 3DS from a clean install. If
anything about it misbehaves for you, install the CIAs from the GitHub release
instead and say so on the issue tracker.

Azahar / Citra: File > Install CIA for the update and the DLC, with the
Japanese game already loaded or installed. Remove any older update title of this
patch, or senyarom's, first: the newest installed update is the one that runs,
and the console picks by version number, not by install order.

Back up your save before switching builds. The second game shows a
corrupted-save prompt if it finds data it does not expect, and confirming
that prompt wipes the slots. Decline it.

If your console is online and offers you an update for the game, decline it.
That is Capcom's own Japanese update. This patch's update declares a higher
version than Capcom's so the offer should not appear once it is installed; if
you see it, decline it, and if it was ever accepted, delete the update title
(0004000E{tid}) from Data Management and install this one again.

CHECK IT TOOK

  Title screen, top right     {ver}
  DLC, {dlc_where}   {dlc_stamp}

If the title screen shows an older number, an older update title is still
installed and outranks this one; delete it and install again.

{dlc_note}

REPORT

Anything on real hardware is worth a note, especially a voice that is silent,
cut off or Japanese, and any text that clips or overflows:
https://github.com/Akoi89/tgaa-3ds-english-patch/issues/1

CREDIT

The English text, voices and art are Capcom's, from The Great Ace Attorney
Chronicles. senyarom's patch did the hard part of carrying Capcom's script
onto the 3DS builds. Scarlet Study made the first playable English 3DS build
years earlier and was used as a reference throughout. Tools and scripts are
GPL-3.0 on the GitHub page. If you want Capcom's translation properly, buy
The Great Ace Attorney Chronicles.

The tooling behind this patch was written with LLM assistance (Claude, through
Claude Code), and so was some of the first game's DLC text that Capcom never
made in English. The full statement, including what was generated and what was
not, is in the README on the GitHub page. No generated audio ships.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='v1.5')
    ap.add_argument('--out', default=os.path.join(HERE, '_out15'))
    a = ap.parse_args()
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(a.out, 'HASHES_%s.txt' % a.tag))]
    h = {(g, k, lab): (fn, int(n), c, s) for g, k, lab, fn, n, c, s in rows}
    for g, m in META.items():
        if (g, 'update', 'patch') not in h:
            continue
        f = lambda k, lab: h[(g, k, lab)]  # noqa: E731
        txt = README.format(g=g, tag=a.tag, jp=m['jp'], en=m['en'], tid=m['tid'], ver=m['ver'], upd=m['upd'],
                            dlc_where=m['dlc_where'], dlc_stamp=m['dlc_stamp'], dlc_note=m['dlc_note'],
                            src_game_size='{:,}'.format(f('base', 'source')[1]), src_game_sha=f('base', 'source')[3],
                            src_dlc_size='{:,}'.format(f('DLC', 'source')[1]), src_dlc_sha=f('DLC', 'source')[3],
                            res_upd_size='{:,}'.format(f('update', 'result')[1]), res_upd_sha=f('update', 'result')[3],
                            res_dlc_size='{:,}'.format(f('DLC', 'result')[1]), res_dlc_sha=f('DLC', 'result')[3],
                            res_base_size='{:,}'.format(f('base', 'result')[1]), res_base_sha=f('base', 'result')[3])
        assert f('update', 'result')[0] == m['upd'], (f('update', 'result')[0], m['upd'])
        for ch in txt:
            assert ord(ch) < 128, 'non-ASCII in README: %r' % ch
        rp = os.path.join(a.out, 'README_%s.txt' % g)
        open(rp, 'w', newline='\r\n').write(txt)
        zp = os.path.join(a.out, '%s-3DS-English-%s-xdelta.zip' % (g, a.tag))
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(rp, 'README.txt')
            for k in ('base', 'update', 'DLC'):
                z.write(os.path.join(a.out, f(k, 'patch')[0]), f(k, 'patch')[0])
            z.write(XD, 'xdelta3.exe')
        print(zp, os.path.getsize(zp))


if __name__ == '__main__':
    main()

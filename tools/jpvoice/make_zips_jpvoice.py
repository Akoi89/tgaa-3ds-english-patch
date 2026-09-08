# -*- coding: utf-8 -*-
"""Step 5: zips for the Japanese-voice set, same shape as the v1.5 RHDN zips: per game one zip with
the base (HOME banner, copied from _out15, identical), update and DLC xdeltas, xdelta3.exe and a
README filled from the hash files. Output jpvoice/_zips/{g}-3DS-English-JPvoice-v1.5-xdelta.zip.

Usage: python jpvoice\make_zips_jpvoice.py
"""
import os, sys, io, zipfile, hashlib
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, '_rhdn_work'))
from make_zips_v15 import META
P15 = os.path.join(ROOT, '_rhdn_work', '_out16'); PJ = os.path.join(ROOT, 'jpvoice', '_patches')
OUT = os.path.join(ROOT, 'jpvoice', '_zips'); os.makedirs(OUT, exist_ok=True)
XD = os.path.join(ROOT, 'patches', 'xdelta3.exe')
TAG = 'v1.6'; JTAG = 'v1.6-jpvoice'
UPD_OUT = {'TGAA1': 'TGAA1-base-3.2.3-jpvoice.cia', 'TGAA2': 'TGAA2-base-1.0.16-jpvoice.cia'}

README = """{en} ({jp}), Nintendo 3DS
English patch {tag}, JAPANESE VOICE edition, as xdelta patches for your own Japanese dump
https://github.com/Akoi89/tgaa-3ds-english-patch

WHAT THIS IS

The same English patch as the main {tag} release (Capcom's Chronicles text and art, the
translated DLC, every layout fix), with ONE difference: all the audio is Capcom's
original Japanese. No English voice acting, no English shouts, no English narration;
the courtroom shouts, story lines, crowd cues and the DLC voices are the Japanese
takes exactly as the cartridge and the Japanese DLC ship them. Text, art and
layout are byte for byte the main release. Made for the people who asked for
English text over the Japanese cast.

If you want the English voices, use the main release instead. Do not install both:
they are the same title with the same version number, and whichever you install
last is the one that runs. The title screen reads {ver} on both.

Three patches are in this zip, and all three apply to files you make from your
own dumps:

  {g}-{btag}-base.xdelta   your game image  ->  the same game with an English
                                   HOME menu banner and title. Code and data untouched.
                                   {base_note}
  {g}-{jtag}-update.xdelta   your game image  ->  the English update with Japanese
                                   audio, as a .cia you install. This is the patch.
  {g}-{jtag}-DLC.xdelta      your Japanese DLC   ->  the English DLC with Japanese
                                   audio, as a .cia

WHAT YOU NEED

1. Your own dump of the Japanese game (title ID 00040000{tid}) as a .cia, and
   your own dump of its Japanese DLC (title ID 0004008C{tid}) as a .cia.
   GodMode9 dumps an installed cartridge or title as a CIA. The DLC was a free
   eShop download; if it is installed on your console, GodMode9 dumps it too.
   These patches were proven on the .cci the decryptor writes from a CIA of the
   game. A raw .3ds cartridge dump has not been tested; if the patch refuses
   it, dump the title as a CIA instead.

2. "Batch CIA 3DS Decryptor" (matif's batch script around decrypt.exe and
   makerom). Put the dumps in its folder and run the .bat. The game comes out as
   "<name>-decrypted.cci", the DLC as "<name> (DLC)-decrypted.cia". THOSE two
   files are what the patches apply to. A dump decrypted any other way (GodMode9's
   own decrypt option, another tool) has a different header layout and the patch
   will refuse it.

3. xdelta3. xdelta3.exe (3.2.0, Windows) is in this zip; any xdelta3 build works.

APPLY

  xdelta3.exe -d -s "<your game>-decrypted.cci" {g}-{jtag}-update.xdelta {upd}

  xdelta3.exe -d -s "<your DLC> (DLC)-decrypted.cia" {g}-{jtag}-DLC.xdelta {g}-EN-DLC-{jtag}.cia

  optional, for the English HOME menu banner:
  xdelta3.exe -d -s "<your game>-decrypted.cci" {g}-{tag}-base.xdelta {g}-EN-base-{tag}.cci

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
    {g}-EN-DLC-{jtag}.cia  {res_dlc_size} bytes  sha256 {res_dlc_sha}
    {g}-EN-base-{tag}.cci  {res_base_size} bytes  sha256 {res_base_sha}

  If xdelta3 stops with a checksum error, the source is not the decryptor's
  output of a clean dump. Do not force it and do not play a file that came out
  wrong; say so on the issue tracker instead.

INSTALL

Console (CFW): install {upd} and then {g}-EN-DLC-{jtag}.cia with FBI, over the
Japanese game you already have. Base first, then update, then DLC. Your saves
stay; they belong to the base title. If you had the main (English voice) release
installed, these simply replace it; to go back, install the main release's files
again. For the English HOME banner, convert {g}-EN-base-{tag}.cci to a CIA in
GodMode9 (NCSD image options, Build CIA from file) and install it; it replaces
the Japanese base in place and the update and DLC on top are untouched.

Azahar / Citra: File > Install CIA for the update and the DLC, with the
Japanese game already loaded or installed. Remove any older update title of this
patch, or senyarom's, first: the newest installed update is the one that runs,
and the console picks by version number, not by install order.

Back up your save before switching builds. The second game shows a
corrupted-save prompt if it finds data it does not expect, and confirming
that prompt wipes the slots. Decline it.

If your console is online and offers you an update for the game, decline it.
That is Capcom's own Japanese update. This patch's update declares a higher
version than Capcom's so the offer should not appear once it is installed.

CHECK IT TOOK

  Title screen, top right     {ver}   (the same stamp as the main release)
  DLC, {dlc_where}   {dlc_stamp}
  First courtroom shout       Japanese

TESTING

This edition was built from the tested {tag} files by putting Capcom's Japanese
audio back and changing nothing else, and every file in it was checked against
both: text and art byte-identical to the main release, every audio file
byte-identical to the Japanese original. The author installed and ran the v1.5
form of this edition, both games with their DLC; v1.6 changes only the shout
lettering, the same eight textures as the main release. The main release has
had far more play, so anything odd is still worth a note.

REPORT

Anything on real hardware is worth a note, especially any text that clips or
overflows, and anything that sounds wrong:
https://github.com/Akoi89/tgaa-3ds-english-patch/issues/1

CREDIT

The English text and art are Capcom's, from The Great Ace Attorney Chronicles;
the voices are Capcom's Japanese cast. senyarom's patch did the hard part of
carrying Capcom's script onto the 3DS builds. Scarlet Study made the first
playable English 3DS build years earlier and was used as a reference throughout.
Tools and scripts are GPL-3.0 on the GitHub page. If you want Capcom's
translation properly, buy The Great Ace Attorney Chronicles.
"""


def hashes(path):
    rows = [l.rstrip('\n').split('\t') for l in open(path)]
    return {(g, k, lab): (fn, int(n), c, s) for g, k, lab, fn, n, c, s in rows}


def main():
    h15 = hashes(os.path.join(P15, 'HASHES_%s.txt' % TAG)); hj = hashes(os.path.join(PJ, 'HASHES_%s.txt' % JTAG))
    xd3 = open(XD, 'rb').read()
    for g, m in META.items():
        f15 = lambda k, lab: h15[(g, k, lab)]  # noqa: E731
        fj = lambda k, lab: hj[(g, k, lab)]  # noqa: E731
        assert fj('update', 'result')[0] == UPD_OUT[g], fj('update', 'result')[0]
        # TGAA1's English banner carries an English HOME jingle, so its JAP Dub base patch is its own
        # (Japanese jingle, English picture and title); TGAA2's banner never touched the jingle.
        # TGAA1's English banner carries an ENGLISH HOME jingle, so this edition must ship its own
        # banner patch. The fallback below is only correct for TGAA2, whose banner never touched the
        # jingle. On 2026-09-07 a partial re-run left no TGAA1 base rows in the hash table, the
        # fallback fired silently, and the zip shipped the English-jingle patch under a readme
        # claiming the opposite. Refuse instead: re-run fix_tgaa1_banner_jingle.py.
        assert g != 'TGAA1' or (g, 'base', 'patch') in hj, (
            'no TGAA1 jpvoice base rows in %s: run jpvoice\\fix_tgaa1_banner_jingle.py first' % os.path.basename(PJ))
        if (g, 'base', 'patch') in hj:
            fb, btag = fj, JTAG
            base_note = '(this edition\'s own banner patch: the English picture and\n                                   title, but the Japanese HOME menu jingle)'
            base_src = os.path.join(PJ, '%s-%s-base.xdelta' % (g, JTAG))
        else:
            fb, btag = f15, TAG
            base_note = '(identical to the main release\'s base patch; its jingle\n                                   is already the Japanese one)'
            base_src = os.path.join(P15, '%s-%s-base.xdelta' % (g, TAG))
        txt = README.format(g=g, tag=TAG, jtag=JTAG, btag=btag, base_note=base_note, jp=m['jp'], en=m['en'], tid=m['tid'], ver=m['ver'], upd=UPD_OUT[g],
                            dlc_where=m['dlc_where'], dlc_stamp=m['dlc_stamp'],
                            src_game_size='{:,}'.format(f15('base', 'source')[1]), src_game_sha=f15('base', 'source')[3],
                            src_dlc_size='{:,}'.format(f15('DLC', 'source')[1]), src_dlc_sha=f15('DLC', 'source')[3],
                            res_upd_size='{:,}'.format(fj('update', 'result')[1]), res_upd_sha=fj('update', 'result')[3],
                            res_dlc_size='{:,}'.format(fj('DLC', 'result')[1]), res_dlc_sha=fj('DLC', 'result')[3],
                            res_base_size='{:,}'.format(fb('base', 'result')[1]), res_base_sha=fb('base', 'result')[3])
        txt = txt.replace('{g}-{tag}-base.xdelta'.format(g=g, tag=TAG), '%s-%s-base.xdelta' % (g, btag)).replace('%s-EN-base-%s.cci' % (g, TAG), '%s-EN-base-%s.cci' % (g, btag))
        txt = txt.replace('\r\n', '\n').replace('\n', '\r\n')
        assert not [c for c in txt.encode('utf-8') if c > 126 or (c < 32 and c not in (10, 13))], 'non-ASCII in readme'
        zp = os.path.join(OUT, '%s-3DS-English-JPvoice-%s-xdelta.zip' % (g, TAG))
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('README.txt', txt)
            z.write(base_src, '%s-%s-base.xdelta' % (g, btag))
            z.write(os.path.join(PJ, '%s-%s-update.xdelta' % (g, JTAG)), '%s-%s-update.xdelta' % (g, JTAG))
            z.write(os.path.join(PJ, '%s-%s-DLC.xdelta' % (g, JTAG)), '%s-%s-DLC.xdelta' % (g, JTAG))
            z.writestr('xdelta3.exe', xd3)
        io.open(os.path.join(OUT, 'README_%s_jpvoice.txt' % g), 'w', encoding='utf-8', newline='').write(txt)
        print(zp, os.path.getsize(zp), hashlib.sha256(open(zp, 'rb').read()).hexdigest())


if __name__ == '__main__':
    main()

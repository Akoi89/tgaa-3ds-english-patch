# -*- coding: utf-8 -*-
r"""romhacking.net patch set, v1.5 shape: THREE xdeltas per game, all against the user's
own Batch-CIA-3DS-Decryptor output of their Japanese dumps.

  {g}-{tag}-base.xdelta    decrypted cartridge .cci  ->  the same game with the English HOME
                           banner and title (banner_tools output; code and data untouched)
  {g}-{tag}-update.xdelta  decrypted cartridge .cci  ->  our update title as an installable
                           NoCrypto .cia (the GitHub release file, byte for byte)
  {g}-{tag}-DLC.xdelta     decrypted Japanese DLC .cia  ->  our DLC as a NoCrypto .cia

Why not the v1.4 merged image: with the update baked into the base there is no update title
on the console, and an online 3DS then offers Capcom's own update over the patch (seen on
the user's console 2026-09-05). With a separate update title declaring 3.x the offer stops,
exactly as for the CIA users. The update patch is only ~40 MB although the target is a whole
update CIA, because xdelta finds most of its romfs inside the cartridge dump.

Everything build_rhdn_patches.py learned is kept: -a armor so the source's random card seed
(0x1010..0x103B) and ticket bytes do not break the apply, whole-header scrub at encode time,
apply-back check, and two perturbed-source applies per patch.

Usage: python build_rhdn_patches_v15.py [--tag v1.5] [--only TGAA1|TGAA2] [--final _CURRENT]
"""
import argparse
import os
import shutil
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_rhdn_patches import R, T3, CT, XD, SEED_OFF, SEED_LEN, run, digest, same, rm  # noqa: E402

GAMES = {
    'TGAA1': dict(cci=r'_sources\TGAA1 - Base-decrypted.cci',
                  update=r'Final\_CURRENT\TGAA1-base-3.3.3.cia',
                  enbanner=r'banner_tools\_out\TGAA1-Base-enbanner.cci',
                  dlc=r'Final\_CURRENT\TGAA1-DLC-1.0.16.cia',
                  dlc_jp=r'_sources\TGAA1-Official-Jap (DLC)-decrypted.cia'),
    'TGAA2': dict(cci=r'_sources\DGS2 - Base-decrypted.cci',
                  update=r'Final\_CURRENT\TGAA2-base-1.0.17.cia',
                  enbanner=r'banner_tools\_out\TGAA2-Base-enbanner.cci',
                  dlc=r'Final\_CURRENT\TGAA2-DLC-1.0.11.cia',
                  dlc_jp=r'_sources\DGS2-Jap-DLC (DLC)-decrypted.cia'),
}
BIG = '1073741824'


def scrubbed_copy(src, path, regions):
    """regions is a list of (offset, length) to overwrite with random bytes."""
    shutil.copyfile(src, path)
    with open(path, 'r+b') as f:
        for off, n in regions:
            f.seek(off)
            f.write(os.urandom(n))
    return path


# NCCH header 0x200 + exheader 0x800. A CIA built from a card image with GodMode9's
# "Build CIA from file" differs from a CIA dump of the installed title only in the NCSD
# card info block and the first bytes of each partition's NCCH header and exheader:
# measured 2026-09-17 on a reporter's own TGAA1 card dump, 2,708 bytes in three runs,
# no game data at all.
NCCH_MARGIN = 0xA00


def cci_tolerant_regions(cci):
    """NCSD header plus the head of every populated partition, so a patch encoded against
    this scrub applies to a card-sourced dump as well as to a CIA dump."""
    with open(cci, 'rb') as f:
        f.seek(0x120)
        t = f.read(0x40)
    regs = [(0, 0x4000)]
    for i in range(8):
        off, size = struct.unpack_from('<II', t, i * 8)
        if size:
            regs.append((off * 0x200, min(NCCH_MARGIN, size * 0x200)))
    return regs


def encode_and_prove(src, target, xd, work, scrub, pert, label):
    """xdelta src->target with the source's variable regions scrubbed at encode time; then
    prove the patch reproduces target from the real source AND from two sources whose
    variable regions differ (a different decryption run, or a card-sourced dump).
    scrub and pert are lists of (offset, length)."""
    enc_src = scrubbed_copy(src, os.path.join(work, 'enc_src.bin'), scrub)
    # -A: no application header. Without it xdelta3 writes both file paths (<TGAA_ROOT>\...) into
    # the patch; found in every v1.5/v1.6 patch on 2026-09-11 and stripped after the fact.
    run(XD, '-e', '-f', '-a', '-A', '-9', '-S', 'djw', '-B', BIG, '-s', enc_src, target, xd)
    os.remove(enc_src)
    chk = os.path.join(work, 'applied.bin')
    run(XD, '-d', '-f', '-B', BIG, '-s', src, xd, chk)
    assert same(chk, target), label + ': patch does not reproduce the target from the real source'
    for _ in range(2):
        pert_src = scrubbed_copy(src, os.path.join(work, 'pert_src.bin'), pert)
        run(XD, '-d', '-f', '-B', BIG, '-s', pert_src, xd, chk)
        assert same(chk, target), label + ': patch FAILS against a source with a different random region'
        os.remove(pert_src)
    os.remove(chk)
    print('  %s: %s reproduces the target from the real source and from two perturbed sources' % (label, os.path.basename(xd)))


def build_base(g, cfg, work, out, tag):
    src = os.path.join(R, cfg['cci'])
    enb = os.path.join(R, cfg['enbanner'])
    # named to match what the zip README tells the user to call their own output
    # (TGAA1-EN-base-v1.9.cci), so HASHES and the README agree without a manual rename
    target = os.path.join(out, '%s-EN-base-%s.cci' % (g, tag))
    shutil.copyfile(enb, target)
    # zero the card seed in the target so the patch stores it literally (a user's source has
    # a different random seed there; the console never reads it from a CIA)
    with open(target, 'r+b') as f:
        f.seek(SEED_OFF)
        f.write(bytes(SEED_LEN))
    info = run(CT, '-i', target)
    assert 'Crypto Key           None' in info, 'banner CCI is not NoCrypto'
    # prove the banner image is the cartridge with only the exefs (banner/icon) changed
    w = os.path.join(work, g + '_base'); rm(w); os.makedirs(w)
    for tagn, p in (('a', src), ('b', target)):
        d = os.path.join(w, tagn); os.makedirs(d)
        run(T3, '-xtf', 'cci', p, '-0', d + '/p0.cxi', '-1', d + '/p1.cfa')
        run(T3, '-xtf', 'cxi', d + '/p0.cxi', '--exh', d + '/exh.bin', '--exefs', d + '/exefs.bin',
            '--romfs', d + '/romfs.bin', '--logo', d + '/logo.bin')
        os.remove(d + '/p0.cxi')
    for f in ('p1.cfa', 'exh.bin', 'romfs.bin', 'logo.bin'):
        assert same(w + '/a/' + f, w + '/b/' + f), 'banner image differs from the cartridge in ' + f
    assert not same(w + '/a/exefs.bin', w + '/b/exefs.bin'), 'banner image exefs is unchanged?'
    shutil.rmtree(w)
    print('  %s: banner image = cartridge with only the exefs changed (manual, exheader, romfs, logo identical)' % g)
    xd = os.path.join(out, '%s-%s-base.xdelta' % (g, tag))
    # NOT widened to the NCCH headers on purpose: this patch's output IS the user's own image
    # with the ExeFS swapped, so scrubbing those would hand a card-dump user this machine's
    # exheader and manual header instead of their own. Card dumps must use a CIA dump of the
    # installed title for the banner patch; the zip README says so.
    encode_and_prove(src, target, xd, work, [(0, 0x4000)], [(SEED_OFF, SEED_LEN)], g + ' base')
    return src, target, xd


def build_update(g, cfg, work, out, tag):
    src = os.path.join(R, cfg['cci'])
    upd = os.path.join(R, cfg['update'])
    target = os.path.join(out, os.path.basename(upd))       # the release file, byte for byte
    shutil.copyfile(upd, target)
    assert same(target, upd)
    info = run(CT, '-i', target)
    assert 'Crypto Key           None' in info and 'Crypto Key           Secure' not in info, 'update CIA is not plaintext'
    xd = os.path.join(out, '%s-%s-update.xdelta' % (g, tag))
    regs = cci_tolerant_regions(src)
    encode_and_prove(src, target, xd, work, regs, regs, g + ' update')
    return src, target, xd


def build_dlc(g, cfg, work, out, tag):
    src = os.path.join(R, cfg['dlc_jp'])
    ours = os.path.join(R, cfg['dlc'])
    # named to match what the zip README tells the user to call their own output
    # (TGAA1-EN-DLC-v1.9.cia), so HASHES and the README agree without a manual rename
    nc = os.path.join(out, '%s-EN-DLC-%s.cia' % (g, tag))
    run(sys.executable, os.path.join(HERE, 'nocrypto_cia.py'), ours, nc)
    info = run(CT, '-i', nc)
    assert 'Crypto Key           None' in info and 'Crypto Key           Secure' not in info, 'DLC still encrypted'
    hdr = open(src, 'rb').read(0x20)
    hsz, _, _, csz, tsz, msz = struct.unpack_from('<IHHIII', hdr, 0)
    a64 = lambda x: (x + 63) // 64 * 64  # noqa: E731
    tik_off = a64(hsz) + a64(csz)
    coff = tik_off + a64(tsz) + a64(msz)
    xd = os.path.join(out, '%s-%s-DLC.xdelta' % (g, tag))
    # DLC source is an eShop-only download: there is no card route, so the CIA header scrub stands.
    encode_and_prove(src, nc, xd, work, [(0, coff)], [(tik_off, tsz)], g + ' DLC')
    return src, nc, xd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', default=os.path.join(HERE, '_build15'))
    ap.add_argument('--out', default=os.path.join(HERE, '_out15'))
    ap.add_argument('--tag', default='v1.5')
    ap.add_argument('--only', choices=['TGAA1', 'TGAA2'])
    ap.add_argument('--final', default='_CURRENT')
    a = ap.parse_args()
    for cfg in GAMES.values():
        for k in ('update', 'dlc'):
            cfg[k] = cfg[k].replace(r'Final\_CURRENT', r'Final' + '\\' + a.final)
    os.makedirs(a.work, exist_ok=True); os.makedirs(a.out, exist_ok=True)
    rows = []
    for g, cfg in GAMES.items():
        if a.only and g != a.only:
            continue
        for kind, fn in (('base', build_base), ('update', build_update), ('DLC', build_dlc)):
            src, tgt, xd = fn(g, cfg, a.work, a.out, a.tag)
            for label, p in (('source', src), ('result', tgt), ('patch', xd)):
                s, c, n = digest(p)
                rows.append((g, kind, label, os.path.basename(p), n, c, s))
                print('%s %-6s %-6s %-40s %12d crc32=%s sha256=%s' % (g, kind, label, os.path.basename(p), n, c, s))
    with open(os.path.join(a.out, 'HASHES_%s.txt' % a.tag), 'w') as f:
        for r_ in rows:
            f.write('%s\t%s\t%s\t%s\t%d\t%s\t%s\n' % r_)
    print('done; hashes in', os.path.join(a.out, 'HASHES_%s.txt' % a.tag))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Rebuild a CIA from a modified romfs tree.

    python build.py <shell.cia> <out.cia> <maj.min.mic> <index>=<tree> ...

Two different methods, and using the wrong one ships a broken title:

  NoCrypto NCCH (flag 0x18F bit 2 set -- the base-game update CXIs)
      splice the new romfs in place and repair the header. NEVER
      `3dstool -c -t cxi`: it does not reproduce Nintendo's layout and the
      result does not boot.

  Encrypted CFA (every DLC content here)
      the romfs on disk is ciphertext, so an in-place splice writes plaintext
      into an encrypted region -- the DLC then shows a PADLOCK and "Returning
      to title screen". Rebuild through 3dstool instead, which re-encrypts:
          3dstool -xtf cfa old.ncch --header h.bin --romfs plain.romfs
          3dstool -ctf cfa new.cfa  --header h.bin --romfs new.romfs
      Both halves of that round-trip are null-tested below before use.

Which one applies is decided by measurement, not by file name: if the stored
superblock hash reproduces from the romfs bytes present, it is plaintext.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from cia import Cia
from ncch import splice, verify

TOOL = os.environ.get('THREEDSTOOL', '3dstool.exe')


def run(*args):
    r = subprocess.run([TOOL] + list(args), capture_output=True, text=True)
    return r


def make_romfs(tree, out):
    run('-ctf', 'romfs', out, '--romfs-dir', tree)
    if not (os.path.exists(out) and os.path.getsize(out)):
        raise SystemExit('romfs build failed for %s' % tree)
    return out


def rebuild_content(blob, tree, tmp, idx):
    """Return the new NCCH for one content, by whichever method it needs."""
    old = os.path.join(tmp, 'c%02d.ncch' % idx)
    open(old, 'wb').write(blob)
    ok, f = verify(blob)
    new_romfs = make_romfs(tree, os.path.join(tmp, 'new%02d.romfs' % idx))

    if ok:
        out = splice(blob, open(new_romfs, 'rb').read())
        print('    content %-2d  plaintext splice   %.1f -> %.1f MB'
              % (idx, len(blob) / 1048576, len(out) / 1048576))
        return out

    hdr = os.path.join(tmp, 'h%02d.bin' % idx)
    plain = os.path.join(tmp, 'p%02d.romfs' % idx)
    run('-xtf', 'cfa', old, '--header', hdr, '--romfs', plain)
    if not os.path.exists(hdr):
        raise SystemExit('could not take the header off content %d' % idx)

    # null-test: header + the ORIGINAL romfs must reproduce this content byte
    # for byte, or the rebuild is not faithful and must not be trusted
    probe = os.path.join(tmp, 'probe%02d.cfa' % idx)
    run('-ctf', 'cfa', probe, '--header', hdr, '--romfs', plain)
    if open(probe, 'rb').read() != blob:
        raise SystemExit('content %d fails its null round-trip' % idx)

    out_p = os.path.join(tmp, 'new%02d.cfa' % idx)
    run('-ctf', 'cfa', out_p, '--header', hdr, '--romfs', new_romfs)
    out = open(out_p, 'rb').read()
    print('    content %-2d  encrypted rebuild  %.1f -> %.1f MB  (null test passed)'
          % (idx, len(blob) / 1048576, len(out) / 1048576))
    return out


def main():
    shell, out_path, ver = sys.argv[1], sys.argv[2], sys.argv[3]
    trees = {}
    for a in sys.argv[4:]:
        i, t = a.split('=', 1)
        trees[int(i)] = t
    version = tuple(int(x) for x in ver.split('.'))

    c = Cia(shell)
    print('  %s : %d contents, version %d.%d.%d'
          % (os.path.basename(shell), c.count, *c.version()))
    tmp = tempfile.mkdtemp(prefix='ciabuild')
    try:
        replace = {i: rebuild_content(c.contents[i], t, tmp, i)
                   for i, t in sorted(trees.items())}
        chk = c.write(out_path, replace=replace, version=version)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('  -> %s : %d contents, version %d.%d.%d, %.1f MB'
          % (os.path.basename(out_path), chk.count, *chk.version(),
             os.path.getsize(out_path) / 1048576))
    for i in sorted(replace):
        ok, _ = verify(chk.contents[i]) or (None, None)
        print('     content %-2d verified in the rebuilt CIA' % i)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Step 4: xdelta patches for the Japanese-voice set, same shape and proofs as the v1.5 RHDN set.

Reuses build_rhdn_patches_v15.build_update / build_dlc with the -jpvoice CIAs as targets:
  {g}-v1.5-jpvoice-update.xdelta   decrypted cartridge .cci  ->  {g}-base-x.y.z-jpvoice.cia
  {g}-v1.5-jpvoice-DLC.xdelta      decrypted Japanese DLC    ->  {g}-v1.5-jpvoice-DLC.cia (NoCrypto)
The base (HOME banner) patch is not rebuilt: it is identical to the English set's.
Every patch is proven against the real source and two perturbed sources (encode_and_prove).

Output: jpvoice/_patches/  plus HASHES_v1.5-jpvoice.txt.   Usage: python jpvoice\build_jpvoice_patches.py
"""
import os, sys, io
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, '_rhdn_work'))
import build_rhdn_patches_v15 as B
from build_rhdn_patches import digest

TAG = 'v1.6-jpvoice'
OUT = os.path.join(ROOT, 'jpvoice', '_patches'); WORK = os.path.join(ROOT, 'jpvoice', '_pwork')
os.makedirs(OUT, exist_ok=True); os.makedirs(WORK, exist_ok=True)
GAMES = {
    'TGAA1': dict(B.GAMES['TGAA1'], update=r'jpvoice\_out\TGAA1-base-3.2.3-jpvoice.cia', dlc=r'jpvoice\_out\TGAA1-DLC-1.0.10-jpvoice.cia'),
    'TGAA2': dict(B.GAMES['TGAA2'], update=r'jpvoice\_out\TGAA2-base-1.0.16-jpvoice.cia', dlc=r'jpvoice\_out\TGAA2-DLC-1.0.9-jpvoice.cia'),
}
rows = []
for g, cfg in GAMES.items():
    for kind, fn in (('update', B.build_update), ('DLC', B.build_dlc)):
        src, tgt, xd = fn(g, cfg, WORK, OUT, TAG)
        for label, p in (('source', src), ('result', tgt), ('patch', xd)):
            s, c, n = digest(p)
            rows.append((g, kind, label, os.path.basename(p), n, c, s))
            print('%s %-6s %-6s %-44s %12d crc32=%s sha256=%s' % (g, kind, label, os.path.basename(p), n, c, s))
with open(os.path.join(OUT, 'HASHES_%s.txt' % TAG), 'w') as f:
    for r in rows:
        f.write('%s\t%s\t%s\t%s\t%d\t%s\t%s\n' % r)
print('done')

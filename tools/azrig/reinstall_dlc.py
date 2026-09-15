# -*- coding: utf-8 -*-
"""Reinstall a DLC CIA over the installed one when the version is unchanged (`azahar -i` is a silent
no-op then). Every installed <content id>.app is overwritten with the CIA's content of that id, and the
installed .tmd with the CIA's TMD. Azahar must be closed. Backs up what it replaces.

    python reinstall_dlc.py <cia> <title_id_low>      e.g. Final/_new/TGAA1-DLC-1.0.11.cia 0014ad00
"""
import hashlib
import os
import shutil
import struct
import sys
import time

sys.path.insert(0, r'G:\Claude\TGAA 1-2\testimony_pipeline')
from cia import Cia  # noqa: E402

cia_path, tid = sys.argv[1], sys.argv[2]
D = os.path.join(os.environ['APPDATA'], 'AzaharPlus', 'sdmc', 'Nintendo 3DS', '0' * 32, '0' * 32, 'title', '0004008c', tid, 'content')
c = Cia(cia_path)
tmd = bytes(c.raw[c.tmd:c.tmd + c.sizes['tmd']])
sig = struct.unpack('>I', tmd[:4])[0]
hdr = {0x10003: 0x240, 0x10004: 0x140, 0x10005: 0x80}[sig]
count = struct.unpack('>H', tmd[hdr + 0x9E:hdr + 0xA0])[0]
chunks = hdr + 0xC4 + 64 * 0x24
ids = [struct.unpack('>I', tmd[chunks + i * 0x30:chunks + i * 0x30 + 4])[0] for i in range(count)]
assert len(ids) == len(c.contents), (len(ids), len(c.contents))
installed = {}
for root, _, fs in os.walk(D):
    for f in fs:
        installed[f.lower()] = os.path.join(root, f)
bk = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_dlcbackup_%s_%s' % (tid, time.strftime('%Y%m%d_%H%M%S')))
os.makedirs(bk)
ok = 0
for cid, blob in zip(ids, c.contents):
    name = '%08x.app' % cid
    path = installed.get(name)
    assert path, 'installed content %s not found' % name
    shutil.copy2(path, bk)
    open(path, 'wb').write(blob)
    ok += hashlib.sha256(open(path, 'rb').read()).digest() == hashlib.sha256(blob).digest()
tmds = [p for n, p in installed.items() if n.endswith('.tmd')]
assert len(tmds) == 1, tmds
shutil.copy2(tmds[0], bk)
open(tmds[0], 'wb').write(tmd)
print('%d/%d contents written and verified, TMD replaced (%s); backup %s' % (ok, len(ids), os.path.basename(tmds[0]), bk))

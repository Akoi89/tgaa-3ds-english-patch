# -*- coding: utf-8 -*-
"""Make the title screens show the real patch version.

TGAA1: the stamp is a NUL-terminated string in the (uncompressed) .code of the
update CXI, a 12-byte slot holding 'ENG 1.0.2'. Patch it in place, then repair the
exefs per-file sha256 (exefs header) and the NCCH exefs superblock hash (0x1C0,
covering the first exefs hash-region = the header); Cia.write repairs the rest.

TGAA2: the stamp is painted into the loose title atlas
UI/4_menu/40_title/tex/title_jpn_01_BM_NOMIP_HQ.tex, sprite x312..400 y176..200,
grey (122,121,118) Segoe UI text peaking at alpha 233. Re-render it.

    python stamp_title_versions.py code <in.cia> <out.cia> "ENG 1.0.18" [tmd maj.min.mic]
    python stamp_title_versions.py tex  <atlas.tex> <out.tex> "ENG 1.0.12"
"""
import os
import hashlib
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cia import Cia
import tex_rgba8

MU = 0x200
FONT = os.environ.get('TGAA_STAMP_FONT', r'C:\Windows\Fonts\segoeui.ttf')
STAMP_REGION = (312, 176, 400, 200)     # x0, y0, x1, y1 in the atlas
STAMP_ANCHOR = (318, 176)
STAMP_FILL = (239, 235, 229)      # same look as the DLC stamps: light fill, dark 1 px outline
STAMP_OUTLINE = (15, 10, 8)        # (the fan's flat grey 122,121,118 at alpha 233 blended into the courtroom)
SLOT_LEN = 12


def _exefs_files(d, ex_off):
    hdr = d[ex_off:ex_off + 0x200]
    out = []
    for i in range(10):
        name = bytes(hdr[i * 16:i * 16 + 8]).rstrip(b'\0')
        off, sz = struct.unpack_from('<II', hdr, i * 16 + 8)
        if name:
            out.append((i, name, off, sz))
    return out


def patch_code(ncch, text):
    d = bytearray(ncch)
    ex_off = struct.unpack_from('<I', d, 0x1A0)[0] * MU
    ex_hash_mu = struct.unpack_from('<I', d, 0x1A8)[0]
    if not (d[0x18F] & 4):
        raise SystemExit('CXI is not NoCrypto; refusing to patch ciphertext')
    if d[0x200 + 0xD] & 1:
        raise SystemExit('.code is compressed; refusing')
    idx, name, off, sz = [f for f in _exefs_files(d, ex_off) if f[1] == b'.code'][0]
    start = ex_off + 0x200 + off
    code = bytes(d[start:start + sz])
    k = code.find(b'ENG 1.0.')
    if k < 0:
        raise SystemExit('stamp string not found in .code')
    new = text.encode('ascii') + b'\0'
    if len(new) > SLOT_LEN:
        raise SystemExit('stamp does not fit the %d-byte slot' % SLOT_LEN)
    old = code[k:k + SLOT_LEN]
    d[start + k:start + k + SLOT_LEN] = new + b'\0' * (SLOT_LEN - len(new))
    h = hashlib.sha256(bytes(d[start:start + sz])).digest()
    d[ex_off + 0x200 - (idx + 1) * 32:ex_off + 0x200 - idx * 32] = h
    d[0x1C0:0x1E0] = hashlib.sha256(bytes(d[ex_off:ex_off + ex_hash_mu * MU])).digest()
    return bytes(d), old.split(b'\0')[0].decode()


def verify_code(ncch):
    ex_off = struct.unpack_from('<I', ncch, 0x1A0)[0] * MU
    ex_hash_mu = struct.unpack_from('<I', ncch, 0x1A8)[0]
    hdr = ncch[ex_off:ex_off + 0x200]
    ok = hashlib.sha256(ncch[ex_off:ex_off + ex_hash_mu * MU]).digest() == ncch[0x1C0:0x1E0]
    found = None
    for i, name, off, sz in _exefs_files(ncch, ex_off):
        blob = ncch[ex_off + 0x200 + off:ex_off + 0x200 + off + sz]
        ok = ok and hashlib.sha256(blob).digest() == hdr[0x200 - (i + 1) * 32:0x200 - i * 32]
        if name == b'.code':
            k = blob.find(b'ENG 1.0.')
            found = blob[k:k + SLOT_LEN].split(b'\0')[0].decode()
    return ok, found


def stamp_tex(tex, text):
    rgb, al = tex_rgba8.decode_rgba8(tex)
    a = np.dstack([rgb, al]).astype(np.float32)
    x0, y0, x1, y1 = STAMP_REGION
    a[y0:y1, x0:x1] = 0
    f = ImageFont.truetype(FONT, 15)
    im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ax, ay = STAMP_ANCHOR[0] - x0, STAMP_ANCHOR[1] - y0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                d.text((ax + dx, ay + dy), text, font=f, fill=STAMP_OUTLINE + (255,))
    d.text((ax, ay), text, font=f, fill=STAMP_FILL + (255,))
    a[y0:y1, x0:x1] = np.asarray(im).astype(np.float32)
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex, a8[..., :3], a8[..., 3]), a8


if __name__ == '__main__':
    mode, src, dst, text = sys.argv[1:5]
    if mode == 'code':
        c = Cia(src)
        new, old = patch_code(c.contents[0], text)
        ver = tuple(int(x) for x in sys.argv[5].split('.')) if len(sys.argv) > 5 else None
        c.write(dst, replace={0: new}, version=ver)
        chk = Cia(dst)
        ok, found = verify_code(chk.contents[0])
        print('  %s: code stamp %r -> %r, exefs hashes %s, TMD %d.%d.%d'
              % (os.path.basename(dst), old, found, 'OK' if ok else 'BROKEN', *chk.version()))
    else:
        tex = open(src, 'rb').read()
        new, _ = stamp_tex(tex, text)
        open(dst, 'wb').write(new)
        print('  stamped %s -> %s' % (text, dst))

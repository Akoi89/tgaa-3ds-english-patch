# -*- coding: utf-8 -*-
"""TGAA1-base-3.2.4 = the released 3.2.3 plus the DLC Picture Book / Theme / Editor's Notes bounce fix.

    python build_tgaa1_324_bounce.py <TGAA1-base-3.2.3.cia> <out TGAA1-base-3.2.4.cia>

Changes to .code, nothing else:
  * three `beq ok-path` -> `b ok-path` after the AOC status check 0x48BB34 (root cause, live-traced
    2026-09-14: dlc_story_audit/bounce/make_bounce_ips.py has the full explanation), the same form
    senyarom used at 0x1CC384;
  * the title-screen stamp literal "ENG 3.2.3" -> "ENG 3.2.4".
TMD title version 3.2.3 -> 3.2.4. ExeFS file hash, ExeFS superblock hash and the CIA/TMD chain are
repaired (patch_code_string's method) and re-verified; the result is compared with the input so that
exactly the intended bytes of .code differ and every other content is byte-identical.
"""
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cia import Cia                               # noqa: E402
from patch_code_string import exefs_files, MU     # noqa: E402

CODE_BASE = 0x100000
WORDS = [(0x1CB050, 0x0A000084, 0xEA000084),
         (0x1CB230, 0x0A00000C, 0xEA00000C),
         (0x1C9998, 0x0A000006, 0xEA000006)]
STAMP_OLD, STAMP_NEW = b'ENG 3.2.3', b'ENG 3.2.4'
VERSION_OLD, VERSION_NEW = (3, 2, 3), (3, 2, 4)


def patch_ncch(ncch):
    d = bytearray(ncch)
    assert d[0x100:0x104] == b'NCCH' and d[0x18F] & 4, 'content 0 is not NoCrypto'
    exo, files = exefs_files(d)
    hreg = struct.unpack_from('<I', d, 0x1A8)[0] * MU
    for i, name, start, size in files:
        if name != b'.code':
            continue
        code = bytearray(d[start:start + size])
        assert len(code) == 4775936, 'unexpected .code size %d (compressed?)' % len(code)
        for addr, old, new in WORDS:
            got = struct.unpack_from('<I', code, addr - CODE_BASE)[0]
            assert got == old, 'at %x found %08x, expected %08x' % (addr, got, old)
            struct.pack_into('<I', code, addr - CODE_BASE, new)
        assert bytes(code).count(STAMP_OLD) == 1, 'stamp %r not found exactly once' % STAMP_OLD
        code = bytearray(bytes(code).replace(STAMP_OLD, STAMP_NEW))
        d[start:start + size] = code
        d[exo + 0x200 - (i + 1) * 0x20:exo + 0x200 - i * 0x20] = hashlib.sha256(bytes(code)).digest()
        break
    else:
        raise SystemExit('no .code in ExeFS')
    d[0x1C0:0x1E0] = hashlib.sha256(bytes(d[exo:exo + hreg])).digest()
    return bytes(d)


def code_of(ncch):
    exo, files = exefs_files(ncch)
    for i, name, start, size in files:
        if name == b'.code':
            return ncch[start:start + size]


def verify(src, out):
    a, b = Cia(src), Cia(out)
    assert b.version() == VERSION_NEW, b.version()
    assert len(a.contents) == len(b.contents)
    for k in range(1, len(a.contents)):
        assert a.contents[k] == b.contents[k], 'content %d changed' % k
    na, nb = a.contents[0], b.contents[0]
    # ExeFS hashes
    exo, files = exefs_files(nb)
    hreg = struct.unpack_from('<I', nb, 0x1A8)[0] * MU
    assert hashlib.sha256(nb[exo:exo + hreg]).digest() == nb[0x1C0:0x1E0], 'ExeFS superblock hash bad'
    for i, name, start, size in files:
        assert hashlib.sha256(nb[start:start + size]).digest() == nb[exo + 0x200 - (i + 1) * 0x20:exo + 0x200 - i * 0x20], name
    # byte diff of the whole content 0: only .code bytes, the ExeFS header hash slot and 0x1C0..0x1E0
    ca, cb = code_of(na), code_of(nb)
    diff = [i for i in range(len(ca)) if ca[i] != cb[i]]
    want = set()
    for addr, old, new in WORDS:
        for j in range(4):
            if struct.pack('<I', old)[j] != struct.pack('<I', new)[j]:
                want.add(addr - CODE_BASE + j)
    s = ca.find(STAMP_OLD)
    for j in range(len(STAMP_OLD)):
        if STAMP_OLD[j] != STAMP_NEW[j]:
            want.add(s + j)
    assert set(diff) == want, 'unexpected .code diff: %d bytes vs %d intended' % (len(diff), len(want))
    code_start = [st for i, n, st, sz in files if n == b'.code'][0]
    other = [i for i in range(len(na)) if na[i] != nb[i] and not (code_start <= i < code_start + len(ca))
             and not (exo <= i < exo + 0x200) and not (0x1C0 <= i < 0x1E0)]
    assert not other, 'content 0 differs outside .code and its hashes at %d places' % len(other)
    return len(diff)


def main():
    src, out = sys.argv[1], sys.argv[2]
    c = Cia(src)
    assert c.version() == VERSION_OLD, 'input is %d.%d.%d, expected 3.2.3' % c.version()
    c.write(out, replace={0: patch_ncch(c.contents[0])}, version=VERSION_NEW)
    n = verify(src, out)
    h = hashlib.sha256(open(out, 'rb').read()).hexdigest()
    print('%s: version 3.2.4, %d .code bytes changed (3 branches + stamp), all other contents identical, '
          'ExeFS + TMD chain verified; sha256 %s, %d bytes' % (os.path.basename(out), n, h, os.path.getsize(out)))


if __name__ == '__main__':
    main()

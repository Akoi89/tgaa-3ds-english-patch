# -*- coding: utf-8 -*-
"""TGAA1 DLC Picture Book / Theme / Editor's Notes bounce-back: IPS for the update's code.bin.

Root cause (live-traced 2026-09-14, notes in CONTINUE_HERE): the DLC screen's viewer paths call
0x48BB34 ("AOC status byte 0x16 != 0") and on nonzero store error 2 and switch the screen to
mode 5, whose click handler finds the viewer gate 0x4D7 unset and exits to the title. senyarom's
patch_tgaa1_dlc_offline.py bypasses this same check in two machines (0x1C90D4, 0x1CC384) but not
in these three. On his Azahar the byte read 0; on ours a background request (code 21) leaves it 5.

Each patch turns `beq <ok-path>` into `b <ok-path>`, the form senyarom used at 0x1CC384.

    python make_bounce_ips.py <out.ips> [<code.bin to verify against>]
"""
import struct
import sys

BASE = 0x100000
PATCHES = [
    # mode 7 (Picture Book and the other type 2/3/4 buttons), sub-state 3
    (0x1CB050, 0x0A000084, 0xEA000084),
    # mode 7, sub-state 7 (the same check on the second pass)
    (0x1CB230, 0x0A00000C, 0xEA00000C),
    # mode 10 (type 9 button)
    (0x1C9998, 0x0A000006, 0xEA000006),
]


def main():
    out = sys.argv[1]
    if len(sys.argv) > 2:
        code = open(sys.argv[2], 'rb').read()
        for addr, old, new in PATCHES:
            got = struct.unpack_from('<I', code, addr - BASE)[0]
            assert got == old, 'at %x found %08x, expected %08x' % (addr, got, old)
        print('verified %d sites against %s' % (len(PATCHES), sys.argv[2]))
    ips = bytearray(b'PATCH')
    for addr, old, new in PATCHES:
        off = addr - BASE
        ips += struct.pack('>I', off)[1:] + struct.pack('>H', 4) + struct.pack('<I', new)
    ips += b'EOF'
    open(out, 'wb').write(ips)
    print('wrote %s (%d bytes, %d records)' % (out, len(ips), len(PATCHES)))


if __name__ == '__main__':
    main()

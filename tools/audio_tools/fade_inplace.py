# -*- coding: utf-8 -*-
"""Give already-fitted .mca voice streams clean edges without changing their audio length.

The only size change allowed is Capcom's zero trailer: the output is padded to a 32-byte
multiple (pad32 rule, 2026-09-06; an 8-mod-32 file clicks at its end on hardware). When that
grows a file, its .stqr row is resynced through fit_slots.sync_index.

The TGAA1 DLC streams were fitted to Capcom's exact byte slot by fit_slots.py, which
trims at a 150-LSB threshold with no fade, so they start and end on a small step
(up to 0.9% of peak). A stream may not grow past its slot (it gets cut off in play),
so no audio is appended. This applies a 5 ms fade-in and a 10 ms fade-out to the
existing samples and re-encodes with the same header, rate and sample count; only
the zero trailer described above can change the byte length.

    python fade_inplace.py <en-tree> <jp-tree> [--apply]

Only files that differ from Capcom's copy in <jp-tree> are touched.
"""
import glob
import os
import sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mca                                       # noqa: E402
from import_t2dlc_shouts import encode           # noqa: E402
from fit_slots import sync_index                 # noqa: E402

FADE_IN, FADE_OUT = 0.005, 0.010


def main():
    en, jp = sys.argv[1], sys.argv[2]
    apply_ = '--apply' in sys.argv
    n = done = 0
    for p in sorted(glob.glob(os.path.join(en, '**', '*.mca'), recursive=True)):
        rel = os.path.relpath(p, en)
        jpp = os.path.join(jp, rel)
        d = open(p, 'rb').read()
        if os.path.exists(jpp) and open(jpp, 'rb').read() == d:
            continue
        n += 1
        h = mca.parse_bytes(d)
        pcm = np.asarray(mca.decode(h), dtype=np.float64)
        rate = h['rate']
        fi, fo = int(rate * FADE_IN), int(rate * FADE_OUT)
        pcm[:fi] *= np.linspace(0.0, 1.0, fi, endpoint=False)
        pcm[-fo:] *= np.linspace(1.0, 0.0, fo, endpoint=False)
        out = encode(d, np.clip(np.rint(pcm), -32768, 32767).astype(np.int16), rate)
        # fit_slots padded the file to Capcom's exact slot; keep that length and keep the
        # original header word for word (only the coefficient/gain block at 0x38..0x60 is new)
        target = len(d) + (-len(d)) % 32              # the old length, 32-aligned
        assert len(out) <= target, (rel, len(out), target)
        out = bytearray(out + bytes(target - len(out)))
        out[:0x38] = d[:0x38]
        out[0x60:h['hdr_end']] = d[0x60:h['hdr_end']]   # header tail only, not the +0x34 zero gap
        out = bytes(out)
        assert len(out) == target and len(out) % 32 == 0
        h2 = mca.parse_bytes(out)
        assert h2['samples'] == h['samples'] and h2['rate'] == h['rate']
        chk = np.asarray(mca.decode(h2), dtype=np.int32)
        pk = max(1, abs(chk).max())
        print('  %-58s %6.2fs  first %.1f%%  last-50 %.1f%%  size %d%s' % (
            rel[-58:], h['samples'] / rate, abs(int(chk[0])) * 100.0 / pk, abs(chk[-50:]).max() * 100.0 / pk,
            len(out), '' if abs(chk[0]) == 0 and abs(chk[-50:]).max() == 0 else '  <-- NOT ZERO'))
        if apply_:
            open(p, 'wb').write(out)
            done += 1
            if len(out) != len(d):
                hits = sync_index(os.path.dirname(p), os.path.basename(p)[:-4], len(out), h2['samples'], h2['rate'])
                print('      grew %d -> %d bytes (trailer), %d index row%s resynced' % (len(d), len(out), hits, '' if hits == 1 else 's'))
                if hits == 0:
                    raise SystemExit('%s grew but no .stqr row in %s names it: the index is now stale, sync it '
                                     'by hand (base-game layout keeps the index one level above wav/)' % (rel, os.path.dirname(p)))
    print('%d replaced streams, %d written%s' % (n, done, '' if apply_ else '  (dry run)'))


if __name__ == '__main__':
    main()

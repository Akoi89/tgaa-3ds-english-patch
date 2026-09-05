# -*- coding: utf-8 -*-
"""Give already-fitted .mca voice streams clean edges WITHOUT changing their length.

The TGAA1 DLC streams were fitted to Capcom's exact byte slot by fit_slots.py, which
trims at a 150-LSB threshold with no fade, so they start and end on a small step
(up to 0.9% of peak). A stream may not grow past its slot (it gets cut off in play),
so unlike the TGAA2 DLC shouts nothing can be appended. This applies a 5 ms fade-in
and a 10 ms fade-out to the existing samples and re-encodes with the same header,
rate and sample count, so the file size and the .stqr record stay identical.

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
        assert len(out) <= len(d), (rel, len(out), len(d))
        out = bytearray(out + bytes(len(d) - len(out)))
        out[:0x38] = d[:0x38]
        out[0x60:h['data_off']] = d[0x60:h['data_off']]
        out = bytes(out)
        assert len(out) == len(d)
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
    print('%d replaced streams, %d written%s' % (n, done, '' if apply_ else '  (dry run)'))


if __name__ == '__main__':
    main()

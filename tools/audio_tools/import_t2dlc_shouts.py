# -*- coding: utf-8 -*-
"""Import Capcom's English shouts into TGAA2's two DLC mini-episodes.

Those episodes shipped with 34 Japanese character shouts over English text --
Naruhodo, Sholmes, Susato, Iris, Gregson and the rest -- because this set was
never imported. Capcom's English recording exists for every one of the 34.

The shouts live inside .arc archives, not loose on disk. That matters twice:
the audit that walks '*.mca' never saw them, and the archive rebuild recomputes
every entry offset, so a replacement may change size freely.

SIZE POLICY. A *streamed* clip larger than Capcom's original is cut off in-game
at an unpredictable point (see fit_slots.py). Archive entries are on a different
load path: no .stqr names them, and the archive carries its own entry table which
is rebuilt with our sizes, so the stale-external-size mechanism has nothing to
work with. Capcom also ships 163 KB entries in these same archives against our
largest at 33 KB.

So the default is FULL QUALITY, and an entry that outgrows Capcom's is reported
rather than quietly degraded. 33 of the 34 fit at full rate regardless; the one
that does not is 2.5s of continuous speech in a 1.39s entry, and fitting it would
mean 12 kHz -- below telephone quality for a shout. The same recording already
ships oversized in TGAA1's base game, so this adds no new class of exposure.

Pass --fit to lower the rate instead, if the archive rule is ever shown to apply.

    python import_t2dlc_shouts.py --report
    python import_t2dlc_shouts.py --apply
    python import_t2dlc_shouts.py --apply --fit
"""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

import dsp
import mca
from dgs2tool.arc import parse_arc, build_arc_bytes
from encode_shouts import decode_wav, steam_english
from fit_slots import trim_edges, resample

TREE = os.path.join(ROOT, 'bounce', 't2rev')
QUIET = 150


def encode(donor, pcm, rate):
    """Rebuild one .mca around Capcom's header, at `rate`."""
    h = mca.parse_bytes(donor)
    adpcm, coefs = dsp.encode(np.asarray(pcm, dtype=np.int16))
    size = (len(adpcm) + 63) // 64 * 64
    d = bytearray(donor[:h['data_off']])
    struct.pack_into('<I', d, 0x0C, len(pcm))
    struct.pack_into('<I', d, 0x10, rate)
    struct.pack_into('<I', d, 0x20, size)
    struct.pack_into('<16h', d, 0x38, *coefs)
    struct.pack_into('<4h', d, 0x58, h['gain'], h['ps'], 0, 0)
    d += adpcm + bytes(size - len(adpcm))
    return bytes(d)


def plan():
    """One job per (archive, entry) that has an English recording."""
    jobs = []
    for dirpath, _, files in os.walk(TREE):
        for fn in sorted(files):
            if not fn.endswith('.arc'):
                continue
            path = os.path.join(dirpath, fn)
            arc = parse_arc(open(path, 'rb').read())
            for e in arc['entries']:
                if e.data[:4] != b'MADP':
                    continue
                src = steam_english(e.name)
                if not src:
                    continue
                h = mca.parse_bytes(e.data)
                pcm = trim_edges(decode_wav(src, h['rate']))
                room = len(e.data) - h['data_off']
                need = (len(pcm) // 14 * 8 + 63) // 64 * 64
                rate = h['rate']
                if need > room and '--fit' in sys.argv:
                    rate = int((room // 64 * 64) // 8 * 14 / (len(pcm) / h['rate']))
                jobs.append(dict(arc=path, name=e.name, short=e.name.split('/')[-1],
                                 donor=e.data, src=src, pcm=pcm, rate=rate,
                                 base_rate=h['rate'], was=len(e.data),
                                 jp=h['samples'] / h['rate'],
                                 en=len(pcm) / h['rate']))
    return jobs


def main():
    jobs = plan()
    if not jobs:
        print('no Japanese shouts with an English recording found')
        return
    apply_ = '--apply' in sys.argv
    cut = [j for j in jobs if j['rate'] != j['base_rate']]
    grew = {j['short']: j for j in jobs
            if (len(j['pcm']) // 14 * 8 + 63) // 64 * 64 + 104 > j['was']}
    print('%d shout entries to replace (%d distinct clips)'
          % (len(jobs), len({j['short'] for j in jobs})))
    print('%d at full rate; %d rate-reduced to fit\n'
          % (len(jobs) - len(cut), len(cut)))
    for j in cut:
        print('   REDUCED %-38s %d Hz (%.0f%%)  %.2fs kept whole'
              % (j['short'][:38], j['rate'], j['rate'] * 100.0 / j['base_rate'], j['en']))
    for s, j in sorted(grew.items()):
        if j['rate'] == j['base_rate']:
            print('   LARGER  %-38s English %.2fs vs Capcom %.2fs entry -- shipped whole'
                  % (s[:38], j['en'], j['jp']))
    if not apply_:
        print('\n--report only; run with --apply to write')
        return

    by_arc = {}
    for j in jobs:
        blob = encode(j['donor'], resample(j['pcm'], j['base_rate'], j['rate']), j['rate'])
        assert blob[:4] == b'MADP'
        by_arc.setdefault(j['arc'], {})[j['name']] = blob
    print()
    for path, repl in sorted(by_arc.items()):
        arc = parse_arc(open(path, 'rb').read())
        out = build_arc_bytes(arc, repl)
        open(path, 'wb').write(out)
        print('   %-28s %d entr%s replaced' % (os.path.basename(path), len(repl),
                                               'y' if len(repl) == 1 else 'ies'))
    print('\n%d entries written across %d archives' % (len(jobs), len(by_arc)))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Prove the DSP-ADPCM encoder before trusting it with anything.

Takes Capcom's own .mca files, decodes them, re-encodes with our encoder, and
decodes that. If the encoder is correct the second decode tracks the first
closely (high SNR). A broken encoder gives SNR near zero or negative.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'arc_tools'))

import dsp
import mca
from arc import entries, decomp

SEP = chr(92)


def decode_bytes(adpcm, coefs, nsamples, h1=0, h2=0):
    h = {'coef': list(coefs), 'adpcm': adpcm, 'samples': nsamples,
         'h1': h1, 'h2': h2}
    return mca.decode(h)


def snr(ref, test):
    n = min(len(ref), len(test))
    a = ref[:n].astype(np.float64)
    b = test[:n].astype(np.float64)
    noise = ((a - b) ** 2).mean()
    if noise == 0:
        return float('inf')
    return 10.0 * np.log10((a ** 2).mean() / noise)


def run(pairs):
    print('%-32s %8s %10s %10s %8s' %
          ('file', 'samples', 'SNR(dB)', 'maxerr', 'sec'))
    results = []
    for name, blob in pairs:
        h = mca.parse_bytes(blob)
        ref = mca.decode(h)
        t0 = time.time()
        adpcm, coefs = dsp.encode(ref)
        el = time.time() - t0
        got = decode_bytes(adpcm, coefs, h['samples'])
        s = snr(ref, got)
        n = min(len(ref), len(got))
        maxerr = int(np.abs(ref[:n].astype(np.int32) - got[:n].astype(np.int32)).max())
        results.append(s)
        print('%-32s %8d %10.2f %10d %8.1f' % (name, h['samples'], s, maxerr, el))
    if results:
        print('\nmean SNR %.2f dB   min %.2f dB' %
              (sum(results) / len(results), min(results)))
    return results


if __name__ == '__main__':
    arcs = ['chr040_jpn.arc', 'chr100_jpn.arc']
    root = os.path.join(HERE, '..', 'basegame', 'rom', 'archive')
    pairs = []
    for a in arcs:
        _, _, es, _ = entries(os.path.join(root, a))
        for e in es:
            if '_v_' in e['name'] and (SEP + 'wav' + SEP) in e['name']:
                d = decomp(e)
                if d[:4] == b'MADP':
                    pairs.append((e['name'].split(SEP)[-1], d))
    run(pairs[:int(sys.argv[1]) if len(sys.argv) > 1 else 3])

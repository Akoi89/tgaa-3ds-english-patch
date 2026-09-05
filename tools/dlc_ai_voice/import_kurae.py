# -*- coding: utf-8 -*-
"""Encode a supplied "Take that!" into the TGAA2 DLC's two loose .mca shouts.

WHAT THIS IS FOR. `chr100_asg_v_kurae_jpn.mca` (Kazuma) and
`chr010_hms_v_kurae_jpn.mca` (Hosonaga) are the only two voices in the DLC that
are still Japanese over English text. They are not a porting oversight: Capcom
recorded no English "Take that" for either character, because the DLC's role
reversal -- Kazuma at the defence bench -- exists nowhere in Chronicles.
Verified again by `extract_reference.py`; the only English kurae masters are
chr000_nhd, chr032_sst and chr101_mkt.

So the audio has to come from outside Capcom's recordings. This tool does not
create it. It takes a wav you supply in `synth/` and encodes it into the game.
Anything built with it is a SYNTHESISED performance, not Capcom's, and the two
builds are kept apart for exactly that reason -- see build_variants.py.

THESE TWO ARE LOOSE FILES, not archive entries. That is why the shout audit
missed them (it walks chr*.arc members), and it also means the archive rule in
import_t2dlc_shouts.py -- "an entry may change size freely, the table is
rebuilt" -- does NOT obviously apply. No .stqr names them either, so the
streamed-slot rule is not proven to apply either. Both loose replacements this
project already ships came out SMALLER than Capcom's, so growth has never been
tested here. The default is therefore to refuse to grow the file;
--allow-growth is an explicit opt-in for someone who has tested it on hardware.

In practice it should not bind: the Japanese slots are 1.32s and 1.33s, and
Capcom's own English "Take that" runs 0.65-0.81s.

    python import_kurae.py --tree <idx2 tree>            # report only
    python import_kurae.py --tree <idx2 tree> --apply
"""
import argparse
import os
import struct
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))

import dsp
import mca
from resample import resample

SYNTH = os.path.join(HERE, 'synth')
QUIET = 150             # matches fit_slots.QUIET
MAX_GAIN = 2.0          # +6 dB ceiling, matches encode_shouts.MAX_GAIN

TARGETS = {
    'chr100_asg_v_kurae_jpn.mca': 'chr100_asg_v_kurae.wav',    # Kazuma
    'chr010_hms_v_kurae_jpn.mca': 'chr010_hms_v_kurae.wav',    # Hosonaga
}


def read_wav(path):
    """16-bit PCM wav -> (mono int16 array, rate). Anything else is refused."""
    with wave.open(path, 'rb') as w:
        if w.getsampwidth() != 2:
            raise SystemExit('%s: %d-bit, needs 16-bit PCM'
                             % (path, w.getsampwidth() * 8))
        rate, ch = w.getframerate(), w.getnchannels()
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2')
    if ch > 1:
        pcm = pcm.reshape(-1, ch).mean(axis=1).round().astype(np.int16)
    return pcm, rate


def trim_edges(pcm):
    nz = np.nonzero(np.abs(np.asarray(pcm)) > QUIET)[0]
    return np.asarray(pcm)[nz[0]:nz[-1] + 1] if len(nz) else np.asarray(pcm)


def match_peak(pcm, ref_peak):
    """Sit at the same loudness in the 3DS mix as the Japanese take it replaces."""
    x = np.asarray(pcm, dtype=np.float64)
    peak = np.abs(x).max()
    if peak > 0 and ref_peak > 0:
        x *= min(ref_peak / peak, MAX_GAIN)
    return np.clip(np.rint(x), -32768, 32767).astype(np.int16)


def encode(donor, pcm, rate):
    """Rebuild one .mca around Capcom's header. Same recipe as import_t2dlc_shouts."""
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


def plan(tree):
    jobs = []
    sound = os.path.join(tree, 'sound')
    for name, wav in sorted(TARGETS.items()):
        dst = os.path.join(sound, name)
        if not os.path.exists(dst):
            raise SystemExit('%s not found -- is --tree really an idx2 romfs?' % dst)
        donor = open(dst, 'rb').read()
        h = mca.parse_bytes(donor)
        job = dict(name=name, path=dst, donor=donor, rate=h['rate'],
                   was=len(donor), jp=h['samples'] / h['rate'],
                   ref_peak=int(np.abs(mca.decode(h)).max()),
                   src=os.path.join(SYNTH, wav))
        if os.path.exists(job['src']):
            pcm, srate = read_wav(job['src'])
            pcm = trim_edges(resample(pcm, srate, h['rate']))
            job['pcm'] = match_peak(pcm, job['ref_peak'])
            job['en'] = len(pcm) / h['rate']
            job['srate'] = srate
        jobs.append(job)
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tree', required=True, help='the DLC idx2 romfs tree')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--allow-growth', action='store_true',
                    help="permit an .mca larger than Capcom's; untested on hardware")
    a = ap.parse_args()

    jobs = plan(a.tree)
    for j in jobs:
        if 'pcm' not in j:
            print('   NO SOURCE  %-30s expected %s'
                  % (j['name'], os.path.relpath(j['src'], HERE)))
    jobs = [j for j in jobs if 'pcm' in j]
    if not jobs:
        raise SystemExit('\nnothing to import: put your wavs in %s' % SYNTH)

    fail = False
    for j in jobs:
        need = 104 + (len(j['pcm']) // 14 * 8 + 63) // 64 * 64
        j['will'] = need
        flag = ''
        if need > j['was']:
            flag = "  LARGER THAN CAPCOM'S (+%d bytes)" % (need - j['was'])
            fail = not a.allow_growth
        print('   %-30s %.2fs from %d Hz, into a %.2fs slot, %d -> %d bytes%s'
              % (j['name'], j['en'], j['srate'], j['jp'], j['was'], need, flag))
    if fail:
        raise SystemExit('\nrefusing to grow a loose .mca: no build has ever tested it.\n'
                         'Shorten the take, or pass --allow-growth and test on hardware.')
    if not a.apply:
        print('\n--report only; run with --apply to write')
        return

    print()
    for j in jobs:
        blob = encode(j['donor'], j['pcm'], j['rate'])
        assert blob[:4] == b'MADP'
        open(j['path'], 'wb').write(blob)
        # read it back and confirm the header describes what is actually there
        h = mca.parse(j['path'])
        assert h['samples'] == len(j['pcm']) and h['rate'] == j['rate']
        assert h['data_size'] == len(h['adpcm'])
        print('   wrote %-30s %d bytes, %.2fs @ %d Hz, header verified'
              % (j['name'], os.path.getsize(j['path']), h['samples'] / h['rate'],
                 h['rate']))


if __name__ == '__main__':
    main()

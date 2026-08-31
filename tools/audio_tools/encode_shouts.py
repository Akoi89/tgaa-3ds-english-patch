# -*- coding: utf-8 -*-
"""Replace TGAA1's 81 Japanese courtroom shouts with Chronicles' English ones.

The 3DS keeps these inside per-character archives:
    archive/chrNNN_jpn.arc  ->  sound/se/go_se_chrNNN/wav/chrNNN_xxx_v_TYPE_jpn
Chronicles ships an English counterpart for every one of them at
    nativeDX11x64/sound/se/go_se_chrNNN/wav/chrNNN_xxx_v_TYPE_eng.xsew
which is a plain RIFF/MS-ADPCM wave, so ffmpeg reads it directly.

32 of the 81 English clips are LONGER than the 3DS slot (up to +1.18 s on the
jury's "Not guilty!"), so a fixed-size rebuild would cut them off mid-word.
Nothing actually forces the old size: the MADP header carries the sample count
and data size, the archive entry can be any length, and the romfs is rebuilt
anyway. So each file is sized to its own content. The shout ONSET still lines
up, because every clip starts at sample 0.

Peak level is matched to the original Japanese clip (gain capped at +6 dB) so
the shout sits at the same loudness in the 3DS mix.

    python encode_shouts.py            # dry run: report coverage only
    python encode_shouts.py --apply    # write rebuilt archives to out/
"""
import os
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

import dsp
import mca
from dgs2tool.arc import parse_arc, build_arc_bytes

FF = os.environ.get('FFMPEG', 'ffmpeg')   # set FFMPEG if it is not on PATH
# Chronicles PC install: point TGAAC_STEAM at .../nativeDX11x64
STEAM = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'se')
ARCDIR = os.path.join(ROOT, 'basegame', 'rom', 'archive')
OUTDIR = os.path.join(HERE, 'out')
MAX_GAIN = 2.0          # +6 dB ceiling, so a quiet take is not blown up


def steam_english(entry_name):
    """3DS entry name -> the matching Chronicles _eng.xsew path, or None."""
    base = entry_name.replace('\\', '/').split('/')[-1]
    base = base.rsplit('.', 1)[0] if '.' in base else base
    if not base.endswith('_jpn'):
        return None
    folder = None
    parts = entry_name.replace('\\', '/').split('/')
    for p in parts:
        if p.startswith('go_se_') or p.startswith('bb_se_'):
            folder = p
    if folder is None:
        return None
    p = os.path.join(STEAM, folder, 'wav', base[:-4] + '_eng.xsew')
    return p if os.path.exists(p) else None


def decode_wav(path, rate):
    """Any ffmpeg-readable file -> mono int16 numpy array at `rate`."""
    out = subprocess.run(
        [FF, '-v', 'error', '-i', path, '-f', 's16le', '-acodec', 'pcm_s16le',
         '-ac', '1', '-ar', str(rate), '-'],
        capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode('utf-8', 'replace')[:300])
    return np.frombuffer(out.stdout, np.int16)


def fit(eng, target_len, ref_peak):
    """Level-match to the original's peak. Length is left alone."""
    x = eng.astype(np.float64)
    peak = np.abs(x).max()
    if peak > 0 and ref_peak > 0:
        x *= min(ref_peak / peak, MAX_GAIN)
    x = np.clip(x, -32768, 32767).astype(np.int16)
    return x, len(x) > target_len


def rebuild_mca(original, pcm):
    """Keep Capcom's header, resize the payload to fit the new audio."""
    h = mca.parse_bytes(original)
    adpcm, coefs = dsp.encode(pcm)
    # Capcom pads the payload past the frames it needs; keep that habit
    size = (len(adpcm) + 63) // 64 * 64
    d = bytearray(original[:h['data_off']])
    struct.pack_into('<I', d, 0x0C, len(pcm))          # sample count
    struct.pack_into('<I', d, 0x20, size)              # data size
    struct.pack_into('<16h', d, 0x38, *coefs)
    struct.pack_into('<4h', d, 0x58, h['gain'], h['ps'], 0, 0)
    d += adpcm + bytes(size - len(adpcm))
    # prove it reads back as what we meant
    chk = mca.parse_bytes(bytes(d))
    assert chk['samples'] == len(pcm) and chk['rate'] == h['rate']
    assert len(chk['adpcm']) == size
    return bytes(d)


def main(apply=False):
    arcs = sorted(f for f in os.listdir(ARCDIR) if f.endswith('.arc'))
    todo = []
    for f in arcs:
        blob = open(os.path.join(ARCDIR, f), 'rb').read()
        arc = parse_arc(blob)
        hits = [e for e in arc['entries']
                if '_v_' in e.name and '/wav/' in e.name.replace('\\', '/')
                and e.data[:4] == b'MADP']
        if hits:
            todo.append((f, arc, hits))

    total = sum(len(h) for _, _, h in todo)
    print('%d archives, %d shout entries' % (len(todo), total))
    if apply:
        os.makedirs(OUTDIR, exist_ok=True)

    done = skipped = grown = 0
    for f, arc, hits in todo:
        repl = {}
        for e in hits:
            src = steam_english(e.name)
            short = e.name.replace('\\', '/').split('/')[-1]
            if src is None:
                print('  -- no English for %s' % short)
                skipped += 1
                continue
            h = mca.parse_bytes(e.data)
            ref = mca.decode(h)
            eng = decode_wav(src, h['rate'])
            pcm, longer = fit(eng, h['samples'], float(np.abs(ref).max()))
            if longer:
                grown += 1
            if apply:
                repl[e.name] = rebuild_mca(e.data, pcm)
            done += 1
        if apply and repl:
            out = build_arc_bytes(arc, repl)
            open(os.path.join(OUTDIR, f), 'wb').write(out)
            print('  %-20s %d replaced  -> %d bytes' % (f, len(repl), len(out)))

    print('\n%d converted, %d skipped, %d given a longer slot' % (done, skipped, grown))
    if not apply:
        print('(dry run -- pass --apply)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--apply' in sys.argv))

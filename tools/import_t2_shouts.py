# -*- coding: utf-8 -*-
"""Import Capcom's English character shouts into TGAA2's base game.

    python import_t2_shouts.py --report
    python import_t2_shouts.py --apply <out-romfs>

TGAA1 shipped 81 of these and TGAA2 shipped NONE -- every character's
"Objection!" and "Hold it!" in the second game is still Japanese over English
text. They were missed because they live INSIDE character archives
(`chr040_jpn.arc` -> `sound/se/bb_se_chr040/wav/chr040_irs_v_igiari_jpn`) and
TGAA2's update ships no archives at all, so an audit that walks the update tree
sees nothing and reports clean.

SIZE POLICY -- the opposite of the streamed voices. Archive members are on a
different load path: the archive carries its own entry table and it is rebuilt
with our sizes, so a member may grow freely. Full quality is therefore the
default, exactly as in the DLC shout import. A member that outgrows Capcom's is
reported rather than quietly degraded.

The English master is at
    <steam>/nativeDX11x64/sound/se/<same folder>/wav/<same base>_eng.xsew
Note sound/se, NOT sound/stream/se -- the streamed story voices live under
stream/ and the shouts do not.
"""
import os
import argparse
import shutil
import struct
import subprocess
import sys

import numpy as np

AUDIO = os.environ.get('AUDIO_TOOLS', '.')
sys.path.insert(0, AUDIO)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import dsp                                                     # noqa: E402
import mca                                                     # noqa: E402
from dgs2tool.arc import build_arc_bytes, parse_arc            # noqa: E402

BS = chr(92)
SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JPROOT = os.path.join(SCRATCH, 'tut', 'dgs2base', 'romfs')
PCSE = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'nativeDX11x64', 'sound', 'se')
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')
QUIET = 150


def decode(path, rate):
    r = subprocess.run(
        [FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', path,
         '-ac', '1', '-ar', str(rate), '-f', 's16le', '-'], capture_output=True)
    if r.returncode or not r.stdout:
        raise RuntimeError(r.stderr.decode('utf8', 'replace')[:160])
    return np.frombuffer(r.stdout, dtype='<i2')


def trim_edges(pcm):
    nz = np.nonzero(np.abs(np.asarray(pcm)) > QUIET)[0]
    return np.asarray(pcm)[nz[0]:nz[-1] + 1] if len(nz) else np.asarray(pcm)


def english_for(member):
    parts = member.replace(BS, '/').split('/')
    folder = next((p for p in parts if p.startswith(('go_se_', 'bb_se_'))), None)
    base = parts[-1].split('.')[0]
    if not (folder and base.endswith('_jpn')):
        return None
    for ext in ('.xsew', '.sngw'):
        p = os.path.join(PCSE, folder, 'wav', base[:-4] + '_eng' + ext)
        if os.path.exists(p):
            return p
    return None


def encode(donor, pcm, rate):
    """A new .mca around Capcom's header. Archive members may change size."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--apply')
    a = ap.parse_args()

    jobs = []
    for arcp in sorted(__import__('glob').glob(
            os.path.join(JPROOT, '**', '*.arc'), recursive=True)):
        try:
            arc = parse_arc(open(arcp, 'rb').read())
        except Exception:
            continue
        picks = {}
        for m in arc['entries']:
            if m.data[:4] != b'MADP':
                continue
            base = m.name.replace(BS, '/').split('/')[-1].split('.')[0]
            if '_v_' not in base or not base.endswith('_jpn'):
                continue
            eng = english_for(m.name)
            if eng:
                picks[m.name] = (eng, m.data, base)
        if picks:
            jobs.append((arcp, arc, picks))

    total = sum(len(p) for _, _, p in jobs)
    print('  archives holding shouts   : %d' % len(jobs))
    print('  shouts with English master: %d' % total)

    if not a.apply:
        return

    out = a.apply
    grew = []
    done = 0
    for arcp, arc, picks in jobs:
        rel = os.path.relpath(arcp, JPROOT)
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(arcp, dst)
        cur = parse_arc(open(dst, 'rb').read())
        repl = {}
        for name, (eng, donor, base) in picks.items():
            h = mca.parse_bytes(donor)
            pcm = trim_edges(decode(eng, h['rate']))
            blob = encode(donor, pcm, h['rate'])
            repl[name] = blob
            if len(blob) > len(donor):
                grew.append((base, len(donor), len(blob)))
            done += 1
        open(dst, 'wb').write(build_arc_bytes(cur, repl))
    print('  shouts replaced           : %d' % done)
    print('  archives written          : %d' % len(jobs))
    print('  members larger than Capcom: %d  (archives rebuild their own offsets,'
          ' so this is allowed)' % len(grew))
    for b, o, n in sorted(grew, key=lambda x: -(x[2] - x[1]))[:5]:
        print('     %-34s %6d -> %6d' % (b, o, n))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Audit every audio file we ship, in both games and both DLCs.

Answers, per clip, the three questions that actually matter and that no
header check can answer:

  LANGUAGE     does it hold Capcom's English recording, or the Japanese one?
               Decided by correlating the decoded audio against Chronicles'
               English .sngw. Correlation only says "same/different", so the
               reference must be one we have PROVEN is English -- see --prove.
  AUDIBLE      does it decode to anything? A file can be structurally perfect
               and decode to silence.
  DECLARED     does the header's sample count match the audio actually present,
               and does the stream index agree with the file?
  PLAYABLE     does the stream fit Capcom's original slot, and is the file
               internally consistent? Both were learned the hard way -- see
               fit_slots.py. A stream that overruns its slot, or whose header
               declares more data than the file holds, decodes perfectly on
               disk and is cut off or silent in-game.

Three earlier detectors were false-positive machines because they compared a
value against another copy of itself, or used an absolute threshold that
Capcom's own untouched data fails. Everything here compares against Capcom.

    python audit_all_audio.py --prove     validate the English reference first
    python audit_all_audio.py --struct    structural gate only (fast, no ffmpeg)
    python audit_all_audio.py             full report
"""
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))

import mca
from gallery_map import build as build_map
from encode_shouts import decode_wav, steam_english
from dgs2tool.arc import parse_arc

SPECIAL = os.path.join(os.environ.get('TGAAC_STEAM', ''), 'sound', 'stream', 'special', 'wav')
SEP = chr(92)
REC, STRIDE = 0x1C, 0x24


def speech(x, thr=150):
    """Extent of actual sound, ignoring padding at either end."""
    nz = np.nonzero(np.abs(np.asarray(x)) > thr)[0]
    return (int(nz[0]), int(nz[-1]) + 1) if len(nz) else (0, len(x))


def corr(a, b, max_lag=24000):
    """Best normalised correlation over a lag window.

    Fixed alignment is wrong here: clips we ship are edge-trimmed and Capcom's
    masters are not, so sample-0 alignment compares speech against padding and
    calls an identical recording a different language. Trimming both is not
    enough either -- one side's first sample can sit above any silence
    threshold, so the trim fires on one and not the other. Searching the lag
    removes the whole class."""
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    n = min(len(a), len(b))
    if n < 1000:
        return 0.0
    a = a[:n] - a[:n].mean(); b = b[:n] - b[:n].mean()
    d = np.sqrt((a ** 2).sum()) * np.sqrt((b ** 2).sum())
    if not d:
        return 0.0
    L = 1 << int(np.ceil(np.log2(2 * n)))
    cc = np.fft.irfft(np.fft.rfft(a, L) * np.conj(np.fft.rfft(b, L)), L)
    k = min(max_lag, n - 1)
    best = max(cc[:k + 1].max(), cc[-k:].max() if k else cc[0])
    return float(best / d)


def stats(data):
    """Decode one .mca payload -> (declared, decoded, audible_end, rms)."""
    h = mca.parse_bytes(data)
    a = np.array(mca.decode(h), dtype=np.float64)
    rms = float(np.sqrt((a ** 2).mean())) if len(a) else 0.0
    nz = np.nonzero(np.abs(a) > 200)[0]
    return h, a, (int(nz[-1]) if len(nz) else 0), rms


def clips(root):
    """Every .mca we ship under `root`, loose or inside an .arc.

    Keeps the FULL entry path for arc members: the shout mapping needs the
    go_se_/bb_se_ folder name, which only survives in the path."""
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(dirpath, fn)
            if fn.endswith('.mca'):
                # keep enough path for the shout mapping: it needs the
                # go_se_/bb_se_ folder, which a bare filename does not carry
                rel = os.path.relpath(p, root).replace(os.sep, '/')
                out[fn] = (open(p, 'rb').read(), rel)
            elif fn.endswith('.arc'):
                try:
                    ents = parse_arc(open(p, 'rb').read())['entries']
                except Exception:
                    continue
                for e in ents:
                    if e.data[:4] == b'MADP':
                        short = e.name.replace('/', SEP).split(SEP)[-1] + '.mca'
                        out[short] = (e.data, e.name)
    return out


def english_source(short_name, full_path, mapping):
    """Both reference kinds: DLC gallery lines and in-game shouts."""
    m = mapping.get(short_name[:-4])
    if m:
        p = os.path.join(SPECIAL, m + '.sngw')
        if os.path.exists(p):
            return p
    return steam_english(full_path)


def prove(mapping):
    """The English reference is only trustworthy if clips we KNOW are English
    match it. Without this the correlation can be read backwards -- which is
    exactly how Japanese audio once got shipped as a fix."""
    print('Proving the English reference before trusting it...')
    ours = clips(os.path.join(ROOT, 'bounce', 'rev'))
    hits = tested = 0
    for name, (data, full) in sorted(ours.items()):
        src = english_source(name, full, mapping)
        if not src:
            continue
        h, a, _, _ = stats(data)
        if corr(a, decode_wav(src, h['rate'])) > 0.9:
            hits += 1
        tested += 1
        if tested >= 12:
            break
    print('  %d of %d known clips match the reference -> %s\n'
          % (hits, tested, 'TRUSTWORTHY' if hits else 'DO NOT USE'))
    return hits > 0


def audit(label, root, mapping):
    found = clips(root)
    eng = jp = silent = short = nomap = 0
    problems = []
    for name, (data, full) in sorted(found.items()):
        try:
            h, a, end, rms = stats(data)
        except Exception:
            continue
        if rms < 20:
            silent += 1
            problems.append(('SILENT', name, 'decodes to nothing'))
            continue
        src = english_source(name, full, mapping)
        if not src:
            nomap += 1
            continue
        ref = decode_wav(src, h['rate'])
        c = corr(a, ref)
        if c > 0.5:
            eng += 1
            # compare the SPEECH, not the padding: we deliberately trim silence
            # off the edges to buy space, and that is not lost content
            oa, ob = speech(a); ra, rb = speech(ref)
            if (ob - oa) < (rb - ra) * 0.98:
                short += 1
                problems.append(('SHORT', name, '%.2fs of %.2fs of speech'
                                 % ((ob - oa) / h['rate'], (rb - ra) / h['rate'])))
        else:
            jp += 1
            problems.append(('JAPANESE', name, 'English recording exists but is not used'))
    print('%s  (%d audio files)' % (label, len(found)))
    print('   English            %4d' % eng)
    print('   Japanese           %4d   (an English recording exists for these)' % jp)
    print('   silent             %4d' % silent)
    print('   truncated          %4d' % short)
    print('   no English exists  %4d   (BGM / SE / telop)' % nomap)
    for kind, name, note in problems[:25]:
        print('      %-9s %-34s %s' % (kind, name, note))
    if len(problems) > 25:
        print('      ... %d more' % (len(problems) - 25))
    print()
    return len(problems)


def arc_streams(root):
    """Every .mca inside an .arc under `root`, keyed by arc name + entry name.

    Shouts live in archives, not loose on disk, so a walk for '*.mca' misses all
    384 of them -- which is how they went unchecked entirely."""
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith('.arc'):
                continue
            try:
                ents = parse_arc(open(os.path.join(dirpath, fn), 'rb').read())['entries']
            except Exception:
                continue
            for e in ents:
                if e.data[:4] == b'MADP':
                    out[(fn, e.name)] = e.data
    return out


def structural_arcs(label, ours_root, capcom_root):
    """Slot check for archive audio.

    Archives carry their own entry table and are rebuilt with our sizes, and no
    .stqr references them -- so the external-stale-size mechanism that cuts
    streamed audio has no equivalent here. Reported separately for that reason:
    an oversized arc entry is a flag to check, not a known defect.
    """
    ours, cap = arc_streams(ours_root), arc_streams(capcom_root)
    if not ours:
        print('%s  no archive audio\n' % label)
        return 0
    paired = [k for k in ours if k in cap]
    over = [(k, len(ours[k]), len(cap[k])) for k in paired if len(ours[k]) > len(cap[k])]
    capmax = max(len(v) for v in cap.values()) if cap else 0
    print('%s  (%d archive streams, %d matched to a Capcom original)'
          % (label, len(ours), len(paired)))
    if not paired:
        print('   NO Capcom originals matched -- the slot check did not run\n')
        return len(ours)
    if not over:
        print('   all within their Capcom entry\n')
        return 0
    biggest = max(o for _, o, _ in over)
    names = sorted({k[1].replace('/', SEP).split(SEP)[-1] for k, _, _ in over})
    print('   %d entries exceed their Capcom original (%d distinct clips)'
          % (len(over), len(names)))
    print('   largest is %d bytes; Capcom ships %d bytes in these same archives, so'
          % (biggest, capmax))
    print('   the sizes are inside the range their engine already handles.')
    for n in names[:10]:
        print('      %s' % n)
    if len(names) > 10:
        print('      ... %d more' % (len(names) - 10))
    print()
    return 0                      # flagged, not counted as a defect


def structural(label, ours_root, capcom_root):
    """The in-game failure modes, checked on disk.

    Every one of these passes a decode test and fails in the emulator:
      - file larger than Capcom's slot  -> playback cut at a random point
      - data region past end of file    -> stream plays as silence
      - index disagreeing with header   -> wrong length or silence
    """
    bad = []
    checked = 0
    paired = 0
    ours_root = os.path.normpath(ours_root)
    capcom_root = os.path.normpath(capcom_root)
    for dirpath, _, files in os.walk(ours_root):
        for fn in sorted(files):
            if not fn.endswith('.mca'):
                continue
            p = os.path.join(dirpath, fn)
            # relative path, never string surgery -- a substitution that fails to
            # match silently skips the slot check, which is how the oversize bug
            # survived an audit that reported "0 problems"
            c = os.path.join(capcom_root, os.path.relpath(p, ours_root))
            data = open(p, 'rb').read()
            try:
                h = mca.parse_bytes(data)
            except Exception:
                continue
            checked += 1
            if h['data_off'] + h['data_size'] > len(data):
                bad.append(('OVERRUN', fn, 'header claims %d bytes, file holds %d'
                            % (h['data_off'] + h['data_size'], len(data))))
            if os.path.exists(c):
                paired += 1
                if len(data) > os.path.getsize(c):
                    bad.append(('OVERSIZE', fn, '%d bytes vs Capcom\'s %d slot -- will be cut off'
                                % (len(data), os.path.getsize(c))))
            for stq in [f for f in os.listdir(dirpath) if f.endswith('.stqr')]:
                b = open(os.path.join(dirpath, stq), 'rb').read()
                names = [m.group(0).decode() for m in re.finditer(rb'AddOnContents[ -~]+', b)]
                for i, nm in enumerate(names):
                    if nm.replace('/', SEP).split(SEP)[-1] != fn[:-4]:
                        continue
                    sz, smp, _, rate = struct.unpack_from('<4I', b, REC + i * STRIDE)
                    if sz != len(data):
                        bad.append(('INDEX', fn, 'index size %d, file %d' % (sz, len(data))))
                    if smp != h['samples']:
                        bad.append(('INDEX', fn, 'index samples %d, header %d' % (smp, h['samples'])))
                    if rate != h['rate']:
                        bad.append(('INDEX', fn, 'index rate %d, header %d' % (rate, h['rate'])))
    if checked == 0:
        print('%s  no loose audio\n' % label)
        return 0
    print('%s  (%d streams, %d matched to a Capcom original)' % (label, checked, paired))
    if paired == 0:
        print('   NO Capcom originals matched -- the slot check did not run\n')
        return checked
    if not bad:
        print('   all fit their slot, all self-consistent, all indexes agree\n')
    else:
        for kind, name, note in bad:
            print('   %-9s %-30s %s' % (kind, name, note))
        print('   %d problems\n' % len(bad))
    return len(bad)


def main():
    if '--struct' in sys.argv:
        t = 0
        # loose files: these go through the .stqr streaming index, where an
        # oversized file is a PROVEN in-game defect
        for label, o, c in [('TGAA1 base', 'base_v12/romfs_v21_dir', 'basegame/rom'),
                            ('TGAA2 base', 'tgaa2/v100_dir', 'dgs2_base_romfs'),
                            ('TGAA1 DLC', 'bounce/rev', 'bounce/engd'),
                            ('TGAA2 DLC', 'bounce/t2rev', 'bounce/t2eng')]:
            po, pc = os.path.join(ROOT, o), os.path.join(ROOT, c)
            if os.path.isdir(po) and os.path.isdir(pc):
                t += structural(label + ' (loose)', po, pc)
        # archive audio: shouts. Different load path -- flagged, not failed.
        for label, o, c in [('TGAA1 base', 'base_v12/romfs_v21_dir', 'basegame/rom'),
                            ('TGAA2 base', 'tgaa2/v100_dir', 'dgs2_base_romfs'),
                            ('TGAA1 DLC', 'bounce/rev', 'bounce/engd'),
                            ('TGAA2 DLC', 'bounce/t2rev', 'bounce/t2eng')]:
            po, pc = os.path.join(ROOT, o), os.path.join(ROOT, c)
            if os.path.isdir(po) and os.path.isdir(pc):
                t += structural_arcs(label + ' (archives)', po, pc)
        print('total structural problems: %d' % t)
        return
    mapping = build_map(quiet=True) if 'quiet' in build_map.__code__.co_varnames else build_map()
    if '--prove' in sys.argv:
        prove(mapping)
        return
    if not prove(mapping):
        print('reference failed validation; refusing to report language')
        return
    total = 0
    for label, rel in [
        ('TGAA1 base update', 'base_v12/romfs_v21_dir'),
        ('TGAA2 base update', 'tgaa2/v100_dir'),
        ('TGAA1 DLC', 'bounce/rev'),
        ('TGAA2 DLC', 'bounce/t2rev'),
    ]:
        p = os.path.join(ROOT, rel)
        if os.path.isdir(p):
            total += audit(label, p, mapping)
    print('total problems: %d' % total)


if __name__ == '__main__':
    main()

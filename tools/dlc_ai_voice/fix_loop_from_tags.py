# -*- coding: utf-8 -*-
"""Fix a looping crowd/chant cue's loop points using the English master's OWN
LoopStart/LoopEnd tags, instead of import_21.py's scale-by-donor-length
formula (which breaks any cue whose take length changed under resampling --
the loop end lands past the real audio, inside the trailing digital-silence
pad; found by the loop audit of 2026-09-23).

Method, per cue (matches the accepted TGAA2 sprechchor_02_st fix):
    1. Decode the English master unclipped (float), read its LoopStart/
       LoopEnd tags from the Ogg comments.
    2. Gain: only if the master's own true peak is at or above full scale,
       apply a single gain bringing the peak to about -0.4 dBFS. Otherwise
       gain 1.0 relative to Capcom's own English master -- NOT import_21's
       ref-peak-matching gain against the Japanese donor, which is a
       different reference level. Measured against the shipped files: the
       shipped bsi_zawameki_st sat at 0.823x its master, so this fix raises
       it about 1.2 dB; the shipped sprechchor_01_st comes out 0.33 dB
       quieter than shipped under this rule. Quantize to int16 once, at
       this level.
    3. Resample 48 kHz -> the rate the stream already uses in this tree
       (never lowered below the Capcom cartridge rate).
    4. Reproduce import_21.plan()'s own Step-1 edge trim EXACTLY: only trims
       if the resampled take does not already fit Capcom's original slot
       (adpcm_bytes(...) > room, room = the Japanese donor's own ADPCM
       payload size, since that donor file IS what plan() saw as `dst`
       before any English replacement). Most looping crowd cues already fit
       untouched -- trim front/back is 0 -- and asserting that from the code
       path, rather than assuming a cached trim sample count, is the whole
       point of this rule (see the brief: "don't assume it's 2856").
    5. Convert the master's tags to the target rate and rebase them on the
       trim (loop_start frame-aligned to 14 like Capcom's own; loop_end is
       NOT frame-aligned, matching Capcom's own convention).
    6. End the stream at loop_end + Capcom's own gap for this cue (gap =
       the Japanese cartridge header's samples - loop_end).
    7. Single DSP-ADPCM encode (dsp.encode), correct per-channel loop
       context (predictor byte + 2 history samples) written at +0x34+i*0x30+40,
       laid out at +0x34.
    8. Sync only the named cues' own stqr row(s) in the same directory
       (sync_index_named); every other row stays byte-identical.

    python fix_loop_from_tags.py --tree <dir> --game TGAA1|TGAA2 --cue <name> [--cue <name> ...]
    python fix_loop_from_tags.py --tree <dir> --game TGAA1|TGAA2 --cue <name> --dry-run
"""
import argparse
import os
import shutil
import struct
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))
DGS2TOOL_PATH = os.environ.get(
    'DGS2TOOL', os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))

RUN_TS = time.strftime('%Y%m%d_%H%M%S')   # one backup folder per run (item 7)

import av                       # noqa: E402
import dsp                      # noqa: E402
import mca                      # noqa: E402
import stqr                     # noqa: E402
import import_21 as I           # noqa: E402
from resample import resample   # noqa: E402

QUIET = I.QUIET                 # 150, same edge-silence threshold as plan()
TARGET_DBFS = -0.4
TARGET_PEAK = 10 ** (TARGET_DBFS / 20.0)

JP_ROOT = {
    'TGAA1': os.path.join(ROOT, 'dlc_story_audit', 'basegame', 'rom'),
    'TGAA2': os.path.join(ROOT, 'dlc_story_audit', 'dgs2_base_romfs'),
}


def find_donor(game, cue):
    p = I.find_one(JP_ROOT[game], cue + '.mca')
    if not p:
        raise SystemExit('no Japanese cartridge donor found for %s under %s'
                          % (cue, JP_ROOT[game]))
    return p


def content_roots(tree):
    """Search only content* folders under --tree (item 5), so a backup folder
    this tool (or another run of it) left as a sibling of content0 can never
    be walked and picked up as if it were live game data. Falls back to
    searching `tree` itself when it has no content* subfolder -- the normal
    case here, where --tree already points at a copied content0's contents
    directly (see make_21_trees.stage())."""
    roots = sorted(d for d in os.listdir(tree)
                    if d.startswith('content') and os.path.isdir(os.path.join(tree, d)))
    return [os.path.join(tree, d) for d in roots] if roots else [tree]


def find_dst(tree, cue):
    for root in content_roots(tree):
        p = I.find_one(root, cue + '.mca')
        if p:
            return p
    # Not a loose file -- look inside .arc archives before giving up, so a
    # cue that moved into an archive fails loudly instead of silently.
    for root in content_roots(tree):
        for dp, _, files in os.walk(root):
            for f in files:
                if f.lower().endswith('.arc'):
                    sys.path.insert(0, DGS2TOOL_PATH)
                    from dgs2tool.arc import parse_arc
                    blob = open(os.path.join(dp, f), 'rb').read()
                    try:
                        a = parse_arc(blob)
                    except Exception:
                        continue
                    for e in a['entries']:
                        if e.name == cue + '.mca':
                            raise SystemExit(
                                '%s lives inside %s (arc member %s) -- this tool '
                                'only rewrites loose .mca files, arc rewriting is '
                                'not implemented' % (cue, os.path.join(dp, f), e.name))
    raise SystemExit('%s.mca not found anywhere under %s' % (cue, tree))


def backup_file(tree, path):
    """Back up `path` (a .mca or .stqr this run is about to overwrite) into a
    timestamped folder OUTSIDE content0, next to it (item 7): a sibling of
    `tree` itself, since --tree here already points at a copied content0's
    contents directly (see make_21_trees.stage()) with no content0 wrapper
    to sit beside. One folder per run (RUN_TS), original relative layout
    preserved underneath it."""
    rel = os.path.relpath(path, tree)
    backup_dir = os.path.join(os.path.dirname(os.path.normpath(tree)),
                               '_loopfix_backup_%s_%s_%d' % (
                                   os.path.basename(os.path.normpath(tree)), RUN_TS, os.getpid()))
    dst = os.path.join(backup_dir, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(path, dst)
    print('backed up %s -> %s' % (path, dst))
    return dst


def fix_cue(tree, game, cue, apply=True):
    dst = find_dst(tree, cue)
    donor_path = find_donor(game, cue)
    jp_bytes = open(donor_path, 'rb').read()
    jp = mca.parse_bytes(jp_bytes)
    ch = jp['channels']
    assert ch == 2, 'only stereo cues are handled: %s has %d channel(s)' % (cue, ch)
    layout = I.donor_layout(jp)
    assert layout == 'block'

    cur = mca.parse(dst)
    RATE = cur['rate']
    assert RATE >= jp['rate'], (
        '%s: tree rate %d Hz is below the Capcom cartridge rate %d Hz -- '
        'refusing to lower it further' % (cue, RATE, jp['rate']))

    master = I.english_source(cue)
    if not master:
        raise SystemExit('no English master (_eng.sngw/.xsew) found for %s' % cue)
    assert master.endswith('.sngw'), 'only vorbis (.sngw) masters are handled here: %s' % master

    c = av.open(master)
    s = c.streams.audio[0]
    src_rate = s.codec_context.sample_rate
    assert src_rate == 48000, (cue, src_rate)
    loop_start_tag = int(s.metadata['LoopStart'])
    loop_end_tag = int(s.metadata['LoopEnd'])
    parts = [f.to_ndarray() for f in c.decode(audio=0)]
    x = np.concatenate(parts, axis=1)          # (2, n) float, NOT clipped
    assert x.dtype.kind == 'f'
    assert x.shape[0] >= 2

    raw_peak = float(np.abs(x).max())
    if raw_peak >= 1.0:
        gain = TARGET_PEAK / raw_peak
    else:
        gain = 1.0

    # Item 2: the QUIET trim gate below must see the level BEFORE this gain,
    # exactly as plan() does (import_21.py:316-318 -- the trim decision runs
    # on `out`, and only afterward does plan() compute and apply its own
    # ref-peak gain). Resample the pre-gain PCM purely to pick the trim edges;
    # the post-gain PCM further down supplies the samples that get written.
    # Same conversion as import_21.load_master(): clip, then astype (truncates, no rint).
    pregain16 = np.clip(x[:2] * 32767.0, -32768, 32767).astype(np.int16)
    out_pregain = [resample(pregain16[i], src_rate, RATE) for i in range(2)]
    full_len = len(out_pregain[0])
    assert all(len(o) == full_len for o in out_pregain)

    # ---- plan()'s own Step-1 edge trim, replayed against the JP donor's own
    #      slot (room), which is what `dst` WAS the moment plan() looked at
    #      it, before any English replacement ever happened.
    pad = 256
    room = jp['data_size']
    need = I.adpcm_bytes(full_len, ch, pad)
    no_fit = cue in I.FULL_TAKE_NO_FIT.get(game, set())
    if need > room:
        loud = np.max([np.abs(o) for o in out_pregain], axis=0)
        nz = np.nonzero(loud > QUIET)[0]
        if len(nz) == 0:
            raise SystemExit('%s: resampled take is below QUIET everywhere' % cue)
        a, b = int(nz[0]), int(nz[-1]) + 1
        need2 = I.adpcm_bytes(b - a, ch, pad)
        if need2 > room and not no_fit:
            raise SystemExit('%s: still %d bytes over room (%d) after edge trim; '
                              'this tool does not lower the rate to fit' % (cue, need2 - room, room))
        if need2 > room and no_fit:
            print('%s: %d bytes over room (%d) after edge trim, but this is a '
                  'FULL_TAKE_NO_FIT cue for %s -- shipping it oversized anyway, '
                  'same as import_21.build() already does (audio at +0x34 '
                  'plays in full past the nominal slot)' % (cue, need2 - room, room, game))
    else:
        a, b = 0, full_len
    print('%s: full resampled length %d, room %d bytes (need %d), trim a=%d b=%d (%s)'
          % (cue, full_len, room, need, a, b, 'no trim' if (a, b) == (0, full_len) else 'edge-trimmed'))

    ratio = RATE / float(src_rate)
    ls_target = int(round(loop_start_tag * ratio))
    le_target = int(round(loop_end_tag * ratio))
    loop_s_raw = ls_target - a
    loop_e_raw = le_target - a
    assert loop_s_raw >= 0, ('%s: trim (a=%d) cuts into the master loop start (%d)'
                              % (cue, a, ls_target))
    loop_s = (loop_s_raw // 14) * 14
    loop_e = loop_e_raw

    gap = jp['samples'] - jp['loop_end']
    n = loop_e + gap
    assert a + n <= full_len, ('%s: computed length %d runs past the resampled '
                                'take (%d available after trim)' % (cue, n, full_len - a))

    # Item 3: check the DECODED (post-ADPCM) output for full-scale samples,
    # not just the pre-encode PCM -- the codec's own quantization can overshoot
    # even when the PCM handed to it does not clip. Lower the gain and
    # re-encode if it does, and say so.
    attempt = 0
    while True:
        xg = x[:2] * gain
        pcm16 = np.clip(np.rint(xg * 32767.0), -32768, 32767).astype(np.int16)
        out = [resample(pcm16[i], src_rate, RATE) for i in range(2)]
        assert all(len(o) == full_len for o in out)
        final = [o[a:a + n] for o in out]
        assert all(len(f) == n for f in final)
        final_peak = max(int(np.abs(f).max()) for f in final)
        assert final_peak < 32767, '%s: pre-encode buffer clips at full scale' % cue

        enc = [dsp.encode(np.asarray(f, dtype=np.int16)) for f in final]
        dec_preview = [I.dec_channel(enc[i][0], enc[i][1], n) for i in range(ch)]
        clip_n = sum(int(np.sum(np.abs(d) >= 32767)) for d in dec_preview)
        if clip_n and attempt < 5:
            old_gain = gain
            gain *= 0.95
            attempt += 1
            print('%s: decoded ADPCM output hit full scale (%d samples) at '
                  'gain %.6f -- lowering to %.6f and re-encoding (attempt %d)'
                  % (cue, clip_n, old_gain, gain, attempt))
            continue
        break
    if clip_n:
        raise SystemExit('%s: decoded output still hits full scale (%d samples) after %d '
                         'gain reductions (gain now %.6f); refusing to write clipped audio'
                         % (cue, clip_n, attempt, gain))

    print('%s: master rate %d, raw peak %.6f (%.4f dBFS), gain %.6f, loop tag %d..%d'
          % (cue, src_rate, raw_peak, 20 * np.log10(raw_peak) if raw_peak > 0 else float('-inf'),
             gain, loop_start_tag, loop_end_tag))
    print('%s: loop @ %d Hz start=%d end=%d, gap=%d (Capcom samples %d - loop_end %d), n=%d, final peak %d'
          % (cue, RATE, loop_s, loop_e, gap, jp['samples'], jp['loop_end'], n, final_peak))

    if not apply:
        print('%s: --dry-run, not writing' % cue)
        return dict(dst=dst, n=n, loop_s=loop_s, loop_e=loop_e, rate=RATE,
                    gain=gain, final=final, jp=jp)

    per = (len(enc[0][0]) + 255) // 256 * 256
    streams = [adpcm + bytes(per - len(adpcm)) for adpcm, _ in enc]
    body = I.interleave(streams, layout)
    size = len(body)

    d = bytearray(jp_bytes[:jp['data_off']])
    struct.pack_into('<I', d, 0x0C, n)
    struct.pack_into('<I', d, 0x10, RATE)
    struct.pack_into('<I', d, 0x20, size)
    struct.pack_into('<f', d, 0x24, n / float(RATE))
    struct.pack_into('<II', d, 0x14, loop_s, loop_e)

    for i, (adpcm, coefs) in enumerate(enc):
        b = 0x38 + i * 0x30
        struct.pack_into('<16h', d, b, *coefs)
        struct.pack_into('<4h', d, b + 32, 0, adpcm[0], 0, 0)
        dec = I.dec_channel(adpcm, coefs, loop_s)
        loop_ps = adpcm[(loop_s // 14) * 8]
        lh1 = int(dec[loop_s - 1]) if loop_s >= 1 else 0
        lh2 = int(dec[loop_s - 2]) if loop_s >= 2 else 0
        struct.pack_into('<4h', d, b + 40, loop_ps, lh1, lh2, 0)

    out_bytes = bytes(d) + bytes(body)
    out_bytes += bytes((-len(out_bytes)) % 32)
    assert out_bytes[:4] == b'MADP'
    assert len(out_bytes) % 32 == 0

    backup_file(tree, dst)
    open(dst, 'wb').write(out_bytes)
    print('%s: wrote %s (%d bytes)' % (cue, dst, len(out_bytes)))

    hh = mca.parse(dst)
    assert hh['samples'] == n and hh['rate'] == RATE
    assert hh['loop_start'] == loop_s and hh['loop_end'] == loop_e
    streams2 = I.deinterleave(hh['adpcm'], ch, layout)
    worst = 1.0
    for i in range(ch):
        got = I.dec_channel(streams2[i], enc[i][1], n)
        worst = min(worst, I.corr(got, final[i]))
    print('%s: round-trip worst channel corr %.6f' % (cue, worst))
    if worst < 0.999:
        raise SystemExit('%s: encode verification failed (corr %.6f)' % (cue, worst))

    return dict(dst=dst, n=n, loop_s=loop_s, loop_e=loop_e, rate=RATE,
                gain=gain, final=final, jp=jp)


def sync_index_named(tree, stqr_path, sound_dir, cue_names):
    """Like import_21.sync_index, but only touches rows for `cue_names`
    (item 4): every other row is left byte-identical even if its own file in
    `sound_dir` now differs from it, since this tool has no business judging
    or fixing a mismatch it did not cause. Backs up the .stqr before writing
    (item 7)."""
    names = set(cue_names)
    blob = bytearray(open(stqr_path, 'rb').read())
    _, _, entries = stqr.parse(bytes(blob))
    changed = 0
    for e in entries:
        base = e['name'].replace('\\', '/').split('/')[-1]
        stem = base[:-4] if base.lower().endswith('.mca') else base
        if stem not in names:
            continue
        p = os.path.join(sound_dir, base if base.endswith('.mca') else base + '.mca')
        if not os.path.exists(p):
            continue
        h = mca.parse(p)
        size = os.path.getsize(p)
        ls, le = struct.unpack_from('<II', blob, e['off'] + 0x14)
        want = (size, h['samples'], h['rate'], h['loop_start'], h['loop_end'])
        if (e['size'], e['samples'], e['rate'], ls, le) == want:
            continue
        struct.pack_into('<II', blob, e['off'] + 4, size, h['samples'])
        struct.pack_into('<I', blob, e['off'] + 0x10, h['rate'])
        struct.pack_into('<II', blob, e['off'] + 0x14, h['loop_start'], h['loop_end'])
        changed += 1
    if changed:
        backup_file(tree, stqr_path)
        open(stqr_path, 'wb').write(bytes(blob))
    return changed


def sync_stqrs(tree, results):
    # results: {cue: fix_cue() return dict}. The .stqr sits one directory
    # above the .mca (.../se/bb_se.stqr next to .../se/wav/<cue>.mca),
    # matching import_21.main()'s own sound/d split.
    by_dir = {}
    for cue, r in results.items():
        by_dir.setdefault(os.path.dirname(r['dst']), []).append(cue)
    for sound_dir, cues_here in sorted(by_dir.items()):
        stqr_dir = os.path.dirname(sound_dir)
        for fn in sorted(os.listdir(stqr_dir)):
            if fn.endswith('.stqr'):
                stqr_path = os.path.join(stqr_dir, fn)
                changed = sync_index_named(tree, stqr_path, sound_dir, cues_here)
                print('synced %s (%d rows changed)' % (stqr_path, changed))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tree', required=True)
    ap.add_argument('--game', required=True, choices=['TGAA1', 'TGAA2'])
    ap.add_argument('--cue', action='append', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    results = {}
    for cue in a.cue:
        results[cue] = fix_cue(a.tree, a.game, cue, apply=not a.dry_run)

    if not a.dry_run:
        sync_stqrs(a.tree, results)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Port the 21 English recordings audit_526.py found unported.

Seven crowd/courtroom streams and fourteen Dance-of-Deduction vocalisations.
Capcom recorded all of them in English; every one has a 3DS slot; none was ever
brought across, because Capcom tags only the English file (`name_eng.sngw`) and
leaves the Japanese bare (`name.sngw`), so a `_jpn` search finds nothing.

    python import_21.py --tree <romfs tree> --game TGAA1|TGAA2
    python import_21.py --tree ... --game ... --apply

TWO FAMILIES, TWO RULES.

  sound/stream/se/wav/*_st.mca   Streamed and named by bb_se.stqr. A stream
                                 larger than Capcom's is cut off in-game at an
                                 unpredictable point (fit_slots.py), and the
                                 index must be re-synced or the cue plays
                                 silence -- the v33 bug. Both are enforced here.
  sound/se/bb_se_ep03_dm_*/wav/  SE bank entries (.sbkr/.srqr). No stream index
                                 names them, so the proven failure mode does not
                                 apply; growth is still refused by default,
                                 because no build has ever tested it.

ORDER OF LEVERS, which is the project's own: trim the silence at the EDGES
first, and only then lower the rate. Getting this backwards costs quality for
nothing -- `ks_failed_st` looked like it needed 90% rate, and 2.21s of its
5.32s is trailing silence, so trimming alone fits it whole at Capcom's rate.
Edges are trimmed ONLY when a take overruns: the 14 Dance clips are synced to
animation and match their Japanese length to the sample, so shifting their
onset would desync them, and they never reach that branch because they fit.

All 20 land at Capcom's own rate. `sprechchor_02_st` in TGAA2 is the one
refusal: 8.86s of speech against a 5.05s slot, which needs 57% even after
trimming, against a 75% floor.
"""
import argparse
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'public_repo', 'tools', 'audio_tools'))

import dsp
import mca
import msadpcm
import stqr
from resample import resample

STEAM = os.path.join(ROOT, 'TGAAC Steam', 'nativeDX11x64')
MAX_GAIN = 2.0          # +6 dB, matches encode_shouts
QUIET = 150             # edge-silence threshold, matches fit_slots.QUIET
RATE_FLOOR = 0.75       # matches the project's floor for rate reduction

CROWD = ['bb_benron_kaishi_st', 'bb_ronkoku_st', 'bsi_zawameki_st',
         'ks_complete_st', 'ks_failed_st', 'sprechchor_01_st', 'sprechchor_02_st']
DANCE = ['v_asg_cloak', 'v_asg_katana', 'v_asg_surprise_eye', 'v_asg_surprise_mask',
         'v_asg_umeki', 'v_dbb_cage', 'v_dbb_excite', 'v_dbb_lever', 'v_dbb_panic',
         'v_dbb_skip', 'v_nhd_surprise', 'v_nhd_surprise2', 'v_sst_run',
         'v_sst_surprise']


def find_one(root, name):
    for dirpath, _, files in os.walk(root):
        if name in files:
            return os.path.join(dirpath, name)
    return None


def english_source(name):
    for suffix in ('_eng.sngw', '_eng.xsew'):
        p = find_one(os.path.join(STEAM, 'sound'), name + suffix)
        if p:
            return p
    return None


def decode_english(path, channels):
    """Capcom's English master -> list of `channels` int16 arrays, and its rate."""
    if path.endswith('.xsew'):
        pcm, rate = msadpcm.decode(path)
        return [pcm] * channels if channels > 1 else [pcm], rate
    import av
    c = av.open(path)
    s = c.streams.audio[0]
    rate = s.codec_context.sample_rate
    parts = [f.to_ndarray() for f in c.decode(audio=0)]
    x = np.concatenate(parts, axis=1)          # (channels, samples), float or int
    if x.dtype.kind == 'f':
        x = np.clip(x * 32767.0, -32768, 32767)
    x = x.astype(np.int16)
    if x.shape[0] >= channels:
        return [x[i] for i in range(channels)], rate
    return [x[0]] * channels, rate             # mono master into a stereo slot


def dec_channel(adpcm, coef, n):
    """Decode one channel back, to verify what was written."""
    out = np.zeros(n, np.int32)
    h1 = h2 = 0
    i = 0
    for f in range(0, len(adpcm), 8):
        if i >= n:
            break
        ps = adpcm[f]
        scale = 1 << (ps & 0x0F)
        p = (ps >> 4) & 0x07
        c1, c2 = coef[p * 2], coef[p * 2 + 1]
        for k in range(14):
            if i >= n:
                break
            b = adpcm[f + 1 + k // 2]
            nib = (b >> 4) if k % 2 == 0 else (b & 0x0F)
            if nib >= 8:
                nib -= 16
            s = (nib * scale * 2048 + c1 * h1 + c2 * h2 + 1024) >> 11
            s = max(-32768, min(32767, s))
            out[i] = s
            h2, h1 = h1, s
            i += 1
    return out


def corr(a, b):
    n = min(len(a), len(b))
    a = a[:n].astype(np.float64); b = b[:n].astype(np.float64)
    a, b = a - a.mean(), b - b.mean()
    d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float((a * b).sum() / d) if d else 0.0


def adpcm_bytes(samples, channels, pad):
    """Capcom's size rule, measured on all seven stereo crowd streams: each
    channel's ADPCM is padded to 256 on its own, THEN interleaved -- so the data
    size is channels * ceil(per_channel / 256) * 256. Mono files pad to 64."""
    per = math.ceil(samples / 14) * 8
    if channels > 1:
        return channels * ((per + 255) // 256 * 256)
    return (per + pad - 1) // pad * pad


def deinterleave(data, channels, layout):
    """Split an interleaved stereo payload into per-channel ADPCM streams."""
    if channels == 1:
        return [data]
    unit = 8 if layout == 'frame' else 256
    step = unit * channels
    return [b''.join(data[i + c * unit:i + (c + 1) * unit]
                     for i in range(0, len(data) - step + 1, step))
            for c in range(channels)]


def interleave(streams, layout):
    unit = 8 if layout == 'frame' else 256
    n = len(streams[0])
    assert all(len(s) == n for s in streams)
    out = bytearray()
    for i in range(0, n, unit):
        for s in streams:
            out += s[i:i + unit]
    return bytes(out)


def donor_layout(h, n=120000):
    """Which interleave does THIS donor use? Capcom's crowd streams are not one
    layout: the two short courtroom stings are per-frame L,R, the murmur, the
    chant and both Dance-outcome cues are 256-byte blocks per channel. Nothing
    in the header says which. Decoding both ways and asking which gives a sane
    left/right correlation does (+0.6..+0.9 right, ~0 or negative wrong)."""
    if h['channels'] == 1:
        return 'mono'
    n = min(n, h['samples'])
    scores = {}
    for layout in ('frame', 'block'):
        L, R = deinterleave(h['adpcm'], 2, layout)
        a = dec_channel(L, list(struct.unpack_from('<16h', h['raw'], 0x38)), n)
        b = dec_channel(R, list(struct.unpack_from('<16h', h['raw'], 0x68)), n)
        scores[layout] = corr(a.astype(np.float64), b.astype(np.float64))
    pick = max(scores, key=scores.get)
    other = min(scores, key=scores.get)
    # The choice must be unambiguous, or the encode/verify pair is merely
    # self-consistent: a wrong pick would still verify against itself. The
    # MARGIN is the signal: the seven real donors decide by 0.40 to 0.95
    # (+0.62 vs +0.12, +0.93 vs -0.02, and a wide-stereo chant at +0.43 vs
    # +0.01). Refuse a coin-flip rather than guess.
    if scores[pick] < 0.35 or scores[pick] - scores[other] < 0.25:
        raise SystemExit('stereo layout ambiguous for this donor: frame %+.3f, block %+.3f'
                         % (scores['frame'], scores['block']))
    return pick


def build(donor_path, chans, rate, layout):
    """Rebuild one .mca around Capcom's header, in the DONOR'S OWN layout.

    Stereo: each channel padded to 256 on its own, then interleaved per-frame
    or per-256-byte-block to match the donor (see donor_layout). Mono: 64-pad.
    Loops: Capcom's loop starts sit on frame boundaries (18704 and 37576 are
    both multiples of 14), and a looping stream needs the decoder's restart
    state -- predictor byte at the loop frame plus the two samples before it --
    written per channel at +40, exactly as stereo_bgm.py does. Leaving those
    as the donor's values describes a stream that no longer exists.
    """
    jp = open(donor_path, 'rb').read()
    h = mca.parse_bytes(jp)
    ch = h['channels']
    n = len(chans[0])
    enc = [dsp.encode(np.asarray(c, dtype=np.int16)) for c in chans]

    if ch > 1:
        per = (len(enc[0][0]) + 255) // 256 * 256
        streams = [adpcm + bytes(per - len(adpcm)) for adpcm, _ in enc]
        body = interleave(streams, layout)
    else:
        adpcm = enc[0][0]
        body = adpcm + bytes(((len(adpcm) + 63) // 64 * 64) - len(adpcm))
    size = len(body)

    d = bytearray(jp[:h['data_off']])
    struct.pack_into('<I', d, 0x0C, n)
    struct.pack_into('<I', d, 0x10, rate)
    struct.pack_into('<I', d, 0x20, size)
    struct.pack_into('<f', d, 0x24, n / float(rate))     # duration, as Capcom writes it

    loop_s = loop_e = 0
    if h['loop_start'] or h['loop_end']:
        f = n / float(h['samples'])
        loop_s = int(h['loop_start'] * f) // 14 * 14           # frame-aligned, like Capcom's
        loop_e = min(int(h['loop_end'] * f), n - 1)
        struct.pack_into('<II', d, 0x14, loop_s, loop_e)

    for i, (adpcm, coefs) in enumerate(enc):
        b = 0x38 + i * 0x30
        struct.pack_into('<16h', d, b, *coefs)
        struct.pack_into('<4h', d, b + 32, 0, adpcm[0], 0, 0)
        if loop_s:
            dec = dec_channel(adpcm, coefs, loop_s)
            loop_ps = adpcm[(loop_s // 14) * 8]
            lh1 = int(dec[loop_s - 1]) if loop_s >= 1 else 0
            lh2 = int(dec[loop_s - 2]) if loop_s >= 2 else 0
            struct.pack_into('<4h', d, b + 40, loop_ps, lh1, lh2, 0)
        else:
            struct.pack_into('<4h', d, b + 40, 0, 0, 0, 0)
    return bytes(d) + bytes(body), enc, n


def sync_index(stqr_path, sound_dir):
    """Rewrite size, sample count AND rate for every row naming a local file.

    Entry layout (stqr.py): +0x04 size, +0x08 samples, +0x0C channels,
    +0x10 rate. Rows whose file is not in this directory are left alone.
    """
    blob = bytearray(open(stqr_path, 'rb').read())
    _, _, entries = stqr.parse(bytes(blob))
    changed = 0
    for e in entries:
        base = e['name'].replace('\\', '/').split('/')[-1]
        p = os.path.join(sound_dir, base if base.endswith('.mca') else base + '.mca')
        if not os.path.exists(p):
            continue
        h = mca.parse(p)
        # The index carries the WHOLE FILE size, not the ADPCM payload size --
        # verified against all 125 untouched rows of bb_se.stqr, which match the
        # file byte for byte and match data_size in not one case. Using
        # data_size here rewrote all 125 rows instead of the 6 that changed.
        size = os.path.getsize(p)
        # The row also duplicates the loop points (+0x14, +0x18), and Capcom's
        # rows agree with Capcom's headers. A rebuilt looping stream has new
        # loop points, so the row must follow or the two describe different
        # streams -- and nothing says which one the game believes.
        ls, le = struct.unpack_from('<II', blob, e['off'] + 0x14)
        want = (size, h['samples'], h['rate'], h['loop_start'], h['loop_end'])
        if (e['size'], e['samples'], e['rate'], ls, le) == want:
            continue
        struct.pack_into('<II', blob, e['off'] + 4, size, h['samples'])
        struct.pack_into('<I', blob, e['off'] + 0x10, h['rate'])
        struct.pack_into('<II', blob, e['off'] + 0x14, h['loop_start'], h['loop_end'])
        changed += 1
    if changed:
        open(stqr_path, 'wb').write(bytes(blob))
    return changed


def plan(tree, game, fit):
    jobs = []
    for group, names in (('stream', CROWD), ('sebank', DANCE)):
        for name in names:
            dst = find_one(tree, name + '.mca')
            src = english_source(name)
            if not dst or not src:
                continue
            h = mca.parse(dst)
            ch = h['channels']
            chans, erate = decode_english(src, ch)
            rate = h['rate']
            pad = 256 if ch > 1 else 64
            slot = os.path.getsize(dst)
            room = slot - h['data_off']
            out = [resample(c, erate, rate) for c in chans]
            trimmed = False

            # Step 1 of the project's own order: trim the silence at the edges,
            # and ONLY if the take does not already fit. The 14 Dance clips are
            # synced to animation and match their Japanese length to the sample,
            # so touching their edges would shift the onset -- they never reach
            # this branch, because they fit untouched.
            if adpcm_bytes(len(out[0]), ch, pad) > room:
                loud = np.max([np.abs(c) for c in out], axis=0)
                nz = np.nonzero(loud > QUIET)[0]
                if len(nz):
                    a, b = int(nz[0]), int(nz[-1]) + 1
                    if a or b < len(out[0]):
                        out = [c[a:b] for c in out]
                        trimmed = True

            # Step 2, only if trimming was not enough: lower the rate.
            if adpcm_bytes(len(out[0]), ch, pad) > room and fit:
                rate = int(rate * room / adpcm_bytes(len(out[0]), ch, pad))
                out = [resample(c, h['rate'], rate) for c in out]

            ref_peak = int(np.abs(mca.decode(h)).max())
            peak = max(int(np.abs(c).max()) for c in out) or 1
            g = min(ref_peak / peak, MAX_GAIN) if ref_peak else 1.0
            out = [np.clip(np.rint(c.astype(np.float64) * g), -32768, 32767)
                   .astype(np.int16) for c in out]
            jobs.append(dict(name=name, group=group, path=dst, src=src, ch=ch,
                             rate=rate, base_rate=h['rate'], chans=out, slot=slot,
                             trimmed=trimmed, layout=donor_layout(h),
                             need=h['data_off'] + adpcm_bytes(len(out[0]), ch, pad),
                             jp=h['samples'] / h['rate'],
                             en=len(out[0]) / rate))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tree', required=True)
    ap.add_argument('--game', required=True, choices=['TGAA1', 'TGAA2'])
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--fit', action='store_true',
                    help='lower the rate where the English overruns the slot')
    ap.add_argument('--allow-growth', action='store_true')
    a = ap.parse_args()

    jobs = plan(a.tree, a.game, a.fit)
    if not jobs:
        raise SystemExit('no target cues found under %s' % a.tree)

    skip = []
    print('%-22s %-7s %2s %8s %8s %9s %9s  %s'
          % ('cue', 'group', 'ch', 'jp', 'english', 'slot', 'needed', 'note'))
    for j in jobs:
        note = j['layout'] + (' edge-trimmed' if j.get('trimmed') else '')
        if j['rate'] != j['base_rate']:
            note = 'rate %d Hz (%.0f%%)' % (j['rate'], 100.0 * j['rate'] / j['base_rate'])
            if j['rate'] < j['base_rate'] * RATE_FLOOR:
                note += ' BELOW FLOOR'
                skip.append(j)
        if j['need'] > j['slot']:
            note = 'OVER by %d bytes' % (j['need'] - j['slot'])
            if not a.allow_growth:
                skip.append(j)
        print('%-22s %-7s %2d %7.2fs %7.2fs %8d %8d  %s'
              % (j['name'], j['group'], j['ch'], j['jp'], j['en'],
                 j['slot'], j['need'], note))
    for j in skip:
        print('   SKIPPING %s' % j['name'])
    jobs = [j for j in jobs if j not in skip]
    print('\n%d cues to write' % len(jobs))
    if not a.apply:
        print('--report only; run with --apply to write')
        return

    print()
    for j in jobs:
        blob, enc, n = build(j['path'], j['chans'], j['rate'], j['layout'])
        assert blob[:4] == b'MADP'
        assert len(blob) <= j['slot'] or a.allow_growth
        open(j['path'], 'wb').write(blob)
        # verify off the written file, per channel, against what we meant to write
        h = mca.parse(j['path'])
        assert h['samples'] == n and h['rate'] == j['rate']
        streams = deinterleave(h['adpcm'], j['ch'], j['layout'])
        worst = 1.0
        for i in range(j['ch']):
            got = dec_channel(streams[i], enc[i][1], min(n, 200000))
            worst = min(worst, corr(got, j['chans'][i][:len(got)]))
        print('   %-22s %7d bytes  %.2fs @ %d Hz  worst channel corr %.4f'
              % (j['name'], os.path.getsize(j['path']), n / j['rate'], j['rate'], worst))
        if worst < 0.95:
            raise SystemExit('%s: encode verification failed' % j['name'])

    # The stream index must agree with the files or the cue plays silence.
    # stqr.sync writes size and sample count but only WARNS on a changed rate,
    # which is not enough here: --fit lowers ks_failed_st to 29401 Hz, and an
    # index still claiming 32728 describes a file that no longer exists.
    for j in jobs:
        if j['group'] != 'stream':
            continue
        sound = os.path.dirname(j['path'])
        d = os.path.dirname(sound)
        for fn in sorted(os.listdir(d)):
            if fn.endswith('.stqr'):
                print('   synced %s (%d rows)'
                      % (fn, sync_index(os.path.join(d, fn), sound)))
        break


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Prove the fixed .mca parser/writers use Capcom's real offset and layout.

Three checks (spec: SPEC_fix_mca_parsers.md), each printed and asserted:

  1. CORPUS: every loose .mca under dgs2_base_romfs/sound (653 Capcom
     originals) parses with data_off == the u32 at +0x34 (not the old,
     wrong +0x1C); the ch0 header ps byte (+0x38+0x22 == +0x5A) equals the
     byte at data_off for >= 652 of them (staffroll_part2 is the known odd
     one, reported, not required to pass); the gap between hdr_end (+0x1C)
     and data_off is zero. Needs TGAA_ROOT (see below); skipped if unset.
  2. ROUND TRIP for the two writers that build their own header offset
     rather than copying donor[:data_off] (stereo_bgm.py, import_anime.py):
     fed a real stereo donor plus synthetic PCM (ffmpeg calls monkeypatched
     out so this runs offline), the output has data at +0x34, a zero gap,
     header bytes before hdr_end unchanged except the fields the writer
     means to change, and channel 1's first-block ps byte sits at
     +0x34+0x100 (block layout, not frame). The two writers pad to
     DIFFERENT rules and are asserted differently (see each test): stereo_bgm
     rounds up to the next 32-byte boundary (o3+size+pad, pad<32, pad bytes
     zero); import_anime fits the donor's own fixed streamed slot (Capcom's
     slot rule -- output length == donor length exactly). Needs TGAA_ROOT.
     Every OTHER writer this job touched (encode_shouts.rebuild_mca,
     import_t2dlc_shouts.encode, import_kurae.encode, import_t2_shouts.encode,
     import_21.build, import_t2_voices.rebuild, rebuild_voices.build,
     fit_slots.rebuild, split_narration.build) copies donor[:h['data_off']],
     so the parser fix alone makes them correct; those are proved by running
     test_pad32_writers_20260914.py (unchanged, an existing selftest),
     reported alongside this file's output per the spec.
  3. DECODE: bb_ronkoku_st.mca and ks_complete_st.mca (the two stereo TGAA2
     donors the earlier blind model test flagged as ambiguous/contradictory)
     decode from +0x34 in 256-byte blocks with channel 1's first-frame ps
     byte matching the header's own ch1 ps field, L/R correlation reported
     (whatever it is), and donor_layout() returns 'block' for both. Needs
     TGAA_ROOT.

Imports the PUBLIC repo's own copies of import_21 and import_anime (not the
dlc_ai_voice / testimony_pipeline project-folder copies), since this test
ships in public_repo.

Set TGAA_ROOT to the project folder (the one containing dlc_story_audit,
dlc_ai_voice, testimony_pipeline) to run the corpus/donor-dependent checks;
without it they are skipped with a clear message (this file itself needs no
such path -- everything it imports lives inside public_repo).

    python test_mca_offsets.py
"""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, '..'))           # public_repo/tools
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TOOLS, 'dlc_ai_voice'))
sys.path.insert(0, TOOLS)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import mca                                     # noqa: E402
import stereo_bgm                              # noqa: E402
import import_21                               # noqa: E402
import import_anime                            # noqa: E402

TGAA_ROOT = os.environ.get('TGAA_ROOT')
if TGAA_ROOT:
    CORPUS = os.path.join(TGAA_ROOT, 'dlc_story_audit', 'dgs2_base_romfs', 'sound')
    BGM_DONOR = os.path.join(TGAA_ROOT, 'dlc_story_audit', 'basegame', 'rom',
                             'sound', 'stream', 'bgm', 'wav', '09_tsuisou_1.mca')
    ANIME_DONOR = os.path.join(TGAA_ROOT, 'dlc_story_audit', 'dgs2_base_romfs',
                               'sound', 'stream', 'anime', 'wav', 'go_anime_1a.mca')
    SE_WAV = os.path.join(CORPUS, 'stream', 'se', 'wav')
else:
    CORPUS = BGM_DONOR = ANIME_DONOR = SE_WAV = None
SCRATCH_OUT = os.path.join(HERE, '_test_mca_offsets_scratch.mca')

failures = []
n_checks = 0
skipped_sections = []


def check(cond, label):
    global n_checks
    n_checks += 1
    print(('PASS ' if cond else 'FAIL ') + label)
    if not cond:
        failures.append(label)
    return cond


def skip_section(label, reason):
    print('SKIP %s: %s' % (label, reason))
    skipped_sections.append(label)


def need_root(label):
    if not TGAA_ROOT:
        skip_section(label, 'TGAA_ROOT is not set (needs the project folder that holds '
                             'dlc_story_audit/dgs2_base_romfs, outside public_repo)')
        return False
    return True


# ---------------------------------------------------------------------------
# 1. corpus scan

def test_corpus():
    if not need_root('1. CORPUS'):
        return
    print('== 1. CORPUS: data_off == u32 at +0x34, over every loose .mca under '
          'dgs2_base_romfs/sound ==')
    n = 0
    off_wrong, gap_nonzero, ps_mismatch = [], [], []
    for dp, _, fs in os.walk(CORPUS):
        for fn in sorted(fs):
            if not fn.endswith('.mca'):
                continue
            p = os.path.join(dp, fn)
            d = open(p, 'rb').read()
            if d[:4] != b'MADP':
                continue
            n += 1
            h = mca.parse_bytes(d)
            real_off = struct.unpack_from('<I', d, 0x34)[0]
            if h['data_off'] != real_off:
                off_wrong.append(fn)
            gap = d[h['hdr_end']:h['data_off']]
            if any(gap):
                gap_nonzero.append(fn)
            ps_at_hdr = d[0x38 + 0x22]
            ps_at_data = d[h['data_off']] if h['data_off'] < len(d) else None
            if ps_at_hdr != ps_at_data:
                ps_mismatch.append(fn)
    print('  files checked: %d' % n)
    check(n == 653, 'corpus has 653 loose .mca files (got %d)' % n)
    check(not off_wrong, 'mca.parse data_off == u32 at +0x34 for every file (wrong: %s)'
          % (off_wrong[:5] or 'none'))
    check(len(gap_nonzero) <= 1,
          'gap (hdr_end..data_off) is zero for >= %d/%d files (nonzero: %s)'
          % (n - 1, n, gap_nonzero))
    check(len(ps_mismatch) <= 1,
          'ch0 header ps byte (+0x5A) equals byte at data_off for >= %d/%d files (mismatch: %s)'
          % (n - 1, n, ps_mismatch))
    if gap_nonzero or ps_mismatch:
        print('  (staffroll_part2.mca is the known odd one; reported, not required to pass)')
    return n


# ---------------------------------------------------------------------------
# 2. round trip: the two writers that build their own header offset

def header_unchanged_except(donor, blob, hdr_end, changed_ranges):
    """donor[0:hdr_end] must equal blob[0:hdr_end] outside `changed_ranges`
    (a list of (start, end) byte spans the writer is meant to change)."""
    bad = []
    for i in range(hdr_end):
        if any(a <= i < b for a, b in changed_ranges):
            continue
        if donor[i] != blob[i]:
            bad.append(i)
    return bad


def check_pad32_exact(blob, data_off, data_size, label):
    """stereo_bgm.py's rule: length == data_off + data_size, rounded up to the
    next 32-byte boundary (pad < 32, pad bytes zero, total % 32 == 0). This is
    the generic pad32 rule, NOT a fixed-slot rebuild."""
    end = data_off + data_size
    pad = (-end) % 32
    check(len(blob) == end + pad,
          '%s: len == o3+size+pad (%d == %d, pad=%d)' % (label, len(blob), end + pad, pad))
    check(pad < 32, '%s: pad < 32 (%d)' % (label, pad))
    check(not any(blob[end:]), '%s: pad bytes are zero' % label)
    check(len(blob) % 32 == 0, '%s: len %% 32 == 0' % label)


def check_donor_slot_exact(blob, donor, data_off, data_size, label):
    """import_anime.py's rule: Capcom's STREAMED SLOT rule, not the generic
    pad32 rule -- the whole output is padded/fits to the DONOR's own exact
    file length (its fixed 3DS slot), which may leave more than 31 zero bytes
    after data_off+data_size."""
    check(len(blob) == len(donor),
          '%s: len == donor slot length exactly (%d == %d)' % (label, len(blob), len(donor)))
    check(len(blob) % 32 == 0, '%s: len %% 32 == 0 (Capcom\'s own file already is)' % label)
    end = data_off + data_size
    check(not any(blob[end:]), '%s: bytes after data_off+data_size are zero (slot tail)' % label)


def test_stereo_bgm_roundtrip():
    if not need_root('2a. stereo_bgm round trip'):
        return
    print('\n== 2a. ROUND TRIP: stereo_bgm.convert() (ffmpeg monkeypatched out) ==')
    donor = open(BGM_DONOR, 'rb').read()
    h = mca.parse_bytes(donor)
    check(h['channels'] == 2, 'BGM donor %s is stereo' % os.path.basename(BGM_DONOR))
    n = min(h['samples'], 14 * 3000)
    t = np.arange(n)
    L = (np.sin(t / 37.0) * 8000).astype(np.int16)
    R = (np.sin(t / 53.0) * 8000).astype(np.int16)

    real_sngw_info, real_decode_stereo = stereo_bgm.sngw_info, stereo_bgm.decode_stereo
    stereo_bgm.sngw_info = lambda path: (0, n - 1, h['rate'])
    stereo_bgm.decode_stereo = lambda path, rate: (L.copy(), R.copy())
    try:
        stereo_bgm.convert(BGM_DONOR, SCRATCH_OUT, log=lambda *a: None)
        blob = open(SCRATCH_OUT, 'rb').read()
    finally:
        stereo_bgm.sngw_info, stereo_bgm.decode_stereo = real_sngw_info, real_decode_stereo
        if os.path.exists(SCRATCH_OUT):
            os.remove(SCRATCH_OUT)

    hb = mca.parse_bytes(blob)
    o3 = struct.unpack_from('<I', donor, 0x34)[0]
    check(hb['data_off'] == o3, 'output data_off == donor o3 (+0x34) (%d == %d)' % (hb['data_off'], o3))
    gap = blob[hb['hdr_end']:hb['data_off']]
    check(not any(gap), 'output gap (hdr_end..data_off) is zero')
    check_pad32_exact(blob, hb['data_off'], hb['data_size'], 'stereo_bgm output')
    bad = header_unchanged_except(donor, blob, hb['hdr_end'],
                                  [(0x0C, 0x10), (0x14, 0x1C), (0x20, 0x24),
                                   (0x38, hb['hdr_end'])])
    check(not bad, 'header bytes 0..hdr_end match the donor except the changed fields (bad offsets: %s)'
          % (bad[:10] or 'none'))
    ch1_ps_hdr = blob[0x38 + 0x30 + 0x22]
    ch1_ps_data = blob[hb['data_off'] + 0x100]
    check(ch1_ps_hdr == ch1_ps_data,
          'ch1 ps byte at data_off+0x100 matches header (block layout, not frame): %d == %d'
          % (ch1_ps_data, ch1_ps_hdr))


def test_import_anime_roundtrip():
    if not need_root('2b. import_anime round trip'):
        return
    print('\n== 2b. ROUND TRIP: import_anime.build() (ffmpeg mix() monkeypatched out) ==')
    if not os.path.exists(ANIME_DONOR):
        skip_section('2b. import_anime round trip', 'no anime donor at %s' % ANIME_DONOR)
        return
    donor = open(ANIME_DONOR, 'rb').read()
    h = mca.parse_bytes(donor)
    check(h['channels'] == 2, 'anime donor %s is stereo' % os.path.basename(ANIME_DONOR))
    n = min(h['samples'], 14 * 3000)
    t = np.arange(n, dtype=np.float64)
    L = np.sin(t / 41.0) * 8000
    R = np.sin(t / 59.0) * 8000

    real_mix = import_anime.mix
    import_anime.mix = lambda name, rate: (L.copy(), R.copy())
    try:
        blob, why = import_anime.build(ANIME_DONOR, log=lambda *a: None)
    finally:
        import_anime.mix = real_mix
    check(blob is not None, 'import_anime.build produced output (why=%s)' % why)
    if blob is None:
        return

    hb = mca.parse_bytes(blob)
    o3 = struct.unpack_from('<I', donor, 0x34)[0]
    check(hb['data_off'] == o3, 'output data_off == donor o3 (+0x34) (%d == %d)' % (hb['data_off'], o3))
    gap = blob[hb['hdr_end']:hb['data_off']]
    check(not any(gap), 'output gap (hdr_end..data_off) is zero')
    check_donor_slot_exact(blob, donor, hb['data_off'], hb['data_size'], 'import_anime output')
    bad = header_unchanged_except(donor, blob, hb['hdr_end'],
                                  [(0x0C, 0x10), (0x20, 0x24), (0x38, hb['hdr_end'])])
    check(not bad, 'header bytes 0..hdr_end match the donor except the changed fields (bad offsets: %s)'
          % (bad[:10] or 'none'))
    ch1_ps_hdr = blob[0x38 + 0x30 + 0x22]
    ch1_ps_data = blob[hb['data_off'] + 0x100]
    check(ch1_ps_hdr == ch1_ps_data,
          'ch1 ps byte at data_off+0x100 matches header (block layout, not frame): %d == %d'
          % (ch1_ps_data, ch1_ps_hdr))


# ---------------------------------------------------------------------------
# 3. decode check on the two flagged stereo donors

def test_decode_two_donors():
    if not need_root('3. DECODE'):
        return
    print('\n== 3. DECODE: bb_ronkoku_st.mca and ks_complete_st.mca, from +0x34 in 256-byte blocks ==')
    for name in ('bb_ronkoku_st', 'ks_complete_st'):
        p = os.path.join(SE_WAV, name + '.mca')
        h = mca.parse(p)
        check(h['channels'] == 2, '%s is stereo' % name)
        L, R = import_21.deinterleave(h['adpcm'], 2, 'block')
        n = min(60000, h['samples'])
        coef0 = list(struct.unpack_from('<16h', h['raw'], 0x38))
        coef1 = list(struct.unpack_from('<16h', h['raw'], 0x68))
        a = import_21.dec_channel(L, coef0, n)
        b = import_21.dec_channel(R, coef1, n)
        c = import_21.corr(a.astype(np.float64), b.astype(np.float64))
        ch1_ps_hdr = h['raw'][0x68 + 0x22]
        ch1_ps_data = h['raw'][h['data_off'] + 0x100]
        check(ch1_ps_hdr == ch1_ps_data,
              '%s: ch1 first-block ps matches header (%d == %d)' % (name, ch1_ps_data, ch1_ps_hdr))
        print('  %-16s data_off=%3d L/R correlation (block) = %+.4f' % (name, h['data_off'], c))
        layout = import_21.donor_layout(h)
        check(layout == 'block', "%s: donor_layout() returns 'block' (got %r)" % (name, layout))


def main():
    test_corpus()
    test_stereo_bgm_roundtrip()
    test_import_anime_roundtrip()
    test_decode_two_donors()
    print('\n%d checks ran, %d failed, %d section(s) skipped'
          % (n_checks, len(failures), len(skipped_sections)))
    if skipped_sections:
        for s in skipped_sections:
            print('  SKIPPED ' + s)
    for f in failures:
        print('  FAIL ' + f)
    if n_checks == 0:
        print('NOTHING RAN: every section was skipped (set TGAA_ROOT to actually test anything)')
        return 1
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Fit Capcom's English narration to the 3DS, which paginates it differently.

    python split_narration.py --report | --apply <romfs>

THE SHAPE OF THE PROBLEM. Each subtitle PAGE has its own voice slot, and the
engine starts a new clip on every page turn. Capcom re-split the narration for
English -- ten takes where the Japanese has twenty lines -- so one English take
spans two 3DS pages. Verified on all ten pairs: the English duration matches the
sum of its two Japanese slots to within a second.

Dropping a whole take into the first slot therefore does NOT work: the page turn
starts the next slot and cuts the line off mid-sentence. That is what a build
doing exactly that sounded like. The take has to be SPLIT at the page boundary
and written into both slots.

Where to split: the Japanese slot lengths give the proportion the two sentences
occupy, and the quietest window near that point is the sentence gap. Nine of ten
land on near-silence; the tenth needs a wider search.

EACH HALF MUST FIT ITS OWN SLOT IN *SECONDS*, NOT ONLY IN BYTES.

Lowering the sample rate shrinks the FILE but leaves the DURATION untouched,
and the page turn is driven by the scene's .sdl timing, which was authored for
the Japanese take. So a rate drop never fixed anything here -- the clip still
outran its page and was cut. The English narration runs longer than the
Japanese, so each half is TIME-COMPRESSED with ffmpeg's atempo (pitch
preserved) until it fits the slot's original duration. Compression is capped;
past the cap the clip is left alone rather than made to gabble.

EACH HALF MUST ALSO FIT ITS OWN SLOT IN BYTES. Confirmed by ear: an oversized clip is cut off
part-way and then plays silence until the page advances on its own timer, even
with the .stqr index synced to the larger size. The documented DLC slot rule
holds for the base game too, so a half that does not fit at full rate has its
sample rate lowered until it does -- never its words trimmed.
"""
import os
import argparse
import re
import struct
import sys

import subprocess

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get('AUDIO_TOOLS',
                                  os.environ.get('AUDIO_TOOLS', '.')))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import dsp                                                     # noqa: E402
import mca                                                     # noqa: E402
import import_t2_voices as I                                   # noqa: E402

BS = chr(92)
I.JP = os.path.join(I.SCRATCH, 'tut', 't1jap', 'romfs', 'sound', 'stream', 'voice')
PAIRS = [('01000_%05d_nrt' % k, '01000_%05d_nrt' % (k + 5)) for k in range(10, 110, 10)]

# Pairs whose BLANK companion page never sounds in game, confirmed by ear: the
# text page plays and the tail is simply lost ("waited with bated breath",
# "when he started whispering to me"). For these the whole take goes on the text
# page and the companion is silenced -- worse quality on two lines, but the
# sentence is complete, which matters more.
# TRIED AND REVERTED. Putting the whole sentence on the text page made those two
# pairs play NOTHING: the page's audio window is about the length of Capcom's own
# slot, so a 5.6 s take in a 3.6 s window fails outright rather than truncating.
# The split version plays the first part correctly and loses only the tail, which
# is strictly better. The tail cannot be recovered -- the blank companion page
# produces no audio at all, and the text page is too short for the English
# sentence, which runs nearly twice the Japanese.
WHOLE_ON_FIRST = set()

# Two tails never sound: 00015 ("waited with bated breath") and 00065 ("when he
# started whispering to me"). Nothing in the FILES distinguishes them from the
# eight tails that do play -- same rate, overlapping size ratios, all inside
# their slots -- so the difference is the page's own display window, which lives
# in the .sdl and is not decoded. These caps shrink just those two by tempo
# alone, to find the window empirically.
# Binary search on the real window, by ear:
#   2.46 / 1.46  silent   (the original split lengths)
#   1.19 / 0.81  PLAYS, but rushed
# Now the midpoint. Capcom's own files here are 3.01 s and 2.38 s and do not
# play either, so these pages are silent beats in the Japanese and the window is
# genuinely shorter than the audio Capcom left in them.
# Split points chosen by GRAMMAR, not by loudness. The acoustic search picks the
# quietest point near a size-derived target, which lands mid-word when the
# delivery has no pause there -- five of ten did. A clause boundary is where a
# listener expects the break, so the target comes from the TEXT: the fraction of
# the sentence up to the given word. The quiet search still runs, but around the
# right place.
TEXT_SPLIT = {
    '01000_00020_nrt': 'In time, there came from the ventilator',
    '01000_00030_nrt': 'Suddenly, Sholmes sprang into action,',
    '01000_00080_nrt': 'I believe this is the terrible coil',
    '01000_00090_nrt': 'In front of us was an enormous adder,',
    # "...'speckled band' | I had ever seen." lands on clean silence (rms 11)
    # but leaves the first half needing 1.56x at 64% quality, worse than the
    # mid-word cut it replaces. Left to the acoustic search.
    # '01000_00100_nrt': "It truly was the most terrible 'speckled band'",
}

# Split points found by scanning for real silence and then reading which word
# sits there, rather than predicting the timestamp from character counts. The
# actor does not always pause where the grammar does.
#   00020  3.54 s  rms    1  true silence, after "a hiss and a soft, almost"
#   00080  1.49 s  rms  202  nearly clean, after "I believe this is the terrible"
#   00030         rms 1492  is the QUIETEST point in the whole take -- the line
#                           is delivered in one breath and has no gap to find,
#                           so it keeps the mathematical split and the 18 ms fade.
#   00080  1.49 s cleans the cut (1718 -> 206) but pushes its tail to 70%
#          quality and 1.43x, the same degradation that was audible elsewhere.
#          Not worth it; left to the acoustic search with its fade.
TIME_SPLIT = {'01000_00020_nrt': 3.54}

TAIL_CAP = {'01000_00015_nrt': 1.80, '01000_00065_nrt': 1.13}
QUIET_OK = 200


SENTENCES = {}


MAX_TEMPO = 2.40          # the two capped tails need more than a normal line
FADE_MS = 18              # softens a cut that had to land mid-word


def soften(pcm, rate, head, tail):
    """Short fades at a join, so a mid-word cut is not a click.

    Half the splits cannot land on silence -- the sentence simply has no pause
    where the page boundary falls. A hard edge there reads as a pop, which is
    more noticeable than the cut itself. An 18 ms ramp removes it."""
    n = int(rate * FADE_MS / 1000.0)
    if n < 8 or len(pcm) < 2 * n:
        return pcm
    out = np.asarray(pcm, dtype=np.float64).copy()
    if head:
        out[:n] *= np.linspace(0.0, 1.0, n)
    if tail:
        out[-n:] *= np.linspace(1.0, 0.0, n)
    return out.astype(np.int16)


def text_fraction(first, whole):
    """How far through the sentence the clause boundary falls."""
    a = ''.join(first.split()).lower()
    b = ''.join(whole.split()).lower()
    i = b.find(a[:max(8, len(a) // 2)])
    return (len(a) / len(b)) if len(b) else 0.5


def find_gap(pcm, rate, da, db, window=1.4, frac=None):
    """Pick the split that leaves BOTH halves easiest to fit, not the quietest.

    Scoring on silence alone starved a slot: one pair split at 38% where the
    slot sizes wanted 55/45, so the small half needed both 1.35x compression
    AND a drop to 70% sample rate, and it is audibly worse than its neighbours.
    What actually matters is how hard each half then has to be squeezed, so
    score candidates by the WORST squeeze they produce and break ties on
    quietness.

    Returns the silence run (start, end) so the pause belongs to neither half.
    """
    total = len(pcm) / rate
    target = total * (frac if frac is not None else da / (da + db))
    if frac is not None:
        # A clause boundary is WHERE THE BREAK BELONGS, so search tightly around
        # it and take the quietest point there rather than letting the squeeze
        # constraint drag the cut back to a louder but better-balanced spot. A
        # wide window plus that constraint moved these splits by 0.00 s.
        window = 0.35
    w = int(rate * 0.10)
    lo = max(0, int((target - window) * rate))
    hi = min(len(pcm) - w, int((target + window) * rate))
    if hi <= lo:
        c = int(target * rate)
        return c, c, 1e9
    e = np.abs(pcm[lo:hi + w]).astype(np.float64)
    conv = np.convolve(e, np.ones(w) / w, mode='valid')
    # Two goals that genuinely conflict on some pairs: cut on silence, and leave
    # both halves easy to fit. Weighting them against each other just trades one
    # flaw for the other, so treat the squeeze as a CONSTRAINT and optimise
    # quietness within it. Only if nothing satisfies the constraint does the
    # least-squeezed candidate win.
    SQUEEZE_LIMIT = 1.20
    ok, fallback = None, None
    for i in range(0, len(conv), max(1, int(rate * 0.02))):
        mid = lo + i + w // 2
        first, second = mid / rate, total - mid / rate
        squeeze = max(first / da if da else 9, second / db if db else 9)
        lvl = float(conv[i])
        if frac is not None or squeeze <= SQUEEZE_LIMIT:
            if ok is None or lvl < ok[2]:
                ok = (lvl, mid, lvl, squeeze)
        if fallback is None or squeeze < fallback[3]:
            fallback = (squeeze, mid, lvl, squeeze)
    best = ok or fallback
    _, mid, lvl, _ = best
    a = np.abs(pcm)
    st = mid
    while st > 0 and a[st - 1] <= QUIET_OK:
        st -= 1
    en = mid
    while en < len(a) and a[en] <= QUIET_OK:
        en += 1
    return st, en, lvl


def capacity(h):
    return (h['data_size'] // 8) * 14


def compress(pcm, rate, target_secs):
    """Speed the take up to `target_secs` without changing its pitch."""
    have = len(pcm) / rate
    if have <= target_secs or target_secs <= 0:
        return pcm, 1.0
    tempo = min(have / target_secs, MAX_TEMPO)
    chain, t = [], tempo
    while t > 2.0:                      # atempo only accepts 0.5..2.0 per stage
        chain.append(2.0); t /= 2.0
    chain.append(t)
    r = subprocess.run(
        [I.FFMPEG, '-hide_banner', '-loglevel', 'error',
         '-f', 's16le', '-ar', str(rate), '-ac', '1', '-i', '-',
         '-filter:a', ','.join('atempo=%.6f' % c for c in chain),
         '-f', 's16le', '-'],
        input=np.asarray(pcm, dtype=np.int16).tobytes(), capture_output=True)
    if r.returncode or not r.stdout:
        return pcm, 1.0
    return np.frombuffer(r.stdout, dtype='<i2'), tempo


def fit(name, pcm_at, rate, seg_bounds):
    """Lower the rate until this half fits its own slot, keeping every word."""
    cap = os.path.join(I.JP, 'wav', name + '.mca')
    room = capacity(mca.parse(cap))
    lo, hi = seg_bounds
    r = rate
    while True:
        seg = pcm_at(r)[lo(r):hi(r)]
        if len(seg) <= room or r <= 8000:
            return seg, r
        r = max(8000, int(r * room / len(seg)) - 1)


def build(name, pcm, rate):
    cap = os.path.join(I.JP, 'wav', name + '.mca')
    donor = open(cap, 'rb').read()
    h = mca.parse(cap)
    adpcm, coefs = dsp.encode(list(np.asarray(pcm, dtype=np.int16)))
    size = (len(adpcm) + 255) // 256 * 256
    d = bytearray(donor[:h['data_off']])
    struct.pack_into('<I', d, 0x0C, len(pcm))
    struct.pack_into('<I', d, 0x10, rate)
    struct.pack_into('<I', d, 0x20, size)
    struct.pack_into('<16h', d, 0x38, *coefs)
    struct.pack_into('<4h', d, 0x58, h['gain'], h['ps'], 0, 0)
    return bytes(d) + adpcm + bytes(size - len(adpcm)), len(pcm), len(donor)


def load_sentences():
    """The on-screen text for each text page, to locate a clause boundary in."""
    import gmdwalk
    root = os.path.join(I.SCRATCH, 'build', 'sp2', 'romfs00')
    if not os.path.isdir(root):
        return
    msg = [v for k, v in gmdwalk.gmds(root).items()
           if k.endswith('opdemo01_jpn.gmd')]
    if not msg:
        return
    labs = sorted(msg[0])
    for i, k in enumerate(range(10, 110, 5)):
        t = gmdwalk.visible(msg[0][labs[i]])
        if t:
            SENTENCES['01000_%05d_nrt' % k] = t


def main():
    load_sentences()
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--apply')
    a = ap.parse_args()
    updates, rough = {}, []
    for first, second in PAIRS:
        ha = mca.parse(os.path.join(I.JP, 'wav', first + '.mca'))
        hb = mca.parse(os.path.join(I.JP, 'wav', second + '.mca'))
        rate = ha['rate']
        da, db = ha['samples'] / rate, hb['samples'] / rate
        pcm = I.trim_edges(I.decode(os.path.join(I.PC, first + '_eng.sngw'), rate))
        if first in WHOLE_ON_FIRST:
            # give the text page the entire sentence; it holds long enough to
            # play what the oversize probe showed it will
            whole, tw = compress(pcm, rate, da * 1.55)
            blob, n, cap_sz = build(first, whole, rate)
            room = capacity(mca.parse(os.path.join(I.JP, 'wav', first + '.mca')))
            r = rate
            while len(whole) > room and r > 12000:
                r = max(12000, int(r * room / len(whole)) - 1)
                whole, tw = compress(I.trim_edges(I.decode(
                    os.path.join(I.PC, first + '_eng.sngw'), r)), r, da * 1.55)
            blob, n, _ = build(first, whole, r)
            open(os.path.join(a.apply, 'sound', 'stream', 'voice', 'wav',
                              first + '.mca'), 'wb').write(blob) if a.apply else None
            updates[first] = (len(blob), n, r)
            sil = np.zeros(int(rate * 0.05), np.int16)
            sblob, sn, _ = build(second, sil, rate)
            if a.apply:
                open(os.path.join(a.apply, 'sound', 'stream', 'voice', 'wav',
                                  second + '.mca'), 'wb').write(sblob)
            updates[second] = (len(sblob), sn, rate)
            print('  %-16s WHOLE on the text page  %4.2fs @%5d x%.2f  | %s silenced'
                  % (first[6:], n / r, r, tw, second[6:11]))
            continue
        frac = None
        if first in TIME_SPLIT:
            frac = TIME_SPLIT[first] / (len(pcm) / rate)
        elif first in TEXT_SPLIT:
            whole = SENTENCES.get(first)
            if whole:
                frac = text_fraction(TEXT_SPLIT[first], whole)
        gs, ge, lvl = find_gap(pcm, rate, da, db, frac=frac)
        if lvl > QUIET_OK:
            rough.append((first, lvl))
        f_end, f_start = gs / len(pcm), ge / len(pcm)
        cache = {}

        def at(r, _f=first):
            if r not in cache:
                cache[r] = I.trim_edges(I.decode(
                    os.path.join(I.PC, _f + '_eng.sngw'), r))
            return cache[r]
        cache[rate] = pcm
        # each half is trimmed on its own, so neither page opens on the pause
        s1, r1 = fit(first, at, rate,
                     (lambda r: 0, lambda r, f=f_end: int(len(at(r)) * f)))
        s2, r2 = fit(second, at, rate,
                     (lambda r, f=f_start: int(len(at(r)) * f), lambda r: len(at(r))))
        s1, s2 = I.trim_edges(s1), I.trim_edges(s2)
        # now make each half fit its slot's DURATION, which is what the page
        # timer enforces
        s1, t1 = compress(s1, r1, da)
        s2, t2 = compress(s2, r2, TAIL_CAP.get(second, db))
        # only the join needs softening: the outer ends are real silence
        rough_cut = lvl > QUIET_OK
        s1 = soften(s1, r1, head=False, tail=rough_cut)
        s2 = soften(s2, r2, head=rough_cut, tail=False)
        parts = ((first, s1, r1), (second, s2, r2))
        line = '  %-16s split %5.2f-%5.2fs rms %5.0f  ' % (first[6:], gs / rate, ge / rate, lvl)
        for nm, seg, r in parts:
            blob, n, cap_size = build(nm, seg, r)
            updates[nm] = (len(blob), n, r)
            line += '| %s %4.2fs @%5d x%.2f ' % (nm[6:11], n / r, r,
                                                 t1 if nm == first else t2)
            if a.apply:
                p = os.path.join(a.apply, 'sound', 'stream', 'voice', 'wav', nm + '.mca')
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, 'wb').write(blob)
        print(line)
    if rough:
        print('  no clean gap found for: %s' % ', '.join('%s (rms %.0f)' % r for r in rough))
    if not a.apply:
        return
    vd = os.path.join(a.apply, 'sound', 'stream', 'voice')
    for st in [f for f in os.listdir(vd) if f.endswith('.stqr')]:
        p = os.path.join(vd, st)
        b = bytearray(open(p, 'rb').read())
        pat = ('sound' + BS + 'stream' + BS + 'voice' + BS + 'wav' + BS).encode()
        names = [m.group(0).decode().split(BS)[-1]
                 for m in re.finditer(re.escape(pat) + rb'[ -~]+', bytes(b))]
        hit = 0
        for i, nm in enumerate(names):
            if nm not in updates:
                continue
            s, n, r = updates[nm]
            o = 0x1C + i * 36
            struct.pack_into('<II', b, o, s, n)
            struct.pack_into('<I', b, o + 12, r)
            hit += 1
        if hit:
            open(p, 'wb').write(bytes(b))
            print('  %s: %d index records synced' % (st, hit))


if __name__ == '__main__':
    main()

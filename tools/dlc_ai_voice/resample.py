# -*- coding: utf-8 -*-
"""Band-limited resampling in numpy, because ffmpeg is not on this machine.

`fit_slots.resample` shells out to ffmpeg and warns that linear interpolation
would alias -- which is right, and matters here: every source is 48 kHz and
every 3DS slot is 22.05 kHz, so more than half the band has to come out before
decimation or it folds back over the shout.

Windowed-sinc (Kaiser, beta 8.6, 32 zero crossings), cutoff at 95% of the new
Nyquist. Tested in --selftest against tones either side of that cutoff.
"""
import numpy as np

ZEROS = 32          # sinc half-width in zero crossings
BETA = 8.6          # Kaiser beta: ~ -90 dB stopband


def resample(pcm, src_rate, dst_rate):
    """int16 sequence at src_rate -> int16 numpy array at dst_rate."""
    if src_rate == dst_rate:
        return np.asarray(pcm, dtype=np.int16)
    x = np.asarray(pcm, dtype=np.float64)
    ratio = float(dst_rate) / float(src_rate)
    # Downsampling must lower the cutoff; upsampling keeps the source band.
    cutoff = 0.95 * min(1.0, ratio)
    half = int(np.ceil(ZEROS / cutoff))

    n_out = int(np.floor(len(x) * ratio))
    if n_out < 1:
        return np.zeros(0, dtype=np.int16)
    centres = np.arange(n_out) / ratio
    left = np.floor(centres).astype(np.int64) - half + 1
    # offsets[j, k] = distance from output j to the k'th source sample it uses
    taps = np.arange(2 * half)
    idx = left[:, None] + taps[None, :]
    dist = centres[:, None] - idx

    w = np.sinc(cutoff * dist) * cutoff
    # Kaiser window over the same support, zero outside it
    r = dist / half
    inside = np.abs(r) <= 1.0
    w *= np.where(inside, np.i0(BETA * np.sqrt(np.maximum(0.0, 1 - r * r)))
                  / np.i0(BETA), 0.0)

    padded = np.concatenate([np.zeros(half), x, np.zeros(half + 2)])
    y = (w * padded[np.clip(idx + half, 0, len(padded) - 1)]).sum(axis=1)
    return np.clip(np.rint(y), -32768, 32767).astype(np.int16)


def _selftest():
    """A tone below the new Nyquist must survive; one above must not alias in."""
    src, dst = 48000, 22050
    t = np.arange(src) / src
    ok = True
    for freq, expect in ((1000, 'pass'), (4000, 'pass'), (18000, 'reject')):
        tone = (np.sin(2 * np.pi * freq * t) * 20000).astype(np.int16)
        out = resample(tone, src, dst)
        # measure energy at the frequency the tone would fold back to
        f = freq if freq < dst / 2 else abs(dst - freq)
        n = len(out)
        k = np.exp(-2j * np.pi * f * np.arange(n) / dst)
        amp = 2 * abs((out * k).sum()) / n
        got = 'pass' if amp > 5000 else 'reject'
        print('   %5d Hz -> %-6s (amplitude %8.1f)  %s'
              % (freq, got, amp, 'OK' if got == expect else 'FAILED'))
        ok &= got == expect
    # length and level
    out = resample(np.zeros(48000, dtype=np.int16) + 1000, src, dst)
    print('   length 1.000s -> %.3fs  %s'
          % (len(out) / dst, 'OK' if abs(len(out) / dst - 1) < 0.001 else 'FAILED'))
    return ok


if __name__ == '__main__':
    raise SystemExit(0 if _selftest() else 1)

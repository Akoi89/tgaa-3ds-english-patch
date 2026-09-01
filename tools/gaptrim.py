# -*- coding: utf-8 -*-
"""Reclaim slot capacity by shortening the SILENCE inside a line, not the speech.

A streamed clip must fit Capcom's slot in bytes, and bytes scale with
duration x sample_rate. Until now the only lever for an over-long English take
was dropping the sample rate, which costs fidelity on every sample. Shortening
the pauses between phrases costs nothing at all -- the speech itself is
untouched, only the dead air between phrases gets shorter.

Gap detection MUST use an energy envelope, not absolute amplitude. Capcom's
masters carry a noise floor well above a fixed threshold like |x| > 150, so an
amplitude test reports a line as having no pauses at all when it really has
600 ms ones. Measured here as 10 ms RMS windows below 2% of the clip's peak.

Trimming is applied at the LEAST aggressive floor that achieves the goal, so a
clip that needs very little keeps almost all of its natural rhythm.
"""
import numpy as np

WIN = 0.010          # 10 ms analysis window
QUIET_FRAC = 0.02    # below 2% of peak RMS counts as silence
# Floors the ear test APPROVED, gentlest first. 200ms and 150ms both landed as
# natural beats. 100ms did not: on a rapid-fire delivery it swallowed the breath
# markers and the read sounded spliced. So the ladder stops at 150ms -- a clip
# that cannot be rescued without trimming harder is left as it is, because the
# whole point is that the speech is untouched.
FLOORS = (0.200, 0.150)
# The full ladder, for measurement only. Do NOT use it to build shipping audio.
FLOORS_EXPERIMENTAL = (0.200, 0.150, 0.120, 0.100, 0.080, 0.060, 0.050)


def gaps(pcm, rate):
    """[(start, end)] sample indices of interior silence runs."""
    w = int(WIN * rate)
    if w < 1 or len(pcm) < w * 3:
        return []
    m = len(pcm) // w
    env = np.sqrt((pcm[:m * w].astype(np.float64).reshape(m, w) ** 2).mean(1))
    if not env.max():
        return []
    quiet = env < QUIET_FRAC * env.max()
    d = np.diff(np.concatenate(([0], quiet.view(np.int8), [0])))
    out = []
    for s, e in zip(np.where(d == 1)[0], np.where(d == -1)[0]):
        if s == 0 or e == m:          # leading/trailing handled by edge trim
            continue
        out.append((s * w, e * w))
    return out


def shrink(pcm, rate, floor):
    """Cap every interior silence run at `floor` seconds."""
    keep = int(floor * rate)
    g = [(s, e) for s, e in gaps(pcm, rate) if e - s > keep]
    if not g:
        return pcm
    parts, prev = [], 0
    for s, e in g:
        parts.append(pcm[prev:s + keep])
        prev = e
    parts.append(pcm[prev:])
    return np.concatenate(parts)


def fit(pcm, rate, cap):
    """Smallest trim that fits `cap` samples. -> (pcm, floor_used or None)."""
    if len(pcm) <= cap:
        return pcm, None
    for f in FLOORS:
        out = shrink(pcm, rate, f)
        if len(out) <= cap:
            return out, f
    return shrink(pcm, rate, FLOORS[-1]), FLOORS[-1]

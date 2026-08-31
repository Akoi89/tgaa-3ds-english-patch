# -*- coding: utf-8 -*-
"""Nintendo DSP-ADPCM encoder -- the codec inside Capcom's .mca / MADP files.

ffmpeg decodes this codec (adpcm_thp) but cannot write it, so this is a port of
the reference encoder: correlate_coefs() derives the 8 predictor pairs from the
audio, _encode_frame() packs 14 samples into 8 bytes by trying every predictor
and every scale and keeping whichever gives the least squared error.

Validate any change with encode_shouts.py --selftest, which re-encodes Capcom's
own audio and reports SNR against their original.
"""
import math

EPS = 2.2204460492503131e-16


def _idiv(a, b):
    """C integer division: truncates toward zero (Python's // floors)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _clamp16(v):
    return 32767 if v > 32767 else (-32768 if v < -32768 else v)


# ---------------------------------------------------------------- coefficients

def _inner_product_merge(buf, off):
    return [-sum(buf[off + x - i] * buf[off + x] for x in range(14))
            for i in range(3)]


def _outer_product_merge(buf, off):
    m = [[0.0] * 3 for _ in range(3)]
    for x in (1, 2):
        for y in (1, 2):
            m[x][y] = float(sum(buf[off + z - x] * buf[off + z - y]
                                for z in range(14)))
    return m


def _analyze_ranges(mtx, idxs):
    recips = [0.0] * 3
    for x in (1, 2):
        val = max(abs(mtx[x][1]), abs(mtx[x][2]))
        if val < EPS:
            return True
        recips[x] = 1.0 / val

    max_index = 0
    for i in (1, 2):
        for x in range(1, i):
            tmp = mtx[x][i]
            for y in range(1, x):
                tmp -= mtx[x][y] * mtx[y][i]
            mtx[x][i] = tmp
        val = 0.0
        for x in range(i, 3):
            tmp = mtx[x][i]
            for y in range(1, i):
                tmp -= mtx[x][y] * mtx[y][i]
            mtx[x][i] = tmp
            t = abs(tmp) * recips[x]
            if t >= val:
                val = t
                max_index = x
        if max_index != i:
            for y in (1, 2):
                mtx[max_index][y], mtx[i][y] = mtx[i][y], mtx[max_index][y]
            recips[max_index] = recips[i]
        idxs[i] = max_index
        if mtx[i][i] == 0.0:
            return True
        if i != 2:
            tmp = 1.0 / mtx[i][i]
            for x in range(i + 1, 3):
                mtx[x][i] *= tmp

    mn, mx = 1.0e10, 0.0
    for i in (1, 2):
        t = abs(mtx[i][i])
        mn = min(mn, t)
        mx = max(mx, t)
    return (mn / mx) < 1.0e-10


def _bidirectional_filter(mtx, idxs, vec):
    x = 0
    for i in (1, 2):
        index = idxs[i]
        tmp = vec[index]
        vec[index] = vec[i]
        if x != 0:
            for y in range(x, i):
                tmp -= vec[y] * mtx[i][y]
        elif tmp != 0.0:
            x = i
        vec[i] = tmp
    for i in (2, 1):
        tmp = vec[i]
        for y in range(i + 1, 3):
            tmp -= vec[y] * mtx[i][y]
        vec[i] = tmp / mtx[i][i]
    vec[0] = 1.0


def _quadratic_merge(v):
    v2 = v[2]
    tmp = 1.0 - v2 * v2
    if tmp == 0.0:
        return True
    v0 = (v[0] - v2 * v2) / tmp
    v1 = (v[1] - v[1] * v2) / tmp
    v[0], v[1] = v0, v1
    return abs(v1) > 1.0


def _finish_record(src, dst):
    a = list(src)
    for z in (1, 2):
        if a[z] >= 1.0:
            a[z] = 0.9999999999
        elif a[z] <= -1.0:
            a[z] = -0.9999999999
    dst[0] = 1.0
    dst[1] = a[2] * a[1] + a[1]
    dst[2] = a[2]


def _matrix_filter(src, dst):
    m = [[0.0] * 3 for _ in range(3)]
    m[2][0] = 1.0
    for i in (1, 2):
        m[2][i] = -src[i]
    for i in (2, 1):
        val = 1.0 - m[i][i] * m[i][i]
        for y in range(1, i + 1):
            m[i - 1][y] = (m[i][i] * m[i][i - y] + m[i][y]) / val
    dst[0] = 1.0
    for i in (1, 2):
        dst[i] = 0.0
        for y in range(1, i + 1):
            dst[i] += m[i][y] * dst[i - y]


def _merge_finish_record(src, dst):
    tmp = [0.0] * 3
    val = src[0]
    dst[0] = 1.0
    for i in (1, 2):
        v2 = 0.0
        for y in range(1, i):
            v2 += dst[y] * src[i - y]
        dst[i] = -(v2 + src[i]) / val if val > 0.0 else 0.0
        tmp[i] = dst[i]
        for y in range(1, i):
            dst[y] += dst[i] * dst[i - y]
        val *= 1.0 - dst[i] * dst[i]
    _finish_record(tmp, dst)


def _contrast_vectors(s1, s2):
    val = (s2[2] * s2[1] + -s2[1]) / (1.0 - s2[2] * s2[2])
    val1 = s1[0] * s1[0] + s1[1] * s1[1] + s1[2] * s1[2]
    val2 = s1[0] * s1[1] + s1[1] * s1[2]
    val3 = s1[0] * s1[2]
    return val1 + 2.0 * val * val2 + 2.0 * (-s2[1] * val + -s2[2]) * val3


def _filter_records(vec_best, exp, records):
    for _ in range(2):
        counts = [0] * exp
        buffers = [[0.0] * 3 for _ in range(exp)]
        tmp = [0.0] * 3
        for rec in records:
            index, value = 0, 1.0e30
            for i in range(exp):
                t = _contrast_vectors(vec_best[i], rec)
                if t < value:
                    value, index = t, i
            counts[index] += 1
            _matrix_filter(rec, tmp)
            for i in range(3):
                buffers[index][i] += tmp[i]
        for i in range(exp):
            if counts[i] > 0:
                for y in range(3):
                    buffers[i][y] /= counts[i]
        for i in range(exp):
            _merge_finish_record(buffers[i], vec_best[i])


def correlate_coefs(samples):
    """samples: sequence of int16 -> list of 16 int16 coefficients."""
    # plain Python ints: numpy int16 silently overflows in the products below
    samples = [int(v) for v in samples]
    records = []
    hist = [0] * 28              # two 14-sample frames; current starts at 14
    n = len(samples)
    pos = 0
    while pos < n:
        block = list(samples[pos:pos + 0x3800])
        pos += 0x3800
        if len(block) % 14:
            block += [0] * (14 - len(block) % 14)
        i = 0
        while i < len(block):
            hist[0:14] = hist[14:28]
            hist[14:28] = block[i:i + 14]
            i += 14
            vec = _inner_product_merge(hist, 14)
            if abs(vec[0]) > 10.0:
                mtx = _outer_product_merge(hist, 14)
                idxs = [0, 0, 0]
                if not _analyze_ranges(mtx, idxs):
                    _bidirectional_filter(mtx, idxs, vec)
                    if not _quadratic_merge(vec):
                        rec = [0.0] * 3
                        _finish_record(vec, rec)
                        # a frame whose reflection coefficient lands on exactly
                        # +/-1 makes _matrix_filter divide by zero (C would emit
                        # inf); drop it -- one candidate among tens of thousands
                        try:
                            _matrix_filter(rec, [0.0] * 3)
                        except ZeroDivisionError:
                            continue
                        records.append(rec)

    if not records:
        return [0] * 16

    vec_best = [[0.0] * 3 for _ in range(8)]
    vec1 = [1.0, 0.0, 0.0]
    tmp = [0.0] * 3
    for rec in records:
        _matrix_filter(rec, tmp)
        for y in (1, 2):
            vec1[y] += tmp[y]
    for y in (1, 2):
        vec1[y] /= len(records)
    _merge_finish_record(vec1, vec_best[0])

    exp = 1
    for w in range(3):
        vec2 = [0.0, -1.0, 0.0]
        for i in range(exp):
            for y in range(3):
                vec_best[exp + i][y] = 0.01 * vec2[y] + vec_best[i][y]
        exp = 1 << (w + 1)
        _filter_records(vec_best, exp, records)

    out = []
    for z in range(8):
        for k in (1, 2):
            d = -vec_best[z][k] * 2048.0
            if d > 0.0:
                out.append(32767 if d > 32767.0 else int(round(d)))
            else:
                out.append(-32768 if d < -32768.0 else int(round(d)))
    return out


# --------------------------------------------------------------------- frames

def _encode_frame(pcm, count, coefs):
    """pcm: list of 16 ints (2 history + 14). Returns 8 packed bytes."""
    in_s = [[0] * 16 for _ in range(8)]
    out_s = [[0] * 14 for _ in range(8)]
    scale = [0] * 8
    dist_accum = [0.0] * 8

    for i in range(8):
        c0, c1 = coefs[i * 2], coefs[i * 2 + 1]
        in_s[i][0], in_s[i][1] = pcm[0], pcm[1]
        distance = 0
        for s in range(count):
            v1 = _idiv(pcm[s] * c1 + pcm[s + 1] * c0, 2048)
            in_s[i][s + 2] = v1
            v3 = _clamp16(pcm[s + 2] - v1)
            if abs(v3) > abs(distance):
                distance = v3
        sc = 0
        while sc <= 12 and (distance > 7 or distance < -8):
            sc += 1
            distance = _idiv(distance, 2)
        scale[i] = -1 if sc <= 1 else sc - 2

        while True:
            scale[i] += 1
            dist_accum[i] = 0.0
            index = 0
            step = 1 << scale[i]
            for s in range(count):
                v1 = in_s[i][s] * c1 + in_s[i][s + 1] * c0
                v2 = _idiv((pcm[s + 2] << 11) - v1, 2048)
                if v2 > 0:
                    v3 = int(v2 / step + 0.4999999)
                else:
                    v3 = int(v2 / step - 0.4999999)
                if v3 < -8:
                    t = -8 - v3
                    if index < t:
                        index = t
                    v3 = -8
                elif v3 > 7:
                    t = v3 - 7
                    if index < t:
                        index = t
                    v3 = 7
                out_s[i][s] = v3
                v1 = (v1 + ((v3 * step) << 11) + 1024) >> 11
                v2 = _clamp16(v1)
                in_s[i][s + 2] = v2
                d = pcm[s + 2] - v2
                dist_accum[i] += float(d) * d
            x = index + 8
            while x > 256:
                x >>= 1
                scale[i] += 1
                if scale[i] >= 12:
                    scale[i] = 11
            if not (scale[i] < 12 and index > 1):
                break

    best = min(range(8), key=lambda i: dist_accum[i])
    for s in range(count):
        pcm[s + 2] = in_s[best][s + 2]
    for s in range(count, 14):
        out_s[best][s] = 0
    frame = bytearray(8)
    frame[0] = ((best << 4) | (scale[best] & 0x0F)) & 0xFF
    for y in range(7):
        frame[y + 1] = ((out_s[best][y * 2] << 4) |
                        (out_s[best][y * 2 + 1] & 0x0F)) & 0xFF
    return bytes(frame)


def encode(samples, coefs=None):
    """int16 sequence -> (adpcm bytes, coefficients)."""
    samples = [int(v) for v in samples]
    if coefs is None:
        coefs = correlate_coefs(samples)
    out = bytearray()
    pcm = [0] * 16
    n = len(samples)
    i = 0
    while i < n:
        count = min(14, n - i)
        pcm[2:16] = list(samples[i:i + count]) + [0] * (14 - count)
        out += _encode_frame(pcm, count, coefs)
        pcm[0], pcm[1] = pcm[14], pcm[15]
        i += count
    return bytes(out), coefs

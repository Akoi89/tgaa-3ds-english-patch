"""Decode the TGAA1 banner CWAV (stereo DSP-ADPCM) to WAV, decode Chronicles'
Japanese and English Naruhodo 'igiari' shouts, and report lengths/correlation."""
import os, struct, sys, wave
import numpy as np
R = os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2')
sys.path.insert(0, os.path.join(R, r'dlc_story_audit\audio_tools')); sys.path.insert(0, os.path.join(R, 'dlc_ai_voice'))
import mca, msadpcm
HB = os.path.join(R, r'dlc_story_audit\_validation\home_banner')


def cwav_decode(path):
    w = open(path, 'rb').read(); nsec = struct.unpack_from('<H', w, 0x10)[0]
    secs = {t: (o, s) for t, _, o, s in (struct.unpack_from('<HHII', w, 0x14 + i * 12) for i in range(nsec))}
    io, isz = secs[0x7000]; info = w[io:io + isz]
    enc, loop, _, _, rate, ls, le = struct.unpack_from('<BBBBIII', info, 8); n = struct.unpack_from('<I', info, 8 + 0x14)[0]
    do, dsz = secs[0x7001]; chans = []
    for c in range(n):
        ro = struct.unpack_from('<HHI', info, 8 + 0x18 + c * 8)[2]; ci = 8 + 0x14 + ro
        so = struct.unpack_from('<HHI', info, ci)[2]; ao = struct.unpack_from('<HHI', info, ci + 8)[2]
        coefs = struct.unpack_from('<16h', info, ci + ao)
        start = do + 8 + so; nbytes = (le + 13) // 14 * 8
        pcm = mca.decode({'coef': list(coefs), 'adpcm': w[start:start + nbytes], 'samples': le, 'h1': 0, 'h2': 0})
        chans.append(np.asarray(pcm, np.int16)[:le])
    return np.stack(chans, 1), rate


def save(path, x, rate):
    x = np.asarray(x, np.int16); ch = 1 if x.ndim == 1 else x.shape[1]
    with wave.open(path, 'wb') as f:
        f.setnchannels(ch); f.setsampwidth(2); f.setframerate(rate); f.writeframes(x.tobytes())


b, br = cwav_decode(os.path.join(HB, 'tgaa1_dump', 'banner.bcwav'))
save(os.path.join(HB, 'tgaa1_banner_sound.wav'), b, br)
print('banner: %d samples, %d Hz, %.2f s, peak L %d R %d, L==R %s' % (len(b), br, len(b) / br, abs(b[:, 0]).max(), abs(b[:, 1]).max(), bool((b[:, 0] == b[:, 1]).all())))
S = os.path.join(R, r'TGAAC Steam\nativeDX11x64\sound\se\go_se_chr000\wav')
for lang in ('jpn', 'eng'):
    x, r = msadpcm.decode(os.path.join(S, 'chr000_nhd_v_igiari_%s.xsew' % lang)); x = np.asarray(x, np.int16)
    save(os.path.join(HB, 'nhd_igiari_%s.wav' % lang), x, r)
    nz = np.nonzero(abs(x.astype(int)) > 300)[0]
    print('%s shout: %d samples, %d Hz, %.2f s (voiced %.2f..%.2f s), peak %d' % (lang, len(x), r, len(x) / r, nz[0] / r, nz[-1] / r, abs(x).max()))
# envelope correlation banner-mono vs jp shout (resampled to banner rate)
m = b.mean(1)
xj, rj = msadpcm.decode(os.path.join(S, 'chr000_nhd_v_igiari_jpn.xsew')); xj = np.asarray(xj, np.float64)
t = np.arange(int(len(xj) * br / rj)) * (rj / br); xr = np.interp(t, np.arange(len(xj)), xj)
def env(x, n=256): return np.array([np.abs(x[i:i + n]).mean() for i in range(0, len(x) - n, n)])
ea, eb = env(m), env(xr); best = (0, -1)
for lag in range(-len(eb), len(ea)):
    a0, a1 = max(0, lag), min(len(ea), lag + len(eb)); s = eb[a0 - lag:a1 - lag]; q = ea[a0:a1]
    if len(q) > 10 and q.std() and s.std():
        c = np.corrcoef(q, s)[0, 1]
        if c > best[1]: best = (lag, c)
print('envelope correlation banner vs JP shout: %.2f at lag %.2f s' % (best[1], best[0] * 256 / br))

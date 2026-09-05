"""Replace the banner's CWAV (the HOME-menu sound) with a WAV file.

    python banner_cwav.py <banner.bin in> <clip.wav> <banner.bin out> [--match-level]

Only PCM16 banner CWAVs are handled (Puyo Puyo Tetris and most games; if
banner_extract.py reports encoding 2 the clip is DSP-ADPCM and this script
stops). The WAV may be mono or stereo, any rate: it is resampled to the
banner's rate and mapped to the banner's channel count. --match-level scales
it (through a peak limiter) to the loudness of the clip it replaces.

CWAV layout used: 0x40 header (file size at 0x0C; section table INFO at 0x14,
DATA at 0x20); INFO, offsets from the INFO section start: encoding u8 at +8,
rate +0xC, loop start +0x10, loop end (= sample count) +0x14, channel count
+0x1C, channel refs after it; each channel's sample ref offset is relative
to DATA+8; DATA = 'DATA' + size + 0x18 padding + channel blocks (8-aligned).
"""
import math, struct, sys, wave
import numpy as np
import csar


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x.astype(np.float64)
    t = np.arange(int(round(len(x) * sr_out / sr_in))) * (sr_in / sr_out)
    half = 16; win = np.kaiser(2 * half + 1, 8.0); cutoff = 0.5 * min(1.0, sr_out / sr_in)
    base = np.floor(t).astype(int); frac = t - base; y = np.zeros(len(t)); xf = x.astype(np.float64)
    for k in range(-half, half + 1):
        idx = np.clip(base + k, 0, len(xf) - 1); dt = k - frac
        y += xf[idx] * np.sinc(2 * cutoff * dt) * 2 * cutoff * win[k + half]
    return y


def rms(p): return math.sqrt(float((p ** 2).mean())) if len(p) else 1.0


def limiter(y, rate, ceil_db=-0.5):
    ceil = 32768 * 10 ** (ceil_db / 20); look = max(8, int(rate * 0.0015)); rel = max(1, int(rate * 0.06))
    a = np.abs(y); pad = np.concatenate([a, np.zeros(look)])
    env = np.max(np.lib.stride_tricks.sliding_window_view(pad, look + 1), axis=1)[:len(y)]
    need = np.minimum(1.0, ceil / np.maximum(env, 1e-9)); g = np.empty_like(need); cur = 1.0; k = math.exp(-1.0 / rel)
    for i in range(len(need)):
        n = need[i]; cur = n if n < cur else n + (cur - n) * k; g[i] = cur
    return np.clip(y * g, -32768, 32767)


def main(src, wav, out, match=False):
    b = open(src, 'rb').read(); cw = struct.unpack_from('<I', b, 0x84)[0]; w = b[cw:]
    info = csar.cwav_info(w)
    if info['enc'] != 1:
        raise SystemExit('banner CWAV encoding is %d, not PCM16; this script only handles PCM16' % info['enc'])
    io_, isz = info['secs'][0x7000]; do_, dsz = info['secs'][0x7001]; blk = bytearray(w[io_:io_ + isz])
    ct = 8 + 0x14; nch = struct.unpack_from('<I', blk, ct)[0]
    refs = [ct + struct.unpack_from('<HHI', blk, ct + 4 + k * 8)[2] for k in range(nch)]
    old0 = struct.unpack_from('<I', blk, refs[0] + 4)[0]
    old = np.frombuffer(w[do_ + 8 + old0:do_ + 8 + old0 + info['samples'] * 2], dtype='<i2').astype(np.float64)
    with wave.open(wav, 'rb') as f:
        ch, sw, sr, n = f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes(); raw = f.readframes(n)
    assert sw == 2, 'WAV must be 16-bit'
    pcm = np.frombuffer(raw, dtype='<i2').reshape(-1, ch).astype(np.float64)
    chans = [resample(pcm[:, c], sr, info['rate']) for c in range(ch)]
    if nch == 1 and ch > 1: chans = [sum(chans) / ch]
    while len(chans) < nch: chans.append(chans[-1])
    chans = chans[:nch]
    if match:
        g = rms(old) / max(rms(chans[0]), 1.0); chans = [limiter(c * g, info['rate']) for c in chans]
        print('level matched: %+.1f dB' % (20 * math.log10(g)))
    ns = len(chans[0]); blocks = [np.round(c).astype('<i2').tobytes() for c in chans]
    struct.pack_into('<I', blk, 0x10, 0); struct.pack_into('<I', blk, 0x14, ns)
    body = bytes(0x18); pos = 0x18
    for k, s in enumerate(blocks):
        pos = (pos + 7) // 8 * 8; body += bytes(pos - len(body)); struct.pack_into('<I', blk, refs[k] + 4, pos); body += s; pos += len(s)
    body += bytes((-len(body)) % 0x20)
    data = b'DATA' + struct.pack('<I', 8 + len(body)) + body
    head = bytearray(w[:0x40]); struct.pack_into('<I', head, 0x0C, 0x40 + len(blk) + len(data))
    struct.pack_into('<HHII', head, 0x14, 0x7000, 0, 0x40, len(blk)); struct.pack_into('<HHII', head, 0x20, 0x7001, 0, 0x40 + len(blk), len(data))
    new_w = bytes(head) + bytes(blk) + data
    chk = csar.cwav_info(new_w); assert chk['samples'] == ns and chk['rate'] == info['rate']
    open(out, 'wb').write(b[:cw] + new_w)
    print('CWAV %d -> %d bytes (%.2f s -> %.2f s, %d ch, %d Hz); banner %d -> %d bytes; wrote %s'
          % (len(w), len(new_w), info['samples'] / info['rate'], ns / info['rate'], nch, info['rate'], len(b), cw + len(new_w), out))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], '--match-level' in sys.argv)

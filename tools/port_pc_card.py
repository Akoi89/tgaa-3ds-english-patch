# -*- coding: utf-8 -*-
"""Port a Chronicles '_eng' sepia-mask card onto a 3DS RGB8 card.

PC fmt 0x2a stores luminance as G*A (see chronicles-pc-texture-format). The 3DS
card supplies the 20-byte header AND the palette (paper/ink sampled inside the
card region, pad colour outside). Output is fmt 0x11 RGB8 via tex_rgba8.encode_rgb8.
"""
import os
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import pctex_rgba, tex_rgba8


def restore_red(out, jp_bytes):
    """The 3DS map cards mark places with RED boxes and an X; Capcom's PC overlay is
    monochrome. Paint the ported ink red wherever the JP 3DS card is red."""
    jp = tex_rgba8.decode_rgb8(jp_bytes).astype(np.float32)
    red = (jp[..., 0] - np.maximum(jp[..., 1], jp[..., 2]) > 50) & (jp[..., 0] > 90)
    if red.sum() < 20:
        return out
    col = jp[red].mean(axis=0)
    ink = out.astype(np.float32).mean(axis=2) < 150
    m = red & ink
    o = out.copy(); o[m] = np.clip(col + 0.5, 0, 255).astype(np.uint8)
    return o


def port(pc_bytes, donor_bytes, mode='paper', jp_bytes=None, fit_frame=False):
    a = np.asarray(pctex_rgba.decode(pc_bytes)).astype(np.float32)
    L = a[..., 1] * a[..., 3] / 255.0
    inside = a[..., 3] > 4
    ref = tex_rgba8.decode_rgb8(donor_bytes).astype(np.float32)
    H, W = ref.shape[:2]
    if mode == 'gold':                      # text-only overlay on black (end card)
        lum = ref.mean(axis=2); gold = ref[lum >= np.percentile(lum, 99.5)].mean(axis=0)
        Ln = np.clip(L / max(1, np.percentile(L[inside], 99.5)), 0, 1)
        rgb = gold[None, None, :] * Ln[..., None]; alpha = Ln
        base = np.zeros((H, W, 3), np.float32)
    else:
        m_small = np.asarray(Image.fromarray((inside * 255).astype(np.uint8)).resize((W, H), Image.NEAREST)) > 128
        reg = ref[m_small]; rl = reg.mean(axis=1)
        paper = reg[rl >= np.percentile(rl, 90)].mean(axis=0); ink = reg[rl <= np.percentile(rl, 4)].mean(axis=0)
        pad = ref[~m_small].mean(axis=0) if (~m_small).sum() > 50 else np.zeros(3)
        lo, hi = np.percentile(L[inside], [0.5, 99.5]); Ln = np.clip((L - lo) / max(1, hi - lo), 0, 1)
        rgb = ink[None, None, :] + (paper - ink)[None, None, :] * Ln[..., None]; alpha = inside.astype(np.float32)
        base = np.broadcast_to(pad, (H, W, 3)).astype(np.float32).copy()
    if fit_frame and jp_bytes is not None:
        # Capcom's ticket is a small centred box; the 3DS card fills its frame. Crop the
        # PC box and stretch it over the opaque (non-pad) area of the JP 3DS card.
        ys, xs = np.nonzero(inside); cy0, cy1, cx0, cx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        jp = tex_rgba8.decode_rgb8(jp_bytes).astype(np.float32); pad_col = jp[:, int(W * 0.9):].reshape(-1, 3).mean(axis=0)
        card = np.abs(jp - pad_col).sum(axis=2) > 40; ys2, xs2 = np.nonzero(card[:, :int(W * 0.8)])
        fy0, fy1, fx0, fx1 = ys2.min(), ys2.max() + 1, xs2.min(), xs2.max() + 1
        rgb_c = rgb[cy0:cy1, cx0:cx1]; al_c = alpha[cy0:cy1, cx0:cx1]
        rgb = np.zeros((H * 4, W * 4, 3), np.float32) + pad_col; alpha = np.zeros((H * 4, W * 4), np.float32)
        # keep the box's aspect: fit inside the frame, centred
        fw, fh = fx1 - fx0, fy1 - fy0; s = min(fw / (cx1 - cx0), fh / (cy1 - cy0)); nw, nh = round((cx1 - cx0) * s * 4), round((cy1 - cy0) * s * 4)
        ox, oy = round((fx0 + (fw - nw / 4) / 2) * 4), round((fy0 + (fh - nh / 4) / 2) * 4)
        rgb[oy:oy + nh, ox:ox + nw] = np.asarray(Image.fromarray(np.clip(rgb_c, 0, 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS))
        alpha[oy:oy + nh, ox:ox + nw] = np.asarray(Image.fromarray((al_c * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) / 255.0
        # surround = the box's own paper tone (not black), pad strip stays the 3DS pad colour
        paper_c = rgb_c[al_c > 0.9]; paper_c = paper_c[paper_c.mean(axis=1) >= np.percentile(paper_c.mean(axis=1), 80)].mean(axis=0)
        base = np.broadcast_to(pad_col, (H, W, 3)).astype(np.float32).copy(); base[fy0:fy1, fx0:fx1] = paper_c
    port_im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    al = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    out = base * (1 - al[..., None]) + np.asarray(port_im).astype(np.float32) * al[..., None]
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    if jp_bytes is not None and mode == 'paper' and not fit_frame:
        out = restore_red(out, jp_bytes)
    return tex_rgba8.encode_rgb8(donor_bytes, out), out

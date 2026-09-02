# -*- coding: utf-8 -*-
"""Put Capcom's Chronicles title logos (title_1/title_2 _eng masks) into the 3DS
title atlases in place of senyarom's hand-drawn wordmarks.

The PC mask (L = G*A, see chronicles-pc-texture-format) has a solid outline and a
softer fill; BOOST pulls the fill to full coverage so the black/cream sprites
come out solid like the originals.  Sprite rectangles were measured from the
shipped atlases (row/column extents), see the 2026-09-01 session notes.
"""
import os
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import tex_rgba8

BOOST = (0.12, 0.50)          # mask' = clip((m - lo) / (hi - lo))


def wordmark(L):
    """Kept for the luminance route (hollow letters) - use solid_wordmark()."""
    m = L > 100; ys, xs = np.nonzero(m[1350:])
    y0, y1, x0, x1 = ys.min() + 1350, ys.max() + 1351, xs.min(), xs.max() + 1
    m = L[y0:y1, x0:x1] / 255.0
    return np.clip((m - BOOST[0]) / (BOOST[1] - BOOST[0]), 0, 1)


def solid_wordmark(A, G=None, stroke=16, thresh=128, close=0):
    """Capcom's title texture is OUTLINE-ONLY: alpha holds the stroke and the ribbon,
    the letter interiors are transparent (the fill is drawn from another layer on PC).
    Rebuild a solid silhouette by geodesic reconstruction: seed = enclosed pixels
    within `stroke` px of the outside (i.e. just across the stroke), then grow the
    seed through the enclosed area. Letter interiors are reached; letter counters
    and the carved ribbon lettering are not (they sit behind a second stroke or
    deep inside the ribbon body) and stay open."""
    from PIL import ImageDraw, ImageFilter
    mb = A > 128; ys, xs = np.nonzero(mb[1350:])           # bbox from the solid stroke
    y0, y1, x0, x1 = ys.min() + 1350, ys.max() + 1351, xs.min(), xs.max() + 1
    cov = (A > thresh)[y0:y1, x0:x1]; h, w = cov.shape       # stroke incl. its soft edge
    if close:   # bridge hairline gaps in the stroke so interiors are enclosed
        cov = np.asarray(Image.fromarray((cov * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(close))) > 0
    pad = np.zeros((h + 2, w + 2), bool); pad[1:-1, 1:-1] = cov
    lab = Image.fromarray(np.where(pad, 255, 0).astype(np.uint8)).copy()   # .copy(): fromarray() can hand back a read-only buffer and floodfill then silently does nothing
    ImageDraw.floodfill(lab, (0, 0), 128)
    assert (np.asarray(lab) == 128).any(), 'flood fill did not run'
    arr = np.asarray(lab); outside = arr == 128; enclosed = arr == 0
    near = np.asarray(Image.fromarray((outside * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * stroke + 1))) > 0
    # the ribbon is a THICK body with its lettering carved out; those carved letters sit
    # close to the ribbon's edge at its flared ends and would be seeded like a letter
    # interior. Seed only across THIN strokes: open the coverage with a 12 px radius
    # to isolate thick bodies, and keep seeds well away from them.
    cov8 = Image.fromarray((pad * 255).astype(np.uint8))
    thick = np.asarray(cov8.filter(ImageFilter.MinFilter(25)).filter(ImageFilter.MaxFilter(25))) > 0
    excl = np.asarray(Image.fromarray((thick * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * stroke + 31))) > 0
    seed = enclosed & near & ~excl
    grown = seed.copy(); it = 0
    while True:
        d = grown.copy()
        d[1:, :] |= grown[:-1, :]; d[:-1, :] |= grown[1:, :]; d[:, 1:] |= grown[:, :-1]; d[:, :-1] |= grown[:, 1:]
        d &= enclosed; it += 1
        if (d == grown).all() or it > 2000: break
        grown = d
    solid = (pad | grown)[1:-1, 1:-1]
    if close:   # undo the closing on the outer edge: keep the true stroke + the fill
        solid = solid & ((A[y0:y1, x0:x1] > thresh) | grown[1:-1, 1:-1])
    return solid.astype(np.float32), it


def fit(mask, bw, bh):
    h, w = mask.shape; s = min(bw / w, bh / h); nw, nh = max(1, round(w * s)), max(1, round(h * s))
    return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)).astype(np.float32) / 255


def place(a, mask, bbox, colour, shadow=None, valign='centre'):
    x0, y0, x1, y1 = bbox; a[y0:y1, x0:x1] = 0
    m = fit(mask, x1 - x0, y1 - y0); h, w = m.shape
    ox = x0 + ((x1 - x0) - w) // 2; oy = y0 + (((y1 - y0) - h) // 2 if valign == 'centre' else 0)
    if shadow is not None:
        sx, sy, scol = shadow; sm = np.zeros_like(m); sm[sy:, sx:] = m[:h - sy, :w - sx]
        a[oy:oy + h, ox:ox + w, :3] = np.array(scol); a[oy:oy + h, ox:ox + w, 3] = sm * 255
    reg = a[oy:oy + h, ox:ox + w].astype(np.float32); col = np.broadcast_to(np.array(colour, np.float32), (h, w, 3))
    al = m[..., None]; a[oy:oy + h, ox:ox + w, :3] = np.clip(col * al + reg[..., :3] * (1 - al) + 0.5, 0, 255)
    a[oy:oy + h, ox:ox + w, 3] = np.clip(np.maximum(reg[..., 3], m * 255) + 0.5, 0, 255)
    return (ox, oy, w, h)


def arc_atlas(tex_bytes, mask, game):
    """title_jpn.arc member: black wordmark sprite (8,14,376,108), subtitle sprite rows
    124..152 (blanked - the ribbon carries it), cream wordmark sprite (8,338,376,438);
    TGAA2 also has separate '2' sprites at x388+ which Capcom's logo makes redundant."""
    rgb, al = tex_rgba8.decode_rgba8(tex_bytes); a = np.dstack([rgb, al]).astype(np.float32)
    place(a, mask, (8, 14, 376, 108), (0, 0, 0))
    a[124:152, 0:384] = 0
    place(a, mask, (8, 338, 376, 438), (228, 224, 200))
    if game == 'BB':
        a[176:336, 388:512] = 0; a[344:512, 384:512] = 0
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex_bytes, a8[..., :3], a8[..., 3]), a8


def loose_atlas(tex_bytes, mask):
    """TGAA2 loose title_jpn_01: dark composite (16,18,378,168) and cream composite
    (14,196,380,348); the ENG version stamp sprite at y181..195 is left alone."""
    rgb, al = tex_rgba8.decode_rgba8(tex_bytes); a = np.dstack([rgb, al]).astype(np.float32)
    place(a, mask, (16, 18, 378, 168), (20, 18, 16), shadow=(3, 3, (0, 0, 0)))
    place(a, mask, (14, 196, 380, 348), (228, 224, 200), shadow=(3, 3, (40, 36, 30)))
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex_bytes, a8[..., :3], a8[..., 3]), a8


# ---- full-colour route (user-supplied official logo PNG/WebP with alpha) -------------
def load_logo_rgba(path):
    im = Image.open(path).convert('RGBA'); a = np.asarray(im).astype(np.float32)
    ys, xs = np.nonzero(a[..., 3] > 8)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def place_rgba(a, logo, bbox, shadow=None):
    """Fit a full-colour RGBA logo into bbox (aspect kept, centred), over a cleared sprite."""
    x0, y0, x1, y1 = bbox; a[y0:y1, x0:x1] = 0
    h0, w0 = logo.shape[:2]; s = min((x1 - x0) / w0, (y1 - y0) / h0); nw, nh = max(1, round(w0 * s)), max(1, round(h0 * s))
    im = Image.fromarray(np.clip(logo, 0, 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS); L = np.asarray(im).astype(np.float32)
    ox = x0 + ((x1 - x0) - nw) // 2; oy = y0 + ((y1 - y0) - nh) // 2
    if shadow is not None:
        sx, sy, scol = shadow; sm = np.zeros((nh, nw), np.float32); sm[sy:, sx:] = L[:nh - sy, :nw - sx, 3]
        a[oy:oy + nh, ox:ox + nw, :3] = np.array(scol); a[oy:oy + nh, ox:ox + nw, 3] = sm
    reg = a[oy:oy + nh, ox:ox + nw]; al = (L[..., 3] / 255.0)[..., None]
    reg[..., :3] = np.clip(L[..., :3] * al + reg[..., :3] * (1 - al) + 0.5, 0, 255)
    reg[..., 3] = np.clip(np.maximum(reg[..., 3], L[..., 3]) + 0.5, 0, 255)
    return (ox, oy, nw, nh)


def arc_atlas_colour(tex_bytes, logo, game):
    rgb, al = tex_rgba8.decode_rgba8(tex_bytes); a = np.dstack([rgb, al]).astype(np.float32)
    place_rgba(a, logo, (8, 14, 376, 108))                        # colour sprite (was the black wordmark)
    a[124:152, 0:384] = 0                                          # subtitle sprite: ribbon carries it
    place(a, logo[..., 3] / 255.0, (8, 338, 376, 438), (228, 224, 200))   # cream silhouette sprite
    if game == 'BB':
        a[176:336, 388:512] = 0; a[344:512, 384:512] = 0
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex_bytes, a8[..., :3], a8[..., 3]), a8


def loose_atlas_colour(tex_bytes, logo):
    rgb, al = tex_rgba8.decode_rgba8(tex_bytes); a = np.dstack([rgb, al]).astype(np.float32)
    place_rgba(a, logo, (16, 18, 378, 168), shadow=(3, 3, (0, 0, 0)))
    place(a, logo[..., 3] / 255.0, (14, 196, 380, 348), (228, 224, 200), shadow=(3, 3, (40, 36, 30)))
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex_bytes, a8[..., :3], a8[..., 3]), a8


# ---- aligned pair: the game draws the cream sprite BEHIND the colour sprite as its
# outline, so both must be the same scale at the same offset; cream = alpha dilated.
def _fit_rgba(logo, bw, bh):
    h0, w0 = logo.shape[:2]; s = min(bw / w0, bh / h0); nw, nh = max(1, round(w0 * s)), max(1, round(h0 * s))
    return np.asarray(Image.fromarray(np.clip(logo, 0, 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)).astype(np.float32)


def _blend(a, ox, oy, rgb, alpha):
    h, w = alpha.shape; reg = a[oy:oy + h, ox:ox + w]; al = (alpha / 255.0)[..., None]
    reg[..., :3] = np.clip(rgb * al + reg[..., :3] * (1 - al) + 0.5, 0, 255)
    reg[..., 3] = np.clip(np.maximum(reg[..., 3], alpha) + 0.5, 0, 255)


def _dilate(m, r):
    out = m.copy()
    for k in range(1, r + 1):
        out[:, k:] = np.maximum(out[:, k:], m[:, :-k]); out[:, :-k] = np.maximum(out[:, :-k], m[:, k:])
    m2 = out.copy()
    for k in range(1, r + 1):
        out[k:, :] = np.maximum(out[k:, :], m2[:-k, :]); out[:-k, :] = np.maximum(out[:-k, :], m2[k:, :])
    return out


def aligned_pair(a, logo, colour_bbox, cream_origin, cream_colour=(228, 224, 200), dilate=4, shadow=None):
    from PIL import ImageFilter
    x0, y0, x1, y1 = colour_bbox; L = _fit_rgba(logo, x1 - x0 - 2 * dilate, y1 - y0 - 2 * dilate); nh, nw = L.shape[:2]
    ox = x0 + ((x1 - x0) - nw) // 2; oy = y0 + ((y1 - y0) - nh) // 2
    a[y0:y1, x0:x1] = 0
    if shadow is not None:
        sx, sy, scol = shadow; sm = np.zeros((nh, nw), np.float32); sm[sy:, sx:] = L[:nh - sy, :nw - sx, 3]
        a[oy:oy + nh, ox:ox + nw, :3] = np.array(scol); a[oy:oy + nh, ox:ox + nw, 3] = sm
    _blend(a, ox, oy, L[..., :3], L[..., 3])
    cx, cy = cream_origin[0] + (ox - x0), cream_origin[1] + (oy - y0)
    pad = np.zeros((nh + 2 * dilate, nw + 2 * dilate), np.float32); pad[dilate:dilate + nh, dilate:dilate + nw] = L[..., 3]
    dil = _dilate(pad, dilate)   # numpy, separable: PIL's MaxFilter garbled this image (row smear) - measured 2026-09-01
    a[cream_origin[1]:cream_origin[1] + (y1 - y0), cream_origin[0]:cream_origin[0] + (x1 - x0)] = 0
    _blend(a, cx - dilate, cy - dilate, np.broadcast_to(np.array(cream_colour, np.float32), dil.shape + (3,)), dil)
    return (ox, oy, nw, nh)


def arc_atlas_aligned(tex_bytes, logo, game):
    rgb, al = tex_rgba8.decode_rgba8(tex_bytes); a = np.dstack([rgb, al]).astype(np.float32)
    aligned_pair(a, logo, (8, 14, 376, 108), (8, 342), dilate=1)   # cream sprite origin = colour origin + 328 rows (measured from the fan atlas: 17..103 vs 342..434 with ~3 px dilation; 324 drew it 4 px high in-game)   # the official logo has its own cream outline; a 3 px halo read as a slab in-game
    a[124:152, 0:384] = 0
    if game == 'BB':
        a[176:336, 388:512] = 0; a[344:512, 384:512] = 0
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex_bytes, a8[..., :3], a8[..., 3]), a8


def loose_atlas_aligned(tex_bytes, logo):
    rgb, al = tex_rgba8.decode_rgba8(tex_bytes); a = np.dstack([rgb, al]).astype(np.float32)
    aligned_pair(a, logo, (16, 18, 378, 168), (15, 198), dilate=1)   # x tuned in-game by the user: 16 was right, 14 was left, 15 is it   # +180 rows (fan: 19..168 vs 196..347, 3 px dilation)
    a8 = a.astype(np.uint8)
    return tex_rgba8.encode_rgba8(tex_bytes, a8[..., :3], a8[..., 3]), a8

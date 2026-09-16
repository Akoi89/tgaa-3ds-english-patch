# -*- coding: utf-8 -*-
"""LaMa (big-lama TorchScript, <MODELS_ROOT>/big-lama.pt, 205,803,670 B, sha256 7ba7aa7ac37a4d41...)
inpainting for the see-through Picture Book pages. Downloaded 2026-09-15 with the user's OK from the
simple-lama-inpainting v0.1.0 release; called directly with torch (the pip wrapper pins old Pillow/NumPy).

inpaint(rgb, mask, box, scale): crop the box plus CONTEXT px of surroundings, optionally upscale, pad to a
multiple of 8, run the model on CPU, scale back, and paste ONLY the masked pixels into a copy of rgb.
"""
import os
import sys

import cv2
import numpy as np
import torch

MODELS_ROOT = os.environ.get('MODELS_ROOT') or sys.exit('set MODELS_ROOT to the models folder')
MODEL = os.path.join(MODELS_ROOT, 'big-lama.pt')
CONTEXT = 48
_model = None


def model():
    global _model
    if _model is None:
        _model = torch.jit.load(MODEL, map_location='cpu')
        _model.eval()
    return _model


def inpaint(rgb, mask, box, scale=2, clip=None):
    """rgb uint8 HxWx3, mask uint8/bool HxW (1 = fill), box (x0,y0,x1,y1) region of interest.
    clip (x0,y0,x1,y1): the model only sees pixels inside it (a see-through panel: art outside the panel is
    full strength and would be copied into the lighter panel)."""
    H, W = mask.shape
    x0, y0, x1, y1 = box
    cx0, cy0 = max(0, x0 - CONTEXT), max(0, y0 - CONTEXT)
    cx1, cy1 = min(W, x1 + CONTEXT), min(H, y1 + CONTEXT)
    if clip is not None:
        cx0, cy0, cx1, cy1 = max(cx0, clip[0]), max(cy0, clip[1]), min(cx1, clip[2]), min(cy1, clip[3])
    crop = rgb[cy0:cy1, cx0:cx1]
    m = (mask[cy0:cy1, cx0:cx1] > 0).astype(np.uint8)
    h, w = m.shape
    if scale != 1:
        crop_s = cv2.resize(crop, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
        m_s = cv2.resize(m, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)
    else:
        crop_s, m_s = crop, m
    hs, ws = m_s.shape
    ph, pw = (-hs) % 8, (-ws) % 8
    img = np.pad(crop_s, ((0, ph), (0, pw), (0, 0)), mode='reflect')
    mm = np.pad(m_s, ((0, ph), (0, pw)), mode='constant')
    t_img = torch.from_numpy(img).permute(2, 0, 1)[None].float() / 255.0
    t_m = torch.from_numpy(mm)[None, None].float()
    with torch.inference_mode():
        out = model()(t_img, t_m)
    res = (out[0].permute(1, 2, 0).numpy() * 255.0).clip(0, 255).astype(np.uint8)[:hs, :ws]
    if scale != 1:
        res = cv2.resize(res, (w, h), interpolation=cv2.INTER_AREA)
    outimg = rgb.copy()
    sel = m.astype(bool)
    outimg[cy0:cy1, cx0:cx1][sel] = res[sel]
    return outimg

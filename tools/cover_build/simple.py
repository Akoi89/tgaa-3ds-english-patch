# -*- coding: utf-8 -*-
"""Simple covers: the official PC banners, untouched, plus English text.

Rules (user's): ignore the old 3DS layout entirely, do not alter the
base images, just add clean legible English text. So each 1024x512
banner is used as-is -- its own official title included -- with the
content list added in a matching style, then downscaled to the 3DS
texture size with its transparency preserved.

One exception, flagged to the user: Episode 0's banner carries
Japanese text and a '_ENG' placeholder where the others carry an
English title, so that line is erased and replaced.
"""
import sys, os
sys.path.insert(0, 'lib')
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from covers import COVERS

F = 'C:/Windows/Fonts/Candarab.ttf'
CREAM = (246, 238, 222)
INK = (38, 30, 24)
LABEL = {'art': 'Picture Book', 'music': 'Music', 'audio': 'Audio',
         'movie': 'Movie', 'cont': ''}
SS = 2                                   # draw at 2048x1024, shrink twice


def styled(draw, xy, text, font, shadow_layer):
    """Cream glyphs, thin dark outline, soft drop shadow (PC title look)."""
    x, y = xy
    sd = ImageDraw.Draw(shadow_layer)
    sd.text((x + 3 * SS, y + 3 * SS), text, font=font, fill=(0, 0, 0, 170))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                draw.text((x + dx * SS, y + dy * SS), text, font=font, fill=INK + (255,))
    draw.text((x, y), text, font=font, fill=CREAM + (255,))


def erase_ep0_text(pc):
    """Erase the Japanese strapline, title and '_ENG' placeholder from the
    Episode 0 banner -- the only cover Capcom never made in English.

    The first version keyed on brightness inside two large boxes, which
    also swallowed the pale hilt of Kazuma's sword and his scabbard and
    inpainted them into blur. Two changes fix that. The bands are tight
    to the measured text rows (rose 364..380, white title 401..433, plus
    room for outlines) rather than reaching up into the artwork, and the
    white test is strict enough that only glyph cores pass: inside the
    tight band every connected component is glyph-sized (<=31x32 px, 28
    of them), with no sword component at all.
    """
    rgb = pc[:, :, :3].copy()
    a = rgb.astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    lum = a @ np.array([0.299, 0.587, 0.114])
    sat = a.max(2) - a.min(2)

    rose = (r - g > 35) & (r - b > 35) & (np.abs(g - b) <= 16) & (r > 150)
    white = (lum > 195) & (sat < 38)

    m = np.zeros(rgb.shape[:2], bool)
    band = np.zeros_like(m); band[356:391, 120:660] = True
    m |= rose & band
    band = np.zeros_like(m); band[393:442, 240:815] = True
    m |= white & band

    # take the glyphs' dark outline and soft shadow with them
    m = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8))
    rgb = cv2.inpaint(rgb, m, 6, cv2.INPAINT_TELEA)
    out = pc.copy(); out[:, :, :3] = rgb
    return out


CARD = (95, 47, 930, 465)          # the banner card's opaque bounds (835x418, 2:1)

# Screen geometry, SOLVED by template-matching a render against an
# in-game screenshot over every candidate window (the fit is
# unambiguous -- the visible width comes out at exactly 400 texture px):
#     visible area = texture x 24..424, y 14..254
#     "Previous/Next Issue" bar covers from y = 230
# So the card fills the visible width and sits flush on the bar.
CARD_W, CARD_H = 400, 200
BAR_Y = 230
CARD_X = 24
CARD_Y = BAR_Y - CARD_H


def full_bleed(pc):
    """Crop to the card and make it fully opaque, filling only the four
    rounded-corner gaps -- so the texture bleeds to every edge and the
    game's own background (a different argyle scale and tone) never
    shows around it as an inset frame.

    The bottom flourish is deliberately NOT erased. An earlier version
    did, to keep it from colliding with the L/R bar, using a
    brighter-than-average test across a band near the bottom -- which
    also caught Kazuma's sword scabbard on Ep 0 and inpainted it into a
    smudge (user spotted it). Now that the card sits flush on the bar
    the flourish simply reads as the card's own bottom trim, so there
    is nothing to erase and nothing to damage.
    """
    x0, y0, x1, y1 = CARD
    c = pc[y0:y1, x0:x1].copy()
    rgb = c[:, :, :3].copy()
    m = (c[:, :, 3] < 250).astype(np.uint8)
    rgb = cv2.inpaint(rgb, m, 6, cv2.INPAINT_TELEA)
    return np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])


def build(n):
    pc = np.array(Image.open('pc_banners/pc%02d.png' % n).convert('RGBA'))
    if n == 0:
        pc = erase_ep0_text(pc)
    pc = full_bleed(pc)
    base = Image.fromarray(pc, 'RGBA')
    big = base.resize((base.width * SS, base.height * SS), Image.LANCZOS)
    text = Image.new('RGBA', big.size, (0, 0, 0, 0))
    shadow = Image.new('RGBA', big.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(text)
    OX, OY = CARD[0], CARD[1]
    S = lambda v: int(v * SS)
    SX = lambda v: int((v - OX) * SS)
    SY = lambda v: int((v - OY) * SS)

    if n == 0:
        # match the other banners' title: same baseline, size and colour
        f = ImageFont.truetype(F, S(40))
        styled(d, (SX(135), SY(388)), 'Episode 0 : At the Supreme Court', f, shadow)

    f_lab = ImageFont.truetype(F, S(26))
    f_txt = ImageFont.truetype(F, S(26))
    y = SY(268)
    for row in COVERS[n]['rows']:
        slot, kind, items, more = row
        line = '   '.join('\u201c%s\u201d' % it for it in items) + ('  + more' if more else '')
        x = SX(150)
        if kind != 'cont':
            lab = LABEL[kind] + ':  '
            styled(d, (x, y), lab, f_lab, shadow)
            x += d.textlength(lab, font=f_lab)
        else:
            x += S(24)
        styled(d, (x, y), line, f_txt, shadow)
        y += S(29)

    shadow = shadow.filter(ImageFilter.GaussianBlur(2.5 * SS))
    big.alpha_composite(shadow)
    big.alpha_composite(text)
    card = np.array(big.resize((CARD_W, CARD_H), Image.LANCZOS).convert('RGB'))

    # Canvas colour is sampled straight off the card's own edge rows --
    # the median of the top row for everything above it, the bottom row
    # for everything below. A flat field cannot disagree with the card's
    # tone the way a tiled pattern did, and the last few rows before the
    # join fade into the card's actual edge pixels, so the seam is exact.
    top_rgb = np.median(card[0], 0)
    bot_rgb = np.median(card[-1], 0)
    full = np.zeros((256, 512, 3), float)
    full[:CARD_Y + CARD_H // 2] = top_rgb
    full[CARD_Y + CARD_H // 2:] = bot_rgb

    FADE = 8
    for k in range(1, FADE + 1):
        t = k / (FADE + 1.0)
        y = CARD_Y - k
        if y >= 0:
            full[y, CARD_X:CARD_X + CARD_W] = card[0] * (1 - t) + top_rgb * t
        y = CARD_Y + CARD_H - 1 + k
        if y < 256:
            full[y, CARD_X:CARD_X + CARD_W] = card[-1] * (1 - t) + bot_rgb * t

    full[CARD_Y:CARD_Y + CARD_H, CARD_X:CARD_X + CARD_W] = card
    out = np.clip(full, 0, 255).astype(np.uint8)
    print('    ep canvas: top #%02x%02x%02x  bottom #%02x%02x%02x'
          % (*top_rgb.astype(int), *bot_rgb.astype(int)))
    return Image.fromarray(np.dstack([out, np.full(out.shape[:2], 255, np.uint8)]), 'RGBA')


if __name__ == '__main__':
    os.makedirs('simple_out', exist_ok=True)
    for n in range(9):
        build(n).save('simple_out/aoc%02d.png' % n)
    print('9 simple covers')

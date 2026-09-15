# -*- coding: utf-8 -*-
"""Export the TGAA1 DLC Picture Book, Editor's Notes, theme and event pages from the SHIPPED DLC 1.0.10.

    python export_pages.py

Source: dlc_ai_voice/_shipped/TGAA1-DLC-1.0.10 (extracted from Final/_CURRENT/TGAA1-DLC-1.0.10.cia).
Writes, next to this script:
  orig/<name>.png         the whole 512x256 texture, lossless (edit THIS canvas; it is what gets re-imported)
  screen/<name>.png       the part the 3DS top screen shows (x 24..424, y 8..248, 400x240), for reading
  guide/<name>.png        the full canvas with the visible rectangle outlined in red
  sheets/<kind>_<n>.png   contact sheets
  manifest.tsv            name, content, sha256 of the .tex, size, format bytes
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
sys.path.insert(0, os.path.join(ROOT, 'jpvoice'))
import tex_view   # noqa: E402

SRC = os.path.join(ROOT, 'dlc_ai_voice', '_shipped', 'TGAA1-DLC-1.0.10')
KINDS = ('design', 'editor', 'theme', 'event')
VIS = (24, 8, 424, 248)


def main():
    for sub in ('orig', 'screen', 'guide', 'sheets'):
        os.makedirs(os.path.join(HERE, sub), exist_ok=True)
    rows, by_kind = [], {}
    for c in sorted(os.listdir(SRC), key=lambda x: int(x[7:])):
        tdir = os.path.join(SRC, c, 'tex')
        if not os.path.isdir(tdir):
            continue
        for fn in sorted(os.listdir(tdir)):
            kind = next((k for k in KINDS if '_%s' % k in fn), None)
            if not kind:
                continue
            b = open(os.path.join(tdir, fn), 'rb').read()
            name = fn.replace('_BM_NOMIP_HQ.tex', '')
            im = tex_view.preview(b)
            im = (im[0] if isinstance(im, tuple) else im).convert('RGBA')
            assert im.size == (512, 256), (fn, im.size)
            im.save(os.path.join(HERE, 'orig', name + '.png'))
            im.crop(VIS).save(os.path.join(HERE, 'screen', name + '.png'))
            g = im.convert('RGB').copy()
            ImageDraw.Draw(g).rectangle((VIS[0] - 1, VIS[1] - 1, VIS[2], VIS[3]), outline=(255, 0, 0))
            g.save(os.path.join(HERE, 'guide', name + '.png'))
            rows.append('\t'.join((name, c, hashlib.sha256(b).hexdigest(), str(len(b)), b[:20].hex())))
            by_kind.setdefault(kind, []).append((name, im.crop(VIS)))
    open(os.path.join(HERE, 'manifest.tsv'), 'w').write('name\tcontent\ttex_sha256\tbytes\theader\n' + '\n'.join(rows) + '\n')
    for kind, items in by_kind.items():
        per = 16
        for s in range(0, len(items), per):
            chunk = items[s:s + per]
            cols = 4
            W, H = 400, 240 + 16
            sheet = Image.new('RGB', (cols * W, ((len(chunk) + cols - 1) // cols) * H), (0, 0, 0))
            d = ImageDraw.Draw(sheet)
            for i, (name, im) in enumerate(chunk):
                x, y = (i % cols) * W, (i // cols) * H
                sheet.paste(im.convert('RGB'), (x, y + 16))
                d.text((x + 3, y + 2), name, fill=(255, 255, 0))
            sheet.save(os.path.join(HERE, 'sheets', '%s_%d.png' % (kind, s // per + 1)))
    print('%d pages exported: %s' % (len(rows), ', '.join('%s %d' % (k, len(v)) for k, v in by_kind.items())))


if __name__ == '__main__':
    main()

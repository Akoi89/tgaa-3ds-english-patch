# -*- coding: utf-8 -*-
"""review/picturebook_comparison.html: every translated page, original beside final/, with the Japanese and
English text. Single file, images as JPEG data URIs."""
import base64
import html
import io
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
tr = {json.loads(l)['page']: json.loads(l) for l in io.open(os.path.join(HERE, 'translations.jsonl'), encoding='utf-8') if l.strip()}
pages = sorted(f[:-4] for f in os.listdir(os.path.join(HERE, 'final')) if f.endswith('.png'))


def b64(path):
    im = Image.open(path).convert('RGB').crop(VIS).resize((600, 360), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=88)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


esc = lambda s: html.escape(s or '').replace('\n', '<br>')
CSS = ('body{background:#1b1b1b;color:#e8e8e8;font:14px system-ui,sans-serif;margin:0;padding:12px 16px}h1{font-size:18px}'
       '.p{margin:16px 0 30px;border-top:1px solid #333;padding-top:10px}.n{color:#fc6;font-weight:600;margin-bottom:6px}'
       '.im{display:flex;flex-wrap:wrap;gap:8px}.im figure{margin:0;flex:1 1 300px;max-width:600px}.im img{width:100%;display:block;border:1px solid #333}'
       'figcaption{font-size:12px;color:#aaa}.t{display:flex;flex-wrap:wrap;gap:10px;margin-top:8px}'
       '.t div{flex:1 1 300px;background:#242424;border:1px solid #333;padding:8px 10px;line-height:1.5}.t h3{margin:0 0 4px;font-size:12px;color:#9cf}'
       '.jp{font-family:"Yu Gothic","Meiryo",sans-serif}')
parts = ['<meta charset="utf-8"><title>Picture Book Comparison</title><style>%s</style>' % CSS,
         '<h1>TGAA1 DLC Picture Book: original and English (%d pages, final set)</h1>' % len(pages)]
for i, p in enumerate(pages):
    t = tr.get(p, {})
    parts.append('<div class="p"><div class="n">%d. %s</div><div class="im"><figure><img src="%s"><figcaption>original</figcaption></figure>'
                 '<figure><img src="%s"><figcaption>English</figcaption></figure></div>'
                 '<div class="t"><div class="jp"><h3>Japanese text</h3>%s</div><div><h3>English text</h3>%s</div></div></div>'
                 % (i + 1, p, b64(os.path.join(HERE, 'orig', p + '.png')), b64(os.path.join(HERE, 'final', p + '.png')), esc(t.get('jp')), esc(t.get('en'))))
out = '\n'.join(parts)
assert not any(c in out for c in '—–')
io.open(os.path.join(HERE, 'review', 'picturebook_comparison.html'), 'w', encoding='utf-8').write(out)
print('%d pages, %.1f MB' % (len(pages), len(out) / 1e6))

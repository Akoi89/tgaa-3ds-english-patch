# -*- coding: utf-8 -*-
"""review/erase_slider.html: single-file slider comparison for the see-through pages, with the LaMa version.

Each image is stored once (JPEG, base64) in a script table; every page has a drag/range slider and a
choice of pair: with wash vs without, original vs with wash, original vs without.
"""
import base64
import html
import io
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = (24, 8, 424, 248)
tr = {json.loads(l)['page']: json.loads(l) for l in io.open(os.path.join(HERE, 'translations.jsonl'), encoding='utf-8')}
pages = open(os.path.join(HERE, '_overlay_pages.txt')).read().split(',')


def b64(path):
    im = Image.open(path).convert('RGB').crop(VIS).resize((800, 480), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=88)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


esc = lambda s: html.escape(s).replace('\n', '<br>')
imgs = {p: [b64(os.path.join(HERE, d, p + '.png')) for d in ('orig', 'final', 'final_nowash', 'final_lama2')] for p in pages}
CSS = ('body{background:#1b1b1b;color:#e8e8e8;font:14px system-ui,sans-serif;margin:0;padding:12px 16px}h1{font-size:18px}'
       '.p{margin:18px 0 36px;border-top:1px solid #333;padding-top:12px;max-width:820px}.n{color:#fc6;font-weight:600;margin-bottom:8px}'
       '.cmp{position:relative;width:100%;max-width:800px;aspect-ratio:5/3;overflow:hidden;border:1px solid #333;cursor:ew-resize;touch-action:pan-y}'
       '.cmp img{position:absolute;inset:0;width:100%;height:100%;display:block;user-select:none;-webkit-user-drag:none;pointer-events:none}'
       '.bar{position:absolute;top:0;bottom:0;left:50%;width:2px;background:#fc6;pointer-events:none}'
       '.tags{display:flex;justify-content:space-between;color:#ccc;font-size:12px;max-width:800px;margin:4px 0}'
       'input[type=range]{width:100%;max-width:800px}.sel{margin:6px 0;font-size:13px}.sel label{margin-right:14px;white-space:nowrap}'
       '.t{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}.t div{flex:1 1 300px;background:#242424;border:1px solid #333;padding:8px 10px;line-height:1.5}'
       '.t h3{margin:0 0 4px;font-size:12px;color:#9cf}.jp{font-family:"Yu Gothic","Meiryo",sans-serif}')
PAIRS = [('current (wash)', 'LaMa', 1, 3), ('original', 'LaMa', 0, 3), ('no wash (Telea)', 'LaMa', 2, 3), ('original', 'current (wash)', 0, 1)]
parts = ['<meta charset="utf-8"><title>Erase Slider</title><style>%s</style>' % CSS,
         '<h1>See-through pages: drag across each picture to compare (%d pages)</h1>' % len(pages) + '<p>LaMa = the AI fill on the thin two-pass mask, no wash. Current = what is in final/ now.</p>',
         '<p>Left of the handle is the first version named under the picture, right of it the second. '
         'Choose the pair under each picture. Twice the 3DS screen size.</p>']
for i, p in enumerate(pages):
    radios = ''.join('<label><input type="radio" name="m%d" value="%d"%s> %s vs %s</label>' % (i, j, ' checked' if j == 0 else '', a, b)
                     for j, (a, b, _, _) in enumerate(PAIRS))
    parts.append('<div class="p"><div class="n">%d. %s</div>'
                 '<div class="cmp" id="c%d"><img class="bot"><img class="top"><div class="bar"></div></div>'
                 '<div class="tags"><span class="lt"></span><span class="rt"></span></div>'
                 '<input type="range" min="0" max="100" value="50" id="r%d"><div class="sel">%s</div>'
                 '<div class="t"><div class="jp"><h3>Japanese text</h3>%s</div><div><h3>English text</h3>%s</div></div></div>'
                 % (i + 1, p, i, i, radios, esc(tr[p]['jp']), esc(tr[p]['en'])))
js = ('<script>var IM=%s;var PAIRS=%s;'
      'IM.forEach(function(set,i){var c=document.getElementById("c"+i),r=document.getElementById("r"+i),'
      'top=c.querySelector(".top"),bot=c.querySelector(".bot"),bar=c.querySelector(".bar"),box=c.parentNode;'
      'function pos(v){top.style.clipPath="inset(0 "+(100-v)+"%% 0 0)";bar.style.left=v+"%%";}'
      'function pair(k){var q=PAIRS[k];top.src=set[q[2]];bot.src=set[q[3]];box.querySelector(".lt").textContent=q[0];box.querySelector(".rt").textContent=q[1];}'
      'r.addEventListener("input",function(){pos(r.value)});'
      'function at(x){var b=c.getBoundingClientRect();var v=Math.max(0,Math.min(100,(x-b.left)/b.width*100));r.value=v;pos(v);}'
      'c.addEventListener("pointerdown",function(e){at(e.clientX);c.setPointerCapture(e.pointerId);});'
      'c.addEventListener("pointermove",function(e){if(e.buttons)at(e.clientX);});'
      'box.querySelectorAll("input[type=radio]").forEach(function(el){el.addEventListener("change",function(){pair(+el.value)})});'
      'pair(0);pos(50);});</script>') % (json.dumps([imgs[p] for p in pages]), json.dumps(PAIRS))
out = '\n'.join(parts) + js
assert not any(c in out for c in '—–')
io.open(os.path.join(HERE, 'review', 'erase_slider.html'), 'w', encoding='utf-8').write(out)
print('%d pages, %.1f MB' % (len(pages), len(out) / 1e6))

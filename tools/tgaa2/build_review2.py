# -*- coding: utf-8 -*-
"""Build the TGAA2 condensed-captions review page (post-playthrough veto tool).

Mirrors TGAA1's court_record_captions.html workflow: every card shows the
official Chronicles text against the shipped condensed text with its 4-line
wrap preview; a 'Revert to official' checkbox per card persists in the
browser; 'Copy veto list' emits the labels to paste back. All 96 are already
applied in TGAA2 v15, so the page exists for vetoes, not approval.

    python build_review2.py <out.html>
"""
import json, os, re, struct, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
sys.path.insert(0, os.path.join(HERE, '..', 'audio_tools'))

from condensed2 import CONDENSED, ACCEPTED_LOSSES
from caption_fit import wrap
from dgs2tool.arc import parse_arc


def advances():
    b = {e.name: e.data for e in parse_arc(
        open(os.path.join(HERE, 'v14_dir', 'archive', 'UI_cmn_jpn.arc'), 'rb').read())['entries']}[
        'UI/0_system/00_font/font03_jpn.gfd']
    h = struct.unpack_from('<4sI8i4f', b, 0)
    off = 56 + h[9] * 4
    off += 4 + struct.unpack_from('<i', b, off)[0] + 1
    d = {}
    for i in range(h[7]):
        e = off + i * 20
        d[struct.unpack_from('<I', b, e)[0]] = struct.unpack_from('<I', b, e + 12)[0] & 0xFFF
    return d


ADV = advances()
W = lambda s: sum(ADV.get(ord(c), 7) for c in s)

rows = {r['label']: r for r in json.load(open(os.path.join(HERE, 'heavy96.json'), encoding='utf-8'))}

cards = []
for lab in sorted(CONDENSED, key=lambda l: (l.startswith('item'), l)):
    r = rows[lab]
    c = CONDENSED[lab]
    lines = wrap(c, W, 199)
    cards.append(dict(label=lab, official=r['official'], scale=r['scale'],
                      condensed=c, lines=lines, loss=ACCEPTED_LOSSES.get(lab)))

def esc(t):
    return html.escape(t, quote=False)

items = []
for c in cards:
    loss = ('<div class="loss">accepted loss: %s</div>' % esc(c['loss'])) if c['loss'] else ''
    prev = '<br>'.join(esc(l) for l in c['lines'])
    items.append('''
<article class="card" data-label="%(label)s">
  <header>
    <span class="lab">%(label)s</span>
    <span class="badge">was shrunk to %(scale).2f</span>
    <label class="veto"><input type="checkbox" data-veto="%(label)s"> Revert to official</label>
  </header>
  <div class="cols">
    <div><h3>Official (Chronicles)</h3><p>%(off)s</p></div>
    <div><h3>Shipped in v15</h3><p>%(con)s</p>
      <div class="preview"><h4>Court Record, 4 lines, full size</h4><p class="mono">%(prev)s</p></div>
    </div>
  </div>
  %(loss)s
</article>''' % dict(label=c['label'], scale=c['scale'], off=esc(c['official']),
                     con=esc(c['condensed']), prev=prev, loss=loss))

page = '''<title>Resolve Caption Vetoes</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@400;600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{--bg:#e9edf1;--surface:#fff;--surface2:#f3f6f8;--line:#cdd6de;--ink:#16202b;--muted:#5a6b7a;
--accent:#8a5f0f;--good:#2c6a4d;--warn:#95651a;--warn-bg:#f4e7cd;--crit:#9d2f2c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#101720;--surface:#18212b;--surface2:#1e2934;
--line:#2d3a47;--ink:#dee6ed;--muted:#8fa0b0;--accent:#d4a851;--good:#6fc39a;--warn:#dcaa55;--warn-bg:#2e2416;--crit:#e0817d}}
:root[data-theme="dark"]{--bg:#101720;--surface:#18212b;--surface2:#1e2934;--line:#2d3a47;--ink:#dee6ed;
--muted:#8fa0b0;--accent:#d4a851;--good:#6fc39a;--warn:#dcaa55;--warn-bg:#2e2416;--crit:#e0817d}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;
margin:0;padding:clamp(18px,3vw,44px);line-height:1.5}
.wrap{max-width:980px;margin:0 auto}
h1{font-family:"Zilla Slab",Georgia,serif;font-size:clamp(26px,4.5vw,40px);margin:0 0 6px;letter-spacing:-.01em}
.sub{color:var(--muted);max-width:66ch;margin:0 0 18px}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:18px 0 26px}
button{font:600 14px "Source Sans 3",sans-serif;padding:9px 16px;border-radius:3px;border:1px solid var(--line);
background:var(--surface);color:var(--ink);cursor:pointer}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff}
#count{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--muted)}
.gate{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--crit);
border-radius:3px;padding:22px;margin:10px 0 0}
.gate h2{font-family:"Zilla Slab",Georgia,serif;margin:0 0 6px}
.gate p{color:var(--muted);margin:0 0 14px;max-width:60ch}
#cards{display:none;flex-direction:column;gap:16px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:3px;padding:16px 18px}
.card header{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
.lab{font-family:"JetBrains Mono",monospace;font-size:12px;font-weight:600;color:var(--accent)}
.badge{font-family:"JetBrains Mono",monospace;font-size:10.5px;background:var(--warn-bg);color:var(--warn);
padding:3px 8px;border-radius:2px;text-transform:uppercase;letter-spacing:.06em}
.veto{margin-left:auto;font-size:13.5px;color:var(--muted);display:flex;gap:6px;align-items:center;cursor:pointer}
.card.vetoed{outline:2px solid var(--crit);outline-offset:-1px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:700px){.cols{grid-template-columns:1fr}}
.cols h3{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:0 0 4px;
font-family:"JetBrains Mono",monospace;font-weight:600}
.cols p{margin:0;font-size:14.5px}
.preview{margin-top:10px;background:var(--surface2);border:1px solid var(--line);border-radius:3px;padding:8px 12px}
.preview h4{font-size:10px;margin:0 0 4px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;
font-family:"JetBrains Mono",monospace;font-weight:600}
.mono{font-family:"JetBrains Mono",monospace;font-size:12.5px;line-height:1.45}
.loss{margin-top:10px;font-size:12.5px;color:var(--warn);font-family:"JetBrains Mono",monospace}
footer{color:var(--muted);font-size:13px;margin-top:28px;border-top:1px solid var(--line);padding-top:14px}
</style>
<div class="wrap">
<h1>Resolve Caption Vetoes</h1>
<p class="sub">All 96 condensed Court Record captions shipped in TGAA2 v15, shown against Capcom&#8217;s official
Chronicles text. Tick <b>Revert to official</b> on any you dislike, then <b>Copy veto list</b> and paste it back
to Claude &#8212; each veto restores the official wording (it will render shrunk again, as upstream ships it).</p>
<div class="gate" id="gate">
  <h2>Spoiler warning</h2>
  <p>These captions describe evidence and people from all five episodes of a game you haven&#8217;t played.
  Open this page after (or during) your playthrough.</p>
  <button class="primary" id="reveal">Show the captions</button>
</div>
<div class="toolbar" id="bar" style="display:none">
  <button class="primary" id="copy">Copy veto list</button>
  <button id="clear">Clear all vetoes</button>
  <span id="count"></span>
</div>
<div id="cards">%(items)s</div>
<footer>Generated from <span class="mono">condensed2.py</span> by <span class="mono">build_review2.py</span> &#8212;
widths measured with font03&#8217;s own advances; every entry verified &#8804;4 lines at 199&#8202;px full size.</footer>
</div>
<script>
(function(){
var KEY='tgaa2-caption-vetoes';
function load(){try{return JSON.parse(localStorage.getItem(KEY))||{}}catch(e){return{}}}
function save(v){try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}}
var vetoes=load();
var boxes=document.querySelectorAll('[data-veto]');
function sync(){
  var n=0;
  boxes.forEach(function(b){
    var on=!!vetoes[b.dataset.veto]; b.checked=on;
    b.closest('.card').classList.toggle('vetoed',on);
    if(on)n++;
  });
  document.getElementById('count').textContent=n+' vetoed of '+boxes.length;
}
boxes.forEach(function(b){b.addEventListener('change',function(){
  if(b.checked)vetoes[b.dataset.veto]=1; else delete vetoes[b.dataset.veto];
  save(vetoes); sync();
})});
document.getElementById('copy').addEventListener('click',function(){
  var list=Object.keys(vetoes).sort().join('\\n')||'(no vetoes)';
  (navigator.clipboard&&navigator.clipboard.writeText(list))||window.prompt('Veto list:',list);
});
document.getElementById('clear').addEventListener('click',function(){vetoes={};save(vetoes);sync();});
document.getElementById('reveal').addEventListener('click',function(){
  document.getElementById('gate').style.display='none';
  document.getElementById('bar').style.display='flex';
  document.getElementById('cards').style.display='flex';
});
sync();
})();
</script>
''' % dict(items=''.join(items))

out = sys.argv[1] if len(sys.argv) > 1 else 'tgaa2_captions_review.html'
open(out, 'w', encoding='utf-8').write(page)
print('wrote %s  (%d cards)' % (out, len(cards)))

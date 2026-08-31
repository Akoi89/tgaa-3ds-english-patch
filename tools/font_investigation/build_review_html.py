# -*- coding: utf-8 -*-
"""Build the cloud review page for the condensed captions."""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'audio_tools'))

from caption_width import arc, advances
from caption_fit import wrap
from condensed import CONDENSED

K = 'UI/0_system/00_font/font03_jpn.gfd'
adv, _ = advances(arc(os.path.join(HERE, '..', 'base_v12', 'romfs_dir',
                                   'archive', 'UI_cmn_jpn.arc'))[K])
W = lambda s: sum(adv.get(ord(c), 7) for c in s)
B, LINE = 796, 199

rows = json.load(open(os.path.join(HERE, 'over_budget.json'), encoding='utf-8'))
groups = {}
for r in rows:
    groups.setdefault(r['text'], []).append(r['label'])

def game_scale(text):
    """The scale the Court Record actually picks: the largest s (in 0.01 steps)
    at which the greedy wrap fits 4 lines of 199 px."""
    s = 1.0
    while s > 0.5 and len(wrap(text, W, LINE / s)) > 4:
        s -= 0.01
    # 0.01 steps accumulate float drift (0.8999...); round so the displayed
    # value and the recommendation threshold always agree
    return round(s, 2)


entries = []
for text, labels in sorted(groups.items(), key=lambda kv: kv[1][0]):
    cond = CONDENSED[labels[0]]
    entries.append(dict(
        labels=labels, kind='profile' if labels[0].startswith('cast') else 'evidence',
        official=text, wo=W(text), shrink=game_scale(text),
        condensed=cond, wc=W(cond), lines=wrap(cond, W, LINE),
        olines=wrap(text, W, LINE),
    ))

def recommend(scale):
    if scale >= 0.90:
        return 'official', ('Shrunk only to %.2f - barely visible on the 3DS screen. '
                            "Not worth touching Capcom's text.") % scale
    return 'condensed', ('Shrunk to %.2f - visibly degraded in game. '
                         'The condensed text renders at full size.') % scale


NOTES = {
    'cast040_02_c': 'Flatter than the original\'s "published in a prominent magazine".',
    'cast103_00_c': 'Restructured sentence. "Thoroughly" would not fit; "most" keeps the intensifier.',
    'item1_12_00_c': 'First person kept by turning "I\'m not sure they can" into a question.',
    'cast218_00_c': 'Drops "to become a lawyer", the point of the test - but 0.69 is the second-worst shrink in the game.',
    'cast205_00_c': 'Loses "further his study" (he already studies English); kept the government-sponsorship fact instead.',
    'cast060_00_c': 'Loses only "eternally"; the souls and the menace survive.',
    'item5_24_00_c': 'Loses "relative positions", though a floor plan shows positions by nature.',
}

e = html.escape
cards = []
for i, en in enumerate(entries, 1):
    ids = ', '.join(en['labels'])
    note = ''
    for lab in en['labels']:
        if lab in NOTES:
            note = '<p class="note">%s</p>' % e(NOTES[lab])
    rec, why = recommend(en['shrink'])
    cards.append('''
<article class="card" data-id="%(id)s" data-rec="%(rec)s" id="c%(n)d">
  <header class="card-head">
    <span class="num">%(n)d</span>
    <span class="kind kind-%(kind)s">%(kind)s</span>
    <code class="labels">%(ids)s</code>
    <span class="rec rec-%(rec)s" title="%(why)s">suggest: %(rec)s</span>
    <label class="veto"><input type="checkbox" data-veto="%(id)s"> <span>Keep official</span></label>
  </header>
  <div class="pair">
    <section class="side">
      <h3>Official <span class="meta"><b>%(wo)d</b> px &middot; shrunk to <b>%(shrink).2f</b></span></h3>
      <div class="rec rec-shrunk" style="--s:%(shrink).3f">%(olines)s</div>
    </section>
    <section class="side">
      <h3>Condensed <span class="meta"><b>%(wc)d</b> px &middot; <b>%(nl)d</b> lines &middot; full size</span></h3>
      <div class="rec">%(clines)s</div>
    </section>
  </div>
  <details class="raw"><summary>Plain text</summary>
    <p><b>Official:</b> %(official)s</p>
    <p><b>Condensed:</b> %(condensed)s</p>
  </details>
  %(note)s
</article>''' % dict(
        n=i, id=en['labels'][0], kind=en['kind'], ids=e(ids),
        wo=en['wo'], shrink=en['shrink'], wc=en['wc'], nl=len(en['lines']),
        olines=''.join('<span>%s</span>' % e(l) for l in wrap(en['official'], W, LINE / en['shrink'])),
        clines=''.join('<span>%s</span>' % e(l) for l in en['lines']),
        official=e(en['official']), condensed=e(en['condensed']), note=note,
        rec=rec, why=e(why)))

page = '''<title>Court Record Captions</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@400;600;700&display=swap">
<style>
:root{
  --ground:#ece6d6; --ground-2:#e2dbc8; --text:#23211c; --muted:#6a665a;
  --card:#f6f0dc; --card-ink:#2a2216; --card-edge:#b9a25a; --trim:#8c6f24;
  --line:#cfc6ad; --accent:#1f5f6b; --veto:#b8432e; --veto-ink:#fff;
  --chip-ev:#3d6b3a; --chip-pr:#6b3d5a; --chip-ink:#fff;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --ground:#16232c; --ground-2:#1d2e39; --text:#dfe5e8; --muted:#96a5ad;
  --card:#f1e9cf; --card-ink:#2a2216; --card-edge:#c4a352; --trim:#d9b85f;
  --line:#2c3f4b; --accent:#8fd0dc; --veto:#e0634b; --veto-ink:#16232c;
  --chip-ev:#7fc07a; --chip-pr:#d48fbd; --chip-ink:#16232c;
}}
:root[data-theme="dark"]{
  --ground:#16232c; --ground-2:#1d2e39; --text:#dfe5e8; --muted:#96a5ad;
  --card:#f1e9cf; --card-ink:#2a2216; --card-edge:#c4a352; --trim:#d9b85f;
  --line:#2c3f4b; --accent:#8fd0dc; --veto:#e0634b; --veto-ink:#16232c;
  --chip-ev:#7fc07a; --chip-pr:#d48fbd; --chip-ink:#16232c;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--text);
  font:16px/1.5 "Source Sans 3",system-ui,Segoe UI,sans-serif;}
main{max-width:72ch;margin:0 auto;padding:2.5rem 1.25rem 6rem}
h1{font:600 2.1rem/1.1 "Crimson Pro",Georgia,serif;margin:0 0 .4rem;text-wrap:balance;letter-spacing:-.01em}
.lede{color:var(--muted);margin:0 0 1.5rem;max-width:62ch}
.lede b{color:var(--text)}
.toolbar{position:sticky;top:0;z-index:5;background:var(--ground-2);border:1px solid var(--line);
  border-radius:6px;padding:.6rem .9rem;display:flex;gap:1rem;align-items:center;flex-wrap:wrap;
  margin:0 0 1.75rem;font-variant-numeric:tabular-nums}
.toolbar .count{font-weight:700}
.toolbar button{font:inherit;font-weight:600;background:var(--accent);color:var(--ground);
  border:0;border-radius:4px;padding:.35rem .8rem;cursor:pointer}
.toolbar button:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.toolbar .hint{color:var(--muted);font-size:.9rem}
.card{border:1px solid var(--line);border-radius:8px;padding:1rem 1.1rem 1.1rem;margin:0 0 1.25rem;background:var(--ground-2)}
.card[data-vetoed="1"]{border-color:var(--veto)}
.card[data-vetoed="1"] .side:last-child{opacity:.45}
.card-head{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin-bottom:.8rem}
.num{font:600 1.1rem "Crimson Pro",serif;color:var(--trim);min-width:2ch;font-variant-numeric:tabular-nums}
.kind{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;padding:.1rem .5rem;border-radius:3px;color:var(--chip-ink)}
.kind-evidence{background:var(--chip-ev)} .kind-profile{background:var(--chip-pr)}
.labels{font-size:.8rem;color:var(--muted)}
.rec{font-size:.72rem;letter-spacing:.05em;text-transform:uppercase;padding:.12rem .5rem;border-radius:3px;border:1px solid var(--line);color:var(--muted);cursor:help}
.rec-condensed{border-color:var(--accent);color:var(--accent)}
.rec-official{border-color:var(--veto);color:var(--veto)}
.toolbar .ghost{background:transparent;color:var(--text);border:1px solid var(--line)}
.veto{margin-left:auto;display:flex;align-items:center;gap:.4rem;cursor:pointer;font-weight:600;user-select:none}
.veto input{accent-color:var(--veto);width:1.05rem;height:1.05rem}
.card[data-vetoed="1"] .veto span{color:var(--veto)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
@media (max-width:640px){.pair{grid-template-columns:1fr}}
.side h3{font:600 .8rem/1.2 "Source Sans 3",sans-serif;letter-spacing:.06em;text-transform:uppercase;margin:0 0 .45rem;color:var(--muted)}
.side h3 .meta{font-weight:400;letter-spacing:0;text-transform:none;margin-left:.4rem;font-variant-numeric:tabular-nums}
.side h3 b{color:var(--text);font-weight:600}
/* the Court Record panel: 4 lines of ~199 px at 12px glyphs -> 1 px = 1.05 CSS px here */
.rec{background:var(--card);color:var(--card-ink);border:2px solid var(--card-edge);border-radius:14px;
  padding:.55rem .8rem;font:400 1.08rem/1.32 "Crimson Pro",Georgia,serif;min-height:calc(4 * 1.32em + 1.1rem);
  box-shadow:inset 0 0 0 3px var(--card),inset 0 0 0 4px var(--card-edge)}
.rec span{display:block;white-space:nowrap;overflow:hidden;text-overflow:clip}
.rec-shrunk span{font-size:calc(1em * var(--s));line-height:calc(1.32em)}
.raw{margin-top:.7rem;font-size:.92rem}
.raw summary{cursor:pointer;color:var(--muted)}
.raw p{margin:.4rem 0 0;font-family:"Crimson Pro",Georgia,serif;font-size:1.02rem}
.note{margin:.6rem 0 0;padding:.45rem .7rem;border-left:3px solid var(--trim);background:var(--ground);font-size:.92rem}
.legend{font-size:.9rem;color:var(--muted);margin:0 0 1.5rem;display:grid;gap:.25rem}
.legend code{color:var(--text)}
@media (prefers-reduced-motion:no-preference){.card{transition:border-color .15s}}
</style>
<main>
<h1>Court Record Captions</h1>
<p class="lede">The Court Record shrinks any caption that will not fit four lines at full size. <b>90 captions</b> (80 unique texts) get shrunk, some to 67%. These are condensed to fit: Capcom's names, Ryunosuke's first person and the jokes are kept; only filler is cut. Each card carries my <b>suggestion</b> — hover it for the reason: keep the official text wherever the shrink is 0.90 or milder (barely visible), take the condensed text below that. <b>Apply suggestions</b> ticks the boxes to match; adjust from there, then copy the list. Tick <b>Keep official</b> on anything you would rather leave alone, then copy the list to me.</p>
<div class="legend">
  <div>Left panel shows the official text at the size the game actually shrinks it to. Right panel is the condensed text at full size.</div>
  <div>Both panels are drawn to the game's proportions: 4 lines, 199 px wide, 12 px serif.</div>
</div>
<div class="toolbar">
  <span><span class="count" id="count">0</span> kept official</span>
  <button id="copy">Copy veto list</button>
  <button id="suggest" class="ghost">Apply suggestions</button>
  <span class="hint" id="hint">Choices are saved in this browser.</span>
</div>
__CARDS__
</main>
<script>
(function(){
  var KEY='tgaa-caption-vetoes';
  var saved={}; try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  var boxes=document.querySelectorAll('input[data-veto]');
  var count=document.getElementById('count'), hint=document.getElementById('hint');
  function refresh(){
    var n=0;
    boxes.forEach(function(b){
      var card=b.closest('.card');
      card.setAttribute('data-vetoed', b.checked?'1':'0');
      if(b.checked) n++;
    });
    count.textContent=n;
  }
  boxes.forEach(function(b){
    b.checked=!!saved[b.dataset.veto];
    b.addEventListener('change',function(){
      saved[b.dataset.veto]=b.checked; if(!b.checked) delete saved[b.dataset.veto];
      localStorage.setItem(KEY,JSON.stringify(saved)); refresh();
    });
  });
  refresh();
  document.getElementById('suggest').addEventListener('click',function(){
    boxes.forEach(function(b){
      var rec=b.closest('.card').getAttribute('data-rec');
      b.checked=(rec==='official');
      saved[b.dataset.veto]=b.checked; if(!b.checked) delete saved[b.dataset.veto];
    });
    localStorage.setItem(KEY,JSON.stringify(saved)); refresh();
    hint.textContent='Suggestions applied — adjust any card, then copy the list.';
  });
  document.getElementById('copy').addEventListener('click',function(){
    var ids=[]; boxes.forEach(function(b){ if(b.checked){
      var c=b.closest('.card'); ids.push('#'+c.id.slice(1)+' '+b.dataset.veto); }});
    var text=ids.length?('Keep official: '+ids.join(', ')):'No vetoes - apply all condensed captions.';
    if(navigator.clipboard){navigator.clipboard.writeText(text).then(function(){hint.textContent='Copied: '+text;});}
    else{hint.textContent=text;}
  });
})();
</script>
'''.replace('__CARDS__', '\n'.join(cards))

out = os.path.join(HERE, 'court_record_captions.html')
open(out, 'w', encoding='utf-8').write(page)
print('wrote', out, len(page), 'bytes,', len(entries), 'cards')

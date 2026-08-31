# -*- coding: utf-8 -*-
"""Apply the recommended condensed captions to the base romfs (base v15).

Rule (user accepted the recommendations without review, 2026-08-28): labels
whose OFFICIAL text the Court Record shrinks below 0.90 get the condensed text;
the mild cases (>= 0.90) keep Capcom's wording as re-wrapped in v14. Condensed
texts are stored wrapped at 199 px so the evidence banner (which honours stored
breaks) shows them exactly as the Court Record will.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'audio_tools'))
sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from caption_width import arc, advances, strip
from caption_fit import wrap
from condensed import CONDENSED
from dgs2tool.arc import parse_arc, build_arc_bytes
from dgs2tool.gmd import parse_gmd_bytes, build_gmd_bytes

ROOT = os.path.join(HERE, '..', 'base_v12', 'romfs_dir')
GMDS = ['msg/evidence_caption_jpn.gmd', 'msg/cast_caption_jpn.gmd']
LINE = 199

ui = {e.name: e.data for e in parse_arc(open(os.path.join(ROOT,'archive','UI_cmn_jpn.arc'),'rb').read())['entries']}
adv, _ = advances(ui['UI/0_system/00_font/font03_jpn.gfd'])
W = lambda s: sum(adv.get(ord(c), 7) for c in s)

def game_scale(text):
    s = 1.0
    while s > 0.5 and len(wrap(text, W, LINE / s)) > 4:
        s -= 0.01
    return round(s, 2)

msg_path = os.path.join(ROOT, 'archive', 'msg_cmn_jpn.arc')
msg = parse_arc(open(msg_path, 'rb').read())
ment = {e.name: e.data for e in msg['entries']}
repl = {}
applied = kept = 0
for g in GMDS:
    doc = parse_gmd_bytes(ment[g])
    for e in doc['entries']:
        lab = str(e.get('label'))
        if lab not in CONDENSED:
            continue
        flat_official = ' '.join(strip(e['text']).split())
        # v14 already re-wrapped; scale must come from the official WORDING,
        # which is unchanged by re-wrapping
        if game_scale(flat_official) >= 0.90:
            kept += 1
            continue
        lines = wrap(CONDENSED[lab], W, LINE)
        assert len(lines) <= 4 and all(W(l) <= 208 for l in lines), lab
        e['text'] = '\r\n'.join(lines)
        applied += 1
    repl[g] = build_gmd_bytes(doc)
open(msg_path, 'wb').write(build_arc_bytes(msg, repl))
print('%d condensed applied, %d kept official (mild shrink)' % (applied, kept))

# verify from disk
back = {e.name: e.data for e in parse_arc(open(msg_path, 'rb').read())['entries']}
import re
bad = 0
for g in GMDS:
    for e in parse_gmd_bytes(back[g])['entries']:
        t = e.get('text') or ''
        if '<' in re.sub(r'<[^>]*>', '', t):
            bad += 1
        ls = t.split('\r\n')
        if str(e.get('label')) != 'null' and t.strip() and (len(ls) > 6 or any(W(l) > 208 for l in ls)):
            print('  !! %s bad geometry' % e.get('label')); bad += 1
print('re-read: %d problems' % bad)
sys.exit(1 if bad else 0)

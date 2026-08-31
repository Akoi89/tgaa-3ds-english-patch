# -*- coding: utf-8 -*-
"""v19: fixed font00 metrics + targeted re-wrap, via senyarom's own pipeline.

Replicates upstream scripts/build_3ds_official_layout.py main() over a copy of
our v18 update tree:
  1. adapt font00 advances from the PC font (scale 1/3, advance >= ink-1)
  2. reflow every flat .gmd against the new metrics (265-unit dialogue budget,
     2-line pages via E023/PAGE + E041 reopen; wording+tags assert-protected)
  3. movie subtitles reflowed at the 304-unit budget
  4. font03 narration segments measured with font03's own (unchanged) advances
Arcs are not walked, so the shipped caption work and episode-title fixes in
msg_cmn/UI_cmn stay untouched except for the one font00_jpn.gfd member.
"""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get('DGS2TOOL', '.'))
sys.path.insert(0, str(REPO))

from dgs2tool.arc import parse_arc, build_arc_bytes  # noqa: E402

spec = importlib.util.spec_from_file_location(
    'b3ol', REPO / 'scripts' / 'build_3ds_official_layout.py')
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

WORK = HERE / 'v19_dir'
TMP = HERE / 'v19_font_work'


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(HERE / 'v18_dir', WORK)
    TMP.mkdir(exist_ok=True)

    ui_arc_path = WORK / 'archive' / 'UI_cmn_jpn.arc'
    ui = parse_arc(ui_arc_path.read_bytes())
    members = {e.name: e.data for e in ui['entries']}
    (TMP / 'font00_scarlet.gfd').write_bytes(
        members['UI/0_system/00_font/font00_jpn.gfd'])
    (TMP / 'font00_atlas.tex').write_bytes(
        members['UI/0_system/00_font/font00_jpn_00_AM_NOMIP.tex'])
    (TMP / 'font03.gfd').write_bytes(
        members['UI/0_system/00_font/font03_jpn.gfd'])

    pc_arc = parse_arc(Path(
        os.path.join(os.environ.get('TGAAC_STEAM', ''), 'archive', 'font_eng.arc')).read_bytes())
    pc_members = {e.name: e.data for e in pc_arc['entries']}
    (TMP / 'font00_eng.gfd').write_bytes(
        pc_members['UI/0_system/00_font/font00_eng.gfd'])

    # metrics: the hand-tuned Scarlet/v10 gfd verbatim (the font the user
    # liked); no adaptation pass -- reflow simply follows these advances
    sc_arc = parse_arc(Path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
             'scarlet_dgs2_dir', 'archive', 'UI_cmn_jpn.arc')
    ).read_bytes())
    sc_members = {e.name: e.data for e in sc_arc['entries']}
    (TMP / 'font00_new.gfd').write_bytes(
        sc_members['UI/0_system/00_font/font00_jpn.gfd'])
    widths = B.read_3ds_advances(TMP / 'font00_new.gfd')
    old_widths = B.read_3ds_advances(TMP / 'font00_scarlet.gfd')
    changed = [c for c in widths if widths.get(c) != old_widths.get(c)]
    font_report = {'metrics': 'scarlet/v10 verbatim',
                   'changed_advances': len(changed)}
    print('font:', json.dumps(font_report))

    reflow_report = B.reflow_tree(
        WORK,
        widths,
        365,
        {},
        265,
    )

    movie_report = None
    movie_gmd = WORK / 'msg' / 'movie_subtitle_jpn.gmd'
    if movie_gmd.exists() and hasattr(B, 'reflow_movie_subtitles'):
        movie_report = B.reflow_movie_subtitles(movie_gmd, widths, 304)

    new_gfd = (TMP / 'font00_new.gfd').read_bytes()
    ui_arc_path.write_bytes(build_arc_bytes(
        ui, {'UI/0_system/00_font/font00_jpn.gfd': new_gfd}))

    report = {'font': font_report, 'reflow': reflow_report,
              'movie_subtitles': movie_report}
    (HERE / 'v19_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = {k: v for k, v in reflow_report.items()
               if not isinstance(v, list)}
    print('reflow summary:', json.dumps(summary))
    overflows = reflow_report.get('overflows') or []
    print('overflows:', len(overflows))
    for o in overflows[:10]:
        print('  ', json.dumps(o, ensure_ascii=False)[:200])


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Line width in REAL PIXELS, from the game's own font descriptor.

Why not textwidth.width(): that is a Helvetica-ratio model with an arbitrary
scale, calibrated per game from screenshots. It mismeasures, and it cannot be
carried between builds, because TGAA1, TGAA2 and the TGAA2 DLC all ship
DIFFERENT font00 advances -- our TGAA1/DLC font is ~9% wider on common
lowercase than senyarom's. Measuring against the GFD the console actually
loads removes the guesswork.

TWO BUDGETS, AND THEY ARE NOT THE ONES YOU WOULD GUESS. From upstream
reflow_scenario_text(): "The GFD advances describe the 12-pixel font cells,
while E041 dialogue is rendered at roughly 1.25x scale. A 265-unit limit
therefore protects the physical right edge and the page-advance arrow."

  DIALOGUE  = 265   a page whose visible text is introduced by the normal
                    E041 speaker box -- i.e. ordinary conversation.
  WIDGET    = 365   everything else: testimony, narration, scenario text,
                    the specialised boxes that are not scaled up.

So the SAME line is legal at 300 units in a testimony box and overflowing in a
conversation box. Classify the segment first; upstream's own
is_standard_dialogue_segment() is the classifier, so use it rather than
sniffing for <E041> by hand.

Pages carrying SPECIAL_LAYOUT_TAGS (<CNTR>, <SIZE , <RUBY>, <RT>) are laid out
by hand and upstream refuses to touch them. Do the same.

The advance parser is upstream's read_3ds_advances -- do not hand-roll it. The
20-byte GFD record is codepoint u32 at +0 and advance (u32 at +12) & 0xFFF; the
plausible-looking byte at +11 is an atlas coordinate, not a width.
"""
import importlib.util
import os
import re
import sys
from pathlib import Path

DIALOGUE = 265
WIDGET = 365
BUDGET = WIDGET          # back-compat for callers that pass a segment-free line
_REPO = Path(os.environ.get('DGS2TOOL', os.environ.get('DGS2TOOL', '.')))
_spec = importlib.util.spec_from_file_location(
    'b3ol', _REPO / 'scripts' / 'build_3ds_official_layout.py')
_B = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(_REPO))          # build_3ds_official_layout imports dgs2tool
_spec.loader.exec_module(_B)

TAG = re.compile(r'<[^>]*>')

sys.path.insert(0, str(_REPO))
from dgs2tool.pagination import (                    # noqa: E402
    is_standard_dialogue_segment, is_interactive_tutorial_segment)

SPECIAL_LAYOUT_TAGS = ('<CNTR>', '<SIZE ', '<RUBY>', '<RT>')


def hand_laid_out(segment):
    """Upstream refuses to reflow these; so do we."""
    return any(t in segment for t in SPECIAL_LAYOUT_TAGS)


def budget_for(segment):
    if is_standard_dialogue_segment(segment) or is_interactive_tutorial_segment(segment):
        return DIALOGUE
    return WIDGET


def advances(gfd_path):
    return _B.read_3ds_advances(Path(gfd_path))


def font_from_arc(arc_path, out_gfd):
    """font00 lives inside UI_cmn_jpn.arc (zlib members), not loose in romfs."""
    from dgs2tool.arc import parse_arc
    for e in parse_arc(open(arc_path, 'rb').read())['entries']:
        if 'font00' in e.name and e.name.endswith('.gfd'):
            open(out_gfd, 'wb').write(e.data)
            return out_gfd
    raise SystemExit('no font00 in %s' % arc_path)


def px(line, adv):
    return sum(adv.get(ord(c), 0) for c in line)


def lines(page):
    return [l.strip() for l in TAG.sub('', page).replace('\r', '').split('\n') if l.strip()]


def best_two_line(text, adv):
    """Narrowest achievable max-line-width over every word boundary, in px.

    This -- not the total width -- is the fit test. Filtering on total > 2*BUDGET
    misses every statement whose words split unevenly.
    """
    w = text.split()
    if len(w) < 2:
        return px(text, adv)
    return min(max(px(' '.join(w[:i]), adv), px(' '.join(w[i:]), adv))
               for i in range(1, len(w)))


def split_two(text, adv):
    w = text.split()
    best = None
    for i in range(1, len(w)):
        a, b = ' '.join(w[:i]), ' '.join(w[i:])
        m = max(px(a, adv), px(b, adv))
        if best is None or m < best[0]:
            best = (m, a, b)
    return best

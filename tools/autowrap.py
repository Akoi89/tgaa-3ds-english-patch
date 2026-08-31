"""
Automatic line-breaking and page-splitting for assembled GMD entry text.

Why this exists: line breaks were previously placed by hand, by writing
multi-line entries in the chunks files. That is unreliable in both
directions -- it is easy to leave a line too wide (it gets clipped at the
right edge; the game does NOT auto-wrap, confirmed by a screenshot of a
newspaper headline cut off mid-word), and just as easy to overcorrect and
produce a 3-line page, where the third line is clipped off the bottom of a
box that is exactly 2 lines tall. A previous pass did precisely that:
fixing width overflows by inserting breaks turned 20 pages into 3- and
4-line pages.

Both limits are properties of the box, not of the translation, so the
build enforces them rather than the translator remembering to. This
module rewrites the '\\r\\n' placement inside each <PAGE>-bounded screen:
existing breaks are kept when they already produce a legal layout, and
otherwise discarded and re-inserted by balanced word-wrapping at the real
measured box width (see textwidth.py and check_fit.py for the
calibration).

When the words cannot fit in 2 lines at all, the text SPILLS ONTO A
CONTINUATION PAGE rather than being reported as unfixable. That is what
the official localization itself does throughout -- a sentence runs two
lines, the player advances, and it finishes on the next page:

    Do I take it then, Counsel, that you
    personally witnessed the scene
        -> where the incident took place?

The tag recipe for a continuation page was taken from those official
entries (sce07_c008_0000 and others) and is exactly:

    <E023><PAGE>\\r\\n<E041 X Y><E025 N>

<E023> is the wait-for-input marker that precedes essentially every
<PAGE>. <E041> (speaker/portrait) and <E025> (text speed) are simply
repeated from the page being split -- continuation pages carry NO <E800>
(those number a voice/---event stream and must not be invented), which is
why 201 of the sampled official pages begin with no <E800> at all.

Splitting is refused inside a paired formatting span (<E006>..<E005>,
<FONT>, <RGB>): those set a state the renderer carries until its closing
tag, and cutting a page in half through one would leave the second page
in a state nothing ever closes.
"""
import re
from tag_align import tokenize
from textwidth import width

MAX_LINES = 2
# Wrap target. The widest normal dialogue line in the pristine official
# v1.0.5 release is 19976 units (n=3320); wrapping is done at 19835,
# leaving a deliberate ~140-unit margin for error in the width model
# itself (textwidth.py uses stand-in font metrics, not this font's own).
# check_fit.py fails only above the true 19976 ceiling, so the margin
# costs nothing but an occasional early break. Corroborated independently by an in-game screenshot:
# on the newspaper-headline screen the first line (w=27973) is visibly
# clipped mid-word while the second, "IS THE CULPRIT A FELLOW
# STUDENT?'..." (w=19695), renders complete -- so the box is at least
# 19695 wide, which rules out the tighter thresholds an earlier pass
# used. Wrapping at 19000 rejected pages the box handles comfortably and
# forced rewrites that were never needed.
SAFE_W = 19835
CNTR_SAFE_W = 23233

_OPEN_SPANS = {'<E006>'}
_CLOSE_SPANS = {'<E005>'}
_OPEN_RE = re.compile(r'^<(FONT|RGB)\b', re.IGNORECASE)
_CLOSE_RE = re.compile(r'^</(FONT|RGB)\b', re.IGNORECASE)


def _wrap_words(words, max_w, max_lines):
    """Word-wrap into at most max_lines lines of at most max_w each.
    Returns list-of-lists-of-word-indices, or None if impossible.

    Deliberately NOT greedy. Greedy wrapping packs the first line as full
    as it will go, which can force a third line onto a page that fits
    perfectly well in two -- e.g. "honestly, we couldn't be more
    different. He's a prodigy, pride of Imperial University." is 1326
    units UNDER the two-line budget, yet greedy overfills line 1 and
    spills two words onto a line 3 that the box cannot show. Since the
    box is only ever 2 lines, the split point is chosen by search, and
    among the splits that fit, the most balanced one wins -- that also
    looks closest to how the official script breaks its lines."""
    if not words:
        return []

    whole = ' '.join(words)
    if width(whole) <= max_w:
        return [list(range(len(words)))]

    if max_lines < 2:
        return None

    best = None
    for k in range(1, len(words)):
        w1 = width(' '.join(words[:k]))
        w2 = width(' '.join(words[k:]))
        if w1 <= max_w and w2 <= max_w:
            badness = abs(w1 - w2)
            if best is None or badness < best[0]:
                best = (badness, k)
    if best is not None:
        k = best[1]
        return [list(range(k)), list(range(k, len(words)))]
    return None


def _greedy_lines(words, max_w):
    """Wrap into as many lines as it takes -- used only to find the
    MINIMUM number of lines the text needs."""
    lines, cur, cur_text = [], [], ''
    for i, w in enumerate(words):
        trial = w if not cur else cur_text + ' ' + w
        if cur and width(trial) > max_w:
            lines.append(cur)
            cur, cur_text = [i], w
        else:
            cur.append(i)
            cur_text = trial
    if cur:
        lines.append(cur)
    return lines


def _balanced_lines(words, max_w, n_lines):
    """Split `words` into exactly n_lines lines, each within max_w,
    making them as even as possible. Returns None if impossible.

    Greedy wrapping crams every line full and leaves the remainder on the
    last one, which reads badly once the text spills onto a continuation
    page: it produces a whole extra screen holding the single word
    "officer!" or "Judicature.". Evening the lines out spreads the text
    so the spill page carries a real share of it, which is also how the
    official script's continuation pages look."""
    n = len(words)
    if n_lines <= 0 or n_lines > n:
        return None

    w_of = {}

    def seg_width(i, j):
        if (i, j) not in w_of:
            w_of[(i, j)] = width(' '.join(words[i:j]))
        return w_of[(i, j)]

    INF = float('inf')
    # best[k][i] = cost of splitting words[i:] into k lines
    best = [[INF] * (n + 1) for _ in range(n_lines + 1)]
    choice = [[-1] * (n + 1) for _ in range(n_lines + 1)]
    best[0][n] = 0
    for k in range(1, n_lines + 1):
        for i in range(n + 1):
            for j in range(i + 1, n + 1):
                w = seg_width(i, j)
                if w > max_w:
                    break
                rest = best[k - 1][j]
                if rest is INF:
                    continue
                slack = max_w - w
                cost = rest + slack * slack
                if cost < best[k][i]:
                    best[k][i] = cost
                    choice[k][i] = j
    if best[n_lines][0] is INF:
        return None
    lines, i = [], 0
    for k in range(n_lines, 0, -1):
        j = choice[k][i]
        lines.append(list(range(i, j)))
        i = j
    return lines


def rewrap_entry(entry_text, label='', max_lines=None, fix_width=True,
                 only_pages=None):
    """Returns (new_text, overfull_pages).

    max_lines overrides the 2-line default for widgets that hold more
    (a location panel holds 5). fix_width=False restricts the pass to
    line-COUNT overflow only, leaving pages that merely run wide exactly
    as they were -- useful when repairing one defect class in someone
    else's script without silently reflowing the rest of it.

    overfull_pages lists any page that could not be laid out even with
    continuation pages -- in practice only a single word wider than the
    box, which no break placement can rescue."""
    if max_lines is None:
        max_lines = MAX_LINES
    # only_pages restricts the pass to specific <PAGE>-bounded screens,
    # by index. Without it, repairing one page also re-flows every other
    # page in the same entry -- which silently rewrites text that was
    # never in question and, worse, can add continuation pages of its own.
    tokens = tokenize(entry_text)

    groups, cur = [], []
    for i, (kind, s) in enumerate(tokens):
        cur.append(i)
        if kind == 'tag' and s == '<PAGE>':
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

    out = []
    overfull = []
    # <E041>/<E025> carry across pages within an entry; a continuation page
    # reuses whatever was most recently in force.
    last_e041 = last_e025 = None

    for group_no, group in enumerate(groups):
        gtokens = [tokens[i] for i in group]
        if only_pages is not None and group_no not in only_pages:
            for k, s in gtokens:
                if k == 'tag':
                    if s.startswith('<E041'):
                        last_e041 = s
                    elif s.startswith('<E025'):
                        last_e025 = s
            out.extend(gtokens)
            continue
        is_cntr = any(k == 'tag' and s == '<CNTR>' for k, s in gtokens)
        max_w = CNTR_SAFE_W if is_cntr else SAFE_W

        for k, s in gtokens:
            if k == 'tag':
                if s.startswith('<E041'):
                    last_e041 = s
                elif s.startswith('<E025'):
                    last_e025 = s

        if not any(k == 'text' and s.strip() for k, s in gtokens):
            out.extend(gtokens)
            continue

        # Break the group into an ordered item stream so tags keep their
        # position relative to the words around them.
        items = []          # ('tag', s) | ('word', s) | ('gap', s)
        for k, s in gtokens:
            if k == 'tag':
                items.append(('tag', s))
                continue
            pos = 0
            while pos < len(s):
                if s[pos].isspace():
                    start = pos
                    while pos < len(s) and s[pos].isspace():
                        pos += 1
                    items.append(('gap', s[start:pos]))
                else:
                    start = pos
                    while pos < len(s) and not s[pos].isspace():
                        pos += 1
                    items.append(('word', s[start:pos]))

        # Group items into UNITS. A unit is everything between two runs of
        # whitespace -- which is not the same as a "word": rebuild() has
        # already decided, carefully, where a space belongs and where two
        # runs butt together with none (a closing quote hugging its word,
        # a passthrough '.' after a name). Those joins carry no whitespace,
        # so treating each text run as its own word and re-inserting a
        # space between them would undo that work and print
        # "Kazuma Asogi . He's also". Only a real gap may become a break.
        unit_of_item = []
        unit = 0
        unit_has_word = False
        for kind, s in items:
            if kind == 'gap':
                if unit_has_word:
                    unit += 1
                    unit_has_word = False
                unit_of_item.append(None)
            else:
                if kind == 'word':
                    unit_has_word = True
                unit_of_item.append(unit)

        n_units = unit + (1 if unit_has_word else 0)
        if n_units == 0:
            out.extend(gtokens)
            continue

        unit_text = [''] * n_units
        for (kind, s), u in zip(items, unit_of_item):
            if kind == 'word' and u is not None and u < n_units:
                unit_text[u] += s

        # For each gap, which unit follows it (None = nothing follows).
        follows = [None] * len(items)
        nxt = None
        for i in range(len(items) - 1, -1, -1):
            if items[i][0] == 'gap':
                follows[i] = nxt
            elif unit_of_item[i] is not None and items[i][0] == 'word':
                nxt = unit_of_item[i]

        # Units that a hand-placed '\r\n' put at the start of a line.
        forced_break = set()
        for i, (kind, s) in enumerate(items):
            if kind == 'gap' and ('\n' in s or '\r' in s):
                nxt_u = None
                for j in range(i + 1, len(items)):
                    if items[j][0] == 'word':
                        nxt_u = unit_of_item[j]
                        break
                if nxt_u:
                    forced_break.add(nxt_u)

        # A page may not start inside a paired formatting span.
        safe_page_start = set()
        depth = 0
        for (kind, s), u in zip(items, unit_of_item):
            if kind == 'tag':
                if s in _OPEN_SPANS or _OPEN_RE.match(s):
                    depth += 1
                elif s in _CLOSE_SPANS or _CLOSE_RE.match(s):
                    depth = max(0, depth - 1)
            elif kind == 'word' and depth == 0 and u is not None:
                safe_page_start.add(u)

        # Keep a hand-placed layout that is already legal.
        raw_lines = [l for l in ''.join(
            ('\n' if ('\n' in s or '\r' in s) else ' ') if kind == 'gap'
            else (s if kind == 'word' else '')
            for kind, s in items).split('\n') if l.strip()]
        if len(raw_lines) > 1 and len(raw_lines) <= MAX_LINES \
                and all(width(l) <= max_w for l in raw_lines):
            out.extend(gtokens)
            continue

        wrapped = _wrap_words(unit_text, max_w, max_lines)
        if wrapped is not None:
            lines = wrapped
            page_of_line = [0] * len(lines)
        else:
            # A hand-placed break is a mandatory boundary here, not just a
            # hint. Once text spills across pages the automatic split can
            # land somewhere that reads badly ("BRUTALLY MURDERED! IS THE"
            # / "CULPRIT A FELLOW STUDENT?"), and there has to be a way to
            # say where a headline or a line of verse actually divides.
            # Each hand-marked segment is then wrapped on its own.
            segments = []
            start = 0
            for u in range(1, n_units):
                if u in forced_break:
                    segments.append((start, u))
                    start = u
            segments.append((start, n_units))

            lines = []
            failed = False
            for a, b in segments:
                seg = unit_text[a:b]
                if not seg:
                    continue
                need = len(_greedy_lines(seg, max_w))
                sub = _balanced_lines(seg, max_w, need)
                if sub is None:
                    failed = True
                    break
                for ln in sub:
                    lines.append([a + i for i in ln])
            if failed or any(
                    width(' '.join(unit_text[i] for i in ln)) > max_w
                    for ln in lines):
                overfull.append(' '.join(unit_text))
                out.extend(gtokens)
                continue
            page_of_line = [n // max_lines for n in range(len(lines))]
            # Never start a page inside a formatting span -- fold such a
            # line back onto the previous page instead.
            for n in range(1, len(lines)):
                if page_of_line[n] != page_of_line[n-1] \
                        and lines[n][0] not in safe_page_start:
                    page_of_line[n] = page_of_line[n-1]

        line_start = {ln[0]: n for n, ln in enumerate(lines)}

        buf = []
        for i, (kind, s) in enumerate(items):
            if kind != 'gap':
                buf.append(('tag' if kind == 'tag' else 'text', s))
                continue
            u = follows[i]
            if u is None or u == 0:
                # leading / trailing whitespace: the original's own layout
                buf.append(('text', s))
                continue
            n = line_start.get(u)
            if n is None:
                buf.append(('text', ' '))
            elif page_of_line[n] == page_of_line[n-1]:
                buf.append(('text', '\r\n'))
            else:
                buf.append(('tag', '<E023>'))
                buf.append(('tag', '<PAGE>'))
                buf.append(('text', '\r\n'))
                if last_e041:
                    buf.append(('tag', last_e041))
                if last_e025:
                    buf.append(('tag', last_e025))

        # merge adjacent text pieces back into single text tokens
        for kind, s in buf:
            if kind == 'text' and out and out[-1][0] == 'text':
                out[-1] = ('text', out[-1][1] + s)
            else:
                out.append((kind, s))

    return ''.join(s for (_, s) in out), overfull

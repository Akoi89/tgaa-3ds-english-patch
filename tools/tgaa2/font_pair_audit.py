# -*- coding: utf-8 -*-
"""Pair-spacing audit for TGAA2 font00: finds overlaps and holes without
screenshots. Composes real atlas glyphs at gfd advances for every bigram in
the shipped scripts and measures row-wise ink distance.

    python font_pair_audit.py <font00.gfd> [script_root=v20_dir/script]

gap < 0  -> glyphs overlap (fix: raise advance)
gap >= 4 -> visible hole  (fixable only if the glyph is above its ink+0
            bearing; per-pair kerning does not exist in this format)
"""
import importlib.util, struct, sys, collections
import numpy as np
from pathlib import Path
REPO = Path(os.environ.get('DGS2TOOL', '.'))
sys.path.insert(0, str(REPO))
from dgs2tool.gmd import parse_gmd_bytes
import os
spec = importlib.util.spec_from_file_location('b3ol', REPO/'scripts'/'build_3ds_official_layout.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
HERE = Path(__file__).resolve().parent
atlas = np.asarray(B.read_atlas(HERE/'v19_font_work'/'font00_atlas.tex'))

def main(gfd_path, script_root):
    blob = Path(gfd_path).read_bytes()
    header = struct.unpack_from('<4sI8i4f', blob, 0)
    off = B._gfd_name_end(blob, 56, header[9])
    G = {}
    for i in range(header[7]):
        e = off + i*20
        cp, tmp1, tmp2, tmp3 = struct.unpack_from('<4I', blob, e)
        gx = (tmp1 >> 8) & 0xFFF; gy = (tmp1 >> 20) & 0xFFF
        gw = tmp2 & 0xFFF; gh = (tmp2 >> 12) & 0xFFF
        if 33 <= cp < 0x250 and gw and gh:
            tile = atlas[gy:gy+gh, gx:gx+gw] > 96
            if tile.any():
                G[chr(cp)] = (tile, tmp3 & 0xFFF)
    freq = collections.Counter()
    for p in sorted(Path(script_root).rglob('*.gmd')):
        doc = parse_gmd_bytes(p.read_bytes())
        for e in doc['entries']:
            t = e.get('text')
            if not t:
                continue
            vis = B.visible(t)
            for a, b in zip(vis, vis[1:]):
                if a in G and b in G:
                    freq[a+b] += 1
    def pair_gap(a, b):
        ta, adv = G[a]; tb, _ = G[b]
        ha = ta.shape[0]; hb = tb.shape[0]
        best = None
        for r in range(max(ha, hb)):
            ra = np.where(ta[r])[0] if r < ha else []
            rb = np.where(tb[r])[0] if r < hb else []
            if len(ra) and len(rb):
                d = (adv + rb[0]) - (ra[-1] + 1)
                best = d if best is None else min(best, d)
        return best
    rows = []
    for pair, n in freq.most_common(800):
        g = pair_gap(pair[0], pair[1])
        if g is not None:
            rows.append((g, n, pair))
    overlaps = sorted(r for r in rows if r[0] < 0)
    holes = sorted((r for r in rows if r[0] >= 4), key=lambda r: -r[1])
    print('pairs:', len(rows), ' overlaps:', len(overlaps))
    for g, n, p in overlaps[:20]:
        print('  OVERLAP %r gap %d freq %d' % (p, g, n))
    for g, n, p in holes[:20]:
        print('  HOLE    %r gap %d freq %d' % (p, g, n))
    return len(overlaps)

if __name__ == '__main__':
    gfd = sys.argv[1] if len(sys.argv) > 1 else str(HERE/'v19_font_work'/'font00_v20.gfd')
    root = sys.argv[2] if len(sys.argv) > 2 else str(HERE/'v20_dir'/'script')
    sys.exit(0 if main(gfd, root) <= 2 else 1)

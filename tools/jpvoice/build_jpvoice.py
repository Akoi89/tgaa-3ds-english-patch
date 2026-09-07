# -*- coding: utf-8 -*-
"""Step 2 of the Japanese-voice build: revert every audio file to Capcom's Japanese and rebuild.

Rule (per our shipped title, from jpvoice/inventory.json written by inventory.py):
  update titles  every file whose top-level dir is in REVERT_DIRS[title]:
                   in the JP update romfs  -> copy the JP file over ours
                   else in the cartridge   -> DELETE it from the update romfs (the console then
                                              falls through to the cartridge's copy; an update
                                              title is a file-level overlay on the base)
                   else (no JP counterpart) -> keep, and list it in the report as UNMATCHED
  DLC titles     every file whose top-level dir is in REVERT_DIRS[title], per content:
                   in the JP DLC's same content -> copy the JP file over ours
                   else -> keep, UNMATCHED
Everything outside REVERT_DIRS is left exactly as shipped (text, art, layout).

The romfs is repacked with 3dstool, spliced into the content with ncch.splice (hash chain
repaired, CXI never rebuilt), and the CIA rewritten by cia.Cia.write with the SAME title version
as the English build. Output: jpvoice/_out/<name>-jpvoice.cia plus a per-title report.

Usage: python jpvoice\build_jpvoice.py            (all four titles)
       python jpvoice\build_jpvoice.py TGAA2_upd  (one)
"""
import os, sys, io, json, hashlib, shutil, subprocess, collections
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
import ncch
from cia import Cia
sys.path.insert(0, os.path.join(ROOT, 'jpvoice'))
from inventory import SRC, TREES, T3, run, romfs_of_ncch, walk, h
sys.path.insert(0, os.path.join(ROOT, 'dlc_icons', 'tgaa2-en-patch'))
from dgs2tool.arc import parse_arc, build_arc_bytes
# member type id of the voice streams inside the character and sound-script archives (.mca)
ARC_AUDIO_EXT = {'79C47B59'}


def revert_arc_audio(ours_path, jp_path, dst):
    """Put the JP voice members back into one archive. Returns ('whole'|'members'|None, n).
    If every differing member is a voice stream, the JP archive is copied whole (byte-identical to
    Capcom's). If text or art members differ too, only the voice members are replaced, through
    build_arc_bytes, so our text and art stay."""
    ao = parse_arc(open(ours_path, 'rb').read()); aj = parse_arc(open(jp_path, 'rb').read())
    mo = {e.name: e.data for e in ao['entries']}; mj = {e.name: e.data for e in aj['entries']}
    diff = [n for n in mo if n in mj and mo[n] != mj[n]]
    aud = [n for n in diff if n.rsplit('.', 1)[-1] in ARC_AUDIO_EXT]
    if not aud:
        return None, 0
    added = set(mo) - set(mj); removed = set(mj) - set(mo)
    if len(aud) == len(diff) and not added and not removed:
        shutil.copyfile(jp_path, dst); return 'whole', len(aud)
    out = build_arc_bytes(ao, {n: mj[n] for n in aud})
    chk = parse_arc(out)
    mc = {e.name: e.data for e in chk['entries']}
    assert set(mc) == set(mo)
    for n in mo:
        assert mc[n] == (mj[n] if n in aud else mo[n]), n
    open(dst, 'wb').write(out)
    return 'members', len(aud)

HERE = os.path.join(ROOT, 'jpvoice')
OUT = os.path.join(HERE, '_out')
os.makedirs(OUT, exist_ok=True)

# Top-level romfs directories whose files are reverted. Filled in from inventory_summary.txt
# (see REVERT_DIRS_NOTE in the report). 'movie' is reverted for the base games only: the DLC
# movies are subtitled commentary whose audio was never dubbed.
REVERT_DIRS = {
    'TGAA1_upd': {'sound', 'movie'},
    'TGAA2_upd': {'sound', 'movie'},
    'TGAA1_dlc': {'sound'},
    'TGAA2_dlc': {'sound'},
}
OUT_NAME = {
    'TGAA1_upd': 'TGAA1-base-3.2.3-jpvoice.cia',
    'TGAA2_upd': 'TGAA2-base-1.0.16-jpvoice.cia',
    'TGAA1_dlc': 'TGAA1-DLC-1.0.10-jpvoice.cia',
    'TGAA2_dlc': 'TGAA2-DLC-1.0.9-jpvoice.cia',
}


def repack(tree_dir, out_romfs):
    if os.path.exists(out_romfs):
        os.remove(out_romfs)
    run(T3, '-ctf', 'romfs', out_romfs, '--romfs-dir', tree_dir)
    return open(out_romfs, 'rb').read()


def build(title, rows):
    g = title.split('_')[0]
    kind = title.split('_')[1]
    s = SRC[g]
    src_cia = s['ours_upd'] if kind == 'upd' else s['ours_dlc']
    c = Cia(src_cia)
    rep = collections.Counter(); unmatched = []; changed_files = []
    replace = {}
    contents = sorted(set(r['content'] for r in rows))
    for ci in contents:
        ours_dir = os.path.join(TREES, g + '_ours_' + kind, 'c%d' % ci)
        work = os.path.join(HERE, '_work', title, 'c%d' % ci)
        if os.path.isdir(work):
            shutil.rmtree(work)
        shutil.copytree(ours_dir, work, ignore=shutil.ignore_patterns('.done'))
        if kind == 'upd':
            jp_upd = os.path.join(TREES, g + '_jp_upd', 'c0')
            jp_cart = os.path.join(TREES, g + '_jp_cart', 'c0')
        else:
            jp_dlc = os.path.join(TREES, g + '_jp_dlc', 'c%d' % ci)
        touched = False
        for r in rows:
            if r['content'] != ci:
                continue
            rel = r['rel']; top = rel.split('/')[0] if '/' in rel else '(root)'
            if rel.endswith('.arc') and r['bucket'] == 'changed':
                dst = os.path.join(work, rel.replace('/', os.sep))
                if kind == 'upd':
                    cands = [os.path.join(TREES, g + '_jp_upd', 'c0', rel.replace('/', os.sep)), os.path.join(TREES, g + '_jp_cart', 'c0', rel.replace('/', os.sep))]
                else:
                    cands = [os.path.join(TREES, g + '_jp_dlc', 'c%d' % ci, rel.replace('/', os.sep))]
                jp = next((p for p in cands if os.path.exists(p)), None)
                if jp is None:
                    rep['arc with no JP counterpart, kept'] += 1; continue
                how, n = revert_arc_audio(dst, jp, dst)
                if how is None:
                    rep['arc changed but no voice members, kept'] += 1; continue
                rep['arc voice members reverted (%s)' % how] += 1; rep['  voice members reverted inside arcs'] += n
                changed_files.append((ci, rel, 'arc-' + how)); touched = True
                continue
            if top not in REVERT_DIRS[title]:
                rep['kept outside revert dirs'] += 1; continue
            if r['bucket'] == 'same':
                rep['already identical to JP'] += 1; continue
            dst = os.path.join(work, rel.replace('/', os.sep))
            if kind == 'upd':
                pu = os.path.join(jp_upd, rel.replace('/', os.sep))
                pc = os.path.join(jp_cart, rel.replace('/', os.sep))
                if os.path.exists(pu):
                    shutil.copyfile(pu, dst); rep['replaced from JP update'] += 1; changed_files.append((ci, rel, 'jp_upd'))
                elif os.path.exists(pc):
                    os.remove(dst); rep['deleted (cartridge copy will be used)'] += 1; changed_files.append((ci, rel, 'deleted'))
                else:
                    rep['UNMATCHED kept'] += 1; unmatched.append((ci, rel))
                    continue
            else:
                pj = os.path.join(jp_dlc, rel.replace('/', os.sep))
                if os.path.exists(pj):
                    shutil.copyfile(pj, dst); rep['replaced from JP DLC'] += 1; changed_files.append((ci, rel, 'jp_dlc'))
                else:
                    rep['UNMATCHED kept'] += 1; unmatched.append((ci, rel))
                    continue
            touched = True
        if not touched:
            continue
        # prune directories emptied by deletions
        for dp, dn, fn in os.walk(work, topdown=False):
            if not dn and not fn and dp != work:
                os.rmdir(dp)
        new_romfs = repack(work, os.path.join(HERE, '_work', title, 'c%d.romfs' % ci))
        blob = c.contents[ci]
        if not (blob[0x18F] & 4):
            # AES-encrypted CFA (DLC): make it NoCrypto first, exactly as the RHDN DLC patch
            # output is built (nocrypto_cia.py); that form installed and ran on the console today.
            sys.path.insert(0, os.path.join(ROOT, '_rhdn_work'))
            from nocrypto_cia import nocrypto
            import tempfile
            td = tempfile.mkdtemp(prefix='nc_')
            blob, why = nocrypto(blob, ci, td)
            shutil.rmtree(td)
            rep['content made NoCrypto before splice'] += 1
        new_blob = ncch.splice(blob, new_romfs)
        ok, _ = ncch.verify(new_blob); assert ok
        replace[ci] = new_blob
    out = os.path.join(OUT, OUT_NAME[title])
    c.write(out, replace=replace, version=c.version())
    chk = Cia(out)
    assert chk.version() == c.version() and chk.count == c.count
    # read-back: every replaced content's romfs equals the work romfs
    for ci, blob in replace.items():
        assert romfs_of_ncch(chk.contents[ci]) == romfs_of_ncch(blob)
    sha = h(out)
    lines = ['%s -> %s' % (title, OUT_NAME[title]), '  version %d.%d.%d, %d contents, %d bytes, sha256 %s' % (chk.version() + (chk.count, os.path.getsize(out), sha)),
             '  revert dirs: %s' % sorted(REVERT_DIRS[title])]
    for k, v in sorted(rep.items()):
        lines.append('  %-40s %6d' % (k, v))
    lines.append('  contents rebuilt: %s' % sorted(replace))
    if unmatched:
        lines.append('  UNMATCHED (kept as shipped, need a decision):')
        for ci, rel in unmatched:
            lines.append('    c%d %s' % (ci, rel))
    io.open(os.path.join(OUT, title + '_report.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    io.open(os.path.join(OUT, title + '_changes.json'), 'w', encoding='utf-8').write(json.dumps(changed_files, indent=0))
    print('\n'.join(lines))


def main():
    rows = json.load(io.open(os.path.join(HERE, 'inventory.json'), encoding='utf-8'))
    want = sys.argv[1:] or ['TGAA1_upd', 'TGAA2_upd', 'TGAA1_dlc', 'TGAA2_dlc']
    for t in want:
        build(t, [r for r in rows if r['title'] == t])


if __name__ == '__main__':
    main()

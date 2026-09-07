# -*- coding: utf-8 -*-
"""Step 1 of the Japanese-voice build: extract every romfs involved and classify our files.

For each of our four shipped titles (TGAA1/TGAA2 update and DLC, Final/_CURRENT) this extracts the
romfs of every content, plus the Japanese sources: the cartridge (decrypted .cci, partition 0), the
official Japanese update CIA (decrypted) and the Japanese DLC CIA (decrypted). Then, per our title
and content, every file is compared against its Japanese counterpart (update: JP update romfs first,
then cartridge romfs; DLC: same content index in the JP DLC) and bucketed:

  same      identical to the JP file
  changed   exists in JP, differs
  new       no JP counterpart in any source

Output: jpvoice/_trees/<label>/<content>/  (extracted romfs directories)
        jpvoice/inventory.json             (per file: title, content, relpath, bucket, size, jp source)
        jpvoice/inventory_summary.txt      (counts per title/content/top-level dir/bucket)

Nothing is modified. Usage: python jpvoice\inventory.py
"""
import os, sys, io, json, hashlib, struct, subprocess, shutil, collections
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
from cia import Cia
T3 = os.path.join(ROOT, '3dstool', '3dstool.exe')
HERE = os.path.join(ROOT, 'jpvoice')
TREES = os.path.join(HERE, '_trees')
os.makedirs(TREES, exist_ok=True)

SRC = {
    'TGAA1': dict(
        ours_upd=os.path.join(ROOT, r'Final\_CURRENT\TGAA1-base-3.2.2.cia'),
        ours_dlc=os.path.join(ROOT, r'Final\_CURRENT\TGAA1-DLC-1.0.10.cia'),
        jp_cart=os.path.join(ROOT, r'_sources\TGAA1 - Base-decrypted.cci'),
        jp_upd=os.path.join(ROOT, r'_sources\TGAA1-Official-Jap (Patch)-decrypted.cia'),
        jp_dlc=os.path.join(ROOT, r'_sources\TGAA1-Official-Jap (DLC)-decrypted.cia')),
    'TGAA2': dict(
        ours_upd=os.path.join(ROOT, r'Final\_CURRENT\TGAA2-base-1.0.15.cia'),
        ours_dlc=os.path.join(ROOT, r'Final\_CURRENT\TGAA2-DLC-1.0.9.cia'),
        jp_cart=os.path.join(ROOT, r'_sources\DGS2 - Base-decrypted.cci'),
        jp_upd=os.path.join(ROOT, r'_sources\DGS2-Official-Jap-v2.3.3 (Patch)-decrypted.cia'),
        jp_dlc=os.path.join(ROOT, r'_sources\DGS2-Jap-DLC (DLC)-decrypted.cia')),
}


def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('FAILED: %s\n%s%s' % (' '.join(a), r.stdout, r.stderr))


def romfs_of_ncch(blob):
    """Return the PLAINTEXT romfs bytes of an NCCH (CXI or CFA) blob, or None if it has none.
    A NoCrypto NCCH is sliced directly. An AES-encrypted CFA (Capcom's DLC contents, and our own
    shipped DLC CIAs, which keep that layer) goes through 3dstool, which decrypts with the retail
    keys; the result has the size the header declares."""
    assert blob[0x100:0x104] == b'NCCH'
    off = struct.unpack_from('<I', blob, 0x1B0)[0] * 0x200
    sz = struct.unpack_from('<I', blob, 0x1B4)[0] * 0x200
    if not sz:
        return None
    flags = blob[0x188:0x190]
    if flags[7] & 4:
        return blob[off:off + sz]
    assert flags[7] & 0x20 == 0, 'seed crypto NCCH, not handled'
    exh = struct.unpack_from('<I', blob, 0x180)[0]
    assert exh == 0, 'encrypted CXI, not handled (only CFA)'
    import tempfile
    td = tempfile.mkdtemp(prefix='ncch_')
    src = os.path.join(td, 'c.cfa'); rom = os.path.join(td, 'c.romfs')
    open(src, 'wb').write(blob)
    run(T3, '-xtf', 'cfa', src, '--romfs', rom)
    raw = open(rom, 'rb').read()
    shutil.rmtree(td)
    assert len(raw) == sz, 'decrypted romfs %d != header %d' % (len(raw), sz)
    return raw


def extract_romfs(raw, outdir):
    if os.path.isdir(outdir) and os.path.exists(os.path.join(outdir, '.done')):
        return
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(os.path.dirname(outdir), exist_ok=True)
    tmp = outdir + '.romfs'
    open(tmp, 'wb').write(raw)
    run(T3, '-xtf', 'romfs', tmp, '--romfs-dir', outdir)
    os.remove(tmp)
    open(os.path.join(outdir, '.done'), 'w').write('ok')


def extract_cia(path, label):
    c = Cia(path)
    out = []
    for i, blob in enumerate(c.contents):
        raw = romfs_of_ncch(blob)
        d = os.path.join(TREES, label, 'c%d' % i)
        if raw is None:
            out.append((i, None)); continue
        extract_romfs(raw, d)
        out.append((i, d))
    return out


def extract_cci_p0(path, label):
    d = open(path, 'rb')
    head = d.read(0x200)
    off, ln = struct.unpack_from('<II', head, 0x120)
    d.seek(off * 0x200)
    blob = d.read(ln * 0x200)
    raw = romfs_of_ncch(blob)
    outdir = os.path.join(TREES, label, 'c0')
    extract_romfs(raw, outdir)
    return outdir


def walk(d):
    out = {}
    for dp, dn, fn in os.walk(d):
        for f in fn:
            if f == '.done':
                continue
            p = os.path.join(dp, f)
            out[os.path.relpath(p, d).replace(os.sep, '/')] = p
    return out


def h(p):
    s = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            s.update(b)
    return s.hexdigest()


def main():
    rows = []
    summary = collections.OrderedDict()
    for g, s in SRC.items():
        print(g, 'extracting ...', flush=True)
        cart = walk(extract_cci_p0(s['jp_cart'], g + '_jp_cart'))
        jpu = extract_cia(s['jp_upd'], g + '_jp_upd')
        jpu_tree = walk(jpu[0][1]) if jpu[0][1] else {}
        ours_u = extract_cia(s['ours_upd'], g + '_ours_upd')
        ours_tree = walk(ours_u[0][1])
        print('  cart %d files, jp update %d files, our update %d files' % (len(cart), len(jpu_tree), len(ours_tree)), flush=True)
        for rel, p in sorted(ours_tree.items()):
            src = None
            if rel in jpu_tree:
                src = ('jp_upd', jpu_tree[rel])
            elif rel in cart:
                src = ('jp_cart', cart[rel])
            if src is None:
                b = 'new'
            else:
                b = 'same' if h(p) == h(src[1]) else 'changed'
            rows.append(dict(title=g + '_upd', content=0, rel=rel, bucket=b, size=os.path.getsize(p), jp=src[0] if src else None))
        # DLC: content by content against the JP DLC
        jpd = extract_cia(s['jp_dlc'], g + '_jp_dlc')
        oud = extract_cia(s['ours_dlc'], g + '_ours_dlc')
        assert len(jpd) == len(oud), 'DLC content count differs %d vs %d' % (len(jpd), len(oud))
        for (i, jd), (_, od) in zip(jpd, oud):
            if od is None:
                continue
            jt = walk(jd) if jd else {}
            ot = walk(od)
            for rel, p in sorted(ot.items()):
                if rel in jt:
                    b = 'same' if h(p) == h(jt[rel]) else 'changed'; src = 'jp_dlc'
                else:
                    b = 'new'; src = None
                rows.append(dict(title=g + '_dlc', content=i, rel=rel, bucket=b, size=os.path.getsize(p), jp=src))
        print('  done', flush=True)
    json.dump(rows, io.open(os.path.join(HERE, 'inventory.json'), 'w', encoding='utf-8'), indent=0)
    # summary: title / content / top dir / bucket
    cnt = collections.Counter()
    for r in rows:
        top = r['rel'].split('/')[0] if '/' in r['rel'] else '(root)'
        cnt[(r['title'], r['content'], top, r['bucket'])] += 1
    lines = ['%-10s %2s %-22s %-8s %6s' % ('title', 'c', 'top dir', 'bucket', 'files')]
    for k in sorted(cnt):
        lines.append('%-10s %2d %-22s %-8s %6d' % (k[0], k[1], k[2], k[3], cnt[k]))
    txt = '\n'.join(lines)
    io.open(os.path.join(HERE, 'inventory_summary.txt'), 'w', encoding='utf-8').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()

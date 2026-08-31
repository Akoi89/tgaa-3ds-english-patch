# -*- coding: utf-8 -*-
"""Pad every replaced DLC stream file back to Capcom's original data_size.

Found by live A/B in Azahar (2026-08-28): issue 0's gallery player goes SILENT
when a stream file is smaller than the original, and other issues' players cut
off. Files LARGER than the original play fine. So: where our re-encode shrank a
file, extend the ADPCM region with zero frames (DSP decodes them as silence) to
the original data_size; where it grew, leave it alone. File length is always
104 + data_size, so padded files come out byte-length identical to Capcom's.
"""
import os, sys, glob, struct, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import mca

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, 'dlc_story_audit') if os.path.basename(ROOT)!='dlc_story_audit' else ROOT

def orig_dir(i):
    for pre in ('f','o'):
        d = os.path.join('video_inject','work','%s%d_dir'%(pre,i),'sound')
        if os.path.isdir(d): return d
    return None

def main(root, apply=False):
    fixed = kept = 0
    for i in range(2, 11):
        cur = os.path.join(root, 'idx%d_dir'%i, 'sound')
        od = orig_dir(i)
        if not (os.path.isdir(cur) and od): continue
        for p in sorted(glob.glob(os.path.join(cur, '*.mca'))):
            base = os.path.basename(p)
            op = os.path.join(od, base)
            if not os.path.exists(op): continue
            ours = open(p,'rb').read()
            orig = open(op,'rb').read()
            if ours == orig:            # untouched Capcom file
                continue
            ho = mca.parse_bytes(ours); hc = mca.parse_bytes(orig)
            if ho['data_size'] >= hc['data_size']:
                kept += 1
                continue
            d = bytearray(ours[:ho['data_off']])
            struct.pack_into('<I', d, 0x20, hc['data_size'])
            d += ho['adpcm'] + bytes(hc['data_size'] - len(ho['adpcm']))
            # some originals carry trailing bytes after the data region; keep them
            tail = orig[hc['data_off'] + hc['data_size']:]
            d += tail
            if len(d) != len(orig):
                print('  NOTE idx%d %s: new %d vs orig %d (data_off %d/%d tail %d)'
                      % (i, base, len(d), len(orig), ho['data_off'], hc['data_off'], len(tail)))
            chk = mca.parse_bytes(bytes(d))
            assert chk['samples'] == ho['samples'] and chk['data_size'] == hc['data_size']
            print('  idx%-2d %-24s %7d -> %7d bytes (padded to original)'%(i,base,len(ours),len(d)))
            if apply:
                open(p,'wb').write(bytes(d))
            fixed += 1
    print('\n%d padded, %d already >= original%s'%(fixed,kept,'' if apply else '  (dry run)'))

if __name__ == '__main__':
    main(sys.argv[1], '--apply' in sys.argv)

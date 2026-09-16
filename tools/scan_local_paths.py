# -*- coding: utf-8 -*-
"""Scan release artifacts (xdeltas, zips and every zip member) for local paths or user names.
    python _rhdn_work/scan_local_paths.py <file or glob> ...
Exit 1 if anything is found. The xdelta header (where a source/target path would sit) is at the start,
so the first 4 MB of each file/member is enough; zips are also scanned in full member by member."""
import glob
import sys
import zipfile

BAD = [b'G:\\', b'G:/', b'Claude', b'Shadow', b'C:\\Users', b'C:/Users', b'TGAA 1-2', b'AppData']


def hits(data):
    return [b.decode() for b in BAD if b in data]


found = 0
for pat in sys.argv[1:]:
    for f in glob.glob(pat):
        h = hits(open(f, 'rb').read(4 * 1024 * 1024))
        print('%-48s %s' % (f, 'LOCAL: ' + ', '.join(h) if h else 'clean'))
        found += bool(h)
        if f.lower().endswith('.zip'):
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    h = hits(z.read(n))
                    print('    %-44s %s' % (n, 'LOCAL: ' + ', '.join(h) if h else 'clean'))
                    found += bool(h)
sys.exit(1 if found else 0)

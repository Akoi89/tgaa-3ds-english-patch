# -*- coding: utf-8 -*-
"""Prove a pad32 build from the CIA: extract it, diff against the previous extraction, and
check that every changed stream is the old stream plus zero bytes to a 32-byte multiple.

    python verify_pad32.py <name> <cia> <old_extraction_root> [allowed extra differing file ...]
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '..', 'dlc_ai_voice'))
sys.path.insert(0, os.environ.get('DGS2TOOL', os.path.join(ROOT, '..', 'dlc_icons', 'tgaa2-en-patch')))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import extract_shipped as es
from dgs2tool.arc import parse_arc


def files(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for fn in fs:
            p = os.path.join(dp, fn)
            out[os.path.relpath(p, root).replace('\\', '/')] = p
    return out


def streams_of(path):
    if path.endswith('.mca'):
        d = open(path, 'rb').read()
        return {'': d} if d[:4] == b'MADP' else {}
    if path.endswith('.arc'):
        try:
            return {e.name: e.data for e in parse_arc(open(path, 'rb').read())['entries'] if e.data[:4] == b'MADP'}
        except Exception:
            return {}
    return {}


def main():
    name, cia, old = sys.argv[1:4]
    allowed = set(sys.argv[4:])
    es.extract(name, cia)
    new = os.path.join(es.OUT, name)
    a, b = files(old), files(new)
    assert set(a) == set(b), 'file sets differ: %s' % sorted(set(a) ^ set(b))[:10]
    changed = [k for k in sorted(a) if open(a[k], 'rb').read() != open(b[k], 'rb').read()]
    n_pad = 0
    bad = []
    for k in changed:
        so, sn = streams_of(a[k]), streams_of(b[k])
        if not sn:
            if k not in allowed:
                bad.append(k)
            continue
        # non-audio members of an arc must be identical; audio members = old + zeros
        if k.endswith('.arc'):
            eo = {e.name: e.data for e in parse_arc(open(a[k], 'rb').read())['entries']}
            en = {e.name: e.data for e in parse_arc(open(b[k], 'rb').read())['entries']}
            assert set(eo) == set(en)
            for n in eo:
                if eo[n][:4] != b'MADP':
                    assert eo[n] == en[n], 'non-audio member changed: %s in %s' % (n, k)
        for n in so:
            o, nw = so[n], sn[n]
            if nw == o:
                continue
            ok = len(nw) % 32 == 0 and nw[:len(o)] == o and nw[len(o):] == bytes(len(nw) - len(o)) and len(nw) - len(o) < 32
            if ok:
                n_pad += 1
            else:
                bad.append('%s::%s' % (k, n))
    print('%d files changed, %d streams = old + zero trailer, %d unexpected: %s' % (len(changed), n_pad, len(bad), bad[:10]))
    assert not bad
    print('OK  md5 %s' % hashlib.md5(open(cia, 'rb').read()).hexdigest())


if __name__ == '__main__':
    main()

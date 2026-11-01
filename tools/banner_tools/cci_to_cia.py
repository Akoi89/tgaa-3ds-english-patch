"""Build an installable CIA from a decrypted CCI with makerom (all partitions,
same indices, title version copied from the reference CIA's TMD).

    python cci_to_cia.py <in.cci> <reference.cia> <out.cia> [--makerom PATH]

makerom must be v0.16 (Batch CIA 3DS Decryptor ships it). Newer makerom
(v0.17 and up) ignores -ver, so a TGAA2 CIA would come out with title
version 0.0.0 instead of 0.2.0. Give its path with --makerom or with the
environment variable TGAA_MAKEROM. No makerom is included in this repository.
"""
import os, struct, subprocess, sys, tempfile

MU = 0x200


def find_makerom(argv):
    path = None
    if '--makerom' in argv:
        i = argv.index('--makerom')
        if i + 1 >= len(argv):
            sys.exit('--makerom needs a path')
        path = argv[i + 1]
        del argv[i:i + 2]
    path = path or os.environ.get('TGAA_MAKEROM')
    if not path or not os.path.isfile(path):
        sys.exit('makerom v0.16 not found (%s). Pass --makerom PATH or set TGAA_MAKEROM. '
                 'It must be v0.16, the one in Batch CIA 3DS Decryptor: newer makerom ignores -ver.'
                 % (path or 'no path given'))
    return path


def tmd_version(cia):
    d = open(cia, 'rb').read(0x20); hdr, typ, ver, cert, tik, tmd, meta = struct.unpack_from('<IHHIIII', d, 0)
    a64 = lambda x: (x + 63) // 64 * 64
    f = open(cia, 'rb'); f.seek(a64(hdr) + a64(cert) + a64(tik) + 0x1DC); return struct.unpack('>H', f.read(2))[0]


def main(cci, ref, out, makerom):
    h = open(cci, 'rb').read(0x200); assert h[0x100:0x104] == b'NCSD'
    parts = [(i,) + struct.unpack_from('<II', h, 0x120 + i * 8) for i in range(8)]
    parts = [(i, o * MU, n * MU) for i, o, n in parts if n]
    ver = tmd_version(ref)
    tmp = tempfile.mkdtemp(prefix='cci2cia_', dir=os.path.dirname(os.path.abspath(out)))
    args = [makerom, '-f', 'cia', '-o', out, '-ver', str(ver), '-ignoresign']
    f = open(cci, 'rb')
    for i, o, n in parts:
        p = os.path.join(tmp, 'p%d.bin' % i); f.seek(o)
        with open(p, 'wb') as w:
            left = n
            while left:
                b = f.read(min(left, 1 << 26)); w.write(b); left -= len(b)
        args += ['-content', '%s:%d:%d' % (p, i, i)]
        print('partition %d: %d bytes' % (i, n))
    print('makerom -ver %d ...' % ver)
    r = subprocess.run(args, capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-2000:])
    for i, o, n in parts:
        os.remove(os.path.join(tmp, 'p%d.bin' % i))
    os.rmdir(tmp)
    print('exit', r.returncode, 'wrote', out, os.path.getsize(out) if os.path.exists(out) else 'MISSING')
    return r.returncode


if __name__ == '__main__':
    argv = sys.argv[1:]
    mk = find_makerom(argv)
    if len(argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(argv[0], argv[1], argv[2], mk))

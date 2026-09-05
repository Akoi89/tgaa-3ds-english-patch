"""Build an installable CIA from a decrypted CCI with makerom (all partitions,
same indices, title version copied from the reference CIA's TMD).

    python cci_to_cia.py <in.cci> <reference.cia> <out.cia>
"""
import os, struct, subprocess, sys, tempfile

MU = 0x200
here = os.path.dirname(os.path.abspath(__file__))
MAKEROM = os.path.join(here, '..', 'makerom.exe')


def tmd_version(cia):
    d = open(cia, 'rb').read(0x20); hdr, typ, ver, cert, tik, tmd, meta = struct.unpack_from('<IHHIIII', d, 0)
    a64 = lambda x: (x + 63) // 64 * 64
    f = open(cia, 'rb'); f.seek(a64(hdr) + a64(cert) + a64(tik) + 0x1DC); return struct.unpack('>H', f.read(2))[0]


def main(cci, ref, out):
    h = open(cci, 'rb').read(0x200); assert h[0x100:0x104] == b'NCSD'
    parts = [(i,) + struct.unpack_from('<II', h, 0x120 + i * 8) for i in range(8)]
    parts = [(i, o * MU, n * MU) for i, o, n in parts if n]
    ver = tmd_version(ref)
    tmp = tempfile.mkdtemp(prefix='cci2cia_', dir=os.path.dirname(os.path.abspath(out)))
    args = [MAKEROM, '-f', 'cia', '-o', out, '-ver', str(ver), '-ignoresign']
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
    sys.exit(main(*sys.argv[1:4]))

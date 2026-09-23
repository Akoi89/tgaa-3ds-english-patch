"""Dump MADP header fields (samples, loop_start, loop_end, data_size vs actual) for
shout entries in a set of arc files. Usage: shout_headers.py <arc or dir>..."""
import os, sys, struct
TGAA_ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the project folder')
ROOT = os.path.join(TGAA_ROOT, 'dlc_story_audit')
sys.path.insert(0, ROOT + '/arc_tools')
import arc

def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for dp, _, fs in os.walk(p):
                for fn in sorted(fs):
                    if fn.endswith('.arc'):
                        yield os.path.join(dp, fn)
        else:
            yield p

only = [a for a in sys.argv[1:] if a.startswith('--only=')]
only = only[0][7:] if only else None
for p in walk([a for a in sys.argv[1:] if not a.startswith('--')]):
    try:
        _, _, es, _ = arc.entries(p)
    except AssertionError:
        continue
    for e in es:
        d = arc.decomp(e)
        if d[:4] != b'MADP':
            continue
        short = e['name'].split('\\')[-1]
        if only and only not in short:
            continue
        samples, rate = struct.unpack_from('<II', d, 0x0C)
        ls, le = struct.unpack_from('<II', d, 0x14)
        hdr_end, dsize = struct.unpack_from('<II', d, 0x1C)
        doff = struct.unpack_from('<I', d, 0x34)[0]
        hdr = d[0x24:0x38].hex()
        print('%-16s %-30s smp=%6d rate=%5d loop=%6d..%6d hdr_end=%3d doff=%3d dsize=%6d len=%6d exp=%6d %s' % (
            os.path.basename(p)[:16], short[:30], samples, rate, ls, le, hdr_end, doff, dsize, len(d),
            doff + (-(-samples // 14)) * 8, 'LOOP>SMP' if le > samples else ''))

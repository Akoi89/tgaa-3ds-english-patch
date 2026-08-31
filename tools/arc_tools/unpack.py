import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arc import entries, decomp

src, out = sys.argv[1], sys.argv[2]
ver, count, es, _ = entries(src)
os.makedirs(out, exist_ok=True)
for e in es:
    rel = e["name"].replace(chr(92), "/")
    p = os.path.join(out, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p + ".bin", "wb").write(decomp(e))
print("unpacked %d entries -> %s" % (count, out))

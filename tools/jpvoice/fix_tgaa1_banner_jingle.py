# -*- coding: utf-8 -*-
"""Step 7: a TGAA1 banner image for the Japanese-voice set whose HOME menu jingle is the Japanese one.

The v1.5 TGAA1 banner patch (banner_tools/_out/TGAA1-Base-enbanner.cci) carries the English
picture, the English title strings in the icon, AND an English jingle (the CBMD's CWAV block
differs from the cartridge's; TGAA2's does not). For the JAP Dub set the jingle goes back:
  composed banner = English banner's CBMD up to its CWAV offset (header + 13 LZ11 models,
                    untouched) + the cartridge banner's CWAV block, verbatim
  spliced into the English enbanner .cci with banner_tools/exefs_banner.py (keeps the icon
  with its English title text; ExeFS size unchanged; NCCH hash chain repaired)
Then: base xdelta (cartridge -> this image) with build_base's full proof (romfs, exheader,
logo, manual identical to the cartridge), and a CIA of it for the NAS folder.
Outputs: jpvoice/_out/TGAA1-Base-enbanner-jpjingle.{cci,cia}, jpvoice/_patches/TGAA1-v1.5-jpvoice-base.xdelta
"""
import os, sys, io, struct, hashlib, shutil, subprocess
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the project folder')
sys.path.insert(0, os.path.join(ROOT, 'banner_tools')); sys.path.insert(0, os.path.join(ROOT, '_rhdn_work'))
import exefs_banner
import build_rhdn_patches_v15 as B
from build_rhdn_patches import digest
OUT = os.path.join(ROOT, 'jpvoice', '_out'); PJ = os.path.join(ROOT, 'jpvoice', '_patches'); WORK = os.path.join(ROOT, 'jpvoice', '_pwork')
JP_CCI = os.path.join(ROOT, r'_sources\TGAA1 - Base-decrypted.cci')
EN_CCI = os.path.join(ROOT, r'banner_tools\_out\TGAA1-Base-enbanner.cci')
EN_CIA = os.path.join(ROOT, r'banner_tools\_out\TGAA1-Base-enbanner.cia')
NEW_CCI = os.path.join(OUT, 'TGAA1-Base-enbanner-jpjingle.cci'); NEW_CIA = os.path.join(OUT, 'TGAA1-Base-enbanner-jpjingle.cia')
MU = 0x200


def exefs_files(cci):
    d = open(cci, 'rb')
    head = d.read(0x200); p0 = struct.unpack_from('<I', head, 0x120)[0] * MU
    d.seek(p0); n = d.read(0x200)
    ex = struct.unpack_from('<I', n, 0x1A0)[0] * MU
    d.seek(p0 + ex); hdr = d.read(0x200)
    out = {}
    for i in range(10):
        name = hdr[i * 16:i * 16 + 8].rstrip(b'\0'); o, s = struct.unpack_from('<II', hdr, i * 16 + 8)
        if name:
            d.seek(p0 + ex + 0x200 + o); out[name] = d.read(s)
    return out


jp = exefs_files(JP_CCI); en = exefs_files(EN_CCI)
bj, be = jp[b'banner'], en[b'banner']
assert bj[:4] == b'CBMD' and be[:4] == b'CBMD'
cj = struct.unpack_from('<I', bj, 0x84)[0]; ce = struct.unpack_from('<I', be, 0x84)[0]
wav_jp = bj[cj:]; wav_en = be[ce:]
assert wav_jp[:4] == b'CWAV' and wav_en[:4] == b'CWAV', (wav_jp[:4], wav_en[:4])
assert ce % 0x20 == 0
composed = be[:ce] + wav_jp
print('EN banner %d B (CWAV %d B) -> composed %d B with the JP CWAV (%d B); models region kept: %s' % (len(be), len(wav_en), len(composed), len(wav_jp), composed[:ce] == be[:ce]))
tmpb = os.path.join(OUT, '_banner_jpjingle.bin'); open(tmpb, 'wb').write(composed)
exefs_banner.main(EN_CCI, tmpb, NEW_CCI)
os.remove(tmpb)
new = exefs_files(NEW_CCI)
assert new[b'banner'] == composed, 'banner read back differs'
for k in new:
    if k != b'banner':
        assert new[k] == en[k], 'exefs file %r changed' % k
assert new[b'icon'] == en[b'icon'] and new[b'icon'] != jp[b'icon'], 'icon must stay the English-title one'
print('spliced: banner == composed, every other ExeFS file (icon with English title, code) identical to the English banner image')

# base xdelta with the full proof, into the jpvoice patch folder
os.makedirs(WORK, exist_ok=True)
cfg = dict(B.GAMES['TGAA1'], enbanner=os.path.relpath(NEW_CCI, ROOT))
TAGJ = os.environ.get('TGAA_JTAG', 'v1.8a-jpvoice')

# STRICT THREE-SOURCE PROOF (added 2026-09-23, REWORK): build_base()'s own internal proof
# only perturbs the 44-byte card seed (SEED_OFF/SEED_LEN), not the whole 0x0-0x4000 NCSD
# header it scrubs at encode time. That gap let a real defect through: a bisected review found
# TGAA1-v1.9-jpvoice-base.xdelta fails "target window checksum mismatch" when byte 0x3FFF (the
# LAST byte of the scrubbed header) is randomised. printhdrs showed why: this build's window 0
# copy started at source offset 0x3FFF (one byte INSIDE the scrubbed region) where the matching
# English base patch's window 0 starts cleanly at 0x4000; xdelta occasionally finds a coincidental
# 1-byte match against the random scrub bytes and extends a copy into the "armored" zone. The fix
# is not a different method (build_base already scrubs 0-0x4000 with -a -A, the same tolerant
# method as the English patches); it is a stronger, mandatory post-build check, retried with a
# fresh random scrub (build_base draws new os.urandom bytes every call) until it truly passes.
SECOND_DECRYPT = os.path.join(ROOT, r'_sources\TGAA1-Official-Jap-decrypted.cci')


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def _decode(xd_path, src_path, out_path):
    r = subprocess.run([B.XD, '-d', '-f', '-B', B.BIG, '-s', src_path, xd_path, out_path], capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr[-300:]
    return _sha(out_path), ''


def strict_three_source_proof(xd_path, target_sha, real_src):
    """Decode xd_path against (1) the real cartridge dump, (2) a copy of it with the WHOLE
    0x0-0x4000 NCSD header randomised, (3) an independent second decrypt of the same cartridge.
    All three must reproduce target_sha byte for byte."""
    chk = os.path.join(WORK, '_strict_check.cci')
    got, err = _decode(xd_path, real_src, chk)
    if got != target_sha:
        return False, 'real dump (%s)' % real_src, err
    randcopy = os.path.join(WORK, '_strict_randheader.cci')
    shutil.copyfile(real_src, randcopy)
    with open(randcopy, 'r+b') as f:
        f.seek(0); f.write(os.urandom(0x4000))
    got, err = _decode(xd_path, randcopy, chk)
    os.remove(randcopy)
    if got != target_sha:
        return False, 'whole-header-randomised copy', err
    got, err = _decode(xd_path, SECOND_DECRYPT, chk)
    if got != target_sha:
        return False, 'second decrypt (%s)' % SECOND_DECRYPT, err
    os.remove(chk)
    return True, None, None


MAX_TRIES = 25
for attempt in range(1, MAX_TRIES + 1):
    src, tgt, xd = B.build_base('TGAA1', cfg, WORK, PJ, TAGJ)
    target_sha = _sha(tgt)
    ok, bad_src, err = strict_three_source_proof(xd, target_sha, src)
    if ok:
        print('TGAA1 base: STRICT three-source proof passed on attempt %d of %d (real dump, '
              'whole-header-randomised copy, second decrypt %s)' % (attempt, MAX_TRIES, os.path.basename(SECOND_DECRYPT)))
        break
    print('TGAA1 base: strict proof FAILED on attempt %d against %s (%s); retrying with a fresh random scrub' % (attempt, bad_src, err.strip()))
else:
    raise SystemExit('TGAA1 base xdelta failed the strict three-source proof after %d attempts' % MAX_TRIES)

rows = []
for label, p in (('source', src), ('result', tgt), ('patch', xd)):
    s, c, n = digest(p); rows.append(('TGAA1', 'base', label, os.path.basename(p), n, c, s))
    print('TGAA1 base   %-6s %-44s %12d crc32=%s sha256=%s' % (label, os.path.basename(p), n, c, s))
with open(os.path.join(PJ, 'HASHES_%s.txt' % TAGJ), 'a') as f:
    for r in rows:
        f.write('%s\t%s\t%s\t%s\t%d\t%s\t%s\n' % r)

# CIA for the NAS folder, version copied from the English banner CIA
r = subprocess.run([sys.executable, os.path.join(ROOT, 'banner_tools', 'cci_to_cia.py'), NEW_CCI, EN_CIA, NEW_CIA], capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-400:])
assert r.returncode == 0 and os.path.exists(NEW_CIA)
sys.path.insert(0, os.path.join(ROOT, 'testimony_pipeline'))
from cia import Cia
a, b = Cia(NEW_CIA), Cia(EN_CIA)
print('new banner CIA: version %s (English banner CIA %s), %d contents, %d bytes, sha256 %s' % (a.version(), b.version(), a.count, os.path.getsize(NEW_CIA), hashlib.sha256(open(NEW_CIA, 'rb').read()).hexdigest()))

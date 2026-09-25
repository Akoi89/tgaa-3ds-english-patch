# -*- coding: utf-8 -*-
r"""Find a release's files in its own folder instead of hand-edited paths.

Before 2026-09-24 build_rhdn_patches_v15.py and make_zips_v15.py carried the update/DLC file
names and version stamps as constants that were repointed by hand every release. That is how
a stale file can ride into a zip (the same class of mix-up that brought the v1.6 DLC icon
sheet back in v1.8b). Now both scripts take --tag and read everything from one folder:

  Final\_new\<tag>\   (default)   or   --release <folder>   (e.g. Final\_CURRENT)

Rules, each one fails loudly:
  * the folder name is <tag>, or the folder holds PROMOTE_<tag>_LOG.txt (that is _CURRENT
    after promotion); anything else is refused
  * exactly one {g}-base-X.Y.Z.cia, one {g}-DLC-X.Y.Z.cia and one {g}-EN-DLC-<vtag>.cia per game
    at the top level (subfolders such as _stale_packaging_* are never looked at)
  * every CIA's TMD title ID is the right game and the right kind (update 0004000E, DLC 0004008C)
The version stamps (ENG 3.3.5, DLC 1.0.17) come from those file names, and the DLC's own tag
comes from the EN-DLC file (a release that did not touch a DLC carries the older file, e.g.
v1.9b shipped TGAA1-EN-DLC-v1.9.cia).
"""
import hashlib
import json
import os
import re
import struct

TIDS = {'TGAA1': '0014AD00', 'TGAA2': '001AE200'}


def _one(folder, rx, what):
    hits = [f for f in os.listdir(folder) if re.fullmatch(rx, f) and os.path.isfile(os.path.join(folder, f))]
    if len(hits) != 1:
        raise SystemExit('release_set: expected exactly one %s in %s, found %s' % (what, folder, hits or 'none'))
    return hits[0], re.fullmatch(rx, hits[0]).group(1)


def cia_title(path):
    """(title id hex, declared title version as 'a.b.c') from the CIA's TMD. The declared
    version is NOT the file-name version (the micro field is 4 bits, and the names diverged),
    so it is only printed, never compared."""
    a64 = lambda x: (x + 63) // 64 * 64  # noqa: E731
    try:
        with open(path, 'rb') as f:
            hsz, _, _, csz, tsz, msz = struct.unpack('<IHHIII', f.read(0x14))
            tmd = a64(hsz) + a64(csz) + a64(tsz)
            f.seek(tmd)
            sig = struct.unpack('>I', f.read(4))[0]
            body = {0x10003: 0x240, 0x10004: 0x140, 0x10005: 0x80}[sig]
            f.seek(tmd + body + 0x4C)
            tid = f.read(8)
            f.seek(tmd + body + 0x9C)
            v = struct.unpack('>H', f.read(2))[0]
    except (struct.error, KeyError, OSError) as e:
        raise SystemExit('release_set: cannot read the TMD of %s (%r)' % (path, e))
    return tid.hex().upper(), '%d.%d.%d' % (v >> 10, (v >> 4) & 0x3F, v & 0xF)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def resolve(root, tag, release=None):
    """root = project root (the folder holding Final). Returns {game: {...}} with absolute paths."""
    if not re.fullmatch(r'v\d+(\.\d+)*[a-z]?', tag or ''):
        raise SystemExit('release_set: --tag must look like v1.9c, got %r' % tag)
    folder = os.path.abspath(release if release and os.path.isabs(release)
                             else os.path.join(root, release or os.path.join('Final', '_new', tag)))
    if not os.path.isdir(folder):
        raise SystemExit('release_set: no release folder %s' % folder)
    name = os.path.basename(folder)
    if name != tag:
        # a promoted folder (_CURRENT) must hold exactly one promote log and it must be this tag,
        # so a log left behind by an older promotion cannot vouch for newer files
        logs = [f for f in os.listdir(folder) if re.fullmatch(r'PROMOTE_.+_LOG\.txt', f)
                and os.path.isfile(os.path.join(folder, f))]
        if logs != ['PROMOTE_%s_LOG.txt' % tag]:
            raise SystemExit('release_set: %s is not named %s and its promote logs are %s, not exactly '
                             'PROMOTE_%s_LOG.txt; refusing to build %s from it' % (folder, tag, logs or 'none', tag, tag))
    out = {}
    for g, tid in TIDS.items():
        upd, uver = _one(folder, r'%s-base-(\d+\.\d+\.\d+)\.cia' % g, '%s-base-X.Y.Z.cia' % g)
        dlc, dver = _one(folder, r'%s-DLC-(\d+\.\d+\.\d+)\.cia' % g, '%s-DLC-X.Y.Z.cia' % g)
        endlc, dtag = _one(folder, r'%s-EN-DLC-(v\d+(?:\.\d+)*[a-z]?)\.cia' % g, '%s-EN-DLC-<tag>.cia' % g)
        declared = {}
        for fn, kind in ((upd, '0004000E'), (dlc, '0004008C'), (endlc, '0004008C')):
            got, declared[fn] = cia_title(os.path.join(folder, fn))
            if got != kind + tid:
                raise SystemExit('release_set: %s declares title %s, expected %s' % (fn, got, kind + tid))
        out[g] = dict(update=os.path.join(folder, upd), dlc=os.path.join(folder, dlc),
                      en_dlc=os.path.join(folder, endlc), ver='ENG ' + uver, upd=upd,
                      dlc_stamp='DLC ' + dver, dlc_tag=dtag, tid=tid,
                      tmd_versions=[declared[upd], declared[dlc]])
    return folder, out


def describe(folder, games):
    print('release folder:', folder)
    for g, m in games.items():
        print('  %s  %s (%s, TMD %s)  %s (%s, TMD %s)  %s' % (
            g, m['upd'], m['ver'], m['tmd_versions'][0], os.path.basename(m['dlc']), m['dlc_stamp'],
            m['tmd_versions'][1], os.path.basename(m['en_dlc'])))


def write_manifest(path, tag, folder, games):
    """Record what was built, with hashes, so make_zips_v15.py packs exactly this set."""
    man = dict(tag=tag, folder=folder, games={})
    for g, m in games.items():
        man['games'][g] = dict(m, update_sha256=sha256(m['update']), en_dlc_sha256=sha256(m['en_dlc']))
    with open(path, 'w') as f:
        json.dump(man, f, indent=1)
    return man


if __name__ == '__main__':
    import sys
    r = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    describe(*resolve(r, sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))

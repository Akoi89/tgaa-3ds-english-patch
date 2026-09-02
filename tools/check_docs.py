# -*- coding: utf-8 -*-
"""Fail the build when the docs name a CIA that no longer exists.

    python check_docs.py            # check
    python check_docs.py --release  # also check the live GitHub release body

Four times in a row a push shipped documentation pointing at deleted or
superseded files: the README's install table, `zip_README.txt`, the v1.0 release
notes, and CONTINUE_HERE.md. Every one had the same cause -- a version number
living in prose that nothing verifies -- and every one was caught by eye, once
after the release had been public for a day.

The release notes case was the damaging one. They told testers the title screen
should read a version that no correct install produces, so a working install
looked like a failed one. Docs that lie about filenames generate false bug
reports, which cost more than the bug would have.

What counts as a defect here: a CIA named in a doc that is neither present in the
build directory nor attached to the release. Names that are historical by
intent -- a superseded build being discussed as history -- go in ALLOW.
"""
import os
import argparse
import glob
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.environ.get('TGAA_ROOT', os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
BUILDS = os.environ.get('TGAA_BUILDS', os.path.join(ROOT, 'Final', '_new'))
REPO = os.environ.get('TGAA_REPO', 'Akoi89/tgaa-3ds-english-patch')
DOCS = [os.path.join(ROOT, 'public_repo', 'README.md'),
        os.path.join(ROOT, 'CONTINUE_HERE.md'),
        # The Reddit drafts are gitignored, but they name CIAs and are aimed
        # at a public audience, so they go stale exactly like the README did
        # -- one shipped a filename that had been deleted two builds earlier.
        os.path.join(ROOT, 'public_repo', 'reddit_post.md'),
        os.path.join(ROOT, 'public_repo', 'reddit_post_3dspiracy.md')]

CIA = re.compile(r'[A-Za-z0-9_.-]+\.cia')
# A doc may legitimately discuss superseded builds -- CONTINUE_HERE.md carries a
# provenance table saying which working tree produced which historical CIA, and
# rewriting those names to current ones would destroy the record rather than fix
# it. Such a region is marked, and skipped:
#     <!-- check_docs: historical -->  ...  <!-- check_docs: end -->
HIST = re.compile(r'<!--\s*check_docs:\s*historical\s*-->.*?'
                  r'(?:<!--\s*check_docs:\s*end\s*-->|\Z)', re.DOTALL)
# The Japanese originals the user supplies, and the placeholder in a shell
# example. Neither is ours to ship and neither tracks a version.
ALLOW = {'Base.cia', 'file.cia', 'dlc.cia', 'TGAA1 - Base.cia', 'TGAA2 - Base.cia'}


def current():
    """Filenames that actually exist to be installed."""
    return set(os.path.basename(p) for p in glob.glob(os.path.join(BUILDS, '*.cia')))


def released():
    try:
        out = subprocess.run(
            ['gh', 'release', 'view', os.environ.get('TGAA_RELEASE_TAG', 'v1.1'), '--repo', REPO, '--json',
             'assets,body'], capture_output=True, text=True, timeout=60)
        if out.returncode:
            return None, None
        d = json.loads(out.stdout)
        return set(a['name'] for a in d['assets']), d.get('body', '')
    except Exception:
        return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release', action='store_true',
                    help='also read the live release body (needs gh)')
    a = ap.parse_args()

    built = current()
    print('  builds in %s' % os.path.relpath(BUILDS, ROOT))
    for n in sorted(built):
        print('     %s' % n)

    assets, body = (None, None)
    if a.release:
        assets, body = released()
        if assets is None:
            print('  WARNING: could not read the release; skipping that check')
        else:
            print('  release assets: %d' % len(assets))

    valid = set(built) | (assets or set())
    bad = 0

    sources = [(p, open(p, encoding='utf-8').read()) for p in DOCS
               if os.path.exists(p)]
    if body:
        sources.append(('<live release body>', body))

    for path, text in sources:
        names = sorted(set(CIA.findall(HIST.sub('', text))) - ALLOW)
        stale = [n for n in names if n not in valid]
        label = path if path.startswith('<') else os.path.relpath(path, ROOT)
        print('\n  %s : %d CIA name(s), %d stale' % (label, len(names), len(stale)))
        for n in stale:
            print('     STALE  %s' % n)
            bad += 1

    # THE CHECK THAT MATTERS: the release serving an OLDER build than the one
    # sitting in the build directory. Every name can be individually valid --
    # the README honestly documents a real asset -- while the combination hands
    # testers new base + old DLC. That is the live defect this whole gate exists
    # for, and name-matching alone cannot see it.
    if assets:
        part = re.compile(r'(TGAA[12]-(?:base|DLC))-(\d+)\.(\d+)\.(\d+)(-[A-Za-z0-9-]+)?\.cia')
        def key(n):
            m = part.match(n)
            return (m.group(1), m.group(5) or '') if m else None
        def ver(n):
            m = part.match(n)
            return tuple(int(m.group(i)) for i in (2, 3, 4)) if m else ()
        shipped = {}
        for n in assets:
            k = key(n)
            if k and ver(n) > ver(shipped.get(k, n)) or (k and k not in shipped):
                shipped[k] = n
        for n in sorted(built):
            k = key(n)
            if k and k in shipped and ver(n) > ver(shipped[k]):
                print('     SUPERSEDED  release serves %s but %s is built'
                      % (shipped[k], n))
                bad += 1

    # the other direction: something shipped that no doc tells anyone about
    if assets:
        doc_text = ' '.join(HIST.sub('', t) for _, t in sources)
        missing = [n for n in sorted(assets) if n not in doc_text]
        for n in missing:
            print('     UNDOCUMENTED (attached to the release, named in no doc)  %s' % n)
            bad += 1

    print('\n  %s' % ('FAIL: %d problem(s)' % bad if bad else 'PASS'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())

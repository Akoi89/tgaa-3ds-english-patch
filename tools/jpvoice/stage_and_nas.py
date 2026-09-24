# -*- coding: utf-8 -*-
"""Step 6: stage the Japanese-voice set in Final/_new/jpvoice and mirror it into the two NAS
'JAP Dub' folders, matching the parent folders' contents (JP base CIA, banner CIA, banner xdelta,
update CIA, DLC CIA) plus the xdelta zip and a README. Every copy is hash-verified.
The DLC CIA placed here is the all-NoCrypto form (the one the DLC xdelta produces; that form
installed and ran on the console today), renamed to the folder convention."""
import os, sys, io, shutil, hashlib
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = os.environ.get('TGAA_ROOT') or sys.exit('set TGAA_ROOT to the project folder')
NAS = os.environ.get('TGAA_NAS') or sys.exit('set TGAA_NAS to the NAS destination folder')
STAGE = os.path.join(ROOT, 'Final', '_CURRENT', 'jpvoice'); os.makedirs(STAGE, exist_ok=True)  # nas_backup.ps1 mirrors this into the NAS 'JAP Dub' folders
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()

# repointed for v1.9 (2026-09-23, REWORK item 3: this was still v1.8a, incl. line 21's base
# xdelta name). TAG/BUILD_DATE drive the readme prose below so the next release only has to
# change these two lines and the SETS dict, not the prose too.
TAG = 'v1.9'
BUILD_DATE = '2026-09-23'
SETS = {
    'TGAA1': dict(parent=os.path.join(NAS, 'The Great Ace Attorney Adventures'),
                  jp_base='TGAA1 - Base.cia', enb_cia=None, enb_xd=None,
                  # the first game's English banner carries an English HOME jingle; the JAP Dub set gets
                  # a banner image with the Japanese jingle instead (fix_tgaa1_banner_jingle.py)
                  extra=[(r'jpvoice\_out\TGAA1-Base-enbanner-jpjingle.cia', 'TGAA1-Base-enbanner-jpjingle.cia'),
                         (r'jpvoice\_patches\TGAA1-v1.9-jpvoice-base.xdelta', 'TGAA1-Base-enbanner-jpjingle.xdelta')],
                  upd=(r'jpvoice\_out\TGAA1-base-3.3.2-jpvoice.cia', 'TGAA1-base-3.3.2-jpvoice.cia'),
                  dlc=(r'jpvoice\_patches\TGAA1-EN-DLC-v1.9-jpvoice.cia', 'TGAA1-DLC-1.0.16-jpvoice.cia'),
                  zip_=(r'jpvoice\_zips\TGAA1-3DS-English-JPvoice-v1.9-xdelta.zip', 'TGAA1-3DS-English-JPvoice-v1.9-xdelta.zip'),
                  stamp='ENG 3.3.2', dlcstamp='DLC 1.0.16'),
    'TGAA2': dict(parent=os.path.join(NAS, 'The Great Ace Attorney 2 Resolve'),
                  jp_base='TGAA2 - Base.cia', enb_cia='TGAA2-Base-enbanner.cia', enb_xd='TGAA2-Base-enbanner.xdelta',
                  upd=(r'jpvoice\_out\TGAA2-base-1.0.17-jpvoice.cia', 'TGAA2-base-1.0.17-jpvoice.cia'),
                  dlc=(r'jpvoice\_patches\TGAA2-EN-DLC-v1.9-jpvoice.cia', 'TGAA2-DLC-1.0.11-jpvoice.cia'),
                  zip_=(r'jpvoice\_zips\TGAA2-3DS-English-JPvoice-v1.9-xdelta.zip', 'TGAA2-3DS-English-JPvoice-v1.9-xdelta.zip'),
                  stamp='ENG 1.0.17', dlcstamp='DLC 1.0.11'),
}


def copy(src, dst):
    if os.path.exists(dst) and sha(dst) == sha(src):
        return 'ok    '
    shutil.copyfile(src, dst)
    assert sha(dst) == sha(src), dst
    return 'copied'


for g, s in SETS.items():
    dst = os.path.join(s['parent'], 'JAP Dub'); os.makedirs(dst, exist_ok=True)
    stage = os.path.join(STAGE, g); os.makedirs(stage, exist_ok=True)
    files = []
    for src, name in [s['upd'], s['dlc'], s['zip_']] + s.get('extra', []):
        src = os.path.join(ROOT, src)
        print(copy(src, os.path.join(stage, name)), 'stage', name)
        files.append((name, os.path.getsize(src), sha(src)))
    if s.get('extra'):
        readme_banner = ["The first game's English banner carries an English HOME menu jingle, so this folder has",
                         'its own banner image and xdelta (-jpjingle): English picture and title, Japanese jingle.',
                         'Files copied from the parent folder: the JP base CIA only.']
    else:
        readme_banner = ['Files here that are NOT audio-specific are copies of the parent folder: the JP base CIA,',
                         'the English-banner base CIA and its xdelta (its jingle is already the Japanese one).']
    readme = ['%s, Japanese voice edition of the %s English patch (built %s)' % (g, TAG, BUILD_DATE), '',
              'Same text, art and layout as the main %s files in the parent folder; ALL audio is' % TAG,
              "Capcom's original Japanese (cartridge and Japanese DLC takes). Same title IDs and the",
              'same version numbers as the main files: install these INSTEAD of them, not as well.',
              'Title screen still reads %s, DLC page %s. This %s form has not been run on a console' % (s['stamp'], s['dlcstamp'], TAG),
              'or in an emulator; every file was checked by an independent re-extraction and comparison instead.', '',
              'Install order: JP base (or the enbanner base), then the -jpvoice update, then the -jpvoice DLC.',
              'The xdelta zip rebuilds the update and DLC from your own decrypted dumps (readme inside).', '',
              ] + readme_banner + ['', 'sha256:']
    for name, n, h in files:
        readme.append('  %-48s %12d  %s' % (name, n, h))
    io.open(os.path.join(stage, 'README.txt'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(readme) + '\n')
    # the parent-folder copies (JP base, and for TGAA2 the banner CIA + xdelta) are staged too, so the
    # staged folder is the complete JAP Dub set and nas_backup.ps1 can mirror it file for file
    for name in (s['jp_base'], s['enb_cia'], s['enb_xd']):
        if name:
            print(copy(os.path.join(s['parent'], name), os.path.join(stage, name)), 'stage', name)
    # (2026-09-23: removed a one-off cleanup that deleted two English-jingle banner files from the
    # NAS JAP Dub folder. They were already gone, and nothing here should delete from the NAS.)
    for name in os.listdir(stage):
        print(copy(os.path.join(stage, name), os.path.join(dst, name)), 'nas  ', name)
    print(g, 'NAS JAP Dub now holds:', sorted(os.listdir(dst)))

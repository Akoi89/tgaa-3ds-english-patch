# -*- coding: utf-8 -*-
"""Step 6: stage the Japanese-voice set in Final/_new/jpvoice and mirror it into the two NAS
'JAP Dub' folders, matching the parent folders' contents (JP base CIA, banner CIA, banner xdelta,
update CIA, DLC CIA) plus the xdelta zip and a README. Every copy is hash-verified.
The DLC CIA placed here is the all-NoCrypto form (the one the DLC xdelta produces; that form
installed and ran on the console today), renamed to the folder convention."""
import os, sys, io, shutil, hashlib
if not getattr(sys.stdout, '_utf8_wrapped', False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'); sys.stdout._utf8_wrapped = True
ROOT = r'G:\Claude\TGAA 1-2'
NAS = r'Z:\Main Files\Games\Emulators and ROMs\DS-DSi-3DS\3DS Games\hshop backup\Extras\Translated Games\The Great Ace Attorney Chronicles'
STAGE = os.path.join(ROOT, 'Final', '_CURRENT', 'jpvoice'); os.makedirs(STAGE, exist_ok=True)  # nas_backup.ps1 mirrors this into the NAS 'JAP Dub' folders
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()

SETS = {
    'TGAA1': dict(parent=os.path.join(NAS, 'The Great Ace Attorney Adventures'),
                  jp_base='TGAA1 - Base.cia', enb_cia=None, enb_xd=None,
                  # the first game's English banner carries an English HOME jingle; the JAP Dub set gets
                  # a banner image with the Japanese jingle instead (fix_tgaa1_banner_jingle.py)
                  extra=[(r'jpvoice\_out\TGAA1-Base-enbanner-jpjingle.cia', 'TGAA1-Base-enbanner-jpjingle.cia'),
                         (r'jpvoice\_patches\TGAA1-v1.5-jpvoice-base.xdelta', 'TGAA1-Base-enbanner-jpjingle.xdelta')],
                  upd=(r'jpvoice\_out\TGAA1-base-3.2.2-jpvoice.cia', 'TGAA1-base-3.2.2-jpvoice.cia'),
                  dlc=(r'jpvoice\_patches\TGAA1-v1.5-jpvoice-DLC.cia', 'TGAA1-DLC-1.0.10-jpvoice.cia'),
                  zip_=(r'jpvoice\_zips\TGAA1-3DS-English-JPvoice-v1.5-xdelta.zip', 'TGAA1-3DS-English-JPvoice-v1.5-xdelta.zip'),
                  stamp='ENG 3.2.2', dlcstamp='DLC 1.0.10'),
    'TGAA2': dict(parent=os.path.join(NAS, 'The Great Ace Attorney 2 Resolve'),
                  jp_base='TGAA2 - Base.cia', enb_cia='TGAA2-Base-enbanner.cia', enb_xd='TGAA2-Base-enbanner.xdelta',
                  upd=(r'jpvoice\_out\TGAA2-base-1.0.15-jpvoice.cia', 'TGAA2-base-1.0.15-jpvoice.cia'),
                  dlc=(r'jpvoice\_patches\TGAA2-v1.5-jpvoice-DLC.cia', 'TGAA2-DLC-1.0.9-jpvoice.cia'),
                  zip_=(r'jpvoice\_zips\TGAA2-3DS-English-JPvoice-v1.5-xdelta.zip', 'TGAA2-3DS-English-JPvoice-v1.5-xdelta.zip'),
                  stamp='ENG 1.0.15', dlcstamp='DLC 1.0.9'),
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
    readme = ['%s, Japanese voice edition of the v1.5 English patch (built 2026-09-06)' % g, '',
              'Same text, art and layout as the main v1.5 files in the parent folder; ALL audio is',
              "Capcom's original Japanese (cartridge and Japanese DLC takes). Same title IDs and the",
              'same version numbers as the main files: install these INSTEAD of them, not as well.',
              'Title screen still reads %s, DLC page %s. Installed and run by the author,' % (s['stamp'], s['dlcstamp']),
              'both games with their DLC (2026-09-06).', '',
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
    # the earlier pass copied the English-jingle banner files into TGAA1's JAP Dub folder; retire them
    for stale in ('TGAA1-Base-enbanner.cia', 'TGAA1-Base-enbanner.xdelta') if s.get('extra') else ():
        p = os.path.join(dst, stale)
        if os.path.exists(p):
            os.remove(p); print('removed', stale, '(English jingle) from the NAS JAP Dub folder')
    for name in os.listdir(stage):
        print(copy(os.path.join(stage, name), os.path.join(dst, name)), 'nas  ', name)
    print(g, 'NAS JAP Dub now holds:', sorted(os.listdir(dst)))

# -*- coding: utf-8 -*-
"""Gather Capcom's English recordings of Kazuma and Hosonaga into one folder.

Nothing here is modified or shipped. It is the reference material a voice tool
needs, plus the evidence for the claim that no English "Take that" exists:

  reference/shouts/    the four English shouts these two characters DO have,
                       decoded to plain 16-bit wav (see msadpcm.py)
  reference/kurae/     the three English "Take that"s Capcom DID record, for
                       other characters -- the delivery and length to match
  reference/asg_lines/ Kazuma's English story lines, copied as .ogg (a .sngw
                       is a plain Ogg Vorbis stream, renamed)
  reference/hms_lines/ the same for Hosonaga

Set TGAAC_STEAM to the Chronicles install directory (the one containing
nativeDX11x64) if it is not the copy inside this project.

    python extract_reference.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

import msadpcm

STEAM = os.environ.get('TGAAC_STEAM') or os.path.join(ROOT, 'TGAAC Steam')
SE = os.path.join(STEAM, 'nativeDX11x64', 'sound', 'se')
VOICE = os.path.join(STEAM, 'nativeDX11x64', 'sound', 'stream', 'voice', 'wav')
OUT = os.path.join(HERE, 'reference')

# The two characters that need a "Take that", and every English shout they have.
OURS = ['chr100_asg', 'chr160_asg', 'chr010_hms']
# Capcom's own English "Take that", for reference on delivery and length.
KURAE = ['chr000_nhd', 'chr032_sst', 'chr101_mkt']


def find_xsew(stem):
    """Locate one _eng.xsew by filename, wherever its se folder is."""
    for dirpath, _, files in os.walk(SE):
        for fn in files:
            if fn == stem:
                return os.path.join(dirpath, fn)
    return None


def dump_shouts(prefixes, types, subdir):
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    n = 0
    for pre in prefixes:
        for t in types:
            stem = '%s_v_%s_eng.xsew' % (pre, t)
            src = find_xsew(stem)
            if not src:
                print('   MISSING  %s' % stem)
                continue
            pcm, rate = msadpcm.decode(src)
            out = os.path.join(d, stem.replace('.xsew', '.wav'))
            msadpcm.write_wav(out, pcm, rate)
            print('   %-34s %.3fs  %d Hz' % (os.path.basename(out), len(pcm) / rate, rate))
            n += 1
    return n


def copy_lines(tag, subdir):
    """Chronicles' .sngw story voices are plain Ogg Vorbis; copy as .ogg."""
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    n = 0
    if not os.path.isdir(VOICE):
        print('   no stream/voice/wav at %s' % VOICE)
        return 0
    for fn in sorted(os.listdir(VOICE)):
        if not fn.endswith('_%s_eng.sngw' % tag):
            continue
        src = os.path.join(VOICE, fn)
        if open(src, 'rb').read(4) != b'OggS':
            print('   SKIP (not Ogg)  %s' % fn)
            continue
        shutil.copyfile(src, os.path.join(d, fn[:-5] + '.ogg'))
        n += 1
    return n


def main():
    if not os.path.isdir(SE):
        raise SystemExit('Chronicles not found at %s -- set TGAAC_STEAM' % STEAM)
    os.makedirs(OUT, exist_ok=True)

    print('English shouts these characters DO have:')
    a = dump_shouts(OURS, ['igiari', 'matta'], 'shouts')
    print('\nEnglish "Take that", the characters Capcom did record:')
    b = dump_shouts(KURAE, ['kurae'], 'kurae')

    print('\nStory lines:')
    for tag, sub in (('asg', 'asg_lines'), ('hms', 'hms_lines')):
        n = copy_lines(tag, sub)
        print('   %-4s %3d English lines -> reference/%s' % (tag, n, sub))

    # State the negative result explicitly rather than leaving it implied.
    missing = [p for p in OURS + ['chr010_hms']
               if not find_xsew('%s_v_kurae_eng.xsew' % p)]
    print('\nNo English "Take that" recording exists for: %s'
          % ', '.join(sorted(set(missing))))
    print('%d shouts and %d reference "Take that"s written to %s' % (a, b, OUT))


if __name__ == '__main__':
    main()

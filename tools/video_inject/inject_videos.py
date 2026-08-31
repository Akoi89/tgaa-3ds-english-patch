# -*- coding: utf-8 -*-
"""Replace the 11 DLC commentary videos with subtitled .moflex versions.

Drop the encoded files in moflex_in/ using the ORIGINAL names
(aoc00_movie_00.moflex etc), then run this. It rebuilds the affected DLC
contents and the CIA; contents may grow, which the builder handles.

    python inject_videos.py <src_cia> <out_cia>

Verified target spec, read off Capcom's own files with ffmpeg:
    video  mobiclip, yuv420p, 400x240, 29.97 fps (30000/1001)
    audio  adpcm_ima_moflex, stereo
           22050 Hz  -- all except the two below
           32000 Hz  -- aoc00_movie_01 and aoc01_movie_00 ONLY
"""
import sys, os, subprocess, shutil, glob

T = os.environ.get('THREEDSTOOL', '3dstool.exe')   # set THREEDSTOOL if not on PATH
FF = os.environ.get('FFMPEG', 'ffmpeg')   # set FFMPEG if it is not on PATH

# movie -> DLC content index (issue N lives in idx N+2)
MOVIES = {
    'aoc00_movie_00': 2, 'aoc00_movie_01': 2, 'aoc01_movie_00': 3,
    'aoc02_movie_00': 4, 'aoc03_movie_00': 5, 'aoc04_movie_00': 6,
    'aoc05_movie_00': 7, 'aoc06_movie_00': 8, 'aoc07_movie_00': 9,
    'aoc07_movie_01': 9, 'aoc08_movie_00': 10,
}
EXPECT_HZ = {'aoc00_movie_01': 32000, 'aoc01_movie_00': 32000}


def probe(path):
    out = subprocess.run([FF, '-i', path], capture_output=True, text=True).stderr
    return out


def verify(name, path):
    """Refuse to inject anything that does not match Capcom's spec."""
    info = probe(path)
    ok = True
    if '400x240' not in info:
        print('   !! %s is not 400x240' % name); ok = False
    if '29.97 fps' not in info:
        print('   !! %s is not 29.97 fps' % name); ok = False
    hz = EXPECT_HZ.get(name, 22050)
    if '%d Hz' % hz not in info:
        print('   !! %s audio should be %d Hz' % (name, hz)); ok = False
    if 'mobiclip' not in info.lower():
        print('   !! %s is not a mobiclip stream' % name); ok = False
    return ok


def main(src, out):
    here = os.path.dirname(os.path.abspath(__file__))
    inbox = os.path.join(here, 'moflex_in')
    have = {os.path.splitext(os.path.basename(p))[0]: p
            for p in glob.glob(os.path.join(inbox, '*.moflex'))}
    if not have:
        print('put the encoded .moflex files in %s first' % inbox); return 1

    print('checking %d file(s) against Capcom spec...' % len(have))
    if not all(verify(n, p) for n, p in sorted(have.items())):
        print('refusing to build -- fix the flagged files first'); return 1
    print('   all good\n')

    unknown = set(have) - set(MOVIES)
    if unknown:
        print('unexpected names (must match the originals): %s' % unknown); return 1

    work = os.path.join(here, 'work'); shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'cia_extract'))
    idxs = sorted({MOVIES[n] for n in have})
    print('rebuilding DLC contents %s' % idxs)
    # split -> extract -> swap -> repack  (same path as every other build)
    subprocess.run([sys.executable,
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'cia_extract', 'split_v17.py'),
                    src, os.path.join(work, 'split')], check=True)
    rep = os.path.join(work, 'rep'); os.makedirs(rep)
    for i in idxs:
        ncch = os.path.join(work, 'split', 'idx%d.ncch' % i)
        hdr = os.path.join(work, 'idx%d.hdr' % i)
        open(hdr, 'wb').write(open(ncch, 'rb').read(512))
        romfs = os.path.join(work, 'idx%d.romfs' % i)
        rdir = os.path.join(work, 'idx%d_dir' % i)
        subprocess.run([T, '-x', '-t', 'cfa', '--header', os.devnull,
                        '-f', ncch, '--romfs', romfs], capture_output=True)
        subprocess.run([T, '-x', '-t', 'romfs', '-f', romfs,
                        '--romfs-dir', rdir], capture_output=True)
        for n, p in have.items():
            if MOVIES[n] != i:
                continue
            dst = os.path.join(rdir, 'movie', n + '.moflex')
            if not os.path.exists(dst):
                print('   !! %s not found in idx%d' % (dst, i)); return 1
            before = os.path.getsize(dst)
            shutil.copyfile(p, dst)
            print('   idx%-2d %s  %d -> %d bytes' % (i, n, before, os.path.getsize(p)))
        nr = os.path.join(rep, 'idx%d.romfs' % i)
        subprocess.run([T, '-c', '-t', 'romfs', '-f', nr,
                        '--romfs-dir', rdir], capture_output=True)
        subprocess.run([T, '-c', '-t', 'cfa', '--header', hdr, '--romfs', nr,
                        '-f', os.path.join(rep, 'idx%d.ncch' % i),
                        '--not-encrypt'], capture_output=True)
    print('\ncontents rebuilt into %s' % rep)
    print('now run a build_vNN.py with SRC=%s OUT=%s REPLACE_DIR=%s' % (src, out, rep))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else main('', ''))

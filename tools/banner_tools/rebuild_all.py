"""One-shot rebuild of both English HOME banners: compose -> banner -> CCI (banner+icon)
-> CIA -> xdelta -> verify by extraction. Usage: python rebuild_all.py <stretch1[,stretch2]> [scale]"""
import os, subprocess, sys, hashlib, filecmp, shutil

R = os.environ.get('TGAA_ROOT', r'G:\Claude\TGAA 1-2'); BT = os.path.join(R, 'banner_tools'); HB = os.path.join(R, r'dlc_story_audit\_validation\home_banner')
OUT = os.path.join(BT, '_out'); CT = os.path.join(R, 'ctrtool.exe'); XD = os.path.join(R, r'patches\xdelta3.exe')
st = sys.argv[1].split(','); stretches = {'tgaa1': st[0], 'tgaa2': st[-1]}; scale = sys.argv[2] if len(sys.argv) > 2 else '1.0'
G = [('tgaa1', 'TGAA1', 'TGAA1_-_Base_base_banner.bin', r'_sources\TGAA1 - Base-decrypted.cci', 'The_Great_Ace_Attorney_1_logo_English.webp', 'TGAA1 - Base.cia'),
     ('tgaa2', 'TGAA2', 'DGS2_-_Base-_base_banner.bin', r'_sources\DGS2 - Base-decrypted.cci', 'The_Great_Ace_Attorney_2_logo_English.webp', 'TGAA2 - Base.cia')]


def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True, cwd=BT); print(r.stdout.strip());
    if r.returncode: print(r.stderr); raise SystemExit('FAILED: ' + ' '.join(a))


for g, GG, ban, cci, logo, ref in G:
    tex = os.path.join(HB, g + '_new_tex.png'); nb = os.path.join(HB, g + '_banner_new.bin'); ic = os.path.join(HB, g + '_icon_new.bin')
    run('python', 'compose_logo.py', os.path.join(HB, g + '_dump', 'model0__256x256_f13.png'), os.path.join(R, r'dlc_story_audit\logo_src', logo), tex, '--stretch', stretches[g], '--scale', scale)
    run('python', 'banner_build2.py', os.path.join(HB, ban), tex, nb)
    snd = os.path.join(HB, g + '_banner_sound_clip.wav')   # optional English shout for the jingle slot
    if os.path.exists(snd):
        run('python', 'banner_cwav_dsp.py', nb, snd, nb + '.snd', '--match-level', '--keep-length'); shutil.move(nb + '.snd', nb)
    src = os.path.join(R, cci); occi = os.path.join(OUT, GG + '-Base-enbanner.cci'); ocia = os.path.join(OUT, GG + '-Base-enbanner.cia'); oxd = os.path.join(OUT, GG + '-Base-enbanner.xdelta')
    run('python', 'exefs_splice.py', src, occi, 'banner=' + nb, 'icon=' + ic)
    run('python', 'cci_to_cia.py', occi, os.path.join(R, r'Final\_CURRENT', ref), ocia)
    run(XD, '-e', '-f', '-s', src, occi, oxd)
    # verify: banner+icon out of the CIA
    tmp = os.path.join(OUT, '_v_' + GG); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    subprocess.run([CT, '--contents=' + os.path.join(tmp, 'c'), ocia], capture_output=True)
    c0 = [f for f in os.listdir(tmp) if f.startswith('c.0000')][0]
    subprocess.run([CT, '--exefsdir=' + os.path.join(tmp, 'x'), os.path.join(tmp, c0)], capture_output=True)
    ok = filecmp.cmp(os.path.join(tmp, 'x', 'banner.bin'), nb, False) and filecmp.cmp(os.path.join(tmp, 'x', 'icon.bin'), ic, False)
    shutil.rmtree(tmp)
    print(GG, 'CIA banner+icon extract-and-compare:', ok, '| md5 cia', hashlib.md5(open(ocia, 'rb').read()).hexdigest(), 'xdelta', hashlib.md5(open(oxd, 'rb').read()).hexdigest(), os.path.getsize(oxd))
    assert ok

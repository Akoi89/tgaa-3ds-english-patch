# -*- coding: utf-8 -*-
"""Every GMD in a romfs, INCLUDING the ones inside .arc archives.

Court Record captions, cast profiles and episode titles do not sit loose in
romfs -- they are zlib members of archive/*.arc. Any audit that only globs
*.gmd silently misses all of them, which is most of the caption work this
project did.

Keys are 'path/in/romfs.arc::member/name.gmd' for archive members and the plain
relative path for loose files, so the two kinds compare cleanly across trees.
"""
import os
import glob
import re
import sys

sys.path.insert(0, os.environ.get('DGS2TOOL', '.'))
from dgs2tool.arc import parse_arc
from dgs2tool.gmd import parse_gmd_bytes

TAG = re.compile(r'<[^>]*>')
RUBY = re.compile(r'<RUBY>\s*<RB>(.*?)</RB>\s*<RT>.*?</RT>\s*</RUBY>', re.S)


def _norm(p, root):
    return os.path.relpath(p, root).replace(os.sep, '/')


def gmds(root):
    """{key: {label: text}} for every GMD in the tree, loose or archived."""
    out = {}
    for p in glob.glob(os.path.join(root, '**', '*.gmd'), recursive=True):
        try:
            g = parse_gmd_bytes(open(p, 'rb').read())
        except Exception:
            continue
        out[_norm(p, root)] = {(e['label'] or '#%d' % i): e['text']
                               for i, e in enumerate(g['entries'])}
    for p in glob.glob(os.path.join(root, '**', '*.arc'), recursive=True):
        try:
            a = parse_arc(open(p, 'rb').read())
        except Exception:
            continue
        for e in a['entries']:
            name = e.name if e.name.endswith('.gmd') else e.name + '.gmd'
            if not e.name.endswith('.gmd') and 'gmd' not in (e.name.split('.')[-1] if '.' in e.name else ''):
                # arc members are stored without extension; sniff the magic
                if not (e.data[:4] in (b'GMD\0', b'\0DMG')):
                    continue
            try:
                g = parse_gmd_bytes(e.data)
            except Exception:
                continue
            key = '%s::%s' % (_norm(p, root), name)
            out[key] = {(x['label'] or '#%d' % i): x['text']
                        for i, x in enumerate(g['entries'])}
    return out


def visible(t):
    """Drawn characters only: ruby folded to its base, every tag removed."""
    return ' '.join(TAG.sub('', RUBY.sub(lambda m: m.group(1), t)).split())


if __name__ == '__main__':
    for root in sys.argv[1:]:
        g = gmds(root)
        arc = sum(1 for k in g if '::' in k)
        print('  %-28s %4d gmd  (%d loose, %d inside arcs)  %6d entries'
              % (root, len(g), len(g) - arc, arc, sum(len(v) for v in g.values())))

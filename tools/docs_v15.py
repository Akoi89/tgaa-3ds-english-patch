# -*- coding: utf-8 -*-
"""Apply the v1.5 edits to README.md and the 3dspiracy Reddit draft, byte-level, exact-match.
Every replacement must match exactly once or the script stops. Run, then diff with git."""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, 'public_repo', 'README.md')
REDDIT = os.path.join(ROOT, 'public_repo', 'reddit_post_3dspiracy.md')

README_EDITS = [
    # playtesters box
    ("""> **Both games install and boot on real 3DS hardware**, confirmed 30 August 2026, and one
> tester has since played both of the second game's DLC stories start to finish on an
> original 3DS. Every fix in v1.4's DLC came out of that run, and the thread is in
> [issue #1](../../issues/1). Everything else was tested in an emulator, which is more
> permissive than a console in at least one known way.
>
> What is still untested is *playing the base games* on hardware. 32 of the first game's
> shouts, the jury verdicts and the pressing voices, have never been heard by anyone, in
> any build, on any platform.""",
     """> **Both games install and boot on real 3DS hardware**, confirmed 30 August 2026, and one
> tester has since played both of the second game's DLC stories start to finish on an
> original 3DS, twice. Every fix in v1.4's DLC came out of that run, and the thread is in
> [issue #1](../../issues/1). Their fourth report, and a recording made on a second
> console, found the cause of the pop at the end of shouts (v1.5, below): a defect that
> had been in every English voice clip in both base games since the first release and
> that an emulator cannot reproduce. Everything else was tested in an emulator, which is
> now known to be more permissive than a console in two ways.
>
> What is still untested is *playing the base games* on hardware. 32 of the first game's
> shouts, the jury verdicts and the pressing voices, have never been heard by anyone, in
> any build, on any platform."""),
    # install table
    ("""| 2 | `TGAA1-base-3.2.1.cia` / `TGAA2-base-1.0.14.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.8.cia` | the DLC |""",
     """| 2 | `TGAA1-base-3.2.2.cia` / `TGAA2-base-1.0.15.cia` | the update |
| 3 | `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia` | the DLC |"""),
    # install-took table
    ("""| TGAA1 title screen, top right | `ENG 3.2.1` |
| TGAA1 DLC, Episode 0 magazine cover | `DLC 1.0.8`, top left (not re-stamped for 1.0.10) |
| TGAA2 title screen, top right | `ENG 1.0.14` |
| TGAA2 DLC, costume pack banner | `DLC 1.0.8`, bottom right |

An older number on a title screen means an older update is still installed: `ENG 1.0.19`
or `ENG 1.0.13` is v1.3 (`ENG 3.2.0` was a staging build that never shipped), `ENG 1.0.18` or `ENG 1.0.12` is v1.1 or v1.2, `ENG 1.0.2` or
`ENG 1.0.4` is v1.0. An older number on a DLC page means the old DLC is still installed.""",
     """| TGAA1 title screen, top right | `ENG 3.2.2` |
| TGAA1 DLC, Episode 0 magazine cover | `DLC 1.0.10`, top left |
| TGAA2 title screen, top right | `ENG 1.0.15` |
| TGAA2 DLC, costume pack banner | `DLC 1.0.9`, bottom right |

An older number on a title screen means an older update is still installed: `ENG 3.2.0`
or `ENG 1.0.14` is v1.4 (v1.4's first game showed `3.2.0` although the file was named
3.2.1; that is fixed), `ENG 1.0.19` or `ENG 1.0.13` is v1.3, `ENG 1.0.18` or `ENG 1.0.12`
is v1.1 or v1.2, `ENG 1.0.2` or `ENG 1.0.4` is v1.0. An older number on a DLC page means
the old DLC is still installed.

**If your console is online and offers you an update for the second game, decline it.**
That is Capcom's own Japanese update, which the console offered because it carried a
higher version number than this patch did. From v1.5 the patch outranks it and the offer
stops; on an older build, accepting it would install the Japanese update over the English
one."""),
    # version paragraph
    ("""The first game's number jumped from `1.0.19` to `3.2.1` in v1.4. That is not nineteen
missed releases. The 3DS stores a title version in a field whose last part cannot go
above 15, so `1.0.16` and up were never real versions: the files were named `1.0.x`
while the console was told something else, and the two had drifted apart. From v1.4
the number on the screen, the number in the filename and the number the console
sees are the same number, and it is one that supersedes every earlier build.""",
     """The first game's number jumped from `1.0.19` to `3.2.1` in v1.4. That is not nineteen
missed releases. The 3DS stores a title version in a field whose last part cannot go
above 15, so `1.0.16` and up were never real versions: the files were named `1.0.x`
while the console was told something else, and the two had drifted apart. From v1.4
the first game's number on the screen, in the filename and in the console are the same
number. The second game keeps `1.0.x` on screen and in the filename, but from v1.5 the
console is told `3.0.x`, for the reason in the box above: Capcom's own update for it is
`1.3.0`, and a lower number is what made consoles offer that update over the patch."""),
    # clean edges paragraph -> real cause
    ("""**Clean edges (v1.4).** The hardware tester heard a pop at the end of some shouts in the
second game's DLC. Every clip this project had imported was cut hard at both ends with no
fade, while Capcom's own shouts and the base games' English clips end in about a tenth of a
second of true silence. All 34 DLC shouts in the second game (85 archive entries, since one clip serves several
character archives) now carry a short fade and the same silent tail; the 42 fitted streams in the first game's DLC got the fade in place,
since those cannot grow past their slot. Whether that was the pop is not proven: the
tester's build is the one without it, and the one with it has only been heard on an
emulator, where it is clean.""",
     """**The pop at the end of shouts (found v1.4, fixed v1.5).** The hardware tester heard a
click at the end of some shouts in the second game's DLC. v1.4 gave every imported clip
a fade and a silent tail like Capcom's, which was correct but was not the cause: the
tester still heard it. A recording of the click, made on a second console and lined up
against the clip, put it about ten milliseconds after the clip's last sample, and the
one structural difference left was this: every voice file Capcom ships ends in a zero
trailer that rounds its length to a multiple of 32 bytes, and every clip this project or
senyarom had written was 8 bytes past that boundary with no trailer. A console reads the
last 32-byte unit past the end of the file and plays whatever it finds there. An
emulator reads exact sizes and never hears it. The trailer is now on every replaced
stream: 89 in the second game's DLC, 130 in the second game and 123 in the first, which
means the base games had been clicking on hardware since the first release and nobody
had played them there to know. The first game's DLC was already aligned. A second
recording on the same console, same shout, same spot, shows nothing at the clip's end.
The recording also showed which file the DLC's scripted shouts play: the base game's
copy, not the DLC's own, which is why fixing the DLC alone had changed nothing."""),
    # text table: add the v1.5 rows after the Herlock caption row
    ("""| **1** | profile caption in the second game's DLC that was five lines in a four-line box, so the game shrank it and thin strokes dropped out; condensed to four (v1.4) |""",
     """| **1** | profile caption in the second game's DLC that was five lines in a four-line box, so the game shrank it and thin strokes dropped out; condensed to four (v1.4) |
| **1** | save-slot title in the second game, Episode 1's, the longest of the five, that ran off the slot's right edge on a console; the "Ep. 1:" label is now drawn a step smaller so the title fits at its normal size, and the chapter line under it, which the game was squeezing to fit, now renders one size down and unsquashed. Seen on screen (v1.5) |
| **2** | system messages in the second game, the return-to-title confirmation and its game-over twin, whose longest lines were the two widest of any dialog in the game, so the box squeezed the whole message sideways until the apostrophe vanished; re-broken onto four and three lines, no words changed. Not yet seen on screen, see the status table (v1.5) |"""),
    # status table rows
    ("""| DLC mini-episode shouts, second game | confirmed in play; the v1.4 clean-edge versions heard on an emulator only |
| The second game's DLC, both stories | **played start to finish on an original 3DS** by a tester, on v1.2; every defect found is fixed in v1.4 and none has been re-checked on hardware yet |
| In-game shouts, both games | correct as files, **never heard in context** |""",
     """| DLC mini-episode shouts, second game | confirmed in play on hardware; the v1.5 trailer fix **recorded clean on a console** at the shout that had clicked |
| The second game's DLC, both stories | **played start to finish on an original 3DS** by a tester, on v1.2 and again on v1.4; every text defect found is fixed, most re-checked on hardware by the tester |
| The v1.5 return-to-title re-wrap, second game | proven by measurement; **not yet seen on screen**, the long form of that message did not come up in testing |
| In-game shouts, both games | correct as files; one of the second game's heard clean on a console after the trailer fix, the rest **never heard in context** |"""),
    ("""| Installing and booting on a 3DS | **confirmed on hardware**, both games, v1.0 builds; the second game's v1.2 set was installed and played on hardware by the tester |""",
     """| Installing and booting on a 3DS | **confirmed on hardware**, both games; installing v1.4 over v1.2 with existing files raised no save prompt on the tester's console |"""),
]

REDDIT_EDITS = [
    ("""2. `TGAA1-base-3.2.1.cia` / `TGAA2-base-1.0.14.cia`
3. `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.8.cia`""",
     """2. `TGAA1-base-3.2.2.cia` / `TGAA2-base-1.0.15.cia`
3. `TGAA1-DLC-1.0.10.cia` / `TGAA2-DLC-1.0.9.cia`"""),
    ("""From v1.1 the on-screen versions are real: as of v1.4 the title screens read `ENG 3.2.1` and `ENG 1.0.14`, and the DLC pages read `DLC 1.0.8` on both, the first game's cover not having been re-stamped for 1.0.10.""",
     """From v1.1 the on-screen versions are real: as of v1.5 the title screens read `ENG 3.2.2` and `ENG 1.0.15`, and the DLC pages read `DLC 1.0.10` and `DLC 1.0.9`."""),
]


def apply(path, edits):
    b = open(path, 'rb').read()
    nl = b'\r\n' if b'\r\n' in b[:4000] else b'\n'
    for old, new in edits:
        o = old.replace('\n', '\r\n' if nl == b'\r\n' else '\n').encode('utf-8')
        n = new.replace('\n', '\r\n' if nl == b'\r\n' else '\n').encode('utf-8')
        c = b.count(o)
        if c != 1:
            raise SystemExit('%s: expected exactly one match, found %d for:\n%s' % (os.path.basename(path), c, old[:120]))
        b = b.replace(o, n)
    open(path, 'wb').write(b)
    print('%s: %d edits applied' % (os.path.basename(path), len(edits)))
    for ch in ('—', '–'):
        assert ch.encode('utf-8') not in b, 'dash in ' + path


apply(README, README_EDITS)
apply(REDDIT, REDDIT_EDITS)

THE GREAT ACE ATTORNEY 1 & 2  -  3DS English patch
Capcom's official English text, on the Japanese 3DS releases, including the DLC
================================================================================

Capcom localised both games for The Great Ace Attorney Chronicles in 2021, but
never brought that text back to the 3DS. senyarom's patch does exactly that. This
builds on top of it: it finishes the DLC, which nothing had translated, and fixes
what playing the result turned up.

Everything else is senyarom's work, untouched -- their layout pipeline, their font
handling, their carry of Capcom's script. This is not a replacement for it.


WHAT YOU NEED
--------------------------------------------------------------------------------
Your own copy of the Japanese base games -- Dai Gyakuten Saiban and/or Resolve.
Cartridge or your own dump. They are not distributed here or anywhere else in this
project.

And a 3DS that can install CIAs, or Azahar / Citra.

You do NOT need senyarom's release installed first. These supersede it.


HOW TO INSTALL
--------------------------------------------------------------------------------
Install in this order. It matters -- the update and the DLC both layer on the base
game.

    1.  the Japanese base game        (yours)
    2.  TGAA1-base-1.0.2.cia          TGAA2-base-1.0.2.cia
    3.  TGAA1-DLC-1.0.4.cia           TGAA2-DLC-1.0.3.cia

TGAA2-base-1.0.1-no-credits.cia is a ROLLBACK, not an upgrade. It is the same
build without the 15 English credit cards. Install it only if the credits sequence
misbehaves, and note it predates the menu readability fix.


BACK UP YOUR SAVE FIRST.  THIS ONE MATTERS
--------------------------------------------------------------------------------
Unlike some patches, this one CAN cost you save data, so please do this.

The second game shows a "save data is corrupted" prompt if it finds save data it
does not expect -- which can happen when switching between builds. CONFIRMING THAT
PROMPT WIPES THE SLOTS. If you see it, decline it and say so, rather than pressing
through.

On hardware the save lives on your SD card under the game's title folder. In
Azahar:

    %APPDATA%\AzaharPlus\sdmc\Nintendo 3DS\<32 zeros>\<32 zeros>\title\00040000\
        0014ad00\data\00000001\go_sys.dat      TGAA1
        001ae200\data\00000001\go_sys.dat      TGAA2

Copy those somewhere before you start.


CHECK THE INSTALL ACTUALLY TOOK
--------------------------------------------------------------------------------
Both games print their version on screen, and the filename, the version the
console reads, and the version painted in-game all agree.

    TGAA1 title screen          ENG 1.0.2
    TGAA1 DLC magazine page     DLC 1.0.4       (top left)
    TGAA2 title screen          ENG 1.0.2
    TGAA2 DLC page              DLC 1.0.3       (bottom right of the banner)

If a version on screen does not match the file you installed, the install did not
take. That is a real bug -- say so, and do not play it, because a failed install
looks exactly like a bug in the patch.


THIS IS A TEST BUILD, AND THAT IS NOT FALSE MODESTY
--------------------------------------------------------------------------------
Both games have now been installed and booted on real 3DS hardware -- 30 August
2026. That was the single largest unknown here, and it is closed. Everything else
was tested in an emulator, which is more permissive than a console in at least one
known way.

What nobody has done yet is PLAY it on hardware, start to finish. If you do, you
are covering the part that is still genuinely untested.

32 of the first game's shouts -- the jury verdicts, and the pressing voices --
have never been heard by anyone, in any build. They are expected to be fine, for
reasons that are written down, but expected is not heard.

The second game's credits sequence has never been run by anyone either.

Every real defect this project has had was found by a person looking or listening.
The automated checks passed a build in which one line was silent and another was
cut in half.


WHERE TO REPORT
--------------------------------------------------------------------------------
The tracking thread, where known issues live:

    https://github.com/Akoi89/tgaa-3ds-english-patch/issues/1

A comment wherever you downloaded this works just as well. "Voice cut off in
Episode 3's trial" is a complete report -- you do not need to investigate it, and
you do not need a GitHub account to be useful.


WHAT TO REPORT
--------------------------------------------------------------------------------
Most useful, in order:

 1. ANY VOICE THAT IS SILENT, CUT OFF MID-WORD, OR IN JAPANESE. This is the
    thinnest part of what has been tested. A jury verdict ("Not guilty!") or a
    press that stops part-way is the single most useful thing you can catch.

 2. Anything that fails to load -- a scene, a movie, the credits.

 3. Text that overflows its box, clips, or renders at the wrong SIZE. 42 menu
    strings in the second game were re-tagged to fix unreadable buttons; if
    anything now looks the wrong size, that is a consequence of it.

 4. Anything at all on real hardware, good or bad.

Say which episode and chapter. A photo of the screen beats a description.


PLEASE DON'T REPORT THESE -- THEY ARE KNOWN
--------------------------------------------------------------------------------
 *  The second game's end credits are in Japanese. 75 cards; 15 are English. The
    rest cannot be ported -- the PC release lays them out differently, so they are
    a typesetting job rather than a copy. This is the largest known gap.

 *  Some voice lines sound slightly duller than others. That is deliberate.
    Capcom's English takes run longer than the Japanese ones they replace, and a
    clip larger than its original slot gets cut off mid-word in game. Rather than
    cut words, those clips run at a lower sample rate -- correct pitch and timing,
    less treble. One line is noticeably affected.

 *  Some English lines are shorter than the Japanese ones were. The English
    performance is simply shorter. A line that ends cleanly is complete.

 *  A DLC card on the title screen is blank, in both games. Cosmetic.

 *  "Editor's Notes" behaves like the Picture Book and Theme buttons in the first
    game's DLC. Known, and it affects all three.


IF YOU ALREADY HAVE SENYAROM'S RELEASE
--------------------------------------------------------------------------------
Three of the four builds are also published as xdelta patches against their
release, in TGAA-patches-for-testers.zip on the release page. Be aware that only
one of them saves much:

    TGAA2-update-1.0.2.xdelta      2 MB   instead of 32 MB
    TGAA1-update-1.0.2.xdelta     29 MB   instead of 62 MB
    TGAA2-DLC-1.0.3.xdelta        29 MB   instead of 38 MB

The DLC patch barely beats the download. If you have the bandwidth, just take
the CIAs -- it is the simpler path and there is less to go wrong.

There is no patch for the first game's DLC. Its contents are encrypted and the
audio work shifted every offset inside them, so the delta comes to 310 MB against
a 326 MB target -- it shares almost nothing with the source, and is not a patch in
any useful sense. That one is the CIA or nothing.


CREDITS
--------------------------------------------------------------------------------
senyarom did the hard part. Their patch supplies the layout pipeline, the font
handling and the carry of Capcom's script onto the 3DS builds -- without it none
of this exists. Where Capcom localised the DLC, the text in these builds IS their
carry of Capcom's English, word for word.

    https://github.com/senyarom/tgaa2-en-patch

Scarlet Study made the first playable English 3DS build, years earlier, and it was
used as a reference throughout.

If you want Capcom's translation properly, buy The Great Ace Attorney Chronicles.
It is very good, it is on every current platform, and it is the reason any of this
can exist.

The Great Ace Attorney and Chronicles are (c) Capcom.

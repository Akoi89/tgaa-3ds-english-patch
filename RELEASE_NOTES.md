# Release Notes

This project brings Capcom's official English text, voices and art from the Chronicles
release onto the Japanese 3DS versions of The Great Ace Attorney 1 and 2, including both
games' DLC. It builds on senyarom's earlier fan patch and ships a base patch and a DLC
patch for each game. Entries below are newest first.

## v1.8a

This release does not change either game. It only fixes the patch files for people who
dump their cartridge rather than an installed digital copy. Until now, patching from a
cartridge dump failed with a checksum error, because the patches were comparing bytes in
the file header that a cartridge dump writes slightly differently from a digital dump,
even though none of the actual game code or data differs. The patches now ignore those
harmless header differences. If you already installed v1.8 from a digital dump, you do
not need this release at all. If you patch from a cartridge dump and hit a checksum
mismatch, this is the fix. The optional HOME menu banner patch still expects a digital
dump and was left alone.

## v1.8

This release fixes artwork in the first game's DLC art book that came out blurred in
v1.7. Some pages show the art director's commentary written over a see through panel
laid on top of the artwork. The previous method for removing the Japanese text under
those panels ended up erasing too much of the picture and having a model repaint what
should have been there, which left smears and pale patches. The new method never repaints
anything: it works out what the art underneath actually looks like from the parts that
are not covered in writing, and only fades out what the writing covers. Twenty nine pages
are corrected this way, and the text now sits exactly where Capcom's Japanese text sat.
One page still has a small clipping issue that could not be fixed cleanly. If you are on
v1.7, only the first game's DLC file needs reinstalling.

## v1.7

This release makes the first game's DLC art book, theme gallery and editor's notes
actually open. In every earlier release, including senyarom's original patch, those three
screens loaded for a moment and then dropped you back to the title screen. The cause was
a leftover check in the game's code that these newer screens still triggered even though
older DLC screens had already been patched around it. With that fixed, everything on
those screens is now translated into English for the first time, since Capcom never
localized this DLC content for Chronicles. The DLC list icons were also redrawn using
Capcom's original artwork, since the old fan versions cut off part of each icon. In the
second game's DLC, a smudged sheet of paper on a score sheet was cleaned up. If you are
coming from v1.6, both the first game's update and its DLC changed, and the second game's
DLC changed too; the second game's main update file is unchanged.

## v1.6

This release replaces the "Objection!" style shout graphics in both games with Capcom's
own versions; the old fan made set had left one rotated copy in Japanese that the first
game actually used. Fifteen more textures that Capcom translated for Chronicles, things
like text painted onto costumes and backgrounds, are ported in as well. The second game's
title screen logo, which had regressed to a fan made version in the previous release, is
restored to Capcom's official colored logo. Some behind the scenes cleanup to the patch
files themselves means older patch downloads that failed for other people should now
apply correctly. If you are coming from v1.5, both games' update files changed; the DLC
files are the same as before and do not need reinstalling.

## v1.5

This release fixes a clicking noise at the end of replaced voice lines on real hardware,
which had been happening since the very first release without anyone noticing on an
emulator. Every voice file Capcom ships ends with some silent padding that a real console
expects; the replaced lines were missing it, so the console read past the end of the file
and played garbage for an instant. All of the replaced lines in both games and their DLC
now have that padding. Two menu screens in the second game that had cramped or cut off
text are also fixed. Both games' title screens now report accurate version numbers, and
the second game's patch now outranks Capcom's own Japanese update, so your console will
stop offering it. Coming from v1.4, all four files for each game changed.

## v1.4

This is the first release with a full hardware playthrough of the DLC stories, and every
issue that turned up during it is fixed here: lines running off the page, a couple of
items still in Japanese, and a caption the game was forced to shrink to fit. A number of
places where earlier translators had split one of Capcom's pages into two because the
English did not fit are now single pages again, since the actual box is wider than they
were working to. The second game's ordinary conversation text no longer gets cut off
under the on screen arrow that steps between lines, which affected a large number of
pages across the whole game. More of Capcom's own English voice recordings that had never
been used before are added in as well. This release also adds an English icon and,
optionally, an English banner and title for your 3DS home screen. Coming from v1.3, all
four files for each game changed.

## v1.3

This release gives the second game the same fix the first game got in v1.2: statements
shown during cross examinations no longer run into the edge of the text box or get their
last letters clipped off, because the box used for statements is narrower than the box
used for ordinary dialogue and earlier builds had not accounted for that. The same fix is
applied to the second game's DLC episodes. Separately, when a new piece of evidence pops
up on screen, the card that appears was cutting off some of the longer descriptions at
the edge; those are now shortened to fit properly in both the pop up and the permanent
evidence list. Nothing about the artwork or voices changed, and the first game is
unchanged from v1.2. Coming from v1.2, only the second game's update and DLC files need
reinstalling.

## v1.2

This release fixes cross examinations in the first game so that the witness statements
you press no longer run into the edge of the text box or get their last character cut
off. The box used for statements is narrower than the ordinary dialogue box because it
has to leave room for the arrows you use to step between statements, and every earlier
build, including senyarom's original patch, had laid the text out against the wrong,
wider measurement. Around sixty statements across all five episodes needed their line
breaks adjusted, and roughly half of those also needed a small wording trim to fit,
always checked against the original Japanese so the meaning stays the same. A couple of
stray typos are also fixed. The second game does not get this fix yet; that is coming in
the next release. Coming from v1.1, only the first game's update file needs reinstalling.

## v1.1

This release brings in Capcom's official artwork on top of the official text added in
v1.0. Both games' title screens now show Capcom's real logo art instead of the earlier
fan made ones, several evidence cards get their true in game names instead of leftover
fan translation names, and the deduction sequence plates in both games are re-rendered
with Capcom's own wording where they previously were not. The first game's ending card is
now in English as well. Title screens also show real, accurate version numbers for the
first time, replacing placeholder numbers that never changed release to release. A
handful of small text corrections bring a few remaining terms in line with Capcom's
spelling. Coming from v1.0, you need to reinstall both games' update files and the first
game's DLC file again, even though the DLC itself has not changed, so that everything on
your system matches.

## v1.0

This is the first public release. It puts Capcom's official English text from the
Chronicles release onto the Japanese versions of both games, DLC included, on top of
senyarom's earlier fan translation work. On top of the text itself, it adds English voice
clips for DLC gallery content and mini episodes that had been left in Japanese, subtitles
for developer commentary videos, magazine covers rebuilt from Capcom's official art, a
large number of evidence captions that previously did not fit and had to be rewritten,
menu text in the second game that had been rendered in an unreadable decorative font, and
several voice clips that were cut off mid word. Both games install and boot on real 3DS
hardware, though the DLC's rarer jury and pressing voice lines had not yet been heard by
anyone in any build. If you have senyarom's original patch, install the files here fresh;
the old tester files are withdrawn.

> **Superseded.** This is an older release; install the [latest release](https://github.com/Akoi89/tgaa-3ds-english-patch/releases/latest) instead.

Capcom's official English text on the Japanese 3DS releases, **including all the DLC**.

Built on top of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch). You need the Japanese base games; they are not distributed here.

## Install, in this order

| order | file | |
|---|---|---|
| 1 | *the Japanese base game* | yours, not distributed |
| 2 | `TGAA1-base-1.0.17.cia` / `TGAA2-base-1.0.11.cia` | the update |
| 3 | `TGAA1-DLC-1.0.8.cia` / `TGAA2-DLC-1.0.5.cia` | the DLC |

The second game's end credits now run entirely in Japanese, as Capcom shipped them.
The separate no-credits build has been withdrawn -- the normal build is that build.

**Returning from an earlier download? Install all four files again, the DLC included.** Every asset here has been rebuilt since the first release, and the DLC was replaced on 1 September. If you grabbed <!-- check_docs: historical -->`TGAA1-DLC-1.0.4.cia` or `TGAA2-DLC-1.0.3.cia`<!-- check_docs: end --> before then, those files no longer exist and what you have is out of date. A current base game with old DLC is an unsupported configuration and may cause unpredictable audio bugs.

**On-screen version numbers.** The DLC now shows its version in one place per game -- the first game's Episode 0 magazine cover reads `DLC 1.0.8` and the second game's costume-pack banner reads `DLC 1.0.5` -- and from this release on those numbers match the DLC filename. The two **title screens** are different: they read `ENG 1.0.2` (first game) and `ENG 1.0.4` (second game) and are frozen there, because those strings were never rebumped. A title screen showing an old number is cosmetic and expected; a DLC page showing `1.0.4` or `1.0.3` means the old DLC is still installed.

**To confirm the update took, check the text instead.** The first cross-examination in the first game should open with *"I was ingesting regulation beef steak at the restaurant in tactical discussion with the old man."* on **two** lines. Three lines, with the third cut off, means it did not install.

## What this adds

- **46** DLC gallery voice clips in Capcom's English, and **34** mini-episode shouts in the second game; those two "Tales" cases spoke Japanese over English text
- **11** commentary videos subtitled, **9** magazine covers rebuilt from the official *Chronicles* banners
- **164** Court Record captions rewritten to fit at full size
- **42** menu strings in the second game that rendered in an unreadable decorative script
- **19** voice clips that were being cut off mid-word in game
- **24** story voice clips in the second game rebuilt at a higher sample rate by shortening the pauses between phrases instead of degrading every sample, and **3** lines brought from Japanese to English for the first time. 76 clips remain Japanese for reasons listed in the README

## Already have senyarom's release?

The tester zip and its xdelta patches have been withdrawn for now: they were built against the older CIAs and would hand you stale builds. Download the CIAs above.

## This is a test build

**Both games install and boot on real 3DS hardware**, confirmed 30 August 2026, and that was the largest unknown here. Everything else was tested in an emulator, which is more permissive than a console in at least one known way. Nobody has yet *played through* on hardware.

**32 of the first game's shouts**, the jury verdicts and the pressing voices, have never been heard by anyone, in any build. The second game's credits sequence has never been run.

**Back up your save before installing.** The second game wipes its slots if you confirm its corrupted-save prompt, which switching builds can trigger. Decline it and report it.

**[report anything wrong in issue #1](../../issues/1)**.





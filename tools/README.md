# Corresponding source

This is the source for the changes layered on top of
[senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch) to produce the
builds on this repository's [releases page](../../../releases).

senyarom's project is **GPL-3.0-or-later**, and 48 of the scripts here import their
`dgs2tool` modules directly. These are derivative works, so they carry the same licence.
See [`../LICENSE`](../LICENSE). Publishing them is the licence working as intended, not a
favour: the same terms that let this project exist require it to pass the freedom on.

## Setting expectations

**This is research code.** It was written to answer specific questions about two specific
games and then kept because it worked. It is not a general toolkit, there are no tests,
several scripts are single-use, and some exist only to prove a thing was safe to do. Paths
that used to be hardcoded are now environment variables, but nothing here has been
hardened for anyone else's machine.

It is published so that anyone can verify or rebuild what the releases contain. That is
the standard the GPL sets, and it is the honest one.

**No game data is included here, and none will be.** Every script expects you to supply
your own extracted content.

## What you need

| | |
|---|---|
| A checkout of [senyarom/tgaa2-en-patch](https://github.com/senyarom/tgaa2-en-patch) | the `dgs2tool` package most of this imports |
| Python 3, with `pillow` and `numpy` | image and audio work |
| `ffmpeg` | audio and video re-encoding |
| [`3dstool`](https://github.com/dnasdw/3dstool) | unpacking and rebuilding CIA contents |
| *The Great Ace Attorney Chronicles* on PC | the source of Capcom's official English audio |

## Environment variables

Nothing is hardcoded to a machine any more. Set what a given script needs:

| variable | what it points at |
|---|---|
| `DGS2TOOL` | your checkout of senyarom/tgaa2-en-patch |
| `FFMPEG` | the ffmpeg binary, if it is not on `PATH` |
| `THREEDSTOOL` | the 3dstool binary, if it is not on `PATH` |
| `TGAAC_STEAM` | the Chronicles PC install, at `.../nativeDX11x64` |
| `AZAHAR` | the Azahar emulator binary (the driving rig only) |
| `BANNER_ART`, `BANNER_OUT`, `SWEEP_OUT` | input and output folders for specific scripts |

## What is here

| folder | |
|---|---|
| `audio_tools/` | the bulk of it. Voice extraction, MCA/DSP-ADPCM encoding, the slot fitter, and the audit that compares every clip against Capcom's own recording |
| `arc_tools/` | reading and rebuilding `.arc` archives |
| `font_investigation/` | glyph advance measurement, caption fitting, and the review-page builder |
| `cover_build/` | rebuilding the DLC magazine covers from the official Chronicles banners |
| `tgaa2/` | second-game specific text work, including the DLC banners |
| `video_inject/` | subtitling and re-encoding the commentary videos to Capcom's container spec |
| `azrig/` | the emulator driving rig: screen capture, input, and a per-process audio meter used to measure what actually reaches the speaker |

### The two worth reading

**`audio_tools/fit_slots.py`** carries the finding that cost the most time. A voice stream
larger than Capcom's original slot is cut off in game at an unpredictable point, not
truncated to the slot length. The measured evidence is in its docstring. The fix trims
only edge silence and then lowers the sample rate until the complete take fits, so the
cost is treble rather than words.

**`azrig/playtime.ps1`** measures what the speaker actually does, against a pre-touch
baseline, using a per-process meter. It exists because the offline audit passed a build in
which one line was silent and another was cut in half. Every real defect in this project
was found by looking or listening; none were found by reading files.

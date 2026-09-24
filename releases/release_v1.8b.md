**Superseded by [v1.9](../../releases/tag/v1.9).** v1.9 removes the grain v1.8b still left in the cutscene sound and fixes a long list of voice and text problems. Redo every patch.

This release fixes the sound in the first game's animated cutscenes.

- **The crackle over the opening narration.** Capcom ships the cutscene sound
  as three pieces, the music, the effects and the voice, and my build adds
  them together. The total came out louder than the file can hold, so the
  loudest instants had their tops chopped flat. In the opening that happens
  126 times in a minute.
- **All seven cutscenes had it**, not just the opening, and some worse.
- **Nothing else about the sound changed.** The fix eases those peaks down
  instead of chopping them, at the same volume as before.
- **Still there:** a faint grain over the cutscenes. That one is the console's
  audio format rather than anything in the patch, and it has been in every
  build since the English narration went in.

Only the first game changed. Redo its patches. The second game and the
Japanese-voice edition are untouched, so keep those. The program file changed
by one byte, the version stamp on the title screen.

# The seven-wheel lock patch, for anyone porting it to another translation

Written for anyone patching The Great Ace Attorney 2 (3DS) into a language other than English.

In the Case 5 suitcase scene the engine builds a lock with six wheels. My English text needed a seven-digit code, and the original six-wheel lock cannot show one. The fix is a small change to the game's executable plus one data file. Neither contains any words, so both carry over to another language unchanged. The three script files and the arm texture that go with my build are English and do not.

Where a number appears below, it came from a byte comparison on the files named, or from the running game on Azahar. A few things I took from earlier notes without re-checking, and those are marked.

## 1. Which executable, and the traps in front of it

TGAA2 is title id `00040000001AE200`. The update's TMD id, `0004000E001AE200`, is not the folder name for anything below. The game's exheader carries the base id, and that is the one every override folder uses. TGAA1 is `000400000014AD00`; a folder with that id would patch the wrong game.

* The ExeFS `.code` is stored **uncompressed** in this title. The exheader flag byte at `0x0D` is `0x02`, so bit 0 is clear, and the file is 5,058,560 bytes. Offsets in this document are file offsets, which are also offsets into the code as the loader sees it.
* Virtual address = file offset + `0x100000`. Example: the new code sits at VA `0x569f80`, file `0x469f80`.
* From the exheader: text VA `0x100000`, size `0x46a000`; read-only data starts at `0x56a000`. The text segment therefore ends at file `0x469fff`.
* The patch adds code without growing the file. Text ends in a run of zero padding, 193 bytes from `0x469f3f` to `0x469fff` in the unpatched file. The new routine uses 20 of them, starting at `0x469f80`. No aligned 32-bit word in the unpatched file points into that run (I checked), and from my notes the only branch to it is the one I added.
* Unpatched `.code`: sha256 `0c3c6ad7ba39eecaa4b1a088710dde917c05652608f07ff403f6d1c275813f83`. Patched: `418c4e10904e4b04762e66ac5fd0be77f80eaf0da5d8762c8ababd973bf6974f`. The unpatched file is byte-identical to the official English v2.3.3 `.code`, so nothing in it comes from my own earlier code changes.

## 2. What the lock is made of

The lock controller is the class `uDialUnlockCtrl`. I read its methods from the code. Each fact below is a literal or an immediate in the executable, and each is changed by one of the sites in section 3.

* **Wheel count.** The count is hard-coded as 6 in about a dozen loops, in the array constructor and destructor, and in the cursor clamp. The wheel handles are an array of 16-byte elements starting at controller offset `0x30`, so six of them end at `0x90`. A seventh element would land on another handle that holds the lock-body model, so I moved that handle to `0xf0` and grew the object from `0xf0` to `0x100` bytes. The size is set in two places: the factory and the static type info.
* **The answer.** A plain 32-bit integer stored at controller offset `0xd0`. The constructor is the only writer, and the literal it loads is at VA `0x27ecd0`. The shipped value is 523104 (`0x0007fb60`); mine is 5231045 (`0x004fd1c5`). The check loop runs from wheel 6 down to wheel 0. For each wheel it takes the answer modulo 10, compares that with the wheel's digit, then divides the answer by 10. So wheel 0, the leftmost, takes the millions digit and wheel 6 takes the ones. The record writes three bytes, so it fits any answer below 16,777,216.
* **Layout.** The wheels are 3D drums. Wheel `i` is placed at x = first - 5.0 * i, where `first` is a float literal: 12.5 for six wheels (centred), 15.0 for seven. The drums are 5 units wide.
* **Camera.** It is read from `scene\lock\lock.lcm`, which has a float at file offset `0x4A8`. The game's file has 0.7836 there. At that angle the screen shows about 30.4 units (from my notes, using a camera distance of 2223.09), which fits six wheels. I set it to 0.9, which shows 34.92 units and fits seven (35 units). Only three bytes of the file change: `c5 97 48` becomes `66 66 66`, and the file stays 1,204 bytes. The Chronicles (PC) copy of the same file differs from the 3DS one in this value only, and it is also 0.9. That tells me how the PC version fits seven wheels, but I could not read the PC code (it is encrypted), so that part is inference from data.
* **Cursor.** The cursor's spacing is a float literal at VA `0x27ece4`: 53.0 for six wheels, 45.82 for seven (5 / 34.92 * 320). The cursor's X is that spacing times the wheel index, plus a base that comes from a GUI file, so I added a small offset: the multiply at `0x27e5a8` now calls the 20-byte routine in section 4, which adds -2.4 pixels.
* **Touch.** Tapping a wheel selects it by a hit test on a fixed grid of screen rectangles, each 53 pixels wide. They are not computed from the model. The width 53 is the six-wheel spacing, so with seven wheels 45.82 pixels apart the grid drifts 7.18 pixels per wheel, and a tap in the middle of a wheel in the right half of the panel selects its left neighbour. Changing the width byte at file `0x425354` from `0x35` (53) to `0x2e` (46) fixes it. In an interpreter run of the game's own hit-test bytes (from my notes, not re-checked), every wheel's centre selects itself. I have not seen the fixed touch behaviour on the running game.

## 3. The 40 patch sites

Offsets are file offsets. There are 40 records and 68 bytes in total. "Bound" means an immediate that was 6 or 5 and is now 7 or 6.

| # | offset | old | new | what it does |
|---|---|---|---|---|
| 1 | `0x17d744` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 2 | `0x17da98` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 3 | `0x17db04` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 4 | `0x17dbd8` | `06` | `07` | cursor right clamp, compare |
| 5 | `0x17dbdc` | `05` | `06` | cursor right clamp, last index |
| 6 | `0x17dd78` | `05` | `06` | answer check, start index (pad path) |
| 7 | `0x17de04` | `f060` | `016c` | object size `mov r6,#0xf0` to `#0x100` (factory) |
| 8 | `0x17e318` | `05` | `06` | answer check, start index (`checkAnswer`) |
| 9 | `0x17e3bc` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 10 | `0x17e430` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 11 | `0x17e4e0` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 12 | `0x17e4e8` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 13 | `0x17e504` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 14 | `0x17e5a8` | `800a20ee` | `74ae0beb` | `vmul.f32 s0,s1,s0` becomes `bl 0x569f80` (cursor X) |
| 15 | `0x17e5f8` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 16 | `0x17e648` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 17 | `0x17e6c8` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 18 | `0x17e850` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 19 | `0x17e880` | `90` | `f0` | handle base `+0x90` to `+0xf0` |
| 20 | `0x17e8ec` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 21 | `0x17e908` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 22 | `0x17ea22` | `48` | `70` | float 12.5 to 15.0, wheel 0 x |
| 23 | `0x17eae0` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 24 | `0x17eb54` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 25 | `0x17ebb0` | `06` | `07` | handle array count in the vector constructor |
| 26 | `0x17ebc8` | `64` | `c4` | constructor store into the moved handle (`+0x64` to `+0xc4`, relative to controller `+0x30`) |
| 27 | `0x17ebd0` | `60` | `c0` | constructor, base of the moved handle (`+0x60` to `+0xc0`, same base) |
| 28 | `0x17ebd4` | `68` | `c8` | constructor store into the moved handle (`+0x68` to `+0xc8`, same base) |
| 29 | `0x17eca4` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 30 | `0x17ecd0` | `60fb07` | `c5d14f` | answer literal 523104 to 5231045 (3 low bytes) |
| 31 | `0x17ece4` | `000054` | `ae4737` | float 53.0 to 45.82, cursor spacing (3 low bytes) |
| 32 | `0x17ed54` | `06` | `07` | wheel loop bound; per-site role not recorded |
| 33 | `0x17ed5c` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 34 | `0x17ed78` | `9c` | `fc` | lock-body handle `+0x9c` to `+0xfc` |
| 35 | `0x17edc8` | `90` | `f0` | handle base `+0x90` to `+0xf0` |
| 36 | `0x17edcc` | `90` | `f0` | handle `+0x90` to `+0xf0` |
| 37 | `0x17ede4` | `06` | `07` | handle array count in the vector destructor |
| 38 | `0x425328` | `f030` | `013c` | object size `mov r3,#0xf0` to `#0x100` (static type info) |
| 39 | `0x425354` | `35` | `2e` | touch rectangle width 53 to 46 |
| 40 | `0x469f80` | 20 zero bytes | see section 4 | the new routine |

Eight of the 9c-to-fc rows, three 90-to-f0 rows and three constructor rows (14 in all) move the same lock-body handle. They must change together, or some method will read the old position and find a wheel there. Rows 1 to 37 are all in the controller's own methods, between VA `0x27d6c4` and `0x27ee14`. Rows 38 and 39 are in the static type-info initialiser at `0x525318`.

## 4. The 20-byte routine

At file `0x469f80`:

`80 0a 20 ee  01 1a 9f ed  01 0a 30 ee  1e ff 2f e1  9a 99 19 c0`

Disassembled with capstone:

* `vmul.f32 s0, s1, s0` (the instruction that was replaced at `0x27e5a8`)
* `vldr s2, [pc, #4]`
* `vadd.f32 s0, s0, s2`
* `bx lr`
* a float, `0xc019999a`, which is -2.4

The caller, `0x27e550`, pushes `lr` at entry, and the instruction after the `bl` is another call, so using `lr` and `s2` here is safe. My first paper estimate for the float was -5.89, from the old and new wheel-0 positions. The build uses -2.4. If your GUI file differs from mine, expect to tune this by eye.

## 5. Digits 0 to 5 only

Each wheel's digit byte, at offset `0xc80` in the wheel object, wraps modulo 6 in the code (add 6 below 0, subtract 6 above 5), and the drum texture shows the faces 0 to 5. I measured both. A code must therefore use only the digits 0 to 5, and there are 6^7 = 279,936 possible seven-digit combinations. 5231045 fits. I did not try to change the wrap.

## 6. How I proved it

* **Emulator.** On Azahar, running my v1.9q build with only the add-on files in the mods folder, the lock showed seven wheels. I set 5231045 with the Down presses, read it as `5 2 3 1 0 4 5` left to right, switched to the Present tab, and the top screen showed "*Click!*". Without the add-on the same build shows six.
* **Interpreter.** I ran the game's own compare routines (`checkAnswer` and the pad-path copy) in a small ARM interpreter over every wheel-face combination. On the patched code, 279,936 combinations (6^7), exactly one was accepted: 5231045. I reran that for this document. On the original code, from my notes, 46,656 combinations accepted only 523104.
* **IPS equality.** I applied the 40-record IPS to the unpatched `.code` and compared sha256 with the patched file above. They match, and 68 bytes differ in total.

## 7. Traps when you reuse it

The patch fits only a `.code` with the exact original bytes at the 40 sites. I checked the following by comparing the bytes at every record.

| `.code` | result |
|---|---|
| my v1.9q English build | 40 of 40 records fit |
| official English v2.3.3 | 40 of 40 (identical file); re-checked for this document |
| Japanese base 1.0, after BLZ decompression | 40 of 40 (from my notes, not re-checked) |
| the file labelled Japanese v2.3.3 (update) in my sources | 1 of 40; a different layout, do not apply (from my notes, not re-checked) |

I could not tell which of the two Japanese executables a real Japanese cartridge with its update would run.

**Azahar (LayeredFS).** Put `code.ips` at `load\mods\00040000001AE200\exefs\code.ips`. Put lock.lcm at `load\mods\00040000001AE200\romfs\scene\lock\lock.lcm`. Mods have to be enabled when you launch (the `-e` option). Use the base id, not the update's id; otherwise nothing happens and nothing tells you. On launch, Azahar logs the patch being applied and the replacement file in use.

**Luma, on a console.** I haven't tried it. I had the Luma3DS loader source (version 13.4) read for me and this is what it says, so treat it as a second-hand reading until someone tests it. `code.ips` goes at `luma\titles\00040000001AE200\code.ips`: the base id again, with no `exefs` folder. Offsets count from the first byte of the decompressed code, and "Enable game patching" has to be on in Luma's config. The romfs file goes under `luma\titles\00040000001AE200\romfs\scene\lock\lock.lcm`. Luma tries the SD card path before the game's own file, so replacing a file the base game already has (`lock.lcm` is one) should work. A file the game's romfs does not have is a different matter: a game that parses the romfs tables itself would not see it.

If you edit the IPS by hand, remember that an IPS offset of `0x454F46` collides with the end marker. Mine has no such record.

## 8. What I have not verified

* A real 3DS and real Luma. Everything above was seen in Azahar only.
* Whether any save file serialises the lock controller. The object grew by 16 bytes. I found nothing in static analysis, and an older save loaded into the patched build and ran the lock, but that is not proof.
* On the final build I only watched the right code open the lock. Wrong-code behaviour, touch selection of all seven wheels, the pad moving to both ends, and leaving and re-entering the puzzle were only seen on earlier builds.
* The cursor bars clip about 16 pixels at the frame edge on wheels 1 and 7. I accepted that.
* Language. `code.ips` and `lock.lcm` are language-neutral: two files, 1,480 bytes together. The three script files with "seven-digit" wording and the `chr303_jpn.arc` arm texture (the Sholmes tattoo has seven glyphs) are English, so you have to redo them for your language.

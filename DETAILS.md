# The Great Ace Attorney 3DS patch: the detail

Everything the README used to carry inline, plus the reasoning and the sources behind every
figure in it.

---

## Something looks wrong. Is it known?

Start here. This is everything I know about that you might actually notice while playing,
sorted by what it looks like on screen rather than by which job it came out of. The rest of
this document is a record of the work, which is a different thing and not much use for
looking something up.

If what you're seeing isn't on this list, please tell me about it in
[issue #1](../../issues/1). If it is on this list, I still don't mind hearing about it, and
I'd much rather have a duplicate than miss something.

| What you're seeing or hearing | Where | What it is |
|---|---|---|
| A line is spoken in Japanese while the text is English | both games, story scenes | 54 lines have no English recording at all. Capcom never made one, and that was checked exhaustively rather than assumed |
| The same, on a line that feels like it should exist | both games, story scenes | FIXED in v1.9. 18 lines had been left in Japanese because Capcom's English take was longer than the Japanese one and a longer clip was believed to get cut off. That cut-off was the misplacement bug described under the cutscene grain: a clip written where the game actually reads it plays to the end whatever its length. All 18 now play Capcom's English. One line in each game was heard in-game; the rest were checked against the recordings offline, and the ones in the second game's last two episodes have not been reached on a console |
| An *Objection!* or *Hold it!* comes out in Japanese | second game, two minor characters | 4 shouts Capcom never re-recorded, for `chr104_mrs` and `chr210_mmm`. Their archives were checked member by member: 100 of the 104 shouts have an English master, these four don't |
| A gallery chant is in Japanese | second game | FIXED in v1.9. The one chant that had stayed Japanese, in Episode 5, was held back because Capcom's English is much longer than the Japanese and a longer clip was believed to get cut off. That was the misplacement bug, not a size limit, so it plays Capcom's English now, at full length and looped where Capcom's recording says. Checked on the PC only; the test save doesn't reach it, so a report from anyone who hears it in-game would help |
| No narration plays on two pages of an episode opening | first game, Episode 2 | FIXED in v1.9. Those two English lines used to be cut to fit a timer set for the Japanese takes; they play in full now. Heard in-game |
| Narration cuts mid-word with a short fade | first game, Episode 2 opening, three places | FIXED in v1.9a. Each page's English plays as two halves, and three of the splits fell inside a word because the clean break used to cost about a third of the audio quality to fit a size limit that turned out to be my own bug. All three now split in a real pause, at full quality. Heard in-game |
| A DLC voice clip sounds duller than the rest, or stops before the line is finished | first game's DLC | FIXED in v1.9. The quality had been lowered on 16 lines, and 3 more trimmed, to keep each clip inside the space Capcom's Japanese clip took, because a bigger clip was cut off in-game. The cut-off was the misplacement bug, not a size rule, so all 19 are re-encoded at full quality and full length. Every one was heard playing to the end in an emulator |
| A voice line in the second game sounds hurried, with the breath between phrases missing | second game, story scenes | FIXED in v1.9. 27 lines had pauses cut out of the middle to make them fit the space, a workaround for the same misplacement bug. The pauses are back, and every second-game voice that had been stored at reduced quality for the same reason is at full quality again: a scan of the finished build found no replaced voice below Capcom's sample rate in either game or either DLC |
| The parchment narration at the start of Episode 2 sounds rushed, or pauses in the middle of a sentence | first game | FIXED in v1.9 and v1.9a. Each page of that opening had been timed for the Japanese takes, and the longer English takes had been sped up, by up to about a third, to finish in time. v1.9 restored the natural pace, but each page's English is in two pieces and the second piece still waited on the cue for the Japanese second line, which left pauses of half a second to over a second on five pages, three of them mid-sentence or mid-word, while two pages felt rushed. v1.9a times each page the way Capcom's PC release does: one continuous read per page, the second piece following the first after the recording's own pause, with the page turns, art and music on Capcom's original timing. Heard in-game: nothing is cut off and nothing overlaps |
| A gasp, effort or cry during the third episode's Dance of Deduction sounds distorted | second game | FIXED in v1.9. Those 14 reactions went through a converter of mine that read part of the source format wrong. Fixed at source; they now decode exactly like the reference decoder. Checked by decoding, not yet heard in the scene |
| The Waiter's Business Card or the Medical Report Card cover doesn't match what the characters say | first game, Episode 1, the Court Record's 3D evidence view | FIXED in v1.9p, reported by backplusone on issue #1. Both pictures were the older fan translation's English art and disagreed with the dialogue. *Chronicles* ships no English version of either, so there was no Capcom picture to carry over; I redrew them for this patch with an image generator and finished them myself. The card's front (Hosonaga's) now reads Imperial Police Bureau / Primary Criminal Investigation Division / Chief Inspector / Satoru Hosonaga, as the characters read it out; the back, the restaurant sketch, is unchanged. The Medical Report Card cover now reads Medical Report Card / Required for every visit / Name: Mr John Wilson / Hotta Clinic; the picture of the open-ledger first state is unchanged. Their small list icons were redone to match. Seen on the emulator: the card's front and back and the cover, all in the 3D view. **Not seen:** the cover's list icon, which only appears later in the story, and the Medical Report details view. Details under *The two redrawn evidence pictures and the capital H* below. Not run on a 3DS |
| A capital H, E or F in a long Court Record caption has lost its crossbar: "Hosonaga-san" reads "IIosonaga-san" | both games, Court Record captions | FIXED in v1.9p, reported by backplusone on issue #1. When a caption is too long for its place the game draws it shrunk, and the crossbar of those three letters is one pixel high in the font, so the shrink could skip it and an H looked like two I's. The letters now have a slightly thicker crossbar, so it survives the shrink. Changed in both games' updates and in the second game's DLC; the first game's DLC has no font of its own. Seen on the emulator in the first game: the Waiter's Business Card caption reads "Hosonaga-san" with its crossbar, and H and E keep theirs in other captions and on the People tab. In the second game the title screen reads ENG 1.0.31 and H and E keep their crossbars in the Court Record of Episode 1 (the Poison Article caption, and the People entries for Yujin Mikotoba, Taketsuchi Auchi and Satoru Hosonaga). **Not seen:** the Red-Handed captions (Episode 5), a capital F in a long caption in either game, and whether any of the second game's captions I looked at was actually shrunk, so that game's result shows the letters intact but not that the old bug would have hit those lines. Details under *The two redrawn evidence pictures and the capital H* below. Not run on a 3DS |
| In the box that asks whether to start a chapter, the chapter name sits against the left edge, and in the second game the episode heading above it is one line in two mismatched fonts | both games, Select Episode then a chapter | FIXED in v1.9p. The chapter name is centred in both games. In the second game the heading is now two centred lines, "Ep. 1:" above the title, so it no longer mixes two fonts on one line. The saved-game (Load and Save) rows keep the heading on one line, set slightly lower with more space under the date, and the Episode 1 and Episode 3 titles are a little smaller than the others so they fit the row. Seen on the emulator: the second game's Episode 1 box and its Episode 2 and Episode 3 saved-game rows, and the first game's centred names in a test build. **Not seen:** the Episode 1, Episode 4 and Final saved-game rows (no such saves; fitted by measurement only), the Save screen, and the exact shipped first-game build (TESTING.md has the current state). Details under *The chapter names and episode headings* below. Not run on a 3DS |
| The manual shows an older name, such as Naruhodou or Holmes, or a menu word that differs from the game | both games, the manual opened from the HOME menu | The manual's text is English and revised as of v1.9o. The main screenshots were retaken in the patched game in v1.9q, but the logo, a few headings and some diagrams are pictures from Scarlet Study's translation and I haven't redrawn them. The text is right where a picture disagrees with it. I plan to redo the pictures later. Not seen on a 3DS |
| The question shown with the Present and Examine buttons is chopped off partway through a word on the lower screen | both games, the 3D investigation (seen in a photo from the first game) | FIXED in v1.9n, reported on issue #1. In the 3D investigation the game puts a question on the lower screen next to the Present and Examine buttons, for example "Point out what it is that proves the victim fell from the roof deck through the skylight!". That text is drawn in a widget that runs further right than the speech bubble does, and it was never part of my width checks, so a few of the longer questions were cut off. Six of these question pages across the two games (the first game's 2 script files, the second game's 4) are re-broken so each line stays inside a safe width: three long ones are split into two pages, the other three just get a new line break. No wording changed. **Not seen on screen:** my emulator run couldn't reach those scenes, so this is measured as files. One more page of the same kind, in the first game, is left as it was and hasn't been checked. Details under *The Present and Examine question* below. Not run on a 3DS |
| A shout has lost its metallic "shing": "Hold it!", "Objection!" or "Take that!" is just the voice | both games and the second game's DLC, the English shouts | FIXED in v1.9n, reported on issue #1. In Capcom's Japanese files that sound effect is mixed into the shout clips themselves, and the English recordings didn't have it, so it was lost. It is mixed back in under 186 English shouts now (40 in the first game, 65 in the second, 81 in the second game's DLC) at the level Capcom used, with a soft limiter so the loud ones don't clip. The first game's DLC has no such clips. I compared two ways of mixing it on a PC render of the clips and chose the limiter version. **Not heard on a 3DS**; the emulator run played two shout cut-ins without a crash but couldn't judge the sound. Six shouts are still Japanese because they were never in the English update: in the second game, `chr104_mrs` and `chr210_mmm` "igiari" and "matta" (4), and in its DLC `chr010_hms` and `chr100_asg` "kurae" (2). The Japanese-voice edition already had the sound and its audio didn't change. Details under *The shout sound effect* below |
| The British-style *Objection!* bubble reads "Objection" cut off after the "n", with no "!" | both games, the British courtroom bubble (seen in the first game's Episode 3 trial) | FIXED in v1.9m. The game draws that word from a 400 px wide window of its picture, and the English word I shipped ran past the right end of the window, so the last letters and the "!" were never drawn. The word is moved inside the window, moved only, not resized. Seen cut off on the emulator in v1.9l (the "n" touching the frame edge, no "!") and whole with the fixed picture loaded as a replacement file (the "!" sits inside the burst, background visible beyond it); that second test did not use the built CIA. Seen in the first game only, in the first Episode 3 cross-examination after Furst's statement 4 is pressed; the second game gets the same fix and I didn't catch its bubble. This blackletter English bubble is Van Zieks's own (the other speakers use the standard bubble); the bare hand seen inside the burst is Ryunosuke's pointing pose showing behind it, and Van Zieks speaks straight after. Not run on a 3DS |
| In the first game's Dance of Deduction, the cyan label that appears when the crosshair is on an object has the tails of g, p, y and j cut flat | first game, Dance of Deduction | FIXED in v1.9m. The game cuts each label's picture into three strips of 32 rows and draws them as one line. My lettering was Georgia 34, whose descenders ran past the bottom strip, so the tails were cut flat on screen (seen on the emulator, matching a render clipped to 32 rows, not the full render). All 74 labels in the first game are re-lettered at Georgia 33 (two long ones at 30 and 29 so they still fit the width), with one shared baseline, so every ascender and descender sits inside the 32 rows; the script's `--fit` mode does it. Seen on the emulator after the fix: three labels in the first Dance ("copious beard", "thick hat", "golden locks") and eight in the second ("aching heart", "claw scratch", "writhing serpent", "Seaman Strogenov", "photograph frame", "Miss Pavlova", "little kitten", "left ear"), each one straight line; I looked at the 6x crops of "golden locks" and "photograph frame" and the g and p tails are whole. Not seen: "small picture", "wastepaper basket", "snake's sloughed skin", "books on the shelf", "cat's toy". The second game draws these labels as text, not from these pictures (a test picture placed in their slots changed nothing), so its 82 label pictures stay as they were and aren't shown in game. Not run on a 3DS |
| The first game's staff credits misspell some names and use job titles that differ from Capcom's | first game, the end credits | FIXED in v1.9m. 44 of the 54 credit pictures are re-lettered to follow Capcom's own English credits from Chronicles, matched person by person (a 45th, `s_credit_cast00`, changes only along its left edge, where a neighbouring column runs across it): staff names as Capcom spells them, given name first, Capcom's job titles, the Japanese voice cast with Capcom's romanisation, and the character names (Iris Wilson, Herlock Sholmes, Kazuma Asogi, Ryunosuke Naruhodo, where the roll said Watson, Holmes, Asougi and Naruhodou). The fan group's own credits are kept. The changed staff names are listed under *Picture pass 2* below. The second game's credits stay Japanese, as decided on 2026-09-01. **Not seen on screen:** the credits are the end of the game and the rig didn't reach them, so the layout, the scroll and the new columns are untested. The credit archive `UI_credit_s_jpn.arc` is 6,136 bytes bigger than before (269,322 to 275,458) because the new lettering compresses worse, and I haven't tested whether the game's loader takes it. Not run on a 3DS |
| A few names and words in pictures were wrong: "Hold it, Mr Holmes!" and "Deduction Failed" on the Dance of Deduction screens, JOHN WATSON on a medical report card, "Yuujin" and "Yuumei" in a tutorial picture, a washed-out bookcase, text crowding a sketch in a DLC design page | both games, as listed | FIXED in v1.9m. The Dance topic pictures (both games) now read "Hold it, Mr Sholmes!" and Capcom's "I can see nothing." in place of "Deduction Failed", in the fan's own letters with only the capital S and the capital I drawn to match. The first game's medical report card in the 3D evidence view reads JOHN WILSON, as the script does. The first game's bookcase picture had been washed out by a block port in v1.6 (945 of its 4,096 texture blocks changed, with pale blue patches); it is the original colours again, with Capcom's "Ship Protocols" book title. The second game's tutorial Court Record screenshot reads "Yujin Mikotoba" and "Imperial Yumei University". The first game's DLC design page for Susato has its text moved clear of the sketches. Seen on the emulator: "Review Start / Hold it, Mr Sholmes!" in both games, "Deduction Failed / I can see nothing." in the first game, JOHN WILSON on the card, and the design page. **Not seen:** the bookcase, the second game's tutorial screenshot (the Guide entry wasn't found) and the second game's Deduction Failed stamp. Not run on a 3DS |
| In the Move list, the start of a place name is hidden under the "You" or "?" tag, and long names are cut off at the end of the bar | both games, the Move menu while investigating | FIXED in v1.9l, reported by 0tozillion-cpu on issue #1. The names were centred on the bar, so the tag at the bar's left end sat on top of the start of any name wider than about 153 units, and names that long ran off the other end. Names now start just after the tag, left-aligned at full size, and every one fits. The ones that were too long use shorter forms: Capcom's own short location titles from Chronicles where they have one ("Supreme Court", "Olive's Hospital Bed"), otherwise a short form I picked for the list ("Naruhodo's Office", "1st-Class Passageway"). The place card you get on arriving somewhere still shows the full name. Measured: 15 of the first game's 24 distinct names and 22 of the second game's 33 were wider than 153. The list's layout file (`dtc_move_sub.gui`) now places the name after the tag; the first game's copy is 16 bytes larger, the second game's is the same size. 26 names changed in 33 entries (13 in the first game, 20 in the second), and the widest new one is 177 units against a limit of 182 that I set (about 186 are free after the tag). First game, old -> new: First-Class Passageway -> 1st-Class Passageway; Kazuma's Cabin (At Night) -> Kazuma's (At Night); Lord Chief Justice's Office -> Chief Justice's Office; Mr Natsume's Lodgings -> Natsume's Lodgings; Naruhodo's Legal Consultancy -> Naruhodo's Office; St Bartholomew's Hospital, Olive's Bed -> Olive's Hospital Bed; Supreme Court Courtroom -> Supreme Court; Windibank's Main Shop -> Main Shop; Windibank's Pawnbrokery -> Pawnbrokery; Windibank's Storeroom -> Storeroom. Second game: Experimentation Stage -> Experiment Stage; First-Class Passageway -> 1st-Class Passageway; Lord Chief Justice's Office -> Chief Justice's Office; Miss Green's Hospital Bed -> Olive's Hospital Bed; Mr Drebber's Back Room -> Drebber's Back Room; Mr Drebber's Workshop -> Drebber's Workshop; Mr Natsume's Lodgings -> Natsume's Lodgings; Mr Shamspeare's Room -> Shamspeare's Room; Mr Vigil's Hospital Bed -> Vigil's Hospital Bed; Naruhodo's Legal Consultancy -> Naruhodo's Office; Port of Dover Quayside -> Dover Quayside; Prison Governor's Office -> Governor's Office; SS Grouse Passageway -> Grouse Passageway; Supreme Court of Judicature -> Supreme Court; The Great Exhibition Grounds -> The Great Exhibition; Windibank's Pawnbrokery -> Pawnbrokery. Seen on the emulator in the first game: Episode 2's list (3 rows) and Episode 5's (6 rows), every name whole, at one left edge, with the tag clear of the text; arriving at Kazuma's Cabin and at the Pawnbrokery still prints the full place card ("SS Burya, First-Class Cabin No. 1", "Windibank's Pawnbrokery"). Seen on the emulator in the second game too, in Episode 2's investigation: 3 rows ("Naruhodo's Office", "Sholmes's Suite", the "You" tag with "Olive's Hospital Bed"), left-aligned at one edge, whole, tag clear; arriving at Sholmes's Suite prints "Sholmes's Suite". A darker bar with no Enter button is the game's own look for a place you can't go to yet; it showed on "Miss Pavlova's Cabin" in the first game and "Naruhodo's Office" in the second. The Court Record titles for the same places are separate strings and weren't changed. Not run on a 3DS |
| A juror's line in the Summation Examination is cut off at the right edge of its box, like "Fair fares is our mott" | both games, the juror speech boxes on the bottom screen | FIXED in v1.9l, reported by 0tozillion-cpu on issue #1. The box holds two rows, and a row that ran past the screen edge was chopped. 46 lines were reworded so each fits in two rows at the normal text size: 28 in the first game and 18 in the second. Eight boxes that had needed three rows now need two. I could have shrunk the text instead; I shortened the wording so the letters stay at their normal size. For example, "You can trust the guild. Fair fares is our motto. / Prices haven't gone above fourpence for years." is now "Trust the guild. Fair fares is our motto. / Prices haven't topped fourpence in years." The statement on the top screen is unchanged. Measured: a row is whole up to about 309 units (text starts 11 units in on a 320-unit screen). Before the change 46 of the 63 juror entries in the two games had a row wider than that or needed three rows (28 of 40 in the first game, 18 of 23 in the second); the widest row now is 305 in the first game and 302 in the second. Seen on the emulator in the first game, Episode 3: all six jurors' boxes whole, including the three the tester reported. The second game's 18 boxes were measured against the same 320-unit screen, which I couldn't confirm for that game, and **haven't been seen on screen**. Not run on a 3DS |
| The words "Invalid Message" show up under a cutscene subtitle | first game, the animated cutscenes: after the station-arrival line, and after the closing monologue line | FIXED in v1.9l, reported by 0tozillion-cpu on issue #1. Capcom's English script holds a placeholder with that name in two subtitle slots (entries 38 and 77 of the cutscene subtitle file). Capcom's PC version never shows it and the 3DS version does. Both slots are now a single space, so nothing shows. Placeholders of the same name sit in other files (110 in the first game, 163 in the second); those weren't part of the report and I left them alone. Checked in the files only: I haven't seen either cutscene on the emulator since the change. Not run on a 3DS |
| The last row of an evidence or autopsy page runs into the bottom of its frame | first game (three pages) and second game (one page), document pages | FIXED in v1.9l, reported by 0tozillion-cpu on issue #1. The first game's autopsy page ("Victim / Male, Far Eastern / Time of Death...") had 10 rows, and the tenth sat on the frame. It is 9 rows now: the wording is re-broken, with one light trim ("almost certainly broken as a result of a strong blow" became "almost certainly broken by a strong blow"). Two other 10-row pages got the same treatment, the 'Thrice-Fired' Mason autopsy report (a blank row after "Brickmaker" went) and the "Additional Notes" page (a blank row under the heading went, and v1.9k's 10 rows are back to 9; no visible text changed), and so did one second-game page, "Autopsy Findings" (one of its three blank rows went). Measured: the panel holds 9 rows cleanly (row pitch 23 px, and the tenth row's ink ran through the frame's dark rule); the widest changed row is 342 against a 365 limit. Seen on the emulator: the Mason autopsy report, 9 rows with no blank row and clear of the frame. The tester's own page, "Additional Notes" and the second game's page were checked in the files, not on screen. Not run on a 3DS |
| A picture looks patched rather than made: a hand-lettered label that doesn't match the art around it, a black box, a smeared newspaper, washed-out Picture Book pages, or the "2" cut off on the second game's HOME menu banner | both games, the first game's DLC Picture Book, the second game's HOME banner | FIXED in v1.9l. I went through the 471 pictures the patch changes, next to Capcom's and the Japanese originals, and redid the ones that fell short. 88 pictures were rebuilt: 13 in the first game's update, 19 in the second game's update, 1 in the second game's DLC (the British Empire card), 54 in the first game's DLC Picture Book, and the second game's HOME banner (the "2" was cut off; it is refitted 246 px wide with 4 to 5 px of margin). In the first game that is the kitchen and entrance labels on the floor plans, the pawn tickets, a note and address, a disc label, the black box round "Witness", a dark bar above "THE GREAT"; and the street map, whose shop and street names now match the script (Meerschaum Street, Briar Road, Calabash Road, Bourbon Books, Yore Books, Mr Natsume's Lodgings), with a layout file (`demo3_00_00.gui`, 16 bytes larger) placing them. On the emulator the first placement put "Lodgings" inside the red box marking his lodgings and the red outline through "Yore"; both labels were moved (the lodgings label 10 px up and 11 px left, "Yore Books" 12 px down) and all three map views in the Episode 4 trial now show every label clear. In the second game it is the newspapers, the name tags and arm writing on character models, a robe and a flag (where Capcom changes a P to an S), the title screen's glow and diamonds, the Final Chapter and Episode 5 opening cards, the "You" and "?" tag art, and the maps. In the Picture Book it is the see-through panels (24 pages had washed out the art behind them), a second red stamp, hand-lettered labels, the theme title streaks and the cover lettering. The brush-written name tags and small production scribbles in the Picture Book stay Japanese, as decided on 2026-09-15; the second game's end credits stay Japanese, as above. The Dance of Deduction name plates were audited; two in the second game had the names misspelled ("Kazuma Asougi", "Sythe's ledger") and now read "Kazuma Asogi" and "Sithe's ledger", as in the script, in the same lettering. Seen on the emulator: the title and DLC stamps, the first game's DLC covers, a sample of Picture Book pages (the Iris issue's page 5 label no longer touches the flower ornament), the Episode 4 street map, and the second game's two DLC cards. **Not seen on screen:** the second game's HOME banner (I didn't install the banner), and the rest of the second game's update pictures. Not run on a 3DS |
| In the Dance of Deduction, the word that flies across the top screen when you present something is cut into three pieces drawn at different heights, stepping down from left to right | both games | FIXED in v1.9q. The flying word is one 128 by 128 picture per phrase (`UI/3_mg/30_together/tex/txt/*.tex`) that the game draws as three strips side by side. The Japanese pictures, and the fan's original English ones, put the baseline 29 rows into every 40-row strip. My lettering sat on a 32-row grid instead, so the three baselines came out 8 rows apart in the second game (37, 29 and 21) and 8 rows apart in the first (34, 26 and 18), which shows as the step. In v1.9q I moved each band of each picture so all three baselines are at 29: 73 second-game pictures by -8, 0 and +8 rows (3 by -7, +1 and +9, where the letter shapes differ), 56 first-game pictures by -5, +3 and +11 (2 by -4, +4 and +12), re-encoded from the decoded pictures with the transparency unchanged. Two second-game pictures that were already on the 40-row grid are byte-identical. Seen on the emulator, as a before and after: the second game's "glass containing ice" (baselines 226, 210 and 194 before; one line after) and the first game's "aching heart" and "writhing serpent". The first game's were loaded as replacement files over the previous update, not from the v1.9q update, and the bottom-screen label looked the same either way. Not seen: other phrases, and the final first-game update on screen. The row spacing in the script that makes the pictures (`dance_plates.py`) still has the old 32-row spacing, noted in a comment; it matters only if the pictures are drawn again. Not run on a 3DS |
| The second game's DLC shows as version 1.1.3 in an installer such as FBI, while the file name and the costume pack banner say 1.0.19 | second game's DLC | Not a fault. A title version's last number is 4 bits, so it stops at 15, and 1.0.15 was the last the DLC could declare. The file `TGAA2-DLC-1.0.19.cia` (and `TGAA2-EN-DLC-v1.9q.cia`) declares 1.1.3, the next version up from the 1.1.2 that v1.9p's DLC declared (v1.9n's declared 1.1.1, v1.9l and v1.9m's 1.1.0); the stamp on the costume pack banner reads `DLC 1.0.19`. I read both in the files; this DLC has not been installed yet. Installing it over an older DLC hasn't been tried, and it hasn't been installed on a 3DS |
| Stray spaces in the text where a hidden control code sat against a word: "student , currently", "touch ' Present '", "m- my omnibus", "Well... I think", double spaces, and three lines that began with the punctuation that belonged to the line before. One evidence-report page (the first game's "Additional Notes") also had Capcom's three "- " list points run into the paragraph | both games and the first game's DLC, mostly the first game | FIXED in v1.9k. A cleanup pass of mine on 2026-09-05 (not senyarom's text) split words wherever one of the game's hidden text-timing or colour codes sat against a word, and joined the pieces back with a space. Every one now matches Capcom's script at that spot, and the three list points each start their own line again. Smaller slips went in the same release: "anti- gravity" (second game), "Sherlock" for "Herlock" in two second-game costume error messages, "judgment" and three dashes in the first game's DLC (now Capcom's form, two " - " and one "--"), missing spaces in three DLC music notes (Iris Wilson, Lord Chief Justice Stronghart, Gina Lestrade), a space inside a bracket in the DLC, and a leading space that pushed a centred system line off centre in both games. Found by comparing every shipped line against Capcom's Chronicles script. 250 places in the first round (221 in the first game, 20 in its DLC, 9 in the second game) plus 13 edits in a second round. The report page went from 9 to 10 rows, the height already proven safe for that page. The widest changed dialogue line is 344 px of the 345 px limit, and no tag, page or line count changed anywhere else. The three tools that caused it are fixed so a later cleanup can't repeat it. Seen on Azahar: the three version stamps, and the first game's Episode 1 tutorial line "Find the victim in the 'People' section of the / Court Record, then touch 'Present'. Try it now."; not run on a 3DS. Everything else was checked in the files, not on screen |
| A thought (the blue text in brackets) that runs onto a second page has its second half spoken: the speaker's mouth moves as if they were talking | both games and the first game's DLC | FIXED in v1.9j. The second page started without its opening bracket, so the game read it as speech and animated the mouth. Every split thought now closes its bracket at the break and opens a new one on the next page, the way Capcom's own script does: "(Now that I'm standing in his shoes...)" then "(...I'm starting to understand something else Naruhodo-san goes through.)". Reported by GlacialSkyfarer on issue #1. 349 page breaks fell inside a thought: 293 in the first game, 6 in its DLC, 50 in the second game, 0 in its DLC. Capcom's Japanese and English scripts have none. Four breaks had split a title from its name ("Mr" / "Miss"); the title now goes onto the second page with the name. The wording puts an ellipsis at each side of the break, and plain brackets where the first page already ends a sentence. The widest changed line is 330 px of the 345 px limit, and no page gained a line. Seen on Azahar in the second game (Episode 1, Trial Start: the second page's mouth moved on v1.9i and stays still on v1.9j); not run on a 3DS. The first game's pages and the DLC's were checked in the files, not on screen |
| On some centred pages (narration, flashbacks, place and time cards, thoughts, a few choices), a line further down the page sits against the left edge while the line above it stays centred | first game, its DLC and the second game's DLC | FIXED in v1.9h. 18 pages in the first game, 5 in its DLC and 6 in the second game's DLC, the last six inherited from the earlier fan patch. Seen on the first game's Episode 5 opening page, in the line "Our first two months in / London passed by in a flash.", confirmed centred in an emulator. The first game's DLC "Telegraphic Supplement" headline, one of the 5, was seen in an emulator, both lines the same orange and both centred; not yet checked on a 3DS |
| A DLC newspaper headline types its second half at a different speed than the first | first game's DLC | FIXED in v1.9h. The headline is split over two pages and the second restated the speed from the top of the first page instead of the one in force, the same split-page speed bug v1.9g fixed elsewhere, missed here. Not a word of dialogue changed. Not yet seen on screen |
| A thought (the blue text in brackets) that runs onto a second page shows the second half in plain white speech instead of blue | both games, mostly the second | FIXED in v1.9g. Splitting a page onto a second page restarted the renderer without saying again what was running at the split point, so a thought in progress was lost. 26 pages in the second game and 2 in the first did this |
| A phrase in red that runs onto a second page loses its red on the second page | second game | FIXED in v1.9g. Same cause as the thought-color row above: red is state that has to be re-said on the new page, not a one-off cue, and the split wasn't re-saying it. 4 pages did this |
| The second half of a split page types at a different speed than the first half | both games, mostly the second | FIXED in v1.9g. The split was re-stating the page's starting typing speed instead of whatever speed was actually running at the split point, so a speed change partway through page one didn't carry onto page two. 104 pages in the second game and 1 in the first did this |
| The location card that pops up when you arrive somewhere has its description, or the place name, running off the right edge | both games, arriving anywhere | FIXED in v1.9f. That card's own width had never been checked: in the first game 14 of 33 titles and 36 of 44 descriptions ran past the proven width, and in the second game 28 of 45 titles and all 30 descriptions did. Descriptions are re-broken to fit with room to spare, not a word changed; where a description still didn't fit, it was given a small wording trim, and long place names are squeezed to fit rather than shortened. Seen fixed in an emulator on the ship in the first game; the second game's cards have not been reached on the test save |
| A line in a second game's autopsy report or case document runs off the page, often mid-word | second game, post-mortem and case documents | FIXED in v1.9f. 24 lines in these full-screen document pages ran past the panel's real width, which had not been measured before; re-broken to fit, not a word changed. Seen fixed in an emulator on the first episode's autopsy report |
| A first-game evidence name, a Dance of Deduction question, or a dialogue page runs past its box | both games, scattered | FIXED in v1.9f. Two evidence names and two Dance of Deduction questions in the first game, and one of Susato's remarks in the second, were shortened slightly to fit; a handful of dialogue pages, including the first game's "Queen's English" tutorial page, are re-broken. Not a fact changed |
| A lowercase t in the first game's DLC Picture Book commentary looks like a stem with a foot rather than a proper crossbar | first game's DLC | FIXED in v1.9f. That font's t had almost no left arm on its crossbar at the size the commentary is set. Only the t was redrawn; no descriptions or line breaks changed |
| The t in a first-game DLC menu heading such as "Picture Book" reads almost like an f | first game, DLC menu | FIXED in v1.9f. The game drew those headings slightly shrunk, and the shrinking blurred away the left half of the t's crossbar. They're drawn at full size now, a little bigger, and every heading still fits its ribbon. Seen on a 3DS, including with the 3D slider at max |
| A capital T, V or W leaves an odd-looking gap before the next letter | both games, including the DLC stories | FIXED in v1.9f. The gap after those three letters is a pixel tighter now, in both games' dialogue font, including each game's own copy of it inside the DLC |
| A lowercase w leaves a sliver of extra space before the next letter, so "was" reads closer to "w as" | the second game's main story | FIXED in v1.9i. The second game's dialogue font gave w one more pixel of room than the first game's and the DLC's; it now matches them, so lines only get narrower and nothing moves to a new line |
| A name at the top of a second-game evidence or profile card looks squeezed together | second game | FIXED in v1.9f. That heading's letter spacing is fixed so the letters no longer crowd each other |
| A line in the speech bubble on the bottom screen is cut off at the right edge, often mid-word | both games, partner talk while examining evidence and in the Dance of Deduction reviews | FIXED in v1.9e. That bubble is narrower than the dialogue box above it, and the width checks only ever measured the top box. Every line in bubble mode was measured with each game's own font and re-broken to fit with room to spare, not a word changed; where two lines weren't enough the page was split in two, the way the game's own continuation pages are built. Seen fixed in an emulator in the first game |
| A Dance of Deduction note card shows one stray letter for its topic, and the conclusion stays blank while the typewriter sound plays | both games, every Dance | FIXED in v1.9d. The card types its title and conclusion in two fonts of its own, and neither had English letters: the title font had only capitals, the conclusion font only the Japanese characters the original needed, so "Intruder's Identity" drew as its capital I. Both fonts now carry Capcom's English lettering from Chronicles, scaled so the longest title and conclusion fit the card. Seen on the card in an emulator in the first game |
| A DLC Music and Sound gallery title runs past its plate | first game's DLC, issues 1 to 8 | FIXED in v1.9 |
| A "Bonus voice recital" track in the DLC Music gallery plays in Japanese | first game's DLC | FIXED in v1.9 for four of the eight. Capcom's English recordings exist for them and are in now, checked on the rig |
| A lowercase t looks broken, or "Picture" reads "Picturc", on a DLC menu heading | first game's DLC menus (the same letters in the second game) | FIXED in v1.9b, redone in v1.9c. The headings use the fan patch's menu font, whose t and e crossbars are one pixel thin; the game draws the headings slightly shrunk and smoothed, and the thin bars vanished. v1.9b thickened both letters but pushed their bottoms a pixel below the line, so the e grew a small tail in lists and dialogue. From v1.9c only the crossbars get a light extra row, and the i, j and l, which read a shade heavier than their neighbours, are slightly lighter. Nothing else in the font moved. Checked on the emulator in the Sound gallery, the DLC headings and the music notes |
| A closing quote mark or a punctuation mark shows as a blank space | first game and its DLC | FIXED in v1.9. A handful of characters, mostly curly closing quotes in the DLC gallery text plus a few punctuation marks in the first game's own text, aren't in any of the game's fonts. Replaced with characters the fonts do carry |
| A "Take that!" comes out in Japanese | second game's DLC, two shouts | No English recording exists for these two. Same class as the four base-game shouts above |
| The gallery text for DLC issues 9 to 13 is Japanese | first game's DLC | FIXED in v1.9c. It's Capcom's placeholder text for issues that were never released ("Track 1 title (provisional)", notes to their own team, two unreleased episode titles). It's in English now and still reads as placeholders |
| The last word or two of a page sits under the page arrow | second game, 38 pages | 13 are a single scream that overflows in Japanese too, and 25 end without a wait marker, so they can't be split without inventing a pause Capcom didn't write |
| A centred banner or heading looks tight against the box edge | first game, 4 pages | One single-word page at 357 units and three identical widget pages at exactly 365. The widget box's own width was never confirmed on screen, so these may not be overflowing at all |
| A line in the fancier, more decorative face runs past the box | first game | Mostly FIXED in v1.9c. The wrapper measures those lines with the other font's metrics, so it wraps them too late ([senyarom issue #7](https://github.com/senyarom/tgaa2-en-patch/issues/7)). Measured across all 126 entries that use the face, four sentences ran over; the worst, in the second Dance of Deduction of Episode 2, put its "!" on the box frame and is re-broken, and a stray space is gone from three. Two lines in the same Dance still end a little under the page arrow; fixing those would need a page break Capcom didn't write |
| The end credits are entirely in Japanese | second game, all 75 cards | Deliberate. The PC release lays them out differently and can't be ported, and a misspelled credit is worse than an untranslated one |
| The DLC menu icons have smudges under the pictures | first game's DLC list | FIXED in v1.9c. The clean icon sheet from v1.7 was replaced by the older one again in v1.8b, because that update was built from a copy of the game files that still held it. The v1.7 sheet is back |
| Picture Book commentary is hard to read at its size | first game's DLC | FIXED in v1.9c on 51 of the 66 pages: the text is usually two sizes bigger, with the see-through panel behind it extended to fit, and faint Japanese that showed behind the English on several pages is gone. The other pages were already as large as their space allows |
| Japanese writing on the artwork inside the Picture Book | first game's DLC | Brush-written name tags and small production scribbles on the design sheets were left as they are |
| The tips of the pencil hair look clipped on a sketches page | first game's DLC, issue 6 | They share pixels with the Japanese writing. Every rule that kept the hair also left readable Japanese, so the tips stay clipped |
| The title card reads "D L C", one letter per slot | both games | FIXED in v1.9c. The card reads "Extras" sideways like Continue and Select Episode, without the diamonds, and turns white when pressed instead of going dark |
| A Court Record profile or caption is drawn small and soft, and thin strokes drop out | both games | The panel shrinks the type rather than clipping it when a caption is too long, so this is what a caption that doesn't fit looks like. FIXED in v1.9 for the first game: every one of its captions was re-measured in the font the panel actually uses, which is not the dialogue font, and the ones over the line were re-wrapped or given a small wording trim, so they all fit at full size now. The second game's captions haven't had that pass yet. If you're looking at a shrunk one, in either game, I want to know which character |
| A full-screen document or report page has text running off the edge | first game | FIXED in v1.9. Sixteen pop-up pages had a line too long for the box; re-wrapped, not a word changed, and checked on the rig. If you hit another one, a photo would help |
| A crackle over the voice in the animated cutscenes | first game, all seven cutscenes | FIXED in v1.8b. Capcom ships the cutscene sound as three separate pieces, the music, the effects and the voice, and my build adds them together. The total came out louder than the file can hold, so the loudest instants had their tops chopped flat: 126 times in the 61 second opening, and in all seven cutscenes. Found in September 2026 from a phone recording made on a console, after three offline checks had passed the broken build |
| A fine grain, like faint static, over the animated cutscenes | first game, all seven cutscenes | FIXED in v1.9. This was written down here as an unfixable format limit, and that was wrong. My own audio tools were writing every English track into the file a few bytes out of position, so the console read each one slightly late, and the grain was the sound of that misread. The tracks now start where Capcom's do. Confirmed by recording the opening in an emulator before and after; the second recording has no grain. Not yet heard on a 3DS. Same root cause as the crowd sounds, the voice-line click and the cut-off voice lines below, and nothing to do with the crackle fixed in v1.8b, which was a separate bug |
| A courtroom crowd sound, like the murmur around the closing arguments, plays back scrambled | both games | FIXED in v1.9. Same misalignment as the cutscene grain, and two crowd sounds in each game were also stored in the wrong channel layout, which is what made those ones scramble rather than just hiss. Every replaced sound in both games and their DLC has been moved back into position |
| A crowd chant or the courtroom murmur goes quiet for a stretch, then jumps back in as it repeats | both games | FIXED in v1.9. Two looping crowd sounds in each game had their loop points set wrong since earlier releases, so each repeat played a silent stretch and then jumped; the chant also had a couple of tiny clipped peaks. Both now loop where Capcom's English recordings say to, and so does the second game's Episode 5 chant, which is new in this release. The murmur dips a little at the start of each cycle; that is in Capcom's recording, not a defect. Checked by decoding, not yet heard in-game |
| A faint click at the end of a replaced voice line | both games and their DLC | FIXED at the root in v1.9. v1.5 stopped the click by giving every replaced clip a silent tail, which worked, but the real reason the console was reading past the end of the clip was that the clip had been written a few bytes early. The clips are written where Capcom writes them now |

**Not on this list and worth knowing:** nobody has played either main game the whole way
through on a console. 32 of the first game's shouts, the jury verdicts and the pressing
voices, have never been heard by anyone in any build on any platform. If you play the first
game, a verdict or a press that stops part way is the single most useful thing to listen
for. The full picture is in the testing status table further down.

---

The first game's number jumped from `1.0.19` to `3.2.1` in v1.4. That is not nineteen
missed releases. The 3DS stores a title version in a field whose last part cannot go
above 15, so `1.0.16` and up were never real versions: the files were named `1.0.x`
while the console was told something else, and the two had drifted apart. From v1.4
the first game's number on the screen, in the filename and in the console are the same
number. The second game keeps `1.0.x` on screen and in the filename, but from v1.5 the
console is told `3.x`, because Capcom's own update for it is
`1.3.0`, and a lower number is what made consoles offer that update over the patch. v1.5
was `3.0.15` to the console; v1.6 was `3.1.0`, because the last part cannot go above 15.

Both title screens now show Capcom's own *Adventures* and *Resolve* logos instead of the
fan-drawn ones, so the logo alone tells you the update took. If you want a text check as
well: in the first game's opening cross-examination the first statement should read *"I
was ingesting regulation beef steak at the restaurant in tactical discussion with the old
man."* on **two** lines. Three lines with the third cut off means the update did not
install.

---

## What this adds on top of senyarom's patch

**What is theirs:** the layout pipeline, the font handling, and the carry of Capcom's
official *script* onto the Japanese 3DS builds. That is the foundation, and it is the hard
part of the problem. Nothing here replaces any of it.

**What is here:** senyarom's patch brings Capcom's text across. This brings across the
rest of what Capcom made, the parts that are not text at all: the English voice acting,
the videos, and the art. On top of that, the DLC that nothing had ever translated, and the
layout bugs that only turn up by playing.

### 1. The DLC, which no English release had ever covered

Every previous effort stops at the base games. Scarlet Study's translation and senyarom's
patch both leave the DLC in Japanese. Even the mod that ports the 3DS DLC across to the
Steam release says in its own readme that the mini-cases are untranslated, and that no
text will be displayed during them at all.

So this is the part that did not exist anywhere before:

| | |
|---|---|
| **2** | mini-episodes in the second game, fully translated and playable |
| **46** | gallery voice clips in the first game's DLC, in Capcom's English rather than Japanese |
| **34** | shouts in those mini-episodes, which had been speaking Japanese over English text |
| **11** | commentary videos in the first game's DLC, subtitled and re-encoded to Capcom's own container spec |
| **14** | magazine covers in the first game's DLC: 9 rebuilt from the official *Chronicles* banner art, 5 relabelled so you can tell the empty issues from the playable one |
| **3** | DLC banners and the icon labels redrawn; the two story banners re-titled on artwork adapted from Capcom's (v1.4) |
| **4** | event pictures in the second game's DLC that were still Japanese: the opening "work of fiction" card and a handwritten score sheet in three views, re-typeset in English at the photograph's own angle and focus (v1.4); the score sheet's paper cleaned of a dark band and leftover brush specks (v1.7) |
| **76** | pages in the first game's DLC that were still Japanese images: 66 Picture Book pages of the art director's commentary with the handwritten notes on the design sheets, 8 theme preview titles and 2 Editor's Notes pages, all now in English (v1.7, see below) |
| **29** | of those Picture Book pages where the commentary sits on a see-through panel over the artwork, redone so the artwork under and around the panel is Capcom's own rather than a blurred repaint (v1.8, see below) |
| **1** | DLC list icon sheet redrawn from Capcom's Japanese plate, because the earlier English sheet cut off the bottom of all 18 icons; the Episode 0 cover and the five empty-issue covers got a cleaner fill behind their titles (v1.7) |

**The playable sample was translated by hand.** The first game's DLC magazine carries a
playable demo as issue No. 13: Episode 1's opening, the Court Record tutorial and a
cross-examination, around **11,300 characters across five script files**. No patch had
translated it. It was done from the Japanese by hand for this release, and it is the one
part of this project that is an original translation rather than a port of Capcom's work.
Issues 9 to 12 turned out to be empty stubs that open and immediately exit, so their
covers are now labelled as such and No. 13 is labelled as the playable one.

**The Picture Book, theme titles and Editor's Notes are new translations too (v1.7).** Their
buttons used to throw you back to the title, so nobody had seen them in English; once they
opened, every page turned out to be a Japanese image. *Chronicles* has no Picture Book, so
there was nothing of Capcom's to port. The English was translated from the Japanese with
Claude's help, reviewed against a second model, and every character name checked against
Capcom's spelling. The commentary is set in one condensed sans serif, the handwritten notes
in a handwriting face, the theme titles in the serif of the Japanese titles. On the 29
pages where the Japanese sat on a see-through panel over the artwork, the covered part of
the art was filled in with an image inpainting model (LaMa) and only those pixels were
changed; everywhere else the page is Capcom's image untouched. Brush-written name tags and
tiny production scribbles on the sketches were left in Japanese.

**Those 29 pages were redone in v1.8, and no model paints them any more.** The mask grown
around each Japanese character ended up covering about three quarters of the panel, because
the characters sit two to four pixels apart and the mask closed the gaps between them, so
the inpainting model was repainting the whole panel and inventing the picture behind it.
That showed as a smeared band along the top of each panel and as characters' legs turned
into pale smudges. Nothing is repainted now. What the panel looks like without the writing
is estimated from the pixels that are not writing, and each pixel is faded towards that
estimate in proportion to how much darker than it it is, so the ink lifts out and the
drawing stays. The English also sits on the row Capcom's Japanese started on rather than a
few rows lower, which is what left the pale band. Every row above the first line of text on
those pages is now byte-identical to Capcom's own page. One page is still not right: on the
rough sketches page in issue 6 the tips of the pencil hair share pixels with the writing,
and every rule that kept the hair also left readable Japanese, so the tips stay clipped.

**Why the buttons bounced.** The DLC screen checks a DLC status byte before it opens the
Picture Book, Theme or Editor's Notes, and turns back to the title if the byte isn't zero.
Traced live in an emulator, the byte read 5, set by a background DLC request that comes back
with an error code. senyarom's offline DLC patch skips that check in the two places the rest
of the DLC list goes through; the same check sits in three more places, and those are the
ones these three screens use. v1.7 skips it there the same way: three branch instructions
in the update's code, nothing else. Capcom's Japanese update has the same code in this
area, so the check itself is Capcom's; as far as I can tell it only trips when the DLC
runs without Nintendo's servers behind it.

**And where Capcom localised a piece of the DLC, this matches Capcom word for word.** One
scene exists in *Chronicles* as official English, which makes an exact check possible:
comparing box by box, **140 of 190 are byte-identical**, and every remaining difference is
either a line wrapped to fit the narrower 3DS box or a curly quote the 3DS font does not
carry. Not a paraphrase of the official text. The official text.

### 2. English voices, in both base games as well as the DLC

Capcom re-recorded the whole cast for *Chronicles*. senyarom's patch is a text port, so
none of those recordings came across: both games still shouted in Japanese over English
text, all the way through the main story.

| | |
|---|---|
| **81** | courtroom shouts in the first game, now Capcom's English, across 41 replaced character archives |
| **25** | story voice clips in the first game |
| **85** | courtroom shouts in the second game |
| **235** | story voice clips in the second game |
| **46** | gallery voice clips in the first game's DLC |
| **34** | shouts in the second game's DLC mini-episodes |
| **7** | animated cutscenes in the first game |
| **20** | narration slots across the first game's episode openings |
| **20** | courtroom crowd and reaction voices in the second game that Capcom recorded in English and no build had ever used: six streamed gallery and courtroom cues, and fourteen gasps, efforts and cries during the third episode's Dance of Deduction (v1.4) |
| **6** | the same six courtroom cues in the first game (v1.4) |

Those 26 had been invisible to every earlier audit for a reason worth writing down:
Capcom tags only the English file (`_eng`) and leaves the Japanese one untagged, so a
search for a Japanese twin found nothing and concluded the English was an orphan. A
whole-install count of all 526 English audio files in *Chronicles* against the four
builds is what found them.

**Pauses, not fidelity, pay for the fit.** A streamed clip has to fit Capcom's slot in
bytes, and bytes scale with duration times sample rate. Where an English take runs long,
the silence *between phrases* is shortened rather than the sample rate lowered, so the
speech itself is untouched. 24 clips that previously had to drop as low as 75% of full
rate now play at a higher one, 17 of them at full, and 3 lines that were left in
Japanese are now English. Pauses are never cut below 150 ms: shorter than that swallows
the breath marks in a fast delivery and the read sounds spliced, which was confirmed by
listening rather than assumed.

v1.9 reverses this. The "fit" was never real: a clip written where the game reads it
plays in full at any size. The 27 second-game lines whose pauses had been shortened have
their pauses back, and the lines that had been stored at reduced quality are at full
quality again.

**The second game was the gap, and it is now closed.** It shipped with ten English clips
covering two characters, while every other voice in it, shouts and story lines alike,
stayed Japanese over English text. There were two separate systems to fix and finding the
second one took someone playing the game and asking why a character sounded wrong.

What is still Japanese, and why:

| | |
|---|---|
| **54** | Capcom never recorded an English take. Verified exhaustively rather than assumed: *Chronicles* ships 288 English voice files and every one of them matches a 3DS clip name, with none left over, so there is no alternate naming convention hiding a recording. |
| **18** | Were left Japanese through v1.8b because the English take runs 1.4x to 3x longer than the Japanese one and a longer clip was believed to get cut off in-game. English since v1.9: the cut-off was my file misplacement bug, not a size limit. |
| **4** | Courtroom shouts for two minor characters, an *Objection!* and a *Hold it!* each, that Capcom never re-recorded in English. Their archives were checked member by member: 104 shouts live inside the character archives, 100 have a *Chronicles* master, these four do not. |
| **1** | A second gallery chant in the second game, left Japanese through v1.8b because Capcom's English runs far longer than the Japanese and a longer clip was believed to get cut off. English since v1.9: the cut-off was my file misplacement bug, not a size limit. Checked offline only. |


The episode openings needed their own approach. Capcom re-recorded the narration for
English in ten takes where the Japanese has twenty lines, so one English take spans two
of the game's pages, and each page has a fixed display window that cuts anything longer.
Lowering the sample rate shrinks a file without shortening it, so the takes are split at
the sentence break and time-compressed with the pitch preserved. Two pages turn out to
have a window shorter than Capcom's own audio, which is why their Japanese never plays
either.

Three splits land mid-word and carry a short fade. A clean break exists for each, but
only by pushing a half to around 65% of full quality, which is more noticeable than the
seam it would fix.

v1.9 changed this for the first game's Episode 2 opening. Instead of squeezing the takes,
the halves played at natural speed and full quality. That fixed the rush and introduced a
smaller problem: each page's English is in two halves, and the second half was still
started by the cue the game uses for the Japanese second line. The Japanese lines don't
break where the English sentences do, so on five pages the second half sat waiting for
half a second to over a second, three times in the middle of a sentence or a word, and two
pages felt rushed for the same reason.

Capcom's PC release has its own English timing for this scene: the same page timing as the
Japanese, with one continuous read per page. v1.9a follows it. Each page's second half now
follows the first after the recording's own natural pause, and the page turns, art and
music are back on Capcom's original timing. The old and new timing were compared by ear
before this went in, and it was then recorded in-game: nothing is cut off and nothing
overlaps. The other episode openings in both games play one piece per page and already
match the PC timing, so they didn't need this. The Japanese-voice edition keeps the
Japanese timing on purpose, because it plays the Japanese recordings.

If you play the second game and hear Japanese where you expected English, that is this,
and it is expected rather than a broken install.

Getting the DLC's clips to play was the harder half. They came out silent or truncated,
and the reason was not obvious:

**A voice stream larger than Capcom's original is cut off in-game, and not at the
original's length.** It stops at an unpredictable point, and how far it overshoots does not
predict where it stops. Measured by metering the speaker, not by reading the file:

| my clip | Capcom's slot | actually played |
|---|---|---|
| 4.10s | 3.81s, over by 0.29s | **0.98s** |
| 4.47s | 3.91s, over by 0.56s | **1.86s** |
| 5.44s | 3.32s, over by 2.12s | **2.77s** |
| 9.04s | 9.18s, fits | full |
| 4.60s | 4.69s, fits | full |

Eighteen streams were oversized, because Capcom's English performances simply run longer
than the Japanese ones they replace. Trimming to fit would have cut words, over two seconds
off one line. Instead the space was bought: edge silence trimmed but never the pauses
inside a line, and where that was not enough, the sample rate lowered just far enough for
the **complete** take to fit. The game honours the rate field, so pitch and timing are
unchanged and the cost is treble rather than words.

Eleven of seventeen kept 90% or more of full rate. **One clip is noticeably duller.** That
is deliberate, and it is the alternative to losing the end of the line.

v1.9 retracts the rule above. The cut-off was real, but its cause was the misplacement
bug described under the cutscene grain, not the clip's size: the tools wrote every clip a
few bytes before where the game reads, and how far into the clip the read went wrong
depended on the audio, which is why the cut point looked unpredictable. A clip written at
Capcom's position plays to the end at any size; one 61% larger than Capcom's was played
three times in an emulator and was complete each time. All 16 rate-reduced clips and the 3
trimmed ones are back at full quality and full length.

**The pop at the end of shouts (found v1.4, fixed v1.5).** The hardware tester heard a
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
copy, not the DLC's own, which is why fixing the DLC alone had changed nothing.

v1.9 found why the clips were past the boundary in the first place: the tools were writing
every imported stream a few bytes early in the file, so the console's read ran past the
true end. The streams are written at Capcom's position now, and the silent tail stays as a
belt and braces.

v1.9 also fixed where three crowd sounds loop: the courtroom murmur and a long crowd chant in
both games, plus the second game's Episode 5 chant, which is English for the first time. The
old import took each loop point from the Japanese recording and stretched it to the English
one's length, so every repeat ran into a stretch of silence and then jumped back in. The loop
points now come straight from Capcom's English recordings, and each stream ends where Capcom
ends its own. The murmur is also about 1 dB louder than before, back at the level of Capcom's
English file, and the long chant lost a couple of tiny clipped peaks. Capcom's English murmur
starts its loop inside a short fade-in, so it dips a little each time round; that's in the
original recording. These were checked by decoding them on a PC. The loops haven't been heard
on a console yet, and the Episode 5 chant can't be reached on the test save.

#### The English manual (v1.9o, pictures retaken in v1.9q)

The short version: the manual you open from the HOME menu is English now, in both games. [Issue #4](../../issues/4) asked for it. Before, the update carried no manual of its own, so the HOME menu showed the Japanese one that comes with the base game. The text is Scarlet Study's fan translation of the manual (their builds are the first game's version 2.4.1 and the second game's 2.1.0), which I revised in place.

What I changed in the text: names and terms follow the game and Capcom's *Chronicles*, so it says Ryunosuke Naruhodo, Herlock Sholmes, Dance of Deduction and Summation Examination where the older text had Naruhodou, Holmes, Joint Reasoning and Closing Argument, and People where it said Profiles. The first page is a short disclaimer saying the manual belongs to a fan patch and that Capcom and Nintendo have nothing to do with it, and the notes pages at the back have an About This Patch page and a list of the names and terms. A few of the titles in the HOME menu's index are shortened to fit.

What changed in v1.9q: the manual's screenshots were the older fan translation's English ones, so I retook the main ones in the patched game, 13 pictures in the first game's manual and 11 in the second's. They cover the title screen, the backlog, pointing in the Dance of Deduction, the Move menu, the Court Record and Present screens, the summation review and the notes. The title screen picture has the patch's version stamp taken out so it can't go stale. The Cross-Examination heading picture now has its hyphen, as Capcom's English writes it. The Summation Examination page shows the six-juror view in the second game; the first game's page shows a close-up of Ryunosuke instead. The About This Patch page now says: "The main screenshots were retaken in the patched game. The logo, a few headings and diagrams are from the older fan manual, so some words may differ. The written text matches the game."

What I haven't done: the logo, a few headings and some diagrams are still the older fan translation's pictures, so a few still show older names, and the first game's Summation Examination page has no jury picture. I plan to redo them as a separate piece of work.

How it's built: the manual is a second content inside each update CIA, next to the game itself, which is the v1.9n build apart from the version stamp. In v1.9o it was 2,023,424 bytes in the first game and 1,994,752 in the second; the v1.9q manual is a different size. The update's version moved to 3.4.0 for the first game, because 3.3.15 was the last number its version field could hold, and the second game's moved to 1.0.30. **Not seen on a 3DS:** this is the first time I've added a second content to one of these CIAs, and no 3DS has opened it. In the emulator the HOME menu viewer shows both manuals correctly when they are put where it looks (it reads the manual from the base game, so it ignores the update's copy), which checks the pages but not the delivery. The patches were proven the same way as every other release, and the Japanese-voice edition carries the same manual. v1.9q changes only the manual and the version numbers (the first game's update is 3.4.2, and the second game's is 1.0.32 by file name and title screen stamp, though an installer reads its version as 3.2.0): it opens and renders in the emulator's HOME menu viewer in both games at both text sizes, the manual packs and unpacks to the same files, and both updates pass a structure check. Nobody has opened it from the update on a 3DS.

#### The shout sound effect (v1.9n)

The short version: when a character shouts "Hold it!", "Objection!" or "Take that!" in Capcom's Japanese files, a short metallic "shing" plays with the voice. Capcom mixed it into the shout clips themselves, so the English recordings, which came without it, played as the voice alone. v1.9n lays the same sound under the English shouts again.

How I found it: the last second or so of many Japanese shout clips matches the "shing" recording (correlation above 0.9 against the effect's own file, which is the same file, 29,487 samples, in both games), and the English clips match it at about zero (0.07 or less in the first game and the second game's DLC). The effect is in 40 of the first game's 97 shout clips, 69 of the second game's 114 and 83 of its DLC's 91, and in none of the first game's DLC clips (that DLC's voice streams are all gallery clips). Fitted against the effect, Capcom's level comes out between 0.3 and 0.5 of the effect's recording, median 0.402, and I used 0.402 on every clip.

What v1.9n replaces: 186 English clips, 40 in the first game (22 sound archives), 65 in the second game (30 archives and 9 loose files) and 81 in the second game's DLC (18 archives and 4 loose files), 70 archives and 13 loose files in all. Each new clip keeps the Japanese clip's header, length and file size, so none is larger than Capcom's. Six shouts that carry the effect in Japanese are not in the English update at all (4 in the second game, 2 in its DLC, named in the list at the top) and stay Japanese. Capcom's clips line the effect up at sample 0 on 179 of the 192 I measured and within 35 samples on the rest; I started it at sample 0 everywhere.

The level problem: the English voice already peaks at full scale, and voice plus effect would peak at 38,000 to 46,000 against a ceiling of 32,767, so a plain sum clips. I rendered two fixes on a PC and compared them. Option A turned the voice down by 1.2 to 4.6 dB (median 3.0) depending on the clip, so every shout got quieter by a different amount. Option B, the one shipped, leaves the voice alone and runs a soft limiter over the sum (starts at 32,000, 5 ms attack, 100 ms release, one setting for every clip). It pulls the level down by at most 0.77 to 3.06 dB per clip (median 2.11), over roughly a fifth of a second around the "shing"; away from those stretches the voice is within 0.15 dB of v1.9m's. Capcom's own voice, with the effect taken out, sits about 0.8 dB below mine, so turning mine down as well would have put the shouts further under Capcom's level. After encoding, every clip correlates with the intended sound at 0.9988 or better, and two separate decoders agree sample for sample on the decoded clips.

Archive size: the clips are the same size as Capcom's, but the sound archives that hold them grow, because each new clip is longer than the English one it replaces. Three character voice archives now end larger than Capcom's own Japanese archive by more than any of that kind did in v1.9m: the first game's `chr413_jpn.arc` (+19,281 bytes as stored, +23,552 unpacked; v1.9m was +12,278), the second game's `chr434_jpn.arc` (+11,363, +14,528 unpacked; v1.9m +1,486) and the second game's DLC `chr614_jpn.arc` (+10,049, +13,376 unpacked), the first DLC archive over its Japanese counterpart (v1.9m was under it by 13,538). I don't know whether the game's loader has a limit per archive, and nothing has been run on a 3DS, so those three are the ones to listen to. No index file names a clip, and none changed.

Checks: all 186 clips read back from the built CIAs are byte for byte the staged ones. Seen on the emulator: the first game's "Hold it!" and the second game's DLC "Objection!" cut-ins play with no crash. The sound itself hasn't been heard by me or anyone on any device. The Japanese-voice edition is unchanged in audio; its rebuilt archives hold Capcom's own clips, checked member by member.

### 3. Text that fits the box, and a font that behaves

Most of the work after the DLC was layout, and most of it is in the **story text**, not
the Court Record: dialogue running past the edge of its box, glyphs colliding, captions
rendering soft, menus in the wrong face.

| | |
|---|---|
| **164** | Court Record captions across both games (68 and 96) rewritten to fit at full size. The panel silently shrinks its font rather than clipping, so long captions rendered small and soft instead of looking broken |
| **1,438** | pages of story dialogue re-broken at the corrected font metrics, which added 124 pages of pagination. Includes the centred pages that overran the box, some running clean off the screen |
| **43** | glyph advances corrected in the second game's dialogue font, including a tuck for overhanging T, Y and L. This affects every line of text in the game, not one screen |
| **0** | end-credit cards in the second game. 15 were briefly English; they were reverted so all 75 are Japanese, because a translated block sitting inside an untranslated roll reads as a bug. See known issues |
| **42** | menu strings in the second game that fell through to a decorative script and were genuinely hard to read: Yes/No, OK, Cancel, Examine, Move, Converse, Present, every game-over option |
| **19** | voice clips in the first game's DLC cut off mid-word, per the section above |
| **202** | cross-examination statements re-laid to the statement box's real width: 65 in the first game (v1.2), 133 in the second and 4 in its DLC (v1.3). That box is narrower than the dialogue box, because the arrows that step between statements sit inside it, and every earlier build had laid statements out against the wider measurement, so the longest lines ended on the border with their last character cut. 17 only needed a new line break; 48 were shortened by the smallest edit that fits, checked against the Japanese. Found by watching Episode 1 played on the patched build, screen by screen; the second game's box was measured in-game with its own font before anything was changed |
| **16** | evidence and profile descriptions in the second game that the evidence pop-up card drew oversize and cut off. They carried a size tag the Court Record panel honours and the pop-up does not; shortened to fit at normal size in both (v1.3) |
| **1** | save/load screen drawing the timestamp straight through the episode title |
| **1** | pagination regression that had inflated the script by 6,855 pages |
| **1,635** | page breaks the translators had added that Capcom's Japanese does not have, joined back into one page now that the real box width is known (v1.4): 26 in the second game's DLC, 114 in the first game's DLC, 1,493 in the first game, 2 in the second. A break was only undone where nothing but the standard page tags sat on it and the joined words fit two lines with room to spare; the rest, where the English is genuinely too long for one page, stay split |
| **62** | of the 66 centred banners, sized text and other widget pages in the first game that ran past the box edge, up to 404 units against a 365 box: 43 re-broken, 19 split into two pages (v1.4). The 4 left alone are one single-word page measuring 357 units (`_sce01_c005_0007`, L_3D_SEARCH_0_PRES page 22) and three identical widget pages measuring exactly 365 (`_sce03_c004_0004` L_2_START and L_2_REPEAT_1, `_sce03_c004_0007` L_UPDATE_1, page 6 of each). The widget box's own width was never confirmed on screen, so those three may not be running past anything; none of the four has been seen clipping on a console |
| **9** | lines in the second game's DLC that ran off the page, found by the hardware tester, re-split or re-wrapped without changing a word, one of them a case document taken from 384 to 336 units; plus three hand-placed breaks Capcom had put inside a decorative script restored, and one page that had grown to three lines split in two (v1.4) |
| **1** | profile caption in the second game's DLC that was five lines in a four-line box, so the game shrank it and thin strokes dropped out; condensed to four (v1.4) |
| **1** | save-slot title in the second game, Episode 1's, the longest of the five, that ran off the slot's right edge on a console; the "Ep. 1:" label is now drawn a step smaller so the title fits at its normal size, and the chapter line under it, which the game was squeezing to fit, now renders one size down and unsquashed. Seen on screen (v1.5) |
| **2** | system messages in the second game, the return-to-title confirmation and its game-over twin, whose longest lines were the two widest of any dialog in the game, so the box squeezed the whole message sideways until the apostrophe vanished; re-broken onto four and three lines, no words changed. Not yet seen on screen, see the status table (v1.5) |
| **7,320** | of the 7,358 pages of ordinary dialogue in the second game that ran under the page-advance arrow (v1.4). The whole game had been wrapped to the edge of the box, 365 units, when the arrow that ends every line sits at 345, so the last word of every long line was drawn under it. Measured on the game's own font and calibrated on screen before anything moved: 344 units touches the arrow, 351 passes it. 5,828 pages only needed their line break moved, 716 single lines became two, and 776 pages that cannot fit two lines at all were split into two pages the way Capcom's own continuation pages are built. Words were never changed, and every event and animation marker in all 8,117 script entries is proven to be in its original place. 38 pages are left alone: 13 are a single scream that overflows in Japanese too, and 25 end without a wait marker, so they cannot be split without inventing a pause Capcom did not write |

The scale of that is easy to understate. Diffing these builds against senyarom's release
file by file, **854 script files differ across the four builds**: 363 in the first game,
431 in the second, 60 across the two DLCs. That is not 854 separate translations, and it
should not be read as one. It is the font-metric and reflow work rewriting line breaks
through nearly every script in both games, which is why it had to be null-tested rather
than eyeballed.

Every one of these was found by a person looking at a screen or listening to a speaker.
**None were found by an offline check**. The automated audit passed a build in which one
line was silent and another was cut in half, and it did so because a path comparison
silently matched nothing. That is why this release asks for playtesters rather than for
more tooling, and why the testing status below is written the way it is.

#### The Present and Examine question (v1.9n)

The short version: in the 3D investigation the game shows a question with the Present and Examine buttons, and a few of those questions were too wide for where the game draws them, so the end of a line was cut off partway through a word. The text is drawn in its own widget, which runs further right than the speech bubble, and none of my width checks had ever measured it. v1.9n re-breaks the six longest questions so every line fits.

The measured part: the safe width for these lines is 290 px, and the widest line I rebuilt is 281 px. Three pages are split into two (the same way the game's own continuation pages are built, with the page's own typing-speed tag repeated), and three get a new line break only. The pages, with each line's width before and after:

| game | script file | before | after |
|---|---|---|---|
| first | `_sce02_c107_0001` | "Point out what it is that proves the victim / fell from the roof deck through the skylight!" (289, 307) | page 1: "Point out what it is that / proves the victim fell" (165, 146); page 2: "from the roof deck through the skylight!" (281) |
| first | `_sce02_c107_0005` | "Where exactly is this alleged mark that you claim / appeared at some point during the trial?" (338, 281) | page 1: "Where exactly is this alleged mark" (235); page 2: "that you claim appeared at / some point during the trial?" (186, 194) |
| second | `_sce00_c006_0050` | "The clue on this fountain pen that clearly reveals its / owner's identity is..." (328, 124) | "The clue on this fountain pen that / clearly reveals its owner's identity is..." (213, 239) |
| second | `_sce01_c104_0030` | "What's so important about the soap...is this part here!" on one line (335) | "What's so important about / the soap...is this part here!" (167, 164) |
| second | `_sce01_c104_0040` | "Where on the meter can the remnants of the method / used to make the fake coins disappear be seen?" (333, 298) | page 1: "Where on the meter can / the remnants of the method" (153, 176); page 2: "used to make the fake / coins disappear be seen?" (139, 155) |
| second | `_sce04_c102_0030` | "Where is the evidence that ties Prosecutor Asogi to / Inspector Gregson?" (325, 123) | "Where is the evidence that ties / Prosecutor Asogi to Inspector Gregson?" (195, 253) |

Only those six script entries changed in text; every other text file is the same as v1.9m. What I haven't confirmed: none of this has been seen on screen, so I don't know whether the game keeps the first page of a split question up while the Present and Examine buttons are open. If only the first page stays up, the first game's "Where exactly is this alleged mark" would read as half a sentence. I also haven't measured the second game's prompt box on screen; I applied the same limit. One more page of this kind is left as it was: the first game's `_sce04_c307_0010` (`L_TF_START_B`, the thought about "one final piece of evidence"), whose two lines measure 331 and 293 px on the 290 limit. I haven't checked whether it is cut off on screen. Not run on a 3DS.

### 4. Capcom's art where the patch had redrawn its own

The *Chronicles* release carries English versions of most of the textures that have words
on them, and where one exists it now replaces the fan-drawn one, so what is painted on
screen agrees with what the dialogue says.

| | |
|---|---|
| **2** | title logos, Capcom's official *Adventures* and *Resolve* marks in colour, replacing hand-drawn ones that still read "Ryuunosuke Naruhodou" |
| **9** | evidence cards (maps, pawn tickets, a contract; 12 textures counting the large variants) that carried fan-translation names such as "Hatch's Pawnbrokers" and "The Ragged Reader" while the text said Windibank's and Bourbon Books. Now Capcom's cards, with the red map markers restored from the Japanese originals |
| **1** | end card in the first game, which was still Japanese: now Capcom's "The Great Ace Attorney, Adventures, FIN" |
| **168** | Dance of Deduction topic plates re-rendered with Capcom's wording (74 in the first game, 94 of 104 in the second, matched through the game's own hit tables). Two plates in the second game had never been translated at all and were still Japanese; one whole stamp atlas the fan patch had missed now has English stamps |
| **1** | evidence card for Madame Tusspells, which carried a different name |
| **2** | title screens showing their real version number, and a label on the DLC title card that was blank: "D L C" at first, "Extras" from v1.9c |
| **1** | Japanese anti-piracy notice on the first game's boot, now blank exactly as the second game already shipped |
| **1** | HOME menu icon for the first game, which showed the Scarlet Study pipe logo; now the cartridge's own picture, with the English title text kept (v1.4) |
| **8** | shout atlases, the big lettering that flashes on a shout, now Capcom's *Chronicles* atlases converted to the exact format of Capcom's Japanese 3DS files, in both games. The fan set both games had shipped left the rotated second variant of the two British-court atlases in Japanese, and the first game draws that variant. Two words change to Capcom's wording with it: "Yes!" for "Sir!", "'Scuse me!" for "Hang on!" (v1.6) |
| **15** | textures Capcom localised for *Chronicles* that no 3DS patch had used: the second game's last chapter title card, and text painted onto character costumes, evidence objects and two backgrounds in both games (6 in the first, 9 in the second). Found by cross-referencing every English texture in *Chronicles* against the two cartridges; each was ported in its 3DS format with only the changed blocks re-encoded, with a base-colour-searching ETC1 encoder, the rest of every texture staying Capcom's own bytes. Still unported, on purpose: the handwritten narration strokes in the episode openings (40 textures whose alpha carries stroke timing the PC files lack), two evidence textures whose PC format does not decode reliably, and one item that is Russian on both platforms (v1.6) |
| **2** | evidence pictures I redrew rather than carried over (v1.9p): the first game's Waiter's Business Card and Medical Report Card cover, because *Chronicles* has no English version of either. See *The two redrawn evidence pictures and the capital H* below |

These were found by decoding every texture Capcom localised for *Chronicles* and looking
at each one next to the 3DS build, rather than trusting filenames.

#### Picture pass 2 (v1.9m)

The short version: after v1.9l I looked at every picture the patch changes, one at a time and at twice the size, next to the Japanese original, because the first check had been done by agents and I didn't trust it. Most were fine. Some weren't, and v1.9m fixes those.

The numbers: 370 pictures, 219 fine, 64 real defects (59 in the first game's update, 1 in its DLC, 4 in the second game's update), 82 second-game Dance label pictures that the game doesn't show (so no defect), and 5 I wanted to see on the emulator first. Pixel-identical copies (second-game pictures equal to an accepted first-game one, DLC fonts equal to base fonts) were compared by file, not looked at again. The 64 defects were 46 first-game Dance labels with clipped tails (all 74 re-lettered so they share a baseline), 8 credit pictures (the credits were then redone as a whole), 5 Dance topic pictures, 2 copies of the medical report card, the bookcase, the DLC design page and the tutorial screenshot. The two British *Objection!* pictures were on the "look on screen" list and turned out to be a real cut-off.

What changed in the build: the first game's update replaces 82 files compared with v1.9l (74 Dance labels, 2 topic pictures, the Objection picture, 5 archives holding the medical card, bookcase and credit cards) plus the version stamp in its program file; the second game's update replaces 6 (3 topic pictures, the tutorial screenshot, the Objection picture, the title screen with its new version number); the first game's DLC replaces its design page and its cover stamp. The text of the game did not change. The second game's DLC and both banner patches are carried over unchanged; the second game's DLC keeps the name `TGAA2-EN-DLC-v1.9l.cia`.

The Dance topic pictures were redone more than once. The first try used Capcom's own distressed lettering for two of the four lines, and I rejected it because it looked soft beside the fan's crisp lines. The version shipped cuts the fan's own letters out of the existing lines (putting all 55 cuts back reproduces the four lines exactly) and draws only the capital S and the capital I to match them.

The staff names that changed on the credit pictures, each as the picture read before and now (Capcom's spelling is used even where it looks odd, for example "Yutake Hukaya"; four of these, Hukaya, Kameyama, Kohno and Mizuno, I flagged as unsure because they disagree with the usual reading of the Japanese): Chieko Akitsuki to Chieko Akizuki; Tomohiko Ohsumi to Tomohiko Osumi; Oranaka Takahiro to Takahiro Oranaka; Aoi Yamamoto to Midori Yamamoto; Shintarou Kojima to Shintaro Kojima; Junshi Jodai to Atsushi Jodai; Jun'ichi Shiba to Jyunichi Shiba; Yuuki Urabe to Yuki Urabe; Uru No to Noh Eul; Yoichi Tagami to Yoichi Tanoue; Kenjirou Tsuda to Kenjiro Tsuda; Takayuki Sugou to Takayuki Sugo; Shin'ya Takahashi to Shinya Takahashi; Koichi Masuyama to Kouichi Masuyama; Yuu Seki to Yu Seki; Yuko Inoue to Yuuko Inoue; Shino Ota to Shino Ohta; Shingo Kamata to Shingo Kamada; Yasuno Masato to Masato Anno; Sho Omachi to Sho Oumachi; Yutaka Fukaya to Yutake Hukaya; Wanqian Xie to Sya Ensei; Ai Katou to Ai Kato; Tomoko Kametani to Tomoko Kameyama; Takako Kawano to Takako Kohno; Koji Ukawa to Kouji Ukawa; Mii Kawaguchi to Mito Kawaguchi; Kil Soung-Ju to KIL SOUNG-JU; Kentarou Tsubone (Real-T) to Kentaro Tsubone (Real-T); Yuuji Matsukura to Yuji Matsukura; Masao Oohashi to Masao Ohashi; Ryouichi Mizuno to Ryuichi Mizuno; Yoshihiro Iwata to Keisuke Iwata; Kousuke Kodama to Kosuke Kodama; Hiromasa Ueda to Kosei Ueda; Kenji Hashi to Kenji Tachibana; Michihiko Ezo to Michihiko Ezou; Jun'ichiro Nakajima to Jyunichiro Nakajima; Jun'ichi Tanizawa to Jyunichi Tanizawa; Ryou Nakajima to Ryo Nakashima; Yuuya Fujita to Yuya Fujita; Yuuta Takahashi to Yuta Takahashi; Takazumi Toshikawa to Kijyun Toshikawa; Yuuichirou Hiraki to Yuichiro Hiraki; Shu Shiotsuki to Syu Shiotsuki; Tomoko Ohnishi to Tomoko Onishi; Ginji Tanaka to Ginzi Tanaka; Masato Nanba to Masato Namba; Ken'ichi Noda to Kenichi Noda; Tohru Arikawa to Toru Arikawa; Eiichirou Sasaki to Eiichiro Sasaki; Masako Honma to Masako Homma; Marie Satou to Marie Sato; Kentarou Omori to Kentaro Omori; Hideki Onuki to Hideki Ohnuki; Hieda Morihiko to Morihiko Hieda; Tetsuya Ono to Tetsuya Ohno; Shin'ichi Sato to Shinichi Sato.

#### The two redrawn evidence pictures and the capital H (v1.9p)

The short version: two of the first game's Episode 1 evidence pictures didn't match what the characters say, and a capital H in a long Court Record caption could lose its crossbar. [Issue #1](../../issues/1), from backplusone, raised both. v1.9p redraws the two pictures and gives H, E and F a slightly thicker crossbar.

The pictures: the Waiter's Business Card (Hosonaga's card) and the Medical Report Card cover. The ones before were the older fan translation's English art, and they disagreed with the dialogue. *Chronicles* ships no English version of either, so there was no Capcom picture to put in their place. I redrew both for this patch with an image generator and finished them myself, so these two are not Capcom's artwork. The card's front now reads Imperial Police Bureau / Primary Criminal Investigation Division / Chief Inspector / Satoru Hosonaga, as the characters read it out; the back, the restaurant sketch, is unchanged. The cover now reads Medical Report Card / Required for every visit / Name: Mr John Wilson / Hotta Clinic; the picture of the open-ledger first state is unchanged. The small icons that stand for each in the Court Record list were redone to match.

The letters: when a caption is too long for its place the game draws it shrunk, and in the Court Record caption font the crossbar of a capital H, E or F is one pixel high, which the shrink could skip. "Hosonaga-san" read "IIosonaga-san" in the first game's Waiter's Business Card caption. Each of the three letters now has a second, fainter row of pixels under its bar, 10 pixels in the font in all, at about 60% of full ink. I tested it on a PC by shrinking single-letter words at 660 combinations of size (68% to 100%) and offset, with nearest-pixel sampling like the game's: the old bar disappeared in about 18.5% of them for each letter and the new bar in none. That is a simulation, not the game's own drawing. The change is in both games' updates and in the second game's DLC; the first game's DLC has no font of its own.

What I haven't seen: the Medical Report Card's list icon, which only shows up at a later point in the story, the Medical Report details view, and the Red-Handed captions in Episode 5. In the second game I saw the title stamp and the Episode 1 Court Record captions named in the crossbar row above, and nothing later in the story. The second game's DLC with the font change was checked in the files only, not installed or booted.

How it's built: in the first game's update, three picture archives (the card and the cover, which the game keeps in two places) and the two list icons are replaced, and the Court Record font; in the second game's update only the font, apart from the chapter text and layout described in the next section. The archives hold the same members in the same order at the same decompressed sizes, but they are a few thousand bytes bigger than before because the new cover compresses worse, and I haven't confirmed that a console's loader takes them. The first game's update was then 3.4.1 and the second game's 1.0.31, which is the last number its version field can hold, so the update after that one had to move to a different number, the way the first game's did in v1.9o. The second game's DLC is `TGAA2-DLC-1.0.18.cia`, declaring version 1.1.2. Both updates and the second game's DLC need redoing; the first game's DLC and both banner patches didn't change. The Japanese-voice edition has all of it. Not run on a 3DS.

#### The chapter names and episode headings (v1.9p)

The short version: the box that asks whether to start a chapter had the chapter name against the left edge, and in the second game the episode heading above it was one line in two mismatched fonts. v1.9p centres the chapter name in both games and, in the second game, sets the heading as two centred lines.

What it looks like. First game: the heading line ("Ep. 1: The Great Departure") is as it was, and the chapter name ("Recess", "Susato's Sudden Entrance") is centred under it instead of sitting at the left. Second game: "Ep. 1:" is on a centred line of its own, the episode title is centred under it, and "Trial Start" is centred below that. The chapter list buttons are unchanged in both games.

The saved-game rows. The same heading text is drawn in the Load and Save rows, where there is only room for one line between the date and the chapter row. In my test builds, making the heading two lines there, or splitting its pieces apart, printed the number over the date and the title over the chapter row, and cut the end of the title off at the edge. So those rows keep the heading on one line. I moved it slightly lower and gave the space under the date a little more room, so it sits more evenly between the date and the chapter row. The first game's saved-game rows are as they were: in a first-game test build the same nudge put the heading closer to the chapter row than to the date, and the shipped first-game build doesn't have it.

The titles. In the second game's saved-game row, the Episode 1 and Episode 3 titles ("The Adventure of the Blossoming Attorney", "The Return of the Great Departed Soul") are the two longest. At the normal size the Episode 3 title ran right up to the frame with no gap after "Ep. 3:", and the Episode 1 title, by measurement, would have overrun the row. They're set a little smaller now; Episode 2, Episode 4 and Final are at the normal size. A smaller size for all five made the letters look thin and gapped, so I didn't use it.

What I haven't seen: the second game's Episode 1, Episode 4 and Final saved-game rows, because I have no such saves, and the Save screen. Those titles fit by measurement. I also haven't seen the boxes for the other episodes or the longest chapter names. The first game's centred names were seen in the build I'm releasing, on the emulator only.

How it's built: in the first game's update, 47 chapter names in the update's chapter text get a centring code at the front, and nothing else in its text or layout changes. In the second game's update, 82 chapter names get the same, the five episode numbers and titles are set in the new form, and three position values for the heading in the title and saved-game screen layout change. The DLCs hold none of these strings or this layout (checked by opening every archive in all four), so they're unaffected. Both updates need redoing. The Japanese-voice edition has all of it. Not run on a 3DS.

### 5. What was sent back upstream

**Both bugs that other people had reported on senyarom's tracker are fixed here:**

- **[#1](https://github.com/senyarom/tgaa2-en-patch/issues/1)**: text stretching outside
  the box and off the screen in the first game's Episode 4. Traced to a centred page in
  `_sce03_c000_0003`, and fixed by the reflow work above.
- **[#2](https://github.com/senyarom/tgaa2-en-patch/issues/2)**: the second game's DLC
  episodes showing blank character names, with every dialogue choice reading as invalid.

Three pull requests went back to senyarom rather than being kept here:
**[#3](https://github.com/senyarom/tgaa2-en-patch/pull/3)** reflows centred pages that
overflow the box, **[#4](https://github.com/senyarom/tgaa2-en-patch/pull/4)** stops
adapted advances running into the next glyph, and
**[#8](https://github.com/senyarom/tgaa2-en-patch/pull/8)** offers concise wording for 93
Court Record captions that overflow the 3DS panel.

Three further issues were filed there. **[#6](https://github.com/senyarom/tgaa2-en-patch/issues/6)**
(the first game's DLC Picture Book and Theme buttons bouncing to the title) is fixed here
from v1.7, as described above. **[#5](https://github.com/senyarom/tgaa2-en-patch/issues/5)**
(the second game's Japanese end credits) remains open, in this build and upstream.
**[#7](https://github.com/senyarom/tgaa2-en-patch/issues/7)** (40 lines in the first game set
in the serif face that overrun the box, because the wrapper measures them with the other
font's metrics) is mostly fixed here from v1.9c, and still open upstream. Both of those two appear
in the list at the top. They are listed here because a contribution section that
only lists wins is not worth much.

---

## Testing status

Moved to its own page: [TESTING.md](TESTING.md) says what has been played, watched and
listened to, and what has only been checked in the files.

---

## Patch files

From v1.5 each release also carries one zip per game, `TGAA1-3DS-English-v1.9q-xdelta.zip`
and `TGAA2-3DS-English-v1.9q-xdelta.zip`, holding three xdelta3 patches that apply to files
you make from your own Japanese dumps with Batch CIA 3DS Decryptor:

| patch | applies to | produces |
|---|---|---|
| `-update.xdelta` | your decrypted game `.cci` | the update CIA, byte for byte the one in row 2 of the README's install table |
| `-DLC.xdelta` | your decrypted DLC `.cia` | the DLC CIA, same contents as row 3 of that table, stored unencrypted |
| `-base.xdelta` | your decrypted game `.cci` | the same game with the English HOME banner, as above |

The zip has xdelta3.exe and a readme with the exact commands, the sizes to expect and the
output hashes. The decryptor writes a few random bytes into every file it makes, so your
source will not hash-match the readme's and the patches are built so that does not
matter; the outputs must match exactly. The update patch is 31 to 37 MB because most of
the update is files that already exist in the game image; the first game's DLC patch is
about 180 MB because the subtitled videos are genuinely new data. The patches were proven
on the `.cci` the decryptor writes from a CIA of the game; from v1.8a the update and DLC
patches also take a `.3ds` cartridge dump turned into a CIA with GodMode9's Build CIA from file
(NCSD image options) and decrypted the same way, ignoring the header bytes
that differ from an installed-title CIA dump. The optional base patch still wants a CIA dump
of an installed title. Same install order afterwards: base, update, DLC.

The same readme text is also on the release on its own, as `TGAA1-README-v1.9q.txt` and
`TGAA2-README-v1.9q.txt`, because romhacking.net wants the readme as a separate link rather
than only inside the zip. `HASHES_v1.9q.txt` on the release lists the size, CRC32 and sha256
of the English xdelta sources, patches and results for both games.

The CIAs stay on the release because they are what the hardware testing was done on, and
because a patch against a file most people dump differently is a support thread waiting
to happen.

## Japanese voice edition

Some people want Capcom's English text over the original Japanese cast. From v1.5 the
release also carries `TGAA1-3DS-English-JPvoice-v1.9q-xdelta.zip` and
`TGAA2-3DS-English-JPvoice-v1.9q-xdelta.zip`: the same three patches as the zips above,
producing the same update and DLC with one difference. Every audio file is Capcom's
Japanese original, taken from the cartridge and the Japanese DLC: the courtroom shouts,
the story lines, the narration, the crowd cues and the DLC voices. Text, art and layout are
byte for byte the main release, and that was checked file by file rather than assumed:
everything outside the sound files and the character archives is identical, and every
reverted file equals the Japanese one. The first game's banner patch in that zip also keeps
the Japanese HOME menu jingle, which the main release's banner replaces. The second game's banner patch in the JPvoice zip is the English set's, so it carries the same HOME banner.

The edition declares the same title versions as the main release, so install one or the
other, not both; the title screens read the same `ENG` stamps. It was checked file by file
against the main release and the Japanese originals before posting: text and art identical
to the main release, and every reverted file identical to the Japanese original. This build
has not been run on a console or in an emulator. The build and its check are `jpvoice/` in
the tools.

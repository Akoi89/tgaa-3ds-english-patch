# -*- coding: utf-8 -*-
"""Condensed testimony statements for TGAA1.

Each must fit two lines at 23600 units (measured in-game with our font:
23564 rendered whole, 23843 clipped). Every edit is the smallest one that
gets there, and keeps the speaker's register. The Japanese was checked for
each so nothing is lost that the original carries.

Keyed by the OFFICIAL text so duplicate labels (_MSG, _UPDATE) all pick up
the same replacement.
"""
DRAFTS = {

# Nosa, mock-military register. "while having" -> "during".
"I was ingesting a regulation beef steak at the restaurant while having a tactical discussion with the old man.":
"I was ingesting regulation beef steak at the restaurant in tactical discussion with the old man.",

# JP is その背後から, literally "from behind". "the back" -> "behind".
"The black-uniformed varsity cadet fired on the English civilian! And from the back, the cowardly little weasel!":
"The black-uniformed cadet fired on the English civilian! And from behind, the cowardly little weasel!",

# Drops the hyphenation artifact and the redundant "I was". Keeps every
# content word, including "precious" (JP has 珍宝, a rare treasure).
"I was on my hands and knees, investigating the where- abouts of my mysteriously absconded precious curio.":
"On my hands and knees, investigating the whereabouts of my absconded precious curio.",

# "at the time" is carried by the surrounding testimony.
"Furthermore! A visual search of the premises at the time confirmed that we were the only personnel present.":
"Furthermore! A visual search of the premises confirmed that we were the only personnel present.",

"Therefore! No one other than the black-uniformed cadet could have dispatched the Englishman. Over and out!":
"Therefore! No one but the black-uniformed cadet could've dispatched the Englishman. Over and out!",

"As far as I've heard, the post-mortem report showed no other possible cause of death besides the gunshot.":
"As far as I've heard, the post-mortem showed no other possible cause of death besides the gunshot.",

"I trust the driver. He has an excellent memory, it seems. Four passengers, with fares totalling twenty pence.":
"I trust the driver. He has an excellent memory, it seems. Four passengers, fares of twenty pence.",

# Juror. "I should like" -> "I'd like" keeps the period politeness.
"I'm changing my leaning to innocent. I should like to hear what the slipshod bookkeeper has to say for himself!":
"I'm changing my leaning to innocent. I'd like to hear what the slipshod bookkeeper has to say for himself!",

"However...I, I suppose you might say that I didn't see the exact moment the stabbing transpired...if that matters.":
"However...I, I suppose you might say I didn't see the moment the stabbing transpired...if that matters.",

"Anyway, the fact remains! There can't have been anyone else inside that carriage, or we all would have seen!":
"Anyway, the fact remains! There can't have been anyone else in that carriage, or we'd all have seen!",

"If anything had happened where we were sitting, don't you think one or the other of us would have noticed?":
"If anything had happened where we were sitting, don't you think one of us would have noticed?",

# "five o'clock in the afternoon" -> "five in the afternoon"; JP is just 夕方の5時.
"As I said, it was five o'clock in the afternoon when the incident occurred. And there was an unusually light fog.":
"As I said, it was five in the afternoon when the incident occurred. And the fog was unusually light.",

"Why it could have been that old man in the green that the defendant saw. I have to call not guilty. It's only right.":
"Why it could have been that old man in green the defendant saw. I have to call not guilty. It's only right.",

# JP says 結婚記念日 (wedding anniversary); "our anniversary" carries it in context.
"It was our wedding anniversary, and Roly was taking me out for a meal. There was no time to change after work.":
"It was our anniversary, and Roly was taking me out for a meal. There was no time to change after work.",

"All of a sudden, one of them just collapsed on the floor. Then the other scattered something before running off!":
"All of a sudden, one of them collapsed on the floor. Then the other scattered something and ran off!",

"The window could have been open when the woman was throwing books. I mean, it's definitely a possibility.":
"The window may have been open when the woman threw the books. I mean, it's definitely a possibility.",

# JP is 冬の火事, just "winter fires". "house" was an addition.
"Winter house fires are dire. You have to open windows to clear the smoke. That's when the chill gets you, see.":
"Winter fires are dire. You have to open windows to clear the smoke. That's when the chill gets you, see.",

"I did leave the scene to go and fetch help, but my trusty Roly was there to make sure nothing was disturbed.":
"I did leave the scene to fetch help, but my trusty Roly was there to make sure nothing was disturbed.",

# JP 同じ構図の写真 / Scarlet both say "angle" rather than "location".
"All we'd need is another shot from a slightly different location, and we could see the scene in three dimensions!":
"All we'd need is another shot from a slightly different angle, and we'd see the scene in three dimensions!",

"But are you seriously suggesting I colluded with these thugs to break into the place on the night of the murder?":
"But are you seriously suggesting I colluded with these thugs to break in on the night of the murder?",

"The bottom line is, I've never had anything to do with the pawnbroking establishment where the man was killed!":
"The bottom line is, I've never had anything to do with the pawnbroker's where the man was killed!",

"It was some low-class brickmaker negotiating with McGilded anyway, was it not? I've no relation to the man!":
"It was some low-class brickmaker negotiating with McGilded, was it not? I've no relation to the man!",

"I pursued the man but he shut himself in the storeroom. I could see him through the peephole in the door, though.":
"I pursued him but he shut himself in the storeroom. I could see him through the door's peephole.",

# --- second pass: found once the filter was corrected to best-two-line-split ---

# Drops the second "seeing"; the boy's "And, and" stammer is the character and stays.
"I remember seeing the knife. And, and I remember seeing both of the attacker's hands with blood on them.":
"I remember seeing the knife. And, and I remember both of the attacker's hands with blood on them.",

# JP is just そのうち ("then/before long"); "a bit" is also truer to her cockney.
"Then after a while, I 'ear this loud bang. Nearly jumped out me skin, I did. An' the scream just...came out.":
"Then after a bit, I 'ear this loud bang. Nearly jumped out me skin, I did. An' the scream just...came out.",

# "novel" is an English embellishment: JP and Scarlet both have only “可能性” / "a possibility".
"If there was some novel alternative explanation about how the victim was stabbed, I might reconsider...":
"If there was some alternative explanation about how the victim was stabbed, I might reconsider...",

# JP ガリデブ夫妻 = "the Garrideb couple", which "the Garridebs" carries exactly.
"This case has nothing to do with Mr and Mrs Garrideb. Believe me, a London bobby is good for his word!":
"This case has nothing to do with the Garridebs. Believe me, a London bobby is good for his word!",

# "on that front" is filler; both "sah!" tics are kept.
"I didn't take my eye off the crime scene for one moment, sah! Nothing strange to report on that front, sah!":
"I didn't take my eye off the crime scene for one moment, sah! Nothing strange to report, sah!",

# "here" is carried by "Every which way you look at it".
"You don't need a stereoscope to see the truth here. Every which way you look at it, it was that pickpocket!":
"You don't need a stereoscope to see the truth. Every which way you look at it, it was that pickpocket!",

# Drops "filthy"; "gutterling" already carries the contempt, and JP has no adjective at all.
"The redemption ticket was stolen from me by the accused – that filthy gutterling – on the day in question.":
"The redemption ticket was stolen from me by the accused – that gutterling – on the day in question.",

# JP opens そして ("and then"), which Scarlet also renders as "Then".
"All of a sudden, I 'eard a scream from over me 'ead, an' that pair on the roof deck went off to call the slops.":
"Then, I 'eard a scream from over me 'ead, an' that pair on the roof deck went off to call the slops.",

}

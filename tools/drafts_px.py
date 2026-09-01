# -*- coding: utf-8 -*-
"""Second pass: the trims needed once lines were measured in REAL PIXELS.

The first pass used the Helvetica model and left 28 lines over the true 365 px
budget. These are keyed on the text as it stands AFTER that pass, so the two
files compose. Every trim here is 1-12 px -- a word or two -- and each was
checked against the Japanese so nothing the original carries is dropped.
"""
DRAFTS_PX = {

# --- TGAA1 -------------------------------------------------------------
# "the man" -> "him" (already established), and "the sight of" goes: the JP is
# 血にまみれたあの両手 -- the hands themselves, with no "sight of".
"D'you think I'd forget the sight of those blood-soaked hands after that butcher stabbed the man?!":
"D'you think I'd forget those blood-soaked hands after that butcher stabbed him?!",

# Juror's verdict. JP is simply <<無罪>>にしておく -- "I'll keep it not guilty".
"Why it could have been that old man in green the defendant saw. I have to call not guilty. It's only right.":
"Why it could have been that old man in green the defendant saw. I'm calling not guilty. It's only right.",

# "is revealed by" -> "lies in"; same claim, tighter, and better English.
"The answer is revealed by the council notice on the counter to which your eyes were inadvertently drawn.":
"The answer lies in the council notice on the counter to which your eyes were inadvertently drawn.",

"The method is revealed by the council notice on the counter to which your eyes were inadvertently drawn.":
"The method lies in the council notice on the counter to which your eyes were inadvertently drawn.",

# "Which means that even if" -> "Which means even if".
"Exactly. Which means that even if the investigation takes a different direction, vital evidence may be lost.":
"Exactly. Which means even if the investigation takes a different direction, vital evidence may be lost.",

# Keeps the "digging up roads / digging up the truth" repetition, which is the
# joke; drops the redundant "to the end" instead.
"Whether it's digging up roads or digging up the truth, you've got to see it through to the end, haven't you?":
"Whether it's digging up roads or digging up the truth, you've got to see it through, haven't you?",

# JP is オバサンが本を投げても -- plain past, not the English progressive.
"Even if the woman was throwing books, it can't be related to this crime if the window was closed, can it?":
"Even if the woman threw books, it can't be related to the crime if the window was closed, can it?",

# "get this over with" -> "this over with"; JP is 早く終わらせてくれ, just "end it".
"Look, I just want to get this over with. If I don't bring home some pay tonight, I'll be in a tidy bit of trouble.":
"Look, I just want this over with. If I don't bring home some pay tonight, I'll be in a tidy bit of trouble.",

"Knocked a candlestick over and set fire to the carpet! Soon had it out, though, and got the window open.":
"Knocked a candlestick over and set fire to the carpet! Soon had it out, and got the window open.",

# JP is 同じ構図 ("the same composition"), so "slightly" was already a liberty.
"All we'd need is another shot from a slightly different angle, and we'd see the scene in three dimensions!":
"All we'd need is another shot from a different angle, and we'd see the scene in three dimensions!",

# Dropping "I'm" moved the split and gained nothing; "for himself" (absent from
# the JP) is the part that actually pays.
"I'm changing my leaning to innocent. I'd like to hear what the slipshod bookkeeper has to say for himself!":
"I'm changing my leaning to innocent. I'd like to hear what the slipshod bookkeeper has to say!",

"And on account of the smoke, I imagine they would have had the windows wide open in spite of the cold.":
"And on account of the smoke, I imagine they'd have had the windows wide open in spite of the cold.",

"Yes, on the day you're referring to, the wife and I did have a bit of a skirmish. Can't recall the reason now.":
"Yes, on the day you're referring to, the wife and I did have a bit of a skirmish. Can't recall the reason.",

# --- TGAA2 DLC ---------------------------------------------------------
# JP is 候補者は (plural, no "each"). This is the 3-line testimony statement.
"There were written and practical exams, negotiation tests...and finally each candidate was awarded a score.":
"There were written and practical exams, negotiation tests...and finally candidates were awarded a score.",

# JP 法廷に立つ = "stands in court"; "who stands" -> "standing" keeps it and
# leaves the formal "I am" of a self-introduction intact.
"I am a second-year student at Yumei University...and a qualified lawyer who stands in court.":
"I am a second-year student at Yumei University...and a qualified lawyer standing in court.",

}

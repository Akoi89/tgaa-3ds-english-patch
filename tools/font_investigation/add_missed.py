# -*- coding: utf-8 -*-
"""Append the 18 captions the first pass missed into CONDENSED.

They were missed because the first selection used "total width > 796 px" when
the real test is "greedy wrap at 199 px needs more than 4 lines" -- wrap waste
means a 712 px caption can still need 5. All 18 are only one line over, so the
trims are small.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'condensed.py')

NEW = {
'cast030_01_c': "A judicial assistant travelling with Kazuma to London on a study tour. The epitome of a refined Japanese lady.",
'cast030_02_c': "A judicial assistant sent to Britain on a study tour. The epitome of a refined Japanese lady, and a huge help to me.",
'cast030_04_c': "A judicial assistant sent to Britain on a study tour. The epitome of a refined Japanese lady, and a huge help to me.",
'cast101_00_c': "A professor of medicine at the Imperial Yumei University. An authority in forensics, and Kazuma's mentor.",
'cast202_00_c': "Head waiter of the European-style restaurant 'La Carneval', serving there on the day of the incident.",
'cast202_02_c': "A chief inspector in the Imperial Police Bureau, undercover as a member of the ship's crew.",
'cast301_00_c': "Owner of 'Rasu-tei', an antiques shop on a street corner in the second district. A witness to the incident.",
'cast303_00_c': "A real wall of a man. A senior Russian crewman, in charge of security around the first-class cabins.",
'item0_04_01_c': "A sketch of the restaurant's layout is on the back. The front states that Hosonaga-san is a police inspector.",
'item1_02_00_c': "The Russian word for 'wardrobe' in purple ink. It appears to have been written in the victim's final moments.",
'item1_10_00_c': "An armband I inherited from Kazuma. It identifies the wearer as a defence lawyer of the Empire of Japan.",
'item1_13_00_c': "A piece of a small glass object, and what looks like a scuff from Kazuma's shoes, found by the victim's body.",
'item1_14_00_c': "A photograph of Miss Pavlova and her 'friend' – a kitten named Darka. Her stage tiara can also be seen.",
'item3_10_00_c': "A second police photograph of the scene just after the incident. It specifically shows the victim's hand.",
'item5_02_00_c': "A fold-up device that lets anybody see things in three dimensions, simply by looking through the eyepieces.",
'item5_23_00_c': "A photograph of the victim, found murdered in the storeroom. It shows the single bullet wound in his back.",
'item5_25_00_c': "A firearm found on the Skulkin brothers when they were arrested. Signs that a single round was fired.",
'item5_29_00_c': "A photograph the Red-Handed Recorder took automatically, showing the scene after the murder.",
}

s = io.open(P, encoding='utf-8').read()
assert s.rstrip().endswith('}'), 'unexpected tail'
block = ['\n # ---- added on the second pass: missed by the width-only selection ----']
for lab in sorted(NEW):
    block.append(" '%s':" % lab)
    block.append('  "%s",' % NEW[lab].replace('"', '\\"'))
s = s.rstrip()[:-1].rstrip() + '\n' + '\n'.join(block) + '\n}\n'
io.open(P, 'w', encoding='utf-8').write(s)
print('added %d entries' % len(NEW))

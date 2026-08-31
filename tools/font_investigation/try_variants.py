# -*- coding: utf-8 -*-
"""Scratch: candidate rewrites for the 18 captions missed by the first pass.
Judged by the real criterion: greedy wrap at 199 px must give <= 4 lines."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'audio_tools'))
from caption_width import arc, advances
from caption_fit import wrap

adv, _ = advances(arc(os.path.join(HERE, '..', 'base_v12', 'romfs_dir', 'archive',
                                   'UI_cmn_jpn.arc'))['UI/0_system/00_font/font03_jpn.gfd'])
W = lambda s: sum(adv.get(ord(c), 7) for c in s)
L = 199

T = {
'cast030_01_c': [
 "A judicial assistant travelling with Kazuma to London on a study tour. The epitome of a refined Japanese lady.",
],
'cast030_02_c': [
 "A judicial assistant sent to Britain on a study tour. The epitome of a refined Japanese lady, and a huge help to me.",
 "A judicial assistant sent to Britain on a study tour. The epitome of a refined Japanese lady, and always a huge help.",
],
'cast101_00_c': [
 "A medical professor at the Imperial Yumei University. An authority in forensic medicine, and Kazuma's mentor.",
],
'cast202_00_c': [
 "Head waiter of the European-style restaurant 'La Carneval'. He was serving there on the day of the incident.",
],
'cast202_02_c': [
 "A chief inspector in the Imperial Police Bureau, undercover as a member of the ship's crew.",
],
'cast301_00_c': [
 "Owner of 'Rasu-tei', an antiques shop on a street corner in the second district. A witness to the incident.",
],
'cast303_00_c': [
 "A real wall of a man. A senior Russian crewman, in charge of security around the first-class cabins.",
],
'item0_04_01_c': [
 "A sketch of the restaurant's layout is on the back. The front states that Hosonaga-san is a police inspector.",
],
'item1_02_00_c': [
 "The Russian word for 'wardrobe' in purple ink. It appears to have been written in the victim's final moments.",
],
'item1_10_00_c': [
 "An armband I inherited from Kazuma. It identifies the wearer as a defence lawyer of the Empire of Japan.",
],
'item1_13_00_c': [
 "A piece of a small glass object, and what looks like a scuff from Kazuma's shoes, found by the victim's body.",
],
'item1_14_00_c': [
 "A photograph of Miss Pavlova and her 'friend' – a kitten named Darka. Her stage tiara can also be seen.",
],
'item3_10_00_c': [
 "A second police photograph of the scene just after the incident. It specifically shows the victim's hand.",
],
'item5_02_00_c': [
 "A fold-up device that lets anybody see things in three dimensions, simply by looking through the eyepieces.",
],
'item5_23_00_c': [
 "A photograph of the victim, found murdered in the storeroom. It shows the single bullet wound in his back.",
],
'item5_25_00_c': [
 "A firearm found on the Skulkin brothers when they were arrested. Signs that a single round was fired.",
],
'item5_29_00_c': [
 "A photograph taken automatically by the Red-Handed Recorder, showing the scene after the murder.",
],
}

if __name__ == '__main__':
    bad = 0
    for lab, vs in T.items():
        for i, t in enumerate(vs):
            n = len(wrap(t, W, L))
            if i == 0 and n > 4:
                bad += 1
            print('%-16s v%d %4d px %d lines %s' % (lab, i + 1, W(t), n, 'OK' if n <= 4 else '<<'))
    print('\n%d first choices still over' % bad)

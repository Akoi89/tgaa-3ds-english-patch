# -*- coding: utf-8 -*-
"""Write the chosen final wording into condensed.py (round 2: judged by the
real criterion, greedy wrap at 199 px must give <= 4 lines)."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'condensed.py')

R = {
'cast040_01_c': "An extraordinary girl who lives with Mr Sholmes. She has a degree in medicine and writes popular short stories.",
'cast040_02_c': "An extraordinary girl living with Mr Sholmes. She has a medical degree and writes popular magazine stories.",
'cast050_00_c': "A young woman who saw the murder from her hiding place aboard the omnibus. The defendant discovered her.",
'cast050_02_c': "A young pickpocket we met at a trial two months ago. Now the defendant, found at the scene beside the victim.",
'cast060_00_c': "A prosecutor known as the Reaper of the Bailey. Those he prosecutes are supposedly damned, one way or another.",
'cast060_02_c': "The infamous London prosecutor known as the Reaper of the Bailey. Further details are not forthcoming.",
'cast070_00_c': "Detective inspector leading Scotland Yard's investigation. Stern, single-minded, and a great lover of fish and chips.",
'cast070_01_c': "Detective inspector leading Scotland Yard's investigation. Stern, single-minded, and a great lover of fish and chips.",
'cast100_00_c': "A second year at the Imperial Yumei University. My best friend and, though a student, a qualified defence lawyer.",
'cast103_00_c': "The Lord Chief Justice. His authority in judicial matters, even over lawyers, is absolute. A most intimidating man.",
'cast103_01_c': "The Lord Chief Justice. His authority in judicial matters, even over lawyers, is absolute. A most intimidating man.",
'cast103_02_c': "The Lord Chief Justice. His authority in judicial matters, even over lawyers, is absolute. A most intimidating man.",
'cast200_00_c': "The lead prosecutor, who appears to have little love for what the cultural reformation has brought about.",
'cast202_01_c': "An Imperial Police Bureau chief inspector, undercover at the European-style restaurant 'La Carneval'.",
'cast207_01_c': "Mr Garrideb's wife, who poses as the maid to keep up appearances. Fierce-tempered, and inclined to get physical.",
'cast218_00_c': "The defendant. A wealthy philanthropist well regarded in London. Defending him is my test of worthiness.",
'cast219_01_c': "A telegraph operator, subpoenaed after a Red-Handed Recorder caught him on film at Windibank's.",
'cast219_02_c': "A telegraph operator at the central communication station. Came to Windibank's as 'Eggert Benedict'.",
'cast219_03_c': "A telegraph operator, once surnamed Milverton. A childhood friend of the Skulkin brothers.",
'cast313_00_c': "Proprietor of a Baker Street pawnbrokery patronised by Mr Sholmes. He has a great sense of duty to his clients.",
'cast313_01_c': "Proprietor of a Baker Street pawnbrokery patronised by Mr Sholmes. Shot dead by an unknown assailant.",
'cast314_00_c': "Broke into Windibank's with his brother Ringo and saw the murder. Claims to be a 'profeshnal baddie' by trade.",
'cast315_00_c': "Broke into Windibank's with his brother Nash and saw the murder. Claims to be a 'profeshnal baddie' by trade.",
'item0_03_01_c': "A dental record. On the day of the murder the victim had treatment, and was forbidden anything but water.",
'item0_09_00_c': "Death occurred just after 2 p.m., from blood loss after a gunshot to the chest. The bullet did not pass through.",
'item1_00_00_c': "Kazuma's diary of his trip to London. In his last entry before his death, he spied a 'speckled band'.",
'item1_05_00_c': "A report from the SS Burya's medical officer. Cause of death: a cervical spine injury. No sign of injury or poison.",
'item9_00_00_c': "A report from the SS Burya's medical officer. Cause of death: a cervical spine injury. No sign of injury or poison.",
'item1_07_00_c': "A record kept by the crew assigned to the first-class cabins. No entries from 2 a.m. until early this morning.",
'item9_03_00_c': "A record kept by the crew assigned to the first-class cabins. No entries from 2 a.m. until early this morning.",
'item1_12_00_c': "Kazuma stuck this over the wardrobe doors for me. It says 'Keep out' in Japanese, but can the Russian crew read it?",
'item2_00_00_c': "A report by the Scotland Yard coroner. Cause of death: internal haemorrhaging from a single stab to the abdomen.",
'item2_01_00_c': "A photograph of the victim on the omnibus. The knife in his abdomen is plain; a crooked old hat partly hides his face.",
'item2_03_00_c': "The eight-seater omnibus, scene of the crime. There were passengers inside and on the roof deck that night.",
'item2_03_01_c': "The eight-seater omnibus, scene of the crime. There were passengers inside and on the roof deck that night.",
'item2_04_10_c': "A largish knife found lodged in the victim's abdomen. Its quality and ornamentation suggest it's quite valuable.",
'item2_05_00_c': "A list of people who borrowed from the defendant at high interest. It includes the victim, who owed twenty guineas.",
'item3_06_01_c': "Where the victim was found lies just outside Constable Beate's beat, which ends in the middle of Briar Road.",
'item3_08_00_c': "A photograph of the scene taken by a policeman just afterwards. A large knife can be seen in the victim's back.",
'item3_08_01_c': "A photograph of the scene taken by a policeman just afterwards. A large knife can be seen in the victim's back.",
'item5_06_10_c': "A metal disk that plays music in a mechanical music box, by means of small protrusions. The piece is unidentified.",
'item5_12_00_c': "Gina's paperwork putting me in charge of her defence. Showing it to Scotland Yard gets us into the crime scene.",
'item5_16_00_c': "A long, unpublished story Mr Sholmes deposited at Mr Windibank's pawnbrokery: 'The Hound of the Baskervilles'.",
'item5_17_00_c': "The victim Mr Windibank's gun, which Gina was holding when found unconscious. Signs of a single discharge.",
'item5_22_00_c': "A Scotland Yard coroner's report confirming instant death from a single bullet to the back. No other trauma.",
'item5_24_00_c': "A plan of Windibank's pawnbrokery, the scene of the crime. It shows the main shop and the rear storeroom.",
'item5_28_00_c': "A photograph the Red-Handed Recorder took automatically, showing the scene shortly before the murder.",
'item5_30_00_c': "The pouch Mr Sholmes wore at his waist during the shooting. One glass phial is smashed, with scorch marks around it.",
'item5_34_00_c': "This strange music box plays only a single tone. Deposited at Windibank's two days before the black overcoat.",
'item9_02_00_c': "The back page of a Russian newspaper: 'Renowned Prima Ballerina of the Novavich Ballet Disappears!'",
}

s = io.open(P, encoding='utf-8').read()
for lab, txt in R.items():
    pat = re.compile(r"( '%s':\n  )\"[^\n]*\"," % re.escape(lab))
    s, n = pat.subn(lambda m, t=txt: m.group(1) + '"' + t.replace('"', '\\"') + '",', s)
    assert n == 1, (lab, n)
io.open(P, 'w', encoding='utf-8').write(s)
print('updated %d entries' % len(R))

# -*- coding: utf-8 -*-
"""Condensed versions of the 72 captions that exceed the Court Record's
full-size budget (796 px = 4 lines x 199). Over that the widget shrinks the
font, which is what makes the long captions render badly.

Rules followed in every rewrite:
  * Capcom's names and spellings stay: Sholmes, Windibank, Ringo, Nash, Beate,
    Mason, Vilen Borshevik, Skulkin, Eggert Benedict, Hosonaga-san, Miss Brett.
  * Ryunosuke's first person stays where the original has it (I'm, me, we).
  * Jokes and flavour stay: 'profeshnal baddie', 'speckled band', fish and
    chips, 'Keep out' in Japanese, the Reaper of the Bailey.
  * Only filler goes: 'in this case', 'A witness to the incident who',
    'that was', 'currently', 'merely', 'relatively', 'in the form of',
    'would appear to', 'of the case', doubled adjectives.
  * British spelling kept.

Scarlet's text was consulted only to judge what is safely cuttable.
"""

# label -> condensed text. Labels sharing an original text get the same rewrite.
CONDENSED = {
 # ---- profiles ----------------------------------------------------------
 'cast040_01_c':
  "An extraordinary girl who lives with Mr Sholmes. She has a degree in medicine and writes popular short stories.",
 'cast040_02_c':
  "An extraordinary girl living with Mr Sholmes. She has a medical degree and writes popular magazine stories.",
 'cast050_00_c':
  "A young woman who witnessed the incident from hiding aboard the omnibus. The defendant discovered her.",
 'cast050_02_c':
  "A young pickpocket we met at a trial two months ago. Now the defendant, found at the scene beside the victim.",
 'cast060_00_c':
  "A prosecutor called the Reaper of the Bailey. The souls of those he prosecutes are supposedly damned, one way or another.",
 'cast060_02_c':
  "The infamous London prosecutor known as the Reaper of the Bailey. Further details are not forthcoming.",
 'cast070_00_c':
  "Detective inspector leading Scotland Yard's investigation. Stern, single-minded, and a great lover of fish and chips.",
 'cast070_01_c':
  "Detective inspector leading Scotland Yard's investigation. Stern, single-minded, and a great lover of fish and chips.",
 'cast100_00_c':
  "A second year at the Imperial Yumei University. My best friend and, though a student, a qualified defence lawyer.",
 'cast103_00_c':
  "The Lord Chief Justice. His authority in judicial matters, even over lawyers, is absolute. A most intimidating man.",
 'cast103_01_c':
  "The Lord Chief Justice. His authority in judicial matters, even over lawyers, is absolute. A most intimidating man.",
 'cast103_02_c':
  "The Lord Chief Justice. His authority in judicial matters, even over lawyers, is absolute. A most intimidating man.",
 'cast200_00_c':
  "The lead prosecutor, who appears to have little love for what the cultural reformation has brought about.",
 'cast202_01_c':
  "An Imperial Police Bureau chief inspector, undercover at the European-style restaurant 'La Carneval'.",
 'cast205_00_c':
  "A scholar sent to Britain by the Japanese government to study English. He's the defendant, accused of attempted murder.",
 'cast206_00_c':
  "A retired army man, landlord to the defendant, Mr Natsume. An old knee injury keeps him in a chair most of the time.",
 'cast206_01_c':
  "A retired army man, landlord to the defendant, Mr Natsume. An old knee injury keeps him in a chair most of the time.",
 'cast207_01_c':
  "Mr Garrideb's wife, who poses as the maid to keep up appearances. Fierce-tempered, and inclined to get physical.",
 'cast207_02_c':
  "Mr Garrideb's wife, who poses as the maid to keep up appearances. She's here today as a member of the jury.",
 'cast208_00_c':
  "The victim, found with a knife in her back. Luckily the wound wasn't fatal, but she remains unconscious in hospital.",
 'cast218_00_c':
  "The defendant. A wealthy philanthropist well regarded in London. Defending him is my test of worthiness.",
 'cast219_00_c':
  "An aloof, high-handed young English gentleman. He came to Windibank's accusing Gina of stealing his redemption ticket.",
 'cast219_01_c':
  "A telegraph operator, subpoenaed over a photograph the Red-Handed Recorders took at Windibank's.",
 'cast219_02_c':
  "A telegraph operator at the central communication station. Came to Windibank's as 'Eggert Benedict'.",
 'cast219_03_c':
  "A telegraph operator, once surnamed Milverton. A childhood friend of the Skulkin brothers.",
 'cast306_00_c':
  "The wife of Constable Roly Beate, and a witness. Recently married, and fiercely proud of her policeman husband.",
 'cast313_00_c':
  "Proprietor of a Baker Street pawnbrokery Mr Sholmes patronises. A very great sense of responsibility to his clients.",
 'cast313_01_c':
  "Proprietor of a Baker Street pawnbrokery patronised by Mr Sholmes. Shot dead by an unknown assailant.",
 'cast314_00_c':
  "Broke into Windibank's with his brother Ringo, witnessing the incident. Claims to be a 'profeshnal baddie' by trade.",
 'cast315_00_c':
  "Broke into Windibank's with his brother Nash, witnessing the incident. Claims to be a 'profeshnal baddie' by trade.",

 # ---- evidence ----------------------------------------------------------
 'item0_03_01_c':
  "A dental record. On the day of the murder the victim had treatment, and was forbidden anything but water.",
 'item0_09_00_c':
  "Death occurred just after 2 p.m., from blood loss after a gunshot to the chest. The bullet did not pass through.",
 'item0_16_00_c':
  "A photograph Hosonaga-san took after the incident. It shows Miss Brett's handbag on a chair by the victim's table.",
 'item1_00_00_c':
  "Kazuma's diary of his trip to London. The last entry, before his death, notes what appeared to be a 'speckled band'.",
 'item1_03_00_c':
  "The front page of a Russian newspaper. The headline reads: 'Revolutionary Vilen Borshevik Flees Russia via Shanghai'.",
 'item1_03_10_c':
  "The back page of a Russian newspaper: 'Renowned Prima Ballerina of the Novavich Ballet Disappears from Shanghai!'",
 'item1_05_00_c':
  "A report from the SS Burya's medical officer. Cause of death: a cervical spine injury. No external injury or poison.",
 'item1_07_00_c':
  "A record kept by the first-class cabin crew. There are virtually no entries from 2 a.m. until early this morning.",
 'item1_12_00_c':
  "Kazuma stuck this over the wardrobe doors for me. It says 'Keep out' in Japanese, but can the Russian crew read it?",
 'item2_00_00_c':
  "A report by the Scotland Yard coroner. Cause of death: internal haemorrhaging from a single stab to the abdomen.",
 'item2_01_00_c':
  "A photograph of the victim on the omnibus. The knife in his abdomen is plain; a crooked old hat partly hides his face.",
 'item2_03_00_c':
  "The eight-seater omnibus, scene of the crime. There were passengers inside and on the roof deck that night.",
 'item2_03_01_c':
  "The eight-seater omnibus, scene of the crime. There were passengers inside and on the roof deck that night.",
 'item2_04_10_c':
  "A largish knife found in the victim's abdomen. Its quality and ornamentation suggest it must be quite valuable.",
 'item2_05_00_c':
  "A list of people who borrowed from the defendant at high interest. It includes the victim, who owed twenty guineas.",
 'item3_01_00_c':
  "A receipt found in Mr Natsume's room, for books he bought from a secondhand bookshop before the incident.",
 'item3_06_00_c':
  "An overview of the case and details about the victim. Found with a knife in her back, she's in hospital, still unconscious.",
 'item3_06_01_c':
  "The victim was found just outside Constable Beate's beat, whose border runs down the middle of Briar Road.",
 'item3_08_00_c':
  "A photograph of the scene taken by a policeman just afterwards. A large knife can be seen in the victim's back.",
 'item3_08_01_c':
  "A photograph of the scene taken by a policeman just afterwards. A large knife can be seen in the victim's back.",
 'item3_09_00_c':
  "A present for Patricia Beate from her husband, Roly. The shock of seeing the stabbed victim made Mrs Beate drop it.",
 'item3_14_01_c':
  "A small piece of metal found inside the bowl of Mr Garrideb's pipe. It's a perfect fit for the missing tip of the knife.",
 'item5_06_10_c':
  "A metal disk that plays music in a mechanical music box, by means of small protrusions. The piece is unidentified.",
 'item5_11_10_c':
  "A redemption ticket from the pawnbrokery of the victim, Mr Windibank: handwritten notes on the back of a photograph.",
 'item5_12_00_c':
  "Gina's paperwork putting me in charge of her defence. Showing it to Scotland Yard gets us into the crime scene.",
 'item5_13_01_c':
  "A redemption ticket from the pawnbrokery of the victim, Mr Windibank. There's what looks like a bloody fingermark on it.",
 'item5_13_10_c':
  "A redemption ticket from the pawnbrokery of the victim, Mr Windibank. The blood on it has been identified as Mr Mason's.",
 'item5_14_00_c':
  "A blood sample analysed with Mr Sholmes' chemical indicator. Different people's blood turns different colours.",
 'item5_14_10_c':
  "Two blood samples analysed with Mr Sholmes' chemical indicator. Different people's blood turns different colours.",
 'item5_14_20_c':
  "Three blood samples analysed with Mr Sholmes' chemical indicator. Different people's blood turns different colours.",
 'item5_14_30_c':
  "Four blood samples analysed with Mr Sholmes' chemical indicator. Different people's blood turns different colours.",
 'item5_16_00_c':
  "A long, unpublished story Mr Sholmes deposited at Mr Windibank's pawnbrokery: 'The Hound of the Baskervilles'.",
 'item5_17_00_c':
  "The victim Mr Windibank's gun, which Gina was holding when found unconscious. Signs of a single discharge.",
 'item5_22_00_c':
  "A Scotland Yard coroner's report confirming instant death from a single bullet to the back. No other trauma.",
 'item5_24_00_c':
  "A plan of Windibank's pawnbrokery, the scene of the crime. It shows the main shop and the rear storeroom.",
 'item5_28_00_c':
  "A photograph the Red-Handed Recorder took automatically, showing the scene shortly before the murder.",
 'item5_30_00_c':
  "The pouch Mr Sholmes wore at his waist during the shooting. One glass phial is smashed, with scorch marks around it.",
 'item5_34_00_c':
  "This music box appears to play only a single tone. Deposited at Windibank's two days before the black overcoat.",
 'item9_00_00_c':
  "A report from the SS Burya's medical officer. Cause of death: a cervical spine injury. No external injury or poison.",
 'item9_01_00_c':
  "The front page of a Russian newspaper. The headline reads: 'Revolutionary Vilen Borshevik Flees Russia via Shanghai'.",
 'item9_02_00_c':
  "The back page of a Russian newspaper: 'Renowned Prima Ballerina of the Novavich Ballet Disappears!'",
 'item9_03_00_c':
  "A record kept by the first-class cabin crew. There are virtually no entries from 2 a.m. until early this morning.",

 # ---- added on the second pass: missed by the width-only selection ----
 'cast030_01_c':
  "A judicial assistant travelling with Kazuma to London on a study tour. The epitome of a refined Japanese lady.",
 'cast030_02_c':
  "A judicial assistant on a study tour to Britain. The epitome of a refined Japanese lady, and a huge help to me always.",
 'cast030_04_c':
  "A judicial assistant on a study tour to Britain. The epitome of a refined Japanese lady, and a huge help to me always.",
 'cast101_00_c':
  "A medical professor at the Imperial Yumei University. An authority in forensic medicine. Kazuma's mentor.",
 'cast202_00_c':
  "Head waiter of the European-style restaurant 'La Carneval', serving there on the day of the incident.",
 'cast202_02_c':
  "A chief inspector in the Imperial Police Bureau, undercover as a member of the ship's crew.",
 'cast301_00_c':
  "Owner of 'Rasu-tei', an antiques shop on a street corner in the second district. A witness to the incident.",
 'cast303_00_c':
  "A real wall of a man. A senior Russian crewman, in charge of security around the first-class cabins.",
 'item0_04_01_c':
  "A sketch of the restaurant's layout is on the back. The front states that Hosonaga-san is a police inspector.",
 'item1_02_00_c':
  "The Russian word for 'wardrobe' in purple ink. It appears to have been written in the victim's final moments.",
 'item1_10_00_c':
  "An armband I inherited from Kazuma. Its wearer is a defence lawyer throughout the Empire of Japan.",
 'item1_13_00_c':
  "A piece of a small glass object, and what looks like a scuff from Kazuma's shoes, found by the victim's body.",
 'item1_14_00_c':
  "A photograph of Miss Pavlova and her 'friend' – a kitten named Darka. Her stage tiara can also be seen.",
 'item3_10_00_c':
  "A second police photograph of the scene just after the incident. It specifically shows the victim's hand.",
 'item5_02_00_c':
  "A fold-up device that lets anybody see things in three dimensions, simply by looking through the eyepieces.",
 'item5_23_00_c':
  "A photograph of the victim, found murdered in the storeroom. It shows the single bullet wound in his back.",
 'item5_25_00_c':
  "A firearm found on the Skulkin brothers when they were arrested. Signs that a single round was fired.",
 'item5_29_00_c':
  "A photograph the Red-Handed Recorder took automatically, showing the scene after the murder.",
}

# Known issues

Some known issues (non-exhaustive ideally yes but maybe not anyways etc) about AdvCiv code or earlier or/and AdvCiv-SAS specific code that may be fixed someday or not (ideally yes too same but maybe not especially if deemed not so bad or even part of the necessary mechanic but then would not be an issue but if known maybe or not or yes but anyways etc anywyas etc anyways etc).

hopefully helpful, thanks, anyways, thanks,

## 1 - Redundant attribute values for all AI Civs

Some known issues, that will not necessarily be fixed, but maybe or not but anyways, however good and maybe useful to keep them as reminder in case we want or for souvenir, anyways:

- while debugging the new ai personality feature in the sevopedia in advciv-sas (our mod), we found some information that some ai attributes seem to be shared accross all leaders:

```
PY:[DEBUG] Cached AI attribute data for leader LEADER_ZARA_YAQOB
PY:[WARNING] Attribute 'iAtPeaceAttitudeChangeLimit' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iAtPeaceAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAtPeaceAttitudeDivisor' has an identical *raw* value (60) across all 53 leaders
PY:[WARNING] Attribute 'iAtPeaceAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeChangeLimit' has an identical *raw* value (5) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeDivisor' has an identical *raw* value (-5) across all 53 leaders
PY:[WARNING] Attribute 'iAtWarAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iAttackOddsChangeRand' has an identical *raw* value (8) across all 53 leaders
PY:[WARNING] Attribute 'iAttackOddsChangeRand' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeChangeLimit' has an identical *raw* value (2) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeDivisor' has an identical *raw* value (50) across all 53 leaders
PY:[WARNING] Attribute 'iBonusTradeAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeChangeLimit' has an identical *raw* value (2) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeDivisor' has an identical *raw* value (12) across all 53 leaders
PY:[WARNING] Attribute 'iDefensivePactAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeChange' has an identical *raw* value (-1) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeDivisor' has an identical *raw* value (-15) across all 53 leaders
PY:[WARNING] Attribute 'iDifferentReligionAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeChange' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeDivisor' has an identical *raw* value (10) across all 53 leaders
PY:[WARNING] Attribute 'iFavoriteCivicAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iFreedomAppreciation' has an identical *raw* value (10) across all 53 leaders
PY:[WARNING] Attribute 'iFreedomAppreciation' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iLostWarAttitudeChange' has an identical *raw* value (-1) across all 53 leaders
PY:[WARNING] Attribute 'iLostWarAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iLoveOfPeace' has an identical *raw* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iLoveOfPeace' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeChangeLimit' has an identical *raw* value (2) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeChangeLimit' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeDivisor' has an identical *raw* value (25) across all 53 leaders
PY:[WARNING] Attribute 'iOpenBordersAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iPeaceWeightRand' has an identical *raw* value (3) across all 53 leaders
PY:[WARNING] Attribute 'iPeaceWeightRand' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeChange' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeDivisor' has an identical *raw* value (10) across all 53 leaders
PY:[WARNING] Attribute 'iSameReligionAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeChange' has an identical *raw* value (1) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeChange' has an identical *normalized* value (0) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeDivisor' has an identical *raw* value (8) across all 53 leaders
PY:[WARNING] Attribute 'iShareWarAttitudeDivisor' has an identical *normalized* value (0) across all 53 leaders
```

Some of these such as iLoveOfPeace are not used in AdvCiv; i disabled (commented-out) from display (in SevoPediaLeader.py) such unused ai attributes to not clutter the display, see [README.md#ai-personality-panel-in-sevopedialeader-and-other-sevopedia-reworks](/README.md#ai-personality-panel-in-sevopedialeader-and-other-sevopedia-reworks) for (more) details, and more specifically in the full AI Personality Panel Feature this [README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored).

Leaving as is otherwise (except from hiding most or/and commenting out unused ones such as iLovePeace (in AdvCiv) anyways) for now if not always or not anyways etc.

We may also spread some values more (i.e. in AdvCiv-SAS etc anyways) that are way too often shared between leaders, not just the common to all leaders, may be a good opportunity perhaps, but not sure or guarnateed, for now only mentionning the issue.

## 2 - (now fixed) Gandhi's base leaderheadinfo's xml had nowarattitudeprob pleased(110)/pleased(115) duplicated instead of (as i suspect it should be anyways etc) pleased(110)/friendly(115)

For example, i had spotted a seemingly mistake/typo/bug in Gandhi's nowar attributes (from AdvCiv), where pleased was repeated twice, while enhancing and adding on the generate_leaders_data.py (see the [README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module) for details) script:

```
            {
                "MemoryType": "MEMORY_VOTED_AGAINST_US",
                "iMemoryAttitudePercent": "0"
            }
        ],
        "NoWarAttitudeProbs": [
            {
                "AttitudeType": "ATTITUDE_FURIOUS",
                "iNoWarProb": "20"
            },
            {
                "AttitudeType": "ATTITUDE_ANNOYED",
                "iNoWarProb": "50"
            },
            {
                "AttitudeType": "ATTITUDE_CAUTIOUS",
                "iNoWarProb": "85"
            },
            {
                "AttitudeType": "ATTITUDE_PLEASED",
                "iNoWarProb": "110"
            },
            {
                "AttitudeType": "ATTITUDE_PLEASED",
                "iNoWarProb": "115"
            }
        ],
        "UnitAIWeightModifiers": "",
```

It is almost certainly a mistake and should be:

```
            {
                "AttitudeType": "ATTITUDE_FRIENDLY",
                "iNoWarProb": "115"
            }
```

Our generate_leaders_data.py (see the [README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module) for details) sucessfully detected/detects it, for example before fixing the XML of Gandhi we have:

```
Microsoft Windows [version 10.0.19045.5737]
(c) Microsoft Corporation. Tous droits réservés.

C:\Users\PC>cd C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\ & python generate_leaders_data.py
[WARNING] Duplicate NoWarAttitudeProb 'ATTITUDE_PLEASED' for leader LEADER_GANDHI
[SUCCESS] Leader data written to: leaders_data_20250426_100035.py

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>
```

And after fixing Gandhi's XML we now have:

```
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>cd C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\ & scan_xml_duplicates-3.3.py
[SUCCESS] Leader data written to: leaders_data_20250426_100152.py

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>
```

So i had the idea to generalize this approach to find if we don't have other such duplicates and perhaps may improve our XML data and reliability, and the result is as explained in the [README_Python_Scripts.md#scan_xml_duplicates-py-script-and-logs_xml_scans](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Python_Scripts.md#scan_xml_duplicates-py-script-and-logs_xml_scans) (see it for details), currently if not always or not etc anyways version 3.3 as per chatgpt's naming and greta help in doing this (coded all i only gave pointers and feedback, joint collaboration hehe anyways.)

Since there are false positives, i am not sure how to interpret it, but hopefully useful enopugh, so adding this script here, and funcitonal enough (skim through results you known false for example maybe i mean, anyways)

Results are very good, if you have good eyes or are veyr patient or/and know where and what to look at or/and other things or not anyways, we successfulyl spot it specifically (Gandhi's seemingly('s?) mistake/typo/bug)

A few screenshots of the issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1WNHP4fQQ1Dbm4JnXx9YDedCnLzrOO8ey?usp=sharing)

## 3 - (now fixed) Barbarians (cities) building wonders

UPDATE: seemingly now fixed using builUnitProb 100 or a similar value, testing more to be sure but seems extremely effective in stopping all (great and wonder) building tendency entirely in barbarian, ened to test more to be sure (in case) i am not mistaken anyways etc, may tone it dow a bit so they can build the barabarian lighthouse they seemingly never do now, but anyways etc

In AdvCiv base code after implementing the barbarians boost to make them more economically viable and/or strong but anyways etc anyways etc anyways etc... Barbarians are still trying to build wonders sometimes, the base AdvCiv code does not prevent that, or/and at least not always maybe or not or yes indeed but anyways etc anyways etc ; and even complete them sometimes actually, for example(s anyways etc anyways etc):

A few screenshots of the issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1p5O09XzbbrM5x2hxFD6RGvBpuU8RzPAd?usp=sharing)

There may be(/have been, but anyways etc) other cases like these, and i don't know if the cause is one of the changes i made to barbarian (xml) code, or how it just is/was. I tried to fix it by using iWonderConstructRand -9999 on LEADER_BARBARIAN in leader head infos xml file, but they still build national and world wonders alike, and all the buildingclass NONE spaghetti code whether it is here (for national wonders) or not (for world wonders) does not change anything, they even build shrines like the mahadhobi as of now me writing this anyways, is not necessarily a bad design, but ideally i would want them to focus more on warmongering their key rol in advciv-sas and be more efficient in that anyways etc. 

So/And anyways etc i removed all such old logic of buildingclass NONE in (adjust if non-steam game or other mod path you have to where your advciv-sas or/and other mod you're using or not etc anyways etc is anyways etc) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Civilizations\CIV4CivilizationInfos.xml`.

For now trying the FLAVOR_MILITARY 10 approach (inspired or rather taken (as i already had the idea but anyways thanks still or not thanks or thanks still or and other or and not anyways etc) from genghis khan's code), not sure it will make a difference but this (value not the leader, i don't know enough about genghis khan to say if he aligns or not, i could maybe express a tentative opinion if i knew more but abstaining from that as i don't know lot or enough about him even though may be cool or/and interesting maybe i mean to know but anyways etc anyways etc)align with their profile of being (more of a at least ideally i.e. in theory if not more ideal too or not but(/) anyways etc anyways etc...) anyways warmongerer anyways etc.

Currently testing a builUnitProb 100 or similar in leader barbarian that seems very very effective, but testing more if i test to be sure, may be fixed now for real or maybe not, hopefully, but maybe or maybe not, but anyways etc anyways etc anyways etc

## 4 - (now fixed) Sevopedia Unit's placeRequires's Religion button (for example any religious missionary unit) not redirecting to sevopedia religion (nothing happens on click anyways etc)

Now fixed: by replacing, in sevopediaunit py file, in placeRequires function/method (of this file anyways etc), `WidgetTypes.WIDGET_HELP_RELIGION` with `WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION`(,) as is done already by base advciv and successfully in sevopedia building, anyways etc anyways etc anyways etc.

This is a bug i have noticed in AdvCiv and after checking, many other mods, among those (few i tried): ROM 291, RFC DOC, Neoteric World (since i have it too (to check their sevopedia content or/and such or/and other or/and not anyways) even though i did not use anything from it at least but may be useful some day or not anyways etc anyways etc), History Rewritten too.

But clicking in AdvCiv in sevopediabuilding for example on any religious temple's placeRequires's religious icon/button successfully redirects to the sevopedia's religion page.

Among the mods i tried, only Realism Invictus's sevopedia unit's placerequires's religion button works as intended and successfully redirects to the religion's page

I tried to import its code but their gc uses difference methods that we don't have it seems like getNumPrereqAndBonuses and such, may not be hard to fix or not, but leaving as is, finding how realism invictus does it, or finding yourself the cause if you want to investigate it, may help solve it.

As for me this is quite minor, and even though i would have loved (really) to fix it (but anyways etc), leaving a note here rather as i don't know also how nested in the code the issue is, i would ideally but anyways love to dive deeper but doing other code things, at least for now if not always or maybe not, but anyways etc, if so (that i would look again), hopefully these lines may (then) serve as a reminder of the issue and the current status of solving it (i have found in realism invictus mod it works fine unlike in other mods (that i tried about/for this issue anyways etc), can investigate from there maybe anyways etc)

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1vRIFzwNijAjbmPBVUvSk90YjURXh-lG1?usp=sharing)

## 5 - (seemingly worked around now) player name same as windows (10's for example anyways etc) username causes new game screen to be stuck unless a custom name is chosen, if/after/while DLL has been fastdep compiled

A quite weird issue i never had before, but after doing a fastdep (auto, not me), since i changed only one .cpp file to add the placeExclusiveCivs new sevopedia feature (see the [/README_Sevopedia_Reworks.md#example-7-unit-list-category](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md#example-7-unit-list-category) for details)

A few screenshots of the issue here in as well as the DLL with which i had the issue (not sure is the cause but happened while having it if i am not mistaken anyways etc) [this Google Drive folder](https://drive.google.com/drive/folders/19T9I75vGCk58pFSR60y2Tmj69-NoFFtk?usp=sharing)

More context of how i implemented the change in the .cpp and such can be found in this Google Drive about Claude AI's first prompt i successfully implemented in AdvCiv-SAS, [by finding such a (Google Drive too anyways etc) link in the Claude AI part of the README there (click on this link to be redirected anyways etc)](/README.md#claude-ai-the-newcomer-hehe-xd-anyways-etc-welcome-anyways-etc)

I don't know if fastdep compiel was the cause or just some weird corruption unnotified happened (i don't know a lot about these if at all hehe but it was reproductible, and my player name also unusually changed just after this fast compile so i can quite confidently say it is maybe indeed related but anyways etc (for example after checking indeed Civ4ScreenShot3010 in the advciv-sas's mod journey drive (see main README.md for link anyways etc), with last compiled DLL before this Claude AI related .cpp change and recompile, had my windows username as default player name as can be seen in screenshot, but the screenshots of the issue in the drive linked above, that happen between Civ4ScreenShot3095(new game not yet started after the cpp changes and recompile) and Civ4ScreenShot3096 (where issue is solved)); in short if my long sentence still makes sense xd and i didnt get tangled into it if this is a word too but anyways etc anyways etc, default civ4 player game suddenly changed from windows username to steam username (that i didnt want to show in screenshots too as is private to me but anyways etc, and this coincidated if this is a word but anyways etc with this screen being stuck issue))

To solve it, or at least after doing this issue that was reproductible if i am not mistaken is now solved, i deleted (adjust to where your mod path is anyways etc) for example for me this is where the folder temp_files/Release/ is: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\Project\temp_files\Release\ , this folder (i deleted it anyways etc), and after recompiling cleanly, now i can play with windows username as usual, even though i had to change back the steam username to the name i wanted (first manually ingame at new game settings screen, then after seeing it works in CivilizationIV.ini (see [CivilizationIV.ini shortcut for example](/_CivilizationIV.ini%20-%20User%20Shortcut%20Example.lnk))), here and for testing at least if not always or not anyways etc or maybe not but for testing or not if i want or not or and other or and not or do or not or etc or etc anyways etc, the windows username is fine with me ("PC" in the screenshots anyways etc anyways etc...)

Not sure what the issue was, would have liked to be notified of the error/corruption cause of it somehow, but program runs fine as usual now, so maybe corrupted unnotified compilation, or fastdep issue perhaps (even though fastdep compiles seemed to work fine in the past as in just yesterday/the day before for the [unitai renaming (commit)](https://github.com/wonderingabout/AdvCiv-SAS/commit/701e2e31279d7ab152f91b431a81c1bae9c22734) but anyways etc as long as is solved is all good maybe even though bit weird but unsettling but whatever it is/was is maybe consistently solved now (not gauranteed, may or not be the case but anyways etc))

So hopefully fine and solved now even though not sure and not guaranteed but maybe is hopefully or maybe not, in all cases hopefully this info is helpful to me or and others or and not anyways etc anyways etc.

## 6 - (now worked around anyways etc) Too long XML code comments cause errors or/and game crashes

Related to [example/issue 9](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#9---art-and-maybe-other-assets-too-or-not-anyways-etc-xml-assets-silently-causing-a-game-crash-during-initgame-loadstartup-instead-of-telling-us-which-asset-was-missing-no-error)

Be careful of having too long XML code comments, they (seem to indeed but anyways etc) cause game crashes (or maybe errors too? Anyways etc) in some circumstances, i assume it is especially due to or/and caused by if it's not same but anyways etc nested code comments more specifically but anyways, since i don't know more, it is only speculation on my end but anyways etc, but moving these nested code comments outside of the XML did fix the early game crash issue that is reproductible.

Something to keep in mind perhaps if i may say i mean anyways while doing XML code comments, that if they have to be long, move them outside of the XML tree entirely maybe, or at least outside the nested ones maybe, tweak this advice or opinion or feel or not feel or yes feel but maybe rather too view/thought as you see fit and/or want or not, hopefully helpful or not or and other or and not but in all cases maybe or not or yes anyways etc anyways etc anyways etc.

More details here too anyways etc in anyways etc anyways etc anyways etc: [AudioDefines-nested-comments-out-of-xml-file-to-avoid-crash.txt](/Assets/XML/Audio/AudioDefines-nested-comments-out-of-xml-file-to-avoid-crash.txt)

## 7 - Screenshots on multi screen display (if playing civ4 with "windowed" and not fullscreen if i am not mistaken as well anyways etc) don't work if not taken in primary screen

On windows 10 at least if not in other systems as well, at least in my machine but anyways etc, since i play in windowed while debugging and such or/and other dev needs or not which is much more convenient but anyways etc, if i put the game window on my second (or any alternative/equivalent or not that may or not exist and that is not main screen anyways etc) screen, then pressing the - Print Screen - key consistently does not create a new screenshot in (repalce with your relevant user path) `C:\Users\PC\Documents\My Games\beyond the sword\ScreenShots\`, but putting the game window back to main screen, (then) the print screen key successfully creates a new screenshot (image) file, for example Civ4ScreenShot4272.JPG while writing this (could be any but anyways etc anyways etc anyways etc), hopefully helpful or not or yes or and other or and not anyways etc to fix the issue and being able to record screen(shots) again anyways etc.

## 8 - Do not edit python files while running the game, even modifying unused/unreached code may cause weird errors

For example as in [these screenshots (google drive folder link anyways etc)](https://drive.google.com/drive/folders/1gyaLERKrDAUbiQeVWl4S7T7tPJB0soR3?usp=sharing), or to copy the err log (path from Notepad++, adjust with your windows username or/and equivalent configuration/version of this that fits/suits your system username or/and other settings anyways etc (C:\Users\PC\Documents\My Games\beyond the sword\Logs\PythonErr.log) anyways etc.

If such issues happen, maybe restart the game and hopefully all fixed, ideally modify python files before game is launched to prevent that, unless you know what or/and why you are doing (it) or/and other (reason) or and not as you prefer or not or yes or and other or and not anyways etc anyways etc anyways etc

## 9 - Art (and maybe other assets too or not anyways etc) XML assets silently causing a game crash during init/game load/startup instead of telling us which asset was missing (no error)

Related to [example/issue 6](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#6---now-worked-around-anyways-etc-too-long-xml-code-comments-cause-errors-orand-game-crashes)

For example, while i was renaming _GEMS to _GEMSTONES, everywhere (with VS Code global search), except one part i had forgotten:

Like this (Results/status anyways etc shown below thanks to VS Code's global search's "Copy all" UI menu anyways etc):

```
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Art\CIV4ArtDefines_Bonus.xml
  118,23: 			<Type>ART_DEF_BONUS_GEMS</Type>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4BuildingInfos.xml
  6512,22: 					<BonusType>BONUS_GEMSTONES</BonusType>
  6706,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Events\CIV4EventTriggerInfos.xml
  11024,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GameInfo\CIV4CorporationInfo.xml
  236,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4BonusInfos.xml
  1332,15: 			<Type>BONUS_GEMSTONES</Type>
  1333,30: 			<Description>TXT_KEY_BONUS_GEMSTONES</Description>
  1334,30: 			<Civilopedia>TXT_KEY_BONUS_GEMSTONES_PEDIA</Civilopedia>
  1336,31: 			<ArtDefineTag>ART_DEF_BONUS_GEMSTONES</ArtDefineTag>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4ImprovementInfos.xml
  482,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\TrueStarts\CIV4TruBonusInfos.xml
  678,13: 			<Type>TRU_GEMSTONES</Type>
  679,20: 			<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ger.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ita.txt
  2293,14: a(S'HAS_BONUS_GEMSTONES'
  2457,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\WS_CustomDomAdv.txt
  2407,14: a(S'HAS_BONUS_GEMSTONES'
  2572,10: a(S'BONUS_GEMSTONES'
```

Here as seen above, i had forgotten to rename `118,23: 			<Type>ART_DEF_BONUS_GEMS</Type>` to `118,23: 			<Type>ART_DEF_BONUS_GEMSTONES</Type>` as well, but instead of getting the usual error like in unitinfos xml or such from little or not little i experimented ith xml of civ4 in the past since doing this advciv-sas mod anyways etc, here we have a silent crash instead of an error, and inspecting the err log or dbg log of pytohn in civ4 shows us nothing, file is empty, the app init log (in C:\Users\PC\Documents\My Games\beyond the sword\Logs\init.log) is not too helpful either:

```
[38971.390] DBG: CIV Init
[38971.390] VERSION: App: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Civ4BeyondSword.exe
[38971.390] VERSION: Build: Thu May 29 04:28:49 2014
[38971.390] VERSION: 3.1.9.0 (128100)
[38971.718] VERSION: Mod Loaded: Mods\AdvCiv-SAS\
[38971.734] DBG: FILE Cat Init
[38972.234] DBG: Game Init
[38972.234] DBG: Multiplayer Init BEGIN
[38972.328] DBG: Multiplayer Init END
[38972.328] DBG: Audio Init
[38972.625] DBG: ArtFileMgr Init
[38972.625] DBG: Python Init
[38974.343] VERSION: CIV Version: 319
[38974.343] VERSION: Minimum Version: 319
[38974.343] VERSION: Save Version: 14223
[38974.343] DBG: Input Init
[38974.343] DBG: Engine Init
[38974.421] DBG: Checking available screen resolution
[38974.546] DBG: Validating screen resolution
[38974.546] DBG: Creating rendererer
[38974.797] DBG: Engine: renderer Initialized
[38974.797] DBG: Engine: Shaders Initialized
[38974.922] DBG: Engine: Scene Lights Initialized
[38974.922] DBG: Music Start
[38974.938] DBG: Font Init
```

But it seems last element we loaded successfully or (maybe? Anyways etc) crashed at while trying to load anyways etc was "Font"(s?)?? Could this be related to art assests or referring/being a reference/mention to(/of?) them perhaps or not?

In all cases, unless i am mistaken or not too knowledgeable about this issue or this part of civ4 knowledge or experience or and other or and not anyways etc, this does not help us directly like as if for exmapel it told us error missing asset X at line etc asset not found or something.

So it seems art xml assets need special attention especially in the case of errors, not as easy to handle, but fixing it now works:

```
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Art\CIV4ArtDefines_Bonus.xml
  118,23: 			<Type>ART_DEF_BONUS_GEMSTONES</Type>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4BuildingInfos.xml
  6512,22: 					<BonusType>BONUS_GEMSTONES</BonusType>
  6706,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Events\CIV4EventTriggerInfos.xml
  11024,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GameInfo\CIV4CorporationInfo.xml
  236,21: 				<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4BonusInfos.xml
  1332,15: 			<Type>BONUS_GEMSTONES</Type>
  1333,30: 			<Description>TXT_KEY_BONUS_GEMSTONES</Description>
  1334,30: 			<Civilopedia>TXT_KEY_BONUS_GEMSTONES_PEDIA</Civilopedia>
  1336,31: 			<ArtDefineTag>ART_DEF_BONUS_GEMSTONES</ArtDefineTag>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Terrain\CIV4ImprovementInfos.xml
  482,22: 					<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\TrueStarts\CIV4TruBonusInfos.xml
  678,13: 			<Type>TRU_GEMSTONES</Type>
  679,20: 			<BonusType>BONUS_GEMSTONES</BonusType>

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ger.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv_ita.txt
  2293,14: a(S'HAS_BONUS_GEMSTONES'
  2457,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\CustomDomAdv.txt
  2549,14: a(S'HAS_BONUS_GEMSTONES'
  2706,10: a(S'BONUS_GEMSTONES'

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Settings\CustomDomAdv\WS_CustomDomAdv.txt
  2407,14: a(S'HAS_BONUS_GEMSTONES'
  2572,10: a(S'BONUS_GEMSTONES'
```

like this:   `118,23: 			<Type>ART_DEF_BONUS_GEMSTONES</Type>`, now works and game can start fine and all at least in main menu anyways etc.

Something to keep in mind if i may say anyways etc if having we/i/you or and other or and not anyways etc have a crash after modifying art assets, but no idea why, it could be linked to this issue or something similar, ideally we'd get a nice error crash message and such, but comitting in smalle rchunks ideally and testing at each step occasionally or lot or not may help prevent or spot these, hopefully this message or rather anyways etc note here in this doc of known civ4 issues also helps me or and other or and not reading this or not or yes or etc or and other or and not anyways etc anyways etc anyways etc...

Also for info init log after successfully load is like this after fixing it and successfully finally (even though was not long but as in/in terms of having success step now if i may say anyways etc anyways etc anyways etc or not or yes or and other or and not anyways etc) anyways etc:

```
[39838.765] DBG: CIV Init
[39838.781] VERSION: App: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Civ4BeyondSword.exe
[39838.781] VERSION: Build: Thu May 29 04:28:49 2014
[39838.781] VERSION: 3.1.9.0 (128100)
[39839.109] VERSION: Mod Loaded: Mods\AdvCiv-SAS\
[39839.109] DBG: FILE Cat Init
[39839.609] DBG: Game Init
[39839.625] DBG: Multiplayer Init BEGIN
[39839.734] DBG: Multiplayer Init END
[39839.765] DBG: Audio Init
[39840.078] DBG: ArtFileMgr Init
[39840.078] DBG: Python Init
[39841.812] VERSION: CIV Version: 319
[39841.812] VERSION: Minimum Version: 319
[39841.812] VERSION: Save Version: 14223
[39841.812] DBG: Input Init
[39841.812] DBG: Engine Init
[39841.890] DBG: Checking available screen resolution
[39842.015] DBG: Validating screen resolution
[39842.015] DBG: Creating rendererer
[39842.250] DBG: Engine: renderer Initialized
[39842.250] DBG: Engine: Shaders Initialized
[39842.375] DBG: Engine: Scene Lights Initialized
[39842.375] DBG: Music Start
[39842.391] DBG: Font Init
[39842.406] DBG: Begin MenuManager
[39842.406] DBG: Total Frame MS: 3681.0  FPS: 000  Min:000 Max:000 Avg:000  SampleFilter:10.000000
 Time   :   Ave  :  Min% :  Max% : Num : Profile Name
-----------------------------------------------------
--------------------------------------------------
```

Anyways etc anyways etc anyways etc...

## 10 - some text characters in XML TXT_KEY tags are not displayed correctly ingame (as `?` or causing other arti(e?)facts maybe too indeed for example anyways etc), while some like `&` cause an XML error and asset failing to load entirely if i am not mistaken anyways etc

Some characters are not displayed correctly and instead show as `?` or cause weird arte(i?)facts like being bold inconsistently or such, here are a few examples here in this [Google Drive folder link](https://drive.google.com/drive/folders/1LeTNL4kKHgQJdZ0mLNzHaOCKkenR9duh?usp=sharing).

They genererally are language specific chars, for example some chars in `Phāṇita` or `Bhāvaprakāśa` or  maybe too (test to be sure if this point/issue i am raising is accurate or not, should be but may not be valid/updated anymroe if someone fixed it somehow or/and othe ror if i am mistaken or maybe not or yes or not or and other or and not anyways etc). Or some other examples like `खण्ड` or such anyways etc are likely to not display correctly or/and cause errors (check ingame or in docs or woemwhere where you can find such info or and other or and not as you prefer or and not or other or and not anyways etc anyways etc anyways etc).

Some characters like the `&` seem to cause an XML error with a real error message and such, and asset failing to load entirely (revert to base civ4 one rather than our version of it), see screenshots for details in the drive link above for details.

And some characters like `–` seem to cause the text to be weird and inconsistently bold (see screenshot(s) for example if provided indeed or not or yes or and other or and not anyways etc)

The solution i use is to simplify these chars generally, for example rename `–` to `-`, or using `_` instead of `खण्ड` to signify it is a language char (some other approaches may work like romanizing, it is an example i went with most simple and accurate in my case/need anyways etc anyways etc anyways etc...), or rename for example `Phāṇita` to `Phanita`, or for example also `Dačice` to `Dacice` (again is an example do as you prefer or not or do or not or and other or and not anyways etc anyways etc anyways etc...)

Adjust this advice/feedback as you see fit or not fit or not see or not adjust or not or yes or and other or and not, hopefully helpful or not or yes or and other or and not anyways etc anyways etc anyways etc...

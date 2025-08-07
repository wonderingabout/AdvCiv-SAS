# Known issues

Some known issues (non-exhaustive ideally yes but maybe not anyways etc) about AdvCiv code or earlier or/and AdvCiv-SAS specific code that may be fixed someday or not (ideally yes too same but maybe not especially if deemed not so bad or even part of the necessary mechanic but then would not be an issue but if known maybe or not or yes but anyways etc anyways etc anyways etc).

Note: if a google drive link is missing or redundantly copy pasted from one known issue to another, you might be able to find it in their parent folder if i may say in this case but anyways etc here in this [Base AdvCiv issues examples](https://drive.google.com/drive/folders/11wTFHidBHTutXXyiaRAhayA7y7d5Rg-8?usp=sharing). Not all issues have a drive folder, but as of now most do.

hopefully helpful, thanks, anyways, thanks,

## 1 - Redundant attribute values for all AI Civs

Some known issues, that will not necessarily be fixed, but maybe or not but anyways, however good and maybe useful to keep them as reminder in case we want or for souvenir, anyways:

- while debugging the new ai personality feature in the sevopedia in advciv-sas (our mod), we found some information that some ai attributes seem to be shared accross all leaders:

```log
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

Some of these such as iLoveOfPeace are not used in AdvCiv; i disabled (commented-out) from display (in SevoPediaLeader.py) such unused ai attributes to not clutter the display, see [README.md#sevopedia-reworks-ai-personality-panel-and-other-sevopedia-reworks](/README.md#sevopedia-reworks-ai-personality-panel-and-other-sevopedia-reworks) for (more) details, and more specifically in the full AI Personality Panel Feature this [README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored).

Leaving as is otherwise (except from hiding most or/and commenting out unused ones such as iLovePeace (in AdvCiv) anyways) for now if not always or not anyways etc.

We may also spread some values more (i.e. in AdvCiv-SAS etc anyways) that are way too often shared between leaders, not just the common to all leaders, may be a good opportunity perhaps, but not sure or guarnateed, for now only mentioning the issue.

## 2 - (now fixed) Gandhi's base leaderheadinfo's xml had nowarattitudeprob pleased(110)/pleased(115) duplicated instead of (as i suspect it should be anyways etc) pleased(110)/friendly(115)

For example, i had spotted a seemingly mistake/typo/bug in Gandhi's nowar attributes (from AdvCiv), where pleased was repeated twice, while enhancing and adding on the generate_leaders_data.py (see the [README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module) for details) script:

```json
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

```json
            {
                "AttitudeType": "ATTITUDE_FRIENDLY",
                "iNoWarProb": "115"
            }
```

Our generate_leaders_data.py (see the [README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Python_Scripts.md#generate_leaders_datapy-script-and-leaders_datapy-module) for details) sucessfully detected/detects it, for example before fixing the XML of Gandhi we have:

```cmd
Microsoft Windows [version 10.0.19045.5737]
(c) Microsoft Corporation. Tous droits réservés.

C:\Users\PC>cd C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\ & python generate_leaders_data.py
[WARNING] Duplicate NoWarAttitudeProb 'ATTITUDE_PLEASED' for leader LEADER_GANDHI
[SUCCESS] Leader data written to: leaders_data_20250426_100035.py

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>
```

And after fixing Gandhi's XML we now have:

```cmd
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>cd C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\ & scan_xml_duplicates-3.3.py
[SUCCESS] Leader data written to: leaders_data_20250426_100152.py

C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS>
```

So i had the idea to generalize this approach to find if we don't have other such duplicates and perhaps may improve our XML data and reliability, and the result is as explained in the [README_Python_Scripts.md#scan_xml_duplicates-py-script-and-logs_xml_scans](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Python_Scripts.md#scan_xml_duplicates-py-script-and-logs_xml_scans) (see it for details), currently if not always or not etc anyways version 3.3 as per chatgpt's naming and greta help in doing this (coded all i only gave pointers and feedback, joint collaboration hehe anyways.)

Since there are false positives, i am not sure how to interpret it, but hopefully useful enopugh, so adding this script here, and funcitonal enough (skim through results you known false for example maybe i mean, anyways)

Results are very good, if you have good eyes or are very patient or/and know where and what to look at or/and other things or not anyways, we successfully spot it specifically (Gandhi's seemingly('s?) mistake/typo/bug)

A few screenshots of the issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1WNHP4fQQ1Dbm4JnXx9YDedCnLzrOO8ey?usp=sharing)

## 3 - (now fixed with a DLL patch) Barbarians (cities) building wonders, in particular now fixed i.e. disabled for world wonders anyways etc

In base advCiv code, after implementing the barbarians boost to make them more economically viable and/or strong but anyways etc anyways etc anyways etc... Barbarians are still trying to build wonders sometimes, the base AdvCiv code does not prevent that, or/and at least not always maybe or not or yes indeed but anyways etc anyways etc ; and even complete them sometimes actually, for example(s anyways etc anyways etc):

A few screenshots of the issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1p5O09XzbbrM5x2hxFD6RGvBpuU8RzPAd?usp=sharing)

There may be(/have been, but anyways etc) other cases like these, and i don't know if the cause is one of the changes i made to barbarian (xml) code, or how it just is/was. I tried to fix it by using iWonderConstructRand -9999 on LEADER_BARBARIAN in leader head infos xml file, but they still build national and world wonders alike, and all the buildingclass NONE spaghetti code whether it is here (for national wonders) or not (for world wonders) does not change anything, they even build shrines like the mahadhobi as of now me writing this anyways, is not necessarily a bad design, but ideally i would want them to focus more on warmongering their key rol in advciv-sas and be more efficient in that anyways etc.

So/And anyways etc i removed all such old logic of buildingclass NONE in (adjust if non-steam game or other mod path you have to where your advciv-sas or/and other mod you're using or not etc anyways etc is anyways etc) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Civilizations\CIV4CivilizationInfos.xml`.

I had tried tweaking/changing WonderConstructRand but seemingly no change at all.

I had also tried using BuilUnitProb 100  or similar in leader barbarian XML, but although it seemed to have helped in most cases, in some cases barbarians would still build world wonders.

Lines such as:

```xml
				<Building>
					<BuildingClassType>BUILDINGCLASS_GREAT_WALL</BuildingClassType>
					<BuildingType>NONE</BuildingType>
				</Building>
```

Were totally ineffective, so i have removed them as well for as of now for wonders i mean if i may say but anyways etc.

Thanks to chatgpt's help, and following recent as of now DLL changes such as in [README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive), it seems to finally be fixed by patching the DLL directly instead in [/CvGameCoreDLL/CvCityAI.cpp](/CvGameCoreDLL/CvCityAI.cpp), as of now only for world wonders (no need to forbid national wonders too strongly as of now at least if not always or not or yes or etc but anyways etc)

## 4 - (now fixed) Sevopedia Unit's placeRequires's Religion button (for example any religious missionary unit) not redirecting to sevopedia religion (nothing happens on click anyways etc)

Now fixed: by replacing, in sevopediaunit py file, in placeRequires function/method (of this file anyways etc), `WidgetTypes.WIDGET_HELP_RELIGION` with `WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION`(,) as is done already by base advciv and successfully in sevopedia building, anyways etc anyways etc anyways etc.

This is a bug i have noticed in AdvCiv and after checking, many other mods, among those (few i tried): ROM 291, RFC DOC, Neoteric World (since i have it too (to check their sevopedia content or/and such or/and other or/and not anyways) even though i did not use anything from it at least but may be useful some day or not anyways etc anyways etc), History Rewritten too.

But clicking in AdvCiv in sevopediabuilding for example on any religious temple's placeRequires's religious icon/button successfully redirects to the sevopedia's religion page.

Among the mods i tried, only Realism Invictus's sevopedia unit's placerequires's religion button works as intended and successfully redirects to the religion's page

I tried to import its code but their gc uses difference methods that we don't have it seems like getNumPrereqAndBonuses and such, may not be hard to fix or not, but leaving as is, finding how realism invictus does it, or finding yourself the cause if you want to investigate it, may help solve it.

As for me this is quite minor, and even though i would have loved (really) to fix it (but anyways etc), leaving a note here rather as i don't know also how nested in the code the issue is, i would ideally but anyways love to dive deeper but doing other code things, at least for now if not always or maybe not, but anyways etc, if so (that i would look again), hopefully these lines may (then) serve as a reminder of the issue and the current status of solving it (i have found in realism invictus mod it works fine unlike in other mods (that i tried about/for this issue anyways etc), can investigate from there maybe anyways etc)

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1vRIFzwNijAjbmPBVUvSk90YjURXh-lG1?usp=sharing)

## 5 - (seemingly worked around now) player name same as windows (10's for example anyways etc) username causes new game screen to be stuck unless a custom name is chosen, if/after/while DLL has been fastdep compiled

A quite weird issue i never had before, but after doing a fastdep (auto, not me), since i changed only one .cpp file to add the placeCivilizations new sevopedia feature (see the [README_Sevopedia_Reworks.md#example-7-unit-list-category](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md#example-7-unit-list-category) for details)

A few screenshots of the issue here in as well as the DLL with which i had the issue (not sure is the cause but happened while having it if i am not mistaken anyways etc) [this Google Drive folder](https://drive.google.com/drive/folders/19T9I75vGCk58pFSR60y2Tmj69-NoFFtk?usp=sharing)

More context of how i implemented the change in the .cpp and such can be found in this Google Drive about Claude AI's first prompt i successfully implemented in AdvCiv-SAS, [by finding such a (Google Drive too anyways etc) link in the Claude AI part of the README there (click on this link to be redirected anyways etc)](/README.md#claude-ai-the-newcomer-hehe-xd-anyways-etc-welcome-anyways-etc)

I don't know if fastdep compiel was the cause or just some weird corruption unnotified happened (i don't know a lot about these if at all hehe but it was reproductible, and my player name also unusually changed just after this fast compile so i can quite confidently say it is maybe indeed related but anyways etc (for example after checking indeed Civ4ScreenShot3010 in the advciv-sas's mod journey drive (see main README.md for link anyways etc), with last compiled DLL before this Claude AI related .cpp change and recompile, had my windows username as default player name as can be seen in screenshot, but the screenshots of the issue in the drive linked above, that happen between Civ4ScreenShot3095(new game not yet started after the cpp changes and recompile) and Civ4ScreenShot3096 (where issue is solved)); in short if my long sentence still makes sense xd and i didnt get tangled into it if this is a word too but anyways etc anyways etc, default civ4 player game suddenly changed from windows username to steam username (that i didnt want to show in screenshots too as is private to me but anyways etc, and this coincidated if this is a word but anyways etc with this screen being stuck issue))

To solve it, or at least after doing this issue that was reproductible if i am not mistaken is now solved, i deleted (adjust to where your mod path is anyways etc) for example for me this is where the folder temp_files/Release/ is: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\Project\temp_files\Release\ , this folder (i deleted it anyways etc), and after recompiling cleanly, now i can play with windows username as usual, even though i had to change back the steam username to the name i wanted (first manually ingame at new game settings screen, then after seeing it works in CivilizationIV.ini (see [CivilizationIV.ini shortcut for example](/_CivilizationIV.ini%20-%20User%20Shortcut%20Example.lnk))), here and for testing at least if not always or not anyways etc or maybe not but for testing or not if i want or not or and other or and not or do or not or etc or etc anyways etc, the windows username is fine with me ("PC" in the screenshots anyways etc anyways etc...)

Not sure what the issue was, would have liked to be notified of the error/corruption cause of it somehow, but program runs fine as usual now, so maybe corrupted unnotified compilation, or fastdep issue perhaps (even though fastdep compiles seemed to work fine in the past as in just yesterday/the day before for the [unitai renaming (commit)](https://github.com/wonderingabout/AdvCiv-SAS/commit/701e2e31279d7ab152f91b431a81c1bae9c22734) but anyways etc as long as is solved is all good maybe even though bit weird but unsettling but whatever it is/was is maybe consistently solved now (not gauranteed, may or not be the case but anyways etc))

So hopefully fine and solved now even though not sure and not guaranteed but maybe is hopefully or maybe not, in all cases hopefully this info is helpful to me or and others or and not anyways etc anyways etc.

See also [README_Known_Issues_In_Base_AdvCiv_Civ4.md#38---no-idea-why-but-anyways-etc-sometimes-compile-mysteriouslystrangelyinconsistently-fails-and-recompiling-succeeds-underwith-but-anyways-etc-exact-same-source-files-if-i-am-not-mistaken-but-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#38---no-idea-why-but-anyways-etc-sometimes-compile-mysteriouslystrangelyinconsistently-fails-and-recompiling-succeeds-underwith-but-anyways-etc-exact-same-source-files-if-i-am-not-mistaken-but-anyways-etc)

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

For example, while i was renaming `_GEMS` to `_GEMSTONES`, everywhere (with VS Code global search), except one part i had forgotten:

Like this (Results/status anyways etc shown below thanks to VS Code's global search's "Copy all" UI menu anyways etc):

```log
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

```log
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

```log
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

```log
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

They genererally are language specific chars, for example some chars in `Phāṇita` or `Bhāvaprakāśa` or  maybe too (test to be sure if this point/issue i am raising is accurate or not, should be but may not be valid/updated anymroe if someone fixed it somehow or/and other or if i am mistaken or maybe not or yes or not or and other or and not anyways etc). Or some other examples like `खण्ड` or such anyways etc are likely to not display correctly or/and cause errors (check ingame or in docs or woemwhere where you can find such info or and other or and not as you prefer or and not or other or and not anyways etc anyways etc anyways etc).

Some characters like the `&` seem to cause an XML error with a real error message and such, and asset failing to load entirely (revert to base civ4 one rather than our version of it), see screenshots for details in the drive link above for details.

And some characters like `–` seem to cause the text to be weird and inconsistently bold (see screenshot(s) for example if provided indeed or not or yes or and other or and not anyways etc)

The solution i use is to simplify these chars generally, for example rename `–` to `-`, or using `_` instead of `खण्ड` to signify it is a language char (some other approaches may work like romanizing, it is an example i went with most simple and accurate in my case/need anyways etc anyways etc anyways etc...), or rename for example `Phāṇita` to `Phanita`, or for example also `Dačice` to `Dacice` (again is an example do as you prefer or not or do or not or and other or and not anyways etc anyways etc anyways etc...)

Adjust this advice/feedback as you see fit or not fit or not see or not adjust or not or yes or and other or and not, hopefully helpful or not or yes or and other or and not anyways etc anyways etc anyways etc...

## 11 - In Debug mode, in map view, unexplored tile by the active player (if i am not mistaken see below anyways etc) if improved, shows as red for example "with Road" or "with Pasture", even though a road is already there and text should be white instead or removed entirely if i am not mistaken anyways etc ; and other weird debug mode display issue(s)

This is a small bug so just mentioning it, and perhaps it is even intended to be this way, but ideally in debug mode (ctrl+z and "chipotle" anyways etc), an unexplored tile by the tile active player (if i am not mistaken about what an active player is or seems to be (the current player, at least our autoplayed on player anyways etc)), even if unexplored but anyways etc, if improved, should should its improvement requirement as white not red or simply remove the improvement (or road too if i am not mistaken? Anyways etc) line entirely (i assume DLL handles this like in sevopedia? Anyways etc)

As this is debug-only, and to not cause further issues, only mentioning it for now and not fixing it, screenshots about this issue, may be useful someday or not but anyways etc

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1lXQ8pyE0A6TJGqlnf4In3V7QuJ0lBhIR?usp=sharing)

Another weird display issue/bug in debug mode is for examples yields are not accurately accounted in some conditions, for example in screenshots 5465, 5466, 5467 of/in the drive link just above anyways etc, sheep plains natural yield should be 1 food of plains + 1 food natural yield change of sheep if i am not mistaken so 2 food, but is displayed as 1 food only for this tile with map reveal (ctrl+z debug mode anyways etc) vs 2 food accurately seemingly, without map reveal. I don't know what the exact issue is as i didn't investigate it, but still is an issue, just mentioning it here, may be helpful or not or yes or and other or and not, hopefully exhaustive too or not or yes or and other or and not as i wanted or not wanted or yes wanted or other or and not, but anyways etc anyways etc anyways etc...

## 11.2 - In debug mode, another weird bug is at wonder list while world wonder has not been built in said civs at least not all anyways etc

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1dtHQbjW9Z55O_KryENWcJsrlMhUVqyTH?usp=sharing)

Similarly to [known issue number 11](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#11---in-debug-mode-in-map-view-unexplored-tile-by-the-active-player-if-i-am-not-mistaken-see-below-anyways-etc-if-improved-shows-as-red-for-example-with-road-or-with-pasture-even-though-a-road-is-already-there-and-text-should-be-white-instead-or-removed-entirely-if-i-am-not-mistaken-anyways-etc--and-other-weird-debug-mode-display-issues), this seems to be a debug mode only bug, as when toggling off debug mode while still in same game (ctrl+z if i am not mistaken as of now if not always or not but anyways etc), a wonder is shown to have been built by many civs, with the date showing hammer icon instead of a data number year or such, and looking inside said cities, no world wonder exists, so this seems to be a visual bug specific to debug mode if i am not mistaken, i didn't check all cities, but a few said to have the world wonder didn't have it, and since it is supposed to be "unique" i.e. only 1 in entire world (not civ-specific as civ4 says about "unique" in another way but anyways etc) i forgot my sentence but anyways etc i assume this is not too important to fix, but mentioning it for exhaustiveness and in case it helps but or not but or yes but but anyways etc

## 12 - (now fixed) Special/generic building monastery's button inconsistently using (uses/was using rather anyways etc) the hindu specific anyways etc monastery button instead of a generic button like the (abstract? Anyways etc / generic) generic temple and generic cathedral were

Hopefully clearer and more consistent now or not or yes or etc or and other or and not or yes or etc anyways etc

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1LyGR9fEuI6HZLtn-R5qxgdlVFPVmhUAc?usp=sharing)

## 13 - (now fixed/reworked) As an appendix to 12 - just before anyways etc, shrines now also appear in tech tree at their religion's tech requirement unlike in base advciv / civ4 too if i am not mistaken anyways etc

Added a PrereqTech for shrines so we can display them in tech tree as well, plus now shrines cannot be built without also having the religion's tech matching (for example during conquest or such, anyways etc), since shrines are not special buildings unlike temple, monastery, cathedral, maybe this is a fine even desirable way to handle it or not or yes or etc or and other or and not but anyways etc, was NONE.

A few screenshots of after the fix/rework (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue/rework anyways etc](https://drive.google.com/drive/folders/1kIRImlhvrB7-65lYNXm46M28FvWOT3f7?usp=sharing)

## 14 - (now removed/fixed if it is a fix anyways etc) duplicate ArtRef Name="building:BUILDING_LIGHTHOUSE" and same for ArtRef Name="building:BUILDING_HARBOR" and ArtRef Name="building:BUILDING_CARTHAGE_COTHON" in CIV4CityLSystem.xml anyways etc

in (adjust to your mod path anyways etc) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Buildings\CIV4CityLSystem.xml`

removed this:

```xml
		<ArtRef Name="building:BUILDING_LIGHTHOUSE">
			<Attribute Class="Era">ERA_ANCIENT,ERA_CLASSICAL,ERA_MEDIEVAL,ERA_RENAISSANCE</Attribute>
			<Attribute Class="Scalar">bNoWaterTest:1</Attribute>
			<!-- this bypasses water testing -->
			<Attribute Class="Scalar">szSpecialLayout:Water</Attribute>
			<Scale>1.5</Scale>
		</ArtRef>
```

in:

```xml
		<ArtRef Name="building:BUILDING_LIGHTHOUSE">
			<Attribute Class="Era">ERA_ANCIENT,ERA_CLASSICAL,ERA_MEDIEVAL,ERA_RENAISSANCE</Attribute>
			<Attribute Class="Scalar">bNoWaterTest:1</Attribute>
			<!-- this bypasses water testing -->
			<Attribute Class="Scalar">szSpecialLayout:Water</Attribute>
			<Scale>1.5</Scale>
		</ArtRef>
		<ArtRef Name="building:BUILDING_LIGHTHOUSE">
			<Attribute Class="Scalar">szNIF:Art/Structures/Buildings/Lighthouse/LighthouseModern.nif</Attribute>
			<Attribute Class="Era">ERA_INDUSTRIAL,ERA_MODERN,ERA_FUTURE</Attribute>
			<Attribute Class="Scalar">bNoWaterTest:1</Attribute>
			<!-- this bypasses water testing -->
			<Attribute Class="Scalar">szSpecialLayout:Water</Attribute>
			<Scale>1.5</Scale>
		</ArtRef>
```

seems like a duplicate, should be safe to remove, but marking it down here if i may say as i don't know a lot about these and to be safe, should be safe to do so though but is for exhaustiveness too perhaps, but anyways etc anyways etc anyways etc...

also note as in code comment of it anyways etc edited or not or yes or anyways etc to fit quite well in this .md readme anyways etc: "<!-- custom: remove seemingly duplicate `<ArtRef Name="building:BUILDING_LIGHTHOUSE">` (removed 1st occurence to be safe that it is not the one used in the game, the 2nd one seems more exhaustive too from the little i can see of it but anyways etc) anyways etc -->

did similarly for the `<ArtRef Name="building:BUILDING_HARBOR">` and `<ArtRef Name="building:BUILDING_CARTHAGE_COTHON">` seemingly duplicated too anyways etc

see some screenshot(s) about this issue in this [google drive folder link](https://drive.google.com/drive/folders/1vP6L16r3PJ0qpwzqOfeycuaTRDKZbNCr?usp=sharing) anyways etc

## 15 - (now fixed) Missing this technology "Cannot be traded" (bTrade if i am not mistaken anyways etc) information in sevopedia tech and tech advisor anyways etc

Fixed missing this technology "Cannot be traded" information in sevopedia tech "Special Abilities" (placeSpecial in py code if i am not mistaken anyways etc) and in tech/technology advsior anyways etc too anyways etc anyways etc anyways etc, see also [README.md#other-advciv-sas-changes-examples](/README.md#other-advciv-sas-changes-examples) for details anyways etc and [Modding_Ressources/README.md#example-of-dll-modification-of-cvgametextmgrcpp-and-other-related-files-to-add-the-new-this-technology-cannot-be-traded-flag-in-sevopedia-tech-s-placespecial-and-in-tech-tree-view-technology-advisor-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/Modding_Ressources/README.md#example-of-dll-modification-of-cvgametextmgrcpp-and-other-related-files-to-add-the-new-this-technology-cannot-be-traded-flag-in-sevopedia-tech-s-placespecial-and-in-tech-tree-view-technology-advisor-anyways-etc) for a lot more details too but anyways etc anyways etc anyways etc hopefully helpful or not or yes or other or etc or yes or other or etc or not or yes or etc but anyways etc

See also [README_Sevopedia_Reworks.md#example-10-techs-category](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md#example-10-techs-category) for details or/and additional info anyways etc.

## 16 - (now fixed) some info is missing in sevopedia outside of/if not loaded from an ingame load for example "Can build research" not in sevopedia main menu but in sevopedia ingame (after map is loaded) anyways etc

Click here to view examples of this issue [in this google drive folder link](https://drive.google.com/drive/folders/1LuVa_Y0XBIeC1VExD7KVrY8siEFYyE3n?usp=sharing)

Some info seem to be missing from sevopedia loaded from main menu (screenshot 6680 for example in drive link above anyways etc) vs same sevopedia page loaded from ingame (screenshot 6681 similarly from there i mean anyways etc), for example at tech_writing, "Can Build Research" is missing from the tech_writing sevopedia page at main menu, but not missing from the same tech_writing page ingame.

Not solving it and at least not now didn't investigate it, but good to mention it somewhere, since sevopedia is meant mostly to be used ingame hopefully fine (enough but anyways etc even though not ideal but anyways etc), but ideally would fix and/or investigate it too, but not guaranteed, may or may never/not do so.

## 17 - (now fixed) missing BBAI getters expose them to sevopedia leader info in gc too for display anyways etc

Click here to view examples of this issue [in this google drive folder link](https://drive.google.com/drive/folders/1wFSJ6huis6w_xg-OmrZGE2Scw8PRhI7e?usp=sharing)

Similarly to fetching most fields of leader info now directly from XML and not strictly requiring leaders_data.py, at least in debug functions, we need/miss the (BBAI but anyways etc) victory weights in the sevopedia leader gc's methods it seems if i am not mistaken (see [Sevopedia/__SevoPediaLeader-gc-inner-debug-content.txt](/Assets/Python/Contrib/Sevopedia/__SevoPediaLeader-gc-inner-debug-content.txt) for details, now added the new methods as part of this fix as shown below, see also drive link above in this example issue too anyways etc)

The XML is like this as reminder anyways etc for example for leader_gandhi anyways etc:

```xml
		<LeaderHeadInfo> <!-- custom: Gandhi (add leader name here too for easier vs code tree read while in the file) -->
			<Type>LEADER_GANDHI</Type>
			<Description>TXT_KEY_LEADER_GANDHI</Description>
			<Civilopedia>TXT_KEY_LEADER_GANDHI_PEDIA</Civilopedia>
			<ArtDefineTag>ART_DEF_LEADER_GANDHI</ArtDefineTag>
			<iWonderConstructRand>10</iWonderConstructRand>
			<iBaseAttitude>2</iBaseAttitude>
			<iBasePeaceWeight>10</iBasePeaceWeight>
			<iWarmongerRespect>0</iWarmongerRespect>
			<iEspionageWeight>50</iEspionageWeight>
			<iRefuseToTalkWarThreshold>6</iRefuseToTalkWarThreshold>
			<iNoTechTradeThreshold>15</iNoTechTradeThreshold>
			<iTechTradeKnownPercent>20</iTechTradeKnownPercent>
			<iMaxGoldTradePercent>10</iMaxGoldTradePercent>
			<!-- BBAI Victory Strategy -->
			<iCultureVictoryWeight>45</iCultureVictoryWeight>
			<iSpaceVictoryWeight>30</iSpaceVictoryWeight>
			<iConquestVictoryWeight>0</iConquestVictoryWeight>
			<iDominationVictoryWeight>5</iDominationVictoryWeight>
			<iDiplomacyVictoryWeight>70</iDiplomacyVictoryWeight>
			<!-- BBAI Victory Strategy -->
			<iMaxWarRand>400</iMaxWarRand>
			<iMaxWarNearbyPowerRatio>100</iMaxWarNearbyPowerRatio>
			<iMaxWarDistantPowerRatio>60</iMaxWarDistantPowerRatio>
```

To do that, and expanding on previous debugging now successful of flavors, nowarattitudeprobs, contact fields, and memory fields (note about all these fields see also [Sevopedia/_sevopedia_helpers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py)), only BBAI victory weights remain so that we may fetch all directly from XML or at least be able to attempt to do so without requiring ideally leaders_data.py anymore (leave it for external non-civ4 ingame data such as comparison .csv tables perhaps anyways etc), after asking chatgpt too, we/i noticed for example for `getMaxWarRand` (if we want to see where the BBAI is missing that getMaxWarRand is though for example if i am not mistaken to hopefully add it in this case but anyways etc) (with VS Code 's global search too i noticed it i mean if i may say indeed but anyways etc (see screenshots for details/examples anyways etc)), modified the (adjust to your mod path anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CyInfoInterface3.cpp file to add such new getters, and also reusing existing getter names for such BBAI victory weights fields that are/were already anyways etc existing in (adjust to your mod path anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvInfo_Civilization.h anyways etc, with chatgpt's help too and my prompts too but anyways etc

Now the getters are added in sevopedia leader, and we successfully see the real DLL modified if i am not mistaken values for the victory weights too, for example for leader gandhi as of now anyways etc:

(from [Sevopedia/_sevopedia_helpers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_helpers.py) too example of output from ingame debug log anyways etc)

```text
==== BBAI VICTORY WEIGHTS ====

Culture Victory Weight: 48
Space Victory Weight: 31
Conquest Victory Weight: -5
Domination Victory Weight: 0
Diplomacy Victory Weight: 79
```

Nice to have this data as well now, as is in our XML too, we may use it to remove the leaders_data.py dependency from our intial old code that depends on this external script due to no BBAI weights before in leader info in sevopedia, and also because i didn't know at the time how to access contact fields, i hadn't thought to inspect gc and gc leader info ('s inner debugn link above in this example issue anyways etc) as well anyways etc perhaps for other uses maybe or not or yes or and other or and not anyways etc, for now we added the data at least.

Note: the value seem/are different from raw xml fields's values, this seems normal as well if i am not mistaken as the DLL alters/modifys the values in some conditions or something, may be better to replicate/display the real DLL specific/advciv(-sas in our case i.e. advciv-sas but anyways etc) ingame data as it is and if i am not mistaken too but in all cases anyways etc

## 17.5 - (now fixed) similarly missing base advciv if i am not mistaken anyways etc specific xml fields in gc of sevopedia leader, now exposed there as well these new getCityRefuseAttitudeThreshold and getNativeCityRefuseAttitudeThreshold anyways etc

Now exposed(/exposing?) these to python as well of gc 's sevopedia leader as well, similarly to how BBAI victory wieghts are now exposed too/as well anyways etc: getCityRefuseAttitudeThreshold and getNativeCityRefuseAttitudeThreshold

## 18 - Very inconsistent naming in some assets

For example _UTOPIA for `_COMMUNISM`, `_OBELISK` for monument sometimes and other times if i am not mistaken it means the actual `_OBELISK`, also for example anyways etc `_CHINESE` being inconsitently but anyways etc unrelated to the chinese empire but instead in some cases to the default art asset of a unit for the asian civilizations in general if i am not mistaken, also using but anyways etc anyways etc anyways etc... `_GREAT_PALACE` instead of `_FORBIDDEN_PALACE` (as was hinted or rather i noticed from a base advciv code comment i am thankful for but anyways etc) i have renamed them as much as i found or/and could and wanted, actually a lot earlier in mod development than when i wrote this example issue, but solving them bit by bit as i see them and or want to ideally too but not guaranteed may or may not but anyways etc.., in all cases anyways etc hopefully asset naming is a lot clearer or/and consistent at least for those i went through, probably did not do all as for remaining ones is wait and see if i may say but anyways etc anyways etc anyways etc...

## 19 - (now removed for the one/those i spotted anyways etc) Unused art assets

Screenshots related to this issue in [this google drive link folder](https://drive.google.com/drive/folders/1Ie5Uln9-vquy601oCUex3QIsgWCGnUXl?usp=sharing) anyways etc

Quite related to [README_Known_Issues_In_Base_AdvCiv_Civ4.md#14---now-removedfixed-if-it-is-a-fix-anyways-etc-duplicate-artref-namebuildingbuilding_lighthouse-and-same-for-artref-namebuildingbuilding_harbor-and-artref-namebuildingbuilding_carthage_cothon-in-civ4citylsystemxml-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#14---now-removedfixed-if-it-is-a-fix-anyways-etc-duplicate-artref-namebuildingbuilding_lighthouse-and-same-for-artref-namebuildingbuilding_harbor-and-artref-namebuildingbuilding_carthage_cothon-in-civ4citylsystemxml-anyways-etc) and also while cleaning up in [README_Known_Issues_In_Base_AdvCiv_Civ4.md#18---very-inconsistent-naming-in-some-assets](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#18---very-inconsistent-naming-in-some-assets)

The `ART_DEF_UNIT_ARCHER_EURASIAN` (see screenshots 6708, 6709, 6710, 6711 in drive linked in/at this example issue anyways etc for what it looks like anyways etc) seems to be unused in base advciv, in civ4 too if i am not mistaken, and in most mods it seems as well if i am not mistaken from a VS Code global search but anyways etc.

Note: the `ART_DEF_UNIT_ARCHER_CHINESE` (see screenshot 6705 similarly anyways etc) now renamed to `ART_DEF_UNIT_ARCHER_ASIAN` for consistency is used though if i am not mistaken as the asian civilizations spearman art asset if i am not mistaken, anyways etc, so keeping it and removing instead the unused in base advciv and in our mod too `ART_DEF_UNIT_ARCHER_EURASIAN` as said before in previous sentence/paragraph if i am not mistaken too but anyways etc anyways etc anyways etc...

Also, if we want an art asset, we can always fetch it / import it from one of the many many existing mods i mean if i may say instead but the civ4 ones are cool too if we need them but and or else but anyways etc we can import the ones we need from mods (or and/from base civ4 but anyways etc), but since we don't use the art asset and it seems to indeed if i am not mistaken be unused, remove it entirely, simpler and cleaner and more consistent with our code and ideally is how id want to do it but anyways etc anyways etc anyways etc, may readd if need(ed?), but most likely won't, but whether i add it or not is as it is etc in this case etc but anyways etc anyways etc anyways etc ; maybe it served some purpose to reference/list it ther eif players or/and modders would want to know it is available in this case but anyways etc, but maybe we can remove it now as we can import many art assets from other mods in this case i mean is kind of them to have kept it but also inefficient in all cases maybe we can remove it now in this case at least if not others or maybe not or other or etc but anwyays etc anyways etc anyways etc...

## 20 - Negative and inconsistent DLL ajusted nowarattitudeprobs for some leaders, like leader_alexander that/who anyways etc has nowarattitude prob furious of -2 lower than furious 0 and lower than cautious 14

Screenshots about this issue can be viewed in this [google drive folder link](https://drive.google.com/drive/folders/1zPIMTN97zhubyrHBzAVLjCb2-YAFmLqG?usp=sharing) anyways etc

Some leaders like Alexander (III the g(G? of just g but anyways etc...)reat but anyways etc...) for example have a value for noWarAttitudeProb Furious of -2 DLL ajusted, which is lower than furious and doesnt seem to make sense.

Alexander's XML is like this:

```xml
			<NoWarAttitudeProbs>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_CAUTIOUS</AttitudeType>
					<iNoWarProb>20</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_PLEASED</AttitudeType>
					<iNoWarProb>80</iNoWarProb>
				</NoWarAttitudeProb>
			</NoWarAttitudeProbs>
```

Since furious and annoyed are missing, they should fall back to defaults (i.e. LEADER_DEFAULTS 's value if i am not mistaken anyways etc) if i am not mistaken, which is as follows at least as of now anyways etc:

```xml
			<NoWarAttitudeProbs>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_FURIOUS</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_ANNOYED</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_CAUTIOUS</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_PLEASED</AttitudeType>
					<iNoWarProb>0</iNoWarProb>
				</NoWarAttitudeProb>
				<NoWarAttitudeProb>
					<AttitudeType>ATTITUDE_FRIENDLY</AttitudeType>
					<iNoWarProb>100</iNoWarProb>
				</NoWarAttitudeProb>
			</NoWarAttitudeProbs>
```

Based on this, since furious and annoyed is an identical value in leader_defaults anyways etc, why isn't it ideally both 0 (for furious and annoyed) in alexander for example, or alternatively both -2 (less ideal i think but i dont know, as attitude should floor at 0 ideally if i may say and if i am not mistaken in my understanding anyways etc), but at least not inconsistently be lower at annoyed (here -2) than at furious (here 0).

Not sure i would fix it (i would have to dig how first) nor how it would influence game, but if want to look again at this issue it is here.

I don't know what the influence of the negative sign is, as otherwise 2 vs 0 should be quite minimal, but not sure is jsut my opinion/feel/thought which i don't know about much in this case, but the negative sign difference is more annoying, and ideally there would be a nice gradation i mean gradually increasing in english if i may say but anyways etc anyways etc anyways etc, hopefully helpful to have compiled this data as i wanted in the way i wanted even though bit tedious xd to be fair i mean anwyyas etc not gonna lie, but is quite cool to have compiled it too now is my feel if i may say for me, but anyways etc.

## 21 - (Now fixed) missing "Cannot enter" terrain or/and feature info in map view of unit effects, unlike in sevopedia (where it is also not clear enough about restrictions (cultural borders + not affected by roads if i am not mistaken anyways etc, now added this info as well anyways etc))

Screenshots about this issue are in this [google drive folder link](https://drive.google.com/drive/folders/1Felp-YagsHPYY3wtVqbV4eSRpwYl6BSb?usp=sharing) anyways etc.

Now solved. As part of adding terrain or/and feature restrictions to some units like chariot units and some siege units anyways etc (catapults and trebuchets i.e. early siege units as of now only at least anyways etc), i noticed the info is not displayed clearly in sevopedia unit's place Special (it doesn't mention this effect applies only in cultural borders, and that for all tiles regardless of whether tile is roaded or not, has no impact on the effect (i.e. roaded or unroaded in cultural borders is walkable but unroaded or roaded outside of cultural borders is not walkable regardless of road status if i may say anyways etc, and unlike in some games like civ3 where adding a road fixed or unlocked the limitation anyways etc))

For the sevopedia unit part, it was modifying the XML as usual if i may say anyways etc.

But for the ingame part, it is first time i modify successfully (and even tried actually anyways etc) the unit effects bullet points, now to also display this info, even though it is on a shorter display, we successfully loop through these terrain(s) or/and feature(s) and display them as such (only tested for features, but i assume would work-function similarly for terrains for example for workboat's ocean terrain restriction if i am not mistaken anyways etc)

It was thanks to chatgpt's help as well and my prompts and digging too anyways etc, even though it struggled at times if i may say and annoyed me bit i mean, i was quite used or expected it if i may say and together we solved it but anyways etc (may have been harder if i was not prepared for such but anyways etc anyways etc anyways etc most likely but anyways etc anyways etc anyways etc...)

First to solve this i followed the trail of the txt key in sevopedia unit, then found it is only once and not twice, and missing in map view. So i tracked instead a txt key already in the map view unit effects bullet points, and i found the scout's (that we added quite recently or not recently but as part of advciv-sas's changes anyways etc being able to walk on impassable terrain anyways etc (and explorers too i assume if i am not mistaken in this assumption too or memory from reading or something that it applies or would apply to explore units in general land ones but anyways etc in advciv-sas i mean anyways etc)), and there i added the method.

But we needed also to modify not only (adjust to your mod path anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvGameTextMgr.cpp but also (same anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvUnit.h too as advised by/with anyways etc chatgpt.

And after a bit of back and forth, we were now first finally anyways etc able to display the text only, a shorter version of it.

Then i wanted to add terrain/feature list information, but tweaking the code based on other samples caused errors at first, so after more samples i mean after i sent more samples to it it provided (to?) me but anyways etc a working code that i cleanly compiled (no fastdep as it may cause errors see this doc ctrl+f "fastdep" or similar or "compile" for details anyways etc hopefully helpful but anyways etc anyways etc)

Since we had the list but buggy, chatgpt was right in its guess that we only needed to tweak the logic, now works and functional, also more informative.

See screenshots linked in this drive for details as well, thanks anyways etc thanks, anyways etc.

## 22 - (Now fixed) Obsolete bonuses (such as BONUS_ELEPHANTS anyways etc) in tech advisor (i.e. tech tree view anyways etc) failing to redirect to sevopedia bonus with id none causing an error, unlike obsolete buildings (like BUILDING_SPIRAL_MINARET for example anyways etc) successfully showing the building item's page anyways etc

See screenshots of this issue in this [google drive folder link](https://drive.google.com/drive/folders/127ReqMyucJZ2gH88ARhgTWwuh6jl4oCs?usp=sharing)

An issue i have noticed during the buildings modifiers rework/rebalancing for wonders mostly, still unfinished as of now but anyways etc, but the issue anyways etc i have noticed is that obsolete bonuses in tech tree view (tech advisor it is called it seems in civ4 if i am not mistaken anyways etc) have an error when clicking on them at the sevopedia bonus redirect (see screenshots for example of error), but clicking on obsolete buildings in tech tree view does not cause an error at all and successfulyl redirects to selected/clicked on building from tech tree view, now in the sevopedia building page anyways etc.

After asking chatgpt and claude ai, i have done some quite extensive or bit maybe rather or lot or both or other anyways etc.. debugging, and have found the issue is we don't pass the correct iItem in pediaJump (in sevopedia main if i am not mistaken anyways etc) for obsolete bonuses, but obsolete buildings have the correct iItem.

This would mean the issue is before, at the pedia jump caller's level if not before.

I have also noticed we have the real id if i am not mistaken in CvTechChooser.py (see screenshots with the debug lines in code comments for example 25 for (obsolete selected) BONUS_ELEPHANTS if i am not mistaken anyways etc), but i don't know how to solve it further, and claude ai and chatgpt seemingly can't find the issue or fix easily as well with these code samples it seems, even though they helped me lot or quite a bit and i didn't show it in screenshots as bit tedious but anyways etc.

Still, adding a fallback iItem (for example of 1 anyways etc) if iItem is -1 seems to workaround it, we get to wrong bonus (like BONUS_COAL in this example anyways etc) but at least no error anymore, also it doesn't seem to break anything, nor to break obsolete buildings in particular that seem to still function as intended or as they did before, so although/while anyways etc it remains yet to solve the obsolete bonus issue, it is perhaps more playable now anyways etc, hopefully helpful or not or yes or and other or and not or yes or etc anyways etc anyways etc anyways etc

update: now fixed: the issue/bug/error anyways etc was seemingly caused by a new base advciv code in CvDLLWidgetData.cpp, now reverted to using `iData1` same as obsolete buildings did (and which didn't have the issue again but anyways etc) and not `widgetDataStruct.m_iData2` at the line after line `case WIDGET_HELP_OBSOLETE_BONUS:` (repetition of me but anyways etc...), which fixed it now if i am not mistaken anyways etc, see also screenshots for details in the google drive anyways etc. So removed previous workaround of using a fallback as well as debug lines as they are not needed anymore now that issue is identified and solved if i am not mistaken anyways etc hopefully helpful or not or yes or etc but anyways etc.

## 23 - (not fixed) Barbarian city being stuck looping producing a barbarian workboat without producing a new unit at each loop plus the barbarian workboat almost always vanishes one or a few turns after its completing, for few dozen turns several times in same autoplay

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1VGGAJZuCwwSdp86PWd-bFFprW7AOdtCK?usp=sharing)

While testing an autoplay before comitting latest changes, i have noticed a barbarian city in a lone island gets stuck producing a 1 hammer barbarian workboat. I have given save files at turn 0, 50, and 100 if one wants to try to reproduce it in this case i mean but anyways etc.

It seems that the issue was resolved after say 30 turns, but then after a unit or such hte barbarian city tried to produce another barbarian workboat and got stuck again for a dozen if not more turns until and including when autoplay ended.

This is not efficient nor ideal, i don't know what the cause is, if it's because the barbarian city is on a lone island, or if it is because the 1 hammer cost of the barbarian workboat somehow creates a bug with overflow, or/and if the issue is something else, but so far AI performs well both barbarians and AI players and i would like to keep improving their efficiency ideally as long as i develop this advciv-sas mod at least if not playing it too or such but anyways etc.

Added the files, screenshots and save files there, in case it helps and to revisit them late rif need(ed?) i mean but anyways etc in this case but anyways etc.

In another autoplay after this one (save file not appended here i.e. not in the drive link of this issue number anyways etc if i may say anyways etc) the issue seems to have happened again in a barbarian city, but lasted luch shorter in this case i mean anyways etc anyways etc, only a few turns, so maybe the issue is not critical if resolves by itself still is reproductible in this case if i may say anyways etc, ideally would be solved, added data if helps but anyways etc anyways etc anyways etc. It is also possible that these are rare instances, as it seems to have happened so far only on costal/naval cities so far from little autoplay i paid attention to focusing/noticing this problem/issue i mean anyways etc, so may not be critical again i mean or may be, but ideally would be nice if solved, but i don't know how to so so i hope this data helps, leaving as is for now anyways etc, hopefully helpful or not or yes or other or and etc anyways etc anyways etc anyways etc.

update: having tried again later this save file 173 turn number 50, the issue is consistently reproductible, and i have increased the hammer cost to higher values like 5 and 20 to see if it was the issue but the issue persists exactly almost the same, just instead of being stuck on always 1 turn until production for many turns, it is now apparent the issue is rather with looping, as say for a 20 hammer worker the countdown reduces fine at each turn at the hammer cost is getting completed, but issue is that often no new unit is produced at end of the cycle when hammer cost is completed, instead it seems like a new loop starts over at 0 hammer.

I have also found issue is not whales or some other water bonus as another east barbarian city in same save file has no problem having upgraded bonuses in these cities, but the difference is this city has a harbor (reworked in xml in advciv-sas, not like the base advciv's harbord, it is now in our mod the first water building anyways etc) unlike the city with the bug i mean anyways etc. But after making the change of now workboats requiring a harbor (see xml for details and reasoning why anyways etc) (and a barbarian_harbor specifically anyways etc for barbarian player's barbarian_workboat if i am not mistaken anyways etc), the issue remains the same, so issue is not that the eastern barbarian city that could improve the water bonsues successfully had a harbor either unlike western barbarian city with the bug. So i do not know exactly what is happening, eastern city is also on a lone island but this doesn't seem to be the cause as it successfully improves its water bonuses unlike western city, but i have noticed eastern city is also stuck producing workboats as well. In the end, i still don't know the cause nor how to fix it, but this helped balance the workboats that may be op in some early starts with a lot of land food plus water food. I have added screenshots of these new results if i may say anyways etc.

## 24 - (Attemptingly fixed) AI Workers often build forts on ressources/bonuses, even if they already have an existing improvement (very inefficient and not immersive)

Note: as of now the changes in the DLL described below in this section can be found in this [advciv-sas commit](https://github.com/wonderingabout/AdvCiv-SAS/commit/6d82d51fe1e3a3262d7c69af67daaacb927175e4) among a few other unrelated changes but or not but or yes but but anyways etc hopefuly helpful or not or yes or etc but anyways etc

This is an issue i had more extensively documented in the known issues about advciv civfanatics thread (see link somewhere in [README.md#me-wonderingabout](/README.md#me-wonderingabout)), that AIs often build forts on top of existing improvements.

This should be very inefficient in most cases as forts, if i am not mistaken but anyways etc... :

- take a long time to build (waste of worker time but anyways etc)
- yield less than improvements
- it is unlikely a human or other player would ideally attack units garrisoned there as it is not advantageous to do so but anyways etc
- it is especially inefficient where/when an improvement is already built that connects the ressource/bonus yet the AI undoes that extremely inefficiently for lower yields and other such disadvantages discussed before or not but anyways etc
- it is also cheaper / more efficient i think at least if i may say in this case at least but anyways etc anyways etc to let the ennemy destroy/pillage an improvement and rebuild it later than to carry fort very low yields on each improved ressource/bonus all the game

There are some other disadvantages such as:

- not immersive to see the AI play so inefficiently, at least to me, but anyways etc

However it could potentially be useful in some cases:

- allow naval units to pass/cross this land tile even if a ressource is on it
- prebuild the connection to a ressource/bonus, but generally the improvement would be available at same time if not before the ressource/bonus becomes visible, unless talking a blind preconnection attempt but way too inefficient
- possibly some other +/- more minor advantages but anyways etc

Overall i feel/think it would be better for the AI to not bother with forts at all, so i tried/am trying to add more restrictions or and cases where the AI would simply, to simplify if i may say but anyways etc the logic, skip entirely forts, which should in most cases help the AI.

So although i don't know too much how to do this, but can manage a bit maybe but anyways etc, i made such changes in the DLL with chatgpt's help, as of now untested (see quick start guide for updated status if any there or and cpp files but ideally quick start guide if there as well) but anyways etc

## 25 - Attempt to fix AIs settling too much and too often on bonuses, especially food bonuses (!!!) and metals and other high production bonuses to a lesser extent

As of now if not all related changes can be found mostly if not almost entirely but anyways etc in this [advciv-sas commit](https://github.com/wonderingabout/AdvCiv-SAS/commit/95347a520d7fbe41465c324ad609bddba32a167d) and this [advciv-sas commit](https://github.com/wonderingabout/AdvCiv-SAS/commit/c20688b2c267ecee883a41168442ffdb22d32fc5) anyways etc. See the .cpp or/and other code updates directly in the code if any updates since then have been made or not, hopefully helpful or not or yes or etc but anyways etc, thanks,

### Origin and description of the problem anyways etc

This is also one of the issues i had noticed in base advciv and that still happens in advciv-sas as of now, so trying to fix it. I had asked about it in the past f1rpo who kindly made/added/pushed but anyways etc this [base advciv commit](https://github.com/f1rpo/AdvCiv/commit/1a372d417a6001e2afe2b40e69824b45fa375907) as a partial patch/fix to it

But while it seemingly may have improved it a bit, AI still settles on metals, and although that may be fine, perhaps even desirable in some cases maybe (metal on hills in particular maybe but anyways etc), AI still often plant their cities on food bonuses which is very very inefficient. As i don't know too much about these but am very eager to improve these ideally if i may say but anyways etc... I asked chatgpt and trying to fix/tweak quite cautiously this logic, quite similarly than in [README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive)

### For bonuses with a food yield

Here using to simplify the logic and also more drastically as food bonuses should be especially important to not settle on unless strong exceptions that we ignore in advciv-sas at least as of now (i can't think of any such exception immediately, maybe rice on plains if such a thing even exists, but still wouldn't hurt to as a general rule even in such a case not settle on the bonus, should more often than not help the AI if i am not mistaken in thinking so but anyways etc), so give a quite strong relatively if i am not mistaken but anyways etc penalty to discourage the AI from settling there at all anyways etc.

### For quite high total production bonuses

The current code now should make AIs more likely (apply a valorization on this plot value to found if i am not mistaken but anyways etc to make the AI think settling/planting on this plot/tile is high(er) but anyways etc value / good/better choice if i am not mistaken but anyways etc) to settle/found city but anyways etc on a plot/tile that has a bonus/ressource with a quite high total production total yield (i.e. with improved yield too if i am not mistaken but anyways etc) on it, if this plot/tile if i am not mistaken but anyways etc:

- in all cases and to a lesser extent than below, has the desert terrain (low food so should be fine perhaps even profitable but anyways etc)
- is on a hill, exception being if it is a hills grassland then not (see at the less likely bullet points list below but anyways etc)

The current code should also make AIs less likely (apply a penalty on this plot value to found if i am not mistaken but anyways etc to make the AI think settling/planting on this plot/tile is lower(er) but anyways etc value / bad/worse choice if i am not mistaken but anyways etc) to settle on a plot if it is:

- on hills grassland, discourage the AI to plant there as production is lower, may not get the extra hammer or may want to improve it rather for only 1 food cost but anyways etc
- if as said before not on hills at all nor on desert, discourage the AI to plant there as well

Overall and as of now, if still updated, here is how it works as kidnly provided by chatgpt thanks without me askign xd thanks chatgpt if i may say maybe me too thanks to me too i mean in this case but anyways etc, which (the table in this case but anyways etc anyways etc anyways etc...) formatted and with some corrections or modifications i added as well but anyways etc:

| Case                                                | Handled? | What Happens                                                  |
| --------------------------------------------------- | -------- | ------------------------------------------------------------- |
| Hill & not Grass                                    | Yes      | Valorized (encouraged to settle)                              |
| Non-Hill                                            | Yes      | General penalty (discouraged to settle)                       |
| Any Grass (including Hill Grass)                    | Yes      | Always gets additional penalty (high food tile)               |
| Low Food terrain (Desert or Snow) & low food bonus  | Yes      | Mild additional valorization if bonus also has low food yield |

### For bonuses with a high total commerce yield

In these cases again (for example as of now the gold bonus, etc (see xml for details anyways etc)), apply a quite strong penalty for bonuses that have a high enough total yield (i.e. with improved yield too if i am not mistaken but anyways etc) such as of now the gold bonus, sivler bonus, incense if i am not mistaken as well, etc. The higher the total yield is, the stronger the penalty is to discourage planting/founding a city there if i am not mistaken but anyways etc.

### About water bonuses/ressources in range but ignored by AI settling instead a non-coastal location

Attempt to fix/address this as well by making the penalty in that case much stronger, as of now increased from -165 to -400 (seems to have been -800 in k-mod if i am not mistaken but anyways etc, see [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details or/and updated value anyways etc), hopefully helps the AI consider more often water ressources or at least not ignore them when they are in range of their city sites considerations if i may say in this case at least maybe but anyways etc anyways etc anyways etc

### About the estimation of the improved yields depending on bonus types

Independently from this, the current code now should also if i am not mistaken but anyways etc also make the AI overestimate purposely the value of improved yields from bonuses with a quite high if not also high but anyways etc food yield in particular, and bonuses with a quite high if not also high but anyways etc production yield to a lesser extent but quite a bit but anyways etc, so that AI doesn't settle/found city on them ideally, but instead around them and then improves them expecting a high yield (instead of planting their city there then can't improve a city tile but anyways etc).

As of now untested or if tested not too much tested (i can run a bit of autoplay but would need extended use to see a difference maybe but anyways etc), but hopefully this improves (and doesn't deprove? Or degrade? Or reduce? But anyways etc...) the existing logic, but anyways etc...

### Results

I only tested it a bit (a few autoplay glances at turn 100), but the results seem extremely good and really much better, may test more to be sure or/and ask player feedback after mod release or and such if we do release it as planned/intended in this case but anwyays etc, so i would say to take this with a bit of caution maybe, but overall if i may say but anyways etc it does seems AIs almost always if not always maximize planting/settling their cities around found bonuses in the radius and not planting on them, cannot tell too much or if this is just small sample but it does seem to make a big difference but anyways etc anyways etc anyways etc.

## 26 - fix/enhance told AI which terrains and features environments are best to settle near. As for local tile to settle on optimization : won't fix for now at least anyways etc)

update 2: told AI which terrains and features environments are best to settle near. Note that as of now however, won't fix local best tile (e.g. on desert rather than on flood plains) to settle on due to this AI behaviour: AI settling on grass instead of locally say desert or snow tile for optimization. I implemented a code that AI do exactly that, but this also resulted in AI going for tundra environment just not to settle on a grass tile, i'd prefer it to settle on a grass tile if surrounded by more grass tiles, rather than going to a tundra environement to optimize not wasting the grass tile. It would be ideal if AI both went for the nicest environment, and then also looked at best plot in said environment ; but until and if i do that (not guaranteed, i have an idea how but not sure is worth wasting best site just for slightly although significantly forgot sentence but anyways etc, what i mean is we could for example (an idea i got didn't check if relevant or not or if other pieces of code already do that except or out of those we added that do that for other parts of the code (storing candidate plots as of now in a struct for tiles to improve in cvunitai but anyways etc) or maybe check where ai found value function is called and tweak there is needed but anyways etc, but for now giving ai best chances by telling it which tiles are good, for non-bonus tiles ; as for bonus tiles as of now still using this system to discourage AI settling on them often (settle on sheep grass is very bad unless locally otherwise extremely good if i am not mistaken but anyways etc) or missing them (having fish in range and not going for coastal location that includes it if i am not mistaken but anyways etc, which seems to work-fucntion better with our change that reverts it stronger and closer to kmod code if i am not mistaken but anyways etc)))

Similarly to [README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#25---attempt-to-fix-ais-settling-too-much-and-too-often-on-bonuses-especially-food-bonuses--and-metals-and-other-high-production-bonuses-to-a-lesser-extent) and [README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses-even-if-they-already-have-an-existing-improvement-very-inefficient-and-not-immersive](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#25---attempt-to-fix-ais-settling-too-much-and-too-often-on-bonuses-especially-food-bonuses--and-metals-and-other-high-production-bonuses-to-a-lesser-extent), also add logic in the DLL for non-bonus/ressource tiles, with chatgpt's help and my prompts and thoughts too but anyways etc anyways etc anyways etc, to help the AI better choose tiles to settle/plant/found city on, prioritizing low-food tiles rather as a general rule (especially hill due to the defense bonus that it has additionally but anyways etc), with some exceptions (such as hill grassland as of now but anyways etc)

Logic as of now summarized as such by chatgpt (i just renamed its "bonus" word to "value" and edited a quite a bit its table but anyways etc)

note: values may be updated, please view code at [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details or/and updated value, hopefully this general logic helps and/or is not too not updated anymore but anyways etc

| Terrain Type | Base Value   | Flood Plains | Hill Value | Total if Hill      | Notes                                                                    |
| ------------ | ------------ | ------------ | ---------- | ------------------ | ------------------------------------------------------------------------ |
| **Grass**    | −25          | N/A          | **0**      | −25                | High food so penalize/discourage; explicitly excluded from hill value    |
| **Plains**   | +25          | N/A          | +50        | **+75**            | Low food but not too low yields so valorize moderately, valorize if hill |
| **Desert**   | +45 or 0(**) | −50(*)       | +50        | **+95** or −50(**) | Flat desert highly valued; floodplains *cancel* valorization change      |
| **Snow**     | +45          | N/A          | +50        | **+95**            | Also encouraged overwrite; very low food so valuable, even more if hill  |
| **Tundra**   | +30          | N/A          | +50        | **+75**            | Low food but also quite low yields so valorize, valorize more if hill    |

(*1) note from a cpp code comment anyways etc: "may not cover the case of for example mod mods having flood plains on other terrains than desert, but it is computationally more efficient to do so i.e. to check i mean but anyways etc in this case but anyways etc the flood plains feature only in its relevant/comaptible in XML terrain(s), which in advciv-sas and as of now only are desert. I don't know how many times we run this instruction, but if it's quite a lot, even saving one instruction may be nice if i may say, remember to modify this if you modify in your mod mod or such the flood plains compatible terrains or/and such but anyways etc"

(**) note 2 from a cpp code comment anyways etc: "as of now flood plains or and other potentially/hypothetically quite high or high food feature cannot exist on hill, so no need to spend computation on them, but ideally in a mod mod if you'd want to account for such, you'd add them (i.e. the flood plains feature for example if it could fit in a hill for example but anyways etc) here to the hill bonus exclusion (as it is a high food tile, better not plant/settle/found city on it and waste it if i may say but anyways etc) then penalize for example the flood plains feature below separately from the terrain "cascade" (as chatgpt calls it but anwyays etc thanks anyways etc) in its own feature cascade rather (if i amy say too if i may say but anyways etc...) so that the feature valorization change (penalty or increase of valorization but anyways etc) also applies to all terrains, not only just to desert, anyways etc. In short, flood plains on hills don't exist if i am not mistaken in base advciv +/- civ nor in advciv-sas, but it is easier and computationally to handle it as such, update your code as you see fit if your mod mod or such supports this so that flood plains on hills are also accurately penalized to discourage AI planting/settling/founding cities there as hills grassland currently is, if you want i mean, hopefully helpful or not or yes or other or etc but anyways etc anyways etc anyways etc."

This table means that for example settling/planting/founding city but anyways etc on a hills desert tile is strongly encouraged, hill with plains quite very if i may say but anyways etc strongly encouraged too, flatland (no hill, no peak) desert still quite significantly too if i may say but slightly less than the hill modifier itself so that if everything else is being the same (as of now we don't have other terrains that would go on a hill plot type if i am not mistaken but anyways etc, but maybe the distinction helps somehow, but anyways etc) so that hill is still slightly preferred in that case (again i don't think as of now we have such terrain where it would apply, but theoretically maybe with some terrain changes, since logic doesn't harm, keep it as is anyways etc).

As for discouraging, hill is irrelevant if the tile is grassland (as hill grassland for 1 food cost has nice yields i think, capitalize on that rather and do not settle there ideally if i am not mistaken should be better in most cases for the AI, at least give a discouragement against that if i may say but anyways etc anyways etc anyways etc), and high food terrains should be avoided to settle/found/plant a city on (not totally discouraged, but should be significant and hopefully help AI not doing so and better choose city spots as it helps a lot throughout the game but anyways etc)

Hopefully this helps the AI better plant/settle/found cities and is not too drastic in having unexpected results, but anyways etc

Results so far seem to be that it does seem to help quite a lot from the few autoplay i ran, but perhaps numbers could be increased a bit, just, i wouldn't want it to compete with the bonus/malus system or overlap of bonus on tiles, or too high values may have some unexpected values who knows in city settling or such other or not civ4 ingame behaviours if i may say maybe but anyways etc.

I am not sure it always improves AI settling behaviour ; there may be some cases where locally AI makes worse settling choices due to these changes, but in most cases, at least in theory if i am not mistaken, and although i don't know too much about these, generally/maybe it should improve AI settling choices even if a bit if not more than a bit but anyways etc maybe but anyways etc, but test to be sure, anyways etc.

Still overall should be an improvement, ideally try it a bit more in this case but anyways etc, but is maybe fine or not too bad as is, again i only ran a few autoplay and don't know too much aobut these, but with chatgpt's help and my thoughts too, it does seem like an improvement, even if a bit, if not a bit lot in this case but anyways etc, hopefully helpful or not or yes or etc, but anyways etc.

## 27 - (now fixed) Some promotions are missing in sevopedia unit's placePromotions

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1hRe5rR9DPBH6XzwllwTLSnh9kbIQwkEG?usp=sharing)

Some promotions were missing in sevopedia unit's placePromotions, for example for the generic swordsman or the zulu impi (melee units combat type if i am not mistaken but anyways etc), they didn't show collateral damage 1 and collateral damage 2 (as of now renamed from base advciv +/- civ4's barrage promotions if i am not mistaken but anyways etc).

So thanks to chatgpt's help, i found the cause althoguh i suspected it too intuitively hehe, but chatgpt told me the issue thnaks to my prompt too but thanks to itself too but anyways etc and provided me and int his code if i may say but anyways etc a working alternative condition of as of now `gc.getPromotionInfo(k).getUnitCombat(eUnitCombat)` (note: `eUnitCombat = gc.getUnitInfo(self.iUnit).getUnitCombatType()`) instead of `isPromotionValid(k, self.iUnit, False)` that was too strict, but just disabling this old too strict condition if i may say but anyways etc showed too many promotions even the ones these units shouldn't have access to such as of now collateral damage 3 and 4 for example anyways etc.

This seems to fix the issue (see screenshots for details, as we specifically now see the missing promotions on top of same old ones if i am not mistaken (didn't check in detail but there seem to be more than before and also to have relevant ones, check screenshots or/and xml for details or comparison or and such but anyways etc)), hopefully helpful or not or yes or etc but anyways etc

## 28 - (now fixed) Wallpaper of our mod's custom being stretched vertically while some of the top of the wallpaper is not shown at all, at 1920 x 1080 game resolution

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1-j9EHLeY7FzJ0iHZqBXIAOyOPfzJVC0t?usp=sharing)..

When adding our mod's custom wallpaper instead of default base advciv +/- civ4 one, one issue i encountered is that our image was stretched vertically, while some of the top of the image was entirely missing.

Note: i have used ri mod's very useful civ4mainmenubg.nif in particular since they use static images like for their wallpaper in main menu at least but anyways etc, see [README.md#using-creator-nightcafe-studio-and-then-pixelcut-ai-to-expand-it-to-1920-x-1080-with-new-details](/README.md#using-creator-nightcafe-studio-and-then-pixelcut-ai-to-expand-it-to-1920-x-1080-with-new-details) for details.

Note 2: in this example i am using a 1920 x 1080 image and game settings at 1920 x 1080 too if i am not mistaken. I assume a smaller or wider in this case but anyways etc image would be shrinked or stretched fine to fit the full screen, but when it comes to some portions of the image being ignored, it has nothing to do with the resolution itself (i.e 1024 x 1024 or 4096 x 2000 would be the same, but difference is aspect ratio (e.g. 16:9 vs 4:3 or such anyways etc)), so i hope these instructions or/and feedback help use the optimal ratio i have found that works-functions well with civ4 engine or so it seems at least with this nif, hopefully helpful anyways etc.

Note 3: i recommend you save a copy of your original image file before trying any of these steps.

So to solve this, through trial and error, i have found that creating fake pixels at the top and also at the bottom of the image seems to the trick well.

Instead of explaining tediously how i found it which may make the explanation very complicated to follow, although i wouldn't mind to, here are the simple steps on how to modify you screenshot so that no part of the image is lost / not displayed ingame (or extremyl close(r) to it if i may say but anyways etc.

I'd also highly recommend again to see the screenshots in the google drive link of this known issue for intermediate steps illustration.

So using Paint.NET for example in this explanation and as it is what i use too if i may say but anyways etc:

1- First (i am using Paint.NET for example here anyways etc) increase canvas size (not crop, not stretch, but canvas size, so that image stays the same, and new pixels appear additionally) and enable the option to not maintain aspect ratio (which actually maintains image ratio, just it also adds other new empty pixels in the image, so Paint.NET thinks image ratio as in full image ratio including the fake pixels has now changed and is no longer say 1920 x 1080 = 16:9 but something else 1920 x 1500 (fake example) is 1920 / 1500 = 1,28 (fake example just to illustrate), which is fine and as intended since the fake pixels won't be displayed in civ4 anyway).

I have tried several sizes if i may say but anyways etc (see screenshots for examples of how it looks ingame), and i have found that through trial and error of various values, image seems to display best with a total (top + bottom) fake empty pixels height of 1440 - 1080 = 360.

Spread these fake pixels evenly between top and bottom, so you have 360 / 2 = 180 fake empty pixels to add on top, and the same number at the bottom as well if i may say in this case at least but anyways etc anyways etc anyways etc...

So back to the resize canvas, choose 1920 x (1080 + 180) = 1920 x 1260 if i am not mistaken anyways etc (and again untick/disable the maintain aspect ratio option).

Then, move your image (the drawing/real image you want to see) to the bottom of the Paint.NET image, so the fake empty pixels that were on the bottom would now be on top (to do that ctrl+a then ctrl+x then ctrl+v then use bottom keyboard arrow, and when close to end/bottom edge, zoom a lot to align it perfectly if i may say but anyways etc).

2- After that, we need to add the bottom fake pixels. To do that, redo again the resize canvas, but this time choose a resolution of 1920 x (1260 + 180) = 1920 x 1440, and also here as well untick/disable the maintain aspect ratio of Paint.NET resize canvas feature if i may say but anyways etc. Then finally save as .dds. If you are satisfied with the ingame result, i'd recommend restarting from your original image (in case you tinkered a bit with the values as i did, else may not be necessary) and do the same steps of this entire section (keep a backup of oyur original image as well in case or if needed but anyways etc), but save after all steps directly as .dds from your original image (say .jp to .dds directly), i am not sure, but maybe quality would be higher than compressing and recompressing a .dds voer and over whiel doing trial and error as i did. Again may or not change anything, but as a theoretical and to be safe if i may say in this case at least and to have best potential rendering in case it helps (again not sure but maybe it does or not but anyways etc), i'd recommend doing it cleanly again after you have found your dimensions that suit your image from your native image directly to .dds but anyways etc (in my case for example i use Paint.NET DXT1 with mipmaps (mimaps seems to have been recommended in some civfanatics forums or/and by chatgpt too xd if i remember it correctly but anyways etc when i (had? But anyways etc...) started developping this mod a few months ago xd if i may say but anywyas etc...) which seems to work-function fine (i don't know if it's best, but it seems to work well here or not too bad so maybe fine to do so but check to be sure in case there is better info or such but anyways etc))

Note: at some values for some reason the screen may appear entirely white, i don't know why exactly if at all, but i have noticed slightly increasing the value or decreasing it solves it, so if say 1920 x 1440 causes an issues (imaginary but for example), try 1920 x 1442 or 1920 x 1438 etc and adjust based on your display or increase / decrease a bit more if still white screen but anyways etc, solved it for me when some values such as 1238,1232, 1250 didn't work-function i.e. also had the white screen weird issue but for example 1240 or 1236 worked-functionned fine if i am not mistaken and remember it correctly anyways etc. I have again no idea why, just use a slightly higher or lower value like in my case 1236 while i was doing trial and error displays fine if i am not mistaken, anyways etc.

Put the output .dds file where civ4mainmenubg.nif is (in our case as of now in [/Assets/Art/AdvCiv_SAS/Main_Menu/wallpaper/](/Assets/Art/AdvCiv_SAS/Main_Menu/wallpaper/)), as defined in `MAINMENU_SCENE_CLASSICAL` (main menu background) (and `MAINMENU_LOAD_CLASSICAL` (loading screen (e.g. loading a save file, loading a new map, etc.) background) in our case too in our mod but anyways etc) in [/Assets/XML/Art/CIV4ArtDefines_Interface.xml](/Assets/XML/Art/CIV4ArtDefines_Interface.xml).

The result is the image appears no longer stretched at the top nor at the bottom part of the image vertically ingame, or if ever still, it should be extremely minimal.

Note 4: i have noticed also we could create fake pixels on the sides too, although much less, as it seems approximately 1 or 2% (gross estimation) of our image is missing on the left and right side, but bit tedious, so for now i fixed the biggest issue if i may say, but ideally one may also try to add fake pixels (say 6-10 pixels on each side to try to see if a larger portion of the as of now 1920 x 1440 image is visible, so it would maybe be say 1926 x 1440 or 1930 x 1440 or more or less around although i didn't try it so this is just speculation on my end, but a tiny portion of the side of the image is not visible, maybe this would help as well or maybe not, ideally i'd try it someday too but not guaranteed may or may not do so, hopefully helpful or not or yes or etc anyways etc...)

Again, screenshots of intermediate steps are also shown in the google drive link in this known issue number's section as well, hopefully helpful or not or yes or etc anyways etc anyways etc anyways etc...

## 29 - (as of now with a workaround) clicking on a specific spot in tech advisor at tech transhumanism's blue box causes a crash

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1-bhTzZeKZg8z_n0hcDJtAY8DnFfuuftg?usp=sharing).

I don't know what the cause is, but clicking, in tech advisor (i.e. tech tree view if i am not mistaken anyways etc), on as of now tech_transhumanism's box (the blue rectalnge) specific position, we consistently get a crash and i have no idea why.

I don't know if me playing in windowed as of now due to it being so much easier for developping/debugging and or such but anyways etc (didn't test full screen but anyways etc).

Err logs and Dbg log don't seem to indicate anything related to this, so make sure you make enough saves regularly before browsing too much on tech advisor at least anyways etc.

As of now, i have found a reliable/consistent workaround anyways etc, which is to click on the tech name itself, then the crash is avoided and we are successfulyl redirected to sevopedia tech anyways etc

update: i have found the issue, and could reproduce it in particular with tech_agriculture, by adding an or prereq that is faulty or/and impossible to meet (i.e. xml asks tech_depopulation for example as of now here anyways etc to research tech_agriculture, even though tech_agriculture shouldn't require any tech as of now i mean anyways etc (and tech_depopulation also requires indirectly uch earlier tech_agriculture, so it is impossible to meet this tech prereq for tech_agriculture anyways etc, hence the crash when right clicking on the modified tech_agriculture's blue box as well anyways etc)).

So it appears that the do research or whatever related or similar to it fails and crashes silently (would be nice to have an error message, ideally no crash anyways etc). I added the lines below at tech_agriculture and it caused same crash:

```xml
			<OrPreReqs>
				<PrereqTech>TECH_DEPOPULATION</PrereqTech>
			</OrPreReqs>
```

So based on this, the crash is caused by impossible prereqs, but an actual error message such as impossible to process the doResearch command would be nicer, as well as ideally not crashing.

Ideally i would fix it, but is tedious, and most importantly, the issue shoudl disappear when we have proper tech preresq not the fake ones that are not functionnal and just taken from any tech i could find to replace with our new techs. So this is only a temporary issue, although less idela, it is probably most efficient to leave as it is. It is also maybe more reliable to have a silent crash rather than adding a complicated way to handle that may react unpredictably and not necessarily always handle correctly the cause or other causes. So seems safer and most efficient to leave it as it is, and just keep in mind if tech advisor crashes happen again, that issue may be faulty tech prereqs.

See also, although not directly related: [README_Known_Issues_In_Base_AdvCiv_Civ4.md#22---now-fixed-obsolete-bonuses-such-as-bonus_elephants-anyways-etc-in-tech-advisor-ie-tech-tree-view-anyways-etc-failing-to-redirect-to-sevopedia-bonus-with-id-none-causing-an-error-unlike-obsolete-buildings-like-building_spiral_minaret-for-example-anyways-etc-successfully-showing-the-building-items-page-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#22---now-fixed-obsolete-bonuses-such-as-bonus_elephants-anyways-etc-in-tech-advisor-ie-tech-tree-view-anyways-etc-failing-to-redirect-to-sevopedia-bonus-with-id-none-causing-an-error-unlike-obsolete-buildings-like-building_spiral_minaret-for-example-anyways-etc-successfully-showing-the-building-items-page-anyways-etc)

## 30 - (Attemptingly fixed) AI workers not prioritizing bonuses to improve, especially food bonuses, and other AI workers optimizations or/and changes anyways etc

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1xeAY-R41d3jQ8W4JvK8mhdRBlkKINpQu?usp=sharing).

This is an issue i had in base advciv, and this solution may not necessarily in all cases be better, but i believe and hope in most cases it helps, at least for the part of the code changed. Rewrote/refactored `CvUnitAI::AI_bestCityBuild` with gemini ai's help for most thanks to its persistence in particular (see [/README.md#gemini-ai](/README.md#gemini-ai)) for details anyways etc.

I have written most details there, so only adding here as less tedious to do so anyways etc, but hopefully helpful or not or yes or etc but anyways etc a few or quite a few screenshots in the google drive link folder mentionned at the top of this known issue section (as of now number 30 anyways etc)

These changes hopefully fix this issue (see "Boston" screenshot in this google drive (as of now screenshot 1478 if i am not mistaken anyways etc)). Although i couldn't reproduce it directly since worker behaviour changed in more ways or it is autoplay variation somehow maybe (less likely but maybe?), starting from same save file 334 (also appended), Washington is quickly improved, firt with bonuses. In some cases, see screenshot 1499 if i am not mistaken anyways etc, other tiles seem to prevail, most likely due to other code parts, but it corrected soon enough and the silver was improved soona after which was the main purpose/goal of these changes (in base advciv i would have a bonus not improved for a few dozen turns if not more if i remember it correctly, which was very unimmersive), so hopefully AI is more efficient this way.

Ideally i would track other places where changes may be necessary, not sure i would do but maybe, or maybe not ; in this case i mean, anyways etc.

As part of this change, i tried to increase AI worker efficiency by having them max put one worker to a tile to improve: if a worker is improving it already, skip it and go to another tile instead (there may be some delay until a worker goes there and starts improving it i mean anyways etc resulting in some ineffiencies of traveling there while a worker is also already travelling there, perhaps closer or not but anyways etc, but it seems to correct better, as soon as the closest worker starts, the other workers bounces back fast to another tile if i may say anyways etc)

This is not always the best choice, but i believe generally AI would be more efficient this way.

As a side effect, this new code seems slightly faster (see gemini ai link for details).

I would want to do other changes ideally to AI worker and such logic, not sure i would but ideally ; and is in this case i mean if i may say, anyways etc.

update note: i have noticed that commenting out the `CvUnitAI::AI_improveBonus` function entirely in the inner body i mean in this case but anyways etc and returning always and only false, we'd fix farm spices issue, however we'd lose the roading bonuses ability we had ; i didn't see an easy way to selectively do this with AIs like chatgpt o-3, so kept as is and tolerating occasional suboptimal improvements for the sake of having many nice ones often (we now mostly handle improving bonuses ourselves in CvUnitAI::AI_bestCityBuild in a way that should be much more efficient anyways etc)

update 2: update: also disabled functionally `CvCityAI::AI_getImprovementValue` and `CvUnitAI::AI_irrigateTerritory` which solved the farm on spices plains issue when unwanted (not in our exceptions below) as well as inefficient and needless farms on floodplains or flatland grass or other unwanted interferences, see these functions (or whatever remains of them for details, as well as screenshots 1858 (no farm on spices plains and no farms on flood plains either since we're not starving) and 1863 (still no farm even at turn 150, now building plantation as intended and city looks very nice improved if i may say but anyways etc) for comparison ; also not shown but no farms on flatland grass anymore since we're not starving there as well if i'm not mistaken in my memories but anyways etc. We now have greater if not total control over our AI workers or close to it, and this improves ai efficiency further if i am not mistaken and is thanks to chatgpt and co or such like claude ai and such if i may say too (and thanks to me too if i may say but anyways etc) but anyways etc

## 31 - (Attemptingly fixed) Deprioritize routes for AI workers in favour of yields first, except in some rare cases

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1BpwAkJ6V4cT8zeN99UOds7wu0efB5PUe?usp=sharing)

Rewrite and greatly simplify `BuildTypes CvUnitAI::AI_betterPlotBuild(CvPlot const& kPlot, BuildTypes eBuild)`, so that we deprioritize routes for AI workers, and build them only in very rare cases, especially in the early game where yields are so important (now prioritize yields over move speed advantage, should help AI a lot in most cases hopefully at least i think so in this case anyways etc), and AI workers would often in base advciv waste time building roads first, sometimes even forgetting to improve the bonus in particular, or other tiles. I hope this makes AI sharper and more efficient, with a cleaner and much simpler best build override, thanks to gemini ai as well and thanks to me too if i may say in this case but anyways etc.

Areas of improvement not related to our code change:

- screenshot 1505: do not build cottage on plains, build on grassland rather, is a better tile to work, and improve any remaining bonus eligible to be improved before that

Hopefully i'd continue improving these ideally but may or may not do anyways etc

## 32 - (now seemingly fixed) Prioritize settling on coast when food environment is low (many tundra or/and plains or/and desert or/and snow (or/and peak although i assume is not counted but to be safe anyways etc)) (the "Corinth screenshot")

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1O-5WGOwvufgZS9z2DJ-wY2hlkTJLhP8I?usp=sharing).

It was an issue i had in base advciv, when AI is in a low environment, say many tundra tiles for example i mean anyways etc, it is likely city would starve soon, so settling on the coast if in reach is much more valuable.

I added a code that counts low terrain or feature tiles in city radius, and if a certain amount is reached (as of now >= 7 medium low (snow, desert (and shoudln't be counted but peak as well but to be safe if i may say but anyways etc))), then we consider this environment to be low-food, and get discouraged if our tile is not coastal. The food penalty is increasing with the among of low-food tiles pas this threshold. See how i implemented it if i may say but anyways etc in `AIFoundValue::evaluate()` in [/CvGameCoreDLL/CitySiteEvaluator.cpp](/CvGameCoreDLL/CitySiteEvaluator.cpp) for details anyways etc.

This means that what was a good spot is now not anymore a good spot, and AI will consider the next best tile instead similarly, which will not get penalized if it is coastal.

As can be seen in screenshots if i may say but anyways etc, with some previous changes i made, AI had a seemingly better understanding or/annd reaction but anyways etc to which bonuses are valuable and to settle near and not on, such as in screenshot 1475, here i assume to successfully grab the water bonuses thankfully thanks to our changes i assume that incentivize this more but anyways etc, however in screenshot 1476, these changes still did not compell AI to settle on coast and corinth in full tundra/snow is starved soon, which could have been avoided just by settling one tile south or somewhere near that for a much higher potential city relatively if i may say but anyways etc.

After these new changes i implemented in this known issue as of now 32 but anyways etc, we can see if i may say but anyways that for example, AI still values water bonuses for coastal planting (screenshot 1580), but now also successfully settles on the coast even if there is no water bonus in range, just to avoid the low-food environment early starving (screenshot 1585 in now city sparta). In particular, thanks to the changes and buffs we made to coastal planting, it may be a bit stronger to plant on coast than in base advciv, relatively, although land should sitll be quite betetr as of now at least if i may say but anyways etc.

Hopefully AI is stronger with these changes anyways etc.

update: increase the penalty a bit to solve some extra cases where some cities still didn't prefer coast, and which seems to indeed successfully solve it as well for these cities, see screenshots 1855 vs 1859 to 1862 for compare anyways etc

## 33 - Tremendously improved and fixed and enhanced AI worker build/improvement logic in CvUnitAI::AI_bestCityBuild

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1WQUG049I2F1nPMhTVrnTstgNYjVslg9i?usp=sharing).

As written in the quick start guide:

Complete overhaul of `CvUnitAI::AI_bestCityBuild` [/CvGameCoreDLL/CvUnitAI.cpp](/CvGameCoreDLL/CvUnitAI.cpp) : now AI workers follow a highly optimized build (improvements) routine and strategy, based on terrain, food, health, fast chopping, etc.

This is done by completely ignoring base advciv +/- civ4 algorithms or/and logic, and defining probabilistically with a value tree our own value system +/- of priority to build based on our own advciv-sas conditions if i may say but anyways etc. Some of the changes include for example favouring cottages on flood plains unless we are low on food then farm, or not overwriting.

Oscillation (i.e. AI workers constantly changing their minds and ovrwriting a mine with a windmill, then a few turns later rewrite the windmill with a mine, etc) should be much much less frequent and cleanly managed, with a set of "holy" improvements never to overwrite (hamlet, village, town, workshop, etc), a penalty for overwriting improvements so AI improves other improvements first, a wait later system to keep best tiles for later if we don't have an immediate good move for them and methodically improving next eligible best, as well as a system to tell the AI which are best and bonus-specific improvements, to fix the banana cottage issue, it will do a plantation or nothing, unless the food gain is high (grassland irrigated for example) then it may do a farm very methodically else leave for later to increase AI worker efficiency.

Also, these changes fix and remove AI opening on a cottage plain, it will look for flood plains first, then grassland, etc. Logic is fine tuned on hills.

There are many related changes as well, please view code there for details.

In screenshots, it can be seen that:

- at turn 50, before any of our changes to this function but anyways etc (screenshot 1525), mecca has farms on grapes plains although plantations are unavailable, and it barely improved its much more profitable grassland tiles. Also, there is a hamlet (!!!) on plains iron which is now destroyed so all investment is lost, and not using this to improve other tiles and now have say a hamlet grassland ideally for example or something similar anyways etc. It seems a plains has a cottage on it instead of grassland, very inefficient and waste of good tiles.
- at turn 50 again, but after our changes, in an early and conservative and much earlier version of our changes (screenshot 1571), mecca is beyond comparison so much more improved, with many villages at turn 50 on grassland, and the grapes have been ignored since we don't have plantation, so workers were not wasted. Needless to say AI is tremendously stronger now with these changes, the iron is ignored as well, although in some runs there seemed to be a cottage at the time in the aztec city (if not always, improving without bonus specific improvement tiles with bonuses should now if i am not mistaken happen much less often still hopefully and if i am not mistaken i mean but anyways etc). Plains are ignored succesfully now until we build on higher food tiles first as intended anyways etc.
- at turn 50 again again (xd if i may say but anyways etc...) (screenshot 1641 but anyways etc), mecca is still strongly developed, although a bit less advanced cottages but they are present, but it is better settled (not on hill grassland anymore due to some unrelated changes i made in the meantime, and its production potential is stronger The aztec cities are doing very well too, not improving nor capitalizing on any plains tile until grass for example are handled first, and bonuses are improved very early in the game as per past changes now fine tuned a bit if i may say or enforced/made sure no issue). AI is now amazingly stronger and more efficient at improving its cities.

Gemini ai and claude ai in particular helped me a lot do these as well as myself anyways etc.

Note for modders: since this is done with if and/or else if and/or else checks, with many continue clauses at plot loop, it should be extremely fast to run as well, we may gain some time also since we don't use base advciv +/- civ4 methods/functions that may have been slower. Also, if you implement new terrains or features or modify existing ones, you'd need to update these checks as well, else your workers may stare clueless having no idea how to improve these terrains or features you added, and you'd need to specify their relative priority vs say floodplains or snow similarly. This is the trade-off or one of the trade offs of this veyr nice optimization but i believe it is very worth it, AI is very competitive now at growing its cities, at least tremedously more than before if i am not mistaken but anyways etc.

As a result, AI cities and workers should be tremendously stronger than in base advciv, at least in theory. They favour economy improvements a bit too much but seem to handle fine having enough production for now although a bit less than before as i didn't tweak it for such. They also favour slow and steady growth, and adapt to current food situation per city to decide next improvement, without overwriting other improvements that already exist until all good other tiles have been improved first, following a detailed value adjustment system if i may say but anyways etc, with the help of gemini ai and claude ai mostly as well as myself too hehe if i may say but anyways etc.

Next goal is to fix citizen allocation that is terrible in base advciv +/- civ4, as as of now for example (screenshots 1573 and 1574) ulundi is starving despite having unallocated pig and corn that are improved for many turns!!!! Or (screenshots 1595 and 1596) prague stagnant while its improved sheep grassland is unallocated. This is shit citizen allocation and i hope to fix it but anyways etc. Hopefully AI is already much stronger with our changes but thanks for past if i may say but anyways etc but i hope i can improve these things among others or not in this case i mean but anyways etc.

update : update: also disabled functionally `CvCityAI::AI_getImprovementValue` and `CvUnitAI::AI_irrigateTerritory` which solved the farm on spices plains issue when unwanted (not in our exceptions below) as well as inefficient and needless farms on floodplains, see update note 2: at [README_Known_Issues_In_Base_AdvCiv_Civ4.md#30---attemptingly-fixed-ai-workers-not-prioritizing-bonuses-to-improve-especially-food-bonuses-and-other-ai-workers-optimizations-orand-changes-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#30---attemptingly-fixed-ai-workers-not-prioritizing-bonuses-to-improve-especially-food-bonuses-and-other-ai-workers-optimizations-orand-changes-anyways-etc) for details with screenshots there as well for comparison anyways etc

## 34 - (Seemingly fixed/tweaked) Major K-Mod suboptimal food plot AI city allocation: starving or stagnant cities prefer 1 hammer over 4 food plots that are unallocated to any population ("Ulundi screenshots", "Prague Screenshots", and others) + food not being valued when food is production (e.g. worker, settler, etc if any more) when it is in fact the exact same and probably more reliable to set rather than production

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1yqmOZ1hSXPtgeVY69eFlj6R6OAM9mdze?usp=sharing).

These are a few of major k-mod bugs or/and very suboptimal city population plot allocation issues i have encountered. I noticed them while still in save file 334 which is a save file which helped me a lot enhance the AI (save file at turn 0 in drive in this known issue or/and related ones as of now anyways etc) if i may say with gemini ai and claude ai's help as well for most and my help too xd if i may say but anyways etc...

About the issues fixed here or patched if not fully fixed, as can be seen in screenshots, before the fixes/patches:

- Screenshots 1573 and 1574 (the "Ulundi screenshots"): a city is starving while having one unhappy citizen, but this could be avoided by allocating any of the pig flatland grass or sheep flatland grass tiles. Although there would be no benefit to do so as city can't grow, starving is not good either, as if the food situation is resolved in the future, we'd be happy to start from a higher point, even if it costs a bit short term production, no need to starve ourselves to death just to produce a bit faster, pay a bit more food ideally to sustain our population during this time even if a bit and even if production is a bit less (ideally only a bit) relatively in this case i mean but anyways etc
- Screenshots 1595 and 1596 (the "Prague screenshots"): a city is stagnant while unhappy as well (1 citizen). Problem: the city allocates a 2 food 1 hammer tile instead of a 5 food 1 commerce tile. I don't believe 1 hammer is better than 3 food, we may want to grow, even if unhappy, and who knows, slave later, or maybe in the meantime unhappiness situation would improve, and we'd be happy to have the extra citizen, potentially also the food bar full and growing in the meantime. But don't overdo this, no point in growing too much if too many citizens are unhappy, but it needs some help here i think, even at the cost of some production, value food a bit more i think, but be careful to not overdo it
- Screenshots 1472 (and 1475 too if i am not mistaken if it is indeed from same time but anyways etc) (the "Boston Screenshots" again if i may say anyways etc): a city is building a worker (food is production (same for the settler too if i am not mistaken and as of now anyways etc)), but it could allocate the fish in anticipation of the worker being completed, so that city could grow at end of project. 3 hammer (and 1 commerce) is same as 3 food (and 1 commerce as well anyways etc) to produce a worker, but the food is more liekly than not, in most cases to be useful, especially for this tundra city that is low on food, so allocate rather the food than the hammer, if all other things are equal).
- Screenshot 1473 (the "Mycenian screenshot"): a city is stagnant, but it has many food tiles it could use to grow. Even if city is barbarian, the flatland grass tiles could be allocated. Note: the specialist usage seems a bit aggressive so we may want to tone it down early so cities can grow more, maybe, but not sure, kept as reference if want to see it later/again in this case i mean but anyways etc

The fixes: they are tentative and quite conservative, perhaps patches in some cases, i am not really sure i found the exact or all causes, but i hope these changes help a lot, as seen in these screenshots, not in same order as before in order to make explanation easier for me (sorry for inconsistency or/and inconvenience hopefully fine or nto too bad to read but as it is maybe too but or not but or yes but anyways etc...) but anyways etc:

- the "Boston Screenshots" issue: i didn't test it, but i think one of the lines if not the line triggering it or related to it was `iValue += bFoodIsProduction ? 0 : (iFoodYieldTimes100+50)/100;` in `CvCityAI::AI_yieldValue`. Problem of this approach if i am not mistaken is that to produce a worker or settler, 3 hammer or 3 food is the exact same, it is 3 production, therefore food should be valued just as much, not 0. When worker is completed, city would be in a position to continue to grow, instead of stagnate or starve, even if a bit. I am not sure this is the only way or thing to fix and didn't check since, but i hope this helps. As of now, it is as such: `iValue += ((iFoodYieldTimes100+50)/100);` with some implementations differences (see below). It seems that in screenshots 1665 and 1666 (screenshot 1673 with the milder final version of the patch seems to indicate a good response as well, with the 2 food tile being used to produce a worker rather than the 1 food 1 hammer one, which should be better after this production (i.e. of a worker i mean if i may say but anyways etc) ends if if i am not mistaken anyways etc), although it used a more exteme approach to try to fix and debug it (see below at ulundi screenshots but anyways etc), when producing a settler, the city does use food yields now even if it is just a small sampel and it could have happened due to other reasons (such as no good hammer tile to compete with the food yields maybe), but indirectly this would also mean developing cottages and such more while producing a settler or worker, here in a flood plains cottage, which is a bit stronger than a 2 food 1 hammer flatland grass forest tile. Although i am no sure this fixes it, it does seem to be better or at least not worse in this sample, while not deteriorating city behaviour early, hoepfully helps and better this way anyways etc.
- the "Ulundi screenshots" issue: in screenshots 1573 and 1574, similarly here, or rather not my bad, but i would say at least that we can maybe fix it or patch it at that line. I tried and implemented other tentative ways to boost food quite conservatively, else cities are very unhappy, low production and high pop (screenshot 1663 and 1664 if i am not mistaken too anyways etc), and similarly the same at aachen (screenshots 1666 and 1667 if i am not mistaken too anyways etc), which is inefficient, but at least all food plots were allocated, very nice ! This indicated if i am not mistaken that issue could be addressed this way, even if in a milder way but anyways etc. So i added a check that if we are unhappy (reusing old k-mod or/and civ4 bits for that but with a new check anyways etc) value food only a bit more, but if we are happy (i.e. that we'd have room to grow), value food quite a bit extra more (but not too much i tried else we'd go back to high pop low production very angry inefficient city). So by giving a food boost but relatively milder one, we now grow but only a bit more, when angry, not a lot more (and when not angry (i.e. happy city anyways etc) we'd grow a lot more although not shown here if i am not mistaken anyways etc)). I didn't contine to check what happens at next turns, but in screenshots 1669 and 1670 for example after this fix or tentative patch, plot allocation seems now to be very very good. Production is high, and city is not starving, growing moderately, which is about perfect i'd say. After all we could slave as said before and would very much need or want the pop if our unhappiness solves. Aachen (screenshot 1672, but difference is city is not unhappy (i.e. is happy but anyways etc)) has also a very good food profile, with high plot plots all allocated and fast growth and quite high production, about perfect too!! Very good response or behaviour in screenshot 1674 as well in karakoum, which is happy too with high food and high production.
- As for the "Prague screenshots" (stagnant city not allocating food), i didn't retest it since prague was settled elsewhere many times, as shown in screnshot 1673, and consistently, i don't know if my change caused this somehow, but this is a fine choice too and a good location, after removing the jungle it is a quite strong grass spot, although a bit weak before that, and is coastal too so good for late game. So i don't have a definitive repsonse but i hope all in all these changes help a lot. Also, i don't know when i took this screenshot but seemingly later during the test changes phase, but seemingly AI would prefer a 1 food 1 hammer 1 commerce flatland plains cottage over an improved 5 food 1 commerce sheep grassland, just because it has 1 unhappy citizen. 1 hammer is not superior to 5 food!!! (or 4 food with the diff even), even if unhappy, extra pop could be used later to slave or when unhapiness is solved food would be more full even if we produce slightly less to do so!!!

The code that seemed to make a nice and decisive positive difference it seems to me at least but anyways etc was as of now this one i added if i am not mistaken anyways etc:

```cpp
		// <!-- custom: commented-out line below (that was a test to try to fix known issue 34 which is seemignly done or at least bypassed at the cost of angry cities still growing and having lower production but anyways etc) fixes it or so it seems, but at the cost of lowered produciton, even if cities have few angry citizens, try to make it more fine-tuned to city current state if i may say but anyways etc: we value food as long as we are not angry, if we are angry, value production in an attempt to build things that would make us go out of unhappiness, but even if we don't, no point in growing further, the citizen won't be allocated anyways etc ; results of this change seem to be very good, cities are not starving anymore unallocating food tiles, they grow until unhappy, then it seems to halt but the food tiles are still reasonable allocated even though production is now high as well and growth slow it seems from quick testing / glances but anyways etc, although this is a patch and not full fix, i hope this helps the issue a lot, or so it seems from quick testing and glance anyways etc -->
		// iValue += ((iFoodYieldTimes100+50)/100) * 100;
		// <!-- custom: note: also include 0 happiness (i.e not unhappy) as it seems in another same file, ulundi again was starving while not unhappy nor happy (at 0 exactly) instead of allocating a food tile anyways etc
		if (iHappinessLevel >= 0)
		{
			iValue += ((iFoodYieldTimes100+50)/100) * 3;
		}
		else
		{
			iValue += ((iFoodYieldTimes100+50)/100);
		}
```

I also did a few other tentative changes that may be relevant or not, not documented here, see [this git commit on the mod's github](https://github.com/wonderingabout/AdvCiv-SAS/commit/a6525a8b7c78ccc5058b657ec5d049d4c41d97a2) for details anyways etc.

Appendix: i have noticed the issue still happens in screenshots 1690 and 1691, now in map 336 but somehow still in ulundi!! (Although all players should be random but anyways etc). The city was just at happiness cap (5 happy vs 5 unhappy = 0 if i am not mistaken, although i am not sure it is exactly counted as such in our code but let's assume for the sake of explanation if i may say but anyways etc), so instead of `>0` i did as is now fixed also above `>=0`. The issue happened again with this change in screenshots 1695 and 1696 (starting from turn 50, the exact same save file that was already at turn 50 if i am not mistaken but anyways etc), but after ending turn, fixed itself at screenshots 1697 and 1698 right away the next, with the very nice sheep hill grassland now allocated and starvation solved :) So i hope this fixes the issue or at least i'd like to think so. If not, i hope and in all cases too i mean if i may say that it helped, and that AI is now stronger or not weaker than it was thnaks to this change (production seems good and strong too in this example if i am not mistaken too but anyways etc).

Hopefully AI is a bit stronger with this changed i attempted to make in a balanced way (not too much food, not as it was too much production)

See also [README_Known_Issues_In_Base_AdvCiv_Civ4.md#40---seemingly-fixed--addressed-tremendousmajor-plot-allocation-improvement-2-if-we-are-high-in-happiness-favour-food-tiles-much-more-and-hammer-tiles-much-less-if-happiness-is-really-high-favour-growth-dynamically-and-plot-allocation-of-these-the-more-we-can-afford-it-even-if-porduction-is-slightly-reduced-short-term-as-a-result-it-auto-corrects-at-high-happiness-with-seemingly-much-stronger-ai-and-developped-cities-as-a-result-excluded-if-food-is-production-eg-worker-settler-etc-if-i-am-not-mistaken-but-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#40---seemingly-fixed--addressed-tremendousmajor-plot-allocation-improvement-2-if-we-are-high-in-happiness-favour-food-tiles-much-more-and-hammer-tiles-much-less-if-happiness-is-really-high-favour-growth-dynamically-and-plot-allocation-of-these-the-more-we-can-afford-it-even-if-porduction-is-slightly-reduced-short-term-as-a-result-it-auto-corrects-at-high-happiness-with-seemingly-much-stronger-ai-and-developped-cities-as-a-result-excluded-if-food-is-production-eg-worker-settler-etc-if-i-am-not-mistaken-but-anyways-etc) for quite related info anyways etc

## 35 - (Attemptingly fixed or addressed) AI building too many military naval units then gets invaded on land and can't defend (10+ galleons and barely any land defender) + do not prioritize water military units if city is landlocked (i assume it means stuck in a lake or something if i am not mistaken but anyways etc)

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/15-WwGpkgFQ87O6t-tCQtJCAeiWQdQRXD?usp=sharing).

It is from when i was still playing base advciv if i may say but anyways etc, but it is an issue i had found (that i had named example 148, to be more precise 148.1 for the screenshot file but or not but or yes but or etc but anyways etc), so the save file(s) and/or screenhsots linked in this google drive issue come from base advciv nor our mod anyways etc, see for details the list of base advciv issues i had compiled as in listed gradually here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814) i made but anyways etc.

I did not test it since then, but i hope the patch/tweak/ tentative fix i added in as of now but anyways etc `CvCityAI::AI_bestUnit` helps and adresses that, making AI much more land-focused and overall stronger, even if it would now come i assume although i didn't check/test in this case if i may say but anyways etc at the cost of being military weaker on naval warfare, but i hope in most cases it would most benefit AI largely to do so anyways etc.

I also fixed thanks to gemini ai various other conditions where we don't want the AI focusing on military naval units, such as before war (build more military land units rather relatively (didn't change land production although i'd want to but maybe fine as such for now but anyways etc, only removed naval military unit one)), or if city is landlocked (i.e. coastal but on a lake, then military naval units would be pointless there, leave it as it is for simplicity, but do not prioritize further in this case if i may say but anyways etc).

## 36 - (Attemptingly fixed or addressed) AI building settlers at critical time when war is likely, instead of preparing for war: very bad as the few more units with the hammer saved could make us gain or not lose the war, while the extra city makes all our empire thinner and our units split, on top of having less units overall as well anyways etc

No screenshots from that time except save files, that i'd prefer not to rescreenshot now but anyways etc, however i had listed this issue in example 47 in the list of base advciv issues i had compiled as in listed gradually here in [this CFC forum post](https://forums.civfanatics.com/threads/ai-city-placement-and-misc-suggestions.695343/page-7#post-16782814) i made but anyways etc, where it happened 2 times to/for Augustus AI making it/him but anyways etc much weaker militarily and my conquest of him much easier in this game (although he/it but anyways etc was still surprisingly strong so is like a wasted chance in this case at least i mean but anyways etc)

In all cases but anyways etc, i have in a similar function than in [README_Known_Issues_In_Base_AdvCiv_Civ4.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but-anyways-etc) (while doing this known issue as well but anyways etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender--do-not-prioritize-water-military-units-if-city-is-landlocked-i-assume-it-means-stuck-in-a-lake-or-something-if-i-am-not-mistaken-but-anyways-etc) (while doing this known issue as well but anyways etc), a spot where we could add such a restriction to settler building.

Hopefully AI is now much stronger with this change as well although i didn't test it since i made it but anyways etc.

## 37 - (Workaround and rebalanced) AI building 2 settlers very inefficiently at same time or when a settler unit already exists - now settler is a national unit (only 1 allowed per player)

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1Uf1OOilcGXfyNix7EwXYhQCcsd-bq4Pa?usp=sharing).

Expanding on previous issue as of now in number 36 but anyways etc, i have also noticed, now in this as of now known issue number 37 but anyways etc, that for example in screenhot 1680, AI was building 2 settlers at same time. It is very inefficient, and i thought that building one settler in top city (for efficiency, as weakest city may take a long time to build it hindering its growth or/and not getting settler ready on time but anyways etc ; ideally i would handle that too but not done for simplicity and as of now simply building in any city that does it but anyways etc) is enough.

Instead of tediously telling AI which city to build its settler on, and only in 1 city at a time, as the hammer loss is huge of building 2 settlers, and also not if we already have a settler unit existing, as founding too many cities may result in economical inefficiency so build them gradually rather instead of spam then crash i'd say i think at least in this case if i may say but anyways etc, making the settler a national unit seems a very very nice tradeoff and easy way to achieve that.

On top of that, it also adds strategy, as now settlers are more precious if i may say in this case at least but anyways etc, as although their price is same as before, killing/hunting a player's settler is worth more, potentially even worth going to war for depending on tempo and your or a player's strategy (kind of how declaring war to (attempt to) steal a worker (now restored in advciv-sas unlike in base advciv but anyways etc, see [README_Quick_Get_Started_Guide.md#civilian-units](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Quick_Get_Started_Guide.md#civilian-units) for details) may be good intiative if i may say but anyways etc). So AIs and all players must get better or be more strategic or/and value more guarding their settlers, as losing one is a higher blow if one may say, as although cost is same, city building would be significantly more delayed.

I believe these changes add nice strategy and overall on top of AI benefits make the game really interesting. Although i was and am not still totally sure about it, maybe humans can use it to their advantage, for example to slave strategically or such to enhance their settler building maybe? Which may also be easier since slaving is worth now in advciv-sas unlike base advciv (see [README_Quick_Get_Started_Guide.md#general-changes-non-exhaustive-see-global-defines-and-other-unrelated-xml-files-for-details](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Quick_Get_Started_Guide.md#general-changes-non-exhaustive-see-global-defines-and-other-unrelated-xml-files-for-details) for details anyways etc), so they can maybe have a small edge over AI players, at least for now sice i didn't or other modders hehe didn't optimize it. But AI players also have handicap advantages especially at higher difficulties so they wouldn't be as affected by this. Still, they may delay a tiny bit more building their cities which should also help them gain in effiency economically or not ruin their hammer production. Instead of doing an extensive code patch or fix or rework, i find or/and believe this works really well, perhaps even best if i may say, and i find it an interesting change.

As for the screenshots, after this change, in screenshots 1684 to 1689, the native american AI player now moves north instead, and is not building 2 settlers at same time. And while the settler is travelling, AI is not wasting time building another settler but is using effectively its hammer. I believe AI will be a lot more efficient thanks to this in most cases. Its city location is also nice in these screenshots 1689 and such, hopefully thanks to our city location settling/founding/planting choices AI changes as well but anyways etc.

Also this change is also thanks to claude ai which (who? But anyways etc) helped me locate where to make units national in the xml although i could have found myself but it helped still thanks claude ai if i may say but anyways etc.

Note: after retesting from turn save file at turn 0 to be sure, and also due to the below as of now known issue 38 so i wanted to test again anyway and since they seemed to do same when starting from save file that is at turn 50 if i'm not mistaken, i wanted to try from save file that is at turn 0 instead, i have found they did it even nicer, and settled extremely ambitiously a super nice city not too far from their capital, very very nice, see screenshots 1701 and 1702 (skipped 1700 since 1702 was more nicely centered around city but 1700 was first centered around city if i may say before 1701 but anyways etc) for details/illustration of it if i may say but or not but or yes but or and etc anyways etc.

## 38 - (No idea why but anyways etc) Sometimes compile mysteriously/strangely/inconsistently fails, and recompiling succeeds under/with but anyways etc exact same source files if i am not mistaken but anyways etc

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1rjgs7CbmxP78ixCWrf4W-a8xn_7mT68k?usp=sharing).

I have no idea why, and this is one of the strangest issues i have encountered so far in base advciv or rather advciv-sas, but recompiling dll after adding a code comment or tweaking it, for peace of mind in my case if i may say but anyways etc, resulted in a compile error at very end (see screenshots for details, log missing as i thought it was a regular issue or/and simply forgot to save it apart back it up if i may say but anyways etc, and overwritten at next compile due to my carelessness hehe if i may say but i hope the screenshot helps enough at least even though log woudl have been ideal maybe unless screenshot has all info but in all cases if i may say anyways etc).

This should not have happened, as i only changed code comments, which should be inconsequential if i am not mistaken regardless of what i type in them but anyways etc.

However, after recompiling, with exact same source files, no change at all if i am not mistaken but anyways etc (except maybe ctrl+z ctrl+y ctrl+s just to make sure i had no other change or for some other related or not reason but anyways etc), then suddenly compile succeeded.

At this point, or in general, i'd say my best guess would be a cosmic ray fell on my PC somehow and corrupted a bit like in the mario speedrun and as it happened to nasa if i am not mistaken but anyways etc.

But in all cases, and more seriously really, even though my previous guess was quite serious too, i'd recommend if all seems good otherwise, to make sure you remove all content in temp_files folder (as i have found fast compile seems to cause issues and i strictly avoid it unless doing quick testing never for final dll as of now at least but anyways etc, as mentionned in [README_Known_Issues_In_Base_AdvCiv_Civ4.md#5---seemingly-worked-around-now-player-name-same-as-windows-10s-for-example-anyways-etc-username-causes-new-game-screen-to-be-stuck-unless-a-custom-name-is-chosen-ifafterwhile-dll-has-been-fastdep-compiled)](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#5---seemingly-worked-around-now-player-name-same-as-windows-10s-for-example-anyways-etc-username-causes-new-game-screen-to-be-stuck-unless-a-custom-name-is-chosen-ifafterwhile-dll-has-been-fastdep-compiled) too if i am not mistaken but anyways etc ; and note too: i think i also made extra sure here that i did delete it as well just before launching the faulty compile, hence my guess that it would be something else like a cosmic ray or soemthign else maybe like a quantic ray xd maybe?? Whatever that means but anyways etc, added this extra clarification as part of reading claude ai's answer or the beginning of it, which gav me the idea to add this, hopefully clearer with this although maybe uneeded or maybe needed in this case i mean but in all cases anyways etc), and compile again, which in this case, again strangely but all goood maybe xd if i may say although i would have liked to know how maybe too indeed if i may say but anyways etc. So adding this info for reference if helps if i may say but anyways etc.

## 39 - (Seemingly fixed or/and enhanced) Make AI workers move sooner to City B or City C or such, and vice versa, if current city is already improved enough and don't need to be over improved, while other cities are not improved enough and would much rather need it

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1eabVp0msOXluGcyoKZzUHhNubsyAOR37?usp=sharing).

After our AI workers had nice and efficient, at least nicer and more effiicent worker routine and algorithm/priorities or/and more often but anyways etc, the issue i noticed is city A and city B are overimproved, while City C badly needed improvements but was under improved, as can be seen for example in screenshots 1728 and 1729, where Ectabana is not improved barely, while AI workers continue to over improve city A that can't allocate any more tiles anyway due to its pop limit (why improve 15+ tiles when pop is around 10, go to city B or city C or such other cities if any)

So i added a fix to that in `CvUnitAI::AI_workerMove`, with chatgpt o-3's help too but anyways etc, see there for details.

After recompiling and testing these changes, as can be seen from existing screenshots between 1734 and 1740, workers move sooner to city C, and around turn 100 to 125, it has an overall nicer edge in terms of improvement, workers are not over improving city A or B too it seems at quick glance if i am not mistaken although i didn't look in detail, so hopefully AI is stronger thanks to these changes as well but anyways etc.

update: added an extra tweak so that workers stay longer in city B (small cities), as they are expected to grow fast, so don't leave at 2 improved plots if city size is size 2, improve say 4 or 5 plots (see code there for details anyways etc)

## 40 - (Seemingly fixed / addressed) Tremendous/Major Plot allocation improvement 2: If we are high in happiness, favour food tiles much more, and hammer tiles much less if happiness is really high (favour growth dynamically and plot allocation of these the more we can afford it), even if porduction is slightly reduced short term as a result, it auto corrects at high happiness, with seemingly much stronger AI and developped cities as a result (excluded if food is production (e.g. worker, settler, etc if i am not mistaken but anyways etc))

See screenshots and files about/related(ing? Anyways etc) to this issue in this [google drive folder link](https://drive.google.com/drive/folders/1OsMF8q8NbcfGFS8oMg-mDkL_F6iju9_w?usp=sharing).

As can be seen in existing screenshots between 1742 and 1745, AI, here China AI but anyways etc, had a major problem with tile allocation, here choosing to allocate a juicy 0 food 6 hammer tile from about turn 50 to close to turn 100. Although the hammer is nice though, it is better to capitalize on food early (which can be symbolized very well as having happiness surplus (e.g. 9 happy and 1 unhappy is 8 happiness surplus anyways etc)).

So thanks to chatgpt 3-o, and my prompt and adjustments or not or yes or etc but anyways etc but it helped me lot too but anywyas etc, i added a patch/fix/tweak in as of now `CvCityAI::AI_yieldValue`, to value food yields in plots the more happiness we have (for example as of now if i'm not mistaken but anyways etc with 9 happy and 1 unhappy so 9 - 1 = 8 happy surplus, we'd have the food value now being multiplied by 8, but if happy surplus is only 2 (say 9 happy 7 unhappy for example but anyways etc) then the food multiplier would only be 2 which seems fine as it is quite mild maybe (i don't know but i assume seeing very quickly other mulitplicative calculations if i may say but anyways etc in this function but only glanced and from my memory of it so check to be sure but anyways etc) but still encouraging growth if i may say but anyways etc).

As an extra nice addition suggested by chatgpt 3-o if i may say but anyways etc, and that i tweaked too if i may say but anyways etc, if we are happy to very happy (as of now 3+ happiness surplus (e.g. 7 happy - 4 unhappy = 3 happiness surplus if i'm not mistaken but anyways etc)), then we also reduce the value of hammer/production, as indeed, it is more valuable to grow, we'd allocate the high production tiles naturally as we have more population, and as long as we have extra happiness, better use it.

Not accounting for health to simplify, and as i assume cities would generally manage it well, even if high early is fine, cities should gradually remove unhealthiness generally if i'm not mistaken, so focus on raising pop as long as we have happiness surplus. Then, when we are close to happiness cap (i.e. happiness about equal to unhappiness, then do not value food as much and go back to hammer economy relatively and or other relevant yields or such (same as before)).

Also added the food is production exception, i.e. if we're producing a worker or settler, 6 hammer is better than 3 food. Provided we can bounce back to food allocation, which is not guaranteed. But thankfully, AI allocates and swaps tiles dynamically, this is extremely nice.

As for results, see existing screenshots between 1760 and 1782 if i'm not mistaken but anyways etc, but they are extremely good or so it seems in this situaiton at least if i may say but anyways etc.

At low pop, china AI best on food, and its cities quickly grow, and actively ignore the copper tasty 0 food 6 hammer tile, seemingly except when producing a worker as they should, then bounce back to food. China AI's city slaves twice if i'm not mistaken too but anyways etc, and has much more buildings at turn 100, effectively using the surprisingly high happiness reserve they have somehow. And China AI could build the great wall in time in its capital too if i'm not mistaken but anyways etc, so high pop cities do not fall into too much food trap, this is a dynamic fix/patch/enhancement or fine-tuning, i don't know if it always apply, but i'd tend to say AI is much stronger thanks to it at least in this sample, other cities seem to behave fine at quick glance too (see the few screenshots there in this drive link for details but anyways etc).

I'm very happy of this result, thanks a lot to chatgpt 3-o for help despite the nagging and that it annoyed me hehe if i may say but anyways etc on math as i told it too if i may say in this case i mean but anyways etc it did hehe, but this helped me and helped a lot if i may say which i told it too in this case i mean but anyways etc, fix the formula and such thanks lot etc i mean but anyways etc.

See also [README_Known_Issues_In_Base_AdvCiv_Civ4.md#34---seemingly-fixedtweaked-major-k-mod-suboptimal-food-plot-ai-city-allocation-starving-or-stagnant-cities-prefer-1-hammer-over-4-food-plots-that-are-unallocated-to-any-population-ulundi-screenshots-prague-screenshots-and-others--food-not-being-valued-when-food-is-production-eg-worker-settler-etc-if-any-more-when-it-is-in-fact-the-exact-same-and-probably-more-reliable-to-set-rather-than-production](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#34---seemingly-fixedtweaked-major-k-mod-suboptimal-food-plot-ai-city-allocation-starving-or-stagnant-cities-prefer-1-hammer-over-4-food-plots-that-are-unallocated-to-any-population-ulundi-screenshots-prague-screenshots-and-others--food-not-being-valued-when-food-is-production-eg-worker-settler-etc-if-any-more-when-it-is-in-fact-the-exact-same-and-probably-more-reliable-to-set-rather-than-production) for quite related info anyways etc

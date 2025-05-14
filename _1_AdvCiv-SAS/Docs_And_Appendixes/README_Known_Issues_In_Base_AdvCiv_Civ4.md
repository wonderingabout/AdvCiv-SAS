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

There may be(/have been, but anyways etc) other cases like these, and i don't know if the cause is one of the changes i made to barbarian (xml) code, or how it just is/was. I tried to fix it by using iWonderConstructRand -9999 on LEADER_BARBARIAN in leader head infos xml file, but they still build national and great wonders alike, and all the buildingclass NONE spaghetti code whether it is here (for national wonders) or not (for great wonders) does not change anything, they even build shrines like the mahadhobi as of now me writing this anyways, is not necessarily a bad design, but ideally i would want them to focus more on warmongering their key rol in advciv-sas and be more efficient in that anyways etc. 

So/And anyways etc i removed all such old logic of buildingclass NONE in (adjust if non-steam game or other mod path you have to where your advciv-sas or/and other mod you're using or not etc anyways etc is anyways etc) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Civilizations\CIV4CivilizationInfos.xml`.

For now trying the FLAVOR_MILITARY 10 approach (inspired or rather taken (as i already had the idea but anyways thanks still or not thanks or thanks still or and other or and not anyways etc) from genghis khan's code), not sure it will make a difference but this (value not the leader, i don't know enough about genghis khan to say if he aligns or not, i could maybe express a tentative opinion if i knew more but abstaining from that as i don't know lot or enough about him even though may be cool or/and interesting maybe i mean to know but anyways etc anyways etc)align with their profile of being (more of a at least ideally i.e. in theory if not more ideal too or not but(/) anyways etc anyways etc...) anyways warmongerer anyways etc.

Currently testing a builUnitProb 100 or similar in leader barbarian that seems very very effective, but testing more if i test to be sure, may be fixed now for real or maybe not, hopefully, but maybe or maybe not, but anyways etc anyways etc anyways etc

## 4 - Sevopedia Unit's placeRequires's Religion button (for example any religious missionary unit) not redirecting to sevopedia religion (nothing happens on click anyways etc)

This is a bug i have noticed in AdvCiv and after checking, many other mods, among those (few i tried): ROM 291, RFC DOC, Neoteric World (since i have it too (to check their sevopedia content or/and such or/and other or/and not anyways) even though i did not use anything from it at least but may be useful some day or not anyways etc anyways etc), History Rewritten too.

But clicking in AdvCiv in sevopediabuilding for example on any religious temple's placeRequires's religious icon/button successfully redirects to the sevopedia's religion page.

Among the mods i tried, only Realism Invictus's sevopedia unit's placerequires's religion button works as intended and successfully redirects to the religion's page

I tried to import its code but their gc uses difference methods that we don't have it seems like getNumPrereqAndBonuses and such, may not be hard to fix or not, but leaving as is, finding how realism invictus does it, or finding yourself the cause if you want to investigate it, may help solve it.

As for me this is quite minor, and even though i would have loved (really) to fix it (but anyways etc), leaving a note here rather as i don't know also how nested in the code the issue is, i would ideally but anyways love to dive deeper but doing other code things, at least for now if not always or maybe not, but anyways etc, if so (that i would look again), hopefully these lines may (then) serve as a reminder of the issue and the current status of solving it (i have found in realism invictus mod it works fine unlike in other mods (that i tried about/for this issue anyways etc), can investigate from there maybe anyways etc)

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1vRIFzwNijAjbmPBVUvSk90YjURXh-lG1?usp=sharing)

## 5 - (seemingly fixed now) player name same as windows (10's for example anyways etc) username causes new game screen to be stuck unless a custom name is chosen, if/after/while DLL has been fastdep compiled

A quite weird issue i never had before, but after doing a fastdep (auto, not me), since i changed only one .cpp file to add the placeExclusiveCivs new sevopedia feature (see the [/README_Sevopedia_Reworks.md#example-7-unit-list-category](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md#example-7-unit-list-category) for details)

A few screenshots of the issue here in as well as the DLL with which i had the issue (not sure is the cause but happened while having it if i am not mistaken anyways etc) [this Google Drive folder](https://drive.google.com/drive/folders/19T9I75vGCk58pFSR60y2Tmj69-NoFFtk?usp=sharing)

More context of how i implemented the change in the .cpp and such can be found in this Google Drive about Claude AI's first prompt i successfully implemented in AdvCiv-SAS, [by finding such a (Google Drive too anyways etc) link in the Claude AI part of the README there (click on this link to be redirected anyways etc)](/README.md#claude-ai-the-newcomer-hehe-xd-anyways-etc-welcome-anyways-etc)

I don't know if fastdep compiel was the cause or just some weird corruption unnotified happened (i don't know a lot about these if at all hehe but it was reproductible, and my player name also unusually changed just after this fast compile so i can quite confidently say it is maybe indeed related but anyways etc (for example after checking indeed Civ4ScreenShot3010 in the advciv-sas's mod journey drive (see main README.md for link anyways etc), with last compiled DLL before this Claude AI related .cpp change and recompile, had my windows username as default player name as can be seen in screenshot, but the screenshots of the issue in the drive linked above, that happen between Civ4ScreenShot3095(new game not yet started after the cpp changes and recompile) and Civ4ScreenShot3096 (where issue is solved)); in short if my long sentence still makes sense xd and i didnt get tangled into it if this is a word too but anyways etc anyways etc, default civ4 player game suddenly changed from windows username to steam username (that i didnt want to show in screenshots too as is private to me but anyways etc, and this coincidated if this is a word but anyways etc with this screen being stuck issue))

To solve it, or at least after doing this issue that was reproductible if i am not mistaken is now solved, i deleted (adjust to where your mod path is anyways etc) for example for me this is where the folder temp_files/Release/ is: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\Project\temp_files\Release\ , this folder (i deleted it anyways etc), and after recompiling cleanly, now i can play with windows username as usual, even though i had to change back the steam username to the name i wanted (first manually ingame at new game settings screen, then after seeing it works in CivilizationIV.ini (see [CivilizationIV.ini shortcut for example](/_CivilizationIV.ini%20-%20User%20Shortcut%20Example.lnk))), here and for testing at least if not always or not anyways etc or maybe not but for testing or not if i want or not or and other or and not or do or not or etc or etc anyways etc, the windows username is fine with me ("PC" in the screenshots anyways etc anyways etc...)

Not sure what the issue was, would have liked to be notified of the error/corruption cause of it somehow, but program runs fine as usual now, so maybe corrupted unnotified compilation, or fastdep issue perhaps (even though fastdep compiles seemed to work fine in the past as in just yesterday/the day before for the [unitai renaming (commit)](https://github.com/wonderingabout/AdvCiv-SAS/commit/701e2e31279d7ab152f91b431a81c1bae9c22734) but anyways etc as long as is solved is all good maybe even though bit weird but unsettling but whatever it is/was is maybe consistently solved now (not gauranteed, may or not be the case but anyways etc))

So hopefully fine and solved now even though not sure and not guaranteed but maybe is hopefully or maybe not, in all cases hopefully this info is helpful to me or and others or and not anyways etc anyways etc.

# 6 - (now worked around anyways etc) Too long XML code comments cause errors or/and game crashes

Be careful of having too long XML code comments, they (seem to indeed but anyways etc) cause game crashes (or maybe errors too? Anyways etc) in some circumstances, i assume it is especially due to or/and caused by if it's not same but anyways etc nested code comments more specifically but anyways, since i don't know more, it is only speculatin, but moving these nested code comments outside of the XML did fix the early game crash issue that is reproductible.

Something to keep in mind perhaps if i may say i mean anyways while doing XML code comments, that if they have to be long, move them outside of the XML tree entirely maybe, or at least outside the nested ones maybe, tweak this advice or opinion or feel or not feel or yes feel but maybe rather too view/thought as you see fit and/or want or not, hopefully helpful or not or and other or and not but in all cases maybe or not or yes anyways etc anyways etc anyways etc.

More details here too anyways etc in anyways etc anyways etc anyways etc: [AudioDefines-nested-comments-out-of-xml-file-to-avoid-crash.txt](/Assets/XML/Audio/AudioDefines-nested-comments-out-of-xml-file-to-avoid-crash.txt)

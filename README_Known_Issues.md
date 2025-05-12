# Known issues

Some known issues (non-exhaustive ideally yes but maybe not anyways etc) about AdvCiv code or earlier or/and AdvCiv-SAS specific code that may be fixed someday or not (ideally yes too same but maybe not especially if deemed not so bad or even part of the necessary mechanic but then would not be an issue but if known maybe or not or yes but anyways etc anywyas etc anyways etc).

## Redundant attribute values for all AI Civs

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

Some of these such as iLoveOfPeace are not used in AdvCiv; i disabled (commented-out) from display (in SevoPediaLeader.py) such unused ai attributes to not clutter the display, see [AI Personality Panel Feature section](/README.md#ai-personality-sevopedia-feature) for (more) details, and more specifically in the full AI Personality Panel Feature [this part](/README_AI_Personality_Panel.md#note-about-some-ai-attributes-being-ignored).

Leaving as is otherwise (except from hiding most or/and commenting out unused ones such as iLovePeace (in AdvCiv) anyways) for now if not always or not anyways etc.

We may also spread some values more (i.e. in AdvCiv-SAS etc anyways) that are way too often shared between leaders, not just the common to all leaders, may be a good opportunity perhaps, but not sure or guarnateed, for now only mentionning the issue.

## (now fixed) Barbarians (cities) building wonders

UPDATE: seemingly now fixed using builUnitProb 100 or a similar value, testing more to be sure but seems extremely effective in stopping all (great and wonder) building tendency entirely in barbarian, ened to test more to be sure (in case) i am not mistaken anyways etc, may tone it dow a bit so they can build the barabarian lighthouse they seemingly never do now, but anyways etc

In AdvCiv base code after implementing the barbarians boost to make them more economically viable and/or strong but anyways etc anyways etc anyways etc... Barbarians are still trying to build wonders sometimes, the base AdvCiv code does not prevent that, or/and at least not always maybe or not or yes indeed but anyways etc anyways etc ; and even complete them sometimes actually, for example(s anyways etc anyways etc):

A few screenshots of the issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1p5O09XzbbrM5x2hxFD6RGvBpuU8RzPAd?usp=sharing)

There may be(/have been, but anyways etc) other cases like these, and i don't know if the cause is one of the changes i made to barbarian (xml) code, or how it just is/was. I tried to fix it by using iWonderConstructRand -9999 on LEADER_BARBARIAN in leader head infos xml file, but they still build national and great wonders alike, and all the buildingclass NONE spaghetti code whether it is here (for national wonders) or not (for great wonders) does not change anything, they even build shrines like the mahadhobi as of now me writing this anyways, is not necessarily a bad design, but ideally i would want them to focus more on warmongering their key rol in advciv-sas and be more efficient in that anyways etc. 

So/And anyways etc i removed all such old logic of buildingclass NONE in (adjust if non-steam game or other mod path you have to where your advciv-sas or/and other mod you're using or not etc anyways etc is anyways etc) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Civilizations\CIV4CivilizationInfos.xml`.

For now trying the FLAVOR_MILITARY 10 approach (inspired or rather taken (as i already had the idea but anyways thanks still or not thanks or thanks still or and other or and not anyways etc) from genghis khan's code), not sure it will make a difference but this (value not the leader, i don't know enough about genghis khan to say if he aligns or not, i could maybe express a tentative opinion if i knew more but abstaining from that as i don't know lot or enough about him even though may be cool or/and interesting maybe i mean to know but anyways etc anyways etc)align with their profile of being (more of a at least ideally i.e. in theory if not more ideal too or not but(/) anyways etc anyways etc...) anyways warmongerer anyways etc.

Currently testing a builUnitProb 100 or similar in leader barbarian that seems very very effective, but testing more if i test to be sure, may be fixed now for real or maybe not, hopefully, but maybe or maybe not, but anyways etc anyways etc anyways etc

## Sevopedia Unit's placeRequires's Religion button (for example any religious missionary unit) not redirecting to sevopedia religion (nothing happens on click anyways etc)

This is a bug i have noticed in AdvCiv and after checking, many other mods, among those (few i tried): ROM 291, RFC DOC, Neoteric World (since i have it too (to check their sevopedia content or/and such or/and other or/and not anyways) even though i did not use anything from it at least but may be useful some day or not anyways etc anyways etc), History Rewritten too.

But clicking in AdvCiv in sevopediabuilding for example on any religious temple's placeRequires's religious icon/button successfully redirects to the sevopedia's religion page.

Among the mods i tried, only Realism Invictus's sevopedia unit's placerequires's religion button works as intended and successfully redirects to the religion's page

I tried to import its code but their gc uses difference methods that we don't have it seems like getNumPrereqAndBonuses and such, may not be hard to fix or not, but leaving as is, finding how realism invictus does it, or finding yourself the cause if you want to investigate it, may help solve it.

As for me this is quite minor, and even though i would have loved (really) to fix it (but anyways etc), leaving a note here rather as i don't know also how nested in the code the issue is, i would ideally but anyways love to dive deeper but doing other code things, at least for now if not always or maybe not, but anyways etc, if so (that i would look again), hopefully these lines may (then) serve as a reminder of the issue and the current status of solving it (i have found in realism invictus mod it works fine unlike in other mods (that i tried about/for this issue anyways etc), can investigate from there maybe anyways etc)

A few screenshots of the current issue (screenshot previews below as long as links are valid anyways etc) in [this Google drive folder about this issue](https://drive.google.com/drive/folders/1vRIFzwNijAjbmPBVUvSk90YjURXh-lG1?usp=sharing)

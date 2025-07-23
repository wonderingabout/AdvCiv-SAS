# Coding Help for AdvCiv / AdvCiv-SAS

This is a non-exhaustive page containing some ressources i found helpful.

## Modding disclaimer and general information

I don't know a lot about XML, C++, or Python, and (only) got familiar with these languages recently as i started developping for Civ4 this AdvCiv-SAS mod.

I did have previous knowledge though.

I cannot be assumed or expected to be available or responsible to provide any coding help or feedback (i'd prefer to have my peace of mind rather, even though i may occasionnaly or more often, but not guaranteed and maybe not if i don't want or do so or any other reason or not, but i might or might not, just this is a fair warning/caution point about that, anyways), however i hope these few ressources i have accumulated may help those who wish to start their own mod.

I can also not be held responsible for any damage resulting of following these instructions, whether these are followed correctly or incorrectly. I am only providing them as general information, and while i hope it helps, you are responsible for checking it, verifying it, and using it, and any consequence that may happen as a result.

Hopefully you'll find them helpful though, but in case not or something happens, this is just to protect myself and talk to you in all fairness.

Else or additionally, you may find more help asking your question(s) directly on [CivFanaticsCenter's Civ4 Forum](https://forums.civfanatics.com/categories/civilization-iv.143/) rather maybe. Hopefully this data i provided is also helpful though.

## A few useful tips

### google drive image link in html tag if i am not mistaken anyways etc

Was not easy to find how, but [this stackoverflow answer](https://stackoverflow.com/a/52067077) shows how to do it successfully, ai-generated images as of now in our advciv-sas mod anyways etc use this successfully as well anyways etc, see also the implementation in the main README.md at [README.md#ai-generated-images](/README.md#ai-generated-images) for example of how it is done successfully at least as of now if it helps anyways etc.

To get the id from the url, what i did and that works as of now anyways etc is to click on the image in the drive folder containing the image, then the sandwich menu whatever they call it xd anyways etc, then "open in new window", then the following url such (for example in `https://drive.google.com/file/d/1_CcxxS36yJmp779-oxuQD3QSWI0eBubC/view` has the id `1_CcxxS36yJmp779-oxuQD3QSWI0eBubC` that i can insert in the src field following the stackoverflow answer instructions/example linked and that as of now seems to work-function fine for all the images we inserted in the git readme as such anyways etc. (note: i didn't add too many images as it would be tedious to manage in the drive vs git, but for non-essential ones and especially heavy ones atleast in advciv-sas i mean anwyays etc anyways etc, moved them to the drive or fetched them for there directly if already there anwyays etc)

Was not easy to find how at least to me anyways etc so i am glad i found how anyways etc and so i mean anyways etc i hope these instructions help i mean at least as of now, anyways etc anyways etc anyways etc.

### Download media assets for example on youtube

Disclaimer/note: for copyright disclaimer and such, please read this first [/README.md#copyright-and-disclaimer](/README.md#copyright-and-disclaimer). Note also it is up to you to download or/and use copyright-safe or not assets in your mod or other places, at least it is your responsibility to do so, these are only provided as general instructions, hopefully helpful but i have to cover myself xd too i mean if i may say but anyways etc.

Disclaimer 2: Specifically about downloading from youtube, it seems from chatgpt's explanation and what i understand of it that even if a media file is public domain, downloading it from youtube may violate a license for example if the recording is not public domain, it is your responsibility to verify and make sure you use a copyright-compliant media file for the general instructions below that i provide in hope they help and without any warranty, in addition to any disclaimers in main readme's copyright section and and in this modding_ressources section as well if i am not mistaken too anyways etc

Moving forward, i found this very nice reddit post if i may say but anyways etc on [how to download youtube videos and parts of youtube videos](https://www.reddit.com/r/youtubedl/wiki/howdoidownloadpartsofavideo/) with yt-dlp, i also found this very nice reddit post too i mean very helpful but anyways etc on [how to download any media file from youtube to mp3 using yt-dlp](https://www.reddit.com/r/youtubedl/comments/130i9og/ytdlp_how_to_automatically_convert_all_audio/)

In case the information of this second link disappears someday, here is a copy of it anyways etc:

>What I actually ended up doing was adding this to the configuration file:
>
>--audio-format mp3 --embed-thumbnail --add-metadata

Thanks for help if i may say but anyways etc thanks anyways etc...

Here is now if i may say but anyways etc (I like this theatrical performance of an announcer i am performing xd and very excited to do so in my mind but anyways etc...) an example of how to download one, for an audio asset for example here anyways etc ! (, but anyways etc) As if i'm not mistaken civ4 expects .mp3 files of a music without copyright claim on it, or "royalty free music" as it seems they call it anyways etc (note: to be honest i think it's kinda shit (the music i mean but anyways etc) but it is helpful and maybe not too bad, but thanks for that anyways etc), for/to download(ing/ but anyways etc...) the entire media file as mp3 in this case if i'm not mistaken anyways etc.

But while writing this, it now played this very nice or cool/relaxing soft if as they say if i may say too in this case but anyways etc or not or etc but anyways etc, from [this youtube playlist](https://www.youtube.com/watch?v=MM2-z8inpY8&list=PLfP6i5T0-DkLlj5LDluZcpP9n6YlATpSG&index=3) for example but anyways etc ; also adding what i know of yt-dlp or not or yes but anyways etc such as using `-x`

(note: personally i also removed the thumbnail as it makes file needlessly heavier, plus may cause bugs or not (untested but maybe or maybe not), also i prefer it more abstract i think? Not sure but is as it is, enable thumbnail if you want but anyways etc) (edit: also so i don't have to worry needlessly about whether/if the image itself is or may be copyrighted xd so hopefully or/and maybe best for all or in/for all cases or not or yes or etc but is as i want it at least in advciv-sas but anyways etc)

```bash
yt-dlp -x https://www.youtube.com/watch?v=MM2-z8inpY8 --audio-format mp3 --add-metadata
```

Please note that it is also possible to set a start time and end time, like i mean you don't have to have the whole file but say from 00:30 to 00:55 section/part of the media file if you want, see the first reddit link in this readme.md section (but anyways etc...) for details if i'm not mistaken and still available, but anyways etc...

Here is an example of how to download same video/media file anyways etc but from seconds 15 to seconds 45 (i.e. from 00:15 to 00:45 of the video/media file if i am not mistaken anyways etc), not sure is best way to do it, may or not be, but at least seems to work/function anyways etc, hopefully helpful or not or yes or other or etc or yes or not or other or etc anyways etc ; but since i couldn't find how exactly to download not best audio AND if i may say anyways etc only a part of the video, then i asked chatgpt who told me how to do it so hopefully helpful or not or yes or etc but anyways etc:

```bash
yt-dlp -x --audio-format mp3 --postprocessor-args "-ss 00:00:15.000 -to 00:00:45.000" "https://www.youtube.com/watch?v=MM2-z8inpY8"
```

To download from a specified time to end, use, as chatgpt advsied/told me when i asked it thanks but anwyays etc (thanks me (i.e. / to me too i mean but anyways etc)) anyways etc:

```bash
yt-dlp -x --audio-format mp3 --postprocessor-args "-ss 00:00:15.000" "https://www.youtube.com/watch?v=MM2-z8inpY8"
```

Then untested but to download from begining to an end time, use similarly as advised/told by chatgpt anyways etc:

```bash
yt-dlp -x --audio-format mp3 --postprocessor-args "-to 00:00:45.000" "https://www.youtube.com/watch?v=MM2-z8inpY8"
```

Note: if you don't know where/when exactly to cut, see note about Audacity in [/README.md#some-useful-tools-while-doing-this](/README.md#some-useful-tools-while-doing-this) hopefully helpful or not or yes or etc but anyways etc

Note 2: there are other websites than youtube to download or find music, including royalty-free one ideally or free for use or such, see [/README.md#some-useful-tools-while-doing-this](/README.md#some-useful-tools-while-doing-this) for example of an example of tool(s) i mention there to not redundantly repeat myself here and in case it changes too and slightly bit tedious but anyways etc hopefully helpful or not or yes or etc or other but anyways etc...

### add media assets

Disclaimer/note: for copyright disclaimer and such, please read this first [/README.md#copyright-and-disclaimer](/README.md#copyright-and-disclaimer). Note also it is up to you to download or/and use copyright-safe or not assets in your mod or other places, at least it is your responsibility to do so, these are only provided as general instructions, hopefully helpful but i have to cover myself xd too i mean if i may say but anyways etc.

To add music to a leader in advciv-sas for example (i assume would be the same or very similar in an advciv or civ4 based mod too if i am not mistaken and if i may say too but anyways etc anyways etc anyways etc), do a vs code global search for example of "ewuare_" (new leader we added in advciv-sas for the kingdom of benin anyways etc) and see in audio xml files (and also a bit in leaderhead too if you track where the corresponding assets such as for example "DIPLO_EWUARE_EARLY" lead to in the leader head info xml file too but anyways etc for an example of how we added his music anyways etc.

Note: be very careful!(!!! but anyways etc anyways etc anyways etc) Need to remove the `.mp3` in filename else file is unreadable anyways etc!!!

### write git commit message gradually as you do changes before committing them, and keep notes of ideas anyways etc

I have noticed while developing this advciv-sas mod at some point it is is so helpful to write bit by bit and gradually the commit message rather than do all changes then try to guess/remember which. Not necessarily listing all changes, but the main ones or most relevant or important ones in importance i mean (redundant to say important importance but anyways etc) as bullet points or such as you prefer anyways etc.

Personally i do so in Notepad++ where i also store notes of ideas of things to add or not for example if i may say anyways etc. I may often not look at it for a long time, and spend bit of time then sorting the ideas and organizing them or not but is very helpful so i would recommend this as well as part or and on top of in this case anyways etc writing commit message notes in a .txt, i'd also recommend writing your ideas in another or same .txt if tidy or readable to you or some similar or as you prefer solution/idea anyways etc.

I started this habit somewhere in this advciv-sas mod development i mean but is very helpful anyways etc, so adding mention of it if helps but anyways etc anyways etc anyways etc.

### full git log with anonymized email in a .txt

Always keep a .txt copy of the full git log of the/your entire project, very useful when doing a global search (for example with VS Code), you can gain while doing so precious information about some features you want to know more about.

You can create such an exhaustive git log automatically in one command, plus also anonymizing the email with a `<hidden>` instead for all authors, as provided to me by chatgpt, for example in git bash for windows, for Steam users (adjust paths and/or such similar things anyways if not steam user) (click on the images below to view them full size):

```cmd
cd "C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS/" && git log --pretty=format:"commit %H%nAuthor: %an <hidden>%nDate:   %ad%n%n%B" --date=iso > git_log_anonymized_email.txt
```

For example for AdvCiv-SAS, i put this file (that i ideally should/try to update every while) in this folder for example [/_0_Common_Docs/git_log_anonymized_email.txt](/_0_Common_Docs/git_log_anonymized_email.txt) (but any place (you want) should do (fine) as long as it is in your mod (anywhere inside it maybe anyways)).

note: it should be possible to create erase in one command the old git log but for now at least anyways etc i prefer to manually copy paste, even though risk is low thanks to git commit versioning and having a github backup or such other files or not anyways etc, still for now doing as such but this command may be optimized/enhanced perhaps rather by having it copy it there directly and overwrite old file, which should be quite safe considering it is a rarely used and not actively written on file only a log if i may say as chatgpt would recommend to me about other topics or files when evaluating safety of a change or/and discuss it suggest it with me in this case i mean but anyways etc if i may say or talking about it with it but anyways etc.

### manual(s) and docs in .txt

Similarly, i have found it very useful to keep a .txt copy of the docs i use, in particular technical ones, and such as the [AdvCiv base docs](/_0_Common_Docs/AdvCiv%20(Base)%20Doc) in particular the [manual in .txt](/_0_Common_Docs/AdvCiv%20(Base)%20Doc/manual.txt)

When doing a global search with VS Code for anything, as long as this manual.txt for example (or other files) are in the mods folders (anywhere, this/her is an example, anyways), then i can and may often (not guaranteed but maybe) also find useful information as part of my global search results.

Not necessarily for all docs, or may if you want, but sure is very convenient, hopefully helpful tip or maybe not but in all cases etc anyways.

#### advciv id changes manual.txt results

note: about the below example, a global search on "HandicapIncrementTurns" directly rather may be more useful (see civ4handicapinfo xml 's code comment(s) for details), but this shows how to navigate if i may say but anyways etc the manual.txt and global search features for example how to use them, may not be the best example but hopefully works-functions-suits quite well here but anyways etc...

VS Code's (for example) global search can be useful in particular but not only, for example, to try to understand what advciv id changes do.

For example while trying to tweak difficulty settings after having added our new script of handicap info display as explained in [README.md#csv-and-md-view-of-the-handicap-difficulties-info-in-a-table-for-all-difficulties-infodata](/README.md#csv-and-md-view-of-the-handicap-difficulties-info-in-a-table-for-all-difficulties-infodata), i was trying, for example in this case but anyways etc, to understand what this unknown (to me at least but anyways etc) `iAIHandicapIncrementTurns` field does, no info in usual websites like kujira or and such anyways etc

Output is as follows for a search on "251" and right click "copy" on the global search results (part of them that are in manual.txt i mean anyways etc):

```log
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_0_Common_Docs\AdvCiv Base Doc\manual.txt
  172,273: To balance out the remaining changes (especially to Free Speech), the threshold for Legendary city culture gets reduced on the low and medium difficulty levels. (On Monarch, the threshold begins to increase, matching the increasing tech costs relevant for Space victory.) 251
  252,229:     • No impact of global research on inflation; instead, adjusted tech costs based on difficulty and the years-per-turn progression for a more historically accurate tech pace, and Immortal and Deity games now start on turn 10. 251, 910
  297,419:     • On Emperor difficulty and above, some of the AI discounts have been reduced, but human civs face increased production costs, research costs, city growth thresholds and Great Person thresholds. The AI also starts with fewer freebies, in particular, without Agriculture on Immortal and Deity and without a second free Settler on Deity. Progres­sive AI bonuses are now based on the game turn instead of the AI era. 251/ 250e
  2243,1: 251 shows the start turn on the Settings tab when it isn't turn 0.
  4821,1: 251, 910: Tech cost adjustments.
  6489,132: Rationale	An extra defender everywhere is a big production sink now that AI production discounts have been reduced (through change 251), especially in the early game. That forum post probably describes an AI enemy in the Classical era; so I could address that situation (to an extent) by adding the extra defender already in the Classical era on Deity. However, I don't really think that this would make the AI more difficult to beat overall as it's not all that often possible to sneak up on the AI through the territory of a third civ that the AI isn't afraid of. It's also a pretty clever stratagem that I don't mind being rewarded a bit. (The reward isn't going to be that great because the conquered cities won't be connected to the player's core territory.)
  6802,10: See also	251 reduces the AI work rate bonuses from the difficulty setting.
  7811,10: See also	251 adjusts the culture level thresholds to the game difficulty level.
  9721,1: 251 increases tech costs for the above-average difficulty levels.
  9913,1: 251 may show the game start turn.
  9980,1: 251: Removes the culture rate modifier that K-Mod adds to Colosseum. And is concerned with the balancing Culture and Space victory.
  10199,221: The AI advantages that are the same for all difficulty settings, namely the discounts on unit supply and upgrade cost, are unaffected by the AI game progress modifier (per-era modifier in BtS, per game turn since change 251).	The per-era modifier increases most of the AI advantages with each passing era. 
  10203,10: See also	251 exempts all AI gold costs from game progress adjustments.
  10221,266: See also	I guess changes to map sizes (137, 165), starting positions (027) and AI behavior have made it considerably more difficult to establish at least four decent cities in the early game. Converting AI worker speed increases into a human worker speed decrease (251) may also have had the (unintended) effect of hampering the early development of human civs more than that of AI civs.
  10224,41: See also	The Deity research rate set by 251 is adjusted to this change.
  10230,1: 251	Pacing adjustments for difficulty levels
  10343,5: See 251 about Marathon culture level thresholds.
  10359,1: 251 uncouples AI unit expenses from the progressive per-era modifier, meaning that AI unit expenses don't depend on the difficulty level in AdvCiv (always halved).
  10449,10: See also	251 shows the game start turn on the Settings tab if it isn't turn 0.
  10556,55: See also	To match the increased production costs that 251 imposes on the civs.
  11371,10: See also	251 increases some expenses for the medium difficulty levels and reduced the number of free wins against Barbarians.
  11854,89: See also	200 reverts the K-Mod changes to Colosseum (25% culture, +20 production cost); 251 lowers the Legendary culture threshold instead.
  11878,10: See also	251 adjusts the AI research speed based on difficulty.
```

While there is some unrelated info of it/about it, some results may also help us also (in (trying to?)?) understand(ing) (but anyways etc) what this 251 id change, or maybe rather for our need specifically if i may say but anyways etc what the `iAIHandicapIncrementTurns` tag/field does, but anyways etc.

One of the main points of this is also to show a manual.txt is much easier to navigate and search on that the .pdf version of it, with VS Code global search or even with a normal text editor or such when simply looking for fast (access but anyways etc) info rather than detailed and nicely displayed one but anyways etc anyways etc anyways etc...

### Sources about XML AI Attributes and their meaning

Please read these docs (highly recommended) if you want to know more about AI attributes:

- [kujira's website](https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/#iclosebordersattitudechange) or for example list of unitAIs [kujira](https://gforestshade.github.io/kujira/post/keyichiran/#%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88) and
[cfc forum with what they do (may be accurate or not anyways)](https://forums.civfanatics.com/threads/list-of-unitais-and-what-they-do.353919/post-8910602), see also [translate to english using web browser trick/technique for/in kujira's website anyways etc](https://github.com/wonderingabout/kujira)
- [modiki civfanatics website](https://modiki.civfanatics.com/index.php/Civ4LeaderHeadInfos) or [modiki's website too](https://modiki.civfanatics.com/index.php/Civ4TraitInfos) for example anyways etc
- [wikidot website for example for bonusinfos](http://civ4.wikidot.com/xml:civ4bonusinfos)

## A few useful other links

- many links in the main README.md first for example maybe indeed or not or yes or and other or and not etc anyways etc... in the [main README.md 's page link](/README.md)
- todo: tutorial on how to compile the DLL and/or files for Advciv (but should not be needed if you only modify XML files if i am not mistaken)
- [Python Class Reference (civ4bug.sourceforge.net)](https://civ4bug.sourceforge.net/PythonAPI/) List of all or many(?) python class detailed info, can be useful for example it helped me implement the Sevopedia religion's (working and finalized at least as of now anyways etc) right panel version of leaders panel, telling [claude AI (see Claude AI's section of the Authors part of the readme.md for details)](/README.md#claude-ai-the-newcomer-hehe-xd-anyways-etc-welcome-anyways-etc) to adjust its code for the `screen.addMultiListControlGFC` to display leaders in a multi line button panel, see Sevopedia religion's code and code coomments for details. I have also made a copy of it (this website's content that is very elpful if i or and maybe others or not or other or etc anwyas etc use it or not anyways etc) here in advciv-sas or the current mod you're using showing this/these doc(s), in the file [civ4bug_sourceforge_net_pythonAPI_AllClasses_html.txt](/_0_Common_Docs/CIV4BUG%20Sourceforge%20net%20All%20Classes%20Doc/civ4bug_sourceforge_net_pythonAPI_AllClasses_html.txt), may help us also for global search (with vs code for example is what we/i i mean use anyways etc  thanks to thosete person(s) who taught me about it anyways etc) if need or and other uses or and not maybe anyways etc.
- inspecting an object, see for example, not sure is best way to do it and i am no expert in it, but i did solve it hehe if i may say but anyways... etc.., just one way i randomly or persistently found that solved the issue of displaying/finding required building method, if it can help you too maybe anyways etc, here it is: `printObjAttrs` in [_sevopedia_debuggers.py](/Assets/Python/Contrib/Sevopedia/_sevopedia_debuggers.py) and [__SevoPediaBuilding-gc-inner-debug-content.txt](/Assets/Python/Contrib/Sevopedia/__SevoPediaBuilding-gc-inner-debug-content.txt) for example, and also [__SevoPediaUnit-gc-inner-debug-content.txt](/Assets/Python/Contrib/Sevopedia/__SevoPediaUnit-gc-inner-debug-content.txt) which helped me adjust Claude AI's (see [Claude AI's part of the authors section of this README.md below for details](/README.md#claude-ai-the-newcomer-hehe-xd-anyways-etc-welcome-anyways-etc) code of the new placeTerrainFeatureCity or similarly named sevopedia unit function/method anyways etc, not using the inaccurate methods Claude AI provided, at least in advciv and advciv-sas by extension since we use same code as in advciv anyways etc, `getHillsAttackPercent()` and `getHillsDefensePercent()` but instead the real at least as appears in our insect of the unitinfo anyways etc as linked just above in same bulelt point if i am not mistaken indeed if i may say anyways etc with `getHillsAttackModifier()` and `getHillsDefenseModifier()` of an otherwise very great code that worked at first try!!! (see also [this screenshot (1) (google drive image link)](https://drive.google.com/file/d/1oE0tG3VjCY7a5ABwlV0MYDhA3ox3Sbe4/view?usp=sharing) and [this screenshot (2) (google drive image link)](https://drive.google.com/file/d/1Yn7dIxzDpuJ2f8wbpXmhn2W0qZ42ADOe/view?usp=sharing) for example of how i solved it if helpful or interesitng or enjyoabel or pelasant or fun or any other else or not or othr or not or yes or and other or and not anyways etc anyways etc anyways etc) And finally shwoed us hills and peaks too so we can expand on it and try to find how to show them in sevoepdia terrain category now :o anyways etc, thanks a lot Claude AI and thanks to me too or and other or and not anways etc , hopefully helpful or not or yes or and other or and not anyways etc anyways etc anyways etc
- todo add links if i have/want(/do) more to add

## In case UnitAIs info from link above is deleted someday, here is a copy here in case, anyways etc

quote from website linked before anyways etc, and adjusted or not or yes or not or yes or and other or and not anyways etc... for AdvCiv-SAS (mod +/- project anyways etc) anyways etc... :

```text
This is based on BBAI, so default BtS may be slightly different:

- UNITAI_ATTACK: General purpose; unit prioritizes joining an attack stack, but also may wander off on search and destroy/explore, sit in a city and defend it, etc.
UNITAI_ATTACK_CITY: Join an attack stack -> If in an attack stack, lead assault on a city once the AI decides the stack should attack a city
- UNITAI_COLLATERAL: Similar to UNITAI_ATTACK_CITY, but may also attack enemy stacks in the field
- UNITAI_PILLAGE: Causes unit to wander off by itself into enemy territory and pillage stuff
- UNITAI_RESERVE: Primary use - Floating defenders to shuffle around between threatened cities. Also is a priority UNITAI type for the AI to change if it needs units of another type (the AI will frequently change reserve units to attack units once it starts warplans, for instance)
- UNITAI_COUNTER: Join an attack stack -> if in stack may leave stack to attack adjacent tiles with enemy units
- UNITAI_CITY_COUNTER: Same as UNITAI_COUNTER, but for cities instead of stacks
- UNITAI_PARADROP: Hold in reserve and drop into enemy territory; very similar to UNITAI_PILLAGE, except units drop deep into enemy territory
- UNITAI_CITY_DEFENSE: Defend a city, never leave the city
- UNITAI_CITY_SPECIAL: Basically the same as UNITAI_CITY_DEFENSE, except the AI deprioritizes this type if a city already has a defender of this AI type, meaning that the AI in unmodded BtS, the AI only ever builds a single machine gun in it's cities
- UNITAI_EXPLORE: Wander around prioritizing terrain that hasn't been revealed until unit is killed
- UNITAI_ATTACK_AIR: Air Unit used for bombing
- UNITAI_CARRIER_AIR: Similar to UNITAI_ATTACK_AIR, but prioritizes filling up carriers
- UNITAI_ATTACK_CITY_LEMMING: beeline enemy cities and Suicide against enemy units
- UNITAI_ICBM: Hold unit, and then launch when at war
- UNITAI_SPY: Basic spy AI (prioritize going into enemy territory and running spy missions - In base BtS this is purely random, with the spys basically wandering around and rolling dice, in BBAI the spys prioritize high value missions and improvements)
- UNITAI_WORKER_SEA: Build sea improvement, if none is available explore
- UNITAI_ATTACK_SEA: Basic sea AI, wander around the oceans in search and destroy mode, join a stack, etc
- UNITAI_RESERVE_SEA: Similar to UNITAI_RESERVE except for sea units
- UNITAI_ESCORT_SEA: Join a stack
- UNITAI_EXPLORE_SEA: Wander around the oceans prioritizing moving into unexplored territory until unit dies
- UNITAI_ASSAULT_SEA: Transport land units for sea assault, launch when a sufficient assault stack is ready; forms core of water domain stacks
- UNITAI_SETTLER_SEA: Ferry settlers and workers over water tiles
- UNITAI_MISSIONARY_SEA: Ferry missionaries over water tiles
- UNITAI_SPY_SEA: Ferry spys over water tiles
- UNITAI_CARRIER_SEA: Be a mobile air base for UNITAI_CARRIER_AIR units
- UNITAI_MISSILE_CARRIER_SEA: similar to UNITAI_CARRIER_SEA but for missiles
- UNITAI_PIRATE_SEA: Wander around pointlessly, sometimes run a blockade if the die roll tells you to and you are in enemy territory

Great people AIs:
- UNITAI_GREAT_PROPHET: Prioritize Building a Shrine and prioritize the religion of which there are the most cities of if multiple shrines can be built; if no shrine can be built, roll dice to decide whether to start a golden age or settle in a high value city (probably the capital)
- UNITAI_GREAT_ARTIST: Not sure what the behavior of this type is actually
- UNITAI_GREAT_SCIENTIST: Build an academy in a high priority city (most likely capital); if no good cities are available for this mission, roll dice to decide whether to settle in a high priority city or start a golden age
- UNITAI_GREAT_GENERAL: Roll dice to decide whether to join a unit or not, if not (most likely scenario), Build a military academy in a high priority city; if no acceptable city is available to build an MA in, join a high priority city (almost always the capital)
- UNITAI_GREAT_MERCHANT: Roll dice to decide if unit should Find best city to conduct trade mission in and do so, or start a golden age, or join a high priority city
- UNITAI_GREAT_ENGINEER: Build an available wonder. If no wonder is available to rush, roll dice to decide whether to start a golden age, or join high priority city



For unit AIs that are correct in the OP, I didn't write anything.
```

## Civ4 ProcessInfos XML info

From: [modiki's website, wayback archive version latest i found anyways etc](https://web.archive.org/web/20230330010924/https://modiki.civfanatics.com/index.php?title=Civ4ProcessInfo) since was/is down the website as of/for now anyways etc

adjusted for advciv-sas or not anyways etc:

```text
Civ4ProcessInfo

The Civ4ProcessInfo file defines what commerce types can be created from production in a city (by default, 100% of production to wealth, research, and culture). This can also be used to create an option to have a city build nothing (by setting all of the commerce types so that no production is applied to them).

All tags must be opened and closed; the first is the "open", the second the "close" tag. If nothing goes inside a "list tag", then it should just be the opening tag with a "/" before the closing bracket. The following tables contain all available tags, as well as their purpose and accepted values.




Contents
1	Tags
1.1	Headers
1.2	Text
1.3	Lists (Multi-line)
1.4	Art
2	Example

Tags

Headers

These tags typically bracket other tags, sometimes the entire file, and are generally used to specify more than one piece of data.

Tag Name						Description
ProcessInfos					This tag surrounds all entries in the file
ProcessInfo						Main bracket for each entry


Text

Tag Name						Description
Type							How the process is referred to in other files
Description						Text for the process in the game
Strategy						Strategy text for the process in the game
TechPrereq						Tech required to build the process in the city


Lists (Multi-line)

All List tags consist of an opening/closing tag, which is shown here, and then each entry within it is another tag with the same name as the parent tag, minus the "s" (i.e. singular, rather than plural).

Tag Name						Description
ProductionToCommerceModifiers	The percent of the city's production applied to each commerce type; top is gold, then research, then culture, then espionage <iProductionToCommerceModifier>100</iProductionToCommerceModifier>



Art

These tags are directly related to the rendering of art for the entry.

Tag Name						Description
Button							The button for the process in the city screen and city production popup


Example

In the following example of code, please note that there is a specific order of all of the tags. You must list the tags in this order for the game to properly interpret your file.

<ProcessInfo>
 <Type>PROCESS_WEALTH</Type>
 <Description>TXT_KEY_PROCESS_WEALTH</Description>
 <Strategy>TXT_KEY_PROCESS_WEALTH_STRATEGY</Strategy>
 <TechPrereq>TECH_CURRENCY</TechPrereq>
 <ProductionToCommerceModifiers>
  <iProductionToCommerceModifier>100</iProductionToCommerceModifier>
  <iProductionToCommerceModifier>0</iProductionToCommerceModifier>
  <iProductionToCommerceModifier>0</iProductionToCommerceModifier>
 </ProductionToCommerceModifiers>
 <Button>Art/Interface/Buttons/Process/ProcessWealth.dds</Button>
</ProcessInfo>
```

## Copy of the tutorial on how to modify GameFonts.tga for FREE

Note: you may want to read all this at least the end before you start doing it, in case you see something that makes you change your mind/choose another approach instead, but do as you prefer anyways etc.

Source: [CFC forum link](https://forums.civfanatics.com/threads/how-to-modify-gamefonts-tga-for-free.181119/)

In case it is deleted, i have made a copy here which is as follows adjsuted or not or and other or and not anyways etc for AdvCiv-SAS (formatting the github readme or and other or and not anyways etc):

```text
Tutorial: Editing GameFonts.tga for Free


- BEFORE YOU START: Get the image(s) you want to add to the file.
- Because I am really cheap, I usually hunt Google Images for what I want and then use IrfanView to resize and edit it. I then paste it into GIMP to save as a DDS file. (I am mystified by GIMP&#8217;s user interface and use it for as little as possible.)
- Get a copy of DTXBmp; install it.
- Go to the GameFonts.tga file you want to edit in File Manager. With the right mouse button, select "Open With" DTXBmp
- You should get a screen that looks like this&#8230; DTXBmpScreenShot2.jpg
- Click on the third icon from the left on the bottom; floating help identifies it as "send to editor".
- The Windows Paint application will pop up with the main icon screen, using filename &#8216;norm.bmp&#8217;. At this point, I like to maximize that window and View->Zoom->Custom->200%
- Pull up the image you want to add. Resize it to be 21 pixels wide by 20 pixels high. Hit Edit->Copy to put it on the clipboard. (Again, I like IrfanView for this purpose.)
- Go over the Paint application and hit Edit->Paste. Then drag it to the next available empty spot of the type you want to use. In my case, I put it after the religion icons. If you are adding a resource, put it after the resource icons. You should be able to enclose your new bitmap within the purple gridlines so that all the lines still show. Click somewhere else in Paint to leave your image there permanently.
- Put the crosshair cursor right at the point where you pasted your picture. The lower right corner of Paint will show the coordinates. Write these down somewhere.
- Notice that all the existing icons in the file have a single green pixel after each icon. I have no idea what this is for, but according to rumor it might be important. So, go to one of the purple gridlines that has it, grab a 3x20 section containing the line, Edit->Copy and then Edit->Paste as once for each icon. You should be able to do this by eye. (Zoom helps!)
- Hit File->Save. (I hope you are still with me because all this has been the EASY part!)
- Go back to DTXBmp and hit the fourth icon from the left on bottom. "Refresh From Edit". The colored image in the center should now reflect your changes. [DO NOT CLOSE THE PAINT APP YET&#8212;you might still want it.]
- Now, go over to the right side where there is a black square with white icons on it. This is the infamous alpha channel part of your tga file. Hit the second icon from the left under it. "Send to Editor".
- [*]Another Paint application will pop up with the filename &#8216;trans.bmp&#8217;. I maximize and zoom here.
- Now, take a look over the white icons and pick the one that is closest to your new image. This will usually be one of the big round ones or the square one for Confucianism. Select a 21x20 area around it. Hit Edit->Copy.
- Now hit Edit->Paste. Move the pasted section to the coordinates that you wrote down in step #8. Click somewhere else in Paint to leave your image there permanently.
- Hit File->Save.
- Go back to DTXBmp. Under the black rectangle, hit the third icon from the left, "Refresh after Edit". Now both the colored image and the alpha channel should reflect your changes.
- In DTXBmp, hit File->Save.
- You are done. Close all the windows.
- Exclaim "What a hassle that was!"
- Reach over and smack your friend who is a graphics expert and is laughing hysterically at you by now. Remind him that you did this for FREE!

The same process will work for GameFonts_75.tga, except that the size of each icon is 16x16 and the size of the bar with the green pixel is 3x16. I have never succeeded in converting GameFonts.tga by resizing it; I have always had to do the whole thing twice.

- I played around with trying to generate the alpha channel by taking the original image and converting it to black & white and then taking the negative. - All of these efforts resulted in abyssmal failure. Cutting and pasting from the real alpha channel is all I could get to work.


Free Windows Applications Mentioned in this Tutorial
- DTXBmp may be found at http://fly.to/mwgfx/
- Irfanview may be found at http://www.irfanview.com/
- GIMP may be found at http://gimp-win.sourceforge.net/stable.html. (You need both the runtime environment and the application.)

Cheers,
Eusebius
```

I am not responsible if it is not updated anymore or inaccurate, but i hope it can be helpful hopefully or maybe not (is not helpful anyways etc) but in all cases is what i wanted to do (to write it here) anyways etc anyways etc anyways etc.

Note: it may be much easier, especially if you import art assets from a mod, to also import the icons from the .tga of a mod, see some screenshots in the google drive link above (about this .tga part) where i show for example the difference between our (current) .tga files (in particular the GameFont.tga and GameFont_75.tga files here in this example anyways etc) (before fixing/updating the icons) and HR mod's .tga files (same i.e. GameFont.tga and GameFont_75.tga files anyways etc anyways etc anyways etc) anyways etc, but i find it also interesting even if painful to know how to do, it may be/serve helpful/us especially if you/we want to add your/our own assets that don't exist in any mod for example, but (this) is just a suggestion do as you prefer anyways etc.

Note 2: This seems to be useful when reordering or/and adding/removing xml assets that depend on/use icons in the .tga file if i am not mistaken anyways etc, i don't know how it all works, but it seems that generally for example for religion assets, after having [reordered the xml order (for example in this git commit anyways etc)](https://github.com/wonderingabout/AdvCiv-SAS/commit/025c696fac3f43dd2b2489d99f36fae3f407ecb4), now the icons are all messed up (paganism religion shows with the judaism icon and or other changes anyways etc, see for example screenshots 5085 and 5086), so the .tga icons's order seems to also need to reflect the xml order or vice versa, and similarly for the _75.tga file if i am not mistaken too do all these steps again for more fun if i may say or not as is more tedious but more accurate hopefully this way unless i am mistaken and there is somehow or could be a better way i don't know of maybe, else hopefully more accurate this way or whichever or not whichever way it may/would be, anyways etc anyways etc anyways etc, again i don't know exactly how it all works but i think this is the general idea and that it works helps quite good maybe or not or yes or and other or and not anyways etc hopefully helpful or not or yes or etc or and other or and not anyways etc.

Note 3: you may want to make backups to avoid overwriting accidentally the wrong file or such or not having a backup of the file needed anyways etc anyways etc anyways etc...

## ICONS code XML names (may or not be exhaustive anyways etc) (with some color changing code as bonus or to be extra exhaustive a bit more than needed but is here if needed maybe anyways etc)

from: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvDllTranslator.cpp`

As follows:

```cpp
#include "CvGameCoreDLL.h"
#include "CvDllTranslator.h"
#include "CvGame.h"
#include "CvPlayer.h"

void CvDllTranslator::initializeTags(CvWString& szTagStartIcon, CvWString& szTagStartOur, CvWString& szTagStartCT, CvWString& szTagStartColor, CvWString& szTagStartLink, CvWString& szTagEndLink, CvWString& szEndLinkReplacement, std::map<std::wstring, CvWString>& aIconMap, std::map<std::wstring, CvWString>& aColorMap)
{
	szTagStartIcon = L"[ICON_";
	szTagStartOur = L"[OUR_";
	szTagStartCT = L"[CT_";
	szTagStartColor = L"[COLOR_";
	szTagStartLink = L"[LINK";
	szTagEndLink = L"[\\LINK";
	szEndLinkReplacement = L"</link>";

	//create icons map
	aIconMap[L"[ICON_BULLET]"] = std::wstring(1, (wchar)gDLL->getSymbolID(BULLET_CHAR));
	aIconMap[L"[ICON_HAPPY]"] = std::wstring(1, (wchar)gDLL->getSymbolID(HAPPY_CHAR));
	aIconMap[L"[ICON_UNHAPPY]"] = std::wstring(1, (wchar)gDLL->getSymbolID(UNHAPPY_CHAR));
	aIconMap[L"[ICON_HEALTHY]"] = std::wstring(1, (wchar)gDLL->getSymbolID(HEALTHY_CHAR));
	aIconMap[L"[ICON_UNHEALTHY]"] = std::wstring(1, (wchar)gDLL->getSymbolID(UNHEALTHY_CHAR));
	aIconMap[L"[ICON_STRENGTH]"] = std::wstring(1, (wchar)gDLL->getSymbolID(STRENGTH_CHAR));
	aIconMap[L"[ICON_MOVES]"] = std::wstring(1, (wchar)gDLL->getSymbolID(MOVES_CHAR));
	aIconMap[L"[ICON_RELIGION]"] = std::wstring(1, (wchar)gDLL->getSymbolID(RELIGION_CHAR));
	aIconMap[L"[ICON_STAR]"] = std::wstring(1, (wchar)gDLL->getSymbolID(STAR_CHAR));
	aIconMap[L"[ICON_SILVER_STAR]"] = std::wstring(1, (wchar)gDLL->getSymbolID(SILVER_STAR_CHAR));
	aIconMap[L"[ICON_TRADE]"] = std::wstring(1, (wchar)gDLL->getSymbolID(TRADE_CHAR));
	aIconMap[L"[ICON_DEFENSE]"] = std::wstring(1, (wchar)gDLL->getSymbolID(DEFENSE_CHAR));
	aIconMap[L"[ICON_GREATPEOPLE]"] = std::wstring(1, (wchar)gDLL->getSymbolID(GREAT_PEOPLE_CHAR));
	aIconMap[L"[ICON_BAD_GOLD]"] = std::wstring(1, (wchar)gDLL->getSymbolID(BAD_GOLD_CHAR));
	aIconMap[L"[ICON_BAD_FOOD]"] = std::wstring(1, (wchar)gDLL->getSymbolID(BAD_FOOD_CHAR));
	aIconMap[L"[ICON_EATENFOOD]"] = std::wstring(1, (wchar)gDLL->getSymbolID(EATEN_FOOD_CHAR));
	aIconMap[L"[ICON_GOLDENAGE]"] = std::wstring(1, (wchar)gDLL->getSymbolID(GOLDEN_AGE_CHAR));
	aIconMap[L"[ICON_ANGRYPOP]"] = std::wstring(1, (wchar)gDLL->getSymbolID(ANGRY_POP_CHAR));
	aIconMap[L"[ICON_OPENBORDERS]"] = std::wstring(1, (wchar)gDLL->getSymbolID(OPEN_BORDERS_CHAR));
	aIconMap[L"[ICON_DEFENSIVEPACT]"] = std::wstring(1, (wchar)gDLL->getSymbolID(DEFENSIVE_PACT_CHAR));
	aIconMap[L"[ICON_MAP]"] = std::wstring(1, (wchar)gDLL->getSymbolID(MAP_CHAR));
	aIconMap[L"[ICON_OCCUPATION]"] = std::wstring(1, (wchar)gDLL->getSymbolID(OCCUPATION_CHAR));
	aIconMap[L"[ICON_POWER]"] = std::wstring(1, (wchar)gDLL->getSymbolID(POWER_CHAR));

	aIconMap[L"[ICON_GOLD]"] = std::wstring(1, (wchar)GC.getInfo(COMMERCE_GOLD).getChar());
	aIconMap[L"[ICON_RESEARCH]"] = std::wstring(1, (wchar)GC.getInfo(COMMERCE_RESEARCH).getChar());
	aIconMap[L"[ICON_CULTURE]"] = std::wstring(1, (wchar)GC.getInfo(COMMERCE_CULTURE).getChar());
	aIconMap[L"[ICON_ESPIONAGE]"] = std::wstring(1, (wchar)GC.getInfo(COMMERCE_ESPIONAGE).getChar());

	aIconMap[L"[ICON_FOOD]"] = std::wstring(1, (wchar)GC.getInfo(YIELD_FOOD).getChar());
	aIconMap[L"[ICON_PRODUCTION]"] = std::wstring(1, (wchar)GC.getInfo(YIELD_PRODUCTION).getChar());
	aIconMap[L"[ICON_COMMERCE]"] = std::wstring(1, (wchar)GC.getInfo(YIELD_COMMERCE).getChar());
	// advc.064:
	aIconMap[L"[ICON_CITIZEN]"] = std::wstring(1, (wchar)gDLL->getSymbolID(CITIZEN_CHAR));
	// <advc.002f>
	aIconMap[L"[ICON_GREATGENERAL]"] = std::wstring(1, (wchar)gDLL->getSymbolID(GREAT_GENERAL_CHAR));
	aIconMap[L"[ICON_AIRPORT]"] = std::wstring(1, (wchar)gDLL->getSymbolID(AIRPORT_CHAR));
	// </advc.002f>
	//create color map
	aColorMap[L"[COLOR_REVERT]"] = CvWString(L"</color>");
	for(int i=0; i < GC.getNumColorInfos(); i++)
	{
		const NiColorA& color = GC.getInfo((ColorTypes) i).getColor();
		CvWString colorType(GC.getInfo((ColorTypes) i).getType());
		CvWString wideColorType;
		wideColorType.Format(L"[%s]", colorType.GetCString());
		CvWString colorOut;
		colorOut.Format(L"<color=%i,%i,%i,%i>", (int) (color.r * 255), (int) (color.g * 255), (int) (color.b * 255), (int) (color.a * 255));
		aColorMap[wideColorType.GetCString()] = colorOut;
	}
}
```

Anyways etc... (Anyways etc anyways etc...)

## Insert an img in a text label in sevopedia

Code sample provided by Claude AI in one of my prompts to add YieldChanges to placeStats in sevopedia building, but the code sample surprisingly and happily if i may say but anyways etc, or maybe rather plesantly or both or not but anyways etc works, so sharing it in case it helps others or me who rereads it or and need or want to reuse it some day, or not, or etc, but anyways etc.

Output looks like this for example: [(google drive folder screenshots link)](https://drive.google.com/drive/folders/1ZY8gTziXBsHoCjjxYRJ4DoJwTf5VHvsy?usp=sharing)

note: modified button path in code below to a button path known to exist in base advciv (civ4 too?), for example the jewish temple

```python
			# <!-- custom: 2.1: Yield Modifiers (Food +x%, Production +x%, Commerce +x%) with power breakdown -->
			for k in range(YieldTypes.NUM_YIELD_TYPES):
				iYieldModifier = buildingInfo.getYieldModifier(k)
				iPowerYieldModifier = buildingInfo.getPowerYieldModifier(k)
				
				# Total modifier (regular + power)
				iTotalYieldModifier = iYieldModifier + iPowerYieldModifier
				
				if (iTotalYieldModifier != 0):
					szText1 = ""
					
					# Base modifier part
					if (iYieldModifier != 0):
						if (iYieldModifier > 0):
							szSign = "+"
						else:
							szSign = ""
						szText1 = szSign + str(iYieldModifier) + "%"
					
					# Power modifier part (optional, only if exists)
					if (iPowerYieldModifier != 0):
						if (len(szText1) > 0):
							szText1 += ", and "
						if (iPowerYieldModifier > 0):
							szPowerSign = "+"
						else:
							szPowerSign = ""
						szText1 += szPowerSign + str(iPowerYieldModifier) + "% with "
						
						# Add power button (using fictional path - replace with actual if found)
						szPowerButton = u"<img=Art/Interface/Buttons/Buildings/Temple_Jewish.dds size=16></img>"
						szText1 += szPowerButton
					
					szText2 = u"%c  %s" % (gc.getYieldInfo(k).getChar(), szText1)
					fillCell(screen, szText2, x, y)
					x, y, rowItemId = getNextItemCoordinates(x, y, rowItemId, columnWidth)
```

note 2: i have tested with a .jpg (source [Stonehedge wallpaper from https://www.wallpaperflare.com/ Current photo size: 4272 x 2848 px • Resolution:4K)](https://www.wallpaperflare.com/stonehenge-england-stone-henge-united-kingdom-grass-sky-wallpaper-ahjky/download) (drives me to quite nostalgic times, even though is in the past now, but anyways etc...) (`szPowerButton = u"<img=Art/AdvCiv_SAS/Wallpapers/Stonehedge/test.dds size=16></img>"`), also appended in the drive folder, but display doesn't work, however converting it to .dds (DXT1 with Paint.NET for example, full resolution) is now displayed accurately and successfully (.dds also appended in drive link mentionned above anyways etc))

In the note 2 example but anyways etc, increasing size to for example 1024 also works, we get a very nice sevopedia background image hehe if i may say but anyways etc, i suspect using a lower resolution base image, perhaps 1080p, or 1440p may produce even better results (less pixelated one (based on the  [past .dds experiment/experience](/README.md#dds-button-size-comparison-analysis) where optimal size seemed to be a bit higher than max icon_size (256px on a 164px if i remember correctly and am not mistaken but anyways etc, so maybe here a 1440p native image may work best? But not sure and would need to test, and in all cases, (but) anyways etc) but anyways etc), perhaps using another DXT conversion too or not, but anyways etc)

note 3: atlas linking buttons such as `szPowerButton = u"<img=,Art/Interface/Buttons/TechTree/Physics.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,1,15 size=32></img>"` (as part of changing tech_physics 's button as part of our tech rework in advciv-sas but anyways etc...) also seems to work quite well, we see the button successfully even though a bit excentered if that is a word in english (not centered around the text), but hopefully good enough but anyways etc at least as proof of concept further if i may say but anyways etc, see the great person button code in place Stats of sevopedia building as well for a cleaner or rather more centered implementation, is just to show/test how it successfully works here but anyways etc ; also for our needs this seems to work very well (whoaaa!!!! If i may say indeed too, but anyways etc...), see screenshot(s) in drive link above for details anyways etc

See also [Assets/XML/Text/AdvCiv-SAS_ImagesAsButtons.xml](/Assets/XML/Text/AdvCiv-SAS_ImagesAsButtons.xml) for details or and other or and not or yes or and other or etc anyways etc, see also also [/Assets/XML/Text/AdvCiv-SAS_Button_Paths_Hardcoded.xml](/Assets/XML/Text/AdvCiv-SAS_Button_Paths_Hardcoded.xml) for extra details or/and adidtional or and alternative or and related or and other or and not or etc but anyways etc information or not or yes or and other or and not but anyways etc anyways etc anyways etc.

note 4: we later also used these/this approach for/to use images as buttons in our sevopedia leader's ai personality panel category headers, with the revived chatgpt's inputs as well, reusing old emojis in our code it provided to me kindly and perhaps enthusiastically if i am not projecting or doing self publicity but anyways etc.. hehe or not or eys or etc or both or none or other or not but anyways etc, is what i want or maybe rather like to do or not but anyways etc, see screenshot 5846 in same google drive link linked above in this section for an example or ingame in sevopedia leader if we still use them now anyways etc

## Import a nif art asset from another mod (example with how we added the impluvium's nif as an import from FFH2 mod's Adventurer's guild building anyways etc)

See steps in screenshots in [this google drive folder (impluvium imported as nif)](https://drive.google.com/drive/folders/1Hx-bvRy7joM54S0Vnmva6HX1h8ZZ-LAh?usp=sharing) anyways etc

In this example the nif was in a .fpk, but i assume it would work similarly if files were scattered in a folder raw if i may say but anyways etc...

Be careful to import all nif related files in the same folder in your mod (or in advciv-sas in this example anyways etc), i am not too technical nor knowledgeable about these but it seems to work/function well for this nif import, hopefully this is helpful too for those who want to try it or not or maybe is helpful or not or yes or etc or and other or and not but anyways etc anyways etc anyways etc...

Note: be careful, in some mods/cases anyways etc the assets such as nif may be scattered across several different fkps, like in ri mod smokehouse1 's nif, scattered accross RI_37_Structures2.FPK (iroquoislh.nif and asian_building.dds) and RI_37_Structures9.FPK (asian_building_shadow.dds) so need to gather them all in one folder if not doing an FPK approach (we don't do FPKs in AdvCiv-SAS at least as of now, anyways etc, see screenshots in the drive link above for details/example anyways etc), in such cases, i would recommend rather to use PakBuild, see [README.md#some-useful-tools-while-doing-this](/README.md#some-useful-tools-while-doing-this) explanation and drive link at PakBuild there for details ; note 2 about this anyways etc: in some mods like c2c for example anyways etc, unpacking in a fodler where you unpacked before seems to create some elements to be missing, 13 by unpacking all fpks in same folder one by one vs 17 files by doing it manually with dragon unpacker, adjust as you see fit the note in this paragraph anyways etc

note 2: sometimes the .kfm is base civ4 for example of the of arabian old camel archer anyways etc so can't find it in the ri mod anyways etc, a hint to that may be if a ctrl+f of the fielname for example "ArabiaCamelArcher.kfm" with one result in our art assets xml before we added it from another mod in the xml, or 2+ results after adding the .kfm in xml too (before finding the actual .kfm file in the mod, then it i very likely the .kfm is a base civ4 file and thus can't be found in any mod unless they especially copy it again in exact same path or path specified which there should be no strong reason to do ince the file already exists ni base civ4 if i am not mistaken anyways etc), so in short if can't find the .kfm or maybe perhaps even the .nif in the mod, in any .fpk or such mod files too perhaps, then maybe the file is a base civ4 oen so just leave path as it is without changing path to your mod specific paths, for example for the camel archer `Art/Units/Unique/Arabia/CamelArcher/ArabiaCamelArcher.kfm` (default keep as is anyways etc) not `Art/AdvCiv_SAS/Units/Camel_Archer/nif/ArabiaCamelArcher.kfm` while desperately trying to find a file that maybe doesn't exist, but many assets have their own ;kfm though so make sure to search too, but generally they should be in path specified in one of the .fpks of the mod or raw path if they don't use fpk for this asset, hopefully helpful, if still no luck try to find the asset in another mod perhaps, hopefully i found the trick before ditching the ri mod files i had already downloaded, so all works in this case i mean but anyways etc, hopefully helpful but anyways etc anyways etc anyways etc...

Like this for example if it helps too, anyways etc... (not sayin this is a standard or ideal to follow, but free or fine maybe to do just i don't know if is best practice or such, but since it works-functions you may use freely this template, evn if it didn't work btw maybe but anyways etc, regardless in all cases here is an example that hopefully or/and maybe helps but in all cases anyways etc...)

```xml
			<NIF>Art/AdvCiv_SAS/Units/Camel_Archer/nif/BerberCamelRiderFinalFinal.nif</NIF>
			<KFM>Art/Units/Unique/Arabia/CamelArcher/ArabiaCamelArcher.kfm</KFM>
			<SHADERNIF>Art/AdvCiv_SAS/Units/Camel_Archer/nif/BerberCamelRiderFinalFinal_fx.nif</SHADERNIF>
```

note3: in some cases it's even harder than that as the nif expects some assets not in the other mod where you're importing it from's folder anyways etc, so with nifskope (see screenshots in drive link in this section of the readme anyways etc), for example for the usa_patriot of/in advciv-sas anyways etc, open the trees and such until you find one or many of the assets the nif requires, in this case it was just brownbesstexture.dds, that was not in ri mod's li_fus_early_america if i am not mistaken anyways etc where the remaining and what i expected to be all but anyways etc unit's art were. So to solve this, i did a search with dragon unpacker in the .fpk of civilization america where i took this unit from, and luckily for us anyways etc this brownbesstexture.dds was there, so i extracted, added it, verified path in nif is relative to current folder as was and not in some other folder parent or child anyways etc to ours, and since all was good by adding this .dds as well in Mods\AdvCiv-SAS\Assets\Art\AdvCiv_SAS\Units\USA_Patriot\nif\ then finally the gun was not purple again of missing art but was the real gun same as in ri mod yohoo!! If i may say but anyways etc. Since it was not luckily too hard to solve unlike harder times i had for example with c2c camel units with many missing assets or and with a path outside of the unit's folder if i remember correctly, i thought it was a good time to add this example to the tutorial since easier and such and i could solve it, while also remembering chatgpt's instructions at the time for c2c even though i didn't succeed at it at the time now solved with the usa patriot that has a nice brown gun in the game (or white in nifskope as in empty if i am not mistaken in this case but anyways etc) i mean but anyways etc anyways etc anyways etc... hopefully helpful, see drive screenshots as well for examples of how i solved it in main steps hopefully helpful anyways etc

## (Old/Deprecated) Example of how to add a static image file (such as .PNG, .JPG, etc) as a leader portrait

Old information from my notes, now we use leader portraits (nif) with an animation, but an earlier version used static images if i may say and am not mistaken in saying so but anyways etc. But these instructions may be helpful to me or others maybe so adding them for reference anyways etc.

Note: if you want to add leaders or other kinds of button art assets or such, below instructions aim to help at that even though they may not be 100% accurate or best practive, but may be maybe or not anyways etc ; however it should also be noted if i may say i mean anyways that it may be easier to rather import existing art assets from many mods, but if you want to import your own manual art asset, perhaps as static images .dds files, this is how i do it, not guaranteed is best way to do it, may or may not be, but it worked and hopefully helpful enough if you want to do so, otherwise i would recommend in general or all cases to maybe import directy already refined art assets from other mods, but as you prefer and wish and is below as i did too if i may say but anyways etc anyways etc anyways etc and as you are free to do or wis to do or not anyways etc...

Leader dimensions obtained using Paint.NET manual selection (approximately but should be quite precise but not guaranteed may or not anyways) on a 4K screen windowed mode.

First, AdvCiv (+/- / AdvCiv-SAS at least for now) base art dimensions:

- in sevopedia (before my fix): 421 x 488 	(ratio: 0,8627)    ;    (reverse-ratio: 1,1591)
- ingame diplomacy: 709 x 866 				(ratio: 0,8187)    ;    (reverse-ratio: 1,1214)

Secondly, Realism invictus, used as reference:

- in sevopedia: 510 x 620     (ratio: 0,8226)    ;    (reverse-ratio: 1,2157)
- ingame diplomacy: 708 x 866 (ratio: 0,8175)    ;    (reverse-ratio: 1,2231)

Thirdly, example of use (not guaranteed to be accurate, may or not be, may help or not, i hope though so but not guaranteed, may or not, anyways, ):

Kingdom of Benin:

- image: 900 x 610 (.PNG)
- it is landscape, so convert=crop here to portrait, reduce to 610 x 610 then think (is closer to portrait), using Paint.NET, image: 610 x 610

- convert to civ4 ratio: converted image = 610 x ? (no need to reduce, 610 < 866 of AdvCiv diplomacy, even if wasn't, is maybe not necessary for higher quality? But since we don't have this problem here, just continue)

- reduce to civ4 dimension (maintain ratio):

? / 610 = 709 / 866

=>

? = 709 / 866 * 610

=>

? = 499,41

=>

? = 499

=>

image: 499 x 610

- crop to this selection size (of 499 x 610) in this example, using Paint.NET for this image (note: this respects image ratio as in advciv diplomacy ingame)

- after it is cropped to 499 x 610, now resize image using Paint.NET to ? x 512 (Let Paint.NET autofill values and choose to maintain aspect ratio). In this example Paint.NET did it to 419 x 512

- after it is resized, now resize again but to 512 x 512 (without maintaining aspect ratio), using Paint.NET

(note: I think it is the same technique or similar in Realism Invictus, as their .dds files are enlarged in display, but ingame they seem to have a fine ratio.)

(note 2: it is also Realism Invictus who gave me indirectly the idea to do this non ratio (2nd) resize, now my image as theirs do not maintain aspect ratio)

- finally, save the image as a .dds file using Paint.NET still (for example (anyways etc) anyways etc), (may use for example maybeDXT1 with mip maps (Bicubic) and keep gamma correction enabled, or DXT5 with mip maps (not tried so far todo or not, anyways, ) for example if you need/use transparency (i don't know a lot about this, is according to ChatGPT's info, which seems accurate about this at least, anyways, ) and i don't know if gamma would be needed or best desired here too maybe, refer to ChatGPT or maybe other specialized places/sources if you want a more specific or/and detailed or/and accurate info maybe anyways etc)

- ingame check result, in my case looks very nice or as nice as could i think with starting image, displays well in (ingame) sevopedia leader view and ingame diplomacy

This is just an example, adapt as you see fit

## (Old/Deprecated) Example of how to create a leader head .dds button from a static image file (such as .PNG, .JPG, etc) (ideally from the leader head image portrait if any, if i am not mistaken but if i may say anyways etc anyways etc anyways etc)

Old information from my notes, as we now we use leader portraits (nif) with an animation, and while doing so also imported the corresponding .dds button that the mod where we imported the .nif animation and such from also had (this .dds button i mean but anyways etc), so we don't make leader .dds buttons from our own leader static images anymore as of now at least in advciv-sas but anyways etc, but an earlier version used static images if i may say and am not mistaken in saying so but anyways etc. But these instructions may be helpful to me or others maybe so adding them for reference anyways etc.

Fourthly, then for the leaderhead button (mini icon of the leader in the sevopedia if i am not mistaken), since now the final dimension displayed is no longer a portrait (no 256 x 512 stretched to 512 x 512 if am not mistaken, so we can directly crop select at 64 x 64 for such a button (leader icon anyways etc without any resize (stretching or compression of ratio or anythign that alters ratio this time if i am not mistaken anyways etc )) from the native image if i am not mistaken (for example .png, any size should do fine too so ideally take the original image if you sitll have it, else maybe the .dds (unstretched)) should maybe do fine anyways if i am not mistaken anyways etc)

So for example you can first make a 96 x 96 crop selection around his head with Paint.NET, then fine tune it (i.e. redo a crop selection on this 96 x 96 (for example .png maybe anyways etc image) to 64 x 64 in a similar manner to the area you prefer to appear in the leader's final icon/button), and save it as a different file for example Ogiso_Igodo_button.dds.

Note: if at 64x64 your leader head is too big or maybe too small, you may try instead to make a bigger selection of say for example 96 x 96 or maybe even 128 x 128 (or any number inbetwwen like 105 x 105, 99 x 99, etc should maybe work too? (to try i didn't but if you want to try it anyways etc)) and then resize it to 64x64, this way leader head would be smaller relatively to the 64 x 64 button.

Then regenerate the .dds in a similar manner than for the full portrait, but no restretching from say 256x512 to 512x512 since 64x64 is alreayd square so just pick same format maybe or/and other and should maybe be good (check to be sure myinfo/thought/feel/intutiion about it is accurate or not anwyays etc)

And finally implement it (the .dds anyways etc) in XML, looks very very good, at least for me i think, anyways, may or not do further beautification or not such as rounded edges or other things or not, but more than good enough for my purpose and i do what i want if i want or not anyways, hope this helps or not maybe doesn't, but wanted to send/write this as well, may serve me to reference it later again, or
someone else or other purpose, anyways,

(note: again check all this to make sure my intution or if no or/and such is accurate or/and updated, hopefully helpful, anyways etc)

## Example of DLL modification of CvGameTextMgr.cpp and other related file(s) to add the new "This technology cannot be traded" flag in sevopedia tech 's placeSpecial and in tech tree view (technology advisor) anyways etc

See screenshots of how this was implemented (not fully exhaustive but hopefully quite a bit exhaustive enough if i may say but anyways etc anyways etc anyways etc) in this [google drive folder](https://drive.google.com/drive/folders/176fGLxIWwOTRYAjafi2OGhe8VuVBZLMT?usp=sharing)

Small sample below /example too but anyways etc:

![0.50_no_tech_trading_example (1).JPG](/_1_AdvCiv-SAS/Images_In_General/misc_0.x/0.50_no_tech_trading_example%20(1).JPG)
![0.710_sevopedia_techs_sample.JPG](/_1_AdvCiv-SAS/Images_In_General/sevopedia_reworks/0.710_sevopedia_techs_sample.JPG)

This was done by adding a new `buildBTradeString` function if i am not mistaken in (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvGameTextMgr.cpp and (adjust to your mod path too anyways etc anyways etc anyways etc) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvGameTextMgr.h

And with the big help or/and support for ideas i found myself too of chatgpt as usual or not usual or usual but in all cases anyways etc...

Since i didn't know how to do it, what helped me if i may say but anyways etc, with past CvGameTextMgr.cpp modifying experiences if i may say but anyways etc i successfully did such as for the power clean/dirty messages, or removing terrain modifiers since they are shown as buttons for clarity in sevopedia unit but anyways etc 's experiences in mind, was to search for one message that is displayed seemingly specifically in sevopedia tech's placeSpecial.

But before that, i also had the idea to make sure the bTrade or something similar related to "trade" or "trad" (ctrl+f) exists in sevopedia tech for example's in gc tech info by inspecting the gc tech info as in [__SevoPediaTech-gc-inner-debug-content.txt](/Assets/Python/Contrib/Sevopedia/__SevoPediaTech-gc-inner-debug-content.txt). While not directly useful, it still helps to know. The info is in `.isTrade()` if i am not mistaken method but anyways etc. I thought at first to hardcode it in placeSpecial's code, but that would be a bit ugly and not cover the tech advisor case where i wanted to show it there while not knowing how. I asked chatgpt and it suggested me indeed this sevopedia tech approach among other several ideas. But then i also had the idea as it suggested too but in another way anyways etc to modify/check more the .cpp anyways etc.

So back to CvGameTextMgr.cpp anyways etc, i found this "Enables Bridge Building" if i am not mistaken but anyways etc.

Then i could search which TXT_KEY uses this, and it is only once and specifically in CvGameTextMgr.cpp.

So by mirroring the functionning of it, but with the new `<bTrade>` (see [kujira's website bTrade info for details anyways etc](https://gforestshade.github.io/kujira/post/civ4techinfos/#btrade) (translate to english with google chrome or your web browser or such or similar but anyways etc) or and some similar or not website or not or yes tat has the info or not or yes or etc but anyways etc for details or and other examples or not but anyways etc)

For example kujira's website says this (translated as such as explained before in previous paragraph/sentence just above if i am not mistaken too as of now in case paragraph(s)'s/sentence(s)'s order changed or maybe it didnt but anyways etc anyways etc anyways etc) provided for convenience too if doesn't bother too maybe but anyways etc... hopefully maybe helps too but maybe doesn't or does or not or yes or other or and etc but anyways etc:

```text
Sets whether this technology is tradable.
If you set this to 1, this technology will be tradable in diplomatic trades.
In BtS, this applies to all technologies except future technologies 1.

Value: 0 or 1

Example:
<bTrade>1</bTrade>
```

So then with the big help of chatgpt and my own ideas too and digging, but and also its support as i may have as well given up on it soon if not for its persistence and encouragement, and finally before i did it just worked luckily, so i am glad this feature (display bTrade info in sevopedia tech and in tech advisor but anyways etc) is in the game now if i may say but anyways etc.

I also modified related files to the .cpp file(s), such as .h file(s) (see screenshots for details as i didn't recheck since then hence the plural singular but from my memory they should only be a very few/low number of files but adding this to be safe and cause bit lazy if i may say to recheck but hopefully helpful or not or yes or etc or and other or and not but anyways etc...).

After all done, recompile the DLL, fix errors if any such as i had forgotten to add the .h (header? After checking it seems to be this too indeede but anyways etc...) but anyways etc during compile, then again recompile (no fastdep as they seem to cause errors as well sometimes) cleanly (ideally todo add tutorial on how to compile DLL for civ4 advciv at least as i had intended to but not sure, i would, however ideally i would greatly want to do so but anyways etc but not guaranteed may or may not do as sad as is or is not but in all cases is maybe as is or not or yes or not or other or etc but in all cases anyways etc), delete the old DLL rather than overwrite, in case we need to revert to old DLL or such, we have it as backup rather than it being lost if we simply copy pasted and overwrote old DLL but anyways etc

What is very nice is that this same code change also displays it in tech advisor (tech tree view, F6 key ingame if i am not mistaken but anyways etc) which i also wanted to do and didn't know how, so this is also my first successful modification of the ingame behaviour of the tech tree view (minus the iGridX and iGridY i did before as well as part of modding but anyways etc)

This bTrade feature being displayed in placeSpecial should ideally have been part of civ4, so i hope players can now see this info if some techs use it (even though it seems in civ4 only future tech uses it, some mods seem to use it for several techs such as middle-earth mod if i am not mistaken but i only glanced quick but anyways etc, as for us in advciv-sas i intend to use it or at least try to use it if not more in a few key techs or arbitrary sadly or not sadly techs i want to use it at to prevent aggressive tech whoreism that is too advantageous to human players, while not forbidding tech trading altogether, hopefully more balanced and interesting this way (personally i play without tech trading in custom game though if i am not mistaken that this is how you do it but anyways etc and at least from last time i played which is quite some time ago but that i may play again or maybe not or yes or not or yes or etc but in all cases modding now as i like to do too but i hope someday i can maybe play again in civ4 i mean but in all cases i enjoy modding too but anyways etc anyways etc anyways etc, maybe a game of advciv-sas someday for me i mean in civ4 but anyways etc, hopefully helpful or not or yes or and other or and not but anyways etc))

I also added the info about the full list of i mean anyways etc which techs are not tradeable in placeSpecial, hopefully not too redundant or spammy this way in this case fo the placeSpecial of sevopedia tech and helpful maybe too or not or yes or etc but anyways etc.

Mods are welcome to use this quite simple but still hopefully useful code as long as they quote me and authors in [README.md#authors](/README.md#authors) as being the authors with mod name, even though it is not an obligation, it is a kind request i make, but in all cases hopefully this feature is helpful or not but not to change topic but anyways etc anyways etc anyways etc

## Example of DLL modification 2: missing BBAI getters expose them to sevopedia leader info in gc too for display anyways etc

See [README_Known_Issues_In_Base_AdvCiv_Civ4.md#17---now-fixed-missing-bbai-getters-expose-them-to-sevopedia-leader-info-in-gc-too-for-display-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#17---now-fixed-missing-bbai-getters-expose-them-to-sevopedia-leader-info-in-gc-too-for-display-anyways-etc) on how this was implemented (google drive with screenshots link there too anyways etc hopefully helpful or not or yes or and other or and not but anyways etc anyways etc anyways etc)

## Example of performance optimization of python loading time (as in when we load the code) and loading times if i may say anyways etc (as in code performance due to how it is optimized from what little or not little i know or and did of it but anyways etc)

The AI Personality feature in/of sevopedia leader has a very or at least quite optimized caching system, i think it is a good example or maybe at least time to show how i did it if it helps or/and others want to see it. Even though i am not too knowledgeable, i hope this info and general process of how i did this can be informative or/and pleasant/enjoyable maybe too or not or yes or other or etc anyways etc, see this doc section for details with google drive link with (= that has anyways etc) screenshots and such anyways etc: [README_AI_Personality_Panel.md#notes-about-performance-optimization-of-the-ai-personality-panel-caching](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_AI_Personality_Panel.md#notes-about-performance-optimization-of-the-ai-personality-panel-caching)

## Files

Please see the files (mostly if not only images) [in the Modding_Ressources Google Drive](https://drive.google.com/drive/folders/1Hx-bvRy7joM54S0Vnmva6HX1h8ZZ-LAh?usp=sharing)

In particular the XML ImagesAsButtons and Hardcoded_Button_Paths tags may be helpful maybe, among other possible files you'd find helpful or not.

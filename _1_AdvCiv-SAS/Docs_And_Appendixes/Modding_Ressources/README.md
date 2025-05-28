# Coding Help for AdvCiv / AdvCiv-SAS

This is a non-exhaustive page containing some ressources i found
helpful.

## Disclaimer and general information

I don't know a lot about XML, C++, or Python, and (only) got
familiar with these languages recently as i started developping
for Civ4 this AdvCiv-SAS mod.

I did have previous knowledge though.

I cannot be assumed or expected to be available or responsible
to provide any coding help or feedback (i'd prefer to have my
peace of mind rather, even though i may occasionnaly or more
often, but not guaranteed and maybe not if i don't want or
do so or any other reason or not, but i might or might not, just
this is a fair warning/caution point about that, anyways),
however i hope these few ressources i have accumulated may help
those who wish to start their own mod.

I can also not be held responsible for any damage resulting of
following these instructions, whether these are followed correctly
or incorrectly. I am only providing them as general information, and
while i hope it helps, you are responsible for checking it, verifying
it, and using it, and any consequence that may happen as a result.
Hopefully you'll find them helpful though, but in case not or
something happens, this is just to protect myself and talk to you
in all fairness.

Else or additionally, you may find more help asking your question(s) directly on
[CivFanaticsCenter's Civ4 Forum](https://forums.civfanatics.com/categories/civilization-iv.143/)
rather maybe. Hopefully this data i provided is also helpful though.

## A few useful tips

### full git log

Always keep a .txt copy of the full git log of the/your entire project, very useful when doing a global search (for example with VS Code), you can gain while doing so precious information about some features you want to know more about.

You can create such an exhaustive git log with, for example in git bash for windows, for Steam users (adjust paths and/or such similar things anyways if not steam user) (click on the images below to view them full size):

```
cd "C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS/" && git --no-pager log > git_log_repository_full.txt
```

For example for AdvCiv-SAS, i put this file (that i ideally should/try to update every while) in this folder [for example](/_0_Common_Docs/git_log_repository_full.txt) (but any place (you want) should do (fine) as long as it is in your mod (anywhere inside it maybe anyways)).

### manual(s) and docs in .txt

Similarly, i have found it very useful to keep a .txt copy of the docs i use, in particular technical ones, and such as the [AdvCiv base docs](/_0_Common_Docs/AdvCiv%20(Base)%20Doc) in particular the [manual in .txt](/_0_Common_Docs/AdvCiv%20(Base)%20Doc/manual.txt)

When doing a global search with VS Code for anything, as long as this manual.txt for example (or other files) are in the mods folders (anywhere, this/her is an example, anyways), then i can and may often (not guaranteed but maybe) also find useful information as part of my global search results.

Not necessarily for all docs, or may if you want, but sure is very convenient, hopefully helpful tip or maybe not but in all cases etc anyways.

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
- inspecting an object, see for example, not sure is best way to do it and i am no expert in it, but i did solve it hehe if i may say but anyways... etc.., just one way i randomly or persistently found that solved the issue of displaying/finding required building method, if it can help you too maybe anyways etc, here it is: [_inspect_object_attrs.py](/Assets/Python/Contrib/Sevopedia/_inspect_object_attrs.py) and [-SevoPediaBuilding-gc-inner-debug-content.txt](/Assets/Python/Contrib/Sevopedia/-SevoPediaBuilding-gc-inner-debug-content.txt) for example, and also [-SevoPediaUnit-gc-inner-debug-content.txt](/Assets/Python/Contrib/Sevopedia/-SevoPediaUnit-gc-inner-debug-content.txt) which helped me adjust Claude AI's (see [Claude AI's part of the authors section of this README.md below for details](/README.md#claude-ai-the-newcomer-hehe-xd-anyways-etc-welcome-anyways-etc) code of the new placeTerrainFeatureCity or similarly named sevopedia unit function/method anyways etc, not using the inaccurate methods Claude AI provided, at least in advciv and advciv-sas by extension since we use same code as in advciv anyways etc, `getHillsAttackPercent()` and `getHillsDefensePercent()` but instead the real at least as appears in our insect of the unitinfo anyways etc as linked just above in same bulelt point if i am not mistaken indeed if i may say anyways etc with `getHillsAttackModifier()` and `getHillsDefenseModifier()` of an otherwise very great code that worked at first try!!! (see also [this screenshot (1) (google drive image link)](https://drive.google.com/file/d/1oE0tG3VjCY7a5ABwlV0MYDhA3ox3Sbe4/view?usp=sharing) and [this screenshot (2) (google drive image link)](https://drive.google.com/file/d/1Yn7dIxzDpuJ2f8wbpXmhn2W0qZ42ADOe/view?usp=sharing) for example of how i solved it if helpful or interesitng or enjyoabel or pelasant or fun or any other else or not or othr or not or yes or and other or and not anyways etc anyways etc anyways etc) And finally shwoed us hills and peaks too so we can expand on it and try to find how to show them in sevoepdia terrain category now :o anyways etc, thanks a lot Claude AI and thanks to me too or and other or and not anways etc , hopefully helpful or not or yes or and other or and not anyways etc anyways etc anyways etc 
- todo add links if i have/want(/do) more to add

## In case UnitAIs info from link above is deleted someday, here is a copy here in case, anyways etc:

quote from website linked before anywyas etc, and adjusted or not or yes or not or yes or and other or and not anyways etc... for AdvCiv-SAS (mod +/- project anyways etc) anyways etc... :

"
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
"

## Civ4 ProcessInfos XML info

From: [modiki's website, wayback archive version latest i found anyways etc](https://web.archive.org/web/20230330010924/https://modiki.civfanatics.com/index.php?title=Civ4ProcessInfo) since was/is down the website as of/for now anyways etc

adjusted for advciv-sas or not anyways etc:

"
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

```
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
"

## Copy of the tutorial on how to modify GameFonts.tga for FREE

Note: you may want to read all this at least the end before you start doing it, in case you see something that makes you change your mind/choose another approach instead, but do as you prefer anyways etc.

Source: [CFC forum link](https://forums.civfanatics.com/threads/how-to-modify-gamefonts-tga-for-free.181119/)

In case it is deleted, i have made a copy here which is as follows adjsuted or not or and other or and not anyways etc for AdvCiv-SAS (formatting the github readme or and other or and not anyways etc):

"
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
"

I am not responsible if it is not updated anymore or inaccurate, but i hope it can be helpful hopefully or maybe not (is not helpful anyways etc) but in all cases is what i wanted to do (to write it here) anyways etc anyways etc anyways etc.

Note: it may be much easier, especially if you import art assets from a mod, to also import the icons from the .tga of a mod, see some screenshots in the google drive link above (about this .tga part) where i show for example the difference between our (current) .tga files (in particular the GameFont.tga and GameFont_75.tga files here in this example anyways etc) (before fixing/updating the icons) and HR mod's .tga files (same i.e. GameFont.tga and GameFont_75.tga files anyways etc anyways etc anyways etc) anyways etc, but i find it also interesting even if painful to know how to do, it may be/serve helpful/us especially if you/we want to add your/our own assets that don't exist in any mod for example, but (this) is just a suggestion do as you prefer anyways etc.

Note 2: This seems to be useful when reordering or/and adding/removing xml assets that depend on/use icons in the .tga file if i am not mistaken anyways etc, i don't know how it all works, but it seems that generally for example for religion assets, after having [reordered the xml order (for example in this git commit anyways etc)](https://github.com/wonderingabout/AdvCiv-SAS/commit/025c696fac3f43dd2b2489d99f36fae3f407ecb4), now the icons are all messed up (paganism religion shows with the judaism icon and or other changes anyways etc, see for example screenshots 5085 and 5086), so the .tga icons's order seems to also need to reflect the xml order or vice versa, and similarly for the _75.tga file if i am not mistaken too do all these steps again for more fun if i may say or not as is more tedious but more accurate hopefully this way unless i am mistaken and there is somehow or could be a better way i don't know of maybe, else hopefully more accurate this way or whichever or not whichever way it may/would be, anyways etc anyways etc anyways etc, again i don't know exactly how it all works but i think this is the general idea and that it works helps quite good maybe or not or yes or and other or and not anyways etc hopefully helpful or not or yes or etc or and other or and not anyways etc.

Note 3: you may want to make backups to avoid overwriting accidentally the wrong file or such or not having a backup of the file needed anyways etc anyways etc anyways etc...

## ICONS code XML names (may or not be exhaustive anyways etc) (with some color changing code as bonus or to be extra exhaustive a bit more than needed but is here if needed maybe anyways etc)

from: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\CvDllTranslator.cpp`

As follows:

```
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

## Files

Please see the files (mostly if not only images) [in the Modding_Ressources Google Drive](https://drive.google.com/drive/folders/1WejRQuHTNXVsTHnAsYTAErS2m_oeaEwp)

In particular the XML icons tags may be helpful maybe, among other possible
files you'd find helpful or not.

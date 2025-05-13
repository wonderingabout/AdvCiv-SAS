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

For example for AdvCiv-SAS, i put this file (that i ideally should/try to update every while) in this folder [for example](/_0.0_Common_Docs/git_log_repository_full.txt) (but any place (you want) should do (fine) as long as it is in your mod (anywhere inside it maybe anyways)).

### manual(s) and docs in .txt

Similarly, i have found it very useful to keep a .txt copy of the docs i use, in particular technical ones, and such as the [AdvCiv base docs](/_0.5_AdvCiv_Base_Docs/) in particular the [manual in .txt](/_0.5_AdvCiv_Base_Docs/manual.txt)

When doing a global search with VS Code for anything, as long as this manual.txt for example (or other files) are in the mods folders (anywhere, this/her is an example, anyways), then i can and may often (not guaranteed but maybe) also find useful information as part of my global search results.

Not necessarily for all docs, or may if you want, but sure is very convenient, hopefully helpful tip or maybe not but in all cases etc anyways.

## A few useful links
- todo: tutorial on how to compile the DLL and/or files for Advciv (but should not
be needed if you only modify XML files if i am not mistaken)
- ressources that mention XML files and tags, useful if you'd want to [get started
doing your own mod](https://github.com/wonderingabout/kujira)
- or alternatively/to complement for example [modiki's website too](https://modiki.civfanatics.com/index.php/Civ4TraitInfos)
maybe (even though i mostly use kujira's website, maybe this one helps too).
- list of unitAIs [kujira](https://gforestshade.github.io/kujira/post/keyichiran/#%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88) and
[cfc forum with what they do (may be accurate or not anyways)](https://forums.civfanatics.com/threads/list-of-unitais-and-what-they-do.353919/post-8910602)
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

## Files

Please see the files (mostly if not only images) [in the Modding_Ressources Google Drive](https://drive.google.com/drive/folders/1WejRQuHTNXVsTHnAsYTAErS2m_oeaEwp)

In particular the XML icons tags may be helpful maybe, among other possible
files you'd find helpful or not.

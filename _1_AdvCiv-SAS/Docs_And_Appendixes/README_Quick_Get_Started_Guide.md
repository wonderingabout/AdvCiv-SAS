# Quick Get Started Guide

This page does not go to go deep into the technicalities, for that see the
[other documents](/_1_AdvCiv-SAS/) of this mod, but it gives instead a quick
starter guide on the key few differences between AdvCiv and AdvCiv-SAS, for
newcomer players used to AdvCiv, Civ4 BTS, or some similar mods.

todo cleanup extensive comments and move them to a longer changes guide notes

## Sevopedia AdvCiv-SAS Entries

Some of the changes in AdvCiv-SAS (coming from AdvCiv) are also listed in the
Sevopedia Entry (non-exhaustive), please visit it there (the screenshot below
(click to view it full size) may not be updated, it is to give a general
idea):

<img src="../Images_In_General/sevopedia_mods_info/0.613_sevopedia_advciv_sas_core_changes (1).JPG" width="250"></img>

See also the main [README.md#changes-from-one-mod-to-another-sevopedia-itemspages](/README.md#changes-from-one-mod-to-another-sevopedia-itemspages) for details.

There are also other additions, in particular written/coded by me wonderingabout, ChatGPT, and Claude AI, which are documented (mostly by me (wonderingabout) though hehe anyways etc), such as the AI personality panel (featuring raw and AI attributes display and ranking for all leaders), very important addition to AdvCiv-SAS, hopefully useful in understanding how each and all AI leaders behave and relate to each other, please read (if interested etc anyways) the (more) extensive documentation of how it works in [README.md#sevopedia-reworks-ai-personality-panel-and-other-sevopedia-reworks](/README.md#sevopedia-reworks-ai-personality-panel-and-other-sevopedia-reworks), or directly in [README_AI_Personality_Panel.md](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_AI_Personality_Panel.md) if you want (to look etc anyways) for the full page.

A copy of the screenshots (may not be latest version of it) of how it looks ingame:

<img src="../Images_In_General/sevopedia_reworks/0.620_sevopedia_AI_Personality_sample (1).JPG" width="250"></img>
<img src="../Images_In_General/sevopedia_reworks/0.620_sevopedia_AI_Personality_sample (2).JPG" width="250"></img>
<img src="../Images_In_General/sevopedia_reworks/0.620_sevopedia_AI_Personality_sample (3).JPG" width="250"></img>

For more screenshot samples of new sevopedia entries or udpated ones (not exhaustive), you can visit the [README.md#sevopedia-reworks-ai-personality-panel-and-other-sevopedia-reworks](/README.md#sevopedia-reworks-ai-personality-panel-and-other-sevopedia-reworks) link (for details (too anyways etc)).

## Handicap info tables .csv and .md and info about the .py script that can regenerate them if need and how

To follow/understand smoother difficulties (called handicap in civ4 if i am not mistaken but anyways etc), i have also added a table view of the differences between difficulties/handicap settings, please see [README.md#csv-and-md-view-of-the-handicap-difficulties-info-in-a-table-for-all-difficulties-infodata](/README.md#csv-and-md-view-of-the-handicap-difficulties-info-in-a-table-for-all-difficulties-infodata) for details

Example output (non-exhaustive, also screenshot may not be updated, best to see link above i would say but anyways etc for details if interested but anyways etc):

<img src="../Images_In_General/scripts/csv_handicap_info_github_view_example.PNG" width="250"></img>
<img src="../Images_In_General/scripts/csv_md_handicap_vs_code_preview_example.PNG" width="250"></img>

## Full exhaustive very long and exhaustive changes

If you want to see the full very exhaustive code changes between AdvCiv current latest stable, for example 1.12 here, and AdvCiv-SAS, please visit this [pull request compare](https://github.com/wonderingabout/AdvCiv-SAS/pull/13).

Be warned though it can be very lengthy, so read below if you want (some of the) main quick pointers rather.

## Main Changes quick starter guide

- tech tree is vastly reordered for historical accuracy (for example steel is at
iron age, pottery is before the wheel, metal casting before currency and before
bronze working; and medicine at iron age, that too should be about accurate),
but it is mostly the same techs as in civ4 bts/base advciv, hopefully easier to get
into/used to, and i did not see a specific reason to change these, initially i
started this AdvCiv-SAS mod mostly to readjust tech tree if i remember correctly.
- Barbarians are now much stronger in the early game economically, they should now grow at a similar pace than human and other players too until the middle game where they will gradually fade. They should also spawn cities more often and be relevant longer in the game, even though for now at least if not always or not they have trouble to grow past a certain size, and are still not a real player (no diplomacy and scattered cities that are independent, but that contribute together to the "barbarian(s?)((,)'s) civilization"), and become a key part in politics or invasion decisions, maybe i mean or not or/and other or not anyways etc. Their (now new)(anyways etc) overall strength increase (for example they are also harder to kill at all difficulties (less to no combat bonus against them, but never reverse bonus to them to make the game fair and balanced and fun as much as possible at least to me or and maybe (to) others ideally or maybe not (and or maybe not ideally or not or other or and not anyways etc) but anwyays etc) is gradual with difficulties), and they should not be (too) op though so hopefully not overbearing either but demanding more strategy or/and attention to hopefully make the game interesting, while filling some unsettled areas if not claimed fast enough in a quite realistic way too maybe anyways etc. They are also more calculating in who they attack, may raze cities much more than in base AdvCiv/Civ4 if am not mistaken anyways, and are more calculating in who they attack target the weak not the strong, anyways etc, or/and other changes or and not anyways etc. See the Barbarians Sevopedia Civilization entry for details ingame or/and the XML for example for the Steam version of the game (adjust to where your AdvCiv-SAS mod is if path is different or/and you don't use the Steam version of the game) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\Civilizations\CIV4CivilizationInfos.xml and related files like CIV4BuildingInfos.xml and CIV4HandicapInfo.xml or/and such.
- the "citizen" specialist is removed, instead added the doctor specialist (that)
gives health todo and a great doctor great person that gives todo unlocked at
medicine tech todo. I found "citizen" quite useless and annoying even sometimes,
hopefully less now and maybe useful hopefully.
- game pace advances exponentially: later eras have fewer techs and units. This
avoids the hassle of a long and tedious endgame, but is also realistic as most
of history in the amount of years, happened in the past. Bronze Age alone was
longer than most of our recent eras for example, and even more so for Stone Age.
However, units and eras give exponentially bigger bonuses too, and tech costs
and such have been adjusted. Taking also into account that players (should/generally
i think) spend more time on the end game to manage all cities and units or other
things, maybe this will even out and game will still feel the same speed for each
era. Beware to not neglect tech as later ones will be key if no player still has
yet won the game. There are also less units and buildings to fasten the end game
(but trying to keep just enough techs to make it last long enough) time per turn
in minutes/hour played.
- as a result of the previous point, it should be even less likely for a "spearman"
(now there are more units of this type in AdvCiv-SAS, see below at military reworks)
to win against a tank, and also much less likely for a swordsman to every match a
musketman, for example, which should also make more sense historically hopefully.
Defenders may have a chance to prevail while being behind in tech but it will be
(much) harder.
- the civilopedia is renamed the sevopedia, it is the same thing but is the name
of the more modern version (made by modders) of it.
- on that note, unit combat types todo refers to unit categories/types, for example
in Civ4 BTS/base AdvCiv these were for example archery units, recon units (scout,
explorer), melee units (spearman, axeman, swordsman, maceman, pikeman, etc.), etc.
- there are many new unit combat types todo, see the sevopedia entry "Unit Combat
Types" for details. This allows to give specific bonuses to specific combat types.
For example, there are now new combat types of units (and modified existing ones
too), for example there is no more "melee" combat type. Instead, for example about
the former spearman (that was part of the melee combat type), there are now 3 new
combat types the old "spearman" can be part of, melee_lancer_light, melee_lancer_medium
(includes the former spearman that is now a lancer medium combat type at the bronze
age era, for example), melee_lancer_heavy. See the "Unit Combat types" category of the
sevopedia (ingame)(the sevopedia has been a bit tweaked/reworked too btw) for details.
- why bother to do (all) that? Each of these combat types have different units with
different strengths and weaknesses, but to give a general idea, generally the faster
ones will have less damage/strength but better at defense/avoiding/harassing other
units quite freely, while the slower ones have high strength, can defend and attack
well, but no such bonuses, and may cost a bit more too. Strategy should be a lot
more important and versatile/flexible/to be adjusted based on local circumstances.
For a full view of all existing units, on top of viewing the "Unit Combat Types",
you can also see the "Units Tree" for a better view of in the sevopedia ingame, or
this version of the units tree i made that lists the unit combat types and era for
it as well if it helps (may be a bit outdated though but should not be too much)
[military tree map view](/README.md#civs-and-units-you-can-expect-in-this-mod).

- A consequence of this is also that now there will be hopefully no more weirdness of
the axeman being good against lancer, now the relationships between types will be more
complicated or rather defined (may make more sense at same time too), for example an
axeman may be good against swordsmen (for example todo), but not against heavy lances.
Light lances may have strong bonuses against all/most melee types, except fast ones,
and light swords strong bonuses against all/most melee types too except fast ones
(their strength would be lower though). Strategy should be much more important while
not being too tedious ideally.
- another example is an ancient Maceman ("warrior" in the stone age) will be stronger
than a medieval light swordsman, but the medieval light swordsman will have (much more)
bonuses that should make him (or her but most often him) more valuable
as a military unit. This is also realistic too, no reason why an ancient maceman could
not defeat a swordsman, if looking at strength and chance alone, unlike what is, a bit
too extremely the case i think, in base advciv/bts, even accounting for armor and such,
i think, an ancient unit may be stronger by melee alone, so some strategy will be necesasry
to have the best (or better) odds in AdvCiv-SAS, i think, hopefully in an immersive
and not tedious experience too.
- unique units are now renamed civilization units: they are not unique and can be built
many times, just by only one civ in AdvCiv-SAS (and in base civ4 BTS/AdvCiv too if i
am not mistaken) if i am not mistaken. Could be shortened to civ units maybe
too as i may or not or not always do further in this doc or/and other docs, hopefully
the meaning of this expression would be clear enough (fast worker for india for example)
- Renamed "Ressource" to "Bonus" for shorter Sevopedia category width, but also perhaps a good opportunity to match code name and game name maybe at least is how i would want to do it an AdvCiv-SAS if hopefully fine as in functionning well anyways etc.
- The tech tree is fairly straightforward, with max one (minus the civ units)
unit type per era, for example, which should hopefully help make sense of that and getting
immersed into it, while not neglecting on strategy, hopefully, at least was my/one of my
goal(s) making (and became as i was making too) this AdvCiv-SAS mod. Note also that this
is not the case for all units and eras, only the ones i found most relevant ones and to
not be tedious enough (there is no work boat 1 work boat 2 workboat 3 etc for example,
only one for all eras, but there are a few workers every few eras, but there are military
units for each new era, at max one unit per combat type (for example "sword light", "lance
heavy", are each one type), and not for all types, also lesser in later stages of the game
to simplify/rush/reach sooner the endgame)
- explore units can attack: but their strength should be quite low
- ground explore units can move through all terrains since the begining of the game,
not water tiles though, but for example peaks. They also all ignore terrain
movement costs, not just the (renaissance) explorer
- air explore units for example the dirigible todo (old airship) can move through
all terrains, including peaks and water tiles
- military units are versatile: swordsmen can defend, archers can attack,
maybe even workers too
- unit promotions have clearer names now too: for example Counter-Archer,
counter Siege, Counter-Tank. Or another example is "City Bombard" (instead
of barrage). Numeric naming has been changed too for clarity and ease of read:
for example "Combat III" is now "Combat 3" too.
- unit promotions are reworked or/and rebalanced: woodsman for example is buffed,
some are rebalanced or nerfed, and other some promotions have also their requirements
changed, for archers have access to city bombard promotion (units are reworked too,
see below), or "Logistics" (named "Commando" before) is now accessible after
Combat 1 or City Attack 1 todo rename. Some are available sooner too, for example
"Logistics" is available at "The Wheel", not "Military Science" anymore, since
we understand roads we can use them, maybe, more strategic importance now too maybe
hopefully.
- military units are reworked: for example the holy roman empire special unit,
to better accomodate its history and stats, can be built starting from a different
tech, in particular the settler is now not freely available but requires agriculture
(is historical too, but for convenience first settler at starting game is provided
for free as it was in Civ4 BTS and AdvCiv)
- some units can only be built under specific conditions, for example each religion
has one unit (same for neo religions at later eras. See religion changes below for
details), for example Buddhism is required to build monks (lance light combat type)
(yes such as shaolin but anyways..) and Christianism for Crusaders, etc.
- on that note, some religious units are listed on the units tree of the sevopedia
while some others not, check for detail the sevopedia (todo update this bullet
point) page of the sevopedia? 
- military units are rebalanced: some op units (according to me) are nerfed
slightly (for example: todo), some weaker ones buffed quite a lot (for example
the jaguar warrior)
- some units have been removed: sometimes for graphical reasons: for example the
rifleman has a new graphic art but the concept of a rifleman remains in itself
(may be rebalanced or not though like the other units though)
- some units have been removed: sometimes for gameplay reasons: for example the
nuclear_submarine is not relevant enough and does not actually hold nuclear weapons, only is nuclear powered if i am not mistaken, but effect is not strong enough to justify the hassle so just remove them anyways etc, also ideally i'd want only and/or mostly only one class (for example a a galleon, a worker, a swordsman, etc.) of unit per era
- removed some units, such as the caravel: was not very sensical / nonsensical to me at least anyways etc that openly nation-specific and announced caravels could freely travel in outer borders even if borders are not open (and send annoying spies and such) without declaring war while doing so, so now this ability is now specific only to the privateer, among visible units at least (unlike the (normal) submarine for example if i am not mistaken anyways etc), and the privateer is now also buffed, see sevopedia for latest values and effects anyways etc
- similarly for the stealth bomber, may remove it as well to simplify gameplay especially the endgame, there are stronger bombers at each era, just not stealth, or for example the panzer has been removed for a sooner, more likely to be useful civ unit: the teutonic (foot) knight. This ability has been removed from most units where i felt/thought it didn't make sense, such as submarines or/and other units.
- some units have been removed: sometimes for historical accuracy or flavor one
could say maybe reasons: for example the phalanx civ unit of the greek empire
is now the hoplite phalanx (a lancer heavy combat type, not based on the axeman
anymore), and available in mid iron age not in bronze age for better historical
accuracy. I did not check them all (maybe todo fix this note if did) but those
who i did and that i found to be (especially if gravely) mistaken and that i
wanted and did decide to fix or did i did fix. Feel free to point historical
accuracies to me, not guaranteed i would fix them, but if i am available to
read them and all i may or/and reply to those requests about these, but
not guaranteed, may or not,
- some units automatically upgrade, for example the workers, scout, and similar
units. They get a new design graphically at a new era, but also more bonuses, for
example every few eras workers may become more and more productive (faster
improvement build time, or/and move speed/ or and other things for example).
This is to remove the tediousness or a part of it from the game
- about this too, for simplicity most unit upgrade are fairly straightforward and
relaxed: all offensive units can be upraded to offense gun units, same for defensive
melee units into defensive gun units, same for all offensive mounted units into
offensive mounted units. I don't want the tediousness (if any must have to be, not
sure about this too but anyways) to be there. Historically is also not so nonsensical
to think archers started to use a gun, or even axemen actually, once it's not an
effective weapon anymore. Cavalries and similar upgrade into tanks, maybe their skills
translate into driving the tank better or having a better understanding of military
tactics/logistics required in doing so. This is mostly to simplify the tedious parts
of the game while also making all units relevant, a few one rather than many useless
ones, so plan your strategy accordingly.
- terrain is very important, almost all units have terrain bonuses, and sometimes
rarely terrain maluses (i prefer to buff the weak than nerf the strong, unless
i think it is relevant (quite strongly))
- another element of attention is that military (at least early ones, now don't
have much strength difference between them. For example, an ancien maceman (warrior)
would be 10 strength, and a swordsman only 15 strength, while an archer would be 6
strength but with extra or/and other bonuses. In exchange of these adjustments, upgrade
costs are much cheaper todo, so you will not be able to build full warriors then upgrade
them later while going full economy. Also, since units are so close in strength now,
at least early ones, terrain multipliers and promotions multipliers play an especially
big part. The power correction part has been entirely removed or rather negated, in
fact slightly under 100 now. As a human even if odds are slightly below certainty, if
odds are good enough, attack. In exchange also, city attack has been severly increased,
now an AI will want to be about twice +/- as strong as city defenders else would not
bother to attack, ideally. Hopefully and ideally, in theory, this means AIs should/would
behave like a human player would or closer to it, hesitating less to attack and may be
willing to risk if good enough odds or reward, but more guarded about attacking stronger
targets otherwise, at least in theory. They should especially target more lone units
outside of cities, but much less those in cities.)
- global defines have been changed to have religion importance higher (in terms
of culture strength (not exactly sure what this means but should be fine and as i
intend i think maybe)) for example, lower revolt chance, anger from war quite a
bit reduced higher reluctance to agree to a war trade, etc. A bit more pragmatic
or/and opportunistic, or possibly realistic conditions, war may not always be a
fatality, at least in the long run, even though it's hell at first, but this is
not a strong or much likeable opinion of me to have, i simply think it would
make gameplay better/easier/more relaxing, and is also more realistic too this way
- some terrains are buffed, for example snow, desert, and water tiles are (very)
important now. Some terrain specific bonuses are added to some units or/and
Civlizations (for example todo), some buildings give bonus to desert and snow yields
, for example the impluvium building (Kingdom of Benin) improves quite a lot the
desert tiles (you can gain more bonuses with other buildings or techs or civs for
example), and another example is the building that replaces moai (nerfed but not a lot)
- some improvement (worker) or/and build 's techs prerequirements and/or such have been adjusted as well, for example build quarry is sooner, and remove forest and remove jungle are now at same time and sooner in tech tree anyways etc, see sevopedia ingame or/and tech tree view ingame or/and xml for details anyways etc
- water buildings are reworked and buffed, the harbor (1st water building) as of now at least anyways etc is a food/health building, then the lighthouse is a gold building, then the port is a (new) (anyways etc) hammer building, moai statues is now a world wonder with a global water effect and a bit stronger overall as a result or in general or not anyways etc, customs house have been buffed too, and other or not related water buildings or such changes that hopefully buff in a balanced way water tiles that were too weak. I also believe since you need to actually work the tiles, these new per tile yield bonuses should be more balanced as they are more gradual, even though stronger generally than previous ones such as trade routes that would apply even if water tiles are not worked, some of these old effects persist, others may be adjusted or not anyways etc, see sevopedia ingame in sevopedia building or xml for updated values and buildings and such anyways etc
- traits have been reworked, some weak traits have been buffed or/and modified,
while some other op traits may have been modified (not necessarily nerfed). For
example, the protective trait has been buffed, as i had found it too weak or/and
not relevant enough. This is not necessarily for all traits. Please look at the
Sevopedia "Traits" entries to have the latest updated version of the traits effects
- start map behaviour is affected, not so much terrain polishing (map script
removing bad tiles such as jungle or snow or peak, they are now kept, but
instead you have more starting vision to choose your spot, which should be
realistic too because at 50 000 BCE (approximately) humans may have enough vision
of their surroundings to know where to live or adjust to it maybe (even though
first city settling is not as realistic, but is for convenience, and could maybe
be imagined as a nomadic settlment in the region maybe, still convenient so allowing
it)), also these "bad" terrains should be buffed a bit or quite a lot, so they
would be more considered as alternative strategic options rather than bad tiles, among
other possible changes
- All units now are affected by city defenses (walls, castles, etc if any more/other), even gunpowder and later on units, seems more realistic to me this way, as walls can help against guns and against all (almost?) units, actually even if not having the tech for guns itself. See also for details: bIgnoreBuildingDefense in CIV4UnitInfos.xml or/and (tranlslate to english ((following) web page (anyways etc)) using web browser or such) https://gforestshade.github.io/kujira/post/civ4unitinfos/#bignorebuildingdefense for details (too anyways etc(.)) anyways etc... .
- worker cost is reduced
- missionaries, spies, corporation executives todo have their cost greatly reduced,
be sure to build them soon enough, also the effects they give access to (if conversion
succeeds for missionaries (for corproations todo maybe it would be 100%?(?))) are even
stronger.
- renamed "great wonders" to "world wonders", but functionally the exact same if i am not mistaken, i hope it is clearer, more intutiive, and in line with "world project", hinting more strongly at the fact that only one is possible in the entire world if i am not mistaken, anyways etc.
- (todo check if still accurate and if we implement this in advciv-sas or simply rather reduce their count or/and rework them anyways etc: ) no more small wonders! To simplify gameplay, world wonders, have stronger and more significant effects now.
- (todo check if still accurate and if we implement this in advciv-sas) some world wonders have changed names to reflect their history more, for example 
"The Great Lighthouse" is now "Lighthouse of Alexandria", and some wonders are tied
to another civ than in civ4 bts/advciv, for example "The great wall" no longer is
linked with China but is now "The Ancient Walls of Benin", if you want to know why,
see [the Mod folder](/_1_AdvCiv-SAS/), i have also put the 
[source](https://thinkafrica.net/walls-of-benin/)
here directly to illustrate this example.
- (todo check if still accurate and if we implement this in advciv-sas) also, each civilization now is tied to a world wonder, everyone can build it,
but if the civilization tied to it builds it first
- some gameplay elements happen at different times, can resarch sooner, build
culture sooner, slavery sooner, plantations sooner, tech trading a bit later (at
guilds i think todo)
- nerf tech whoreism (if that is a word anyways etc), which AIs are especially vulnerable to and that humans can abuse, by adding a few or quite many new "This tech cannot be traded" flags in sevopedia, tech tree view (tech advisor) at some techs, hopefully this makes the game more interesting and strategic, while not preventing tech trading altogether (unless you use the "No Tech Trading" option in custom game if i am not mistaken which disables it entirely if i am not mistaken too anyways etc), so you can't gain 10 techs in a row with just one tech anymore, but maybe you can profit a bit from tech trading if you don't use the option i.e. if you play with tech trading enabled (personally i don't play with tech trading at least as of now anyways etc and when i last played but anyways etc but i hope it is more balanced this way now anyways), added also a new "This Technology cannot be traded" sevopedia tech (in "Special Abilities" panel (placeSpecial in the py code if i am not mistaken too anyways etc)) and tech tree view (called "technology advisor" if i am not mistaken too anyways etc) (see also [/Modding_Ressources/README.md#example-of-dll-modification-of-cvgametextmgrcpp-to-add-the-new-this-technology-cannot-be-traded-flag-in-sevopedia-leader-s-placespecial-and-in-tech-tree-view-technology-advisor-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/Modding_Ressources/README.md#example-of-dll-modification-of-cvgametextmgrcpp-to-add-the-new-this-technology-cannot-be-traded-flag-in-sevopedia-leader-s-placespecial-and-in-tech-tree-view-technology-advisor-anyways-etc) for details on how this was implemented/coded in advciv-sas by me with the help of chatgpt/becomingthrough but anyways etc anyways etc anyways etc...), hopefully gameplay is more balanced and interesting this way, perhaps informative too with my changes if i may say, but anyways etc anyways etc anyways etc...
- reduce TECH_COST_NOTRADE_MODIFIER from -23 to -20 (see (adjust to your mod path) C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GlobalDefines_advc.xml for details and or latest updated value anyways etc), which as reminder according to the base advciv code comment if i am not mistaken anyways etc: " <!-- advc.550d: This modifier is applied to tech costs when playing with the "No Tech Trading" option. The effect of the modifier is reduced in the early and late game. Recommended: -23, meaning that tech costs are taken times 100% - 23% = 77%. This multiplier gets further adjusted to the tech era and map size. Use 0 for BtS behavior (tech costs unaffected by the "No Tech Trading" option). -->"
- slavery iProductionPerPopulation increased (currently from 24 to 26, see xml for latest updated value as it was too weak and also (it was) (anyways etc) too advantageous in base advciv at least in my experience anyways etc at emperor/monarch to not slave at all, so making slavery more of a risk worthy strategy, considering its cost of immediate population loss and anger, detailed reasoning in `HURRY_POPULATION` of [/Assets/XML/GameInfo/CIV4HurryInfo.xml](/Assets/XML/GameInfo/CIV4HurryInfo.xml) for details anyways etc), the granary building is also nerfed or/and reworked a bit rather, as a cheaper and (quite) slightly (anyways etc) less (anyways etc) food generating building, see sevopedia building ingame for details or/and docs or/and code comments for details. civ-specific versions of the granary unaffected at least not all, so the civs with a civ-specific granary gain more advantages of having one as their civ-specific building, anyways etc. Reworked in particular the incan granary (terrace) to be a production/growth building now not a culture one anymore, see docs for details or/and ideally sevopedia ingame entry for details
- also replaced some civ-specific buildings, especially late game ones or/and (those i deemed but anyways etc) (too but anyways etc) inefficient, such as/like but anyways etc the russian research institute (now removed) (is (but anyways etc)) now replaced with the new building gord for a more/stronger early game impact (based on the castle), see xml or ingame sevopedia or and docs or and other or and not for details, anyways etc
- some ressources are not revealed until a certain tech: sheep is always visible,
but gold not until metal casting.
- a few new civs added, mostly in snow/desert terrains, or underrepresented parts
of the world, see [world map with civs](/README.md#civs-and-units-you-can-expect-in-this-mod)
(todo add link), for example The Kingdom Of Benin (Nigeria), or in weaker terrains
(that are now buffed), for example Canada
- (may not be accurate anymore todo among other possible changes to fix in this doc or not or and update or and not anyways etc, given as generla info hopefully helpful ro tnot or and other or and not check seopedisa for latets ocntent todo fix or view this later or not for me (to do so or not (do so) anyways etc anyways etc anyways etc)) Leaders have been changed: unless strongly desired, all civs have at max 2
leaders, should be plenty for a variety of gameplay, i don't want to clutter, prefer
to go deep in strategy instead, for example Joan Of Arc has been added, and Louis XIV
and De Gaulle removed, generally i preferred to keep the stronger ones, Cleopatra
added and Hatscheputt removed for example
- (may not be accurate anymore todo among other possible changes to fix in this doc or not or and update or and not anyways etc, given as generla info hopefully helpful ro tnot or and other or and not check seopedisa for latets ocntent todo fix or view this later or not for me (to do so or not (do so) anyways etc anyways etc anyways etc)) Leader animations removed, since now some don't have, better if none have maybe,
instead i tried to put some nice images relatively as i thought would fit and i like, took quite a lot from existing mods
- Some new ressources, for example camel and todo, some removed ressources, for
example hit ressources and todo
- Renamed "Wine" (Bonus) to "Grapes". As part of renaming wine to grapes, additionally reworked grapes: now improved by IMPROVEMENT_FARM, not anymore by the old improvement_winery now removed. This matches historicality better if i may say and if it's a word anyways etc, as wine was consumed much before 4000 BC. Also, some wines are not made from grapes at all if i am not mistaken, and grapes can be eaten out of the wine usage. Updated bonus's description with a wikipedia based one as often if not always done when updating pedia entries of/in advciv-sas or and other mods using this mod's (i.e. this advciv-sas's code anyways etc). Also, the winery/happiness part of wine is transferred to the grocer building instead, now grapes gives happiness not health anymore. Similarly although not directly related, sugar now also gives happiness not health anymore through grocer. Hopefully buffes these mid game bonus effects while making these ressources more relevant as they were (a) bit (anyways etc) weak compared to say wheat or maize. See code comments for details or the ingame sevopedia entry of the grapes with also maybe or not or yes anyways etc latest updated info if anything changed since i wrote (am writing currently but anyways etc also wrote when viewing from later the new now maybe or not or yes anyways etc) but this should be the bulk of it and hopefully makes gameplay more accurate or/and interesting perhaps or/and enjoyable or not anyways etc.
- Not tested if i may say but anyways etc, in theory AIs should value Iron bonus/ressource especially more, and horse more too, as an objective, using `<iAIObjective>10</iAIObjective>` (was 0), (ideally not restricting trade if uneeded extra in possession but not tested nor do i know too much about it anyways etc but hopefully maybe would work as intended maybe not guaranteed though anyways etc may or not anyways etc) if they don't have it, was 0
- Adjusted the name and repartition and spawn chance as well as yields of many ressources, please view sevopedia bonus for latest info and [this commit](https://github.com/wonderingabout/AdvCiv-SAS/commit/b841968682f022e2cefbe1722efb3520492659b8) for details. In general, to get the main idea of it, some ressources that were weak are now stronger (for example silver, deer, etc.), some are a bit weaker (for example gold, but it could barely be considered a nerf anyways etc), ressources/bonuses overall give less gpt to make game more gradual. Food land ressources spawn significantly less but after various testing increased it to values where they still spawn enough for game not to be boring or tedious, the idea is there will be more competition around them, as a result they also generally have a bit stronger bonuses, as well as reworked ones (for example sugar gives base hammer (productivity, horse gives base food but then improved gives only hammer, etc, see sevopedia bonus for details)), and deer in particular spawns much more as it is the only representative of snow or rather tundra ressources, its bonuses are among strongest which seems accurate as it is both a very healthy and rich food. As a result, tundra cities if they have deer near them should be a lot more viable, example that may not be accurate in the future of me writing this, but for example as of now these screenshots from the drive for example show how it looks (view around screenshot 5235 to 5249 of the google drive for other samples of that time of this rework now finalized as of me writing this anyways etc): view for example screenshots 5238 of the drive here https://drive.google.com/file/d/1178did3ROEoIV_wbonpH91jZcdaNtzRg/view?usp=sharing and 5241 of the drive as well here for example https://drive.google.com/file/d/15acCk947FpTMmDJdzg6sMXCXOjYwiUB0/view?usp=sharing anyways etc. Also, water ressources spawn more, especially for the now renamed clam into the more general molluscs and fish as they are general ressources. Similarly, i have run a few tests  to make sure (or at least try to (as best as i could or and wanted anyways etc hopefully accurate enough or not or yes or and other or and not anyways etc)) they don't spawn too much, so these are quite conservative tweaks but significant. With also buildings like the harbor quite strongly buffed or/and reworked (view sevopedia for details) now, water planting/settling cities should be a strong alternative to purely land ones, especially to complete an otherwise nice land location but poorer in ressources. I tried to make sure naval planting doesn't become too op or the opposite for land, i hope more versatility and strategy(ies? Anyways etc) can be used now as part of this rework, as well as more accurate gameplay. On that note, some pedia entries have been updated, whales have been buffed too, etc, please view for details sevopedia bonus or/and docs or/and other pages anyways etc (or don't blame me if not accurate info you have hehe if i may say but do as you prefer here is all the info i have or most that was not too tedious or forgetted or rather forgotten xd if i may say but anyways etc of me to say but anyways etc...), i hope gameplay will or and can be more interesting now with these balance changes without skewing too much at one side or the other, and that now there are more possibilities to play civ4 in a balanced perhaps competitive way, at least in theory and to best i could do at least of now, hopefully enjoyable or and helpful or not at least to me, may be tweaked in the future or and not, anyways etc.
- as for desert tiles and how to buff and rework them quite similarly than with BONUS_DEER (deer) + BONUS_MOVIES (hit movies), but quite differently since the later new ressource (no spoil but anyways etc...) is related to military units as well so adjust that repartition with that and link with bonus_horse in mind but anyways etc, replace BONUS_MOVIES with BONUS_CAMEL, art import from rfc doc mod anyways etc, hit bonuses/ressources are (i found at least anyways etc) tedious to maintain/manage for small gains but anyways etc, as for camel it can be directly used to buff desert (food in particular anyways etc) tiles or/and be an alternative mount to the horse and opens the door if i may say but anyways etc to having camel mounts multiple/many ones/units anyways etc anyways etc, may also have some interactions with wonders or such or not such or yes such but anyways etc ; is based on BONUS_HORSE's xml and adjusted and such ; also similarly to deer in tundra tiles, give camel, the only representative animal of desert tiles, a quite high food yield and such, hopefully is accurate too anyways etc as camels can store water in their bodies if i am not mistaken or such in similar or such or not anyway etc kind of "reservoir" if it's a word in english and if i may say or not but anyways etc ; in all cases should be balanced to make camel a king or/and among them food as in highest food yield food and to buff desert tiles too anyways, reduce frequency of bonus_horse which bonus_camel is now an alternative to anyways etc even more now that we added bonus_camel, not necessarily a huge lot more nor does it need to be strictly i mean similar to bonus_horse's ratio (partly because is only on desert tiles for camel unlike horse that is on many types of tiles if am not mistaken too anyways etc, so lower bonus_horse repartition/frequency a bit more while making bonus_camel follow its own formula anyways etc), also reduced quite bit slightly but anyways etc the repartition of other high food land animal bonuses/ressources anyways etc to accomodate bonus_camel being quite present in the map and have ressources/bonuses being still rare enough hopefully so players fight/compete for them as should be ideally in a strategy game i mean maybe but anyways etc
- remove horse from tundra tiles, there is enough deer for food, plus now that there are less horse tiles, make it more likely players would have them, i.e. in non-tundra tiles anyways etc
- unit upgrade paths reworked, for example chariots upgrade to horse_archers now not to knights anymore, war elephants upgrade to knights not to cuirassiers anymore, see sevopedia ingame or/and tech tree view or/and xml for accurate/updated value(s) anyways etc
- made ressources/bonuses generally spawn more towards the edges of the map, it was a bit too skewed towards central spawning for most bonuses, giving central start too big of an advantage over edge start, hopefully and with other bonuses and changes to spawn rate and such a bit closer now or/and balanced anyways etc
- (may not be accurate anymore todo among other possible changes to fix in this doc or not or and update or and not anyways etc, given as general info hoepfully helpful ro tnot or and other or and not check seopedisa for latets ocntent todo fix or view this later or not for me (to do so or not (do so) anyways etc anyways etc anyways etc)) todo: space victory removed, it's too tedious to do, instead the USA is the
only civ who wins if they build the programme Appolo, make sure to keep them in
check
- some special units are changed: the USA's Navy Seal or some other units are
not relevant soon enough, or/and not accurate (enough), replaced with a sooner
unit for example todo
- religion "taoism" has been renamed to "daoism" and all related entries (temple
and other buildings, units such as missionary etc, and description/history in
sevopedia and such), i have heard many times of the "Dao" (or read maybe rather
anyways etc) in manhua (translated) but never ever saw "Tao", while both seem
correct as chinese translitterations if am not mistaken, it seemed that Dao is
perhaps more fit, but in all cases even if not i'd rather use this one i'm more
famililar with and that makes more sense to me, hopefully clearer for others or/and
maybe not anyways etc
- shrines now require a religion to be built, for example the daoist shrine now
(also) requires to have the daoism religion, and not just own the holy city, this
way the shrine can appear in the sevopedia religion new buildings panel (see the [README_Sevopedia_Reworks.md#example-5-religion-category](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md#example-5-religion-category)),
but also seems to make more sense unless i am mistaken or/and it (may?) create other
issues possibly or maybe not, then (i'd) try it and see, this means for example
conquerring a city is now not enough to build a shrine, you need the specific
religion for it, which again seems to make more sense to me too so maybe an all in
all better change, unless i am mistaken, but try and see, maybe works well or maybe
not or yes or other, anyways etc
- shrines now also require a tech to be built, which is their religion's tech requirement. This allows to make shrines to also appear in tech tree, plus now shrines cannot be built without also having the religion's tech matching (for example during conquest or such, anyways etc), since shrines are not special buildings unlike temple, monastery, cathedral, maybe this is a fine even desirable way to handle it (in tech tree display, also about the conquest thing or similar or other issues or examples of what may happen but anyways etc as these are world wonders unlike the temple, the monastery, and the cathedral), tech prerequirement for shrines was NONE. See also [README_Known_Issues_In_Base_AdvCiv_Civ4.md#13---now-fixedreworked-as-an-appendix-to-12---just-before-anyways-etc-shrines-now-also-appear-in-tech-tree-at-their-religions-tech-requirement-unlike-in-base-advciv--civ4-too-if-i-am-not-mistaken-anyways-etc](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#13---now-fixedreworked-as-an-appendix-to-12---just-before-anyways-etc-shrines-now-also-appear-in-tech-tree-at-their-religions-tech-requirement-unlike-in-base-advciv--civ4-too-if-i-am-not-mistaken-anyways-etc) for details if any more than this are there anyways such as the/some anyways etc screenshots or and such or and not anyways etc
- one new religion, paganism is added, confucianism is removed, maybe more early
wars, also historically more relevant/+/-accurate too i think
- fixed many religious inaccuracies in leaders, at least some or those i could spot
with (being) enough certainty (certain enough) anyways etc, for example frederick
the great was agnostic not christian, brennus seems to have leaned more towards no
religion in gaul than paganism (not an accuracy just did not make him auto pagan)
if i am not mistaken, cyrus not religious pagan but darius is, seemingly, chruchill
not being so and really christian that he would (strongly (enough)) prefer it over
other religions, (if i am not mistaken about these or/and others) anyways etc, see
[notes_about_religious_design.txt](/_1_AdvCiv-SAS/Docs_And_Appendixes/notes_about_religious_design.txt)
for details
- in particular, an important nuance, is that a leader can prefer a religion without
having said religion himself/herself/itself, for example genghis khan seems to have
been tengrist something if i am not mistaken anyways etc, but (see notes linked above
for details) still seems to have had a quite strong liking/preference for daoism, especially
if he had to choose a religion among those in civ4, including none or daoism, if i am not
mistaken about the recollection and analysis i read, so is jsut my opinion not necessarily
accurate but convenient to fill daoism if accurate enough, and maybe accurate too in
general anyways etc
- religion is very important: unlike in civ4 where they are very similar, now
each religion has specific bonuses (for example paganism gives slavery bonuses,
but buddhism gives science bonus), also the cathedrals have been removed (too
much clutter, and now the monasteries are called "Altars", very strong buildings
so you must (i think) pay a lot of attention to religion and consider which one
you want)
- later in the game, neo religion, for example judaism has a neoreligion zionism
(even though not strictly religious), islam has jihad, with big bonuses, just
as in real life, even in modern eras, religions continue to play a big part in
politics and society, for better or worse, i think though
- the techs are mostly the same, they have been completely reordered to better
fit historical accuracy (see timeline i provided too, should be very accurate
now or much more), for example metal casting is before bronze age, the wheel
before pottery, and currency before mathematics. Hopefully should be quite fast
to adjust ideally, it is really the same techs for most at historical points
- gradual gameplay: slower early game, faster late game (less of a chore too
now maybe)
- Handicap (i.e. difficulty) settings are now gradually harder, lower/lowest handicap being harder, and highest difficulties being less of a grind and hard in their own ways at least in theory, see docs for details and status update on these or/and xml for details.
- AIs get no free techs now, todo, they should perform well enough, and receive other
types of bonuses, that they don't need techs for free, it won't feel anymore like they
are playing a different kind of game hopefully, also less of a grind at higher difficulties
(but hard in different ways todo)
- difficulties have also been adjusted in that lower difficulties are harder (i don't
want them to be placeholders anymore), and harder ones less of a grind (ideally),
consider starting at a low difficulty to adjust first if not sure or to get used to
the gameplay
- costs of tech and units (todo and iTrainPercent) are always the same for the human player at all handicap/difficulties settings unlike in base AdvCiv, now only AI costs (and iAITrainPercent) vary across difficulties anyways etc, maybe it helps for example for calculations and such to have a fixed unit or tech (todo) price at all difficulties if you want to go from one difficulty to the other, a unit or tech is always same price for the human player, so you can reuse some strategies more easily maybe or quicker adjust
- there are some exceptions to this, for example iUnitCostPercent and iAIUnitCostPercent (maintenance in gold per turn for the units if i am not mistaken anyways etc) are now in advciv-sas the same for all players, this is to allow for a fairer gameplay and more reliable at all difficulties, difficulty is adjusted indirectly or and through other parameters/settings to make game more or less hard(er?) accross difficulties, but i wanted the unit maintenance (gold per turn ) cost especially to be closer at all difficulties, now exactly the same, see xml or handicap data table (see above at head of this doc for link to the table of all difficulties). Note: when it comes to military hammer cost, it still varies accross difficulties for AI players, but should feel closer now while hopefully still a challenging challenge iff i may say repeatedly but anyways etc, similar reasoning for tech beaker/i.e. flat gold cost (i('d?) (anyways etc)) need to balance them though now if i want and if not already done after writing this anyways etc, please check docs xml or better or additionally maybe too anyways etc maybe also the handicap data table (link at head of this doc anyways etc) 
- i intend this AdvCiv-SAS mod to be quite fast paced anyways etc but still long enough to hopefully enjoy it (view docs for details if any more docs or details exist), game starts at -50 000 BC but it increments very fast (5 000 per turn then gradually less, so after a few dozen turns approximately at normal speed you should already be at the bronze age) (view docs or ingame for latest updated info anyways etc), see also for more details [README_Tech_Tree.md](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Tech_Tree.md). Then the year number and gameplay pace does not slow as much (at least i tried to make it so, that each end game turn doesn't take ages)
- some units can be built at different times, also for historical accuracy
- otherwise simple gameplay, i don't like clutter
- opportunistic and efficient AI: the AI will not be much more aggressive than
AdvCiv, it will be more cautious to start wars, but will hesitate less when it
(thinks it can) profit, so be careful and plan well
- overall not too much clutter, i don't want too many things, but i want the things i
have/add, to go (very) in depth in them rather, so quite lightweight and hopefully
easy to digest and get used to it, but deep that you'd want to play it more, maybe, ideally
- todo animals can be captured?
- some convenience and quality of life changes: for example WFYABTA ("We fear you are
becoming too advanced" is now renamed as "We fear you are trading more than us", but
it is exactly the same effect, just it is not related to tech pace at all (i was 4 techs
behind from an AI if i remember correctly but still got this message from it, after some
(frustrating) research i found it is not related to tech advancement but how much you
trade with all players (trade less and it will/should(?) fade eventually))), also some other
fixes about "the forge has been destroyed" when it was sometimes not destroyed misleading
messaged tweaked to something not misleading (for example "The forge has caught fire"),
cavalry at rifling not military tradition todo may change, clearer sevopedia with new
menus such as types of ressources, victory conditions, and tweaked existing ones to be
clearer or/and easier to navigate hopefully, i hope this helps.
- enabled floodplains after raze, hopefully they (previous city (owners) developped the
land well enough that it can still be profitable, also for more relaxed and interesting
gameplay, i would want the difficulty to be elsewhere, not in such tedious things)
- voluntary vassals are permanent, think of their culture being absorbed by the empire,
and them merging with the empire, becoming its citizens, so pay attention to that, and
if you don't want it to happen to other rivals, plan your strategy based on that maybe
- rebalanced great artist: nerf/reduce early bomb culture instant culture gain from 700 to 500 per era, and increase culture per turn for long term victory culture path or and other uses from 12 to 18 per turn anyways etc
- unlike in AdvCiv, we love the king chance is restored, i think it's a cool mechanic
and also pleasant for the player, maybe realistic too, so if it can happen all good
(feels good in civ3 for example at least from/in my experience playing it)
- unless specified otherwise, the source for the Sevopedia content, the place text panels
(history text panel generally if i am not mistaken) is more often than not and in most
cases Wikipedia. Info may be reordered and slightly edited or more heavily so, not saying
it everytime (that the source is wikipedia) to reduce tediousness of saying it and writing
everytime, while hopefully not reducing game immersion for the player too. Sometimes i
quote from other sources or make addition of my own, some of these sources may be found
in the [docs](/_1_AdvCiv-SAS/Docs_And_Appendixes/) or/and in other places of this AdvCiv-SAS
mod hopefully, or you (or it in general anyways) could maybe be googled (or search engine
of your choice or preference or some other way) by typing bits of the text content and
hopefully finding the source for the rest. It may be a bit (too) tedious for me to
compile/gather all these sources, but some of them can be found, if not most, in the docs
spread at different places. Hopefully this is convenient enough or not too inconvenient
so that i can focus more on gameplay changes and such, and maybe helps the player too
(immersion, or more indirectly more content and such since i can focus more on other
things but not promised, may or not, ideally would, but doing as i want or not, i hope
this helps though, anyways)

- todo continue

# README_Sevopedia_Reworks.md

Below are the details on how the tech tree was made in/for AdvCiv-SAS as well as links to other related docs in AdvCiv-SAS or/and external sources as well if any anyways etc.

If any images below in this readme mention a google drive link, you can access it from main readme's entire google drive folder link, or for convenience access directly closest google drive folder at least as of now here in [Misc 0.x file images google drive folder link](https://drive.google.com/drive/folders/1-s26vjr5m9J9vPTIH-kSwpgkoqjmMjl2?usp=sharing) anyways etc.

## Current Tech Tree ingame

<img src="../Images_In_General/misc_0.x/0.34_Techtree_ingame (1).JPG" alt="0.34_Techtree_ingame (1).JPG" width="250"></img>
<img src="../Images_In_General/misc_0.x/0.34_Techtree_ingame (2).JPG" alt="0.34_Techtree_ingame (2).JPG" width="250"></img>
<img src="../Images_In_General/misc_0.x/0.34_Techtree_ingame (3).JPG" alt="0.34_Techtree_ingame (3).JPG" width="250"></img>
<img src="../Images_In_General/misc_0.x/0.34_Techtree_ingame (4).JPG" alt="0.34_Techtree_ingame (4).JPG" width="250"></img>

## Additional info about the tech tree anyways etc

In AdvCiv-SAS, history starts at -50 000 BCE (may not be accurate if not latest updated, view `<DefineName>START_YEAR</DefineName>` in (adjust to your mod path) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GlobalDefines_advc.xml`, and the code comment just before `<GameTurnInfos>` (or/and the code in this xml tag too if i am not mistaken that this is indeed an xml tag anyways etc anyways etc anyways etc...) in (adjust to your mod path similarly/as well anyways etc...) `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\XML\GameInfo\CIV4GameSpeedInfo.xml`) and quickly spans until bronze age, then gradually slowing down in the process (as in civ4 (base advciv too?) (Anyways etc)), perhaps a bit more gradual and less very slow endgame perhaps todo or would not be done or yes would be or other but anyways etc.

At first and before doing a/the (more) simplified tech tree above, the original tech tree approach i had in mind for AdvCiv-SAS was a more complicated or rather complex one (see [README_Tech_Tree.md#abstract-timeline-tech-tree](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Tech_Tree.md#abstract-timeline-tech-tree)) but anyways etc.

But while refining it and drafting several versions (see also the [misc_0.x](/_1_AdvCiv-SAS/Images_In_General/misc_0.x/) for details or other alternative versions anyways etc) or the google drive of the mod (link in [the main README.md](/README.md) anyways etc), i found it more desirable/suitable for AdvCiv-SAS, at least would be how i want to do it rather but anyways etc, to have less inefficient techs (alphabet, paper, that slow the tech progress for no real key tech progress, hindering the feeling of progression for the player perhaps at least for me and making it a drag, making it also less likely to reach end game (modern and such era/techs anyways etc as is too tedious and long among other reasons or not anyways etc at least for me perhaps others or not or yes but in all cases or not or yes or other anyways etc, anyways etc)), repurposing them where i want more relevant techs (consitution, medicine in early eras for example, naturalism in renaissance anyways etc), AI tech ideally too if we do in modern or future/robotic era if we implement it partly or entirely even if just the techs or maybe an actual era too but in allc cases anyways etc.

So i hope this more efficient tech tree helps have a smoother game experience for players at least me, and make it more likely and less tedious to reach endgame in an enjoyable way at least to me if not other shopefully or maybe (they) would not but (anyways etc) anyways etc, among with other AI changes or/and other changes as well in AdvCiv-SAS that maybe help (achieve) that or get closer to that goal but anyways etc, anyways etc

## More info on notes

View also notes files that have tech in their name, or and other notes files that while not directly named with "tech" in their filename, may also contain directly or indirectly related tech information (ideally i should have (more maybe anyways etc or not or yes or etc or and other or and not anyways etc separated the info, but sometimes also the info is intertwined so not possible to separate unless duplicating the info, so or/and i hope there is still enough info in these docs hopefully or not but anyways etc...))

These files include (may not be exhaustive in case i forgot some or maybe i didn't but anyways etc...) (note: see them in the mod's google drive to view the file and for details anyways etc, some text in them is not updated or not relevant anymore, some of it should be informative about some technological choices in advciv-sas if i may say and if i am not mistaken hopefully helpful or not or yes or other or etc but anyways etc anyways etc anyways etc):

- notes_about_tech_design_choices.txt
- notes_about_tech_design_indirect_associations.txt
- notes_about_tech_design_swapped_simplified_tree.txt
- notes_about_techs_civ4_to_remove_or_replace_or_add.txt

## Abstract timeline tech tree

(click on google drive link at top of this readme to view it on google drive rather at full size anyways etc)

![0.33_Techtree_modified.png](https://drive.google.com/thumbnail?id=1XZqhjw0PFoBR2YY0M7uhtddSeo2kinWo&sz=w4000)

As explained in the [README_Tech_Tree.md#more-info-on-notes](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Tech_Tree.md#more-info-on-notes) section just above, there are more details there (i.e. in these notes anyways etc about why and how the tech tree was made as such anyways etc)

## Earlier prototype / alternative version

Very early before starting to develop this advciv-sas mod (not long before it), i had made this prototype reworked tech tree that is done only by swapping techs (click on google drive link at top of this readme to view it on google drive rather at full size anyways etc)

(click on google drive link at top of this readme to view it on google drive rather at full size anyways etc)

![0.30_tech_tree_mini.jpg](https://drive.google.com/thumbnail?id=1ySmVauqYXmBKJhHKwLMFGvnoVaVkmpXL&sz=w4000)

It is actually what motivated me to start the mod, at least one of the reasons, along with sadly not being able to change easily enough base advciv with my contributions/suggestions (see [README.md#authors](/README.md#authors) for bit more details anyways etc) and realizing with my exchanges or not with @f1rpo main advciv maintainer that indeed i could do it in my own mod rather and not be limited rather than force myself to align with base advciv enough, and also being dependent on them/the base advciv mod being responsive enough as i'd want and was ready and motivated for in this case at least but anyways etc.

It is also painful times as this project could not be implemented and i had to abandon it, but it was not lost if i may say as a lot of the new reworked tech tree took inspiration on this original idea even though i changed it quite a bit since then, it was also a lot of fun to do and very challenging as i did it all in one day i mean anyways etc with no other modification allowed than swapping and replacing techs (total num the same i mean anyways etc). More details as well here in [AdvCiv/pull/10](https://github.com/f1rpo/AdvCiv/pull/10) even though is bit painful to remember sharing for exhaustiveness and as something to look back on for me at least and in this case anyways etc. Actually quite lto painful not sure if i'll keep it longterm in the readme, maybe will or maybe not if too tedious to remember to remove will see but anyways etc, but for now i want to add this, anyways etc, is also good opportunity to make mod lighter by removing such heavy unnecessary images since we dont use them as much but helpful to reference to everywhile if i am reworking the tech tree maybe or not if i may say but anyways etc (i could have directly removed them entirely but useful at least for now to have them here if not for always or maybe not, but is as it is for now at least regardless of how it will be or not in the future, hopefully helpful and informative at least to me even though bit painful but anyways etc.)

## Earlier but much later version

Then if i am not mistaken much later i did this swapping based version but that was based or/and closer (i don't remember exactly but i think it was as such anyways etc) on the abstract time line that is shown in this section as well, if i am not mistaken, i thought i could gain some benefits from representing the tech tree in real civ4 design before reworking it, which i think helped to more easily visualize how techs could fit and their effects and such (even though it's essentially the same info dispalyed in another way, it helped to organize it and such as well and reflect on it if i remember or/and guess how it went correctly anyways etc, it may have also helped to visualize a bit too even if less and was not too long considering it was mostly matching previous prototype and abstract timeline if i am not mistaken from my memories of it i mean but anyways etc anyways etc anyways etc), before we used the real ingame reworked tech tree as in docs, if i am not mistaken this is how it went i mean and why, not 100% sure but quite close in this case i mean but anyways etc.

(click on google drive link at top of this readme to view it on google drive rather at full size anyways etc)

![0.30b_tech_tree_mini_temp.png](https://drive.google.com/thumbnail?id=1e42RDsufVEuBpY9ZVii2uFC65wXP-wnt&sz=w4000)

## Starting techs rework

As it is too lengthy to put in the [README_Quick_Get_Started_Guide.md](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Quick_Get_Started_Guide.md), here are how we changed the starting civ techs in our mod

### before most recent as of now rework anyways etc

#### main table (chatgpt 5 written anyways etc) - before change anyways etc

Done amazingly by chatgpt 5 (numbers are line in our xml civilization info file as of now anyways etc), check if accurate and thanks a lot chatgpt 5 and thanks to my prompt and such too if i may say but anyways etc

| Civ                      | Lines       | FreeTechs                               | Allowed-only? |
|--------------------------|-------------|------------------------------------------|---------------|
| America                  | 9–142       | 109→Fishing, 113→Agriculture             | ❌            |
| Arabia                   | 143–244     | 219→The Wheel, 223→Mysticism             | ❌            |
| Aztec                    | 245–346     | 321→Mysticism, 325→Hunting               | ✅            |
| Babylon                  | 347–452     | 427→Agriculture, 431→The Wheel           | ❌            |
| Byzantium                | 453–562     | 537→The Wheel, 541→Mysticism             | ❌            |
| Carthage                 | 563–669     | 644→Fishing, 648→Mining                  | ✅            |
| Celt                     | 670–784     | 755→Hunting, 759→Mysticism               | ✅            |
| China                    | 785–898     | 869→Agriculture, 873→Mining              | ❌            |
| Egypt                    | 899–1024    | 995→The Wheel, 999→Agriculture           | ❌            |
| England                  | 1025–1136   | 1103→Fishing, 1107→Mining                | ✅            |
| Ethiopia                 | 1137–1256   | 1215→Hunting, 1219→Mining                | ✅            |
| Kingdom of Benin         | 1257–1366   | 1341→Mysticism, 1345→Fishing             | ✅            |
| France                   | 1367–1480   | 1447→The Wheel, 1451→Agriculture         | ❌            |
| Germany                  | 1481–1603   | 1574→Pottery, 1578→Mining                | ✅            |
| Greece                   | 1604–1718   | 1689→Fishing, 1693→Hunting               | ✅            |
| Holy Roman               | 1719–1830   | 1805→Mysticism, 1809→Hunting             | ✅            |
| Inca                     | 1831–1931   | 1906→Agriculture, 1910→Mysticism         | ❌            |
| India                    | 1932–2098   | 2069→Mysticism, 2073→Mining              | ✅            |
| Japan                    | 2099–2199   | 2174→Fishing, 2178→The Wheel             | ❌            |
| Khmer                    | 2200–2307   | 2282→Hunting, 2286→Mining                | ✅            |
| Korea                    | 2308–2404   | 2379→Mining, 2383→Mysticism              | ✅            |
| Mali                     | 2405–2500   | 2475→The Wheel, 2479→Mining              | ❌            |
| Maya                     | 2501–2610   | 2585→Mining, 2589→Mysticism              | ✅            |
| Mongol                   | 2611–2713   | 2684→The Wheel, 2688→Hunting             | ❌            |
| Native America           | 2714–2829   | 2804→Agriculture, 2808→Fishing           | ❌            |
| Netherlands              | 2830–2942   | 2917→Agriculture, 2921→Fishing           | ❌            |
| Ottoman                  | 2943–3048   | 3019→The Wheel, 3023→Agriculture         | ❌            |
| Persia                   | 3049–3183   | 3154→Agriculture, 3158→Hunting           | ❌            |
| Portugal                 | 3184–3294   | 3269→Fishing, 3273→Mining                | ✅            |
| Rome                     | 3295–3419   | 3390→Fishing, 3394→Mining                | ✅            |
| Russia                   | 3420–3531   | 3498→Hunting, 3502→Mining                | ✅            |
| Spain                    | 3532–3638   | 3613→Fishing, 3617→Mysticism             | ✅            |
| Sumeria                  | 3639–3742   | 3716→Mysticism, 3720→Pottery             | ✅            |
| Scandinavia              | 3743–3847   | 3822→Fishing, 3826→Hunting               | ✅            |
| Zulu                     | 3848–3949   | 3924→Agriculture, 3928→Hunting           | ❌            |
| Minor                    | 3950–4087   | 4046→Mining, 4050→Mysticism, 4054→Fishing, 4058→The Wheel, 4062→Agriculture, 4066→Hunting | ❌ |
| Barbarian                | 4088–EOF    | 4487→Pottery, 4491→Fishing, 4495→Seafaring, 4500→Masonry | ❌ |

#### Global tech totals (should sum to 70 = 35 civs × 2) - before change anyways etc

Without counting barbarians and minor, the total count among civs is as of now (thanks to chatgpt 5 too and my prompt and such too hehe but anyways etc):

Allowed starting techs

- Mining:     13
- Fishing:    12
- Mysticism:  12
- Hunting:    11
- Pottery:     2

### after most recent as of now rework anyways etc

After a few or quite many back and forth and reviewing rounds with chatgpt 5 which helped me tons but also me hehe and my own ideas but it helped lot too but anyways etc, here are (below but anyways etc) the adjusted starting techs for civs as of now in advciv-sas, written by chatgpt 5. This was mostly to remove/replace old now removed tech_agriculture and tech_the_wheel starters that are now no longer starting techs, as well as quite along with it rebalance it and rework it all if i may say but anyways etc. I think the result is really good at least much better than it was check if accurate anyways etc.

#### main table (chatgpt 5 written with some tweaks from me but anyways etc)

Goals: (1) stay historically/thematically sane, (2) avoid **too many repeats** of the same pair, and (3) **not too many “amazing” pairs** like **Mining+Hunting** (early rush spike) and **Mining+Pottery** (eco+production spike) — while keeping **quite a few enough** for clear identity/variety.

Note: **Fishing+Mining is fine** (Fishing is weakest), so we use it without concern as long as there is not too much of it.

| Civ               | Old FreeTechs                 | New FreeTechs                 | Rationale |
|-------------------|-------------------------------|-------------------------------|-----------|
| America           | Fishing, Agriculture          | **Fishing, Hunting**          | Drops disallowed Agriculture. Frontier/scouting flavor; modest econ. *Avoids Mining+Hunting / Mining+Pottery.* |
| Arabia            | The Wheel, Mysticism          | **Mysticism, Pottery**        | Replaces Wheel. Oasis trade + early religion; balanced culture/commercial start. *Avoids Mining+Pottery.* |
| Aztec             | Mysticism, Hunting            | **Mining, Mysticism**         | **Jaguar** now at Bronze Working → Mining speeds access. Mysticism matches ritual/state culture. We **avoid Mining+Hunting** to curb rush. |
| Babylon           | Agriculture, The Wheel        | **Pottery, Mysticism**        | **Bowman** is now **Longbow-class** at Construction. Pottery fits the Masonry → Construction lane (bricks, aqueducts, Hanging Gardens), while Mysticism preserves the temple/garden flavor. |
| Byzantium         | The Wheel, Mysticism          | **Mysticism, Fishing**        | Bosporus/seaborne empire + spiritual tone; removes early-road snowball. |
| Carthage          | Fishing, Mining               | **Fishing, Pottery**          | Maritime commerce + cottages; **drops Mining** to lower early snowball and reduce pair repetition. |
| Celt              | Hunting, Mysticism            | **Hunting, Mining**           | **Gallic Warrior** metallurgy path justified; shifts from “druidic” to martial. **Intentional strong pair** (Mining+Hunting) for civ-specific unit identity; kept rare overall. |
| China             | Agriculture, Mining           | **Mining, Pottery**           | Bronze/iron + ceramics traditions; we keep this as **one of the few** strong **Mining+Pottery** pairs for identity. |
| Egypt             | The Wheel, Agriculture        | **Hunting, Pottery**          | Keep **Pottery** to flow into **Masonry → Construction** (builder identity: Pyramids, aqueducts, etc.). Add **Hunting** to align the **War Chariot** path. |
| England           | Fishing, Mining               | **Fishing, Mining**           | Industrial metals identity fits; Fishing+Mining is acceptable (Fishing is weakest). Also avoids overusing Mining+Pottery. |
| Ethiopia          | Hunting, Mining               | **Hunting, Mysticism**        | Highlands/faith; **removes Mining+Hunting** spike while keeping early defense. |
| Kingdom of Benin  | /                             | **Mysticism, Fishing**        | Coastal trade + religious courts; already balanced and flavorful. |
| France            | The Wheel, Agriculture        | **Hunting, Pottery**          | Aristocratic hunt + towns; replaces disallowed pair. |
| Germany           | Pottery, Mining               | **Pottery, Mining**           | Crafts + metalwork flexibility. **One of the few** Mining+Pottery we keep (Old World metallurgy). |
| Greece            | Fishing, Hunting              | **Fishing, Mysticism**        | Still coastal/Aegean, but we emphasize oracles/cults/philosophy. Avoids Mining+Pottery/Hunting spikes. |
| Holy Roman        | Mysticism, Hunting            | **Mysticism, Hunting**        | Clerical legitimacy + levies; varied without Mining spikes. |
| Inca              | Agriculture, Mysticism        | **Pottery, Mining**           | Andean mining/metallurgy (copper, arsenical bronze; large-scale gold/silver extraction) + state logistics makes Mining a great fit. Also supports Quechua @ **Iron Working** |
| India             | Mysticism, Mining             | **Mysticism, Mining**         | Spiritual tradition + engineering; not an “amazing” pair. |
| Japan             | Fishing, The Wheel            | **Fishing, Hunting**          | Keeps maritime identity; **Jōmon hunter-gatherer** roots make Hunting plausible. Avoids adding another Mining+Pottery or Mining+Hunting. |
| Khmer             | Hunting, Mining               | **Fishing, Hunting**          | Tonlé Sap/Mekong fisheries + elephants/camps; **removes Mining+Hunting** rush spike. |
| Korea             | Mining, Mysticism             | **Mining, Mysticism**         | Metalwork/engineering + Confucian culture; solid, non-“amazing” pair. |
| Mali              | The Wheel, Mining             | **Hunting, Pottery**          | **Skirmisher** is now **Longbow-class** at Construction. Hunting keeps the Sahel skirmisher/camp identity; Pottery sustains early commerce while beelining Construction. They don't need mining as much for their civ-specific unit. |
| Maya              | Mining, Mysticism             | **Mysticism, Pottery**        | Classic Maya = obsidian/chert/jade; metals are late/minor. Holkan @ Bronze Working (Mining line) remains reachable, but early Pottery better fits their builder profile and ramps Ball Court @ Construction, while Mysticism matches ritual/astronomy and supplies early culture. |
| Mongol            | The Wheel, Hunting            | **Hunting, Mysticism**        | Pastoral steppe with early horses: Hunting → Animal Husbandry → Mounted Combat (and Barracks @ Hunting in AdvCiv-SAS), which also matches their aggressive-leaning leader profiles; Mysticism reflects Tengri/shamanic cohesion and supplies early culture/monuments to claim steppe space. |
| Native America    | Agriculture, Fishing          | **Hunting, Mining**           | Replace inland Fishing with Mining (abstracts obsidian/flint/quarries). **Dog Soldier** benefits from the Bronze Working line. Adds one OP pair by design; helps identity. |
| Netherlands       | Agriculture, Fishing          | **Fishing, Pottery**          | Maritime commerce + early cottages; *no Mining* for a gentler opener. |
| Ottoman           | The Wheel, Agriculture        | **Fishing, Pottery**          | **Fishing** to reflect an early maritime footprint on the **Aegean**, **Sea of Marmara** (Bosporus), **Black Sea**, and the **eastern Mediterranean**. Pair with **Pottery** to support early crafts/urbanization and a builder-empire profile. They don't need as much strong starting techs for their civ-specific unit that is later in the game. |
| Persia            | Agriculture, Hunting          | **Hunting, Mining**           | Nearer to **Iron Working** path in your tree; strong metallurgy tradition. We accept one more OP pair for identity; totals remain balanced. |
| Portugal          | Fishing, Mining               | **Fishing, Pottery**          | Age-of-Discovery maritime commerce; Mining ceded to reduce repetition and fund other civs’ thematic needs. |
| Rome              | Fishing, Mining               | **Fishing, Mining**           | Metals for **Legionary** timing; avoids Hunting and Mining+Pottery extremes. |
| Russia            | Hunting, Mining               | **Pottery, Mining**           | Land-empire emphasis (settlement/crafts) and less “fishy” opening. Keeps metal identity; also offsets Ottoman’s change to keep 14/14/14/14/14 totals. |
| Spain             | Fishing, Mysticism            | **Fishing, Mysticism**        | Maritime reach + organized religion; avoids Mining spikes. |
| Sumeria           | Mysticism, Pottery            | **Mysticism, Mining**         | **Vulture** (axe) loves metals; still not the “amazing” Mining+Pottery/Hunting. |
| Scandinavia       | Fishing, Hunting              | **Fishing, Hunting**          | Seafaring + raiding/hunting; balanced opener without Mining; keeps variety. |
| Zulu              | Agriculture, Hunting          | **Hunting, Mining**           | **Intentionally keep an OP pair (Mining+Hunting)** for **Impi** flavor/identity; brings Agriculture into compliance. |

#### Global tech totals (should sum to 70 = 35 civs × 2)

| Tech      | Count |
|-----------|-------|
| Fishing   | 14    |
| Hunting   | 14    |
| Mysticism | 14    |
| Pottery   | 14    |
| Mining    | 14    |

#### Starting pair counts (canonicalized; order-insensitive)

| Pair                   | Count |
|------------------------|-------|
| Mining + Mysticism     | 4     |
| Fishing + Hunting      | 4     |
| Fishing + Mysticism    | 4     |
| Fishing + Pottery      | 4     |
| Hunting + Mining       | 4     |
| Mining + Pottery       | 4     |
| Hunting + Pottery      | 3     |
| Mysticism + Pottery    | 3     |
| Hunting + Mysticism    | 3     |
| Fishing + Mining       | 2     |

**Sanity checks:**

- Pair counts sum to **35** civs.  
- Tech totals sum to **70** picks (5 techs × 14 each). ✅

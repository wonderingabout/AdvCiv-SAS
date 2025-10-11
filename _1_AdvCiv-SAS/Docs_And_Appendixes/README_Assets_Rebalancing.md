# README_Assets_Rebalancing

Some of the asset rebalancing is shown here (not exhaustive)

## Menu

Below is the menu, generated thanks to chatgpt (as of now i'm using chatgpt 5 which does this very well and fast anyways etc among other versions who/which could or not but anyways etc), feeding it the global search results of these entries and telling the format of the entries :), and then i adjusted a bit after but anyways etc. Hopefully helpful, thanks a lot chatgpt 5 hehe (among other versions or not had i tried with them but anyways etc). If you're curious how i did it, see this [google drive folder link](https://drive.google.com/drive/folders/1B18cJ8GYD8X_0vMoiTihVz0tthg5m_sg?usp=sharing) 's screenshots for details, hopefully helpful or not or yes or etc anyways etc

[Starting techs rework](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#starting-techs-rework)  
[Leaders' traits rework](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#leaders-traits-rework)  

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

## Leaders' traits rework

While doing/considering in this case i mean but anyways etc the holy roman empire civ-specific unit's rework or replacement, i have noticed charlemagne's traits were not in accord with his historical profile (i asked chatgpt 5 thanks since i don't know too much if at all aobut his history and leader profile or/and such and to be sure and have its advice as well thanks but anyways etc).

It is also limiting when we want as now to assign a new unit e.g. to the holy roman empire or possibly building, so i thought this was a good time to rework leader traits for balance, accuracy, and overall synergy with the civ's profile, as well as its civ-specific units and buildings, and also to match ingame behaviour +/- more(/most? But anyways etc) importantly xml or and such if / as much as possible or relevant i mean if i may say but anyways etc.

Done with the help of chatgpt 5 thanks a lot and thanks to my prompts too and/or adjustments and/or thoughts in this case i mean but anyways etc and/or formatting and/or such but anyways etc, check if accurate in this case i mean but anyways etc.

### previous state

This is extracted from the [CIV4LeaderHeadInfos.xml](/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml) rather but anyways etc, as we had issues importing it from our custom leaders_data_to_csv or/and it took too much time, due to data being too big or/and such i guess maybe if i'm not mistaken i mean in this case but anyways etc.

#### main table before changes to traits anyways etc

| Leader | Traits |
|---|---|
| Alexander | Philosophical, Aggressive |
| Asoka | Spiritual, Organized |
| Augustus | Imperialist, Industrious |
| Bismarck | Expansive, Industrious |
| Boudica | Charismatic, Aggressive |
| Brennus | Spiritual, Charismatic |
| Catherine | Creative, Imperialist |
| Charlemagne | Imperialist, Protective |
| Churchill | Charismatic, Protective |
| Cyrus | Charismatic, Imperialist |
| Darius | Organized, Financial |
| De Gaulle | Industrious, Charismatic |
| Elizabeth | Philosophical, Financial |
| Ewuare | Imperialist, Spiritual |
| Frederick | Philosophical, Organized |
| Gandhi | Spiritual, Philosophical |
| Genghis Khan | Aggressive, Imperialist |
| Gilgamesh | Protective, Creative |
| Hammurabi | Organized, Aggressive |
| Hannibal | Financial, Charismatic |
| Hatshepsut | Spiritual, Creative |
| Huayna Capac | Industrious, Financial |
| Isabella | Spiritual, Expansive |
| Joao | Imperialist, Expansive |
| Julius Caesar | Organized, Imperialist |
| Justinian | Spiritual, Imperialist |
| Kublai Khan | Aggressive, Creative |
| Lincoln | Philosophical, Charismatic |
| Louis XIV | Industrious, Creative |
| Mansa Musa | Spiritual, Financial |
| Mao Zedong | Expansive, Protective |
| Mehmed | Expansive, Organized |
| Moctezuma | Aggressive, Spiritual |
| Napoleon | Organized, Charismatic |
| Pacal | Financial, Expansive |
| Pericles | Philosophical, Creative |
| Peter | Philosophical, Expansive |
| Qin Shi Huang | Industrious, Protective |
| Ragnar | Financial, Aggressive |
| Ramesses | Spiritual, Industrious |
| Franklin Roosevelt | Industrious, Organized |
| Saladin | Protective, Spiritual |
| Shaka | Aggressive, Expansive |
| Sitting Bull | Philosophical, Protective |
| Stalin | Industrious, Aggressive |
| Suleiman | Imperialist, Philosophical |
| Suryavarman | Expansive, Creative |
| Tokugawa | Protective, Aggressive |
| Victoria | Imperialist, Financial |
| Wang Kon | Financial, Protective |
| Washington | Expansive, Charismatic |
| Willem van Oranje | Creative, Financial |
| Zara Yaqob | Creative, Organized |

#### raw traits assignment count

| Trait | Count |
|---|---|
| Spiritual | 11 |
| Imperialist | 11 |
| Aggressive | 10 |
| Expansive | 10 |
| Financial | 10 |
| Charismatic | 9 |
| Creative | 9 |
| Industrious | 9 |
| Organized | 9 |
| Philosophical | 9 |
| Protective | 9 |

#### pairs count

| Pair | Count |
|---|---|
| Imperialist + Spiritual | 2 |
| Aggressive + Charismatic | 1 |
| Aggressive + Creative | 1 |
| Aggressive + Expansive | 1 |
| Aggressive + Financial | 1 |
| Aggressive + Imperialist | 1 |
| Aggressive + Industrious | 1 |
| Aggressive + Organized | 1 |
| Aggressive + Philosophical | 1 |
| Aggressive + Protective | 1 |
| Aggressive + Spiritual | 1 |
| Charismatic + Expansive | 1 |
| Charismatic + Financial | 1 |
| Charismatic + Imperialist | 1 |
| Charismatic + Industrious | 1 |
| Charismatic + Organized | 1 |
| Charismatic + Philosophical | 1 |
| Charismatic + Protective | 1 |
| Charismatic + Spiritual | 1 |
| Creative + Expansive | 1 |
| Creative + Financial | 1 |
| Creative + Imperialist | 1 |
| Creative + Industrious | 1 |
| Creative + Organized | 1 |
| Creative + Protective | 1 |
| Creative + Spiritual | 1 |
| Expansive + Financial | 1 |
| Expansive + Imperialist | 1 |
| Expansive + Industrious | 1 |
| Expansive + Organized | 1 |
| Expansive + Philosophical | 1 |
| Expansive + Protective | 1 |
| Expansive + Spiritual | 1 |
| Financial + Imperialist | 1 |
| Financial + Industrious | 1 |
| Financial + Organized | 1 |
| Financial + Philosophical | 1 |
| Financial + Protective | 1 |
| Financial + Spiritual | 1 |
| Imperialist + Industrious | 1 |
| Imperialist + Organized | 1 |
| Imperialist + Philosophical | 1 |
| Imperialist + Protective | 1 |
| Industrious + Organized | 1 |
| Industrious + Protective | 1 |
| Industrious + Spiritual | 1 |
| Organized + Philosophical | 1 |
| Organized + Spiritual | 1 |
| Philosophical + Protective | 1 |
| Philosophical + Spiritual | 1 |
| Protective + Spiritual | 1 |

### new state after rework with rationale and/or such anyways etc

#### main table after changes to traits anyways etc

| Leader | Current Traits | Recommendation | Rationale |
|---|---|---|---|
| Alexander | Philosophical, Aggressive | **Keep** | Philosopher-king + relentless conqueror fits. |
| Asoka | Spiritual, Organized | **Spiritual, Protective** | Edicts focused on welfare/stability: medical care for people & animals, wells/trees, non-violence. Reads as “guardian of the realm’s well-being.” |
| Augustus | Imperialist, Industrious | **Keep** | Empire builder + massive works program. |
| Bismarck | Expansive, Industrious | **Organized, Protective** | Why not Aggressive? He orchestrated three short, limited wars (1864, 1866, 1870–71) to unify Germany, then spent the rest of his career preventing great-power war via alliance webs (Dreikaiserbund, Reinsurance Treaty, Congress of Berlin). That’s sharp power politics, not a “wade-in-and-smash” military persona. He wasn’t a battlefield leader; his hallmark is calculated diplomacy + internal statecraft. What really defines him? Organized: high-efficiency governance—central civil service, Reichsbank, tariffs, and the pioneering social insurance system (health 1883, accident 1884, old-age 1889). This maps perfectly to your “-75% upkeep” / efficient state. Protective (in your mod’s sense = stability/no anarchy/health): post-1871 his entire strategy was systemic risk management (deterrence, balance) and domestically “order first” (Anti-Socialist Laws) plus worker protection through insurance—i.e., protecting the state’s cohesion and people’s welfare. Verdict (accuracy-first): Go Organized + Protective. It captures both the manager-state architect and the stability/health side far better than Aggressive. (Charismatic doesn’t fit his public vibe, and Imperialistic doesn’t match his reluctant, late, and limited colonial stance.) |
| Boudica | Charismatic, Aggressive | **Keep** | War leader rallying tribes; morale + offense. |
| Brennus | Spiritual, Charismatic | **Keep** | Druidic authority + chieftain charisma. |
| Catherine | Creative, Imperialist | **Philosophical, Imperialist** | Enlightened despot: corresponded with Voltaire/Diderot, issued the Nakaz, pushed legal/educational reform—more thinker-ruler than pure arts patron. Philosophical = ideas shaping policy. Catherine is the poster child for Enlightened absolutism: the Nakaz (Instruction), legal/education reforms, heavy engagement with Voltaire/Diderot, commissions on law and schooling. Her brand is “rules by ideas.”. Creative = culture output/patronage. She absolutely patronized the arts (Hermitage, theatre), but that was a means to an ideological/modernizing end, not her core identity. If you want to signal culture yields in gameplay, Creative is fine; historically, it’s secondary to her policymaking. |
| Charlemagne | Imperialist, Protective | **Aggressive, Organized** | Empire via conquest and capitularies/marches/missi dominici. Less settler/colonial growth; more “fight + administer.” Dropping Imperialist narrows the tag to true expansion engines. `<!-- custom: note: this is more controversial/debatable according to chatgpt 5, but i hope it is accurate enough. As for ingame behaviour, he seems to perform nice in some games so i hope this helps mesh better with his more aggressive overall civ4 profile if i'm not mistaken but anyways etc. -->` |
| Churchill | Charismatic, Protective | **Keep** | Wartime morale + defensive strategy. |
| Cyrus | Charismatic, Imperialist | **Keep** | Founder of vast empire; tolerant unifier. |
| Darius | Organized, Financial | **Keep** | Satrapies/roads/taxation; efficient and wealthy. |
| De Gaulle | Industrious, Charismatic | **Charismatic, Organized** | Resistance icon and founder of the Fifth Republic’s institutions. Post-war modernization happened, but his identity is leadership + constitutional/administrative redesign more than building programs. |
| Elizabeth | Philosophical, Financial | **Creative, Financial** | Her era is literally shorthand for a cultural bloom: Shakespeare/Marlowe, theatres, court masques, music, letters. She wasn’t a “philosopher-queen” so much as a savvy ruler who presided over (and patronized) an artistic boom. Keeping Financial also tracks (privateering, merchant ventures, early global trade). |
| Ewuare | Imperialist, Spiritual | **Spiritual, Industrious** | Benin’s strong court/ritual religion. Benin’s strength = urban works (walls/ditches), craft guilds, and court art; expansion via hegemony/tribute more than settler-style growth. Industrious captures that better than Imperialist. |
| Frederick | Philosophical, Organized | **Philosophical, Creative** | Enlightenment/arts over bureaucracy. |
| Gandhi | Spiritual, Philosophical | **Keep** | Canonical fit. |
| Genghis Khan | Aggressive, Imperialist | **Keep** | Archetypal conqueror. |
| Gilgamesh | Protective, Creative | **Keep** | Walls/city defense + epic/civic culture. |
| Hammurabi | Organized, Aggressive | **Organized, Protective** | Lawgiver/city-builder; warfare largely pragmatic/defensive. |
| Hannibal | Financial, Charismatic | **Keep** | Hallmark = operational genius + multi-ethnic army cohesion and Italian defections after Cannae. More “inspire & outmaneuver” than brute-force brutality. Charismatic still supports a war playstyle (cheaper promos) without the raw smash of Aggressive; Financial keeps Carthaginian commerce. |
| Hatshepsut | Spiritual, Creative | **Spiritual, Financial** | Iconic Punt expedition + trade-focused reign; commerce funded temples/works. Her identity reads more “trade & temple economy” than “arts output.” `<!-- custom: also will most likely buff her if i'm not mistaken, which is nice i think if i may say but anyways etc -->` |
| Huayna Capac | Industrious, Financial | **Industrious, Organized** | Inca economy was state-planned and labor-tax (mit’a), not money/market-driven. “Organized” fits roads, storehouses, and redistribution much better than “Financial.” |
| Isabella | Spiritual, Expansive | **Spiritual, Aggressive** | Militant piety + ruthless campaigns; reads truer than “Imperialist.” |
| Joao | Imperialist, Expansive | **Imperialist, Financial** | Maritime commerce + colonial charters; cleaner than Expansive overlap. |
| Julius Caesar | Organized, Imperialist | **Aggressive, Imperialist** | Primary identity = conqueror (Gaul, Civil War). Keep Imperialist for expansion; swap in Aggressive to reflect operational boldness. `<!-- custom: plus matches with xml profile of aggression and thematic epicness if i may say and if i am not mistaken but anyways etc -->` |
| Justinian | Spiritual, Imperialist | **Philosophical, Industrious** | Big reconquests (Africa, Italy, S. Hispania) + colossal building + Corpus Juris Civilis are uncontested. Critics say the reconquest wars/taxation left the state overextended and then the Justinianic Plague hit hard; newer work debates how devastating the plague really was. Net: “restorer & codifier,” but also “overstretched the empire.”. Less “Spiritual,” more “Legal/Scholar + Empire-builder.”. Reconquests ≠ colonization. His lasting mark is legal/intellectual codification + mega building (Hagia Sophia, fortifications), not founding/settler-driven growth. |
| Kublai Khan | Aggressive, Creative | **Imperialist, Creative** | Completed the Song conquest and pursued large overseas campaigns (Japan, Đại Việt/Champa, Burma, Java). Emphasize empire-building/expansion over personal ferocity; keep Creative for patronage/tolerance. |
| Lincoln | Philosophical, Charismatic | **Keep** | Moral/philosophical leadership + national unity. |
| Louis XIV | Industrious, Creative | **Keep** | Palace/works + arts and culture. |
| Mansa Musa | Spiritual, Financial | **Keep** | Pilgrimage/religion + trans-Saharan wealth. He was devout (Hajj, mosques), *and* a patron of learning (Timbuktu/Sankore). |
| Mao Zedong | Expansive, Protective | **Aggressive, Protective** | Mass campaigns and external war (Civil War, Korea), purges, and militant mobilization read more “Aggressive” than “cheap administration.” Protective still captures internal security/defense posture. `<!-- custom: i like this one very much as i think he was very brutal wasn't he xd, from very little i know about him i mean in this case i mean if i may say but anyways etc -->` |
| Mehmed | Expansive, Organized | **Imperialist, Aggressive** | Siege monster and serial conqueror (Constantinople, Balkans, Anatolia); “The Conqueror” leans warlike more than “efficient administration.” |
| Moctezuma | Aggressive, Spiritual | **Keep** | Militarism + ritual/faith. |
| Napoleon | Organized, Charismatic | **Imperialist, Charismatic** | Signature is conquest + continental empire (client states, annexations). He *did* codify/administer, but his core identity isn’t “low-upkeep governance”—it’s expansion + leadership aura. |
| Pacal | Financial, Expansive | **Financial, Industrious** | Monumental architecture/engineering + trade. |
| Pericles | Philosophical, Creative | **Keep** | Golden Age of philosophy and arts. |
| Peter | Philosophical, Expansive | **Imperialist, Organized** | lean warmonger/reformer, not “arts guy.” → Switch to Imperialist, Organized (state-driven expansion + Table of Ranks/navy/army reform) |
| Qin Shi Huang | Industrious, Protective | **Keep** | Great Wall/standardization + legalist control. |
| Ragnar | Financial, Aggressive | **Keep** | Raiding/commerce + martial ferocity. |
| Ramesses | Spiritual, Industrious | **Keep** | Temple/monument builder with priestly legitimation. |
| Franklin Roosevelt | Industrious, Organized | **Industrious, Charismatic** | New Deal public works -> keep Industrious. His defining edge was coalition-building and morale (Fireside Chats, wartime leadership) more than bureaucratic cost efficiency. |
| Saladin | Protective, Spiritual | **Spiritual, Charismatic** | Admired by both sides; unifying religious leadership — not just a “defender.” He led major offensive campaigns (Hattin, Jerusalem) and had broad admiration. Your switch to Spiritual, Charismatic is very defensible; I wouldn’t go back to Protective unless you want to emphasize “shield of Islam” over his rallying aura. |
| Shaka | Aggressive, Expansive | **Aggressive, Organized** | Fits Ikhanda-style admin — “charismatic” in Civ terms can imply inspirational popularity; historically he ruled more by fear/discipline. Your pick Aggressive, Organized is perfect (impi/regimental system + logistics). I wouldn’t use Charismatic here. |
| Sitting Bull | Philosophical, Protective | **Keep** | Visionary/teacher + defensive resistance. |
| Stalin | Industrious, Aggressive | **Keep** | Forced industrialization + ruthless offensives. |
| Suleiman | Imperialist, Philosophical | **Keep** | “Lawgiver” persona + patronage of learning fits Philosophical better than Spiritual for gameplay and history; keeps imperial scope. `<!-- custom: plus if i remember enough i read he was quite areligious or religious open no? If so phi might fit better indeed than spi no? Thanks anyways etc thanks -->` |
| Suryavarman | Expansive, Creative | **Industrious, Creative** | Builder of Angkor; monumental works + culture. |
| Tokugawa | Protective, Aggressive | **Protective, Organized** | After unification, policy emphasized internal order, class discipline, and isolation over external aggression; governance beats battlefield ferocity. `<!-- custom: from a very quick search and my intuition/memory of what i read aobut him, he was very cautious and cunning/scheming rather if i'm not mistaken so maybe aggressive doesn't fit as well but anyways etc; also from a balance standpoint, if he is isolated, he would benefit much more from tax/costs reduction to run smoothly his empire than aggressive right? If i may say i mean but anyways etc. -->` |
| Victoria | Imperialist, Financial | **Keep** | Global empire + finance/trade. |
| Wang Kon | Financial, Protective | **Organized, Spiritual** | this is the softest OP fit. He’s the founder/administrator (Organized, yes), but the “Protective” piece is less uniquely his (many big defensive moments come under successors). Organized + Spiritual: his Ten Injunctions stress protecting Buddhism, geomancy/ritual legitimacy—reads as statecraft grounded in religion. Bottom line: If you want to trim OP without losing accuracy, flip Wang Kon → Organized, Spiritual (history-first, no change to rare Financial) |
| Washington | Expansive, Charismatic | **Protective, Charismatic** | Preservation-first Fabian strategy in the Revolution + 1777 army-wide smallpox inoculation (public-health safeguarding). Still inspirational. |
| Willem van Oranje | Creative, Financial | **Keep** | Tolerance/trade + arts/commerce. |
| Zara Yaqob | Creative, Organized | **Spiritual, Organized** | Strong doctrinal/religious policy + centralized rule — deeply doctrinal, centralizing, sometimes harsh. Spiritual, Organized > Creative. (He wrote and enforced doctrine more than fostering open culture.) |

#### new traits total count

| Trait         | Count |
|---------------|------:|
| Spiritual     |    12 |
| Aggressive    |    12 |
| Imperialist   |    12 |
| Charismatic   |    11 |
| Industrious   |    11 |
| Organized     |    11 |
| Financial     |    10 |
| Protective    |    10 |
| Philosophical |     9 |
| Creative      |     8 |

Sanity: 53 leaders × 2 = 106 total assignments.

#### new pairs total count anyways etc

| Pair | Count |
|---|---|
| Aggressive + Imperialist | 3 |
| Organized + Protective | 3 |
| Aggressive + Organized | 2 |
| Aggressive + Spiritual | 2 |
| Charismatic + Imperialist | 2 |
| Charismatic + Protective | 2 |
| Charismatic + Spiritual | 2 |
| Creative + Financial | 2 |
| Creative + Industrious | 2 |
| Creative + Philosophical | 2 |
| Financial + Charismatic | 2 |
| Imperialist + Charismatic | 2 |
| Imperialist + Creative | 2 |
| Imperialist + Financial | 2 |
| Imperialist + Organized | 2 |
| Industrious + Charismatic | 2 |
| Industrious + Creative | 2 |
| Industrious + Imperialist | 2 |
| Industrious + Organized | 2 |
| Industrious + Spiritual | 2 |
| Philosophical + Aggressive | 2 |
| Philosophical + Charismatic | 2 |
| Philosophical + Creative | 2 |
| Philosophical + Imperialist | 2 |
| Philosophical + Industrious | 2 |
| Philosophical + Protective | 2 |
| Protective + Charismatic | 2 |
| Protective + Creative | 2 |
| Protective + Industrious | 2 |
| Protective + Spiritual | 2 |
| Aggressive + Charismatic | 1 |
| Aggressive + Creative | 1 |
| Aggressive + Financial | 1 |
| Aggressive + Protective | 1 |
| Charismatic + Organized | 1 |
| Creative + Imperialist | 1 |
| Creative + Protective | 1 |
| Financial + Industrious | 1 |
| Financial + Organized | 1 |
| Imperialist + Industrious | 1 |
| Imperialist + Organized | 1 |
| Industrious + Organized | 1 |
| Industrious + Philosophical | 1 |
| Industrious + Protective | 1 |
| Philosophical + Protective | 1 |
| Philosophical + Spiritual | 1 |
| Protective + Spiritual | 1 |

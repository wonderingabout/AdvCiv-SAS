# README_Assets_Rebalancing

Some of the asset rebalancing is shown here (not exhaustive)

## Menu

Below is the menu, generated thanks to chatgpt (as of now i'm using chatgpt 5 which does this very well and fast anyways etc among other versions who/which could or not but anyways etc), feeding it the global search results of these entries and telling the format of the entries :), and then i adjusted a bit after but anyways etc. Hopefully helpful, thanks a lot chatgpt 5 hehe (among other versions or not had i tried with them but anyways etc). If you're curious how i did it, see this [google drive folder link](https://drive.google.com/drive/folders/1B18cJ8GYD8X_0vMoiTihVz0tthg5m_sg?usp=sharing) 's screenshots for details, hopefully helpful or not or yes or etc anyways etc

[How to](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#how-to)  
[Starting techs rework](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#starting-techs-rework)  
[Leaders' traits rework](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#leaders-traits-rework)  
[Leaders' favourite civics rework](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#leaders-favourite-civics-rework)  
[Leaders' Favourite religions rework](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#leaders-favourite-religions-rework)  

## How to

A quite easy way to gather the original data with chatgpt 5.1 for example, is, using vs code (or any tool you prefer), to do a global search (see for example [Another example of how to use VS Code global search](/_1_AdvCiv-SAS/Docs_And_Appendixes/Modding_Ressources/README.md#another-example-of-how-to-use-vs-code-global-search-also-shows-an-example-of-how-to-also-browse-the-civ4-bug-doc-copy-included-in-our-mod-anyways-etc) anyways etc.) for say `<Type>LEADER_` and `<FavoriteReligion>` and then copy paste the results found in civ4leaderheadinfos xml file asking chatgpt to merge them into an .md table. There may be easier ways to do it, but this one is quite effective and worked for me, hopefully helpful but anyways etc.

## Starting techs rework

As it is too lengthy to put in the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Main_Changes_Guide.md), here are how we changed the starting civ techs in our mod

### before most recent as of now rework anyways etc

#### main table (chatgpt 5 written anyways etc) - before change anyways etc

Done amazingly by chatgpt 5 (numbers are line in our xml civilization info file as of now anyways etc), check if accurate and thanks a lot chatgpt 5 and thanks to my prompt and such too if i may say but anyways etc

See below in the main table after changes as it includes the before values as well but anyways etc.

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

While doing/considering in this case i mean but anyways etc the holy roman empire civ-specific unit's rework or replacement, i have noticed charlemagne's traits were not in accord with his historical profile (i asked chatgpt 5 thanks since i don't know too much if at all about his history and leader profile or/and such and to be sure and have its advice as well thanks but anyways etc).

It is also limiting when we want as now to assign a new unit e.g. to the holy roman empire or possibly building, so i thought this was a good time to rework leader traits for balance, accuracy, and overall synergy with the civ's profile, as well as its civ-specific units and buildings, and also to match ingame behaviour +/- more(/most? But anyways etc) importantly xml or and such if / as much as possible or relevant i mean if i may say but anyways etc.

Done with the help of chatgpt 5 thanks a lot and thanks to my prompts too and/or adjustments and/or thoughts in this case i mean but anyways etc and/or formatting and/or such but anyways etc, check if accurate in this case i mean but anyways etc.

### previous state

This is extracted from the [CIV4LeaderHeadInfos.xml](/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml) rather but anyways etc, as we had issues importing it from our custom leaders_data_to_csv or/and it took too much time, due to data being too big or/and such i guess maybe if i'm not mistaken i mean in this case but anyways etc.

#### main table before changes to traits anyways etc

See below in the main table after changes as it includes the before values as well but anyways etc.

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
| Roosevelt | Industrious, Organized | **Industrious, Charismatic** | New Deal public works -> keep Industrious. His defining edge was coalition-building and morale (Fireside Chats, wartime leadership) more than bureaucratic cost efficiency. |
| Saladin | Protective, Spiritual | **Spiritual, Charismatic** | Admired by both sides; unifying religious leadership — not just a “defender.” He led major offensive campaigns (Hattin, Jerusalem) and had broad admiration. Your switch to Spiritual, Charismatic is very defensible; I wouldn’t go back to Protective unless you want to emphasize “shield of Islam” over his rallying aura. |
| Shaka | Aggressive, Expansive | **Aggressive, Organized** | Fits Ikhanda-style admin — “charismatic” in Civ terms can imply inspirational popularity; historically he ruled more by fear/discipline. Your pick Aggressive, Organized is perfect (impi/regimental system + logistics). I wouldn’t use Charismatic here. |
| Sitting Bull | Philosophical, Protective | **Keep** | Visionary/teacher + defensive resistance. |
| Stalin | Industrious, Aggressive | **Keep** | Forced industrialization + ruthless offensives. |
| Suleiman | Imperialist, Philosophical | **Keep** | “Lawgiver” persona + patronage of learning fits Philosophical better than Spiritual for gameplay and history; keeps imperial scope. `<!-- custom: plus if i remember enough i read he was quite areligious or religious open no? If so phi might fit better indeed than spi no? Thanks anyways etc thanks -->` |
| Suryavarman | Expansive, Creative | **Industrious, Creative** | Builder of Angkor; monumental works + culture. |
| Tokugawa | Protective, Aggressive | **Protective, Organized** | After unification, policy emphasized internal order, class discipline, and isolation over external aggression; governance beats battlefield ferocity. `<!-- custom: from a very quick search and my intuition/memory of what i read about him, he was very cautious and cunning/scheming rather if i'm not mistaken so maybe aggressive doesn't fit as well but anyways etc; also from a balance standpoint, if he is isolated, he would benefit much more from tax/costs reduction to run smoothly his empire than aggressive right? If i may say i mean but anyways etc. -->` |
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

## Leaders' favourite civics rework

Based on the old base advciv 1.12 data (or current advciv-sas if missing such as for new leaders we added like as of now Ewuare or/and such if any anyways etc), check if accurate anyways etc.

Goal is to make it more historically accurate, balanced in gameplay, and more or less evenly spread (although less of a focus but an additional ideal extra) anyways etc. Also to to account for our reworked/replaced civics such as of now civic_wage_labor, civic_trade_bloc, civic_protectionism, etc.

### before changes favourite civics per leader anyways etc

See below in the main table after changes as it includes the before values as well but anyways etc.

### before changes favourite civics count per civic anyways etc

| Civic              | Count as favourite |
|--------------------|--------------------|
| Hereditary Rule    | 9                  |
| Representation     | 5                  |
| Bureaucracy        | 4                  |
| Free Religion      | 4                  |
| Theocracy          | 4                  |
| Vassalage          | 4                  |
| Nationhood         | 3                  |
| Organized Religion | 3                  |
| Police State       | 3                  |
| Universal Suffrage | 3                  |
| Caste System       | 2                  |
| Free Market        | 2                  |
| Mercantilism       | 2                  |
| State Property     | 2                  |
| Emancipation       | 1                  |
| Environmentalism   | 1                  |
| Free Speech        | 1                  |
| Pacifism           | 0                  |
| Serfdom            | 0                  |
| Slavery            | 0                  |

| Civic            | Count as favourite |
|------------------|--------------------|
| Barbarism        | 0                  |
| Decentralization | 0                  |
| Despotism        | 0                  |
| Paganism         | 0                  |
| Tribalism        | 0                  |

- sanity: total favourites across all civics = **53** (should match number of leaders)

### after changes favourite civics per leader anyways etc

Done with the help of chatgpt 5.1, and other ais for check-up such as claude sonnet 4.5 and grok 4.1 and others anyways etc, and my reviewing or/and such as well i mean if i may say but anyways etc. Check if accurate anyways etc.

note: as of now advciv-sas civics are (check if updated in sevopedia/xml but anyways etc) wage labor is medieval new, protecitonism is late classical new (replaces mercantilism), environmentalism is removed in favour of trade_bloc (medieval (1300s) at printing press in our mod), and civic_paganism has been renamed to civic_prehistoric_religion (although it's as of now the same civic, just to distinguish/differentiate it from the religion_paganism we as of now added in advciv-sas but anyways etc.).

Also i added this info from chatgpt 5.1's thoughts as i found it very accurate and nicely phrased thanks anyways etc: "I think favorite civics should relate to the core of a leader's regime—such as government, legal, or religious systems—not just practices like slavery, which were widespread. For example, Caesar, Hannibal, and Pericles all had slavery—so choosing "Slavery" for one wouldn't add accuracy. Similarly, serfdom or trade bloc membership should be linked more to their regime and identity, not the specific labor practices of their time.".

| Leader            | Current Favourite Civic | Recommendation         | Rationale                                                                                                                                                                                                                                                                                                 |
| ----------------- | ----------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alexander         | Vassalage               | **Keep**               | Alexander’s distinct pattern is: aristocratic companions who owe service for status/land, overlordship of allied Greek poleis and subject kings, use of a Persian-style layered hierarchy (satraps, sub-kings). In other words: a very militarised overlord + vassal network structure. Given that, I think Claude is right that our previous change doesn’t really add clarity; it just makes him “generic monarch” instead of “overlord of vassals”. I’d now revert Alexander back to Vassalage as favourite civic. That gives us one very clear “Vassalage leader” in the classical era (plus Ragnar etc.), and still leaves Hereditary Rule plenty represented elsewhere. `<!-- custom: note: based on claude sonnet 4.5's feedback anyways etc -->` |
| Asoka             | Free Religion           | **Pacifism**           | Post-Kalinga, Asoka is defined by renouncing conquest, promoting dhamma, and issuing moral edicts; a peace-focused religious civic captures his historical identity much better than a modern pluralist Free Religion.                                                                                    |
| Augustus          | Representation          | **Bureaucracy**        | Augustus builds a durable imperial administration (provinces, census, tax, standing army) centered on Rome; Civ-style Bureaucracy is exactly “imperial capital + strong apparatus,” which fits him far better than Representation.                                                                        |
| Bismarck          | Nationhood              | **Keep**               | His short, limited wars (1864, 1866, 1870–71) are national unification wars built on conscription and mass mobilization; “Nation in arms” plus post-1871 nation-state management fits Nationhood very well.                                                                                               |
| Boudica           | Universal Suffrage      | **Nationhood**         | Historically she leads a revolt framed as defending “the people” and their land against Rome, rallying tribes into a war coalition; at Civ scale that is closer to a draft/war-mobilization civic than to late-game elections. We avoid Tribalism as a favourite because it’s an empty civic in your mod. |
| Brennus           | Organized Religion      | **Vassalage**          | I’d lean to changing Brennus to Vassalage – that gives him something more personal, and different from Boudica, without stretching what we actually know. For this Brennus (279 BCE, Thermopylae/Delphi one), the only clear thing in the sources is that he’s a fearsome coalition war-leader. He commands a big multi-tribal force with subordinate chiefs and warbands – lots of personal loyalty and “follow this chieftain into Greece for plunder.” We know far more about him as an overlord of warriors than as a religious organiser or nation-builder. So: Boudica = Nationhood → “people’s war / uprising of the Britons”. Brennus = Vassalage → “overlord with allied chiefs and retinues on campaign.” That keeps them both Celtic and warlike, but with distinctly different regime “shapes”. `<!-- custom: based on my past research, Brennus was fairly areligious, so after pointing/suggesting/asking chatgpt 5.1 this question/point, it told me organized religion works as a celtic society broad abstraction but not so typical of brennus himself who was not known for his piety or such if i understood it correctly. Since i want something more personalized to leaders ideally, changed it from the old organized religion then instead of keeping same trait anyways etc. It then rereviewed the table again with this perspective/idea in mind and no other change needed for accuracy or such according to it, except for Cyrus (see his line for details anyways etc) check if accurate anyways etc thanks for help lot still chatgpt 5.1 anyways etc: -->` "Short answer: with the Brennus change, I don’t see any other leader where the current favourite civic clearly misses their personal/regime identity in the way “Organized Religion → Brennus” did." anyways etc. |
| Catherine         | Hereditary Rule         | **Keep**               | Whatever her Enlightenment correspondence, she is an autocratic empress whose legitimacy rests on dynastic monarchy and palace coups; Hereditary Rule is exactly that.                                                                                                                                    |
| Charlemagne       | Vassalage               | **Keep**               | Carolingian rule is the textbook example of counts, marcher lords, and benefices granted for service; Vassalage is one of the most accurate favourite civic matches in the entire roster.                                                                                                                 |
| Churchill         | Nationhood              | **Keep**               | Churchill’s moment is wartime Britain: mass conscription, propaganda, and appeals to “the nation” rather than technocratic administration or economics. Nationhood fits that role.                                                                                                                        |
| Cyrus             | Vassalage               | **Hereditary Rule**    | Cyrus is a dynastic “King of Kings” ruling through satraps but anchored in royal lineage; in your civic set, simple Hereditary Rule is a closer abstraction than medieval-style Vassalage. `<!-- custom: following note at brennus: -->` "Right, so the “conflicted” feeling with Cyrus is basically: he looks like a Vassalage guy (King of Kings + satraps), but he is first and foremost a dynastic monarch. What Cyrus actually did (very condensed)" + "He overthrew the Median king, then conquered Lydia and Babylon, creating the Achaemenid Empire in the mid-6th c. BCE. To hold all that together, he used satraps – regional governors – to rule provinces on his behalf. The Achaemenid kings used the title “King of Kings” (shahanshah / basileus tōn basileōn), signalling that there were other kings beneath them – local dynasts and city-kings who stayed in place as subordinates. He’s also famous (maybe a bit romantically) for relatively lenient policies toward conquered peoples – e.g. letting exiles return and respecting local cults (Cyrus Cylinder, Jewish return from Babylon, etc.). So structurally, that does smell a lot like Civ’s Vassalage: a top ruler with subordinate rulers owing service." + "So the conflict is: Vassalage captures the shape of his empire. Hereditary Rule captures the core of his kingship and keeps Darius as the administrative/system guy. On balance, for your goals (personalised, regime-identity-focused, and avoiding too much overlap with Darius), Hereditary Rule wins by a nose. If someday you introduce a second Persian leader focused on the “network of subject kings” angle, that one would be a great place to use Vassalage as their favourite." |
| Darius            | Free Religion           | **Bureaucracy**        | Darius is the system-builder: satrapies, royal roads, inspectors, standardized tribute. His key trait is administrative statecraft, not modern religious liberty; Bureaucracy fits that centralizing impulse.                                                                                             |
| De Gaulle         | Nationhood              | **Keep**               | From the Free French to the Fifth Republic, his whole persona is “voice of the nation” and institutional refounder; a national-mobilization civic suits him well.                                                                                                                                         |
| Elizabeth         | Free Religion           | **Free Market**        | Her reign is the birth of English global commerce: chartered companies, privateering, Atlantic ventures. A trade-centric economic civic (Free Market) better captures the “Elizabethan sea-trade” identity than a modern secular religion policy.                                                         |
| Ewuare            | Hereditary Rule         | **Keep**               | The Oba of Benin is a sacral, hereditary monarch whose power rests on lineage, court ritual, and palace institutions; that is straight Hereditary Rule in Civ terms.                                                                                                                                      |
| Frederick         | Universal Suffrage      | **Bureaucracy**        | Frederick the Great is the archetypal “enlightened despot” running a drill-state and efficient civil service; he is much more a bureaucratic monarch than any kind of democrat.                                                                                                                           |
| Gandhi            | Universal Suffrage      | **Pacifism**           | Gandhi’s historical persona centers on non-violent resistance, fasting, and moral pressure, not on holding office inside a voting system; a peace-oriented religious civic is a cleaner expression of his role.                                                                                           |
| Genghis Khan      | Police State            | **Keep**               | Mongol rule under Genghis is total war, harsh law, and near-total social mobilization; Police State is a very accurate Civ-level abstraction.                                                                                                                                                             |
| Gilgamesh         | Hereditary Rule         | **Keep**               | Bronze Age Uruk is a city-state under a semi-divine king; a basic hereditary monarchy fits that legendary setting well enough.                                                                                                                                                                            |
| Hammurabi         | Bureaucracy             | **Keep**               | He is literally the go-to example for codified law and early centralized administration; Bureaucracy is exactly what his Civ design is already gesturing at.                                                                                                                                              |
| Hannibal          | Free Market             | **Trade Bloc**         | If you keep the current meaning of “Trade Bloc” (intergovernmental economic union), I still think Hannibal → Free Market is more accurate than Hannibal → Trade Bloc. Why I’d still lean Hannibal = Free Market" + "Given your own rule: favourite civic = the thing that best captures the leader’s regime identity or vibe, not “we need to showcase this civic” then for Hannibal: Core Hannibal / Carthage vibe: Maritime merchant city-empire" + "Money + ports + trade routes fund mercenary armies" + "Carthage as a rich commercial power clashing with a land empire (Rome)" + "Conceptually that is much closer to: Free Market → “commerce-driven society where markets and trade dominate the economy” than to: Trade Bloc → “formal intergovernmental agreement / customs union between multiple states”" + "Your Trade Bloc pedia text (screenshot) is very explicitly about: USMCA, EU-style blocs, 19–20th century economic integration, regional organisations, etc. Carthage’s system is an imperial maritime network, not an institutional trade bloc among equal partners. So if we stay literal about the concept as written, Hannibal’s “dream civic” is still Free Market." + "Given everything you’ve told me about accuracy > symmetry, my honest recommendation is still: Hannibal → Free Market, zero Trade Bloc favourites is OK." |
| Hatshepsut        | Organized Religion      | **Keep**               | Her major beats are Punt expeditions, temple building, and religious legitimation of her rule; a “temples help build things” civic matches that temple-economy flavor well.                                                                                                                               |
| Huayna Capac      | Hereditary Rule         | **State Property**     | The Inca economy is state-planned: no private land, labor tax (mit’a), state storehouses and roads. A command-economy civic like State Property maps far better to that than a generic monarchy favourite.                                                                                                |
| Isabella          | Theocracy               | **Keep**               | Reconquista, Inquisition, and militant Catholic policy: she is almost the archetype for a Theocracy in Civ terms.                                                                                                                                                                                         |
| Joao              | Hereditary Rule         | **Free Market**        | Portuguese expansion under Joao leans into Atlantic trade, colonies, and commercial charters; a pro-commerce economic civic is a better summary than another monarchy tag.                                                                                                                                |
| Julius Caesar     | Representation          | **Police State**       | In practice Caesar’s regime is a personal dictatorship backed by loyal legions and proscriptions; a hardline Police State matches that concentration of power better than a representative-government civic.                                                                                              |
| Justinian         | Theocracy               | **Keep**               | He rules an explicitly Christian empire, sponsors councils, enforces orthodoxy, and fuses imperial and religious authority; Theocracy is on-point here.                                                                                                                                                   |
| Kublai Khan       | Bureaucracy             | **Keep**               | As Yuan emperor he leans heavily on Chinese imperial bureaucracy and civil officials; Bureaucracy is exactly the flavor you want to highlight for him.                                                                                                                                                    |
| Lincoln           | Emancipation            | **Nationhood**         | Lincoln’s presidency is the archetype of “save the Union” via mass mobilization: conscription, war bonds, and appeals to the nation; a draft/propaganda civic expresses that better than a labor-law civic.                                                                                               |
| Louis XIV         | Hereditary Rule         | **Keep**               | “L’etat, c’est moi” is pure absolutist monarchy; Hereditary Rule is the clean and accurate match.                                                                                                                                                                                                         |
| Mansa Musa        | Free Market             | **Keep**               | His fame comes from gold, caravans, and trade routes linking West Africa to the wider Islamic world; a trade-oriented economic civic suits him perfectly. Mansa Musa – Free Market vs Trade Bloc: I agree with your current choice: Free Market. His story is gold + caravans + pilgrimage and wealth, not designing a customs union. |
| Mao Zedong        | State Property          | **Keep**               | Mao leads a communist revolution and then rules a centrally planned economy with collectivization and five-year plans; State Property is exactly the canonical choice.                                                                                                                                    |
| Mehmed            | Vassalage               | **Hereditary Rule**    | Mehmed II is a dynastic Ottoman sultan; while he does rely on timar grants and provincial notables, the core structure is an hereditary sultanate, which fits Hereditary Rule better than medieval Vassalage.                                                                                             |
| Moctezuma         | Police State            | **Theocracy**          | The Aztec state fuses ruler and priesthood, with ritual war and sacrifice as religious duty; a state-religion fusion civic better captures that sacral militarism than a generic police regime.                                                                                                           |
| Napoleon          | Representation          | **Nationhood**         | Napoleon is the poster child for levée en masse and national armies fighting for “la nation”; Nationhood captures the mass-mobilization aspect of Napoleonic France more clearly than any formal representative system.                                                                                   |
| Pacal             | Hereditary Rule         | **Caste System**       | Classic Maya society is strongly stratified with nobles, priests, and commoners in fixed roles; a labor/social-stratification civic like Caste System is a closer abstraction than a generic monarchy favourite.                                                                                          |
| Pericles          | Representation          | **Keep**               | Periclean Athens stands in for democracy in Civ: assembly, juries, pay for civic service; using Representation for that is standard and thematically right.                                                                                                                                               |
| Peter             | Bureaucracy             | **Keep**               | Peter the Great is all about building a Western-style, centrally administered state (Table of Ranks, new capital, modernized army); Bureaucracy is a perfect description.                                                                                                                                 |
| Qin Shi Huang     | Bureaucracy             | **Police State**       | Qin unification is remembered for harsh Legalist law, forced labor, book burnings, and secret police; in your civic set that’s closer to a hard Police State than to neutral “capital gets extra commerce.”                                                                                               |
| Ragnar            | Hereditary Rule         | **Vassalage**          | Viking warbands and jarls revolve around personal loyalty and service to a war-leader; Civ’s Vassalage (lords owing military service) is a good abstraction for that retinue-based society.                                                                                                               |
| Ramesses          | Organized Religion      | **Keep**               | Ramesses II is temple and monument king, backed by priestly legitimation; staying with Organized Religion keeps the “temple economy builds big things” vibe intact.                                                                                                                                       |
| Roosevelt         | Mercantilism            | **Universal Suffrage** | FDR governs within a mature electoral democracy, re-elected multiple times and using the state to intervene in the economy; a modern democratic government civic fits his role better than a narrow trade-policy one.                                                                                     |
| Saladin           | Theocracy               | **Keep**               | He’s remembered as the pious unifier leading jihad and defending Jerusalem; a tight fusion of state and religion is exactly what Theocracy represents.                                                                                                                                                    |
| Shaka             | Police State            | **Keep**               | Shaka’s Zulu state is a hyper-militarized regimental society with intense discipline and coercion; Police State is a very accurate Civ-scale summary.                                                                                                                                                     |
| Sitting Bull      | Environmentalism        | **Nationhood**         | In Civ terms he stands for defending his people’s land and sovereignty against an expanding state; a “defend the nation/people” civic matches that resistance role better than a late-game environmental/trade-bloc civic.                                                                                |
| Stalin            | State Property          | **Keep**               | Stalin’s USSR is the classic example of full state ownership and command planning; State Property is the obvious and accurate favourite.                                                                                                                                                                  |
| Suleiman          | Hereditary Rule         | **Bureaucracy**        | Suleiman “the Lawgiver” is as much about kanun (imperial law) and administrative order as conquest; highlighting a capital-centered admin civic better reflects that than another generic monarchy favourite.                                                                                             |
| Suryavarman       | Caste System            | **Keep**               | Angkor-era Khmer society is highly hierarchical with temple elites and organized labor; Caste System is a good abstraction for that social order.                                                                                                                                                         |
| Tokugawa          | Mercantilism            | **Protectionism**      | The Tokugawa shogunate’s sakoku policy (closed borders, tightly controlled trade) is basically a protectionist, restricted-trade order; your Protectionism civic maps to that very cleanly and replaces Mercantilism in the mod.                                                                          |
| Victoria          | Representation          | **Free Market**        | Victorian Britain is the textbook 19th-century industrial capitalist and free-trade power (post-Corn Laws etc.); a pro-market economic civic captures that better than tweaking the government form.                                                                                                      |
| Wang Kon          | Caste System            | **Organized Religion** | As founder of Goryeo he strongly supports Buddhism and religious institutions as pillars of the state; a temple-driven Organized Religion civic fits his Spiritual/Organized flavor better than labor structure alone.                                                                                    |
| Washington        | Free Speech             | **Representation**     | Washington presides over the founding of a representative republic and then voluntarily steps down; a government civic representing representative institutions is the cleanest expression of his role.                                                                                                   |
| Willem van Oranje | Free Religion           | **Keep**               | He’s famous for religious tolerance and coalition politics in the Dutch Revolt; a pluralist Free Religion civic is exactly his slot.                                                                                                                                                                      |
| Zara Yaqob        | Theocracy               | **Keep**               | Zara Yaqob is known for enforcing strict Christian orthodoxy and writing doctrinal works; a strong state-church fusion civic is the right summary.                                                                                                                                                        |

- sanity: leaders listed in this table = **53** (one favourite civic per leader)

### after changes favourite civics count per civic anyways etc

| Civic              | Count as favourite |
|--------------------|--------------------|
| Bureaucracy        | 7                  |
| Nationhood         | 7                  |
| Hereditary Rule    | 6                  |
| Free Market        | 5                  |
| Theocracy          | 5                  |
| Police State       | 4                  |
| Vassalage          | 4                  |
| Organized Religion | 3                  |
| State Property     | 3                  |
| Caste System       | 2                  |
| Pacifism           | 2                  |
| Representation     | 2                  |
| Free Religion      | 1                  |
| Protectionism      | 1                  |
| Universal Suffrage | 1                  |
| Free Speech        | 0                  |
| Serfdom            | 0                  |
| Slavery            | 0                  |
| Trade Bloc         | 0                  |
| Wage Labor         | 0                  |

| Civic                | Count as favourite |
|----------------------|--------------------|
| Barbarism            | 0                  |
| Decentralization     | 0                  |
| Despotism            | 0                  |
| Prehistoric Religion | 0                  |
| Tribalism            | 0                  |

Sanity: total favourites across all civics = 53 (one per leader, matches leader count).

## Leaders' Favourite religions rework

This is the oldest rework i made and which i had made without AI if i remember it correctly at least at that time, unlike how i did it later as of now for the other reworks in this doc.

Since its structure and way of doing it was quite differently done (not using chatgpt or such to web search info but digging myself if i remember it correctly but anyways etc.) (note: chatgpt 5.1 helped me a bit to find some typoes or such here and then as of now to format and summarize the already existing data into a table and/or such but anyways etc.), adding them here in the doc after these other reworks but anyways etc.

### notes_about_religious_design

#### Brennus

According to this document [https://boutique.tropismes.com/bonus/extrait/9782812148347](https://boutique.tropismes.com/bonus/extrait/9782812148347), page 29, Gaul leaders/chiefs (maybe that includes brennus of the Gaul too?) did not exert a strong religious pressure on their people as they were driven by freedom if i understand it correctly.

If this accurate and reliable, i may want/have/need to change brennus's xml to focus less on religion and more on civis, perhaps even boudica's but there may be more data on her since she is more recent, and i didn't look yet anyways etc (at least not in detail, only that she was seemingly more religious at least than what i know now of brenus if this doc is accurate, but it was quick glance too on boudica anyways so may look later or maybe not though, anyways etc.), so may apply this to brennus only or/and other similar leaders or not anyways etc.

Note: in advciv-sas as of now confucianism has been removed and replaced with paganism religion anyways etc.

#### Churchill

From a quick search not detailed but anyways etc., churchill didn't seem to have a strong preference for it or any religion, so is none now, allows also to declutter christianity that was bloated.

#### Cyrus

cyrus seems to not be strongly religious and quite open too in/from [https://en.wikipedia.org/wiki/Cyrus_the_Great#Religion_and_philosophy](https://en.wikipedia.org/wiki/Cyrus_the_Great#Religion_and_philosophy) if i am not mistaken anyways etc.

#### Darius

it seems darius is a bit more religious though (at least than cyrus), in these sources:

- [http://www.teheran.ir/spip.php?article2533#gsc.tab=0](http://www.teheran.ir/spip.php?article2533#gsc.tab=0)
- [https://en.wikipedia.org/wiki/Religion_in_the_Achaemenid_Empire](https://en.wikipedia.org/wiki/Religion_in_the_Achaemenid_Empire)

#### Ewuare

as for Ewuare (kingdom of benin), christianity seems to be an important part of the kingdom, but the beninese also have their own kind of or own religion with human sacrifices ([https://en.wikipedia.org/wiki/Kingdom_of_Benin#Human_sacrifice](https://en.wikipedia.org/wiki/Kingdom_of_Benin#Human_sacrifice)) and/or such but anyways etc., plus their benin bronzes and such; makes me more lean (if i am not mistaken) towards the fact that (THEY) they were more pagans, so going with that instead but anyways etc.

#### Frederick

frederick seems to be agnostic (quite strongly xd from the very little read i had here (in french) which is quite funny, the ironic pleasantry/plaisanterie in his letter anyways etc.): [https://fr.wikipedia.org/wiki/Fr%C3%A9d%C3%A9ric_II_(roi_de_Prusse)](https://fr.wikipedia.org/wiki/Fr%C3%A9d%C3%A9ric_II_(roi_de_Prusse)); but i read little about it and this page seems enough to say he is agnostic indeed maybe anyways etc, but seems a bit enough.

update: since i can't find what this refers to at a quick glance, i now asked chatgpt 5.1 about it still no luck xd i mean but anyways etc. My best guess is in one of his correspondances with someone else he noted how something is ironic or/and paradoxical, this is how i remember it but nothing specific, maybe i should have written it or maybe not since i didn't, but anyways etc. At least i tried xd maybe i mean if i may say but anyways etc.

#### Genghis Khan

genghis khan seems to have been tengrist something i mean anyways, but according to a quick search, it seems he had great respect for daoism: [https://fr.wikipedia.org/wiki/Religion_en_Mongolie#Tao%C3%AFsme](https://fr.wikipedia.org/wiki/Religion_en_Mongolie#Tao%C3%AFsme)

>Bien que Gengis Khan ait été avant tout tengriste, il manifesta un grand respect à l'égard du dirigeant de la secte taoïste Quanzhen, Qiu Chuji, lorsque celui-ci lui rendit visite dans l'Hindou Kouch, à Kaboul, en 1222, à son invitation, et prédit la conquête de la Chine par les Mongols. En retour, Gengis Khan lui donna d'importants pouvoirs politiques et religieux. Il fut exempté de taxes, et depuis Pékin, sa secte fut la plus favorisée de l'Empire Mongol. Il défendit la liberté d'autogestion des autres sectes, auprès du khagan, qu'il s'agisse des taoïstes, des bouddhistes, des chrétiens nestoriens ou des musulmans[18].

therefore, it is not incorrect to say, among civ4 advciv-sas's religions in particular, hat his favourite religion, if he had to choose one, is not none but maybe rather indeed daoism, is also quie convenient even though was not main goal that this is not filled, anyways etc., one leader can have a favourite religion even though not having said religion themselves; this is perhaps an important distinction i should add in changelogs and added now anyways etc.

#### Lincoln

as for lincoln, according to sources i read, lincoln was not christian, not strongly enough at all at least, here are a few sources i read:

- [https://en.wikipedia.org/wiki/Religious_views_of_Abraham_Lincoln#:~:text=Although%20Lincoln%20never%20made%20an,Christ%20in%20the%20religious%20sense](https://en.wikipedia.org/wiki/Religious_views_of_Abraham_Lincoln#:~:text=Although%20Lincoln%20never%20made%20an,Christ%20in%20the%20religious%20sense)
- [https://apps.legislature.ky.gov/LegislativeMoments/moments09RS/web/Lincoln%20moments%206.pdf](https://apps.legislature.ky.gov/LegislativeMoments/moments09RS/web/Lincoln%20moments%206.pdf)
- [https://www.thegospelcoalition.org/blogs/justin-taylor/was-abraham-lincoln-a-christian/](https://www.thegospelcoalition.org/blogs/justin-taylor/was-abraham-lincoln-a-christian/)
- [https://www.reddit.com/r/todayilearned/comments/llardq/til_that_abraham_lincolns_religious_views_are/](https://www.reddit.com/r/todayilearned/comments/llardq/til_that_abraham_lincolns_religious_views_are/)

i did not look at them in (long) detail, but i think in detail enough hopefully but anyways etc. that i can assert quite faithfully/strongly but anways maybe that he was definitely leaning more agnostic than christian, reddit comments also lean in that direction, was not christian even though had a strong christian education. Lincoln seems more agnostic or not strongly favouring a religion, so for civ4 i changed it to none rather than christianity, he seems to be a free person rather which i like i mean if i may say but anyways etc. (But also even if he were not such free man and really christian, he is free to do so to (else it would defeat the purpose xd i mean if i may say but anyways etc.)).

#### Pericles

pericles prefers religion according to [https://ehne.fr/fr/eduscol/pericles-est-il-vraiment-le-grand-homme-de-la-democratie-athenienne#:~:text=Enfin%2C%20P%C3%A9ricl%C3%A8s%20s'est%20appuy%C3%A9,ont%20beaucoup%20fait%20pour%20la](https://ehne.fr/fr/eduscol/pericles-est-il-vraiment-le-grand-homme-de-la-democratie-athenienne#:~:text=Enfin%2C%20P%C3%A9ricl%C3%A8s%20s'est%20appuy%C3%A9,ont%20beaucoup%20fait%20pour%20la) so going with religion paganism hopefully accurate enough anyways etc.

#### Wang Kon

for wang kon, according to civ4 wiki (in [https://civilization.fandom.com/wiki/Wang_Kon_(Civ4)](https://civilization.fandom.com/wiki/Wang_Kon_(Civ4))):

>During his reign Wang Kon promoted Buddhism as the state religion, and oversaw the conquest of northern Korea and parts of Manchuria. When dealing with local clans,

if i am not mistaken, he promoted buddhism as the state religion; i don't know why his preferred religion was confucianism, but since there is no confucianism anymore now in advciv-sas, he leans closer (i think) to buddhism based on this maybe anyways etc. than say paganism or none religion (favourite), is convenient to increase buddhism leader count that is really low and not increase paganism leader count that is high enough (a bit too high but historically fine and matching christinaity so maybe fine too anyways etc); Hopefully fine enough and accurate enough even though not exhaustive but anyways etc.

### Other leaders

Not documented in my old notes, but many leaders have also been changed, mostly if not only to paganism.

### Summary of the favourite religion leaders' changes in advciv-sas anyways etc

A summary of my previous notes with the help of chatgpt 5.1 (check if accurate anyways etc.) anyways etc, showing base advciv's (except for some leader(s) like Ewuare since they didn't exist in base advciv but anyways etc.) favourite religion vs advciv-sas.

| Leader             | Base         | New              | Rationale |
| ------------------ | ------------ | ---------------- | --------- |
| Alexander          | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Asoka              | Buddhism     | Keep             |           |
| Augustus           | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Bismarck           | Christianity | Keep             |           |
| Boudica            | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Brennus            | None         | Keep             | Already had no favourite religion; the Brennus note mainly informed other XML tweaks (less religious emphasis, more civics focus), not a favourite religion change. |
| Catherine          | Christianity | Keep             |           |
| Charlemagne        | Christianity | Keep             |           |
| Churchill          | Christianity | **None**         | Biographical sketches don’t show a strong personal attachment to any one faith; dropping his Christian favourite both matches that and helps reduce Christianity’s over-representation in the roster. |
| Cyrus              | None         | Keep             | After a quick read of his religious views, Cyrus looks relatively open and not strongly attached to a single faith, so leaving his favourite religion as None still fits. |
| Darius             | None         | **Paganism**     | Darius appears more overtly religious than Cyrus in the sources; giving him a specific favourite religion in-game (Paganism as generic Achaemenid state cult) reflects that. |
| De Gaulle          | Christianity | Keep             |           |
| Elizabeth          | Christianity | Keep             |           |
| Ewuare             |              | **Paganism**     | New leader in AdvCiv-SAS; for the Kingdom of Benin, Christianity appears late and local religion (including human sacrifice and royal ritual) is central, so Ewuare uses Paganism as favourite religion. |
| Frederick          | Christianity | **None**         | French and other sources often describe Frederick II as deist/agnostic; his favourite religion is changed from Christianity to None to reflect that more sceptical stance. |
| Gandhi             | Hinduism     | Keep             |           |
| Genghis Khan       | None         | **Daoism**       | Historically tengrist but showed particular respect for the Quanzhen Taoist master Qiu Chuji; among your available religions, Daoism is the closest fit, and it usefully fills what was previously an empty favourite-religion slot for him. |
| Gilgamesh          | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Hammurabi          | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Hannibal           | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Hatshepsut         | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Huayna Capac       | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Isabella           | Christianity | Keep             |           |
| Joao               | Christianity | Keep             |           |
| Julius Caesar      | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Justinian          | Christianity | Keep             |           |
| Kublai Khan        | Buddhism     | Keep             |           |
| Lincoln            | Christianity | **None**         | Sources generally paint Lincoln as religiously complex / sceptical rather than a clear Christian partisan; treating him as effectively agnostic and removing his Christian favourite keeps him more neutral. |
| Louis XIV          | Christianity | Keep             |           |
| Mansa Musa         | Christianity | **Islam**        | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Mao Zedong         | Hinduism     | **None**         | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Mehmed             | Islam        | Keep             |           |
| Moctezuma          | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Napoleon           | Christianity | Keep             |           |
| Pacal              | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Pericles           | None         | **Paganism**     | Pericles leans heavily on civic religion, festivals and public cult; giving him Paganism as a favourite ties him to the generic “classical city cults” bucket instead of leaving him without any religious preference. |
| Peter              | None         | **Christianity** | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Qin Shi Huang      | Taoism       | **Daoism**       | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Ragnar             | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Ramesses           | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Roosevelt          | Christianity | Keep             |           |
| Saladin            | Islam        | Keep             |           |
| Shaka              | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Sitting Bull       | None         | **Paganism**     | Undocumented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Stalin             | None         | Keep             |           |
| Suleiman           | Islam        | Keep             |           |
| Suryavarman        | Hinduism     | Keep             |           |
| Tokugawa           | Buddhism     | Keep             |           |
| Victoria           | Christianity | Keep             |           |
| Wang Kon           | Confucianism | **Buddhism**     | As founder of Goryeo he promoted Buddhism as state religion; with Confucianism removed from AdvCiv-SAS, switching his favourite to Buddhism keeps him anchored to an organised religion that matches the history better than Paganism or None. |
| Washington         | Christianity | Keep             |           |
| Willem van Oranje  | Christianity | Keep             |           |
| Zara Yaqob         | Christianity | Keep             |           |

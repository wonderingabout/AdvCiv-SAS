# README_Assets_Rebalancing

Some of the asset rebalancing is shown here (not exhaustive)

## Menu

[How to](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#how-to)  
[Civs' starting techs rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#civs-starting-techs-rework)  
[Tech quote swaps rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#tech-quote-swaps-rework)  
[Civ-specific buildings rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#civ-specific-buildings-rework)  
[Civ-specific units rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#civ-specific-units-rework)  
[Leaders' traits rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#leaders-traits-rework)  
[Leaders' favourite civics rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#leaders-favourite-civics-rework)  
[Leaders' Favourite religions rework](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#leaders-favourite-religions-rework)  

## How to

A quite easy way to gather the original data with chatgpt 5.1 for example, is, using vs code (or any tool you prefer), to do a global search (see for example [Another example of how to use VS Code global search](/_1_AdvCiv-SAS/Docs/Modding_Ressources/README.md#another-example-of-how-to-use-vs-code-global-search-also-shows-an-example-of-how-to-also-browse-the-civ4-bug_doc-copy-included-in-our-mod)) for say `<Type>LEADER_` and `<FavoriteReligion>` and then copy paste the results found in civ4leaderheadinfos xml file asking chatgpt to merge them into an .md table. There may be easier ways to do it, but this one is quite effective and worked for me.

More recently, i found or noticed that giving old and new XML files (e.g., `CIV4UnitInfos.xml`) to an LLM or such is enough for it to compile them into a nice .md table comparison or such; there may be other ways too but this seems quite good for example.

## Civs' starting techs rework

As it is too lengthy to put in the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md), here are how we changed the starting civ techs in our mod

### before most recent as of now rework

#### main table (chatgpt 5 written) - before change

Done amazingly by chatgpt 5 (numbers are line in our xml civilization info file as of now), check if accurate and thanks a lot chatgpt 5 and thanks to my prompt and such too

See below in the main table after changes as it includes the before values as well.

### after most recent as of now rework

After a few or quite many back and forth and reviewing rounds with chatgpt 5 which helped me tons but also me hehe and my own ideas but it helped lot too, here are (below) the adjusted starting techs for civs as of now in advciv-sas, written by chatgpt 5. This was mostly to remove/replace old now removed tech_agriculture and tech_the_wheel starters that are now no longer starting techs, as well as quite along with it rebalance it and rework it all. I think the result is really good at least much better than it was check if accurate.

#### main table (chatgpt 5 written with some tweaks from me)

Goals: (1) stay historically/thematically sane, (2) avoid **too many repeats** of the same pair, and (3) **not too many "amazing" pairs** like **Mining+Hunting** (early rush spike) and **Mining+Pottery** (eco+production spike) - while keeping **quite a few enough** for clear identity/variety.

Note: **Fishing+Mining is fine** (Fishing is weakest), so we use it without concern as long as there is not too much of it.

| Civ | Old FreeTechs | New FreeTechs | Rationale |
| --- | --- | --- | --- |
| America | Fishing, Agriculture | **Fishing, Hunting** | Drops disallowed Agriculture. Frontier/scouting flavor; modest econ. *Avoids Mining+Hunting / Mining+Pottery.* |
| Arabia | The Wheel, Mysticism | **Hunting, Mysticism** | Desert pastoral/tribal-warrior flavor + smooth path toward Animal Husbandry/camels; Mysticism preserves religion/culture identity (and your civ-specific building is university-based so no Pottery dependency). |
| Aztec | Mysticism, Hunting | **Mining, Mysticism** | **Jaguar** now at Bronze Working -> Mining speeds access. Mysticism matches ritual/state culture. We **avoid Mining+Hunting** to curb rush. |
| Babylon | Agriculture, The Wheel | **Pottery, Mysticism** | **Bowman** is now **Longbow-class** at Construction. Pottery fits the Masonry -> Construction lane (bricks, aqueducts, Hanging Gardens), while Mysticism preserves the temple/garden flavor. |
| Byzantium | The Wheel, Mysticism | **Mysticism, Fishing** | Bosporus/seaborne empire + spiritual tone; removes early-road snowball. |
| Carthage | Fishing, Mining | **Fishing, Pottery** | Maritime commerce + cottages; **drops Mining** to lower early snowball and reduce pair repetition. |
| Celt | Hunting, Mysticism | **Hunting, Mining** | **Gallic Warrior** metallurgy path justified; shifts from "druidic" to martial. **Intentional strong pair** (Mining+Hunting) for civ-specific unit identity; kept rare overall. |
| China | Agriculture, Mining | **Mining, Pottery** | Bronze/iron + ceramics traditions; we keep this as **one of the few** strong **Mining+Pottery** pairs for identity. |
| Egypt | The Wheel, Agriculture | **Hunting, Pottery** | Keep **Pottery** to flow into **Masonry -> Construction** (builder identity: Pyramids, aqueducts, etc.). Add **Hunting** to align the **War Chariot** path. |
| England | Fishing, Mining | **Keep** | Industrial metals identity fits; Fishing+Mining is acceptable (Fishing is weakest). Also avoids overusing Mining+Pottery. |
| Ethiopia | Hunting, Mining | **Hunting, Mysticism** | Highlands/faith; **removes Mining+Hunting** spike while keeping early defense. |
| Kingdom of Benin | / | **Mysticism, Pottery** | Pottery anchors the "fortified/urban builder court-state" + supports your Impluvium/aqueduct line; Mysticism keeps the ritual/court legitimacy flavor (and avoids pushing them toward early bronze play). |
| France | The Wheel, Agriculture | **Hunting, Pottery** | Aristocratic hunt + towns; replaces disallowed pair. |
| Germany | Pottery, Mining | **Keep** | Crafts + metalwork flexibility. **One of the few** Mining+Pottery we keep (Old World metallurgy). |
| Greece | Fishing, Hunting | **Mining, Mysticism** | Keeps the "culture/religion" signal (temples/oracles/cults) while also pushing the Hoplite -> Bronze/Iron line sooner via Mining; better matches "bronze + sacred polis" as a starter identity. |
| Holy Roman | Mysticism, Hunting | **Mysticism, Pottery** | Reads more like "Church + towns/guild/urban administration" than generic hunting, and unlocks their civ-specific building (Courthouse-based) sooner via the Pottery line. |
| Inca | Agriculture, Mysticism | **Pottery, Mining** | Andean mining/metallurgy (copper, arsenical bronze; large-scale gold/silver extraction) + state logistics makes Mining a great fit. Also supports Quechua @ **Iron Working** |
| India | Mysticism, Mining | **Keep** | Spiritual tradition + engineering; not an "amazing" pair. |
| Ireland | / | **Fishing, Mysticism** | Maritime + monastic/cultural identity; balanced opener without Mining/Hunting spikes. |
| Japan | Fishing, The Wheel | **Fishing, Hunting** | Keeps maritime identity; **Jomon hunter-gatherer** roots make Hunting plausible. Avoids adding another Mining+Pottery or Mining+Hunting. |
| Khmer | Hunting, Mining | **Fishing, Hunting** | Tonle Sap/Mekong fisheries + elephants/camps; **removes Mining+Hunting** rush spike. |
| Korea | Mining, Mysticism | **Fishing, Mining** | Keeps Mining (the more distinctive "Korea-coded" pillar: metals/engineering), and adds Fishing to reflect a peninsula/coastal civilization with strong maritime/trade exposure - without implying an early religion-race start. |
| Mali | The Wheel, Mining | **Hunting, Pottery** | **Skirmisher** is now **Longbow-class** at Construction. Hunting keeps the Sahel skirmisher/camp identity; Pottery sustains early commerce while beelining Construction. They don't need mining as much for their civ-specific unit. |
| Maya | Mining, Mysticism | **Mysticism, Pottery** | Classic Maya = obsidian/chert/jade; metals are late/minor. Holkan @ Bronze Working (Mining line) remains reachable, but early Pottery better fits their builder profile and ramps Ball Court @ Construction, while Mysticism matches ritual/astronomy and supplies early culture. |
| Mongol | The Wheel, Hunting | **Hunting, Mysticism** | Pastoral steppe with early horses: Hunting -> Animal Husbandry -> Mounted Combat (and Barracks @ Hunting in AdvCiv-SAS), which also matches their aggressive-leaning leader profiles; Mysticism reflects Tengri/shamanic cohesion and supplies early culture/monuments to claim steppe space. |
| Native America | Agriculture, Fishing | **Hunting, Mining** | Replace inland Fishing with Mining (abstracts obsidian/flint/quarries). **Dog Soldier** benefits from the Bronze Working line. Adds one OP pair by design; helps identity. |
| Netherlands | Agriculture, Fishing | **Fishing, Pottery** | Maritime commerce + early cottages; *no Mining* for a gentler opener. |
| Ottoman | The Wheel, Agriculture | **Fishing, Pottery** | **Fishing** to reflect an early maritime footprint on the **Aegean**, **Sea of Marmara** (Bosporus), **Black Sea**, and the **eastern Mediterranean**. Pair with **Pottery** to support early crafts/urbanization and a builder-empire profile. They don't need as much strong starting techs for their civ-specific unit that is later in the game. |
| Persia | Agriculture, Hunting | **Hunting, Mining** | Nearer to **Iron Working** path in your tree; strong metallurgy tradition. We accept one more OP pair for identity; totals remain balanced. |
| Portugal | Fishing, Mining | **Fishing, Pottery** | Age-of-Discovery maritime commerce; Mining ceded to reduce repetition and fund other civs' thematic needs. |
| Rome | Fishing, Mining | **Keep** | Metals for **Legionary** timing; avoids Hunting and Mining+Pottery extremes. |
| Russia | Hunting, Mining | **Pottery, Mining** | Land-empire emphasis (settlement/crafts) and less "fishy" opening. Keeps metal identity; also offsets Ottoman's change to keep 14/14/14/14/14 totals. |
| Spain | Fishing, Mysticism | **Keep** | Maritime reach + organized religion; avoids Mining spikes. |
| Sumeria | Mysticism, Pottery | **Mysticism, Mining** | **Vulture** (axe) loves metals; still not the "amazing" Mining+Pottery/Hunting. |
| Scandinavia | Fishing, Hunting | **Keep** | Seafaring + raiding/hunting; balanced opener without Mining; keeps variety. |
| Zulu | Agriculture, Hunting | **Hunting, Mining** | **Intentionally keep an OP pair (Mining+Hunting)** for **Impi** flavor/identity; brings Agriculture into compliance. |

#### Global tech totals

| Tech | Count |
| --- | --- |
| Mining | 15 |
| Pottery | 15 |
| Hunting | 14 |
| Fishing | 14 |
| Mysticism | 14 |

#### Starting pair counts (canonicalized; order-insensitive)

| Pair                | Count |
| ------------------- | ----- |
| Fishing + Hunting   | 4     |
| Fishing + Pottery   | 4     |
| Hunting + Mining    | 4     |
| Mysticism + Mining  | 4     |
| Mysticism + Pottery | 4     |
| Pottery + Mining    | 4     |
| Fishing + Mining    | 3     |
| Hunting + Mysticism | 3     |
| Hunting + Pottery   | 3     |
| Fishing + Mysticism | 3     |

**Sanity checks:**

- Pair counts sum to **36** civs.  
- Tech totals sum to **72** picks. OK

## Tech quote swaps rework

| Quote | Base AdvCiv tech | AdvCiv-SAS tech |
| --- | --- | --- |
| "Oh! I have slipped the surly bonds of Earth - Put out my hand and touched the Face of God." - John Gillespie Magee, Junior | Advanced Flight | Keep |
| "Art for art's sake is an empty phrase. Art for the sake of truth, art for the sake of the good and the beautiful, that is the faith I am searching for." - George Sand | Aesthetics | Keep |
| "Oh farmers, pray that your summers be wet and your winters clear." - Virgil | Agriculture | Keep |
| "I cannot live without books" - Thomas Jefferson | Paper | Keep |
| "Behind a veil, unseen yet present, I was the forceful soul that moved this mighty body." - Jean Racine | Stealth | Alien Life |
| "Blessed shall be the fruit of thy cattle, the increase of thy kine, and the flocks of thy sheep." - The Bible, Deut. 28:4 | Animal Husbandry | Keep |
| "Artillery adds dignity to what would otherwise be a vulgar brawl." - Frederick the Great | Artillery | Keep |
| "People can have the Model T in any color - so long as it's black." - Henry Ford | Assembly Line | Keep |
| "Astronomy compels the soul to look upwards and leads us from this world to another." - Plato | Astronomy | Keep |
| "Banking establishments are more dangerous than standing armies." - Thomas Jefferson | Banking | Keep |
| "Everything in life is somewhere else, and you get there in a car." - E. B. White | Combustion | Keep |
| "There is a single light of science, and to brighten it anywhere is to brighten it everywhere." - Isaac Asimov | Fiber Optics | Biology |
| "There is no wealth like knowledge, no poverty like ignorance." - Ali ibn Abi-Talib | Education | Broader Education |
| "It is entirely seemly for a young man killed in battle to lie mangled by the bronze spear. In his death all things appear fair." - Homer | Bronze Working | Keep |
| "For everything there is a season and a time for every purpose under heaven." - Ecclesiastes | Calendar | Keep |
| "Chemistry means the difference between poverty and starvation and the abundant life." - Robert Brent | Chemistry | Keep |
| "I will to my lord be true and faithful, and love all which he loves and shun all which he shuns." - Anglo Saxon Oath of Fealty | Feudalism | Chivalry |
| "The bureaucracy is expanding to meet the needs of the expanding bureaucracy" - Unknown | Civil Service | Keep |
| "To bring about the rule of righteousness in the land, so that the strong should not harm the weak." - Hammurabi's Code; Prologue | Code Of Laws | Keep |
| "I just want to say one word to you. Just one word: plastics." - Calder Willingham, The Graduate | Plastics | Composites |
| "When I give food to the poor, they call me a saint. When I ask why the poor have no food, they call me a communist." - Dom Helder Camara | Utopia | Communism |
| "The whole is greater than the sum of its parts." - Aristotle | Composites | Fusion |
| "Never trust a computer you can't throw out a window." - Steve Wozniak | Computers | Keep |
| "No freeman shall be taken, imprisoned, or in any other way destroyed, except by the lawful judgment of his peers." - The Magna Carta | Constitution | Keep |
| "I must study politics and war that my sons may have liberty to study mathematics and philosophy." - John Adams | Military Science | Keep |
| "Corporation, n. An ingenious device for obtaining individual profit without individual responsibility." - Ambrose Bierce | Corporation | Keep |
| "Everything is worth what its purchaser will pay for it." - Publius Syrus | Currency | Keep |
| "It has been said that democracy is the worst form of government except all the others that have been tried." - Winston Churchill | Democracy | Keep |
| "Compound interest is the most powerful force in the universe." - ascribed to Albert Einstein | Economics | Construction |
| "All the world's a stage, And all the men and women merely players. They have their exits and their entrances; And one man in his time plays many parts. " - William Shakespeare | Drama | Romanticism |
| "We do not inherit the earth from our ancestors, we borrow it from our children" - unknown | Ecology | Keep |
| "People of the same trade seldom meet together, even for merriment and diversion, but the conversation ends in a conspiracy against the public." - Adam Smith | Guilds | Economics |
| "We will make electricity so cheap that only the rich will burn candles." - Thomas Edison | Electricity | Keep |
| "A designer knows he has achieved perfection not when there is nothing left to add, but when there is nothing left to take away." - Antoine de Saint-Exupry | Engineering | Keep |
| "Tell me what you eat, and I will tell you what you are." - Anthelme Brillat-Savarin | Refrigeration | Environmentalism |
| "The great masses of the people... will more easily fall victims to a big lie than to a small one." - Adolf Hitler | Fascism | Mass Media |
| "I am the state." - ascribed to Louis XIV | Divine Right | Feudalism |
| "Political power grows out of the barrel of a gun." - Mao Zedong | Rifling | Firearms |
| "Give a man a fish and you feed him for a day. Teach a man to fish and you feed him for a lifetime." - Lao Tzu | Fishing | Keep |
| If the radiance of a thousand suns were to burst at once into the sky, that would be like the splendor of the Mighty One... I am become Death, the Shatterer of Worlds. - J. Robert Oppenheimer, quoting "The Bhagavad Gita" | Fission | Keep |
| "For once you have tasted flight you will walk the earth with your eyes turned skywards, for there you have been and there you will long to return." - ascribed to Leonardo Da Vinci | Flight | Keep |
| "Any sufficiently advanced technology is indistinguishable from magic." - Arthur C. Clarke | Fusion | AI |
| "I fooled you, I fooled you, I got pig iron, I got pig iron, I got all pig iron." - Lonnie Donegan, "Rock Island Line" | Railroad | Game Theory |
| "Soon it will be a sin for parents to have a child which carries the heavy burden of genetic disease." - Bob Edwards | Genetics | Keep |
| "You can get more of what you want with a kind word and a gun than you can with just a kind word." - Al Capone | Gunpowder | Keep |
| "If you chase two rabbits, you will lose them both." - proverb | Hunting | Keep |
| "There is one rule for the industrialist and that is: Make the best quality of goods possible at the lowest cost possible, paying the highest wages possible." - Henry Ford | Industrialism | Keep |
| "You should hammer your iron when it is glowing hot." - Publius Syrus | Iron Working | Keep |
| "A multitude of rulers is not a good thing. Let there be one ruler, one king." - Homer, The Iliad | Monarchy | Later Abrahamism |
| "Any society that would give up a little liberty to gain a little security will deserve neither and lose both." - Benjamin Franklin | Liberalism | Keep |
| "Some books are to be tasted, others to be swallowed, and some few to be chewed and digested." - Sir Francis Bacon | Literature | Keep |
| "A god from the machine" - Menander | Machinery | Keep |
| "You would make a ship sail against the winds and currents by lighting a bon-fire under her deck? I have no time for such nonsense." - Napoleon, on Robert Fulton's Steamship (anecdote) | Steam Power | Marine Technology |
| "It is from their foes, not their friends, that cities learn the lesson of building high walls." - Aristophanes | Masonry | Keep |
| "The only thing worse than being talked about is not being talked about." - Oscar Wilde | Mass Media | Fascism |
| "If in other sciences we should arrive at certainty without doubt and truth without error, it behooves us to place the foundations of knowledge in mathematics." - Roger Bacon | Mathematics | Keep |
| "As to diseases make a habit of two things - to help, or at least, to do no harm." - Hippocrates | Medicine | Keep |
| "Meditation brings wisdom; lack of meditation leaves ignorance. Know well what leads you forward and what holds you back." - The Buddha | Meditation | Keep |
| "Before that steam drill shall beat me down, I'll die with my hammer in my hand." - from "John Henry, the Steel-Driving Man" | Steel | Metal Casting |
| "Do not throw the arrow which will return against you." - Kurdish Proverb | Archery | Water Wheel |
| "And them that take the sword shall perish by the sword." - The Bible, Matthew | Metal Casting | Military Tradition |
| "The man who moves a mountain begins by carrying away small stones." - Confucius | Mining | Keep |
| "And on the pedestal these words appear: 'My name is Ozymandias, king of kings: Look on my works, ye Mighty, and despair!' Nothing beside remains." - Percy Bysshe Shelley | Construction | Monarchy |
| "I am the Lord thy God. Thou shalt have no other gods before Me." - The Bible, Exodus | Monotheism | Keep |
| "If you speak the truth, have a foot in the stirrup." - Turkish proverb | Horseback Riding | Mounted Combat |
| "Nature herself has imprinted on the minds of all the idea of God." - Cicero | Mysticism | Bioengineering |
| "A man does not have himself killed for a half-pence a day or for a petty distinction. You must speak to the soul in order to electrify him." - ascribed to Napoleon Bonaparte | Nationalism | Keep |
| "I do not feel obliged to believe that the same God who has endowed us with sense, reason, and intellect has intended us to forgo their use." - Galileo Galilei | Scientific Method | Naturalism |
| "The wisest men follow their own direction." - ascribed to Euripides | Compass | Navigation |
| "I have gained this by philosophy: that I do without being commanded what others do only from fear of the law." - ascribed to Aristotle | Philosophy | Keep |
| "To every action there is always opposed an equal reaction." - Isaac Newton | Physics | Keep |
| "Not at all similar are the race of the immortal gods and the race of men who walk upon the earth." - Homer | Polytheism | Keep |
| "The Lord bless you and keep you; the Lord make His face to shine upon you and be gracious to you; the Lord lift up His countenance upon you and give you peace." - The Bible, Numbers | Priesthood | Postaxial Religion |
| "Hath not the potter power over the clay, to make one vessel unto honor, and another unto dishonor?" - The Bible, Romans | Pottery | Keep |
| "What gunpowder did for war, the printing press has done for the mind." - Wendell Phillips | Printing Press | Keep |
| "The whole is more than the sum of its parts." - Aristotle | Replaceable Parts | Quantum Mechanics |
| "Then one fine mornin' she puts on a New York station. You know her life was saved by Rock 'n' Roll." - The Velvet Underground, "Rock And Roll" | Radio | Keep |
| "The real problem is not whether machines think, but whether men do." - B.F. Skinner | Robotics | Robot Rights |
| "The Earth is the cradle of the mind, but one cannot eternally live in a cradle." - Konstantin E. Tsiolkovsky | Rocketry | Keep |
| "If music be the food of love, play on." - William Shakespeare | Music | Mysticism |
| "You can't direct the wind, but you can adjust your sails." - Unknown | Sailing | Keep |
| "Beep...beep...beep...beep..." - Sputnik I | Satellites | Keep |
| "One doesn't discover new lands without losing sight of the shore." - Andre Gide | Optics | Seafaring |
| "Nothing travels faster than the speed of light with the possible exception of bad news, which obeys its own special laws." - Douglas Adams | Laser | Space Exploration |
| "Victorious warriors win first and then go to war, while defeated warriors go to war first and then seek to win." - Sun-Tzu | Military Tradition | Professional Army |
| "What is happiness? The feeling that power is growing, that resistance is overcome." - Friedrich Nietzsche | Superconductors | Steam Power |
| "Two cities have been formed by two loves: the earthly by the love of self; the heavenly by the love of God." - St. Augustine | Theology | Terraforming |
| "It is not the strongest of the species that survive, but the one most responsive to change." - Charles Darwin (paraphrase) | Biology | Theory Of Evolution |
| "Put your shoulder to the wheel." - ascribed to Aesop | The Wheel | Keep |
| "The future will be better tomorrow." - Dan Quayle | Future Tech | Transhumanism |
| "Words have the power to both destroy and heal. When words are both true and kind, they can change our world." - ascribed to the Buddha | Alphabet | Depopulation |
| "True glory consists in doing what deserves to be written; in writing what deserves to be read." - Pliny the Elder | Writing | Keep |

## Civ-specific buildings rework

No counts yet (faster pass).  

Note: water buildings are generally avoided as they are too situational (useless in land maps or cities, etc.) and often weaker, unless they strongly fit or well enough.

| Civ | Before (Base AdvCiv) | After (AdvCiv-SAS) | Rationale |
| --- | --- | --- | --- |
| America | Mall (Supermarket) | **Keep** (Keep) | |
| Arabia | Madrassa (Library) | **Keep** (University) | Thematic fit, more balanced than op library. |
| Aztec | Sacrificial Altar (Courthouse) | **Keep** (Monument) | Much stronger than late courthouse. Fits aztec early slaving profile |
| Babylon | Garden (Colosseum) | **Keep** (Keep) | |
| Byzantium | Hippodrome (Theatre) | **Keep** (Stable) | Stronger and more efficient building than weak situational culture of the theater for this civ, since the stable is likely almost always desired for their civ-specific unit in particular. As of now takes most of old theater building effects with some cultural effects instead of all happiness effects. |
| Carthage | Cothon (Harbor) | **Keep** (Port) | Port is the new AdvCiv-SAS stronger water classical production building |
| Celt | Dun (Walls) | **La Tene Smithy** (Forge) | Dun is weak and too defensive/situational; also doesn't match the aggressive Celtic profile. Shift to a Forge-based UB for a stronger metalwork identity, with happiness support tied to Iron/Copper. Good synergy with their swordsman-based civ-specific unit and overall military profile that may use these bonuses as well. |
| China | Pavillion (Theatre) | **Changpingcang** (Market) | Not so cultural game profile plus it is weaker. This new building leans into a market-management/state-stability theme (price smoothing and social calm) rather than pure food storage. As China in this setup is often health-rich, extra happiness support is valuable and a nice synergy for larger empires and sustained city growth. Identity with happy from Rice capitalizes on such excess health, and food kept fits thematically and is not as op later in the game. |
| Egypt | Obelisk (Monument) | **Keep** (Keep) | |
| England | Stock Exchange (Bank) | **Keep** (Keep) | |
| Ethiopia | Stele (Monument) | **Metsehaf Bet** (Library) | Distinctive theology-to-scholarship identity via Ge'ez manuscript/commentary tradition. Also uses underused library slot and declutters the overused monument slot. Strong religious identity (priest-scholar) => as of now GP Priest plus culture-scaling profile. Also aims to go better with Zara Yaqob's trading/diplomat/growth ingame profile |
| Ireland | / | **Scriptorium** (University) | New civ: strong monastic-learning thematic fit (scriptoria as centers of manuscript copying/scholarship) and good gameplay/profile match for Irish leaders with gold/diplomatic/science leanings. University timing keeps it meaningful without becoming an overpowered early spike like a library would be with the as of now scriptorium's effects. |
| Kingdom of Benin | / | **Impluvium** (Aqueduct) | New civ: Thematic fit; plus fits Ewuare's production/growth profile |
| France | Salon (Observatory) | **Keep** (University) | Observatory removed (to unclutter); thematic fit with Lumieres theme |
| Germany | Assembly Plant (Factory) | **Longhouse** (Granary) | Late/weak building; replaced with an early impactful one with thematic fit (LBK (Linearbandkeramik / Linear Pottery culture)) and gameplay fit for Germany's growth profile |
| Greece | Odeon (Colosseum) | **Keep** (Keep) | |
| Holy Roman | Rathaus (Courthouse) | **Keep** (Keep) | |
| Inca | Terrace (Granary) | **Qullqa** (Keep) | Renaming for thematic fit; rework for historical accuracy and to make it stronger (financial/organized incan economy profile) rather than mixing culture and growth weirdly and in a bit op way. |
| India | Mausoleum (Jail) | **Keep** (Keep) | Jail is moved to late Classical so fine as such |
| Japan | Shale Plant (Factory) | **Doujou** (Jail) | Late/weak building; replaced with an early impactful one; thematic fit and boosts Tokugawa/Japan's isolationist profile by strengthening its espionage and military independence potential |
| Khmer | Baray (Aqueduct) | **Keep** (Keep) | |
| Korea | Seowon (University) | **Gyeongdang** (Library) | Use a more ancient-coded Korean school identity tied to Korea's long education tradition (Taehak, Gyeongdang, later state academies). This uses underused library slot, declutters overused university slot, and keeps the civ's science identity, and also reflects the historical pairing of scholarship, state ideology, and social cohesion. Great general chance similarly to how it was done for the japan_doujou (martial arts training). |
| Mali | Mint (Forge) | **Keep** (Keep) | |
| Maya | Ball Court (Colosseum) | **Keep** (Keep) | |
| Mongol | Ger (Stable) | **Keep** (Keep) | |
| Native America | Totem (Monument) | **Keep** (Keep) | |
| Netherlands | Dike (Levee) | **Keep** (Keep) | |
| Ottoman | Hammam (Aqueduct) | **Keep** (Keep) | |
| Persia | Apothecary (Grocer) | **Keep** (Keep) | |
| Portugal | Feitoria (Custom House) | **Keep** (Keep) | Focus on trades routes and new Joao's financial/imperialistic profile more |
| Rome | Forum (Market) | **Keep** (Keep) | |
| Russia | Research Institute (Observatory) | **Gord** (Castle) | Observatory removed (to unclutter); fits Russia's aggressive/military profile |
| Scandinavia | Trading Post (Lighthouse) | **Keep** (Port) | Following water buildings rework; port is a stronger production hub especially given military profile of Ragnar, closer to historical time too |
| Spain | Citadel (Castle) | **Keep** (Keep) | |
| Sumeria | Ziggurat (Courthouse) | **Ziggurat** (Monument) | Much stronger than late courthouse. Fits sumerian early religious/historical/culture profile more; better thematic fit for an ancient civilization. |
| Zulu | Ikhanda (Barracks) | **Keep** (Keep) | |

## Civ-specific units rework

Done with the help of GPT-5.5 Thinking thanks. Since balance is prone to change, this section should be read as "as of now" documentation; see Sevopedia Unit for updated data.

General system context from the SAS docs: combat types are refined/split (archer subtypes, mounted melee/ranged, melee polearm/shock); weak/late civ-specific units are often replaced by earlier or more impactful ones; selected resource requirements are relaxed for civ-specific variants while generic Swordsman/Cannon remain iron-only to preserve strategic pressure.

Legend: `str` = combat strength; `h` = hammer cost; `mv` = movement; `tech` = required tech(s); `res` = required bonus/resource(s); `free` = free promotion(s); `mods` = selected modifier changes; `vsClass`/`vsCombat` = modifiers against a unit class/combat type; `TerrainAtk`/`TerrainDef` and `FeatureAtk`/`FeatureDef` = terrain/feature attack/defense modifiers.

Terrain/feature modifiers are usually treated as secondary flavor or fine-tuning in this table. Rationales mention them only when they materially change timing, access, matchups, or role; otherwise the diff/summary columns are enough.

Note: some units like Worker-type units are civilian as of now, so their terrain/feature combat modifiers are documented mainly for consistency/exhaustiveness.

| Civ | Before | After | Old UU → current SAS UU diff | SAS generic → SAS UU delta | Summary / rationale |
| --- | --- | --- | --- | --- | --- |
| America / USA | AMERICAN_NAVY_SEAL (MARINE; GUN) | **USA_PATRIOT** (**RIFLEMAN**; Keep) | str 24→15, h 160→120; tech INDUSTRIALISM, RIFLING→MILITARY_TRADITION, FIREARMS; free AMPHIBIOUS, MARCH→FIRST_STRIKE1; gains FeatureAtk FOREST 25, FeatureDef FOREST 25, TerrainAtk DESERT 10, TerrainAtk GRASS 25, +6 more; loses FirstStrikeChance 1, FirstStrikes 1, vsClass ARTILLERY 50, vsClass MACHINE_GUN 50 | vs SAS RIFLEMAN: free none→FIRST_STRIKE1; gains FeatureAtk FOREST 25, FeatureDef FOREST 25, TerrainAtk DESERT 10, TerrainAtk GRASS 25, +4 more. | Earlier Patriot/Rifleman timing is more useful and plausible than a late Marine-only UU. |
| Arabia | ARABIA_CAMELARCHER (KNIGHT; MOUNTED) | **ARABIA_HAJJAN** (**CAMEL_KNIGHT**; **MOUNTED_RANGED**) | h 90→95; tech GUILDS, HORSEBACK_RIDING, ARCHERY→CHIVALRY, MOUNTED_COMBAT; res none→CAMEL, IRON; free none→FIRST_STRIKE1; mods Withdraw 15→20; gains FeatureDef FOREST -25, FeatureDef JUNGLE -25, TerrainAtk DESERT 50, TerrainDef DESERT 35 | vs SAS CAMEL_KNIGHT: free none→FIRST_STRIKE1; mods TerrainAtk DESERT 25→50, TerrainDef DESERT 25→35, Withdraw 10→20; loses FeatureAtk FOREST -25, FeatureAtk JUNGLE -25. | Mounted-ranged camel knight: stronger vs Pikemen and broader polearm counters than melee knights; resists gun/modern units better than melee-mounted units do (same logic as Cuirassiers/Dragoons); retreat supports skirmishing. |
| Aztec | AZTEC_JAGUAR (SWORDSMAN; MELEE) | Keep (**AXEMAN**; **MELEE_SHOCK**) | tech IRON_WORKING→BRONZE_WORKING; free WOODSMAN1→SENTRY; gains FeatureAtk FOREST 10, FeatureAtk JUNGLE 25, FeatureDef FOREST 10, FeatureDef JUNGLE 50, +2 more; loses CityAtk 10 | vs SAS AXEMAN: res COPPER, IRON→none; free none→SENTRY; mods FeatureAtk JUNGLE 10→25, FeatureDef JUNGLE 10→50. | Jaguar moves to earlier no-bonus Axeman role; old Jaguar was weak/late and worse than normal Swordsman in practice; supports early aggressive Aztec profile and Sacrificial Altar/slavery economy. |
| Babylon | BABYLON_BOWMAN (ARCHER; ARCHER) | Keep (**LONGBOWMAN**; **ARCHER_BOW_SHORT**) | str 3→5, h 25→45; tech ARCHERY→CONSTRUCTION, HUNTING; free none→CITY_RAIDER1; mods CityDef 50→25; gains FirstStrikeChance 1, TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, +3 more; loses vsCombat MELEE 50 | vs SAS LONGBOWMAN: str 4→5; free RETREAT1→CITY_RAIDER1; mods CityDef 50→25; gains TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, TerrainDef GRASS 25, +1 more; loses CityAtk 10. | Bowman moves to Construction Longbow slot; more versatile than ancient city garrison and can support offensive Babylon pushes. |
| Byzantium | BYZANTINE_CATAPHRACT (KNIGHT; MOUNTED) | Keep (**HORSE_KNIGHT**; **MOUNTED_MELEE**) | h 90→105; tech GUILDS, HORSEBACK_RIDING→CHIVALRY, MOUNTED_COMBAT; gains FeatureAtk FOREST -25, FeatureAtk JUNGLE -25, FeatureDef FOREST -25, FeatureDef JUNGLE -25, +7 more | vs SAS HORSE_KNIGHT: str 10→12, h 95→105; gains TerrainAtk DESERT 10, TerrainAtk GRASS 25, TerrainAtk PLAINS 10, TerrainDef DESERT 10, +2 more. | Slight nerf through cost increase as Cataphract was a bit too strong. |
| Carthage | CARTHAGE_NUMIDIAN_CAVALRY (HORSE_ARCHER; MOUNTED) | Keep (Keep; **MOUNTED_MELEE**) | str 5→6; tech HORSEBACK_RIDING, ARCHERY→MOUNTED_COMBAT, HUNTING; free FLANKING1→RETREAT1; mods Withdraw 20→15; gains FeatureAtk FOREST -25, FeatureAtk JUNGLE -25, FeatureDef FOREST -25, FeatureDef JUNGLE -25, +4 more; loses vsCombat MELEE 50 | vs SAS HORSE_ARCHER: free none→RETREAT1; mods Withdraw 20→15; gains FeatureAtk FOREST -25, FeatureAtk JUNGLE -25, TerrainAtk DESERT 10, TerrainAtk PLAINS 25, +2 more. | Raises Numidian to Horse Archer-level strength and shifts from narrow anti-melee gimmick to more general mobile skirmisher/withdraw unit. |
| Celts | CELTIC_GALLIC_WARRIOR (SWORDSMAN; MELEE) | Keep (Keep; **MELEE_SHOCK**) | h 40→42; free GUERILLA1→FIRST_STRIKE1; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk PLAINS 10, TerrainDef PLAINS 10 | vs SAS SWORDSMAN: res IRON→COPPER, IRON; free none→FIRST_STRIKE1; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk PLAINS 10, TerrainDef PLAINS 10. | Guerilla hill-defense was too situational and a bad match for Brennus/Boudica aggressive profile; first-strike sword role is more generally useful; copper/iron access improves flexibility. |
| China | CHINA_CHOKONU (CROSSBOWMAN; ARCHER) | **CHINA_ZHUGE_NU** (Keep; **ARCHER_CROSSBOW**) | h 60→65; tech MACHINERY, ARCHERY→CIVIL_SERVICE, HUNTING; res IRON→COPPER, IRON; free none→COLLATERAL_DAMAGE1; mods Collateral 50→15, CollateralLimit 60→200; gains FeatureAtk FOREST 25, FeatureDef FOREST 25, HillsAtk 25, HillsDef 25, +4 more; loses vsCombat MELEE 50 | vs SAS CROSSBOWMAN: res IRON→COPPER, IRON; free none→COLLATERAL_DAMAGE1; mods FirstStrikes 1→2; gains Collateral 15, CollateralLimit 200, CollateralMaxUnits 5, FeatureAtk FOREST 25, +3 more. | Slightly reduces old collateral burst and anti-melee focus, but adds first-strike utility and broader buildability through copper/iron access. |
| Netherlands / Dutch | NETHERLANDS_OOSTINDIEVAARDER (FRIGATE; NAVAL) | **DUTCH_SWIFT_WORKER** (**WORKER**; **NONE**) | str 8→0, h 90→50, mv 5→3; tech CHEMISTRY, ASTRONOMY→none; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, WorkRate 100; loses Bombard 12, Cargo 3 | vs SAS WORKER: mv 2→3; gains FeatureAtk FOREST 50, FeatureDef FOREST 50. | Late naval UU was too weak/situational; early Worker is useful on every map, better fits Dutch economy/growth, restores old BTS Fast Worker effect, and gives India real worker-UU company. |
| Egypt | EGYPT_WARCHARIOT (CHARIOT; MOUNTED) | **EGYPTIAN_WAR_CHARIOT** (Keep; **MOUNTED_MELEE**) | mods vsClass AXEMAN 100→75; gains FeatureAtk FOREST -50, FeatureAtk JUNGLE -50, FeatureDef FOREST -25, FeatureDef JUNGLE -25, +5 more | vs SAS CHARIOT: str 4→5; gains TerrainAtk DESERT 35, TerrainAtk GRASS 10, TerrainDef DESERT 35, TerrainDef GRASS 10. | — |
| England | ENGLISH_REDCOAT (RIFLEMAN; GUN) | **ENGLISH_YEOMAN_ARCHER** (**CROSSBOWMAN**; **ARCHER_BOW_LONG**) | str 14→7, h 110→60; tech RIFLING→CIVIL_SERVICE, HUNTING; free none→SENTRY; gains CityDef 10, FeatureAtk FOREST 25, FeatureDef FOREST 50, FirstStrikes 1, +4 more; loses vsCombat GUN 25, vsCombat MOUNTED 25 | vs SAS CROSSBOWMAN: str 6→7, h 65→60; res IRON→none; free none→SENTRY; mods HillsAtk 25→15, HillsDef 25→15, vsCombat MELEE_SHOCK 50→10; gains CityDef 10, FeatureAtk FOREST 25, FeatureDef FOREST 50. | Earlier no-iron Yeoman gives England defensive/versatile power before late Redcoat timing; less anti-melee focused than SAS Crossbow, but overall stronger, easier to build, and better fits England's defensive/economy/growth profile. |
| Ethiopia | ETHIOPIAN_OROMO_WARRIOR (MUSKETMAN; GUN) | Keep | str 9→12, h 80→100; tech GUNPOWDER→FIREARMS; free DRILL1, DRILL2→FIRST_STRIKE1; gains TerrainAtk DESERT 10, TerrainAtk GRASS 10, TerrainAtk PLAINS 25, TerrainDef DESERT 10, +2 more | vs SAS MUSKETMAN: free none→FIRST_STRIKE1; gains FirstStrikes 1, TerrainAtk DESERT 10, TerrainAtk GRASS 10, TerrainAtk PLAINS 25, +3 more. | — |
| France | FRENCH_MUSKETEER (MUSKETMAN; GUN) | Keep | str 9→12, h 80→100, mv 2→1; tech GUNPOWDER→FIREARMS; free none→COUNTER_MOUNTED, COLLATERAL_DAMAGE1; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk PLAINS 10, TerrainAtk TUNDRA 10, +2 more | vs SAS MUSKETMAN: free none→COUNTER_MOUNTED, COLLATERAL_DAMAGE1; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk PLAINS 10, TerrainAtk TUNDRA 10, +2 more. | Buffs weak move-speed-only effect: movement helps positioning, not combat; anti-mounted/collateral gives actual fighting value against strong Renaissance/Industrial mounted units. |
| Germany | GERMAN_PANZER (TANK; ARMOR) | **GERMAN_HUSSAR** (**DRAGOON**; **MOUNTED_RANGED**) | str 28→16, h 180→140; tech INDUSTRIALISM, RIFLING→MILITARY_TRADITION, FIREARMS, MOUNTED_COMBAT; res OIL→HORSE; free BLITZ→RETREAT1; gains FeatureAtk FOREST 25, FeatureDef JUNGLE -25, TerrainAtk TUNDRA 10, TerrainDef TUNDRA 10, +2 more; loses FirstStrikes 2, vsCombat ARMOR 50 | vs SAS DRAGOON: h 150→140; free none→RETREAT1; gains FeatureAtk FOREST 25, TerrainAtk TUNDRA 10, TerrainDef TUNDRA 10; loses FeatureDef FOREST -25. | Earlier than usually-too-late Panzer; later UU timing helps counterbalance Germany's strong early UB. |
| Greece | GREEK_PHALANX (AXEMAN; MELEE) | **GREEK_HOPLITE** (**SPEARMAN**; **MELEE_POLEARM**) | gains CityDef 10, FeatureAtk FOREST 10, FeatureDef FOREST 10, HillsAtk 10, +7 more; loses defVsClass CHARIOT 100, vsCombat MELEE 50 | vs SAS SPEARMAN: mods vsCombat MELEE_SHOCK 10→25; gains CityDef 10, TerrainAtk GRASS 10, TerrainAtk PLAINS 25, TerrainDef GRASS 10, +1 more; loses FeatureAtk JUNGLE 10, FeatureDef JUNGLE 10. | Spear/polearm Hoplite is more accurate; SAS Spearman buff makes it better outside cities too, especially vs melee, while still guarding stacks against horse/camel archers and War Elephants. |
| Holy Rome | HOLY_ROMAN_LANDSKNECHT (PIKEMAN; MELEE) | **HOLY_ROMAN_HOUFNICE** (**CANNON**; **SIEGE**) | str 6→13, h 60→130; tech ENGINEERING→CHEMISTRY, MACHINERY; res IRON→COPPER, IRON; free none→CITY_BOMBARD_DAMAGE; gains Bombard 12, Collateral 100, CollateralLimit 200, CollateralMaxUnits 6, +6 more; loses vsCombat MELEE 100, vsCombat MOUNTED 100 | vs SAS CANNON: h 140→130; res IRON→COPPER, IRON; free none→CITY_BOMBARD_DAMAGE; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk PLAINS 10, TerrainAtk TUNDRA 10, +2 more. | Old Landsknecht was a weak late defensive melee unit near guns; Houfnice gives Charlemagne offensive siege that stays useful into the Renaissance. |
| Inca | INCAN_QUECHUA (WARRIOR; MELEE) | Keep (**SWORDSMAN**; **MELEE_SHOCK**) | str 2→6, h 15→42; tech none→IRON_WORKING; res none→COPPER, IRON; free COMBAT1→MOBILITY_COST; gains CityAtk 10, FeatureAtk FOREST 10, FeatureDef FOREST 10, HillsAtk 25, +5 more; loses CityDef 25 | vs SAS SWORDSMAN: res IRON→COPPER, IRON; free none→MOBILITY_COST; gains FeatureAtk FOREST 10, FeatureDef FOREST 10, HillsAtk 25, HillsDef 25, +4 more. | AdvCiv Quechua was too weak and obsolete too quickly in the very early Warrior slot; later Swordsman-slot Quechua fits Inca's builder/economy profile and later historical identity better. |
| India | INDIAN_FAST_WORKER (WORKER; NONE) | Keep | h 60→50; gains FeatureAtk JUNGLE 10, FeatureDef JUNGLE 10, TerrainAtk DESERT 10, TerrainAtk PLAINS 25, +2 more | vs SAS WORKER: gains FeatureAtk JUNGLE 10, FeatureDef JUNGLE 10, TerrainAtk DESERT 10, TerrainAtk PLAINS 25, +2 more. | — |
| Japan | JAPAN_SAMURAI (MACEMAN; MELEE) | Keep (Keep; **MELEE_SHOCK**) | h 70→65; tech CIVIL_SERVICE, MACHINERY→CIVIL_SERVICE, IRON_WORKING; res IRON→COPPER, IRON; free DRILL1→COMBAT1; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, FirstStrikeChance 1, TerrainAtk TUNDRA 10, +3 more; loses FirstStrikes 2, vsCombat MELEE 50 | vs SAS MACEMAN: free none→COMBAT1; mods vsCombat MELEE_SHOCK 25→50; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, FirstStrikeChance 1, TerrainAtk TUNDRA 10, +1 more. | — |
| Khmer | KHMER_BALLISTA_ELEPHANT (WAR_ELEPHANT; MOUNTED) | Keep (Keep; **MOUNTED_RANGED**) | tech CONSTRUCTION, HORSEBACK_RIDING→MOUNTED_COMBAT, ANIMAL_HUSBANDRY; res IVORY→ELEPHANTS; gains FeatureAtk JUNGLE 25, FeatureDef FOREST -25, TerrainAtk PLAINS 25, TerrainDef PLAINS 25, +1 more; loses vsCombat MOUNTED 50 | vs SAS WAR_ELEPHANT: mods FeatureAtk JUNGLE -25→25, TerrainAtk PLAINS 10→25, TerrainDef PLAINS 10→25; gains FirstStrikes 1; loses FeatureAtk FOREST -25, FeatureDef JUNGLE -25. | Ranged War Elephant gives different matchups than base melee War Elephant, especially vs Spearman/Pikeman and broader polearm counters; not just a raw strength buff. |
| Korea | KOREAN_HWACHA (CATAPULT; SIEGE) | Keep (**CANNON**; Keep) | str 5→13, h 50→140; tech CONSTRUCTION→CHEMISTRY, MACHINERY; free none→COLLATERAL_DAMAGE1; mods Bombard 8→12, CollateralLimit 50→200, CollateralMaxUnits 6→7; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk GRASS 10, TerrainDef GRASS 10; loses vsCombat MELEE 50 | vs SAS CANNON: res IRON→none; free none→COLLATERAL_DAMAGE1; mods CollateralMaxUnits 6→7; gains FeatureAtk FOREST 50, FeatureDef FOREST 50, TerrainAtk GRASS 10, TerrainDef GRASS 10. | Catapult/Trebuchet window is short; Cannon-slot Hwacha stays useful much longer and better fits Korean gunpowder/fire-arrow technology. |
| Mali | MALI_SKIRMISHER (ARCHER; ARCHER) | Keep (**LONGBOWMAN**; **ARCHER_BOW_SHORT**) | str 4→5, h 25→45; tech ARCHERY→CONSTRUCTION, HUNTING; free none→FIRST_STRIKE1; mods CityDef 50→25; gains FeatureAtk JUNGLE 10, FeatureDef JUNGLE 10, FirstStrikes 1, TerrainAtk DESERT 25, +4 more; loses HillsDef 25 | vs SAS LONGBOWMAN: str 4→5; free RETREAT1→FIRST_STRIKE1; mods CityDef 50→25, Withdraw 25→50; gains FeatureAtk JUNGLE 10, FeatureDef JUNGLE 10, TerrainAtk DESERT 25, TerrainAtk PLAINS 25, +2 more; loses CityAtk 10, HillsDef 25. | Skirmisher becomes active field defender/harasser instead of early city garrison. |
| Maya | MAYA_HOLKAN (SPEARMAN; MELEE) | Keep (Keep; **MELEE_POLEARM**) | str 4→5; tech HUNTING, BRONZE_WORKING→BRONZE_WORKING; free none→RETREAT1; gains FeatureAtk FOREST 10, FeatureAtk JUNGLE 25, FeatureDef FOREST 10, FeatureDef JUNGLE 50, +4 more; loses vsCombat MOUNTED 100 | vs SAS SPEARMAN: res COPPER, IRON→none; free none→RETREAT1; mods FeatureAtk JUNGLE 10→25, FeatureDef JUNGLE 10→50; gains Withdraw 15, vsCombat MOUNTED_RANGED 50; loses HillsAtk 10, HillsDef 25. | Old Holkan was weak; SAS Spearman buffs plus Retreat make it a stronger skirmisher/support unit for field fighting and even city attacks. |
| Mongolia | MONGOL_KESHIK (HORSE_ARCHER; MOUNTED) | **MONGOL_KHISHIGTEN** (**HORSE_KNIGHT**; **MOUNTED_MELEE**) | str 6→10, h 50→105; tech HORSEBACK_RIDING, ARCHERY→CHIVALRY, MOUNTED_COMBAT; res HORSE→HORSE, IRON; free none→BLITZKRIEG, RETREAT1; mods Withdraw 20→15; gains FeatureAtk JUNGLE -25, FeatureDef JUNGLE -25, TerrainAtk DESERT 25, TerrainAtk GRASS 25, +2 more; loses FirstStrikes 1, vsClass CATAPULT 50 | vs SAS HORSE_KNIGHT: h 95→105; free none→BLITZKRIEG, RETREAT1; mods Withdraw 10→15; gains TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, TerrainDef GRASS 25; loses FeatureAtk FOREST -25, FeatureDef FOREST -25. | Keshik window was too short before Knights; Horse Knight slot gives Mongolia a longer medieval cavalry window toward its historical peak. Free terrain movement, retreat, and Blitz emphasize tactical control over Cataphract-style raw strength. |
| Native America | NATIVE_AMERICA_DOG_SOLDIER (AXEMAN; MELEE) | Keep (Keep; **MELEE_SHOCK**) | str 4→5; free none→FIRST_STRIKE1; gains TerrainAtk DESERT 25, TerrainAtk GRASS 10, TerrainAtk PLAINS 10, TerrainAtk TUNDRA 10, +6 more; loses vsCombat MELEE 100 | vs SAS AXEMAN: res COPPER, IRON→none; free none→FIRST_STRIKE1; gains TerrainAtk DESERT 25, TerrainAtk GRASS 10, TerrainAtk PLAINS 10, TerrainAtk TUNDRA 10, +4 more; loses FeatureAtk FOREST 10, FeatureAtk JUNGLE 10, FeatureDef FOREST 10, FeatureDef JUNGLE 10. | No-metal anti-sword pressure without locking Dog Soldier into pure defense. |
| Ottomans | OTTOMAN_JANISSARY (MUSKETMAN; GUN) | Keep | str 9→14, h 80→110; tech GUNPOWDER→FIREARMS; gains TerrainAtk DESERT 10, TerrainAtk GRASS 25, TerrainAtk PLAINS 10, TerrainDef DESERT 10, +2 more; loses vsCombat ARCHER 25, vsCombat MELEE 25, vsCombat MOUNTED 25 | vs SAS MUSKETMAN: str 12→14, h 100→110; gains TerrainAtk DESERT 10, TerrainAtk GRASS 25, TerrainAtk PLAINS 10, TerrainDef DESERT 10, +2 more. | — |
| Persia | PERSIA_IMMORTAL (CHARIOT; MOUNTED) | Keep (**SWORDSMAN**; **MELEE_POLEARM**) | str 4→6, h 30→38, mv 2→1; tech THE_WHEEL→IRON_WORKING; res HORSE→COPPER, IRON; gains CityAtk 10, TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, +3 more; loses Withdraw 10, vsClass AXEMAN 100, vsCombat ARCHER 25 | vs SAS SWORDSMAN: h 42→38; res IRON→COPPER, IRON; gains TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, TerrainDef GRASS 25, +2 more. | Closer to Civ3 sword-based Immortal: Chariot anti-archer rush→later Swordsman/Polearm fighter with bonuses vs melee-shock and mounted-melee; copper/iron access improves buildability. |
| Portugal | PORTUGAL_CARRACK (CARAVEL; NAVAL) | Keep (**GALLEON**; Keep) | str 3→5, mv 4→6; tech OPTICS→ASTRONOMY; mods Cargo 2→4; gains TerrainAtk COAST 10, TerrainAtk OCEAN 25, TerrainDef COAST 25, TerrainDef OCEAN 25 | vs SAS GALLEON: str 4→5, h 70→60, mv 4→6; gains TerrainAtk COAST 10, TerrainAtk OCEAN 25, TerrainDef COAST 25, TerrainDef OCEAN 25. | Naval UUs are usually weak/situational in SAS, but Portugal is the iconic exception: stronger, faster Carrack is closer to military Frigate-grade ocean control while still supporting trade/transport. |
| Rome | ROME_PRAETORIAN (SWORDSMAN; MELEE) | **ROMAN_LEGIONARY** (Keep; **MELEE_SHOCK**) | str 7→6, h 40→42; res IRON→COPPER, IRON; free MARCH→COMBAT1; gains CityAtk 10, FeatureAtk FOREST 10, FeatureDef FOREST 10, TerrainAtk DESERT 10, +3 more | vs SAS SWORDSMAN: res IRON→COPPER, IRON; free none→COMBAT1; gains FeatureAtk FOREST 10, FeatureDef FOREST 10, TerrainAtk DESERT 10, TerrainAtk PLAINS 25, +2 more. | Strength reduced because Praetorian was too strong; broader buildability through copper/iron access; weak March healing swapped for Combat I to support Roman classical aggression/solid expansion. |
| Russia | RUSSIA_COSSACK (CAVALRY; MOUNTED) | Keep (**DRAGOON**; **MOUNTED_RANGED**) | str 15→16, h 120→150; tech MILITARY_TRADITION, RIFLING, HORSEBACK_RIDING→MILITARY_TRADITION, FIREARMS, MOUNTED_COMBAT; gains FeatureAtk FOREST 25, FeatureDef JUNGLE -25, TerrainAtk SNOW 50, TerrainAtk TUNDRA 25, +4 more; loses vsCombat MOUNTED 50 | vs SAS DRAGOON: gains FeatureAtk FOREST 25, TerrainAtk SNOW 50, TerrainAtk TUNDRA 25, TerrainDef SNOW 50, +3 more; loses FeatureDef FOREST -25. | — |
| Spain | SPANISH_CONQUISTADOR (CUIRASSIER; MOUNTED) | Keep (**HORSE_CUIRASSIER**; **MOUNTED_RANGED**) | str 12→13, h 100→130; tech MILITARY_TRADITION, GUNPOWDER, HORSEBACK_RIDING→FIREARMS, MOUNTED_COMBAT; free none→AMPHIBIOUS; mods Withdraw 15→30; gains FeatureAtk FOREST 25, FeatureDef JUNGLE -25, TerrainAtk PLAINS 25, TerrainDef PLAINS 25; loses vsCombat MELEE 50 | vs SAS HORSE_CUIRASSIER: free none→AMPHIBIOUS; mods Withdraw 15→30; gains FeatureAtk FOREST 25, TerrainAtk PLAINS 25, TerrainDef PLAINS 25; loses FeatureDef FOREST -25. | — |
| Sumeria | SUMERIAN_VULTURE (AXEMAN; MELEE) | Keep (Keep; **MELEE_SHOCK**) | str 6→5; gains TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, TerrainDef GRASS 25, +2 more; loses vsCombat MELEE 25 | vs SAS AXEMAN: mods vsCombat MELEE_SHOCK 25→50; gains TerrainAtk DESERT 25, TerrainAtk GRASS 25, TerrainDef DESERT 25, TerrainDef GRASS 25; loses FeatureAtk FOREST 10, FeatureAtk JUNGLE 10, FeatureDef FOREST 10, FeatureDef JUNGLE 10. | — |
| Vikings / Scandinavia | VIKING_BESERKER (MACEMAN; MELEE) | **SCANDINAVIA_VIKING** (Keep; **MELEE_SHOCK**) | h 70→65; tech CIVIL_SERVICE, MACHINERY→CIVIL_SERVICE, IRON_WORKING; mods CityAtk 10→20; gains FeatureAtk FOREST 25, FeatureDef FOREST 25, TerrainAtk SNOW 50, TerrainAtk TUNDRA 25, +4 more; loses vsCombat MELEE 50 | vs SAS MACEMAN: free none→AMPHIBIOUS; gains CityAtk 20, FeatureAtk FOREST 25, FeatureDef FOREST 25, TerrainAtk SNOW 50, +3 more. | Replaces awkward Berserker framing with iconic Viking raider role; stronger amphibious Maceman matters more before Knights/Crossbows make standard Macemen feel weak, matching the historical Viking era better. |
| Zulu | ZULU_IMPI (SPEARMAN; MELEE) | Keep (Keep; **MELEE_POLEARM**) | str 4→5; tech HUNTING→BRONZE_WORKING; free MOBILITY→none; gains HillsAtk 10, HillsDef 25, TerrainAtk DESERT 10, TerrainAtk GRASS 25, +6 more; loses vsCombat MOUNTED 100 | vs SAS SPEARMAN: mv 1→2; mods vsCombat MELEE_SHOCK 10→25; gains TerrainAtk DESERT 10, TerrainAtk GRASS 25, TerrainAtk PLAINS 10, TerrainDef DESERT 10, +2 more; loses FeatureAtk FOREST 10, FeatureAtk JUNGLE 10, FeatureDef FOREST 10, FeatureDef JUNGLE 10. | SAS Spearman buffs and stronger melee-shock focus make Impi a stronger field fighter; keeps fast 2-move pressure for Shaka/Zulu aggression; still counters mounted units. |
| Kingdom of Benin | — | New **KINGDOM_OF_BENIN_DISCIPLINED_CROSSBOWMAN** (**CROSSBOWMAN**; **ARCHER_CROSSBOW**) | new SAS UU; str 6; h 65; mv 1; tech CIVIL_SERVICE, HUNTING; res COPPER, IRON; free LOGISTICS; mods HillsAtk 25, HillsDef 25, Withdraw 35, FirstStrikes 1, +5 more | vs SAS CROSSBOWMAN: res IRON→COPPER, IRON; free none→LOGISTICS; mods Withdraw 25→35; gains FeatureAtk JUNGLE 50, FeatureDef JUNGLE 50, TerrainAtk PLAINS 25, TerrainDef PLAINS 25. | Broader buildability through Copper/Iron access; Logistics promotion suits Benin organized warfare/siege-logistics theme; field kit supports fighting outside static defense. |
| Ireland | — | New **IRELAND_FLYING_COLUMN** (**RIFLEMAN**; **GUN**) | new SAS UU; str 15; h 120; mv 1; tech MILITARY_TRADITION, FIREARMS; free LOGISTICS; mods Withdraw 10, vsCombat MOUNTED_MELEE 50, vsCombat MOUNTED_RANGED 25, FeatureAtk FOREST 25, +1 more | vs SAS RIFLEMAN: free none→LOGISTICS; gains FeatureAtk FOREST 25, FeatureDef FOREST 50, Withdraw 10. | Ireland is late historically, so Rifleman timing avoids an even-later Infantry UU; Logistics/withdraw fits guerrilla/independence-war style while keeping the unit relevant. |

## Leaders' traits rework

While doing/considering the holy roman empire civ-specific unit's rework or replacement, i have noticed charlemagne's traits were not in accord with his historical profile (i asked chatgpt 5 thanks since i don't know too much if at all about his history and leader profile or such and to be sure and have its advice as well thanks).

It is also limiting when we want as now to assign a new unit e.g. to the holy roman empire or possibly building, so i thought this was a good time to rework leader traits for balance, accuracy, and overall synergy with the civ's profile, as well as its civ-specific units and buildings, and also to match ingame behaviour +/- more(/most?) importantly xml or and such if / as much as possible or relevant i mean.

Done with the help of chatgpt 5 thanks a lot and thanks to my prompts too or adjustments or thoughts or formatting or such, check if accurate. Also, since then, reviewed and adjusted with the help of several other LLMs.

Note: asking GPT-5.5-Thinking (i.e. ChatGPT) in a temporary chat additionally to the usual history-aware chat gives/yields surprisingly good results.

### previous state

This is extracted from the [CIV4LeaderHeadInfos.xml](/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml) rather, as we had issues importing it from our custom leaders_data_to_ or it took too much time, due to data being too big or i guess maybe if i'm not mistaken.

#### main table before changes to traits

See below in the main table after changes as it includes the before values as well.

#### raw traits assignment count

| Trait | Count |
| --- | --- |
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
| --- | --- |
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

### new state after rework with rationale or such

#### main table after changes to traits

| Leader | Current Traits | Recommendation | Rationale |
| --- | --- | --- | --- |
| Alexander | Philosophical, Aggressive | **Keep** | Philosopher-king + relentless conqueror fits. |
| Asoka | Spiritual, Organized | **Spiritual, Protective** | Edicts focused on welfare/stability: medical care for people & animals, wells/trees, non-violence. Reads as "guardian of the realm's well-being." |
| Augustus | Imperialist, Industrious | **Keep** | Empire builder + massive works program. |
| Bismarck | Expansive, Industrious | **Organized, Protective** | Why not Aggressive? He orchestrated three short, limited wars (1864, 1866, 1870-71) to unify Germany, then spent the rest of his career preventing great-power war via alliance webs (Dreikaiserbund, Reinsurance Treaty, Congress of Berlin). That's sharp power politics, not a "wade-in-and-smash" military persona. He wasn't a battlefield leader; his hallmark is calculated diplomacy + internal statecraft. What really defines him? Organized: high-efficiency governance-central civil service, Reichsbank, tariffs, and the pioneering social insurance system (health 1883, accident 1884, old-age 1889). This maps perfectly to your "-75% upkeep" / efficient state. Protective (in your mod's sense = stability/no anarchy/health): post-1871 his entire strategy was systemic risk management (deterrence, balance) and domestically "order first" (Anti-Socialist Laws) plus worker protection through insurance-i.e., protecting the state's cohesion and people's welfare. Verdict (accuracy-first): Go Organized + Protective. It captures both the manager-state architect and the stability/health side far better than Aggressive. (Charismatic doesn't fit his public vibe, and Imperialistic doesn't match his reluctant, late, and limited colonial stance.) |
| Boudica | Charismatic, Aggressive | **Keep** | War leader rallying tribes; morale + offense. |
| Brennus | Spiritual, Charismatic | **Keep** | Druidic authority + chieftain charisma. |
| Catherine | Creative, Imperialist | **Philosophical, Imperialist** | Enlightened despot: corresponded with Voltaire/Diderot, issued the Nakaz, pushed legal/educational reform-more thinker-ruler than pure arts patron. Philosophical = ideas shaping policy. Catherine is the poster child for Enlightened absolutism: the Nakaz (Instruction), legal/education reforms, heavy engagement with Voltaire/Diderot, commissions on law and schooling. Her brand is "rules by ideas.". Creative = culture output/patronage. She absolutely patronized the arts (Hermitage, theatre), but that was a means to an ideological/modernizing end, not her core identity. If you want to signal culture yields in gameplay, Creative is fine; historically, it's secondary to her policymaking. |
| Charlemagne | Imperialist, Protective | **Imperialist, Organized** | For Charlemagne — Charles the Great, king of the Franks and later crowned emperor in 800 — I’d describe him as ambitious, energetic, commanding, religious, reform-minded, and often ruthless. He was not just a ceremonial ruler. He spent much of his reign campaigning, especially against the Saxons, whose conquest took more than 30 years, and he built a huge Frankish empire by force. At the same time, he cared a lot about administration, law, education, the church, and royal control; Britannica describes him as focused on making inherited political institutions more effective. So, in plain terms, Charlemagne’s personality was something like: warrior-king, empire-builder, Christian reformer, strict ruler, and organizer of a huge realm. He could be visionary and culturally important, but also brutal, especially in the forced Christianization of conquered peoples. Imperialistic: excellent fit; probably the best trait for him. He expanded Frankish power enormously through conquest, creating one of the largest Western European empires since Rome. Organized: excellent alternate; he cared about administration, law, education, church reform, royal agents, and governing a large empire. Historically, this may fit better than Protective. |
| Churchill | Charismatic, Protective | **Keep** | Wartime morale + defensive strategy. |
| Cyrus | Charismatic, Imperialist | **Keep** | Founder of vast empire; tolerant unifier. |
| Darius | Organized, Financial | **Keep** | Satrapies/roads/taxation; efficient and wealthy. |
| De Gaulle | Industrious, Charismatic | **Charismatic, Organized** | Resistance icon and founder of the Fifth Republic's institutions. Post-war modernization happened, but his identity is leadership + constitutional/administrative redesign more than building programs. |
| Elizabeth | Philosophical, Financial | **Creative, Financial** | Her era is literally shorthand for a cultural bloom: Shakespeare/Marlowe, theatres, court masques, music, letters. She wasn't a "philosopher-queen" so much as a savvy ruler who presided over (and patronized) an artistic boom. Keeping Financial also tracks (privateering, merchant ventures, early global trade). `<!-- custom: plus her being creative gives a very varied English civ with our current English leader other pairs -->` |
| Ewuare | Imperialist, Spiritual | **Spiritual, Industrious** | Benin's strong court/ritual religion. Benin's strength = urban works (walls/ditches), craft guilds, and court art; expansion via hegemony/tribute more than settler-style growth. Industrious captures that better than Imperialist. |
| Frederick | Philosophical, Organized | **Philosophical, Creative** | Enlightenment/arts over bureaucracy. |
| Gandhi | Spiritual, Philosophical | **Keep** | Canonical fit. |
| Grace O'Malley | Financial, Aggressive | **Keep** | Maritime raider profile and commerce fit; keep as-is. |
| Genghis Khan | Aggressive, Imperialist | **Keep** | Archetypal conqueror. |
| Gilgamesh | Protective, Creative | **Keep** | Walls/city defense + epic/civic culture. |
| Hammurabi | Organized, Aggressive | **Keep** | Hammurabi seems to have been disciplined, pragmatic, ambitious, legalistic, and highly concerned with royal authority. We do not know his “personality” in a modern psychological sense, because most surviving evidence is royal, administrative, or legal, but his actions suggest a ruler who wanted to impose order on a complicated kingdom. He ruled Babylon roughly 1792–1750 BCE, expanded it from a smaller city-state into a major territorial kingdom, and conquered much of southern Babylonia. He is most famous for the Code of Hammurabi, a large collection of legal decisions covering trade, family law, crime, slavery, debt, and civil disputes. So, in plain terms, I would describe him as: orderly, authoritarian, calculating, justice-focused, pious, and strategically aggressive. Not “nice,” exactly. His law code could be harsh, and punishments depended heavily on social class. But he clearly wanted to present himself as a king of law, stability, punishment, and social order. Organized: perfect fit; this is the best trait for him. Hammurabi is remembered above all as a lawgiver and administrator. The Code of Hammurabi, royal building projects, canals, temples, walls, and central authority all fit “Organized.” Aggressive: Good fit; he was not just a lawgiver; he was also a conqueror. Babylon became a major Mesopotamian power under him through military expansion. `<!-- custom: as of now, the Bowman (civ-specific Babylonian unit) does not synergize with the Aggressive trait, but this allows Babylon to stay relevant as a military/aggressive playstyle civ well into later eras (knights, alternative swordsmen play, guns, etc.). Plus, as of now the bowman is very strong so seems balanced as such. -->` |
| Hannibal | Financial, Charismatic | **Keep** | Hallmark = operational genius + multi-ethnic army cohesion and Italian defections after Cannae. More "inspire & outmaneuver" than brute-force brutality. Charismatic still supports a war playstyle (cheaper promos) without the raw smash of Aggressive; Financial keeps Carthaginian commerce. |
| Hatshepsut | Spiritual, Creative | **Spiritual, Financial** | Iconic Punt expedition + trade-focused reign; commerce funded temples/works. Her identity reads more "trade & temple economy" than "arts output." `<!-- custom: also will most likely buff her if i'm not mistaken, which is nice i think -->` |
| Huayna Capac | Industrious, Financial | **Industrious, Organized** | Inca economy was state-planned and labor-tax (mit'a), not money/market-driven. "Organized" fits roads, storehouses, and redistribution much better than "Financial." |
| Isabella | Spiritual, Expansive | **Spiritual, Imperialistic** | Isabella seems to have been deeply religious, disciplined, politically clever, personally austere, determined, and very hard-edged. She was not just a passive queen beside Ferdinand; she made major decisions, defended her claim in a succession war, took an active interest in the Granada campaign, and backed Columbus. She also had a strong sense of order and moral certainty. That could look like justice, seriousness, and administrative discipline to supporters, but also like rigidity, intolerance, and ruthlessness by modern standards, especially because of the Inquisition and the expulsion/conversion policies. Spiritual: Perfect fit; religion was central to her rule: “the Catholic” title, church strengthening, the Inquisition, the Granada crusading spirit, and religious unity as state policy. Imperialistic: very strong fit; She helped finish the Reconquista, supported overseas expansion through Columbus, and her reign began Spain’s New World empire. |
| Joao | Imperialist, Expansive | **Imperialist, Financial** | Maritime commerce + colonial charters; cleaner than Expansive overlap. |
| Julius Caesar | Organized, Imperialist | **Aggressive, Imperialist** | Primary identity = conqueror (Gaul, Civil War). Keep Imperialist for expansion; swap in Aggressive to reflect operational boldness. `<!-- custom: plus matches with xml profile of aggression and thematic epicness -->` |
| Justinian | Spiritual, Imperialist | **Philosophical, Industrious** | Big reconquests (Africa, Italy, S. Hispania) + colossal building + Corpus Juris Civilis are uncontested. Critics say the reconquest wars/taxation left the state overextended and then the Justinianic Plague hit hard; newer work debates how devastating the plague really was. Net: "restorer & codifier," but also "overstretched the empire.". Less "Spiritual," more "Legal/Scholar + Empire-builder.". Reconquests != colonization. His lasting mark is legal/intellectual codification + mega building (Hagia Sophia, fortifications), not founding/settler-driven growth. |
| Kublai Khan | Aggressive, Creative | **Keep** | For Kublai Khan, I’d describe his personality as: ambitious, pragmatic, cultured, commanding, imperial, administratively minded, and less purely destructive than Genghis Khan. Kublai was Genghis Khan’s grandson, became Great Khan in 1260, founded the Yuan dynasty, and completed the Mongol conquest of China in 1279. That made him the first Yuan ruler of all China. The big difference between Genghis and Kublai is that Genghis feels like the archetypal steppe conqueror, while Kublai feels more like a conqueror-emperor. He still used Mongol military power, but he also adopted Chinese-style administration, moved the capital to Dadu/Beijing, used centralized bureaucracy, supported roads, postal stations, canal repair, trade, and cultural life. So in plain terms: Kublai was a Mongol conqueror who wanted to rule like a Chinese emperor. Aggressive: Strong fit; He was still a Mongol war leader and completed the conquest of China. It fits, though not as perfectly as it does for Genghis. Creative: Surprisingly strong fit; This captures his courtly, cultural, capital-building side: Yuan China had major cultural development, foreign exchange, roads, postal systems, and a new imperial capital. `<!-- custom: plus from a gameplay stance not sharing imperialistic with genghis khan allows to have a more varied mongol civ (although both are as of now still aggressive, seems thematically and strategicall more varied as such for this civ, and reduces imperialistic overall footprint among all civs). -->` |
| Lincoln | Philosophical, Charismatic | **Keep** | Moral/philosophical leadership + national unity. |
| Louis XIV | Industrious, Creative | **Keep** | Palace/works + arts and culture. |
| Mansa Musa | Spiritual, Financial | **Keep** | Pilgrimage/religion + trans-Saharan wealth. He was devout (Hajj, mosques), *and* a patron of learning (Timbuktu/Sankore). |
| Michael Collins | Philosophical, Organized | **Keep** | Administrative/intelligence-state profile; keep as-is. |
| Mao Zedong | Expansive, Protective | **Aggressive, Protective** | Mass campaigns and external war (Civil War, Korea), purges, and militant mobilization read more "Aggressive" than "cheap administration." Protective still captures internal security/defense posture. `<!-- custom: i like this one very much as i think he was very brutal wasn't he xd, from very little i know about him -->` |
| Mehmed | Expansive, Organized | **Imperialist, Organized** | For Mehmed II “the Conqueror”, I’d describe his personality as: ambitious, severe, intelligent, autocratic, cultured, strategic, and intensely empire-minded. He was not just a battlefield ruler. He captured Constantinople in 1453, expanded Ottoman power through the Balkans and Anatolia, and helped turn the Ottoman state into a more centralized imperial system. Britannica describes him as a great military leader and notes that he reorganized Ottoman government, codified laws, and became a model of the autocratic Ottoman emperor. At the same time, Mehmed was not simply a crude conqueror. He was interested in scholarship, law, architecture, theology, and classical/Renaissance learning. After taking Constantinople, he tried to restore the city as an imperial capital, invited scholars and artists to court, and patronized major building projects. So, in plain terms, his “personality” was something like: a ruthless intellectual conqueror who wanted to be both an Islamic sultan and a new Roman emperor. Organized: Excellent fit; Probably his best trait. Mehmed centralized government, codified law, rebuilt Constantinople, and strengthened the imperial structure. Imperialistic: Perfect alternate; Honestly, this may fit better than Expansive. He was literally “the Conqueror,” aimed at imperial restoration, and saw himself as heir to Rome. |
| Moctezuma | Aggressive, Spiritual | **Keep** | Militarism + ritual/faith. |
| Napoleon | Organized, Charismatic | **Imperialist, Charismatic** | Signature is conquest + continental empire (client states, annexations). He *did* codify/administer, but his core identity isn't "low-upkeep governance"-it's expansion + leadership aura. |
| Pacal | Financial, Expansive | **Financial, Industrious** | Monumental architecture/engineering + trade. |
| Pericles | Philosophical, Creative | **Keep** | Golden Age of philosophy and arts. |
| Peter | Philosophical, Expansive | **Philosophical, Organized** | For Peter the Great, I’d describe his personality as: curious, energetic, forceful, practical, reformist, impatient, authoritarian, and often brutal. Peter was obsessed with making Russia stronger by learning from Western Europe. He modernized the army and government, promoted technology, education, trade, and naval power, and founded St. Petersburg as a new western-facing capital. He also expanded Russian power through wars against Sweden, the Ottoman Empire, and Persia. But he was not a gentle reformer. He increased the monarchy’s power over nobles and the Orthodox Church, and some reforms were imposed harshly. Britannica notes that his reforms could be brutal and costly, and that he even had his own son Alexis tortured after suspecting him of conspiracy. So, in plain terms, Peter was: a restless modernizer who wanted to drag Russia into great-power status, whether people liked it or not. Not “philosopher” in the calm academic sense, but he was curious, technical, experimental, and obsessed with learning from foreign experts. He modernized administration, strengthened bureaucracy, reformed the army and state, and centralized authority. This may fit him even better than Philosophical. |
| Qin Shi Huang | Industrious, Protective | **Keep** | Great Wall/standardization + legalist control. |
| Ragnar | Financial, Aggressive | **Keep** | Raiding/commerce + martial ferocity. |
| Ramesses | Spiritual, Industrious | **Keep** | Temple/monument builder with priestly legitimation. |
| Roosevelt | Industrious, Organized | **Industrious, Charismatic** | New Deal public works -> keep Industrious. His defining edge was coalition-building and morale (Fireside Chats, wartime leadership) more than bureaucratic cost efficiency. |
| Saladin | Protective, Spiritual | **Spiritual, Charismatic** | Admired by both sides; unifying religious leadership - not just a "defender." He led major offensive campaigns (Hattin, Jerusalem) and had broad admiration. Your switch to Spiritual, Charismatic is very defensible; I wouldn't go back to Protective unless you want to emphasize "shield of Islam" over his rallying aura. |
| Shaka | Aggressive, Expansive | **Aggressive, Organized** | Fits Ikhanda-style admin - "charismatic" in Civ terms can imply inspirational popularity; historically he ruled more by fear/discipline. Your pick Aggressive, Organized is perfect (impi/regimental system + logistics). I wouldn't use Charismatic here. |
| Sitting Bull | Philosophical, Protective | **Keep** | Visionary/teacher + defensive resistance. |
| Stalin | Industrious, Aggressive | **Keep** | Forced industrialization + ruthless offensives. |
| Suleiman | Imperialist, Philosophical | **Keep** | "Lawgiver" persona + patronage of learning fits Philosophical better than Spiritual for gameplay and history; keeps imperial scope. `<!-- custom: plus if i remember enough i read he was quite areligious or religious open no? If so phi might fit better indeed than spi no? Thanks thanks -->` |
| Suryavarman | Expansive, Creative | **Industrious, Creative** | Builder of Angkor; monumental works + culture. |
| Tokugawa | Protective, Aggressive | **Protective, Organized** | After unification, policy emphasized internal order, class discipline, and isolation over external aggression; governance beats battlefield ferocity. `<!-- custom: from a very quick search and my intuition/memory of what i read about him, he was very cautious and cunning/scheming rather so maybe aggressive doesn't fit as well; also from a balance standpoint, if he is isolated, he would benefit much more from tax/costs reduction to run smoothly his empire than aggressive right? If i may say i mean -->` |
| Victoria | Imperialist, Financial | **Keep** | Global empire + finance/trade. |
| Wang Kon | Financial, Protective | **Keep** | For Wang Kon, better romanized today as Wang Geon, I’d describe his personality as: pragmatic, patient, diplomatic, conciliatory, strategic, religious, and quietly ambitious. He founded the Goryeo dynasty in 918 and completed the unification of the Later Three Kingdoms by receiving Silla’s surrender in 935 and defeating Later Baekje in 936. Unlike someone like Shaka or Genghis, Wang Geon’s image is less “destroy everything” and more absorb, reconcile, and stabilize. Britannica notes that he went to great lengths to absorb people from defeated states, which fits the picture of a coalition-building founder rather than a purely destructive conqueror. So in plain terms: Wang Kon was a unifier-king: military enough to win, diplomatic enough to keep the peace afterward. Financial: Strong fit; Goryeo became a durable kingdom with aristocratic, administrative, and economic foundations. Wang Kon’s strength was consolidation, not reckless expansion. Protective: Good fit; He unified Korea and then focused on stabilizing and securing the realm. Protective fits a ruler who builds a defensible state rather than constantly expanding outward. `<!-- custom: in terms of gameplay, protective (and financial to a lesser extent) also fits the more defensive korean gameplay with the as of now library-based civ-specific building and overall defensive unit, and thematically, this maybe also fits the broader theme of the protective trait (stability, conciliation, etc.). It also gives Korea more ancient power with (financial immediate scaling + protective immediate def) which may better align with the Ancient Korea history stressing change of the civ-specific building too. -->` |
| Washington | Expansive, Charismatic | **Protective, Charismatic** | Preservation-first Fabian strategy in the Revolution + 1777 army-wide smallpox inoculation (public-health safeguarding). Still inspirational. |
| Willem van Oranje | Creative, Financial | **Keep** | Tolerance/trade + arts/commerce. |
| Zara Yaqob | Creative, Organized | **Spiritual, Organized** | Strong doctrinal/religious policy + centralized rule - deeply doctrinal, centralizing, sometimes harsh. Spiritual, Organized > Creative. (He wrote and enforced doctrine more than fostering open culture.) |

#### new traits total count

| Trait         | Count |
| ------------- | ----: |
| Aggressive    |    12 |
| Imperialist   |    12 |
| Organized     |    12 |
| Financial     |    12 |
| Philosophical |    11 |
| Spiritual     |    11 |
| Industrious   |    11 |
| Charismatic   |    11 |
| Protective    |    10 |
| Creative      |     8 |

#### new pairs total count

| Pair                        | Count |
| --------------------------- | ----: |
| Aggressive + Financial      |     2 |
| Aggressive + Imperialist    |     2 |
| Aggressive + Organized      |     2 |
| Charismatic + Imperialist   |     2 |
| Charismatic + Protective    |     2 |
| Charismatic + Spiritual     |     2 |
| Creative + Financial        |     2 |
| Creative + Industrious      |     2 |
| Creative + Philosophical    |     2 |
| Financial + Imperialist     |     2 |
| Financial + Spiritual       |     2 |
| Imperialist + Organized     |     2 |
| Imperialist + Philosophical |     2 |
| Industrious + Spiritual     |     2 |
| Organized + Philosophical   |     2 |
| Organized + Protective      |     2 |
| Aggressive + Charismatic    |     1 |
| Aggressive + Creative       |     1 |
| Aggressive + Industrious    |     1 |
| Aggressive + Philosophical  |     1 |
| Aggressive + Protective     |     1 |
| Aggressive + Spiritual      |     1 |
| Charismatic + Financial     |     1 |
| Charismatic + Industrious   |     1 |
| Charismatic + Organized     |     1 |
| Charismatic + Philosophical |     1 |
| Creative + Protective       |     1 |
| Financial + Industrious     |     1 |
| Financial + Organized       |     1 |
| Financial + Protective      |     1 |
| Imperialist + Industrious   |     1 |
| Imperialist + Spiritual     |     1 |
| Industrious + Organized     |     1 |
| Industrious + Philosophical |     1 |
| Industrious + Protective    |     1 |
| Organized + Spiritual       |     1 |
| Philosophical + Protective  |     1 |
| Philosophical + Spiritual   |     1 |
| Protective + Spiritual      |     1 |
| Charismatic + Creative      |     0 |
| Creative + Imperialist      |     0 |
| Creative + Organized        |     0 |
| Creative + Spiritual        |     0 |
| Financial + Philosophical   |     0 |
| Imperialist + Protective    |     0 |

## Leaders' favourite civics rework

Based on the old base advciv 1.12 data (or current advciv-sas if missing such as for new leaders we added like as of now Ewuare or such if any), check if accurate.

Goal is to make it more historically accurate, balanced in gameplay, and more or less evenly spread (although less of a focus but an additional ideal extra). Also to to account for our reworked/replaced civics such as of now civic_wage_labor, civic_trade_bloc, civic_protectionism, etc.

### before changes favourite civics per leader

See below in the main table after changes as it includes the before values as well.

### before changes favourite civics count per civic

| Civic | Count as favourite |
| --- | --- |
| Hereditary Rule | 9 |
| Representation | 5 |
| Bureaucracy | 4 |
| Free Religion | 4 |
| Theocracy | 4 |
| Vassalage | 4 |
| Nationhood | 3 |
| Organized Religion | 3 |
| Police State | 3 |
| Universal Suffrage | 3 |
| Caste System | 2 |
| Free Market | 2 |
| Mercantilism | 2 |
| State Property | 2 |
| Emancipation | 1 |
| Environmentalism | 1 |
| Free Speech | 1 |
| Pacifism | 0 |
| Serfdom | 0 |
| Slavery | 0 |

| Civic | Count as favourite |
| --- | --- |
| Barbarism | 0 |
| Decentralization | 0 |
| Despotism | 0 |
| Paganism | 0 |
| Tribalism | 0 |

- sanity: total favourites across all civics = **53** (should match number of leaders)

### after changes favourite civics per leader

Done with the help of chatgpt 5.1, and other ais for check-up such as claude sonnet 4.5 and grok 4.1 and others, and my reviewing or such as well i mean. Check if accurate.

note: as of now advciv-sas civics are (check if updated in Sevopedia/xml) wage labor is medieval new, protecitonism is late classical new (replaces mercantilism), environmentalism is removed in favour of trade_bloc (medieval (1300s) at printing press in our mod), and civic_paganism has been renamed to civic_prehistoric_religion (although it's as of now the same civic, just to distinguish/differentiate it from the religion_paganism we as of now added in advciv-sas).

Also i added this info from chatgpt 5.1's thoughts as i found it very accurate and nicely phrased thanks: "I think favorite civics should relate to the core of a leader's regime-such as government, legal, or religious systems-not just practices like slavery, which were widespread. For example, Caesar, Hannibal, and Pericles all had slavery-so choosing "Slavery" for one wouldn't add accuracy. Similarly, serfdom or trade bloc membership should be linked more to their regime and identity, not the specific labor practices of their time.".

| Leader | Current Favourite Civic | Recommendation | Rationale |
| --- | --- | --- | --- |
| Alexander | Vassalage | **Keep** | Alexander's distinct pattern is: aristocratic companions who owe service for status/land, overlordship of allied Greek poleis and subject kings, use of a Persian-style layered hierarchy (satraps, sub-kings). In other words: a very militarised overlord + vassal network structure. Given that, I think Claude is right that our previous change doesn't really add clarity; it just makes him "generic monarch" instead of "overlord of vassals". I'd now revert Alexander back to Vassalage as favourite civic. That gives us one very clear "Vassalage leader" in the classical era (plus Ragnar etc.), and still leaves Hereditary Rule plenty represented elsewhere. `<!-- custom: note: based on claude sonnet 4.5's feedback -->` |
| Asoka | Free Religion | **Pacifism** | Post-Kalinga, Asoka is defined by renouncing conquest, promoting dhamma, and issuing moral edicts; a peace-focused religious civic captures his historical identity much better than a modern pluralist Free Religion. |
| Augustus | Representation | **Bureaucracy** | Augustus builds a durable imperial administration (provinces, census, tax, standing army) centered on Rome; Civ-style Bureaucracy is exactly "imperial capital + strong apparatus," which fits him far better than Representation. |
| Bismarck | Nationhood | **Keep** | His short, limited wars (1864, 1866, 1870-71) are national unification wars built on conscription and mass mobilization; "Nation in arms" plus post-1871 nation-state management fits Nationhood very well. |
| Boudica | Universal Suffrage | **Nationhood** | Historically she leads a revolt framed as defending "the people" and their land against Rome, rallying tribes into a war coalition; at Civ scale that is closer to a draft/war-mobilization civic than to late-game elections. We avoid Tribalism as a favourite because it's an empty civic in your mod. |
| Brennus | Organized Religion | **Vassalage** | I'd lean to changing Brennus to Vassalage - that gives him something more personal, and different from Boudica, without stretching what we actually know. For this Brennus (279 BCE, Thermopylae/Delphi one), the only clear thing in the sources is that he's a fearsome coalition war-leader. He commands a big multi-tribal force with subordinate chiefs and warbands - lots of personal loyalty and "follow this chieftain into Greece for plunder." We know far more about him as an overlord of warriors than as a religious organiser or nation-builder. So: Boudica = Nationhood -> "people's war / uprising of the Britons". Brennus = Vassalage -> "overlord with allied chiefs and retinues on campaign." That keeps them both Celtic and warlike, but with distinctly different regime "shapes". `<!-- custom: based on my past research, Brennus was fairly areligious, so after pointing/suggesting/asking chatgpt 5.1 this question/point, it told me organized religion works as a celtic society broad abstraction but not so typical of brennus himself who was not known for his piety or such if i understood it correctly. Since i want something more personalized to leaders ideally, changed it from the old organized religion then instead of keeping same trait. It then rereviewed the table again with this perspective/idea in mind and no other change needed for accuracy or such according to it, except for Cyrus (see his line for details) check if accurate thanks for help lot still chatgpt 5.1: -->` "Short answer: with the Brennus change, I don't see any other leader where the current favourite civic clearly misses their personal/regime identity in the way "Organized Religion -> Brennus" did.". |
| Catherine | Hereditary Rule | **Keep** | Whatever her Enlightenment correspondence, she is an autocratic empress whose legitimacy rests on dynastic monarchy and palace coups; Hereditary Rule is exactly that. |
| Charlemagne | Vassalage | **Keep** | Carolingian rule is the textbook example of counts, marcher lords, and benefices granted for service; Vassalage is one of the most accurate favourite civic matches in the entire roster. |
| Churchill | Nationhood | **Keep** | Churchill's moment is wartime Britain: mass conscription, propaganda, and appeals to "the nation" rather than technocratic administration or economics. Nationhood fits that role. |
| Cyrus | Vassalage | **Hereditary Rule** | Cyrus is a dynastic "King of Kings" ruling through satraps but anchored in royal lineage; in your civic set, simple Hereditary Rule is a closer abstraction than medieval-style Vassalage. `<!-- custom: following note at brennus: -->` "Right, so the "conflicted" feeling with Cyrus is basically: he looks like a Vassalage guy (King of Kings + satraps), but he is first and foremost a dynastic monarch. What Cyrus actually did (very condensed)" + "He overthrew the Median king, then conquered Lydia and Babylon, creating the Achaemenid Empire in the mid-6th c. BCE. To hold all that together, he used satraps - regional governors - to rule provinces on his behalf. The Achaemenid kings used the title "King of Kings" (shahanshah / basileus ton basileon), signalling that there were other kings beneath them - local dynasts and city-kings who stayed in place as subordinates. He's also famous (maybe a bit romantically) for relatively lenient policies toward conquered peoples - e.g. letting exiles return and respecting local cults (Cyrus Cylinder, Jewish return from Babylon, etc.). So structurally, that does smell a lot like Civ's Vassalage: a top ruler with subordinate rulers owing service." + "So the conflict is: Vassalage captures the shape of his empire. Hereditary Rule captures the core of his kingship and keeps Darius as the administrative/system guy. On balance, for your goals (personalised, regime-identity-focused, and avoiding too much overlap with Darius), Hereditary Rule wins by a nose. If someday you introduce a second Persian leader focused on the "network of subject kings" angle, that one would be a great place to use Vassalage as their favourite." |
| Darius | Free Religion | **Bureaucracy** | Darius is the system-builder: satrapies, royal roads, inspectors, standardized tribute. His key trait is administrative statecraft, not modern religious liberty; Bureaucracy fits that centralizing impulse. |
| De Gaulle | Nationhood | **Keep** | From the Free French to the Fifth Republic, his whole persona is "voice of the nation" and institutional refounder; a national-mobilization civic suits him well. |
| Elizabeth | Free Religion | **Free Market** | Her reign is the birth of English global commerce: chartered companies, privateering, Atlantic ventures. A trade-centric economic civic (Free Market) better captures the "Elizabethan sea-trade" identity than a modern secular religion policy. |
| Ewuare | Hereditary Rule | **Keep** | The Oba of Benin is a sacral, hereditary monarch whose power rests on lineage, court ritual, and palace institutions; that is straight Hereditary Rule in Civ terms. |
| Frederick | Universal Suffrage | **Bureaucracy** | Frederick the Great is the archetypal "enlightened despot" running a drill-state and efficient civil service; he is much more a bureaucratic monarch than any kind of democrat. |
| Gandhi | Universal Suffrage | **Pacifism** | Gandhi's historical persona centers on non-violent resistance, fasting, and moral pressure, not on holding office inside a voting system; a peace-oriented religious civic is a cleaner expression of his role. |
| Genghis Khan | Police State | **Keep** | Mongol rule under Genghis is total war, harsh law, and near-total social mobilization; Police State is a very accurate Civ-level abstraction. |
| Gilgamesh | Hereditary Rule | **Keep** | Bronze Age Uruk is a city-state under a semi-divine king; a basic hereditary monarchy fits that legendary setting well enough. |
| Hammurabi | Bureaucracy | **Keep** | He is literally the go-to example for codified law and early centralized administration; Bureaucracy is exactly what his Civ design is already gesturing at. |
| Hannibal | Free Market | **Keep** | If you keep the current meaning of "Trade Bloc" (intergovernmental economic union), I still think Hannibal -> Free Market is more accurate than Hannibal -> Trade Bloc. Why I'd still lean Hannibal = Free Market" + "Given your own rule: favourite civic = the thing that best captures the leader's regime identity or vibe, not "we need to showcase this civic" then for Hannibal: Core Hannibal / Carthage vibe: Maritime merchant city-empire" + "Money + ports + trade routes fund mercenary armies" + "Carthage as a rich commercial power clashing with a land empire (Rome)" + "Conceptually that is much closer to: Free Market -> "commerce-driven society where markets and trade dominate the economy" than to: Trade Bloc -> "formal intergovernmental agreement / customs union between multiple states"" + "Your Trade Bloc pedia text (screenshot) is very explicitly about: USMCA, EU-style blocs, 19-20th century economic integration, regional organisations, etc. Carthage's system is an imperial maritime network, not an institutional trade bloc among equal partners. So if we stay literal about the concept as written, Hannibal's "dream civic" is still Free Market." + "Given everything you've told me about accuracy > symmetry, my honest recommendation is still: Hannibal -> Free Market, zero Trade Bloc favourites is OK." |
| Hatshepsut | Organized Religion | **Keep** | Her major beats are Punt expeditions, temple building, and religious legitimation of her rule; a "temples help build things" civic matches that temple-economy flavor well. |
| Huayna Capac | Hereditary Rule | **State Property** | The Inca economy is state-planned: no private land, labor tax (mit'a), state storehouses and roads. A command-economy civic like State Property maps far better to that than a generic monarchy favourite. |
| Isabella | Theocracy | **Keep** | Reconquista, Inquisition, and militant Catholic policy: she is almost the archetype for a Theocracy in Civ terms. |
| Joao | Hereditary Rule | **Free Market** | Portuguese expansion under Joao leans into Atlantic trade, colonies, and commercial charters; a pro-commerce economic civic is a better summary than another monarchy tag. |
| Julius Caesar | Representation | **Police State** | In practice Caesar's regime is a personal dictatorship backed by loyal legions and proscriptions; a hardline Police State matches that concentration of power better than a representative-government civic. |
| Justinian | Theocracy | **Keep** | He rules an explicitly Christian empire, sponsors councils, enforces orthodoxy, and fuses imperial and religious authority; Theocracy is on-point here. |
| Kublai Khan | Bureaucracy | **Keep** | As Yuan emperor he leans heavily on Chinese imperial bureaucracy and civil officials; Bureaucracy is exactly the flavor you want to highlight for him. |
| Lincoln | Emancipation | **Nationhood** | Lincoln's presidency is the archetype of "save the Union" via mass mobilization: conscription, war bonds, and appeals to the nation; a draft/propaganda civic expresses that better than a labor-law civic. |
| Louis XIV | Hereditary Rule | **Keep** | "L'etat, c'est moi" is pure absolutist monarchy; Hereditary Rule is the clean and accurate match. |
| Mansa Musa | Free Market | **Keep** | His fame comes from gold, caravans, and trade routes linking West Africa to the wider Islamic world; a trade-oriented economic civic suits him perfectly. Mansa Musa - Free Market vs Trade Bloc: I agree with your current choice: Free Market. His story is gold + caravans + pilgrimage and wealth, not designing a customs union. |
| Mao Zedong | State Property | **Keep** | Mao leads a communist revolution and then rules a centrally planned economy with collectivization and five-year plans; State Property is exactly the canonical choice. |
| Mehmed | Vassalage | **Hereditary Rule** | Mehmed II is a dynastic Ottoman sultan; while he does rely on timar grants and provincial notables, the core structure is an hereditary sultanate, which fits Hereditary Rule better than medieval Vassalage. |
| Moctezuma | Police State | **Theocracy** | The Aztec state fuses ruler and priesthood, with ritual war and sacrifice as religious duty; a state-religion fusion civic better captures that sacral militarism than a generic police regime. |
| Napoleon | Representation | **Nationhood** | Napoleon is the poster child for levee en masse and national armies fighting for "la nation"; Nationhood captures the mass-mobilization aspect of Napoleonic France more clearly than any formal representative system. |
| Pacal | Hereditary Rule | **Caste System** | Classic Maya society is strongly stratified with nobles, priests, and commoners in fixed roles; a labor/social-stratification civic like Caste System is a closer abstraction than a generic monarchy favourite. |
| Pericles | Representation | **Keep** | Periclean Athens stands in for democracy in Civ: assembly, juries, pay for civic service; using Representation for that is standard and thematically right. |
| Peter | Bureaucracy | **Keep** | Peter the Great is all about building a Western-style, centrally administered state (Table of Ranks, new capital, modernized army); Bureaucracy is a perfect description. |
| Qin Shi Huang | Bureaucracy | **Police State** | Qin unification is remembered for harsh Legalist law, forced labor, book burnings, and secret police; in your civic set that's closer to a hard Police State than to neutral "capital gets extra commerce." |
| Ragnar | Hereditary Rule | **Vassalage** | Viking warbands and jarls revolve around personal loyalty and service to a war-leader; Civ's Vassalage (lords owing military service) is a good abstraction for that retinue-based society. |
| Ramesses | Organized Religion | **Keep** | Ramesses II is temple and monument king, backed by priestly legitimation; staying with Organized Religion keeps the "temple economy builds big things" vibe intact. |
| Roosevelt | Mercantilism | **Universal Suffrage** | FDR governs within a mature electoral democracy, re-elected multiple times and using the state to intervene in the economy; a modern democratic government civic fits his role better than a narrow trade-policy one. |
| Saladin | Theocracy | **Keep** | He's remembered as the pious unifier leading jihad and defending Jerusalem; a tight fusion of state and religion is exactly what Theocracy represents. |
| Shaka | Police State | **Keep** | Shaka's Zulu state is a hyper-militarized regimental society with intense discipline and coercion; Police State is a very accurate Civ-scale summary. |
| Sitting Bull | Environmentalism | **Nationhood** | In Civ terms he stands for defending his people's land and sovereignty against an expanding state; a "defend the nation/people" civic matches that resistance role better than a late-game environmental/trade-bloc civic. |
| Stalin | State Property | **Keep** | Stalin's USSR is the classic example of full state ownership and command planning; State Property is the obvious and accurate favourite. |
| Suleiman | Hereditary Rule | **Bureaucracy** | Suleiman "the Lawgiver" is as much about kanun (imperial law) and administrative order as conquest; highlighting a capital-centered admin civic better reflects that than another generic monarchy favourite. |
| Suryavarman | Caste System | **Keep** | Angkor-era Khmer society is highly hierarchical with temple elites and organized labor; Caste System is a good abstraction for that social order. |
| Tokugawa | Mercantilism | **Protectionism** | The Tokugawa shogunate's sakoku policy (closed borders, tightly controlled trade) is basically a protectionist, restricted-trade order; your Protectionism civic maps to that very cleanly and replaces Mercantilism in the mod. |
| Victoria | Representation | **Free Market** | Victorian Britain is the textbook 19th-century industrial capitalist and free-trade power (post-Corn Laws etc.); a pro-market economic civic captures that better than tweaking the government form. |
| Wang Kon | Caste System | **Organized Religion** | As founder of Goryeo he strongly supports Buddhism and religious institutions as pillars of the state; a temple-driven Organized Religion civic fits his Spiritual/Organized flavor better than labor structure alone. |
| Washington | Free Speech | **Representation** | Washington presides over the founding of a representative republic and then voluntarily steps down; a government civic representing representative institutions is the cleanest expression of his role. |
| Willem van Oranje | Free Religion | **Keep** | He's famous for religious tolerance and coalition politics in the Dutch Revolt; a pluralist Free Religion civic is exactly his slot. |
| Zara Yaqob | Theocracy | **Keep** | Zara Yaqob is known for enforcing strict Christian orthodoxy and writing doctrinal works; a strong state-church fusion civic is the right summary. |

- sanity: leaders listed in this table = **53** (one favourite civic per leader)

### after changes favourite civics count per civic

| Civic | Count as favourite |
| --- | --- |
| Bureaucracy | 7 |
| Nationhood | 7 |
| Hereditary Rule | 6 |
| Free Market | 5 |
| Theocracy | 5 |
| Police State | 4 |
| Vassalage | 4 |
| Organized Religion | 3 |
| State Property | 3 |
| Caste System | 2 |
| Pacifism | 2 |
| Representation | 2 |
| Free Religion | 1 |
| Protectionism | 1 |
| Universal Suffrage | 1 |
| Free Speech | 0 |
| Serfdom | 0 |
| Slavery | 0 |
| Trade Bloc | 0 |
| Wage Labor | 0 |

| Civic | Count as favourite |
| --- | --- |
| Barbarism | 0 |
| Decentralization | 0 |
| Despotism | 0 |
| Prehistoric Religion | 0 |
| Tribalism | 0 |

Sanity: total favourites across all civics = 53 (one per leader, matches leader count).

## Leaders' Favourite religions rework

This is the oldest rework i made and which i had made without AI if i remember it correctly at least at that time, unlike how i did it later as of now for the other reworks in this doc.

Since its structure and way of doing it was quite differently done (not using chatgpt or such to web search info but digging myself if i remember it correctly) (note: chatgpt 5.1 helped me a bit to find some typoes or such here and then as of now to format and summarize the already existing data into a table or such), adding them here in the doc after these other reworks.

### notes_about_religious_design

#### Brennus

According to this document [https://boutique.tropismes.com/bonus/extrait/9782812148347](https://boutique.tropismes.com/bonus/extrait/9782812148347), page 29, Gaul leaders/chiefs (maybe that includes brennus of the Gaul too?) did not exert a strong religious pressure on their people as they were driven by freedom if i understand it correctly.

If this accurate and reliable, i may want/have/need to change brennus's xml to focus less on religion and more on civis, perhaps even boudica's but there may be more data on her since she is more recent, and i didn't look yet (at least not in detail, only that she was seemingly more religious at least than what i know now of brenus if this doc is accurate, but it was quick glance too on boudica anyways so may look later or maybe not though.), so may apply this to brennus only or other similar leaders or not.

Note: in advciv-sas as of now confucianism has been removed and replaced with paganism religion.

#### Churchill

From a quick search not detailed, churchill didn't seem to have a strong preference for it or any religion, so is none now, allows also to declutter christianity that was bloated.

#### Cyrus

cyrus seems to not be strongly religious and quite open too in/from [https://en.wikipedia.org/wiki/Cyrus_the_Great#Religion_and_philosophy](https://en.wikipedia.org/wiki/Cyrus_the_Great#Religion_and_philosophy).

#### Darius

it seems darius is a bit more religious though (at least than cyrus), in these sources:

- [http://www.teheran.ir/spip.php?article2533#gsc.tab=0](http://www.teheran.ir/spip.php?article2533#gsc.tab=0)
- [https://en.wikipedia.org/wiki/Religion_in_the_Achaemenid_Empire](https://en.wikipedia.org/wiki/Religion_in_the_Achaemenid_Empire)

#### Ewuare

as for Ewuare (kingdom of benin), christianity seems to be an important part of the kingdom, but the beninese also have their own kind of or own religion with human sacrifices ([https://en.wikipedia.org/wiki/Kingdom_of_Benin#Human_sacrifice](https://en.wikipedia.org/wiki/Kingdom_of_Benin#Human_sacrifice)) or such, plus their benin bronzes and such; makes me more lean towards the fact that (THEY) they were more pagans, so going with that instead.

#### Frederick

frederick seems to be agnostic (quite strongly xd from the very little read i had here (in french) which is quite funny, the ironic pleasantry/plaisanterie in his letter): [https://fr.wikipedia.org/wiki/Fr%C3%A9d%C3%A9ric_II_(roi_de_Prusse)](https://fr.wikipedia.org/wiki/Fr%C3%A9d%C3%A9ric_II_(roi_de_Prusse)); but i read little about it and this page seems enough to say he is agnostic indeed maybe, but seems a bit enough.

update: since i can't find what this refers to at a quick glance, i now asked chatgpt 5.1 about it still no luck xd. My best guess is in one of his correspondances with someone else he noted how something is ironic or paradoxical, this is how i remember it but nothing specific, maybe i should have written it or maybe not since i didn't. At least i tried xd maybe i mean.

#### Genghis Khan

genghis khan seems to have been tengrist something, but according to a quick search, it seems he had great respect for daoism: [https://fr.wikipedia.org/wiki/Religion_en_Mongolie#Tao%C3%AFsme](https://fr.wikipedia.org/wiki/Religion_en_Mongolie#Tao%C3%AFsme)

>Bien que Gengis Khan ait ete avant tout tengriste, il manifesta un grand respect a l'egard du dirigeant de la secte taoiste Quanzhen, Qiu Chuji, lorsque celui-ci lui rendit visite dans l'Hindou Kouch, a Kaboul, en 1222, a son invitation, et predit la conquete de la Chine par les Mongols. En retour, Gengis Khan lui donna d'importants pouvoirs politiques et religieux. Il fut exempte de taxes, et depuis Pekin, sa secte fut la plus favorisee de l'Empire Mongol. Il defendit la liberte d'autogestion des autres sectes, aupres du khagan, qu'il s'agisse des taoistes, des bouddhistes, des chretiens nestoriens ou des musulmans[18].

therefore, it is not incorrect to say, among civ4 advciv-sas's religions in particular, hat his favourite religion, if he had to choose one, is not none but maybe rather indeed daoism, is also quie convenient even though was not main goal that this is not filled., one leader can have a favourite religion even though not having said religion themselves; this is perhaps an important distinction i should add in changelogs and added now.

#### Lincoln

as for lincoln, according to sources i read, lincoln was not christian, not strongly enough at all at least, here are a few sources i read:

- [https://en.wikipedia.org/wiki/Religious_views_of_Abraham_Lincoln#:~:text=Although%20Lincoln%20never%20made%20an,Christ%20in%20the%20religious%20sense](https://en.wikipedia.org/wiki/Religious_views_of_Abraham_Lincoln#:~:text=Although%20Lincoln%20never%20made%20an,Christ%20in%20the%20religious%20sense)
- [https://apps.legislature.ky.gov/LegislativeMoments/moments09RS/web/Lincoln%20moments%206.pdf](https://apps.legislature.ky.gov/LegislativeMoments/moments09RS/web/Lincoln%20moments%206.pdf)
- [https://www.thegospelcoalition.org/blogs/justin-taylor/was-abraham-lincoln-a-christian/](https://www.thegospelcoalition.org/blogs/justin-taylor/was-abraham-lincoln-a-christian/)
- [https://www.reddit.com/r/todayilearned/comments/llardq/til_that_abraham_lincolns_religious_views_are/](https://www.reddit.com/r/todayilearned/comments/llardq/til_that_abraham_lincolns_religious_views_are/)

i did not look at them in (long) detail, but i think in detail enough hopefully. that i can assert quite faithfully/strongly but anyways maybe that he was definitely leaning more agnostic than christian, reddit comments also lean in that direction, was not christian even though had a strong christian education. Lincoln seems more agnostic or not strongly favouring a religion, so for civ4 i changed it to none rather than christianity, he seems to be a free person rather which i like i mean. (But also even if he were not such free man and really christian, he is free to do so to (else it would defeat the purpose xd i mean.)).

#### Pericles

pericles prefers religion according to [https://ehne.fr/fr/eduscol/pericles-est-il-vraiment-le-grand-homme-de-la-democratie-athenienne#:~:text=Enfin%2C%20P%C3%A9ricl%C3%A8s%20s'est%20appuy%C3%A9,ont%20beaucoup%20fait%20pour%20la](https://ehne.fr/fr/eduscol/pericles-est-il-vraiment-le-grand-homme-de-la-democratie-athenienne#:~:text=Enfin%2C%20P%C3%A9ricl%C3%A8s%20s'est%20appuy%C3%A9,ont%20beaucoup%20fait%20pour%20la) so going with religion paganism hopefully accurate enough.

#### Wang Kon

for wang kon, according to civ4 wiki (in [https://civilization.fandom.com/wiki/Wang_Kon_(Civ4)](https://civilization.fandom.com/wiki/Wang_Kon_(Civ4))):

>During his reign Wang Kon promoted Buddhism as the state religion, and oversaw the conquest of northern Korea and parts of Manchuria. When dealing with local clans,

he promoted buddhism as the state religion; i don't know why his preferred religion was confucianism, but since there is no confucianism anymore now in advciv-sas, he leans closer (i think) to buddhism based on this maybe. than say paganism or none religion (favourite), is convenient to increase buddhism leader count that is really low and not increase paganism leader count that is high enough (a bit too high but historically fine and matching christinaity so maybe fine too); Hopefully fine enough and accurate enough even though not exhaustive.

### Other leaders

Not documented in my old notes (sometimes as of now directly in XML code comments near `<FavoriteReligion>` it seems (but check to be sure)), but many leaders have also been changed, mostly if not only to paganism.

### Summary of the favourite religion leaders' changes in advciv-sas

A summary of my previous notes with the help of chatgpt 5.1 (check if accurate), showing base advciv's (except for some leader(s) like Ewuare since they didn't exist in base advciv) favourite religion vs advciv-sas.

| Leader | Base | New | Rationale |
| --- | --- | --- | --- |
| Alexander | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Asoka | Buddhism | Keep | |
| Augustus | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Bismarck | Christianity | Keep | |
| Boudica | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Brennus | None | Keep | Already had no favourite religion; the Brennus note mainly informed other XML tweaks (less religious emphasis, more civics focus), not a favourite religion change. |
| Catherine | Christianity | Keep | |
| Charlemagne | Christianity | Keep | |
| Churchill | Christianity | **None** | Biographical sketches don't show a strong personal attachment to any one faith; dropping his Christian favourite both matches that and helps reduce Christianity's over-representation in the roster. |
| Cyrus | None | Keep | After a quick read of his religious views, Cyrus looks relatively open and not strongly attached to a single faith, so leaving his favourite religion as None still fits. |
| Darius | None | **Paganism** | Darius appears more overtly religious than Cyrus in the sources; giving him a specific favourite religion in-game (Paganism as generic Achaemenid state cult) reflects that. |
| De Gaulle | Christianity | Keep | |
| Elizabeth | Christianity | Keep | |
| Ewuare | | **Paganism** | New leader in AdvCiv-SAS; for the Kingdom of Benin, Christianity appears late and local religion (including human sacrifice and royal ritual) is central, so Ewuare uses Paganism as favourite religion. |
| Frederick | Christianity | **None** | French and other sources often describe Frederick II as deist/agnostic; his favourite religion is changed from Christianity to None to reflect that more sceptical stance. |
| Gandhi | Hinduism | Keep | |
| Genghis Khan | None | **Daoism** | Historically tengrist but showed particular respect for the Quanzhen Daoist master Qiu Chuji; among your available religions, Daoism is the closest fit, and it usefully fills what was previously an empty favourite-religion slot for him. |
| Gilgamesh | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Grace O'Malley | | **None** | New leader in AdvCiv-SAS; no favourite religion in current XML. |
| Hammurabi | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Hannibal | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Hatshepsut | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Huayna Capac | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Isabella | Christianity | Keep | |
| Joao | Christianity | Keep | |
| Julius Caesar | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Justinian | Christianity | Keep | |
| Kublai Khan | Buddhism | Keep | |
| Lincoln | Christianity | **None** | Sources generally paint Lincoln as religiously complex / sceptical rather than a clear Christian partisan; treating him as effectively agnostic and removing his Christian favourite keeps him more neutral. |
| Louis XIV | Christianity | Keep | |
| Mansa Musa | Islam | Keep | |
| Mao Zedong | None | Keep | |
| Mehmed | Islam | Keep | |
| Michael Collins | | **Christianity** | New leader in AdvCiv-SAS; Christianity in current XML. |
| Moctezuma | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Napoleon | Christianity | Keep | |
| Pacal | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Pericles | None | **Paganism** | Pericles leans heavily on civic religion, festivals and public cult; giving him Paganism as a favourite ties him to the generic "classical city cults" bucket instead of leaving him without any religious preference. |
| Peter | Christianity | Keep | |
| Qin Shi Huang | Taoism | **Daoism** | Taoism was renamed Daoism in AdvCiv-SAS. |
| Ragnar | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Ramesses | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Roosevelt | Christianity | Keep | |
| Saladin | Islam | Keep | |
| Shaka | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Sitting Bull | None | **Paganism** | Not documented in [notes_about_religious_design](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#notes_about_religious_design). |
| Stalin | None | Keep | |
| Suleiman | Islam | Keep | |
| Suryavarman | Hinduism | Keep | |
| Tokugawa | Buddhism | Keep | |
| Victoria | Christianity | Keep | |
| Wang Kon | Confucianism | **Buddhism** | As founder of Goryeo he promoted Buddhism as state religion; with Confucianism removed from AdvCiv-SAS, switching his favourite to Buddhism keeps him anchored to an organised religion that matches the history better than Paganism or None. |
| Washington | Christianity | Keep | |
| Willem van Oranje | Christianity | Keep | |
| Zara Yaqob | Christianity | Keep | |

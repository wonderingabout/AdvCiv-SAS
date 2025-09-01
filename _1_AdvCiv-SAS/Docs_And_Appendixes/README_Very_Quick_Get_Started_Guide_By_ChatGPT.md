# Very Quick Get Started Guide

This guide highlights key differences between AdvCiv-SAS and AdvCiv/Civ4 BTS. It’s intentionally practical and a bit verbose so newer players can follow the “what changed” and “why it matters.” For technical details, see the main [README](/README.md) and the docs under [/_1_AdvCiv-SAS/](/_1_AdvCiv-SAS/).

## Sevopedia

Some changes are also summarized directly in the Sevopedia. See [README: Sevopedia reworks](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md). Sample screenshots are provided there.

- New/updated Sevopedia content (e.g., the AI personality panel with raw attributes and cross-leader comparisons) aims to make leader behavior easier to understand. See the section above for images and details.

## Handicap info tables (.csv / .md) and script

To help compare difficulty (“handicap”) settings, tables are generated as CSV/MD. See README: Handicap tables for examples and the script that produces them.

## Full code diff (very long)

For the exhaustive diff between AdvCiv stable (e.g., 1.12) and AdvCiv-SAS, see the compare PR. It’s big; the guide below is the digest.

## Main Changes — quick starter guide

### Translations

- New or changed content in AdvCiv-SAS ships with English text only. If your game language isn’t English, those entries will still appear (in English). Implementation notes are documented at `TXT_KEY_ADVCIV_SAS_CORE_CHANGES_PEDIA_SR` in the XML comments.

### Renaming (non-exhaustive)

- “WFYABTA” → “We fear you are trading more than us.” Same mechanic; the new text reflects that it’s about trading volume, not tech pace.
- Nuclear interception text clarifies that displayed chance is **adjusted** by nuke evasion; see the forum thread for context ([civfanatics](https://forums.civfanatics.com/threads/sdi-icbm-and-tactical-nukes.239415/)).
- “Civilopedia” → “Sevopedia.”
- “Ressource(s)” → “Bonus(es).”
- Bonus names standardized: Ivory → Elephants; Cow → Cattle; Clam → Molluscs; Wine → Grapes, etc.
- Terrain/Feature: Ice (Terrain) → Ice Sheet; Ice (Feature) → Ice Cap.
- “Great wonders” → “World wonders” (functionally the same).
- Leader names corrected where needed (e.g., Montezuma → Moctezuma II).
- Taoism → Daoism (with matching building/unit names and encyclopedia text).
- “Unique units” → “Civilization units” (they aren’t singletons; they’re civ-specific).
- Promotion names made more explicit (e.g., Counter-Archer, Counter-Siege, City Bombard Damage). Roman numerals → Arabic (“Combat 3”).

### Sevopedia reworks & related UI

- Wider content area, narrower main category column; fills available screen space.
- Many entries (religions, some techs/buildings/units/bonuses/terrains/features) now use neutral encyclopedia-style blurbs (often Wikipedia-based) for clarity/context. See [README: Sevopedia reworks](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Sevopedia_Reworks.md).

### Concepts (currently under “Outdated” category)

- Added informational entries like `concept_rivers`, `concept_route_road`, `concept_route_railroad`. These aren’t kept fully in sync with SAS rules; they’re there as general Civ4 references and for UI reuse. See [README: Concepts](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Concepts.md).

### AI — General behaviour (non-exhaustive; see XML/defines for full detail)

#### General changes (AI)

- Global AI settings lean toward pragmatic, opportunistic play over role-play: religion weight adjustments, lower revolt chance, lower war anger, more willingness to demand tribute and sometimes declare if refused, less inclination to take bad wars (especially multi-front). For specifics, see `Assets/XML/AI_Variables_GlobalDefines.xml`, `AI_Variables_GlobalDefines.xml`, and `BBAI_Game_Options_GlobalDefines.xml` for the exact values you changed.

#### Units in general (AI)

- **Scrapping & UnitAI production quotas (generalized)**: Reworked scrapping across (almost) all `UnitAI` types to stop destroy→rebuild loops. Paired with per-`UnitAI` **max/quotas** in `CvCityAI::AI_chooseUnit` and scrapping guards in `CvUnit::canScrap`. Policy examples: during **war/danger**, suppress explorers/settlers and redirect output to land units; on **naval-heavy** maps (archipelago) allow higher naval quotas, **land-heavy** maps (pangaea/continents) lower; in war/danger, naval production quotas drop (sometimes to **0**) but **existing** ships aren’t auto-scrapped; **workers** use a **decaying max** so late-game excess can be scrapped conservatively. Fixes the “naval dementia” case (mass privateers/galleons while land cities fall). See [KI#53](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#53---beyond-tremendously-improved-naval-dementia-of-producing-privateersgalleons-then-seemingly-scrapping-them-and-repeat-orand-of-more-importantly-building-galleons-and-privateers-in-droves-and-excess-if-i-may-say-but-anyways-etc-despite-enemy-threatening-cities-of-land-capture-for-20-turns-and-losing-capital-as-a-result-anyways-etc-fixedaddressed-by-now-managing-production-of-each-unitai-with-max-by-type-in-cvcityaiai_chooseunit-as-well-as-disallowing-scrapping-and-managing-it-by-unitai-type-globally-as-well-in-cvunitcanscrap-by-type-as-well-with-max-and-such-other-conditions-for-some-units-like-as-of-now-workers-anyways-etc) (complements [KI#52](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#52---beyond-tremendously-improved-anyways-etc-remove-ai-scrapping-of-military-land-units-as-way-too-many-units-are-scrapped-early-yet-we-really-need-them-to-defend-against-barbarians-or-our-rivals-or-such-anyways-etc)).

#### Settlers (AI)

- Avoid settling on bonuses (especially food/metal/high-production/commerce) unless the immediate overall site value clearly justifies it. See [KI#25](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#25---seemingly-fixed-ais-settling-too-much-and-too-often-on-bonuses-especially-food-bonuses--and-metals-and-other-high-production-bonuses-or-also-commerce-bonuses-to-a-lesser-extent).
- **Respect water bonuses:** if a coast bonus would be in BFC but the site is non-coastal, apply a stronger penalty so we don’t “count” unusable sea resources. Penalty moved from **-165 → -400** (K-Mod used ~-800). See [code ref](/CvGameCoreDLL/CitySiteEvaluator.cpp).
- **Low-food environments** (tundra/plains/desert/snow/peak counted for safety): even without water bonuses, **prefer coastal sites** so the city can actually grow instead of being stuck at very low pop. See [KI#32](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#32---now-seemingly-fixed-prioritize-settling-on-coast-when-food-environment-is-low-many-tundra-orand-plains-orand-desert-orand-snow-orand-peak-although-i-assume-is-not-counted-but-to-be-safe-anyways-etc-the-corinth-screenshot).
- **Environment heuristics (non-bonus tiles):** favor sites with lots of grassland/flood plains; penalize plains/desert BFCs. For the tile you settle on, prefer hill-plains/tundra/desert; avoid settling on hill-grass/flood plains unless doing so unlocks a clearly superior multi-bonus BFC. See [KI#26](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#26---seemingly-fixed-for-the-plot-of-the-settled-city-only-in-general-the-ai-should-aim-to-settle-on-a-hill-and-avoid-settling-on-flatland-grassland-or-flood-plains-where-possible-or-during-the-first-city---city-1-when-there-is-no-good-site-yet-to-take).
- **Health tolerance:** don’t reject good jungle sites just for early unhealth. Allow a threshold (more strict for capital, looser later), and consider forest health offsets and flood plains exceptions. Jungle can be chopped later; value the site’s potential, not just immediate health. (Threshold examples: ~≤350 “healthpercent” for capitals; ~≤450 for later cities.)
- **Spacing:** remove old long-distance penalties that forced tight clusters. Cities are evaluated by distance to the nearest city (not the capital), with penalties only for “too close” or “way too far,” strongest early and fading as the empire grows.
- **Settler evaluation — midgame desert/bonus bias fix**: Disabled the buggy `AIFoundValue::adjustToCivSurroundings` that, from about **turn 51+**, made settlers overvalue founding **on desert bonus tiles** (e.g., **Camel**) or **inside** desert belts. Replaced it with a very small inline pass in its only caller, `AIFoundValue::evaluate`. Observed effect: no longer plants directly on Camel/desert; instead settles **around** large deserts. **Since the spacing change above**, also tightened distance-to-civs and culture-pressure checks to **hard-reject** sites that are **too far** or **heavily pressed** (instead of just penalizing). See [KI#54](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#54---fixed-major-base-advciv---civ4-in-aifoundvalueadjusttocivsurroundings-causing-ai-settlers-to-value-midgame-turn-50-for-example-here-anways-etc-settling-on-camel-desert-worked-around-and-disabled-this-function-entirely-now-inline-a-very-simplified-version-of-it-inline-in-its-only-caller).
- **Defense/barbarian surroundings:** drop special “avoid barbarians” or “weaker barb cities” site adjustments; choose the best yield sites regardless.
- **Who builds settlers:** only the **capital** can build settlers, and only at **pop ≥ 5** (unless a city is stuck at low growth, in which case building one can be allowed). This leverages food→hammer conversion efficiently and reduces early barbarian losses from small frontier cities producing settlers.
- **Free window:** during the first ~75 turns at Normal speed (scaled by game speed), a “free to produce settler” period lets the capital grow before switching into chosen early strategy (offense, defense, etc.).
- **First city logic:** settlers consider a larger no-penalty scouting radius for founding the capital (`CvUnitAI::AI_foundFirstCity`), and no longer auto-reject non-coastal/non-river sites if a worse “preferred” site exists. It’ll just pick the **best** overall site. See [KI#43](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#43---attemptingly-improvedenhanced-ai-settlers-for-the-first-city-found...).
- **Avoid excessively watery capitals:** if fewer than **12** “good starter BFC tiles” (land + coastal bonus tiles, excluding the city tile), apply a strong penalty so the capital doesn’t start surrounded by mostly low-yield coast. Other cities may still take such sites later. See [KI#44](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#44---enhanced-makeencourage-ai-settlers-walk-away-from-bad-starting-sites...).
- **Additional tweaks:** value fresh water more (logic refactored/merged), value settling on **hill-plains** much more, and disable legacy “anti-crowd” biases so the choice stays yield-driven.

#### Workers (AI)

- Strongly discourage building **forts on bonuses** (very poor early yield/time trade). See [KI#24](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#24---attemptingly-fixed-ai-workers-often-build-forts-on-ressourcesbonuses...).
- Always improve **bonuses first**, prioritizing **food** bonuses. Major refactor of `CvUnitAI::AI_bestCityBuild` to use a probabilistic value tree tuned for SAS. See [KI#30](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#30---attemptingly-fixed-ai-workers-not-prioritizing-bonuses...).
- One worker per improvement **cap** to avoid over-stacking on slow tiles and reduce capture risk.
- Greatly simplified `AI_betterPlotBuild`: hard **de-prioritization of roads/routes** early; build them only when they’re truly the best move. Focus is on **yields first**. See [KI#31](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#31---attemptingly-fixed-deprioritize-routes-for-ai-workers...).
- **Overhaul: `AI_bestCityBuild` (full routine):** “holy” improvements (never overwrite: **hamlet, village, town, workshop**) and “semi-holy” (contextual: **farms** in food-poor cities, **cottages** in food-rich cities); fast/ordered improvement; **bonus-specific rules** (e.g., don’t cottage bananas; prefer plantation or a farm only if it makes clear sense); **terrain-aware cottage/farm logic** (flood plains favored for cottages unless the city is food-poor); **minimal oscillation**; prefer steady growth; avoid overwriting until other workable tiles are improved; hold top tiles for later if the “now” move would be inferior. See [KI#33](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#33---tremendously-improved-and-fixed-and-enhanced-ai-worker-buildimprovement-logic-in-cvunitaiai_bestcitybuild).
- **Mobility:** workers leave “over-improved” cities sooner to help weaker ones; later pass further improves cross-city mobility and bravery within borders (less idle parking). See [KI#39](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#39---seemingly-fixed-orand-enhanced-make-ai-workers-move-sooner-to-city-b...) and [KI#41](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#41---seemingly-fixed-beyond-tremendously-improved-ai-worker-mobility...).
- **Retreat logic:** fix excessive retreat → “parking in city” edge cases with a wake-from-retreat and saner thresholds. See [KI#50](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#50---tremendously-improvedfixedenhanced-excessive-ai-worker-retreat-logic...).

#### City Plots (AI)

- Fix K-Mod allocation pathologies: starving/stagnant cities no longer choose **+1 hammer** over **+4 food** unworked plots; also value food correctly when **food is production** (settlers/workers). See [KI#34](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#34---seemingly-fixedtweaked-major-k-mod-suboptimal-food-plot-ai-city-allocation...).
- If happiness room is **high**, push growth harder: favor food tiles more, deemphasize hammers (unless **food is currently production**). See [KI#40](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#40---seemingly-fixed--addressed-tremendousmajor-plot-allocation-improvement-2...).

#### Specialists (AI)

- Never pick **Citizen** specialist (very inefficient). Implemented in `CvCityAI::AI_jobChangeValue`.
- Add **sanity guards**: in small cities (and larger ones with headroom), don’t run specialists at all until growth caps are reached (with food/happiness checks). **Barbarian** cities, on top of these rules, may only run **Scientist** specialists when they must run any. See [KI#45](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#45---addressed--patched--worked-around-ai-cities-assigning-too-soon-orand-too-often...).

#### City Production (AI)

- - **“No production” stall — worked around / fixed**: AI cities no longer sit on **no production**. Added a robust fallback: produce the **most expensive suitable land combat unit**; if a candidate is **extremely overpriced for the era**, switch to the **cheapest suitable** instead. **Civilians** (e.g., scouts) are excluded. This prevents idle turns (e.g., will build an archer in the Ancient era) and cuts wasted hammers. See [KI#51](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#51---worked-around--fixed-massive-seemingly-base-advciv---civ4-issue-if-im-not-mistaken-of-many-cities-entering-no-production-early-for-1-or-several-turns-many-times-during-the-game-early-and-possibly-later-this-is-why-many-cities-have-a-process-rather-than-no-production-as-processes-are-not-available-early-and-are-listed-among-fallbacks-if-production-fails-it-seems-but-check-to-be-sure-anyways-etc). Related: handicap settings were **slightly reduced** to keep difficulty even with the new efficiency.

#### Leaders (AI)

- Adjusted `iBuildUnitProb` for a number of leaders (some up, some down) and also **+10** globally so AIs field more units (they died too often to barbarians, especially with stronger barbarians). See XML for exact numbers.
- Corrected favorite religions where historical support was weak or inaccurate; scope limited to “favorite religion” for now (see your notes file for sources).

#### Buildings (AI)

- Tightened/reworked **wonder-keep** thresholds in `CvCityAI::AI_chooseProduction`: if at war/planning war/in danger and not close to completion, AIs will **ditch world wonders** (highest threshold when weaker) and redirect hammers to urgent needs (e.g., walls/units). See **[KI#48](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#48---enhancedreworked-ai-building-walls-when-they-are-stronger-and-dont-need-it-or-wonders-when-they-are-weaker-or-in-danger-dont-build-wonders-for-our-neighbours-when-they-capture-us-and-overall-added-a-lot-of-extra-buildingvalue-reject-orand-always-build-first-logic-depending-on-building-type-andor-such-anyways-etc--and-reworked-as-well-the-ditching-wonders-logic-to-be-seemingly-stricter-and-more-wardanger-focused-anyways-etc)**.
- Added **pre-filtering** rules in `CvCityAI::AI_buildingValue` so hammers go where they matter: skip walls when safe/strong; avoid wonders when weak/in danger (focus on core cities if relevant); keep early culture to BFC needs; do **not** block economy/growth buildings; fall back to base logic after the pre-filters. AIs tend to value **Heroic/National Epics** more and build them in top-hammer cities. See **[KI#48](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#48---enhancedreworked-ai-building-walls-when-they-are-stronger-and-dont-need-it-or-wonders-when-they-are-weaker-or-in-danger-dont-build-wonders-for-our-neighbours-when-they-capture-us-and-overall-added-a-lot-of-extra-buildingvalue-reject-orand-always-build-first-logic-depending-on-building-type-andor-such-anyways-etc--and-reworked-as-well-the-ditching-wonders-logic-to-be-seemingly-stricter-and-more-wardanger-focused-anyways-etc)**.

#### Military (AI)

- Curb **naval overbuild**: in `CvCityAI::AI_bestUnit`, reduce making excess naval combat units (esp. when landlocked or when land war is likely) to prevent getting invaded on land with too few defenders. See **[KI#35](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#35---attemptingly-fixed-or-addressed-ai-building-too-many-military-naval-units-then-gets-invaded-on-land-and-cant-defend-10-galleons-and-barely-any-land-defender)**.
- Avoid **settlers at critical war timings**: bias `AI_bestUnit` away from settlers when war is likely; prepare for war instead. Related: settler is a **national unit (1 max)**. See **[KI#36](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#36---attemptingly-fixed-or-addressed-ai-building-settlers-at-critical-time-when-war-is-likely-instead-of-preparing-for-war-very-bad-as-the-few-more-units-with-the-hammer-saved-could-make-us-gain-or-not-lose-the-war-while-the-extra-city-makes-all-our-empire-thinner-and-our-units-split-on-top-of-having-less-units-overall-as-well-anyways-etc)** and **[Civilian Units](#civilian-units)**.
- Disable unreliable **UnitAIs** for AIs: `UNITAI_COLLATERAL`, `UNITAI_PILLAGE`, `UNITAI_PIRATE_SEA` to reduce suicides/baiting and keep stacks focused.
- Retune UnitAI **selection/weights** in `AI_bestUnit`, `AI_bestUnitAI`, `AI_chooseProduction`: land maps emphasize `UNITAI_ATTACK` / `UNITAI_ATTACK_CITY` (with some `UNITAI_RESERVE`); defense mode emphasizes `UNITAI_CITY_DEFENSE` / `UNITAI_CITY_SPECIAL` / `UNITAI_RESERVE`; naval UnitAIs are downweighted on land-focused maps. Goal: fewer wandering/baited units; more decisive stacks.
- Rebalance perceived **iPower**: downweight some naval units; adjust certain land units (e.g., warrior, animals) to reduce **fake power** that triggers bad wars. See `/Assets/XML/Units/CIV4UnitInf_os_UnitAI_and_notes.txt`.
- **Barracks**: lower flavor military (e.g., 10 → 6 for the generic barracks) so non-militaristic leaders don’t overbuild it; increase `iAIWeight` substantially (e.g., 0 → 70; 75 for Zulu barracks) so when built, it’s for solid ROI (earlier experienced troops). Rationale drawn partly from FFH2’s use of 40 as a baseline.
- **Stables**: similarly increase `iAIWeight` (e.g., 0 → 75) so they’re pursued when relevant.
- XML **DefaultUnitAI / UnitAIs / NotUnitAIs**: align roles with efficiency (e.g., swordsmen primarily offensive even if versatile; longbows defensive unless explicitly set otherwise).
- Early **siege**: adjust UnitAIs so early siege doesn’t get baited away from core attack/defense purposes.
- Promotions logic in `CvUnitAI::AI_promotionValue`: add **hard rules** so AIs pick context-appropriate promotions (e.g., City Garrison for `UNITAI_CITY_DEFENSE`, City Raider for `UNITAI_ATTACK_CITY`; avoid Woodsman/Medic on front-line attackers unless context justifies). Rules apply per **UnitAI** (not just by unit type); with exceptions like recon. See **[KI#47](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#47---fixed--addressed--enhanced-ai-choosing-poorly-promotions-for-its-units-now-added-a-set-of-hard-rules-in-which-case-some-promotions-are-not-good-and-to-ignore-as-is-most-efificient-in-most-times-and-rarely-cases-where-some-promotions-are-best-to-always-go-first-for-eg-as-of-no-city_garrison-first-for-unitai_city_defense-city_raider-first-for-unitai_attack_city-etc-if-any-more-anyways-etc)**.
- New-city **minimum defenders**: ensure new cities are founded/left with **2+ defenders** (priority to capital). Optimization disabled after ~turn 120 (scaled) to save compute once empires stabilize. See **[KI#49](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#49---enhancedaddressed-ai-having-4-defenders-in-capital-city-but-only-1-defender-in-city-b-that-gets-captured-or-razed-by-barbarians-then-now-almost-always-if-not-always-new-cities-go-be-founded-with-2-defenders)**.
- **Scrapping safeguards**: added pre-checks to stop scrapping **useful units**—**all land military units are protected**, and **no unit can be scrapped before turn 150**. Fixes early “produce then scrap” cases (e.g., macemen) and keeps forces on the map vs. barbarians/rivals (**no economy check**). See **[KI#52](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#52---beyond-tremendously-improved-anyways-etc-remove-ai-scrapping-of-military-land-units-as-way-too-many-units-are-scrapped-early-yet-we-really-need-them-to-defend-against-barbarians-or-our-rivals-or-such-anyways-etc)**.
- **Musketmen — AI role**: now also flagged with `UNITAI_ATTACK_CITY`, so the AI uses Musketmen more often in **offensive city-assault** roles. Civ-specific Musketman variants may also include additional changes.
- **Grenadiers & Bazookas — AI role**: now also flagged with `UNITAI_CITY_DEFENSE`, so the AI may use them more for **city defense**.

### UI / In-game

- Disable colored ring **worker recommendations** (keep city site suggestions). Removes computation and avoids conflicts with the new worker logic. Change in `CvGame::updateColoredPlots`.

### General changes (non-exhaustive; see GlobalDefines/XML)

- **Timeline / Pace**: game starts at **-50 000 BC** on `GAMESPEED_NORMAL`, then accelerates (large early steps, smaller later ones). Other game speeds currently follow base AdvCiv pacing. See *CIV4GameSpeedInfo.xml* and [Tech tree](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Tech_Tree.md).
- **Start map behavior**: less “terrain polishing”; more starting **vision** so you can choose a spot rather than forcing ideal tiles.
- **Slavery**: `HURRY_POPULATION` production increased (**27**). See *CIV4HurryInfo.xml* (`HURRY_POPULATION`).
- **Leader random selection**: `PER_EXTRA_LEADER_CIV_SELECTION_WEIGHT` **20 → 0** (all civs equal chance regardless of leader count). See *GlobalDefines_advc.xml*.
- **We Love the King Day**: restored (present in SAS).
- **Research scaling — sea level**: `iResearchPercent = 100` for High / Medium / Low (**was** `117 / 100 / 87`). Sea level no longer alters research pace.
- **Research scaling — world size**: `iResearchPercent` **rescaled** from `95 / 98 / 102 / 115 / 137 / 150` to `85 / 90 / 95 / 100 / 125 / 150` (so **Standard = 100**). This makes Standard the baseline and keeps scaling explicit.

### Handicap i.e. difficulty settings (non-exhaustive)

See the **CSV/MD tables** for exact values ([handicap tables](/README.md#csv-and-md-view-of-the-handicap-difficulties-info-in-a-table-for-all-difficulties-info)).

- **No free techs** for AI or human.
- **Human costs fixed** across difficulties for tech/unit (`iResearchPercent`, `iTrainPercent` stay constant for the human). AI equivalents scale with difficulty.
- **Unit maintenance** (`iUnitCostPercent`, `iAIUnitCostPercent`) aligned across difficulties for fairness; difficulty tuned through other params.
- **No delayed starts**: `INCREASE_START_TURN` disabled; all difficulties start on **turn 0**.
- **AI worker speed**: `iAIWorkRateModifier` **0** on all difficulties.
- **AI starting workers**: `iAIStartingWorkerUnits` **0** on all difficulties.
- **Goodies (huts)**: remove **worker/settler** pops; rebalance barbarian outcomes (fewer strong, more weak at high difficulties); increase **experience** rewards at higher difficulties.
- **Handicap normalization (starting units)**: Reduced/standardized several handicap fields so they’re **the same at all difficulties**: `iStartingDefenseUnits`, `iStartingWorkerUnits`, `iStartingExploreUnits`, `iAIStartingDefenseUnits`, `iAIStartingWorkerUnits`, `iAIStartingExploreUnits`. This reflects recent AI improvements (workers, building choices, scrapping rules, unit mix) and aims to keep games fair while the AI remains competitive. See [Handicap tables](/README.md#csv-and-md-view-of-the-handicap-difficulties-info-in-a-table-for-all-difficulties-info).
- **Difficulty scaling — `iAIHandicapIncrementTurns`**: **disabled (set to 0 on all difficulties)**. This removes the **per-turn** AI discount that made games progressively harder; with SAS’s improved hammer efficiency, that scaling led to runaway AIs at high levels. Now AI cost/research **modifiers** come **only** from the static **difficulty (handicap) XML fields** (e.g., `iAITrainPercent`, `iAIBuildingCostPercent`, `iAIResearchPercent`, …), which have been **retuned to be linear by difficulty (not per-turn)**—hard but fair. Practical effects: fewer excess units and lower bankruptcy risk, healthier mid→late-game economies, and challenge that relies on AI competency gains rather than exponential scaling.

### Specialists (non-exhaustive)

- **Citizen**: now **+1 hammer, +1 commerce** (was +1 hammer). See Sevopedia/XML.
- **Priest**: now adds **+1 culture** (total **+1 hammer, +2 commerce, +1 culture**).
- **Engineer**: now **+1 hammer** (total **+3 hammers**).

### Terrains / Features (non-exhaustive)

- Overall: **snow**, **desert**, and **water** tiles strengthened via bonus/building changes (see Bonus/Buildings sections).
- **Floodplains persist after raze** (city destruction doesn’t remove them).
- **Recon units** (ground) can move through **all terrains** (`bCanMoveImpassable`) and **ignore terrain movement costs**; air recon (e.g., **airship**) can move across all terrains (`bCanMoveAllTerrain`), including peaks/water.
- **Movement restrictions** (outside cultural borders): some units (e.g., **chariots**, some **siege**) can’t move in **forest/jungle**; mounted melee/ranged receive **forest/jungle** combat penalties (ranged limited to defense penalty). See Sevopedia entries for per‑unit modifiers.
- **Feature: Jungle** rework: remove the food penalty (**no food malus**), increase unhealth to `iHealthPercent` **-50**, set feature defense `iDefense` **-25** (still +25% rival defense in features → net 0 in jungle). **Remove jungle** now yields **+20 hammers**.
- **Feature: Fallout** `iHealthPercent` **-50 → -75**.
- **Feature: Flood Plains** `iHealthPercent` **-40 → -50**.
- **Terrain: Tundra** base yield adds **+1 commerce**.

### Bonus (non-exhaustive)

- **Wine → Grapes**: now improved by **Plantation** (not Winery). Happiness moved to **Grocer** (Grapes and Sugar both give happiness via Grocer). See Sevopedia/XML.
- **AI objective** emphasis for key strategic bonuses: Iron, Horse, Aluminum (`<iAIObjective>10</iAIObjective>`).
- **Hit bonuses** functionally disabled (kept late in tree, obsolete on reveal) to avoid LSystem issues; dependent assets rebalanced or left as‑is where appropriate.
- **Camel** replaces Hit Movies; spawns on **desert**. High food profile; supports camel‑mounted units (see Military section).
- **Spawn tweaks**: water bonuses more frequent (Fish/Molluscs); **Whales** can also spawn on **coast**; **Horses** removed from **tundra**; many bonuses shifted slightly toward **map edges**; overall frequencies/yields rebalanced (e.g., **Deer** stronger and more common as core tundra food).
- **Gemstones** can spawn on **flood plains**/flatlands; no longer on **hills**. See Sevopedia/XML.

### Improvements and worker builds (non-exhaustive)

- **Tech prereqs** adjusted (e.g., **Quarry** earlier; **Remove Forest** and **Remove Jungle** available together and earlier).
- **Farms without irrigation** unlock at **Engineering**.
- **Worker cost reduced** (see XML for exact value).
- **Workshops** can be built on **tundra** (`<TerrainMakesValids>`).
- **Railroads** placed earlier in the tree (**Steam Power**). See Techs.

### Technologies (non-exhaustive)

- **Large reorder** for historical flow (e.g., Pottery before Wheel; Metal Casting before Currency and Bronze Working; Medicine earlier). Total tech count kept similar to base.
- Gameplay timings shift: **culture**, **slavery**, **plantations**, etc., often **earlier**.
- Many techs flagged **“Cannot be traded.”** New UI strings added to Sevopedia Tech (Special Abilities) and Tech Advisor to display this. See *Modding_Ressources/README* entry.
- **TECH_COST_NOTRADE_MODIFIER** **-23 → -20** (when No Tech Trading game option is on). See *GlobalDefines_advc.xml*.
- **Exponential pacing**: fewer late‑era techs/units to avoid a tedious endgame.
- **FirstFreeUnitClass** assignments reshuffled to diversify GP races (one GP type per tech; often earlier).

### Eras

- **Future era** reworked into a full era with techs/units/buildings and its own music; begins with **tech_depopulation** as a balancing/historical nod. See Sevopedia/XML.
- **Era info** is shown in Sevopedia Tech entries.
- **Eras — research scaling**: `iResearchPercent = 100` for all eras; `iTechCostModifier = 0`. Tech costs now come directly from TechInfos (no hidden per-era multipliers).
- **Eras — anarchy scaling**: `iAnarchyPercent = 100` for all eras (**was** `50 / 50 / 40 / 40 / 34 / 34 / 34`). In practice this yields about **2 turns** of anarchy when you change civics (or similar). Intent: add strategic weight without tedium; **indirectly buffs** traits with **no anarchy** (e.g., Spiritual).
- **Eras — growth & production scaling flattened**: set `iGrowthPercent` (food-to-grow), `iTrainPercent` (unit cost), `iConstructPercent` (building cost), and `iCreatePercent` (project cost) to **100 for all eras** (**was** `100 / 100 / 100 / 90 / 80 / 70 / 60`). Removes late-era discounts that sped up mid/late game; pacing is now **predictable and gradual**, with balance handled directly via per-item `iCost` instead.
- **Eras — worker builds & improvements scaling flattened**: set `iBuildPercent` and `iImprovementPercent` from **100/100/100/90/80/70/60 → 100** at **all eras**. The original reason for the era-based scaling isn’t known; this change is intentional to keep tile-development pacing **predictable and consistent** across eras and to tune balance directly through base costs/worker rates rather than hidden era multipliers.
- **Eras — culture scaling flattened**: set `iCulturePercent` from **100/100/80/70/60/50/50 → 100** at **all eras**. Removes late-era culture acceleration so culture growth stays **consistent** and driven by **commerce/buildings**, not hidden era multipliers. In **AdvCiv-SAS**, if we ever want modern (or ancient) culture to weigh differently, we prefer adjusting the **explicit culture values on buildings/units** rather than reintroducing era-wide modifiers.

### Civilizations (non-exhaustive)

- New civs added (e.g., **Kingdom of Benin**). See [World map with civs](/README.md#world-map-with-civs).

### Leaders (non-exhaustive)

- Each leader now has **distinct leader music** (previous BTS/AdvCiv shared tracks split per leader). See [Copyright & disclaimer](/README.md#copyright-and-disclaimer).

### Barbarians (non-exhaustive)

- **Barbarians — stronger early game & smarter aggression**: economically **stronger in the early game**, growing at a pace closer to human/AI civs and **founding cities more often**, so they stay **relevant longer** before gradually fading by midgame. They still aren’t a full player (**no diplomacy**; **scattered independent cities** that collectively count as the Barbarian civilization). Difficulty scaling is adjusted so players have **less to no combat bonus vs. barbarians** (never a reverse bonus for barbs), with strength **rising gradually by difficulty**. Barbarians also **fill unclaimed land** if it’s left open, tend to **target weaker rivals**, and may **raze cities** more than base AdvCiv/Civ4. This pairs with the AI’s improved **hammer efficiency and availability** (far fewer scrapping/no-production issues): by engaging and “burning off” surplus early units (e.g., **ancient macemen, archers, longbowmen**), barbarians help prevent runaway over-production and early bankruptcies while empires keep growing. For definitions and exact knobs, see the Sevopedia **Barbarian Civilization** entry and XML: [CIV4CivilizationInfos.xml](/Assets/XML/Civilizations/CIV4CivilizationInfos.xml), [CIV4BuildingInfos.xml](/Assets/XML/Buildings/CIV4BuildingInfos.xml), and [CIV4HandicapInfo.xml](/Assets/XML/GameInfo/CIV4HandicapInfo.xml); also see the SAS **handicap tables** in the repo for comparative values.
- Combat bonuses **against** barbarians are reduced/removed in a difficulty-scaled way (never a reverse bonus **to** barbarians). They choose targets more carefully and **raze** cities more often than base AdvCiv/Civ4. See Sevopedia and XML (e.g., `CIV4CivilizationInfos.xml`, building/handicap XML) and the SAS handicap comparison tables.
- Barbarian **workers** are civ-specific and **cannot be captured** (prevents worker farming).  
- Barbarian **workboat** is civ-specific mainly for cost/balance.  
- Barbarian **leader button/icon** is distinct (no longer Genghis Khan’s). See Sevopedia for the new button source credit.

### Traits (non-exhaustive)

- Several traits reworked. Weaker ones are buffed/modified; some previously OP ones are adjusted. Example: **Protective** is stronger; **Industrious** shifts away from “wonders faster” toward **worker/production-oriented** effects (elements formerly in Expansive). See in-game Sevopedia → Traits for current effects (+x culture / +x hammer / +x commerce as listed there).

### Civics (non-exhaustive)

- Some civics reworked/rebalanced (e.g., **Representation** earlier in SAS and with adjusted effects).
- Some civics moved on the tech tree for history/balance/variety. **Slavery** is now at **Agriculture** (earlier), which weakens the **Bronze Working** beeline and opens non-military paths.

### Buildings (non-exhaustive)

- **Granary:** cheaper, slightly weaker food retention. Civ-specific granaries unchanged (so their relative advantage increases).

- **Water building line reworked/buffed:**
  - **Harbor** (first water building): health/food oriented.
  - **Lighthouse:** gold oriented (**+x commerce** from worked tiles where applicable).
  - **Port (new):** production oriented (**+x hammer** from worked tiles where applicable).
  - **Moai Statues:** world wonder with broader water synergy; somewhat stronger overall.
  - **Customs House:** buffed.  
  *(Goal: make water tiles more viable while requiring you to work them for the benefits; yields apply per worked tile, not passively from routes.)*

- Fewer **national** wonders and relatively more **world** wonders.
- **Palace-likes** (Forbidden Palace, Versailles, etc.) mostly reworked as **world** wonders with tech prereqs so they appear in the tech tree and AIs don’t build them too early. (Barbarian Palace unchanged; used as a balance lever.)
- Many world-wonder effects simplified/retuned; overall costs adjusted (often slightly **lower**) because:
  - `BonusProductionModifiers` (e.g., +100% with Marble) are **greatly reduced** (world: mostly removed; national: mostly reduced). Example: **Parthenon** is now **+25% with Marble** (was +100%).
- Removed buildings that didn’t carry their weight or distorted pacing (e.g., **Space Elevator**, **West Point**).
- **Iron Works:** now requires **both Coal and Iron** empire-wide; city requirement count lowered; cost up moderately (e.g., **700 → 800**) so timing/placement matter more.
- **Heroic Epic** (`iMilitaryProductionModifier`): **100% → 50%**. The always-on military production boost was too strong and could let AIs run away; this tones it down while keeping the building relevant.
- Some **civ-specific** buildings replaced (especially late-game or underwhelming ones). Example: Russian **Research Institute** replaced with **Gord** (castle-based, earlier impact).
- Added `BuildingClassRequired` chains to curb spam and improve AI focus: e.g., **Drydock** now requires **Port**.
- Science buildings’ **culture** trimmed (e.g., **Library +2 culture → +1 culture**); similar trims on a few non-purely-cultural national wonders (**Heroic/National Epic, Forbidden Palace**).
- **Barbarians** no longer attempt **world wonders** (prevents hammer sinks). See [KI#3](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#3---now-fixed-with-a-dll-patch-barbarians-cities-building-wonders-in-particular-now-fixed-ie-disabled-for-world-wonders-anyways-etc).

### Culture

- **Great Artist** rework: instant culture bomb **reduced** (e.g., **700 → 500** per era), culture **per turn increased** (e.g., **12 → 18** culture/turn). This strengthens long-term culture play while toning down early spikes.

### Religions (non-exhaustive)

- **Paganism** added, **Confucianism** removed (fewer total religions, earlier conflicts slightly more likely, arguably more historical). **Judaism** stays as early representative of monotheism in Civ’s roster.
- **Missionaries:** significantly **cheaper**.
- **Monasteries:** simplified — now **espionage** buildings with a **low Great Person rate**; **no longer obsolete**; **no longer give science** (keeps science buildings cleaner and the theming clearer).
- **Shrines** now **require their religion in the city and the religion’s tech** (so they appear in the tech tree and can’t be built just by conquest). See [KI#12](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#12---shrines-now-require-their-religion) and [KI#13](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#13---shrines-now-appear-in-tech-tree).
- **Note on leader preferences:** a leader may **prefer** a religion without adopting it (role-play nuance; see your notes linked from the KI entries).

### Corporations (non-exhaustive)

- **Executives:** significantly **cheaper**.
- Each corporation now uses **one distinct Great Person** type (no overlaps).

### Civilian Units

- `DOW_UNIT_CAPTURE_CHANCE` **0 → 50**: workers can be captured **on the turn war is declared**, same as other turns. Aligns with the base capture chance and rewards opportunistic warfare.
- **Settler** is a **national unit (1 max)** per empire. This prevents AI from building two at once or building a new one while an existing settler is travelling, improves hammer/food efficiency, and raises the stakes on timing/escorts. See [KI#37](/_1_AdvCiv-SAS/Docs_And_Appendixes/README_Known_Issues_In_Base_AdvCiv_Civ4.md#37---workaround-and-rebalanced-ai-building-2-settlers-very-inefficiently...).

### Military & related units (non-exhaustive)

- **Unit Combat Types** expanded/refined (e.g., archers split into short/long/crossbow; mounted split into mounted-melee vs mounted-ranged). Lets counters be more specific (e.g., pikes vs mounted-melee but not vs mounted-ranged). Some civ UUs shift types accordingly (e.g., **Ballista Elephant** is mounted-ranged while **War Elephant** is mounted-melee). **Airship** becomes **Recon** (no longer sees subs; later recon can).
- **Reassignments:** e.g., **Mechanized Infantry** counts as **Armored** (not “Gun”) for counter logic.
- **City defenses** affect all units, including gunpowder and later. See `bIgnoreBuildingDefense` in `CIV4UnitInfos.xml`.
- **Collateral** values normalized (fixed cases like **Stealth Bomber** having higher base collateral than its limit). Most units now show a **collateral damage limit** (starting at 0 for many). **Collateral promotions 1/2** are broadly available where eligible. Info shown in Sevopedia (Unit chart/Special Abilities) and unit hover panels.
- **Build timing** tweaks for some units for historical pacing; see Tech Tree.
- **Warrior / “Ancient Maceman”** rebalanced: higher base strength, lower city-combat, gains **vs Animals** bonus; cost slightly up.
- **Archer / Longbowman:** both available earlier with lower base strength and cost but with new stat mixes; **Archer** no longer upgrades to late units; **Longbow** upgrades to **Crossbow** (earlier availability).
- **Barracks** now require **Hunting**.
- **Explorer-class** units can **attack**, but with low strength.
- Units more **versatile:** e.g., Swords defend better; Archers can attack more credibly.
- **Naval/animal** units broadly rebalanced; see XML for details.
- **Grenadiers & Bazooka (formerly Anti-Tank Infantry)**: rebalanced into **hybrid, versatile “foot-bomber” roles**.
- **Gun units buffed (relative to pre-gun)**: units that **carry firearms** (e.g., **Musketman**, **Horse/Camel Cuirassiers**) are **relatively stronger** than their pre-gun counterparts.
- **Promotions retuned:**
  - Some buffed (e.g., **Woodsman**), some nerfed, some prereqs changed (e.g., **Archers** can take **City Bombard**; **Logistics** (formerly Commando) requires **Combat 1** or **City Raider 1**; higher-tier promotions (**City Raider/Garrison/First Strike 3**) also need **Combat 2**).
  - **Logistics** now at **The Wheel** (was Military Science).
  - Removed redundant promotions (e.g., **Tactics**), to avoid broken retreat odds.
- **Unit redesigns:**
  - Weak/late UUs replaced by earlier/impactful ones (e.g., Dutch **East Indiaman** → Dutch **Swift Worker**; German **Panzer** → **Hussar**).
  - **Air** unit costs generally increased.
- **Upgrade paths** simplified and made more sensible:
  - Mounted tiers upgrade along mounted lines (e.g., **Chariot → Horse Archer**; **War Elephant → Knight**).
  - Cross-mount upgrades allowed (**Horse ↔ Camel** where logical).
  - **Longbows/Crossbows/Macemen → Musketmen** (more historical/balanced; reduces abuse by **Cuirassiers**, which are slightly stronger but more expensive).
  - **Cavalry → Tanks** now.
- **Naval upgrades** cleaned up; **Ironclad** can enter ocean and is buffed, serving as a real upgrade from Frigates. See [README: military tree](/README.md#military-tree-and-changes) for full upgrade maps.
- `BBAI_DEFENSIVE_PACT_BEHAVIOR` **disabled (0)** to restore default BTS behavior (pacts break on DoW).
- **Voluntary vassals** are **permanent** (culture absorption/merger flavor).
- **Permanent Alliance** moved off the main military path (was on both **Communism** and **Fascism**) to reduce military beeline dominance and respect “one tech per major unlock” consistency.
- **Costs:** some late/mechanical/robotic units have **no support cost**; **Privateer** now **has support** (was free).
- **Stealth** removed where it didn’t make sense (kept for subs, spies, stealth bombers).
- **Caravel** removed (privileged border passing felt wrong); shift that niche to **Privateer** (buffed) and streamline the era’s naval roster.
- **Nuclear Submarine** removed (under-impactful relative to complexity).

## Fixes

See [Known issues / fixes](/README.md#known-issues-that-may-be-fixed-or-not-fixed-in-base-advciv-orand-civ4-anyways-etc) for the indexed list and links to before/after notes and screenshots.

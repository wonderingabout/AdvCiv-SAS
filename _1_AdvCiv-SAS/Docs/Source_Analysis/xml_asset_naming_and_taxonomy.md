# XML Asset Naming and Taxonomy

**History reviewed through the 2026-11-05 AdvCiv-SAS tree.**

Written on 2026-11-04 by ChatGPT-5.6-Sol and GPT-6.1-Sol (Codex); the Monument / Obelisk explanation was reviewed by Claude code Opus 5.5. Updated through the 2026-11-05 Viking-namespace restoration by ChatGPT-5.6-Sol.

This document records **what AdvCiv-SAS renamed, split, reclassified or otherwise changed in inherited AdvCiv/Beyond the Sword asset naming and taxonomy; when it changed; why it changed; which companion identifiers or consumers changed with it; and what happened to that form later**.

Its scope is broader than primary XML `<Type>` fields: where the same naming decision affected `TXT_KEY_*` identifiers, player-facing English names, art/audio IDs, classes, `UNITAI_*`, True Starts IDs or other companion namespaces, those changes are recorded too.

It is primarily a historical change ledger: current names and classifications are useful insofar as they show the result of an evidenced change.

For future maintenance and LLM review, do not infer a rename merely because one inherited `Type` disappeared and another appeared. Treat an old -> new relationship as a rename only when the Git history, source comments or an otherwise clear companion-family change establishes that lineage.

Likewise, do not flatten a one-to-many split such as `UNITCOMBAT_ARCHER` into one arbitrary rename: record the split and the units/consumers that moved into each new family.

Replacements, splits, reclassifications and new content are recorded separately so that later cleanup does not repeat or undo deliberate work by accident. Ordinary wording/UI edits that are unrelated to an asset's identity are out of scope, while asset-related display-name or text-key changes are in scope even when the primary XML Type stayed unchanged.

Detailed balance values remain in [`README_Assets_Rebalancing.md`](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md); this document focuses on **asset naming/identity, taxonomy history and the reason for the structural change**.

## Menu

- [At-a-glance change ledger](#at-a-glance-change-ledger)
- [Restoration decisions](#restoration-decisions)
- [Clearest inherited example: Monument / Obelisk](#clearest-inherited-example-monument--obelisk)
  - [How the confusion arose](#how-the-confusion-arose)
  - [What plain `OBELISK` meant in each field](#what-plain-obelisk-meant-in-each-field)
  - [SAS rule and cleanup](#sas-rule-and-cleanup)
- [Inherited naming slips found during review](#inherited-naming-slips-found-during-review)
- [Companion completeness finding: True Starts](#companion-completeness-finding-true-starts)
- [Bonuses](#bonuses)
  - [2026-11-04 machine-ID restoration](#2026-11-04-machine-id-restoration)
  - [Gems to gemstones](#gems-to-gemstones)
  - [Ivory to elephants](#ivory-to-elephants)
  - [Wine to grapes](#wine-to-grapes)
  - [Corn to maize](#corn-to-maize)
  - [Clam to molluscs and cow to cattle](#clam-to-molluscs-and-cow-to-cattle)
  - [Movies to camel is not a rename](#movies-to-camel-is-not-a-rename)
- [Leaders](#leaders)
  - [`LEADER_CHINESE_LEADER -> LEADER_MAO_ZEDONG`](#leader_chinese_leader---leader_mao_zedong)
  - [`LEADER_MONTEZUMA -> LEADER_MOCTEZUMA`](#leader_montezuma---leader_moctezuma)
- [Civilizations](#civilizations)
- [Same-Type display and text-key renames](#same-type-display-and-text-key-renames)
- [Religions](#religions)
- [Units and Great People](#units-and-great-people)
  - [Great People: exact 4750 naming changes](#great-people-exact-4750-naming-changes)
  - [Unit-combat taxonomy splits](#unit-combat-taxonomy-splits)
  - [Same-Type unit class and role reclassifications](#same-type-unit-class-and-role-reclassifications)
  - [Naming-led unit changes](#naming-led-unit-changes)
  - [Unit replacements and splits](#unit-replacements-and-splits)
- [Buildings](#buildings)
  - [Naming-led building changes](#naming-led-building-changes)
    - [Monument / Obelisk namespace cleanup](#monument--obelisk-namespace-cleanup)
  - [Building replacements and redesigns](#building-replacements-and-redesigns)
- [Promotions](#promotions)
- [Technologies](#technologies)
  - [Direct or explicitly evidenced inherited lineages](#direct-or-explicitly-evidenced-inherited-lineages)
  - [Reused identifiers that final-state diffs can hide](#reused-identifiers-that-final-state-diffs-can-hide)
- [Civics](#civics)
- [Other XML Type families](#other-xml-type-families)
  - [Art-definition-only naming corrections](#art-definition-only-naming-corrections)
- [Systematic AdvCiv 1.14 -> SAS Type-set reconciliation](#systematic-advciv-114---sas-type-set-reconciliation)
- [Historical evidence](#historical-evidence)

## At-a-glance change ledger

The table below is intentionally about **changes**, not a description of the current asset set. Detailed category tables below give companion IDs and commit evidence.

| Family | Documented inherited -> SAS naming changes | Main practical commit(s) / date(s) | Later state by 2026-11-04 |
| --- | --- | --- | --- |
| Bonuses | `GEMS -> GEMSTONES`; `IVORY -> ELEPHANTS`; `WINE -> GRAPES`; `CORN -> MAIZE`; `CLAM -> MOLLUSCS`; `COW -> CATTLE` | 4767-4770, 4776; 2025-05-21 to 2025-05-24 | The six inherited machine-ID families were restored on 2026-11-04 while SAS display/gameplay terminology stayed; `MOVIES -> CAMEL` is **not** a rename |
| Leaders | `LEADER_CHINESE_LEADER -> LEADER_MAO_ZEDONG`; `LEADER_MONTEZUMA -> LEADER_MOCTEZUMA` | 4749, 2025-05-11; 4743, 2025-05-08 | Both inherited machine-ID families were restored on 2026-11-04; displayed names remain Mao Zedong and Moctezuma II |
| Civilizations | `CIVILIZATION_VIKING -> CIVILIZATION_SCANDINAVIA`; same-Type display changes also include American Empire -> United States of America and Amerindian Empire -> Native American Empire | 4878, 2025-07-15; display changes 4883, 2025-07-21 | Inherited `VIKING` machine namespace restored on 2026-11-05 while the displayed Scandinavia identity remains; both same-Type display changes remain |
| Religion family | Taoism -> Daoism across religion, buildings, missionary, art and text-key namespaces | 4740-4741, 2025-05-07 | Daoism family still present; Confucianism removal/Paganism addition was separate |
| Great-Person units/classes | `UNIT_PROPHET/ARTIST/SCIENTIST/MERCHANT/ENGINEER -> UNIT_GREAT_*`; same for `UNITCLASS_*`; corresponding `UNITAI_* -> UNITAI_GREAT_*`; `UNITAI_GENERAL -> UNITAI_GREAT_GENERAL` | 4750, `701e2e3127`, 2025-05-11 | Still present |
| Great-Person specialist display | Inherited machine ID already `SPECIALIST_GREAT_PRIEST`; SAS changed its displayed text from **Great Prophet** to **Great Priest** while the mobile unit remained Great Prophet | 4750, `701e2e3127`, 2025-05-11 | Still present; this is a text change, not a SpecialistInfo Type rename |
| Same-Type display/text changes | `TERRAIN_SNOW`: Ice -> Ice Sheet; `FEATURE_ICE`: Ice -> Ice Cap; `LEADER_PACAL`: Pacal -> Pacal II; `LEADER_JUSTINIAN`: Justinian -> Justinian I; `LEADER_SURYAVARMAN`: Suryavarman -> Suryavarman II; `CIVILIZATION_AMERICA`: American Empire -> United States of America; `CIVILIZATION_NATIVE_AMERICA`: Amerindian Empire -> Native American Empire; Persia Immortal text-key typo `PERIA -> PERSIA` | 4461-4462, 4648, 4841, 4883 | Machine Types stayed the same; display/text-key history is nevertheless part of the naming audit |
| Selected units | In addition to Hoplite/Legionary/Viking and artillery/tank renames: `KNIGHT -> HORSE_KNIGHT`, `CUIRASSIER -> HORSE_CUIRASSIER`, `MARINE -> MODERN_INFANTRY`, `AT_INFANTRY -> BAZOOKA`, `ARABIA_CAMELARCHER -> ARABIA_HAJJAN`, plus the Great-Person family | 4750, 4841, 4858, 4871, 4878, 4909-4910, 4957 and later | Mixed; some are pure naming, many are rename + redesign or line splits |
| Buildings | Direct naming cleanups include `OBELISK -> MONUMENT`, `GREAT_PALACE -> FORBIDDEN_PALACE`, `NATIONAL_SECURITY -> SECURITY_BUREAU`, `GREAT_DAM -> THREE_GORGES_DAM` and `CHICHEN_ITZA -> TEMPLE_OF_KUKULCAN`; many inherited UBs were later replaced rather than merely renamed | 4748-4750, 4764, 4985; later UB replacement waves through 6113 | Direct rename families remain documented separately from replacement/redesign lineages |
| Promotions | Numerous mechanics-descriptive renames such as `MARCH -> MEDIC_AMBULATORY`, `COVER -> COUNTER_ARCHER`, `FORMATION -> COUNTER_MOUNTED`, `DRILL* -> FIRST_STRIKE*`, `FLANKING* -> RETREAT*` | 4625-4676 and 4865, 2025-04-10 to 2025-07-09 | Mostly still present; Navigator intermediate naming was later consolidated |
| Technologies | `UTOPIA -> COMMUNISM`; `SAILING -> SEAFARING`; `OPTICS -> SAILING`; `COMPASS -> NAVIGATION`; `STEEL -> MARINE_TECHNOLOGY`; `HORSEBACK_RIDING -> MOUNTED_INFANTRY -> MOUNTED_COMBAT`; `THEOLOGY -> POSTAXIAL_RELIGION`; `DIVINE_RIGHT -> LATER_ABRAHAMISM`; `RIFLING -> FIREARMS`; `EDUCATION -> BROADER_EDUCATION`; many later slots were deliberate replacements | 4781, 4830, 4857, 4863, 4967-4976 and later | Mixed; several intermediate names were superseded or reused |
| Civics | `PAGANISM -> PREHISTORIC_RELIGION`; `EMANCIPATION -> WAGE_LABOR`; later `MERCANTILISM -> PROTECTIONISM` and `ENVIRONMENTALISM -> TRADE_BLOC` were redesign/replacement lineages | 4748, 5104, 5121 | All four inherited IDs absent by 2026-11-04; successors documented below |
| Unit combat taxonomy | `ARCHER -> ARCHER_BOW_SHORT / ARCHER_BOW_LONG / ARCHER_CROSSBOW`; `AIR -> AIR_BOMBER / AIR_FIGHTER` (Airship later moved to `RECON`); `MOUNTED -> MOUNTED_MELEE / MOUNTED_RANGED`; `MELEE -> MELEE_POLEARM / MELEE_SHOCK` | 4602/4605/4606, 4616/4618, 4866, 5019; 2025-04-08 to 2025-09-28 | All four broad inherited families were deliberately refined; this is taxonomy history, not four one-to-one aliases |

When a renamed identifier is later restored, removed or superseded, preserve the historical row here and update the **later state** rather than rewriting the original change. Old-to-current translation entries can additionally be recorded in [`Docs/Deprecated`](/_1_AdvCiv-SAS/Docs/Deprecated/README.md).

## Restoration decisions

Decisions and their reasons as of 2026-11-05, from the user, ChatGPT-5.6-Sol and Claude code Opus 5.5. An inherited machine ID is worth restoring where SAS kept the inherited asset and changed little more than its name; the player-facing SAS names stay either way.

- **Bonuses and the two leader families:** restored, because SAS kept these assets and map scripts place bonuses by their `BONUS_*` names.
- **Scandinavia civilization:** the inherited `VIKING` machine namespace was restored as one whole family on 2026-11-05 while the player-facing identity stays Scandinavia.
  - Companions use the same machine namespace, including `UNIT_VIKING_VIKING` and `BUILDING_VIKING_CHIEFTAINS_HALL`; the deliberate repeated `VIKING` distinguishes the civilization namespace from the unit name instead of recreating a mixed Monument/Obelisk-style family.
  - SAS-created art folders follow the restored machine namespace too.
  - The civilization remains listed under S because Custom Game order follows the shown short name, not `<Type>` (KI#1073).
- **Daoism:** undecided. It is the same religion with the same building and missionary slots, but SAS also removed Confucianism and added Paganism. Reordering religions would also need matching GameFont glyphs, because religion icons are assigned in XML order.
- **Religion order:** kept as SAS's historical founding order (2025-05-22) rather than BtS's, which starts with Judaism. Religions are referenced by their Types, not their position, so the BtS order would give little compatibility; the GameFont glyphs follow the SAS order, and `xml_display_order.py` keeps them in step (KI#1073).
- **Kept as SAS names**, because they changed too much for inherited names to give real compatibility. Many mods also change these families heavily, as SAS did, unlike leaders and civilizations, which SAS has barely changed. Their inherited names therefore matter less for compatibility, and map scripts rarely name them, unlike bonuses:
  - technologies, whose tree SAS largely replaced;
  - buildings and ordinary units, many of them replaced or redesigned;
  - unit combat types, which SAS split;
  - promotions, whose SAS names describe their mechanics; many players know the inherited names, but the SAS ones are clearer;
  - Great People `GREAT_*` IDs, which are clearer and consistent with Great General and Great Spy;
  - civics.

## Clearest inherited example: Monument / Obelisk

The Monument/Obelisk naming that SAS inherited from Civ4 (introduced by Warlords, then carried unchanged through BtS and AdvCiv 1.14) was a clear defect, not a matter of naming taste: one plain name, `OBELISK`, stood for two different buildings, and which one depended on the field being read. The 4748 source comment called it "extremely confusing".

### How the confusion arose

- **Vanilla Civ4:** the generic building really was the Obelisk. `BUILDING_OBELISK` used `TXT_KEY_BUILDING_OBELISK` and `ART_DEF_BUILDING_OBELISK` (`Obelisk.nif`), so every field agreed.
- **Warlords, carried unchanged into BtS and AdvCiv 1.14:** the generic building's player-facing name and art became Monument (`TXT_KEY_BUILDING_MONUMENT`, `ART_DEF_BUILDING_MONUMENT` with `Monument.nif`), and Egypt received its own replacement building with the obelisk model.
  - The old generic IDs `BUILDING_OBELISK` and `BUILDINGCLASS_OBELISK` were kept.
  - The Monument's class `BUILDINGCLASS_OBELISK` kept `TXT_KEY_BUILDING_OBELISK` as its own `<Description>`.
  - Egypt's new building `BUILDING_EGYPTIAN_OBELISK` was given that same plain `TXT_KEY_BUILDING_OBELISK` as its `<Description>`.

### What plain `OBELISK` meant in each field

- **In the IDs, it meant the generic Monument.**
  - `<Type>` `BUILDING_OBELISK` and `<BuildingClass>` `BUILDINGCLASS_OBELISK`, although the building's `<Description>` `TXT_KEY_BUILDING_MONUMENT` showed players "Monument".
  - So references such as Stonehenge's `<FreeBuilding>BUILDINGCLASS_OBELISK</FreeBuilding>` and Egypt's replacement mapping read as if they concerned an obelisk, while they meant the Monument.
  - The generic build sound `AS2D_BUILD_OBELISK` (and `SND_BUILD_OBELISK`) was also the `<ConstructSound>` of both buildings.
- **In the text key `TXT_KEY_BUILDING_OBELISK`, it meant both buildings.**
  - Egypt's building: its `<Type>` `BUILDING_EGYPTIAN_OBELISK` and its pedia/strategy keys `TXT_KEY_BUILDING_EGYPTIAN_OBELISK_PEDIA` / `_STRATEGY` all carried the `EGYPTIAN` prefix, but its description key did not, so it looked like the generic building's key.
  - The Monument's building class: `BUILDINGCLASS_OBELISK`, the class that the generic Monument belonged to and that Egypt's Obelisk replaced, used the same key as its own `<Description>`. So the Monument's class was named "Obelisk", while the Monument building itself was named "Monument".
- **Result:** searching for `OBELISK` found the Monument's Type, class and sound together with Egypt's name, and nothing in the identifier said which building a given match belonged to.

### SAS rule and cleanup

Practical commit **4748**, `bf00d29700`, 2025-05-10, established one rule: **`MONUMENT` means the generic building, its class and its generic companions; `EGYPTIAN_OBELISK` means Egypt's replacement wherever an identifier needs to name it.** The displayed names stayed "Monument" and "Obelisk".

- **Generic Monument:** `BUILDING_MONUMENT`, `BUILDINGCLASS_MONUMENT` with `TXT_KEY_BUILDING_MONUMENT` as the class description, and `*_MONUMENT` audio IDs.
- **Egyptian Obelisk:** `BUILDING_EGYPTIAN_OBELISK` (unchanged) with `TXT_KEY_BUILDING_EGYPTIAN_OBELISK`, still mapped as Egypt's replacement for the renamed Monument class.
- **The cleanup's own slip:** the SAS art override still contained the unused vanilla `ART_DEF_BUILDING_OBELISK` (`Obelisk.nif`) beside BtS's `ART_DEF_BUILDING_MONUMENT`. Renaming it in 4748 produced two `ART_DEF_BUILDING_MONUMENT` entries, one pointing to the obelisk model; practical commit 5473 (`e8ad16f247`, 2026-02-20) removed that duplicate.

The table lists each affected namespace:

| Namespace / consumer | Inherited state | SAS after 4748 | What was clarified |
| --- | --- | --- | --- |
| Generic building Type | `BUILDING_OBELISK` | `BUILDING_MONUMENT` | The generic Monument's machine ID now matches what the building actually is and what players already saw |
| Generic class description | `BUILDINGCLASS_OBELISK` (the Monument's class) used `TXT_KEY_BUILDING_OBELISK`, the same key as Egypt's building | `TXT_KEY_BUILDING_MONUMENT` | The Monument's class is no longer named "Obelisk" while the Monument building is named "Monument" |
| Generic building class | `BUILDINGCLASS_OBELISK` | `BUILDINGCLASS_MONUMENT` | Civ replacement mappings, Stonehenge/free-building logic and other class consumers no longer call the generic Monument class "Obelisk" |
| Generic description | Already `TXT_KEY_BUILDING_MONUMENT` | Kept `TXT_KEY_BUILDING_MONUMENT` | This was one source of the inherited contradiction: display text already said Monument while the primary Type/class said Obelisk |
| Generic art-definition Type | BtS's generic building already used `ART_DEF_BUILDING_MONUMENT` (`Monument.nif`); the SAS override also kept the unused vanilla `ART_DEF_BUILDING_OBELISK` (`Obelisk.nif`) | 4748 renamed that leftover to `ART_DEF_BUILDING_MONUMENT`, leaving two `ART_DEF_BUILDING_MONUMENT` entries, one pointing to `Obelisk.nif`; 5473 (`e8ad16f247`, 2026-02-20) removed that duplicate | The rename itself briefly created a Monument art ID with the obelisk model; only the `Monument.nif` entry remains |
| Generic build/tutorial audio | `AS2D_BUILD_OBELISK`, `SND_BUILD_OBELISK`, `AS2D_TUTORIAL_BUILD_OBELISK_*`, `SND_TUTORIAL_BUILD_OBELISK_*` | Corresponding `*_MONUMENT` IDs | Audio companions no longer preserve the misleading generic Obelisk name |
| Egyptian UB Type | `BUILDING_EGYPTIAN_OBELISK` | **Unchanged** | This is the object that actually represents an Obelisk, so its explicit machine identity remained appropriate |
| Egyptian replacement class | `BUILDINGCLASS_OBELISK` | `BUILDINGCLASS_MONUMENT` | The Egyptian Obelisk remains Egypt's replacement for the generic Monument class after the class rename |
| Egyptian description key | `TXT_KEY_BUILDING_OBELISK` | `TXT_KEY_BUILDING_EGYPTIAN_OBELISK` | Removes the last ambiguous plain `OBELISK` text-key use; the English display remains simply **Obelisk** |
| Egyptian pedia/strategy keys | Already `TXT_KEY_BUILDING_EGYPTIAN_OBELISK_PEDIA` / `_STRATEGY` | Kept | These companions were already unambiguous and therefore did not need renaming |
| City/civilization references | Generic references used the inherited Obelisk class/Type family; Egypt mapped that class to `BUILDING_EGYPTIAN_OBELISK` | References moved to the Monument class/Type family while Egypt still maps it to `BUILDING_EGYPTIAN_OBELISK` | The class relationship became explicit without renaming the Egyptian object itself |

This is also why `BUILDING_EGYPTIAN_OBELISK` appears in the [same-Type display/text-key table](#same-type-display-and-text-key-renames): part of the cleanup was a primary Type/class rename, while another part was a text-key disambiguation with the Egyptian BuildingInfo Type left unchanged.

## Inherited naming slips found during review

Human and LLM systematic reviews of the inherited XML also noticed smaller, plainly careless names: misspellings, and text keys copied from a neighbouring entry. Some were fixed; others remain because they are harmless or tied to code.

| Inherited name | Slip | SAS status |
| --- | --- | --- |
| `TXT_KEY_UNIT_PERIA_IMMORTAL*` for `UNIT_PERSIA_IMMORTAL` | `PERIA` for `PERSIA` in the description/pedia key family | Corrected to `TXT_KEY_UNIT_PERSIA_IMMORTAL*` in 4841, `630168d5b8`, 2025-06-24 |
| `UNIT_VIKING_BESERKER` and its art/text companions | `BESERKER` for `BERSERKER` | Gone with the 4878 (`632293eb54`, 2025-07-15) rename to `UNIT_SCANDINAVIA_VIKING`, which was made for the Viking -> Scandinavia naming rather than the spelling |
| `CONTROL_SELECTYUNITTYPE`, `CONTROL_SELECTYUNITALL` | Stray `Y` in `SELECTUNIT` | Kept: also used as `CvEnums.h` enum names, and invisible to players |
| `CONTROL_SELECT_HEALTHY` | `<Description>` `TXT_KEY_MAIN_MENU_HALL_OF_FAME` copied from an unrelated control | Kept |
| `MEMORY_CANCELLED_DEFENSIVE_PACT`, `MEMORY_CANCELLED_VASSAL_AGREEMENT`, `MEMORY_DECLARED_WAR_RECENT` | All use `TXT_KEY_MEMORY_CANCELLED_OPEN_BORDERS` as `<Description>` | Kept |
| `BUILDING_IRON_WORKS` / `TXT_KEY_BUILDING_IRONWORKS`, `LEADER_LOUIS_XIV` / `TXT_KEY_LEADER_LOUISXIV`, `UNITCLASS_WORKBOAT` / `TXT_KEY_UNIT_WORK_BOAT`, `PROMOTION_CITY_RAIDER1` / `TXT_KEY_PROMOTION_CITYRAIDER1` | Type and text key split words differently, so searching one spelling misses the other | Kept |
| `PROMOTION_LEADER` / `TXT_KEY_PROMOTION_GREAT_GENERAL`, `TERRAIN_SNOW` / `TXT_KEY_TERRAIN_ICE` (beside a separate `FEATURE_ICE`), `MISSION_AIRPATROL` / `TXT_KEY_MISSION_INTERCEPT`, `COMMERCE_ESPIONAGE` / `TXT_KEY_ESPIONAGE_CULTURE` | Type and text key name different concepts, so one can be mistaken for another asset | Kept; the displayed names are right |
| `GAMEOPTION_NO_FLIPPING_AFTER_CONQUEST` / `TXT_KEY_GAME_OPTION_FLIPPING_AFTER_CONQUEST` | The key drops the `NO` of its Type; its English reads "No City Flipping after Conquest" | Kept |
| `CONTROL_NEXTUNIT` and `CONTROL_PREVUNIT` both use `TXT_KEY_ACTION_PREVIOUS_PLOT_UNIT_HELP`; `EVENT_CYCLONE_*` and `EVENT_MONSOON_*` use `TXT_KEY_EVENT_HURRICANE_*` | One key shared by different entries, like the memory rows above | Kept |

A 2026-11-05 count found 143 XML entries whose `<Description>` key does not match their `<Type>`, out of 1,764 such pairs; 134 already exist in AdvCiv 1.14 and the rest come from BtS files SAS now ships or follow normal patterns such as the `_DESC` civilization keys. New SAS assets match their keys.

A CI check enforcing matching names was considered but not added: it would fail on those inherited pairs, and fixing them would mean renaming inherited IDs or text keys, which the restoration decisions above avoid for compatibility. The table lists the pairs most likely to mislead instead.

## Companion completeness finding: True Starts

The companion-name sweep behind this audit also exposed a separate completeness defect: SAS had added two playable civilizations and three leaders without adding the corresponding True Starts records.

This is not itself an asset rename, but it is directly relevant to the audit's purpose because enumerating companion namespaces is what made the missing data obvious.

The same evidence had independently been recorded as [KI#936](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-936).

| SAS object added outside inherited AdvCiv | Missing companion found on 2026-11-04 | Runtime consequence before fix | Resolution |
| --- | --- | --- | --- |
| `CIVILIZATION_IRELAND` | `TRU_IRELAND` / `TruCivInfo` | Could not be selected for a Random True Starts slot; fixed Ireland plus another Random player entered an unsafe missing-civ-info dereference path | Added minimal required Dublin coordinates; optional climate/terrain targets remain at True Starts defaults |
| `CIVILIZATION_KINGDOM_OF_BENIN` | `TRU_KINGDOM_OF_BENIN` / `TruCivInfo` | Could not be selected for a Random True Starts slot; fixed Benin plus another Random player entered the same unsafe path | Added minimal required Benin City coordinates; optional climate/terrain targets remain at True Starts defaults |
| `LEADER_EWUARE` | `TRU_EWUARE` / `TruLeaderInfo` | Runtime tolerated the omission but the leader silently lacked True Starts chronology/bias data | Added with start year 1440 from the SAS Civilopedia chronology |
| `LEADER_GRACE_OMALLEY` | `TRU_GRACE_OMALLEY` / `TruLeaderInfo` | Same optional leader-data loss | Added without `iStartOfReign`; the exact start of leadership is not established by the current source text |
| `LEADER_MICHAEL_COLLINS` | `TRU_MICHAEL_COLLINS` / `TruLeaderInfo` | Same optional leader-data loss | Added with start year 1922 from the SAS Civilopedia chronology |
| `BONUS_CAMEL` | No `TRU_CAMEL` row | **No completeness defect.** `TruBonusInfo` is intentionally sparse; no row means no resource-specific True Starts bias | Left absent unless future gameplay tuning gives Camel an actual True Starts bias |

The fix added `.github/workflows/build/xml/true_starts_coverage.py`. Before the XML repair, that check failed on exactly the two missing playable civilizations and three missing playable-civilization leaders. After the repair it passes.

The maintained invariant is intentionally narrower than "every asset has a `TRU_*` companion": every playable/AI-playable civilization must have exactly one `TruCivInfo`; SAS also maintains one `TruLeaderInfo` per leader belonging to a playable civilization; supplied `TruBonusInfo` rows must be valid and unique but bonus coverage is optional.

This distinction prevents future maintenance or an LLM from "fixing" intentionally sparse bonus data merely for naming symmetry.

Runtime confirmation on 2026-11-04 used True Starts with fixed Ewuare/Kingdom of Benin and fixed Grace O'Malley/Ireland plus 14 Random players. The game reached `GAME_START` and serialized the turn-0 start checkpoint, directly exercising the previously unsafe mixed fixed-new-civilization + Random-player path.

The CI separately verifies that the two civilizations are also present in the Random candidate data.

## Bonuses

The six resource rows below are historically evidenced rename lineages. The final Movies/Camel row is included because the raw Type-set difference can look like a rename even though history shows that it was a replacement with different content.

| Base AdvCiv/BtS machine ID | SAS 2025 machine ID | Main renamed companions | Practical commit/date | Why / nature of change | Later state |
| --- | --- | --- | --- | --- | --- |
| `BONUS_GEMS` | `BONUS_GEMSTONES` | `ART_DEF_BONUS_GEMS -> ...GEMSTONES`; `TRU_GEMS -> TRU_GEMSTONES`; description/pedia text keys | 4767, `f551d27b34`, 2025-05-21 | "Gemstones" was considered more accurate and understandable than "Gems" | **Machine family restored to `GEMS` on 2026-11-04; display remains Gemstones** |
| `BONUS_IVORY` | `BONUS_ELEPHANTS` | `ART_DEF_BONUS_IVORY -> ...ELEPHANTS`; `TRU_IVORY -> TRU_ELEPHANTS`; description/pedia text keys | 4768, `ea75187aa4`, 2025-05-21 | Generalized the displayed Elephants naming to the XML asset family; names the animal rather than processed ivory | **Machine family restored to `IVORY` on 2026-11-04; display remains Elephants** |
| `BONUS_WINE` | `BONUS_GRAPES` | `ART_DEF_BONUS_WINE -> ...GRAPES`; `TRU_WINE -> TRU_GRAPES`; description/pedia text keys | 4769, `10b06b59d6`, 2025-05-21 | Names the raw map resource rather than one product; same change also removed Winery and redesigned improvement behavior | **Machine family restored to `WINE` on 2026-11-04; Grapes/Plantation gameplay remains** |
| `BONUS_CORN` | `BONUS_MAIZE` | `ART_DEF_BONUS_CORN -> ...MAIZE`; `TRU_CORN -> TRU_MAIZE`; description/pedia text keys | 4770, `86d9c24298`, 2025-05-22 | Terminology rename; no more specific rationale is preserved in the commit than the recorded naming choice | **Machine family restored to `CORN` on 2026-11-04; display remains Maize** |
| `BONUS_CLAM` | `BONUS_MOLLUSCS` | `ART_DEF_BONUS_CLAM -> ...MOLLUSCS`; `TRU_CLAM -> TRU_MOLLUSCS`; description/pedia text keys | 4776, `b841968682`, 2025-05-24 | Broadens the resource from one shellfish to a wider mollusc category, alongside distribution changes | **Machine family restored to `CLAM` on 2026-11-04; display remains Molluscs** |
| `BONUS_COW` | `BONUS_CATTLE` | `ART_DEF_BONUS_COW -> ...CATTLE`; `TRU_COW -> TRU_CATTLE`; description/pedia text keys; `COWS` audio IDs became `CATTLE` | 4776, `b841968682`, 2025-05-24 | Naming choice made during the broader resource rework; no separate detailed rationale is preserved | **Machine family and inherited `COWS` audio IDs restored on 2026-11-04; display remains Cattle** |
| `BONUS_MOVIES` | `BONUS_CAMEL` | **No rename companion relationship** | 4832, `44cb420869`, 2025-06-14 | Movies was removed; Camel was added as a different resource with camel unit lines | **Replacement/new content, not a rename** |

### 2026-11-04 machine-ID restoration

The six inherited bonus machine families above were restored in place on 2026-11-04 while retaining the SAS player-facing names and gameplay payloads. This was an intentional reversal of the **machine-identifier** part of the 2025 naming cleanup, not a reversal of the resource redesigns themselves.

Bonuses are unusually compatibility-sensitive because map generation, imported `PrivateMaps` scripts, WorldBuilder/scenario data and other mod content commonly refer to `BONUS_*` identifiers directly. These six resources remain direct descendants of inherited AdvCiv/BtS resource slots even where SAS changed their distribution, yields, Civilopedia text or improvement/building interactions.

Keeping different machine names therefore imposed a broad compatibility cost for comparatively little benefit: the clearer SAS terminology can live in `TXT_KEY_*` English text without forcing external map content to learn a new identifier.

This differs from many SAS buildings, units and technologies whose identity or gameplay role changed substantially enough that inherited machine names can be misleading or offer little interoperability value.

The restoration covers the applicable companion namespaces and consumers, including `BONUS_*`, `ART_DEF_BONUS_*`, `TRU_*`, `TXT_KEY_BONUS_*`, CustomDomAdv `HAS_BONUS_*`/`BONUS_*` entries, XML/Python references, PlotLSystem bonus selectors, map-script literals, and the inherited `COWS` audio IDs that had been renamed with Cattle.

Historical Git/changelog/source-analysis evidence retains the old SAS machine names because those names were correct for those historical states. See [`Deprecated/xml_asset_names.md`](/_1_AdvCiv-SAS/Docs/Deprecated/xml_asset_names.md) for the concise retired-SAS-to-current translation.

This improves map-script/scenario/mod interoperability but does **not** promise general old-save or pre-SAS scenario compatibility: AdvCiv-SAS has many other structural additions/removals and does not support save compatibility across arbitrary revisions.

In particular, `BONUS_WINE` still displays and plays as SAS Grapes, `BONUS_CORN` as Maize, `BONUS_CLAM` as Molluscs, `BONUS_COW` as Cattle, `BONUS_IVORY` as Elephants and `BONUS_GEMS` as Gemstones.

The detailed notes below preserve the original rename history and rationale.

### Gems to gemstones

Practical commit **4767**, `f551d27b34`, 2025-05-21.

Companion rename family:

- `BONUS_GEMS -> BONUS_GEMSTONES`
- `ART_DEF_BONUS_GEMS -> ART_DEF_BONUS_GEMSTONES`
- `TRU_GEMS -> TRU_GEMSTONES`
- `TXT_KEY_BONUS_GEMS -> TXT_KEY_BONUS_GEMSTONES`
- `TXT_KEY_BONUS_GEMS_PEDIA -> TXT_KEY_BONUS_GEMSTONES_PEDIA`
- Literal `BONUS_GEMS` references were correspondingly changed in building, event-trigger, corporation, improvement and CustomDomAdv data; the reviewed 2026-11-04 map scripts used `BONUS_GEMSTONES`.

The commit explicitly describes "Gemstones" as more accurate and understandable than "Gems" and also changed the resource button. Its historical note records that an initially missed `ART_DEF_BONUS_GEMS` companion caused a silent startup crash until the art-def Type was renamed too. This is a concrete example of why the companion family matters, not just the primary BonusInfo `<Type>`.

By 2026-11-04, SAS had also materially changed Gemstones distribution/terrain data after the inherited AdvCiv version. The rename history therefore does not imply that the SAS BonusInfo payload still matched AdvCiv. On 2026-11-04 only the machine family was restored to `BONUS_GEMS` / `ART_DEF_BONUS_GEMS` / `TRU_GEMS` / inherited text-key IDs; the Gemstones display and SAS payload remained.

### Ivory to elephants

Practical commit **4768**, `ea75187aa4`, 2025-05-21.

Companion rename family:

- `BONUS_IVORY -> BONUS_ELEPHANTS`
- `ART_DEF_BONUS_IVORY -> ART_DEF_BONUS_ELEPHANTS`
- `TRU_IVORY -> TRU_ELEPHANTS`
- `TXT_KEY_BONUS_IVORY -> TXT_KEY_BONUS_ELEPHANTS`
- `TXT_KEY_BONUS_IVORY_PEDIA -> TXT_KEY_BONUS_ELEPHANTS_PEDIA`
- Python random-event lookups, unit/building/improvement references and other XML `BonusType`/`BonusGift` references were updated with the main Type.

The commit says this generalized an earlier text-key-only "Elephants" rename to the XML asset family. Conceptually, SAS names the map resource after the animal rather than the processed material "Ivory."

This is naming-led, but later resource balance and unit requirements mean the SAS object payload is not simply the inherited block. On 2026-11-04 the machine family returned to `BONUS_IVORY` and inherited companions while the displayed resource remained Elephants.

### Wine to grapes

Practical commit **4769**, `10b06b59d6`, 2025-05-21.

Companion rename family:

- `BONUS_WINE -> BONUS_GRAPES`
- `ART_DEF_BONUS_WINE -> ART_DEF_BONUS_GRAPES`
- `TRU_WINE -> TRU_GRAPES`
- `TXT_KEY_BONUS_WINE -> TXT_KEY_BONUS_GRAPES`
- `TXT_KEY_BONUS_WINE_PEDIA -> TXT_KEY_BONUS_GRAPES_PEDIA`

This is **rename + redesign**, not merely an identifier cleanup. The same commit removed `IMPROVEMENT_WINERY`, `ART_DEF_IMPROVEMENT_WINERY` and `BUILD_WINERY`, moved Grapes to Farm-based improvement logic at that time, and reworked associated Grocer happiness/health behavior.

Grapes were later moved to `IMPROVEMENT_PLANTATION`; by the 2026-11-04 identifier restoration, Plantation was the current gameplay relationship.

The rationale distinguishes the raw map resource (grapes, which can be eaten or processed) from wine as a product and notes that not all wine is grape wine.

The identifier rename and the gameplay redesign are separate historical facts: changing only the machine identifier does not recreate the inherited Wine/Winery gameplay object. On 2026-11-04 the machine family returned to `BONUS_WINE`, but the player-facing resource remains Grapes and the SAS improvement/building redesign remains in force.

The same-day follow-up review also corrected stale Farm + `BONUS_WINE` PlotLSystem rules to the current Plantation relationship and added a relationship check so graphical rules follow the gameplay XML; KI#1074 records it with the remaining Farm-era leftovers in that file.

### Corn to maize

Practical commit **4770**, `86d9c24298`, 2025-05-22.

Companion rename family:

- `BONUS_CORN -> BONUS_MAIZE`
- `ART_DEF_BONUS_CORN -> ART_DEF_BONUS_MAIZE`
- `TRU_CORN -> TRU_MAIZE`
- `TXT_KEY_BONUS_CORN -> TXT_KEY_BONUS_MAIZE`
- `TXT_KEY_BONUS_CORN_PEDIA -> TXT_KEY_BONUS_MAIZE_PEDIA`

The historical commit explicitly records the rename but does not preserve a separate detailed rationale comparable with Grapes or Molluscs. This document therefore records the terminology change without inventing an unstated reason. On 2026-11-04 the machine family returned to `BONUS_CORN`; the displayed resource remains Maize.

### Clam to molluscs and cow to cattle

Practical commit **4776**, `b841968682`, 2025-05-24, as part of a broader resource-balance rework.

Molluscs companion family:

- `BONUS_CLAM -> BONUS_MOLLUSCS`
- `ART_DEF_BONUS_CLAM -> ART_DEF_BONUS_MOLLUSCS`
- `TRU_CLAM -> TRU_MOLLUSCS`
- `TXT_KEY_BONUS_CLAM -> TXT_KEY_BONUS_MOLLUSCS`
- `TXT_KEY_BONUS_CLAM_PEDIA -> TXT_KEY_BONUS_MOLLUSCS_PEDIA`

Cattle companion family:

- `BONUS_COW -> BONUS_CATTLE`
- `ART_DEF_BONUS_COW -> ART_DEF_BONUS_CATTLE`
- `TRU_COW -> TRU_CATTLE`
- `TXT_KEY_BONUS_COW -> TXT_KEY_BONUS_CATTLE`
- `TXT_KEY_BONUS_COW_PEDIA -> TXT_KEY_BONUS_CATTLE_PEDIA`

The Molluscs rationale is preserved in the XML/history: it intentionally broadens "Clam" to a more general resource category and uses that broader scope when adjusting where/how commonly it can appear.

The same commit also renamed Cow to Cattle, but no equally specific standalone rationale is preserved; it should simply be recorded as the naming choice made during that resource rework rather than reverse-engineering an explanation.

By 2026-11-04, both resources also had SAS-specific distribution/balance data, so the rename lineage should not be read as evidence that their payloads still matched inherited AdvCiv. On 2026-11-04 the machine families returned to `BONUS_CLAM` and `BONUS_COW` (including the inherited `COWS` audio IDs), while the displayed resources remain Molluscs and Cattle.

### Movies to camel is not a rename

Practical commit **4832**, `44cb420869`, 2025-06-14, added the Camel resource and camel unit lines and removed the old Hit Movies resource.

`BONUS_MOVIES -> BONUS_CAMEL` must **not** be entered into a rename table as though these were two names for the same asset. `BONUS_CAMEL` is new SAS content. The old BtS/AdvCiv Movies object was removed and its former place in the resource set was used while introducing a different concept.

The same distinction applies to companion IDs: there is no meaningful `ART_DEF_BONUS_MOVIES -> ART_DEF_BONUS_CAMEL`, `TXT_KEY_BONUS_MOVIES -> TXT_KEY_BONUS_CAMEL`, or similar rename relationship. They belong to different assets.

## Leaders

SAS made two direct inherited leader-family renames in May 2025, then restored both inherited machine families on 2026-11-04. The restoration follows the same compatibility principle as the bonus restoration: these remain the same inherited leader slots despite SAS personality, trait and Civilopedia changes, and the player-facing names never needed different machine IDs.

The benefit is less direct than for bonuses, which map scripts use directly. AdvCiv-SAS does not support scenarios, and its other changes can still make external content incompatible. But XML, WorldBuilder or True Starts data that names the inherited leader families becomes easier to adapt and compare.

| Base AdvCiv/BtS name | SAS name introduced in 2025 | Main renamed companions | Practical commit/date | Why / nature of original change | Later state on 2026-11-04 |
| --- | --- | --- | --- | --- | --- |
| `LEADER_CHINESE_LEADER` | `LEADER_MAO_ZEDONG` | Leader art, `TRU_*`, description/pedia text keys, diplomacy response keys | 4749, `a230337b9f`, 2025-05-11 | Replaced a placeholder-like machine name with the actual leader name | **Restored to `LEADER_CHINESE_LEADER`**; inherited `TXT_KEY_LEADER_CHINESE_LEADER` again supplies the displayed **Mao Zedong** name, while the SAS pedia/personality data remain |
| `LEADER_MONTEZUMA` | `LEADER_MOCTEZUMA` | Leader art, `TRU_*`, description/pedia text keys, diplomacy response keys, diplomacy audio IDs; related Montezuma Castle text key | 4743, `72338fcc2b`, 2025-05-08 | Spelling/name normalization | **Restored to `LEADER_MONTEZUMA`**; SAS overrides under the inherited text keys keep the displayed **Moctezuma II** spelling and updated pedia; the city name uses the inherited **Montezuma Castle** text again |

### `LEADER_CHINESE_LEADER -> LEADER_MAO_ZEDONG`

Practical commit **4749**, `a230337b9f`, 2025-05-11.

Companions include:

- `LEADER_CHINESE_LEADER -> LEADER_MAO_ZEDONG`
- `ART_DEF_LEADER_CHINESE_LEADER -> ART_DEF_LEADER_MAO_ZEDONG`
- `TRU_CHINESE_LEADER -> TRU_MAO_ZEDONG`
- `TXT_KEY_LEADER_CHINESE_LEADER -> TXT_KEY_LEADER_MAO_ZEDONG`
- `TXT_KEY_LEADER_CHINESE_LEADER_PEDIA -> TXT_KEY_LEADER_MAO_ZEDONG_PEDIA`
- Diplomacy response keys containing the old `LEADER_CHINESE_LEADER` component were renamed to the Mao Zedong family.
- The 2026-11-04 predumped Sevopedia leader data and other generated/reference data also keyed the SAS leader Type.

This was a clear naming-led change: the inherited placeholder-like machine identifier was replaced with the actual leader name. By 2026-11-04, Mao data also differed materially from AdvCiv in AI/personality and trait data, so the rename was not the only SAS-side difference.

On 2026-11-04 the machine family returned to `LEADER_CHINESE_LEADER`, including `ART_DEF_LEADER_CHINESE_LEADER`, `TRU_CHINESE_LEADER`, the inherited description/pedia key family and `AI_DIPLO_*_LEADER_CHINESE_LEADER_*` response keys.

The temporary SAS `TXT_KEY_LEADER_MAO_ZEDONG` description override was removed entirely because the inherited `TXT_KEY_LEADER_CHINESE_LEADER` already displays **Mao Zedong**; the expanded SAS Civilopedia remains under `TXT_KEY_LEADER_CHINESE_LEADER_PEDIA`. This makes external data that names the inherited leader easier to reuse, without reverting Mao's SAS gameplay or displayed identity.

### `LEADER_MONTEZUMA -> LEADER_MOCTEZUMA`

Practical commit **4743**, `72338fcc2b`, 2025-05-08.

Companions include:

- `LEADER_MONTEZUMA -> LEADER_MOCTEZUMA`
- `ART_DEF_LEADER_MONTEZUMA -> ART_DEF_LEADER_MOCTEZUMA`
- `TRU_MONTEZUMA -> TRU_MOCTEZUMA`
- `TXT_KEY_LEADER_MONTEZUMA -> TXT_KEY_LEADER_MOCTEZUMA`
- `TXT_KEY_LEADER_MONTEZUMA_PEDIA -> TXT_KEY_LEADER_MOCTEZUMA_PEDIA`
- `AI_DIPLO_*_LEADER_MONTEZUMA_* -> AI_DIPLO_*_LEADER_MOCTEZUMA_*` key families.

This was a spelling/name normalization. By 2026-11-04, the Moctezuma payload also differed materially from inherited AdvCiv data, including `iBuildUnitProb`, favorite civic and favorite religion.

On 2026-11-04 the machine family returned to `LEADER_MONTEZUMA`, including leader art, `TRU_MONTEZUMA`, `AI_DIPLO_*_LEADER_MONTEZUMA_*`, and the inherited `AS2D_DIPLO_MONTEZUMA_*` / `DIPLO_MONTEZUMA_*` audio IDs.

The description and pedia keys also returned to `TXT_KEY_LEADER_MONTEZUMA*`, but SAS keeps its English overrides so the player-facing leader remains **Moctezuma II** and the updated pedia is preserved.

`TXT_KEY_CITY_NAME_MONTEZUMA_CASTLE` was likewise restored, and its SAS override was removed so the inherited BtS text **Montezuma Castle** applies again. That is the real site's name: later settlers named the Arizona cliff dwelling (Montezuma Castle National Monument) after Moctezuma, so "Moctezuma Castle" was not a spelling correction.

The rename-only diplomacy text copies that had been needed for the temporary `MOCTEZUMA` key family were removed so the inherited text family can be used again.

As of 2026-11-04, `LEADER_EWUARE`, `LEADER_GRACE_OMALLEY` and `LEADER_MICHAEL_COLLINS` were new SAS content rather than inherited leader renames.

## Civilizations

| Base AdvCiv/BtS name | SAS name | Main renamed companions | Practical commit/date | Why / nature of change | Status on 2026-11-04 |
| --- | --- | --- | --- | --- | --- |
| `CIVILIZATION_VIKING` | `CIVILIZATION_SCANDINAVIA` | Civilization art; `TRU_VIKING -> TRU_SCANDINAVIA`; civ description/short/adjective/pedia keys; then-current Viking UU/UB naming | 4878, `632293eb54`, 2025-07-15 | Broadened the civilization identity from "Viking" to "Scandinavia" and renamed the associated civ-specific family | **Machine family restored to `VIKING` on 2026-11-05; display remains Scandinavia** |

Companions changed in the same naming family include:

- `ART_DEF_CIVILIZATION_VIKINGS -> ART_DEF_CIVILIZATION_SCANDINAVIA`
- `TRU_VIKING -> TRU_SCANDINAVIA`
- `TXT_KEY_CIV_VIKING_DESC -> TXT_KEY_CIV_SCANDINAVIA_DESC`
- `TXT_KEY_CIV_VIKING_SHORT_DESC -> TXT_KEY_CIV_SCANDINAVIA_SHORT_DESC`
- `TXT_KEY_CIV_VIKING_ADJECTIVE -> TXT_KEY_CIV_SCANDINAVIA_ADJECTIVE`
- The civilization pedia key was moved to the Scandinavia naming family.
- The then-current civ-specific building changed from `BUILDING_VIKING_TRADING_POST` to `BUILDING_SCANDINAVIA_TRADING_POST` with matching art/text companions.
- The unit changed from `UNIT_VIKING_BESERKER` to `UNIT_SCANDINAVIA_VIKING` with matching art/text companions.

Later SAS changes replaced the Scandinavian Trading Post with `BUILDING_SCANDINAVIA_CHIEFTAINS_HALL`. By 2026-11-04, `UNIT_SCANDINAVIA_VIKING` and the Chieftain's Hall were therefore current descendants of the renamed civilization namespace rather than the inherited Berserker/Trading Post payloads.

On 2026-11-05 the **machine-facing namespace** was restored consistently without undoing those SAS redesigns: `CIVILIZATION_VIKING`, `ART_DEF_CIVILIZATION_VIKINGS`, `TRU_VIKING`, the inherited civ text-key family, Viking audio/music IDs, `UNIT_VIKING_VIKING`, and `BUILDING_VIKING_CHIEFTAINS_HALL` now identify the current SAS civilization family.

- Player-facing names and gameplay remain **Scandinavia**, **Viking**, and **Chieftain's Hall**.
- The two SAS-created art directories likewise use `Viking_Viking` and `Viking_Chieftains_Hall`.

The civilization block intentionally remains in the S position. Custom Game follows the shown short name rather than the machine `<Type>` (KI#1073), so moving it to V would make the player-visible list less alphabetical.

By the restoration date, the Scandinavia civilization block also differed materially from inherited AdvCiv data beyond its Type: its UB, UU, initial civic and pedia/art references had changed. `CIVILIZATION_IRELAND` and `CIVILIZATION_KINGDOM_OF_BENIN` are new SAS civilizations rather than inherited civilization renames.

## Same-Type display and text-key renames

A machine-Type comparison alone misses changes where SAS deliberately kept the inherited gameplay `Type` but changed the displayed name or corrected a companion text-key identifier. These are naming changes too, and future maintenance should not rediscover or undo them merely because the primary Type stayed stable.

| Stable machine Type | AdvCiv/BtS wording / companion | SAS change | Practical commit/date | Why / nature of change | State on 2026-11-04 |
| --- | --- | --- | --- | --- | --- |
| `TERRAIN_SNOW` | Displayed as **Ice** through `TXT_KEY_TERRAIN_ICE` | **Ice Sheet** | 4648, `123e9fa97b`, 2025-04-11 | Distinguishes the land terrain from the separate water/plot feature after correcting the earlier assumption that the feature necessarily represented all ice | Active; Type and text-key ID unchanged |
| `FEATURE_ICE` | Displayed as **Ice** | **Ice Cap** | 4648, `123e9fa97b`, 2025-04-11 | Gives the feature a distinct geographic name from the Ice Sheet terrain | Active; Type unchanged |
| `LEADER_PACAL` | **Pacal** | **Pacal II** | 4461, `b4a0462f41`, 2025-04-01 | More specific regnal/historical name | Active |
| `LEADER_JUSTINIAN` | **Justinian** | **Justinian I** | 4462, `c471021670`, 2025-04-02 | Restored/normalized to the fuller BtS-equivalent historical name | Active |
| `LEADER_SURYAVARMAN` | **Suryavarman** | **Suryavarman II** | 4462, `c471021670`, 2025-04-02 | Restored/normalized to the fuller BtS-equivalent historical name | Active |
| `LEADER_ALEXANDER` | **Alexander** in AdvCiv | **Alexander III The Great**, later shortened to **Alexander III** | XML change present by 4650, `f624f9b8bb`, 2025-04-11; shortened 4860, `9fdf775f56`, 2025-07-07 | Added regnal specificity, then shortened the overlong form while keeping the disambiguating regnal number | Active as Alexander III |
| `LEADER_ISABELLA` | **Isabella** | **Isabella I** | 4650, `f624f9b8bb`, 2025-04-11 | Adds the regnal number for historical specificity | Active |
| `CIVILIZATION_AMERICA` | **American Empire** | **United States of America**; short form **United States** (**The USA** until 2026-11-04) | 4883, `f6b992b469`, 2025-07-21 | The source comment explicitly preferred the actual country name; "United States ... Empire" was both too long and semantically awkward | Active; civilization Type unchanged |
| `CIVILIZATION_NATIVE_AMERICA` | **Amerindian Empire** | **Native American Empire** | 4883, `f6b992b469`, 2025-07-21 | Reverted the displayed terminology to the clearer Native American wording | Active; civilization Type unchanged |
| `BUILDING_EGYPTIAN_OBELISK` | Reused generic description key `TXT_KEY_BUILDING_OBELISK` | Explicit `TXT_KEY_BUILDING_EGYPTIAN_OBELISK` companion | 4748, `bf00d29700`, 2025-05-10 | The generic building became Monument; the actual Egyptian Obelisk kept its BuildingInfo Type but received a non-ambiguous text-key family | Active; BuildingInfo Type unchanged |
| `UNIT_PERSIA_IMMORTAL` | Description/pedia companion typo family `TXT_KEY_UNIT_PERIA_IMMORTAL*` | `TXT_KEY_UNIT_PERSIA_IMMORTAL*` | 4841, `630168d5b8`, 2025-06-24 | Corrected `PERIA` -> `PERSIA`; the unit Type itself was already `UNIT_PERSIA_IMMORTAL` | Active; text-key fix only |
| `SPECIALIST_GREAT_PRIEST` | Displayed as **Great Prophet** | **Great Priest** | 4750, `701e2e3127`, 2025-05-11 | Deliberately distinguishes the settled specialist from the mobile `UNIT_GREAT_PROPHET`; see the Great-Person section | Active; SpecialistInfo Type unchanged |

There are also later name-length cleanups that should not be mistaken for restoration to untouched AdvCiv wording. For example, Alexander was present as **Alexander III The Great** during SAS history and was shortened to the current **Alexander III** in practical 4860 (`9fdf775f56`, 2025-07-07).

Similar temporary fullname experiments for some leaders were later shortened for UI/scoreboard fit. The important distinction is whether the primary machine Type changed, the player-facing text changed, or both.

## Religions

| Base AdvCiv/BtS naming family | SAS naming family | Main renamed companions | Practical commit/date | Why / nature of change | Status on 2026-11-04 |
| --- | --- | --- | --- | --- | --- |
| Taoism / `RELIGION_TAOISM` | Daoism / `RELIGION_DAOISM` | Religion Type; Taoist/Daoist temple, cathedral, monastery and shrine classes/Types; missionary class/Type/art; religion/building/unit text keys | 4740, `50e7c8749e`, 2025-05-07; art follow-up 4741, `d5ad78bc04` | Pinyin/modern naming change; the follow-up kept Daoism XML names while reverting to default Civ4 art files | **Active** |
| Confucianism | Removed; Paganism added separately | Separate religion/building/unit families | 4743, 2025-05-08 | Removal plus unrelated new religion, **not** a rename lineage | **Not a rename** |

Practical commit **4740**, `50e7c8749e`, 2025-05-07, renamed the inherited Taoism naming family to Daoism. Practical commit **4741**, `d5ad78bc04`, then reverted to default Civ4 art assets while intentionally retaining the renamed XML tags. That second step is useful evidence that machine IDs and actual art-file paths do not need to share the same wording.

The known companion family includes:

- `RELIGION_TAOISM -> RELIGION_DAOISM`
- `BUILDINGCLASS_TAOIST_TEMPLE -> BUILDINGCLASS_DAOIST_TEMPLE`
- `BUILDINGCLASS_TAOIST_CATHEDRAL -> BUILDINGCLASS_DAOIST_CATHEDRAL`
- `BUILDINGCLASS_TAOIST_MONASTERY -> BUILDINGCLASS_DAOIST_MONASTERY`
- `BUILDINGCLASS_TAOIST_SHRINE -> BUILDINGCLASS_DAOIST_SHRINE`
- `BUILDING_TAOIST_TEMPLE -> BUILDING_DAOIST_TEMPLE`
- `BUILDING_TAOIST_CATHEDRAL -> BUILDING_DAOIST_CATHEDRAL`
- `BUILDING_TAOIST_MONASTERY -> BUILDING_DAOIST_MONASTERY`
- `BUILDING_TAOIST_SHRINE -> BUILDING_DAOIST_SHRINE`
- `UNITCLASS_TAOIST_MISSIONARY -> UNITCLASS_DAOIST_MISSIONARY`
- `UNIT_TAOIST_MISSIONARY -> UNIT_DAOIST_MISSIONARY`
- `ART_DEF_UNIT_TAOIST_MISSIONARY -> ART_DEF_UNIT_DAOIST_MISSIONARY`
- `TXT_KEY_RELIGION_TAOISM* -> TXT_KEY_RELIGION_DAOISM*`
- `TXT_KEY_BUILDING_TAOIST_* -> TXT_KEY_BUILDING_DAOIST_*`
- `TXT_KEY_UNIT_TAOIST_MISSIONARY* -> TXT_KEY_UNIT_DAOIST_MISSIONARY*`

This was a broad naming-family change rather than a one-Type rename. The machine identifiers, building/unit companions and player-facing text are therefore best understood as one historical naming family.

The later removal of Confucianism and addition of Paganism in practical commit 4743 were **not** a `CONFUCIANISM -> PAGANISM` rename. They were separate removal/addition decisions.

## Units and Great People

Units are the clearest example of why a Type-set difference is not automatically a rename table. In the 2026-11-04 tree, some inherited `UNIT_*` IDs had been renamed, some had changed class/role, some had been replaced by unrelated civ-specific units, and some generic lines had been split into several SAS units.

### Great People: exact 4750 naming changes

Practical commit **4750**, `701e2e31279d7ab152f91b431a81c1bae9c22734`, **2025-05-11**, is the main Great-Person naming commit. Its own message says it renamed Great People `UNITAI`, `UNITCLASS`, `UNIT` and **partially specialist naming**.

The point was to remove an inherited inconsistency: Great Spy and Great General already used "Great" in some machine namespaces, while Prophet, Artist, Scientist, Merchant and Engineer often did not, even though their inherited player-facing unit names already said "Great ...".

| AdvCiv/BtS before | SAS change in 4750 | Companion changes / non-changes | Why it changed | Later state by 2026-11-04 |
| --- | --- | --- | --- | --- |
| `UNIT_PROPHET`; `UNITCLASS_PROPHET`; `UNITAI_PROPHET` | `UNIT_GREAT_PROPHET`; `UNITCLASS_GREAT_PROPHET`; `UNITAI_GREAT_PROPHET` | `ART_DEF_UNIT_PROPHET -> ART_DEF_UNIT_GREAT_PROPHET`; inherited unit description key was already `TXT_KEY_UNIT_GREAT_PROPHET`, so that key did **not** need renaming | Make the machine IDs agree with the inherited displayed unit name and with the explicit Great-Person family | Present |
| `UNIT_ARTIST`; `UNITCLASS_ARTIST`; `UNITAI_ARTIST` | `UNIT_GREAT_ARTIST`; `UNITCLASS_GREAT_ARTIST`; `UNITAI_GREAT_ARTIST` | `ART_DEF_UNIT_ARTIST -> ART_DEF_UNIT_GREAT_ARTIST`; `ART_DEF_UNIT_ARTIST_MODERN -> ART_DEF_UNIT_GREAT_ARTIST_MODERN`; Great Artist text keys were already Great-named | Same consistency cleanup | Present |
| `UNIT_SCIENTIST`; `UNITCLASS_SCIENTIST`; `UNITAI_SCIENTIST` | `UNIT_GREAT_SCIENTIST`; `UNITCLASS_GREAT_SCIENTIST`; `UNITAI_GREAT_SCIENTIST` | Corresponding unit art identifiers moved to `ART_DEF_UNIT_GREAT_SCIENTIST*`; inherited displayed name already identified the unit as Great Scientist | Same consistency cleanup | Present |
| `UNIT_MERCHANT`; `UNITCLASS_MERCHANT`; `UNITAI_MERCHANT` | `UNIT_GREAT_MERCHANT`; `UNITCLASS_GREAT_MERCHANT`; `UNITAI_GREAT_MERCHANT` | Corresponding art identifiers moved to the `ART_DEF_UNIT_GREAT_MERCHANT*` family; Great Merchant display key already existed | Same consistency cleanup; also removes confusing code/comment references where ordinary-sounding `UNITAI_MERCHANT` meant the Great Person | Present |
| `UNIT_ENGINEER`; `UNITCLASS_ENGINEER`; `UNITAI_ENGINEER` | `UNIT_GREAT_ENGINEER`; `UNITCLASS_GREAT_ENGINEER`; `UNITAI_GREAT_ENGINEER` | Corresponding art identifiers moved to `ART_DEF_UNIT_GREAT_ENGINEER*`; Great Engineer display key already existed | Same consistency cleanup | Present |
| Great General unit/class already had `GREAT_GENERAL` naming, but AI type was `UNITAI_GENERAL` | `UNITAI_GENERAL -> UNITAI_GREAT_GENERAL` | `UNIT_GREAT_GENERAL` and `UNITCLASS_GREAT_GENERAL` did not need this rename | Bring the AI enum into the same Great-Person naming pattern | Present |
| Great Spy already had `UNITAI_GREAT_SPY`; ordinary Spy separately used `UNITAI_SPY` | **No Great Spy rename** | Both AI types intentionally remain distinct | The commit explicitly warns not to collapse the normal Spy and Great Spy AI types | Unchanged distinction retained |
| Machine ID already `SPECIALIST_GREAT_PRIEST`, but inherited player-facing text for `TXT_KEY_SPECIALIST_GREAT_PRIEST` said **Great Prophet** | SAS overrides the text as **Great Priest**; the `SPECIALIST_GREAT_PRIEST` Type itself is unchanged | Mobile unit remains `UNIT_GREAT_PROPHET`; ordinary `SPECIALIST_PRIEST` remains ordinary Priest | Deliberately distinguish the unique/mobile **Prophet** from the settled city specialist. The historical comment reasons that a city can have a continuing/successive Great Priest role, while the Great Prophet remains the unique Great-Person unit; it also makes the settled specialist line up with ordinary Priest terminology | Present |
| Ordinary specialist IDs such as `SPECIALIST_SCIENTIST`, `SPECIALIST_ARTIST`, `SPECIALIST_MERCHANT`, `SPECIALIST_ENGINEER`, `SPECIALIST_PRIEST` | **No rename** | Normal specialists stay non-Great machine types | Commit explicitly says these represent ordinary specialists, not Great People | Unchanged |

This commit therefore made **three different kinds of naming change at once**: unit/class Types gained `GREAT_`, UnitAI enums gained `GREAT_`, and one already-Great specialist Type kept its machine ID but changed its displayed English name from Great Prophet to Great Priest. Future cleanup should not flatten these into one generic rename rule.

### Unit-combat taxonomy splits

The inherited AdvCiv unit XML still used the standard BtS combat families `UNITCOMBAT_ARCHER`, `UNITCOMBAT_AIR`, `UNITCOMBAT_MOUNTED` and `UNITCOMBAT_MELEE`. SAS deliberately replaced each broad family with a finer taxonomy.

These changes are important to this history because a raw Type-set diff otherwise looks like several unrelated deletions/additions or, worse, suggests a false one-to-one rename.

The split commits were cross-cutting changes: besides `CIV4UnitCombatInfos.xml` and `CIV4UnitInfos.xml`, they updated promotion eligibility/counters, traits/buildings/events, feat/UI code, BUG unit naming and in some cases DLL enums. Future cleanup should therefore treat the combat Type and its consumers as one structural family.

| Inherited AdvCiv/BtS combat family | SAS taxonomy change | Practical commit/date | Why the family was split | 2026-11-04 members / important exceptions |
| --- | --- | --- | --- | --- |
| `UNITCOMBAT_ARCHER` | `UNITCOMBAT_ARCHER_BOW_SHORT`, then `...BOW_LONG`, then `...CROSSBOW` | 4602 `280ba37fb9`, 2025-04-08; 4605 `4f283385cc`, 2025-04-08; 4606 `8a03454195`, 2025-04-09 | The imported BtS UnitCombat file was explicitly brought into SAS so archery could be represented as **short bow / long bow / crossbow** rather than one generic Archer family. This lets promotions, traits, buildings, events, counters and UI/feat handling target the distinct weapon families instead of treating all archers identically. | **Short bow:** Archer, Mali Skirmisher, Babylon Bowman. **Long bow:** Longbowman, English Yeoman Archer. **Crossbow:** Crossbowman, Chinese Zhuge Nu, Benin Disciplined Crossbowman. |
| `UNITCOMBAT_AIR` | first renamed to `UNITCOMBAT_AIR_BOMBER`, then new sibling `UNITCOMBAT_AIR_FIGHTER` added | 4616 `9b2a569e43`, 2025-04-09; 4618 `d67de51165`, 2025-04-09 | The first commit alone looks like a rename, but the next commit establishes the actual design: inherited generic Air was split so bomber and fighter aircraft could have different promotion/counter behavior. | **Bomber:** Bomber, Stealth Bomber. **Fighter:** Fighter, Jet Fighter. Airship later left the air-combat taxonomy entirely and became Recon. |
| `UNITCOMBAT_MOUNTED` | `UNITCOMBAT_MOUNTED_MELEE` + `UNITCOMBAT_MOUNTED_RANGED` | 4866 `b58da78c99`, 2025-07-09 | Source comment records the gameplay reason directly: split mounted units so **Pikemen are not generically strong against Cuirassiers or Horse Archers**. The distinction supports different spear/pike counters and different terrain/promotion behavior for contact cavalry versus ranged/skirmishing cavalry. | **Melee:** Chariot, Egyptian War Chariot, Numidian Cavalry, War Elephant, Horse Knight, Cataphract, Khishigten, Camel Knight. **Ranged:** Horse Archer, Camel Archer, Ballista Elephant, Hajjan, Horse Cuirassier, Conquistador, Camel Cuirassier, Dragoon, Cossack, German Hussar. Persian Immortal is a special later reclassification to `MELEE_POLEARM`, not either mounted family. |
| `UNITCOMBAT_MELEE` | `UNITCOMBAT_MELEE_POLEARM` + `UNITCOMBAT_MELEE_SHOCK` | 5019 `1733842bdd`, 2025-09-28 | The commit records the intended counter graph: axes/shock troops should beat polearms without a bronze Axeman automatically hard-countering later swords/pikes; Crossbows should remain strong against close-combat `MELEE_SHOCK` units but not against armored/defensive polearms such as Pikemen. The split also creates room for visually/role-appropriate exceptions such as the lance-bearing Persian Immortal. | **Polearm:** Persian Immortal, Spearman, Zulu Impi, Greek Hoplite, Pikeman. **Shock:** Warrior, Axeman, Sumerian Vulture, Native American Dog Soldier, Aztec Jaguar, Swordsman, Celtic Gallic Warrior, Roman Legionary, Incan Quechua, Maceman, Japanese Samurai, Scandinavian Viking. |

This taxonomy is also reflected in promotion and counter naming. For example, the later mechanics-descriptive promotion family can target `COUNTER_MOUNTED` or specific combat families without recreating the inherited all-mounted/all-melee assumptions.

Conversely, `UNITCOMBAT_GUN`, `ARMOR`, `SIEGE`, `HELICOPTER`, `NAVAL` and `RECON` remain inherited families rather than analogous global splits, even though individual units can move between them.

### Same-Type unit class and role reclassifications

A second systematic comparison looked at units whose **`UNIT_*` Type survived unchanged** between AdvCiv 1.14 and the 2026-11-04 SAS tree but whose `Class`, `Combat`, domain or role changed. These are easy to miss in a Type-only audit and are not name aliases; they record that SAS changed what inherited object the same unit identifier represents.

| Stable unit Type | AdvCiv classification | SAS classification / main evidence | When / why |
| --- | --- | --- | --- |
| `UNIT_AIRSHIP` | `UNITCOMBAT_AIR`, `DOMAIN_AIR`, `UNITAI_ATTACK_AIR` | `UNITCOMBAT_RECON`, `DOMAIN_LAND`, later `UNITAI_EXPLORE` | 4911 `92fc29e26e`, 2025-07-27 reworked Airship into a recon/observer unit rather than an ordinary combat aircraft; later cleanup made the default AI match that role. |
| `UNIT_MECHANIZED_INFANTRY` | `UNITCOMBAT_GUN` | `UNITCOMBAT_ARMOR` | Present by practical 4970 `e2dbc313c7`, 2025-09-01, with an explicit `was UNITCOMBAT_GUN` source comment; SAS classifies the mechanized unit with armored forces rather than ordinary gun infantry. |
| `UNIT_PERSIA_IMMORTAL` | `UNITCLASS_CHARIOT`, `UNITCOMBAT_MOUNTED` | `UNITCLASS_SWORDSMAN`, then `UNITCOMBAT_MELEE_POLEARM` | 4841 `630168d5b8`, 2025-06-24 reworked the Immortal from Civ4's Chariot basis to a Swordsman basis for historical/timeline fit; the 5019 melee split then classified the lance-bearing model as Polearm. |
| `UNIT_BABYLON_BOWMAN` | `UNITCLASS_ARCHER`, `UNITCOMBAT_ARCHER` | `UNITCLASS_LONGBOWMAN`, `UNITCOMBAT_ARCHER_BOW_SHORT` | Already present in the military-overhaul reapply by practical 4521, 2025-04-04; the later archer taxonomy then made the weapon family explicit. SAS uses Bowman in the Construction/Longbow slot while keeping it a short-bow combat type. |
| `UNIT_MALI_SKIRMISHER` | `UNITCLASS_ARCHER`, `UNITCOMBAT_ARCHER` | `UNITCLASS_LONGBOWMAN`, `UNITCOMBAT_ARCHER_BOW_SHORT` | Same military-overhaul lineage as Babylon Bowman; the unit was moved from the ancient Archer slot to the later Longbow slot while retaining a short-bow combat identity. |
| `UNIT_KOREAN_HWACHA` | `UNITCLASS_CATAPULT` | `UNITCLASS_CANNON` | 4877 `67a01372c8`, 2025-07-15 explicitly reworked Hwacha as a Cannon-based unit. |
| `UNIT_RUSSIA_COSSACK` | `UNITCLASS_CAVALRY`, `UNITCOMBAT_MOUNTED` | `UNITCLASS_DRAGOON`, `UNITCOMBAT_MOUNTED_RANGED` | The Mounted split supplied the ranged combat family; 5119 `47c2913350`, 2025-11-17 then replaced generic Cavalry with Dragoon and moved Cossack into that intended mobile-gunpowder slot. |
| `UNIT_SPANISH_CONQUISTADOR` | `UNITCLASS_CUIRASSIER`, `UNITCOMBAT_MOUNTED` | `UNITCLASS_HORSE_CUIRASSIER`, `UNITCOMBAT_MOUNTED_RANGED` | 4858 `601d40d995`, 2025-07-04 introduced the explicit `HORSE_` class naming; 4866 then split mounted combat and classified Cuirassier-style units as ranged. |
| `UNIT_BYZANTINE_CATAPHRACT` | `UNITCLASS_KNIGHT`, `UNITCOMBAT_MOUNTED` | `UNITCLASS_HORSE_KNIGHT`, `UNITCOMBAT_MOUNTED_MELEE` | 4858 renamed the generic horse Knight class to distinguish it from Camel Knight; 4866 then placed the Cataphract in mounted melee. |
| `UNIT_AZTEC_JAGUAR` | `UNITCLASS_SWORDSMAN`, `UNITCOMBAT_MELEE` | `UNITCLASS_AXEMAN`, `UNITCOMBAT_MELEE_SHOCK` | 4894 `0c8c5d8906`, 2025-07-23 explicitly moved Jaguar to the earlier Axeman role to strengthen the Aztec early-aggression window; the later melee split classified that role as Shock. |
| `UNIT_INCAN_QUECHUA` | `UNITCLASS_WARRIOR`, `UNITCOMBAT_MELEE` | `UNITCLASS_SWORDSMAN`, `UNITCOMBAT_MELEE_SHOCK` | 4983 `2a56f33057`, 2025-09-04 explicitly reworked Quechua as a Swordsman-based unit; the later melee split classified Swordsman-family units as Shock. |

The current civ-specific unit roster and exact stat changes are maintained in [`README_Assets_Rebalancing.md#civ-specific-units-rework`](/_1_AdvCiv-SAS/Docs/README_Assets_Rebalancing.md#civ-specific-units-rework). The table here deliberately records only the **structural lineage** needed to understand why inherited class/combat relationships no longer match SAS.

The same automated comparison also finds ordinary `DefaultUnitAI` changes for surviving units. Those are not listed here unless they accompany an identity/taxonomy change (for example Airship), because changing a unit's preferred AI role is balance/behavior tuning rather than asset naming. `UNITAI_*` **Type renames** themselves remain in scope and are documented in the Great-Person section.

### Naming-led unit changes

The following have a clear historical rename lineage. "Naming-led" here does not promise unchanged gameplay data.

| AdvCiv/BtS before | SAS change | Practical commit/date | Why recorded in history | Main companions / later state |
| --- | --- | --- | --- | --- |
| `UNIT_ARABIA_CAMELARCHER` | `UNIT_ARABIA_HAJJAN` | 4841, `630168d5b8`, 2025-06-24 | Explicit rename to the more distinctive/historically grounded Hajjan term, accompanied by a unit redesign | Art/text companions renamed; **rename + redesign**, not a payload-preserving alias |
| `UNIT_KNIGHT` | `UNIT_HORSE_KNIGHT` | 4858, `601d40d995`, 2025-07-04 | Makes the horse branch explicit after Camel Knight was added | `UNITCLASS_KNIGHT -> UNITCLASS_HORSE_KNIGHT`; horse-specific art identifiers followed; **line split/generalization** |
| `UNIT_CUIRASSIER` | `UNIT_HORSE_CUIRASSIER` | 4858, `601d40d995`, 2025-07-04 | Same reason as Horse Knight: distinguish the horse branch from Camel Cuirassier | `UNITCLASS_CUIRASSIER -> UNITCLASS_HORSE_CUIRASSIER`; **line split/generalization** |
| `UNIT_MARINE` | `UNIT_MODERN_INFANTRY` | 4871, `378e9fd759`, 2025-07-11 | Explicit unit/class rename while refactoring the modern infantry line | `UNITCLASS_MARINE -> UNITCLASS_MODERN_INFANTRY`; art/text companions changed; gameplay role also changed |
| `UNIT_GREEK_PHALANX` | `UNIT_GREEK_HOPLITE` | 4878, `632293eb54`, 2025-07-15 | Direct asset rename; the commit cites a Hoplite historical reference. No more specific separate rationale is preserved | `ART_DEF_UNIT_GREEK_PHALANX -> ART_DEF_UNIT_GREEK_HOPLITE`; unit description/pedia keys moved likewise; SAS later changed balance/class data separately |
| `UNIT_ROME_PRAETORIAN` | `UNIT_ROMAN_LEGIONARY` | 4878, `632293eb54`, 2025-07-15 | Direct asset rename to Legionary; commit does not preserve a more detailed standalone rationale | Art + unit description/pedia keys renamed with it |
| `UNIT_VIKING_BESERKER` | `UNIT_SCANDINAVIA_VIKING` | 4878, `632293eb54`, 2025-07-15 | Coupled to `VIKING -> SCANDINAVIA`; historical note explicitly distinguishes "Viking" as an activity/profession from Norse/Scandinavian identity, so the civilization became Scandinavia while this UU became the Viking | The redesigned SAS Viking remains, but its 2026-11-05 machine namespace is `UNIT_VIKING_VIKING` with matching art/text companions |
| `UNIT_MODERN_ARMOR` | `UNIT_MODERN_TANK` | 4909, `b2560ac6b6`, 2025-07-27 | Naming cleanup to Tank terminology; no more specific rationale preserved here | `UNITCLASS_MODERN_ARMOR -> UNITCLASS_MODERN_TANK`; art + text keys renamed |
| `UNIT_MOBILE_ARTILLERY` | `UNIT_SELF_PROPELLED_ARTILLERY` | 4910, `eba1162c66`, 2025-07-27 | More specific artillery terminology; no more detailed standalone rationale preserved here | Unit class, art and text keys renamed |
| `UNIT_ARTILLERY` | `UNIT_MODERN_ARTILLERY`, later `UNIT_FIELD_GUN` | 4910; then 5117, `44aca208a6`, 2025-11-16 | The later Field Gun change explicitly says "modern" was a poor fit because the unit represented roughly WWI / slightly earlier timing, unlike SAS units labeled Modern | Class/art/text followed the intermediate and later names; `MODERN_ARTILLERY` became superseded |
| `UNIT_AT_INFANTRY` | `UNIT_BAZOOKA` | 4957, `fe58e13463`, 2025-08-24 | Explicit rename to the weapon represented by the redesigned anti-tank infantry unit | `UNITCLASS_AT_INFANTRY -> UNITCLASS_BAZOOKA`; description/pedia companions changed; balance was also adjusted |
| `UNIT_MONGOL_KESHIK` | `UNIT_MONGOL_KHISHIGTEN` | 5024, `93f2d43f9f`, 2025-10-01 | Historical naming + redesign: commit says Khishigten was considered more accurate and moved the UU to Horse Knight timing for stronger medieval fit | Art, build audio and text renamed; class/role also changed, so this is rename + redesign |
| `UNIT_EGYPT_WARCHARIOT` | `UNIT_EGYPTIAN_WAR_CHARIOT` | 5037, `a4255a54e6`, 2025-10-06 | Naming normalization; no separate detailed rationale preserved | Art + description/pedia keys renamed; Chariot class retained |
| `UNIT_CHINA_CHOKONU` | `UNIT_CHINA_ZHUGE_NU` | 5118, `c4d71d146c`, 2025-11-16 | Commit explicitly records Cho-Ko-Nu as non-standard/incorrect Wade-Giles romanization and Zhuge Nu as modern pinyin | Art, build audio and text keys renamed; still present as of review |

These rows preserve direct naming lineages only. They should not be read as evidence that the 2026-11-04 unit payloads or civ-specific unit roster still matched inherited AdvCiv.

### Unit replacements and splits

These are not represented as simple old-name/new-name pairs because the underlying unit identity or role changed:

- `UNIT_GERMAN_PANZER -> UNIT_GERMAN_HUSSAR` (4843, 2025-06-25): replacement in a different unit role/era.
- `UNIT_NETHERLANDS_OOSTINDIEVAARDER ->` Dutch/Netherlands Swift Worker (4849, 2025-06-27): naval UU replaced by a Worker-based UU.
- `UNIT_AMERICAN_NAVY_SEAL -> UNIT_USA_PATRIOT` (4850, 2025-06-27): replacement with a Rifleman-based UU.
- `UNIT_ENGLISH_REDCOAT -> UNIT_ENGLISH_YEOMAN_ARCHER` (5025, 2025-10-02): replacement in a different class/era.
- `UNIT_HOLY_ROMAN_LANDSKNECHT -> UNIT_HOLY_ROMAN_HOUFNICE` (5049, 2025-10-09): replacement in a different combat role.
- `UNIT_CAVALRY -> UNIT_DRAGOON` (5119, 2025-11-17): explicit replacement/rework.
- `UNIT_PORTUGAL_CARRACK -> UNIT_PORTUGAL_CACADOR` and `UNIT_MAYA_HOLKAN -> UNIT_MAYA_QUICK_WORKER` (6121, 2026-08-17): explicit civ-specific role replacements.
- `UNIT_CARAVEL`, `UNIT_SUBMARINE` and `UNIT_STEALTH_DESTROYER` (with their inherited UnitClass companions) were removed during naval/modern unit-tree redesign; no one-to-one successor is asserted.
- `UNIT_CONFUCIAN_MISSIONARY` / `UNITCLASS_CONFUCIAN_MISSIONARY` were removed with Confucianism; the Pagan missionary is separate new religion content, not a direct rename.

## Buildings

Building differences likewise mix clear naming cleanups with entirely new civ-specific building designs.

### Naming-led building changes

| AdvCiv/BtS before | SAS change | Practical commit/date | Why it changed | Main companion changes |
| --- | --- | --- | --- | --- |
| `BUILDING_OBELISK` | `BUILDING_MONUMENT` | 4748, `bf00d29700`, 2025-05-10 | Untangled a namespace collision where the generic **Monument** was internally called Obelisk while Egypt's actual **Obelisk** reused part of that same naming family | Building/class/art/audio/reference families moved to Monument; the Egyptian UB retained `BUILDING_EGYPTIAN_OBELISK` but gained an explicit Egyptian description key; see the detailed namespace table below |
| `BUILDING_GREAT_PALACE` | `BUILDING_FORBIDDEN_PALACE` | 4749, `a230337b9f`, 2025-05-11 | Machine ID changed to match the actual displayed wonder name | Building class, art, description and pedia keys all moved from `GREAT_PALACE` to `FORBIDDEN_PALACE` |
| `BUILDING_NATIONAL_SECURITY` | `BUILDING_SECURITY_BUREAU` | 4750, `701e2e3127`, 2025-05-11 | Historical comment says "National Security" sounded like a national-wonder concept; "Security Bureau" was clearer for the building | Building class, art, description and pedia keys renamed |
| `BUILDING_GREAT_DAM` | `BUILDING_THREE_GORGES_DAM` | 4764, `e82115dc5a`, 2025-05-21 | Machine ID changed to the specific wonder name; movie naming was already associated with Three Gorges Dam | Building class, art, description and pedia keys renamed |
| `BUILDING_CHICHEN_ITZA` | `BUILDING_TEMPLE_OF_KUKULCAN` | 4985, `b9e253a3ce`, 2025-09-04 | Renamed from the archaeological site/city name to the represented temple itself | Building class, building art, movie art, description/pedia and `_NA` text keys renamed |

These rows have direct historical naming lineages. As with the other families, that does not imply that their 2026-11-04 building payloads were otherwise identical to inherited AdvCiv/BtS.

#### Monument / Obelisk namespace cleanup

See [Clearest inherited example: Monument / Obelisk](#clearest-inherited-example-monument--obelisk) for the full field-by-field history of this cleanup.

### Building replacements and redesigns

The following inherited building disappearances are **not** interpreted as simple renames. They are recorded explicitly because many changed building class, era or gameplay role at the same time:

| AdvCiv/BtS inherited asset | SAS lineage / successor | Practical commit/date | Why this is not treated as a simple rename |
| --- | --- | --- | --- |
| `BUILDING_SISTINE_CHAPEL` | `BUILDING_NATYA_SHASTRA` | 4831, 2025-06-11 | Explicit world-wonder replacement/rework with a different cultural/historical identity |
| `BUILDING_JAPANESE_SHALE_PLANT` | `BUILDING_JAPAN_DOUJOU` | 4882, 2025-07-18 | Civ-specific building replaced into a different building class and role |
| `BUILDING_INCAN_TERRACE` | `BUILDING_INCAN_QULLQA` | 4883, 2025-07-21 | Civ-specific building redesign lineage, not merely terminology |
| `BUILDING_KOREAN_SEOWON` | `BUILDING_KOREAN_GYEONGDANG` | 5467, 2026-02-19 | Replaced with a Library-based UB and new gameplay identity |
| `BUILDING_CHINESE_PAVILLION` | `BUILDING_CHINESE_CHANGPINGCANG` | 5468, 2026-02-20 | Replaced with a Market-based UB rather than preserving the inherited building identity |
| `BUILDING_CELTIC_DUN` | `BUILDING_CELTIC_LA_TENE_SMITHY` | 5471, 2026-02-20 | Replacement/rework into a different building concept |
| `BUILDING_ETHIOPIAN_STELE` | `BUILDING_ETHIOPIAN_METSEHAF_BET` | 5473, 2026-02-20 | Replacement/rework rather than machine-name cleanup |
| `BUILDING_KHMER_BARAY` | `BUILDING_KHMER_HALL_OF_DANCERS` | 6098, 2026-08-10 | Explicit class/role replacement |
| `BUILDING_SPANISH_CITADEL` | `BUILDING_SPANISH_LONJA` | 6098, 2026-08-10 | Explicit class/role replacement |
| `BUILDING_AMERICAN_MALL` | `BUILDING_AMERICAN_FEDERAL_COURTHOUSE` | 6099, 2026-08-10 | Replaced from the inherited Mall identity into a Courthouse-based civ building |
| `BUILDING_NATIVE_AMERICA_TOTEM` | `BUILDING_NATIVE_AMERICA_SOLDIERS_LODGE` | 6099, 2026-08-10 | Replaced from the Monument class into a Jail/espionage-focused civ building |
| `BUILDING_ARABIAN_MADRASSA` | `BUILDING_ARABIAN_FURUSIYYA_MAYDAN` | 6113, 2026-08-14 | Replaced with a different class/role during the major civ-building redesign |
| `BUILDING_CARTHAGE_COTHON` | `BUILDING_CARTHAGE_PUNIC_AGORA` | 6113, 2026-08-14 | Port-based Cothon replaced by a Grocer-based commercial/military-expansion identity |
| `BUILDING_GERMAN_ASSEMBLY_PLANT` | `BUILDING_GERMAN_LONGHOUSE -> BUILDING_GERMAN_ZUNFTHAUS` | 4822, `3b4013f45e`, 2025-06-08 -> 6113, 2026-08-14 | Assembly Plant was first removed in favor of a Granary-based Longhouse; that SAS intermediate was later replaced by a Forge-based craft/manufacturing identity |
| `BUILDING_NETHERLANDS_DIKE` | `BUILDING_NETHERLANDS_BEURS` | 6113, 2026-08-14 | Geography-dependent Levee replacement became a Bank/trade-focused identity |
| `BUILDING_PORTUGAL_FEITORIA` | `BUILDING_PORTUGAL_PEIXARIA` | 6113, 2026-08-14 | Custom House/Feitoria lineage replaced by a Grocer-based marine-resource identity |
| `BUILDING_RUSSIAN_RESEARCH_INSTITUTE` | `BUILDING_RUSSIAN_PRIKAZ` | 6113, 2026-08-14 | University/science identity replaced by Courthouse/administration/espionage identity |
| `BUILDING_VIKING_TRADING_POST` | `BUILDING_SCANDINAVIA_TRADING_POST -> BUILDING_SCANDINAVIA_CHIEFTAINS_HALL` | 4878, 2025-07-15 -> 6113, 2026-08-14 | First followed the civilization `VIKING -> SCANDINAVIA` naming change; later replaced the Port-based Trading Post with a Barracks-based Chieftains' Hall; the current 2026-11-05 machine namespace is `BUILDING_VIKING_CHIEFTAINS_HALL` |

Additional non-rename cases remain important:

- `BUILDING_CONFUCIAN_TEMPLE`, `BUILDING_CONFUCIAN_CATHEDRAL`, `BUILDING_CONFUCIAN_MONASTERY` and `BUILDING_CONFUCIAN_SHRINE` were removed with Confucianism; the later Pagan building family is separate content, not a `CONFUCIAN_* -> PAGAN_*` rename.
- `BUILDING_OBSERVATORY`, `BUILDING_SPACE_ELEVATOR` and `BUILDING_WEST_POINT` are removals/restructures without a justified one-to-one rename mapping in this document.
- SAS also added genuinely new building families such as the Ireland/Kingdom of Benin and Barbarian buildings; additions are not retroactively paired with unrelated inherited disappearances.

## Promotions

Promotions contain many true naming-led changes. Unlike bonuses, the SAS machine names were often chosen specifically to expose the promotion's actual mechanic more directly.

Early direct renames:

| AdvCiv/BtS before | SAS change | Practical commit/date | Why it changed | Text-key companion |
| --- | --- | --- | --- | --- |
| `PROMOTION_MARCH` | `PROMOTION_MEDIC_AMBULATORY` | 4625, `3b45f408a0`, 2025-04-10 | Mechanics-descriptive naming: identifies the mobile-healing role instead of the generic "March" label | `TXT_KEY_PROMOTION_MARCH -> TXT_KEY_PROMOTION_MEDIC_AMBULATORY` |
| `PROMOTION_INTERCEPTION1/2` | `PROMOTION_AIR_INTERCEPTION1/2` | 4626, `2640080673`, 2025-04-10 | Names the air mechanic explicitly | Matching text keys renamed |
| `PROMOTION_ACE` | `PROMOTION_AIR_EVASION` | 4664, `95aa7ee6e6`, 2025-04-12 | Replaces flavor label with the actual air-evasion mechanic | Matching text key renamed |
| `PROMOTION_RANGE1/2` | `PROMOTION_AIR_RANGE1/2` | 4665, `3c4bd28130`, 2025-04-12 | Makes the air domain explicit | Matching text keys renamed |
| `PROMOTION_BLITZ` | `PROMOTION_BLITZKRIEG` | 4666, `4fd828365a`, 2025-04-12 | Naming clarification; no more specific rationale preserved here | Matching text key renamed |
| `PROMOTION_ACCURACY` | `PROMOTION_CITY_BOMBARD_DAMAGE` | 4667, `9a1ebaa447`, 2025-04-12 | Exposes the actual city-bombard effect in the identifier | Matching text key renamed |
| `PROMOTION_COVER` | `PROMOTION_COUNTER_ARCHER` | 4668, `b5928cb09f`, 2025-04-12 | Exposes the countered unit family | Matching text key renamed |
| `PROMOTION_PINCH` | `PROMOTION_COUNTER_GUN` | 4669, `cdf955b1ba`, 2025-04-12 | Exposes the countered unit family | Matching text key renamed |
| `PROMOTION_SHOCK` | `PROMOTION_COUNTER_MELEE` | 4670, `ea048798c9`, 2025-04-12 | Exposes the countered unit family | Matching text key renamed |
| `PROMOTION_FORMATION` | `PROMOTION_COUNTER_MOUNTED` | 4671, `17b45f2768`, 2025-04-12 | Exposes the countered unit family | Matching text key renamed |
| `PROMOTION_CHARGE` | `PROMOTION_COUNTER_SIEGE` | 4672, `2ea5ba06c3`, 2025-04-12 | Exposes the countered unit family | Matching text key renamed |
| `PROMOTION_AMBUSH` | `PROMOTION_COUNTER_TANK` | 4673, `1bb325ddf6`, 2025-04-12 | Exposes the countered unit family | Matching text key renamed |
| `PROMOTION_COMMANDO` | `PROMOTION_LOGISTICS` | 4674, `1ab998439d`, 2025-04-12 | Renames toward the movement/logistics effect rather than the inherited flavor label | Matching text key renamed |
| `PROMOTION_BARRAGE1/2/3` | `PROMOTION_COLLATERAL_DAMAGE1/2/3` | 4676, `bf2f1f4367`, 2025-04-12 | Exposes the collateral-damage mechanic directly | Matching text keys renamed; SAS later added Collateral Damage 4/5 |

Practical commit **4865**, `d4e9766e55`, 2025-07-09, performed another naming/rebalance pass:

| AdvCiv/BtS before | SAS change | Why / historical note | Later state by 2026-11-04 |
| --- | --- | --- | --- |
| `PROMOTION_GUERILLA1/2/3` | `PROMOTION_HILLS_MASTER1/2/3` | Renames the line around its hill specialization rather than the inherited flavor term | Present |
| `PROMOTION_DRILL1/2/3/4` | `PROMOTION_FIRST_STRIKE1/2/3/4` | Names the line for its core first-strike mechanic | Present |
| `PROMOTION_FLANKING1/2` | `PROMOTION_RETREAT1/2` | Names the line for withdrawal/retreat behavior | Present |
| `PROMOTION_MOBILITY` | `PROMOTION_NAVIGATOR1` | Part of the navigation/movement-line reorganization | Intermediate name later consolidated into `PROMOTION_NAVIGATOR` |
| inherited Navigation/Navigator structure | reorganized Navigator line | Consolidated overlapping navigation terminology | Final `PROMOTION_NAVIGATOR` present |
| `PROMOTION_TACTICS` | `PROMOTION_MOBILITY_COST` | Mechanics-descriptive movement-cost naming | Present |
| `PROMOTION_MORALE` | `PROMOTION_MOBILITY_RANGE` | Mechanics-descriptive movement-range naming | Present |

For these promotions, matching `TXT_KEY_PROMOTION_*` descriptions were generally renamed with the Type as part of the same naming family.

## Technologies

Technology naming was much more extensive than the earlier version of this audit showed. It also contains the most dangerous false positives: SAS repeatedly **renamed**, **repurposed**, **removed**, and later **reintroduced** tech identifiers while rebuilding the tree. The table therefore records lineage and classification instead of assuming that equal XML positions imply identity.

### Direct or explicitly evidenced inherited lineages

| AdvCiv/BtS before | SAS lineage | Practical commit/date | Classification / why | State on 2026-11-04 |
| --- | --- | --- | --- | --- |
| `TECH_HORSEBACK_RIDING` | `TECH_MOUNTED_INFANTRY -> TECH_MOUNTED_COMBAT` | 4786, 2025-05-28 -> 4805, 2025-06-04 | Rename/generalization around the broader mounted branch | `TECH_MOUNTED_COMBAT` active |
| `TECH_UTOPIA` | `TECH_COMMUNISM` | 4781, `f50ab80096`, 2025-05-28 | **Direct explicit rename.** The commit title and source comments both say `_UTOPIA -> _COMMUNISM`; pedia/text were rewritten for actual Communism | Active |
| `TECH_SAILING` | `TECH_SEAFARING` | 4830, `1569533198`, 2025-06-11 | Direct rename during the water-tech reordering; broadens the earliest maritime concept | Active |
| `TECH_OPTICS` | `TECH_SAILING` | 4830, `1569533198`, 2025-06-11 | Direct rename/reassignment in the same water-tech reordering | Active; note that the `TECH_SAILING` identifier was reused for a different inherited slot |
| `TECH_COMPASS` | `TECH_NAVIGATION` | 4830, `1569533198`, 2025-06-11 | Direct rename to the broader navigation concept | Active |
| `TECH_STEEL` | `TECH_MARINE_TECHNOLOGY` | 4857, `fad16d7de7`, 2025-07-03 | Explicit replacement/rename during tree redesign; source comments consistently record Steel as replaced by Marine Technology | Active; concept changed substantially |
| `TECH_PAPER` | `TECH_THEORY_OF_EVOLUTION` | 4857, `fad16d7de7`, 2025-07-03 | Explicit slot/concept replacement, **not** a synonym | Theory of Evolution active; the `TECH_PAPER` identifier was later reintroduced for a different lineage |
| `TECH_REPLACEABLE_PARTS` | `TECH_GAME_THEORY` | 4857, `fad16d7de7`, 2025-07-03 | Explicit concept replacement | Game Theory active |
| `TECH_ALPHABET` | `TECH_NATURALISM` | 4857, `fad16d7de7`, 2025-07-03 | Explicit concept replacement | Naturalism active |
| `TECH_THEOLOGY` | `TECH_POSTAXIAL_RELIGION` | 4863, `ac1596d613`, 2025-07-08 | Explicit rename/reframing: source comment says Theology was too broad for the specific historical/religious period represented | Postaxial Religion later replaced by Drama in 6081 |
| `TECH_DIVINE_RIGHT` | `TECH_LATER_ABRAHAMISM` | 4863, `ac1596d613`, 2025-07-08 | Explicit rename/reframing: source comment says Divine Right belongs earlier and the slot was reframed around later Abrahamic religions | Later Abrahamism later replaced by Sacred Architecture in 6081 |
| `TECH_PLASTICS` | `TECH_DEPOPULATION` | 4883, `f6b992b469`, 2025-07-21 | Future-era slot repurposing, not semantic rename | Depopulation active |
| `TECH_STEALTH` | `TECH_ALIEN_LIFE` | 4883, `f6b992b469`, 2025-07-21 | Future-era slot repurposing | Alien Life active |
| `TECH_FIBER_OPTICS` | `TECH_AI` | 4883, `f6b992b469`, 2025-07-21 | Future-era slot repurposing | AI active |
| `TECH_RAILROAD` | `TECH_QUANTUM_MECHANICS` | 4883, `f6b992b469`, 2025-07-21 | Future-era slot repurposing | Quantum Mechanics active |
| `TECH_ROBOTICS` | `TECH_ROBOTIC_RIGHTS -> TECH_ROBOT_RIGHTS` | 4883, `f6b992b469`, 2025-07-21 -> 5051, `a276719b71`, 2025-10-09 | Concept repurposing followed by direct naming cleanup | Robot Rights active |
| `TECH_LASER` | `TECH_TERRAFORMING` | 4883, `f6b992b469`, 2025-07-21 | Future-era slot repurposing | Terraforming active |
| `TECH_FUTURE_TECH` | `TECH_TRANSHUMANISM` | 4883, `f6b992b469`, 2025-07-21 | Future-era slot repurposing | Transhumanism active |
| `TECH_SCIENTIFIC_METHOD` | `TECH_WATER_WHEEL` | 4967, `455a85d30a`, 2025-08-29 | Explicit replacement/repurposing, not a semantic rename | Water Wheel active |
| `TECH_GUILDS` | `TECH_CHIVALRY` | 4968, `ca1e3bdee8`, 2025-08-29 | Explicit replacement | Chivalry active |
| `TECH_PRIESTHOOD` | `TECH_BIOENGINEERING` | 4968, `ca1e3bdee8`, 2025-08-29 | Explicit unrelated slot replacement | Bioengineering active |
| `TECH_ARCHERY` | `TECH_SPACE_EXPLORATION` | 4968, `ca1e3bdee8`, 2025-08-29 | Explicit unrelated slot replacement | Space Exploration active |
| `TECH_RIFLING` | `TECH_FIREARMS` | 4975, `e8199e74b3`, 2025-09-03 | Direct naming/generalization inside the firearms-tree redesign | Active |
| `TECH_EDUCATION` | `TECH_BROADER_EDUCATION` | 4976, `c332858b4a`, 2025-09-03 | Direct naming/generalization | Active |
| `TECH_MUSIC` | `TECH_MUSIC_THEORY -> TECH_ROMANTICISM` | 5192, `b9d4edfdac`, 2025-12-14 -> 5199, `cc3e2951cd`, 2025-12-16 | First a direct rename, then a concept replacement | Romanticism active |
| `TECH_REFRIGERATION` | `TECH_ENVIRONMENTALISM` | 5210, 2025-12-18 | Concept replacement/reuse of the old civic term | Environmentalism tech active |
| `TECH_SUPERCONDUCTORS` | `TECH_PROFESSIONAL_ARMY` | 5487-5489, `c76f21df59` / `e746207160`, 2026-02-26 | Explicit functional replacement then reskin | Professional Army active |
| `TECH_ECOLOGY` | `TECH_AUTOMOBILES` | 6081, `38afe787cd`, 2026-08-05 | Explicit replacement during another major tech-tree rework | Automobiles active |
| intermediate `TECH_POSTAXIAL_RELIGION` | `TECH_DRAMA` | 6081, `38afe787cd`, 2026-08-05 | Explicit replacement; this **reintroduced the inherited `TECH_DRAMA` identifier** after Drama had previously been repurposed | Drama active |
| intermediate `TECH_LATER_ABRAHAMISM` | `TECH_SACRED_ARCHITECTURE` | 6081, `38afe787cd`, 2026-08-05 | Explicit replacement | Sacred Architecture active |

### Reused identifiers that final-state diffs can hide

The tech tree demonstrates why this audit cannot be generated only from the 2026-11-04 Type-set difference:

- Inherited `TECH_PAPER` was explicitly replaced by `TECH_THEORY_OF_EVOLUTION` in 4857. Later, practical 5487 functionally replaced `TECH_DRAMA` with a **new/reintroduced `TECH_PAPER`**. The same text token therefore denotes different historical lineages at different times.
- In practical 4830, inherited `TECH_SAILING` became `TECH_SEAFARING`, while inherited `TECH_OPTICS` became the new `TECH_SAILING`. Seeing `TECH_SAILING` in both base AdvCiv and current SAS does **not** mean that asset was unchanged.
- In 6081, `TECH_POSTAXIAL_RELIGION` was replaced with `TECH_DRAMA`, reintroducing another inherited identifier after prior tree churn.

These cases are especially important for future LLM/code archaeology: a common old/current identifier can still have been removed and later reused for a different tech.

## Civics

The civic comparison also contained more direct lineage than the earlier audit recorded.

| AdvCiv/BtS before | SAS lineage | Practical commit/date | Why / nature of change | State on 2026-11-04 |
| --- | --- | --- | --- | --- |
| `CIVIC_PAGANISM` | `CIVIC_PREHISTORIC_RELIGION` | 4748, `bf00d29700`, 2025-05-10 | Direct Type/text-key rename during the early religious/barbarian rework; reframes the default civic as a historical stage rather than the broad "Paganism" label | Active |
| `CIVIC_EMANCIPATION` | `CIVIC_WAGE_LABOR` | 5104, `a85a49b1af`, 2025-11-11 | Commit explicitly says **rename and rework** | Active |
| `CIVIC_MERCANTILISM` | `CIVIC_PROTECTIONISM` | 5121, `5f27d95b1d`, 2025-11-17 | Commit explicitly says the old Mercantilism civic was reworked as Protectionism | Active; redesign, not payload-preserving rename |
| `CIVIC_ENVIRONMENTALISM` | `CIVIC_TRADE_BLOC` | 5121, `5f27d95b1d`, 2025-11-17 | Commit explicitly replaces the old economy Environmentalism civic with Trade Bloc | Active; concept replacement |

SAS also briefly had its own `CIVIC_REGIONAL_TRADE -> CIVIC_TRADE_LEAGUE` naming lineage in practical 5119 (`47c2913350`, 2025-11-17). That is useful internal SAS history, but neither side is an inherited AdvCiv civic, so it is not counted as an AdvCiv -> SAS rename in the primary table. The same-day economy-civic redesign then settled on the current Trade Bloc / Protectionism structure.

## Other XML Type families

A same-path AdvCiv 1.14 vs. SAS 2026-11-04 Type-set comparison also found these differences, which are not ordinary asset renames:

- The inherited UnitCombat taxonomy was deliberately split into the Archer, Air, Mounted and Melee subfamilies documented in [Unit-combat taxonomy splits](#unit-combat-taxonomy-splits). In particular, `UNITCOMBAT_AIR -> UNITCOMBAT_AIR_BOMBER` is only the first half of the Air split because `UNITCOMBAT_AIR_FIGHTER` was added two practical commits later.
- `UNITAI_ARTIST/ENGINEER/GENERAL/MERCHANT/PROPHET/SCIENTIST -> UNITAI_GREAT_*` is the Great-Person companion family documented above.
- `TRAIT_EXPANSIVE` was absent from the 2026-11-04 TraitInfo set with no replacement Type recorded here; deletion is not a rename.
- SAS adds `GAMESPEED_NITRO`, `GAMESPEED_SLOW`, `GAMESPEED_TURBO` and `GAMESPEED_VERY_SLOW`; these are additions, not inherited-name changes.
- SAS adds `HANDICAP_ROOKIE` and `HANDICAP_DEITY_PLUS`; these are additions.
- AdvCiv's `WORLDSIZE_XXL` was absent while SAS had several new `WORLDSIZE_SAS*` sizes plus Arena; this is a world-size redesign/addition family rather than `XXL ->` one arbitrary SAS size.
- `COLOR_CITY_BROWN` was absent from the 2026-11-04 `CIV4ColorVals.xml`; no rename successor is asserted.
- `BONUSCLASS_DISABLED` is new SAS support infrastructure.
- `IMPROVEMENT_WINERY` and `BUILD_WINERY` were removed as part of the Grapes redesign, not renamed.
- ControlInfo differences (`CONTROL_CORPORATION_SCREEN`, `CONTROL_FINANCIAL_SCREEN`, `CONTROL_RELIGION_SCREEN` versus the 2026-11-04 advisor controls) reflect UI/control restructuring, not simple asset renaming.
- The direct AdvCiv comparison found no Type-set difference in `CIV4SpecialistInfos.xml` or `CIV4ProjectInfo.xml`; importantly, Great-Person unit renaming intentionally did not rename ordinary `SPECIALIST_*` IDs.

Art definitions and text keys show much larger set differences because they are companion namespaces for the gameplay objects above plus new SAS UI/content. Most are therefore recorded with their owning asset family. A few art-definition renames were independent consistency fixes and are worth recording separately.

### Art-definition-only naming corrections

[KI#19](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-19) records a cluster of inherited unit-art identifiers whose geographic labels did not match the models or how SAS used them. These are not UnitInfo renames; they are `ART_DEF_UNIT_*` identifier corrections.

| Inherited / earlier art Type | SAS lineage | Practical commit/date | Why | State on 2026-11-04 |
| --- | --- | --- | --- | --- |
| `ART_DEF_UNIT_ARCHER_CHINESE` | `ART_DEF_UNIT_ARCHER_ASIAN -> ART_DEF_UNIT_LONGBOWMAN_ASIAN` | 4832, `44cb420869`, 2025-06-14 -> 5934, `ca5b991a4a`, 2026-06-10 | First generalized a not-specifically-Chinese model to Asian; later corrected the unit category because the model visually represents a longbowman | Longbowman Asian active; noted as unused at review time |
| `ART_DEF_UNIT_SWORDSMAN_CHINESE` | `ART_DEF_UNIT_SWORDSMAN_ASIAN` | 4832, `44cb420869`, 2025-06-14 | Model was considered broadly Asian rather than specifically Chinese and no generic Asian swordsman art Type existed | Active |
| `ART_DEF_UNIT_CHARIOT_CHINESE` | `ART_DEF_UNIT_CHARIOT_ASIAN` | 4832, `44cb420869`, 2025-06-14 | Same geographic-generalization cleanup | Active |
| `ART_DEF_UNIT_SPEARMAN_EURASIAN` | `ART_DEF_UNIT_SPEARMAN_ASIAN` | 4832, `44cb420869`, 2025-06-14; KI#19 cleanup reinforced in 5934 | Source comment says the model looks clearly Asian/Mongol rather than European/Eurasian | Active |

This family is useful evidence for the audit's broader rule: asset-name history includes companion namespaces where the identifier itself carries a misleading semantic claim, even when no gameplay `UNIT_*` Type changes.

## Systematic AdvCiv 1.14 -> SAS Type-set reconciliation

To prevent the audit from drifting back into a remembered-example list, the 2026-11-04 review compared the primary `<Type>` sets in every matching AdvCiv 1.14 / SAS gameplay XML file and reconciled every meaningful disappearance against history.

Because AdvCiv inherits BtS `CIV4UnitCombatInfos.xml` rather than shipping its own override, that family was additionally reconstructed from the inherited BtS set preserved in SAS's initial import and checked against all surviving AdvCiv unit assignments.

A second pass compared every surviving inherited `UNIT_*` Type's `Class`, `Combat` and `Domain`, which is what exposed the same-Type reclassifications above. This table is deliberately compact: detailed reasons remain in the category sections above.

| XML family | Inherited Types absent from SAS by 2026-11-04 | Reconciliation |
| --- | --- | --- |
| NewConcept / pedia concepts | The inherited BtS concept-page set (`CONCEPT_AIR_COMBAT`, trait concepts, corporations/events/espionage concepts, etc.) was removed from `CIV4NewConceptInfos.xml` | Documentation/Sevopedia restructuring; SAS added its own `CONCEPT_SAS_*` pages. This is not a one-to-one asset rename family |
| Bonus | `CLAM`, `CORN`, `COW`, `GEMS`, `IVORY`, `WINE`, `MOVIES` | First six are evidenced rename families; Movies was removed and Camel added as different content |
| Civilization | `VIKING` | `VIKING -> SCANDINAVIA`; Ireland and Kingdom of Benin are additions |
| Leader | `CHINESE_LEADER`, `MONTEZUMA` | Direct renames to Mao Zedong and Moctezuma; Ewuare, Grace O'Malley and Michael Collins are additions |
| Civic | `PAGANISM`, `EMANCIPATION`, `MERCANTILISM`, `ENVIRONMENTALISM` | Reconciled above respectively to Prehistoric Religion, Wage Labor, Protectionism and Trade Bloc, with the latter two being redesign/replacement lineages |
| Technology | 26 inherited Types absent | Every direct/repurposed lineage established by history is listed in the Technologies section; importantly, same-name reintroductions such as Paper/Sailing/Drama mean final Type sets alone are insufficient |
| UnitCombat | `ARCHER`, `AIR`, `MOUNTED`, `MELEE` absent as broad inherited families | Deliberate one-to-many taxonomy splits: Archer -> short/long/crossbow; Air -> bomber/fighter (with Airship later Recon); Mounted -> melee/ranged; Melee -> polearm/shock. Exact commits, members and rationale are documented above |
| Unit / UnitClass | Great People, Knight/Cuirassier, Marine, AT Infantry, artillery/tank lines, several UUs, Taoist missionary, plus removed naval units | Direct renames and splits are listed above; the systematic same-Type comparison also found the class/role moves for Airship, Mechanized Infantry, Immortal, Bowman, Skirmisher, Hwacha, Cossack, Conquistador, Cataphract, Jaguar and Quechua; civ-UU replacements and pure removals are classified separately rather than paired by position |
| Building | Generic naming cleanups, Taoist family, many inherited UBs, Confucian family, Observatory/Space Elevator/West Point | Naming-led rows, Daoism family and exact UB replacements are recorded above; remaining removed wonders/buildings are not assigned invented successors |
| Promotion | 32 inherited promotion Types absent | The direct mechanics-descriptive rename series is documented above; added higher tiers and later reorganizations are not treated as one-to-one aliases |
| UnitAI | `ARTIST`, `ENGINEER`, `GENERAL`, `MERCHANT`, `PROPHET`, `SCIENTIST` | Great-Person `UNITAI_GREAT_*` rename family in practical 4750 |
| Trait | `TRAIT_EXPANSIVE` | Removed; no rename successor asserted |
| Improvement / Build | `IMPROVEMENT_WINERY`, `BUILD_WINERY` | Removed as part of the Wine -> Grapes gameplay redesign; Farm first replaced Winery, and Grapes later moved to Plantation; this is gameplay lineage, not an identifier rename |
| UI Control | Corporation / Financial / Religion screen controls absent; World/Foreign Diplomacy controls added | Advisor/UI restructuring, not asset rename lineage |
| Game speed / Handicap / World size | New SAS entries | Additions, not inherited-name changes |

A separate same-Type/display comparison also found naming changes that the Type-set pass cannot see, including Ice -> Ice Sheet/Ice Cap, Pacal II, Justinian I, Suryavarman II, the USA / Native American civilization display names, Great Priest, and the Persia Immortal text-key correction. Those are documented in [Same-Type display and text-key renames](#same-type-display-and-text-key-renames).

This reconciliation is intentionally **not** a claim that every removed Type has a successor. When history says "replace", "remove", "split", or adds unrelated content, the audit preserves that classification rather than manufacturing a rename merely to make the sets pair up.

## Historical evidence

The practical commit number is included for convenient human navigation, together with the short SHA and date where useful. The Git SHA remains the unique identity because practical commit counts can repeat across divergent/merged history.

The main rename archaeology used these historical anchors:

- Same-Type/display naming: 4461-4462 (leader regnal names), 4648 (Ice Sheet / Ice Cap), 4841 (Persia text-key correction), 4883 (USA / Native American display names).
- Promotions/unit-combat: practical commits 4616, 4625-4626, 4664-4676 and 4865.
- Daoism: 4740-4741.
- Moctezuma/religion restructuring: 4743.
- Monument: 4748.
- Mao Zedong and Forbidden Palace: 4749.
- Great People and Security Bureau: 4750.
- Three Gorges Dam: 4764.
- Utopia -> Communism: 4781, `f50ab80096`, 2025-05-28.
- Water-tech naming chain (Sailing -> Seafaring, Optics -> Sailing, Compass -> Navigation): 4830, `1569533198`, 2025-06-11.
- Bonus naming series: 4767-4770 and 4776.
- Camel/new resource replacement and first Asian unit-art naming cleanup: 4832.
- Steel/Paper/Replaceable Parts/Alphabet tech replacements: 4857, `fad16d7de7`, 2025-07-03.
- Horse Knight/Cuirassier split: 4858, `601d40d995`, 2025-07-04.
- Theology -> Postaxial Religion and Divine Right -> Later Abrahamism: 4863, `ac1596d613`, 2025-07-08.
- Marine -> Modern Infantry: 4871, `378e9fd759`, 2025-07-11.
- Scandinavia, Hoplite, Legionary and Viking: 4878.
- Modern Tank/artillery naming: 4909-4910 and 5117.
- AT Infantry -> Bazooka: 4957, `fe58e13463`, 2025-08-24.
- Scientific Method/Guilds/Priesthood/Archery tech repurposing: 4967-4968.
- Rifling -> Firearms and Education -> Broader Education: 4975-4976.
- Temple of Kukulcan: 4985.
- Khishigten, Egyptian War Chariot and Zhuge Nu: 5024, 5037 and 5118.
- Robot Rights naming cleanup: 5051.
- Civic lineages: Paganism -> Prehistoric Religion in 4748; Emancipation -> Wage Labor in 5104; Mercantilism/Environmentalism -> Protectionism/Trade Bloc in 5121.
- Music -> Music Theory -> Romanticism: 5192 and 5199; Refrigeration -> Environmentalism: 5210.
- Superconductors -> Professional Army and Drama/Paper reuse: 5487-5489.
- Later technology replacement pass (Postaxial Religion / Later Abrahamism / Ecology -> Drama / Sacred Architecture / Automobiles): 6081.
- Major later UB replacements: German Assembly Plant -> Longhouse in 4822; 5467-5473, 6098-6099 and 6113 for later inherited-UB replacement waves; 6121 for later civ-specific unit/building work.
- KI#19 art-definition correction follow-up, including Archer Asian -> Longbowman Asian: 5934.

The 2026-11-04 state is recorded only to answer whether a historical SAS rename had already been reverted or superseded by that date. If a name changes again later, keep the original old -> new row and append the later result. Retired identifiers that need an old-to-current translation can additionally be cross-referenced from [`Docs/Deprecated`](/_1_AdvCiv-SAS/Docs/Deprecated/README.md).

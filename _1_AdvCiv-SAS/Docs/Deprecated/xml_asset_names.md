# Retired XML asset names

Use this reference to translate machine-facing asset identifiers found in older AdvCiv-SAS source, logs, screenshots, discussions and historical documentation into the current identifiers. The full chronology and rationale are in [`xml_asset_naming_and_taxonomy.md`](/_1_AdvCiv-SAS/Docs/Source_Analysis/xml_asset_naming_and_taxonomy.md).

It lists only names that were retired while the asset itself kept working under another name, for example `BONUS_GRAPES` becoming `BONUS_WINE` again. Fixes found along the way belong in the [Known Issues](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md): the stale Farm rules for Grapes plot art, found after the bonus restoration, are KI#1074, not a name change.

## Menu

- [Bonus identifier restoration](#bonus-identifier-restoration)
- [Leader identifier restoration](#leader-identifier-restoration)
- [Civilization identifier restoration](#civilization-identifier-restoration)
- [Religion identifier restoration](#religion-identifier-restoration)
- [Compatibility note](#compatibility-note)

## Bonus identifier restoration

AdvCiv-SAS renamed six inherited bonus machine families in May 2025 while also keeping or introducing clearer player-facing terminology. On 2026-11-04 the inherited AdvCiv/BtS machine families were restored for map-script, scenario and mod-content interoperability; the SAS English names and gameplay changes remain.

| Retired SAS machine family | Current inherited machine family | Player-facing SAS name |
| --- | --- | --- |
| `BONUS_GEMSTONES`, `ART_DEF_BONUS_GEMSTONES`, `TRU_GEMSTONES`, `TXT_KEY_BONUS_GEMSTONES*`, `HAS_BONUS_GEMSTONES` | `BONUS_GEMS`, `ART_DEF_BONUS_GEMS`, `TRU_GEMS`, `TXT_KEY_BONUS_GEMS*`, `HAS_BONUS_GEMS` | Gemstones |
| `BONUS_ELEPHANTS`, `ART_DEF_BONUS_ELEPHANTS`, `TRU_ELEPHANTS`, `TXT_KEY_BONUS_ELEPHANTS*`, `HAS_BONUS_ELEPHANTS` | `BONUS_IVORY`, `ART_DEF_BONUS_IVORY`, `TRU_IVORY`, `TXT_KEY_BONUS_IVORY*`, `HAS_BONUS_IVORY` | Elephants |
| `BONUS_GRAPES`, `ART_DEF_BONUS_GRAPES`, `TRU_GRAPES`, `TXT_KEY_BONUS_GRAPES*`, `HAS_BONUS_GRAPES` | `BONUS_WINE`, `ART_DEF_BONUS_WINE`, `TRU_WINE`, `TXT_KEY_BONUS_WINE*`, `HAS_BONUS_WINE` | Grapes |
| `BONUS_MAIZE`, `ART_DEF_BONUS_MAIZE`, `TRU_MAIZE`, `TXT_KEY_BONUS_MAIZE*`, `HAS_BONUS_MAIZE` | `BONUS_CORN`, `ART_DEF_BONUS_CORN`, `TRU_CORN`, `TXT_KEY_BONUS_CORN*`, `HAS_BONUS_CORN` | Maize |
| `BONUS_MOLLUSCS`, `ART_DEF_BONUS_MOLLUSCS`, `TRU_MOLLUSCS`, `TXT_KEY_BONUS_MOLLUSCS*`, `HAS_BONUS_MOLLUSCS` | `BONUS_CLAM`, `ART_DEF_BONUS_CLAM`, `TRU_CLAM`, `TXT_KEY_BONUS_CLAM*`, `HAS_BONUS_CLAM` | Molluscs |
| `BONUS_CATTLE`, `ART_DEF_BONUS_CATTLE`, `TRU_CATTLE`, `TXT_KEY_BONUS_CATTLE*`, `HAS_BONUS_CATTLE`; `SND_*CATTLE_RES*` / `AS3D_*CATTLE_RES*` | `BONUS_COW`, `ART_DEF_BONUS_COW`, `TRU_COW`, `TXT_KEY_BONUS_COW*`, `HAS_BONUS_COW`; inherited `SND_*COWS_RES*` / `AS3D_*COWS_RES*` | Cattle |

`BONUS_CAMEL` is not a restored alias for `BONUS_MOVIES`: Camel is separate SAS content that replaced the removed Hit Movies resource slot historically.

Since 2026-11-08, Camel and Peat take the places of base AdvCiv's first two Hit bonuses, Hit Musicals (`BONUS_DRAMA`) and Hit Singles (`BONUS_MUSIC`), and `BONUS_MOVIES` (Hit Movies) is the remaining disabled one; SAS's earlier disabled `BONUS_MUSIC` is retired.

## Leader identifier restoration

AdvCiv-SAS renamed two inherited leader machine families in May 2025. On 2026-11-04 the inherited AdvCiv/BtS machine identifiers were restored while the SAS player-facing names and gameplay/personality changes remain.

The benefit is less direct than for bonuses. AdvCiv-SAS does not support scenarios, and its other changes can still make external content incompatible. But XML, WorldBuilder or True Starts data that names the inherited leader families becomes easier to adapt and compare, and the SAS display names never needed different machine IDs.

| Retired SAS machine family | Current inherited machine family | Player-facing SAS name |
| --- | --- | --- |
| `LEADER_MAO_ZEDONG`, `ART_DEF_LEADER_MAO_ZEDONG`, `TRU_MAO_ZEDONG`, `TXT_KEY_LEADER_MAO_ZEDONG*`, `AI_DIPLO_*_LEADER_MAO_ZEDONG_*` | `LEADER_CHINESE_LEADER`, `ART_DEF_LEADER_CHINESE_LEADER`, `TRU_CHINESE_LEADER`, `TXT_KEY_LEADER_CHINESE_LEADER*`, `AI_DIPLO_*_LEADER_CHINESE_LEADER_*` | Mao Zedong |
| `LEADER_MOCTEZUMA`, `ART_DEF_LEADER_MOCTEZUMA`, `TRU_MOCTEZUMA`, `TXT_KEY_LEADER_MOCTEZUMA*`, `AI_DIPLO_*_LEADER_MOCTEZUMA_*`, `AS2D_DIPLO_MOCTEZUMA_*` / `DIPLO_MOCTEZUMA_*` | `LEADER_MONTEZUMA`, `ART_DEF_LEADER_MONTEZUMA`, `TRU_MONTEZUMA`, `TXT_KEY_LEADER_MONTEZUMA*`, `AI_DIPLO_*_LEADER_MONTEZUMA_*`, `AS2D_DIPLO_MONTEZUMA_*` / `DIPLO_MONTEZUMA_*` | Moctezuma II |

The temporary `TXT_KEY_LEADER_MAO_ZEDONG` description entry was removed because inherited `TXT_KEY_LEADER_CHINESE_LEADER` already displays **Mao Zedong**. SAS still overrides the inherited Mao pedia key with its expanded Civilopedia text.

For Moctezuma, SAS continues to override the inherited `TXT_KEY_LEADER_MONTEZUMA` and `TXT_KEY_LEADER_MONTEZUMA_PEDIA` keys so the player-facing spelling remains **Moctezuma II**.

The related machine key `TXT_KEY_CITY_NAME_MOCTEZUMA_CASTLE` likewise returned to `TXT_KEY_CITY_NAME_MONTEZUMA_CASTLE`, and its SAS override was removed so the inherited BtS text **Montezuma Castle** applies again. That is the real site's name: later settlers named the Arizona cliff dwelling (Montezuma Castle National Monument) after Moctezuma, so "Moctezuma Castle" was not a spelling correction.

## Civilization identifier restoration

On 2026-11-05 the Scandinavia civilization returned to the inherited `VIKING` machine namespace for easier reuse of inherited/external XML and WorldBuilder data. Its player-facing identity stays **Scandinavian Empire / Scandinavia / Scandinavian**, and its SAS gameplay redesigns remain.

| Retired SAS machine family | Current inherited machine family | Player-facing SAS name |
| --- | --- | --- |
| `CIVILIZATION_SCANDINAVIA`, `ART_DEF_CIVILIZATION_SCANDINAVIA`, `TRU_SCANDINAVIA`, `TXT_KEY_CIV_SCANDINAVIA_*`, `AS3D_SCANDINAVIA_*`, `SND_SCANDINAVIA_*`, `AS2D_SONG_SCANDINAVIA`, `SONG_SCANDINAVIA*` | `CIVILIZATION_VIKING`, `ART_DEF_CIVILIZATION_VIKINGS`, `TRU_VIKING`, `TXT_KEY_CIV_VIKING_*`, inherited `AS3D_VIKING_*` / `SND_VIKING_*`, `AS2D_SONG_VIKING`, `SONG_VIKING` / `SONG_VIKINGS_SCENARIO*` | Scandinavia |
| `UNIT_SCANDINAVIA_VIKING`, `ART_DEF_UNIT_SCANDINAVIA_VIKING`, `TXT_KEY_UNIT_SCANDINAVIA_VIKING*` | `UNIT_VIKING_VIKING`, `ART_DEF_UNIT_VIKING_VIKING`, `TXT_KEY_UNIT_VIKING_VIKING*` | Viking |
| `BUILDING_SCANDINAVIA_CHIEFTAINS_HALL`, `ART_DEF_BUILDING_SCANDINAVIA_CHIEFTAINS_HALL`, `TXT_KEY_BUILDING_SCANDINAVIA_CHIEFTAINS_HALL*`, `BLDGCIV_BUILDING_SCANDINAVIA_CHIEFTAINS_HALL` | `BUILDING_VIKING_CHIEFTAINS_HALL`, `ART_DEF_BUILDING_VIKING_CHIEFTAINS_HALL`, `TXT_KEY_BUILDING_VIKING_CHIEFTAINS_HALL*`, `BLDGCIV_BUILDING_VIKING_CHIEFTAINS_HALL` | Chieftain's Hall |

The repeated `VIKING` in `UNIT_VIKING_VIKING` is intentional: the first component is the restored civilization namespace and the second is the unit's displayed identity. The physical SAS art directories likewise moved from `Scandinavia_Viking` / `Scandinavia_Chieftains_Hall` to `Viking_Viking` / `Viking_Chieftains_Hall`.

The civilization XML block remains under **S**, not V, because Custom Game follows the shown short name **Scandinavia** rather than the machine `<Type>` (KI#1073).

## Religion identifier restoration

On 2026-11-05 Daoism returned to the inherited `TAOISM`/`TAOIST` machine names, which map scripts, WorldBuilder files and other mods use. Its player-facing name stays **Daoism / Daoist**, and its SAS gameplay changes remain. SAS added no art of its own for this family, so no art files moved.

| Retired SAS machine family | Current inherited machine family | Player-facing SAS name |
| --- | --- | --- |
| `RELIGION_DAOISM`, `TXT_KEY_RELIGION_DAOISM*`, `EFFECT_MISSIONARY_ACTIVE_DAOISM` | `RELIGION_TAOISM`, `TXT_KEY_RELIGION_TAOISM*`, `EFFECT_MISSIONARY_ACTIVE_TAOISM` | Daoism |
| `BUILDINGCLASS_DAOIST_*`, `BUILDING_DAOIST_*`, `ART_DEF_BUILDING_DAOIST_*`, `TXT_KEY_BUILDING_DAOIST_*`, `ART_DEF_MOVIE_SHRINE_DAOIST`, `BLDGCLASS_BUILDINGCLASS_DAOIST_*` | `BUILDINGCLASS_TAOIST_*`, `BUILDING_TAOIST_*`, `ART_DEF_BUILDING_TAOIST_*`, `TXT_KEY_BUILDING_TAOIST_*`, `ART_DEF_MOVIE_SHRINE_TAOIST`, `BLDGCLASS_BUILDINGCLASS_TAOIST_*` | Daoist Temple, Cathedral, Monastery and Shrine |
| `UNITCLASS_DAOIST_MISSIONARY`, `UNIT_DAOIST_MISSIONARY`, `ART_DEF_UNIT_DAOIST_MISSIONARY`, `TXT_KEY_UNIT_DAOIST_MISSIONARY*`, `*_DAOIST_MISSIONARY` (BUG unit-naming keys) | `UNITCLASS_TAOIST_MISSIONARY`, `UNIT_TAOIST_MISSIONARY`, `ART_DEF_UNIT_TAOIST_MISSIONARY`, `TXT_KEY_UNIT_TAOIST_MISSIONARY*`, `*_TAOIST_MISSIONARY` | Daoist Missionary |
| `AS2D_*DAOIST*`, `AS3D_*DAOIST*`, `SND_*DAOIST*` | inherited `AS2D_*TAOIST*`, `AS3D_*TAOIST*`, `SND_*TAOIST*` | (sounds) |

Restoring the names did not change the religion order, so the GameFont glyphs stay where they are; `xml_display_order.py` lists the restored `RELIGION_TAOISM` in its glyph order.

The [`retired_xml_asset_names.py`](/.github/workflows/README.md#buildxmlretired_xml_asset_namespy) CI check reads the first column of these tables and fails if active code uses one of the retired names again.

## Compatibility note

The restored identifiers reduce needless incompatibility with inherited or external content. For bonuses, this directly helps map scripts, which commonly place resources by their standard `BONUS_*` strings.

For leaders and the restored Viking civilization family, it mainly makes external data that names the inherited families easier to reuse. None of these restorations makes pre-SAS scenarios supported; see the root README's [support scope](/README.md#not-supported-in-advciv-sas).

These restorations do not restore the inherited gameplay payloads: for example, `BONUS_WINE` still represents the SAS Grapes resource and its current improvement/building behavior.

Historical Git logs, published changelogs, old Known Issues evidence, source-analysis records and saved log examples intentionally retain the identifier that was current when that evidence was produced.

Prepared by ChatGPT-5.6-Sol, 2026-11-04; updated through the Viking civilization restoration by ChatGPT-5.6-Sol, 2026-11-05.

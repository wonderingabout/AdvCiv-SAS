# Retired XML asset names

Use this reference to translate machine-facing asset identifiers found in older AdvCiv-SAS source, logs, screenshots, discussions and historical documentation into the current identifiers. The full chronology and rationale are in [`xml_asset_naming_and_taxonomy.md`](/_1_AdvCiv-SAS/Docs/Source_Analysis/xml_asset_naming_and_taxonomy.md).

## Menu

- [Bonus identifier restoration](#bonus-identifier-restoration)
- [Leader identifier restoration](#leader-identifier-restoration)
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

## Compatibility note

The restored identifiers reduce needless incompatibility with inherited or external content. For bonuses, this directly helps map scripts, which commonly place resources by their standard `BONUS_*` strings.

For leaders, it mainly makes external data that names the inherited leader families easier to reuse. Neither makes pre-SAS scenarios supported; see the root README's [support scope](/README.md#not-supported-in-advciv-sas).

These restorations do not restore the inherited gameplay payloads: for example, `BONUS_WINE` still represents the SAS Grapes resource and its current improvement/building behavior.

The restored bonus selectors in `CIV4PlotLSystem.xml` can use inherited names again. The SAS override still supplies plot art rules for Grapes on Farms, so it remains in use. The inherited BtS file uses `IMPROVEMENT_WINERY` for those rules.

Historical Git logs, published changelogs, old Known Issues evidence, source-analysis records and saved log examples intentionally retain the identifier that was current when that evidence was produced.

Prepared by ChatGPT-5.6-Sol, 2026-11-04.

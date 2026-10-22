# GlobalDefine name-length review

Reviewed on 2026-10-21 by ChatGPT-5.6-Sol and GPT-6.1-Sol after KI#1001's DefineTextVal capacity mitigation. The follow-up KI#1001.2 cleanup is now complete: the repository keeps a 42-byte desired naming maximum while preserving KI#1001's separate 255-byte loader-safety boundary.

## Scope and conclusion

This review began with a preventive question raised while fixing KI#1001: SAS define names had grown much longer than inherited Firaxis/K-Mod/AdvCiv names, so should they be shortened for safety, maintenance or performance?

The evidence supports three separate conclusions:

- **Loader safety:** `CvXMLLoadUtility::ReadGlobalDefines` reads `<DefineName>` through `char szName[256]`. The existing KI#1001 checker therefore treats 255 UTF-8 content bytes as the conservative repository-safe maximum, leaving one byte for the C-string terminator.
- **Variable-system capacity:** after loading, the name is a `std::string` key in `stdext::hash_map<std::string, FVariable*>`; no smaller semantic key-length limit is visible in the DLL source.
- **Naming policy:** Base AdvCiv 1.14, SAS's direct parent, tops out at 42 bytes in its supplied define names. SAS adopted that as a readability/headroom target rather than an engine correctness threshold.

The cleanup succeeded without needing to relax that target. The pre-cleanup SAS maximum was 114 bytes and 459 SAS names exceeded 42 bytes; the current SAS maximum is 42 bytes and no shipped define exceeds the target.

## Relationship to the audit album and KI#1001

This is not a newly promoted audit defect.

C031-WIP555 / F680, later KI#1001, found a concrete shipped `DefineTextVal` violation: `SAS_MAP_SCRIPT_NAMES_LAND_HEAVY` had reached 297 bytes while the inherited text branch used `char szVal[256]`. That active data/loader mismatch was mitigated separately.

The same album work noticed `char szName[256]`, but the then-current define names remained below the buffer capacity. KI#1001.2 therefore stayed explicitly preventive: it improves naming headroom and maintainability without claiming a second demonstrated runtime failure.

## Loader and lookup mechanics

The inherited GlobalDefines reader uses a fixed temporary for the key:

```cpp
char szName[256];
if (GetChildXmlVal(szName))
    GC.getDefinesVarSystem()->SetValue(szName, value);
```

The visible FXML raw-string interface receives a `char*` but no destination capacity. As with KI#1001's text values, the closed EXE does not expose what it would do with an overlong name. A 255-byte content ceiling is therefore the conservative lossless boundary for this specific `char[256]` destination.

After loading, `FVariableSystem` does not retain a 256-byte key array. It declares:

```cpp
typedef stdext::hash_map<std::string, FVariable*> FVariableHash;
```

and lookups use `m_mapVariableMap.find(szVariable)`. This supports treating 256 as an XML-loader scratch-buffer constraint rather than a general `FVariableSystem` naming limit.

The public Civ IV Wiki describes GlobalDefines as `DefineName` paired with typed value fields, without documenting a separate short-name limit. A CivFanatics DLL explanation likewise describes `getDefineINT` as looking up XML-loaded values in a hash table with strings as keys.

Those public references are useful corroboration; the local SDK source remains the stronger evidence for the implementation used by SAS.

## AdvCiv-SAS before/after census

The PR-start baseline is main commit `8aae7bd1e3b0a765b8897e3aa121ea90920a5f4a`. Both baseline and current trees ship 977 unique names across nine loaded GlobalDefines/PythonCallbackDefines files: 667 SAS names and 310 inherited names.

| Measure | Pre-cleanup SAS | Current SAS |
| --- | ---: | ---: |
| SAS define names | 667 | 667 |
| Names above 42 bytes | 459 | 0 |
| Longest name | 114 bytes | 42 bytes |
| Median name length | 49 bytes | 35 bytes |
| Nearest-rank 95th percentile | 77 bytes | 41 bytes |
| Mean name length | 51.13 bytes | 33.68 bytes |

A total of 628 SAS names changed and 39 retained their baseline spelling. The 628 include all 459 originally-over-limit names plus 169 shorter names renamed for family consistency, terminology consistency, word boundaries or clearer scope. Across the renamed keys, aggregate key text is 11,635 bytes shorter; this is a naming/storage observation, not a gameplay-performance claim.

### SAS five-byte distribution

| Name length (bytes) | Pre-cleanup SAS names | Current SAS names |
| --- | ---: | ---: |
| 11-15 | 0 | 4 |
| 16-20 | 8 | 13 |
| 21-25 | 16 | 48 |
| 26-30 | 22 | 116 |
| 31-35 | 49 | 183 |
| 36-40 | 75 | 234 |
| 41-45 | 100 | 69 |
| 46-50 | 93 | 0 |
| 51-55 | 73 | 0 |
| 56-60 | 64 | 0 |
| 61-65 | 46 | 0 |
| 66-70 | 32 | 0 |
| 71-75 | 46 | 0 |
| 76-80 | 19 | 0 |
| 81-85 | 5 | 0 |
| 86-90 | 6 | 0 |
| 91-95 | 5 | 0 |
| 96-100 | 5 | 0 |
| 101-105 | 1 | 0 |
| 106-110 | 1 | 0 |
| 111-115 | 1 | 0 |

### Inherited names shipped in SAS

The 310 inherited names were not part of the SAS rename campaign. Their direct-parent comparison remains useful because the longest shipped inherited name is still 42 bytes.

| File | Defines | Longest name (bytes) | Longest name |
| --- | ---: | ---: | --- |
| `Assets/XML/AI_Variables_GlobalDefines.xml` | 38 | 36 | `UWAI_WEIGHT_PRESERVATION_OF_PARTNERS` |
| `Assets/XML/BBAI_Game_Options_GlobalDefines.xml` | 9 | 32 | `BBAI_VICTORY_STRATEGY_DOMINATION` |
| `Assets/XML/GlobalDefinesAlt.xml` | 40 | 41 | `WARLORD_EXTRA_EXPERIENCE_PER_UNIT_PERCENT` |
| `Assets/XML/GlobalDefines_advc.xml` | 134 | 42 | `WE_LOVE_THE_KING_POPULATION_MIN_POPULATION` |
| `Assets/XML/GlobalDefines_devel.xml` | 9 | 30 | `ENABLE_DEBUG_TOOLS_MULTIPLAYER` |
| `Assets/XML/LeadFromBehind_GlobalDefines.xml` | 10 | 23 | `LFB_DEFENSIVEADJUSTMENT` |
| `Assets/XML/PythonCallbackDefines.xml` | 62 | 38 | `USE_CAN_FOUND_CITIES_ON_WATER_CALLBACK` |
| `Assets/XML/TechDiffusion_GlobalDefines.xml` | 8 | 37 | `TECH_COST_FIRST_KNOWN_PREREQ_MODIFIER` |

## External inherited/reference census

The local `sources_refs` archives provided comparison points outside the current mod folder. Counts reflect the GlobalDefines/PythonCallbackDefines files present in each supplied reference archive; mod archives can omit unchanged stock files, so these are not engine-wide totals.

| Reference | Defines scanned | Longest `DefineName` bytes | Longest name |
| --- | ---: | ---: | --- |
| AdvCiv 1.14 | 312 | 42 | `WE_LOVE_THE_KING_POPULATION_MIN_POPULATION` |
| K-Mod 1.46 | 111 | 41 | `WARLORD_EXTRA_EXPERIENCE_PER_UNIT_PERCENT` |
| Civ4CE BtS stock XML | 430 | 46 | `INITIAL_FREE_MILITARY_UNITS_POPULATION_PERCENT` |
| Civ4CE Warlords stock XML | 311 | 46 | `INITIAL_FREE_MILITARY_UNITS_POPULATION_PERCENT` |
| Civ4CE Civ4 stock XML | 295 | 46 | `INITIAL_FREE_MILITARY_UNITS_POPULATION_PERCENT` |
| Taurus 1.04 | 34 | 30 | `GLOBAL_WARMING_UNHEALTH_WEIGHT` |

These references show why 42 bytes was a defensible direct-parent style target while also confirming that it is not a universal Civ4 engine limit. Stock BtS examples reach 46 bytes without establishing a correctness boundary.

## Final naming policy

The desired maximum is **42 UTF-8 bytes**, matching Base AdvCiv 1.14's longest supplied define name. KI#1001's separate 255-byte checker remains the hard repository safety boundary for the inherited loader buffers.

Names use concise `SAS_<family>_<effect>` structure rather than mechanically copying full function names. Repeated terms are kept consistent so one grep finds related settings.

Compact technical vocabulary such as `PCT`, `MIN`, `MAX`, `VAL`, `PROD`, `BLDG`, `PWR`, `ATK`, `MILIT`, `VICT`, `BARB`, `NAT`, `LVL`, `_ON`, `T_NORM_GS` and `T_UNSCALED_GS` is preferred when it remains clear. Word boundaries use `_` when space permits.

The full deprecated/original-to-current mapping is preserved in [KI#1001.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1001.2). Intermediate drafting spellings remain in Git history rather than in the final reference table.

If a future clear setting cannot fit 42 bytes without losing an important distinction, review the policy explicitly rather than introducing an obscure abbreviation solely to satisfy the number.

## Performance considerations

Shorter names reduce key storage and the amount of string data involved in hashing/comparison, so there is a small technical basis for expecting shorter keys to be cheaper in isolation. Actual lookup cost is not determined by length alone; collisions and where strings first differ also matter.

More importantly, AdvCiv-SAS already avoids many repeated string lookups. AdvCiv's centralized cached integer defines use enum-indexed access, and SAS commonly uses function-local `static const` values for fixed process-lifetime settings. In those cases the string lookup is paid during cache initialization or first use rather than on every gameplay read.

No define-name benchmark was performed. The cleanup is justified primarily by readability, predictable grep/search vocabulary, reduced typo surface and extra headroom below the inherited loader boundary, not as a measured gameplay-performance optimization.

## Save and integration considerations

No current caller was found that serializes the GlobalDefines `FVariableSystem` through its generic `Read`/`Write` methods. Define names therefore are not part of the current SAS save schema merely because `FVariableSystem` supports generic stream serialization.

A pure rename that preserves value and behavior should not require save conversion. It does require every XML/C++/Python reference to move together, and native define literals require a matching rebuilt DLL/XML pair. The existing DLL define-change guard protects that integration boundary.

Behavioral redesigns remain separate. In particular, map-script heaviness versus each player's actual geography is an AI/gameplay interpretation question, not part of this naming cleanup.

## Maintenance workflow

1. Keep the 255-byte loader-safety CI as the hard correctness boundary.
2. Keep the 42-byte style checker passing across all shipped GlobalDefines/PythonCallbackDefines files.
3. Use the shared naming vocabulary and explicit turn/game-speed units in [AGENTS.md](/AGENTS.md#defines-and-ai-behavior).
4. Update XML declarations, all runtime lookups and mechanically copied cache/member identifiers together.
5. Keep KI#1001.2 as the canonical deprecated/original-to-current map for this cleanup; do not duplicate that map in a second hand-maintained list.
6. Reject retired names in active XML/C++/Python through CI while allowing historical docs, captured logs, changelogs and Git history to retain old spellings.
7. Rebuild the DLL whenever a native C++ lookup string changes before gameplay testing.

## Evidence and references

- Current SAS loader/storage: `CvGameCoreDLL/CvXMLLoadUtilitySet.cpp`, `CvGameCoreDLL/FVariableSystem.h`, `CvGameCoreDLL/FVariableSystem.inl` and `CvGameCoreDLL/CvGlobals.cpp`.
- Current SAS data and CI: `Assets/XML/*GlobalDefines*.xml`, `Assets/XML/PythonCallbackDefines.xml`, `.github/workflows/build/xml/global_define_lengths.py`, `.github/workflows/build/xml/global_define_name_style.py` and the retired-name checker.
- Album context: `cpp_file_audit_album.txt`, C031-WIP555/WIP556, F680/KI#1001.
- Local external references: `sources_refs/AdvCiv-1.14.zip`, `Civ4-K-Mod-master-1.46.zip`, `Civ4CE-main.zip` and `Taurus-1.04.zip`.
- [Civ IV Wiki: GlobalDefines](https://civ4.wikidot.com/xml:globaldefines) documents the public XML structure.
- [CivFanatics: How to change city growth threshold?](https://forums.civfanatics.com/threads/how-to-change-city-growth-threshold.619005/) includes Nightinggale's explanation that GlobalDefines are cached in a hash table with string lookup keys.

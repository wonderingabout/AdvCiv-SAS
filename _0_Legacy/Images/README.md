# Legacy base AdvCiv UI screenshots

These screenshots are retained as a visual reference for the pre-AdvCiv-SAS/base-AdvCiv interface. They are useful for comparing inherited UI behavior with current AdvCiv-SAS screens and for giving LLM/code agents direct visual context.

The captures are believed to come from roughly the AdvCiv 1.12-1.14 period, but the image files do not establish an exact AdvCiv version. Treat them as representative legacy references rather than exact-version regression baselines.

The folders intentionally mirror current [`_1_AdvCiv-SAS/Images/`](/_1_AdvCiv-SAS/Images/) categories where useful:

- `advisors/` includes Domestic, Foreign, Military, Technology, Victory and Info screens, plus two stitched tech trees, `0.610_tech_tree_merged_bts_web.webp` (BtS) and `0.611_tech_tree_merged_civ4_vanilla_web.webp` (vanilla Civ4), the counterparts of the SAS `1.5160_tech_tree_merged`. They are not AdvCiv captures: they come from the [Civilization Wiki](https://civilization.fandom.com/wiki/List_of_technologies_in_Civ4), hence the `_web` suffix. The Finance, Civics and Religion advisors use their F2, F3 and F7 families (`0.200`, `0.300`, `0.700`).
- `main_menu/` includes the inherited custom-game map-selection view (`0.310_main_menu_simple_game_select_map.JPG`); the base-AdvCiv Custom Game screen corresponds to the current AdvCiv-SAS `Simple Game`.
- `sevopedia/` includes base-AdvCiv Sevopedia pages for most categories (techs, units and unit chart, promotions, buildings, projects, specialists, terrains, features, bonuses, improvements, civilizations, leaders, traits, corporations, concepts, hints and shortcuts), named after their current `1.6xx`-`1.8xx` AdvCiv-SAS counterparts. `0.740_sevopedia_civics_python_exception.JPG` captures a Python exception raised by the Civics page of the base-AdvCiv Sevopedia.
- `ui_other/` includes the city screen (`0.990_city_screen.JPG`) and the three diplomacy screens (`0.970_diplomacy_screen`, mirroring SAS `1.970`). It uses `0.990` instead of mirroring SAS `1.400_city_screen` because `0.4xx` is the F4 Foreign advisor family and `0.6xx`-`0.8xx` are taken by Sevopedia.

The CI [image filename policy](/.github/workflows/README.md#builddocumentationimage_filename_policypy) requires every folder here to also exist in `_1_AdvCiv-SAS/Images/`, since the legacy tree is a subset.

Legacy/reference screenshots use the `0.x` filename namespace, while maintained AdvCiv-SAS screenshots use `1.x`; see the [current image notes](/_1_AdvCiv-SAS/Images/README.md). Within the legacy advisor set, F-key families are grouped where the inherited shortcut is meaningful (`0.1xx` F1 Domestic, `0.2xx` F2 Finance, `0.3xx` F3 Civics, `0.4xx` F4 Foreign, `0.5xx` F5 Military, `0.6xx` F6 Technology, `0.7xx` F7 Religion, `0.8xx` F8 Victory and `0.9xx` F9 Info). Other legacy captures reuse the closest current screen/category numbering when that makes comparison clearer; within a family, tab captures get their own number such as `0.400` Foreign Relations, `0.410`/`0.411` Resources and `0.800` Victories.

The supplied generic `Civ4ScreenShot####.JPG` names were replaced with descriptive names. Related captures use ordinary numbered variants such as `(1)`, `(2)` and `(3)` rather than partially inferred chronology such as `early`, unless chronology is independently established.

# Legacy base AdvCiv UI screenshots

These screenshots are retained as a visual reference for the pre-AdvCiv-SAS/base-AdvCiv interface. They are useful for comparing inherited UI behavior with current AdvCiv-SAS screens and for giving LLM/code agents direct visual context.

The captures are believed to come from roughly the AdvCiv 1.12-1.14 period, but the image files do not establish an exact AdvCiv version. Treat them as representative legacy references rather than exact-version regression baselines.

## Menu

[About these shots](#about-these-shots)\
&emsp;[Folders](#folders)\
&emsp;[Numbering and naming](#numbering-and-naming)\
&emsp;[Games shown](#games-shown)\
[Advisors](#advisors)\
&emsp;[Domestic Advisor](#domestic-advisor)\
&emsp;[Finance Advisor](#finance-advisor)\
&emsp;[Civics Advisor](#civics-advisor)\
&emsp;[Foreign Advisor](#foreign-advisor)\
&emsp;[Military Advisor](#military-advisor)\
&emsp;[Technology Advisor](#technology-advisor)\
&emsp;[Religion Advisor](#religion-advisor)\
&emsp;[Victory screen](#victory-screen)\
&emsp;[Info screen](#info-screen)\
[Main menu](#main-menu)\
[Sevopedia](#sevopedia)\
&emsp;[Leaders and traits](#leaders-and-traits)\
&emsp;[Civilizations](#civilizations)\
&emsp;[Units and promotions](#units-and-promotions)\
&emsp;[Buildings and wonders](#buildings-and-wonders)\
&emsp;[Terrains and features](#terrains-and-features)\
&emsp;[Bonuses](#bonuses)\
&emsp;[Improvements](#improvements)\
&emsp;[Technologies](#technologies)\
&emsp;[Civics](#civics)\
&emsp;[Projects](#projects)\
&emsp;[Specialists and corporations](#specialists-and-corporations)\
&emsp;[Concepts, hints and shortcuts](#concepts-hints-and-shortcuts)\
[Other screens](#other-screens)\
&emsp;[Diplomacy](#diplomacy)\
&emsp;[City screen](#city-screen)

## About these shots

### Folders

The folders intentionally mirror current [`_1_AdvCiv-SAS/Images/`](/_1_AdvCiv-SAS/Images/) categories where useful:

- `advisors/` includes Domestic, Foreign, Military, Technology, Victory and Info screens, plus two stitched tech trees, `0.610_tech_tree_merged_bts_web.webp` (BtS) and `0.611_tech_tree_merged_civ4_vanilla_web.webp` (vanilla Civ4), the counterparts of the SAS `1.5160_tech_tree_merged`. They are not AdvCiv captures: they come from the [Civilization Wiki](https://civilization.fandom.com/wiki/List_of_technologies_in_Civ4), hence the `_web` suffix. The Finance, Civics and Religion advisors use their F2, F3 and F7 families (`0.200`, `0.300`, `0.700`).
- `main_menu/` includes the inherited custom-game map-selection view (`0.310_main_menu_simple_game_select_map.JPG`); the base-AdvCiv Custom Game screen corresponds to the current AdvCiv-SAS `Simple Game`.
- `sevopedia/` includes base-AdvCiv Sevopedia pages for most categories (techs, units and unit chart, promotions, buildings, projects, specialists, terrains, features, bonuses, improvements, civilizations, leaders, traits, civics, corporations, concepts, hints and shortcuts), named after their current `1.6xx`-`1.8xx` AdvCiv-SAS counterparts.
- `ui_other/` includes the city screen (`0.990_city_screen (1).JPG` and `(2)_huge_48civs`) and the three diplomacy screens (`0.970_diplomacy_screen`, mirroring SAS `1.970`). It uses `0.990` instead of mirroring SAS `1.400_city_screen` because `0.4xx` is the F4 Foreign advisor family and `0.6xx`-`0.8xx` are taken by Sevopedia.

The CI [image filename policy](/.github/workflows/README.md#builddocumentationimage_filename_policypy) requires every folder here to also exist in `_1_AdvCiv-SAS/Images/`, since the legacy tree is a subset.

### Numbering and naming

Legacy/reference screenshots use the `0.x` filename namespace, while maintained AdvCiv-SAS screenshots use `1.x`; see the [current image notes](/_1_AdvCiv-SAS/Images/README.md). Within the legacy advisor set, F-key families are grouped where the inherited shortcut is meaningful (`0.1xx` F1 Domestic, `0.2xx` F2 Finance, `0.3xx` F3 Civics, `0.4xx` F4 Foreign, `0.5xx` F5 Military, `0.6xx` F6 Technology, `0.7xx` F7 Religion, `0.8xx` F8 Victory and `0.9xx` F9 Info). Other legacy captures reuse the closest current screen/category numbering when that makes comparison clearer; within a family, tab captures get their own number such as `0.400` Foreign Relations, `0.410`/`0.411` Resources and `0.800` Victories.

The supplied generic `Civ4ScreenShot####.JPG` names were replaced with descriptive names. Related captures use ordinary numbered variants such as `(1)`, `(2)` and `(3)` rather than partially inferred chronology such as `early`, unless chronology is independently established.

### Games shown

Most shots of the game screens come from a few games, so shots of one game can be compared with each other:

- A Khmer game at turn 100 (525 BC), with Yasodharapura as capital.
- An Ottoman game at turn 121 (AD 1), with Istanbul as capital and Judaism as state religion, and a second Ottoman game at turn 100.
- A Maya game at turn 200 (AD 1550), on a Large Pangaea at Monarch difficulty with 11 players.
- A game at turn 190 (AD 1450), for the city screen of Mecca.
- A 48-civilization game on a Huge map, its main menu and screens at about turn 101 and its advisors at turn 152 (AD 740), once most civilizations had met, base AdvCiv's largest size, with the 48-civilization DLL built from f1rpo's [`48civs` branch](https://github.com/f1rpo/AdvCiv/tree/48civs) (the user, 2026-11-23): its shots carry `_huge_48civs` and show screens built for far fewer players, beside SAS's `_sas48` shots of the same screens.

Every image here is shown below; the [orphan image check](/.github/workflows/README.md#builddocumentationorphan_imagespy) fails on an image that no document names, so a new legacy shot gets its place on this page.

## Advisors

### Domestic Advisor

The city list of the Khmer game, with each city's yields, specialists and production.

<img src="/_0_Legacy/Images/advisors/0.100_domestic_advisor.JPG" alt="0.100_domestic_advisor.JPG" width="250">

### Finance Advisor

The Ottoman game's treasury at 117 gold, losing 12 a turn, with its commerce, income and expense columns.

<img src="/_0_Legacy/Images/advisors/0.200_finance_advisor.JPG" alt="0.200_finance_advisor.JPG" width="250">

### Civics Advisor

The starting civics of the Ottoman game (Despotism, Barbarism, Slavery, Decentralization, Paganism), each with its upkeep.

<img src="/_0_Legacy/Images/advisors/0.300_civics_advisor.JPG" alt="0.300_civics_advisor.JPG" width="250">

### Foreign Advisor

Relations: the web of known leaders in the Khmer game, such as Elizabeth, Washington, Bismarck and Qin Shi Huang, with contact, war and Open Borders lines.

<img src="/_0_Legacy/Images/advisors/0.400_foreign_advisor_relations.JPG" alt="0.400_foreign_advisor_relations.JPG" width="250">

With 48 civilizations at turn 152, most of them met, the web packs every portrait into a half-ring, their lines crossing into a solid mass ([KI#134.6](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.6)).

<img src="/_0_Legacy/Images/advisors/0.400_foreign_advisor_relations_huge_48civs.JPG" alt="0.400_foreign_advisor_relations_huge_48civs.JPG" width="250">

Glance, with 48 civilizations: the attitude grid outgrows the window, its columns past the right edge ([KI#134](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134)).

<img src="/_0_Legacy/Images/advisors/0.401_foreign_advisor_glance%20(1)_huge_48civs.JPG" alt="0.401_foreign_advisor_glance (1)_huge_48civs.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.401_foreign_advisor_glance%20(2)_huge_48civs.JPG" alt="0.401_foreign_advisor_glance (2)_huge_48civs.JPG" width="250">

Resources: domestic resources and each leader's trades, many rows reading "Not Connected to Trade Network"; first in the Khmer game, then twice in the Ottoman game at turn 100.

<img src="/_0_Legacy/Images/advisors/0.410_foreign_advisor_resources.JPG" alt="0.410_foreign_advisor_resources.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.411_foreign_advisor_resources%20(1).JPG" alt="0.411_foreign_advisor_resources (1).JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.411_foreign_advisor_resources%20(2).JPG" alt="0.411_foreign_advisor_resources (2).JPG" width="250">

Info: each leader's civics and favorite civic.

<img src="/_0_Legacy/Images/advisors/0.420_foreign_advisor_info.JPG" alt="0.420_foreign_advisor_info.JPG" width="250">

Techs: what each leader wants, can research, will share and won't share; in the Khmer game, then in the Ottoman game.

<img src="/_0_Legacy/Images/advisors/0.430_foreign_advisor_techs%20(1).JPG" alt="0.430_foreign_advisor_techs (1).JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.430_foreign_advisor_techs%20(2).JPG" alt="0.430_foreign_advisor_techs (2).JPG" width="250">

### Espionage screen

A separate screen in base AdvCiv (`Ctrl + E`), a tab of the Foreign Diplomacy advisor in SAS: each leader's espionage points and weight, with the passive effects and missions on the right; in a normal game, then with 48 civilizations, whose two-line rows crowd each weight and "per Turn" into the next row ([KI#134.5](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.5)).

<img src="/_0_Legacy/Images/advisors/0.440_espionage_screen%20(1).JPG" alt="0.440_espionage_screen (1).JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.440_espionage_screen%20(2)_huge_48civs.JPG" alt="0.440_espionage_screen (2)_huge_48civs.JPG" width="250">

### Military Advisor

The world map beside the Khmer game's unit list, grouped by unit category.

<img src="/_0_Legacy/Images/advisors/0.500_military_advisor.JPG" alt="0.500_military_advisor.JPG" width="250">

With 48 civilizations the leader buttons fill two rows and spill a third below their panel, over the map's frame ([KI#134.4](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.4)).

<img src="/_0_Legacy/Images/advisors/0.500_military_advisor_huge_48civs.JPG" alt="0.500_military_advisor_huge_48civs.JPG" width="250">

### Technology Advisor

The tech tree at turn 0 (4000 BC), from Fishing and Hunting to the medieval techs.

<img src="/_0_Legacy/Images/advisors/0.600_technology_advisor.JPG" alt="0.600_technology_advisor.JPG" width="250">

The whole BtS and vanilla Civ4 tech trees, stitched from the Civilization Wiki rather than captured in AdvCiv.

<img src="/_0_Legacy/Images/advisors/0.610_tech_tree_merged_bts_web.webp" alt="0.610_tech_tree_merged_bts_web.webp" width="250">
<img src="/_0_Legacy/Images/advisors/0.611_tech_tree_merged_civ4_vanilla_web.webp" alt="0.611_tech_tree_merged_civ4_vanilla_web.webp" width="250">

### Religion Advisor

The religions with their founding dates and holy cities, and the Ottoman cities' faiths under Judaism.

<img src="/_0_Legacy/Images/advisors/0.700_religion_advisor.JPG" alt="0.700_religion_advisor.JPG" width="250">

### Victory screen

The four tabs in the Maya game: Victories (time, conquest, domination, cultural, space race and diplomatic progress, with Shaka leading), Settings (the game's options and the other leaders with their traits), Resolutions (the Apostolic Palace's Hinduism votes, with Darius I as resident) and Members (its voting members).

<img src="/_0_Legacy/Images/advisors/0.800_victory_screen_victories.JPG" alt="0.800_victory_screen_victories.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.810_victory_screen_settings.JPG" alt="0.810_victory_screen_settings.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.820_victory_screen_resolutions.JPG" alt="0.820_victory_screen_resolutions.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.830_victory_screen_members.JPG" alt="0.830_victory_screen_members.JPG" width="250">

### Info screen

The four tabs in the Maya game: Graph (every player's score over the whole game), Demographics (our rank against the best, worst and average rival), Top 5 Cities / Wonders (Istanbul, Babylon, Delhi, Mutal and Persepolis, beside the world wonders list) and Statistics (units built and lost, buildings and improvements).

<img src="/_0_Legacy/Images/advisors/0.900_info_screen_graph.JPG" alt="0.900_info_screen_graph.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.910_info_screen_demographics.JPG" alt="0.910_info_screen_demographics.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.920_info_screen_top_cities_wonders.JPG" alt="0.920_info_screen_top_cities_wonders.JPG" width="250">
<img src="/_0_Legacy/Images/advisors/0.930_info_screen_statistics.JPG" alt="0.930_info_screen_statistics.JPG" width="250">

The Graph tab with 48 civilizations: the lines crowd together and the legend runs up over the title and the dropdowns ([KI#134.3](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.3)).

<img src="/_0_Legacy/Images/advisors/0.900_info_screen_graph_huge_48civs.JPG" alt="0.900_info_screen_graph_huge_48civs.JPG" width="250">

## Main menu

The custom game's map selection, with Mixed_Continents chosen and the dark default globe that every map script showed then.

<img src="/_0_Legacy/Images/main_menu/0.310_main_menu_simple_game_select_map.JPG" alt="0.310_main_menu_simple_game_select_map.JPG" width="250">

The Custom Game screen set up for 48 civilizations, its player list scrolled to teams 42 to 48.

<img src="/_0_Legacy/Images/main_menu/0.330_main_menu_custom_game_huge_48civs.JPG" alt="0.330_main_menu_custom_game_huge_48civs.JPG" width="250">

## Sevopedia

The old Civilopedia, which base AdvCiv shows instead of the Sevopedia when BUG's Sevopedia option is off: one alphabetical index of every entry.

<img src="/_0_Legacy/Images/sevopedia/0.600_civilopedia_index.JPG" alt="0.600_civilopedia_index.JPG" width="250">

### Leaders and traits

Hammurabi's page (Aggressive and Organized, favorite civic Bureaucracy), then the Aggressive trait with its leaders and K-Mod's note on its faster Jail.

<img src="/_0_Legacy/Images/sevopedia/0.620_sevopedia_leaders.JPG" alt="0.620_sevopedia_leaders.JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.624_sevopedia_traits.JPG" alt="0.624_sevopedia_traits.JPG" width="250">

### Civilizations

The Viking Empire, with its starting techs, leader, unique building and unique unit.

<img src="/_0_Legacy/Images/sevopedia/0.670_sevopedia_civilizations.JPG" alt="0.670_sevopedia_civilizations.JPG" width="250">

### Units and promotions

The Melee Units chart (strength, moves and cost), the Camel Archer's page and the Flanking I promotion.

<img src="/_0_Legacy/Images/sevopedia/0.630_sevopedia_unit_chart.JPG" alt="0.630_sevopedia_unit_chart.JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.680_sevopedia_units.JPG" alt="0.680_sevopedia_units.JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.730_sevopedia_promotions.JPG" alt="0.730_sevopedia_promotions.JPG" width="250">

### Buildings and wonders

The Madrassa (the Arabian Library), the Coal Plant and the Parthenon.

<img src="/_0_Legacy/Images/sevopedia/0.690_sevopedia_buildings%20(1).JPG" alt="0.690_sevopedia_buildings (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.690_sevopedia_buildings%20(2).JPG" alt="0.690_sevopedia_buildings (2).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.690_sevopedia_buildings%20(3).JPG" alt="0.690_sevopedia_buildings (3).JPG" width="250">

### Terrains and features

Grassland, then the Jungle feature.

<img src="/_0_Legacy/Images/sevopedia/0.700_sevopedia_terrains.JPG" alt="0.700_sevopedia_terrains.JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.640_sevopedia_features.JPG" alt="0.640_sevopedia_features.JPG" width="250">

### Bonuses

Fur, then Oil with the units it enables.

<img src="/_0_Legacy/Images/sevopedia/0.650_sevopedia_bonuses%20(1).JPG" alt="0.650_sevopedia_bonuses (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.650_sevopedia_bonuses%20(2).JPG" alt="0.650_sevopedia_bonuses (2).JPG" width="250">

### Improvements

The Farm, the Workshop and the Mine, each with its yields and bonus yields.

<img src="/_0_Legacy/Images/sevopedia/0.720_sevopedia_improvements%20(1).JPG" alt="0.720_sevopedia_improvements (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.720_sevopedia_improvements%20(2).JPG" alt="0.720_sevopedia_improvements (2).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.720_sevopedia_improvements%20(3).JPG" alt="0.720_sevopedia_improvements (3).JPG" width="250">

### Technologies

Hunting, then Astronomy with AdvCiv's note on its changes.

<img src="/_0_Legacy/Images/sevopedia/0.710_sevopedia_techs%20(1).JPG" alt="0.710_sevopedia_techs (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.710_sevopedia_techs%20(2).JPG" alt="0.710_sevopedia_techs (2).JPG" width="250">

### Civics

Theocracy, then Serfdom with its K-Mod and AdvCiv notes.

<img src="/_0_Legacy/Images/sevopedia/0.740_sevopedia_civics%20(1).JPG" alt="0.740_sevopedia_civics (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.740_sevopedia_civics%20(2).JPG" alt="0.740_sevopedia_civics (2).JPG" width="250">

### Projects

The Internet, then the Apollo Program.

<img src="/_0_Legacy/Images/sevopedia/0.750_sevopedia_projects%20(1).JPG" alt="0.750_sevopedia_projects (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.750_sevopedia_projects%20(2).JPG" alt="0.750_sevopedia_projects (2).JPG" width="250">

### Specialists and corporations

The Specialists overview, then Mining Inc.

<img src="/_0_Legacy/Images/sevopedia/0.760_sevopedia_specialists.JPG" alt="0.760_sevopedia_specialists.JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.770_sevopedia_corporations.JPG" alt="0.770_sevopedia_corporations.JPG" width="250">

### Concepts, hints and shortcuts

The Happiness game concept, the Advanced Start BtS concept, AdvCiv's hints and the Map Layers shortcuts.

<img src="/_0_Legacy/Images/sevopedia/0.800_sevopedia_conceptinfos%20(1).JPG" alt="0.800_sevopedia_conceptinfos (1).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.800_sevopedia_conceptinfos%20(2).JPG" alt="0.800_sevopedia_conceptinfos (2).JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.801_sevopedia_hints.JPG" alt="0.801_sevopedia_hints.JPG" width="250">
<img src="/_0_Legacy/Images/sevopedia/0.850_sevopedia_shortcuts.JPG" alt="0.850_sevopedia_shortcuts.JPG" width="250">

## Other screens

### Diplomacy

Three leaders in the Ottoman game: Genghis Khan (Annoyed), Washington (Pleased) and Julius Caesar (Furious, offering a ceasefire).

<img src="/_0_Legacy/Images/ui_other/0.970_diplomacy_screen%20(1).JPG" alt="0.970_diplomacy_screen (1).JPG" width="250">
<img src="/_0_Legacy/Images/ui_other/0.970_diplomacy_screen%20(2).JPG" alt="0.970_diplomacy_screen (2).JPG" width="250">
<img src="/_0_Legacy/Images/ui_other/0.970_diplomacy_screen%20(3).JPG" alt="0.970_diplomacy_screen (3).JPG" width="250">

### City screen

Mecca at turn 190, building a Knight, with its worked tiles circled.

<img src="/_0_Legacy/Images/ui_other/0.990_city_screen%20(1).JPG" alt="0.990_city_screen (1).JPG" width="250">

Nidaros, a Viking city, at turn 152 in the 48-civilization game, growing and building an Axeman.

<img src="/_0_Legacy/Images/ui_other/0.990_city_screen%20(2)_huge_48civs.JPG" alt="0.990_city_screen (2)_huge_48civs.JPG" width="250">

### Scoreboard

The map with 48 civilizations: the scoreboard holds every player in one column, which runs up past the top bar and over the turn counter ([KI#134.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.2)).

<img src="/_0_Legacy/Images/ui_other/0.410_scoreboard_huge_48civs.JPG" alt="0.410_scoreboard_huge_48civs.JPG" width="250">

### Replay, Your Place in History and UN screens

With 48 civilizations: the Replay screen's event list, "Your Place in History" (the Dan Quayle screen) and the UN screen, whose ring of leaders covers its own portraits and names ([KI#134.8](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.8)).

<img src="/_0_Legacy/Images/ui_other/0.982_replay_screen_huge_48civs.JPG" alt="0.982_replay_screen_huge_48civs.JPG" width="250">
<img src="/_0_Legacy/Images/ui_other/0.983_dan_qayle_screen_huge_48civs.JPG" alt="0.983_dan_qayle_screen_huge_48civs.JPG" width="250">
<img src="/_0_Legacy/Images/ui_other/0.988_un_screen_huge_48civs.JPG" alt="0.988_un_screen_huge_48civs.JPG" width="250">

### Debug Mode screens

The Debug Info screen (`Shift + F2`), at vanilla's fixed 1024 x 768 with its Team Relations tab, and the GameFont Display screen (`Ctrl + Shift + F1`), its table empty, as in SAS until [KI#1107](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1107).

<img src="/_0_Legacy/Images/ui_other/0.986_debug_info_screen.JPG" alt="0.986_debug_info_screen.JPG" width="250">
<img src="/_0_Legacy/Images/ui_other/0.987_game_font_display.JPG" alt="0.987_game_font_display.JPG" width="250">

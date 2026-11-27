# AdvCiv-SAS documentation images

This tree contains maintained AdvCiv-SAS screenshots and other documentation/reference images.

## Menu

- [Image numbering and naming](#image-numbering-and-naming)
- [Retaking screenshots](#retaking-screenshots)

## Image numbering and naming

Numbered AdvCiv-SAS image series use the `1.x` namespace. The corresponding legacy/base-AdvCiv reference tree uses `0.x` under [`_0_Legacy/Images/`](/_0_Legacy/Images/), making the source generation visible in filenames without changing the established category numbers inside each SAS series.

For example, existing SAS families such as main-menu `1.3xx`, UI `1.4xx`, advisor `1.5xx`, Sevopedia `1.6xx+`, and late/misc screen `1.9xx` retain the same suffix/grouping that they had before the namespace split; only the leading `0.` became `1.`. Descriptive unnumbered image names remain valid where a numbered series is not useful.

Image basenames are kept unique across `_0_Legacy/Images/` and `_1_AdvCiv-SAS/Images/`. This makes screenshots easier to identify in documentation, logs, agent handoffs and filename searches without depending on the containing folder to disambiguate them.

Image folders are one per topic. When one grows large, move a coherent topic into a subfolder of it.

On 2026-11-10 `LLM/` held 119 files, so the screenshots of agents' desktop apps (Codex, the Claude app, pricing pages) moved into the subfolder [`LLM/desktop_windows/`](/_1_AdvCiv-SAS/Images/LLM/desktop_windows/), named after the [Desktop Windows Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Desktop_Windows.md) that shows them.

The art-tool samples stayed directly in `LLM/`, where `regenerate_art_samples.py` writes them and a CI check follows them.

Shots of one screen are numbered with a space, such as `1.515_military_advisor (1).JPG` to `(4).JPG`, because that is what batch renaming produces: in Q-Dir, selecting several files and renaming them gives each its ` (n)` (Windows Explorer was not tested).

- The space is less practical elsewhere: Markdown links spell it `%20`, and paths in a shell or a grep need quoting. It stays for the quick batch renames.

A shot that shows a variant of another, rather than a screen of its own, carries a suffix after its number, so a folder listing tells the variants apart without opening them, and each sorts beside the shot it varies. Batch renaming keeps these suffixes too. Examples as of 2026-11-21:

- `_sas48`: the same tab in a 48-civilization game, such as `1.513_foreign_advisor (2)_sas48_page1.JPG`, the Glance tab paged, which base AdvCiv does not do, and `(4)_sas48`, the Espionage tab's compact rows. [KI#134.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.2) to [KI#134.8](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-134.8) set them beside base AdvCiv's `_huge_48civs` shots.
  - `_page1` to `_page3` (2026-11-23): one shot per page of a paged tab, here the Glance tab's three pages of 47 rivals.
- `_individual`: the Military Advisor's Map tab with individual units shown, `1.515_military_advisor (2)_individual.JPG`.
- `_selected_dots`: the same tab with a unit type selected, its units shown as white dots on the minimap, `1.515_military_advisor (2)_selected_dots.JPG`; it replaced the plain Map tab shot, which showed nothing more (Galley, turn 201).
- `_hover`: a shot whose hover is the point, such as `1.513_foreign_advisor (1)_hover.JPG`, an attitude's breakdown on the Relations tab.
- `_late`: a late-game save, such as `1.511_domestic_advisor (4)_late.JPG`, for corporations.
- `_active` and `_built_active`: the Victory screen with a vote source built and voting.
- `_top_WB` and `_bottom_AS`: the two ends of one long table, the Changes tab's WorldBuilder edits at the top and Advanced Start buys at the bottom.
- `_blue`: a non-default setting, here the blue background, shown not as our preferred look but to show that it can be changed, since many players do not know it; the suffix also reminds whoever retakes the shot to set it first.

The two-client LAN walkthrough screenshots (`1.297_m_*`) have their own folder, [`multiple_instances/`](/_1_AdvCiv-SAS/Images/multiple_instances/), named after [README_Multiple_Instances.md](/_1_AdvCiv-SAS/Docs/README_Multiple_Instances.md) that shows them, rather than `diagnostics/`: they show the game's own menus, lobby and chat, not output from a diagnostic recorder.

## Retaking screenshots

Screenshots are taken by hand for now: choosing the save and the moment, and using the screen while doing it, is what shows its UI faults, more than a polished picture would (the user, 2026-11-21). Some shots therefore go stale between refreshes, so what each one is meant to show is recorded with it, in [`doc_screenshots.json`](/LLM_Helpers/game_runs/doc_screenshots.json) under `shows`, together with its save, screen, tabs and any hover. A stale shot is then easy to spot and to retake with the same purpose.

- Use Civ4's own screenshot (Print Screen, or `SASPilotClient.py shot`): the game area at 1920 x 1080 as JPG, as the existing images are, rather than a desktop capture with the window's frame.
  - Keep the game at 1920 x 1080, the user's own resolution, and do not maximize it on a 4K screen: a 4K shot is about four times heavier, and Civ4's art and fonts, made for far lower resolutions, show no more detail there.
- Most advisor shots come from a turn-201 game with our civ in the top 60% of the scoreboard but not leading: too weak, it has few techs, bonuses or wonders to show; too strong, the screens look one-sided. Several tradeable resources help too.
- The tech bar is in most shots, so pick a moment with a tech chosen and under way, ideally with some progress, and no anarchy: the bar then shows what SAS changed there, the tech's icon and no needless "Research:" before its name.
- Some views need their own save:
  - a late game (about turn 301) for corporations;
  - varied battles for the Battles tab: several civilizations, a mix of terrain and features, hills, a captured Worker, fights on land and at sea, and the plot buttons that jump the map to each battle; an archipelago-like map gives more sea battles than a Pangaea;
  - the Military Advisor's other tabs at turn 101 to 151, to show earlier units such as Swordsmen, with its extra views: all units shown, where each unit's line names its promotions and a Worker's line its current job, such as building a Quarry; late in a game Workers usually have nothing left to build, so their lines show no job;
  - a SAS48 game at turn 101 to 151 for what only many civilizations show, such as the Espionage tab's compact rows and the Glance tab's pages, beside the normal tabs from the turn-201 game for comparison;
  - a tiny-islands game, to show the AI's naval play.
  - for the Victory screen, a save with the United Nations or the Apostolic Palace built and voting, ideally both, so the Resolutions and Members tabs show real content and the Diplomatic rows their dates and chairs.
  - for the World Advisor's Changes tab, a game with both kinds of history: WorldBuilder edits at the top, as the newest, and the Advanced Start buys below them; an Advanced Start in an earlier era keeps its buys few enough not to fill the table.
- In debug mode, an advisor's player dropdown can switch to another leader whose view shows more, as for the Battles tab on 2026-11-21 (Zara Yaqob on an island map), and a long table can be scrolled to the slice that shows the most.
- A hover that is part of a feature belongs in the shot, chosen to show the feature at its fullest: on the Relations tab an attitude with several modifiers, and on the Bonuses tab a resource that several buyers would take at different prices, such as Gemstones at 8, 10 and 6 gold on the turn-201 game.
- The city screen shows SAS's breakdowns, so pick a city where they have values other than 0: its Great Person and culture breakdown hovered, with specialists, a religion or corporations among the culture sources, and enough builds for four full production chooser rows.
  - `1.400_city_screen (1)_spec_break_relig_gp_bldg.JPG` (turn 201: Great Person points from buildings, a religion's culture) and `(2)_spec_break_corp.JPG` (turn 301: specialists and corporations) together cover these.
- When one change touches many shots, such as the commerce sliders' background on 2026-11-21, [`doc_screenshots.py`](/LLM_Helpers/README.md#doc_screenshotspy) retakes the listed ones in bulk.

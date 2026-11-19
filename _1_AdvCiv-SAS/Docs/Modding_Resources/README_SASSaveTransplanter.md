# AdvCiv-SAS SASSaveTransplanter

How to recreate the turn-0 world of a save that the current build can no longer load, as a new save written by the current build: what the tool does, what it keeps, what the current rules change, and what was tried and measured on the way. For AI/LLM helpers and the user alike.

Any commit may break existing saves ([AGENTS.md](/AGENTS.md#unsupported-and-deprecated-features)), so a good test start or an old game stops loading as the mod changes. The transplanter does not repair the save; it carries the world over as text.

## Menu

[What it does](#what-it-does)\
[First results (2026-11-16)](#first-results-2026-11-16)\
[What it keeps and what it cannot](#what-it-keeps-and-what-it-cannot)\
&emsp;[A transplant is the same world, not the same game](#a-transplant-is-the-same-world-not-the-same-game)\
[Choices](#choices)\
[Renames and mappings](#renames-and-mappings)\
[Running an old build beside the current one](#running-an-old-build-beside-the-current-one)\
[Other directions: into base AdvCiv or an older AdvCiv-SAS](#other-directions-into-base-advciv-or-an-older-advciv-sas)\
[Other tools considered](#other-tools-considered)\
[Limits](#limits)\
[Where it stands (2026-11-16)](#where-it-stands-2026-11-16)

## What it does

[`SASSaveTransplanter.py`](/LLM_Helpers/sassavetransplanter/SASSaveTransplanter.py) runs five steps with one command:

1. **Export.** The build that wrote the save loads a copy of it and writes its world as a WorldBuilder file (`.CivBeyondSwordWBSave`) plus a facts file. WorldBuilder text names every terrain, bonus, unit, leader and tech by its XML type, such as `BONUS_WHEAT`, so no binary field and no XML index crosses versions.
2. **Type check.** [`SASSaveTransplanterWorld.py`](/LLM_Helpers/sassavetransplanter/SASSaveTransplanterWorld.py) checks every type name and leader or civilization text key against the current XML, applies the renames in [`type_renames.json`](/LLM_Helpers/sassavetransplanter/type_renames.json), and refuses to go on while a name is missing.
3. **Import.** The current build starts on that file as a scenario; the tool clicks through its three setup screens, then sets techs and random seeds as asked.
4. **Save and re-export.** SASPilot saves the game as a normal current-format save and exports the world again.
5. **Compare.** The re-export is compared with what went in, plot by plot, and the two builds' facts files are compared for what WorldBuilder text does not hold.

```bash
python LLM_Helpers/sassavetransplanter/SASSaveTransplanter.py transplant "C:/Users/PC/Documents/My Games/beyond the sword/Saves/single/old_sas_saves_0/PC BC-50000 SAS-4986 249 0.CivBeyondSwordSave" --build AdvCiv-SAS-4986 --release-tree "C:/Users/PC/Downloads/AdvCiv-SAS_LLM/chatgpt_context_sources/AdvCiv-SAS_old_versions/AdvCiv-SAS-4986" --out "C:/Users/PC/Downloads/AdvCiv-SAS_LLM/save_transplants/sas4986_249" --mapping LLM_Helpers/sassavetransplanter/type_renames.json
```

The output folder then holds:

| File | What it is |
| --- | --- |
| `preserve_T0.CivBeyondSwordSave` | the new save with the map exactly as it was, written by the current build |
| `update_T0.CivBeyondSwordSave` | the new save where the current build also placed its new map features and resources; see `--map-variants` |
| `transplant.report.json` | every step's result: dropped techs, seeds set, both comparisons, each player's techs explained |
| `source.CivBeyondSwordWBSave`, `source.facts.json` | the world as the source build wrote it |
| `transplant.CivBeyondSwordWBSave` | the same after renames and the tech policy; what the current build loaded |
| `preserve_reexport.*`, `update_reexport.*` | each variant's world as the current build wrote it back |
| `transplant.types.json`, `preserve.roundtrip.json`, `update.roundtrip.json` | the type check and each variant's WorldBuilder comparison in full |
| `update.allowed_plot_changes.json` | the plots the map update changed, with the exact lines each gained; the comparison accepts these and nothing else |
| `preserve_setup_ok/`, `update_setup_ok/` | the picture taken at the OK button before each setup click |

The copy of the old save that the source build loads is named for the run (`source_copy_<UTC>_<pid>`) and removed once that build has closed; the original is only read.

Other commands: `inventory <folders>` counts saves by the mod their header names, `export` and `import` run one side alone, `facts` compares two facts files, and `install-mod-copy` installs an old release beside the current mod without the export hook (see [Running an old build beside the current one](#running-an-old-build-beside-the-current-one)).

## First results (2026-11-16)

Run by Claude Code Fable 5.2 with a Debug-opt DLL of the day, following ChatGPT's October 2026 design and candidate script.

- **Same build, control run.** A Standard Pangaea turn-0 game of the current build, exported, loaded as a scenario and exported again: the two WorldBuilder files were byte-identical (3,168 plots, 48 teams, 48 players).
- **AdvCiv-SAS 4986, from 2025.** `PC BC-50000 SAS-4986 249 0.CivBeyondSwordSave`, a Large Pangaea with 11 civilizations, which the current build cannot load:
  - The 4986 release, installed beside the current mod as `Mods/AdvCiv-SAS-4986`, loaded the save and exported it.
  - All 4,368 plots came over unchanged: plot type, terrain, feature, improvement, rivers, area sizes, and food, production and commerce on every plot under the current rules.
  - 36 bonuses changed name only, through six documented renames: `BONUS_CATTLE` to `BONUS_COW`, `BONUS_ELEPHANTS` to `BONUS_IVORY`, `BONUS_GEMSTONES` to `BONUS_GEMS`, `BONUS_GRAPES` to `BONUS_WINE`, `BONUS_MAIZE` to `BONUS_CORN`, `BONUS_MOLLUSCS` to `BONUS_CLAM`.
  - All 11 players kept their slot, civilization, leader, handicap, starting plot, gold and units; `LEADER_MOCTEZUMA` became `LEADER_MONTEZUMA`.
  - The 18 player slots of 4986 became 48, the extra 30 empty.
  - The new save reloaded and autoplayed 40 turns with no Python error.
- **What the current rules changed**, each listed in the report:
  - Leader traits, for 8 of the 11 leaders: Suryavarman went from Expansive and Creative to Industrious and Creative.
  - Starting techs of two civilizations, by the default tech policy below: Benin from Mysticism and Fishing to Mysticism and Pottery, Korea from Mysticism and Mining to Fishing and Mining.

## What it keeps and what it cannot

- **Kept exactly:** the map (size, wrap, latitudes, every plot), bonuses, starting plots, each player's slot, civilization, leader, handicap, gold, civics and units with their level, experience, promotions and unit AI, game speed, era, calendar, options, victories and turn limits.
- **Recomputed by the current build:** everything derived, such as yields, areas, scores, traits and what a civilization's units and buildings are.
- **Not in WorldBuilder text, so new unless set:** the random seeds (see `--seeds`), the map script's name and its custom options.
  - The receiving game's map script name is the WorldBuilder file's path. The DLL classifies land-heavy and naval-heavy maps by script name first (`CvGame::recomputeMapnameHeaviness`), so a transplant falls back to the classification by starting areas (KI#42, KI#336); the 4986 Pangaea came out `landHeavy=1` that way. `CvInitCore::updatePangaea` reads the name too and is false for a transplant.
- **Turn 0 only.** A later turn's export is refused: cities, diplomacy, AI memory and timers are only partly in WorldBuilder text, and what the new rules should do with them is a separate question. A turn-0 transplant can be autoplayed forward under current rules instead.

### A transplant is the same world, not the same game

Measured on the control run: the original save and its transplant, with the same seeds set, were each autoplayed 30 turns and their SASGameRecords compared with [`compare_sasgamerecord_rng.py`](/LLM_Helpers/README.md#compare_sasgamerecord_rngpy).

- At load, the game, team and plot fingerprints matched, and so did both random states.
- The unit fingerprints did not: WorldBuilder recreates units plot by plot, so the same units get other IDs. Player 0's Settler was unit 8192 in the original and 16385 in the transplant, with the Warrior the other way round.
- The random streams then parted within turn 0 (1,245 against 1,337 calls by the first end of turn), as units act in ID order.

So compare AI changes between two games made from the same transplant, not between a transplant and its source. A possible extension would be recreating units in the source's ID order; unit birthmarks, drawn from the random stream at creation, would still differ.

## Choices

- **Purpose behind the defaults** (the user, 2026-11-16): keep the world, the civilizations and the starting state, and play them under today's rules and AI. Identical outcomes are not a goal; for the old rules, run the old build.
- **`--map-variants both`** (default): two saves, `preserve_T0` with the map exactly as it was and `update_T0` where the current build also places the map feature and resource types the source build's XML did not have, such as Marsh and Peat, on plots that hold none. `preserve` and `update` make one only, which skips the other import.
  - First called `--new-content keep/add/both`. The user found "content" vague, as it could mean units, and Codex (GPT-6.1-Sol) proposed naming what each choice produces. Renamed types are mapped in both variants; that is compatibility, not a choice.
  - **What is detected:** the source build's XML type lists are compared with the current build's, so a feature or bonus type added later is found with no change to the tool. The report's `mapTypes` step lists new and retired types for terrains, features, bonuses, improvements and routes.
  - **What is placed:** new features and new bonuses that have a placement order. Marsh uses SAS's own fractal (`addMarshesAtPlot`); any other new feature uses its XML appearance chance; a bonus uses the DLL's `addUniqueBonusType` or `addNonUniqueBonusType`, chosen by `isOneArea` as `CvMapGenerator::addBonuses` does.
  - **What is only listed:** a new terrain, improvement or route. Every plot already has a terrain, and nothing says which plots should change; changing them would reshape the world the transplant is meant to keep.
  - **Where nothing is placed:** plots that already hold a feature or bonus, starting plots and plots with units. The DLL's bonus placement knows no starts, so a bonus it puts there is taken off again and listed.
  - **The source's map script is not replayed.** A script can replace feature or bonus placement on a new map; the report's `mapScript` says which of `addFeatures`, `addBonuses` and `addBonusType` the script of that name defines today, and the update uses the general placement either way. Rivers, coasts and start normalization are never rerun.
  - **Checked plot by plot:** the map update returns every plot it changed with its content before and after. Only "new feature on a plot without one" and "new bonus on a plot without one" are accepted, and the WorldBuilder comparison then accepts exactly those lines on exactly those plots. The report's `nearStarts` counts the additions inside each start's 21 city plots.
  - **Result on 4986 save `249`** (2026-11-16): 26 Marsh and 1 Peat, on a Marsh. Camel was not added: 4986 already had it, with 6 on that map. A further 22 plots that the Marsh fractal chose are held by Forest or Jungle; on a new map Marsh is placed before Forest, so a new map of that size has more. Five starts got Marsh in their city plots, one of them 3 and the others 1.
- **`--free-grants current`** (default; first called `--techs`): each civilization's free techs and each unit's free promotions come from the current build's rules in place of the source build's. `--free-grants source` keeps exactly the source's.
  - Promotions: a 4986 Tokugawa's Archers kept Retreat I from 4986 and gained City Garrison I from the current Protective trait. The source build's free promotions are found by creating one probe unit per type in the source game, as Python cannot ask which unit combats a trait's promotion applies to.
  - Why it exists: a scenario start adds the loading build's civilization free techs to the techs in the file. The first 4986 import therefore gave Benin Mysticism and Fishing from 4986 plus Pottery from the current XML, a start neither build would deal.
  - With `current`, the techs that were 4986's free techs for that civilization leave the file first; techs from another origin, such as a handicap's AI techs, stay. The report's `techs` step says for every player whether the result is what the policy predicts.
- **`--seeds source`** (default): both random generators continue from the source game's states, so the same transplant always gives the same game. `--seeds new` keeps what the scenario start drew.
- **`--human-slot N`**: the slot the human takes; default the source save's active player. The scenario's first screen preselects the first playable slot and the tool only clicks OK, so for another slot every other slot is marked unplayable in the file. Not needed in the first runs, where the human was slot 0, and not tested.
- **`--mapping`**: renames to apply. Nothing is substituted without one, and a type or text key the current XML lacks stops the run with the names listed.

## Renames and mappings

[`type_renames.json`](/LLM_Helpers/sassavetransplanter/type_renames.json) holds only names that AdvCiv-SAS retired while the asset lived on under another name, each backed by [Deprecated XML asset names](/_1_AdvCiv-SAS/Docs/Deprecated/xml_asset_names.md). The same name maps the same way from any source version, so one flat table is enough.

- A type that was removed, split or merged is not a rename and needs a decision; the type check lists the plots and players it affects. Find when it changed in the `commit_diffs` corpus ([AGENTS.md](/AGENTS.md#source-analysis)) before adding a mapping.
- Text keys are mapped too. The first 4986 import showed the Aztec leader's name as the raw `TXT_KEY_LEADER_MOCTEZUMA`: the player block names its leader text by key, the key was retired, and only type names were being checked.
- `GlobalTypes.xml` counts as definitions: the first type check reported four `ARTSTYLE_` values as missing, although the game has them, because that file defines engine types without a `<Type>` tag.

## Running an old build beside the current one

`--release-tree` names an extracted release; the tool copies its `Assets`, `PrivateMaps`, `Resource` and `Settings` to `Mods/<--build>` once and leaves the release as it was. The extracted releases, 4986 to 6200, are under `C:\Users\PC\Downloads\AdvCiv-SAS_LLM\chatgpt_context_sources\AdvCiv-SAS_old_versions`.

- **The copy alone**, for instance to launch an old build for a bisect, is `install-mod-copy <extracted release> <folder name>`; `--dry-run` says what it would rewrite. It adds no export hook and touches no save.

  ```bash
  python LLM_Helpers/sassavetransplanter/SASSaveTransplanter.py install-mod-copy "C:/Users/PC/Downloads/AdvCiv-SAS_LLM/chatgpt_context_sources/AdvCiv-SAS_old_versions/AdvCiv-SAS-4986" AdvCiv-SAS-4986
  ```

- **Only the tool's own copies are written to.** Each copy holds `SASModCopy.json`, naming the release it came from. A folder under `Mods` without that file is refused, as is a copy made from another release, and the export hook is installed only while no Civ4 runs.
  - The first version accepted any existing folder, so `--build AdvCiv` would have patched a real AdvCiv installation (Codex (GPT-6.1-Sol)'s review, 2026-11-16).
  - After copying, files that still name the old mod folder are listed under `otherReferences` for inspection. Only the theme paths below were tested, on AdvCiv-SAS 4986; base AdvCiv 1.14 names its folder in the same three places.
- **A mod under another folder name** needs three things, which the tool does to the copy:
  - its settings file named `<folder>.ini`;
  - the theme path renamed in `Assets/XML/Art/CIV4ArtDefines_Misc.xml` (`DEFAULT_THEME_NAME`) and twice in `Resource/Civ4.thm`. Without it AdvCiv stops at startup on an "Invalid path to UI theme" dialog, as the first 4986 launch did.
- **A save names its mod folder** in its header (`Mods\AdvCiv-SAS\`), and Civ4 asks to restart into that mod when it differs. The tool gives the source build a copy of the save with the header's mod path rewritten.
  - The checksum that ends a save does not cover the mod path, so the copy needs no checksum repair; [c4lib](https://github.com/hankinsohl/c4lib)'s `checksum.cpp` lists what it covers.
- **The export is unattended.** The copy's `EntryPoints/CvEventInterface.py` gets a small wrapper around `onEvent`, and [`SASSaveTransplanterExport.py`](/LLM_Helpers/sassavetransplanter/SASSaveTransplanterExport.py) writes the world with the build's own `CvWBDesc` on the first game update after the load. It uses only the stock BtS Python API, as a 4986 build has no SASPilot or SASGameRecord.
- A save the current build still loads needs none of this: with `--build AdvCiv-SAS` SASPilot loads it and runs the same exporter. That is also how to keep a test start as text before a later commit breaks its save.
- Saves of other mods (Caveman2Cosmos, base AdvCiv) sit in the same folders under the same `PC BC-<year>` names; `inventory` reads each header's mod before anything is assigned to a build. Embedded source history starts at practical 6358 (`94f6359e2`, 2026-08-31); for older saves the filename, timestamps and a successful load on a candidate build are the evidence.

## Other directions: into base AdvCiv or an older AdvCiv-SAS

Asked by the user on 2026-11-16: can a current world go into base AdvCiv, or an old one into a newer base AdvCiv? `--destination <folder>` names the receiving build, which must be a mod copy made by `install-mod-copy`; `--build` stays the build that wrote the save, and either may be the current mod.

```bash
python LLM_Helpers/sassavetransplanter/SASSaveTransplanter.py transplant "<a current turn-0 save>" --build AdvCiv-SAS --destination AdvCiv-1.14-copy --destination-release-tree "<Mods>/AdvCiv" --mapping LLM_Helpers/sassavetransplanter/type_map_sas_to_advciv_1.14.json --map-variants preserve --out "<output folder>"
```

- **No SASPilot there.** The receiving copy's hook does the import in the game (`finishImport` in the exporter): source grants, seeds, map update, re-export and `CyGame.saveGame`, which is in the stock BtS API. The current build still imports through SASPilot.
- **Types the receiving build lacks** need a decision in the mapping file: `types` renames, `drop` leaves out.
  - [`type_map_sas_to_advciv_1.14.json`](/LLM_Helpers/sassavetransplanter/type_map_sas_to_advciv_1.14.json) maps `CIVIC_PREHISTORIC_RELIGION` and `PROMOTION_RETREAT1` back to the AdvCiv names they were renamed from (practical 4748 and 4865, found in the `commit_diffs` corpus) and drops Marsh, Peat and Camel.
  - A drop applies to plot feature, bonus, improvement and route lines, unit promotions and team techs. A type used elsewhere, such as a civilization or a leader, stops the type check until it is mapped.
- **Player slots:** current AdvCiv-SAS writes 48 team and player blocks and base AdvCiv has 18. The unused blocks after the last used one are cut; a used slot is never moved, and a file naming a cut slot stops the run.
- **Free techs and promotions** follow `--free-grants current` as in any transplant, so the receiving build deals its own. The user's view (2026-11-16): unlike civilizations, leaders and resources, these are not part of the world and may take the receiving build's settings.
- **Load check** (every transplant, off with `--no-verify-load`): the receiving build loads the new save once more and exports it, and that world must equal the one exported before saving.
  - The players' name lines are left out of that comparison: a scenario start holds them as text keys (`LeaderName=TXT_KEY_LEADER_ISABELLA`), and after a save and load the game only has the text (`LeaderName=Isabella I`). The first load check failed on exactly those lines for all 11 players.
- **Result** (2026-11-16, folder `sas_current_to_advciv114`): a current Standard Pangaea turn-0 world with 8 civilizations became a base AdvCiv 1.14 save. All 3,168 plots matched after 38 Marsh, 7 Camel and 2 Peat were dropped, techs and units were as the policy predicts, and the save reloaded in AdvCiv with the same world.
  - AdvCiv's setup screens have a lighter OK bar, so the first reference picture did not match and nothing was clicked until `setup_ok_button_advciv_1926x1120.png` was added. That bar shows the moving sky behind it: two pictures a minute apart differed by 2.65, close to the limit of 4.
- **Not tried:** a base AdvCiv save into AdvCiv-SAS or into another AdvCiv version (1.11 to 1.12), and a current world into an older AdvCiv-SAS. The first needs the reverse mapping, with Flanking I and Paganism mapped forward.

## Other tools considered

- [c4lib](https://github.com/hankinsohl/c4lib) and its `c4edit` (local source copy at `C:\Users\PC\Downloads\c4lib-master`) decode a save's binary with a schema. Not needed while the matching build can be run, which decodes its own save; it stays the fallback for a save whose build cannot run, and would need a schema for that build's layout.
- [c4recover](https://github.com/hankinsohl/c4recover) (`C:\Users\PC\Downloads\c4recover-master`) lifts the Locked Modified Assets restriction; no save needed it.
- ChatGPT's research record of 2026-10-27 compared further tools (civ4save, Civilization 4 Map Studio, WorldBuilder Studio, the BtS Map Validator, `savemap.py`); its conclusion, WorldBuilder text as the interchange format, is what was built.

## Limits

- Tested on two builds, 4986 and the current one, on Pangaea maps with the human in slot 0. Team games, scenarios with cities, `--human-slot` and saves of releases between 4986 and 6200 were not run.
- The import clicks OK on the three scenario setup screens until SASPilot answers. Before each click it compares the picture at the button with the reference pictures in [`Images/LLM/sassavetransplanter/`](/_1_AdvCiv-SAS/Images/LLM/sassavetransplanter/), such as `setup_ok_button_1926x1120.png`, and waits until the user has been idle for 1.5 s.
  - The pictures sat beside the script until 2026-11-16, when they moved there with the other pictures helpers read.
  - At a window size with no reference picture nothing is clicked: after a minute the run asks for OK to be clicked by hand and names the folder of pictures it took at the button, one of which can become the new reference. Only 1926 x 1120 windows, SAS's and base AdvCiv 1.14's, have references so far.
  - Launched this way, the Civilization step kept BtS's 850 x 569 box until a 2026-11-16 fix of the setup-size EXE patch ([KI#1082.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1082.2)). OK stays at the same corner, and the reference picture still matched on all three steps after the fix.
  - While those screens are up, Civ4 has the keyboard: letters the user typed elsewhere landed in the Leader Name box twice on 2026-11-16 ("PCdo", "PCor"). The human's name is therefore checked before anything is saved, and the import is repeated up to three times; a third failure leaves no save.
- One Civ4 at a time: every step refuses to start while a Civ4 is running.
- A source build older than its installed copy's art or DLL needs is not handled: the copy must start on this computer.

## Where it stands (2026-11-16)

On the `sassavetransplanter` branch since 2026-11-16, built on `saspilot`, which it needs: `LLM_Helpers/sassavetransplanter/`, this guide, the one-line `bNeverAlive` fix in `Assets/Python/pyWB/CvWBDesc.py` ([KI#1095](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1095)), and `requestFromJson` in `LLM_Helpers/saspilot/SASPilotCommands.py` ([KI#1096](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1096)).

Run outputs are in `Downloads/AdvCiv-SAS_LLM/save_transplants`, and the 4986 source build is installed as `Mods/AdvCiv-SAS-4986`.

- Done and run:
  - the control run, two 4986 saves (`249` Normal Noble and `251` Marathon Prince) under both `--free-grants` policies, and a 40-turn autoplay of the first, all with the first version of the tool;
  - after Codex (GPT-6.1-Sol)'s first review, `--map-variants both` on save `249` (folder `sas4986_249_variants`): both variants succeeded, with three checked OK clicks each and no retry.
  - after Codex (GPT-6.1-Sol)'s second review, the same run again with the load check (both variants pass once name text is left out of it), and a current world into base AdvCiv 1.14; see [Other directions](#other-directions-into-base-advciv-or-an-older-advciv-sas).
- Not reviewed by Codex (GPT-6.1-Sol): what followed his second review, namely the hook import (`finishImport`, `import_world_hook`), `drop_types`, `trim_unused_slots`, `rename_facts`, `check_outputs` and the load check.
- Not rerun since those changes: `--free-grants source`, and the same-build control run.
- Not done:
  - the helper's section in [LLM_Helpers/README.md](/LLM_Helpers/README.md) (the scenario setup steps were mapped on 2026-11-16, in the UI map and the [Game Runs Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Game_Runs.md#the-screens-outside-a-game));
  - this guide's Menu, markdownlint and CI;
  - a release between 4986 and 6200, a team game, `--human-slot`, a save from before 4986 or from base AdvCiv.
- Found on the way: SASPilot's `save` failed for a path holding a backslash before a "u" (`...\update_T0`), which its JSON reader took for a `\uXXXX` escape. Requests are now read by `requestFromJson`; the DLL's replies still use `fromJson`. See [KI#1096](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-1096).
- [`SASSaveTransplanterUnitState.py`](/LLM_Helpers/sassavetransplanter/SASSaveTransplanterUnitState.py) is the SASPilot `py` snippet (`SASPilotClient.py py @<file>`) that listed each player's and unit's fields, unit IDs included, in the original save and in its transplant for the fidelity comparison above.

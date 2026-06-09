# GitHub workflow checks

These files are developer/repository automation, not Civ4 runtime files.

- `build.yml` runs checks that should pass for ordinary committed builds.
- `build/` contains Python 3 build-check scripts used by `build.yml`.
- `lib/` contains shared Python 3 helpers used by workflow scripts.
- Future `release.yml` and `release/` checks can be added for release-only checks such as documentation marker cleanup and archive contents.

These scripts run outside Civ4, so they may use modern Python 3. They do not need Civ4 Python 2.4 compatibility.

## Features

According to ChatGPT-5.5:

- GitHub workflow checks live under [`.github/workflows`](/.github/workflows/).
- Workflow YAML files must stay directly in that folder (e.g. `build.yml`), while Python 3 build-check scripts live under `build/` and shared workflow helpers live under `lib/`.
- `build.yml` is the authoritative list of build checks
- The `.github/` workflow folder is development infrastructure and should stay excluded from player release archives through `.gitattributes`.

For example, this helped spot map scripts that were previously unclassified in SAS map-script heaviness defines; they are now listed explicitly for exhaustiveness.

## Current build checks

- `build/launch_guard.py`: verifies `SASDefineGuard.py` exists and its int/string sentinel constants match `GlobalDefines_advciv_sas.xml`.
- `build/xml_comments.py`: verifies XML comments under `Assets/XML` do not contain illegal double hyphen `--` and are not left unclosed.
- `build/xml_sas_text_english.py`: verifies AdvCiv-SAS-owned GameText XML files (`Assets/XML/Text/AdvCiv-SAS*.xml`) only use `<English>` language entries, except a narrow whitelist for inherited/renamed diplomacy text entries that intentionally keep old non-English fields.
- `build/define_tag_refs.py`: verifies any SAS `DefineTextVal` token that looks like a known Civ4 XML tag (e.g. bonuses, techs, building classes, units, promotions) references a real XML `<Type>` value; successful matches are printed by default, and `--quiet` suppresses them.
- `build/define_int_bounds.py`: verifies `GlobalDefines_advciv_sas.xml` integer values stay within `[-100000, 100000]`, except the launch-guard sentinel checked separately by `build/launch_guard.py`.
- `build/opening_music.py`: verifies main-menu opening music has a valid `Audio2DScripts.xml` trigger/fixed script, and if shuffle is enabled, at least one valid non-`NONE` shuffle script.
- `build/bbai_log.py`: verifies BBAI logging is disabled by default in `Assets/XML/GlobalDefines_advciv_sas.xml`.
- `build/fonts.py`: verifies shared UI font defaults are `1 / 2 / 3 / 4 / 3`.
- `build/aip.py`: verifies the Sevopedia Leader AI Personality Panel is enabled, uses the predumped cache by default, does not dump recomputed cache data to the log by default, and has a non-empty predumped cache file.
- `build/worldsizes.py`: verifies `SAS_MAGIC_WORLDSIZE_*` constants in `Assets/Python/SASMagicNumbers.py` match the `Assets/XML/GameInfo/CIV4WorldInfo.xml` order.
- `build/mapscripts.py`: verifies every playable `PrivateMaps/*.py` script is listed exactly once across the SAS map-script heaviness/coverage defines, and every listed map script exists in `PrivateMaps/`. `SAS_MAP_SCRIPT_NAMES_HEAVINESS_UNSPECIFIED` is coverage-only and is not read by the DLL; it documents map scripts intentionally left outside the explicit land-heavy / almost-all-land / naval-heavy override lists.

## Run Locally

Note for LLMs/Users: this script can also be run locally, for example on Git Bash:

```bash
py "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\.github\workflows\build\bbai_log.py"
```

## Not currently automated

The Python UI markup-escaping rule from `AGENTS.md` is intentionally not checked here yet. Raw dynamic/user text that reaches font-tagged UI renderers (`screen.setText`, `screen.setLabel`, `SASTextScale.labelText`, etc.) should keep raw text in state and escape only the display string (`&`, `<`, `>`), but broad static scanning would produce too many false positives in normal Python code, comparisons, comments, already-escaped text, and non-user-facing strings.

Only add a build check for this if it can be made targeted to a known risky path, such as a specific Sevopedia search-label rendering function or another function that displays raw user-entered text.

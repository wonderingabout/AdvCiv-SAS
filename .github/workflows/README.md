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

For example, this helped spot [map scripts that were previously unclassified in SAS map-script heaviness defines](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27198308080/job/80295526028); they are now listed explicitly for exhaustiveness. This also helped spot and fix duplicate parent XML keys [found by new GitHub workflow check](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27258698041/job/80498936912) (See if needed [KI#148](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#148---fixed-base-advciv-issue-and-one-advciv-sas-issue-of-duplicate-parent-xml-keys-found-by-new-github-workflow-check)).

## Current build checks

- `build/launch_guard.py`: verifies `SASDefineGuard.py` exists and its int/string sentinel constants match `GlobalDefines_advciv_sas.xml`.
- `build/xml_comments.py`: verifies XML comments under `Assets/XML` do not contain illegal double hyphen `--` and are not left unclosed.
- `build/xml_sas_text_english.py`: verifies AdvCiv-SAS-owned GameText XML files (`Assets/XML/Text/AdvCiv-SAS*.xml`) only use `<English>` language entries, except a narrow whitelist for inherited/renamed diplomacy text entries that intentionally keep old non-English fields.
- `build/xml_text_duplicate_tags.py`: verifies each GameText `TXT_KEY`-style `<TEXT>/<Tag>` entry under `Assets/XML/Text` is defined only once, with source line numbers for duplicate definitions. Inspired by the old AdvCiv-SAS blind [scan_xml_duplicates-3.3.py](/LLM_Helpers/scan_xml_duplicates-3.3.py) (see [Legacy XML duplicate discovery scanner (``scan_xml_duplicates-3.3.py``)](/LLM_Helpers/README.md#legacy-xml-duplicate-discovery-scanner-scan_xml_duplicates-33py)). This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27332010214/job/80746523894) and fix XML text duplicate errors. See [KI#149](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#149---fixed-base-advciv-issue-duplicate-xml-text-tags-found-by-new-github-workflow-check).
- `build/xml_parent_duplicate_keys.py`: verifies parent-style XML objects are not defined twice with the same key, such as duplicate `*Info` `<Type>` values or duplicate audio `ScriptID` / `SoundID` entries. This intentionally does not check child/list duplicate semantics, which can be more context-dependent.
- `build/xml_child_duplicate_report.py`: checks suspicious duplicate child/list XML entries inside the same parent object, failing on high-confidence duplicates such as duplicate flavors, leader memory/contact keys, civilization city names, and unit/promotion lists; reports lower-confidence duplicates such as exact duplicate event trigger `Text + Era` entries without failing, prints source line numbers, and hides known allowed/noisy duplicates such as weighted goody huts and reused world-picker art paths unless run with `--show-ignored`. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27336768909/job/80762873956) and fix XML text duplicate errors. See [KI#150](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#150---fixed-base-advciv-issue-and-some-advciv-sas-priority-duplicate-xml-childlist-entries-found-by-new-github-workflow-check).
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

## Dependabot

[`.github/dependabot.yml`](/.github/dependabot.yml) enables Dependabot version updates for GitHub Actions. It is currently scheduled daily for initial testing so outdated action versions such as `actions/checkout` and `actions/setup-python` can produce an update PR quickly. If this becomes noisy, change the schedule to weekly or monthly.

For example, as of 2026-06-09, this was added to help address the following GitHub Actions maintenance warning, after which Dependabot was added to track action-version updates automatically:

```text
build-checks
Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, actions/setup-python@v5. Actions will be forced to run with Node.js 24 by default starting June 16th, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/

Which it fixed here: [dependabot@PR#24](https://github.com/wonderingabout/AdvCiv-SAS/pull/24).

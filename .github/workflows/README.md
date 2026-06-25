# GitHub workflow checks

These files are developer/repository automation, not Civ4 runtime files.

- `python-ruff.yml` shows full Ruff output and runs critical Ruff Python sanity checks.
- `python24-compile.yml` runs the real CPython 2.4 parser/bytecode compiler through Docker.
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

## Python Ruff workflow

[`python-ruff.yml`](/.github/workflows/python-ruff.yml) runs latest Ruff through `astral-sh/ruff-action` as a separate Python sanity workflow. It intentionally runs isolated from [`ruff.toml`](/ruff.toml), because `ruff.toml` is for the user's VS Code Ruff extension and local editing signal/noise, not for CI strictness. The local config keeps legacy Civ4/Python 2.4 false-positive noise manageable in the user's IDE, while GitHub should show the broader repository picture.

The workflow first prints the full `ruff check . --isolated --select ALL` grouped report so all findings are visible, then fails on a practical critical gate (ignoring only those deemed non-critical and too noisy after empirical review) for syntax/parse errors and Pyflakes bug checks. The first GitHub run showed that only a few rules were clearly too noisy, so this is the first cautious narrowing step; narrow further only from actual failure output. For example, this helped spot shadowed duplicate Python callbacks in the base Civ4 `Oasis.py` map script (see [KI#164](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#164---fixed-base-civ4-oasis-map-script-had-shadowed-python-callbacks-found-by-the-python-ruff-github-actions-workflow)) and a dormant undefined `Point` (instead of `PointLayout`) helper in `RectLayout.py` (see [KI#165](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#165---fixed-base-advciv-bug-dormant-rectlayout-upperleft-helper-returned-undefined-point-instead-of-pointlayout-found-by-python-ruff-github-actions-workflow)).

Note: Separate artifacts were considered, which according to ChatGPT-5.5 are as of now limited to 500MB for free users, but GitHub Actions already lets us view on the web browser/URL and download workflow logs as ZIP (as of now right click "Download Log Archive"), so we do not need and so do not use artifact storage for now.

## Python 2.4 compile workflow

[`python24-compile.yml`](/.github/workflows/python24-compile.yml) runs [`build/python24_compile.py`](#buildpython24_compilepy) inside `ghcr.io/wonderingabout/python-2.4:2.4.6`, built from the separate [`wonderingabout/python-2.4-docker`](https://github.com/wonderingabout/python-2.4-docker) Docker-image recipe. It checks `Assets/Python` and `PrivateMaps` with the real CPython 2.4 parser/bytecode compiler, which is closer to Civ4's embedded Python than Ruff or modern Python 3.

This is intentionally a syntax/compile compatibility check only: it does not launch Civ4, run gameplay code, import `CvPythonExtensions`, or validate engine-only runtime objects. It uses `docker run` after normal checkout instead of a job-level container so GitHub Actions and checkout still run on the ordinary runner, while the old image only needs to provide Python 2.4. A [test run confirmed it fails](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27897204427) on Python 2.5+ ternary syntax such as `SAS_MAGIC_PY24_COMPILE_BREAK_TEST = 1 if True else 0` in `Assets/Python/SASMagicNumbers.py`.

## Current build checks

- [`build/temp_files.py`](#buildtemp_filespy)
- [`build/line_endings.py`](#buildline_endingspy)
- [`build/assets_dlls.py`](#buildassets_dllspy)
- [`build/global_defines_nonempty.py`](#buildglobal_defines_nonemptypy)
- [`build/launch_guard.py`](#buildlaunch_guardpy)
- [`build/define_int_bounds.py`](#builddefine_int_boundspy)
- [`build/xml_comments.py`](#buildxml_commentspy)
- [`build/xml_suspicious_angle_tags.py`](#buildxml_suspicious_angle_tagspy)
- [`build/xml_suspicious_text_chars.py`](#buildxml_suspicious_text_charspy)
- [`build/xml_sas_text_english.py`](#buildxml_sas_text_englishpy)
- [`build/xml_text_duplicate_tags.py`](#buildxml_text_duplicate_tagspy)
- [`build/xml_parent_duplicate_keys.py`](#buildxml_parent_duplicate_keyspy)
- [`build/xml_child_duplicates.py`](#buildxml_child_duplicatespy)
- [`build/tech_columns.py`](#buildtech_columnspy)
- [`build/civ_specific_asset_techs.py`](#buildciv_specific_asset_techspy)
- [`build/civ_specific_not_weaker.py`](#buildciv_specific_not_weakerpy)
- [`build/define_tag_refs.py`](#builddefine_tag_refspy)
- [`build/raw_getinfotype.py`](#buildraw_getinfotypepy)
- [`build/opening_music.py`](#buildopening_musicpy)
- [`build/bbai_log.py`](#buildbbai_logpy)
- [`build/fonts.py`](#buildfontspy)
- [`build/detail_manager.py`](#builddetail_managerpy)
- [`build/aip.py`](#buildaippy)
- [`build/aip_predump_values.py`](#buildaip_predump_valuespy)
- [`build/worldsizes.py`](#buildworldsizespy)
- [`build/mapscripts.py`](#buildmapscriptspy)
- [`build/python24_compile.py`](#buildpython24_compilepy)

### `build/temp_files.py`

Verifies `CvGameCoreDLL/Project/temp_files/` exists through its zero-byte tracked placeholder file and is otherwise empty, verifies `.gitignore` does not hide it, and allows only the matching `.gitattributes` `export-ignore` rules used to keep it out of GitHub Download ZIP / git archive release archives. This helps catch stale fast-compile temp files. We check this because we suspect fast compiles can be unreliable, and also helps catch forgetting to replace the committed DLL after compiling (see also [KI#38](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#38---no-idea-why-but-sometimes-compile-mysteriouslystrangelyinconsistently-fails-and-recompiling-succeeds-underwith-but-exact-same-source-files-if-i-am-not-mistaken-but) and [KI#38.2](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#382---weird-dll-xml-errors-at-launch-solved-by-recompiling-the-exact-same-dll-cosmic-ray-2-or-something-else-maybe-or-whatever-maybe-but)).

### `build/line_endings.py`

Verifies active text-like source/config/docs files do not mix CRLF and LF line endings within the same file and that non-empty files end with a newline. This is intentionally a reporting/fail-fast build check only; for local reviewed cleanup, use [`LLM_Helpers/fix_line_endings.py`](/LLM_Helpers/fix_line_endings.py). Generated/reference helper folders such as `LLM_Helpers/outputs` are excluded to avoid noise from old reports/diffs.

The script prints its scan mode. In a normal Git checkout it lists tracked files with `git ls-files` and checks the current checked-out bytes. In a plain exported folder, such as an extracted light-source zip without `.git`, it falls back to scanning the configured active source/doc folders directly.

Before the first cleanup, this checker found 79 local worktree issues, while GitHub Actions reported only 19. Comparing local bytes with `git show :path` showed that some local mixed-EOL files were clean LF-only in Git's indexed blob (e.g., `BugInit.py`) while true CI failures stayed mixed in both (e.g., `Pangaea.py`).

Fixing all local findings updated 78 worktree files, but staging kept only the 19 stored-content changes that Git/CI saw. This makes local output useful cleanup/export guidance, while staged/GitHub output is the authoritative committed-content failure set.

Note: later on, we noticed a line endings test failed locally:

```log
FAIL text line-ending hygiene
  - .github/workflows/build/aip_predump_values.py: has mixed line endings: CRLF=560, LF=2, lone_CR=0
  - Assets/Python/Contrib/Sevopedia/SevoPediaLeaderAIPValues.py: has mixed line endings: CRLF=485, LF=1, lone_CR=0
  ```

The LF-only lines are just blank lines:

```log
.github/workflows/build/aip_predump_values.py
  LF-only line 393
  LF-only line 440

Assets/Python/Contrib/Sevopedia/SevoPediaLeaderAIPValues.py
  LF-only line 334
```

But it passed on [GitHub Actions test](https://github.com/wonderingabout/AdvCiv-SAS/pull/29/commits/c0e4c7624edafb022946267c606692071784dbf0): GitHub Actions checks its own post-checkout bytes, so local/exported mixed line endings can still need cleanup even when CI passes. When this happens in a Git checkout, the script notes failing worktree files that are already clean in the Git index. To make this clearer, the checker now prints its scan mode and can note when a failing worktree file is already clean in the Git index.

### `build/assets_dlls.py`

Recursively verifies `Assets` contains only the two expected DLL files (`Assets/CvGameCoreDLL.dll` for the main/48-civ DLL and `Assets/CvGameCoreDLL_18_civs_DLL.dll` for the 18-civ DLL), and verifies the 18-civ DLL is not larger than the main DLL by byte size.

### `build/global_defines_nonempty.py`

Verifies GlobalDefines XML files under `Assets/XML` have `<Define>` entries with non-empty `<DefineName>` values, unique define names within each file, and exactly one non-empty value field (normally `iDefineIntVal`, `fDefineFloatVal`, or `DefineTextVal`). This preventively catches accidental blank define values. We check this because we suspect they may possibly cause unclear errors; for intentional "empty" string-like behavior, explicit values such as `NONE` are clearer and more reliable.

### `build/launch_guard.py`

Verifies `SASDefineGuard.py` exists and its int/string sentinel constants match `GlobalDefines_advciv_sas.xml`.

### `build/define_int_bounds.py`

Verifies `GlobalDefines_advciv_sas.xml` integer values stay within `[-100000, 100000]`, except specific intentional outliers such as the launch-guard sentinel checked by [`build/launch_guard.py`](#buildlaunch_guardpy) and the high bonus-Fallout scrub worker value.

### `build/xml_comments.py`

Verifies XML comments under `Assets/XML` do not contain illegal double hyphen `--` and are not left unclosed.

### `build/xml_suspicious_angle_tags.py`

Verifies raw XML files under `Assets/XML` do not contain suspicious malformed-looking tag punctuation such as doubled opening angles or extra closing angles after tags, catching valid-but-wrong text like `<French>>...`. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27342682844/job/80783239087) and fix suspicious malformed-looking XML tag punctuation. See [KI#151](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#151---fixed-base-advciv-issue-suspicious-malformed-looking-xml-angle-tags-found-by-new-github-workflow-check).

### `build/xml_suspicious_text_chars.py`

Verifies XML text does not contain high-confidence corrupted characters such as `?` inside a word-like token, Unicode replacement characters in active/non-ignored text, common mojibake fragments, or raw control characters; inherited non-English replacement-character noise is hidden by default and can be listed with `--show-ignored`. This intentionally does not enforce broader typography policy such as em dashes, curly quotes, or accented letters. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27400470104/job/80977135402) and fix the corresponding errors. See [KI#152](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#152---fixed-suspicious-replacement-question-marks-in-lengthy-sevopedia-xml-found-by-new-github-workflow-check).

### `build/xml_sas_text_english.py`

Verifies AdvCiv-SAS-owned GameText XML files (`Assets/XML/Text/AdvCiv-SAS*.xml`) only use `<English>` language entries, except a narrow whitelist for inherited/renamed diplomacy text entries that intentionally keep old non-English fields.

### `build/xml_text_duplicate_tags.py`

Verifies each GameText `TXT_KEY`-style `<TEXT>/<Tag>` entry under `Assets/XML/Text` is defined only once, with source line numbers for duplicate definitions. Inspired by the old AdvCiv-SAS blind [scan_xml_duplicates-3.3.py](/LLM_Helpers/scan_xml_duplicates-3.3.py) (see [Legacy XML duplicate discovery scanner (``scan_xml_duplicates-3.3.py``)](/LLM_Helpers/README.md#legacy-xml-duplicate-discovery-scanner-scan_xml_duplicates-33py)). This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27332010214/job/80746523894) and fix XML text duplicate errors. See [KI#149](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#149---fixed-base-advciv-issue-duplicate-xml-text-tags-found-by-new-github-workflow-check).

### `build/xml_parent_duplicate_keys.py`

Verifies parent-style XML objects are not defined twice with the same key, such as duplicate `*Info` `<Type>` values or duplicate audio `ScriptID` / `SoundID` entries. This intentionally does not check child/list duplicate semantics, which can be more context-dependent.

### `build/xml_child_duplicates.py`

Checks suspicious duplicate child/list XML entries inside the same parent object, failing on high-confidence duplicates such as duplicate flavors, leader memory/contact keys, civilization city names, and unit/promotion lists; reports lower-confidence duplicates such as exact duplicate event trigger `Text + Era` entries without failing, prints source line numbers, and hides known allowed/noisy duplicates such as weighted goody huts and reused world-picker art paths unless run with `--show-ignored`. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27336768909/job/80762873956) and fix XML text duplicate errors. See [KI#150](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#150---fixed-base-advciv-issue-and-some-advciv-sas-priority-duplicate-xml-childlist-entries-found-by-new-github-workflow-check).

### `build/tech_columns.py`

Verifies all techs in the same tech-tree column (`iGridX`) share the same core column values, currently `iCost` and `iAsset`; different `iGrid` column rows in the same column are allowed, but same-timing techs should normally have identical research cost and asset/trade valuation.

### `build/civ_specific_asset_techs.py`

Verifies civ-specific building and unit assets do not require a later starting tech-tree column (`iGridX`) or an earlier obsolete tech-tree column than the generic asset they replace; same-column parallel tech variation is allowed for flavor. This helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27463441180/job/81181382278) and fix corresponding errors; e.g., `iGridX=3 has multiple iAsset values: iAsset=8: TECH_THE_WHEEL(GridY=5), TECH_WRITING(GridY=7), TECH_MONARCHY(GridY=11), TECH_METAL_CASTING(GridY=19); iAsset=16: TECH_SAILING(GridY=1)`.

Verifies civ-specific building and unit assets do not require a later starting tech-tree column (`iGridX`) or an earlier obsolete tech-tree column than the generic asset they replace; same-column parallel tech variation is allowed for flavor. For example, this helped [spot](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27461191223/job/81175197986) and fix `BUILDING_AZTEC_SACRIFICIAL_ALTAR: building class BUILDINGCLASS_MONUMENT replacement uses later tech column than default BUILDING_MONUMENT: TECH_CALENDAR (GridX=2, GridY=11) after TECH_MYSTICISM (GridX=1, GridY=11)`, but `BUILDING_JAPAN_DOUJOU` (JAIL) requiring `TECH_MEDITATION` parallel (`iGridY=9`) to `TECH_CONSTITUTION` required by the generic `BUILDING_JAIL` is fine so it does not need a fix. Similarly for `BUILDING_EGYPTIAN_OBELISK: building class BUILDINGCLASS_MONUMENT replacement uses earlier ObsoleteTech column than default BUILDING_MONUMENT: TECH_BROADER_EDUCATION (GridX=10, GridY=11) before TECH_LIBERALISM (GridX=13, GridY=11)` being obsolete sooner and so weaker than the generic monument so fixed it (obsolete is now same `GridY` or later).

### `build/civ_specific_not_weaker.py`

Verifies civ-specific unit/building replacements are not weaker than their generic class defaults. Unit replacements fail if their `iCombat` or `iPower` is lower than the default unit for the same `UnitClass`; building replacements fail if their `iPower` is lower than the default building for the same `BuildingClass`.

### `build/define_tag_refs.py`

Verifies any SAS `DefineTextVal` token that looks like a known Civ4 XML tag (e.g. bonuses, techs, building classes, units, promotions) references a real XML `<Type>` value; successful matches are printed by default, and `--quiet` suppresses them.

### `build/raw_getinfotype.py`

Verifies runtime Python files do not add raw `getInfoTypeForString(...)` or `CvUtil.findInfoTypeNum(...)` lookups outside strict helper implementations and narrow legacy/dynamic exceptions. Use `getInfoTypeOrFail(...)` or `findInfoTypeNumOrFail(...)` for literal/static XML tag lookups so missing or renamed tags fail loudly. Python comments and string literals are ignored, so code-generation strings such as those in `savemap.py` are not flagged by this check. This allowed to [find](https://github.com/wonderingabout/AdvCiv-SAS/actions/runs/27464773794/job/81185039717) this alternative lookup and that it needed an or fail handling too: now fixed.

### `build/opening_music.py`

Verifies main-menu opening music has a valid `Audio2DScripts.xml` trigger/fixed script, and if shuffle is enabled, at least one valid non-`NONE` shuffle script.

### `build/bbai_log.py`

Verifies BBAI logging is disabled by default in `Assets/XML/GlobalDefines_advciv_sas.xml`.

### `build/fonts.py`

Verifies shared UI font defaults are `1 / 2 / 3 / 4 / 3`.

### `build/detail_manager.py`

Verifies `Assets/XML/Misc/CIV4DetailManager.xml` `CITYBILLBOARD_SCALE` keys match the committed shared UI font/default billboard-scale defines and the base values used by `Assets/Python/SASBillboardScale.py`, catching stale rewritten billboard scales after temporary UI upscaling.

### `build/aip.py`

Verifies the Sevopedia Leader AI Personality Panel is enabled, uses the predumped cache by default, does not dump recomputed cache data to the log by default, and has a non-empty predumped cache file.

### `build/aip_predump_values.py`

Validates effective AIP predump values outside Civ4. It compares committed entries in `Assets/Python/Contrib/Sevopedia/SevoPediaLeaderCachePredumped.py` against values reconstructed from `Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`, mirroring the narrow DLL path needed for these values: `LEADER_DEFAULTS` copy behavior, `CvLeaderHeadInfo::GetChildXmlValByName` missing-tag defaults, primitive array/list loading, and `UWAI::applyPersonalityWeight` with `UWAI_PERSONALITY_PERCENT`.

This script is intentionally separate from [`build/aip.py`](#buildaippy). `aip.py` remains the lightweight release-safety check, while this deeper value mirror checks the committed predump against effective XML+DLL-style values. It currently checks full cached tuples for direct scalar getter keys, scalar attitude-threshold getters, flavors, no-war attitude probabilities, contact aggregate values, and displayed positive/negative memory aggregate values. Contact and memory aggregate formulas are shared with the in-game AIP helper code; unit AI modifiers and improvement modifiers are not checked because they are not currently displayed/predumped. The script fails by default when mismatches or missing/unparsed entries are found; use `--allow-mismatch` only for exploratory/debug runs such as `--no-uwai`.

Practical predump workflow: this checker reconstructs the same AIP cache tuples outside Civ4 through the shared provider-based cache builder, using an XML/UWAI provider instead of the in-game `gc`/DLL provider. This gives CI and local scripts an automatic way to detect stale committed predump data without launching Civ4. If the checker reports stale predump data, refresh the committed file manually for now by temporarily setting `SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_CACHE_USE_PREDUMPED = 0` and `SAS_SEVOPEDIA_LEADER_AI_PERSONALITY_CACHE_DUMP_TO_LOG = 1`, opening the Leaders / AI Personality panel once, copying the generated `PythonDbg.log` block into `SevoPediaLeaderCachePredumped.py`, restoring the defaults, and rerunning this checker.

This full-tuple check is intentionally stricter than a raw-value-only comparison. During development, the earlier numeric-only check passed, but the tuple check found 394 stale predump entries after shared/runtime AIP label metadata had changed. The underlying values were mostly correct, but many committed labels were missing updated `%` text, such as `Build Unit (52)` instead of `Build Unit % (52)`. Refreshing `SevoPediaLeaderCachePredumped.py` fixed those mismatches and confirmed that this check catches display-cache drift, not just numeric-value drift.

Example local command (Git Bash):

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && python .github/workflows/build/aip_predump_values.py
```

### `build/worldsizes.py`

Verifies hardcoded C++/Python `WorldSizeTypes` enum exposure matches the `Assets/XML/GameInfo/CIV4WorldInfo.xml` order, and that old `SAS_MAGIC_WORLDSIZE_*` Python runtime references have not returned.

### `build/mapscripts.py`

Verifies every playable `PrivateMaps/*.py` script is listed exactly once across the SAS map-script heaviness/coverage defines, and every listed map script exists in `PrivateMaps/`. `SAS_MAP_SCRIPT_NAMES_HEAVINESS_UNSPECIFIED` is coverage-only and is not read by the DLL; it documents map scripts intentionally left outside the explicit land-heavy / almost-all-land / naval-heavy override lists.

### `build/python24_compile.py`

Compile-checks runtime Civ4 Python files under `Assets/Python` and `PrivateMaps` with CPython 2.4 through [`python24-compile.yml`](/.github/workflows/python24-compile.yml). It uses `py_compile` on each source file but redirects bytecode to a temporary directory so the workflow catches real Python 2.4 parser/bytecode errors without writing `.pyc` files into the mounted repository. This check complements Ruff: Ruff gives modern static diagnostics, while this workflow confirms the old parser still accepts the files Civ4 can load.

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
```

Which it fixed here: [dependabot@PR#24](https://github.com/wonderingabout/AdvCiv-SAS/pull/24).

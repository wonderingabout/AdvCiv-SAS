# External helper tools

Primary audience: coding agents (Claude Code, Codex, etc.) invoking these scripts on the user's behalf. Prefer agent-spec bullets over prose; show example output where it clarifies the contract.

This folder contains external helper scripts, mostly Python 3, for tasks outside Civ4's embedded Python runtime. These scripts are meant for LLM-assisted workflows, balancing workflows, code review, refactoring support, report generation, and other tooling.

Important distinction:

- Helper scripts may use modern Python 3.
- Output files do not automatically need to be Civ4 Python 2.4-compatible.
- Only source-rewrite helpers that modify Python files loaded by Civ4 must preserve Python 2.4-compatible target code.
- Text reports, tuning reports, XML summaries, and other external artifacts only need to be useful and accurate for their workflow.

Always review diffs before committing generated source changes.

## Menu

- [Source-rewrite helpers](#source-rewrite-helpers)
  - [`collapse_multiline_calls.py`](#collapse_multiline_callspy)
  - [`collapse_multiline_calls2.py`](#collapse_multiline_calls2py)
  - [`fix_matrix_indent.py`](#fix_matrix_indentpy)
  - [`collapse_multiline_brackets.py`](#collapse_multiline_bracketspy)
  - [`wrap_python2_prints_for_linting.py`](#wrap_python2_prints_for_lintingpy)
- [CvMainInterface single-line cleanup reference scripts](#cvmaininterface-single-line-cleanup-reference-scripts)
  - [`singleline_pass.py`](#cvmaininterface-single-line-cleanup-reference-scripts)
  - [`singleline_pass_comments.py`](#cvmaininterface-single-line-cleanup-reference-scripts)
  - [`singleline_pass3_comments_and_long.py`](#cvmaininterface-single-line-cleanup-reference-scripts)
  - [`comment_cleanup_pass_v2.py`](#cvmaininterface-single-line-cleanup-reference-scripts)
- [Game speed helper scripts](#game-speed-helper-scripts)
  - [`compare_speed_summaries.py`](#compare_speed_summariespy)
  - [`autotune_speed_from_xml.py`](#autotune_speed_from_xmlpy)
- [Game info comparison helpers](#game-info-comparison-helpers)
  - [`compare_handicap_infos.py`](#compare_handicap_infospy)
- [Static audit helpers](#static-audit-helpers)
  - [`audit_define_keys.py`](#audit_define_keyspy)
  - [`audit_unused_text_keys.py`](#audit_unused_text_keyspy)
- [Workflow rule for timeline tuning](#workflow-rule-for-timeline-tuning)
- [General notes for future LLM helpers](#general-notes-for-future-llm-helpers)

## Source-rewrite helpers

### `collapse_multiline_calls.py`

Conservative source-rewrite helper for Python files.

- Collapses multiline call-like statements and simple parenthesized return expressions into one line.
- Useful for making Civ4 Python calls easier to grep/review and for reducing harmless continuation-indent noise.
- Skips statements containing comments, multiline strings, explicit backslash continuations, and large list/dict/table assignments.
- Preserves line endings and refuses to write if significant token sequence changes.
- Safer than `collapse_multiline_brackets.py` for broad cleanup because it does not collapse arbitrary bracketed dictionaries/lists/tables.
- Still review the diff before committing. The goal is searchability and reviewability, not general formatting.
- For broad passes, prefer active mod/helper source. Avoid reference/comparison folders such as `_0_Common_Docs` unless the task explicitly needs them.
- If the diff starts touching large data tables, comments, fragile indentation, or hard-to-review inherited files, stop and narrow the target set.

Single-file examples:

```powershell
python LLM_Helpers\collapse_multiline_calls.py PrivateMaps\Mirror.py
python LLM_Helpers\collapse_multiline_calls.py PrivateMaps\Mirror.py --in-place
python LLM_Helpers\collapse_multiline_calls.py PrivateMaps\Mirror.py --diff
```

Broad run workflow from PowerShell. The helper processes one file at a time, so this loop copies a temporary runner, applies it to every tracked or untracked `.py` file except the runner itself, then removes the runner. The helper can also be run on a single file from PowerShell or Git Bash; this broad pass was tested with PowerShell for file generation, then Git Bash for staged diff output.

```powershell
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS"; Copy-Item "LLM_Helpers\collapse_multiline_calls.py" "LLM_Helpers\collapse_multiline_calls_TEMP_RUNNER.py"; $script=(Resolve-Path "LLM_Helpers\collapse_multiline_calls_TEMP_RUNNER.py").Path; Get-ChildItem -Recurse -File -Filter *.py | Where-Object { $_.FullName -ne $script } | ForEach-Object { py $script $_.FullName --in-place }; Remove-Item $script; git diff --ignore-space-at-eol --stat; git diff --check
```

Broad staged-review workflow from Git Bash after the files were modified. This stages only `.py` files, writes a timestamped staged diff under `LLM_Helpers/outputs`, prints the staged stat, and runs the staged whitespace check:

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && mkdir -p LLM_Helpers/outputs && ts=$(date +%Y%m%d_%H%M%S) && out="LLM_Helpers/outputs/staged_collapse_multiline_calls_${ts}.diff" && git ls-files -z -m -o --exclude-standard '*.py' | xargs -0 -r git add && git diff --cached --ignore-space-at-eol > "$out" && git diff --cached --ignore-space-at-eol --stat && git diff --cached --check && echo "wrote $out"
```

### `collapse_multiline_calls2.py`

Targeted second-pass source-rewrite helper.

- Separate follow-up to `collapse_multiline_calls.py`; keep the first helper as the committed known-good pass 1.
- Collapses multiline `def` headers such as `def __init__(..., ...):`.
- Collapses selected long map-generation calls such as `generatePlotsInRegion(...)`, `generateCenter(...)`, and `generateCenterPlot(...)`.
- Skips comments inside the collapsed statement, multiline strings, explicit backslash continuations, list/dict/table assignments, calls whose first argument is a list/dict literal, and long boolean return cascades beyond the conservative line cap.
- Preserves line endings and refuses to write if significant token sequence changes.
- Intended for narrow cleanup after the first collapse pass, not as a general formatter.

Tested broad run workflow from Git Bash. The helper itself processes one file at a time, but this was tested as a broad repo pass using a temporary runner. The loop applies it to every tracked or untracked `.py` file except the runner itself, removes the runner, stages Python changes, writes a timestamped staged diff under `LLM_Helpers/outputs`, prints the staged stat, and runs the staged whitespace check:

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && cp "LLM_Helpers/collapse_multiline_calls2.py" "LLM_Helpers/collapse_multiline_calls2_TEMP_RUNNER.py" && runner="LLM_Helpers/collapse_multiline_calls2_TEMP_RUNNER.py"; { git ls-files -z '*.py'; git ls-files -z -o --exclude-standard '*.py'; } | while IFS= read -r -d '' f; do [ "$f" = "$runner" ] && continue; py "$runner" "$f" --in-place; done; rm "$runner"; mkdir -p LLM_Helpers/outputs; ts=$(date +%Y%m%d_%H%M%S); out="LLM_Helpers/outputs/staged_collapse_multiline_calls2_${ts}.diff"; git ls-files -z -m -o --exclude-standard '*.py' | xargs -0 -r git add; git diff --cached --ignore-space-at-eol > "$out"; git diff --cached --ignore-space-at-eol --stat; git diff --cached --check; echo "wrote $out"
```

### `fix_matrix_indent.py`

Targeted matrix/data indentation cleanup helper.

- Normalizes mixed tab/space indentation inside multiline list/dict/tuple assignment blocks.
- Intended mainly for old Civ4 map-script matrix/data blocks such as `templates = {...}`, region tables, coordinate tables, and similar static data.
- Does not collapse lines; keeps large matrices and tables multiline for readability.
- Does not touch the assignment's first line indentation, because that may be real Python block indentation.
- Converts mixed leading indentation inside the data block to spaces-only indentation.
- Uses tabsize 4 by default, matching the intended editor-style alignment for these visual matrix/data blocks better than Python's historical tabsize 8.
- Strips trailing whitespace only on lines whose leading indentation was changed.
- Preserves line endings and refuses to write if significant token sequence changes.
- Intended for Ruff `E101` cleanup in matrix/data blocks, not as a general indentation fixer.

Tested broad run workflow from Git Bash. The helper processes one file at a time, so this loop copies a temporary runner, applies it to every tracked or untracked `.py` file except the runner itself, removes the runner, stages Python changes, writes a timestamped staged diff under `LLM_Helpers/outputs`, prints the staged stat, and runs the staged whitespace check:

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && cp "LLM_Helpers/fix_matrix_indent.py" "LLM_Helpers/fix_matrix_indent_TEMP_RUNNER.py" && runner="LLM_Helpers/fix_matrix_indent_TEMP_RUNNER.py"; { git ls-files -z '*.py'; git ls-files -z -o --exclude-standard '*.py'; } | while IFS= read -r -d '' f; do [ "$f" = "$runner" ] && continue; py "$runner" "$f" --in-place; done; rm "$runner"; mkdir -p LLM_Helpers/outputs; ts=$(date +%Y%m%d_%H%M%S); out="LLM_Helpers/outputs/staged_fix_matrix_indent_${ts}.diff"; git ls-files -z -m -o --exclude-standard '*.py' | xargs -0 -r git add; git diff --cached --ignore-space-at-eol > "$out"; git diff --cached --ignore-space-at-eol --stat; git diff --cached --check; echo "wrote $out"
```

In the tested broad PrivateMaps pass, this produced a high-impact Ruff cleanup: for example, `Wheel.py` dropped from roughly 400 Ruff findings to 15, while the staged diff was still mostly mechanical whitespace-only matrix indentation replacement.

```bash
LLM_Helpers/fix_matrix_indent.py     |  290 ++++++++
PrivateMaps/Archipelago.py           |  186 +++---
PrivateMaps/BTG_Lagoon.py            |  220 +++----
PrivateMaps/Balanced.py              |    4 +-
PrivateMaps/Custom_Continents.py     | 1200 +++++++++++++++++-----------------
PrivateMaps/Equal_Islands_V2_beta.py |  188 +++---
PrivateMaps/Great_Plains.py          |    4 +-
PrivateMaps/Hub.py                   |  738 ++++++++++-----------
PrivateMaps/Ice_Age.py               |    8 +-
PrivateMaps/Inland_Sea.py            |  628 +++++++++---------
PrivateMaps/Islands.py               |  188 +++---
PrivateMaps/Pangaea.py               |   24 +-
PrivateMaps/Rainforest.py            |    4 +-
PrivateMaps/Ring.py                  |  646 +++++++++---------
PrivateMaps/Tectonics.py             |   22 +-
PrivateMaps/Wheel.py                 |  786 +++++++++++-----------
16 files changed, 2713 insertions(+), 2423 deletions(-)
```

### `collapse_multiline_brackets.py`

Legacy/reference helper.

- Collapses multi-line bracketed expressions (`(...)`, `[...]`, `{...}`) in a single Python source file to one-liners.
- Useful idea: make boilerplate Civ4 API calls and helper invocations greppable on one line.
- Preserves line endings, string literals, and comments outside collapsed ranges.
- Important caution: this script strips line comments and indentation inside collapsed ranges.
- Because many AdvCiv-SAS UI files contain important inline/manual-layout comments, do not use this blindly on comment-heavy files.
- Run on ONE file at a time and eyeball the diff before committing. A whole-directory sweep was tried once and reverted.

Example:

```powershell
python LLM_Helpers\collapse_multiline_brackets.py Assets\Python\Contrib\Sevopedia\_sevopedia_helpers.py
```

### `wrap_python2_prints_for_linting.py`

Conservative Python 2 print-wrapper helper.

- Converts simple active Python 2 bare prints such as `print "hello"` and `print "value = %s" % value` to Python 2.4/3-compatible single-expression calls such as `print("hello")` and `print("value = %s" % value)`.
- Skips ambiguous cases such as redirected prints, trailing-comma prints, semicolon-packed lines, and top-level comma prints; manually rewrite those with one formatted string such as `print("player %s pass %s failed" % (playerID, iPass))`.
- Does not touch commented-out prints, because comments do not block Ruff/Python 3 parsing.
- Intended to reduce parser/linter noise while preserving Civ4 Python 2.4 runtime compatibility.

Example:

```powershell
python LLM_Helpers\wrap_python2_prints_for_linting.py --recursive --diff Assets\Python PrivateMaps
python LLM_Helpers\wrap_python2_prints_for_linting.py --recursive --in-place Assets\Python PrivateMaps
python LLM_Helpers\wrap_python2_prints_for_linting.py --recursive --check Assets\Python PrivateMaps
```

### CvMainInterface single-line cleanup reference scripts

These were generated during a GPT-5.5-Thinking cleanup of `CvMainInterface.py` to make the file easier for grep, VS Code review, and future LLM agents.

The generated scripts were staged working scripts, not polished repo utilities:

- `singleline_pass.py`
  - First conservative pass.
  - Collapsed uncommented multiline logical statements.
  - Skipped statements containing comments.
- `singleline_pass_comments.py`
  - Second staged pass.
  - Collapsed more multiline statements.
  - Preserved comments by moving them above the collapsed statement instead of deleting them.
- `singleline_pass3_comments_and_long.py`
  - Third staged pass and best reference for the final single-line statement approach.
  - Allowed more long-line/comment-aware collapses.
  - Also handled some commented-out multiline code groups.
  - This was run after earlier passes, on an already-modified file.
- `comment_cleanup_pass_v2.py`
  - Fourth staged/reference pass, focused on comments rather than statements.
  - Condensed simple wrapped prose comments.
  - Fixed minor comment typos and wording issues.
  - Intentionally left structured notes, custom XML-style comments, and commented-out code mostly alone.
  - This is separate from the single-line statement passes and should be reviewed as a comment-only cleanup.

Important: `singleline_pass3_comments_and_long.py` should not be treated as guaranteed to include all behavior from pass 1 and pass 2 when run directly on a raw original file. It is the best reference implementation from the final single-line statement pass, not a clean all-in-one tool. Likewise, `comment_cleanup_pass_v2.py` is a later comment-cleanup reference pass, not part of the statement-collapsing logic.

Future LLM/code agents should either:

- reuse the staged scripts only in the same order and review each diff, or
- preferably consolidate the useful logic into one or two clean repo-ready utilities, for example:

```text
collapse_multiline_python.py
condense_python_comments.py
```

A cleaned source-rewrite utility should support:

- command-line input path instead of hardcoded sandbox paths;
- optional `--in-place`;
- optional `--output`;
- optional `--move-comments`;
- optional `--collapse-commented-code` for statement tools;
- optional typo/comment-normalization rules for comment tools;
- line-ending preservation;
- string literal preservation;
- comment preservation;
- summary stats;
- dry-run or diff output if practical.

#### ChatGPT sandbox path note

Some generated scripts may contain paths such as:

```text
/mnt/data/CvMainInterface.singleline2.py
/mnt/data/CvMainInterface.singleline3.py
```

Those were ChatGPT sandbox paths, not repo paths. Codex, Claude Code, local PowerShell, or other agents should replace them with actual repository paths such as:

```text
Assets\Python\Screens\CvMainInterface.py
```

or accept a path from the command line.

#### Safety rule for source-rewrite helpers

For helpers that rewrite Python source files, especially files loaded by Civ4:

- preserve meaningful code tokens;
- preserve strings exactly;
- preserve comments or move them deliberately;
- never silently delete explanatory comments;
- do not rely on Python 3 `ast.parse` as proof of Civ4 Python 2.4 compatibility;
- review the git diff manually;
- smoke-test in game when the file is UI/runtime-sensitive.

The goal is not general Python formatting. The goal is to make large, LLM-maintained files easier to search, patch, and review.

Good target style for LLM-facing UI files:

```text
one semantic UI operation = one searchable line
manual layout decision = keep local and visible
large table/list = one item per line when that is clearer
commented-out code = preserve intent; do not auto-destroy it
```

## Game speed helper scripts

### `compare_speed_summaries.py`

- Reads the latest Sevopedia Game Speed chart dump from `PythonDbg.log`.
- Compares `Normal` vs one selected speed across summary rows.
- Also compares flattened increment sequences (Years and Months) index by index.
- Can focus summaries to one index (`--summary`), while still printing increment comparison.
- Automatically writes a timestamped `.txt` file.
- Output filename is short and sortable: `<UTC-ISO>_<speed>[_sXX].txt` (e.g. `20260217T110501Z_slow_s06.txt`).

Examples:

```powershell
python LLM_Helpers\compare_speed_summaries.py --speed slow
python LLM_Helpers\compare_speed_summaries.py --speed marathon --summary 6
python LLM_Helpers\compare_speed_summaries.py --log "C:\Users\PC\Documents\My Games\beyond the sword\Logs\PythonDbg.log" --speed veryslow
```

Auto-save with timestamp under `LLM_Helpers\outputs` (git-ignored):

```powershell
python LLM_Helpers\compare_speed_summaries.py --speed slow
python LLM_Helpers\compare_speed_summaries.py --speed slow --summary 6
python LLM_Helpers\compare_speed_summaries.py --speed slow --output-dir LLM_Helpers\outputs
```

### `autotune_speed_from_xml.py`

- Computes Summary rows directly from `Assets/XML/GameInfo/CIV4GameSpeedInfo.xml`.
- Does not require `PythonDbg.log`.
- Can print XML-based `Normal` vs selected speed comparison.
- Optional draft autoloop mode for `GAMESPEED_SLOW`.
- Iterates candidate timeline tweaks and reports the best-scoring result.
- Writes timestamp-first output files in `LLM_Helpers\outputs` (`<UTC-ISO>_<speed>_<mode>.txt`).

XML-native comparison and draft autoloop:

```powershell
python LLM_Helpers\autotune_speed_from_xml.py --speed slow
python LLM_Helpers\autotune_speed_from_xml.py --speed slow --summary-steps 50
python LLM_Helpers\autotune_speed_from_xml.py --speed slow --summary-steps 100 --focus-start-pct 20 --focus-end-pct 80
python LLM_Helpers\autotune_speed_from_xml.py --speed slow --autoloop --iterations 8000 --seed 1
```

## Game info comparison helpers

### `compare_handicap_infos.py`

- Report-only. Does not modify source files.
- Compares one `CIV4HandicapInfo.xml` against another; pass both XML paths explicitly.
- Compares handicap entries by XML order/index, so added/removed difficulties in other mods show with the missing side blank instead of relying on hardcoded difficulty names.
- Missing/new fields on either side are also shown with the missing side blank.
- Adds a separate entry table with each index's left/right `Type` and `Description`, then lists changed fields by index.
- Flattens handicap XML by field path and writes an LLM-friendly Markdown table with flat numeric deltas and percentage deltas, computed as `(file 2 - file 1) / file 1` when both values are numeric and file 1 is nonzero.
- Repeated XML collections such as `Goodies`, `FreeTechs`, and `AIFreeTechs` are compared as compact counted lists instead of noisy index-by-index rows.
- Writes timestamped output to `LLM_Helpers\outputs\handicap_compare_<UTC-ISO>.md` by default; this folder is git-ignored.
- `--example-output` writes to `LLM_Helpers\examples\handicap_infos_compared.md` instead, useful when publishing a stable hosted example URL.
- The report includes its UTC run time, output path, and full input paths because XML assets can change between analysis runs.
- The same Markdown file includes a tab-separated spreadsheet matrix: one row per field, and grouped file 1/file 2/delta columns for each handicap index. Empty cells mean that field/index has no shown change or no matching value on that side.
- Optional `--file1-label`/`--file2-label` labels make published examples clearer while the defaults stay generic.
- `--tsv-output` optionally writes the same matrix as a separate `.tsv` file too.
- Created with GPT-5.5/Codex and reviewed with GPT-5.5-Thinking.

```powershell
python LLM_Helpers\compare_handicap_infos.py "..\AdvCiv\Assets\XML\GameInfo\CIV4HandicapInfo.xml" "Assets\XML\GameInfo\CIV4HandicapInfo.xml" --file1-label "Base AdvCiv 1.12" --file2-label "AdvCiv-SAS"
python LLM_Helpers\compare_handicap_infos.py "..\AdvCiv\Assets\XML\GameInfo\CIV4HandicapInfo.xml" "Assets\XML\GameInfo\CIV4HandicapInfo.xml" --file1-label "Base AdvCiv 1.12" --file2-label "AdvCiv-SAS" --example-output
python LLM_Helpers\compare_handicap_infos.py "..\SomeMod\Assets\XML\GameInfo\CIV4HandicapInfo.xml" "Assets\XML\GameInfo\CIV4HandicapInfo.xml" --file1-label SomeMod --file2-label AdvCiv-SAS --output C:\tmp\handicap_compare.md --tsv-output C:\tmp\handicap_compare.tsv
python LLM_Helpers\compare_handicap_infos.py C:\tmp\file1.xml C:\tmp\file2.xml
```

## Static audit helpers

### `audit_define_keys.py`

- Report-only. Does not modify source.
- Audits literal `getDefine{BOOL,FLOAT,INT,STRING}("X")` across both Python and DLL source:
  - `Assets/Python/**/*.py`
  - `CvGameCoreDLL/**/*.{cpp,h}` (skip with `--no-dll`)
- Checks each used key against `<DefineName>` declarations from:
  - mod `Assets/XML/*.xml`
  - base BTS `*.xml` (auto: `<mod-root>/../../Assets/XML/`, override `--bts-xml-dir`)
  - vanilla Civ4 `*.xml` (auto: `<mod-root>/../../../Assets/XML/`, override `--vanilla-xml-dir`)
  - any `--extra-xml <file-or-dir>` (repeatable)
- Variable-arg calls (`gc.getDefineINT(szVar)`, `GC.getDefineINT(SOME_MACRO)`) counted only, not audited.
- Use this instead of a runtime `getDefineINTOrFail` wrapper: no clean missing sentinel (returns `0`/`""` for both missing and legit zero/empty). `SASDefineGuard.verify_or_raise()` handles the wholesale "defines didn't load" case; this script handles per-key drift.
- Exit 1 on drift, 0 otherwise. Writes timestamped report to `LLM_Helpers/outputs/` by default.

```powershell
python LLM_Helpers\audit_define_keys.py
python LLM_Helpers\audit_define_keys.py --show-callsites
python LLM_Helpers\audit_define_keys.py --no-dll
python LLM_Helpers\audit_define_keys.py --no-output-file
python LLM_Helpers\audit_define_keys.py --extra-xml <path>
```

Each XML scope is scanned recursively (`rglob *.xml`), but the report only lists files that actually contributed at least one `<DefineName>`. This keeps the audit boundary auditable without dumping hundreds of unrelated entity XMLs (Buildings, Units, etc.).

Example output (clean run, exit 0):

```text
mod XML files (scanned 155, contributed): 9
  - Assets\XML\AI_Variables_GlobalDefines.xml
  - Assets\XML\BBAI_Game_Options_GlobalDefines.xml
  - Assets\XML\GlobalDefines_advc.xml
  - Assets\XML\GlobalDefines_advciv_sas.xml
  - Assets\XML\GlobalDefines_devel.xml
  - Assets\XML\GlobalDefinesAlt.xml
  - Assets\XML\LeadFromBehind_GlobalDefines.xml
  - Assets\XML\PythonCallbackDefines.xml
  - Assets\XML\TechDiffusion_GlobalDefines.xml
BTS XML files (scanned 121, contributed): 2
  - <bts>\Assets\XML\GlobalDefines.xml
  - <bts>\Assets\XML\PythonCallbackDefines.xml
vanilla XML files (scanned 129, contributed): 2
  - <civ4>\Assets\XML\GlobalDefines.xml
  - <civ4>\Assets\XML\GlobalDefinesAlt.xml
extra XML files (scanned 0, contributed): 0
mod XML defines:               697
BTS XML defines:               430
vanilla XML defines:           295
extra XML defines:             0
distinct literal keys (py):    134
distinct literal keys (dll):   658
variable-arg calls (skipped):  491

OK: every literal getDefine{BOOL,FLOAT,INT,STRING} key is declared somewhere.
wrote LLM_Helpers\outputs\20260515T201121Z_audit_define_keys_ok.txt
```

Drift output (exit 1) groups undeclared keys by source, optionally with `--show-callsites`:

```text
DRIFT: 2 key(s) used but not declared in any scanned XML:
  [python]
    SAS_RENAMED_KEY
      - Assets\Python\Screens\CvFoo.py
  [dll_cpp]
    SAS_REMOVED_KEY
      - CvGameCoreDLL\CvBar.cpp
```

### `audit_unused_text_keys.py`

- Report-only. Does not modify source.
- Flags mod GameText `<Tag>TXT_KEY_*` entries that are defined but referenced nowhere.
- DEFINITION: `<Tag>TXT_KEY_FOO</Tag>` inside a `<TEXT>...</TEXT>` block, in files matched by `--text-glob` (default `Assets/XML/Text/*.xml`).
- REFERENCED if the exact token appears in:
  - mod `Assets/Python/**/*.py`, `CvGameCoreDLL/**/*.{cpp,h}`, `Assets/XML/**/*.xml` (`<Tag>` spans scrubbed so a definition is not its own reference)
  - base BTS `Python/**/*.py` + `XML/**/*.xml` (auto: `<mod-root>/../../Assets`, override `--base-assets`)
  - vanilla Civ4 `Python/**/*.py` + `XML/**/*.xml` (auto: `<mod-root>/../../../Assets`, override `--vanilla-assets`)
  - skip the external scan with `--no-external` (mod-only; expect engine/front-end false positives)
- Scanning base+vanilla is the authoritative source for inherited engine/front-end keys (main menu, setup, Civilopedia, sealevel/worldsize Info XML) the mod does not override — confirmed used by evidence, not whitelist.
- Buckets: LIKELY-UNUSED (candidates); REVIEW (name under a known dynamic-construction prefix, e.g. `TXT_KEY_BUG_OPT_*` built via `"..."+id`); engine-derived suffixes (`_PEDIA/_STRATEGY/_HELP/...`) treated used if the base key is referenced. Output is candidates, not proof — a small pure-EXE-internal residue can remain; verify before deleting.
- `--prefix TXT_KEY_SAS` to focus on mod-custom keys. Exit 1 if any LIKELY-UNUSED, 0 otherwise. Timestamped report to `LLM_Helpers/outputs/` unless `--no-output-file`.

```powershell
python LLM_Helpers\audit_unused_text_keys.py
python LLM_Helpers\audit_unused_text_keys.py --text-glob "Assets/XML/Text/AdvCiv-SAS_*.xml"
python LLM_Helpers\audit_unused_text_keys.py --prefix TXT_KEY_SAS
python LLM_Helpers\audit_unused_text_keys.py --no-external --no-output-file
```

Example output (real run, `--text-glob "Assets/XML/Text/AdvCiv-SAS_*.xml"`; exit 1 because candidates were found):

(from LLM_Helpers\outputs\unused_text_keys_20260517T162642Z.txt)

```text
AdvCiv-SAS unused GameText key audit
mod root : C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS
text glob: Assets/XML/Text/AdvCiv-SAS_*.xml
external : C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets | C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Assets
defined  : 1283 tags in 3 files | referenced tokens: 10510 | rescued by base/vanilla: 11
LIKELY-UNUSED: 16 | REVIEW (maybe dynamic): 28 | duplicate-defined: 0

=== LIKELY UNUSED (no reference in mod, base BTS, or vanilla; verify before deleting) ===

[Assets/XML/Text/AdvCiv-SAS_main.xml]
  TXT_KEY_MAP_SCRIPT_SAS_WORLD_SIZES_DESCR
  TXT_KEY_PEDIA_BUILD_FEATURE_STRUCT
  TXT_KEY_PEDIA_BUILD_IMPROVEMENT
  TXT_KEY_PEDIA_BUILD_REMOVE
  TXT_KEY_PEDIA_BUILD_REMOVES_FEATURES
  TXT_KEY_PEDIA_CHANGES
  TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_OUTCOME_COUNT
  TXT_KEY_PEDIA_SAS_IMPROVEMENTS_SHORT
  TXT_KEY_PEDIA_SAS_MUSIC_GROUPING_LEADERS_DIPLO
  TXT_KEY_PEDIA_SAS_MUSIC_GROUPING_MENUS_OPENING
  TXT_KEY_PEDIA_SAS_OPEN_PEDIA_ENTRY
  TXT_KEY_PEDIA_SAS_PLAY_MOVIE
  TXT_KEY_PEDIA_TECH_OBSOLETE_UNITS_TREE_NOTE
  TXT_KEY_PEDIA_UNTRADEABLE_TECH_REMINDER
  TXT_KEY_SEALEVEL_HIGH_RECOMMEND
  TXT_KEY_SEALEVEL_LOW_RECOMMEND

=== REVIEW: matches a known dynamic-construction prefix (likely used via string concat) ===

[Assets/XML/Text/AdvCiv-SAS_main.xml]
  TXT_KEY_BUG_OPTLABEL_FOREIGN_ADVISOR
  TXT_KEY_BUG_OPTLABEL_FOREIGN_DIPLOMACY_ADVISOR
  TXT_KEY_BUG_OPTLABEL_INFO_SCREENS
  TXT_KEY_BUG_OPTLABEL_RELIGIOUS_ADVISOR
  TXT_KEY_BUG_OPTLABEL_SEVOPEDIA
  TXT_KEY_BUG_OPTLABEL_VICTORY_CONDITIONS
  TXT_KEY_BUG_OPT_ACO__IGNOREBARBFREEWINS_HOVER
  TXT_KEY_BUG_OPT_ADVISORS__BUGRELIGIOUSTAB_HOVER
  TXT_KEY_BUG_OPT_ADVISORS__BUGRELIGIOUSTAB_TEXT
  TXT_KEY_BUG_OPT_ADVISORS__EFAGLANCETAB_HOVER
  TXT_KEY_BUG_OPT_ADVISORS__GPTECHPREFS_HOVER
  TXT_KEY_BUG_OPT_ADVISORS__GPTECHPREFS_TEXT
  TXT_KEY_BUG_OPT_AUTOSAVE__USEPLAYERNAME_HOVER
  TXT_KEY_BUG_OPT_MAININTERFACE__MODNAMEINREPLAYS_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_AIR_BOMBER_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_AIR_BOMBER_TEXT
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_AIR_FIGHTER_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_AIR_FIGHTER_TEXT
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_ARCHER_BOW_LONG_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_ARCHER_BOW_LONG_TEXT
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_ARCHER_BOW_SHORT_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_ARCHER_BOW_SHORT_TEXT
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_ARCHER_CROSSBOW_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_ARCHER_CROSSBOW_TEXT
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_MOUNTED_MELEE_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_MOUNTED_MELEE_TEXT
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_MOUNTED_RANGED_HOVER
  TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_MOUNTED_RANGED_TEXT
```

`rescued by base/vanilla` counts tags a mod-only scan would have wrongly flagged that the inherited base/vanilla scan proved are used (e.g. `TXT_KEY_MAIN_MENU_*`, `TXT_KEY_PEDIA_SCREEN_TOP`).

This run helped identify (after review) the following as unused and safe to remove from `Assets/XML/Text/AdvCiv-SAS_main.xml`:

```log
TXT_KEY_PEDIA_BUILD_FEATURE_STRUCT
TXT_KEY_PEDIA_BUILD_IMPROVEMENT
TXT_KEY_PEDIA_BUILD_REMOVE
TXT_KEY_PEDIA_BUILD_REMOVES_FEATURES
TXT_KEY_PEDIA_SAS_EVENT_TRIGGER_OUTCOME_COUNT
TXT_KEY_PEDIA_SAS_IMPROVEMENTS_SHORT
TXT_KEY_PEDIA_SAS_MUSIC_GROUPING_LEADERS_DIPLO
TXT_KEY_PEDIA_SAS_MUSIC_GROUPING_MENUS_OPENING
TXT_KEY_PEDIA_SAS_OPEN_PEDIA_ENTRY
TXT_KEY_PEDIA_SAS_PLAY_MOVIE
TXT_KEY_PEDIA_UNTRADEABLE_TECH_REMINDER
```

## Workflow rule for timeline tuning

- Always run one full 5% bird-view (`Normal` vs current target speed) before sharing a draft.
- Do not rely only on focused slices (`--focus-start-pct/--focus-end-pct`) when evaluating a candidate.
- After each local tweak, re-check the full 5% table to catch late drift and endpoint issues early.
- After each accepted candidate edit, generate a fresh human-readable review file with:

```powershell
python LLM_Helpers\compare_speed_summaries.py --speed <speed>
```

Use this `slow_*.txt` / `marathon_*.txt` style output as the primary review artifact for discussion.

## General notes for future LLM helpers

- Prefer small, reviewable, single-purpose scripts.
- Keep generated output in `LLM_Helpers\outputs` when possible.
- Do not claim a helper is safe for broad directory sweeps unless it was tested that way.
- Explain whether a script edits files, prints reports, or only suggests changes.
- When editing source files, always preserve behavior first and readability second.
- When output is only a report, optimize for clarity and usefulness rather than runtime compatibility.

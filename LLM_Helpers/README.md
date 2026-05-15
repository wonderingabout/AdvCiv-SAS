# External helper tools

Primary audience: coding agents (Claude Code, Codex, etc.) invoking these scripts on the user's behalf. Prefer agent-spec bullets over prose; show example output where it clarifies the contract.

This folder contains external helper scripts, mostly Python 3, for tasks outside Civ4's embedded Python runtime. These scripts are meant for LLM-assisted workflows, balancing workflows, code review, refactoring support, report generation, and other tooling.

Important distinction:

- Helper scripts may use modern Python 3.
- Output files do not automatically need to be Civ4 Python 2.4-compatible.
- Only source-rewrite helpers that modify Python files loaded by Civ4 must preserve Python 2.4-compatible target code.
- Text reports, tuning reports, XML summaries, and other external artifacts only need to be useful and accurate for their workflow.

Always review diffs before committing generated source changes.

## Source-rewrite helpers

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

### ChatGPT single-line cleanup scripts

These were generated during a ChatGPT-5.5 Thinking cleanup of `CvMainInterface.py` to make the file easier for grep, VS Code review, and future LLM agents.

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

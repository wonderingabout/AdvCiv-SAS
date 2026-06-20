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

- [Python source cleanup helpers](#python-source-cleanup-helpers)
  - [`collapse_multiline_calls.py`](#collapse_multiline_callspy)
  - [`collapse_multiline_calls2.py`](#collapse_multiline_calls2py)
  - [`collapse_multiline_parens_safe.py`](#collapse_multiline_parens_safepy)
  - [`fix_matrix_indent.py`](#fix_matrix_indentpy)
  - [`collapse_flat_literals.py`](#collapse_flat_literalspy)
  - [`wrap_python2_prints_for_linting.py`](#wrap_python2_prints_for_lintingpy)
  - [`collapse_multiline_brackets.py`](#collapse_multiline_bracketspy)
  - [`fix_line_endings.py`](#fix_line_endingspy)
- [C++ source cleanup helpers](#c-source-cleanup-helpers)
  - [`collapse_cpp_signatures.py`](#collapse_cpp_signaturespy)
  - [`collapse_cpp_inline_returns.py`](#collapse_cpp_inline_returnspy)
  - [`collapse_cpp_inline_statements.py`](#collapse_cpp_inline_statementspy)
- [CvMainInterface cleanup reference scripts](#cvmaininterface-cleanup-reference-scripts)
  - [`singleline_pass.py`](#singleline_passpy)
  - [`singleline_pass_comments.py`](#singleline_pass_commentspy)
  - [`singleline_pass3_comments_and_long.py`](#singleline_pass3_comments_and_longpy)
  - [`comment_cleanup_pass_v2.py`](#comment_cleanup_pass_v2py)
  - [Comparison with Base AdvCiv 1.12's Main Interface processed similarly](#comparison-with-base-advciv-112s-main-interface-processed-similarly)
  - [Notes](#notes)
- [Game speed helper scripts](#game-speed-helper-scripts)
  - [`compare_speed_summaries.py`](#compare_speed_summariespy)
  - [`autotune_speed_from_xml.py`](#autotune_speed_from_xmlpy)
- [Game info comparison helpers](#game-info-comparison-helpers)
  - [`compare_handicap_infos.py`](#compare_handicap_infospy)
- [Static audit helpers](#static-audit-helpers)
  - [`audit_define_keys.py`](#audit_define_keyspy)
  - [`audit_unused_text_keys.py`](#audit_unused_text_keyspy)
- [Legacy XML duplicate discovery scanner (``scan_xml_duplicates-3.3.py``)](#legacy-xml-duplicate-discovery-scanner-scan_xml_duplicates-33py)
- [Source packaging helper](#source-packaging-helper)
  - [`make_light_source_zip.py`](#make_light_source_zippy)
- [Workflow rule for timeline tuning](#workflow-rule-for-timeline-tuning)
- [General notes for future LLM helpers](#general-notes-for-future-llm-helpers)

## Python source cleanup helpers

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

### `collapse_multiline_parens_safe.py`

Broad but safety-checked parenthesis-collapse helper.

- Collapses multiline parenthesized expressions to one physical line.
- Intended mainly for old Civ4 Python files where wrapped parenthesized calls/expressions create Ruff/Pylance mixed-indentation noise.
- Broader than `collapse_multiline_calls.py` because it is not limited to call-like statements.
- Safer than the legacy `collapse_multiline_brackets.py` because it defaults to parentheses only and skips risky ranges.
- Skips ranges containing comments, multiline strings, explicit backslash continuations, unmatched brackets, overly large blocks, and lines exceeding the configured maximum line length.
- Preserves strings and line endings.
- Compares significant token streams when tokenization works.
- If a file is already indentation-broken and cannot be tokenized, the helper can still apply local parenthesis-only rewrites and reports that token verification was skipped. Review those files especially carefully.
- Optional flags can include square/curly bracket ranges, but do not use those broadly unless the task explicitly needs them and the diff is easy to review.
- Always review the staged diff before committing. This is not a general formatter.

Broad Git Bash staged-review workflow. This copies a temporary runner, applies it to every tracked or untracked `.py` file except the runner itself, stages Python changes, writes the full staged diff and a check report under `LLM_Helpers/outputs`, prints the staged stat, runs `git diff --cached --check`, and reruns Ruff `E101` so the user/agent can compare the remaining mixed-indent count:

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && cp "LLM_Helpers/collapse_multiline_parens_safe.py" "LLM_Helpers/collapse_multiline_parens_safe_TEMP_RUNNER.py" && runner="LLM_Helpers/collapse_multiline_parens_safe_TEMP_RUNNER.py" && mkdir -p LLM_Helpers/outputs && ts=$(date +%Y%m%d_%H%M%S) && runlog="LLM_Helpers/outputs/run_collapse_multiline_parens_safe_${ts}.txt" && diff="LLM_Helpers/outputs/staged_collapse_multiline_parens_safe_${ts}.diff" && report="LLM_Helpers/outputs/check_collapse_multiline_parens_safe_${ts}.txt" && { git ls-files -z '*.py'; git ls-files -z -o --exclude-standard '*.py'; } | while IFS= read -r -d '' f; do [ "$f" = "$runner" ] && continue; py "$runner" "$f" --in-place; done > "$runlog" 2>&1; rc=$?; rm -f "$runner"; [ $rc -eq 0 ] || { cat "$runlog"; exit $rc; }; git ls-files -z -m -o --exclude-standard '*.py' | xargs -0 -r git add --; git diff --cached --ignore-space-at-eol > "$diff"; { echo "=== collapse_multiline_parens_safe run log ==="; cat "$runlog"; echo; echo "=== git diff --cached --ignore-space-at-eol --stat -- *.py ==="; git diff --cached --ignore-space-at-eol --stat -- '*.py'; echo; echo "=== git diff --cached --check -- *.py ==="; git diff --cached --check -- '*.py'; echo; echo "=== remaining Ruff E101 ==="; py -m ruff check . --select E101 --output-format=grouped || true; echo; echo "runlog=$runlog"; echo "diff=$diff"; } > "$report" 2>&1 && cat "$report" && echo "wrote $report" && echo "wrote $diff"
```

On top of the code formatting/grepping gains, notably helped reduce ruff errors.

```md
54 files changed
816 insertions / 1875 deletions
net ~1059 physical lines removed
E101 Indentation contains mixed spaces and tabs count: ~1068 -> 259
total remaining Ruff E101 report errors: 349
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

### `collapse_flat_literals.py`

Conservative flat-literal collapse helper.

- Collapses simple flat multiline Python list/tuple assignment literals to one physical line.
- Intended for small option lists, name lists, simple region-data arrays, GameFont-style flat token lists, and similar grep-friendly data.
- Does not target matrix-like map templates, nested lists/dicts/tuples, comments inside literals, or large table-style data where one row per line is clearer.
- Preserves trailing commas if they already exist; this keeps the rewrite mechanical and avoids unnecessary token/style changes.
- Refuses risky edits when significant token sequence changes.
- Default `--max-line-len` is intentionally fairly high because this helper targets grep-friendly flat data arrays, not normal prose/code wrapping.
- This is not a general formatter. Review the staged diff before committing.

Tested broad run workflow from Git Bash. The helper processes one file at a time, so this loop copies a temporary runner, applies it to every tracked or untracked `.py` file except the runner itself, removes the runner, stages Python changes, writes a timestamped staged diff under `LLM_Helpers/outputs`, prints the staged stat, and runs the staged whitespace check:

```bash
cd "/c/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Mods/AdvCiv-SAS" && cp "LLM_Helpers/collapse_flat_literals.py" "LLM_Helpers/collapse_flat_literals_TEMP_RUNNER.py" && runner="LLM_Helpers/collapse_flat_literals_TEMP_RUNNER.py" && mkdir -p LLM_Helpers/outputs && ts=$(date +%Y%m%d_%H%M%S) && runlog="LLM_Helpers/outputs/run_collapse_flat_literals_${ts}.txt" && diff="LLM_Helpers/outputs/staged_collapse_flat_literals_${ts}.diff" && report="LLM_Helpers/outputs/check_collapse_flat_literals_${ts}.txt" && { git ls-files -z '*.py'; git ls-files -z -o --exclude-standard '*.py'; } | while IFS= read -r -d '' f; do [ "$f" = "$runner" ] && continue; py "$runner" "$f" --in-place; done > "$runlog" 2>&1; rc=$?; rm -f "$runner"; [ $rc -eq 0 ] || { cat "$runlog"; exit $rc; }; git ls-files -z -m -o --exclude-standard '*.py' | xargs -0 -r git add --; git diff --cached --ignore-space-at-eol > "$diff"; { echo "=== collapse_flat_literals run log ==="; cat "$runlog"; echo; echo "=== staged stat ==="; git diff --cached --ignore-space-at-eol --stat -- '*.py'; echo; echo "=== staged whitespace check ==="; git diff --cached --check -- '*.py'; echo; echo "runlog=$runlog"; echo "diff=$diff"; } > "$report" 2>&1 && cat "$report" && echo "wrote $report" && echo "wrote $diff"
```

Tested broad pass result with default line length 500:

```text
19 flat literals collapsed across 15 existing source files.
One risky old vendored file, Assets\Python\BUG\configobj.py, was refused by the token-safety check.
The pass caught the longer flat GameFontDisplay character-name list in addition to shorter option/name/region-data arrays.
Run git diff --cached --check before committing.
```

Example intended rewrites:

```python
selection_names = [
	"TXT_KEY_MAP_WRAP_FLAT",
	"TXT_KEY_MAP_WRAP_CYLINDER",
	"TXT_KEY_MAP_WRAP_TOROID",
]
```

becomes:

```python
selection_names = ["TXT_KEY_MAP_WRAP_FLAT", "TXT_KEY_MAP_WRAP_CYLINDER", "TXT_KEY_MAP_WRAP_TOROID",]
```

```python
phonetic_array = [
	'Alpha', 'Bravo', 'Charlie',
	'Delta', 'Echo', 'Foxtrot',
]
```

becomes:

```python
phonetic_array = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',]
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

### `fix_line_endings.py`

External cleanup helper for line-ending hygiene.

- Reports or fixes mixed CRLF/LF line endings and missing final newlines.
- Does not run automatically in GitHub Actions; the workflow check only reports/fails.
- Defaults to active repo text-like files and excludes generated/reference helper folders such as `LLM_Helpers/outputs` and `LLM_Helpers/examples`.
- Preserves each file's dominant existing line-ending style by default, so it does not force the whole repo to LF or CRLF.
- Adds a final newline to non-empty text files by default; use `--no-final-newline` only when deliberately preserving a missing final newline.
- Use `--eol lf` or `--eol crlf` only for deliberate normalization passes.
- Always review the diff before committing generated source changes.

Examples:

```powershell
python LLM_Helpers\fix_line_endings.py
python LLM_Helpers\fix_line_endings.py --diff
python LLM_Helpers\fix_line_endings.py --in-place
python LLM_Helpers\fix_line_endings.py Assets\Python PrivateMaps --diff
python LLM_Helpers\fix_line_endings.py Assets\Python PrivateMaps --in-place
```

## C++ source cleanup helpers

### `collapse_cpp_signatures.py`

Conservative signature-only source-rewrite helper for C/C++ files.

- Collapses safe multiline function declarations/definitions to one physical line, mainly to make signatures easier to scan, grep, and compare.
- Signature-only by design: ordinary multiline calls, logging statements, and constructor-like local statements are left alone. If call cleanup is wanted later, use a separate helper such as `collapse_cpp_calls.py` with separate rules.
- Skips control-flow statements, comments that would become misleading, block-comment boundaries, and candidates that do not look like function headers.
- Unindented root-scope declarations in `.cpp` files are treated like safe declarations; nested constructor-like local statements are omitted from the normal ignored report unless `--include-nonsignature-ignored` is used.
- Qualified `::` signatures are also detected when the prefix contains template commas such as `std::pair<int,int>` or `KmodPathFinder<StepMetric,Node>`.
- Indented header declarations may use qualified return types such as `std::pair<int,int>`; only indented qualified callable names are treated as likely local calls.
- Nested class/struct declarations are handled, while declaration-shaped local constructor calls inside inline function bodies stay skipped.
- Allows trailing end-of-signature `//` comments (for example `) const // advc.031`) and inline one-line `/* ... */` tail comments; comments inside the parameter list are skipped unless a trace-hoisting mode below handles them.
- Uses a generous default `--max-line-len 600` and `--max-span-lines 16` because this helper is meant to make safe signatures one-line-first; lower them for a narrower review.
- `--hoist-comments` can move whole-line comments from inside a collapsed signature above the signature, while still skipping inline comments inside the parameter list.
- `--trace-hoisted-comments` also appends a custom trace note to hoisted comments, recording whether the comment was before, after, or between specific parameters. Use `--trace-credit "GPT-5.5 (reviewed script output)"` or similar when the generated comments were externally reviewed.
- `--trace-inline-comments` similarly hoists inline `//` comments and extractable multiline `/* ... */` comments from inside the parameter list, strips them from the collapsed signature line, and appends trace metadata for their original parameter position.
- Existing whole-line `<!-- custom: ... -->` comments inside signatures receive the same hoist-position trace note as other whole-line comments.
- `--tail-exposed-to-python-comments` handles the common header-only case where `// Exposed to Python` was placed inside a multiline declaration; it moves that metadata to the final tail comment, after any existing tail comment.
- Defaults to tracked C/C++ files under `CvGameCoreDLL`; you can also pass one or more files/folders for a narrower review.
- `--diff-file` writes the review diff to a file. Without an explicit path, it creates a timestamped file under `LLM_Helpers/outputs/`.
- `--ignored-file` writes a separate review report of skipped signature-like multiline candidates and the reason they were left alone, such as unsafe comments, line length, or unsupported tail syntax. Use `--include-nonsignature-ignored` only when you also want the very noisy/exhaustive ordinary-call/local-statement candidates.
- Empirically idempotent after the first full DLL pass: rerunning with the default broad scan reported `Scanned 350 C/C++ file(s). No safe C++ signature collapses found.`
- Always review the diff before committing. This is not a general C++ formatter. External review in ChatGPT or another non-agentic context can be useful for long generated diff/report files before applying the changes locally.

Example diagnostic run with output files and no source changes (Git Bash):

```Bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_signatures.py ./CvGameCoreDLL --diff-file --ignored-file
```

This writes timestamped files like `LLM_Helpers/outputs/collapse_cpp_signatures_20260619T150412Z.diff.txt` and `LLM_Helpers/outputs/collapse_cpp_signatures_20260619T150412Z_ignored.txt`.

Example apply run (Git Bash):

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_signatures.py ./CvGameCoreDLL --in-place
```

Example apply run with traceable hoisted comments (Git Bash):

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_signatures.py ./CvGameCoreDLL --max-line-len 600 --max-span-lines 16 --trace-hoisted-comments --trace-credit "GPT-5.5 (reviewed script output)" --in-place
```

Example apply run with traceable whole-line and inline hoisted comments (Git Bash):

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_signatures.py ./CvGameCoreDLL --max-line-len 600 --max-span-lines 16 --trace-inline-comments --trace-hoisted-comments --tail-exposed-to-python-comments --trace-credit "GPT-5.5 (reviewed script output)" --in-place
```

Example apply run for `// Exposed to Python` declaration metadata (Git Bash):

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_signatures.py ./CvGameCoreDLL --max-line-len 600 --max-span-lines 16 --tail-exposed-to-python-comments --in-place
```

Example results:

- First full pass: 118 files changed, 1360 insertions, and 2662 deletions.
- A follow-up comment-hoisting pass, amended into the same commit because it seemed small and contained, collapsed 31 more signatures across 23 files.
- A later pass improved old comment text preservation and appended trace notes for where each hoisted comment had originally been placed: it was 66 insertions and 117 deletions.
- Another `// Exposed to Python` metadata pass collapsed 102 more header declarations across 13 files.
- A broad inline-comment trace pass collapsed 125 more signatures across 37 files.
- A multiline block-comment trace pass collapsed 21 more signatures across 13 files.
- A root-scope `.cpp` declaration pass collapsed 6 explicit-template-instantiation signatures in `CvGameTextMgr.cpp`.
- An existing-custom-comment pass collapsed 2 more `setUnitHelp` signatures while preserving their custom rationale comments and adding hoist-position trace notes.
- A qualified-template-prefix pass collapsed 8 more `::` signatures with template commas in the prefix.
- A qualified-return-type header pass collapsed 4 more declarations using `std::` return types.
- A nested-class declaration pass collapsed 2 more `InvasionGraph::Node` declarations while keeping inline-function local constructor calls skipped.

Example (nested simple comments) (before):

```cpp
void CvDeal::endTrade(TradeData trade, PlayerTypes eFromPlayer,
	PlayerTypes eToPlayer, bool bTeam, /* advc.036: */ bool bUpdateAttitude,
	PlayerTypes eCancelPlayer) // advc.130p
```

Example (nested simple comments) (after):

```cpp
void CvDeal::endTrade(TradeData trade, PlayerTypes eFromPlayer, PlayerTypes eToPlayer, bool bTeam, /* advc.036: */ bool bUpdateAttitude, PlayerTypes eCancelPlayer) // advc.130p
```

Example 2 (overloaded signatures) (before) :

```cpp
	/*	(Had been named "addHumanMessage" in K-Mod;
		Definition moved into CvDLLInterfaceIFaceBase.cpp.) */ // </advc.127>
	void addMessage(PlayerTypes ePlayer, bool bForce, int iLength, CvWString szString,
			LPCTSTR pszSound = NULL, InterfaceMessageTypes eType = MESSAGE_TYPE_INFO,
			LPCSTR pszIcon = NULL, ColorTypes eFlashColor = NO_COLOR,
			int iFlashX = -1, int iFlashY = -1,
			bool bShowOffScreenArrows = false, bool bShowOnScreenArrows = false);
	// advc: Wrapper for passing iFlashX, iFlashY more conveniently
	void addMessage(PlayerTypes ePlayer, bool bForce, int iLength,
			CvWString szString, CvPlot const& kPlot,
			LPCTSTR pszSound = NULL, InterfaceMessageTypes eType = MESSAGE_TYPE_INFO,
			LPCSTR pszIcon = NULL, ColorTypes eFlashColor = NO_COLOR,
			bool bShowOffScreenArrows = true, bool bShowOnScreenArrows = true);
```

Example 2 (overloaded signatures) (after):

```cpp
	/*	(Had been named "addHumanMessage" in K-Mod;
		Definition moved into CvDLLInterfaceIFaceBase.cpp.) */ // </advc.127>
	void addMessage(PlayerTypes ePlayer, bool bForce, int iLength, CvWString szString, LPCTSTR pszSound = NULL, InterfaceMessageTypes eType = MESSAGE_TYPE_INFO, LPCSTR pszIcon = NULL, ColorTypes eFlashColor = NO_COLOR, int iFlashX = -1, int iFlashY = -1, bool bShowOffScreenArrows = false, bool bShowOnScreenArrows = false);
	// advc: Wrapper for passing iFlashX, iFlashY more conveniently
	void addMessage(PlayerTypes ePlayer, bool bForce, int iLength, CvWString szString, CvPlot const& kPlot, LPCTSTR pszSound = NULL, InterfaceMessageTypes eType = MESSAGE_TYPE_INFO, LPCSTR pszIcon = NULL, ColorTypes eFlashColor = NO_COLOR, bool bShowOffScreenArrows = true, bool bShowOnScreenArrows = true);
```

Example 3 (traceable hoisted comment) (before):

```cpp
bool CvUnitAI::AI_cityAttack(int iRange, int iOddsThreshold,
	// advc (comment): No caller uses eFlags anymore (not since K-Mod 1.15)
	MovementFlags eFlags, bool bFollow)
```

Example 3 (traceable hoisted comment) (after):

```cpp
// advc (comment): No caller uses eFlags anymore (not since K-Mod 1.15) <!-- custom: hoisted from multiline signature between `iOddsThreshold` and `eFlags` by collapse_cpp_signatures.py. (GPT-5.5 (reviewed script output)) -->
bool CvUnitAI::AI_cityAttack(int iRange, int iOddsThreshold, MovementFlags eFlags, bool bFollow)
```

### `collapse_cpp_inline_returns.py`

Conservative header-only helper for simple inline C++ functions.

- Collapses inline functions whose body is exactly one `return ...;` statement to one physical line, including wrapped return expressions and signatures that already have `{` on the signature line.
- Joins a one-line `template<...>` prefix onto the collapsed inline function when the combined line stays below `--max-line-len`.
- Signature tail comments such as `// Exposed to Python` are preserved after the collapsed body.
- Opening-brace comments such as `{	// advc: ...` are hoisted above the collapsed function; closing-brace tail comments such as `} // </advc.opt>` are preserved after the collapsed body.
- Leading `// ...` and `/* ... */` body comments are hoisted above the collapsed function; multiline block comments are normalized to one line.
- Return-line tail comments such as `return x; // advc.opt` are hoisted above the collapsed function so the code line stays focused on the greppable function.
- Skips constructors/destructors, multi-statement bodies, mid-body comments after the return statement, multiline signatures, and lines exceeding `--max-line-len`.
- Separate from `collapse_cpp_signatures.py` because it rewrites function bodies, not just signatures.
- Always review the diff before committing; this is a grep/readability cleanup, not a formatter.

Example diagnostic run with output file and no source changes:

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_inline_returns.py ./CvGameCoreDLL --diff-file
```

Example apply run:

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_inline_returns.py ./CvGameCoreDLL --in-place
```

Reviewed passes used this to collapse:

- simple inline return helpers such as `int getGoldPerTurnByPlayer(PlayerTypes ePlayer) const { return m_aiGoldPerTurnByPlayer.get(ePlayer); } // Exposed to Python`
- wrapped-return helpers such as `template<bool bCHECK_HAS_MET> int countFreeRivals() const { return PlayerIter<FREE_MAJOR_CIV, bCHECK_HAS_MET ? KNOWN_POTENTIAL_ENEMY_OF : POTENTIAL_ENEMY_OF>::count(m_kAgentTeam.getID()); }`
- and brace-on-signature wrappers such as `CvCityAI* AI_getCapital() const { return AI_getCity(m_iCapitalCityID); }`.
- comment-bearing wrappers such as `bool AI_isAnyWaterDanger(CvPlot const& kPlot, int iRange = DANGER_RANGE) const { return (AI_getWaterDanger(kPlot, iRange, 1) >= 1); } // </advc.opt>`.

Example (before):

```cpp
	int getGoldPerTurnByPlayer(PlayerTypes ePlayer) const															// Exposed to Python
	{
		return m_aiGoldPerTurnByPlayer.get(ePlayer);
	}
```

Example (after):

```cpp
	int getGoldPerTurnByPlayer(PlayerTypes ePlayer) const { return m_aiGoldPerTurnByPlayer.get(ePlayer); } // Exposed to Python
```

### `collapse_cpp_inline_statements.py`

Conservative header-only helper for simple inline C++ functions whose body is exactly one non-return statement.

- Complements `collapse_cpp_inline_returns.py`; use this for simple setters, wrapper calls, assignment helpers, `BOOST_STATIC_ASSERT(false);` stubs, and similar one-statement bodies.
- Hoists whole-line body comments and statement tail comments above the collapsed function, and joins one-line `template<...>` prefixes when safe.
- Skips constructors/destructors, initializer-list bodies, `return` bodies, control-flow bodies, delete/throw/SAFE_DELETE bodies, block comments, multi-statement bodies, multiline signatures, and lines exceeding `--max-line-len`.
- Always review the diff before committing; this is a grep/readability cleanup, not a formatter.

Example diagnostic run with output file and no source changes:

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_inline_statements.py ./CvGameCoreDLL --diff-file
```

Example apply run:

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/collapse_cpp_inline_statements.py ./CvGameCoreDLL --in-place
```

Example (before):

```cpp
	template<>
	void applyOp<OP_MULT>(CompactV& cvValue, CompactV cvMultiplier)
	{
		cvValue = static_cast<CompactV>(cvValue * cvMultiplier);
	}
```

Example (after):

```cpp
	template<> void applyOp<OP_MULT>(CompactV& cvValue, CompactV cvMultiplier) { cvValue = static_cast<CompactV>(cvValue * cvMultiplier); }
```

Done with the very nice help of GPT-5.5 (on Codex) thanks.

## CvMainInterface cleanup reference scripts

These were generated during a GPT-5.5-Thinking cleanup of `CvMainInterface.py` to make the file easier for grep, VS Code review, and future LLM agents.

The generated scripts were staged working scripts, not polished repo utilities:

### `singleline_pass.py`

- First conservative pass.
- Collapsed uncommented multiline logical statements.
- Skipped statements containing comments.

### `singleline_pass_comments.py`

- Second staged pass.
- Collapsed more multiline statements.
- Preserved comments by moving them above the collapsed statement instead of deleting them.

### `singleline_pass3_comments_and_long.py`

- Third staged pass and best reference for the final single-line statement approach.
- Allowed more long-line/comment-aware collapses.
- Also handled some commented-out multiline code groups.
- This was run after earlier passes, on an already-modified file.

### `comment_cleanup_pass_v2.py`

- Fourth staged/reference pass, focused on comments rather than statements.
- Condensed simple wrapped prose comments.
- Fixed minor comment typos and wording issues.
- Intentionally left structured notes, custom XML-style comments, and commented-out code mostly alone.
- This is separate from the single-line statement passes and should be reviewed as a comment-only cleanup.

### Comparison with Base AdvCiv 1.12's Main Interface processed similarly

For comparison purposes, we also applied the same scripts to Base AdvCiv 1.12's main interface (as of 2026-06-10), with the help of ChatGPT-5.5.

The resulting file is stored in [CvMainInterface_1_12_singleline.py](/LLM_Helpers/examples/CvMainInterface_1_12_singleline.py). Before as of now adding our copyright a few heading comments, the diff was: Line count: 7279 -> 6021, so 1258 physical lines removed.

We store an example of this as of now because this file has significantly deviated due to formatting change, because it is easier to read for agents or perhaps users too, because the file is large, and because some user seemingly mentioned the comparison is harder.

### Notes

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
  TXT_KEY_MAP_SCRIPT_SAS_SIMPLE_FLAT_GRASS_DESCR
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

## Legacy XML duplicate discovery scanner (``scan_xml_duplicates-3.3.py``)

`scan_xml_duplicates-3.3.py` is an older broad XML duplicate scanner kept here for reference and discovery work, on [AdvCiv-SAS@python-scripts branch's GitHub repository](https://github.com/wonderingabout/AdvCiv-SAS/blob/python-scripts/scan_xml_duplicates-3.3.py).

This script scans `Assets/XML` recursively and reports repeated sibling XML entries based on a broad heuristic: if sibling tags repeat, it compares either their first child field/value or their direct text value. Because this is intentionally broad, it can find useful suspicious patterns, but it can also report valid Civ4 XML structures where repetition is intentional, weighted, or structurally normal.

It should not be treated as a release gate or as proof that every reported duplicate is wrong. Instead, it is useful as an exploratory audit tool: run it when looking for possible XML cleanup targets, review the output manually, and then move high-confidence findings into the curated GitHub workflow checks.

This legacy scanner notably helped inspire and calibrate the newer `.github/workflows/build` XML audits, including the parent duplicate-key checker, child/list duplicate checker, and duplicate text-tag checker. The newer workflow scripts are stricter and more conservative: they check reviewed XML patterns with clearer semantics, print source line numbers, and avoid known noisy cases such as weighted goody hut entries or reused world-picker UI art paths.

In short: this script is kept as a historical and practical discovery helper, while the GitHub workflow checks are the maintained release-safety layer.

## Source packaging helper

### `make_light_source_zip.py`

- Creates a timestamped light source ZIP for a Civ4 mod, mainly for compact local/LLM/code-agent review handoffs.
- Uses repo-relative archive paths and `ZIP_STORED` / no compression. ZIP is intentionally used instead of 7z because 7z uploads caused errors before, while ZIP is currently an as of now seemingly easily compatible format for ChatGPT/code-agent review.
- Default output directory is the mod root. Use `--output-dir` for Downloads or another handoff folder.
- Output filename defaults to `<detected-mod-folder-name>_light_source_<timestamp>.zip`, with `UnspecifiedModName` as a fallback. Use `--mod-name` or `--prefix` only for unusual/manual labels.
- Includes small source/data/docs folders useful for review: root lone files, selected `Assets` folders, root helper/doc/config folders, top-level `CvGameCoreDLL` files, and top-level `CvGameCoreDLL/Project` files under 1 MB, plus `_1_AdvCiv-SAS/Docs` and `_1_AdvCiv-SAS/git_logs`.
- Missing optional folders are skipped with warnings, so the helper can also be run on base AdvCiv or partial comparison folders.
- Skips generated/helper outputs by default, Python cache files, previous light-source ZIPs, heavy/binary `.dll` and `.fpk`, non-useful compact-review `.tga`, original `manual.pdf`/`manual.odt`, `Assets/res/Cursors`, and large/temporary DLL project artifacts such as `.sdf` or project files over 1 MB.
- Does not globally exclude common image files such as `.jpg` or `.png`; small previews can be useful for LLM review, e.g. GameFont previews. Avoid heavy art/image folders by not adding those folders to the include lists instead.
- Use `--dry-run` first to review file count, size, target archive path, and included repo-relative paths without writing the ZIP.
- Created/refined with help of ChatGPT-5.5 and Codex.

Tools like here WizTree helped find which folders/files are heavy to exclude.

Example to write to Downloads (Git Bash):

```bash
cd "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS" && python ./LLM_Helpers/make_light_source_zip.py --output-dir "C:\Users\PC\Downloads"
```

Example of output (Git Bash):

```text
Repo root: C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-
SAS
Mod name:  AdvCiv-SAS
Prefix:    AdvCiv-SAS_light_source
Archive:   C:\Users\PC\Downloads\AdvCiv-SAS_light_source_20260620T124720.zip
Files:     944
Size:      43,264,448 bytes before ZIP container overhead
Mode:      ZIP_STORED / no compression
Wrote:     944 file(s)
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

# External helper tools

This folder contains external Python 3 helper scripts for tasks outside Civ4's embedded Python 2.4 runtime — balancing workflows, code refactoring, report generation, tuning experiments, etc.

General note for LLM/code-agent helpers:

- These scripts are external tools. They may use modern Python 3 even when the mod itself must still run in Civ4's old Python 2.4 runtime.
- Only worry about Python 2.4-safe **output** when the script rewrites a Python file that Civ4 will actually load, such as files under `Assets\Python`.
- Report outputs, tuning summaries, `.txt` review files, generated diagnostics, and other helper artifacts do **not** need to be Civ4-loadable. Make them clear for humans and LLMs.
- When a helper rewrites source code, preserve behavior first: do not silently delete comments, do not rewrite strings, and review the diff before committing.
- Paths created by ChatGPT in `/mnt/data/...` are sandbox paths, not repo paths. Codex/Claude/local agents should replace them with repo-relative paths such as `Assets\Python\Screens\CvMainInterface.py`.

- `collapse_multiline_brackets.py`
  - Legacy/simple character-based collapser for multi-line bracketed expressions (`(...)`, `[...]`, `{...}`) in a single Python source file.
  - Use to make boilerplate Civ4 API calls and helper invocations greppable on one line.
  - Preserves line endings (CRLF or LF), string literals, and comments outside collapsed ranges.
  - Strips line comments and indentation **inside** collapsed ranges, so be careful on comment-heavy files.
  - **Run on ONE file at a time** and eyeball the diff before committing — a whole-directory sweep was tried once and reverted.

- `singleline_pass3_comments_and_long.py` / future `collapse_multiline_python.py`
  - ChatGPT-generated safer basis for LLM-first multiline-to-single-line cleanup.
  - Intended goal: one logical API/layout operation per physical line, so grep and LLM context snippets show the whole operation.
  - Better than `collapse_multiline_brackets.py` for comment-heavy files because it moves inline comments above collapsed statements instead of deleting them.
  - Can also collapse clearly code-like commented-out multiline blocks.
  - The ChatGPT-generated pass scripts were made in a sandbox and may contain hardcoded `/mnt/data/...` paths. Before adding one to the repo, convert it to a normal CLI tool that accepts a target path and optional `--in-place`/review-copy mode.
  - For source-rewrite helpers, useful checks are: unchanged meaningful code-token sequence, preserved comment text, reviewed diff, and an in-game smoke test for UI files.

- `compare_speed_summaries.py`
  - Reads the latest Sevopedia Game Speed chart dump from `PythonDbg.log`.
  - Compares `Normal` vs one selected speed across summary rows.
  - Also compares flattened increment sequences (Years and Months) index by index.
  - Can focus summaries to one index (`--summary`), while still printing increment comparison.
  - Automatically writes a timestamped `.txt` file.
  - Output filename is short and sortable: `<UTC-ISO>_<speed>[_sXX].txt` (e.g. `20260217T110501Z_slow_s06.txt`).

- `autotune_speed_from_xml.py`
  - Computes Summary rows directly from `Assets/XML/GameInfo/CIV4GameSpeedInfo.xml` (no `PythonDbg.log` needed).
  - Can print XML-based `Normal` vs selected speed comparison.
  - Optional draft autoloop mode for `GAMESPEED_SLOW`: iterates candidate timeline tweaks and reports best-scoring result.
  - Writes timestamp-first output files in `LLM_Helpers\outputs` (`<UTC-ISO>_<speed>_<mode>.txt`).

Examples (PowerShell from mod root):

```powershell
python LLM_Helpers\collapse_multiline_brackets.py Assets\Python\Contrib\Sevopedia\_sevopedia_helpers.py
```

Safer LLM-first single-line cleanup, once the ChatGPT pass script is cleaned into a repo tool:

```powershell
python LLM_Helpers\collapse_multiline_python.py Assets\Python\Screens\CvMainInterface.py --in-place --move-comments --collapse-commented-code
```

After source-rewrite cleanup:

```powershell
git diff -- Assets\Python\Screens\CvMainInterface.py
```

Review checklist for source-rewrite helpers:

- No comment text was silently deleted.
- Moved comments still describe the collapsed statement accurately.
- The tool reports unchanged meaningful code tokens when possible.
- Python 3 syntax checks are only sanity checks, not proof of Civ4 Python 2.4 compatibility.
- For UI files such as `CvMainInterface.py`, prefer a real in-game smoke test.

Speed summary comparison:

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

XML-native comparison and draft autoloop:

```powershell
python LLM_Helpers\autotune_speed_from_xml.py --speed slow
python LLM_Helpers\autotune_speed_from_xml.py --speed slow --summary-steps 50
python LLM_Helpers\autotune_speed_from_xml.py --speed slow --summary-steps 100 --focus-start-pct 20 --focus-end-pct 80
python LLM_Helpers\autotune_speed_from_xml.py --speed slow --autoloop --iterations 8000 --seed 1
```

Workflow rule for timeline tuning:

- Always run one full 5% bird-view (`Normal` vs current target speed) before sharing a draft.
- Do not rely only on focused slices (`--focus-start-pct/--focus-end-pct`) when evaluating a candidate.
- After each local tweak, re-check the full 5% table to catch late drift and endpoint issues early.
- After each accepted candidate edit, generate a fresh human-readable review file with:
  - `python LLM_Helpers\compare_speed_summaries.py --speed <speed>`
  - Use this `slow_*.txt`/`marathon_*.txt` style output as the primary review artifact for discussion.

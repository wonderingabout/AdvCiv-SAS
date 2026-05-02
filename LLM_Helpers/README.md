# External helper tools

This folder contains external Python 3 scripts for tasks outside Civ4's embedded Python 2.4 runtime — balancing workflows, code refactoring, etc.

- `collapse_multiline_brackets.py`
  - Collapses multi-line bracketed expressions (`(...)`, `[...]`, `{...}`) in a single Python source file to one-liners.
  - Use to make boilerplate Civ4 API calls and helper invocations greppable on one line.
  - Preserves line endings (CRLF or LF), string literals, and out-of-range comments.
  - Strips line comments and indentation **inside** collapsed ranges.
  - **Run on ONE file at a time** and eyeball the diff before committing — a whole-directory sweep was tried once and reverted.

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

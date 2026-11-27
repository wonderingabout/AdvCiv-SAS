# Retired names

Names of SAS tools and features that were renamed, with their current names, oldest first. The list began on 2026-11-17, when bringing the SASPilot work's fixes to main showed that its renames needed a guard.

We rename old references retroactively, so these names should appear only in history records; [`retired_names.py`](/.github/workflows/README.md#builddocumentationretired_namespy) fails on a listed name anywhere else.

## Menu

- [Tool and feature names](#tool-and-feature-names)

## Tool and feature names

| Retired name | Current name | Checked | Renamed | Why |
| --- | --- | --- | --- | --- |
| `SASGameSummary` | `SASGameRecord` | yes | 2026-08-05 | The unreleased structured game-record feature was renamed and standardized as SASGameRecord throughout its DLL file names and symbols, XML defines, `GAME_RECORD_*` rows, log file names, CI and documentation, at practical 6083. |
| `save transplanter` | `SASSaveTransplanter` | yes | 2026-11-17 | Its own work, on its branch, named it SASSaveTransplanter, like SASPilot; main's mentions, and main's history, were renamed to match. |
| `the pilot` | `SASPilot` | yes | 2026-11-17 | Early SASPilot entries called it "the pilot", which only reads clearly beside SASPilot's own docs; on main, without them, it is vague and clashes with the ordinary sense, as in SGR180's "pilot" of causal links. |
| `save_transplant`, `save_transplanter`, `SASSaveTransplantExport`, `transplant_t0_world` | `sassavetransplanter`, such as `LLM_Helpers/sassavetransplanter/` and `README_SASSaveTransplanter.md`; `SASSaveTransplanterExport`, `SASSaveTransplanterWorld` | yes | 2026-11-18 | Its early paths, `LLM_Helpers/save_transplant/`, `Images/LLM/save_transplant/`, `README_Save_Transplanter.md` and `sas_save_transplanter.py`, used the plain-English name, which the `save transplanter` entry above misses with an underscore; two of its files had other names.<br>Plural `save_transplants`, the run outputs' folder outside the repository, is not caught, nor is a plain `/transplant`: the transplanter still writes `transplant.CivBeyondSwordWBSave`. Its third old file, `pilot_dump_player_unit_state.py`, falls under the `/pilot` entry. |
| `/pilot` | `/saspilot`, such as `Images/LLM/saspilot/` for SASPilot's screenshots; `Images/LLM/game_runs/` for the Civ4 crash dialogs | yes | 2026-11-18 | The `_1_AdvCiv-SAS/Images/LLM/pilot/` folder kept the old nickname through the "the pilot" rename; see the path note below. |

- Matching ignores case and takes whole words only, so "Save transplanter" is caught too, while plural "pilots", as in a harbour's pilots, is not.
- Listed as "the pilot", not plain "pilot": the word also has its ordinary senses here, as in SASGameRecord's revision history, where revision 180 "pilots" causal links, and the Sevopedia's harbour pilots; even " pilot" with a leading space matched two of those. "The pilot" was the nickname itself, and no ordinary use had it.
- The check reads text, not file or folder names, so a rename has to reach the paths by hand: rename a folder or file that carries the old name in the same pass.
  - Example (2026-11-17): `_1_AdvCiv-SAS/Images/LLM/pilot/` kept its name through the "the pilot" rename, and two Civ4 crash-dialog screenshots were then copied to main inside it, the path kept on purpose to spare a later merge.
    - The user caught it while skimming the review; the screenshots moved to `Images/LLM/game_runs/`, beside the Game Runs guide that shows them.
    - Carrying a retired name along to save a step only moves the fix later, and relies on someone noticing it then.
    - "The pilot" could not catch the path, which holds only "pilot", so the user asked why the path itself was not searched for: `/pilot` is now listed, which catches any folder, or file name starting with "pilot", after a slash, while no ordinary text has it.
      - Listed without a trailing slash: whole-word matching rejects a letter right after the name, and in a link a file name follows the folder's slash. A first draft listed only `LLM/pilot`; the user suggested the broader `/pilot`, which also catches names like `pilot_native_mailbox_prototype_*`.
- **Checked** turns a name's check on (`yes`) or off (`no`) one by one, such as while a branch that still uses the old name, like SASPilot's own docs, catches up, so it can merge main without failing.
- History records keep their own wording: the dev logs, the `commit_diffs` corpus, archived changelogs, the source-analysis records (the C++ File Audit Album and the archaeology record), the recorders' revision histories and this folder.
  - They name old names on purpose, such as commit titles quoted as written ("Add BBAI and SASGameSummary AI Settler security information") or the rename itself.

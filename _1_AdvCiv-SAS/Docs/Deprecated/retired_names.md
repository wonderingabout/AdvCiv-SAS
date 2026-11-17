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
| `the pilot` | `SASPilot` | yes | 2026-11-17 | Early SASPilot entries called it "the pilot", which only reads clearly beside SASPilot's own docs; on main, without them, it is vague and clashes with the ordinary sense, as in SGR 180's "pilot" of causal links. |

- Matching ignores case and takes whole words only, so "Save transplanter" is caught too, while plural "pilots", as in a harbour's pilots, is not.
- Listed as "the pilot", not plain "pilot": the word also has its ordinary senses here, as in SASGameRecord's revision history, where revision 180 "pilots" causal links, and the Sevopedia's harbour pilots; even " pilot" with a leading space matched two of those. "The pilot" was the nickname itself, and no ordinary use had it.
- **Checked** turns a name's check on (`yes`) or off (`no`) one by one, such as while a branch that still uses the old name, like SASPilot's own docs, catches up, so it can merge main without failing.
- History records keep their own wording: the dev logs, the `commit_diffs` corpus, archived changelogs, the source-analysis records (the C++ File Audit Album and the archaeology record), the recorders' revision histories and this folder.
  - They name old names on purpose, such as commit titles quoted as written ("Add BBAI and SASGameSummary AI Settler security information") or the rename itself.

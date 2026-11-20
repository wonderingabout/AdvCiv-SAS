# Renamed repository paths

Use this reference to translate folder and file paths found in older commits, logs, discussions and historical records into the current ones.

## Menu

- [Legacy documentation](#legacy-documentation)
- [Modding resources](#modding-resources)
- [Dev logs](#dev-logs)
- [Better BTS AI's SVN history](#better-bts-ais-svn-history)

## Legacy documentation

On 2026-11-03, commit `029cd420b` ("Reorganize legacy documentation and image namespaces") replaced `_0_Common_Docs` with a structured `_0_Legacy/Docs/` tree:

| Old path | Current path |
| --- | --- |
| `_0_Common_Docs/AdvCiv_Base_Doc/`, earlier `AdvCiv Base Doc/` | `_0_Legacy/Docs/AdvCiv/` |
| `_0_Common_Docs/BBAI_Doc/`, earlier `BBAI Doc/` | `_0_Legacy/Docs/BBAI/` |
| `_0_Common_Docs/BUG_Doc/`, earlier `BUG Doc/` | `_0_Legacy/Docs/BUG/` |
| `_0_Common_Docs/CIV4BUG_Sourceforge_net_All_Classes_Doc/civ4bug_pythonAPI_AllClasses_html.txt`, earlier in `CIV4BUG Sourceforge net All Classes Doc/` | `_0_Legacy/Docs/Civ4BUG_Python_API/all_classes_web.txt` |
| `_0_Common_Docs/K-Mod_Doc/`, earlier `K-Mod Doc/` | `_0_Legacy/Docs/K-Mod/` |
| `_0_Common_Docs/git_logs/` | `_0_Legacy/Docs/git_logs/`, since 2026-11-17 `_0_Legacy/Docs/dev_logs/`, see below |

- Why: "Common" did not say what the folder held, inherited documentation from the mods AdvCiv-SAS builds on. `_0_Legacy` names it and pairs with `_1_AdvCiv-SAS`, separating inherited reference material from our own, and its `Images/` folder took the base-AdvCiv UI screenshots in the same move.
  - The `_Doc` suffixes and the long SourceForge-derived names repeated what the folder already says, so they were shortened; the [Legacy README](/_0_Legacy/README.md) records each source.
- Our own records were updated to the new paths on 2026-11-17, the [C++ File Audit Album](/_1_AdvCiv-SAS/Docs/Source_Analysis/cpp_file_audit_album.txt) included, for easier grepping and archiving.

## Modding resources

On 2026-11-10, commit `3d6f100d1` ("Group LLM_Helpers into folders named by job, tidy the Docs folders, …") renamed the modding guides' folder and moved the two logging guides into it:

| Old path | Current path |
| --- | --- |
| `_1_AdvCiv-SAS/Docs/Modding_Ressources/` | `_1_AdvCiv-SAS/Docs/Modding_Resources/` |
| `_1_AdvCiv-SAS/Docs/README_Logging_Inventory.md` | `_1_AdvCiv-SAS/Docs/Modding_Resources/README_Logging_Inventory.md` |
| `_1_AdvCiv-SAS/Docs/README_Logging_Flushing_Comparison.md` | `_1_AdvCiv-SAS/Docs/Modding_Resources/README_Logging_Flushing_Comparison.md` |

- Why: "Ressources" is the French spelling; the folder took the English one, like the rest of the repository.
- Old names remain where they match old commits: the markdownlint ignore globs for the archived changelogs and a commit-diff filtering test.
  - The user's Google Drive folder is still titled "Modding_Ressources", which AGENTS.md quotes as that folder's real title.
  - So the old spelling is not in the [retired names](/_1_AdvCiv-SAS/Docs/Deprecated/retired_names.md) check, which would fail on those correct uses.

## Dev logs

On 2026-11-17 both `git_logs` folders became `dev_logs`, and their files were renamed to match:

| Old path | Current path |
| --- | --- |
| `_0_Legacy/Docs/git_logs/git_log_anonymized_email_001_K-Mod.txt` | `_0_Legacy/Docs/dev_logs/dev_log_anonymized_email_001_K-Mod.txt` |
| `_0_Legacy/Docs/git_logs/git_log_anonymized_email_002_Base_AdvCiv.txt` | `_0_Legacy/Docs/dev_logs/dev_log_anonymized_email_002_Base_AdvCiv.txt` |
| `_1_AdvCiv-SAS/Docs/git_logs/git_log_anonymized_email_003_AdvCiv-SAS.txt` | `_1_AdvCiv-SAS/Docs/dev_logs/dev_log_anonymized_email_003_AdvCiv-SAS.txt` |

The light-source ZIP's generated files followed: `_SNAPSHOT_CONTEXT/git_log_since_tracked_advciv_sas_log.txt` became `dev_log_since_tracked_advciv_sas_log.txt`, and `pending_upstream/GIT_LOG.txt` became `DEV_LOG.txt`.

- Why: Better BTS AI (BBAI) is part of AdvCiv-SAS's older history, after Civ4CE's vanilla, Warlords and BtS code and before K-Mod, but its history came from SVN rather than Git.
  - The `commit_diffs` corpus lacked it, which showed while tracing KI#1090.2's bindings, and so did the message logs. Whether a revision came from Git or SVN, it is the same development history, so "dev" names it without the distinction.
  - Since the same change, `commit_diffs` holds its revisions as `BBAI_r<revision>.diff`, as the next section explains, and `_0_Legacy/Docs/dev_logs/dev_log_anonymized_email_000_BBAI.txt` holds their messages.
  - The two folders stay apart, as the repository splits inherited from SAS material: the pre-SAS logs are finished history, while the SAS log grows with each update. One numbering runs across both, and the same folder name finds both in one search; `commit_diffs` remains the single place to search all history at once.
- Old names remain where history needs them:
  - Commits before the rename, and so the `commit_diffs` corpus generated from them, keep the old paths.
  - The ZIP still summarizes `/git_logs/` and `/git_log_anonymized_email.txt` beside the new names, so those old commits stay summarized.
  - Our own records, the C++ File Audit Album and Known Issues included, cite the new paths; only verbatim copies such as the dev logs and published changelogs keep the old ones.

## Better BTS AI's SVN history

On the same day, Better BTS AI's SVN export moved into the `commit_diffs` corpus:

| Old path | Current path |
| --- | --- |
| `LLM_Helpers/context/svn_history/bbai/BBAI_r<revision>.diff` | `LLM_Helpers/context/commit_diffs/BBAI_r<revision>.diff` |
| `LLM_Helpers/context/svn_history/bbai/INDEX.txt` | its rows, segment `BBAI`, in `LLM_Helpers/context/commit_diffs/INDEX.txt` |
| `LLM_Helpers/context/svn_history/bbai/PATH_HISTORY_INDEX.txt` | its rows, `BBAI r<revision> …`, in `LLM_Helpers/context/commit_diffs/PATH_HISTORY_INDEX.txt` |

- Why: we used to keep separate homes for SVN and Git history, its diffs in `svn_history/` and our Git commits in `commit_diffs/`. That was brittle, easy to forget and needless: whichever system recorded it, it is all our history, and in one home a single grep covers every layer.
  - The `BBAI_r*.diff` files stay tracked there, while everything else in `commit_diffs/` is generated and Git-ignored, because our Git cannot regenerate SVN history.
  - The export's two index files were dropped: each revision file's header holds the same data, and rebuilding from the headers reproduced all 597 index rows and all 10,249 path rows exactly.
- Old names remain where history needs them: commits before the move keep the old paths, and the ZIP still keeps their patches out of our own commit diffs. Known Issues that cited the old folder now cite `commit_diffs/`.

Prepared by Claude code Opus 5.5, 2026-11-17.

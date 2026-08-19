AdvCiv-SAS tracked commit-diff history mirror
===========================================

Purpose
-------
This directory is a greppable repository copy of the same filtered reachable-history patches normally generated inside a light-source ZIP at:
  _SNAPSHOT_CONTEXT/commit_diffs/

It exists so a normal GitHub clone, Codex/code agent, IDE search, or local grep can investigate K-Mod -> pre-SAS AdvCiv -> AdvCiv-SAS history without first generating or unpacking a handoff ZIP.

Authority and synchronization
-----------------------------
Current repository source and Git history remain authoritative. This directory is generated review/index data and can lag HEAD until explicitly synchronized.

Refresh it from the repository root with:
  python LLM_Helpers/sync_tracked_commit_diffs.py

Preview a refresh without changing files/cache with:
  python LLM_Helpers/sync_tracked_commit_diffs.py --dry-run

The synchronizer reuses make_light_source_zip.py's exact history segmentation, privacy filtering, patch-size limits, INDEX.txt generation, PATH_HISTORY_INDEX.txt generation, and commit reuse policy. The private .git SHA cache is checked first, then this tracked mirror is accepted as a read-only secondary cache when an entry validates against the current policy; Git renders only missing/new entries. Stale generated commit files are removed when history is rewritten.

Self-recursion guard
--------------------
LLM_Helpers/commit_diffs/ is deliberately excluded from the historical patches produced by make_light_source_zip.py. It is also skipped as an ordinary file tree when producing a light-source ZIP, which instead generates a fresh _SNAPSHOT_CONTEXT/commit_diffs/ copy directly from Git.

Without that exclusion, a tracked archive refresh would be recorded inside later archived diffs, causing recursive history-of-history growth.

Because a Git commit cannot contain a diff of its own not-yet-existing SHA, a synchronized tracked mirror naturally stops at the committed HEAD from which it was generated. The later commit that records the refreshed mirror is therefore not represented until a future synchronization; this small lag is expected and harmless.

Navigation
----------
Start with INDEX.txt for chronological/segment metadata or PATH_HISTORY_INDEX.txt to find commits touching a known repository path, then open the matching <segment>_<practical-count>_<short-sha>.diff file.

The tracked mirror is development/LLM infrastructure and is export-ignored from player/release archives.

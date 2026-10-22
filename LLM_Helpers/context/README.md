# Shared development context

This directory contains development reference data for local code agents and light-source handoffs. It is not Civ4 runtime content, and `.gitattributes` excludes it from player/release archives.

- `commit_diffs/` is a **Git-ignored, locally generated** mirror of filtered current-`HEAD` ancestry with `INDEX.txt`, `PATH_HISTORY_INDEX.txt`, and per-commit diff files. Git history is authoritative. Refresh the local mirror independently with `python LLM_Helpers/refresh_commit_diffs.py`; normal full-history light-source ZIP creation generates the same context for the archive and refreshes the local mirror after the ZIP succeeds. The private immutable-SHA cache under Git metadata avoids rerendering unchanged commits. The directory is intentionally not tracked because its contents are reproducible from Git and tracking them would duplicate repository history inside repository history.
- [`commit_rewrite_map_6164_6402.tsv`](/LLM_Helpers/context/commit_rewrite_map_6164_6402.tsv) translates pre-rewrite SHAs from the one-time 2026 cleanup; the [deprecated commit-identifier reference](/_1_AdvCiv-SAS/Docs/Deprecated/commit_rewrites.md) provides its dedicated documentation entry point.
  - Practical commits 1-6163 were left byte-for-byte unchanged. Practical commits 6164-6402 were rewritten only to remove the formerly tracked generated `commit_diffs` corpus from history.
  - Practical counts, commit subjects, author dates and committer dates were preserved; embedded references to rewritten SHAs in commit messages may have been translated to their canonical replacements.
- No automatic SHA-rewrite helper is tracked permanently. The one-time migration used a temporary byte-safe helper only on files known to contain pre-rewrite references.
  - A future canonical commit can share a short SHA prefix with an old pre-rewrite commit, so automatic prefix replacement and a permanent CI ban on old short prefixes would be unsafe.
  - For an old reference, establish that it belongs to the pre-rewrite practical 6164-6402 history, then translate it through the table.
- `mapscript_refs/` contains imported upstream/third-party map-script originals for provenance and inherited-regression comparisons. These files are immutable reference sources rather than playable `PrivateMaps` files and are tracked because they are not reproducible from this repository's Git ancestry.

Generated commit diffs and imported map-script references are both excluded from generated historical patches so they cannot create recursive history-of-history output or drown runtime-source archaeology in reference-data churn.

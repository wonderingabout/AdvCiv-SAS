# Shared development context

This tracked, greppable context is shared by local Codex/code agents, GitHub/file-only reviewers, and the AdvCiv-SAS light-source ZIP. It is development reference data, not Civ4 runtime content, and `.gitattributes` excludes it from player/release archives.

- `commit_diffs/` contains filtered current-`HEAD` ancestry with `INDEX.txt` and `PATH_HISTORY_INDEX.txt`. Refresh it independently with `python LLM_Helpers/refresh_commit_diffs.py`; normal full-history light-source ZIP creation refreshes the same canonical directory after successfully writing the archive. The private immutable-SHA cache under Git metadata avoids rerendering unchanged commits.
- `mapscript_refs/` contains imported upstream/third-party map-script originals for provenance and inherited-regression comparisons. The files are immutable references rather than playable `PrivateMaps` sources.

Both directories are excluded from generated historical patches so their own generated/imported revisions cannot obscure runtime-source history or create recursive history-of-history patches.

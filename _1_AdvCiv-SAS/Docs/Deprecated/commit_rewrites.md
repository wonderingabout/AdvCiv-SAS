# Rewritten commit identifiers

The one-time 2026 history cleanup removed the formerly tracked, generated `commit_diffs` corpus from historical commits. The old commit identifiers remain useful for locating references in earlier discussions and logs.

## Translation table source

[`commit_rewrite_map_6164_6402.tsv`](/LLM_Helpers/context/commit_rewrite_map_6164_6402.tsv) maps each old SHA to its canonical replacement for practical commits 6164-6402. Practical commits 1-6163 were unchanged.

The rewrite preserved practical counts, commit subjects, author dates and committer dates; embedded references to rewritten SHAs in commit messages may have been translated to their canonical replacements.

The table remains at that existing path. This document supplies the historical-reference entry point without copying the data.

Translate a SHA only after establishing that it belongs to this rewrite. A short prefix alone is insufficient evidence.

The one-time migration used a temporary byte-safe helper on files known to contain pre-rewrite references; no automatic SHA-rewrite helper is tracked permanently. Later canonical commits can share short prefixes with old commits, so automatic prefix replacement or a permanent CI ban on those prefixes would be unsafe.

Prepared by GPT-6.1-Sol, 2026-10-22.

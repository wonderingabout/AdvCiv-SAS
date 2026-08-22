# Web changelog working files

This folder keeps AdvCiv-SAS release-changelog examples, drafts, and continuation checkpoints in Git for future user/LLM release work. The whole folder is `export-ignore`, so none of these working/reference files are included in GitHub Download ZIP / `git archive` player packages.

## Current next-release draft

- `changelog_next_release_checkpoint_12_stable_to_current.txt` is the current preserved content checkpoint built from the last stable AdvCiv-SAS 6020 release toward the current next-release candidate. It adds a more complete AI pass and release-facing source-archaeology framing.
- `changelog_next_release_checkpoint_12_cfc_spacing.txt` contains the same checkpoint with CFC-oriented spacing: no blank lines between individual items inside a section. Section boundaries remain separated for readability.
- Checkpoints 10 and 11 are retained as recovery points.
- `changelog_next_release_checkpoint_state.txt` records the most important continuation rules so a later LLM can resume without reconstructing the workflow.
- `changelog_release_example_6020.txt` is the previous published-style reference/example.

The current draft is close but not final. The user may prefer to rewrite the release overview/introduction personally so it expresses the release's overall purpose in exactly the intended voice. LLM effort should therefore prioritize the body: exhaustively recover meaningful shipped changes, rationale, and useful numerical values, while keeping the prose compact enough for web publication.

For the public changelog, always compare the previous stable release directly with the final new release. Temporary development-only names, values, designs, and experiments between those two states are evidence for understanding the final change, not player-facing history.

CivFanatics currently limits an individual post to about 50,000 characters and ModDB to about 100,000 characters. Do not sacrifice important body substance too early merely to hit one-post length: preserve meaningful content first, then trim or split the CFC version if necessary. The user's web formatting can provide indentation/list presentation, so final CFC-oriented drafts should not put blank lines between each item within a section.

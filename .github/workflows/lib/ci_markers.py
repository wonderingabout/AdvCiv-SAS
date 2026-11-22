# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The markers a commit message carries to state an intent the change alone cannot show; the checks still run and verify the change against it, unlike GitHub's [skip ci], which silences them.
# They were plain phrases before (2026-11-22): "Update DLL", taken from base AdvCiv's commits, "Edit dev log" and "Convert line endings", each in its own check, and a squash-merge intent read from "(draft)" in commit titles.
# The user wanted one recognizable family and one spelling per intent, so each is now one bracketed token, greppable as "[ci_", and kept here once for every check that reads it. (Claude code Opus 5.5) -->
UPDATE_DLL = "[ci_update_dll]"
EDIT_DEV_LOG = "[ci_edit_dev_log]"
CONVERT_LINE_ENDINGS = "[ci_convert_line_endings]"
SQUASH_PR = "[ci_squash_pr]"

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The markers a commit message carries to state an intent the change alone cannot show; the checks still run and verify the change against it, unlike GitHub's [skip ci], which silences them.
# They were plain phrases before (2026-11-22): "Update DLL", taken from base AdvCiv's commits, "Edit dev log" and "Convert line endings", each in its own check, and a squash-merge intent read from "(draft)" in commit titles.
# The user wanted one recognizable family and one spelling per intent, so each is now one bracketed token, greppable as "[ci_", and kept here once for every check that reads it. (Claude code Opus 5.5) -->
UPDATE_DLL = "[ci_update_dll]"
EDIT_DEV_LOG = "[ci_edit_dev_log]"
CONVERT_LINE_ENDINGS = "[ci_convert_line_endings]"
SQUASH_PR = "[ci_squash_pr]"

# <!-- custom: The markers a source comment carries to state why a line is a handled exception to a check; kept here too since 2026-11-25, so one file lists every token CI reads and ci_markers_listed.py can require each in the workflows README.
# They grew apart, each check choosing its own: resource-cache-direct: (2026-10-20), sas-ci-string-compare-exemption: (2026-11-16) and ci_define_uncached:, which the user asked to be specific, as generic words such as "Not cached:" can appear in any prose and exempt a line unnoticed. (Claude code Opus 5.5) -->
RESOURCE_CACHE_DIRECT = "resource-cache-direct:"
STRING_COMPARE_EXEMPTION = "sas-ci-string-compare-exemption:"
DEFINE_UNCACHED = "ci_define_uncached:"
# <!-- custom: A module-level call whose define reads cannot run at import, for the reason given, such as CvEventInterface's initAfterReload(), whose reads sit behind BugInit.init(), which does not succeed while the game is still initializing; python_define_reads_import.py does not follow it (2026-11-26). See KI#128.6. (Claude code Opus 5.5) -->
IMPORT_CALL = "ci_import_call:"
# <!-- custom: A module that holds plain values only and imports nothing, such as SASMagicNumbers.py and SASSessionTunables.py, so any module can import it at any time; python_pure_modules.py keeps it so. (Claude code Opus 5.5) -->
PURE_MODULE = "ci_pure_module:"

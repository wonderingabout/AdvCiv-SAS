#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: hands-free switches, which spare players clicks and manual steps, must ship with their player-facing values.

# <!-- custom: Players should see what ships; developers and agents switch some of these off locally with LLM_Helpers/diagnostics/toggle_dev_diagnostics.py, as with the diagnostic logs, so a forgotten local value must not reach a commit.
# The others are not toggled locally, but one switched off by mistake would bring back the clicks or lost saves it removes, so the check covers every hands-free switch the Main Changes Guide describes. (Claude Code Opus 5.5) -->

from pathlib import Path
import argparse
import sys

# <!-- custom: Resolve the shared XML define reader from this subject subfolder, as aip.py does. (Claude Code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import add_staged_argument, get_default_repo_root, read_global_define_ints, require_int_values


EXPECTED_SHIPPED_VALUES = {
	"SAS_UI_DAWN_OF_MAN_ON": 1,
	"SAS_AIAUTOPLAY_DISMISS_INFO_POPUPS_ON": 1,
	"SAS_AIAUTOPLAY_DEFAULT_SCALE_BY_SPEED_ON": 1,
	"SAS_FAST_SAVE_GAME_START_ON": 1,
	"SAS_FAST_SAVE_GAME_END_ON": 1,
	"SAS_FAST_SAVE_AUTOPLAY_STOP_ON": 1,
	"SAS_SCOREBOARD_AUTOCENTER_DEFAULT_ON": 1,
	"SAS_ASSERT_SILENT_ACTION": 1,
}


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that hands-free development switches ship with their player-facing values.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	add_staged_argument(parser)
	args = parser.parse_args()

	failures = require_int_values(read_global_define_ints(args.repo_root, args.staged), EXPECTED_SHIPPED_VALUES)
	if failures:
		print("FAIL hands-free switch shipped values")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print("PASS hands-free switch shipped values")
	return 0


if __name__ == "__main__":
	sys.exit(main())

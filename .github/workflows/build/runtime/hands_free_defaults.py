#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: switches that local development turns off for hands-free runs must ship with their player-facing values.

# <!-- custom: Players should see what ships; developers and agents switch these off locally with LLM_Helpers/diagnostics/toggle_dev_diagnostics.py, as with the diagnostic logs, so a forgotten local value must not reach a commit. (Claude Code Opus 5.5) -->

from pathlib import Path
import argparse
import sys

# <!-- custom: Resolve the shared XML define reader from this subject subfolder, as aip.py does. (Claude Code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import add_staged_argument, get_default_repo_root, read_global_define_ints, require_int_values


EXPECTED_SHIPPED_VALUES = {
	"SAS_UI_DAWN_OF_MAN_ON": 1,
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

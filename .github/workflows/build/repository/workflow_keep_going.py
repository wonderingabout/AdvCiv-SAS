#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Every check step of checks-*.yml must keep running after an earlier check fails, so one push reports every failure.
# A step added without that condition is skipped after any earlier failure, and nothing would show it: the workflow stays valid and passes whenever the checks pass.
# Whether a script itself collects all its findings is left to review: an audit of 95 scripts on 2026-11-09 flagged 25 by their exits, of which about 6 really stopped early. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; pathlib finds the workflows; re finds their steps; sys reports the result and reaches the shared helpers. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import sys

# <!-- custom: Resolve shared-helper paths from this subject subfolder, as the other repository checks do. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root

WORKFLOWS = Path(".github/workflows")
KEEP_GOING = "if: ${{ !cancelled() && steps.setup.outcome == 'success' }}"
STEP = re.compile(r"^\s*- (name|uses|run):\s*(.*)$")


def check_workflow(name, text):
	# <!-- custom: Reads the text, as the runner's Python has no YAML module. (Claude code Opus 5.5) -->
	lines = text.splitlines()
	setup = next((k for k, line in enumerate(lines) if line.strip() == "id: setup"), None)
	if setup is None:
		return [f"{name}: its setup step has no 'id: setup', which the keep-going condition needs"]
	failures = []
	for k in range(setup + 1, len(lines)):
		step = STEP.match(lines[k])
		if not step:
			continue
		following = next((line.strip() for line in lines[k + 1:] if line.strip() and not line.strip().startswith("#")), "")
		if following != KEEP_GOING:
			failures.append(f"{name}:{k + 1}: step {step.group(2)!r} needs '{KEEP_GOING}' right after its name")
	return failures


def main():
	parser = argparse.ArgumentParser(description="Check that every check step of checks-*.yml keeps running after an earlier check fails.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	paths = sorted((args.repo_root / WORKFLOWS).glob("checks-*.yml"))
	failures = [failure for path in paths for failure in check_workflow(path.name, path.read_text(encoding="utf-8"))]
	if failures:
		print("FAIL workflow keep-going steps")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS workflow keep-going steps ({len(paths)} workflows)")
	return 0


if __name__ == "__main__":
	sys.exit(main())

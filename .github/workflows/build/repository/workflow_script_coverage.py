#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Every check script under .github/workflows/build must be run by a workflow: on 2026-11-16 string_label_compares.py sat in build/source, passing locally, while no workflow ran it, and no check noticed.
# A script counts as run when a workflow names its path; shared helpers in lib/ and modules whose names start with "_" are imported, not run, so they are left out.
# Its README section is checked by folder_indexes.py, so an unwired script and an undocumented one each fail on their own. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; pathlib finds the scripts and workflows; sys reports the result and reaches the shared helpers. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import sys

# <!-- custom: Resolve shared-helper paths from this subject subfolder, as the other repository checks do. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root

WORKFLOWS = Path(".github/workflows")
BUILD = WORKFLOWS / "build"


def check_scripts(scripts, workflow_text):
	return ["%s is not run by any workflow; add a step to the matching checks-*.yml" % script for script in scripts if script not in workflow_text]


def build_scripts(root):
	# <!-- custom: Paths relative to the repository root, with forward slashes, as the workflows write them. (Claude code Opus 5.5) -->
	scripts = []
	for path in sorted((root / BUILD).rglob("*.py")):
		relative = path.relative_to(root)
		if "__pycache__" in relative.parts or "lib" in relative.parts or path.name.startswith("_"):
			continue
		scripts.append(relative.as_posix())
	return scripts


def main():
	parser = argparse.ArgumentParser(description="Check that every check script under .github/workflows/build is run by a workflow.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	scripts = build_scripts(args.repo_root)
	workflow_text = "\n".join(path.read_text(encoding="utf-8") for path in sorted((args.repo_root / WORKFLOWS).glob("*.yml")))
	failures = check_scripts(scripts, workflow_text)
	if failures:
		print("FAIL workflow script coverage")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS workflow script coverage (%d scripts)" % len(scripts))
	return 0


if __name__ == "__main__":
	sys.exit(main())

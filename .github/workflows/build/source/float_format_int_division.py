#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python must not format an integer division with %.Nf.
# <!-- custom: Python 2.4 divides two integers to an integer, so "%.2f" % (a * 100 / b) always prints .00: vanilla Civ4's Victory screen showed the best rival's population and land shares as 2.00% for 2.30% and 2.06% at turn 120 of a SAS48 islands autoplay (2026-11-15), while ours, computed with 100.0, kept its decimals.
# A line is flagged when a %.Nf format is applied to arguments that divide with no float in them (no literal such as 100.0, no float()); a division by a value already float passes only with one of those, so convert it there.
# KI#290 itself, the same mechanism in a map script's angles, shows in no format, so this check does not cover it. See KI#290.2. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


# <!-- custom: The folders the game runs Python from come from lib/runtime_python.py, one list for every runtime Python check, so a new one is added once (2026-11-27). (Claude code Opus 5.5) -->
from runtime_python import RUNTIME_PYTHON_DIRS
SCAN_RELATIVE_DIRS = tuple(Path(folder) for folder in RUNTIME_PYTHON_DIRS)
FLOAT_FORMAT_APPLIED = re.compile(r'%[-+ 0#]*\d*\.\d*f[^"\']*["\']\s*%\s*(.*)$')
FLOAT_MARKER = re.compile(r'\d\.\d|\d\.(?!\w)|\bfloat\s*\(')
DIVISION = re.compile(r'[\w)\]]\s*/\s*[\w(]')


def find_problems(repo_root):
	problems = []
	for relative in SCAN_RELATIVE_DIRS:
		folder = repo_root / relative
		if not folder.is_dir():
			continue
		for path in sorted(folder.rglob("*.py")):
			text = path.read_text(encoding="utf-8", errors="replace")
			for number, line in enumerate(text.splitlines(), 1):
				if line.lstrip().startswith("#"):
					continue
				match = FLOAT_FORMAT_APPLIED.search(line)
				if not match:
					continue
				arguments = match.group(1)
				if DIVISION.search(arguments) and not FLOAT_MARKER.search(arguments):
					problems.append("%s:%d: %%.Nf applied to an integer division - write 100.0 or float() so Python 2.4 keeps the decimals (KI#290.2)" % (path.relative_to(repo_root).as_posix(), number))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that runtime Python never formats an integer division with %.Nf.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve())
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL float format integer division (%d)" % len(problems))
		return 1
	print("PASS float format integer division")
	return 0


if __name__ == "__main__":
	sys.exit(main())

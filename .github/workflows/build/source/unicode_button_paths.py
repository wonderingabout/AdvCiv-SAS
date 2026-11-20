#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python must not start a button or icon path as u"".
# <!-- custom: The engine's icon arguments, such as setTableText's, take char const*, so a unicode icon raises a Boost ArgumentError; CvVictoryScreen set szNameButton = u"" for a vote building built by an unmet team, and the whole Victory screen broke at turn 120 of a SAS48 island autoplay (2026-11-15).
# SASTextScale now passes icons through str(), but a direct screen call does not, so paths start as plain "". Names ending in Icons (plural) hold icon characters for text and stay unicode. See KI#118.2. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import re
import sys

# <!-- custom: xml_defines from the workflows' lib/ gives the repository root, as the other build checks find it. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


SCAN_RELATIVE_DIRS = (Path("Assets/Python"), Path("PrivateMaps"))
UNICODE_PATH_DEFAULT = re.compile(r'\b(sz\w*(?:Button|Icon))\s*=\s*u(""|\'\')')


def find_problems(repo_root):
	problems = []
	for relative in SCAN_RELATIVE_DIRS:
		for path in sorted((repo_root / relative).rglob("*.py")):
			text = path.read_text(encoding="utf-8", errors="replace")
			for number, line in enumerate(text.splitlines(), 1):
				if line.lstrip().startswith("#"):
					continue
				match = UNICODE_PATH_DEFAULT.search(line)
				if match:
					problems.append('%s:%d: %s = u"" - start button and icon paths as plain "", as the engine takes them as char const* (KI#118.2)' % (path.relative_to(repo_root).as_posix(), number, match.group(1)))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that runtime Python never starts a button or icon path as u\"\".")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve())
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL unicode button paths (%d)" % len(problems))
		return 1
	print("PASS unicode button paths")
	return 0


if __name__ == "__main__":
	sys.exit(main())

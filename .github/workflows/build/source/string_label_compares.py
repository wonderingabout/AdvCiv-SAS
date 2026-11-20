#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: KI#300.2's first draft told its two kinds of Timeline events apart with "city" and "player" strings; a misspelt one would have compared false without any error, and the same review found three Sevopedia screens doing the same (2026-11-16).
# So a comparison of runtime Python with a short lowercase string literal must carry a "sas-ci-string-compare-exemption: <reason>" note on its line or the line above, inside a credited custom comment like any other: a label of our own is better as a boolean, a widget or a value that fails when misspelt, while a string read from outside (a BUG option type, XML "true") is fine with its reason.
# Inherited files that compare values read from their own option files are skipped whole. (Claude code Opus 5.5) -->
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCAN = (Path("Assets/Python"), Path("PrivateMaps"))
COMPARE = re.compile(r"""(?:==|!=)\s*u?(["'])[a-z][a-z_]*\1|u?(["'])[a-z][a-z_]*\2\s*(?:==|!=)""")
NOTE = "sas-ci-string-compare-exemption:"
# <!-- custom: Inherited files SAS does not extend: BUG's option-type core and unit-naming codes, which compare values read from option files or the player's naming pattern, and Planet Generator, a third-party map script whose options are its own string labels, where SAS only fixes bugs.
# A file SAS edits stays checked with reason notes instead, so a label added there later is still caught: the Customizable Domestic Advisor was first skipped whole, though SAS works in it. (Claude code Opus 5.5) -->
SKIP = {
	"Assets/Python/BUG/BugOptions.py",
	"Assets/Python/Contrib/UnitNameEventManager.py",
	"PrivateMaps/Planet_Generator_0_68.py",
}


def code_part(line):
	# <!-- custom: The comparison must be in code, not in a comment; a '#' inside a string is rare enough here to ignore. (Claude code Opus 5.5) -->
	return line.split("#", 1)[0]


def noted(lines, index):
	return NOTE in lines[index] or (index > 0 and NOTE in lines[index - 1])


def chain_head(lines, index):
	# <!-- custom: The if that starts the if/elif chain holding this elif, so one note above an if covers its elif branches, as in a dispatch on one value. (Claude code Opus 5.5) -->
	line = lines[index]
	indent = line[:len(line) - len(line.lstrip())]
	for back in range(index - 1, -1, -1):
		previous = lines[back]
		if not previous.strip() or previous.startswith(indent + "\t") or previous.startswith(indent + " ") or previous.strip().startswith("#"):
			continue
		if previous.startswith(indent + "elif"):
			continue
		if previous.startswith(indent + "if"):
			return back
		return None
	return None


def file_errors(path, relative):
	lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
	errors = []
	for index, line in enumerate(lines):
		if not COMPARE.search(code_part(line)):
			continue
		if noted(lines, index):
			continue
		if line.lstrip().startswith("elif"):
			head = chain_head(lines, index)
			if head is not None and noted(lines, head):
				continue
		errors.append("%s:%d: comparison with a string literal without a '%s <reason>' note: %s" % (relative, index + 1, NOTE, line.strip()[:120]))
	return errors


def main():
	parser = argparse.ArgumentParser(description="Require a reason for string-literal comparisons in runtime Python.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	files = sorted(path for folder in SCAN for path in (args.repo_root / folder).rglob("*.py"))
	errors = []
	for path in files:
		relative = path.relative_to(args.repo_root).as_posix()
		if relative not in SKIP:
			errors.extend(file_errors(path, relative))
	if errors:
		print("FAIL string label comparisons")
		for error in errors:
			print("  - " + error)
		return 1
	print("PASS string label comparisons (%d file(s) checked)" % len(files))
	return 0


if __name__ == "__main__":
	sys.exit(main())

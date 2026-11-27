#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: a custom comment is not indented deeper than both the code line
# before it and the code line after it.
#
# <!-- custom: A scripted edit once inserted retirement notes two levels too deep in RiseFall.cpp and GroupPathFinder.cpp; the code compiled, so only a review noticed.
# Comparing with only the next code line flagged legitimate end-of-block notes, so both neighbours must be shallower, and a comment directly under a block opener (`{`, `:`, `(`, `,`, `\`) is skipped. See KI#136. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import sys

SOURCE_GLOBS = ("CvGameCoreDLL/*.cpp", "CvGameCoreDLL/*.h", "Assets/Python/**/*.py", "PrivateMaps/*.py")
CUSTOM_PREFIXES = ("// <!-- custom:", "# <!-- custom:")
COMMENT_PREFIXES = ("//", "#", "/*", "*")
BLOCK_OPENERS = ("{", ":", "(", ",", "\\")


def indent(line: str) -> int:
	return len(line) - len(line.lstrip(" \t"))


def is_code(line: str) -> bool:
	return line.strip() != "" and not line.lstrip(" \t").startswith(COMMENT_PREFIXES)


def check_lines(name: str, lines: list[str]) -> list[str]:
	failures: list[str] = []
	for i, line in enumerate(lines):
		if not line.lstrip(" \t").startswith(CUSTOM_PREFIXES):
			continue
		# <!-- custom: The line directly above, comment or code: a commented-out block opener legitimately nests the note. (Claude code Opus 5.5) -->
		above = i - 1
		while above >= 0 and lines[above].strip() == "":
			above -= 1
		if above >= 0 and lines[above].rstrip().endswith(BLOCK_OPENERS):
			continue
		prev = i - 1
		while prev >= 0 and not is_code(lines[prev]):
			prev -= 1
		nxt = i + 1
		while nxt < len(lines) and not is_code(lines[nxt]):
			nxt += 1
		if prev < 0 or nxt >= len(lines):
			continue
		if indent(line) > indent(lines[prev]) and indent(line) > indent(lines[nxt]):
			failures.append(f"{name}:{i + 1}: custom comment is indented deeper than the code before ({indent(lines[prev])}) and after ({indent(lines[nxt])}) it")
	return failures


def check_repo(repo_root: Path) -> list[str]:
	failures: list[str] = []
	for pattern in SOURCE_GLOBS:
		for path in sorted(repo_root.glob(pattern)):
			try:
				text = path.read_bytes().decode("utf-8")
			except UnicodeDecodeError:
				# <!-- custom: Legacy non-UTF-8 files carry no custom comments worth this check. (Claude code Opus 5.5) -->
				continue
			failures.extend(check_lines(path.relative_to(repo_root).as_posix(), text.replace("\r\n", "\n").split("\n")))
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that custom comments are not indented deeper than the code around them.")
	parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4], help="repository root")
	args = parser.parse_args()
	failures = check_repo(args.repo_root)
	if failures:
		print("FAIL custom comment indentation")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print("PASS custom comment indentation")
	return 0


if __name__ == "__main__":
	sys.exit(main())

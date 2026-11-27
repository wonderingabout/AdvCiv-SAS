#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every lint or type-checker suppression in our Python names its rule and says why.

# <!-- custom: AGENTS.md asks to avoid noqa, and when one is needed to name the rule and explain it nearby; on 2026-11-12 two had slipped in, one with no reason at all, both for a late import after a sys.path entry.
# Both were fixed at the cause, by loading the module with importlib; this check keeps any new suppression honest instead of relying on review. (Claude code Opus 5.5) -->
import argparse
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Verbatim third-party copies keep their own comments. (Claude code Opus 5.5) -->
SKIPPED = ("LLM_Helpers/context/", "_0_Legacy/")
SUPPRESSION = re.compile(r"#\s*(noqa|type:\s*ignore|pyright:\s*ignore)\b(.*)", re.I)
# <!-- custom: A named rule: noqa: E402, type: ignore[attr-defined], pyright: ignore[reportMissingImports]. (Claude code Opus 5.5) -->
RULE = re.compile(r"^(?::\s*[A-Z]+[0-9]+(?:\s*,\s*[A-Z]+[0-9]+)*|\[[A-Za-z0-9_,\- ]+\])")
MIN_REASON = 10


def comments(text: str) -> list[tuple[int, str]]:
	found = []
	try:
		for token in tokenize.generate_tokens(io.StringIO(text).readline):
			if token.type == tokenize.COMMENT:
				found.append((token.start[0], token.string))
	except (tokenize.TokenError, SyntaxError, IndentationError):
		# <!-- custom: Python 2 files, such as Civ4's runtime scripts, may not tokenize under Python 3; fall back to whole-line comments there. (Claude code Opus 5.5) -->
		found = [(i, line.strip()) for i, line in enumerate(text.splitlines(), 1) if line.strip().startswith("#")]
	return found


def check_text(text: str) -> list[tuple[int, str]]:
	problems = []
	found = comments(text)
	by_line = {line: comment for line, comment in found}
	for line, comment in found:
		match = SUPPRESSION.search(comment)
		if not match:
			continue
		rest = match.group(2)
		rule = RULE.match(rest)
		if not rule:
			problems.append((line, "%s without a named rule; name it, such as 'noqa: E402' or 'pyright: ignore[reportMissingImports]'" % match.group(1)))
			continue
		reason = rest[rule.end():].strip(" #()-:;,")
		previous = by_line.get(line - 1, "")
		if len(reason) < MIN_REASON and len(previous.strip("# ")) < MIN_REASON:
			problems.append((line, "%s without a reason; fix the cause if possible, or say why on the same line or the line above" % match.group(1)))
	return problems


def tracked_python(root: Path) -> list[Path]:
	out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.py"], cwd=root, capture_output=True, check=True).stdout
	return [root / name for name in out.decode("utf-8").split("\0") if name and not name.startswith(SKIPPED)]


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that every lint or type-checker suppression names its rule and says why.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	failures = []
	for path in tracked_python(args.repo_root):
		if not path.is_file():
			continue
		text = path.read_bytes().decode("utf-8", errors="replace")
		for line, problem in check_text(text):
			failures.append("%s:%d: %s" % (path.relative_to(args.repo_root).as_posix(), line, problem))
	if failures:
		print("FAIL lint suppressions")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS lint suppressions")
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the DLL Makefiles call Windows tools that Git Bash also ships under the same name by their System32 path.

# <!-- custom: The Makefile's build provenance counts objects with DIR /S /B ... | FIND /C /V "", and a bare FIND is whichever find.exe comes first on PATH.
# A build started from Git Bash, or from cmd.exe launched by it, inherits a PATH with C:\Program Files\Git\usr\bin first, and Unix find then crawled all of C: while nmake waited: on 2026-11-11 (README_DLL_Compilation.md) and again on 2026-11-13 through build_dll.py.
# The guide's "not from Git Bash" rule did not stop the second, so the Makefile names %SystemRoot%\System32\find.exe and this check keeps it so.
# SHARED_NAMES are the .exe names found both in Git's usr\bin and in System32 on 2026-11-13. See KI#38.7. (Claude code Opus 5.5) -->
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MAKEFILES = ("CvGameCoreDLL/Project/Makefile", "CvGameCoreDLL/Project/Makefile.project", "CvGameCoreDLL/Project/Makefile.user")
SHARED_NAMES = ("expand", "find", "sort", "tar", "timeout", "whoami")
# <!-- custom: Only where cmd runs a command: a recipe line's start, after @, or after |, &, ( or a quote. The first version matched any word, so "@ECHO sort complete" failed (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
TOOL = re.compile(r"(?:^[\t ]*@?|[|&('][\t ]*)(%s)(?:\.exe)?(?![\w.\\/-])" % "|".join(SHARED_NAMES), re.I)
SYSTEM32 = re.compile(r"System32\\$", re.I)


CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def check_text(name: str, text: str) -> list[str]:
	failures = []
	# <!-- custom: Split on "\n" only: str.splitlines() also breaks at a form feed, which hid the very character the test below plants. (Claude code Opus 5.5) -->
	for number, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
		# <!-- custom: Writing the System32 path through a shell once turned "\find.exe" into a form feed and "ind.exe", which this check's name test could not see; any control character but tab and line ends now fails (2026-11-13). (Claude code Opus 5.5) -->
		if CONTROL.search(line):
			failures.append("%s:%d: control character %r, likely a backslash escape such as \\f taken by a shell or script" % (name, number, CONTROL.search(line).group(0)))
		if line.lstrip().startswith("#"):
			continue
		for match in TOOL.finditer(line):
			if SYSTEM32.search(line[:match.start()].rstrip('"')):
				continue
			failures.append("%s:%d: bare %s resolves through PATH, where Git Bash's Unix %s can come first; call %%SystemRoot%%\\System32\\%s.exe" % (name, number, match.group(1), match.group(1).lower(), match.group(1).lower()))
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that the DLL Makefiles call Windows tools shared with Git Bash by their System32 path.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	failures = []
	for name in MAKEFILES:
		path = args.repo_root / name
		if path.is_file():
			failures += check_text(name, path.read_bytes().decode("latin-1"))
	if failures:
		print("FAIL Makefile Windows tools")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS Makefile Windows tools")
	return 0


if __name__ == "__main__":
	sys.exit(main())

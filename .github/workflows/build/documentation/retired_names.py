#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: We rename old references retroactively, so agents meet only current names.
# On 2026-11-17 SASSaveTransplanter's old plain-English name was replaced across main and its history, yet the same day an agent wrote the old name twice in new text, the dev-log check's comment and its README section, and only the user's review caught it.
# This fails on any name listed in the retired_names.md table outside the history records, so a returning old name is caught when written.
# The table stays the single list, as the retired define and XML asset checks do with theirs. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options, pathlib finds the files, re matches the names, subprocess lists the tracked files, sys reports the result. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
LIST = Path("_1_AdvCiv-SAS/Docs/Deprecated/retired_names.md")
TABLE_HEADER = "| Retired name |"
# <!-- custom: History records keep the wording of their time: the dev logs, the commit_diffs corpus, archived changelogs, the Deprecated folder, which names the old names on purpose, and the source-analysis records and recorders' revision histories, which quote old commit titles and describe the renames themselves, such as SASGameRecord's at practical 6083. (Claude code Opus 5.5) -->
HISTORY = re.compile(r"(^|/)(dev_logs|commit_diffs|changelogs_web|Deprecated|Source_Analysis|revisions)/")
# <!-- custom: The check's test must spell the old names to test them. (Claude code Opus 5.5) -->
EXEMPT = {".github/workflows/tests/documentation/test_retired_names.py"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".xml", ".cpp", ".h", ".yml", ".json", ".ps1", ".bat", ".tsv", ".ini", ".html", ".js", ".css"}


def retired_names(root):
	names = []
	in_table = False
	for line in (root / LIST).read_text(encoding="utf-8").splitlines():
		if line.startswith(TABLE_HEADER):
			in_table = True
			continue
		if in_table and line.startswith("| ---"):
			continue
		if in_table and line.startswith("|"):
			cells = [cell.strip() for cell in line.split("|")]
			# <!-- custom: The Checked column turns each name on or off, so a branch still using an old name can merge main and rename later. (Claude code Opus 5.5) -->
			if cells[3] == "yes":
				names += re.findall(r"`([^`]+)`", cells[1])
			elif cells[3] != "no":
				raise SystemExit(f"{LIST.as_posix()}: Checked must be yes or no, not {cells[3]!r}")
			continue
		in_table = False
	return names


def errors_in(text, relative, names):
	errors = []
	for name in names:
		# <!-- custom: Whole words only, so a retired name does not match a longer word, such as the plural "pilots" of a harbour. (Claude code Opus 5.5) -->
		# <!-- custom: The guard applies only where the name ends in a letter: a listed path starting with a slash first matched nothing, as the folder letter before the slash, such as the M of `Images/LLM`, failed it. (Claude code Opus 5.5) -->
		before = r"(?<![A-Za-z])" if name[0].isalpha() else ""
		after = r"(?![A-Za-z])" if name[-1].isalpha() else ""
		for match in re.finditer(before + re.escape(name) + after, text, re.I):
			line = text.count("\n", 0, match.start()) + 1
			errors.append(f"{relative}:{line}: \"{match.group(0)}\" is a retired name; use the current one listed in {LIST.as_posix()}")
	return errors


def main():
	parser = argparse.ArgumentParser(description="Fail on retired tool and feature names outside the history records.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	names = retired_names(args.repo_root)
	# <!-- custom: Untracked files too, minus ignored ones: the first local run missed this check's own new files, which were not yet added. (Claude code Opus 5.5) -->
	tracked = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=args.repo_root, capture_output=True, text=True, check=True).stdout.splitlines()
	errors = []
	checked = 0
	for relative in tracked:
		path = args.repo_root / relative
		if relative in EXEMPT or HISTORY.search(relative) or path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
			continue
		checked += 1
		errors += errors_in(path.read_text(encoding="utf-8", errors="replace"), relative, names)
	for error in errors:
		print("FAIL " + error)
	if errors:
		return 1
	print("PASS retired names (%d names checked, %d files)" % (len(names), checked))
	return 0


if __name__ == "__main__":
	sys.exit(main())

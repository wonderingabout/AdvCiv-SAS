#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Numbered references are one token, PR#50 as KI#1104 and SGR210 are, so one grep finds every mention; the spellings live in lib/reference_spellings.py.
# Pull requests were written both ways, 29 spaced against 5 joined in the docs, so a grep for one missed the other (the user, 2026-11-23); every tracked text file was converted then, history copies such as the dev logs and the archived release notes included, as one grep is the point.
# squash_pr_number.py holds commit messages to the same table.
# --fix rewrites the spaced forms in place. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse reads the options, pathlib and subprocess list and read the tracked files, sys reports the result and finds the shared table. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
# <!-- custom: The spellings shared with the commit-message check. (Claude code Opus 5.5) -->
from reference_spellings import SPELLINGS, joined, spaced

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Imported reference material from other mods and the map scripts' originals is not ours to respell. (Claude code Opus 5.5) -->
EXCLUDED = ("LLM_Helpers/context/",)


def tracked_text_files(repo):
	names = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True, check=True).stdout.decode("utf-8").split("\0")
	for name in names:
		path = repo / name
		if not name or name.startswith(EXCLUDED) or not path.is_file():
			continue
		data = path.read_bytes()
		if b"\0" in data[:8192]:
			continue
		try:
			yield name, data.decode("utf-8"), "utf-8"
		except UnicodeDecodeError:
			yield name, data.decode("latin-1"), "latin-1"


def file_errors(name, text):
	errors = []
	for number, line in enumerate(text.split("\n"), 1):
		for label in spaced(line):
			errors.append("%s:%d: write %s references as one token, such as %s; line was: %s" % (name, number, label, joined(label + (" #50" if label != "SGR" else " 210")), line.strip()[:160]))
	return errors


def main():
	parser = argparse.ArgumentParser(description="Fail on a numbered reference written with a space, such as a pull request or a KI, in tracked text files; it is written as one token, such as PR#50.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	parser.add_argument("--fix", action="store_true", help="rewrite the spaced forms as one token in place")
	args = parser.parse_args()
	errors, fixed = [], 0
	for name, text, encoding in tracked_text_files(args.repo_root):
		if not spaced(text):
			continue
		if args.fix:
			(args.repo_root / name).write_bytes(joined(text).encode(encoding))
			fixed += 1
			continue
		errors += file_errors(name, text)
	if args.fix:
		print("FIXED %d file(s)" % fixed)
		return 0
	for error in errors:
		print("ERROR: " + error)
	if errors:
		print("FAIL numbered references (%d)" % len(errors))
		return 1
	print("PASS numbered references (%s)" % ", ".join(label for label, _, _ in SPELLINGS))
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# External helper: apply exact text replacements to one file from a patch file, keeping the file's line endings and encoding.

# <!-- custom: On 2026-11-13 two agents patching SASPilot's C++, Python and Markdown wrote this same script about ten times in their scratchpads: each replacement must match exactly once, and the file's CRLF or LF must survive.
# Passing the texts through a shell failed repeatedly instead: heredocs mangled backslashes and regex escapes, an apostrophe ended a quoted block, and sed left mixed line endings in pilot.py.
# A patch file written with the agent's file-writing tool has no shell quoting at all, so the texts arrive as written. (Claude code Fable 5.2) -->

# <!-- custom: argparse exposes the CLI, pathlib reads and writes the files, sys sets the exit status. (Claude code Fable 5.2) -->
import argparse
from pathlib import Path
import sys

OLD_MARK = "<<<<<<< OLD"
SPLIT_MARK = "======="
NEW_MARK = ">>>>>>> NEW"


def parse_patch(text: str) -> list[tuple[str, str]]:
	# <!-- custom: Blocks in the layout of a merge conflict, which agents and editors already know; text outside blocks is ignored, so a patch file can carry notes. (Claude code Fable 5.2) -->
	pairs = []
	old_lines = None
	new_lines = None
	for number, line in enumerate(text.split("\n"), 1):
		if line == OLD_MARK:
			if old_lines is not None:
				raise SystemExit("patch line %d: %s inside an open block" % (number, OLD_MARK))
			old_lines = []
		elif line == SPLIT_MARK and old_lines is not None and new_lines is None:
			new_lines = []
		elif line == NEW_MARK:
			if new_lines is None:
				raise SystemExit("patch line %d: %s without %s and %s before it" % (number, NEW_MARK, OLD_MARK, SPLIT_MARK))
			pairs.append(("\n".join(old_lines), "\n".join(new_lines)))
			old_lines = None
			new_lines = None
		elif new_lines is not None:
			new_lines.append(line)
		elif old_lines is not None:
			old_lines.append(line)
	if old_lines is not None:
		raise SystemExit("patch ends inside a block; each needs %s, %s and %s on lines of their own" % (OLD_MARK, SPLIT_MARK, NEW_MARK))
	if not pairs:
		raise SystemExit("no replacement blocks found in the patch file")
	return pairs


def main() -> None:
	parser = argparse.ArgumentParser(description="Apply exact text replacements to one file. The patch file holds blocks of '<<<<<<< OLD', the text to find, '=======', the text to put, '>>>>>>> NEW', each marker on its own line. Every old text must occur exactly once (or --count times); otherwise nothing is written.")
	parser.add_argument("target", help="the file to change")
	parser.add_argument("patch", help="the patch file with the replacement blocks")
	parser.add_argument("--encoding", default="utf-8", help="the target's encoding (default utf-8; cp1252 for legacy sources)")
	parser.add_argument("--count", type=int, default=1, help="how many times each old text must occur (default 1); all are replaced")
	parser.add_argument("--dry-run", action="store_true", help="check the matches without writing")
	args = parser.parse_args()
	target = Path(args.target)
	raw = target.read_bytes().decode(args.encoding)
	# <!-- custom: Match on LF text and restore the file's dominant ending afterwards, so a patch written with LF fits a CRLF file and no mixed endings are left. (Claude code Fable 5.2) -->
	crlf = raw.count("\r\n") > raw.count("\n") - raw.count("\r\n")
	text = raw.replace("\r\n", "\n")
	pairs = parse_patch(Path(args.patch).read_text(encoding="utf-8").replace("\r\n", "\n"))
	# <!-- custom: Check every block before changing anything, and report all that fail, so one run shows everything to fix. (Claude code Fable 5.2) -->
	failures = []
	for index, (old, new) in enumerate(pairs, 1):
		found = text.count(old)
		if found != args.count:
			failures.append("block %d: found %d times, expected %d: %r" % (index, found, args.count, old[:80]))
	if failures:
		print("\n".join(failures))
		sys.exit(1)
	for old, new in pairs:
		text = text.replace(old, new)
	if crlf:
		text = text.replace("\n", "\r\n")
	if not args.dry_run:
		target.write_bytes(text.encode(args.encoding))
	print("%s %d replacement block(s) in %s (%s)" % ("checked" if args.dry_run else "applied", len(pairs), target, "CRLF" if crlf else "LF"))


if __name__ == "__main__":
	main()

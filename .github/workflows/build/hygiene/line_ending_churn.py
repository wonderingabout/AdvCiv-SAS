#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: line_endings.py catches a file with mixed endings, but not one switched whole from CRLF to LF or back, which turns every line into a change.
# On 2026-11-16 a commit switched .github/workflows/README.md from LF to CRLF (1,640 lines changed for 20 real ones), and on 2026-11-17 an agent's sed edit switched it back (1,751 for 22); the user noticed the second only from its line count.
# This fails when a commit changes at least MIN_EOL_LINES lines of a file whose content, line endings aside, did not change there; a deliberate conversion passes with "Convert line endings" in the message. See KI#1097. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options, json reads the GitHub event, os reads its environment, pathlib finds the repository, sys reports the result. (Claude code Opus 5.5) -->
import argparse
import json
import os
from pathlib import Path
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push, PR and local runs check the same commits as the other commit rules. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "repository"))
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

MARKER = "Convert line endings"
# <!-- custom: Small enough to catch any whole-file switch, large enough that an edit touching a few lines' endings, such as a pasted block, passes. (Claude code Opus 5.5) -->
MIN_EOL_LINES = 20


def numstat(repo, commit, *options):
	counts = {}
	for row in git(repo, "show", "--numstat", "--format=", *options, commit).decode("utf-8", errors="replace").splitlines():
		added, deleted, path = row.split("\t", 2)
		if added != "-":
			counts[path] = int(added) + int(deleted)
	return counts


def commit_errors(repo, commit):
	if MARKER in git(repo, "log", "-1", "--format=%B", commit).decode("utf-8", errors="replace"):
		return []
	errors = []
	ignoring = numstat(repo, commit, "--ignore-cr-at-eol")
	for path, changed in numstat(repo, commit).items():
		eol_only = changed - ignoring.get(path, 0)
		if eol_only >= MIN_EOL_LINES:
			errors.append(f"commit {commit[:12]} changes {changed} lines of {path}, {eol_only} of them only in their line endings; restore the file's earlier endings (LLM_Helpers/formatting/fix_line_endings.py keeps each file's dominant style), or say \"{MARKER}\" in the message for a deliberate conversion")
	return errors


def main():
	parser = argparse.ArgumentParser(description="Fail when a commit switches a file's line endings, turning unchanged lines into changes.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	parser.add_argument("--base-ref", help="explicit range base; omitted for a local single-commit check")
	parser.add_argument("--head-ref", default="HEAD")
	parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
	parser.add_argument("--event-path", type=Path, default=os.environ.get("GITHUB_EVENT_PATH"), help="GitHub event JSON for complete push/PR commit selection")
	args = parser.parse_args()
	try:
		if args.base_ref:
			commits = commits_in_range(args.repo_root, args.base_ref, args.head_ref)
		elif args.event_path:
			event = json.loads(args.event_path.read_text(encoding="utf-8"))
			commits = event_commits(args.repo_root, args.event_name, event, args.head_ref)
		elif args.event_name in {"push", "pull_request"}:
			raise RuntimeError("push/PR checks require --event-path or --base-ref; refusing to check only the last commit")
		else:
			commits = [commit_id(args.repo_root, args.head_ref)]
		errors = [error for commit in commits for error in commit_errors(args.repo_root, commit)]
	except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
		print(f"FAIL line ending churn setup: {exc}")
		return 1
	for error in errors:
		print(f"FAIL {error}")
	if errors:
		return 1
	print(f"PASS line ending churn ({len(commits)} commit(s) checked)")
	return 0


if __name__ == "__main__":
	sys.exit(main())

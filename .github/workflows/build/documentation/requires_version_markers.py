#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: The Main Changes Guide marks each change "(Requires AdvCiv-SAS N+)", N being the practical number, git rev-list --count, of the commit that lands it on main, so players know which version has it.
# The number was written by hand and nothing checked it (2026-11-22): a number above the landing commit claims a version that lacks the change, and one below it tells players of earlier versions they have it.
# So a newly added marker must equal the practical number its change lands at: each commit's own count when commits land one by one, through a push, a rebase or a merge, whose count already includes what it merged; main's count + 1 for a PR marked [ci_squash_pr], whose commits become that one squash commit. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse and json read the CLI and GitHub event, collections counts each number's markers, pathlib and sys locate the shared revision code, re finds the markers, subprocess runs Git. (Claude code Opus 5.5) -->
import argparse
import collections
import json
from pathlib import Path
import re
import subprocess
import sys

# <!-- custom: Reuse the revision checks' commit selection and squash reading, so this check judges the same commits, or the same squash commit, as they do. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "diagnostics"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import sas_revision_history as sgr
from revision_history import pull_request_squashes, squash_tree

ROOT = Path(__file__).resolve().parents[4]
MARKER = re.compile(r"Requires AdvCiv-SAS (\d+)\+")
# <!-- custom: Archived release texts and generated context quote old markers as they were, so copying them in is not a new claim. (Claude code Opus 5.5) -->
SKIPPED = ("_1_AdvCiv-SAS/Docs/changelogs_web/", "LLM_Helpers/context/", "LLM_Helpers/outputs/")


def git(repo, *args):
	return subprocess.run(["git", *args], cwd=repo, capture_output=True).stdout.decode("utf-8", errors="replace")


def count(repo, commit):
	return int(git(repo, "rev-list", "--count", commit).strip())


# <!-- custom: Each changed Markdown file with its path before the change: Codex's review (2026-11-22) found a renamed file's unchanged markers read as new, as the old path was looked up at the new name.
# NUL-separated fields, as Git quotes a path such as café.md otherwise and the quoted name matched no file, so its markers went unchecked (Codex's second review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def markdown_changes(repo, base, commit):
	revisions = [base] if commit is None else [base, commit]
	fields = git(repo, "diff", "--name-status", "-M", "-z", *revisions, "--", "*.md").split("\0")
	changes = []
	index = 0
	while index < len(fields) and fields[index]:
		status = fields[index]
		if status.startswith(("R", "C")):
			old, new = fields[index + 1], fields[index + 2]
			index += 3
		else:
			old = new = fields[index + 1]
			index += 2
		if not new.startswith(SKIPPED):
			changes.append((old, new))
	return changes


def numbers(repo, commit, path):
	if commit is None:
		file = repo / path
		text = file.read_text(encoding="utf-8", errors="replace") if file.is_file() else ""
	else:
		text = git(repo, "show", "%s:%s" % (commit, path))
	return collections.Counter(MARKER.findall(text))


def transition_errors(repo, base, commit, expected):
	errors = []
	for old, path in markdown_changes(repo, base, commit):
		# <!-- custom: Only a number that now appears more often counts as added, so rewording, moving or deleting an existing entry does not. (Claude code Opus 5.5) -->
		added = numbers(repo, commit, path) - numbers(repo, base, old)
		for value in sorted(added):
			if int(value) != expected:
				where = commit[:12] if commit else "working tree"
				errors.append("%s, %s: adds (Requires AdvCiv-SAS %s+), but this change lands at practical %d" % (path, where, value, expected))
	return errors


# <!-- custom: Codex's review (2026-11-22) found two landing numbers that disagreed with where a change really lands:
# a squash lands on the target branch's current tip, which may have moved past the PR's merge base, so it is that tip's count + 1;
# and a PR merged with a merge commit lands at the merge commit's count, which the PR's own commits cannot know, so an unmarked PR is left to the push on main, which judges each first-parent commit, merge commits included. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def check(repo, default_branch_ref=None, event_name="local", event_data=None, squash=False):
	_, default = sgr.resolve_default_branch(repo, default_branch_ref)
	target = default
	if event_name == "pull_request":
		pull = (event_data or {}).get("pull_request", {})
		squash = pull_request_squashes(repo, pull)
		if not squash:
			return []
		target = pull.get("base", {}).get("sha") or default
		tree = squash_tree(repo, target, pull.get("head", {}).get("sha"))
		if tree:
			return transition_errors(repo, target, tree, count(repo, target) + 1)
	errors = []
	for base, commit in sgr.revision_transitions(repo, default, event_name, event_data, squash):
		expected = count(repo, target) + 1 if squash else count(repo, commit)
		errors += transition_errors(repo, base, commit, expected)
	return errors


def main():
	parser = argparse.ArgumentParser(description="Check that a newly added (Requires AdvCiv-SAS N+) names the practical number its change lands at.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	parser.add_argument("--default-branch-ref")
	parser.add_argument("--event-name", choices=("local", "push", "pull_request", "workflow_dispatch"), default="local")
	parser.add_argument("--event-path", type=Path)
	parser.add_argument("--squash", action="store_true", help="judge the branch as the one commit a squash merge makes, as a PR marked [ci_squash_pr] is")
	args = parser.parse_args()
	event_data = json.loads(args.event_path.read_text(encoding="utf-8")) if args.event_path else None
	try:
		errors = check(args.repo_root, args.default_branch_ref, args.event_name, event_data, args.squash)
	except (ValueError, OSError, subprocess.CalledProcessError) as exc:
		print("FAIL Requires version markers setup: %s" % exc)
		return 1
	for error in errors:
		print("FAIL " + error)
	if errors:
		return 1
	print("PASS Requires version markers")
	return 0


if __name__ == "__main__":
	sys.exit(main())

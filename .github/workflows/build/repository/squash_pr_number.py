#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: A squash commit names its PR in its title as PR#N, so git log and the dev logs lead back to the PR's page, its review and its draft commits.
# GitHub's default squash title ends with a bare " (#N)", which does not say what the number counts and could be an issue's; the user names a PR like a KI, one token with no space, as KI#1104 is written thousands of times and never "KI #", so one grep for PR#50 finds every mention.
# So a squash title must name PR#N, and a commit message writing a numbered reference with a space, such as a PR or a KI, fails, on any branch; numbered_references.py holds the repository's files to the same spellings.
# PR#50's squash commit was first pushed naming no PR and without its [ci_squash_pr] marker, and rewritten on 2026-11-23 to carry both and this check: the message drafted for it, pasted into GitHub's squash box and reworked in the amend that followed, replaced GitHub's own title and its body, which lists the PR's commit messages with their marker; nothing asked a draft for either (the user, 2026-11-23).
# On a push to the default branch, and locally on it, a commit carrying [ci_squash_pr] fails unless its title names its PR; squash_message.py --message asks a drafted squash message for both before the merge.
# This guards marked commits only: a squash whose message dropped both, as PR#50's did, leaves nothing to tell it from an ordinary commit, so the draft check is the guard for that case (Codex's review, 2026-11-23).
# GitHub's squash body is a repository setting; set as this repository has it, listing the PR's commit messages, it carries the marker.
# A PR's own commits carry the marker without a number, so PR runs and other branches are not checked. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

from __future__ import annotations

# <!-- custom: argparse, json, os and pathlib read the CLI and the GitHub event, re the title, sys the exit code. (Claude code Opus 5.5) -->
import argparse
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push and local runs check the same commits as the other message rules, and the shared marker spelling. (Claude code Opus 5.5) -->
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from ci_markers import SQUASH_PR
# <!-- custom: The numbered-reference spellings shared with the file check. (Claude code Opus 5.5) -->
from reference_spellings import spaced

# <!-- custom: A positive number only, and the title as Git's subject, %s, which joins a wrapped first paragraph: Codex's review (2026-11-23) found (#0) accepted, and a title ending "Title continued (#50)" on its second line rejected.
# squash_message.py imports pr_reference, so the draft check and this one read a PR reference alike. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def pr_reference(number=None):
	digits = str(number) if number else "[1-9][0-9]*"
	return re.compile(r"(?<![A-Za-z0-9])PR#" + digits + r"(?![0-9])")


def commit_errors(repo, commit, squash_rule=True):
	message = git(repo, "log", "-1", "--format=%B", commit).decode("utf-8", errors="replace")
	errors = []
	# <!-- custom: Numbered references, such as a PR or a KI, are one token in messages as in files, by the table numbered_references.py checks the files with (the user, 2026-11-23). (Claude code Opus 5.5) -->
	for label in spaced(message):
		errors.append("commit %s writes a %s reference with a space; write it as one token, such as PR#50 or KI#1104; line was: %s" % (commit[:12], label, next(line for line in message.splitlines() if label in spaced(line)).strip()[:160]))
	if squash_rule and SQUASH_PR in message:
		title = git(repo, "log", "-1", "--format=%s", commit).decode("utf-8", errors="replace").strip()
		if not pr_reference().search(title):
			errors.append("commit %s carries %s, so it is a squash merge, but its title does not name its PR as PR#50; GitHub's bare (#50) does not count; title was: %s" % (commit[:12], SQUASH_PR, title))
	return errors


def on_default_branch(repo, event_name, event):
	if event_name == "push":
		default = (event.get("repository") or {}).get("default_branch") or "main"
		return event.get("ref") == "refs/heads/" + default
	if event_name == "local":
		return git(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip() == "main"
	return False


def main():
	parser = argparse.ArgumentParser(description="Require commit messages to spell a PR as PR#N, and a squash commit on the default branch, marked " + SQUASH_PR + ", to name its PR in its title.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	parser.add_argument("--base-ref", help="explicit range base; omitted for a local single-commit check")
	parser.add_argument("--head-ref", default="HEAD")
	parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
	parser.add_argument("--event-path", type=Path, default=os.environ.get("GITHUB_EVENT_PATH"), help="GitHub event JSON for complete push commit selection")
	args = parser.parse_args()
	try:
		event = json.loads(args.event_path.read_text(encoding="utf-8")) if args.event_path else {}
		squash_rule = on_default_branch(args.repo_root, args.event_name, event)
		if args.base_ref:
			commits = commits_in_range(args.repo_root, args.base_ref, args.head_ref)
		elif args.event_path:
			commits = event_commits(args.repo_root, args.event_name, event, args.head_ref)
		elif args.event_name in {"push", "pull_request"}:
			raise RuntimeError("push/PR checks require --event-path or --base-ref; refusing to check only the last commit")
		else:
			commits = [commit_id(args.repo_root, args.head_ref)]
		errors = [error for commit in commits for error in commit_errors(args.repo_root, commit, squash_rule)]
	except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
		print(f"FAIL squash PR numbers setup: {exc}")
		return 1
	for error in errors:
		print(f"FAIL {error}")
	if errors:
		return 1
	print(f"PASS squash PR numbers ({len(commits)} commit(s) checked)")
	return 0


if __name__ == "__main__":
	sys.exit(main())

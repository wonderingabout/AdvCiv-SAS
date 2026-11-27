#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: A squash merge's commit message is written only when the PR is merged, so the rules that read a commit's message, a bumped revision named in the title, a new KI named in the title and [ci_update_dll] for a shipped DLL, can check it only on the push to main, after the merge, too late to fix on the PR.
# On 2026-11-22 the squash title drafted for PR#50 ended "(KI#1104, KI#21.7)" without SGR210, which its squash commit bumps, so that push would have failed; reading CI's checklist on GitHub was not a habit either.
# So this works out what the squash message must contain from the whole PR, and checks a drafted message given with --message, locally before merging; on a PR marked [ci_squash_pr] it also shows the checklist as a GitHub warning. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse and json read the CLI and GitHub event, os its defaults, pathlib the paths, re the title labels, subprocess Git, sys the exit code and helper paths. (Claude code Opus 5.5) -->
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

# <!-- custom: Reuse the checks whose rules the squash commit must meet, so this list cannot drift from them: the revision readers, the KI anchor rule and the marker spellings. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "diagnostics"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import sas_revision_history as sgr
import runtime_revision_history as runtime
from ki_commit_titles import KNOWN_ISSUES, TITLE_LIMIT, anchors, names
# <!-- custom: SQUASH_PR added: a drafted squash message must keep the marker, so the commit is still known as a squash on main. (Claude code Opus 5.5) -->
from ci_markers import SQUASH_PR, UPDATE_DLL
# <!-- custom: The DLL gate's own changed-path rule, so the checklist asks for the marker exactly when that gate will: Codex found a DLL renamed to .bin dropped from this list while the gate still required it (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dll_commit_message import changed_paths
from revision_history import pull_request_squashes, squash_tree
# <!-- custom: The PR reference rule shared with the check that judges the squash commit on main, so the draft and the commit are read alike. (Claude code Opus 5.5) -->
from squash_pr_number import pr_reference
from reference_spellings import spaced

ROOT = Path(__file__).resolve().parents[4]


def git(repo, *args):
	return subprocess.check_output(["git", *args], cwd=repo).decode("utf-8", errors="replace")


def runtime_revision(repo, commit):
	return runtime.revision(runtime.read(repo, commit, runtime.SOURCE), runtime.read(repo, commit, runtime.DEFINES))


def requirements(repo, base, tip):
	# <!-- custom: What the one squash commit, base to tip, will change: each revision label it bumps, each KI it opens and whether it ships a DLL. (Claude code Opus 5.5) -->
	labels = []
	for prefix, read in (("SGR", sgr.commit_revision), ("Runtime", runtime_revision)):
		before, after = read(repo, base), read(repo, tip)
		if after is not None and after != before:
			labels.append("%s%d" % (prefix, after))
	diff = git(repo, "diff", "-U0", base, tip, "--", KNOWN_ISSUES)
	kis = sorted(anchors(diff, "+") - anchors(diff, "-"), key=lambda ki: [int(part) for part in ki.split(".")])
	dll = any(path.lower().endswith((".dll", ".dll.build.json")) for path in changed_paths(repo, tip, base))
	return labels, kis, dll


def pr_label(number):
	return "PR#%s" % number if number else "PR#N, its PR number"


# <!-- custom: number added: the PR's number, from the event or --pr, which the title must name as PR#N, one token as KI#1104 is, rather than GitHub's bare (#N); the message must also keep [ci_squash_pr], so squash_pr_number.py can tell the commit is a squash after the merge.
# PR#50's squash commit, first pushed without both and rewritten on 2026-11-23 to carry them and these rules, lost them because the message drafted here and pasted into GitHub's squash box replaced GitHub's own title and body, and this checklist did not yet ask for them (the user, 2026-11-23). (Claude code Opus 5.5) -->
def checklist(labels, kis, dll, number=None):
	items = ["the title names %s" % pr_label(number), "the message keeps %s" % SQUASH_PR]
	items += ["the title names %s" % label for label in labels]
	if kis:
		where = "title" if len(kis) <= TITLE_LIMIT else "message"
		items += ["the %s names KI#%s" % (where, ki) for ki in kis]
	if dll:
		items.append("the message carries %s" % UPDATE_DLL)
	return items


# <!-- custom: number added, the PR's number, which the title must name as PR#N; without it, any PR#N passes. (Claude code Opus 5.5) -->
def message_errors(message, labels, kis, dll, number=None):
	title = message.strip().splitlines()[0] if message.strip() else ""
	# <!-- custom: The title is read as Git will commit it, its first paragraph joined, and only a positive number passes (Codex's review, 2026-11-23). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	subject = " ".join(line.strip() for line in message.strip().split("\n\n")[0].splitlines())
	errors = [] if pr_reference(number).search(subject) else ["title must name %s, one token as KI#1104 is; GitHub's bare (#N) does not count; title was: %s" % (pr_label(number), title)]
	errors += ["message writes a %s reference with a space; write it as one token, such as PR#50 or KI#1104" % label for label in spaced(message)]
	if SQUASH_PR not in message:
		errors.append("message must keep %s, so the squash commit is still known as one on main" % SQUASH_PR)
	errors += ["title must name %s; title was: %s" % (label, title) for label in labels if not re.search(r"(?<![A-Za-z0-9])" + re.escape(label) + r"(?![0-9])", title)]
	text = title if len(kis) <= TITLE_LIMIT else message
	errors += ["%s must name KI#%s" % ("title" if len(kis) <= TITLE_LIMIT else "message", ki) for ki in kis if not names(text, ki)]
	if dll and UPDATE_DLL not in message:
		errors.append("message must carry %s, as the PR ships a DLL" % UPDATE_DLL)
	# <!-- custom: The DLL gate also refuses the marker when no DLL or build report changed, so a draft carrying it needlessly fails here too (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not dll and UPDATE_DLL in message:
		errors.append("message carries %s, but the PR changes no DLL or build report" % UPDATE_DLL)
	return errors


def main():
	parser = argparse.ArgumentParser(description="List, and with --message check, what a squash merge's commit message must contain.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	parser.add_argument("--default-branch-ref", help="the branch the PR merges into; default origin's main")
	parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
	parser.add_argument("--event-path", type=Path, default=os.environ.get("GITHUB_EVENT_PATH"))
	parser.add_argument("--message", type=Path, help="a drafted squash message to check, such as the one pasted into GitHub's squash box")
	parser.add_argument("--pr", type=int, help="with --message locally, the PR's number its title must name as PR#N, such as 50; without it any PR#N passes")
	args = parser.parse_args()
	repo = args.repo_root
	number = args.pr
	try:
		if args.event_name == "pull_request":
			pull = json.loads(args.event_path.read_text(encoding="utf-8"))["pull_request"]
			if not pull_request_squashes(repo, pull):
				print("PASS squash message (PR not marked for a squash merge)")
				return 0
			number = pull.get("number")
			target = pull["base"]["sha"]
			tip = pull["head"]["sha"]
		elif args.event_name == "local":
			_, default = sgr.resolve_default_branch(repo, args.default_branch_ref)
			if default is None:
				raise RuntimeError("no default branch to compare with; pass --default-branch-ref")
			target = default
			tip = git(repo, "rev-parse", "HEAD").strip()
		else:
			print("PASS squash message (only PR and local runs have a squash to plan)")
			return 0
		# <!-- custom: Compare the target with the tree the squash would commit, so changes already on the target are not asked of the squash message; a conflicting PR falls back to its merge base (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		tree = squash_tree(repo, target, tip)
		labels, kis, dll = requirements(repo, target, tree) if tree else requirements(repo, git(repo, "merge-base", target, tip).strip(), tip)
	except (RuntimeError, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
		print("FAIL squash message setup: %s" % exc)
		return 1
	items = checklist(labels, kis, dll, number)
	if args.message:
		errors = message_errors(args.message.read_text(encoding="utf-8"), labels, kis, dll, number)
		for error in errors:
			print("FAIL squash message: " + error)
		if errors:
			return 1
		print("PASS squash message (%d requirement(s) met)" % len(items))
		return 0
	if not items:
		print("PASS squash message (no requirement)")
		return 0
	# <!-- custom: A ::warning:: line becomes an annotation on GitHub's PR page, where it shows without opening the log; locally it prints as is. (Claude code Opus 5.5) -->
	prefix = "::warning title=Squash message::" if args.event_name == "pull_request" else ""
	print(prefix + "The squash commit message must: " + "; ".join(items) + ". Check a draft with: python .github/workflows/build/repository/squash_message.py --message FILE")
	print("PASS squash message (checklist only; pass --message to check a draft)")
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: The dev logs are hand-edited copies of git log: on 2026-11-17, 650 of the SAS log's 2,420 entries, 8 of base AdvCiv's and 3 of K-Mod's differed from Git's own messages, with typo, churn and wording fixes.
# A naive regeneration with git log would silently erase them, so a changed log must keep its earlier content as its exact tail, new entries going on top, unless the commit message carries [ci_edit_dev_log] ("Edit dev log" before 2026-11-22).
# The files are named anonymized_email: every Author line must be <hidden>.
# Addresses in message bodies, such as agents' and bots' Co-authored-by and Signed-off-by trailers, stay as their commits wrote them. (Claude code Opus 5.5) -->
#
# <!-- custom: Every logged commit must also still be in the checked branch's history: a history rewrite gives new SHAs, and the log would keep citing commits that no longer exist there.
# On 2026-11-17 main was rewritten twice the same day, once to give SASSaveTransplanter its name in older commits and once to reword KI#1091's message; the SAS log then ended just before the rewritten commits, but a rewrite reaching further back would have left it stale unseen. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse parses the options, json reads the GitHub event, os reads its environment, pathlib finds the logs, re matches their paths, sys reports the result. (Claude code Opus 5.5) -->
import argparse
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push, PR and local runs check the same commits as the other commit rules. (Claude code Opus 5.5) -->
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

# <!-- custom: The key after anonymized_email_, such as 003_AdvCiv-SAS.txt, names a log across folders and the git_logs to dev_logs rename. (Claude code Opus 5.5) -->
DEV_LOG = re.compile(r"(^|/)Docs/(?:dev|git)_logs/(?:dev|git)_log_anonymized_email_([^/]+\.txt)$")
# <!-- custom: The shared marker spelling, kept once in lib/ci_markers.py with the other commit-message markers. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from ci_markers import EDIT_DEV_LOG
EDIT_MARKER = EDIT_DEV_LOG
LOGGED_COMMIT = re.compile(r"^commit ([0-9a-f]{40})\s*$", re.M)


def tree_errors(repo: Path) -> list[str]:
    errors = []
    paths = sorted(path.relative_to(repo).as_posix() for path in repo.glob("*/Docs/dev_logs/dev_log_anonymized_email_*.txt"))
    if not paths:
        return ["no dev log found under */Docs/dev_logs/"]
    for path in paths:
        for number, line in enumerate((repo / path).read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("Author:") and not line.endswith(" <hidden>"):
                errors.append(f"{path}:{number}: author is not anonymized: {line.strip()[:120]}")
    return errors


def history_errors(repo: Path, head: str) -> list[str]:
    # <!-- custom: One rev-list of the whole branch, as the logs hold thousands of commits; the CI checkout fetches full history (fetch-depth 0), so a missing commit means it left the history, not a shallow clone. (Claude code Opus 5.5) -->
    history = set(git(repo, "rev-list", head).decode("utf-8").split())
    errors = []
    for path in sorted(repo.glob("*/Docs/dev_logs/dev_log_anonymized_email_*.txt")):
        missing = [sha for sha in LOGGED_COMMIT.findall(path.read_text(encoding="utf-8")) if sha not in history]
        if missing:
            errors.append(f"{path.relative_to(repo).as_posix()}: {len(missing)} logged commit(s) not in {head}'s history, first {missing[0][:12]}; after a history rewrite, replace the old SHAs with the new ones from the rewrite's map, keeping the entries' hand edits, and say \"{EDIT_MARKER}\" in the message")
    return errors


def changed_dev_logs(repo: Path, commit: str) -> list[tuple[str, str, str]]:
    # <!-- custom: Rename detection follows a log to its earlier path, as when the git_logs folders became dev_logs.
    # A move that also prepends many entries can fall below Git's 50% similarity and show as a delete plus an add, as the test's small fixture did, so a deleted and an added log with the same key are paired too. (Claude code Opus 5.5) -->
    rows = git(repo, "diff-tree", "--root", "-r", "-M", "--name-status", "--no-commit-id", commit).decode("utf-8").splitlines()
    changes = []
    deleted: dict[str, str] = {}
    added: dict[str, str] = {}
    for row in rows:
        parts = row.split("\t")
        status = parts[0][0]
        old, new = (parts[1], parts[2]) if status in "RC" else (parts[1], parts[1])
        match = DEV_LOG.search(new) or DEV_LOG.search(old)
        if not match:
            continue
        if status == "D":
            deleted[match.group(1)] = old
        elif status == "A":
            added[match.group(1)] = new
        else:
            changes.append((status, old, new))
    for key, old in deleted.items():
        changes.append(("R", old, added.pop(key)) if key in added else ("D", old, old))
    return changes


def blob(repo: Path, rev: str, path: str) -> str:
    return git(repo, "show", f"{rev}:{path}").decode("utf-8").replace("\r\n", "\n")


def commit_errors(repo: Path, commit: str) -> list[str]:
    message = git(repo, "log", "-1", "--format=%B", commit).decode("utf-8", errors="replace")
    if EDIT_MARKER in message:
        return []
    errors = []
    for status, old, new in changed_dev_logs(repo, commit):
        if status == "D":
            errors.append(f"commit {commit[:12]} deletes {old}")
            continue
        before = blob(repo, f"{commit}^", old)
        after = blob(repo, commit, new)
        if not after.endswith(before):
            errors.append(f"commit {commit[:12]} changes earlier entries of {new}, not only adding new ones on top; a git log regeneration would erase the hand edits, so restore them, or say \"{EDIT_MARKER}\" in the message for a deliberate edit")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Keep the dev logs' authors anonymized, their hand-edited entries intact and their commits in the branch's history.")
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
        errors = tree_errors(args.repo_root) + history_errors(args.repo_root, args.head_ref) + [error for commit in commits for error in commit_errors(args.repo_root, commit)]
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL dev logs setup: {exc}")
        return 1
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        return 1
    print(f"PASS dev logs ({len(commits)} commit(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

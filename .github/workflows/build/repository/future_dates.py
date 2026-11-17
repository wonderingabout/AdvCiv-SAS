#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: A date a commit adds cannot be later than the day it was committed: on the evening of 2026-11-16, Claude Code took 2026-11-17 from its session's date, and two commits added it to AGENTS.md, a KI entry, three check comments and the workflow README before the user noticed.
# The committer date counts, in the committer's own time zone, so an amend after midnight may add the new day's date. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse parses the options, date compares the days, json reads the GitHub event, os reads its environment, pathlib finds the repository, re finds the dates, sys reports the result. (Claude code Opus 5.5) -->
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push, PR and local runs check the same commits as the other commit rules. (Claude code Opus 5.5) -->
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

DATE = re.compile(r"(?<![\d-])(20\d\d)-(\d\d)-(\d\d)(?![\d-])")
# <!-- custom: Generated history exports quote other commits' text, whose dates are their own. (Claude code Opus 5.5) -->
SKIPPED_HISTORY = ("LLM_Helpers/context/",)
# <!-- custom: Test fixtures make up dates on purpose, this check's own test included. (Claude code Opus 5.5) -->
SKIPPED_TESTS = (".github/workflows/tests/", "tests/")


def added_lines(repo, commit):
    # <!-- custom: --root gives the first commit's lines too; merges show no diff here, as their lines were checked in the commits they merge. (Claude code Opus 5.5) -->
    text = git(repo, "diff-tree", "--root", "-r", "-p", "-U0", "--no-color", "--no-ext-diff", "--no-commit-id", commit).decode("utf-8", errors="replace")
    path = None
    for line in text.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("+") and path and not path.startswith(SKIPPED_HISTORY + SKIPPED_TESTS):
            yield path, line[1:]


def commit_errors(repo, commit):
    committed = date.fromisoformat(git(repo, "log", "-1", "--format=%cd", "--date=short", commit).decode("ascii").strip())
    errors = []
    for path, line in added_lines(repo, commit):
        for match in DATE.finditer(line):
            try:
                written = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            except ValueError:
                continue
            if written > committed:
                errors.append("commit %s adds %s to %s, after its own commit date %s; take dates from the local clock or the commit date, not a session's date: %s" % (commit[:12], match.group(0), path, committed.isoformat(), line.strip()[:160]))
    return errors


def main():
    parser = argparse.ArgumentParser(description="Reject dates later than the commit that adds them.")
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
        print(f"FAIL future dates setup: {exc}")
        return 1
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        return 1
    print(f"PASS future dates ({len(commits)} commit(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

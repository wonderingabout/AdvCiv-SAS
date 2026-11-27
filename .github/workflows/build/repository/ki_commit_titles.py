#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Finding the commit that opened a Known Issue meant searching its text, unless the title named it as most did, such as (SGR194, KI#203.2).
# Of the last 400 commits that touched README_Known_Issues.md on 2026-11-10, 45 of 55 adding one KI named it in the title, but most adding two or three did not, and audit reconciliations added up to 33 at once.
# So a commit adding up to three KIs must name each in its title, and one adding more must name each somewhere in its message; KIs merely edited are not required. (Claude code Opus 5.5) -->

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push, PR and local runs check the same commits for both rules. (Claude code Opus 5.5) -->
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

KNOWN_ISSUES = "_1_AdvCiv-SAS/Docs/README_Known_Issues.md"
TITLE_LIMIT = 3


def anchors(diff, sign):
    return set(re.findall(r'^\%s<a id="ki-([0-9]+(?:\.[0-9]+)*)"></a>' % sign, diff, re.MULTILINE))


def added_kis(repo, commit):
    lineage = git(repo, "rev-list", "--parents", "-n", "1", commit).decode().split()
    revisions = [lineage[1], commit] if len(lineage) > 1 else [git(repo, "hash-object", "-t", "tree", "--stdin").decode().strip(), commit]
    diff = git(repo, "diff", "-U0", *revisions, "--", KNOWN_ISSUES).decode("utf-8", errors="replace")
    # <!-- custom: Moving or renumbering an entry removes and re-adds its anchor; only anchors new to the file count. (Claude code Opus 5.5) -->
    return sorted(anchors(diff, "+") - anchors(diff, "-"), key=lambda ki: [int(part) for part in ki.split(".")])


def names(text, ki):
    # <!-- custom: KI#1076 must not be satisfied by KI#1076.2 or KI#10760. (Claude code Opus 5.5) -->
    if re.search(r"KI#" + re.escape(ki) + r"(?![0-9]|\.[0-9])", text):
        return True
    # <!-- custom: An audit can add dozens of whole-number KIs; a range such as KI#1036-KI#1068 or KI#1036-1068 names them all. (Claude code Opus 5.5) -->
    if "." in ki:
        return False
    return any(int(low) <= int(ki) <= int(high) for low, high in re.findall(r"KI#([0-9]+)\s*[-–]\s*(?:KI#)?([0-9]+)(?![0-9]|\.[0-9])", text))


def commit_errors(repo, commit):
    new = added_kis(repo, commit)
    if not new:
        return []
    title = git(repo, "log", "-1", "--format=%s", commit).decode("utf-8", errors="replace").strip()
    message = git(repo, "log", "-1", "--format=%B", commit).decode("utf-8", errors="replace")
    where, text = ("title", title) if len(new) <= TITLE_LIMIT else ("message", message)
    missing = [ki for ki in new if not names(text, ki)]
    if not missing:
        return []
    return ["commit %s adds %s; its %s must name %s (up to %d new KIs belong in the title, more anywhere in the message); title was: %s" % (commit[:12], ", ".join("KI#" + ki for ki in new), where, ", ".join("KI#" + ki for ki in missing), TITLE_LIMIT, title)]


def main():
    parser = argparse.ArgumentParser(description="Require commits that add Known Issues to name them in their title or message.")
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
        print(f"FAIL Known Issue commit titles setup: {exc}")
        return 1
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        return 1
    print(f"PASS Known Issue commit titles ({len(commits)} commit(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Agents credit themselves in the code comments they write, so a Co-authored-by trailer on every commit only added noise; Claude Code added one by default despite the user's rule (2026-11-16).
# A credit written inline in the message body, where it says something, stays allowed; only a trailer line is rejected. (Claude code Opus 5.5) -->

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push, PR and local runs check the same commits as the other message rules. (Claude code Opus 5.5) -->
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

# <!-- custom: Only listed co-authors may appear in a trailer, such as Dependabot when GitHub squashes its PR: a list of agents to reject would miss the next agent that adds one by default, while the maintainers are few.
# Names are matched before the "<", so no email address is kept here; add a new maintainer or bot to this set. (Claude code Opus 5.5) -->
ALLOWED_CO_AUTHORS = {"dependabot[bot]"}
TRAILER = re.compile(r"^co-authored-by:\s*([^<\n]*)", re.IGNORECASE | re.MULTILINE)


def commit_errors(repo, commit):
    message = git(repo, "log", "-1", "--format=%B", commit).decode("utf-8", errors="replace")
    rejected = [name.strip() or "(no name)" for name in TRAILER.findall(message) if name.strip().lower() not in ALLOWED_CO_AUTHORS]
    if not rejected:
        return []
    title = message.splitlines()[0] if message else ""
    return ["commit %s has a Co-authored-by trailer for %s, who is not in ALLOWED_CO_AUTHORS; credit agents in their code comments, or inline in the message where it matters; title was: %s" % (commit[:12], ", ".join(rejected), title)]


def main():
    parser = argparse.ArgumentParser(description="Reject Co-authored-by trailer lines in commit messages.")
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
        print(f"FAIL commit trailers setup: {exc}")
        return 1
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        return 1
    print(f"PASS commit trailers ({len(commits)} commit(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: A line a commit adds must not repeat the line right above or below it: such doubles come from a merge resolution keeping both sides, a script run twice or a paste, and nothing else catches them, as the code still runs.
# Three were found in 2026-11-18's review, harmless but confusing: SevoPediaMusic.py set the same label twice, and the inherited CvDanQuayle.py and CvCustomizableDomesticAdvisor.py assigned or hid the same thing twice.
# Only added lines count: across the tracked code, 114 lines repeat their neighbour, most on purpose, such as two NEWLINE appends for a blank line or matrix rows in map scripts.
# A deliberate double can say so with a trailing comment, which makes the lines differ. See KI#1098. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse parses the options, json reads the GitHub event, os reads its environment, pathlib finds the repository, re reads hunk headers and spots decoration lines, sys reports the result. (Claude code Opus 5.5) -->
import argparse
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse the DLL message check's commit selection, so push, PR and local runs check the same commits as the other commit rules. (Claude code Opus 5.5) -->
from dll_commit_message import ROOT, commit_id, commits_in_range, event_commits, git

CODE_SUFFIXES = (".py", ".cpp", ".h", ".inl", ".ps1")
# <!-- custom: XML repeats rows on purpose, such as <iCommerce>0</iCommerce> lists, and history exports quote other commits.
# Tests repeat calls on purpose too: replayed over main's last 400 commits, the only other hits were two harnesses calling a function twice to prove the second call changes nothing or counts again. (Claude code Opus 5.5) -->
SKIPPED = ("LLM_Helpers/context/", ".github/workflows/tests/", "tests/")
# <!-- custom: Closing brackets, separators and comment rules repeat by design, so a line of only such characters is not counted. (Claude code Opus 5.5) -->
DECORATION = re.compile(r"^[\s{}()\[\];,#/*\-=_<>!~|]*$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def added_line_numbers(repo, commit):
    # <!-- custom: --root gives the first commit's lines too; merges show no diff here, as their lines were checked in the commits they merge.
    # --ignore-cr-at-eol keeps a line-ending conversion from counting every line as added: the 2026-11-17 conversion otherwise flagged CvDanQuayle.py's inherited double. (Claude code Opus 5.5) -->
    text = git(repo, "diff-tree", "--root", "-r", "-p", "-U0", "--ignore-cr-at-eol", "--no-color", "--no-ext-diff", "--no-commit-id", commit).decode("utf-8", errors="replace")
    added, path, number = {}, None, 0
    for line in text.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            match = HUNK.match(line)
            number = int(match.group(1)) if match else 0
        elif line.startswith("+") and path and path.endswith(CODE_SUFFIXES) and not path.startswith(SKIPPED):
            added.setdefault(path, set()).add(number)
            number += 1
        elif line.startswith(" "):
            number += 1
    return added


def duplicate_errors(path, lines, numbers):
    errors = []
    for number in sorted(numbers):
        index = number - 1
        if index >= len(lines) or DECORATION.match(lines[index]):
            continue
        # <!-- custom: An added line is checked against both neighbours, and each pair is reported at its second line, so a pair whose two lines were both added appears once. (Claude code Opus 5.5) -->
        for first, second in ((index - 1, index), (index, index + 1)):
            if 0 <= first and second < len(lines) and lines[first] == lines[second]:
                errors.append("%s:%d repeats the line above it; drop one, or say why on it if both are meant: %s" % (path, second + 1, lines[second].strip()[:160]))
    return sorted(set(errors))


def commit_errors(repo, commit):
    errors = []
    for path, numbers in added_line_numbers(repo, commit).items():
        raw = git(repo, "show", "%s:%s" % (commit, path)).decode("utf-8", errors="replace")
        lines = raw.replace("\r\n", "\n").split("\n")
        errors += ["commit %s: %s" % (commit[:12], error) for error in duplicate_errors(path, lines, numbers)]
    return errors


def main():
    parser = argparse.ArgumentParser(description="Reject an added code line that repeats the line next to it.")
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
        print(f"FAIL adjacent duplicate lines setup: {exc}")
        return 1
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        return 1
    print(f"PASS adjacent duplicate lines ({len(commits)} commit(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

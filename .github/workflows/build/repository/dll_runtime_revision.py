#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Require a matching Release build when native Runtime code changes, including the migration from compiled to XML revision labels.
# XML-only label/observer updates need no native rebuild.
# Historical compiled bumps remain covered by the same native-content rule; comments alone do not force builds. (GPT-6.1-Sol) -->

# <!-- custom: argparse/os/json select the same explicit integration event as the other DLL guards; hashlib/re validate the built source identity, pathlib locates files, and sys supplies CLI exit status. (GPT-6.1-Sol) -->
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

# <!-- custom: Reuse Git range selection, Release report/binary verification and tree identities from the existing repository DLL checks. (GPT-6.1-Sol) -->
from dll_commit_message import ROOT, build_report_errors, commit_id, commits_in_range, event_commits, git
from dll_define_changes import blob_id, DLL

SOURCE = "CvGameCoreDLL/SASRuntimeStatus.cpp"
CHECK = ".github/workflows/build/repository/dll_runtime_revision.py"


# <!-- custom: Compare native tokens rather than the XML implementation label; strip comments with a literal-aware pattern so strings containing comment markers retain their meaning. (GPT-6.1-Sol) -->
def native_content(repo, commit, path=SOURCE):
    if commit is None or blob_id(repo, commit, path) is None:
        return b""
    source = git(repo, "show", f"{commit}:{path}")
    tokens = re.findall(rb'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/|[A-Za-z_][A-Za-z_0-9]*|[0-9][A-Za-z_0-9.]*|>>=|<<=|->\*|\.\.\.|::|->|\+\+|--|&&|\|\||<<|>>|<=|>=|==|!=|[+*/%&|^!-]=|[^\s]', source, re.DOTALL)
    return tuple(token for token in tokens if not token.startswith((b"//", b"/*")))


# <!-- custom: Discover the dedicated native Runtime files in both trees so a new, renamed or removed header cannot bypass rebuild evidence merely because the revision moved to XML. (GPT-6.1-Sol) -->
def native_paths(repo, commit):
    if commit is None:
        return set()
    paths = git(repo, "ls-tree", "-r", "--name-only", commit, "--", "CvGameCoreDLL/").decode("utf-8").splitlines()
    return {path for path in paths if re.fullmatch(r"CvGameCoreDLL/SASRuntime[^/]*\.(?:cpp|h)", path)}


# <!-- custom: Ordinary integration validates each native-changing commit; an explicitly squash-bound PR compares its final head with the merge base, matching the recorder-history policy. (GPT-6.1-Sol) -->
def check(repo, commits, squash_base=None):
    commits = list(dict.fromkeys(commits))
    if squash_base is not None and len(commits) != 1:
        raise ValueError("squash review requires one candidate head")
    errors = []
    bumps = 0
    for commit in commits:
        if blob_id(repo, commit, CHECK) is None:
            continue
        parents = git(repo, "rev-list", "--parents", "-n", "1", commit).decode().split()
        parent = squash_base if squash_base is not None else (parents[1] if len(parents) > 1 else None)
        changed = [path for path in sorted(native_paths(repo, parent) | native_paths(repo, commit))
                   if native_content(repo, parent, path) != native_content(repo, commit, path)]
        if not changed:
            continue
        bumps += 1
        prefix = f"{commit[:12]}: native Runtime implementation changed"
        if blob_id(repo, commit, SOURCE) is None:
            errors.append(prefix + ": missing native Runtime source")
            continue
        if blob_id(repo, commit, DLL) in (None, blob_id(repo, parent, DLL)):
            errors.append(prefix + ": update the Release DLL/report in this commit")
            continue
        report_errors = build_report_errors(repo, commit, [DLL])
        errors.extend(report_errors)
        if report_errors:
            continue
        report = json.loads(git(repo, "show", f"{commit}:{DLL}.build.json").decode("utf-8-sig"))
        # <!-- custom: Git normalizes source line endings while Windows builds hash exact CRLF bytes.
        # Validate each changed surviving native file, not just the publisher, without inferring a build from a changed binary alone. (GPT-6.1-Sol) -->
        for path in changed:
            if blob_id(repo, commit, path) is None:
                continue
            entry = next((row for row in report.get("buildInputsBefore", []) if row.get("path") == path), None)
            source = git(repo, "show", f"{commit}:{path}").replace(b"\r\n", b"\n")
            expected = {hashlib.sha256(source).hexdigest(), hashlib.sha256(source.replace(b"\n", b"\r\n")).hexdigest()}
            if entry is None or str(entry.get("sha256", "")).lower() not in expected:
                errors.append(prefix + f": Release report does not match the Runtime source {path}")
            if any(row.get("path") == path and row.get("change") in ("CONTENT_CHANGED", "REMOVED", "ADDED") for row in report.get("buildInputChanges", [])):
                errors.append(prefix + f": Runtime source changed during the build: {path}; rebuild from stable source")
    return errors, bumps


def main():
    parser = argparse.ArgumentParser(description="Require matching shipped Release evidence for native Runtime implementation changes on default-branch integration.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--base-ref")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", "local"))
    parser.add_argument("--event-path", type=Path, default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--squash", action="store_true", help="review the base-to-head candidate as one explicitly squash-bound integration")
    args = parser.parse_args()
    try:
        head = args.head_ref
        squash_base = None
        if args.squash and not args.base_ref:
            raise ValueError("local --squash requires --base-ref")
        if args.base_ref:
            commits = commits_in_range(args.repo_root, args.base_ref, head)
            if args.squash:
                squash_base = git(args.repo_root, "merge-base", args.base_ref, head).decode().strip()
                commits = [commit_id(args.repo_root, head)]
        elif args.event_name == "workflow_dispatch":
            commits = [commit_id(args.repo_root, head)]
        elif args.event_path:
            event = json.loads(args.event_path.read_text(encoding="utf-8"))
            if args.event_name == "push" and event.get("deleted"):
                print("PASS native Runtime DLL (deleted branch)")
                return 0
            target = event["pull_request"]["base"]["ref"] if args.event_name == "pull_request" else event.get("ref", "").removeprefix("refs/heads/")
            if target != event["repository"]["default_branch"]:
                print("PASS native Runtime DLL (deferred until default-branch integration)")
                return 0
            head = event["pull_request"]["head"]["sha"] if args.event_name == "pull_request" else event["after"]
            commits = event_commits(args.repo_root, args.event_name, event, head)
            if args.event_name == "pull_request" and any(label.get("name") == "revision:squash" for label in event["pull_request"].get("labels", [])):
                squash_base = git(args.repo_root, "merge-base", event["pull_request"]["base"]["sha"], head).decode().strip()
                commits = [commit_id(args.repo_root, head)]
        elif args.event_name not in ("local", "workflow_dispatch"):
            raise RuntimeError("GitHub checks require an event payload or explicit base")
        else:
            commits = [commit_id(args.repo_root, head)]
        errors, bumps = check(args.repo_root, commits, squash_base)
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL native Runtime DLL setup: {exc}")
        return 1
    for error in errors:
        print("FAIL " + error)
    if not errors:
        print(f"PASS native Runtime DLL ({bumps} native changes checked)")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())

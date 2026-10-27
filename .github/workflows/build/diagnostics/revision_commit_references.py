#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Share the existing Git event/squash boundaries and visible Markdown parser; argparse/json expose the same workflow interface, re validates hashes, and subprocess checks actual ancestry. (GPT-6.1-Sol) -->
import argparse
import json
import re
import subprocess
from pathlib import Path
# <!-- custom: Reuse the recorder checks' Git boundaries/readers and source markers plus the shared visible-entry parser, keeping reference lifetime separate from revision increments. (GPT-6.1-Sol) -->
import sas_revision_history as sgr
import runtime_revision_history as runtime
from revision_history import revision_entries


def references(text):
    result = []
    for number, body in revision_entries(text):
        field = re.search(r"^- \*\*Git commit:\*\* (.+)$", body, re.MULTILINE)
        result.append((number, None if field is None else field.group(1).strip().strip("`")))
    return result


def read(repo, commit, path):
    data = sgr.git_show(repo, commit, str(path))
    return "" if data is None else data.decode("utf-8", "replace")


# <!-- custom: A commit cannot contain its own final SHA; permit pending at introduction, but reject carrying that same revision into another commit, even without a recorder change.
# Squash mode compares only its aggregate boundary. (GPT-6.1-Sol) -->
def pending_errors(before, after):
    previous = dict(references(before))
    return [f"revision {number}: finalize pending Git commit in the next commit"
            for number, value in references(after)
            if value == "pending" and previous.get(number) == "pending"]


def runtime_revision(repo, commit):
    return runtime.revision(read(repo, commit, runtime.SOURCE))


# <!-- custom: Validate both recorders' current references against canonical history or new feature lineage, including Runtime's previously unchecked hashes.
# A rewritten/squashed branch must reconcile its references; unchanged merges preserve valid commit identities. (GPT-6.1-Sol) -->
def reference_errors(repo, path, reader, default_commit, first_marker=1):
    entries = references(read(repo, None, path))
    default_revision = reader(repo, default_commit) if default_commit else None
    canonical = set() if default_commit is None else set(subprocess.check_output(
        ["git", "rev-list", default_commit], cwd=repo, text=True).splitlines())
    lineage = set(subprocess.check_output(["git", "rev-list", "HEAD"], cwd=repo, text=True).splitlines())
    errors = []
    for index, (number, value) in enumerate(entries):
        if value == "pending":
            if index:
                errors.append(f"revision {number}: only the latest entry may remain pending")
            continue
        if value is None or not re.fullmatch(r"[0-9a-f]{40}", value):
            errors.append(f"revision {number}: expected full Git commit hash or latest-entry pending")
            continue
        eligible = canonical | (lineage if default_revision is None or number > default_revision else set())
        if value not in eligible:
            errors.append(f"revision {number}: Git commit absent from eligible ancestry; reconcile after amend/rebase/squash")
        elif number >= first_marker and reader(repo, value) != number:
            errors.append(f"revision {number}: Git commit does not contain its matching recorder revision")
    return errors


def check(repo, default_branch_ref=None, event_name="local", event_data=None, squash=False):
    _, default_commit = sgr.resolve_default_branch(repo, default_branch_ref)
    if subprocess.check_output(["git", "rev-parse", "--is-shallow-repository"], cwd=repo).strip() != b"false":
        return ["revision references require full Git history (checkout fetch-depth: 0)"]
    transitions = sgr.revision_transitions(repo, default_commit, event_name, event_data, squash)
    errors = []
    # <!-- custom: SGR revisions before 69 predate its explicit source marker; their hashes still require valid ancestry.
    # Runtime has a compiled marker from revision 1. (GPT-6.1-Sol) -->
    for path, reader, first_marker in ((sgr.HISTORY, sgr.commit_revision, 69), (runtime.HISTORY, runtime_revision, 1)):
        errors.extend(f"{path}: {error}" for error in reference_errors(repo, path, reader, default_commit, first_marker))
        for parent, commit in transitions:
            # <!-- custom: Enforce the new lifetime rule from its introducing commit onward; immutable earlier commits may contain the old omission, while current references are still audited and repaired. (GPT-6.1-Sol) -->
            if parent and (commit is None or sgr.git_show(repo, commit, ".github/workflows/build/diagnostics/revision_commit_references.py") is not None):
                label = commit[:12] if commit else "working-tree squash"
                errors.extend(f"{path}, {label}: {error}" for error in pending_errors(
                    read(repo, parent, path), read(repo, commit, path)))
        # <!-- custom: Check the staged commit candidate, not unrelated local build outputs or diagnostic overrides.
        # An actual next commit still finalizes pending references even if it only updates artifacts or documentation. (GPT-6.1-Sol) -->
        if not any(commit is None for _parent, commit in transitions) and subprocess.check_output(["git", "diff", "--cached", "--name-only", "HEAD", "--"], cwd=repo).strip():
            staged = subprocess.run(["git", "show", ":" + str(path).replace("\\", "/")], cwd=repo, capture_output=True)
            errors.extend(f"{path}, working-tree: {error}" for error in pending_errors(
                read(repo, "HEAD", path), staged.stdout.decode("utf-8", "replace")))
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check recorder commit references and one-commit pending lifetime.")
    parser.add_argument("--repo-root", type=Path, default=sgr.ROOT)
    parser.add_argument("--default-branch-ref")
    parser.add_argument("--event-name", default="local")
    parser.add_argument("--event-path", type=Path)
    parser.add_argument("--squash", action="store_true")
    args = parser.parse_args()
    event = json.loads(args.event_path.read_text(encoding="utf-8")) if args.event_path else None
    errors = check(args.repo_root, args.default_branch_ref, args.event_name, event, args.squash)
    for error in errors:
        print("FAIL " + error)
    if not errors:
        print("PASS recorder commit references and pending lifetime")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

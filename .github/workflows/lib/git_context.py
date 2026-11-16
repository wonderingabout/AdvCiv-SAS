#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Move the existing Git/base and text-reading functions out of the source-provenance checker so both source and Markdown checks share them without importing one another's scanners.
# Preserve range recovery, error handling and legacy text decoding. (GPT-6.1-Sol) -->
from pathlib import Path
import subprocess
import sys


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result


def has_commit(repo: Path, ref: str) -> bool:
    return run_git(repo, "cat-file", "-e", ref + "^{commit}", check=False).returncode == 0


def ensure_base(repo: Path, base_ref: str | None, event_name: str | None) -> str | None:
    if base_ref and set(base_ref) == {"0"}:
        return None
    if not base_ref:
        candidate = "HEAD^"
        return candidate if has_commit(repo, candidate) else None
    if has_commit(repo, base_ref):
        return push_base_in_history(repo, base_ref) if event_name == "push" else base_ref
    if event_name == "push":
        fetched = run_git(repo, "fetch", "--no-tags", "origin", base_ref, check=False)
        if fetched.returncode == 0 and has_commit(repo, base_ref):
            return base_ref
        print(
            "NOTICE: push-before commit %s is unavailable; change-range checks cannot "
            "check this rewritten push range." % base_ref,
            file=sys.stderr,
        )
        return None
    raise RuntimeError("change-range base %s is unavailable; fetch the base commit first" % base_ref)


# <!-- custom: A push's "before" is the old remote tip, which a force push may have replaced: on 2026-11-16 main was reset under the SASPilot squash, and source_change_provenance.py judged the new commit against that squash, reporting every SASPilot import and binding as removed.
# Judge the push against the newest commit both histories share instead, which for an ordinary push is "before" itself. (Claude code Opus 5.5) -->
def push_base_in_history(repo: Path, before: str) -> str | None:
    if run_git(repo, "merge-base", "--is-ancestor", before, "HEAD", check=False).returncode == 0:
        return before
    merge_base = run_git(repo, "merge-base", before, "HEAD", check=False)
    if merge_base.returncode:
        print("NOTICE: rewritten push from %s shares no history with HEAD; change-range checks cannot check this push range." % before, file=sys.stderr)
        return None
    shared = merge_base.stdout.decode("ascii").strip()
    print("NOTICE: push rewrote history from %s; checking changes since their shared commit %s." % (before, shared), file=sys.stderr)
    return shared


def git_text(repo: Path, ref: str, path: str) -> str | None:
    result = run_git(repo, "show", "%s:%s" % (ref, path), check=False)
    if result.returncode:
        return None
    return decode_text(result.stdout)


# <!-- custom: Use identical legacy decoding for current and historical text so spacing comparisons do not invent edits from encoding differences. (GPT-6.1-Sol) -->
def decode_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")

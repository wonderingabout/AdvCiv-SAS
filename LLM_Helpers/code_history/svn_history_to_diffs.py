#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Standard library only, so the exporter runs anywhere with Python and needs no svn client: urllib and xml for the server's WebDAV log, difflib for patches, concurrent.futures for parallel revisions, and the rest for paths, options and retries. (Claude code Opus 5.5) -->
from __future__ import annotations

import argparse
import concurrent.futures
import difflib
# <!-- custom: fnmatch for --summarize globs, os for atomic file replacement, re for email redaction, sys for exit codes and time for retry backoff. (Claude code Opus 5.5) -->
import fnmatch
import os
import re
import sys
import time
# <!-- custom: urllib and ElementTree talk to the SVN server and parse its log; dataclasses and pathlib hold the parsed revisions and output paths. (Claude code Opus 5.5) -->
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


# <!-- custom: Same defaults as COMMIT_DIFF_MAX_* in make_light_source_zip.py, but check what a run omitted: these limits dropped CvPlayer.cpp and six other core files from Better BTS AI's r379, so that export raises them. See KI#771.2. (Claude code Opus 5.5) -->
DEFAULT_MAX_FILE_PATCH_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_FILE_CHANGED_LINES = 10_000
DEFAULT_MAX_REVISION_PATCH_BYTES = 16 * 1024 * 1024
BINARY_PATTERNS = ("*.7z", "*.bin", "*.bmp", "*.dds", "*.dll", "*.exe", "*.exp", "*.fpk", "*.gif", "*.ico", "*.idb", "*.ilk", "*.jpg", "*.kf", "*.lib", "*.ncb", "*.nif", "*.obj", "*.opt", "*.pch", "*.pdb", "*.png", "*.rar", "*.sdf", "*.suo", "*.tga", "*.zip")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*\w")
NS = {"S": "svn:", "D": "DAV:"}
ACTIONS = {"added-path": "A", "modified-path": "M", "deleted-path": "D", "replaced-path": "R"}


@dataclass(frozen=True)
class Change:
    action: str
    path: str
    kind: str
    text_mods: bool
    copy_path: str | None
    copy_rev: int | None


@dataclass(frozen=True)
class Revision:
    number: int
    author: str
    date: str
    message: str
    changes: tuple[Change, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a Subversion repository's history as one greppable diff per revision, plus INDEX.txt and PATH_HISTORY_INDEX.txt. Needs only Python and an http(s) SVN server (mod_dav_svn); no svn client.")
    parser.add_argument("--url", required=True, help="Repository root URL, for example https://svn.code.sf.net/p/civ4betterai/code/")
    parser.add_argument("--out", required=True, type=Path, help="Output folder. Existing revision files are kept, so an interrupted run resumes.")
    parser.add_argument("--label", required=True, help="Short name that prefixes each file, for example BBAI")
    parser.add_argument("--start", type=int, default=1, help="First revision (default 1)")
    parser.add_argument("--end", type=int, default=None, help="Last revision (default: the latest)")
    # <!-- custom: Realism Invictus lives at /realism/bts/trunk/mod inside the shared civ4mods repository, so a root export would mix in every other mod. (Claude code Opus 5.5) -->
    parser.add_argument("--path", action="append", default=[], metavar="PREFIX", help="Keep only changes under this repository path, for example /realism/bts/trunk/mod; revisions with none are skipped. Repeatable.")
    parser.add_argument("--summarize", action="append", default=[], metavar="GLOB", help="Path glob to list without fetching its contents, such as vendored libraries or art folders. Repeatable.")
    parser.add_argument("--workers", type=int, default=4, help="Revisions fetched in parallel (default 4)")
    # <!-- custom: RI's 630-revision export took about two hours oldest-first, while the revisions we wanted first (2026's EXE patches and Python reload) were the last ones. (Claude code Opus 5.5) -->
    parser.add_argument("--newest-first", action="store_true", help="Fetch the newest revisions first, so recent history is readable while older revisions are still downloading")
    parser.add_argument("--max-file-patch-bytes", type=int, default=DEFAULT_MAX_FILE_PATCH_BYTES)
    parser.add_argument("--max-file-changed-lines", type=int, default=DEFAULT_MAX_FILE_CHANGED_LINES)
    parser.add_argument("--max-revision-patch-bytes", type=int, default=DEFAULT_MAX_REVISION_PATCH_BYTES)
    parser.add_argument("--force", action="store_true", help="Re-render revision files that already exist")
    return parser.parse_args()


def open_url(request: urllib.request.Request | str) -> bytes:
    # <!-- custom: Retry transient network failures, but not 404: that answer means the path is absent at that revision. (Claude code Opus 5.5) -->
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code == 404 or attempt == 4:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == 4:
                raise
        time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def log_report(root_url: str, revision_range: str) -> ET.Element:
    body = f'<?xml version="1.0"?><S:log-report xmlns:S="svn:">{revision_range}<S:discover-changed-paths/><S:path></S:path></S:log-report>'.encode("ascii")
    return ET.fromstring(open_url(urllib.request.Request(root_url, data=body, method="REPORT", headers={"Content-Type": "text/xml"})))


def fetch_log(root_url: str, start: int, end: int | None) -> tuple[int, list[Revision]]:
    # <!-- custom: Log from the repository root: a path-scoped log would silently miss history under older locations, and copy origins come from the same report.
    # With no revision range, SourceForge's server returned only the latest revision, so read that first and then request the span explicitly.
    # The span used to start at r1 whatever --start said; it now covers only the requested revisions, since RI's shared repository logs thousands of other mods' revisions before r5000. (Claude code Opus 5.5) -->
    youngest = int(log_report(root_url, "").find("S:log-item", NS).findtext("D:version-name", namespaces=NS))
    last = youngest if end is None else min(end, youngest)
    revisions = []
    for item in log_report(root_url, f"<S:start-revision>{start}</S:start-revision><S:end-revision>{last}</S:end-revision>").findall("S:log-item", NS):
        changes = []
        for element in item:
            action = ACTIONS.get(element.tag.split("}")[1])
            if action is None:
                continue
            copy_rev = element.get("copyfrom-rev")
            changes.append(Change(action, element.text or "", element.get("node-kind", "unknown"), element.get("text-mods") != "false", element.get("copyfrom-path"), int(copy_rev) if copy_rev else None))
        revisions.append(Revision(int(item.findtext("D:version-name", namespaces=NS)), item.findtext("D:creator-displayname", "(no author)", NS), item.findtext("S:date", "", NS), item.findtext("D:comment", "", NS) or "", tuple(sorted(changes, key=lambda change: change.path))))
    return youngest, sorted(revisions, key=lambda revision: revision.number)


def in_scope(path: str, prefixes: list[str]) -> bool:
    return not prefixes or any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)


def scope_revision(revision: Revision, prefixes: list[str]) -> Revision:
    # <!-- custom: Copy origins outside the scope are kept on the change itself, so a file copied in from another mod still diffs against its source. (Claude code Opus 5.5) -->
    return Revision(revision.number, revision.author, revision.date, revision.message, tuple(change for change in revision.changes if in_scope(change.path, prefixes)))


def fetch_file(root_url: str, path: str, revision: int) -> bytes | None:
    try:
        return open_url(f"{root_url}!svn/bc/{revision}{urllib.parse.quote(path)}")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def base_location(revision: Revision, change: Change) -> tuple[str, int]:
    if change.copy_path is not None:
        return change.copy_path, change.copy_rev
    # <!-- custom: A file edited inside a folder copied in this same revision does not exist at its new path in the previous revision, so diff it against the copy source. (Claude code Opus 5.5) -->
    parents = [candidate for candidate in revision.changes if candidate.copy_path is not None and change.path.startswith(candidate.path + "/")]
    if parents:
        parent = max(parents, key=lambda candidate: len(candidate.path))
        return parent.copy_path + change.path[len(parent.path):], parent.copy_rev
    return change.path, revision.number - 1


def text_lines(data: bytes) -> list[str]:
    # <!-- custom: Old Civ4 sources are often cp1252.
    # Normalize line endings so a CRLF conversion does not look like a whole-file rewrite; such a revision is reported as having no text change. (Claude code Opus 5.5) -->
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("cp1252", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def describe_change(change: Change) -> str:
    origin = f" (from {change.copy_path}@{change.copy_rev})" if change.copy_path else ""
    return f"{change.action} {change.path}{origin}"


def matches_any(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path.lower(), pattern.lower()) for pattern in patterns)


def render_change(root_url: str, revision: Revision, change: Change, args: argparse.Namespace, remaining_bytes: int) -> tuple[str, str]:
    # <!-- custom: Returns (text, omission), where omission is "" (complete), "note" (nothing to show) or "text" (real text was left out, which makes the revision partial). (Claude code Opus 5.5) -->
    header = f"Index: {change.path}\n"
    if change.kind != "file":
        return "", "note"
    if matches_any(change.path, args.summarize):
        return f"{header}# Omitted: matches --summarize\n\n", "text"
    if matches_any(change.path, BINARY_PATTERNS):
        return f"{header}# Binary file, contents not shown\n\n", "note"
    if change.action == "A" and change.copy_path and not change.text_mods:
        return f"{header}# Copied unchanged from {change.copy_path}@{change.copy_rev}\n\n", "note"
    if change.action == "M" and not change.text_mods:
        return f"{header}# Properties changed only\n\n", "note"
    if remaining_bytes <= 0:
        return f"{header}# Omitted: revision patch limit reached\n\n", "text"

    old_path, old_rev = base_location(revision, change)
    needs_old = change.action in ("M", "D") or change.copy_path is not None or (change.action == "R")
    old_data = fetch_file(root_url, old_path, old_rev) if needs_old else None
    new_data = None if change.action == "D" else fetch_file(root_url, change.path, revision.number)
    if (needs_old and old_data is None and change.action != "R") or (change.action != "D" and new_data is None):
        return f"{header}# Unavailable: the server has no contents for this path at this revision\n\n", "text"
    if b"\0" in (old_data or b"") or b"\0" in (new_data or b""):
        return f"{header}# Binary file, contents not shown\n\n", "note"

    old_lines = text_lines(old_data) if old_data is not None else []
    new_lines = text_lines(new_data) if new_data is not None else []
    from_name = f"{old_path}@{old_rev}" if old_data is not None else "/dev/null"
    to_name = f"{change.path}@{revision.number}" if new_data is not None else "/dev/null"
    patch = list(difflib.unified_diff(old_lines, new_lines, from_name, to_name, lineterm=""))
    if not patch:
        return f"{header}# No text change (line endings or identical content)\n\n", "note"
    changed = sum(1 for line in patch[2:] if line[:1] in "+-")
    body = "\n".join(patch) + "\n\n"
    if len(body.encode("utf-8")) > args.max_file_patch_bytes or changed > args.max_file_changed_lines:
        return f"{header}# Omitted: {changed} changed lines exceed the per-file limit\n\n", "text"
    return header + body, ""


def revision_filename(label: str, number: int) -> str:
    return f"{label}_r{number:06d}.diff"


def render_revision(root_url: str, revision: Revision, args: argparse.Namespace) -> None:
    target = args.out / revision_filename(args.label, revision.number)
    if target.exists() and not args.force:
        return
    parts = []
    used = 0
    shown = omitted = 0
    for change in revision.changes:
        text, omission = render_change(root_url, revision, change, args, args.max_revision_patch_bytes - used)
        parts.append(text)
        used += len(text.encode("utf-8"))
        omitted += omission == "text"
        shown += omission == ""
    coverage = "full" if not omitted else ("partial" if shown else "summary-only")
    message_lines = revision.message.splitlines() or ["(no message)"]
    header = ["# SVN revision diff", f"# Source: {root_url}", f"# Revision: {revision.number}", f"# Author: {revision.author}", f"# Date: {revision.date}", f"# Coverage: {coverage}", "# Message:"]
    header += [f"#   {line}" for line in message_lines]
    header.append(f"# Changed paths ({len(revision.changes)}):")
    header += [f"#   {describe_change(change)}" for change in revision.changes]
    text = EMAIL_PATTERN.sub("[email redacted]", "\n".join(header) + "\n\n" + "".join(parts))
    temporary = target.with_suffix(".tmp")
    temporary.write_bytes(text.encode("utf-8"))
    os.replace(temporary, target)


def read_coverage(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("# Coverage: "):
                return line.split(": ", 1)[1].strip()
            if not line.startswith("#"):
                break
    raise ValueError(f"{path} has no coverage line")


def write_indexes(root_url: str, revisions: list[Revision], args: argparse.Namespace) -> dict[str, int]:
    span = f"r{revisions[0].number}-r{revisions[-1].number}"
    index = [f"# SVN revision diff index for {args.label}", f"# Source: {root_url} ({span}, logged from the repository root)", "# Generated by LLM_Helpers/code_history/svn_history_to_diffs.py.", "# Files are named <label>_r<revision>.diff; coverage is full, partial or summary-only.", "# Columns: revision<TAB>date<TAB>author<TAB>changed-paths<TAB>coverage<TAB>title-preview"]
    totals: dict[str, int] = {}
    history: dict[str, list[str]] = {}
    for revision in revisions:
        coverage = read_coverage(args.out / revision_filename(args.label, revision.number))
        totals[coverage] = totals.get(coverage, 0) + 1
        title = next((line.strip() for line in revision.message.splitlines() if line.strip()), "(no message)")
        index.append(EMAIL_PATTERN.sub("[email redacted]", f"{revision.number}\t{revision.date}\t{revision.author}\t{len(revision.changes)}\t{coverage}\t{title.replace(chr(9), ' ')[:120]}"))
        for change in revision.changes:
            origin = f" from {change.copy_path}@{change.copy_rev}" if change.copy_path else ""
            history.setdefault(change.path, []).append(f"  {args.label} r{revision.number} {change.action}{origin}")
    (args.out / "INDEX.txt").write_bytes(("\n".join(index) + "\n").encode("utf-8"))
    paths = [f"# Path history for {args.label} ({span})", "# Maps each path to the revisions that changed it, newest -> oldest.", "# Rows: <label> r<revision> <A|M|D|R> [from <path>@<revision>]. Follow a 'from' origin to continue a file's history before its copy."]
    for path in sorted(history):
        paths.append(path)
        paths.extend(reversed(history[path]))
    (args.out / "PATH_HISTORY_INDEX.txt").write_bytes(("\n".join(paths) + "\n").encode("utf-8"))
    return totals


def main() -> int:
    args = parse_args()
    root_url = args.url.rstrip("/") + "/"
    args.out.mkdir(parents=True, exist_ok=True)
    youngest, logged = fetch_log(root_url, args.start, args.end)
    scoped = [scope_revision(revision, args.path) for revision in logged]
    revisions = [revision for revision in scoped if revision.changes or not args.path]
    if not revisions:
        print(f"No revisions in range{' under ' + ', '.join(args.path) if args.path else ''}; the repository's latest is r{youngest}.", file=sys.stderr)
        return 1
    print(f"{args.label}: r{revisions[0].number}-r{revisions[-1].number}, {len(revisions)} revisions, {sum(len(revision.changes) for revision in revisions)} changed paths")
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        order = reversed(revisions) if args.newest_first else revisions
        futures = {pool.submit(render_revision, root_url, revision, args): revision.number for revision in order}
        for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
            if future.exception() is not None:
                failures.append((futures[future], future.exception()))
            if done % 25 == 0 or done == len(futures):
                print(f"  {done}/{len(futures)} revisions, {len(failures)} failed", flush=True)
    # <!-- custom: Report failures loudly and write no index over an incomplete set; rerunning fetches only the missing revisions. (Claude code Opus 5.5) -->
    if failures:
        for number, error in sorted(failures, key=lambda failure: failure[0]):
            print(f"r{number} failed: {error}", file=sys.stderr)
        print(f"{len(failures)} revisions failed. Rerun the same command to retry them.", file=sys.stderr)
        return 1
    totals = write_indexes(root_url, revisions, args)
    size = sum(path.stat().st_size for path in args.out.iterdir() if path.is_file())
    print(f"Coverage: {totals}")
    print(f"Wrote {args.out} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: argparse for options, re for hunk headers and sys for the exit code. (Claude code Opus 5.5) -->
from __future__ import annotations

import argparse
import re
import sys
# <!-- custom: pathlib reads the export and checkout; text_lines makes the comparison normalize text exactly as the exporter did. (Claude code Opus 5.5) -->
from pathlib import Path

from svn_history_to_diffs import text_lines


HUNK = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
HISTORY_ROW = re.compile(r"  \S+ r(\d+) ([AMDR])(?: from (.+)@(\d+))?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify an svn_history_to_diffs.py export: rebuild files from their stored patches, from the first revision, and compare them with a checkout.")
    parser.add_argument("--out", required=True, type=Path, help="Export folder holding the .diff files and PATH_HISTORY_INDEX.txt")
    parser.add_argument("--label", required=True, help="Label used for the export, for example BBAI")
    parser.add_argument("--checkout", required=True, type=Path, help="Checkout folder to compare with")
    parser.add_argument("--repo-path", required=True, help="Repository path of that checkout, for example trunk/CvGameCoreDLL")
    parser.add_argument("--glob", action="append", default=[], help="File pattern inside the checkout. Repeatable. Default: *.cpp and *.h")
    return parser.parse_args()


def load_history(out: Path) -> dict[str, list[tuple[int, str, str | None, int | None]]]:
    history: dict[str, list[tuple[int, str, str | None, int | None]]] = {}
    current = ""
    for line in (out / "PATH_HISTORY_INDEX.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        if not line.startswith("  "):
            current = line
            history[current] = []
            continue
        match = HISTORY_ROW.match(line)
        history[current].append((int(match[1]), match[2], match[3], int(match[4]) if match[4] else None))
    return history


def chain(history: dict, path: str, last_revision: int) -> list[tuple[int, str, str]]:
    # <!-- custom: Oldest-first (revision, action, path) steps for one file, following copy origins backwards.
    # A file born inside a copied folder has no copy row of its own, so the nearest copied parent supplies its origin. (Claude code Opus 5.5) -->
    rows = sorted((row for row in history.get(path, []) if row[0] <= last_revision), key=lambda row: row[0])
    for index in range(len(rows) - 1, -1, -1):
        if rows[index][1] in "AR":
            rows = rows[index:]
            break
    if rows and rows[0][1] in "AR":
        revision, action, origin, origin_revision = rows[0]
        steps = chain(history, origin, origin_revision) if origin else []
        return steps + [(row[0], "M" if origin and row[0] == revision else row[1], path) for row in rows]
    parent = path
    while "/" in parent[1:]:
        parent = parent.rsplit("/", 1)[0]
        copies = [row for row in history.get(parent, []) if row[1] in "AR" and row[2] and row[0] <= last_revision]
        if copies:
            copy = max(copies, key=lambda row: row[0])
            return chain(history, copy[2] + path[len(parent):], copy[3]) + [(row[0], row[1], path) for row in rows if row[0] > copy[0]]
    return [(row[0], row[1], path) for row in rows]


def section(out: Path, label: str, revision: int, path: str) -> str | None:
    text = (out / f"{label}_r{revision:06d}.diff").read_bytes().decode("utf-8")
    header = f"\nIndex: {path}\n"
    start = text.find(header)
    if start < 0:
        return None
    start += len(header)
    end = text.find("\nIndex: ", start)
    return text[start:end if end >= 0 else len(text)]


def apply_patch(old: list[str], patch: str) -> list[str]:
    lines = patch.split("\n")
    index = next((position for position, line in enumerate(lines) if line.startswith("@@")), len(lines))
    result: list[str] = []
    position = 0
    while index < len(lines) and lines[index].startswith("@@"):
        match = HUNK.match(lines[index])
        old_left = int(match[2] or 1)
        new_left = int(match[4] or 1)
        start = int(match[1]) - 1 if old_left else int(match[1])
        result += old[position:start]
        position = start
        index += 1
        while old_left > 0 or new_left > 0:
            kind, value = lines[index][:1], lines[index][1:]
            index += 1
            if kind in " -":
                if old[position] != value:
                    raise ValueError(f"line {position + 1} does not match the patch")
                position += 1
                old_left -= 1
            if kind in " +":
                result.append(value)
                new_left -= 1
    return result + old[position:]


def rebuild(out: Path, label: str, steps: list[tuple[int, str, str]]) -> tuple[list[str] | None, str]:
    lines: list[str] = []
    for revision, action, path in steps:
        patch = section(out, label, revision, path)
        if patch is None:
            continue
        if action == "D":
            lines = []
            continue
        if patch.startswith("# Omitted") or patch.startswith("# Unavailable") or patch.startswith("# Binary"):
            return None, f"r{revision}: {patch.splitlines()[0]}"
        if patch.lstrip().startswith("---"):
            lines = apply_patch([] if action in "AR" else lines, patch)
    return lines, ""


def main() -> int:
    args = parse_args()
    history = load_history(args.out)
    newest = max(row[0] for rows in history.values() for row in rows)
    # <!-- custom: Git Bash rewrote a leading-slash argument into a Windows path, which silently matched no files, so the slash is optional and added here. (Claude code Opus 5.5) -->
    repo_path = "/" + args.repo_path.strip("/")
    patterns = args.glob or ["*.cpp", "*.h"]
    matched = bad = unverifiable = patches = 0
    for pattern in patterns:
        for file_path in sorted(args.checkout.rglob(pattern)):
            path = f"{repo_path}/{file_path.relative_to(args.checkout).as_posix()}"
            steps = chain(history, path, newest)
            if not steps:
                continue
            try:
                lines, reason = rebuild(args.out, args.label, steps)
            except (ValueError, IndexError) as error:
                bad += 1
                print(f"FAIL {path}: {error}")
                continue
            if lines is None:
                unverifiable += 1
                print(f"SKIP {path}: {reason}")
            elif lines != text_lines(file_path.read_bytes()):
                bad += 1
                print(f"FAIL {path}: rebuilt file differs from the checkout")
            else:
                matched += 1
                patches += len(steps)
    print(f"{matched} files match after replaying {patches} patches; {bad} failed; {unverifiable} could not be rebuilt")
    return 1 if bad or not matched else 0


if __name__ == "__main__":
    sys.exit(main())

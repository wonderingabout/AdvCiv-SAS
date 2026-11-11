#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Evidence screenshots live in Google Drive folders linked from the docs, mostly one folder per Known Issue.
# A link copied from another entry still opens a real folder, so the wrong evidence goes unnoticed: on 2026-11-11, KI#1071 linked KI#2's folder.
# Require each Drive file or folder to be linked at most once per document, and every Drive link to have a recognised form with an ID.
# Whether a link opens is not checked: that needs the network and the folder's sharing settings. (Claude Code Opus 5.5) -->
# <!-- custom: argparse/pathlib provide the repository CLI, re extracts the links, subprocess lists the tracked Markdown files and sys reports the exit status. (Claude Code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Inherited and imported material keeps its own links. (Claude Code Opus 5.5) -->
EXCLUDED_PREFIXES = ("_0_Legacy/", "LLM_Helpers/context/", "_1_AdvCiv-SAS/Docs/changelogs_web/")
DRIVE_LINK = re.compile(r"https?://(?:drive|docs)\.google\.com/[^\s)\]>\"'`]+")
DRIVE_ID_FORMS = (
    re.compile(r"/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]{20,})"),
    re.compile(r"/file/d/([A-Za-z0-9_-]{20,})"),
    re.compile(r"[?&]id=([A-Za-z0-9_-]{20,})"),
    re.compile(r"/(?:document|spreadsheets|presentation)/d/([A-Za-z0-9_-]{20,})"),
)


def drive_id(link):
    for form in DRIVE_ID_FORMS:
        match = form.search(link)
        if match:
            return match.group(1)
    return None


def markdown_files(root):
    # <!-- custom: Plain git ls-files quotes names with characters such as an accented letter, so a tracked file named with an accented letter could not be opened, as Codex's 2026-11-11 review found; -z lists them unquoted, NUL-separated. (Claude Code Opus 5.5) -->
    listed = [path for path in subprocess.run(["git", "ls-files", "-z", "*.md"], cwd=root, capture_output=True, check=True).stdout.decode("utf-8").split("\0") if path]
    return [path for path in listed if not path.startswith(EXCLUDED_PREFIXES)]


def check_text(name, text):
    errors = []
    lines_by_id = {}
    for number, line in enumerate(text.splitlines(), 1):
        for link in DRIVE_LINK.findall(line):
            found = drive_id(link)
            if found is None:
                errors.append(f"{name}:{number}: unrecognised Google Drive link form: {link}")
                continue
            lines_by_id.setdefault(found, []).append(number)
    for found, numbers in lines_by_id.items():
        if len(numbers) > 1:
            lines = ", ".join(str(number) for number in numbers)
            errors.append(f"{name}: Drive ID {found} is linked on lines {lines}; each file or folder should be linked once per document, so check that each place links its own evidence")
    return errors, sum(len(numbers) for numbers in lines_by_id.values())


def main():
    parser = argparse.ArgumentParser(description="Check that each Google Drive file or folder is linked at most once per Markdown document, with a recognised link form.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = []
    count = 0
    for path in markdown_files(args.repo_root):
        file_errors, file_count = check_text(path, (args.repo_root / path).read_text(encoding="utf-8"))
        errors.extend(file_errors)
        count += file_count
    print(f"{'FAIL' if errors else 'PASS'} Google Drive links ({count} links)")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())

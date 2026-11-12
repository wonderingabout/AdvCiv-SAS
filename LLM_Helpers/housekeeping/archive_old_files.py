#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Folders that agents and the user list often, such as Civ4's ScreenShots and Logs, grew to thousands of entries; on 2026-11-10 ScreenShots held 3,000+ images and was slow to list even on an SSD.
# Moving the older entries into one dated subfolder keeps every file while the folder itself stays small; the user had been doing this by hand with names such as old10-part2.
# This helper keeps the newest entries in place and moves the rest into old_<UTC time>, so archives sort by date.
# It only previews unless --apply is given. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; datetime names the archive folder; pathlib handles paths; shutil moves entries. (Claude Code Opus 5.5) -->
import argparse
import datetime
from pathlib import Path
import shutil
# <!-- custom: subprocess asks Windows whether Civ4 runs; sys gives the exit code. (Claude Code Opus 5.5) -->
import subprocess
import sys

USER_ROOT = Path.home() / "Documents" / "My Games" / "beyond the sword"
KNOWN_FOLDERS = {
    "screenshots": USER_ROOT / "ScreenShots",
    "logs": USER_ROOT / "Logs",
    "autoplay-screenshots": Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "autoplay_screenshots",
}
ARCHIVE_PREFIX = "old"


def civ4_running():
    # <!-- custom: A failed tasklist printed nothing and read as "Civ4 closed", letting --apply move live logs, as Codex's 2026-11-11 review showed; an unanswered check now counts as running. (Claude Code Opus 5.5) -->
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Civ4BeyondSword.exe", "/NH"], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return True
    return "Civ4BeyondSword.exe" in result.stdout


def files_by_recency(folder):
    # <!-- custom: Skip archive folders and in-progress autoplay reports, which become JSON only after the runner finishes writing them. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
    files = [
        path for path in folder.iterdir()
        if path.is_file() and not path.name.startswith(ARCHIVE_PREFIX) and not path.match("SASAutoplay_*.tmp")
    ]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def archive(folder, keep, apply):
    # <!-- custom: Shared by the command line and by run_autoplay.py, which tidies the folders it fills once its own Civ4 is closed, so no agent has to remember the upkeep (user's request, 2026-11-12).
    # Returns how many entries moved. (Claude code Opus 5.5) -->
    files = files_by_recency(folder)
    moving = files[keep:]
    archive_folder = folder / (ARCHIVE_PREFIX + "_" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    print("%s: %d entries %s, %d %s to %s" % (folder, len(files) - len(moving), "stay" if apply else "would stay", len(moving), "move" if apply else "would move", archive_folder.name))
    if not apply or not moving:
        return 0
    archive_folder.mkdir()
    moved = 0
    for path in moving:
        # <!-- custom: Codex noted that Civ4 was checked only once before moving, so a second runner could launch during a long move; the check now repeats every 200 entries and stops the move. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
        if moved and moved % 200 == 0 and civ4_running():
            print("Civ4 started while archiving; stopped after %d entries" % moved)
            return moved
        shutil.move(str(path), str(archive_folder / path.name))
        moved += 1
    print("moved %d entries" % moved)
    return moved


def archive_crowded(keep=1000):
    # <!-- custom: Archives only the known folders holding more than keep entries, and nothing while any Civ4 runs. (Claude code Opus 5.5) -->
    if civ4_running():
        return 0
    moved = 0
    for folder in KNOWN_FOLDERS.values():
        if civ4_running():
            break
        if folder.is_dir() and len(files_by_recency(folder)) > keep:
            moved += archive(folder, keep, True)
    return moved


def main():
    parser = argparse.ArgumentParser(description="Keep a folder's newest entries and move the rest into a dated old_<UTC> subfolder. Previews unless --apply is given.")
    parser.add_argument("folder", nargs="?", help="a folder path, or one of: " + ", ".join(sorted(KNOWN_FOLDERS)))
    parser.add_argument("--all", action="store_true", help="check every known folder instead of one, archiving those with more than --keep entries when --apply is given")
    parser.add_argument("--keep", type=int, default=1000, help="how many of the newest entries stay in place (default 1000)")
    parser.add_argument("--apply", action="store_true", help="move the entries; without it, only list what would move")
    args = parser.parse_args()
    if args.all == bool(args.folder):
        parser.error("give one folder, or --all")
    folders = list(KNOWN_FOLDERS.values()) if args.all else [KNOWN_FOLDERS.get(args.folder, Path(args.folder))]
    # <!-- custom: Civ4 writes into ScreenShots and Logs while it runs, and an open log must not move mid-write. (Claude Code Opus 5.5) -->
    if args.apply and civ4_running():
        parser.error("Civ4 is running; close it before archiving")
    for folder in folders:
        if not folder.is_dir():
            if args.all:
                continue
            parser.error("not a folder: %s" % folder)
        archive(folder, args.keep, args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())

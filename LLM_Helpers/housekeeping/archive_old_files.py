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


# <!-- custom: Crash dumps clutter by size, not by count: a full dump of a game is 1.2 to 1.5 GB, so moving them into an old_ subfolder frees nothing.
# desktop_windows.py dump leaves a Civ4BeyondSword_<pid>_<time>.dmp copy in Temp per crash, and crash_dumps/ grows as dumps are kept for KIs (3.1 GB on 2026-11-18).
# So dumps get a report rather than an archive, and nothing is deleted: a kept dump may still be a KI's evidence, which only whoever works that KI can judge.
# The user asked on 2026-11-18 that a forgotten dump not go unnoticed. (Claude code Opus 5.5) -->
DUMP_PLACES = (
    ("Temp", Path.home() / "AppData" / "Local" / "Temp", "Civ4BeyondSword*.dmp"),
    ("crash_dumps", Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "crash_dumps", "**/*.dmp"),
)
DUMP_LIMIT_GB = 5
TEMP_DUMP_DAYS = 7


def dump_report(quiet=False):
    # <!-- custom: Quiet, as after an autoplay run, it prints only when the dumps pass DUMP_LIMIT_GB or a Temp copy is older than TEMP_DUMP_DAYS, so a run with nothing to say stays silent. (Claude code Opus 5.5) -->
    now = datetime.datetime.now().timestamp()
    rows = []
    for place, folder, pattern in DUMP_PLACES:
        if folder.is_dir():
            for path in folder.glob(pattern):
                stat = path.stat()
                rows.append((place, path, stat.st_size, (now - stat.st_mtime) / 86400.0))
    total_gb = sum(row[2] for row in rows) / 1073741824.0
    stale = [row for row in rows if row[0] == "Temp" and row[3] > TEMP_DUMP_DAYS]
    if quiet and total_gb <= DUMP_LIMIT_GB and not stale:
        return total_gb
    for place, path, size, age in sorted(rows, key=lambda row: -row[2]):
        print("%-11s %7.2f GB  %5.0f days  %s" % (place, size / 1073741824.0, age, path))
    print("Civ4 crash dumps: %d, %.2f GB in all%s" % (len(rows), total_gb, " (over %d GB)" % DUMP_LIMIT_GB if total_gb > DUMP_LIMIT_GB else ""))
    if stale:
        print("%d dump copies in Temp are over %d days old; keep a useful one in crash_dumps/ with its DLL and PDB, and send the rest to the Recycle Bin" % (len(stale), TEMP_DUMP_DAYS))
    return total_gb


def main():
    parser = argparse.ArgumentParser(description="Keep a folder's newest entries and move the rest into a dated old_<UTC> subfolder. Previews unless --apply is given.")
    parser.add_argument("folder", nargs="?", help="a folder path, or one of: " + ", ".join(sorted(KNOWN_FOLDERS)))
    parser.add_argument("--all", action="store_true", help="check every known folder instead of one, archiving those with more than --keep entries when --apply is given")
    parser.add_argument("--keep", type=int, default=1000, help="how many of the newest entries stay in place (default 1000)")
    parser.add_argument("--apply", action="store_true", help="move the entries; without it, only list what would move")
    parser.add_argument("--dumps", action="store_true", help="instead, list Civ4 crash dumps in Temp and crash_dumps/ with their size and age; deletes nothing")
    args = parser.parse_args()
    if args.dumps:
        dump_report()
        return 0
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

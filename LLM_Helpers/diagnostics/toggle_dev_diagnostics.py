#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Toggle the usual local development diagnostics in GlobalDefines_advciv_sas.xml on or back to shipped defaults.

# <!-- custom: __future__.annotations postpones evaluation of this Python-3 helper's annotations. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse exposes the on/off/status CLI; re edits define values in place, subprocess checks for a running Civ4 process and reads the committed XML, pathlib locates the XML, and sys finds define_values.py beside this script. (Claude code Opus 5.5) -->
import argparse
import re
import subprocess
import sys
from pathlib import Path


# <!-- custom: Helpers now sit in LLM_Helpers folders named by job, so find the repo root from the LLM_Helpers folder instead of a fixed parent depth. (Claude code Opus 5.5) -->
REPO_ROOT = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent
DEFINES_RELATIVE = "Assets/XML/GlobalDefines_advciv_sas.xml"
DEFINES_PATH = REPO_ROOT / DEFINES_RELATIVE
# <!-- custom: The shipped values once lived in this table too, a second copy of what the CI checks require that could drift from them.
# Import them from define_values.py, which those checks import too, so "off" always yields what CI accepts; the development values sit beside them so both settings are seen in one place.
# Remembering to re-enable the unstaged development values after each commit/amend was tedious, and forgetting meant losing records from the next test run. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parent))
from define_values import DEVELOPMENT_VALUES, SHIPPED_VALUES  # noqa: E402 - run_autoplay.py loads this script by file path, so its folder is not always on sys.path


def build_dev_diagnostics() -> dict[str, tuple[int, int]]:
    # <!-- custom: A toggled define without a CI-required shipped value would have no committable value for "off"; add it to define_values.py first. (Claude code Opus 5.5) -->
    unpinned = [name for name in DEVELOPMENT_VALUES if name not in SHIPPED_VALUES]
    if unpinned:
        raise SystemExit("No CI check pins a shipped value for %s; add one to LLM_Helpers/diagnostics/define_values.py before toggling it." % ", ".join(unpinned))
    return {name: (SHIPPED_VALUES[name], dev) for name, dev in DEVELOPMENT_VALUES.items()}


# Each entry is name: (shipped, development).
DEV_DIAGNOSTICS = build_dev_diagnostics()


def define_pattern(name: str) -> re.Pattern:
    return re.compile(r"(<DefineName>%s</DefineName>\s*<iDefineIntVal>)(-?\d+)(</iDefineIntVal>)" % re.escape(name))


def civ4_running() -> bool:
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Civ4BeyondSword.exe", "/NH"], capture_output=True, text=True, check=True)
    return "Civ4BeyondSword.exe" in result.stdout


def current_values(text: str) -> dict[str, int]:
    values = {}
    for name in DEV_DIAGNOSTICS:
        matches = define_pattern(name).findall(text)
        if len(matches) != 1:
            raise SystemExit("Expected exactly one %s define in %s, found %d." % (name, DEFINES_PATH, len(matches)))
        values[name] = int(matches[0][1])
    return values


# <!-- custom: On 2026-11-19 every value was at its development setting except SAS_UI_DAWN_OF_MAN_ON, left at 1 after a branch switch, and the per-line status did not make the odd one out stand out; the screen then showed in agent test games.
# Report which values are not at the setting most of them share, so a partial restore is visible from status and from run_autoplay.py. (Claude code Opus 5.5) -->
def mixed_values(values: dict[str, int]) -> tuple[str, list[str]]:
    dev_names = [name for name, value in values.items() if value == DEV_DIAGNOSTICS[name][1]]
    if len(dev_names) == len(values):
        return "development", []
    shipped_names = [name for name, value in values.items() if value == DEV_DIAGNOSTICS[name][0]]
    if len(shipped_names) == len(values):
        return "shipped", []
    if len(dev_names) >= len(shipped_names):
        return "development", [name for name in values if name not in dev_names]
    return "shipped", [name for name in values if name not in shipped_names]


def int_defines(text: str) -> dict[str, int]:
    return {match.group(1): int(match.group(2)) for match in re.finditer(r"<DefineName>(\w+)</DefineName>\s*<iDefineIntVal>(-?\d+)</iDefineIntVal>", text)}


# <!-- custom: The toggle sees only its own table, so a define changed locally by habit outside it would go unnoticed and "off" would not reset it.
# Comparing every integer define with the committed XML shows such changes without another list to keep. (Claude code Opus 5.5) -->
def untoggled_changes(text: str) -> list[tuple[str, int | None, int | None]]:
    committed = int_defines(subprocess.run(["git", "-C", str(REPO_ROOT), "show", "HEAD:" + DEFINES_RELATIVE], capture_output=True, check=True).stdout.decode("utf-8"))
    current = int_defines(text)
    return [(name, committed.get(name), current.get(name)) for name in sorted(set(committed) | set(current)) if name not in DEV_DIAGNOSTICS and committed.get(name) != current.get(name)]


def read_mixed_values() -> tuple[str, list[str]]:
    return mixed_values(current_values(DEFINES_PATH.read_bytes().decode("utf-8")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Toggle the usual local development diagnostics (%s) on, or back to shipped defaults." % ", ".join(DEV_DIAGNOSTICS))
    parser.add_argument("mode", choices=("on", "off", "status", "stage"), help="on = development values, off = shipped defaults, status = print current values, exiting 1 when they are mixed, stage = stage the working file with shipped defaults, leaving it unchanged")
    args = parser.parse_args()
    # <!-- custom: Read/write bytes so the file's CRLF line endings and encoding stay untouched. (Claude code Opus 5.5) -->
    text = DEFINES_PATH.read_bytes().decode("utf-8")
    values = current_values(text)
    if args.mode == "status":
        for name, current in values.items():
            shipped, dev = DEV_DIAGNOSTICS[name]
            label = "development" if current == dev else "shipped" if current == shipped else "custom"
            print("%s=%d (%s)" % (name, current, label))
        for name, committed, current in untoggled_changes(text):
            print("not toggled, differs from HEAD: %s %s -> %s" % (name, "-" if committed is None else committed, "-" if current is None else current))
        majority, odd = mixed_values(values)
        if not odd:
            print("all %s" % majority)
            return
        raise SystemExit("MIXED: mostly %s, but not %s; run 'on' or 'off' to make them consistent" % (majority, ", ".join(odd)))
    for name, current in values.items():
        shipped, dev = DEV_DIAGNOSTICS[name]
        target = dev if args.mode == "on" else shipped
        text = define_pattern(name).sub(lambda m: "%s%d%s" % (m.group(1), target, m.group(3)), text)
        print("%s: %d -> %d" % (name, current, target))
    # <!-- custom: "off" then "on" around staging needs Civ4 closed, and on 2026-11-19 the user had it open on a game; staging a copy with shipped values leaves the working file, and the game reading it, untouched.
    # git hash-object --path applies the repository's line-ending rules, as "git add" would. (Claude code Opus 5.5) -->
    if args.mode == "stage":
        sha = subprocess.run(["git", "-C", str(REPO_ROOT), "hash-object", "-w", "--path=" + DEFINES_RELATIVE, "--stdin"], input=text.encode("utf-8"), capture_output=True, check=True).stdout.decode("ascii").strip()
        subprocess.run(["git", "-C", str(REPO_ROOT), "update-index", "--cacheinfo", "100644," + sha + "," + DEFINES_RELATIVE], check=True)
        print("staged %s with shipped defaults; the working file keeps its values" % DEFINES_RELATIVE)
        return
    # <!-- custom: Live XML edits during a run have produced XML errors and crashes; refuse rather than edit under a running game. (Claude code Opus 5.5) -->
    if civ4_running():
        raise SystemExit("Civ4BeyondSword.exe is running; close it before editing GlobalDefines (nothing was written).")
    DEFINES_PATH.write_bytes(text.encode("utf-8"))
    print("wrote %s" % DEFINES_PATH)


if __name__ == "__main__":
    main()

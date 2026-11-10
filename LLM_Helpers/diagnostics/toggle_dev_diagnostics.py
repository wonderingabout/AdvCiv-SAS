#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Toggle the usual local development diagnostics in GlobalDefines_advciv_sas.xml on or back to shipped defaults.

# <!-- custom: __future__.annotations postpones evaluation of this Python-3 helper's annotations. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse exposes the on/off/status CLI; re edits define values in place, subprocess checks for a running Civ4 process, and pathlib locates the XML. (Claude code Opus 5.5) -->
import argparse
import re
import subprocess
from pathlib import Path


# <!-- custom: Helpers now sit in LLM_Helpers folders named by job, so find the repo root from the LLM_Helpers folder instead of a fixed parent depth. (Claude code Opus 5.5) -->
DEFINES_PATH = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent / "Assets" / "XML" / "GlobalDefines_advciv_sas.xml"
# <!-- custom: Remembering to re-enable these unstaged development values after each commit/amend was tedious, and forgetting meant losing records from the next test run.
# Shipped values match the diagnostics CI expectations, so "off" yields a committable XML.
# Each entry is name: (shipped, development). (Claude code Opus 5.5) -->
DEV_DIAGNOSTICS = {
    "SAS_SGR_LOG": (0, 3),
    "SAS_SGR_MAP_ANNOTATION_TEXT_ON": (0, 1),
    "SAS_RUNTIME_STATUS_ON": (0, 1),
    "SAS_RUNTIME_SCREENSHOT_WATCH_ON": (0, 1),
    "SAS_RUNTIME_SOURCE_WATCH_ON": (0, 1),
}


def define_pattern(name: str) -> re.Pattern:
    return re.compile(r"(<DefineName>%s</DefineName>\s*<iDefineIntVal>)(-?\d+)(</iDefineIntVal>)" % re.escape(name))


def civ4_running() -> bool:
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Civ4BeyondSword.exe", "/NH"], capture_output=True, text=True, check=True)
    return "Civ4BeyondSword.exe" in result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Toggle the usual local development diagnostics (%s) on, or back to shipped defaults." % ", ".join(DEV_DIAGNOSTICS))
    parser.add_argument("mode", choices=("on", "off", "status"), help="on = development values, off = shipped defaults, status = print current values")
    args = parser.parse_args()
    # <!-- custom: Read/write bytes so the file's CRLF line endings and encoding stay untouched. (Claude code Opus 5.5) -->
    text = DEFINES_PATH.read_bytes().decode("utf-8")
    for name, (shipped, dev) in DEV_DIAGNOSTICS.items():
        matches = define_pattern(name).findall(text)
        if len(matches) != 1:
            raise SystemExit("Expected exactly one %s define in %s, found %d." % (name, DEFINES_PATH, len(matches)))
        current = int(matches[0][1])
        if args.mode == "status":
            label = "development" if current == dev else "shipped" if current == shipped else "custom"
            print("%s=%d (%s)" % (name, current, label))
            continue
        target = dev if args.mode == "on" else shipped
        text = define_pattern(name).sub(lambda m: "%s%d%s" % (m.group(1), target, m.group(3)), text)
        print("%s: %d -> %d" % (name, current, target))
    if args.mode == "status":
        return
    # <!-- custom: Live XML edits during a run have produced XML errors and crashes; refuse rather than edit under a running game. (Claude code Opus 5.5) -->
    if civ4_running():
        raise SystemExit("Civ4BeyondSword.exe is running; close it before editing GlobalDefines (nothing was written).")
    DEFINES_PATH.write_bytes(text.encode("utf-8"))
    print("wrote %s" % DEFINES_PATH)


if __name__ == "__main__":
    main()

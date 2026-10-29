#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Keep runtime recording disabled for distributed gameplay; local developer overrides remain separate.
# Source-token inventories cannot establish callback ordering or valid JSON, and made ordinary refactoring require parallel checker edits.
# The native harness exercises output/timing/failure behavior; actual EXE lifecycle observations require game testing. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->

# <!-- custom: Path/argparse provide the repository CLI; sys exposes the shared XML helpers. (GPT-6.1-Sol) -->
from pathlib import Path
import argparse
# <!-- custom: Distinguish executable filename literals from comments when validating declared launch/load references; this is not a control-flow parser. (GPT-6.1-Sol) -->
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
# <!-- custom: Reuse integer-Define parsing and shipped-value validation rather than inspect source spellings. (GPT-6.1-Sol) -->
from xml_defines import get_default_repo_root, read_global_define_ints, require_int_values


# <!-- custom: Default-value checks alone did not require a newly added observer to declare its control.
# Register each shipped PowerShell/C# companion's switch and launch/load owner, including shared helpers; the C# listener and environment helper inherit the Runtime master rather than starting independent processes.
# This small inventory enforces explicit control review, not a source-token proof of execution paths; Windows fixtures still exercise real launch/lifecycle behavior. (GPT-6.1-Sol) -->
RUNTIME_COMPONENT_CONTROLS = {
    "SASRuntimeExitObserver.ps1": ("SAS_RUNTIME_STATUS_ON", "CvGameCoreDLL/SASRuntimeStatus.cpp"),
    "SASRuntimeSourceObserver.ps1": ("SAS_RUNTIME_SOURCE_WATCH_ON", "CvGameCoreDLL/SASRuntimeStatus.cpp"),
    "SASRuntimeScreenshotObserver.ps1": ("SAS_RUNTIME_SCREENSHOT_WATCH_ON", "Assets/SASRuntimeExitObserver.ps1"),
    "SASRuntimeDialogObserver.cs": ("SAS_RUNTIME_STATUS_ON", "Assets/SASRuntimeExitObserver.ps1"),
    "SASRuntimeObserverEnvironment.ps1": ("SAS_RUNTIME_STATUS_ON", "Assets/SASRuntimeExitObserver.ps1"),
}


# <!-- custom: Tokenize comments and string literals together so quoted filenames inside comments do not count, while // or # inside a real quoted path stays literal.
# C++/C# and the current PowerShell owner forms are supported; dynamically assembled filenames need deliberate review rather than an inferred execution claim. (GPT-6.1-Sol) -->
def referenced_filename(name, source):
    token = re.compile(r"//[^\n]*|/\*.*?\*/|\#.*?$|<\#.*?\#>|(?P<quoted>\"(?:\\.|[^\"\\])*\"|'(?:''|[^'])*')", re.MULTILINE | re.DOTALL)
    return any(match.group("quoted") and name in match.group("quoted") for match in token.finditer(source))


def observer_control_errors(repo_root, defines):
    failures = []
    # <!-- custom: A suffix-only SASRuntime*Observer glob could silently miss a newly named companion.
    # Scan every shipped top-level .ps1/.cs file so renaming an observer cannot remove the registration requirement. (GPT-6.1-Sol) -->
    components = {path.name: path for path in (repo_root / "Assets").iterdir() if path.is_file() and path.suffix.lower() in (".ps1", ".cs")}
    failures.extend(f"Assets/{name}: registered companion is missing; reconcile its launch/load owner and control registration" for name in sorted(RUNTIME_COMPONENT_CONTROLS.keys() - components.keys()))
    for path in sorted(components.values()):
        if path.name not in RUNTIME_COMPONENT_CONTROLS:
            failures.append(f"Assets/{path.name}: declare its default-off Define and launch/load owner in RUNTIME_COMPONENT_CONTROLS; review actual pre-gating too")
            continue
        control, owner = RUNTIME_COMPONENT_CONTROLS[path.name]
        if defines.get(control) != 0:
            failures.append(f"Assets/{path.name}: component control {control} must exist and ship as 0")
        owner_path = repo_root / owner
        if not owner_path.is_file() or not referenced_filename(path.name, owner_path.read_text(encoding="utf-8")):
            failures.append(f"Assets/{path.name}: declared launch/load owner {owner} has no filename literal referencing it outside comments")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Check shipped runtime-recording/source-watcher defaults.")
    parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
    args = parser.parse_args()
    # <!-- custom: Source and screenshot observation are independently opt-in; enforce their shipped defaults too, even when the parent runtime switch is off. (GPT-6.1-Sol) -->
    defines = read_global_define_ints(args.repo_root)
    failures = require_int_values(defines, {"SAS_RUNTIME_STATUS_ON": 0, "SAS_RUNTIME_PLAYER_TURN_LIVE_THRESHOLD_MS": 3000, "SAS_RUNTIME_PLAYER_TURN_LIVE_REFRESH_MS": 3000, "SAS_RUNTIME_SOURCE_WATCH_ON": 0, "SAS_RUNTIME_SCREENSHOT_WATCH_ON": 0})
    failures.extend(observer_control_errors(args.repo_root, defines))
    if failures:
        print("FAIL SAS runtime-status default")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASS SAS runtime status: recording/source/screenshot defaults off; shipped companion controls and owners declared")
    return 0


if __name__ == "__main__":
    sys.exit(main())

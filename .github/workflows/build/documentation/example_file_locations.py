#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Reserve _example for textual/code/data captures in Docs/examples; screenshots use descriptive names without that marker in Images.
# argparse/pathlib provide the CLI and path classification; sys locates shared Git range handling. (GPT-6.1-Sol) -->
import argparse
from pathlib import Path, PurePosixPath
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
# <!-- custom: Reuse push/PR base resolution and Git's filename inventory instead of scanning or decoding every file. (GPT-6.1-Sol) -->
import git_context

ROOT = Path(__file__).resolve().parents[4]
CHECKER = Path(__file__).resolve().relative_to(ROOT).as_posix()
EXAMPLES = "_1_AdvCiv-SAS/Docs/examples/"
IMAGES = "_1_AdvCiv-SAS/Images/"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tga", ".dds", ".ico"}


def placement_errors(paths):
    errors = []
    for value in sorted(set(paths)):
        path = PurePosixPath(value)
        if "_example" not in path.name.lower():
            continue
        # <!-- custom: Imported/generated context is not maintained capture output; executable test modules can name the examples they validate without themselves being example artifacts. (GPT-6.1-Sol) -->
        if value.startswith(("_0_Common_Docs/", "LLM_Helpers/context/", "LLM_Helpers/outputs/", "_SNAPSHOT_CONTEXT/")):
            continue
        if value.startswith((".github/workflows/tests/", "tests/")) and path.name.startswith("test_"):
            continue
        if path.suffix.lower() in IMAGE_SUFFIXES:
            errors.append(f"{value}: _example is reserved for textual/code/data examples; rename the image and keep screenshots under {IMAGES}")
            continue
        if value.startswith(EXAMPLES):
            continue
        errors.append(f"{value}: put named textual/code/data _example artifacts under {EXAMPLES}")
    return errors


def check(repo, base_ref=None, event_name=None, full=False):
    raw = git_context.run_git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z").stdout
    current = {name for name in raw.decode("utf-8").split("\0") if name and (repo / name).is_file()}
    untracked = set(git_context.run_git(repo, "ls-files", "--others", "--exclude-standard", "-z").stdout.decode("utf-8").split("\0"))
    base = None if full else git_context.ensure_base(repo, base_ref, event_name)
    if base is not None:
        changed = set(git_context.run_git(repo, "diff", "--name-only", "-z", "--diff-filter=ACMRT", base, "--").stdout.decode("utf-8").split("\0"))
        if CHECKER not in changed and CHECKER not in untracked:
            current &= changed | untracked
    return placement_errors(current)


def main():
    parser = argparse.ArgumentParser(description="Reserve _example filenames for textual/code/data examples under Docs/examples.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--base-ref")
    parser.add_argument("--event-name")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    errors = check(args.repo_root, args.base_ref, args.event_name, args.all)
    print("FAIL example artifact locations" if errors else "PASS example artifact locations")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Keep maintained documentation/reference image names globally identifiable, and reserve 0.x/1.x for legacy/SAS numbered image series respectively. (ChatGPT-5.6-Sol) -->
from collections import defaultdict
import argparse
from pathlib import Path, PurePosixPath
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
# <!-- custom: git_context supplies run_git so the policy also sees untracked, not-yet-committed images. (Claude Code Sonnet 5.5) -->
import git_context

ROOT = Path(__file__).resolve().parents[4]
LEGACY_IMAGES = "_0_Legacy/Images/"
SAS_IMAGES = "_1_AdvCiv-SAS/Images/"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tga", ".dds", ".ico"}

# <!-- custom: The two Images trees hold maintained screenshots and templates. Civ4 art
# and resources use their runtime layout, and the FPK example preserves its extracted path. (GPT-6.1-Sol) -->
IMAGE_DIRECTORIES = (LEGACY_IMAGES, SAS_IMAGES, "Assets/Art/", "Assets/Res/")
IMAGE_FILE_EXCEPTIONS = {
    "_1_AdvCiv-SAS/Docs/examples/fpk/fpk_tool_extract_example/art/terrain/routes/roads/roadprimitive.dds",
}


def image_paths(paths):
    return sorted({value for value in paths if PurePosixPath(value).suffix.lower() in IMAGE_SUFFIXES})


# <!-- custom: The legacy tree is a subset of the SAS tree, so only legacy-to-SAS direction is checked: each _0_Legacy top-level folder (Docs, Images) and each _0_Legacy/Images subfolder (advisors, sevopedia, ...) must also exist in the SAS tree.
# Legacy/Docs subfolders (AdvCiv, BBAI, ...) are inherited-source folders without SAS counterparts and are deliberately not checked. (Claude Code Sonnet 5.5) -->
def mirror_errors(paths):
    legacy_top = "_0_Legacy/"
    sas_top = "_1_AdvCiv-SAS/"
    errors = []
    def first_folders(prefix):
        result = set()
        for value in paths:
            if value.startswith(prefix):
                parts = value[len(prefix):].split("/")
                if len(parts) > 1:
                    result.add(parts[0])
        return result
    for folder in sorted(first_folders(legacy_top) - first_folders(sas_top)):
        errors.append(f"{legacy_top}{folder}/: legacy folder has no {sas_top}{folder}/ counterpart")
    for folder in sorted(first_folders(LEGACY_IMAGES) - first_folders(SAS_IMAGES)):
        errors.append(f"{LEGACY_IMAGES}{folder}/: legacy image folder has no {SAS_IMAGES}{folder}/ counterpart")
    return errors


def filename_errors(paths):
    images = image_paths(paths)
    errors = mirror_errors(paths)
    by_name = defaultdict(list)
    for value in images:
        if not value.startswith(IMAGE_DIRECTORIES) and value not in IMAGE_FILE_EXCEPTIONS:
            errors.append(f"{value}: image outside allowed locations. Put maintained images in {SAS_IMAGES}")
        if not value.startswith((LEGACY_IMAGES, SAS_IMAGES)):
            continue
        name = PurePosixPath(value).name
        by_name[name.casefold()].append(value)
        if value.startswith(LEGACY_IMAGES) and not name.startswith("0."):
            errors.append(f"{value}: legacy/reference image filenames must use the 0.x namespace")
        if value.startswith(SAS_IMAGES) and name[:1].isdigit() and not name.startswith("1."):
            errors.append(f"{value}: numbered AdvCiv-SAS image filenames must use the 1.x namespace")
    for values in sorted(by_name.values(), key=lambda group: [item.casefold() for item in group]):
        if len(values) > 1:
            errors.append("duplicate maintained image basename: " + " | ".join(values))
    return errors


def check(repo):
    raw = git_context.run_git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z").stdout
    current = [name for name in raw.decode("utf-8").split("\0") if name and (repo / name).is_file()]
    return filename_errors(current)


def main():
    parser = argparse.ArgumentParser(description="Check maintained image namespaces, basename uniqueness and allowed image locations.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.repo_root)
    print("FAIL documentation image filename policy" if errors else "PASS documentation image filename policy")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

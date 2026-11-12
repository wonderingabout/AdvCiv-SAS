#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: The LLM_Helpers README and this folder's README were reordered by hand on 2026-11-10 to follow their folders alphabetically, after both had drifted into an ad hoc order.
# Keeping that order, and the README sections in step with the folders on disk, should not depend on remembering it, so this check reports every place where they differ.
# Modding_Resources/README.md's "Guides in this folder" list makes the same promise about its folder, so it is checked here too. (Claude code Opus 5.5) -->

from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
HELPERS = "LLM_Helpers"
# <!-- custom: outputs/ holds Git-ignored reports and __pycache__ holds bytecode; neither is a folder of helpers. (Claude code Opus 5.5) -->
NOT_FOLDERS = {"outputs", "__pycache__"}
# <!-- custom: context/ holds reference corpora of thousands of files, described as a whole rather than file by file. (Claude code Opus 5.5) -->
UNLISTED_FOLDERS = {"context"}
HELPER_SUFFIXES = {".py", ".json"}
GUIDES = "_1_AdvCiv-SAS/Docs/Modding_Resources"
# <!-- custom: Folders whose helpers are documented only in a guide, so that guide is the one place for their subject.
# On 2026-11-12 the Ghidra setup and pitfalls had been written in the tools table, this README and the EXE patches guide, so a fix to one would have left the others stale.
# For these, every helper (Ghidra's .java scripts included) must be named in the guide, and the README section must stay a pointer: one line linking to the guide and its disclaimer.
# The guide is left out of player downloads while this README ships, so the user wanted the line to say "see" without describing the helpers, and a check so it stays that way. (Claude code Opus 5.5) -->
GUIDE_DOCUMENTED_FOLDERS = {"exe_analysis": (GUIDES + "/README_EXE_Patches.md", "/LICENSE.md#the-games-executable")}
GUIDE_DOCUMENTED_SUFFIXES = HELPER_SUFFIXES | {".java"}
GUIDES_HEADING = "Guides in this folder"


def headings(text):
    # <!-- custom: Yield (line index, level, title) for headings outside fenced code, since bash examples in fences start with # too. (Claude code Opus 5.5) -->
    fence = False
    for index, line in enumerate(text.splitlines()):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        match = re.match(r"^(#{1,6}) (.*)$", line)
        if match and not fence:
            yield index, len(match.group(1)), match.group(2).strip()


def unordered(names, what):
    expected = sorted(names, key=str.lower)
    if names == expected:
        return []
    return ["%s are not in alphabetical order: %s; expected %s" % (what, ", ".join(names), ", ".join(expected))]


def check_helpers(root):
    errors = []
    base = root / HELPERS
    readme_path = base / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for path in sorted(base.iterdir()):
        if path.is_file() and path.name != "README.md":
            errors.append("%s/%s: only README.md belongs directly in %s/; move it into the folder of its job" % (HELPERS, path.name, HELPERS))
    folders = sorted(path.name for path in base.iterdir() if path.is_dir() and path.name not in NOT_FOLDERS)
    found = list(headings(text))
    sections = [(index, title[1:-2]) for index, level, title in found if level == 2 and re.fullmatch(r"`[^`/]+/`", title)]
    names = [name for _, name in sections]
    errors += unordered(names, "%s/README.md folder sections" % HELPERS)
    for name in sorted(set(folders) - set(names)):
        errors.append("%s/%s/ has no `## `%s/`` section in %s/README.md" % (HELPERS, name, name, HELPERS))
    for name in sorted(set(names) - set(folders)):
        errors.append("%s/README.md has a section for %s/, which does not exist" % (HELPERS, name))
    # <!-- custom: Read rows only up to the first subheading after Folders; the before/after tables of earlier names under it also start with a folder in backticks. (Claude code Opus 5.5) -->
    folders_start = next(index for index, level, title in found if level == 2 and title == "Folders")
    folders_end = next(index for index, level, _ in found if index > folders_start and level <= 3)
    table = [match.group(1) for match in re.finditer(r"^\| `([^`/]+)/` \|", "\n".join(lines[folders_start:folders_end]), re.MULTILINE)]
    errors += unordered(table, "%s/README.md Folders table rows" % HELPERS)
    if sorted(table) != folders:
        errors.append("%s/README.md Folders table lists %s; the folders are %s" % (HELPERS, ", ".join(sorted(table)), ", ".join(folders)))
    h2 = [index for index, level, _ in found if level == 2] + [len(lines)]
    for index, name in sections:
        if name in UNLISTED_FOLDERS or name not in folders:
            continue
        end = next(i for i in h2 if i > index)
        section = "\n".join(lines[index:end])
        if name in GUIDE_DOCUMENTED_FOLDERS:
            errors += check_guide_documented(root, name, index, end, found, section)
            continue
        for path in sorted((base / name).rglob("*")):
            if path.suffix in HELPER_SUFFIXES and "__pycache__" not in path.parts and path.name not in section:
                errors.append("%s: not described in the `%s/` section of %s/README.md" % (path.relative_to(root).as_posix(), name, HELPERS))
    return errors


def check_guide_documented(root, name, start, end, found, section):
    errors = []
    guide, disclaimer = GUIDE_DOCUMENTED_FOLDERS[name]
    where = "the `%s/` section of %s/README.md" % (name, HELPERS)
    body = [line for line in section.splitlines()[1:] if line.strip()]
    if len(body) != 1:
        errors.append("%s has %d lines; keep it the single line pointing to %s and its disclaimer, since its helpers are documented only there" % (where, len(body), guide))
    for target in ("/" + guide, disclaimer):
        if target not in section:
            errors.append("%s must link to %s" % (where, target))
    for index, _, title in found:
        if start < index < end:
            errors.append("%s has subsection %r; its helpers are documented only in %s, so keep the section a short pointer" % (where, title, guide))
    guide_path = root / guide
    if not guide_path.is_file():
        return errors + ["%s documents %s/%s/ but does not exist" % (guide, HELPERS, name)]
    text = guide_path.read_text(encoding="utf-8")
    for path in sorted((root / HELPERS / name).rglob("*")):
        if path.suffix in GUIDE_DOCUMENTED_SUFFIXES and "__pycache__" not in path.parts and path.name not in text:
            errors.append("%s: not described in %s, where %s/%s/ is documented" % (path.relative_to(root).as_posix(), guide, HELPERS, name))
    return errors


def check_workflows(root):
    errors = []
    readme = root / ".github" / "workflows" / "README.md"
    text = readme.read_text(encoding="utf-8")
    found = list(headings(text))
    start = next(index for index, level, title in found if level == 2 and title == "Helper reference")
    end = next((index for index, level, _ in found if level == 2 and index > start), len(text.splitlines()))
    subjects = [(index, title) for index, level, title in found if level == 3 and start < index < end]
    errors += unordered([title for _, title in subjects], ".github/workflows/README.md helper reference subjects")
    bounds = [index for index, _ in subjects] + [end]
    for (index, title), stop in zip(subjects, bounds[1:]):
        scripts = [Path(re.search(r"`([^`]+)`", heading).group(1)).name for i, level, heading in found if level == 4 and index < i < stop and heading.startswith("`")]
        errors += unordered(scripts, ".github/workflows/README.md %s helpers" % title)
    areas = [match.group(1) for match in re.finditer(r"^\| `(build/[^`]+/)` \|", text, re.MULTILINE)]
    errors += unordered(areas, ".github/workflows/README.md helper/test areas")
    return errors


def check_guides(root):
    folder = root / GUIDES
    text = (folder / "README.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    found = list(headings(text))
    start = next((index for index, level, title in found if level == 2 and title == GUIDES_HEADING), None)
    if start is None:
        return ["%s/README.md has no `## %s` section" % (GUIDES, GUIDES_HEADING)]
    end = next((index for index, level, _ in found if index > start and level <= 2), len(lines))
    listed = re.findall(r"^- \[[^\]]+\]\(/" + re.escape(GUIDES) + r"/([^)#]+\.md)\)", "\n".join(lines[start:end]), re.MULTILINE)
    guides = sorted(path.name for path in folder.glob("*.md") if path.name != "README.md")
    errors = unordered(listed, "%s/README.md guides" % GUIDES)
    for name in sorted(set(guides) - set(listed)):
        errors.append("%s/%s is not listed under `## %s` in %s/README.md" % (GUIDES, name, GUIDES_HEADING, GUIDES))
    for name in sorted(set(listed) - set(guides)):
        errors.append("%s/README.md lists %s, which is not in that folder" % (GUIDES, name))
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check that folder indexes (the LLM_Helpers, workflow and Modding Resources READMEs) list what their folders hold, in alphabetical order.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check_helpers(args.repo_root) + check_workflows(args.repo_root) + check_guides(args.repo_root)
    print("FAIL folder indexes" if errors else "PASS folder indexes")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

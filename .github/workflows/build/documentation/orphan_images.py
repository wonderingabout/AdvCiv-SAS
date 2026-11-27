#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: markdown_images.py fails on an embed whose image is missing, but not the other way round: an image no doc, JSON or script names went unnoticed.
# A 2026-11-21 scan found 70, 3 SAS screenshots left out of the docs among them; they were embedded, and the legacy shots and font previews got an index, so the check needs no exemptions. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: subprocess lists the files through Git, pathlib reads them, and quote gives a name's %20 spelling as Markdown links write it. (Claude code Opus 5.5) -->
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[4]
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg")
# <!-- custom: Generated corpora and helper outputs quote old file names, so a mention there must not keep a removed image alive. (Claude code Opus 5.5) -->
NON_REFERENCE_PREFIXES = ("LLM_Helpers/context/", "LLM_Helpers/outputs/", "_SNAPSHOT_CONTEXT/", ".git/")
# <!-- custom: Binary formats skipped as reference sources: reading them as text costs time and their bytes can hold a name by chance. (Claude code Opus 5.5) -->
BINARY_SUFFIXES = IMAGE_SUFFIXES + (".dds", ".tga", ".dll", ".pdb", ".exe", ".lib", ".obj", ".nif", ".kf", ".fpk", ".bik", ".mp3", ".wav", ".ogg", ".zip", ".7z", ".civbeyondswordsave", ".chm", ".pdf", ".ttf", ".ico")


def repository_files(root: Path) -> list[str]:
    # <!-- custom: Tracked and untracked-but-not-ignored files, as markdown_structure.py does, so a new image fails before its first commit; Git-free light-source archives fall back to the filesystem. (Claude code Opus 5.5) -->
    if (root / ".git").exists():
        result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root, check=True, stdout=subprocess.PIPE)
        names = result.stdout.decode("utf-8").split("\0")
    else:
        names = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    return sorted({name for name in names if name and not name.startswith(NON_REFERENCE_PREFIXES) and (root / name).is_file()})


def orphan_images(root: Path, names: list[str]) -> list[str]:
    images = [name for name in names if name.lower().endswith(IMAGE_SUFFIXES)]
    corpus = []
    for name in names:
        if name.lower().endswith(BINARY_SUFFIXES):
            continue
        data = (root / name).read_bytes()
        if b"\0" in data:
            continue
        corpus.append((name, data.decode("utf-8", errors="ignore")))
    orphans = []
    for image in images:
        # <!-- custom: Match the file name rather than its path: scripts and tables name an image without its folder, and Markdown spells spaces as %20. (Claude code Opus 5.5) -->
        filename = image.rsplit("/", 1)[-1]
        spellings = {filename, quote(filename, safe="()&,+'!")}
        if not any(other != image and any(spelling in text for spelling in spellings) for other, text in corpus):
            orphans.append(image)
    return orphans


def main() -> int:
    names = repository_files(ROOT)
    orphans = orphan_images(ROOT, names)
    image_count = sum(1 for name in names if name.lower().endswith(IMAGE_SUFFIXES))
    if orphans:
        print("Images that no doc, JSON or script names; embed or list each where it belongs, or remove it:")
        for orphan in orphans:
            print(f"  {orphan}")
        print(f"\n{len(orphans)} of {image_count} image(s) unreferenced.")
        return 1
    print(f"Orphan images OK: all {image_count} image(s) are named somewhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

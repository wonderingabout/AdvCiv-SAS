#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout (see Authors in root README.md)
#
# <!-- custom: Create a timestamped Civ4 mod light source ZIP for quick local/LLM review handoffs.
# Store repo-relative paths with ZIP_STORED/no compression so creation is fast and the archive remains easy to inspect.
# Refined with ChatGPT-5.5 and Codex. -->
# Create a timestamped, no-compression light source ZIP for a Civ4 mod.

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator
from zipfile import ZIP_STORED, ZipFile


ASSET_SUBDIRS = (
    "Assets/Python",
    "Assets/Config",
    "Assets/res",
    "Assets/XML",
)

ROOT_SUBDIRS = (
    "PrivateMaps",
    ".claude",
    ".github",
    "Long_Comments",
    "_0_Common_Docs",
    "LLM_Helpers",
    "Resource",
    "Settings",
    ".vscode",
)

EXTRA_SUBDIRS = (
    "_1_AdvCiv-SAS/Docs",
    "_1_AdvCiv-SAS/git_logs",
)

DLL_TOP_LEVEL_DIR = "CvGameCoreDLL"
DLL_PROJECT_DIR = "CvGameCoreDLL/Project"
DLL_PROJECT_MAX_BYTES = 1 * 1024 * 1024
DEFAULT_OUTPUT_DIR = "."
DEFAULT_MOD_NAME = "UnspecifiedModName"
ARCHIVE_LABEL = "light_source"
DEFAULT_ARCHIVE_PREFIX = None
GENERATED_ARCHIVE_MARKER = "_light_source_"

# Skip Python bytecode/cache folders anywhere in the tree. They are generated,
# can be heavy, and confuse LLM/code-agent reviews with stale duplicate code.
SKIP_DIR_NAMES = {".git", "__pycache__"}

# Skip whole folders that are included through a parent folder but do not help
# compact LLM/code-agent review. Civ4 cursor assets are visual/binary UI files
# and are usually noise for source/debugging tasks.
SKIP_REL_DIRS = {"assets/res/cursors"}

# Skip generated/binary payloads that are too heavy or not useful for compact
# ChatGPT/code-agent source review. FPK art packs and DLL binaries should be
# shared separately only when specifically needed.
SKIP_SUFFIXES = {".pyc", ".pyo", ".dll", ".fpk", ".tga"}

# Visual Studio database files can be very large and are regenerated locally.
# Other small lone project files are useful enough to keep.
DLL_PROJECT_SKIP_SUFFIXES = {".sdf"}

# Skip original manuals because converted text copies are easier to grep and
# enough for compact LLM/code-agent review.
SKIP_FILE_NAMES = {"manual.pdf", "manual.odt"}

# Do not exclude common readable image files globally. Small previews/screenshots
# can be useful for LLM review, e.g. GameFont previews. Avoid heavy art/image
# folders by not adding those folders to the include lists instead. TGA is
# excluded above because ChatGPT/code-agent review generally cannot inspect it
# usefully in this compact source archive.


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a timestamped Civ4 mod light source ZIP with no compression."
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to the mod/repo root. Defaults to auto-detection from cwd/script path.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Output directory, relative to the mod/repo root unless absolute. "
            f"Default: {DEFAULT_OUTPUT_DIR}"
        ),
    )
    parser.add_argument(
        "--mod-name",
        default=None,
        help=(
            "Archive filename mod name. Defaults to the detected mod folder name, "
            f"with an {DEFAULT_MOD_NAME} fallback."
        ),
    )
    parser.add_argument(
        "--prefix",
        default=DEFAULT_ARCHIVE_PREFIX,
        help=(
            "Full archive filename prefix before the timestamp. Defaults to "
            "<mod-name>_light_source. Use this only for manual labels or old naming."
        ),
    )
    parser.add_argument(
        "--include-helper-outputs",
        action="store_true",
        help="Include LLM_Helpers/outputs. By default it is skipped to avoid bundling generated reports/ZIPs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be archived without writing the ZIP.",
    )
    return parser.parse_args()


def find_repo_root(repo_root_arg: str | None) -> Path:
    if repo_root_arg:
        root = Path(repo_root_arg).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit(f"Repo root does not exist or is not a directory: {root}")
        return root

    candidates: list[Path] = []
    try:
        candidates.append(Path.cwd().resolve())
    except OSError:
        pass

    script_path = Path(__file__).resolve()
    candidates.extend([script_path.parent, *script_path.parents])

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "Assets").is_dir() or (candidate / DLL_TOP_LEVEL_DIR).is_dir():
            return candidate

    raise SystemExit("Could not auto-detect mod/repo root. Run from the mod root or pass --repo-root.")


def safe_filename_part(text: str | None, fallback: str) -> str:
    if text is None:
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip()).strip("._-")
    return cleaned or fallback


def derive_mod_name(repo_root: Path, mod_name_arg: str | None) -> str:
    """Return the filename-safe mod name used in the output archive name."""
    # Normally this comes from the mod folder itself, e.g. .../Mods/AdvCiv-SAS
    # -> AdvCiv-SAS. --mod-name exists only for unusual folder names or manual labels.
    return safe_filename_part(mod_name_arg or repo_root.name, DEFAULT_MOD_NAME)


def archive_prefix(mod_name: str, prefix_arg: str | None) -> str:
    """Return the filename-safe archive prefix before the timestamp."""
    if prefix_arg:
        return safe_filename_part(prefix_arg, f"{mod_name}_{ARCHIVE_LABEL}")
    return f"{mod_name}_{ARCHIVE_LABEL}"


def output_path(repo_root: Path, output_dir_arg: str, prefix: str, create_dir: bool) -> Path:
    out_dir = Path(output_dir_arg).expanduser()
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir
    if create_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    return out_dir / f"{prefix}_{stamp}.zip"


def rel_for_message(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def should_skip_dir(path: Path, repo_root: Path, include_helper_outputs: bool) -> bool:
    if path.name in SKIP_DIR_NAMES:
        return True
    rel = rel_for_message(path, repo_root).lower()
    if rel in SKIP_REL_DIRS:
        return True
    if not include_helper_outputs:
        if rel == "llm_helpers/outputs" or rel.startswith("llm_helpers/outputs/"):
            return True
    return False


def should_skip_file(path: Path) -> bool:
    name = path.name.lower()
    if name in SKIP_FILE_NAMES:
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    # Avoid recursively bundling earlier archives created by this script when
    # the default output folder is the mod root.
    if path.suffix.lower() == ".zip" and GENERATED_ARCHIVE_MARKER in name:
        return True
    return False


def iter_tree_files(root: Path, repo_root: Path, include_helper_outputs: bool) -> Iterator[Path]:
    if not root.exists():
        print(f"Warning: missing folder skipped: {rel_for_message(root, repo_root)}")
        return
    if not root.is_dir():
        print(f"Warning: not a folder, skipped: {rel_for_message(root, repo_root)}")
        return

    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            if should_skip_dir(child, repo_root, include_helper_outputs):
                continue
            yield from iter_tree_files(child, repo_root, include_helper_outputs)
        elif child.is_file() and not should_skip_file(child):
            yield child


def iter_root_files(repo_root: Path) -> Iterator[Path]:
    for child in sorted(repo_root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_file() and not should_skip_file(child):
            yield child


def iter_dll_top_level_files(repo_root: Path) -> Iterator[Path]:
    dll_dir = repo_root / DLL_TOP_LEVEL_DIR
    if not dll_dir.is_dir():
        print(f"Warning: missing folder skipped: {DLL_TOP_LEVEL_DIR}")
        return
    for child in sorted(dll_dir.iterdir(), key=lambda p: p.name.lower()):
        if child.is_file() and not should_skip_file(child):
            yield child


def iter_dll_project_top_level_files(repo_root: Path) -> Iterator[Path]:
    project_dir = repo_root / DLL_PROJECT_DIR
    if not project_dir.is_dir():
        print(f"Warning: missing folder skipped: {DLL_PROJECT_DIR}")
        return
    for child in sorted(project_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_file() or should_skip_file(child):
            continue
        if child.suffix.lower() in DLL_PROJECT_SKIP_SUFFIXES:
            continue
        size = child.stat().st_size
        if size >= DLL_PROJECT_MAX_BYTES:
            print(
                "Warning: DLL project file over 1 MB skipped: "
                f"{rel_for_message(child, repo_root)} ({size:,} bytes)"
            )
            continue
        yield child


def collect_files(repo_root: Path, include_helper_outputs: bool) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()

    def add(paths: Iterable[Path]) -> None:
        for path in paths:
            rel = path.relative_to(repo_root).as_posix()
            if rel not in seen:
                seen.add(rel)
                files.append(path)

    add(iter_root_files(repo_root))

    for rel_dir in ASSET_SUBDIRS:
        add(iter_tree_files(repo_root / rel_dir, repo_root, include_helper_outputs))

    for rel_dir in ROOT_SUBDIRS:
        add(iter_tree_files(repo_root / rel_dir, repo_root, include_helper_outputs))

    add(iter_dll_top_level_files(repo_root))
    add(iter_dll_project_top_level_files(repo_root))

    for rel_dir in EXTRA_SUBDIRS:
        add(iter_tree_files(repo_root / rel_dir, repo_root, include_helper_outputs))

    return sorted(files, key=lambda p: p.relative_to(repo_root).as_posix().lower())


def write_zip(zip_path: Path, repo_root: Path, files: Iterable[Path]) -> int:
    count = 0
    temp_path = zip_path.with_suffix(zip_path.suffix + ".tmp")
    if temp_path.exists():
        temp_path.unlink()

    with ZipFile(temp_path, "w", compression=ZIP_STORED, allowZip64=True) as archive:
        for path in files:
            rel = path.relative_to(repo_root).as_posix()
            archive.write(path, rel)
            count += 1

    temp_path.replace(zip_path)
    return count


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(args.repo_root)
    mod_name = derive_mod_name(repo_root, args.mod_name)
    prefix = archive_prefix(mod_name, args.prefix)
    zip_path = output_path(repo_root, args.output_dir, prefix, not args.dry_run)
    files = collect_files(repo_root, args.include_helper_outputs)
    total_bytes = sum(path.stat().st_size for path in files)

    print(f"Repo root: {repo_root}")
    print(f"Mod name:  {mod_name}")
    print(f"Prefix:    {prefix}")
    print(f"Archive:   {zip_path}")
    print(f"Files:     {len(files)}")
    print(f"Size:      {total_bytes:,} bytes before ZIP container overhead")
    print("Mode:      ZIP_STORED / no compression")

    if args.dry_run:
        for path in files:
            print(path.relative_to(repo_root).as_posix())
        print("Dry run only; no archive written.")
        return 0

    count = write_zip(zip_path, repo_root, files)
    print(f"Wrote:     {count} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

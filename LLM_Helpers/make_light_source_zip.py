#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout (see Authors in root README.md)
#
# Create a timestamped Civ4 mod light source ZIP for quick local/LLM review handoffs.
# Store repo-relative paths and use ZIP_DEFLATED by default so adding selected screenshot folders stays reasonably uploadable.
# Refined with ChatGPT-5.5, ChatGPT-5.6-Sol, and Codex.
# Create a timestamped light source ZIP for a Civ4 mod.

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Iterable, Iterator
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


# <!-- custom: Keep Git's canonical `Assets/Res` casing here even on Windows, whose case-insensitive filesystem may also display/accept `Assets/res`; GitHub/Linux paths and CI are case-sensitive. (ChatGPT-5.6-Sol) -->
ASSET_SUBDIRS = (
    "Assets/Python",
    "Assets/Config",
    "Assets/Res",
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
    "_1_AdvCiv-SAS/SASGameRecord_log",
)

# Optional screenshot-folder whitelist for visual LLM/code-agent context, e.g. advisors, main menu, Sevopedia, rendered SASGameRecord map text, and common UI.
# Keep this explicit instead of including all image folders so broad image additions do not silently bloat the archive.
IMAGE_SUBDIRS = (
    "_1_AdvCiv-SAS/Images/advisors",
    "_1_AdvCiv-SAS/Images/main_menu",
    "_1_AdvCiv-SAS/Images/SASGameRecord_map_text",
    "_1_AdvCiv-SAS/Images/sevopedia",
    "_1_AdvCiv-SAS/Images/ui_other",
)

DLL_TOP_LEVEL_DIR = "CvGameCoreDLL"
DLL_PROJECT_DIR = "CvGameCoreDLL/Project"
DLL_PROJECT_MAX_BYTES = 1 * 1024 * 1024
DEFAULT_OUTPUT_DIR = "."
DEFAULT_MOD_NAME = "UnspecifiedModName"
ARCHIVE_LABEL = "light_source"
DEFAULT_ARCHIVE_PREFIX = None
DEFAULT_COMPRESSION_LEVEL = 6
GENERATED_ARCHIVE_MARKER = "_light_source_"
# Archive-only snapshot helpers so ZIP-only reviewers can distinguish repository files from
# generated context and can recover committed/staged/unstaged changes without `.git`.
GENERATED_CONTEXT_DIR = "_SNAPSHOT_CONTEXT"
GENERATED_CONTEXT_README_NAME = f"{GENERATED_CONTEXT_DIR}/README.txt"
GENERATED_GIT_MANIFEST_NAME = f"{GENERATED_CONTEXT_DIR}/repo_file_manifest.txt"
GENERATED_GIT_STATE_NAME = f"{GENERATED_CONTEXT_DIR}/git_repository_state.txt"
GENERATED_GIT_IGNORED_TREE_NAME = f"{GENERATED_CONTEXT_DIR}/git_ignored_paths_tree.txt"
GENERATED_STAGED_DIFF_NAME = f"{GENERATED_CONTEXT_DIR}/staged_changes_no_eol.diff"
GENERATED_UNSTAGED_DIFF_NAME = f"{GENERATED_CONTEXT_DIR}/unstaged_changes_no_eol.diff"
GENERATED_INCREMENTAL_GIT_LOG_NAME = f"{GENERATED_CONTEXT_DIR}/git_log_since_tracked_advciv_sas_log.txt"
TRACKED_ADVCIV_SAS_GIT_LOG = "_1_AdvCiv-SAS/git_logs/git_log_anonymized_email_003_AdvCiv-SAS.txt"

# Skip Python bytecode/cache folders anywhere in the tree.
# They are generated, can be heavy, and confuse LLM/code-agent reviews with stale duplicate code.
SKIP_DIR_NAMES = {".git", "__pycache__"}

# Skip whole folders that are included through a parent folder but do not help compact LLM/code-agent review.
# Civ4 cursor assets are visual/binary UI files and are usually noise for source/debugging tasks.
SKIP_REL_DIRS = {"assets/res/cursors"}

# Skip generated/binary payloads that are too heavy or not useful for compact ChatGPT/code-agent source review.
# FPK art packs and DLL binaries should be shared separately only when specifically needed.
SKIP_SUFFIXES = {".pyc", ".pyo", ".dll", ".fpk", ".tga"}

# Preserve this exact build-check/workflow folder in light-source archives, including any current contents.
# It is intentionally exported even though release archives omit build temp files.
PRESERVED_LIGHT_SOURCE_TEMP_DIR = "CvGameCoreDLL/Project/temp_files"

# Visual Studio database files can be very large and are regenerated locally.
# Other small lone project files are useful enough to keep.
DLL_PROJECT_SKIP_SUFFIXES = {".sdf"}

# Skip original manuals because converted text copies are easier to grep and enough for compact LLM/code-agent review.
SKIP_FILE_NAMES = {"manual.pdf", "manual.odt"}

# Do not exclude common readable image files globally.
# Small previews/screenshots can be useful for LLM review, e.g. GameFont previews.
# Avoid heavy art/image folders by not adding those folders to the include lists instead.
# TGA is excluded above because ChatGPT/code-agent review generally cannot inspect it usefully in this compact source archive.


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a timestamped Civ4 mod light source ZIP."
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
        "--compression-level",
        type=int,
        default=DEFAULT_COMPRESSION_LEVEL,
        choices=range(0, 10),
        metavar="0-9",
        help=(
            "ZIP_DEFLATED compression level. Default: "
            f"{DEFAULT_COMPRESSION_LEVEL}. Use 0 for ZIP_STORED / no compression."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be archived without writing the ZIP.",
    )
    parser.add_argument(
        "--no-duration",
        action="store_true",
        help="Do not print ZIP write duration. Useful when stable/deterministic-looking command output is preferred.",
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


def run_git(repo_root: Path, *args: str) -> tuple[str | None, str | None]:
    """Run Git at repo_root and return stdout or a concise error."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        return None, str(exc)

    if result.returncode != 0:
        error = result.stderr.strip() or f"git exited with status {result.returncode}"
        return None, error
    return result.stdout, None


def build_git_manifest(repo_root: Path) -> str:
    """Build an archive-only inventory of the local Git tracked file tree."""
    tracked_raw, error = run_git(repo_root, "ls-files", "-z")
    if tracked_raw is None:
        return (
            "# Local Git tracked-file manifest\n"
            "# Generated automatically by LLM_Helpers/make_light_source_zip.py.\n"
            f"# This helper exists only inside {GENERATED_CONTEXT_DIR}/ in the light-source ZIP; it is not a repository file.\n"
            "# Git tracked-file metadata was unavailable while creating this archive.\n\n"
            f"Git error: {error}\n"
        )

    tracked = sorted(path for path in tracked_raw.split("\0") if path)
    lines = [
        "# Local Git tracked-file manifest",
        "# Generated automatically by LLM_Helpers/make_light_source_zip.py.",
        f"# This helper exists only inside {GENERATED_CONTEXT_DIR}/ in the light-source ZIP; it is not a repository file.",
        "# The light archive intentionally omits many tracked assets/binaries. Use this manifest",
        "# to distinguish 'not included in this ZIP' from 'not present in the local Git repository'.",
        "# Tracked paths preserve Git's canonical path spelling/casing.",
        "# Untracked paths are intentionally not enumerated; selected untracked source files can",
        "# still be present normally in the ZIP, without exposing unrelated local filenames here.",
        "",
        f"Tracked files: {len(tracked)}",
        "",
        "[TRACKED FILES - git ls-files]",
        *tracked,
    ]
    return "\n".join(lines) + "\n"


def build_git_repository_state(repo_root: Path, selected_files: Iterable[Path]) -> str:
    """Build compact repository, upstream, tracked-worktree, and selected-untracked state."""
    branch_raw, branch_error = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    head_raw, head_error = run_git(repo_root, "rev-parse", "HEAD")
    count_raw, count_error = run_git(repo_root, "rev-list", "--count", "HEAD")
    upstream_raw, upstream_error = run_git(
        repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
    )
    ahead_behind_raw, ahead_behind_error = run_git(
        repo_root, "rev-list", "--left-right", "--count", "HEAD...@{u}"
    )
    status_raw, status_error = run_git(repo_root, "status", "--short", "--untracked-files=no")
    tracked_raw, tracked_error = run_git(repo_root, "ls-files", "-z")

    if branch_raw is None and head_raw is None and status_raw is None:
        error = branch_error or head_error or status_error or "Git metadata unavailable"
        return (
            "# Local Git repository state\n"
            "# Generated automatically by LLM_Helpers/make_light_source_zip.py.\n"
            f"# This helper exists only inside {GENERATED_CONTEXT_DIR}/ in the light-source ZIP; it is not a repository file.\n\n"
            f"Git error: {error}\n"
        )

    branch = branch_raw.strip() if branch_raw else "unknown"
    head = head_raw.strip() if head_raw else "unknown"
    commit_count = count_raw.strip() if count_raw else f"unknown ({count_error})"
    upstream = upstream_raw.strip() if upstream_raw else None
    ahead = behind = None
    if ahead_behind_raw:
        parts = ahead_behind_raw.split()
        if len(parts) >= 2:
            ahead, behind = parts[0], parts[1]

    selected_untracked: list[str] = []
    if tracked_raw is not None:
        tracked = {path for path in tracked_raw.split("\0") if path}
        selected_untracked = sorted(
            path.relative_to(repo_root).as_posix()
            for path in selected_files
            if path.relative_to(repo_root).as_posix() not in tracked
        )

    lines = [
        "# Local Git repository state",
        "# Generated automatically by LLM_Helpers/make_light_source_zip.py.",
        f"# This helper exists only inside {GENERATED_CONTEXT_DIR}/ in the light-source ZIP; it is not a repository file.",
        "# Upstream/ahead-behind values use the locally known upstream ref and can be stale until git fetch.",
        "# AdvCiv-SAS commonly uses the total commit count as its practical version number in documentation",
        "# (for example, 'requires AdvCiv-SAS X+'); HEAD remains the exact source-state identifier.",
        "# Short-status format uses two columns: X = index/staged state, Y = working-tree/unstaged state.",
        "# Examples: 'M ' = staged modification, ' M' = unstaged modification, 'MM' = staged and modified again.",
        "# General untracked paths are intentionally omitted; only untracked files already selected for this ZIP are listed below.",
        "",
        f"Branch: {branch}",
        f"HEAD: {head}",
        f"Commit count: {commit_count}",
    ]
    if upstream:
        lines.append(f"Upstream: {upstream}")
        if ahead is not None and behind is not None:
            lines.append(f"Ahead/behind upstream: {ahead} / {behind}")
        elif ahead_behind_error:
            lines.append(f"Ahead/behind upstream: unavailable ({ahead_behind_error})")
    else:
        lines.append(f"Upstream: none ({upstream_error or 'not configured'})")

    lines.extend(["", "[TRACKED WORKING TREE STATUS - git status --short --untracked-files=no]"])
    if status_raw is not None:
        lines.extend(status_raw.rstrip().splitlines() or ["(clean)"])
    else:
        lines.append(f"(unavailable: {status_error})")

    lines.extend(["", "[SELECTED ZIP FILES NOT TRACKED BY GIT]"])
    if tracked_raw is None:
        lines.append(f"(unavailable: {tracked_error})")
    else:
        lines.extend(selected_untracked or ["(none)"])
    return "\n".join(lines) + "\n"


def render_path_tree(paths: Iterable[str]) -> list[str]:
    """Render slash-separated paths as a compact ASCII tree."""
    root: dict[str, dict] = {}
    directory_paths: set[str] = set()
    for raw_path in paths:
        is_directory = raw_path.endswith("/")
        clean_path = raw_path.rstrip("/")
        if not clean_path:
            continue
        parts = [part for part in clean_path.split("/") if part]
        node = root
        built: list[str] = []
        for part in parts:
            built.append(part)
            node = node.setdefault(part, {})
        if is_directory:
            directory_paths.add("/".join(built))

    lines = ["."]

    def walk(node: dict[str, dict], prefix: str, parent_parts: list[str]) -> None:
        names = sorted(node, key=str.lower)
        for index, name in enumerate(names):
            is_last = index == len(names) - 1
            current_parts = [*parent_parts, name]
            current_path = "/".join(current_parts)
            suffix = "/" if current_path in directory_paths else ""
            lines.append(prefix + ("`-- " if is_last else "|-- ") + name + suffix)
            children = node[name]
            if children:
                walk(children, prefix + ("    " if is_last else "|   "), current_parts)

    walk(root, "", [])
    return lines


def build_git_ignored_paths_tree(repo_root: Path) -> str:
    """Build a compact tree of paths ignored by the effective local Git ignore rules."""
    ignored_raw, error = run_git(
        repo_root,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "--directory",
        "-z",
    )
    lines = [
        "# Local Git ignored-path tree",
        "# Generated automatically by LLM_Helpers/make_light_source_zip.py.",
        f"# This helper exists only inside {GENERATED_CONTEXT_DIR}/ in the light-source ZIP; it is not a repository file.",
        "# Uses Git's effective standard ignore rules. Entire ignored directories can be collapsed to one entry,",
        "# which keeps this useful as context without enumerating every generated/build file underneath them.",
        "# This complements repo_file_manifest.txt: ignored local paths are neither tracked paths nor necessarily ZIP contents.",
        "",
    ]
    if ignored_raw is None:
        lines.append(f"Git ignored-path metadata unavailable: {error}")
        return "\n".join(lines) + "\n"

    ignored_paths = sorted(path for path in ignored_raw.split("\0") if path)
    lines.append(f"Ignored entries: {len(ignored_paths)}")
    lines.append("")
    lines.append("[IGNORED PATHS - git ls-files --others --ignored --exclude-standard --directory]")
    lines.extend(render_path_tree(ignored_paths) if ignored_paths else ["(none)"])
    return "\n".join(lines) + "\n"

def build_git_diff(repo_root: Path, cached: bool) -> bytes:
    """Return a raw review diff while ignoring line-ending/trailing-EOL-only noise."""
    args = ["diff"]
    if cached:
        args.append("--cached")
    args.extend(
        [
            "--no-ext-diff",
            "--no-color",
            "--ignore-space-at-eol",
            "--ignore-cr-at-eol",
            "--",
        ]
    )
    raw, error = run_git(repo_root, *args)
    if raw is None:
        # Keep archive creation useful even when the supplied folder is not a Git checkout.
        return f"# Git diff unavailable: {error}\n".encode("utf-8")
    return raw.encode("utf-8")


def latest_commit_in_tracked_git_log(repo_root: Path) -> tuple[str | None, str | None]:
    """Return the newest commit already recorded in the tracked AdvCiv-SAS Git log."""
    log_path = repo_root / TRACKED_ADVCIV_SAS_GIT_LOG
    if not log_path.is_file():
        return None, f"tracked Git log not found: {TRACKED_ADVCIV_SAS_GIT_LOG}"
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, str(exc)
    match = re.search(r"(?m)^commit ([0-9a-fA-F]{40})\s*$", text)
    if not match:
        return None, f"no full commit hash found in {TRACKED_ADVCIV_SAS_GIT_LOG}"
    return match.group(1).lower(), None


def build_incremental_git_log(repo_root: Path) -> str:
    """Build compact history from the tracked SAS Git-log boundary through this snapshot's HEAD."""
    base_commit, base_error = latest_commit_in_tracked_git_log(repo_root)
    head_raw, head_error = run_git(repo_root, "rev-parse", "HEAD")
    head_commit = head_raw.strip() if head_raw else None

    lines = [
        "# Incremental AdvCiv-SAS Git history for this light-source snapshot",
        "# Generated automatically by LLM_Helpers/make_light_source_zip.py.",
        f"# Tracked history file: {TRACKED_ADVCIV_SAS_GIT_LOG}",
        "# This archive-only file fills the gap after that tracked history through snapshot HEAD.",
        "# Unlike the tracked AdvCiv-SAS Git log (newest -> oldest), this generated gap is",
        "# chronological (oldest -> newest), so snapshot HEAD is the final commit below.",
        "# It lists every intervening commit message without duplicating potentially huge source/XML patches.",
        "# Detailed commit messages can preserve implemented notes removed later from the temporary untracked changes.md.",
        "# Author email addresses are intentionally hidden.",
        "",
    ]

    if base_commit is None:
        lines.append(f"Unable to determine tracked-log boundary: {base_error}")
        return "\n".join(lines) + "\n"
    if head_commit is None:
        lines.append(f"Unable to determine snapshot HEAD: {head_error}")
        return "\n".join(lines) + "\n"

    base_resolved_raw, base_resolved_error = run_git(repo_root, "rev-parse", base_commit)
    if base_resolved_raw is None:
        lines.append(f"Tracked-log boundary commit is unavailable in this checkout: {base_commit}")
        lines.append(f"Git error: {base_resolved_error}")
        return "\n".join(lines) + "\n"
    base_resolved = base_resolved_raw.strip()

    merge_base_raw, merge_base_error = run_git(repo_root, "merge-base", base_resolved, head_commit)
    if merge_base_raw is None:
        lines.append(f"Unable to verify tracked-log boundary against HEAD: {merge_base_error}")
        return "\n".join(lines) + "\n"
    if merge_base_raw.strip() != base_resolved:
        lines.append(f"Tracked-log boundary is not an ancestor of snapshot HEAD: {base_resolved}")
        lines.append(f"Snapshot HEAD: {head_commit}")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            f"Tracked-log boundary already recorded: {base_resolved}",
            f"Snapshot HEAD: {head_commit}",
            f"Git range below: {base_resolved}..{head_commit}",
            "Boundary commit is excluded below because it already exists in the tracked Git log.",
            "Order: oldest newer commit -> snapshot HEAD.",
            "",
        ]
    )

    if base_resolved == head_commit:
        lines.append("(No newer committed changes after the tracked Git-log boundary.)")
        return "\n".join(lines) + "\n"

    count_raw, _ = run_git(repo_root, "rev-list", "--count", f"{base_resolved}..{head_commit}")
    if count_raw:
        lines.append(f"Newer commits: {count_raw.strip()}")
        lines.append("")

    log_raw, log_error = run_git(
        repo_root,
        "log",
        "--reverse",
        "--no-patch",
        "--no-color",
        "--pretty=format:commit %H%nAuthor: %an <hidden>%nDate:   %ai%n%n%B",
        f"{base_resolved}..{head_commit}",
    )
    if log_raw is None:
        lines.append(f"Unable to generate incremental Git log: {log_error}")
        return "\n".join(lines) + "\n"

    lines.append("[ALL NEWER COMMITS - MESSAGES | OLDEST -> NEWEST]")
    lines.append(log_raw.rstrip())
    return "\n".join(lines) + "\n"


def build_snapshot_context_readme() -> str:
    """Explain the generated archive-only snapshot context files."""
    return (
        "AdvCiv-SAS light-source snapshot context\n"
        "========================================\n\n"
        "This folder is generated only inside the light-source ZIP. It is not part of the repository.\n\n"
        "repo_file_manifest.txt\n"
        "  Canonical tracked Git paths from git ls-files. This is only the repository file inventory.\n\n"
        "git_repository_state.txt\n"
        "  Current branch/HEAD, commit count, locally known upstream/ahead-behind state, tracked\n"
        "  git status --short output, and ZIP-selected files that are not tracked by Git. X is\n"
        "  staged/index state; Y is unstaged/working-tree state (for example M<space>, <space>M, and MM).\n"
        "  AdvCiv-SAS commonly uses Commit count as its practical version number (for example X in\n"
        "  'requires AdvCiv-SAS X+'); HEAD is the exact source-state identifier.\n\n"
        "git_ignored_paths_tree.txt\n"
        "  Compact ASCII tree of paths ignored by Git's effective standard ignore rules. Entire ignored\n"
        "  directories can be collapsed to one entry, so this adds useful local context without listing\n"
        "  every generated/build file beneath them.\n\n"
        "staged_changes_no_eol.diff\n"
        "  Raw staged diff (HEAD -> index), with end-of-line whitespace/CR-only noise ignored.\n"
        "  An empty file means there were no staged tracked changes.\n\n"
        "unstaged_changes_no_eol.diff\n"
        "  Raw unstaged diff (index -> working tree), with end-of-line whitespace/CR-only noise ignored.\n"
        "  An empty file means there were no unstaged tracked changes.\n\n"
        "git_log_since_tracked_advciv_sas_log.txt\n"
        f"  Commit messages after the newest commit already recorded in {TRACKED_ADVCIV_SAS_GIT_LOG}\n"
        "  through this snapshot's HEAD. The boundary commit is not duplicated. Unlike the tracked\n"
        "  AdvCiv-SAS Git log (newest -> oldest), this generated gap is ordered oldest -> newest,\n"
        "  so snapshot HEAD appears at the bottom. Detailed commit messages can preserve implemented\n"
        "  notes that were later removed from the temporary untracked changes.md.\n"
    )


def build_generated_context(repo_root: Path, selected_files: Iterable[Path]) -> dict[str, bytes]:
    """Return every archive-only context file keyed by ZIP-relative path."""
    selected_files = list(selected_files)
    return {
        GENERATED_CONTEXT_README_NAME: build_snapshot_context_readme().encode("utf-8"),
        GENERATED_GIT_MANIFEST_NAME: build_git_manifest(repo_root).encode("utf-8"),
        GENERATED_GIT_STATE_NAME: build_git_repository_state(repo_root, selected_files).encode("utf-8"),
        GENERATED_GIT_IGNORED_TREE_NAME: build_git_ignored_paths_tree(repo_root).encode("utf-8"),
        GENERATED_STAGED_DIFF_NAME: build_git_diff(repo_root, cached=True),
        GENERATED_UNSTAGED_DIFF_NAME: build_git_diff(repo_root, cached=False),
        GENERATED_INCREMENTAL_GIT_LOG_NAME: build_incremental_git_log(repo_root).encode("utf-8"),
    }


def should_skip_dir(path: Path, repo_root: Path) -> bool:
    if path.name in SKIP_DIR_NAMES:
        return True
    rel = rel_for_message(path, repo_root).lower()
    if rel in SKIP_REL_DIRS:
        return True
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


def iter_tree_files(root: Path, repo_root: Path) -> Iterator[Path]:
    if not root.exists():
        print(f"Warning: missing folder skipped: {rel_for_message(root, repo_root)}")
        return
    if not root.is_dir():
        print(f"Warning: not a folder, skipped: {rel_for_message(root, repo_root)}")
        return

    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            if should_skip_dir(child, repo_root):
                continue
            yield from iter_tree_files(child, repo_root)
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


def iter_preserved_temp_files(repo_root: Path) -> Iterator[Path]:
    temp_dir = repo_root / PRESERVED_LIGHT_SOURCE_TEMP_DIR
    if not temp_dir.is_dir():
        print(f"Warning: missing folder skipped: {PRESERVED_LIGHT_SOURCE_TEMP_DIR}")
        return
    for path in sorted(temp_dir.rglob("*"), key=lambda p: p.relative_to(repo_root).as_posix().lower()):
        if path.is_file():
            yield path


def collect_files(repo_root: Path) -> list[Path]:
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
        add(iter_tree_files(repo_root / rel_dir, repo_root))

    for rel_dir in ROOT_SUBDIRS:
        add(iter_tree_files(repo_root / rel_dir, repo_root))

    add(iter_dll_top_level_files(repo_root))
    add(iter_dll_project_top_level_files(repo_root))
    add(iter_preserved_temp_files(repo_root))

    for rel_dir in EXTRA_SUBDIRS:
        add(iter_tree_files(repo_root / rel_dir, repo_root))

    for rel_dir in IMAGE_SUBDIRS:
        add(iter_tree_files(repo_root / rel_dir, repo_root))

    return sorted(files, key=lambda p: p.relative_to(repo_root).as_posix().lower())


def write_zip(zip_path: Path, repo_root: Path, files: Iterable[Path], compression_level: int, generated_context: dict[str, bytes]) -> int:
    count = 0
    temp_path = zip_path.with_suffix(zip_path.suffix + ".tmp")
    if temp_path.exists():
        temp_path.unlink()

    compression_method = ZIP_STORED if compression_level <= 0 else ZIP_DEFLATED
    with ZipFile(temp_path, "w", compression=compression_method, compresslevel=(None if compression_method == ZIP_STORED else compression_level), allowZip64=True) as archive:
        preserved_temp_dir = repo_root / PRESERVED_LIGHT_SOURCE_TEMP_DIR
        if preserved_temp_dir.is_dir():
            archive.writestr(PRESERVED_LIGHT_SOURCE_TEMP_DIR.rstrip("/") + "/", b"")
        for path in files:
            rel = path.relative_to(repo_root).as_posix()
            archive.write(path, rel)
            count += 1
        for rel, data in sorted(generated_context.items()):
            archive.writestr(rel, data)
            count += 1

    temp_path.replace(zip_path)
    return count


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(args.repo_root)
    mod_name = derive_mod_name(repo_root, args.mod_name)
    prefix = archive_prefix(mod_name, args.prefix)
    zip_path = output_path(repo_root, args.output_dir, prefix, not args.dry_run)
    files = collect_files(repo_root)
    generated_context = build_generated_context(repo_root, files)
    total_bytes = sum(path.stat().st_size for path in files) + sum(len(data) for data in generated_context.values())
    compression_mode = "ZIP_STORED / no compression" if args.compression_level <= 0 else f"ZIP_DEFLATED / compression level {args.compression_level}"

    print(f"Repo root: {repo_root}")
    print(f"Mod name:  {mod_name}")
    print(f"Prefix:    {prefix}")
    print(f"Archive:   {zip_path}")
    print(f"Files:     {len(files)} selected + {len(generated_context)} generated snapshot-context files")
    print(f"Size:      {total_bytes:,} bytes before ZIP container overhead")
    print(f"Mode:      {compression_mode}")

    if args.dry_run:
        for path in files:
            print(path.relative_to(repo_root).as_posix())
        for rel in sorted(generated_context):
            print(f"(generated) {rel}")
        print("Dry run only; no archive written.")
        return 0

    start_time = perf_counter()
    count = write_zip(zip_path, repo_root, files, args.compression_level, generated_context)
    duration_ms = int((perf_counter() - start_time) * 1000)
    print(f"Wrote:     {count} file(s)")
    print(f"ZIP size:  {zip_path.stat().st_size:,} bytes")
    if not args.no_duration:
        print(f"Duration:  {duration_ms:,} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

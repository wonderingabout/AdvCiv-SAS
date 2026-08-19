# (c) 2026 wonderingabout & AI helpers
from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

import make_light_source_zip as light_source


GENERATED_NAMES = {"INDEX.txt", "PATH_HISTORY_INDEX.txt"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize the tracked greppable commit-diff mirror from current Git ancestry.")
    parser.add_argument("--repo-root", default=None, help="AdvCiv-SAS repository root. Defaults to the same auto-detection as make_light_source_zip.py.")
    parser.add_argument("--dry-run", action="store_true", help="Report additions/updates/removals without changing tracked mirror files or the Git-history cache.")
    return parser.parse_args()


def generated_value_matches_file(value: bytes | Path, path: Path) -> bool:
    if not path.is_file():
        return False
    if isinstance(value, Path):
        try:
            return path.stat().st_size == value.stat().st_size and filecmp.cmp(path, value, shallow=False)
        except OSError:
            return False
    try:
        return path.read_bytes() == value
    except OSError:
        return False


def write_generated_value(value: bytes | Path, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, Path):
        shutil.copyfile(value, path)
    else:
        path.write_bytes(value)


def main() -> int:
    args = parse_args()
    repo_root = light_source.find_repo_root(args.repo_root)
    tracked_dir = repo_root / light_source.TRACKED_COMMIT_DIFF_DIR
    generated, summary = light_source.build_commit_diff_history_context(repo_root, -1, write_cache=not args.dry_run)
    prefix = light_source.GENERATED_COMMIT_DIFF_DIR.rstrip("/") + "/"

    wanted: dict[Path, bytes | Path] = {}
    for rel, value in generated.items():
        if not rel.startswith(prefix):
            continue
        wanted[tracked_dir / rel[len(prefix):]] = value

    existing_generated: set[Path] = set()
    if tracked_dir.is_dir():
        existing_generated.update(path for path in tracked_dir.glob("*.diff") if path.is_file())
        existing_generated.update(tracked_dir / name for name in GENERATED_NAMES if (tracked_dir / name).is_file())
    stale = sorted(existing_generated - set(wanted))

    added = updated = unchanged = 0
    for path, value in sorted(wanted.items(), key=lambda item: item[0].name.lower()):
        if not path.exists():
            added += 1
        elif generated_value_matches_file(value, path):
            unchanged += 1
            continue
        else:
            updated += 1
        if not args.dry_run:
            write_generated_value(value, path)

    if not args.dry_run:
        for path in stale:
            path.unlink()
        tracked_dir.mkdir(parents=True, exist_ok=True)

    print(f"Repo root: {repo_root}")
    print(f"Tracked mirror: {light_source.TRACKED_COMMIT_DIFF_DIR}")
    print(summary)
    print(f"Sync: added={added}, updated={updated}, removed={len(stale)}, unchanged={unchanged}")
    if args.dry_run:
        print("Dry run: no tracked mirror files or history cache were changed.")
    else:
        print("Reminder: the mirror is generated from the current committed HEAD, so the commit that records this synchronization cannot contain its own diff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

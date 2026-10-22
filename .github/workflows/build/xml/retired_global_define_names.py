#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Use the Deprecated migration table associated with KI#1001.2 as the single retired-name source, then reject those spellings in active XML/C++/Python so rename cleanup cannot silently regress.
# Historical docs/log captures remain searchable because this checker does not scan them. (ChatGPT-5.6-Sol) -->

# <!-- custom: pathlib reads the canonical table and active files; re parses bounded keys/table rows; argparse and sys provide the CLI and exit status. (GPT-6.1-Sol) -->
from pathlib import Path
import argparse
import re
import sys


MAP_FILE = Path("_1_AdvCiv-SAS/Docs/Deprecated/global_define_names.md")
MAP_START = "<!-- KI1001.2_GLOBAL_DEFINE_MAP_START -->"
MAP_END = "<!-- KI1001.2_GLOBAL_DEFINE_MAP_END -->"
ROW_RE = re.compile(r"^\| `(?P<old>SAS_[^`]+)` \| `(?P<new>SAS_[^`]+)` \|", re.MULTILINE)


def get_default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_retired_map(repo_root: Path) -> tuple[dict[str, str], list[str]]:
    path = repo_root / MAP_FILE
    if not path.is_file():
        return {}, [f"missing KI#1001.2 mapping source: {MAP_FILE}"]

    text = path.read_text(encoding="utf-8")
    if text.count(MAP_START) != 1 or text.count(MAP_END) != 1:
        return {}, [f"{MAP_FILE}: expected exactly one retired-name map start/end marker"]

    start = text.index(MAP_START) + len(MAP_START)
    end = text.find(MAP_END, start)
    if end < 0:
        return {}, [f"{MAP_FILE}: retired-name map end marker precedes its start marker"]
    rows = list(ROW_RE.finditer(text[start:end]))
    if not rows:
        return {}, [f"{MAP_FILE}: KI#1001.2 retired-name map contains no SAS conversion rows"]

    mapping: dict[str, str] = {}
    current_names: set[str] = set()
    errors: list[str] = []
    for match in rows:
        old = match.group("old")
        new = match.group("new")
        if old == new:
            errors.append(f"{MAP_FILE}: mapping repeats unchanged name {old}")
        if old in mapping:
            errors.append(f"{MAP_FILE}: duplicate retired name {old}")
        if new in current_names:
            errors.append(f"{MAP_FILE}: duplicate current name {new}")
        mapping[old] = new
        current_names.add(new)
    return mapping, errors


def active_source_paths(repo_root: Path):
    roots = (
        (Path("Assets/XML"), {".xml"}),
        (Path("Assets/Python"), {".py"}),
        (Path("PrivateMaps"), {".py"}),
        (Path("CvGameCoreDLL"), {".cpp", ".h", ".inl"}),
    )
    for relative_root, suffixes in roots:
        base = repo_root / relative_root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            relative = path.relative_to(repo_root)
            if relative.parts[:2] == ("CvGameCoreDLL", "Project"):
                continue
            yield path


def current_sas_names(repo_root: Path) -> set[str]:
    path = repo_root / "Assets/XML/GlobalDefines_advciv_sas.xml"
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"<DefineName>\s*(SAS_[^<\s]+)\s*</DefineName>", text))


def check(repo_root: Path) -> tuple[list[str], dict[str, int]]:
    mapping, errors = load_retired_map(repo_root)
    if errors:
        return errors, {"mapping_count": len(mapping), "file_count": 0, "hit_count": 0}

    current = current_sas_names(repo_root)
    if not current:
        return ["missing or empty Assets/XML/GlobalDefines_advciv_sas.xml"], {"mapping_count": len(mapping), "file_count": 0, "hit_count": 0}

    for old, new in mapping.items():
        if old in current:
            errors.append(f"Assets/XML/GlobalDefines_advciv_sas.xml: retired name is still declared: {old}")
        if new not in current:
            errors.append(f"{MAP_FILE}: current mapped name is not declared: {old} -> {new}")
    if errors:
        return errors, {"mapping_count": len(mapping), "file_count": 0, "hit_count": 0}

    alternatives = b"|".join(re.escape(name.encode("ascii")) for name in sorted(mapping, key=len, reverse=True))
    # <!-- custom: Copied caches can have lowercase or uppercase prefixes (iSAS_..., IS_SAS_...).
    # Permit either before the retired spelling, but retain the right boundary so a longer unrelated key is not mistaken for it. (GPT-6.1-Sol) -->
    retired_re = re.compile(rb"(" + alternatives + rb")(?![A-Z0-9_])")

    file_count = 0
    hit_count = 0
    for path in active_source_paths(repo_root):
        file_count += 1
        data = path.read_bytes()
        for match in retired_re.finditer(data):
            old = match.group(1).decode("ascii")
            line = data.count(b"\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(repo_root).as_posix()}:{line}: retired GlobalDefine name {old}; use {mapping[old]}")
            hit_count += 1

    return errors, {"mapping_count": len(mapping), "file_count": file_count, "hit_count": hit_count}


def main() -> int:
    parser = argparse.ArgumentParser(description="Reject KI#1001.2 retired SAS GlobalDefine names in active XML/C++/Python source.")
    parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
    args = parser.parse_args()

    errors, stats = check(args.repo_root)
    if errors:
        print(f"FAIL retired GlobalDefine names: {len(errors)} issue(s), mapping={stats['mapping_count']}, activeFiles={stats['file_count']}")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"PASS retired GlobalDefine names: {stats['mapping_count']} retired names absent across {stats['file_count']} active XML/C++/Python files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: argparse exposes full-audit and diff modes; pathlib resolves formats, while sys locates shared Git and separator handling. (GPT-6.1-Sol) -->
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
# <!-- custom: Reuse source provenance's literal-aware blank-row ancestry and the common Git range reader; deleting code can create a bad separator without inserting lines. (GPT-6.1-Sol) -->
from blank_lines import blank_line_errors
from git_context import decode_text, ensure_base, git_text, run_git

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Source C++/Python/XML already have diff-aware spacing checks; Markdown uses markdownlint.
# Cover the remaining maintained text formats here, preserving archives, copied references and generated captures. (GPT-6.1-Sol) -->
LIMIT_ONE = {".ini", ".cfg", ".toml", ".yml", ".yaml", ".json", ".jsonc", ".txt"}
LIMIT_TWO = {".inl", ".rc", ".ps1", ".sh", ".bat", ".cmd", ".mk", ".mak", ".def"}
IGNORED_PREFIXES = (
    "_0_Common_Docs/", "LLM_Helpers/context/", "LLM_Helpers/outputs/", "_SNAPSHOT_CONTEXT/",
    "_1_AdvCiv-SAS/Docs/examples/", "_1_AdvCiv-SAS/Docs/git_logs/", "_1_AdvCiv-SAS/Docs/changelogs_web/",
    "Assets/Art/", "Assets/Python/Contrib/Sevopedia/Debug/", "CvGameCoreDLL/Project/temp_files/",
)
HISTORICAL_FILES = {
    "_1_AdvCiv-SAS/Docs/Source_Analysis/cpp_file_audit_album.txt",
    "_1_AdvCiv-SAS/Docs/Source_Analysis/historical_source_archaeology.txt",
}


def policy(path):
    if path.startswith(IGNORED_PREFIXES) or path in HISTORICAL_FILES:
        return None
    suffix = Path(path).suffix.lower()
    if Path(path).name in {".gitattributes", ".gitignore"}:
        return "config", 1
    if Path(path).name.startswith("Makefile"):
        return "makefile", 2
    if suffix in LIMIT_ONE:
        return suffix, 1
    if suffix in LIMIT_TWO:
        return suffix, 2
    return None


# <!-- custom: Audit mode finds all eligible runs once; normal CI compares changed files with its event base and rejects only newly introduced runs.
# Shared ancestry detection also catches separators joined by block deletion, retaining existing shorter runs and literal content. (GPT-6.1-Sol) -->
def check(repo, base_ref=None, event_name="local", audit=False):
    base = None if audit else ensure_base(repo, base_ref, event_name)
    args = ("ls-files", "-z") if base is None else ("diff", "--name-only", "--diff-filter=ACMRTUXB", "-z", base, "--")
    paths = run_git(repo, *args).stdout.decode("utf-8").split("\0")
    errors = []
    count = 0
    for path in filter(None, paths):
        setting = policy(path)
        target = repo / path
        if setting is None or not target.is_file():
            continue
        suffix, maximum = setting
        current = decode_text(target.read_bytes())
        before = "" if base is None else git_text(repo, base, path) or ""
        count += 1
        errors.extend(blank_line_errors(path, before, current, suffix, maximum))
    return errors, count


def main():
    parser = argparse.ArgumentParser(description="Reject newly introduced excessive blank separators in supplementary maintained text formats.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--base-ref")
    parser.add_argument("--event-name", default="local")
    parser.add_argument("--all", action="store_true", help="Audit the complete current scope before enabling diff-only enforcement")
    args = parser.parse_args()
    errors, count = check(args.repo_root, args.base_ref, args.event_name, args.all)
    print(("FAIL" if errors else "PASS") + f" text blank separators ({count} files checked)")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

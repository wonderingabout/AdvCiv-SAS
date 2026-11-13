#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: argparse and pathlib provide the CLI and repository paths; sys locates the shared Git reader. (Claude Code Sonnet 5.5) -->
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
# <!-- custom: git_context.run_git lists tracked and untracked files so uncommitted edits are checked before they are committed. (Claude Code Sonnet 5.5) -->
import git_context

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Only text formats are scanned; binaries such as .lnk, .ani and .chm legitimately contain control bytes.
# Tab, line feed and carriage return are allowed; every other C0 control byte and DEL is rejected. (Claude Code Sonnet 5.5) -->
# <!-- custom: Form feed was allowed too, as an old page break, though no text file held one. On 2026-11-13 a shell turned "\find.exe" into a form feed and "ind.exe" in the Makefile and the workflows README, and "\f" did the same elsewhere, four times in one session; this check passed each time, and Read does not show the character.
# No text file holds one now, so form feed is rejected like the rest; .tsv joined the formats for the text manifests. See KI#38.7. (Claude code Opus 5.5) -->
TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".xml", ".yml", ".yaml", ".json", ".jsonc", ".jsonl", ".cpp", ".c", ".h", ".inl", ".ps1", ".bat", ".cmd", ".sh",
    ".ini", ".cfg", ".toml", ".csv", ".tsv", ".diff", ".patch", ".html", ".css", ".js", ".sln", ".vcxproj", ".filters", ".rc", ".def", ".mk", ".mak",
}
TEXT_NAMES = {".gitattributes", ".gitignore"}
ALLOWED = {0x09, 0x0A, 0x0D}


def is_text_path(path):
    name = Path(path).name
    return name in TEXT_NAMES or name.startswith("Makefile") or Path(path).suffix.lower() in TEXT_SUFFIXES


# <!-- custom: A PowerShell double-quoted string turned `0 into NUL and `a into BEL inside AGENTS.md and the workflows README while documenting 0.610_tech_tree_* and `advisors`; neither the editor diff, Markdown structure nor line-ending checks flagged them, and NUL showed up only as red NUL markers in VS Code.
# Report the first byte offset per line with a readable escape so the source of the typo can be found. (Claude Code Sonnet 5.5) -->
def control_errors(path, data):
    errors = []
    for number, line in enumerate(data.split(b"\n"), 1):
        found = sorted({byte for byte in line if (byte < 0x20 or byte == 0x7F) and byte not in ALLOWED})
        if found:
            names = ", ".join("0x%02X" % byte for byte in found)
            offset = next(index for index, byte in enumerate(line) if byte in found)
            context = line[max(0, offset - 20):offset + 20].decode("utf-8", "replace")
            context = "".join(char if char.isprintable() else "<0x%02X>" % ord(char) for char in context)
            errors.append(f"{path}:{number}: control character(s) {names}; near: {context}")
    return errors


def check(repo):
    raw = git_context.run_git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z").stdout
    paths = [name for name in raw.decode("utf-8").split("\0") if name]
    errors = []
    count = 0
    for path in paths:
        target = repo / path
        if not is_text_path(path) or not target.is_file():
            continue
        count += 1
        errors.extend(control_errors(path, target.read_bytes()))
    return errors, count


def main():
    parser = argparse.ArgumentParser(description="Reject stray control characters (NUL, BEL, ...) in maintained text files.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, count = check(args.repo_root)
    print(("FAIL" if errors else "PASS") + f" text control characters ({count} files checked)")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

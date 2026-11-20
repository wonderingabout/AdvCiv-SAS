#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A post-fix replay paragraph was inserted before KI#979's existing archaeology and credits, breaking the discovery thread.
# Check clear paragraph insertions within existing KI entries; append new developments after prior reasoning rather than rewriting their apparent chronology.
# This structural guard permits corrections/reflow and cannot establish whether replacement prose changes historical meaning. (GPT-6.1-Sol) -->

# <!-- custom: argparse exposes the range-aware CLI, difflib aligns existing paragraphs, pathlib locates the repository, re identifies entry boundaries, and sys loads the shared Git context and reports failures. (GPT-6.1-Sol) -->
import argparse
import difflib
from pathlib import Path
import re
import sys

# <!-- custom: Reuse lib/git_context for the same push/PR base resolution and historical-text decoding as the other documentation checks. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import git_context

ROOT = Path(__file__).resolve().parents[4]
DOCUMENT = "_1_AdvCiv-SAS/Docs/README_Known_Issues.md"
ENTRY = re.compile(r"^## KI#(\d+(?:\.\d+)*)\b[^\n]*\n", re.MULTILINE)
ANCHOR = re.compile(r'^\s*<a\s+id="ki-[^"]+"\s*></a>\s*$', re.MULTILINE)
# <!-- custom: Archive headers identify supporting files rather than a step in the investigation; their conventional top placement must not trigger a history-insertion error. (GPT-6.1-Sol) -->
ARCHIVE_HEADER = re.compile(r"^(?:Screenshots/files|Files/screenshots) for this issue:\s", re.IGNORECASE)


# <!-- custom: Index bodies by stable KI number so menu edits, title/status changes, new entries and entry ordering do not masquerade as inserted history.
# Strip the next entry's anchor and normalize paragraph whitespace so source wrapping does not create false additions. (GPT-6.1-Sol) -->
def entries(text):
    headings = list(ENTRY.finditer(text))
    result = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = ANCHOR.sub("", text[heading.end():end])
        paragraphs = []
        line = text.count("\n", 0, heading.end()) + 1
        cursor = 0
        for match in re.finditer(r"\S[^\n]*(?:\n(?!\s*\n)[^\n]*)*", body):
            paragraph = " ".join(match.group().split())
            line += body.count("\n", cursor, match.start())
            cursor = match.start()
            if not ARCHIVE_HEADER.match(paragraph):
                paragraphs.append((paragraph, line))
        result[heading.group(1)] = paragraphs
    return result


# <!-- custom: Reject pure insertions only when prior body paragraphs still follow them.
# Replacements/deletions may be factual corrections, and an entirely new KI has no existing chronology to preserve; review still decides whether such edits are appropriate. (GPT-6.1-Sol) -->
def chronology_errors(old, new):
    errors = []
    previous = entries(old)
    for number, paragraphs in entries(new).items():
        before = previous.get(number)
        if not before:
            continue
        old_values = [value for value, _line in before]
        new_values = [value for value, _line in paragraphs]
        matcher = difflib.SequenceMatcher(None, old_values, new_values, autojunk=False)
        for kind, start, _end, new_start, _new_end in matcher.get_opcodes():
            if kind == "insert" and start < len(before):
                errors.append(f"{DOCUMENT}:{paragraphs[new_start][1]}: KI#{number}: new paragraph inserted before existing history; append the follow-up at the entry's end")
    errors += moved_errors(previous, entries(new))
    return errors


# <!-- custom: On 2026-11-18 a KI#38.7 patch applied at a shifted line landed inside KI#39, and moving it back carried KI#39's last three paragraphs into KI#38.7.
# The insertion rule above saw nothing, as deletions are allowed and a new entry has no history, and the structure checks passed; only the user's review noticed.
# So a paragraph that leaves an entry still present and appears in another fails; a whole entry merged into another, as KI#176.2 into KI#1091, leaves no source and passes.
# Only a paragraph found in a single entry before and after counts: replayed over the 546 commits that changed this document, the first draft failed 7, each a shared credit line such as "Found and documented in the C++ File Audit Album with the help of ChatGPT-5.6-Sol; …", which stayed in dozens of other entries when one entry's credit changed. (Claude code Opus 5.5) -->
def moved_errors(previous, current):
    errors = []
    found, owners = {}, {}
    for number, paragraphs in current.items():
        for value, line in paragraphs:
            found.setdefault(value, []).append((number, line))
    for number, paragraphs in previous.items():
        for value, _line in paragraphs:
            owners.setdefault(value, set()).add(number)
    for number, before in previous.items():
        if number not in current:
            continue
        kept = {value for value, _line in current[number]}
        for value, _line in before:
            if value in kept or len(owners[value]) > 1 or len(found.get(value, [])) != 1:
                continue
            other, line = found[value][0]
            errors.append(f"{DOCUMENT}:{line}: a paragraph of KI#{number} now sits in KI#{other}; keep it in its own entry")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Keep new KI history paragraphs at their entry's end.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--base-ref")
    parser.add_argument("--event-name", choices=("local", "push", "pull_request", "workflow_dispatch"), default="local")
    args = parser.parse_args()
    try:
        base = git_context.ensure_base(args.repo_root, args.base_ref, args.event_name)
        old = git_context.git_text(args.repo_root, base, DOCUMENT) if base else None
        path = args.repo_root / DOCUMENT
        new = path.read_text(encoding="utf-8-sig") if path.exists() else None
        errors = chronology_errors(old, new) if old is not None and new is not None and old != new else []
    except (OSError, RuntimeError) as exc:
        print(f"FAIL Known Issues chronology: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("FAIL Known Issues chronology\n  - " + "\n  - ".join(errors))
        return 1
    print("PASS Known Issues chronology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

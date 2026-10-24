#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: SAS gameplay modules were easy to miss in the root README and Main Changes Guide even when their features were described.
# Enforce a visible filename linked to its exact repository path, using Git's tracked/changed path inventory rather than reading every gameplay source file. (GPT-6.1-Sol) -->
# <!-- custom: argparse supplies local/full-audit modes; pathlib classifies repository paths, re recognizes deliberate filename branding, and sys locates shared helpers and returns CI exit status. (GPT-6.1-Sol) -->
import argparse
from pathlib import Path, PurePosixPath
import re
import sys
# <!-- custom: Decode root-anchored Markdown destinations, including percent-escaped filenames and optional fragments, without accepting external or similarly named files as the same source. (GPT-6.1-Sol) -->
from urllib.parse import unquote, urlsplit

# <!-- custom: Share range recovery with the other changed-file checks and reuse the existing Markdown parser for inline/reference links, comments and fences. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import git_context
import markdown_links as markdown

ROOT = Path(__file__).resolve().parents[4]
CHECKER = Path(__file__).resolve().relative_to(ROOT).as_posix()
GUIDE = "_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md"
DOCUMENTS = ("README.md", GUIDE)
SOURCE_ROOTS = ("Assets/Python/", "Assets/XML/", "PrivateMaps/", "CvGameCoreDLL/")
SOURCE_EXTENSIONS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hxx", ".inl", ".def", ".rc", ".py", ".xml"}


# <!-- custom: Match the deliberate SAS branding, including lowercase underscore/hyphen tokens such as GlobalDefines_advciv_sas.xml.
# A case-insensitive arbitrary substring would also match inherited StartPointsAsHandicap.cpp, which has no SAS branding.
# Project/build helpers are outside gameplay scope. (GPT-6.1-Sol) -->
def gameplay_source(path):
    name = PurePosixPath(path).name
    branded = "SAS" in name or re.search(r"(?:^|[_-])sas(?=[_.-]|$)", name, re.IGNORECASE)
    return bool(branded and path.startswith(SOURCE_ROOTS)
                and not path.startswith("CvGameCoreDLL/Project/")
                and PurePosixPath(path).suffix.lower() in SOURCE_EXTENSIONS)


# <!-- custom: Preserve offsets while marking inline code spans: a code-formatted filename inside a real link is valid, but an entire example link inside backticks is not a rendered source reference. (GPT-6.1-Sol) -->
def inline_code_spans(text):
    spans = []
    index = 0
    while True:
        start = text.find("`", index)
        if start < 0:
            return spans
        end = start + 1
        while end < len(text) and text[end] == "`":
            end += 1
        marker = text[start:end]
        close = text.find(marker, end)
        while close >= 0 and ((close > 0 and text[close - 1] == "`") or
                              (close + len(marker) < len(text) and text[close + len(marker)] == "`")):
            close = text.find(marker, close + 1)
        if close < 0:
            index = end
            continue
        index = close + len(marker)
        spans.append((start, index))


# <!-- custom: Count a filename only in its link's visible label, not incidental prose, a hidden comment, a code example or a bare link to another file.
# Repository-root links remain durable when the guide moves, matching the existing Markdown link policy. (GPT-6.1-Sol) -->
def documented_sources(text):
    clean = markdown.strip_html_comments(markdown.without_fenced_code(text))
    result = set()
    code = iter(inline_code_spans(clean))
    span = next(code, None)
    for offset, destination in markdown.markdown_links(clean):
        while span is not None and span[1] <= offset:
            span = next(code, None)
        if span is not None and span[0] <= offset < span[1]:
            continue
        target = urlsplit(destination)
        if target.scheme or target.netloc or not target.path.startswith("/"):
            continue
        path = unquote(target.path).lstrip("/")
        end = markdown.matching_bracket(clean, offset, "[", "]")
        if end >= 0 and PurePosixPath(path).name in clean[offset + 1:end] and gameplay_source(path):
            result.add(path)
    return result


def missing_links(paths, text, document=GUIDE):
    documented = documented_sources(text)
    return [f"{path}: add an explicit filename link [`{PurePosixPath(path).name}`](/{path}) beside its relevant feature in {document}"
            for path in sorted(set(paths) - documented)]


# <!-- custom: Audit all current candidates on request or when no comparison base exists; normal runs validate changed/renamed sources only.
# Updating this checker also audits the full current scope so rule changes cannot leave older omissions behind.
# Also check formerly documented paths whose documentation links disappear, preventing a docs-only edit from undoing the clean baseline without rescanning source contents.
# Deleted sources are not required. (GPT-6.1-Sol) -->
def check(repo, base_ref=None, event_name=None, full=False):
    raw = git_context.run_git(repo, "ls-files", "-z", "--", "Assets/Python", "Assets/XML", "PrivateMaps", "CvGameCoreDLL").stdout
    tracked = {path for path in raw.decode("utf-8").split("\0")
               if gameplay_source(path) and (repo / path).is_file()}
    base = None if full else git_context.ensure_base(repo, base_ref, event_name)
    if full or base is None:
        selected = tracked
    else:
        raw = git_context.run_git(repo, "diff", "--name-only", "-z", "--diff-filter=ACMRT", base, "--").stdout
        changed = set(raw.decode("utf-8").split("\0"))
        selected = tracked if CHECKER in changed else tracked & changed
    errors = []
    checked = set()
    for document in DOCUMENTS:
        target = repo / document
        current = target.read_text(encoding="utf-8-sig") if target.is_file() else ""
        required = set(selected)
        if base is not None and document in changed:
            old = git_context.git_text(repo, base, document) or ""
            required |= tracked & (documented_sources(old) - documented_sources(current))
        if not required:
            continue
        checked |= required
        if not target.is_file():
            errors.append(f"{document}: missing documentation for {len(required)} SAS source file(s)")
        else:
            errors.extend(missing_links(required, current, document))
    return errors, len(checked)


def main():
    parser = argparse.ArgumentParser(description="Require explicit root README and Main Changes Guide links for SAS-named gameplay source files.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--base-ref")
    parser.add_argument("--event-name")
    parser.add_argument("--all", action="store_true", help="audit every current tracked SAS-named gameplay source")
    args = parser.parse_args()
    try:
        errors, count = check(args.repo_root, args.base_ref, args.event_name, args.all)
    except RuntimeError as error:
        print(f"FAIL SAS source guide: {error}")
        return 1
    print(f"{'FAIL' if errors else 'PASS'} SAS source guide ({count} source file(s) checked across both documents)")
    for error in errors:
        print("  - " + error)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())

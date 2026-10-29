#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Filenames mentioned only as generic companion JSON were difficult to locate, even when their features were documented.
# Require searchable output paths in the two overview documents; scan only the owned Runtime publishers and build-report wrapper, not unrelated JSON settings, captures or generated files. (GPT-6.1-Sol) -->
# <!-- custom: pathlib/argparse provide the scoped repository CLI; re recognizes native format strings and same-line PowerShell concatenations, while sys imports the existing Markdown fence/comment filters. (GPT-6.1-Sol) -->
import argparse
from pathlib import Path
import re
import sys

# <!-- custom: Reuse documentation parsing so examples and hidden comments cannot substitute for visible filename/path guidance. (GPT-6.1-Sol) -->
import markdown_links as markdown

ROOT = Path(__file__).resolve().parents[4]
DOCUMENTS = ("README.md", "_1_AdvCiv-SAS/Docs/README_Logging_Inventory.md")
RUNTIME_NAME = re.compile(r"\b(SASRuntime[A-Za-z]+)(_[^\r\n]*?)?(\.jsonl?)\b")


# <!-- custom: Replace process-specific suffix expressions with a wildcard, retaining exact fixed filenames and JSON versus JSONL.
# This covers existing C++ printf strings and PowerShell concatenations without pretending to parse arbitrary executable path-building code. (GPT-6.1-Sol) -->
def runtime_paths(source):
    return {"Logs/" + match[1] + ("_*" if match[2] else "") + match[3]
            for match in RUNTIME_NAME.finditer(source)}


def missing_paths(paths, text):
    visible = markdown.strip_html_comments(markdown.without_fenced_code(text))
    return [path for path in sorted(paths) if "`" + path + "`" not in visible]


def check(root):
    publishers = [root / "CvGameCoreDLL/SASRuntimeStatus.cpp", *sorted((root / "Assets").glob("SASRuntime*.ps1"))]
    paths = set()
    for publisher in publishers:
        paths.update(runtime_paths(publisher.read_text(encoding="utf-8")))
    if not paths:
        return ["No Runtime output names discovered; review the publisher scope/extraction before accepting an empty audit."], 0
    wrapper = (root / "CvGameCoreDLL/Project/build_with_report.ps1").read_text(encoding="utf-8")
    if "'CvGameCoreDLL.dll.build.json'" not in wrapper:
        return ["Build-report filename construction changed; review its documented output paths."], len(paths)
    paths.update(("CvGameCoreDLL/Project/Release/CvGameCoreDLL.dll.build.json", "Assets/CvGameCoreDLL.dll.build.json"))
    errors = []
    for document in DOCUMENTS:
        text = (root / document).read_text(encoding="utf-8")
        errors.extend(f"{document}: explicitly name `{path}` beside its relevant feature/location guidance" for path in missing_paths(paths, text))
    return errors, len(paths)


def main():
    parser = argparse.ArgumentParser(description="Require explicit Runtime JSON/JSONL and DLL build-report paths in README and Logging Inventory.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, count = check(args.repo_root)
    print(f"{'FAIL' if errors else 'PASS'} diagnostic output names ({count} paths across both documents)")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())

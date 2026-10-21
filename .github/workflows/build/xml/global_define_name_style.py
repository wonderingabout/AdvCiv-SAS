#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Enforce the preventive GlobalDefine naming target chosen from Base AdvCiv 1.14's 42-byte maximum, separately from KI#1001's hard 255-byte loader-safety limit. See KI#1001.2. (ChatGPT-5.6-Sol) -->

# <!-- custom: pathlib locates XML, argparse exposes the repository override, sys loads the sibling safety checker, and ElementTree decodes define names for the shared byte counter. (GPT-6.1-Sol) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))

# <!-- custom: Reuse the proven loader-surface discovery and UTF-8 byte counting from the hard safety checker so the style rule cannot silently inspect a different set of shipped define files. (ChatGPT-5.6-Sol) -->
import global_define_lengths as lengths


DESIRED_MAX_DEFINE_NAME_BYTES = 42


def check(repo_root: Path) -> tuple[list[str], dict[str, object]]:
    violations: list[tuple[int, str, Path]] = []
    paths = lengths.loaded_define_paths(repo_root)
    if not paths:
        return ["no shipped GlobalDefines/PythonCallbackDefines XML files found"], {}

    define_count = 0
    max_name: tuple[int, str, Path] = (0, "", Path())
    for path in paths:
        relative = path.relative_to(repo_root)
        try:
            xml_root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            return [f"{relative}: XML parse error: {exc}"], {}

        for index, define in enumerate((node for node in xml_root.iter() if lengths.local_name(node.tag) == "Define"), 1):
            define_count += 1
            name = lengths.raw_child_text(define, "DefineName") or ""
            name_bytes = lengths.utf8_size(name)
            label = name.strip() or f"<Define> #{index}"
            if name_bytes > max_name[0]:
                max_name = (name_bytes, label, relative)
            if name_bytes > DESIRED_MAX_DEFINE_NAME_BYTES:
                violations.append((name_bytes, label, relative))

    violations.sort(key=lambda item: (-item[0], item[1], str(item[2])))
    failures = [
        f"{relative}: {name} DefineName is {size} UTF-8 bytes; desired maximum is {DESIRED_MAX_DEFINE_NAME_BYTES}"
        for size, name, relative in violations
    ]
    return failures, {
        "file_count": len(paths),
        "define_count": define_count,
        "violation_count": len(violations),
        "max_name": max_name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check shipped GlobalDefine names against SAS's AdvCiv-scale desired naming maximum.")
    parser.add_argument("--repo-root", type=Path, default=lengths.get_default_repo_root(), help="repository root; defaults to the root containing .github/")
    args = parser.parse_args()

    failures, stats = check(args.repo_root)
    if failures:
        print(f"FAIL GlobalDefine desired name lengths: {stats.get('violation_count', len(failures))} name(s) exceed {DESIRED_MAX_DEFINE_NAME_BYTES} UTF-8 bytes")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    max_name = stats["max_name"]
    print(
        "PASS GlobalDefine desired name lengths: "
        f"{stats['define_count']} defines across {stats['file_count']} file(s); "
        f"longest name={max_name[0]} bytes ({max_name[1]} in {max_name[2]}), "
        f"desired maximum={DESIRED_MAX_DEFINE_NAME_BYTES}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

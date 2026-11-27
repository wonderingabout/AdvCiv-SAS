#!/usr/bin/env python3

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

from __future__ import annotations

# <!-- custom: argparse/pathlib provide the offline CLI, json emits machine-readable summaries, and defaultdict groups streamed byte counts without retaining the whole record. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
import argparse
import json
from collections import defaultdict
from pathlib import Path


def classify_line(line: bytes, action_subtypes: bool = False) -> str:
    body = line.rstrip(b"\r\n")
    if body.startswith(b"GAME_RECORD_"):
        parts = body.split()
        token = parts[0]
        if action_subtypes and token == b"GAME_RECORD_ACTION":
            for field in parts[1:]:
                if field.startswith(b"type="):
                    return "GAME_RECORD_ACTION[%s]" % field[5:].decode("ascii", "replace")
        return token.decode("ascii", "replace")
    if body.startswith(b"|"):
        return "MAP_ASCII_BODY"
    if not body:
        return "BLANK"
    return "OTHER"


def summarize_lines(lines, action_subtypes: bool = False) -> dict:
    groups = defaultdict(lambda: {"lines": 0, "bytes": 0})
    total_lines = 0
    total_bytes = 0
    for line in lines:
        key = classify_line(line, action_subtypes=action_subtypes)
        groups[key]["lines"] += 1
        groups[key]["bytes"] += len(line)
        total_lines += 1
        total_bytes += len(line)
    result = {
        "totalLines": total_lines,
        "totalBytes": total_bytes,
        "families": [],
    }
    for name, values in sorted(groups.items(), key=lambda item: (-item[1]["bytes"], -item[1]["lines"], item[0])):
        entry = {"family": name, "lines": values["lines"], "bytes": values["bytes"]}
        entry["linePercent"] = (100.0 * values["lines"] / total_lines) if total_lines else 0.0
        entry["bytePercent"] = (100.0 * values["bytes"] / total_bytes) if total_bytes else 0.0
        result["families"].append(entry)
    return result


def summarize_bytes(data: bytes, action_subtypes: bool = False) -> dict:
    # <!-- custom: splitlines returns no item for a final empty tail; this fixture-friendly entry point counts each supplied physical line. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
    return summarize_lines(data.splitlines(keepends=True), action_subtypes=action_subtypes)


def summarize_path(path: Path, action_subtypes: bool = False) -> dict:
    # <!-- custom: Stream large records rather than retain their entire contents merely to count them; the grouped totals are the only persistent analysis state. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
    with path.open("rb") as handle:
        result = summarize_lines(handle, action_subtypes=action_subtypes)
    result["path"] = str(path)
    return result


def format_text(result: dict) -> str:
    rows = [
        "SASGameRecord volume summary",
        "Path: %s" % result["path"],
        "Total: %d lines, %d bytes" % (result["totalLines"], result["totalBytes"]),
        "",
        "%-44s %10s %9s %12s %9s" % ("Family", "Lines", "Line %", "Bytes", "Byte %"),
        "%-44s %10s %9s %12s %9s" % ("-" * 44, "-" * 10, "-" * 9, "-" * 12, "-" * 9),
    ]
    for entry in result["families"]:
        rows.append(
            "%-44s %10d %8.2f%% %12d %8.2f%%"
            % (
                entry["family"],
                entry["lines"],
                entry["linePercent"],
                entry["bytes"],
                entry["bytePercent"],
            )
        )
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report physical line and byte volume by SASGameRecord row family."
    )
    parser.add_argument("log", type=Path, help="SASGameRecord .log file")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a text table")
    parser.add_argument(
        "--action-subtypes",
        action="store_true",
        help="split GAME_RECORD_ACTION rows by their type= token",
    )
    args = parser.parse_args()

    result = summarize_path(args.log, action_subtypes=args.action_subtypes)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

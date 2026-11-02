#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Convert a Claude Code desktop session-export ZIP into a readable chat transcript.

# <!-- custom: __future__.annotations postpones evaluation of this Python-3 helper's return annotations. (GPT-6.1-Sol) -->
from __future__ import annotations

# <!-- custom: argparse exposes the input/output CLI; json decodes transcript records, pathlib manages filenames and UTF-8 output, and zipfile reads the exported archive without extracting it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
import argparse
import json
from pathlib import Path
import zipfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a Claude Code desktop session-export ZIP (transcript.jsonl) into a readable .txt chat transcript.")
    parser.add_argument("zip_path", help="Session-export ZIP, e.g. Downloads/session-export-<id>.zip.")
    parser.add_argument("--output", default=None, help="Output .txt path. Defaults to the ZIP path with a .txt suffix.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    zip_path = Path(args.zip_path)
    output = Path(args.output) if args.output else zip_path.with_suffix(".txt")
    rows = zipfile.ZipFile(zip_path).read("transcript.jsonl").decode("utf-8").splitlines()
    # <!-- custom: The desktop export is a raw JSONL log, and copying from the chat view captured only a small slice of a long session.
    # Keep user/assistant prose in full but reduce each tool call to a one-line marker; thinking and raw tool output are omitted, which shrank a 2 MB log to about 24 KB. (Claude code Opus 5.5) -->
    parts = []
    for row in rows:
        record = json.loads(row)
        role = record.get("type")
        if role not in ("user", "assistant"):
            continue
        content = record["message"]["content"]
        if isinstance(content, str):
            # <!-- custom: String content can belong to either role; preserve its actual speaker just as the text-block path does. (GPT-6.1-Sol) -->
            parts.append("=== %s ===\n%s\n" % ("USER" if role == "user" else "CLAUDE", content.strip()))
            continue
        for block in content:
            block_type = block.get("type")
            if block_type == "text" and block.get("text", "").strip():
                parts.append("=== %s ===\n%s\n" % ("USER" if role == "user" else "CLAUDE", block["text"].strip()))
            elif block_type == "tool_use":
                tool_input = block.get("input", {})
                desc = tool_input.get("description") or tool_input.get("file_path") or tool_input.get("pattern") or tool_input.get("query") or ""
                parts.append("  [tool: %s%s]\n" % (block["name"], (" - %s" % desc) if desc else ""))
    if not parts:
        raise SystemExit("No user/assistant messages found in %s; refusing to write an empty transcript." % zip_path)
    output.write_text("\n".join(parts), encoding="utf-8")
    print("wrote %s (%d bytes, %d entries)" % (output, output.stat().st_size, len(parts)))


if __name__ == "__main__":
    main()

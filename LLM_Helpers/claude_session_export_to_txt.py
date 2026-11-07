#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Convert a Claude Code session log (local .jsonl or desktop session-export ZIP) into a readable chat transcript.

# <!-- custom: __future__.annotations postpones evaluation of this Python-3 helper's return annotations. (GPT-6.1-Sol) -->
from __future__ import annotations

# <!-- custom: argparse exposes the input/output CLI; json decodes transcript records, pathlib manages filenames and UTF-8 output, and zipfile reads the exported archive without extracting it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
import argparse
import json
from pathlib import Path
import zipfile

# <!-- custom: Use the same configurable output folder as the Codex and ChatGPT transcript helper. (GPT-6.1-Sol) -->
# <!-- custom: latest_claude_session finds this repository's newest session log in the same shared path module. (Claude code Opus 5.5) -->
from chat_export_paths import DEFAULT_EXPORT_DIR, latest_claude_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a Claude Code session log (local .jsonl, or a desktop session-export ZIP holding transcript.jsonl) into a readable .txt chat transcript.")
    parser.add_argument("source_path", nargs="?", help="Local session log <session-id>.jsonl or a session-export ZIP such as Downloads/session-export-<id>.zip. Defaults to this repository's most recently modified session log.")
    parser.add_argument("--output", default=None, help=f"Output .txt path. Defaults to {DEFAULT_EXPORT_DIR / 'claude-<input-stem>.txt'}.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = Path(args.source_path) if args.source_path else latest_claude_session()
    output = Path(args.output) if args.output else DEFAULT_EXPORT_DIR / f"claude-{source_path.stem}.txt"
    # <!-- custom: Only the desktop app writes the export ZIP, so Codex could not produce one; the app keeps the same records in the local <session-id>.jsonl, which any agent can read.
    # Exporting this session by zipping that log first gave the same transcript format. (Claude code Opus 5.5) -->
    if source_path.suffix.lower() == ".jsonl":
        rows = source_path.read_text(encoding="utf-8").splitlines()
    else:
        rows = zipfile.ZipFile(source_path).read("transcript.jsonl").decode("utf-8").splitlines()
    # <!-- custom: The desktop export is a raw JSONL log, and copying from the chat view captured only a small slice of a long session.
    # Keep user/assistant prose in full but reduce each tool call to a one-line marker; thinking and raw tool output are omitted, which shrank a 2 MB log to about 24 KB. (Claude code Opus 5.5) -->
    # <!-- custom: Stable === USER === and === CLAUDE === separators make message boundaries easy to grep in long handoff transcripts, as in openai_chat_export_to_txt.py. (Claude code Opus 5.5) -->
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
        raise SystemExit("No user/assistant messages found in %s; refusing to write an empty transcript." % source_path)
    if not args.output:
        output.parent.mkdir(parents=True, exist_ok=True)
    # <!-- custom: The "x" mode refuses to overwrite an earlier export, but a rerun showed a raw FileExistsError traceback; report it as a one-line error instead. (Claude code Opus 5.5) -->
    try:
        with output.open("x", encoding="utf-8") as stream:
            stream.write("\n".join(parts))
    except FileExistsError:
        raise SystemExit("%s already exists; pass a different --output to keep both exports." % output)
    print("wrote %s (%d bytes, %d entries)" % (output, output.stat().st_size, len(parts)))


if __name__ == "__main__":
    main()

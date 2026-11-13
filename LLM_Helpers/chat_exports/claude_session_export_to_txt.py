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
# <!-- custom: --list needs the project's log folder (claude_project_dir), re to count each log's "model" fields and datetime to print each log's last write time. (Claude code Fable 5.2) -->
from chat_export_paths import claude_project_dir
import datetime
import re


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a Claude Code session log (local .jsonl, or a desktop session-export ZIP holding transcript.jsonl) into a readable .txt chat transcript.")
    parser.add_argument("source_path", nargs="?", help="Local session log <session-id>.jsonl or a session-export ZIP such as Downloads/session-export-<id>.zip. Defaults to this repository's most recently modified session log.")
    parser.add_argument("--output", default=None, help=f"Output .txt path. Defaults to {DEFAULT_EXPORT_DIR / 'claude-<input-stem>.txt'}.")
    parser.add_argument("--list", type=int, nargs="?", const=10, default=None, metavar="N", help="List this repository's N most recent session logs (default 10) with their last write time, size, model and opening words, instead of exporting.")
    return parser.parse_args()


# <!-- custom: Asked on 2026-11-13 to read "the last Fable chat, then the last Opus chat", the agent had to grep every log's "model" field by hand, since the newest log is the asking session itself and filenames are only session IDs.
# List the recent logs with their most frequent model and first user words, so a session can be picked by who wrote it and what it was about. (Claude code Fable 5.2) -->
def list_sessions(count: int) -> None:
    sessions = sorted(claude_project_dir().glob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)[:count]
    for path in sessions:
        text = path.read_text(encoding="utf-8")
        models = {}
        for model in re.findall(r'"model":"([^"<]+)"', text):
            models[model] = models.get(model, 0) + 1
        model = max(models, key=models.get) if models else "-"
        opening = "-"
        for row in text.split("\n"):
            # <!-- custom: Cheap pre-filter: only user rows are decoded, as a long log holds thousands of rows. (Claude code Fable 5.2) -->
            if '"type":"user"' not in row:
                continue
            content = json.loads(row).get("message", {}).get("content")
            if isinstance(content, list):
                content = " ".join(block.get("text", "") for block in content if block.get("type") == "text")
            if content and content.strip() and not content.lstrip().startswith("<"):
                # <!-- custom: The first test stopped with UnicodeEncodeError on an emoji in an opening line: the Windows console is cp1252, so print non-ASCII characters as "?". (Claude code Fable 5.2) -->
                opening = " ".join(content.split())[:90].encode("ascii", "replace").decode("ascii")
                break
        stat = path.stat()
        print("%s  %s  %8d KB  %-18s %s" % (datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"), path.name, stat.st_size // 1024, model, opening))


def main() -> None:
    args = parse_args()
    if args.list is not None:
        list_sessions(args.list)
        return
    source_path = Path(args.source_path) if args.source_path else latest_claude_session()
    output = Path(args.output) if args.output else DEFAULT_EXPORT_DIR / f"claude-{source_path.stem}.txt"
    # <!-- custom: Only the desktop app writes the export ZIP, so Codex could not produce one; the app keeps the same records in the local <session-id>.jsonl, which any agent can read.
    # Exporting this session by zipping that log first gave the same transcript format. (Claude code Opus 5.5) -->
    if source_path.suffix.lower() == ".jsonl":
        rows = source_path.read_text(encoding="utf-8").split("\n")
    else:
        rows = zipfile.ZipFile(source_path).read("transcript.jsonl").decode("utf-8").split("\n")
    # <!-- custom: str.splitlines() also splits on Unicode line separators such as U+2028 inside the JSON text, which cut 3 records of a long session in half on 2026-11-10; JSONL records end only at a newline. (Claude Code Opus 5.5) -->
    rows = [row for row in rows if row.strip()]
    # <!-- custom: The desktop export is a raw JSONL log, and copying from the chat view captured only a small slice of a long session.
    # Keep user/assistant prose in full but reduce each tool call to a one-line marker; thinking and raw tool output are omitted, which shrank a 2 MB log to about 24 KB. (Claude code Opus 5.5) -->
    # <!-- custom: Stable === USER === and === CLAUDE === separators make message boundaries easy to grep in long handoff transcripts, as in openai_chat_export_to_txt.py. (Claude code Opus 5.5) -->
    # <!-- custom: Agents export their own live session as a backup every while, and the app may be writing the log's last line at that moment: skip only an unfinished final line; a broken line elsewhere still fails loudly. (Claude Code Opus 5.5) -->
    if rows:
        try:
            json.loads(rows[-1])
        except ValueError:
            rows = rows[:-1]
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

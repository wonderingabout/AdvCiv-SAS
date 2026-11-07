#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Use standard-library readers for local Codex JSONL and ChatGPT app pages so this converter needs no credentials or packages. (GPT-6.1-Sol) -->
import argparse
import json
from pathlib import Path
import re

# <!-- custom: Use the same configurable output folder as the Claude transcript helper. (GPT-6.1-Sol) -->
from chat_export_paths import DEFAULT_EXPORT_DIR


def codex_messages(source):
    # <!-- custom: Read original conversation messages instead of compaction snapshots, which can repeat older turns. (GPT-6.1-Sol) -->
    with source.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            try:
                record = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"Invalid JSON in Codex record {number}. Retry if the session is still writing.") from exc
            item = record.get("payload", {})
            if record.get("type") != "response_item" or item.get("type") != "message":
                continue
            role = item.get("role")
            if role not in ("user", "assistant"):
                continue
            parts = []
            for block in item["content"]:
                if block.get("type") not in ("input_text", "output_text"):
                    continue
                value = block["text"]
                if role == "user" and re.fullmatch(
                    r"<(environment_context|external_codex_apps_[\w]+)>[\s\S]*?</\1>\s*", value.strip()
                ):
                    continue
                parts.append(value)
            label = "USER" if role == "user" else "CODEX"
            if item.get("phase") == "commentary":
                label = "CODEX UPDATE"
            yield label, "\n\n".join(parts)


def chatgpt_messages(source):
    pages = json.loads(source.read_text(encoding="utf-8-sig"))
    if isinstance(pages, dict):
        pages = [pages]
    if not pages or pages[-1]["page"]["hasMore"]:
        raise ValueError("The ChatGPT export is missing its oldest page.")
    thread = pages[0]["thread"]
    if thread["kind"] != "chatgpt":
        raise ValueError("Expected ChatGPT app chat pages.")
    seen = set()
    for page in reversed(pages):
        if page["thread"]["id"] != thread["id"] or page["page"]["order"] != "newest_first":
            raise ValueError("Expected newest-first pages from one ChatGPT conversation.")
        for turn in reversed(page["turns"]):
            if turn["id"] in seen:
                raise ValueError("Duplicate ChatGPT turn in the input pages.")
            seen.add(turn["id"])
            for item in turn["items"]:
                kind = item["type"]
                if kind not in ("userMessage", "agentMessage"):
                    continue
                blocks = item.get("content", [])
                if item.get("truncated") or any(block.get("truncated") for block in blocks):
                    raise ValueError("The app truncated a message. Export from a source with the full text.")
                if kind == "userMessage":
                    yield "USER", "\n\n".join(block["text"] for block in blocks if block["type"] == "text")
                else:
                    yield "CHATGPT", item["text"]


def main():
    parser = argparse.ArgumentParser(description="Convert a Codex session or ChatGPT app chat pages to readable TXT.")
    parser.add_argument("source", choices=("codex", "chatgpt"))
    parser.add_argument("input", type=Path, help="Codex rollout JSONL or ChatGPT read_thread JSON pages in fetch order.")
    parser.add_argument("--output", type=Path, help=f"TXT destination. Defaults to {DEFAULT_EXPORT_DIR / '<source>-<input-stem>.txt'}.")
    args = parser.parse_args()
    output = args.output or DEFAULT_EXPORT_DIR / f"{args.source}-{args.input.stem}.txt"
    reader = codex_messages if args.source == "codex" else chatgpt_messages
    try:
        # <!-- custom: Stable speaker separators make it easy to grep message boundaries in long handoff transcripts. (GPT-6.1-Sol) -->
        entries = [f"=== {role} ===\n{message}" for role, message in reader(args.input) if message.strip()]
        if not entries:
            raise ValueError("No conversation text found.")
        if args.output is None:
            output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write("\n\n".join(entries) + "\n")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"Wrote {output} ({len(entries)} messages).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Use standard-library readers for local Codex JSONL and ChatGPT app pages so this converter needs no credentials or packages. (GPT-6.1-Sol) -->
import argparse
# <!-- custom: Timestamp share snapshots in UTC so repeat exports of the same link get separate filenames. (GPT-6.1-Sol) -->
from datetime import datetime, timezone
import json
from pathlib import Path
import re
# <!-- custom: sys prints --tail as UTF-8, since a cp1252 console garbled the agent header's middle dot. (Claude Code Opus 5.5) -->
import sys

# <!-- custom: Use the same configurable output folder as the Claude transcript helper. (GPT-6.1-Sol) -->
from chat_export_paths import DEFAULT_EXPORT_DIR


def latest_codex_rollout():
    # <!-- custom: Codex files each chat under the day it started (~/.codex/sessions/<y>/<m>/<d>/rollout-*.jsonl), so the chat open today can sit in an October folder; pick the most recently written log instead. (Claude Code Opus 5.5) -->
    root = Path.home() / ".codex"
    logs = list(root.glob("sessions/*/*/*/rollout-*.jsonl")) + list(root.glob("archived_sessions/rollout-*.jsonl"))
    if not logs:
        raise ValueError(f"No Codex rollout logs under {root}.")
    return max(logs, key=lambda path: path.stat().st_mtime)


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


def shared_chat_messages(url):
    # <!-- custom: A shared page can list all turn containers while rendering only nearby messages.
    # Scroll to each container and require its message before writing any TXT. (GPT-6.1-Sol) -->
    try:
        from playwright.sync_api import Error as PlaywrightError, sync_playwright
    except ImportError as exc:
        raise ValueError("Share export requires Playwright. Run: python -m pip install playwright") from exc

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome")
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            # <!-- custom: ChatGPT also serves a fully rendered layout with different role markers.
            # Both layouts keep message text separate from the surrounding controls. (GPT-6.1-Sol) -->
            desktop = page.locator("main div[data-turn-id-container]:not([data-turn-id-container='client-created-root'])")
            rendered = page.locator("main [data-conversation-transcript] [data-message-role]")
            desktop.or_(rendered).first.wait_for(state="attached")
            if rendered.count():
                turns = rendered.all()
            else:
                turn_ids = desktop.evaluate_all("(nodes) => nodes.map(node => node.dataset.turnIdContainer)")
                if len(set(turn_ids)) != len(turn_ids) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", id_) for id_ in turn_ids):
                    raise ValueError("The shared page returned invalid or duplicate turn IDs.")
                turns = [desktop.and_(page.locator(f'[data-turn-id-container="{id_}"]')) for id_ in turn_ids]

            for number, turn in enumerate(turns, 1):
                try:
                    role = turn.get_attribute("data-message-role", timeout=10000)
                    if role is None:
                        message = turn.locator("section [data-message-author-role]")
                        if not message.is_visible():
                            turn.evaluate("(node) => node.scrollIntoView({block: 'start', behavior: 'instant'})", timeout=10000)
                        message.wait_for(timeout=10000)
                        role = message.get_attribute("data-message-author-role")
                    else:
                        message = turn.locator("[data-user-message-bubble], [data-assistant-markdown-root]")
                    body = message.inner_text(timeout=10000).strip()
                except PlaywrightError as exc:
                    raise ValueError(f"Could not read shared turn {number} of {len(turns)}: {exc}") from exc
                if role not in ("user", "assistant") or not body:
                    raise ValueError(f"Shared turn {number} of {len(turns)} has no exportable message text.")
                yield ("USER" if role == "user" else "CHATGPT"), body
            # <!-- custom: Refuse a partial export if navigating through the snapshot exposed more turns than the initial list. (GPT-6.1-Sol) -->
            if desktop.or_(rendered).count() != len(turns):
                raise ValueError("The shared page changed its turn list during export. Retry the share link.")
    except PlaywrightError as exc:
        raise ValueError(f"Could not load the shared chat in Chrome: {exc}") from exc


def main():
    parser = argparse.ArgumentParser(description="Export a Codex session, ChatGPT app pages or a shared ChatGPT conversation to TXT.")
    parser.add_argument("source", choices=("codex", "chatgpt", "share"))
    parser.add_argument("input", nargs="?", help="Codex rollout JSONL, ChatGPT read_thread JSON pages, or a ChatGPT share URL. For codex, omit it to use the most recently written Codex log.")
    parser.add_argument("--output", type=Path, help=f"TXT destination. Defaults to an input-based filename in {DEFAULT_EXPORT_DIR}.")
    # <!-- custom: An agent waiting for Codex's answer needs only its last few messages; on 2026-11-10 Claude Code exported the whole 3 MB chat and cut its end with awk each time.
    # --tail prints them instead of writing a file. (Claude Code Opus 5.5) -->
    parser.add_argument("--tail", type=int, help="print only the last N messages to the console instead of writing a file")
    args = parser.parse_args()
    if args.input is None and args.source != "codex":
        parser.error("input is required for chatgpt and share")
    try:
        if args.source == "share":
            share = re.fullmatch(r"https://chatgpt\.com/share/([0-9a-fA-F-]{36})/?", args.input)
            if not share:
                raise ValueError("Expected a ChatGPT share URL (https://chatgpt.com/share/...).")
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            filename = f"chatgpt-share-{share[1]}-{stamp}.txt"
            messages = shared_chat_messages(args.input)
        else:
            source = Path(args.input) if args.input else latest_codex_rollout()
            filename = f"{args.source}-{source.stem}.txt"
            reader = codex_messages if args.source == "codex" else chatgpt_messages
            messages = reader(source)
        output = args.output or DEFAULT_EXPORT_DIR / filename
        # <!-- custom: Stable speaker separators make it easy to grep message boundaries in long handoff transcripts. (GPT-6.1-Sol) -->
        entries = [f"=== {role} ===\n{message}" for role, message in messages if message.strip()]
        if not entries:
            raise ValueError("No conversation text found.")
        if args.tail:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            print("\n\n".join(entries[-args.tail:]))
            return
        if args.output is None:
            output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write("\n\n".join(entries) + "\n")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"Wrote {output} ({len(entries)} messages).")


if __name__ == "__main__":
    main()

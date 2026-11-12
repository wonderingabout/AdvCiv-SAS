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


def codex_message_text(item, omit_agents=False):
    # <!-- custom: The Markdown export and turn list used to hide all text starting with "<", which also hid real XML and HTML prompts.
    # Match the injected context blocks explicitly so those prompts stay searchable. (GPT-6.1-Sol) -->
    parts = []
    for block in item.get("content", []):
        if block.get("type") not in ("input_text", "output_text"):
            continue
        value = block["text"]
        if item.get("role") == "user":
            stripped = value.strip()
            if re.fullmatch(r"<(environment_context|external_codex_apps_[\w]+)>[\s\S]*?</\1>", stripped):
                continue
            if omit_agents and stripped.startswith("# AGENTS.md instructions for "):
                continue
        parts.append(value)
    return "\n\n".join(parts)


def codex_messages(source, steps=False):
    # <!-- custom: Read original conversation messages instead of compaction snapshots, which can repeat older turns. (GPT-6.1-Sol) -->
    # <!-- custom: steps also yields the commands Codex ran and the start of their output, which its app folds under "Worked for".
    # On 2026-11-11 they showed how a review reproduced its findings with a Python harness; unfolding them in the app took clicks that brought its window forward. (Claude Code Opus 5.5) -->
    with source.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            try:
                record = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"Invalid JSON in Codex record {number}. Retry if the session is still writing.") from exc
            item = record.get("payload", {})
            if steps and record.get("type") == "response_item" and item.get("type") in STEP_TYPES:
                yield step_entry(item)
                continue
            if record.get("type") != "response_item" or item.get("type") != "message":
                continue
            role = item.get("role")
            if role not in ("user", "assistant"):
                continue
            label = "USER" if role == "user" else "CODEX"
            if item.get("phase") == "commentary":
                label = "CODEX UPDATE"
            yield label, codex_message_text(item)


STEP_TYPES = ("custom_tool_call", "function_call", "custom_tool_call_output", "function_call_output")
STEP_INPUT_CHARS = 1500
STEP_OUTPUT_CHARS = 600


def step_entry(item):
    if item["type"].endswith("_output"):
        output = item.get("output")
        if isinstance(output, list):
            output = "".join(block.get("text", "") for block in output if isinstance(block, dict))
        return "CODEX STEP OUTPUT", str(output)[:STEP_OUTPUT_CHARS]
    return "CODEX STEP", str(item.get("input") or item.get("arguments") or "")[:STEP_INPUT_CHARS]


def codex_turns(source):
    # <!-- custom: Lists each turn's duration, step count and opening user words, to find long turns worth reading in full. (Claude Code Opus 5.5) -->
    started, steps, first_words, turns = {}, {}, {}, []
    current = None
    with source.open("rb") as stream:
        for line in stream:
            record = json.loads(line)
            item = record.get("payload", {})
            kind = item.get("type")
            stamp = record.get("timestamp")
            if kind == "task_started":
                current = item.get("turn_id")
                started[current], steps[current] = stamp, 0
            elif current and kind in ("custom_tool_call", "function_call"):
                steps[current] += 1
            elif current and kind == "message" and item.get("role") == "user" and current not in first_words:
                words = " ".join(codex_message_text(item, omit_agents=True).split())
                if words:
                    first_words[current] = words[:100]
            elif kind == "task_complete" and item.get("turn_id") in started:
                turn = item["turn_id"]
                begin = datetime.fromisoformat(started[turn].replace("Z", "+00:00"))
                end = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                turns.append(((end - begin).total_seconds() / 60, begin, steps[turn], first_words.get(turn, "")))
    return turns

CMD_PATTERNS = (re.compile(r'cmd:\s*`((?:\\.|[^`\\])*)`', re.S), re.compile(r'cmd:\s*"((?:\\.|[^"\\])*)"', re.S))
PATCH_FILE = re.compile(r"\*\*\* (?:Update|Add|Delete) File: ([^\\\n]+)")


def unescape_command(command):
    return command.replace("\\n", "\n").replace('\\"', '"').replace("\\`", "`").replace("\\\\", "\\")


def step_lines(text):
    # <!-- custom: A step's input is JavaScript calling Codex's tools; pull out the shell commands and patched files the way the app's Copy as Markdown lists them, and name any other tool. (Claude Code Opus 5.5) -->
    # <!-- custom: Direct shell calls store cmd as a JSON argument, unlike JavaScript batches. (GPT-6.1-Sol) -->
    if text.lstrip().startswith("{"):
        try:
            arguments = json.loads(text)
        except ValueError:
            arguments = None
        if isinstance(arguments, dict) and isinstance(arguments.get("cmd"), str):
            return ["Ran `%s`" % arguments["cmd"]]
    lines = []
    for pattern in CMD_PATTERNS:
        for command in pattern.findall(text):
            lines.append("Ran `%s`" % unescape_command(command))
    for path in PATCH_FILE.findall(text):
        lines.append("Edited `%s`" % path.strip())
    if not lines:
        lines += ["Called `%s`" % name for name in re.findall(r"tools\.(\w+)\(", text)]
    return lines or ["Tool call"]


def codex_title(source):
    index = Path.home() / ".codex" / "session_index.jsonl"
    session = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", source.name)
    title = None
    if index.is_file() and session:
        for line in index.open(encoding="utf-8"):
            entry = json.loads(line)
            if entry.get("id") == session[1]:
                title = entry.get("thread_name")
    return title or source.stem


def quoted(text):
    return "\n".join("> " + line if line else ">" for line in text.split("\n"))


def markdown_turn(turn):
    out = []
    if turn["user"]:
        out.extend([quoted(turn["user"]), ""])
    inner = []
    for kind, value in turn["items"]:
        if kind == "note":
            inner.extend([quoted(value), ">"])
        elif kind == "output":
            inner.append("> Tool output excerpt")
            inner.append(">")
            inner.extend(">     " + line if line else ">" for line in value.splitlines())
            inner.append(">")
        else:
            summary = "Ran a command" if len(value) == 1 else "Ran %d commands" % len(value)
            inner.extend(["> <details><summary>%s</summary>" % summary, ">"])
            for line in value:
                inner.extend(quoted("- " + line).split("\n"))
                inner.append(">")
            inner.extend(["> </details>", ">"])
    if inner:
        label = "%d previous messages" % len(turn["items"])
        if turn["minutes"] is not None:
            label += " - worked for %dm %02ds" % divmod(int(round(turn["minutes"] * 60)), 60)
        out.extend(["<details><summary>%s</summary>" % label, ""] + inner[:-1] + ["", "</details>", ""])
    if turn["answer"]:
        out.extend([turn["answer"], ""])
    return out


def codex_markdown(source, steps=False):
    # <!-- custom: The app's Copy as Markdown gives this layout, but on a 100,000-line chat it copied nothing for several tries, and clicking it brought Codex's window forward so the user's typing landed there (2026-11-11).
    # This writes it from the log instead: the user's message quoted, a details block with Codex's progress notes and grouped commands, then its final answer, plus each turn's working time, which the copy lacks. (Claude Code Opus 5.5) -->
    out = ["# " + codex_title(source), ""]
    turn = None
    with source.open("rb") as stream:
        for line in stream:
            record = json.loads(line)
            item = record.get("payload", {})
            kind = item.get("type")
            if kind == "task_started":
                if turn is not None:
                    out.extend(markdown_turn(turn))
                turn = {"user": "", "items": [], "answer": "", "start": record.get("timestamp"), "minutes": None}
            elif turn is None or record.get("type") not in ("response_item", "event_msg"):
                continue
            elif kind == "message" and record.get("type") == "response_item":
                text = codex_message_text(item, omit_agents=True)
                if item.get("role") == "user" and text.strip():
                    turn["user"] = (turn["user"] + "\n\n" + text).strip()
                elif item.get("role") == "assistant" and item.get("phase") == "commentary":
                    turn["items"].append(("note", text))
                elif item.get("role") == "assistant":
                    turn["answer"] = text
            elif kind in ("custom_tool_call", "function_call") and record.get("type") == "response_item":
                lines = step_lines(str(item.get("input") or item.get("arguments") or ""))
                if turn["items"] and turn["items"][-1][0] == "steps":
                    turn["items"][-1][1].extend(lines)
                else:
                    turn["items"].append(("steps", lines))
            elif steps and kind in ("custom_tool_call_output", "function_call_output") and record.get("type") == "response_item":
                _, output = step_entry(item)
                if output.strip():
                    turn["items"].append(("output", output))
            elif kind == "task_complete" and turn.get("start"):
                begin = datetime.fromisoformat(turn["start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                turn["minutes"] = (end - begin).total_seconds() / 60
    if turn is not None:
        out.extend(markdown_turn(turn))
    return "\n".join(out).rstrip() + "\n"


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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--tail", type=int, help="print only the last N messages to the console instead of writing a file")
    parser.add_argument("--steps", action="store_true", help="codex: include tool calls and output excerpts in text exports, or add output excerpts to Markdown")
    mode.add_argument("--markdown", action="store_true", help="codex: write the chat in the layout of the app's Copy as Markdown, with each turn's working time")
    mode.add_argument("--longest", type=int, help="codex: list the N longest turns with their duration, step count and opening words, instead of exporting")
    args = parser.parse_args()
    if args.source != "codex" and (args.steps or args.markdown or args.longest is not None):
        parser.error("--steps, --markdown and --longest require the codex source")
    if args.steps and args.longest is not None:
        parser.error("--steps requires a transcript export, not --longest")
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
            # <!-- custom: A UTC timestamp in the default name lets one thread be exported again later: the bare rollout name refused a second snapshot of the same Codex thread with "File exists" (2026-11-12).
            # Existing files are still never overwritten. (Claude code Opus 5.5) -->
            snapshot = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            if args.markdown and args.source == "codex":
                output = args.output or DEFAULT_EXPORT_DIR / f"codex-{source.stem}-{snapshot}.md.txt"
                if args.output is None:
                    output.parent.mkdir(parents=True, exist_ok=True)
                with output.open("x", encoding="utf-8") as stream:
                    stream.write(codex_markdown(source, steps=args.steps))
                print(f"Wrote {output}.")
                return
            if args.longest and args.source == "codex":
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
                for minutes, begin, step_count, words in sorted(codex_turns(source), reverse=True)[:args.longest]:
                    print(f"{minutes:6.1f} min  {step_count:3d} steps  {begin:%Y-%m-%d %H:%M} UTC  {words}")
                return
            filename = f"{args.source}-{source.stem}-{snapshot}.txt"
            messages = codex_messages(source, args.steps) if args.source == "codex" else chatgpt_messages(source)
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

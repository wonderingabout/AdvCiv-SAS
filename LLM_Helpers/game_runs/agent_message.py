#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Send a message from one agent to another agent's desktop app (Codex or the Claude app) following the convention in README_Desktop_Windows.md: a header with the sender and the UTC time to the millisecond, then the text, then a closing tag naming the sender and the reply wanted, e.g. [/Claude Code Opus 5.5 · Reply: user].
# Every send on 2026-11-10 repeated the same steps by hand: build the header, check the target's message box is empty, paste, press Enter, give focus back.
# Two of those sends picked up the user's keystrokes because the box was not checked in the same command, so this helper does all of it in one go. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; datetime stamps the header; subprocess asks PowerShell for the app's process ID; sys and pathlib handle exits and files; tempfile holds the screenshot. (Claude Code Opus 5.5) -->
import argparse
import datetime
# <!-- custom: re finds the header and closing tag for --check. (Claude Code Opus 5.5) -->
import re
import subprocess
import sys
import tempfile
from pathlib import Path
# <!-- custom: json reads Codex's session log for --wait-reply; time paces its polling. (Claude Code Opus 5.5) -->
import json
import time

# <!-- custom: desktop_windows, beside this script, finds, screenshots and pastes into the window. (Claude Code Opus 5.5) -->
import desktop_windows

REPLIES = ("none needed", "Claude app", "Codex app", "user")

# <!-- custom: "box" is where to click to type; "text" is the box's text area (left, top, right, bottom), left of the buttons, which must hold no dark text before pasting.
# Points were first measured on maximized windows on 2026-11-10 and kept here in code.
# On 2026-11-11 both apps moved to one 4K monitor, half each (see "Side by side on one monitor" in README_Desktop_Windows.md), and the maximized points clicked the wrong place, so sends needed --box and --text-area by hand.
# So each app now has named layouts, keyed by the window's outer width, and the helper picks the one matching the live window.
# They live in app_layouts.json beside this script, with when and how each was measured, since app updates move them and re-measuring should not mean editing code.
# Each run reads the file once at start, so a fixed layout applies from the next send on without touching code another agent may be running at that moment, such as a background --wait-reply; a wrong number cannot break the script's logic either.
# Each text area starts just right of where the blinking text cursor sits: a click that left the cursor there made an empty Codex box read as "16 dark pixels". (Claude Code Opus 5.5) -->
LAYOUTS_FILE = Path(__file__).resolve().parent / "ui_maps" / "app_layouts.json"
APPS = json.loads(LAYOUTS_FILE.read_text(encoding="utf-8"))["apps"]
LAYOUT_NAMES = sorted({name for app in APPS.values() for name in app["layouts"]})


def pick_layout(app, pid, name):
	# <!-- custom: The named layout if given; otherwise the one whose width is within 100 px of the window's, or None when no layout fits, so the caller must pass --box and --text-area. (Claude Code Opus 5.5) -->
	layouts = APPS[app]["layouts"]
	if name:
		return name, layouts[name]
	desktop_windows.make_dpi_aware()
	left, _top, right, _bottom = desktop_windows.window_rect(desktop_windows.find_window(pid))
	for key, layout in layouts.items():
		if abs((right - left) - layout["width"]) <= 100:
			return key, layout
	return None, None


def find_pid(process):
	command = "(Get-Process -Name '%s' -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1).Id" % process
	result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
	pid = result.stdout.strip()
	if not pid:
		sys.exit("no %s window found" % process)
	return int(pid)


def dark_pixels(pid, area):
	# <!-- custom: Typed text is near black, the placeholder ("Work with Codex", "Enter to send...") is light gray, so counting dark pixels tells an empty box from a draft. (Claude Code Opus 5.5) -->
	# <!-- custom: Pillow reads the screenshot; imported here so --dry-run works without it. (Claude Code Opus 5.5) -->
	from PIL import Image
	path = Path(tempfile.gettempdir()) / "agent_message_check.png"
	desktop_windows.screenshot(pid, path)
	image = Image.open(path).convert("RGB")
	left, top, right, bottom = area
	# <!-- custom: A maximized layout forced on a half-width window reached past its edge and crashed with "image index out of range"; name the mismatch instead. (Claude Code Opus 5.5) -->
	if right > image.width or bottom > image.height:
		sys.exit("the text area %s lies outside the %dx%d window; is --layout right for it?" % (area, image.width, image.height))
	return sum(1 for x in range(left, right, 2) for y in range(top, bottom, 2) if sum(image.getpixel((x, y))) < 200)


def build(sender, text, reply):
	stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
	# <!-- custom: The message first ended with a plain "Reply: <value>" line; the user found it weak, since those words appear in ordinary text and do not grep as an end, so it closes with a tag mirroring the header. (Claude Code Opus 5.5) -->
	return "[%s · %s UTC] %s\n[/%s · Reply: %s]" % (sender, stamp, text.strip(), sender, reply)


def check(text):
	# <!-- custom: Report text outside a message's header and closing tag, which came from someone else, usually the user typing in the box during the paste: on 2026-11-10 Codex spotted "nd", "i s", "and re", "diso" and "ve" by eye; this does it for any agent.
	# Returns a list of problems, empty when clean. (Claude Code Opus 5.5) -->
	header = re.search(r"\[([^/\]][^\]]*?) · [0-9-]+ [0-9:.]+ UTC\]", text)
	if header is None:
		return ["no header such as [Claude Code Opus 5.5 · 2026-11-10 21:15:02.123 UTC]"]
	problems = []
	if text[:header.start()].strip():
		problems.append("text before the header: %r" % text[:header.start()].strip())
	sender = header.group(1)
	close = re.search(r"\[/([^\]]*) · Reply: ([^\]]*)\]", text[header.end():])
	if close is None:
		return problems + ["no closing tag such as [/%s · Reply: user]" % sender]
	if close.group(1) != sender:
		problems.append("closing tag names %r, header names %r" % (close.group(1), sender))
	if close.group(2) not in REPLIES:
		problems.append("unknown Reply value %r" % close.group(2))
	after = text[header.end() + close.end():]
	if after.strip():
		problems.append("text after the closing tag: %r" % after.strip())
	return problems


# <!-- custom: Each app's session logs: Codex writes each thread to ~/.codex/sessions/<year>/<month>/<day>/rollout-*.jsonl, Claude Code each session to ~/.claude/projects/<project>/<session>.jsonl. (Claude Code Opus 5.5) -->
SESSION_LOGS = {
	"codex": (Path.home() / ".codex" / "sessions", "*/*/*/rollout-*.jsonl"),
	"claude": (Path.home() / ".claude" / "projects", "*/*.jsonl"),
}


def log_sizes(app):
	# <!-- custom: Only logs touched in the last two days can receive the reply, which keeps the scan short. (Claude Code Opus 5.5) -->
	root, pattern = SESSION_LOGS[app]
	cutoff = time.time() - 2 * 86400
	sizes = {}
	for path in root.glob(pattern):
		stat = path.stat()
		if stat.st_mtime >= cutoff:
			sizes[path] = stat.st_size
	return sizes


def message_text(content):
	if isinstance(content, str):
		return content
	return "\n\n".join(block.get("text", "") for block in content if isinstance(block, dict) and "text" in block)


def codex_step(record, state):
	# <!-- custom: Codex marks the end of a turn with a "task_complete" event; its answer is the last assistant message in the "final_answer" phase before it. (Claude Code Opus 5.5) -->
	item = record.get("payload", {})
	is_message = record.get("type") == "response_item" and item.get("type") == "message"
	if not state["found"]:
		state["found"] = is_message and item.get("role") == "user" and state["marker"] in message_text(item.get("content", []))
	elif is_message and item.get("role") == "assistant" and item.get("phase") == "final_answer":
		state["answer"] = message_text(item.get("content", []))
	elif item.get("type") == "task_complete":
		return (True, state["answer"])
	return None


def claude_step(record, state):
	# <!-- custom: Claude Code ends a turn with assistant records whose stop_reason is "end_turn", a thinking block then the text, sharing one message ID, followed by a "stop_hook_summary" entry (observed in its log on 2026-11-11).
	# So the turn has ended at the first other record after them, and the answer is their text. (Claude Code Opus 5.5) -->
	message = record.get("message")
	if not isinstance(message, dict):
		message = {}
	content = message.get("content", [])
	if not state["found"]:
		state["found"] = record.get("type") == "user" and state["marker"] in message_text(content)
	elif record.get("type") == "assistant" and message.get("stop_reason") == "end_turn":
		state["ending"] = True
		text = message_text(content)
		if text:
			state["answer"] = (state["answer"] + "\n\n" + text) if state["answer"] else text
	elif state.get("ending"):
		return (True, state["answer"])
	# <!-- custom: Codex's live test found that a later human message arriving before the answer could have its answer taken for ours.
	# Claude Code folds such a message into the running turn, so one answer may cover both; it is flagged rather than dropped.
	# A human message is a user record with text; tool results are user records too, but hold only tool_result blocks. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	elif record.get("type") == "user" and not record.get("isMeta") and message_text(content).strip():
		state["later_message"] = True
	return None


TURN_STEPS = {"codex": codex_step, "claude": claude_step}


def reply_since(app, before, marker):
	# <!-- custom: Read only what each log gained since the send.
	# Returns None until the turn holding our message ends, then (True, answer, later_message), with answer None if that turn gave no final answer and later_message set if another human message came first (Claude Code only).
	# The first version returned at the first "task_complete" in any watched log.
	# Codex's review reproduced that another thread's turn, or with --queue the turn Codex was already working on, could be taken for the reply.
	# So it now waits for the user message that holds our header, unique to the millisecond, and takes the end of the turn after it in that log. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	for path, size in log_sizes(app).items():
		start = before.get(path, 0)
		if size <= start:
			continue
		# <!-- custom: Codex's review also reproduced a JSONDecodeError when the recorded size fell inside a record Codex was writing; so read from one byte earlier and drop everything up to the first newline unless that byte is one.
		# That record began before the send, so it cannot be ours. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
		with path.open("rb") as stream:
			stream.seek(max(start - 1, 0))
			data = stream.read(size - max(start - 1, 0))
		if start > 0:
			data = data[data.find(b"\n") + 1:]
		state = {"marker": marker, "found": False, "answer": None}
		# <!-- custom: The last piece has no newline yet when the app is mid-write, so it waits for the next poll. (Claude Code Opus 5.5) -->
		for line in data.split(b"\n")[:-1]:
			result = TURN_STEPS[app](json.loads(line), state)
			if result is not None:
				return result + (state.get("later_message", False),)
		# <!-- custom: Codex's live test also found that a log ending right after Claude Code's final text kept waiting for one more record; a complete end_turn answer is enough. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
		if state.get("ending") and state["answer"]:
			return (True, state["answer"], state.get("later_message", False))
	return None


def wait_reply(app, before, marker, timeout):
	# <!-- custom: On 2026-11-11 Claude Code waited for a Codex review with a shell loop on the newest log, so neither agent nor user had to check Codex's window or guess how long to wait; this keeps that loop, and works the other way for Codex waiting on Claude Code. (Claude Code Opus 5.5) -->
	deadline = time.time() + timeout
	while time.time() < deadline:
		result = reply_since(app, before, marker)
		if result is not None:
			return result
		time.sleep(2)
	return None


def main():
	parser = argparse.ArgumentParser(description="Send a tagged message to the Codex or Claude app, checking its message box is empty first.")
	parser.add_argument("--to", choices=sorted(APPS))
	parser.add_argument("--sender", help='agent and model, e.g. "Claude Code Opus 5.5"')
	parser.add_argument("--reply", choices=REPLIES, help="what the sender expects back")
	parser.add_argument("--check", type=Path, metavar="FILE", help="instead of sending, check a received message saved in FILE for text outside its header and closing tag")
	source = parser.add_mutually_exclusive_group()
	source.add_argument("--text")
	source.add_argument("--file", type=Path, help="UTF-8 file holding the message body, which avoids shell quoting")
	parser.add_argument("--queue", action="store_true", help="send with Ctrl+Enter, queueing it while the target is working")
	parser.add_argument("--layout", choices=LAYOUT_NAMES, help="the target window's layout from app_layouts.json; by default picked from its width")
	parser.add_argument("--check-box", action="store_true", help="only report the picked layout and whether the target's message box is empty, without sending")
	parser.add_argument("--box", type=int, nargs=2, metavar=("X", "Y"), help="override where to click in the target window")
	parser.add_argument("--text-area", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="override the box's text area for the empty check")
	parser.add_argument("--idle-seconds", type=float, default=5.0, help="send only after no keyboard or mouse input for this long; 2.5 let a typing user's next keys in")
	parser.add_argument("--idle-timeout", type=int, default=120, help="give up if the user is never idle that long within this many seconds")
	parser.add_argument("--dry-run", action="store_true", help="print the message without sending it")
	parser.add_argument("--wait-reply", action="store_true", help="after sending, wait until the target app ends the turn holding this message and print its final answer, read from that app's session log")
	parser.add_argument("--wait-timeout", type=int, default=1800, help="give up waiting for the reply after this many seconds")
	args = parser.parse_args()
	# <!-- custom: The header's middle dot printed as a replacement character in a cp1252 console. (Claude Code Opus 5.5) -->
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	if args.check:
		problems = check(args.check.read_text(encoding="utf-8"))
		print("\n".join(problems) if problems else "clean: nothing outside the header and closing tag")
		sys.exit(1 if problems else 0)
	if args.check_box:
		# <!-- custom: Lets an agent confirm the picked layout and the empty-box reading, for example after moving a window, without sending anything. (Claude Code Opus 5.5) -->
		if not args.to:
			parser.error("--check-box needs --to")
		pid = find_pid(APPS[args.to]["process"])
		layout_name, layout = pick_layout(args.to, pid, args.layout)
		if layout is None and not args.text_area:
			sys.exit("no layout in app_layouts.json matches the %s window's width; pass --layout or --text-area, or measure the window and add its layout there" % args.to)
		dark = dark_pixels(pid, tuple(args.text_area or layout["text"]))
		print("%s (pid %d): layout %s, %d dark pixels in the text area, %s" % (args.to, pid, layout_name or "custom", dark, "empty" if dark <= 5 else "not empty"))
		sys.exit(0 if dark <= 5 else 1)
	if not (args.to and args.sender and args.reply and (args.text is not None or args.file)):
		parser.error("sending needs --to, --sender, --reply and --text or --file")

	app = APPS[args.to]
	body = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
	message = build(args.sender, body, args.reply)
	if args.dry_run:
		print(message)
		return
	pid = find_pid(app["process"])
	layout_name, layout = pick_layout(args.to, pid, args.layout)
	if layout is None and not (args.box and args.text_area):
		sys.exit("no layout in app_layouts.json matches the %s window's width; pass --layout, or --box and --text-area after a screenshot, and add the measured layout there" % args.to)
	text_area = tuple(args.text_area or layout["text"])
	box = tuple(args.box or layout["box"])
	print("layout: %s" % (layout_name or "custom"))
	# <!-- custom: The empty-box check alone was not enough: on 2026-11-10 a send through this helper still arrived with the user's keystrokes at both ends ("and re" before the header, "diso" after the Reply: line), typed during the second the target was in front.
	# Waiting until the user has been idle for a moment closes most of that gap; the delimiters catch what still slips in. (Claude Code Opus 5.5) -->
	if not desktop_windows.wait_for_idle_user(args.idle_seconds, args.idle_timeout):
		sys.exit("the user kept typing or moving the mouse for %d seconds; not sending" % args.idle_timeout)
	dark = dark_pixels(pid, text_area)
	if dark > 5:
		sys.exit("the %s message box is not empty (%d dark pixels): someone may be typing there; not sending" % (args.to, dark))
	before = log_sizes(args.to) if args.wait_reply else None
	desktop_windows.paste(pid, box[0], box[1], message, "ctrl+enter" if args.queue else "enter")
	print("sent to %s (pid %d):" % (args.to, pid))
	print(message)
	print("Check the sent message: anything before its header or after its closing tag was not yours.")
	if args.wait_reply:
		name = {"codex": "Codex", "claude": "Claude Code"}[args.to]
		print("waiting for %s to end the turn holding this message..." % name, flush=True)
		result = wait_reply(args.to, before, message[:message.index(" UTC]") + 5], args.wait_timeout)
		if result is None:
			sys.exit("no reply from %s within %d seconds" % (name, args.wait_timeout))
		# <!-- custom: Codex's review found that a turn ending without a final answer exited successfully with an empty reply; say so and fail instead. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
		if result[1] is None:
			sys.exit("%s ended the turn holding this message without a final answer" % name)
		print("=== %s REPLY ===" % name.upper())
		print(result[1])
		if result[2]:
			print("Note: another message reached %s before this answer, so the answer may cover it too." % name)


if __name__ == "__main__":
	main()

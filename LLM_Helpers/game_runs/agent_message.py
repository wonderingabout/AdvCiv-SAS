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

# <!-- custom: desktop_windows, beside this script, finds, screenshots and pastes into the window. (Claude Code Opus 5.5) -->
import desktop_windows

REPLIES = ("none needed", "Claude app", "Codex app", "user")

# <!-- custom: Window-relative points for each app maximized on a 3840x2100 screen, observed on 2026-11-10.
# "box" is where to click to type; "text" is the box's text area (left, top, right, bottom), left of the caret and buttons, which must hold no dark text before pasting.
# These apps change their layout often: when a send is refused or lands wrong, take a screenshot and pass --box and --text instead. (Claude Code Opus 5.5) -->
APPS = {
	"codex": {"process": "ChatGPT", "box": (2250, 1929), "text": (1650, 1905, 2900, 1955)},
	"claude": {"process": "claude", "box": (2100, 2007), "text": (1650, 1975, 2550, 2035)},
}


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
	parser.add_argument("--box", type=int, nargs=2, metavar=("X", "Y"), help="override where to click in the target window")
	parser.add_argument("--text-area", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="override the box's text area for the empty check")
	parser.add_argument("--idle-seconds", type=float, default=5.0, help="send only after no keyboard or mouse input for this long; 2.5 let a typing user's next keys in")
	parser.add_argument("--idle-timeout", type=int, default=120, help="give up if the user is never idle that long within this many seconds")
	parser.add_argument("--dry-run", action="store_true", help="print the message without sending it")
	args = parser.parse_args()
	# <!-- custom: The header's middle dot printed as a replacement character in a cp1252 console. (Claude Code Opus 5.5) -->
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	if args.check:
		problems = check(args.check.read_text(encoding="utf-8"))
		print("\n".join(problems) if problems else "clean: nothing outside the header and closing tag")
		sys.exit(1 if problems else 0)
	if not (args.to and args.sender and args.reply and (args.text is not None or args.file)):
		parser.error("sending needs --to, --sender, --reply and --text or --file")

	app = APPS[args.to]
	body = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
	message = build(args.sender, body, args.reply)
	if args.dry_run:
		print(message)
		return
	pid = find_pid(app["process"])
	# <!-- custom: The empty-box check alone was not enough: on 2026-11-10 a send through this helper still arrived with the user's keystrokes at both ends ("and re" before the header, "diso" after the Reply: line), typed during the second the target was in front.
	# Waiting until the user has been idle for a moment closes most of that gap; the delimiters catch what still slips in. (Claude Code Opus 5.5) -->
	if not desktop_windows.wait_for_idle_user(args.idle_seconds, args.idle_timeout):
		sys.exit("the user kept typing or moving the mouse for %d seconds; not sending" % args.idle_timeout)
	dark = dark_pixels(pid, tuple(args.text_area or app["text"]))
	if dark > 5:
		sys.exit("the %s message box is not empty (%d dark pixels): someone may be typing there; not sending" % (args.to, dark))
	box = tuple(args.box or app["box"])
	desktop_windows.paste(pid, box[0], box[1], message, "ctrl+enter" if args.queue else "enter")
	print("sent to %s (pid %d):" % (args.to, pid))
	print(message)
	print("Check the sent message: anything before its header or after its closing tag was not yours.")


if __name__ == "__main__":
	main()

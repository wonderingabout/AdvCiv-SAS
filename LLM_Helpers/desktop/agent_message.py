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
LAYOUTS_FILE = Path(__file__).resolve().parent / "layouts" / "app_layouts.json"
APPS = json.loads(LAYOUTS_FILE.read_text(encoding="utf-8"))["apps"]
LAYOUT_NAMES = sorted({name for app in APPS.values() for name in app["layouts"]})


def matching_layouts(app, pid):
	# <!-- custom: Was pick_layout, which returned the first layout whose width is within 100 px of the window's; now every such layout, as one width can have several, such as before and after a zoom change, and read_box picks among them from a screenshot. (Claude Code Opus 5.5) -->
	desktop_windows.make_dpi_aware()
	left, _top, right, _bottom = desktop_windows.window_rect(desktop_windows.find_window(pid))
	return [(key, layout) for key, layout in APPS[app]["layouts"].items() if abs((right - left) - layout["width"]) <= 100]


def find_pid(process, required=True):
	# <!-- custom: Was find_pid(process); required=False returns None instead of exiting, for --start, which opens the app when it has no window. (Claude code Opus 5.5) -->
	command = "(Get-Process -Name '%s' -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1).Id" % process
	result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True)
	pid = result.stdout.strip()
	if not pid:
		if required:
			sys.exit("no %s window found; --start opens the app first" % process)
		return None
	return int(pid)


def start_app(name, timeout, settle, positions):
	# <!-- custom: Open the app when it has no window, so an agent can reach Codex after the user closed it (the user's request, 2026-11-15) instead of asking for it to be reopened.
	# Store apps have no stable .exe path (WindowsApps holds a versioned folder), so the launch goes through explorer.exe and shell:AppsFolder with the AppUserModelID kept in app_layouts.json.
	# The window appears before its message box can take text, so a few seconds more pass before sending; --positions then puts it back in a saved desktop layout, as a fresh window opens wherever the app last was. (Claude code Opus 5.5) -->
	app = APPS[name]
	pid = find_pid(app["process"], required=False)
	if pid is None:
		subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + app["launch"]])
		deadline = time.time() + timeout
		while pid is None and time.time() < deadline:
			time.sleep(1.0)
			pid = find_pid(app["process"], required=False)
		if pid is None:
			sys.exit("%s did not open a window within %d seconds" % (name, timeout))
		print("started %s (pid %d); waiting %d seconds for it to load" % (name, pid, settle), flush=True)
		time.sleep(settle)
	else:
		print("%s already open (pid %d)" % (name, pid))
	if positions:
		print("positions %s: %s" % (positions, desktop_windows.restore_positions(positions)))
	return pid


def area_reading(image, area):
	# <!-- custom: Typed text is near black, the placeholder ("Work with Codex", "Ctrl+Enter to queue") is gray, so counting dark pixels tells an empty box from a draft.
	# Returns (dark, gray, gray_left) over every other pixel, gray_left being the leftmost gray column or None; gray stops at a channel sum of 620, below the box's own border (213 per channel), and counts the placeholder (195 to 205) and the anti-aliased edges of typed text. (Claude Code Opus 5.5) -->
	left, top, right, bottom = area
	# <!-- custom: A maximized layout forced on a half-width window reached past its edge and crashed with "image index out of range"; name the mismatch instead. (Claude Code Opus 5.5) -->
	if right > image.width or bottom > image.height:
		sys.exit("the text area %s lies outside the %dx%d window; is --layout right for it?" % (area, image.width, image.height))
	dark = 0
	gray = 0
	gray_left = None
	for x in range(left, right, 2):
		for y in range(top, bottom, 2):
			pixel = image.getpixel((x, y))
			if sum(pixel) < 200:
				dark += 1
			elif sum(pixel) <= 620 and max(pixel) - min(pixel) < 30:
				gray += 1
				if gray_left is None:
					gray_left = x
	return dark, gray, gray_left


# <!-- custom: Measured on 2026-11-26: an area on the text line read about 250 gray pixels from the placeholder, while a stale one clipping its edge read 38 to 39. (Claude Code Opus 5.5) -->
MIN_PLACEHOLDER_GRAY = 80
# <!-- custom: Each text area starts just right of the caret, where the placeholder and typed text begin, so the placeholder's gray starts at the area's left edge; the sampling step is 2 pixels. (Claude Code Opus 5.5) -->
PLACEHOLDER_LEFT_TOLERANCE = 8


def frame_found(image, frame):
	# <!-- custom: The composer's top border, a gray line with the box's white inside just below it, sampled every 8 pixels between its measured ends; at least 90% must match.
	# It anchors the box's identity on its own chrome rather than on its contents, as Codex's review (GPT-6.2-Sol) advised after reproducing a gray toolbar at the area's left edge reading as an empty box.
	# A multi-line draft grows the box upward and moves the frame, which also fails closed. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
	left, right, y, value = frame
	if y + 3 >= image.height or right > image.width:
		return False
	samples = range(left + 20, right - 20, 8)
	matches = 0
	for x in samples:
		edge = sum(image.getpixel((x, y))) / 3.0
		inside = sum(image.getpixel((x, y + 3))) / 3.0
		if abs(edge - value) <= 10 and inside - edge >= 10:
			matches += 1
	return matches >= 0.9 * len(samples)


def decide_box(readings):
	# <!-- custom: Takes (name, area, dark, gray, gray_left, frame) per candidate area, frame being whether its composer border was found, and returns ("EMPTY" or "NOT_EMPTY", index) or ("UNKNOWN", reason); kept free of screenshots so CI can test it with fixtures.
	# A draft anywhere fails closed: any area with more than 5 dark pixels means not empty.
	# "Empty" needs exactly one area with its composer frame in place and its placeholder gray starting at its left edge; none or several means unknown.
	# A first version picked the area with the most ink, which Codex's review (GPT-6.2-Sol) showed is evidence of ink, not of identity: a stale crop over a gray toolbar could outscore the real crop holding a short draft, and the paste would land beside it. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
	darkest = None
	for index, (_name, _area, dark, _gray, _gray_left, _frame) in enumerate(readings):
		if dark > 5 and (darkest is None or dark > readings[darkest][2]):
			darkest = index
	if darkest is not None:
		return "NOT_EMPTY", darkest
	matches = [index for index, (_name, area, _dark, gray, gray_left, frame) in enumerate(readings) if frame and gray >= MIN_PLACEHOLDER_GRAY and gray_left is not None and gray_left - area[0] <= PLACEHOLDER_LEFT_TOLERANCE]
	if len(matches) == 1:
		return "EMPTY", matches[0]
	if matches:
		return "UNKNOWN", "several areas (%s) show the placeholder" % ", ".join(readings[index][0] for index in matches)
	return "UNKNOWN", "no area (%s) shows the placeholder at its left edge inside its composer frame" % ", ".join(reading[0] for reading in readings)


def read_box(app, pid, name, text_area):
	# <!-- custom: Returns (layout name, layout, text area, dark pixels, verdict) for the message box, verdict EMPTY or NOT_EMPTY, or exits when the box cannot be identified; None when no layout matches the window.
	# On 2026-11-26 the user changed the apps' zoom, and each stored area went stale its own way: Claude's caught the + button and the caret, so an empty box read as 6 dark pixels and Codex's reply was held; Codex's lay below a text line that had moved up, so a short draft would have read as empty and been pasted over.
	# A zoom setting cannot be read from the window, and app updates move the box just the same, so one screenshot decides through decide_box. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: Pillow reads the screenshot; imported here so --dry-run works without it. (Claude Code Opus 5.5) -->
	from PIL import Image
	layouts = APPS[app]["layouts"]
	if name:
		# <!-- custom: A named layout with --text-area keeps the layout's click point and checks the given area, as before 2026-11-26; Codex's review (GPT-6.2-Sol) caught the first rewrite dropping the named layout there. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
		candidates = [(name, layouts[name], tuple(text_area or layouts[name]["text"]))]
	elif text_area:
		candidates = [("custom", None, tuple(text_area))]
	else:
		candidates = [(key, layout, tuple(layout["text"])) for key, layout in matching_layouts(app, pid)]
	if not candidates:
		return None
	path = Path(tempfile.gettempdir()) / "agent_message_check.png"
	desktop_windows.screenshot(pid, path)
	image = Image.open(path).convert("RGB")
	# <!-- custom: A hand-given --text-area without a layout counts as its own identity, being measured by whoever passes it; a layout needs its measured frame. (Claude Code Opus 5.5) -->
	readings = [(key, area) + area_reading(image, area) + ((layout is None) or ("frame" in layout and frame_found(image, layout["frame"])),) for key, layout, area in candidates]
	verdict, detail = decide_box(readings)
	if verdict == "UNKNOWN":
		sys.exit("cannot identify the %s message box: %s; it may hold a very short draft, or the zoom, the window size or an app update has moved it; screenshot it, and if it moved, measure its layout in app_layouts.json" % (app, detail))
	key, layout, area = candidates[detail]
	return key, layout, area, readings[detail][2], verdict


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


def open_codex_thread(thread, settle):
	# <!-- custom: A freshly started Codex shows its home screen, a new chat, so a message sent there would start a new conversation rather than reach the thread the agents were using (seen on 2026-11-15).
	# The app registers codex://threads/<id>, found in its bundle, and the ID is the session ID ending each rollout log's name.
	# The thread is named by its sidebar title, from ~/.codex/session_index.jsonl (one row per naming, so the last row for an ID wins), or by ID: the user pointed out that the newest log need not be the wanted thread, as a side question in another chat would move that one up; 'latest' stays for when it is. (Claude code Opus 5.5) -->
	if not re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-", thread) and thread != "latest":
		names = {}
		for line in (Path.home() / ".codex" / "session_index.jsonl").read_text(encoding="utf-8").splitlines():
			if line.strip():
				row = json.loads(line)
				names[row["id"]] = row.get("thread_name") or ""
		exact = [i for i, n in names.items() if n.lower() == thread.lower()]
		found = exact or [i for i, n in names.items() if thread.lower() in n.lower()]
		if len(found) != 1:
			sys.exit("Codex thread %r matches %s; pass more of its title or its ID" % (thread, ", ".join("%r (%s)" % (names[i], i) for i in found) or "no title"))
		print("Codex thread %r is %s" % (names[found[0]], found[0]))
		thread = found[0]
	if thread == "latest":
		root, pattern = SESSION_LOGS["codex"]
		newest = max(root.glob(pattern), key=lambda path: path.stat().st_mtime, default=None)
		if newest is None:
			sys.exit("no Codex session log under %s" % root)
		thread = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$", newest.name).group(1)
	subprocess.run(["cmd.exe", "/c", "start", "", "codex://threads/" + thread], check=True)
	print("opened Codex thread %s" % thread, flush=True)
	time.sleep(settle)


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


def reply_since(app, before, marker, seen=None):
	# <!-- custom: seen, when given, gets "arrived" set once our message shows in the log, so wait_reply can stop early when a send never landed. (Claude code Opus 5.5) -->
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
		if seen is not None and state["found"]:
			seen["arrived"] = True
		# <!-- custom: Codex's live test also found that a log ending right after Claude Code's final text kept waiting for one more record; a complete end_turn answer is enough. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
		if state.get("ending") and state["answer"]:
			return (True, state["answer"], state.get("later_message", False))
	return None


# <!-- custom: --wait-for first started from each log's current size, so it found only a message the app had not started yet; on 2026-11-19 Codex had already answered a review, and the wait sat on a reply that was already in its log.
# So start each log at the line holding the header when it is there, which finds an answered, running or queued message alike, and at its end otherwise. (Claude Code Opus 5.5) -->
def marker_offsets(app, marker):
	needles = [marker.encode("utf-8"), json.dumps(marker)[1:-1].encode("ascii")]
	offsets = {}
	for path, size in log_sizes(app).items():
		with path.open("rb") as stream:
			data = stream.read(size)
		# <!-- custom: The first match: Codex copies the message into a later "compacted" record, and starting there missed it. (Claude Code Opus 5.5) -->
		hits = [i for i in [data.find(needle) for needle in needles] if i >= 0]
		found = min(hits) if hits else -1
		offsets[path] = (data.rfind(b"\n", 0, found) + 1) if found >= 0 else size
	return offsets


def wait_reply(app, before, marker, timeout, arrival_timeout=120):
	# <!-- custom: On 2026-11-11 Claude Code waited for a Codex review with a shell loop on the newest log, so neither agent nor user had to check Codex's window or guess how long to wait; this keeps that loop, and works the other way for Codex waiting on Claude Code. (Claude Code Opus 5.5) -->
	# <!-- custom: The reply wait used to watch only for the turn's end, so a message that never reached the app looked like a slow reply: on 2026-11-17 a paste went to the user's window instead of Codex and the wait ran its full 30 minutes.
	# So the message itself must appear in the app's log within arrival_timeout, 2 minutes by default, as an app logs a message it receives at once; otherwise the wait stops and says the send did not arrive. (Claude code Opus 5.5) -->
	start = time.time()
	deadline = start + timeout
	seen = {"arrived": False}
	while time.time() < deadline:
		result = reply_since(app, before, marker, seen)
		if result is not None:
			return result
		if arrival_timeout is not None and not seen["arrived"] and time.time() - start > arrival_timeout:
			return "NOT_ARRIVED"
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
	parser.add_argument("--start", action="store_true", help="open the target app first if it has no window (from its launch ID in app_layouts.json), then send; with no message, only open it")
	parser.add_argument("--start-timeout", type=int, default=60, help="seconds to wait for the started app's window")
	parser.add_argument("--start-settle", type=int, default=8, help="seconds to wait after the window appears, before its message box takes text")
	parser.add_argument("--positions", help="after --start, restore this saved desktop layout (desktop_windows.py positions list)")
	parser.add_argument("--thread", help="Codex only: open this thread before sending, by its sidebar title (or a unique part of it), its session ID, or latest for the thread last written to; a freshly started Codex otherwise shows a new chat")
	parser.add_argument("--arrival-timeout", type=int, default=120, help="stop waiting if the message has not appeared in the target app's log after this many seconds, as when the send did not land; not applied with --queue")
	parser.add_argument("--wait-for", metavar="HEADER", help='send nothing; wait for the reply to a queued message already sent, given by its header, e.g. "[Claude Code Opus 5.5 · 2026-11-18 13:54:43.765 UTC]"')
	args = parser.parse_args()
	# <!-- custom: The header's middle dot printed as a replacement character in a cp1252 console.
	# It runs before --wait-for, which Codex's 2026-11-18 review showed raised UnicodeEncodeError on a reply holding a check mark when it returned earlier. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	if args.wait_for:
		# <!-- custom: On 2026-11-18 a --queue send's wait stopped after 2 minutes, saying the message did not reach Codex, although it sat in Codex's queue: an app logs a queued message only when it starts on it, so the arrival check does not apply to one, and resending to wait again would have queued it twice.
		# This picks up the wait for a message already sent, queued or not. (Claude Code Opus 5.5) -->
		if not args.to:
			parser.error("--wait-for needs --to")
		name = {"codex": "Codex", "claude": "Claude Code"}[args.to]
		print("waiting for %s to end the turn holding %s..." % (name, args.wait_for), flush=True)
		result = wait_reply(args.to, marker_offsets(args.to, args.wait_for), args.wait_for, args.wait_timeout, None)
		if result is None:
			sys.exit("no reply from %s within %d seconds" % (name, args.wait_timeout))
		if result[1] is None:
			sys.exit("%s ended the turn holding this message without a final answer" % name)
		print("=== %s REPLY ===" % name.upper())
		print(result[1])
		return
	if args.start:
		if not args.to:
			parser.error("--start needs --to")
		start_app(args.to, args.start_timeout, args.start_settle, args.positions)
	if args.thread:
		if args.to != "codex":
			parser.error("--thread is for --to codex")
		open_codex_thread(args.thread, 3)
	if (args.start or args.thread) and args.text is None and not args.file and not args.check_box:
		return
	if args.check:
		problems = check(args.check.read_text(encoding="utf-8"))
		print("\n".join(problems) if problems else "clean: nothing outside the header and closing tag")
		sys.exit(1 if problems else 0)
	if args.check_box:
		# <!-- custom: Lets an agent confirm the picked layout and the empty-box reading, for example after moving a window, without sending anything. (Claude Code Opus 5.5) -->
		if not args.to:
			parser.error("--check-box needs --to")
		pid = find_pid(APPS[args.to]["process"])
		reading = read_box(args.to, pid, args.layout, args.text_area)
		if reading is None:
			sys.exit("no layout in app_layouts.json matches the %s window's width; pass --layout or --text-area, or measure the window and add its layout there" % args.to)
		layout_name, _layout, _area, dark, verdict = reading
		print("%s (pid %d): layout %s, %d dark pixels in the text area, %s" % (args.to, pid, layout_name, dark, "empty" if verdict == "EMPTY" else "not empty"))
		# <!-- custom: Was "verdict == 'EMPTY' and 0 or 1", a Python 2.4 idiom that always gave 1, as 0 is false; Codex's review (GPT-6.2-Sol) caught it. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
		sys.exit(0 if verdict == "EMPTY" else 1)
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
	# <!-- custom: The box is read after the idle wait, from the same screenshot that picks the layout, so the reading is as fresh as it can be before the paste. (Claude Code Opus 5.5) -->
	reading = read_box(args.to, pid, args.layout, args.text_area)
	if reading is None or (reading[1] is None and not args.box):
		sys.exit("no layout in app_layouts.json matches the %s window's width; pass --layout, or --box and --text-area after a screenshot, and add the measured layout there" % args.to)
	layout_name, layout, _area, dark, verdict = reading
	box = tuple(args.box or layout["box"])
	print("layout: %s" % layout_name)
	if verdict != "EMPTY":
		sys.exit("the %s message box is not empty (%d dark pixels): someone may be typing there; not sending" % (args.to, dark))
	before = log_sizes(args.to) if args.wait_reply else None
	# <!-- custom: paste stops when the target loses focus during the click, paste and Enter; say what happened rather than show a traceback. (Claude Code Opus 5.5) -->
	try:
		desktop_windows.paste(pid, box[0], box[1], message, "ctrl+enter" if args.queue else "enter")
	except RuntimeError as error:
		sys.exit("not sent to %s: %s; send again once the user is idle" % (args.to, error))
	print("sent to %s (pid %d):" % (args.to, pid))
	print(message)
	print("Check the sent message: anything before its header or after its closing tag was not yours.")
	# <!-- custom: On 2026-11-19 a review went to Codex with --reply "Claude app" and no --wait-reply; Codex answered in its own window and nothing woke the sender, so the user wondered why no reply came.
	# Name the header to wait on, since the reply is otherwise read only by someone who looks. (Claude Code Opus 5.5) -->
	if not args.wait_reply and args.reply != "none needed":
		print('Nothing waits for the reply: run again with --wait-for "%s" in the background to be woken when it ends.' % message[:message.index(" UTC]") + 5])
	if args.wait_reply:
		name = {"codex": "Codex", "claude": "Claude Code"}[args.to]
		print("waiting for %s to end the turn holding this message..." % name, flush=True)
		# <!-- custom: A queued message is logged only when the app starts on it, which can be long after the send, so it gets no arrival check. (Claude Code Opus 5.5) -->
		result = wait_reply(args.to, before, message[:message.index(" UTC]") + 5], args.wait_timeout, None if args.queue else args.arrival_timeout)
		if result == "NOT_ARRIVED":
			sys.exit("the message did not reach %s: it was not in its log after %d seconds, so check its window and where the paste went" % (name, args.arrival_timeout))
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

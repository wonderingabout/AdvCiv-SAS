#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Follows a SASPilot command log (Logs/SASPilot_<processStartUtc>_<pid>.jsonl, written by SASPilotClient.py) like tail -f, one readable line per command, so a person can watch an agent play in a terminal tab, as a game console shows commands scroll by (the user's idea, 2026-11-14).
# By default only orders are shown, with their turn and the agent's note=; --all adds the reads, which are most of the commands. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, json the log lines, subprocess and sys open the --window console, time the polling, Path the log folder. (Claude code Opus 5.5) -->
import argparse
from importlib import import_module
import json
# <!-- custom: os for the console's own PID, written to <log>.watch. (Claude code Opus 5.5) -->
import os
import subprocess
import sys
import time
from pathlib import Path

# <!-- custom: format_json from the formatting helpers lays out --pretty results as the UI map files are. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# <!-- custom: desktop_windows for --window, from LLM_Helpers/desktop since 2026-11-15. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
format_json = import_module("formatting.json_format").format_json
# <!-- custom: console_colors, from the same folder, holds the shared palette and to_html for --html. (Claude code Opus 5.5) -->
console_colors = import_module("formatting.console_colors")

# <!-- custom: The same folder pilot.LOGS_DIR names, computed here so the watcher starts without importing the client. (Claude code Opus 5.5) -->
LOGS_DIR = Path.home() / "Documents" / "My Games" / "beyond the sword" / "Logs"


def newest_log(pid):
	# <!-- custom: With a running client, its own log, named by its start time as pilot.log_path names it: the newest file of a PID could belong to an earlier process that had the same PID (Codex's review).
	# None until that log exists. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if pid:
		ticks = process_instance(pid)
		if ticks is not None:
			started = time.strftime("%Y%m%dT%H%M%S", time.gmtime(ticks / 10000000.0 - 11644473600))
			own = LOGS_DIR / ("SASPilot_%s_%d.jsonl" % (started, pid))
			return own if own.exists() else None
	pattern = "SASPilot_*_%d.jsonl" % pid if pid else "SASPilot_*.jsonl"
	logs = sorted(LOGS_DIR.glob(pattern), key=lambda path: path.stat().st_mtime)
	return logs[-1] if logs else None


def process_instance(pid):
	# <!-- custom: The running process's creation time (FILETIME ticks), or None when it has ended or cannot be opened: the PID alone could be reused by a new process, which would keep the watcher on a dead client's log (Codex's review), so the watcher compares this value with the one it saw at start.
	# STILL_ACTIVE is 259. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	import ctypes
	from ctypes import wintypes
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	kernel32.OpenProcess.restype = wintypes.HANDLE
	handle = kernel32.OpenProcess(0x1000, False, pid)
	if not handle:
		return None
	try:
		code = wintypes.DWORD()
		if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != 259:
			return None
		times = [wintypes.FILETIME() for _ in range(4)]
		if not kernel32.GetProcessTimes(handle, *[ctypes.byref(t) for t in times]):
			return None
		return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
	finally:
		kernel32.CloseHandle(handle)


def short(value, limit):
	# <!-- custom: limit 0 keeps the whole text: the user found results and arguments cut with "..." in the console and wanted them whole by default, cutting only for those who prefer it (2026-11-14).
	# The log itself keeps at most pilot.LOG_RESULT_CHARS of a result. (Claude code Opus 5.5) -->
	text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
	if limit <= 0 or len(text) <= limit:
		return text
	return text[:limit - 3] + "..."


# <!-- custom: Colors for the human view, so an error stands out among hundreds of lines: errors red and game and operator banners yellow, then, by the user's choice the same day, results sky blue, the agent's notes bright white, then bold orchid when the user asked for them to stand out, and 'py' code light green (2026-11-14).
# Off unless main enables them for a console; the log itself stays plain JSON.
# The palette lives in formatting/console_colors.py, shared with other helpers at the user's request. (Claude code Opus 5.5) -->
_style = {}


def _learn_operator(record):
	# <!-- custom: An operator's number, from its operator row, keyed as pilot._log_request keys it: by session when there is one, else by name. (Claude code Opus 5.5) -->
	args = record.get("args") or {}
	if args.get("number"):
		_style.setdefault("numbers", {})[args.get("session") or args.get("operator")] = args["number"]


def _operator_number(record):
	return _style.get("numbers", {}).get(record.get("operatorSession") or record.get("operator"), "?")


def _count(record, kind):
	# <!-- custom: "#00013 (op6)": one number per kind that rises down the screen, then the operator.
	# The first per-operator form, "6.3" for operator 6's third note, restarted at 1 for each operator, so the numbers did not rise down the screen, which the user read as backward (2026-11-14); each line already names its operator in the op column.
	# Zero-padded to five digits, as the request numbers are, so the numbers sort and grep exactly ("why #00013" does not also match #000130), the user's idea.
	# The operator rows read before the watcher's start (see main) give the numbers of operators that joined earlier. (Claude code Opus 5.5) -->
	_style[kind] = _style.get(kind, 0) + 1
	return "#%05d (op%s)" % (_style[kind], _operator_number(record))


def paint(text, role):
	return console_colors.paint(text, role)


def emit(text):
	# <!-- custom: A line for the console, or for the page when --html collects them. (Claude code Opus 5.5) -->
	if "html" in _style:
		_style["html"].append(text)
	else:
		print(text, flush=True)


def format_record(record, width, pretty=False, max_lines=40, inline_width=140):
	# <!-- custom: The row SASPilotClient.py writes when a game starts or is loaded, shown as a banner so each game's commands are set apart; see pilot.log_game_marker. (Claude code Opus 5.5) -->
	# <!-- custom: Banners begin with the row's time like other lines: an operator can join long before its first order or leave long after its last, which the banner alone did not show (the user, 2026-11-14). (Claude code Opus 5.5) -->
	when = "%-12s " % record.get("utc", "")[11:23].rstrip("Z")
	if record.get("kind") == "game":
		args = record.get("args") or {}
		banner = when + "=== game %s: %s (map %s, turn %s) ===" % (args.get("event"), args.get("save") or "new game", args.get("map"), args.get("gameTurn"))
		# <!-- custom: The recommended-settings check that 'start' runs, so the console shows it too; rows from before it was added carry none. (Claude code Opus 5.5) -->
		if args.get("settingsError"):
			banner += "\n    " + paint("settings check failed: " + args["settingsError"], "error")
		elif args.get("settingsChecked") is not None:
			unset = args.get("settingsNotSet") or []
			settings = "settings: %d recommended, %s" % (args["settingsChecked"], unset and "%d not set: %s" % (len(unset), ", ".join(unset)) or "all set")
			banner += "\n    " + (unset and paint(settings, "error") or settings)
		return paint(banner, "banner")
	# <!-- custom: The row SASPilotClient.py writes when an operator first sends a command to this client, or says it leaves; see pilot._log_request. (Claude code Opus 5.5) -->
	if record.get("kind") == "operator":
		args = record.get("args") or {}
		# <!-- custom: The session's first 8 characters tell two sessions of one agent apart, as a Claude Code session ID begins its log's file name. (Claude code Opus 5.5) -->
		session = args.get("session")
		# <!-- custom: Operators present, counted from the join and leave rows in order, as the user asked for the current total on each operator row (2026-11-14); an operator that just stops still counts as present. (Claude code Opus 5.5) -->
		present = _style.setdefault("present", {})
		present[session or args.get("operator")] = args.get("event") != "left"
		_learn_operator(record)
		args = dict(args)
		args["total"] = "%s, %d present" % (args.get("total") or len(present), len([key for key in present if present[key]]))
		return paint(when + "=== operator %s %s: %s%s%s ===" % (args.get("number") or "?", args.get("event"), args.get("operator"), session and " (session %s)" % session[:8] or "", args.get("total") and ", operators: %s" % args["total"] or ""), "banner")
	turn = record.get("turn")
	# <!-- custom: The UTC time of day to the millisecond, as SASPilotClient.py writes it; older lines written to the second show without one. (Claude code Opus 5.5) -->
	# <!-- custom: T<turn>-<n>, the request's number within its turn, which SASPilotClient.py writes; lines from before the numbering show T<turn> alone. (Claude code Opus 5.5) -->
	# <!-- custom: The turn zero-padded to four digits, T0068, so lines sort and grep by turn ("T0068-" matches turn 68 only, not 680), the user's idea (2026-11-14); four as a Marathon game passes 1,000 turns. (Claude code Opus 5.5) -->
	number = "T%s" % ("?" if turn is None else "%04d" % turn)
	if record.get("n") is not None:
		number += "-%05d" % record["n"]
	# <!-- custom: Each line names its operator by number, op1, op2, as the user asked whether every command should say who sent it (2026-11-14); the log row holds the name and session, the banner when it joined says which is which.
	# op?
	# for a row from no known operator. (Claude code Opus 5.5) -->
	operator = "op%s" % _operator_number(record)
	head = "%-12s %s %-4s %-5s %s" % (record.get("utc", "")[11:23].rstrip("Z"), number, operator, record.get("kind", ""), record.get("cmd", ""))
	args = record.get("args") or {}
	if args:
		# <!-- custom: Code of several lines is shown as a block under the command, as the user saw a multi-line 'py' print its first line after code= and run its other lines into the following ones (2026-11-14). (Claude code Opus 5.5) -->
		code_block = []
		parts = []
		for (key, value) in sorted(args.items()):
			if key == "code" and record.get("cmd") == "py" and isinstance(value, str) and "\n" in value:
				# <!-- custom: The log keeps the whole code, the record of what a 'py' order did and where a snippet worth a command shows up; the console, the user's view, shows its first line unless --code, as the user asked whether code was needed there (2026-11-14). (Claude code Opus 5.5) -->
				if _style.get("code"):
					code_block = value.splitlines()
					parts.append("code=(%d lines below)" % len(code_block))
				else:
					parts.append("code=" + paint(value.splitlines()[0], "code") + " (+%d lines; shown without --short-code)" % (len(value.splitlines()) - 1))
			elif key == "code" and record.get("cmd") == "py":
				# <!-- custom: A long one-line snippet filled the console too, so without --code it is cut at 100 characters, like a multi-line one at its first line.
				# Each 'py' call sends its whole code; a snippet that keeps coming back becomes a command instead, as 'map' and 'scout' did. (Claude code Opus 5.5) -->
				limit = width and 40
				if not _style.get("code"):
					limit = 100
				parts.append("code=" + paint(short(value, limit), "code"))
			else:
				parts.append("%s=%s" % (key, short(value, width and 40)))
		head += " " + " ".join(parts)
	else:
		code_block = []
	lines = [head] + [paint("      | " + line, "code") for line in code_block]
	if record.get("note"):
		# <!-- custom: Notes are numbered from the watcher's start like errors, "why #12", so a reason can be pointed at without counting; the user asked for an automatic number rather than one the agent writes (2026-11-14). (Claude code Opus 5.5) -->
		# <!-- custom: Then with the operator, "why #00012 (op2)", as several agents may pilot one client (the user, 2026-11-14); see _count. (Claude code Opus 5.5) -->
		lines.append(paint("    why %s: %s" % (_count(record, "notes"), record["note"]), "note"))
	if not record.get("ok"):
		# <!-- custom: Errors are numbered from the watcher's start, so "ERROR #3" says how many came before it without counting by eye; with the operator like notes, "ERROR #00003 (op6)". (Claude code Opus 5.5) -->
		lines[0] = paint(lines[0], "error")
		lines.append(paint("    ERROR %s: %s" % (_count(record, "errors"), short(record.get("error") or "", width)), "error"))
	elif "result" in record:
		# <!-- custom: --pretty prints a result as indented JSON, cut at max_lines: a nested result such as 'workers city=Hippo' read as one long line (the user, 2026-11-14). A result the log cut at 1,500 characters is a string and prints as it is.
		# The log itself stays one JSON object per line, as agents are its main readers and grep or parse it line by line; the console is the human view, one line per command unless --pretty. (Claude code Opus 5.5) -->
		result = record["result"]
		# <!-- custom: A text map ('map', 'routes') prints as the picture it is, one map row per line: in one JSON line its rows ran together, unreadable (2026-11-14).
		# The other fields stay on the first line. (Claude code Opus 5.5) -->
		if isinstance(result, dict) and isinstance(result.get("rows"), list) and all(isinstance(row, str) for row in result["rows"]):
			rest = dict((key, value) for (key, value) in result.items() if key != "rows")
			lines.append(paint("    -> " + short(rest, width), "result"))
			lines.extend([paint("       " + row, "result") for row in result["rows"]])
		elif pretty and not isinstance(record["result"], str):
			# <!-- custom: The shared formatter keeps short rows together and uses inline_width for the console. (Claude code Opus 5.5) -->
			body = format_json(record["result"], 1, inline_width).splitlines()
			if max_lines > 0 and len(body) > max_lines:
				body = body[:max_lines] + ["... (%d more lines)" % (len(body) - max_lines)]
			lines.append(paint("    -> " + body[0], "result"))
			lines.extend([paint("       " + line, "result") for line in body[1:]])
		else:
			lines.append(paint("    -> " + short(record["result"], width), "result"))
	return "\n".join(lines)


def console_window():
	# <!-- custom: This console's own window: a classic console window belongs to its console host, not to this Python, so a lookup by os.getpid() is not reliable (Codex's review).
	# None when there is no visible one, as under a pseudoconsole, and then nothing is moved. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	import ctypes
	hwnd = ctypes.windll.kernel32.GetConsoleWindow()
	if not hwnd or not ctypes.windll.user32.IsWindowVisible(hwnd):
		return None
	return hwnd


def arrange(civ_pid, console_hwnd, slot, slots, monitor):
	# <!-- custom: One horizontal band per piloted client, top to bottom: its Civ4 at its own size in the band's top-left corner (shrunk only to fit the band), its watcher console filling the rest of the band to the right.
	# First set up on 2026-11-14 at the user's 3840x2160 monitor (work area 3840x2100, taskbar excluded) with a 1920x1110 Civ4 window: halving the screen had stretched Civ4 to 1920x2100, which the user called a "monster chicken", and they wanted Civ4 untouched and the console stretched.
	# Two bands are meant for two clients side by side (`multiple`); other resolutions were not tried. (Claude code Opus 5.5) -->
	import desktop_windows
	areas = desktop_windows.monitors()
	left, top, right, bottom = areas[monitor - 1]
	band_height = (bottom - top) // slots
	band_top = top + band_height * slot
	frame = desktop_windows.visible_frame(civ_pid)
	civ_width = min(frame[2] - frame[0], right - left)
	civ_height = min(frame[3] - frame[1], band_height)
	desktop_windows.place_frame(civ_pid, left, band_top, left + civ_width, band_top + civ_height)
	desktop_windows.place_window(console_hwnd, left + civ_width, band_top, right, band_top + band_height)


def open_window(args):
	# <!-- custom: A console of its own, so the watcher is on the desktop rather than inside an app's terminal panel, which the user had to open to see it (2026-11-14).
	# The child arranges itself once its console exists, as only then does it have a window. (Claude code Opus 5.5) -->
	child = [sys.executable, str(Path(__file__).resolve())] + [item for item in sys.argv[1:] if item != "--window"] + ["--arrange-self"]
	process = subprocess.Popen(child, creationflags=subprocess.CREATE_NEW_CONSOLE)
	print("SASPilotConsole opened, process %d" % process.pid)
	return 0


def main():
	parser = argparse.ArgumentParser(description="SASPilotConsole follows a SASPilot command log to print each order with its turn and note. Examples: SASPilotConsole.py; SASPilotConsole.py --all; SASPilotConsole.py --pid 23768 --from-start; SASPilotConsole.py --window --pid 23768 (own console, laid out beside Civ4)")
	parser.add_argument("log", nargs="?", help="a SASPilot_*.jsonl log; default the newest in the Civ4 Logs folder, or the newest of --pid")
	parser.add_argument("--pid", type=int, help="follow this client's newest log")
	parser.add_argument("--all", action="store_true", help="show reads too, not only orders")
	parser.add_argument("--from-start", action="store_true", help="print the log from its beginning instead of only new lines")
	parser.add_argument("--once", action="store_true", help="print what the log holds and exit, without following it")
	parser.add_argument("--pretty", action="store_true", help="print results as indented JSON instead of one line")
	parser.add_argument("--inline-width", type=int, default=140, help="--pretty: keep a collection on one line when it fits this many characters (default 140)")
	parser.add_argument("--max-lines", type=int, default=40, help="--pretty: cut a result after this many lines (default 40; 0 for no limit)")
	parser.add_argument("--width", type=int, default=0, help="cut results and errors to this many characters, and arguments to 40; default 0 shows them whole")
	parser.add_argument("--window", action="store_true", help="open the watcher in a console of its own and lay it out with --pid's Civ4: Civ4 at its size top-left in its band, the console filling the rest")
	parser.add_argument("--slot", type=int, default=1, help="--window: this client's band, from the top (default 1)")
	parser.add_argument("--slots", type=int, default=1, help="--window: how many bands to split the monitor into, one per client (default 1; 2 for two clients)")
	parser.add_argument("--monitor", type=int, default=1, help="--window: the monitor, 1 the leftmost (default 1)")
	parser.add_argument("--no-color", action="store_true", help="plain text, without the colors a console otherwise gets (errors red, banners yellow, results sky blue, notes bold orchid, code light green)")
	parser.add_argument("--short-code", action="store_true", help="cut 'py' code: a multi-line one to its first line, a long line to 100 characters; by default the whole code is shown, multi-line code as a block")
	parser.add_argument("--html", help="write the whole log, as the console shows it with colors, to this HTML file and exit, e.g. for documentation; takes --all, --pretty and --width")
	parser.add_argument("--arrange-self", action="store_true", help=argparse.SUPPRESS)
	args = parser.parse_args()
	if args.window:
		if not args.pid:
			parser.error("--window needs --pid, the Civ4 to lay out beside")
		return open_window(args)
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	# <!-- custom: Whole code by default: the user found the cut code lost "a lot of substance", as the code tells what a 'py' order did (2026-11-14); --short-code cuts it. (Claude code Opus 5.5) -->
	_style["code"] = not args.short_code
	# <!-- custom: --html reads the whole log once, with colors on whatever the console, and writes the page instead of printing (the user, 2026-11-14: "now it's super easy to doc"). (Claude code Opus 5.5) -->
	if args.html:
		args.once = True
		args.from_start = True
		console_colors.set_enabled(True)
		_style["html"] = []
	elif not args.no_color:
		console_colors.enable()
	if args.arrange_self:
		try:
			# <!-- custom: The console is resolved before Civ4 is moved, so a console that cannot be placed leaves Civ4 where it was (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			hwnd = console_window()
			if hwnd is None:
				print("no visible console window; the windows were left as they were", file=sys.stderr)
			else:
				arrange(args.pid, hwnd, args.slot - 1, args.slots, args.monitor)
		except Exception as error:
			print("could not arrange the windows: %s" % error, file=sys.stderr)
	path = Path(args.log) if args.log else newest_log(args.pid)
	# <!-- custom: Without a log yet, wait for one, so the watcher can be started before the agent's first command; a log that appears meanwhile is read from its start, or its first line, written as the file was made, was skipped (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	waited = False
	while path is None:
		if args.once:
			print("no SASPilot log in %s" % LOGS_DIR, file=sys.stderr)
			return 1
		# <!-- custom: Likewise, a client that ends before writing any log ends the wait. (Claude code Opus 5.5) -->
		if args.pid and process_instance(args.pid) is None:
			print("Civ4 process %d is not running and wrote no SASPilot log" % args.pid, file=sys.stderr)
			return 1
		waited = True
		time.sleep(1.0)
		path = newest_log(args.pid)
	# <!-- custom: A console of its own says it is open in <log>.watch, its PID and creation time, which pilot.ensure_watcher reads to reopen a console that was closed: on 2026-11-14 the user could not find the console, which had ended with the agent's session while Civ4 ran on (the user asked for it to start with the pilot). (Claude code Opus 5.5) -->
	if args.arrange_self and args.pid:
		try:
			path.with_suffix(".watch").write_text(json.dumps({"pid": os.getpid(), "instance": process_instance(os.getpid()), "slot": args.slot, "slots": args.slots}), encoding="ascii")
		except OSError as error:
			print("could not write %s: %s" % (path.with_suffix(".watch"), error), file=sys.stderr)
	# <!-- custom: A header saying what this console is: it opened with only "following <log>" and a date line, which the user found unclear (2026-11-14).
	# The full UTC start time, the watcher's own command line as run (interpreter, script and arguments), the log and the Civ4 process with its start time, as the log's name holds. (Claude code Opus 5.5) -->
	started = time.time()
	# <!-- custom: Named SASPilotConsole, one word as the user asked, the name the SASPilot Guide uses for the window people watch (2026-11-14): its title bar showed only the path to python.exe, so with two clients open nothing told which console was whose.
	# The script, first pilot_watch.py, became pilot_console.py the same day, lowercase like the pilot.py and pilot_scout.py of then, as a CamelCase name beside SASPilotCommands.py, the one in-game file Civ4 hot-reloads, could read as another in-game file.
	# On 2026-11-15 the user asked for it to carry the window's name, SASPilotConsole.py, so the script, the title bar and the guide match; the other desktop scripts followed as SASPilot<Role>.py in their own LLM_Helpers/saspilot folder, which Civ4 never loads.
	# They start with a shebang and argparse, unlike SASPilotCommands.py. (Claude code Opus 5.5) -->
	if os.name == "nt":
		import ctypes
		ctypes.windll.kernel32.SetConsoleTitleW(u"SASPilotConsole - Civ4 client %s" % (args.pid or "newest"))
	print("=== SASPilotConsole started %s.%03dZ ===" % (time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(started)), int(started * 1000) % 1000), file=sys.stderr)
	print("command: %s" % subprocess.list2cmdline([sys.executable, str(Path(__file__).resolve())] + sys.argv[1:]), file=sys.stderr)
	print("log:     %s" % path, file=sys.stderr)
	if args.pid:
		print("client:  Civ4 process %d, started %s UTC (from the log's name)" % (args.pid, path.stem.split("_")[1] if path.stem.count("_") >= 2 else "?"), file=sys.stderr)
	# <!-- custom: "filter:" was "shows:", which the user read as the arguments (2026-11-14); it is which lines are printed. (Claude code Opus 5.5) -->
	print("filter:  %s" % ("every command" if args.all else "orders, errors, and game and operator banners; --all adds reads"), file=sys.stderr)
	# <!-- custom: The recommended-settings check, here as well as on the game banner: a game started before the banner carried it never showed it, and the user looked for it at the console's start (2026-11-14).
	# SASPilotClient.py is imported only for this. (Claude code Opus 5.5) -->
	try:
		import SASPilotClient as pilot
		rows = pilot.settings_check()
		unset = ["%s=%s (recommended %s)" % (row["name"], row["current"], row["recommended"]) for row in rows if not row["ok"]]
		settings = "settings: %d recommended, %s" % (len(rows), unset and "%d not set: %s" % (len(unset), ", ".join(unset)) or "all set")
		print(unset and paint(settings, "error") or settings, file=sys.stderr)
	except Exception as error:
		print(paint("settings: check failed: %s" % error, "error"), file=sys.stderr)
	# <!-- custom: The columns are named once here, as the user did not see the row's kind in "12:47:35.192 T35-00016 order py": it is the third column, unlabelled (2026-11-14). (Claude code Opus 5.5) -->
	print("columns: UTC time, T<turn>-<request in turn>, op<operator number> (see the operator banners), kind (read or order), command, arguments; then why #<n> (op<operator>): (the agent's note), -> (the result) or ERROR #<n> (op<operator>)", file=sys.stderr)
	with open(path, encoding="utf-8", errors="replace") as handle:
		if not (args.from_start or args.once or waited):
			# <!-- custom: The lines skipped still hold the operator rows, read here for the numbers alone, so a note from an operator that joined before this console opened shows "why 1.3", not "why ?.3". (Claude code Opus 5.5) -->
			for line in handle:
				if '"kind": "operator"' in line:
					try:
						_learn_operator(json.loads(line))
					except ValueError:
						pass
		pending = ""
		last_date = None
		idle_polls = 0
		instance = args.pid and process_instance(args.pid)
		while True:
			chunk = handle.readline()
			if not chunk:
				if args.html:
					# <!-- custom: Mode "x" refuses an existing file: passing the log itself as --html would have replaced the JSONL with HTML (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
					try:
						with open(args.html, "x", encoding="utf-8") as page:
							page.write(console_colors.to_html("\n".join(_style["html"]), "SASPilot log %s" % path.name))
					except FileExistsError:
						print("%s exists; choose a new file name" % args.html, file=sys.stderr)
						return 1
					print("wrote %s (%d lines)" % (args.html, len(_style["html"])), file=sys.stderr)
					return 0
				if args.once:
					return 0
				# <!-- custom: A watcher outlived its Civ4: on 2026-11-14 two watcher consoles were open, one still following client 31664 half an hour after it had closed, as nothing told the watcher; each relaunch with --watch then added a console.
				# With --pid, check every 5 s of quiet that the client still runs, and end with it. (Claude code Opus 5.5) -->
				idle_polls += 1
				if args.pid and idle_polls % 20 == 0 and (instance is None or process_instance(args.pid) != instance):
					print("Civ4 process %d has ended; the watcher stops" % args.pid, flush=True)
					# <!-- custom: A console of its own closes with the process, so the line stays readable a few seconds first. (Claude code Opus 5.5) -->
					if args.arrange_self:
						time.sleep(5.0)
					return 0
				time.sleep(0.25)
				continue
			idle_polls = 0
			# <!-- custom: A line read while SASPilotClient.py is still appending it has no newline yet; keep it until the rest arrives. (Claude code Opus 5.5) -->
			pending += chunk
			if not pending.endswith("\n"):
				continue
			line, pending = pending.strip(), ""
			if not line:
				continue
			try:
				record = json.loads(line)
			except ValueError:
				continue
			if args.all or record.get("kind") != "read" or not record.get("ok"):
				# <!-- custom: Lines show the time only, so a date line marks each new UTC day; a game played over days stays readable (the user, 2026-11-14). (Claude code Opus 5.5) -->
				date = record.get("utc", "")[:10]
				if date and date != last_date:
					# <!-- custom: Named like the other banners (=== game, === operator), so grep '=== date' finds the day changes; it was the one unnamed === line (the user, 2026-11-14). (Claude code Opus 5.5) -->
					emit("=== date %s (UTC) ===" % date)
					last_date = date
				emit(format_record(record, args.width, args.pretty, args.max_lines, args.inline_width))


if __name__ == "__main__":
	raise SystemExit(main())

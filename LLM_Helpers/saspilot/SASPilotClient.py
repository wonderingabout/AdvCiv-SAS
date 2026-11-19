#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Command-line client of SASPilot, the in-game bridge in Assets/Python/SASPilot.py: reads and drives a running Civ4 through JSON requests instead of screenshots and clicks.
# A request is a file req_<id>.json in the game's mailbox folder SASPilot/<pid>, written whole and renamed into place; the game answers with rep_<id>.json on its next frame.
# See _1_AdvCiv-SAS/Docs/Modding_Resources/README_SASPilot.md for the commands and what was tried. (Claude code Fable 5.2 + Opus 5.5) -->

# <!-- custom: argparse reads the options, json the requests and replies, os and time the mailbox files and waits, sys the exit codes, uuid the request IDs, Path the folders. (Claude code Fable 5.2) -->
import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

# <!-- custom: run_autoplay from game_runs and desktop_windows from desktop, imported where used: on 2026-11-15 SASPilot's files moved to their own LLM_Helpers/saspilot folder, as the user saw piloting as a job of its own, and desktop_windows to LLM_Helpers/desktop. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "game_runs"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "desktop"))

# <!-- custom: desktop_windows launches and closes Civ4; run_autoplay writes the per-run INI and reads save headers. (Claude code Fable 5.2) -->
# <!-- custom: Both are imported only in the functions that need them: they took 18 of the 38 ms that importing this file cost, and every command starts a new Python (2026-11-13). (Claude code Opus 5.5) -->

# <!-- custom: The same folder as run_autoplay.USER_DIR, computed here so a plain request does not import run_autoplay. (Claude code Opus 5.5) -->
MAILBOX_ROOT = Path(os.environ["USERPROFILE"]) / "Documents" / "My Games" / "beyond the sword" / "SASPilot"
# <!-- custom: Replies at least this large are parsed and printed with orjson instead of the json module.
# On a Huge map's 1.6 MB plot reply the json module took 9 ms to parse and 58 ms to print indented, against 7 and 2 ms (2026-11-13); orjson costs about 27 ms to import, so small replies keep the json module. (Claude code Opus 5.5) -->
ORJSON_MIN_BYTES = 200000
# <!-- custom: How often the client looks for the reply.
# It was 0.02 s, which became most of the wait once the game served requests every frame; 0.001 s measured below 3 ms per ping (2026-11-13). (Claude code Opus 5.5) -->
POLL_SECONDS = 0.001


# <!-- custom: Per-client command log Logs/SASPilot_<processStartUtc>_<pid>.jsonl, one line per request: the user had nothing to watch while an agent played (replies are deleted once read), and a game reviewed later lacked the orders and their reasons to set beside SASGameRecord (2026-11-14).
# SASPilotConsole.py follows it. (Claude code Opus 5.5) -->
LOGS_DIR = MAILBOX_ROOT.parent / "Logs"
# <!-- custom: Commands that never change the game; a command with one of ORDER_ARGS is an order even so, e.g. 'espionage weight=' or 'fog on='. Everything else, 'py' included, is logged as an order, since it may change the game. (Claude code Opus 5.5) -->
READ_COMMANDS = frozenset(("help", "ping", "advise", "role", "demographics", "trainable", "bonustrade", "tech", "graph", "deals", "scores", "player", "players", "units", "unit", "cities", "city", "plot", "plots", "grid", "fog", "path", "targets", "wartargets", "messages", "todo", "info", "routes", "group", "diplo", "trade", "techs", "odds", "sites", "builds", "look", "finance", "domestic", "military", "relations", "espionage", "spy", "turn", "popups", "civics", "sliders", "religion", "types", "pedia", "citizens", "greatpeople", "workers", "map", "scout", "resources", "reminders", "research", "hurry", "freetech"))
# <!-- custom: Codex's review found 'popups held=' (it switches holding) and 'profile' (it can run any command repeatedly) logged as reads, and the query forms of 'research', 'hurry' and 'freetech' as orders. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
ORDER_ARGS = {"fog": ("on",), "espionage": ("weight",), "sliders": ("percent",), "citizens": ("automated",), "civics": ("set",), "religion": ("convert",), "popups": ("held",), "research": ("tech",), "hurry": ("hurry",), "freetech": ("tech",), "role": ("set",)}
# <!-- custom: A logged result longer than this is cut, so a 1.6 MB plot reply does not flood the log; its size is still recorded. (Claude code Opus 5.5) -->
LOG_RESULT_CHARS = 1500
# <!-- custom: Set by main for this invocation: the top-level command, so wait_for_turn's pings are not logged under 'endturn', and its note=, written on the first logged request only. (Claude code Opus 5.5) -->
_log_context = {"command": None, "note": None, "operator": None, "session": None}


class PilotError(Exception):
	pass


def _process_start_utc(pid):
	# <!-- custom: The same <processStartUtc>_<pid> naming as SASRuntime's per-process files (KI#1081), as a PID alone is reused by Windows; from GetProcessTimes, None if the process cannot be opened. (Claude code Opus 5.5) -->
	import ctypes
	from ctypes import wintypes
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	kernel32.OpenProcess.restype = wintypes.HANDLE
	handle = kernel32.OpenProcess(0x1000, False, pid)
	if not handle:
		return None
	try:
		times = [wintypes.FILETIME() for _ in range(4)]
		if not kernel32.GetProcessTimes(handle, *[ctypes.byref(t) for t in times]):
			return None
		ticks = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
		return time.strftime("%Y%m%dT%H%M%S", time.gmtime(ticks / 10000000.0 - 11644473600))
	finally:
		kernel32.CloseHandle(handle)


def log_path(pid):
	started = _process_start_utc(pid)
	if started is None:
		return None
	return LOGS_DIR / ("SASPilot_%s_%d.jsonl" % (started, pid))


def command_kind(command, args):
	if command not in READ_COMMANDS:
		return "order"
	for key in ORDER_ARGS.get(command, ()):
		if key in (args or {}):
			return "order"
	return "read"


def _log_request(pid, command, args, reply, error, kind=None):
	# <!-- custom: A failed log write never fails the command: the log is for watching and review, the command is the work. (Claude code Opus 5.5) -->
	# <!-- custom: The gate comes first: with SAS_PILOT_LOG=0 in the environment nothing is opened or formatted. The game never pays for this log, which the client writes. (Claude code Opus 5.5) -->
	# <!-- custom: Returns whether the line was written, which the explicit operator markers report (Codex's review); other callers ignore it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if os.environ.get("SAS_PILOT_LOG") == "0":
		return False
	if command == "ping" and _log_context["command"] != "ping":
		return False
	try:
		path = log_path(pid)
		if path is None:
			return False
		# <!-- custom: To the millisecond, as agent messages are timestamped: several commands land in one second, as when a city's queue gets two items (the user's request, 2026-11-14). (Claude code Opus 5.5) -->
		now = time.time()
		record = {"utc": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + ".%03dZ" % (int(now * 1000) % 1000), "cmd": command, "kind": kind or command_kind(command, args), "args": args or {}}
		# <!-- custom: Who sent the command, as several agents may pilot one client, such as Claude Code beside Codex instances (the user's idea, 2026-11-14): --operator or SAS_PILOT_OPERATOR, e.g. "Claude Code Opus 5.5".
		# Rows without one are left without the field rather than given a guess. (Claude code Opus 5.5) -->
		operator = _log_context["operator"]
		if operator:
			record["operator"] = operator
		# <!-- custom: The name alone would merge two sessions of the same agent and model, such as two Claude Code Opus 5.5 chats, which are different operators (the user, 2026-11-14).
		# So the agent's session ID goes with it, and name plus session is the operator's identity below; Claude Code's ID is also its session log's file name, which ties a row to its chat. (Claude code Opus 5.5) -->
		session = _log_context["session"]
		if session:
			record["operatorSession"] = session
		# <!-- custom: The note goes on the first order, or on the invoked command itself if that is a read: 'price' and 'endturn --turns' read the screen or the turn first, and the note landed on that read, which the watcher hides (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if _log_context["note"] and (record["kind"] == "order" or command == _log_context["command"]):
			record["note"] = _log_context["note"]
			_log_context["note"] = None
		if reply is not None:
			record["turn"] = reply.get("gameTurn")
			record["ok"] = bool(reply.get("ok"))
			record["ms"] = round(reply.get("roundTripMs", 0.0), 3)
			if reply.get("ok"):
				text = json.dumps(reply.get("result"), ensure_ascii=False, separators=(",", ":"))
				record["bytes"] = reply.get("replyBytes")
				# <!-- custom: A text map ('map', 'routes') keeps whole rows within the budget, with how many were left out, so the watcher can still draw it: cut as a string, a 70x40 map lost its rows (Codex reproduced it, 2026-11-14). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				result = reply.get("result")
				if len(text) > LOG_RESULT_CHARS and isinstance(result, dict) and isinstance(result.get("rows"), list):
					kept = dict((key, value) for (key, value) in result.items() if key != "rows")
					budget = LOG_RESULT_CHARS - len(json.dumps(kept, ensure_ascii=False))
					rows = []
					for row in result["rows"]:
						budget -= len(json.dumps(row, ensure_ascii=False)) + 1
						if budget < 0:
							break
						rows.append(row)
					kept["rows"] = rows
					kept["rowsOmitted"] = len(result["rows"]) - len(rows)
					record["result"] = kept
					record["truncated"] = True
				elif len(text) > LOG_RESULT_CHARS:
					record["result"] = text[:LOG_RESULT_CHARS]
					record["truncated"] = True
				else:
					record["result"] = reply.get("result")
			else:
				record["error"] = reply.get("error")
		else:
			record["ok"] = False
			record["error"] = error
		LOGS_DIR.mkdir(parents=True, exist_ok=True)
		# <!-- custom: Each request is numbered within its game turn (n) and within the log (seq), so the watcher can show T285-00012 and a line can be cited exactly: the user saw many rows in the same second (2026-11-14). seq is the exact reference, as a turn's numbers repeat after reloading an earlier turn.
		# Every SASPilotClient.py call is a new process, so the counters live in a small .seq file beside the log; a failed request takes the last turn.
		# Codex forced two calls to read the same counters and both wrote seq=9, so the .seq file is locked (msvcrt, one byte) from reading the counters to appending the line. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		import msvcrt
		descriptor = os.open(str(path.with_suffix(".seq")), os.O_RDWR | os.O_CREAT | os.O_BINARY)
		try:
			# <!-- custom: LK_LOCK retries for about 10 s and then raises, which the outer except turns into a skipped line rather than a stuck command. (Claude code Opus 5.5) -->
			msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
			try:
				os.lseek(descriptor, 0, 0)
				try:
					# <!-- custom: Read to the end: a single 4096-byte read would cut the JSON once the operator list outgrew it, and the ValueError below would then silently reset the counters and operators (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
					chunks = []
					while True:
						chunk = os.read(descriptor, 65536)
						if not chunk:
							break
						chunks.append(chunk)
					counters = json.loads(b"".join(chunks).decode("ascii"))
				except ValueError:
					counters = {"turn": None, "n": 0, "seq": 0}
				if record.get("turn") is None:
					record["turn"] = counters.get("turn")
				if record["turn"] != counters.get("turn"):
					counters["turn"] = record["turn"]
					counters["n"] = 0
				lines = []
				# <!-- custom: The first row from an operator not yet in this log is preceded by a row of kind "operator", "Operator 2 joined: <name>", numbered in order of arrival; operators are remembered in the .seq file, under the same lock, so two agents starting at once still get distinct numbers.
				# grep '"kind": "operator"' lists who piloted the client. (Claude code Opus 5.5) -->
				operators = counters.setdefault("operators", [])
				# <!-- custom: The session alone when there is one: the name can vary within a session (a call without SAS_PILOT_OPERATOR is named by the agent's kind), the session cannot. (Claude code Opus 5.5) -->
				identity = session or operator
				# <!-- custom: An explicit 'operator joined' registers the operator too: it first wrote an unnumbered join, and the operator's next command a second, numbered one (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if operator and identity not in operators and record["kind"] == "operator" and record["args"].get("event") == "joined":
					operators.append(identity)
				elif operator and identity not in operators and record["kind"] != "operator":
					operators.append(identity)
					counters["n"] += 1
					counters["seq"] += 1
					joined = {"utc": record["utc"], "cmd": "operator", "kind": "operator", "args": {"event": "joined", "operator": operator, "session": session, "number": len(operators), "total": len(operators)}, "operator": operator, "turn": record["turn"], "ok": True, "n": counters["n"], "seq": counters["seq"]}
					if session:
						joined["operatorSession"] = session
					lines.append(joined)
				if record["kind"] == "operator":
					# <!-- custom: How many operators this log has had, on each operator row, as the user asked for the total (2026-11-14). (Claude code Opus 5.5) -->
					record["args"]["total"] = len(operators)
					record["args"]["session"] = session
					record["args"]["number"] = (identity in operators and operators.index(identity) + 1) or None
				counters["n"] += 1
				counters["seq"] += 1
				record["n"] = counters["n"]
				record["seq"] = counters["seq"]
				lines.append(record)
				with open(path, "a", encoding="utf-8") as handle:
					for line in lines:
						handle.write(json.dumps(line, ensure_ascii=False) + "\n")
				os.lseek(descriptor, 0, 0)
				os.ftruncate(descriptor, 0)
				os.write(descriptor, json.dumps(counters).encode("ascii"))
				return True
			finally:
				os.lseek(descriptor, 0, 0)
				msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
		finally:
			os.close(descriptor)
	except Exception:
		return False


def list_operators(pid):
	# <!-- custom: 'operator list': every operator of this client's log, in order of arrival, with its join and leave times, so who piloted and when is one command away rather than a grep (the user, 2026-11-14).
	# left is null until 'operator left' is written; an agent that just stops shows its last command instead.
	# Read from the log, the record of what happened; the .seq file holds only the identities, for numbering. (Claude code Opus 5.5) -->
	path = log_path(pid)
	if path is None or not path.exists():
		raise PilotError("no command log for client %d" % pid)
	operators = {}
	with open(path, encoding="utf-8", errors="replace") as handle:
		for line in handle:
			try:
				record = json.loads(line)
			except ValueError:
				continue
			name = record.get("operator")
			session = record.get("operatorSession")
			if not name and not session:
				continue
			# <!-- custom: Keyed by session when there is one, as _log_request numbers them; the name shown is the fullest one seen, so "Claude Code Opus 5.5" wins over a bare "Claude Code". (Claude code Opus 5.5) -->
			key = session or name
			entry = operators.get(key)
			if entry is None:
				entry = operators[key] = {"number": None, "operator": name, "session": session, "joined": record.get("utc"), "left": None, "commands": 0, "lastCommand": None, "errors": 0, "lastError": None}
			if name and len(name) > len(entry["operator"] or ""):
				entry["operator"] = name
			if record.get("kind") == "operator":
				args = record.get("args") or {}
				if args.get("number"):
					entry["number"] = args["number"]
				if args.get("event") == "left":
					entry["left"] = record.get("utc")
				# <!-- custom: An explicit join after a leave is a return: Codex's joined, left, joined test still showed present 0. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				elif args.get("event") == "joined":
					entry["left"] = None
			# <!-- custom: Game markers are rows the client writes at a start or load, not the operator's commands (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			elif record.get("kind") == "game":
				continue
			else:
				entry["commands"] += 1
				entry["lastCommand"] = record.get("utc")
				# <!-- custom: Refused commands per operator, such as a 'py' snippet in Python 3 syntax, so an agent can see how often it erred and when last (the user, 2026-11-14). (Claude code Opus 5.5) -->
				if not record.get("ok"):
					entry["errors"] += 1
					entry["lastError"] = record.get("utc")
				# <!-- custom: A command after a 'left' means the operator came back, so it is shown as present again. (Claude code Opus 5.5) -->
				entry["left"] = None
	result = sorted(operators.values(), key=lambda entry: (entry["number"] is None, entry["number"] or 0, entry["joined"] or ""))
	return {"log": str(path), "count": len(result), "present": len([entry for entry in result if entry["left"] is None]), "operators": result}


def remind(args, failed):
	# <!-- custom: Reminders the agent gets with each command's output, so the user need not point these out every time (the user, 2026-11-14): an error, and a 'py' order, whose snippet may belong in a command (AGENTS.md); 'SASPilotClient.py review' gathers them.
	# Printed on stderr, which the agent's tool shows beside the reply. (Claude code Opus 5.5) -->
	if args.command == "py":
		print("pilot: reminder: a 'py' order; if a later game would ask this again, make it a command in SASPilotCommands.py rather than writing the code again (AGENTS.md). 'SASPilotClient.py review' lists this session's snippets.", file=sys.stderr)
	elif failed:
		print("pilot: reminder: 'SASPilotClient.py review' lists this session's errors and 'py' snippets.", file=sys.stderr)


def review(pid):
	# <!-- custom: 'SASPilotClient.py review': for this operator's session, its errors and its 'py' snippets grouped by code, most repeated first, from the client's log.
	# A snippet written more than once is the clearest case for a command; errors show what to fix in SASPilot or in how it is used. (Claude code Opus 5.5) -->
	path = log_path(pid)
	if path is None or not path.exists():
		raise PilotError("no command log for client %d" % pid)
	session = _log_context["session"]
	operator = _log_context["operator"]
	errors = []
	snippets = {}
	with open(path, encoding="utf-8", errors="replace") as handle:
		for line in handle:
			try:
				record = json.loads(line)
			except ValueError:
				continue
			if session and record.get("operatorSession") != session:
				continue
			if not session and record.get("operator") != operator:
				continue
			if record.get("kind") in ("game", "operator"):
				continue
			if not record.get("ok"):
				errors.append({"utc": record.get("utc"), "turn": record.get("turn"), "n": record.get("n"), "cmd": record.get("cmd"), "error": ((record.get("error") or "").splitlines() or [""])[0][:300]})
			if record.get("cmd") == "py":
				code = (record.get("args") or {}).get("code") or ""
				entry = snippets.setdefault(code, {"count": 0, "first": record.get("utc"), "last": None, "code": code})
				entry["count"] += 1
				entry["last"] = record.get("utc")
	grouped = sorted(snippets.values(), key=lambda entry: -entry["count"])
	return {"session": session, "operator": operator, "errors": len(errors), "errorList": errors[-20:], "pySnippets": sum([entry["count"] for entry in grouped]), "distinctSnippets": len(grouped), "snippets": grouped}


def health(pid, timeout):
	# <!-- custom: 'SASPilotClient.py health', the user's idea (2026-11-14): SASPilot's own state in one reply, gathered from 'ping' (the bridge's tick errors), the settings check, 'review' (this session's errors and 'py' snippets), 'operator list', the session's role and fog, and whether a watcher console follows this client.
	# "problems" lists what needs a look, empty when all is well. (Claude code Opus 5.5) -->
	ping = request(pid, "ping", {}, timeout)
	if not ping.get("ok"):
		raise PilotError("ping failed: %s" % ping.get("error"))
	state = ping["result"]
	role = request(pid, "role", {}, timeout)
	fog = request(pid, "fog", {}, timeout)
	unset = [row["name"] for row in settings_check() if not row["ok"]]
	mine = review(pid)
	operators = list_operators(pid)
	watchers = []
	try:
		# <!-- custom: subprocess asks PowerShell for running watcher processes; imported here as only this listing needs it. (Claude code Opus 5.5) -->
		import subprocess
		output = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'SASPilotConsole' } | ForEach-Object { $_.CommandLine }"], capture_output=True, text=True, timeout=30).stdout
		watchers = [line for line in output.splitlines() if "--pid %d" % pid in line]
	except Exception:
		watchers = None
	problems = []
	if state.get("tickError"):
		problems.append("bridge tick error: %s" % state["tickError"])
	if unset:
		problems.append("settings not at their recommended values: %s" % ", ".join(unset))
	if mine["errors"]:
		problems.append("%d errors this session ('SASPilotClient.py review')" % mine["errors"])
	repeated = [entry for entry in mine["snippets"] if entry["count"] > 1]
	if repeated:
		problems.append("%d 'py' snippets written more than once: candidates for commands" % len(repeated))
	if watchers == []:
		problems.append("SASPilotConsole is missing for this client ('SASPilotConsole.py --window --pid %d')" % pid)
	return {"pid": pid, "gameTurn": state.get("gameTurn"), "pilotRevision": state.get("pilotRevision"), "tickErrorCount": state.get("tickErrorCount"), "role": role.get("result", {}).get("role"), "fog": fog.get("result", {}).get("fog"), "settingsNotSet": unset, "sessionErrors": mine["errors"], "sessionSnippets": mine["pySnippets"], "repeatedSnippets": len(repeated), "operators": operators["count"], "operatorsPresent": operators["present"], "watchers": watchers is not None and len(watchers) or None, "problems": problems}


def log_game_marker(pid, event, save, state):
	# <!-- custom: One Civ4 process often plays dozens of games in a session (each replay and each 'menu path=' loads one), so its command log mixes them; SASGameRecord and BBAI split per load because the DLL knows each load. A row of kind "game" at each 'start' and load, with the save (or the new game's map) and its turn, marks where each game begins: grep '"kind": "game"' to split the log, and SASPilotConsole.py prints it as a banner (the user, 2026-11-14).
	# A file per game was not chosen: a session of short replays would leave dozens of small files. (Claude code Opus 5.5) -->
	args = {"event": event, "save": save, "map": state.get("mapScript"), "gameTurn": state.get("gameTurn"), "loads": state.get("loads"), "role": state.get("role") or "all"}
	# <!-- custom: The recommended-settings check went only to the terminal that ran 'start' (stderr), so a person watching the console never saw it; the user asked whether it had been forgotten (2026-11-14).
	# Its result goes on the game row too: how many were checked and the names not at their recommended value, which the watcher's banner shows. (Claude code Opus 5.5) -->
	try:
		rows = settings_check()
		args["settingsChecked"] = len(rows)
		args["settingsNotSet"] = ["%s=%s (recommended %s)" % (row["name"], row["current"], row["recommended"]) for row in rows if not row["ok"]]
	except Exception as error:
		args["settingsError"] = str(error)
	_log_request(pid, "game", args, {"ok": True, "gameTurn": state.get("gameTurn"), "result": None}, None, kind="game")


def live_mailboxes():
	import desktop_windows
	# <!-- custom: A mailbox outlives its process, so keep only folders whose PID still runs; a recycled PID that is not Civ4 never answers and times out. (Claude code Fable 5.2) -->
	result = []
	if MAILBOX_ROOT.is_dir():
		for folder in MAILBOX_ROOT.iterdir():
			if folder.name.isdigit() and desktop_windows.process_alive(int(folder.name)):
				result.append(int(folder.name))
	return sorted(result)


def layout_clients(monitor=1, wait=0.0):
	# <!-- custom: The user's ask (2026-11-15): with two clients, each console beside its own Civ4, rather than the second client's console opened full height over the first.
	# One band per running client, the oldest on top, as SASPilotConsole.arrange lays out a band; a console is found by the title it sets, waiting up to 'wait' seconds for one just opened. (Claude code Opus 5.5) -->
	import desktop_windows
	import SASPilotConsole
	clients = [(SASPilotConsole.process_instance(pid), pid) for pid in live_mailboxes()]
	clients = [pid for (instance, pid) in sorted(clients) if instance is not None]
	deadline = time.monotonic() + wait
	placed = []
	for slot in range(len(clients)):
		pid = clients[slot]
		title = u"SASPilotConsole - Civ4 client %d" % pid
		hwnd = desktop_windows.window_by_title(title)
		while hwnd is None and time.monotonic() < deadline:
			time.sleep(0.5)
			hwnd = desktop_windows.window_by_title(title)
		if hwnd is None:
			continue
		SASPilotConsole.arrange(pid, hwnd, slot, len(clients), monitor)
		placed.append(pid)
	return placed


def remove_dead_mailboxes():
	import desktop_windows
	# <!-- custom: Dead processes' folders hold only our own request and reply files, so they are deleted directly. (Claude code Fable 5.2) -->
	if not MAILBOX_ROOT.is_dir():
		return
	for folder in MAILBOX_ROOT.iterdir():
		if folder.name.isdigit() and not desktop_windows.process_alive(int(folder.name)):
			for item in folder.iterdir():
				item.unlink()
			folder.rmdir()


def pick_pid(pid):
	if pid is not None:
		return pid
	# <!-- custom: A single mailbox is used without checking its process, which needs desktop_windows; if that Civ4 has exited, the request's timeout says so. (Claude code Opus 5.5) -->
	if MAILBOX_ROOT.is_dir():
		folders = [int(folder.name) for folder in MAILBOX_ROOT.iterdir() if folder.name.isdigit()]
		if len(folders) == 1:
			return folders[0]
	pids = live_mailboxes()
	if len(pids) == 1:
		return pids[0]
	if not pids:
		raise PilotError("no piloted Civ4 is running; start one with: SASPilotClient.py start")
	raise PilotError("several piloted clients run (%s); pass --pid" % ", ".join(str(p) for p in pids))


def load_orjson():
	# <!-- custom: orjson is optional: without it, large replies use the json module, slower but the same data (Codex's review found a large reply raised ImportError instead). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	try:
		import orjson
		return orjson
	except ImportError:
		return None


def load_reply(raw):
	if len(raw) >= ORJSON_MIN_BYTES:
		orjson = load_orjson()
		if orjson is not None:
			return orjson.loads(raw)
	return json.loads(raw.decode("ascii"))


def request(pid, command, args=None, timeout=60.0):
	# <!-- custom: Every request, including those 'price', 'endturn --turns' and 'menu' send for one invocation, goes to the command log; see _log_request. (Claude code Opus 5.5) -->
	try:
		reply = _request(pid, command, args, timeout)
	# <!-- custom: Any failure, not only PilotError: a raw OSError writing the request escaped the log (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	except Exception as error:
		_log_request(pid, command, args, None, "%s: %s" % (type(error).__name__, error))
		raise
	_log_request(pid, command, args, reply, None)
	return reply


def _request(pid, command, args=None, timeout=60.0):
	# <!-- custom: Returns the reply dict: ok, result or error and traceback, gameTurn.
	# The game serves requests on its updates, every frame in game, so a reply can wait behind a long AI turn or a load. (Claude code Fable 5.2 + Opus 5.5) -->
	mailbox = MAILBOX_ROOT / str(pid)
	if not mailbox.is_dir():
		raise PilotError("no mailbox %s; is SASPilot on for that client?" % mailbox)
	request_id = "%d_%s" % (time.time_ns(), uuid.uuid4().hex[:8])
	# <!-- custom: roundTripMs runs from writing the request to reading the reply; with the game's gameMs it splits a request into serving time and waiting for the game to look. (Claude code Opus 5.5) -->
	started = time.perf_counter()
	# <!-- custom: The game's session from its hello.json, which a launched game requires on every request, so a stale request in a recycled PID's folder cannot run (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	text = json.dumps({"id": request_id, "cmd": command, "args": args or {}, "session": _hello_session(mailbox / "hello.json")})
	request_name = "req_%s.json" % request_id
	temp = mailbox / ("tmp_%s.json" % request_id)
	temp.write_text(text, encoding="ascii")
	temp.replace(mailbox / request_name)
	reply_path = mailbox / ("rep_%s.json" % request_id)
	deadline = time.monotonic() + timeout
	# <!-- custom: Without the liveness check in pick_pid, a mailbox left by a crashed Civ4 waited out the whole timeout; checking once a late reply passes 1 s reports it then, and costs nothing when the reply is quick (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	alive_check_at = time.monotonic() + 1.0
	while True:
		if reply_path.exists():
			try:
				raw = reply_path.read_bytes()
			except OSError:
				# <!-- custom: An unreadable reply restarted the loop before the deadline check, so a locked one could wait for ever (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if time.monotonic() > deadline:
					raise PilotError("the reply to request %s, %s, could not be read within %g s" % (request_id, reply_path.name, timeout))
				time.sleep(POLL_SECONDS)
				continue
			# <!-- custom: Replies are renamed into place whole, so one that does not parse is a bridge bug, not a write in progress: retrying it hid an invalid reply behind a timeout.
			# The file is kept for inspection. (Claude code Fable 5.2) -->
			try:
				reply = load_reply(raw)
			except ValueError as error:
				raise PilotError("reply %s is not valid JSON (%s)" % (reply_path, error))
			reply_path.unlink()
			reply["roundTripMs"] = (time.perf_counter() - started) * 1000.0
			reply["replyBytes"] = len(raw)
			return reply
		if alive_check_at is not None and time.monotonic() > alive_check_at:
			alive_check_at = None
			# <!-- custom: desktop_windows tells whether the game process is still alive; imported only when a reply is late. (Claude code Opus 5.5) -->
			import desktop_windows
			if not desktop_windows.process_alive(pid):
				try:
					(mailbox / request_name).unlink()
				except OSError:
					pass
				raise PilotError("Civ4 %d has exited" % pid)
		if time.monotonic() > deadline:
			# <!-- custom: Withdraw the unanswered request so it does not run later, out of context. (Claude code Fable 5.2) -->
			# <!-- custom: Only a request the game has not claimed can be withdrawn: it renames req_ to run_ before running it (SASPilotCommands.poll).
			# The error now says which case it was, as a retry after a command already started would repeat it (ChatGPT's review, 2026-11-14). (Claude code Opus 5.5 + ChatGPT-5.6-Sol) -->
			try:
				(mailbox / request_name).unlink()
				started_note = "it was withdrawn before the game took it, so retrying is safe"
			except FileNotFoundError:
				# <!-- custom: A run_ only says the game claimed it; a failed read or reply write can leave it behind, so the outcome is unknown either way (Codex's review).
				# One last look catches a reply that landed at the deadline; the request ID lets the caller find a later one. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if reply_path.exists():
					continue
				started_note = "the game claimed request %s, outcome unknown, so check the game's state before retrying; a late reply would be %s" % (request_id, reply_path.name)
			except OSError:
				started_note = "request %s could not be withdrawn, so check the game's state before retrying" % request_id
			# <!-- custom: desktop_windows tells whether the game process is still alive, before saying the request timed out. (Claude code Opus 5.5) -->
			import desktop_windows
			if not desktop_windows.process_alive(pid):
				raise PilotError("Civ4 %d has exited" % pid)
			raise PilotError("no reply to %r within %g s (%s); Civ4 %d may be loading, in a long turn, at the main menu or showing a dialog" % (command, timeout, started_note, pid))
		time.sleep(POLL_SECONDS)


def call(pid, command, args=None, timeout=60.0):
	# <!-- custom: The result alone, raising on a failed command; for scripts that import this module. (Claude code Fable 5.2) -->
	reply = request(pid, command, args, timeout)
	if not reply.get("ok"):
		raise PilotError("%s\n%s" % (reply.get("error"), reply.get("traceback", "")))
	return reply.get("result")


def wait_for_turn(pid, timeout, after_turn=None, after_loads=None):
	# <!-- custom: Until a game runs and it is the active player's turn with no autoplay left: after start, endturn, autoplay or a load. (Claude code Fable 5.2) -->
	import desktop_windows
	deadline = time.monotonic() + timeout
	last = None
	while time.monotonic() < deadline:
		if not desktop_windows.process_alive(pid):
			raise PilotError("Civ4 %d has exited" % pid)
		try:
			last = call(pid, "ping", timeout=min(10.0, max(1.0, deadline - time.monotonic())))
		except PilotError:
			continue
		# <!-- custom: after_turn also requires a later game turn: sendTurnComplete takes effect after the reply, so a ping right after 'endturn' still showed the old turn as active. (Claude code Fable 5.2) -->
		# <!-- custom: after_loads requires a load counted after that number; see load_game. (Claude code Opus 5.5) -->
		if last.get("inGame") and last.get("turnActive") and not last.get("autoPlayTurns") and (after_turn is None or last.get("gameTurn", -1) > after_turn) and (after_loads is None or (last.get("loads") or 0) > after_loads):
			return last
		time.sleep(0.2)
	raise PilotError("no active turn within %g s; last ping: %s" % (timeout, json.dumps(last)))


def load_game(pid, path, timeout=600.0):
	# <!-- custom: Loads a save in a running client and returns once that game waits for orders.
	# Waiting for an active turn alone returned at once on the game being left, which still answered as in game, so the first commands after a load ran on the old game (2026-11-13); SASPilot counts finished loads, and this waits for the count to rise. (Claude code Opus 5.5) -->
	check_save_mod(Path(path))
	before = call(pid, "ping").get("loads")
	if before is None:
		raise PilotError("this client's SASPilot does not count loads; restart Civ4 so its Python includes SASPilot.onLoad")
	call(pid, "menu", {"path": str(path)})
	state = wait_for_turn(pid, timeout, after_loads=before)
	log_game_marker(pid, "load", str(path), state)
	return state


def resolve_save(name):
	# <!-- custom: SASPilotReplay.py already took a bare name from Saves/single, while start --save took only a path, so on 2026-11-13 "start --save sas_pilot_fogplay_t148" failed; both now share this lookup.
	# The extension may be left out too. (Claude code Opus 5.5) -->
	# <!-- custom: The extension is added before anything is looked up, and only a bare name falls back to Saves/single: the first draft checked the path without its extension, so "samples/local" went to Saves/single although samples/local.CivBeyondSwordSave existed (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	save = Path(name)
	if not save.suffix:
		save = save.with_suffix(".CivBeyondSwordSave")
	if not save.is_absolute() and not save.is_file():
		# <!-- custom: A relative path missing from the working folder is also tried under Saves, as Civ4 lists saves there: on 2026-11-15 "start --save single/WILLEM_VAN_T0119_..._STOP" failed, as only a bare name was looked up. (Claude code Opus 5.5) -->
		if save.parent == Path("."):
			save = Path(MAILBOX_ROOT).parent / "Saves" / "single" / save.name
		else:
			save = Path(MAILBOX_ROOT).parent / "Saves" / save
	return save.resolve()


def check_save_mod(path):
	# <!-- custom: Every mod names its saves "PC BC-<year>" by default, so on 2026-11-13 a Caveman2Cosmos save in the shared Saves folder was taken for an AdvCiv-SAS one, and Civ4 stopped on a dialog asking to restart into that mod, which SASPilot cannot answer.
	# So SASPilot refuses a save made for another mod before Civ4 sees it.
	# See "Loading a save" in README_SASPilot.md. (Claude code Opus 5.5) -->
	# <!-- custom: The header is read by run_autoplay.save_mod_folder, which autoplay already used for the same check, rather than a second copy (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	import run_autoplay
	if not Path(path).is_file():
		raise PilotError("save not found: %s" % path)
	expected = "Mods\\%s\\" % run_autoplay.MOD_FOLDER
	try:
		found = run_autoplay.save_mod_folder(path)
	except ValueError as error:
		raise PilotError(str(error))
	if found.lower() != expected.lower():
		raise PilotError("%s was saved with %s, not %s; Civ4 would ask to restart into that mod" % (path, found or "no mod", expected))


def settings_check():
	# <!-- custom: The user suggested a greeting that lists the recommended settings for agent runs with their values, warning of those not set (2026-11-14): with the Dawn of Man screen or a tech splash on, a game waits on a Continue button SASPilot does not press, and with SASGameRecord off a game leaves no record to review.
	# The development values come from toggle_dev_diagnostics.py, so the two cannot drift apart.
	# They are read from the working tree, which may differ from the committed values players get.
	# Returns one row per setting: file, name, current, recommended, ok. (Claude code Opus 5.5) -->
	sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "diagnostics"))
	import toggle_dev_diagnostics
	# <!-- custom: The settings agent runs want besides the toggle's list moved to define_values.py as AGENT_RUN_VALUES on 2026-11-19, so each switched value has one home. (Claude code Opus 5.5) -->
	from define_values import AGENT_RUN_VALUES
	text = toggle_dev_diagnostics.DEFINES_PATH.read_bytes().decode("utf-8")
	wanted = dict([(name, dev) for (name, (shipped, dev)) in toggle_dev_diagnostics.DEV_DIAGNOSTICS.items()])
	wanted.update(AGENT_RUN_VALUES)
	rows = []
	for name, value in sorted(wanted.items()):
		matches = toggle_dev_diagnostics.define_pattern(name).findall(text)
		current = len(matches) == 1 and matches[0][1] or None
		rows.append({"file": "GlobalDefines_advciv_sas.xml", "name": name, "current": current, "recommended": str(value), "ok": current == str(value)})
	# <!-- custom: CivilizationIV.ini settings too (the user, 2026-11-14): LoggingEnabled for PythonErr.log and the other Civ4 logs, GenerateCrashDumps for a dump to debug a crash with, FullScreen 0 so screenshots and window layouts work, HidePythonExceptions 0 so a Python error shows.
	# Keys are matched without regard to case, as the file writes them in lower case. (Claude code Opus 5.5) -->
	ini_path = MAILBOX_ROOT.parent / "CivilizationIV.ini"
	ini = {}
	if ini_path.is_file():
		for line in ini_path.read_text(encoding="latin-1").splitlines():
			if "=" in line and not line.lstrip().startswith(";"):
				key, value = line.split("=", 1)
				ini[key.strip().lower()] = value.strip()
	for key, value in (("LoggingEnabled", "1"), ("GenerateCrashDumps", "1"), ("FullScreen", "0"), ("HidePythonExceptions", "0")):
		current = ini.get(key.lower())
		rows.append({"file": "CivilizationIV.ini", "name": key, "current": current, "recommended": value, "ok": current == value})
	return rows


def print_settings_check():
	rows = settings_check()
	unset = [row for row in rows if not row["ok"]]
	print("pilot: %d recommended settings checked, %d not set (values from the working tree; committed values may differ, as players get the shipped ones):" % (len(rows), len(unset)), file=sys.stderr)
	for row in rows:
		print("  %-4s %s %s = %s (recommended %s)" % (row["ok"] and "ok" or "WARN", row["file"], row["name"], row["current"], row["recommended"]), file=sys.stderr)
	if unset:
		print("  'python LLM_Helpers/diagnostics/toggle_dev_diagnostics.py on' sets the GlobalDefines ones; edit with Civ4 closed.", file=sys.stderr)


def start(args):
	print_settings_check()
	# <!-- custom: desktop_windows finds running clients and launches Civ4 detached, and run_autoplay writes the per-run INI; imported here as only start needs them. (Claude code Opus 5.5) -->
	import desktop_windows
	import run_autoplay
	settings = {}
	if args.save:
		save = resolve_save(args.save)
		if not save.is_file():
			raise PilotError("save not found: %s" % save)
		check_save_mod(save)
		settings["QuickStart"] = "0"
		settings["Map"] = "Pangaea"
	else:
		save = None
		settings["QuickStart"] = "1"
		# <!-- custom: The INI wants full type names, and Civ4 silently fell back to Standard for "--world-size Large" (Continents game, 2026-11-19, noticed only from the START save's name), so a short name gets its prefix. (Claude code Opus 5.5) -->
		for key, value, prefix in (("Map", args.map, None), ("WorldSize", args.world_size, "WORLDSIZE_"), ("GameSpeed", args.speed, "GAMESPEED_"), ("QuickHandicap", args.handicap, "HANDICAP_")):
			if value:
				if prefix and not value.upper().startswith(prefix):
					value = prefix + value.upper()
				settings[key] = value
		if args.fixed_seeds:
			settings["SyncRandSeed"] = "1"
			settings["MapRandSeed"] = "1"
	running = desktop_windows.civ4_processes()
	if running and not args.multiple:
		raise PilotError("Civ4 is already running (%s); close it or pass --multiple" % ", ".join(str(p) for p, _ in running))
	remove_dead_mailboxes()
	# <!-- custom: A random ID for this launch, written into the per-run INI and echoed by the game in hello.json; see the wait below. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	session = uuid.uuid4().hex
	ini_name = "SASPilot_%s_%d.ini" % (time.strftime("%Y%m%dT%H%M%S"), os.getpid())
	ini_path = desktop_windows.DEFAULT_CIV4_DIR / ini_name
	# <!-- custom: The launch role goes in the per-run INI, which the bridge applies, locked, before its first request: sent as a 'role' request after the game was ready, a second client could send 'py' or lock another role in between (Codex's review, round 33). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	pilot_lines = ["[SASPilot]", "On = 1", "Session = %s" % session]
	if args.role:
		pilot_lines.append("Role = %s" % args.role)
	run_autoplay.write_request_ini(run_autoplay.USER_DIR / "CivilizationIV.ini", ini_path, None, False, "-", "Pilot", settings, extra_lines=pilot_lines)
	arguments = "ini=%s" % ini_name
	if save is not None:
		arguments = '/FXSLOAD="%s" %s' % (save, arguments)
	if args.multiple:
		arguments += " multiple"
	# <!-- custom: The mailbox is named by PID, which Windows recycles, so a folder left by a dead client could already hold a hello.json and end this wait before the new game had started (ChatGPT's review, 2026-11-14).
	# A first fix accepted a hello written after the launch, with two seconds of slack, which Codex's review noted could still take a recent stale file; only a hello carrying this launch's session ID counts now. (Claude code Opus 5.5 + ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	pid = desktop_windows.launch_detached(arguments)
	print("launched pid %d: %s" % (pid, arguments), file=sys.stderr, flush=True)
	deadline = time.monotonic() + args.timeout
	hello = MAILBOX_ROOT / str(pid) / "hello.json"
	while not _hello_session(hello) == session:
		if not desktop_windows.process_alive(pid):
			raise PilotError("Civ4 %d exited while starting" % pid)
		if time.monotonic() > deadline:
			raise PilotError("no mailbox for pid %d within %g s; per-run INI left at %s" % (pid, args.timeout, ini_path))
		time.sleep(0.5)
	state = wait_for_turn(pid, max(5.0, deadline - time.monotonic()))
	state["iniFile"] = str(ini_path)
	# <!-- custom: Fog is the game-side session's switch and starts off, so relaunching the fog-on playthrough at turn 156 silently gave full sight until a reply showed "fog": false three turns later (2026-11-13).
	# --fog switches it on before the first command. (Claude code Opus 5.5) -->
	if args.fog:
		reply = request(pid, "fog", {"on": 1}, 60.0)
		if not reply.get("ok"):
			raise PilotError("could not switch fog on: %s" % reply.get("error"))
		state["fog"] = True
	# <!-- custom: --role play keeps the session fair from its first command: fog on, and 'py', the WorldBuilder, fog=0 and other teams' player= refused by the bridge (the user's roles idea, 2026-11-14). (Claude code Opus 5.5) -->
	if args.role:
		# <!-- custom: Locked, as a later 'role set=all' from the same mailbox lifted it (Codex's review, round 32); the bridge has applied it from the INI by now, so this confirms it and gives an older command module the role too. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		reply = request(pid, "role", {"set": args.role, "lock": 1}, 60.0)
		if not reply.get("ok"):
			raise PilotError("could not set the role: %s" % reply.get("error"))
		state["role"] = args.role
		state["fog"] = True
	log_game_marker(pid, args.save and "load" or "new", args.save and str(resolve_save(args.save)) or None, state)
	# <!-- custom: --watch opens the command console laid out beside the new Civ4 at once, rather than a second command after it (the user, 2026-11-14); see SASPilotConsole.py --window. (Claude code Opus 5.5) -->
	# <!-- custom: On by default since the user asked that SASPilot start with its console (2026-11-14).
	# --no-watch was removed the same day: Codex started a scouting trial with it, so the user, watching, saw one console for two clients and could not follow that one. Every client now has its console, as the user asked; SAS_PILOT_WATCH=0 stays for automated tests that must not open windows. (Claude code Opus 5.5) -->
	state["watch"] = ensure_watcher(pid, args.watch_slots, args.watch_slot)
	# <!-- custom: A second client's console opened full height in band 1 of 1 over the first one's (2026-11-15), so with --multiple and no --watch-slots every running client is laid out again, one band each. (Claude code Opus 5.5) -->
	if args.multiple and args.watch_slots == 1 and state["watch"]:
		state["layout"] = layout_clients(wait=15.0)
	return state


def open_watcher(pid, slots=1, slot=1):
	import subprocess
	# <!-- custom: The launcher's status line went to stdout ahead of the reply's JSON on the first test, which would break an agent parsing the reply; said on stderr instead. (Claude code Opus 5.5) -->
	process = subprocess.Popen([sys.executable, str(Path(__file__).resolve().parent / "SASPilotConsole.py"), "--window", "--pid", str(pid), "--slots", str(slots), "--slot", str(slot)], stdout=subprocess.DEVNULL)
	print("pilot: opened SASPilotConsole for client %d (launcher process %d); SAS_PILOT_WATCH=0 turns this off" % (pid, process.pid), file=sys.stderr)
	return True


def ensure_watcher(pid, slots=None, slot=None):
	# <!-- custom: Open the client's console, or reopen it when it has closed: on 2026-11-14 the console ended with the agent's session while Civ4 ran on, and the user could not find it.
	# The console writes its PID and creation time to <log>.watch; a missing file, a process that ended or a reused PID means it is gone.
	# One file read and one OpenProcess per command, far below a request's time.
	# Only for a client with a log, as a console waits on one. (Claude code Opus 5.5) -->
	if os.environ.get("SAS_PILOT_WATCH") == "0":
		return False
	try:
		path = log_path(pid)
		if path is None or not path.exists():
			return False
		# <!-- custom: The check and the launch run under a lock on <log>.watchlock, so one caller at a time decides: Codex reproduced two callers that both found no console and both opened one (round 33), then, with an exclusive claim file, two that both took over a stale claim (round 34).
		# A caller that finds the lock held leaves the console to the one holding it; the lock goes with the process, so a call that dies frees it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		import msvcrt
		descriptor = os.open(str(path.with_suffix(".watchlock")), os.O_RDWR | os.O_CREAT | os.O_BINARY)
		try:
			try:
				msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
			except OSError:
				return False
			try:
				marker = path.with_suffix(".watch")
				try:
					state = json.loads(marker.read_text(encoding="ascii"))
				except (OSError, ValueError):
					state = {}
				# <!-- custom: A {"declined": true} marker left by the removed --no-watch has no pid, so the console opens below. (Claude code Opus 5.5) -->
				# <!-- custom: A console launched in the last 30 s that has not written its PID yet; written under the lock, so the next caller sees it. (Claude code Opus 5.5) -->
				if state.get("opening") and time.time() - state["opening"] < 30:
					return False
				if state.get("pid"):
					import SASPilotConsole
					if SASPilotConsole.process_instance(state["pid"]) == state.get("instance"):
						return False
				# <!-- custom: In the band the closed console had, so two clients' consoles keep their places; 'start' gives its own. (Claude code Opus 5.5) -->
				slots = slots or state.get("slots") or 1
				slot = slot or state.get("slot") or 1
				marker.write_text(json.dumps({"opening": time.time(), "slots": slots, "slot": slot}), encoding="ascii")
				return open_watcher(pid, slots, slot)
			finally:
				os.lseek(descriptor, 0, 0)
				msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
		finally:
			os.close(descriptor)
	except Exception:
		return False


def _bridge(pid, command, command_args, timeout):
	reply = request(pid, command, command_args, timeout)
	if not reply.get("ok"):
		raise PilotError("%s: %s" % (command, reply.get("error")))
	return reply["result"]


def _reply_with(pid, screen, comments, timeout, bound=None):
	# <!-- custom: bound is (partner, conversation): Codex's review mocked another leader's trade screen opening before the one 'price' asked for, and 'price' accepted that leader's counter-offer, then declined in his conversation.
	# A screen of anyone else, or of a later conversation, is now refused before any reply. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if bound is not None and (screen.get("who"), screen.get("conversation")) != bound:
		raise PilotError("the screen is now with player %s, conversation %s, not %s; see 'diplo'" % (screen.get("who"), screen.get("conversation"), bound))
	for comment in comments:
		for choice in screen.get("replies", []):
			if choice["comment"] == comment:
				return _bridge(pid, "reply", {"n": choice["n"], "screen": screen["screen"]}, timeout)
	return None


# <!-- custom: Replies that only end a conversation; a screen offering anything else (a deal, peace, a demand) is left for the agent.
# On turn 289 (2026-11-14) Kublai's war declaration, Joao's thanks and two cancelled deals queued up one after another, and each needed a 'diplo' and a 'reply'. (Claude code Opus 5.5) -->
LEAVE_REPLIES = ("USER_DIPLOCOMMENT_EXIT", "USER_DIPLOCOMMENT_NO_RENEGOTIATE")
# <!-- custom: The AI lines that only inform.
# Codex's review mocked a wartime greeting offering both Suggest peace and Exit, and the first version sent Exit, as it went by the replies alone; now only these lines are closed, whatever else the screen offers. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
# <!-- custom: AI_DIPLOCOMMENT_PEACE is the "Wonderful."
# that follows choosing peace at a first contact; at turn 8 of the turn-0 game (2026-11-14) it stopped 'leave', though it offers only "something else" and Exit. (Claude code Opus 5.5) -->
# <!-- custom: AI_DIPLOCOMMENT_STOP_DENIED is the AI's answer to our refusal of its demand to stop trading (Sitting Bull at turn 115 of the turn-0 game, 2026-11-14); it only informs, and stopped 'leave'. (Claude code Opus 5.5) -->
LEAVE_AI_COMMENTS = ("AI_DIPLOCOMMENT_THANKS", "AI_DIPLOCOMMENT_GLAD", "AI_DIPLOCOMMENT_CANCEL_DEAL", "AI_DIPLOCOMMENT_DECLARE_WAR", "AI_DIPLOCOMMENT_SOMETHING_ELSE", "AI_DIPLOCOMMENT_NO_PEACE", "AI_DIPLOCOMMENT_PEACE", "AI_DIPLOCOMMENT_STOP_DENIED")
LEAVE_ONLY_REPLY_COMMENTS = ("AI_DIPLOCOMMENT_DECLARE_WAR",)


def leave_screens(pid, timeout, rounds=12):
	# <!-- custom: Close diplomacy screens that only inform, as a person clicks through them: the exit reply, or the only reply of a war declaration.
	# Stops at a screen with a choice and returns it, with the screens closed before it. (Claude code Opus 5.5) -->
	closed = []
	for _ in range(rounds):
		screen = call(pid, "diplo", {}, timeout)
		if not screen.get("open"):
			# <!-- custom: The next queued screen opens a frame or two after the last reply, so look once more before calling it done. (Claude code Opus 5.5) -->
			time.sleep(0.3)
			screen = call(pid, "diplo", {}, timeout)
			if not screen.get("open"):
				return {"closed": closed, "open": None}
		replies = screen.get("replies", [])
		choice = None
		if screen.get("aiComment") not in LEAVE_AI_COMMENTS:
			replies_to_try = []
		else:
			replies_to_try = replies
		for reply in replies_to_try:
			if reply["comment"] in LEAVE_REPLIES:
				choice = reply
		if choice is None and screen.get("aiComment") in LEAVE_ONLY_REPLY_COMMENTS and len(replies) == 1:
			choice = replies[0]
		# <!-- custom: A deal on the table is a choice, except on a cancelled-deal screen, which shows the deal that just ended. (Claude code Opus 5.5) -->
		offered = bool(screen.get("theyOffer") or screen.get("weOffer")) and screen.get("aiComment") != "AI_DIPLOCOMMENT_CANCEL_DEAL"
		if choice is None or offered:
			return {"closed": closed, "open": {"screen": screen.get("screen"), "who": screen.get("whoName"), "aiComment": screen.get("aiComment"), "aiText": screen.get("aiText"), "replies": [(r["n"], r["comment"]) for r in replies], "theyOffer": screen.get("theyOffer"), "weOffer": screen.get("weOffer")}}
		call(pid, "reply", {"n": choice["n"], "screen": screen["screen"]}, timeout)
		closed.append({"who": screen.get("whoName"), "aiComment": screen.get("aiComment"), "reply": choice["comment"]})
	return {"closed": closed, "open": "still open after %d screens" % rounds}


def ask_price(pid, price_args, timeout):
	# <!-- custom: Asking an AI's price took five shell steps each time: 'contact' with the items on the table, waiting for the screen, 'reply' with "What do you want for this?", reading the counter-offer and leaving; the chained one-liners broke as soon as an AI's own offer was already on screen (Water Wheel and Machinery at turns 168 and 169, 2026-11-13).
	# 'price' does them in order and leaves the screen with nothing agreed, so a price can be compared across leaders before buying through 'contact' and 'reply'. (Claude code Opus 5.5) -->
	if _bridge(pid, "diplo", {}, timeout).get("open"):
		raise PilotError("a diplomacy screen is already open; answer it first ('diplo', 'reply')")
	price_args = dict(price_args)
	# <!-- custom: accept=1 takes the counter-offer this call read, on the screen that showed it, as clicking "We accept" right after reading it does; Machinery for 180 gold at turn 174 (2026-11-13). Without it nothing is agreed. (Claude code Opus 5.5) -->
	# <!-- custom: Only true/1 or false/0: Codex's review mocked accept=flase, which bool() took as true and sent the acceptance. Checked before diplomacy opens. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	accept = price_args.pop("accept", False)
	if accept not in (True, False, 1, 0):
		raise PilotError("accept takes true/1 or false/0, not %r" % (accept,))
	bAccept = bool(accept)
	_bridge(pid, "contact", price_args, timeout)
	deadline = time.monotonic() + 15.0
	screen = {}
	while not screen.get("open"):
		if time.monotonic() > deadline:
			raise PilotError("the trade screen did not open")
		time.sleep(0.3)
		screen = _bridge(pid, "diplo", {}, timeout)
	if screen.get("who") != price_args.get("with"):
		raise PilotError("player %s's screen opened instead of player %s's; see 'diplo'" % (screen.get("who"), price_args.get("with")))
	# <!-- custom: Only the trade table this request opened: Codex's review mocked the same leader's own greeting opening before it, and 'price' bound to the greeting and dismissed it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if screen.get("aiComment") != "AI_DIPLOCOMMENT_TRADING":
		raise PilotError("a %s screen opened, not the trade table; see 'diplo'" % screen.get("aiComment"))
	bound = (screen.get("who"), screen.get("conversation"))
	# <!-- custom: Selling, with only our own items on the table, the screen asks "What will you give me for this?"
	# (FISH_FOR_DEAL) instead of "What do you want for this?"
	# (OFFER): offering Monarchy to Moctezuma at turn 120 of the second fog-on game came back unpriced (2026-11-13). (Claude code Opus 5.5) -->
	# <!-- custom: With items on both sides, the screen offers "Can you complete this deal?"
	# (COMPLETE_DEAL) and Propose instead: Navigation against Meditation and Drama with Kublai at turn 133 came back unpriced.
	# COMPLETE_DEAL is the counter-offer the window gives for such a table. (Claude code Opus 5.5) -->
	asked = _reply_with(pid, screen, ["USER_DIPLOCOMMENT_OFFER", "USER_DIPLOCOMMENT_FISH_FOR_DEAL", "USER_DIPLOCOMMENT_COMPLETE_DEAL"], timeout, bound)
	if asked is None:
		result = {"priced": False, "aiComment": screen.get("aiComment"), "replies": [choice["comment"] for choice in screen.get("replies", [])]}
	else:
		result = {"priced": asked.get("aiComment") == "AI_DIPLOCOMMENT_TRY_THIS_DEAL", "aiComment": asked.get("aiComment"), "theyGive": asked.get("theyOffer"), "weGive": asked.get("weOffer")}
		if bAccept and result["priced"]:
			# <!-- custom: The screen says GLAD once the reply is handled, whether or not the game then carried the deal out, so this reports only that the acceptance was sent; read the result back, such as the tech or the gold (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			accepted = _reply_with(pid, asked, ["USER_DIPLOCOMMENT_ACCEPT"], timeout, bound)
			result["acceptSent"] = accepted is not None
			if accepted is not None:
				result["aiAnswer"] = accepted.get("aiComment")
	# <!-- custom: Leave without agreeing: decline a counter-offer, then exit; a few rounds, as each reply can bring a new AI line.
	# Whether the screen closed is reported, rather than returning with it still open after the last round (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	result["screenClosed"] = False
	# <!-- custom: A stop while leaving is reported in the result, not raised: Codex's review mocked a new conversation opening after the acceptance, and the raised error discarded acceptSent, so a caller could retry a purchase already sent. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Never mind before Exit, and closed only if still closed a second later: at turn 114 of the turn-0 game (2026-11-14) Exit straight from Louis's trade table after his refusal reported the screen closed, yet the table was open again moments later, which blocked the next 'price' ("a diplomacy screen is already open").
	# Never mind returned to his main screen (AI_DIPLOCOMMENT_WELL), and Exit from there stayed closed. (Claude code Opus 5.5) -->
	try:
		for _ in range(6):
			screen = _bridge(pid, "diplo", {}, timeout)
			if not screen.get("open"):
				time.sleep(1.0)
				screen = _bridge(pid, "diplo", {}, timeout)
				if not screen.get("open"):
					result["screenClosed"] = True
					break
			if _reply_with(pid, screen, ["USER_DIPLOCOMMENT_REJECT", "USER_DIPLOCOMMENT_NEVERMIND", "USER_DIPLOCOMMENT_EXIT"], timeout, bound) is None:
				raise PilotError("could not leave the screen; see 'diplo'")
		# <!-- custom: The last check after the fourth round sat outside this handler, so its failure could still drop acceptSent (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		# <!-- custom: The same one-second stability test as in the loop: this last probe took a momentary close as closed (Codex's review, round 36). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if not result["screenClosed"] and not _bridge(pid, "diplo", {}, timeout).get("open"):
			time.sleep(1.0)
			if not _bridge(pid, "diplo", {}, timeout).get("open"):
				result["screenClosed"] = True
	except PilotError as error:
		result["cleanupStopped"] = str(error)
	return result


def _hello_session(path):
	# <!-- custom: The session ID in a mailbox's hello.json, or None while it is missing or being replaced. (Claude code Opus 5.5) -->
	try:
		return json.loads(path.read_text(encoding="ascii")).get("session")
	except (OSError, ValueError):
		return None


def close(pid):
	import desktop_windows
	import run_autoplay
	outcome = run_autoplay.close_civ4(pid)
	remove_dead_mailboxes()
	# <!-- custom: The per-run INI and the .bak Civ4 makes of it are ours; remove those no client still uses. (Claude code Fable 5.2) -->
	if not desktop_windows.civ4_processes():
		for leftover in desktop_windows.DEFAULT_CIV4_DIR.glob("SASPilot_*.ini*"):
			leftover.unlink()
	return {"civ4": outcome}


def bench(pid, command, command_args, count, timeout):
	# <!-- custom: Sends the same request count times in a row and summarizes both timings, so changes to the bridge's pace can be compared on equal terms. (Claude code Opus 5.5) -->
	round_trips = []
	game_times = []
	ticks = {}
	for _ in range(count):
		reply = request(pid, command, command_args, timeout)
		if not reply.get("ok"):
			raise PilotError("%s failed: %s" % (command, reply.get("error")))
		round_trips.append(reply["roundTripMs"])
		game_times.append(reply.get("gameMs", -1.0))
		ticks[reply.get("tick", "-")] = ticks.get(reply.get("tick", "-"), 0) + 1
	def summary(values):
		ordered = sorted(values)
		return {"min": ordered[0], "median": ordered[len(ordered) // 2], "mean": sum(ordered) / len(ordered), "max": ordered[-1]}
	return {"command": command, "count": count, "roundTripMs": summary(round_trips), "gameMs": summary(game_times), "servedOn": ticks}


def parse_value(text):
	# <!-- custom: key=value arguments are JSON when they parse (numbers, true, lists), plain strings otherwise, so x=12 and item=UNIT_WARRIOR both work unquoted. (Claude code Fable 5.2) -->
	try:
		return json.loads(text)
	except ValueError:
		return text


def digest_waits(digest):
	return any(digest["todo"].get(key) for key in ("idleCities", "idleUnits", "needsResearch", "heldPopups", "diplomacy", "freeTechOwed"))


def print_digest(digest, brief, compact=True):
	# <!-- custom: Thirty turns of JSON digests took a throwaway parser to read in the fog-on playthrough (2026-11-13); --brief prints what a person would glance at: one line per message, and one listing what waits, if anything. (Claude code Opus 5.5) -->
	if not brief:
		print(json.dumps(digest, ensure_ascii=False, indent=None if compact else 1))
		return
	turn = digest["gameTurn"]
	for message in digest["messages"]:
		print("T%d %s: %s" % (turn, message["messageType"].replace("MESSAGE_TYPE_", ""), message["text"]))
	for notice in digest.get("notices", []):
		print("T%d NOTICE: %s" % (turn, notice))
	todo = digest["todo"]
	waits = []
	if todo.get("needsResearch"):
		waits.append("research")
	for city in todo.get("idleCities", []):
		waits.append("city %s (id %d)" % (city["name"], city["id"]))
	for unit in todo.get("idleUnits", []):
		waits.append("unit %s %d at %d,%d" % (unit["type"], unit["id"], unit["x"], unit["y"]))
	for popup in todo.get("heldPopups", []):
		waits.append("popup %s id %d %s: %s" % (popup["type"], popup["id"], json.dumps(popup.get("about")), ",".join(popup["buttons"])))
	if todo.get("diplomacy"):
		waits.append("diplomacy screen %d with player %d (%s): %s" % (todo["diplomacy"]["screen"], todo["diplomacy"]["who"], todo["diplomacy"]["aiComment"], ",".join(todo["diplomacy"]["replies"])))
	if todo.get("freeTechOwed"):
		waits.append("free tech x%d (freetech)" % todo["freeTechOwed"])
	if waits:
		print("T%d waits: %s" % (turn, "; ".join(waits)))
	elif not digest["messages"]:
		print("T%d" % turn)
	# <!-- custom: What the game does not announce, such as an angry city or a tech a neighbour could be offered; see the bridge's 'reminders' (the user, 2026-11-14).
	# Printed only when they differ from the last turn's, as "Gilgamesh could be offered TECH_SEAFARING" came back every turn (2026-11-14). (Claude code Opus 5.5) -->
	texts = [entry["text"] for entry in digest.get("reminders", [])]
	if texts and texts != _log_context.get("lastReminders"):
		print("T%d remind: %s" % (turn, "; ".join(texts)))
	_log_context["lastReminders"] = texts
	# <!-- custom: Rivals' power against ours, as the scoreboard shows it, when it changes, so it is watched every turn as the user advised (2026-11-14): "Gilgamesh 1.22" is 1.22 times our power. (Claude code Opus 5.5) -->
	power = ", ".join(["%s %d.%03d" % (entry["name"], entry["ratioPerMille"] / 1000, entry["ratioPerMille"] % 1000) for entry in digest.get("power", [])])
	if power and power != _log_context.get("lastPower"):
		print("T%d power: %s" % (turn, power))
	_log_context["lastPower"] = power
	if digest.get("skippedLastTurn"):
		print("T%d skipped last turn: %s" % (turn, json.dumps(digest["skippedLastTurn"], ensure_ascii=False)))


def main():
	parser = argparse.ArgumentParser(description="Read and drive a running Civ4 (AdvCiv-SAS) through SASPilot. Examples: SASPilotClient.py start --map Pangaea; SASPilotClient.py help; SASPilotClient.py units; SASPilotClient.py move unit=3 x=10 y=12; SASPilotClient.py py \"game.getGameTurn()\"; SASPilotClient.py endturn; SASPilotClient.py close")
	parser.add_argument("--pid", type=int, help="the Civ4 process to talk to; optional while exactly one piloted client runs")
	parser.add_argument("--timeout", type=float, default=None, help="seconds to wait for the reply (default 60; 600 for start and wait)")
	parser.add_argument("--compact", action="store_true", help="print JSON on one line")
	parser.add_argument("--map", help="start: map script name without .py")
	parser.add_argument("--world-size", help="start: e.g. WORLDSIZE_STANDARD")
	parser.add_argument("--speed", help="start: e.g. GAMESPEED_NORMAL")
	parser.add_argument("--handicap", help="start: e.g. HANDICAP_NOBLE")
	parser.add_argument("--fixed-seeds", action="store_true", help="start: SyncRandSeed and MapRandSeed 1, for a repeatable new game")
	parser.add_argument("--save", help="start: load this save instead of starting a new game")
	parser.add_argument("--fog", action="store_true", help="start: switch fog on once the game runs, so replies show only what the player knows, as for a playthrough; a new client starts with fog off")
	parser.add_argument("--role", choices=("play", "assist", "all"), help="start: the session's role, locked until Civ4 closes; play allows only what a player sees and does, facts only (fog on; py, the WorldBuilder, fog=0, other teams' player= and 'advise' refused); assist adds advice; default all")
	# <!-- custom: --no-watch was removed on 2026-11-14 so every client has its console (see start()); an old command line with it now fails loudly rather than hiding the console. (Claude code Opus 5.5) -->
	parser.add_argument("--watch", action="store_true", help="start: SASPilotConsole always opens (SASPilotConsole.py --window) beside the new Civ4, Civ4 at its own size top-left and the console filling the rest, and any later command reopens it if it was closed; kept so older command lines still run. SAS_PILOT_WATCH=0 is only for automated tests that must not open windows")
	parser.add_argument("--watch-slots", type=int, default=1, help="start --watch: bands to split the monitor into, one per client (2 for two clients)")
	parser.add_argument("--watch-slot", type=int, default=1, help="start --watch: this client's band, from the top")
	parser.add_argument("--multiple", action="store_true", help="start: allow other Civ4 clients and pass Civ4's 'multiple' argument")
	parser.add_argument("--timing", action="store_true", help="print the request's roundTripMs and gameMs on stderr")
	parser.add_argument("--count", type=int, default=20, help="bench: how many requests to send")
	parser.add_argument("--no-wait", action="store_true", help="endturn: return at once instead of waiting for the active player's next turn; menu path=: return without waiting for the load")
	parser.add_argument("--turns", type=int, default=1, help="endturn: end up to this many turns, stopping early at a turn where something waits for orders (as 'todo' lists it); prints each turn's digest as one line")
	parser.add_argument("--note", help="the reason for this command, written with it in the command log (Logs/SASPilot_<start>_<pid>.jsonl) that SASPilotConsole.py follows; note=... among the arguments does the same, except for 'py'")
	parser.add_argument("--operator", help="who sends the commands, e.g. \"Claude Code Opus 5.5\", written on each command-log row; default SAS_PILOT_OPERATOR. 'operator joined' and 'operator left' mark the start and end of a turn at the controls")
	parser.add_argument("--brief", action="store_true", help="endturn: print each turn's digest as short text lines (turn, messages, what waits) instead of JSON")
	parser.add_argument("command", help="start (warns of recommended settings not set; check prints them), list, layout (each running client and its SASPilotConsole in a band of its own, oldest on top), wait, close, operator joined|left|list (mark the --operator taking or leaving the controls in the command log; list them all with their times), review (this session's errors and its 'py' snippets grouped, most repeated first), health (SASPilot's own state and its problems in one reply), leave (click through diplomacy screens that only inform; stops at one with a choice), price with= take=[...] give=[...] [accept=1] (an AI's counter-offer; nothing agreed unless accept=1), bench <command> [key=value...], or a bridge command ('help' lists them)")
	parser.add_argument("arguments", nargs="*", help="key=value pairs; for 'py', the code itself, '-' for stdin or @file")
	args = parser.parse_args()
	# <!-- custom: note= on any command is the agent's reason for it: taken out here, so the game never sees it, and written with the command's log line for the watcher and later review. (Claude code Opus 5.5) -->
	kept = []
	for item in args.arguments:
		if item.startswith("note=") and args.command != "py":
			_log_context["note"] = item[5:]
		else:
			kept.append(item)
	args.arguments = kept
	if args.note:
		_log_context["note"] = args.note
	_log_context["operator"] = args.operator or os.environ.get("SAS_PILOT_OPERATOR") or None
	# <!-- custom: SAS_PILOT_OPERATOR_SESSION for any agent; Claude Code sets CLAUDE_CODE_SESSION_ID in its shell (seen 2026-11-14).
	# Codex sets CODEX_THREAD_ID (and CODEX_SESSION_ID), its rollout ID, as it reported the same day. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	_log_context["session"] = os.environ.get("SAS_PILOT_OPERATOR_SESSION") or os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CODEX_THREAD_ID") or None
	# <!-- custom: An agent's shell gives its session but not its model, and an agent can forget SAS_PILOT_OPERATOR for one call: two of this session's 'py' commands were logged without an operator (2026-11-14).
	# So the agent's kind names the operator when none is given; the session, the same either way, keeps those rows with the named ones. (Claude code Opus 5.5) -->
	if not _log_context["operator"]:
		if os.environ.get("CLAUDE_CODE_SESSION_ID"):
			_log_context["operator"] = "Claude Code"
		elif os.environ.get("CODEX_THREAD_ID"):
			_log_context["operator"] = "Codex"
	_log_context["command"] = args.command
	# <!-- custom: City and leader names can hold characters the Windows console code page lacks. (Claude code Fable 5.2) -->
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	reply_bytes = 0
	try:
		if args.command == "start":
			if args.timeout is None:
				args.timeout = 600.0
			result = start(args)
		elif args.command == "check":
			print_settings_check()
			return 0
		elif args.command == "list":
			result = live_mailboxes()
		elif args.command == "layout":
			result = {"placed": layout_clients()}
		else:
			pid = pick_pid(args.pid)
			if args.command != "close":
				ensure_watcher(pid)
			if args.command == "close":
				result = close(pid)
			elif args.command == "wait":
				result = wait_for_turn(pid, args.timeout or 600.0)
			elif args.command == "leave":
				result = leave_screens(pid, args.timeout or 60.0)
			elif args.command == "health":
				result = health(pid, args.timeout or 60.0)
			elif args.command == "review":
				result = review(pid)
			elif args.command == "operator":
				# <!-- custom: 'operator left' writes the closing row an agent cannot leave by just stopping, so the log shows who stopped piloting and when; 'operator joined' writes the opening row without a game command. (Claude code Opus 5.5) -->
				event = (args.arguments or ["joined"])[0]
				if event == "list":
					result = list_operators(pid)
				elif event not in ("joined", "left"):
					raise PilotError("operator takes 'joined', 'left' or 'list', not %r" % event)
				elif not _log_context["operator"]:
					raise PilotError("operator needs --operator \"<agent> <model>\" or SAS_PILOT_OPERATOR")
				else:
					written = _log_request(pid, "operator", {"event": event, "operator": _log_context["operator"]}, {"ok": True, "result": None}, None, kind="operator")
					# <!-- custom: The marker is this command's whole purpose, so say whether it reached the log; SAS_PILOT_LOG=0 or a failed write give written false (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
					result = {"operator": _log_context["operator"], "session": _log_context["session"], "event": event, "written": bool(written)}
			elif args.command == "price":
				price_args = {}
				for item in args.arguments:
					key, value = item.split("=", 1)
					price_args[key] = parse_value(value)
				result = ask_price(pid, price_args, args.timeout or 60.0)
			elif args.command == "bench":
				if not args.arguments:
					raise PilotError("bench needs a command, e.g. SASPilotClient.py bench ping")
				bench_args = {}
				for item in args.arguments[1:]:
					key, value = item.split("=", 1)
					bench_args[key] = parse_value(value)
				result = bench(pid, args.arguments[0], bench_args, args.count, args.timeout or 60.0)
			else:
				if args.command == "py":
					code = " ".join(args.arguments)
					if code == "-":
						code = sys.stdin.read()
					elif code.startswith("@"):
						code = Path(code[1:]).read_text(encoding="utf-8")
					command_args = {"code": code}
				else:
					command_args = {}
					for item in args.arguments:
						if "=" not in item:
							raise PilotError("expected key=value, got %r" % item)
						key, value = item.split("=", 1)
						command_args[key] = parse_value(value)
				# <!-- custom: Loading a save waits until that game is ready, unless --no-wait; see load_game. (Claude code Opus 5.5) -->
				# <!-- custom: 'save' too, so a bare name saves where 'start --save' and 'menu path=' find it; it took only a full path (2026-11-13). (Claude code Opus 5.5) -->
				if args.command in ("menu", "save") and command_args.get("path"):
					command_args["path"] = str(resolve_save(command_args["path"]))
				if args.command == "menu" and command_args.get("path") and not args.no_wait:
					result = load_game(pid, command_args["path"], args.timeout or 600.0)
					print(json.dumps(result, indent=None if args.compact else 1, ensure_ascii=False))
					return 0
				if args.command == "menu" and command_args.get("path"):
					check_save_mod(Path(command_args["path"]))
				# <!-- custom: With --turns the first turn was ended before anything was checked, so a batch could start by skipping a waiting unit or popup (Codex's review); now nothing is ended while something waits, and the digest says what. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if args.command == "endturn" and args.turns > 1:
					digest = call(pid, "turn", {}, 60.0)
					if digest_waits(digest):
						print_digest(digest, args.brief, True)
						return 0
				reply = request(pid, args.command, command_args, args.timeout or 60.0)
				if args.timing:
					print("roundTripMs=%f gameMs=%s servedOn=%s" % (reply["roundTripMs"], reply.get("gameMs"), reply.get("tick")), file=sys.stderr)
				if not reply.get("ok"):
					print(reply.get("error"), file=sys.stderr)
					print(reply.get("traceback", ""), file=sys.stderr)
					return 1
				result = reply.get("result")
				reply_bytes = reply["replyBytes"]
				if args.command == "endturn" and not args.no_wait:
					# <!-- custom: endturn first printed the ping of the new turn; a person then sees the turn's events and what waits, so print the game's 'turn' digest instead, with what the ended turn skipped (fog-on playthrough, 2026-11-13). (Claude code Opus 5.5) -->
					skipped = result.get("skipped")
					wait_for_turn(pid, args.timeout or 600.0, after_turn=result["gameTurn"])
					result = call(pid, "turn", {}, 60.0)
					if skipped:
						result["skippedLastTurn"] = skipped
					# <!-- custom: Playing the fog-on game, most turns needed nothing but End Turn, one call each, until a unit or city wanted orders; --turns repeats it as a person presses End Turn until something waits, printing the turns passed as single lines. (Claude code Opus 5.5) -->
					for _ in range(args.turns - 1):
						if digest_waits(result):
							break
						print_digest(result, args.brief, True)
						reply = request(pid, "endturn", {}, args.timeout or 60.0)
						if not reply.get("ok"):
							raise PilotError(reply.get("error"))
						wait_for_turn(pid, args.timeout or 600.0, after_turn=reply["result"]["gameTurn"])
						result = call(pid, "turn", {}, 60.0)
				# <!-- custom: The last digest was printed indented while the earlier ones were single lines (Codex's review); print every digest of a --turns batch alike. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if args.command == "endturn" and not args.no_wait and (args.brief or args.turns > 1):
					print_digest(result, args.brief, True)
					return 0
				if args.command == "py" and isinstance(result, dict):
					# <!-- custom: Show what the code printed as text, then its value. (Claude code Fable 5.2) -->
					if result.get("output"):
						sys.stdout.write(result["output"])
						if not result["output"].endswith("\n"):
							sys.stdout.write("\n")
					result = result.get("result")
					if result is None:
						return 0
	except PilotError as error:
		print("pilot: %s" % error, file=sys.stderr)
		remind(args, True)
		return 1
	remind(args, False)
	orjson = None
	if reply_bytes >= ORJSON_MIN_BYTES:
		orjson = load_orjson()
	if orjson is not None:
		# <!-- custom: orjson indents by 2 rather than 1; see ORJSON_MIN_BYTES. (Claude code Opus 5.5) -->
		sys.stdout.flush()
		sys.stdout.buffer.write(orjson.dumps(result, option=0 if args.compact else orjson.OPT_INDENT_2) + b"\n")
		return 0
	print(json.dumps(result, indent=None if args.compact else 1, ensure_ascii=False))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

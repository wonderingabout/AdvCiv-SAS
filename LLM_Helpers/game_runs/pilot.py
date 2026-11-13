#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Command-line client of SASPilot, the in-game bridge in Assets/Python/SASPilot.py: reads and drives a running Civ4 through JSON requests instead of screenshots and clicks.
# A request is a file req_<id>.json in the game's mailbox folder SASPilot/<pid>, written whole and renamed into place; the game answers with rep_<id>.json on its next frame.
# See _1_AdvCiv-SAS/Docs/Modding_Resources/README_Pilot.md for the commands and what was tried. (Claude code Fable 5.2 + Opus 5.5) -->

# <!-- custom: argparse reads the options, json the requests and replies, os and time the mailbox files and waits, sys the exit codes, uuid the request IDs, Path the folders. (Claude code Fable 5.2) -->
import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

# <!-- custom: desktop_windows launches and closes Civ4; run_autoplay writes the per-run INI and reads save headers. (Claude code Fable 5.2) -->
# <!-- custom: Both are imported only in the functions that need them: they took 18 of the 38 ms that importing this file cost, and every command starts a new Python (2026-11-13). (Claude code Opus 5.5) -->

# <!-- custom: The same folder as run_autoplay.USER_DIR, computed here so a plain request does not import run_autoplay. (Claude code Opus 5.5) -->
MAILBOX_ROOT = Path(os.environ["USERPROFILE"]) / "Documents" / "My Games" / "beyond the sword" / "SASPilot"
# <!-- custom: Replies at least this large are parsed and printed with orjson instead of the json module. On a Huge map's 1.6 MB plot reply the json module took 9 ms to parse and 58 ms to print indented, against 7 and 2 ms (2026-11-13); orjson costs about 27 ms to import, so small replies keep the json module. (Claude code Opus 5.5) -->
ORJSON_MIN_BYTES = 200000
# <!-- custom: How often the client looks for the reply. It was 0.02 s, which became most of the wait once the game served requests every frame; 0.001 s measured below 3 ms per ping (2026-11-13). (Claude code Opus 5.5) -->
POLL_SECONDS = 0.001


class PilotError(Exception):
	pass


def live_mailboxes():
	import desktop_windows
	# <!-- custom: A mailbox outlives its process, so keep only folders whose PID still runs; a recycled PID that is not Civ4 never answers and times out. (Claude code Fable 5.2) -->
	result = []
	if MAILBOX_ROOT.is_dir():
		for folder in MAILBOX_ROOT.iterdir():
			if folder.name.isdigit() and desktop_windows.process_alive(int(folder.name)):
				result.append(int(folder.name))
	return sorted(result)


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
		raise PilotError("no piloted Civ4 is running; start one with: pilot.py start")
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
	# <!-- custom: Returns the reply dict: ok, result or error and traceback, gameTurn. The game serves requests on its updates, every frame in game, so a reply can wait behind a long AI turn or a load. (Claude code Fable 5.2 + Opus 5.5) -->
	mailbox = MAILBOX_ROOT / str(pid)
	if not mailbox.is_dir():
		raise PilotError("no mailbox %s; is the pilot on for that client?" % mailbox)
	request_id = "%d_%s" % (time.time_ns(), uuid.uuid4().hex[:8])
	# <!-- custom: roundTripMs runs from writing the request to reading the reply; with the game's gameMs it splits a request into serving time and waiting for the game to look. (Claude code Opus 5.5) -->
	started = time.perf_counter()
	text = json.dumps({"id": request_id, "cmd": command, "args": args or {}})
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
				time.sleep(POLL_SECONDS)
				continue
			# <!-- custom: Replies are renamed into place whole, so one that does not parse is a bridge bug, not a write in progress: retrying it hid an invalid reply behind a timeout. The file is kept for inspection. (Claude code Fable 5.2) -->
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
			import desktop_windows
			if not desktop_windows.process_alive(pid):
				try:
					(mailbox / request_name).unlink()
				except OSError:
					pass
				raise PilotError("Civ4 %d has exited" % pid)
		if time.monotonic() > deadline:
			# <!-- custom: Withdraw the unanswered request so it does not run later, out of context. (Claude code Fable 5.2) -->
			try:
				(mailbox / request_name).unlink()
			except OSError:
				pass
			import desktop_windows
			if not desktop_windows.process_alive(pid):
				raise PilotError("Civ4 %d has exited" % pid)
			raise PilotError("no reply to %r within %g s; Civ4 %d may be loading, in a long turn, at the main menu or showing a dialog" % (command, timeout, pid))
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
	# <!-- custom: Loads a save in a running client and returns once that game waits for orders. Waiting for an active turn alone returned at once on the game being left, which still answered as in game, so the first commands after a load ran on the old game (2026-11-13); SASPilot counts finished loads, and this waits for the count to rise. (Claude code Opus 5.5) -->
	check_save_mod(Path(path))
	before = call(pid, "ping").get("loads")
	if before is None:
		raise PilotError("this client's SASPilot does not count loads; restart Civ4 so its Python includes SASPilot.onLoad")
	call(pid, "menu", {"path": str(path)})
	return wait_for_turn(pid, timeout, after_loads=before)


def resolve_save(name):
	# <!-- custom: pilot_replay.py already took a bare name from Saves/single, while start --save took only a path, so on 2026-11-13 "start --save sas_pilot_fogplay_t148" failed; both now share this lookup. The extension may be left out too. (Claude code Opus 5.5) -->
	# <!-- custom: The extension is added before anything is looked up, and only a bare name falls back to Saves/single: the first draft checked the path without its extension, so "samples/local" went to Saves/single although samples/local.CivBeyondSwordSave existed (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	save = Path(name)
	if not save.suffix:
		save = save.with_suffix(".CivBeyondSwordSave")
	if not save.is_absolute() and save.parent == Path(".") and not save.is_file():
		save = Path(MAILBOX_ROOT).parent / "Saves" / "single" / save.name
	return save.resolve()


def check_save_mod(path):
	# <!-- custom: Every mod names its saves "PC BC-<year>" by default, so on 2026-11-13 a Caveman2Cosmos save in the shared Saves folder was taken for an AdvCiv-SAS one, and Civ4 stopped on a dialog asking to restart into that mod, which the pilot cannot answer.
	# So the pilot refuses a save made for another mod before Civ4 sees it. See "Loading a save" in README_Pilot.md. (Claude code Opus 5.5) -->
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


def start(args):
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
		for key, value in (("Map", args.map), ("WorldSize", args.world_size), ("GameSpeed", args.speed), ("QuickHandicap", args.handicap)):
			if value:
				settings[key] = value
		if args.fixed_seeds:
			settings["SyncRandSeed"] = "1"
			settings["MapRandSeed"] = "1"
	running = desktop_windows.civ4_processes()
	if running and not args.multiple:
		raise PilotError("Civ4 is already running (%s); close it or pass --multiple" % ", ".join(str(p) for p, _ in running))
	remove_dead_mailboxes()
	ini_name = "SASPilot_%s_%d.ini" % (time.strftime("%Y%m%dT%H%M%S"), os.getpid())
	ini_path = desktop_windows.DEFAULT_CIV4_DIR / ini_name
	run_autoplay.write_request_ini(run_autoplay.USER_DIR / "CivilizationIV.ini", ini_path, None, False, "-", "Pilot", settings, extra_lines=["[SASPilot]", "On = 1"])
	arguments = "ini=%s" % ini_name
	if save is not None:
		arguments = '/FXSLOAD="%s" %s' % (save, arguments)
	if args.multiple:
		arguments += " multiple"
	pid = desktop_windows.launch_detached(arguments)
	print("launched pid %d: %s" % (pid, arguments), file=sys.stderr, flush=True)
	deadline = time.monotonic() + args.timeout
	while not (MAILBOX_ROOT / str(pid) / "hello.json").exists():
		if not desktop_windows.process_alive(pid):
			raise PilotError("Civ4 %d exited while starting" % pid)
		if time.monotonic() > deadline:
			raise PilotError("no mailbox for pid %d within %g s; per-run INI left at %s" % (pid, args.timeout, ini_path))
		time.sleep(0.5)
	state = wait_for_turn(pid, max(5.0, deadline - time.monotonic()))
	state["iniFile"] = str(ini_path)
	# <!-- custom: Fog is the game-side session's switch and starts off, so relaunching the fog-on playthrough at turn 156 silently gave full sight until a reply showed "fog": false three turns later (2026-11-13). --fog switches it on before the first command. (Claude code Opus 5.5) -->
	if args.fog:
		reply = request(pid, "fog", {"on": 1}, 60.0)
		if not reply.get("ok"):
			raise PilotError("could not switch fog on: %s" % reply.get("error"))
		state["fog"] = True
	return state


def _bridge(pid, command, command_args, timeout):
	reply = request(pid, command, command_args, timeout)
	if not reply.get("ok"):
		raise PilotError("%s: %s" % (command, reply.get("error")))
	return reply["result"]


def _reply_with(pid, screen, comments, timeout, bound=None):
	# <!-- custom: bound is (partner, conversation): Codex's review mocked another leader's trade screen opening before the one 'price' asked for, and 'price' accepted that leader's counter-offer, then declined in his conversation. A screen of anyone else, or of a later conversation, is now refused before any reply. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if bound is not None and (screen.get("who"), screen.get("conversation")) != bound:
		raise PilotError("the screen is now with player %s, conversation %s, not %s; see 'diplo'" % (screen.get("who"), screen.get("conversation"), bound))
	for comment in comments:
		for choice in screen.get("replies", []):
			if choice["comment"] == comment:
				return _bridge(pid, "reply", {"n": choice["n"], "screen": screen["screen"]}, timeout)
	return None


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
	# <!-- custom: Selling, with only our own items on the table, the screen asks "What will you give me for this?" (FISH_FOR_DEAL) instead of "What do you want for this?" (OFFER): offering Monarchy to Moctezuma at turn 120 of the second fog-on game came back unpriced (2026-11-13). (Claude code Opus 5.5) -->
	# <!-- custom: With items on both sides, the screen offers "Can you complete this deal?" (COMPLETE_DEAL) and Propose instead: Navigation against Meditation and Drama with Kublai at turn 133 came back unpriced. COMPLETE_DEAL is the counter-offer the window gives for such a table. (Claude code Opus 5.5) -->
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
	# <!-- custom: Leave without agreeing: decline a counter-offer, then exit; a few rounds, as each reply can bring a new AI line. Whether the screen closed is reported, rather than returning with it still open after the last round (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	result["screenClosed"] = False
	# <!-- custom: A stop while leaving is reported in the result, not raised: Codex's review mocked a new conversation opening after the acceptance, and the raised error discarded acceptSent, so a caller could retry a purchase already sent. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	try:
		for _ in range(4):
			screen = _bridge(pid, "diplo", {}, timeout)
			if not screen.get("open"):
				result["screenClosed"] = True
				break
			if _reply_with(pid, screen, ["USER_DIPLOCOMMENT_EXIT", "USER_DIPLOCOMMENT_REJECT", "USER_DIPLOCOMMENT_NEVERMIND"], timeout, bound) is None:
				raise PilotError("could not leave the screen; see 'diplo'")
		# <!-- custom: The last check after the fourth round sat outside this handler, so its failure could still drop acceptSent (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if not result["screenClosed"] and not _bridge(pid, "diplo", {}, timeout).get("open"):
			result["screenClosed"] = True
	except PilotError as error:
		result["cleanupStopped"] = str(error)
	return result


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
	if digest.get("skippedLastTurn"):
		print("T%d skipped last turn: %s" % (turn, json.dumps(digest["skippedLastTurn"], ensure_ascii=False)))


def main():
	parser = argparse.ArgumentParser(description="Read and drive a running Civ4 (AdvCiv-SAS) through SASPilot. Examples: pilot.py start --map Pangaea; pilot.py help; pilot.py units; pilot.py move unit=3 x=10 y=12; pilot.py py \"game.getGameTurn()\"; pilot.py endturn; pilot.py close")
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
	parser.add_argument("--multiple", action="store_true", help="start: allow other Civ4 clients and pass Civ4's 'multiple' argument")
	parser.add_argument("--timing", action="store_true", help="print the request's roundTripMs and gameMs on stderr")
	parser.add_argument("--count", type=int, default=20, help="bench: how many requests to send")
	parser.add_argument("--no-wait", action="store_true", help="endturn: return at once instead of waiting for the active player's next turn; menu path=: return without waiting for the load")
	parser.add_argument("--turns", type=int, default=1, help="endturn: end up to this many turns, stopping early at a turn where something waits for orders (as 'todo' lists it); prints each turn's digest as one line")
	parser.add_argument("--brief", action="store_true", help="endturn: print each turn's digest as short text lines (turn, messages, what waits) instead of JSON")
	parser.add_argument("command", help="start, list, wait, close, price with= take=[...] give=[...] [accept=1] (an AI's counter-offer; nothing agreed unless accept=1), bench <command> [key=value...], or a bridge command ('help' lists them)")
	parser.add_argument("arguments", nargs="*", help="key=value pairs; for 'py', the code itself, '-' for stdin or @file")
	args = parser.parse_args()
	# <!-- custom: City and leader names can hold characters the Windows console code page lacks. (Claude code Fable 5.2) -->
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	reply_bytes = 0
	try:
		if args.command == "start":
			if args.timeout is None:
				args.timeout = 600.0
			result = start(args)
		elif args.command == "list":
			result = live_mailboxes()
		else:
			pid = pick_pid(args.pid)
			if args.command == "close":
				result = close(pid)
			elif args.command == "wait":
				result = wait_for_turn(pid, args.timeout or 600.0)
			elif args.command == "price":
				price_args = {}
				for item in args.arguments:
					key, value = item.split("=", 1)
					price_args[key] = parse_value(value)
				result = ask_price(pid, price_args, args.timeout or 60.0)
			elif args.command == "bench":
				if not args.arguments:
					raise PilotError("bench needs a command, e.g. pilot.py bench ping")
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
		return 1
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

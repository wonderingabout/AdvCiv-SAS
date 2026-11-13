#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Unattended AI Auto Play from the command line: launch Civ4 with a save, play the requested turns, report how the run ended, and exit Civ4.
# The request reaches the game through an [SASAutoplay] section in a per-run INI passed as ini=, read by Assets/Python/SASAutoplayRequest.py; the save loads through the EXE's /FXSLOAD= argument.
# Completion is read from this process's own SASRuntimeHistory_<start>_<pid>.jsonl, not the shared SASRuntimeStatus.json, which two clients overwrite (see changes_new.md). (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; datetime stamps the run; json reads the history rows and writes the summary. (Claude Code Opus 5.5) -->
import argparse
import datetime
import json
# <!-- custom: os, re and struct handle the environment, INI lines and the save header. (Claude Code Opus 5.5) -->
import os
import re
import struct
# <!-- custom: sys, time and pathlib handle exit codes, polling waits and paths. (Claude Code Opus 5.5) -->
import sys
import time
from pathlib import Path

# <!-- custom: desktop_windows, beside this script, launches, screenshots and closes Civ4. (Claude Code Opus 5.5) -->
import desktop_windows

# <!-- custom: importlib loads housekeeping/archive_old_files.py from its file for the folder upkeep at the end of a run, without a sys.path entry. (Claude code Opus 5.5) -->
import importlib.util

_ARCHIVE_SPEC = importlib.util.spec_from_file_location("archive_old_files", Path(__file__).resolve().parents[1] / "housekeeping" / "archive_old_files.py")
if _ARCHIVE_SPEC is None or _ARCHIVE_SPEC.loader is None:
	raise SystemExit("cannot load LLM_Helpers/housekeeping/archive_old_files.py")
archive_old_files = importlib.util.module_from_spec(_ARCHIVE_SPEC)
_ARCHIVE_SPEC.loader.exec_module(archive_old_files)

REPO_ROOT = next(p for p in Path(__file__).resolve().parents if p.name == "LLM_Helpers").parent
MOD_FOLDER = REPO_ROOT.name
USER_DIR = Path(os.environ["USERPROFILE"]) / "Documents" / "My Games" / "beyond the sword"
LOGS_DIR = USER_DIR / "Logs"
# <!-- custom: Write reports directly in Logs so an issue report can collect them with SGR and Runtime without tracking down separate run folders.
# The same Explorer view can sort these files by date or size, and the Logs archive can move them together.
# Optional PNGs can dwarf their JSON reports, so keep them in Downloads for separate review and cleanup. (GPT-6.1-Sol) -->
DEFAULT_OUTPUT_ROOT = LOGS_DIR
DEFAULT_SCREENSHOT_ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "AdvCiv-SAS_LLM" / "autoplay_screenshots"

# <!-- custom: Outcomes, from best to worst. (Claude Code Opus 5.5) -->
COMPLETED = "COMPLETED"  # <!-- custom: autoplay ended as scheduled (Claude Code Opus 5.5) -->
ENDED_EARLY = "ENDED_EARLY"  # <!-- custom: autoplay ended for another recorded cause (victory, defeat, assertion, interruption...) (Claude Code Opus 5.5) -->
NOT_STARTED = "NOT_STARTED"  # <!-- custom: the save loaded but autoplay never started (Claude Code Opus 5.5) -->
STALLED = "STALLED"  # <!-- custom: Civ4 is alive but no turn progress for --stall-minutes (Claude Code Opus 5.5) -->
FAILURE_DIALOG = "FAILURE_DIALOG"  # <!-- custom: the Runtime dialog observer saw a runtime-error or crash dialog (Claude Code Opus 5.5) -->
EXITED = "EXITED"  # <!-- custom: Civ4 exited before autoplay ended (Claude Code Opus 5.5) -->
TIMED_OUT = "TIMED_OUT"  # <!-- custom: --timeout-minutes elapsed (Claude Code Opus 5.5) -->
REQUEST_FAILED = "REQUEST_FAILED"  # <!-- custom: SASAutoplayRequest.py raised an error naming this run's request, such as leaders not applied; a rejected request now stops before autoplay starts (Claude Code Opus 5.5) -->


def utc_now():
	return datetime.datetime.now(datetime.timezone.utc)


def stamp(moment):
	return moment.strftime("%Y%m%dT%H%M%SZ")


def save_mod_folder(save_path):
	# <!-- custom: A BtS save begins with a 4-byte version, then a 4-byte length and the mod path, e.g. "Mods\AdvCiv-SAS\"; an empty path means no mod. (Claude Code Opus 5.5) -->
	with open(save_path, "rb") as handle:
		header = handle.read(8 + 260)
	# <!-- custom: A file shorter than the header raised struct.error rather than this message; pilot.py shares this reader (Codex's review). """+C+""" -->
	if len(header) < 8:
		raise ValueError("%s does not look like a Civ4 save (%d bytes)" % (save_path, len(header)))
	length = struct.unpack_from("<i", header, 4)[0]
	if length < 0 or length > 260:
		raise ValueError("%s does not look like a Civ4 save (mod path length %d)" % (save_path, length))
	if len(header) < 8 + length:
		raise ValueError("%s ends inside its mod path" % save_path)
	return header[8:8 + length].decode("latin-1")


# <!-- custom: extra_lines appends further sections, such as pilot.py's [SASPilot]; added as an optional last parameter so existing callers are unchanged. (Claude code Fable 5.2) -->
def write_request_ini(base_ini, out_ini, turns, debug_mode, run_id, alias, game_settings, leaders=None, extra_lines=None):
	# <!-- custom: Copy the user's CivilizationIV.ini so graphics and audio settings match, then load this mod in a window and append the autoplay request.
	# game_settings overrides further existing keys by name, such as QuickStart and the [GAME] keys of a new game. (Claude Code Opus 5.5) -->
	text = base_ini.read_bytes().decode("latin-1")
	overrides = {"mod": "Mods\\%s" % MOD_FOLDER, "fullscreen": "0", "alias": alias}
	overrides.update((key.lower(), value) for key, value in game_settings.items())
	lines = []
	in_request = False
	for line in text.splitlines():
		header = re.match(r"\s*\[([^\]]+)\]", line)
		if header:
			in_request = header.group(1).strip().lower() == "sasautoplay"
		if in_request:
			continue
		key = re.match(r"\s*([A-Za-z]+)\s*=", line)
		if key and key.group(1).lower() in overrides:
			line = "%s = %s" % (key.group(1), overrides.pop(key.group(1).lower()))
		lines.append(line)
	if overrides:
		raise ValueError("%s lacks the keys %s" % (base_ini, ", ".join(sorted(overrides))))
	# <!-- custom: turns=None writes no request, so the game waits at turn 0 without autoplay: map_preview_dds.py needs a map with no cities yet (2026-11-12). (Claude code Opus 5.5) -->
	if turns is not None:
		lines += ["", "[SASAutoplay]", "Turns = %d" % turns, "DebugMode = %d" % int(debug_mode), "RunId = %s" % run_id]
		if leaders:
			lines.append("Leaders = %s" % leaders)
	if extra_lines:
		lines += [""] + list(extra_lines)
	lines.append("")
	out_ini.write_bytes("\r\n".join(lines).encode("latin-1"))


def find_history(pid, since):
	# <!-- custom: Runtime names its history SASRuntimeHistory_<processStartUtc>_<pid>.jsonl; the PID alone could match an older run. (Claude Code Opus 5.5) -->
	for path in LOGS_DIR.glob("SASRuntimeHistory_*_%d.jsonl" % pid):
		if path.stat().st_mtime >= since.timestamp() - 5:
			return path
	return None


def read_records(path):
	records = []
	with open(path, encoding="utf-8", errors="replace") as handle:
		for line in handle:
			line = line.strip()
			if not line:
				continue
			try:
				records.append(json.loads(line))
			except ValueError:
				pass  # <!-- custom: an append in progress; the next poll reads it whole (Claude Code Opus 5.5) -->
	return records


def read_exit_observation(pid, since):
	for path in LOGS_DIR.glob("SASRuntimeExit_*_%d.json" % pid):
		if path.stat().st_mtime >= since.timestamp() - 5:
			try:
				return json.loads(path.read_text(encoding="utf-8-sig"))
			except ValueError:
				return None
	return None


def newer_files(folder, pattern, since):
	cutoff = since.timestamp() - 2
	return sorted(str(p) for p in folder.rglob(pattern) if p.stat().st_mtime >= cutoff)


def own_game_record(candidates, run_id, pid):
	# <!-- custom: SGR199+ names the writing client's processId in its session header and the request's RunId in its INI settings snapshot.
	# Either identifies this run's file; other clients' files name their own.
	# A DLL built before SGR199 has the RunId only. (Claude Code Opus 5.5) -->
	run_marker = "SASAutoplay.RunId=%s" % run_id
	pid_marker = " processId=%d " % pid
	for path in candidates:
		with open(path, encoding="latin-1") as handle:
			for line in handle:
				if line.startswith("GAME_RECORD_SESSION_SETTINGS") and run_marker in line:
					return path
				if line.startswith("GAME_RECORD_") and " processUtc=" in line and pid_marker in line:
					return path
	return None


def python_errors(since):
	path = LOGS_DIR / "PythonErr.log"
	if not path.exists() or path.stat().st_mtime < since.timestamp() or path.stat().st_size == 0:
		return []
	return path.read_text(encoding="latin-1").splitlines()[-30:]


def summarize_transitions(records):
	state = {"loaded": False, "started": None, "ended": None, "turn": -1, "lastPopup": None}
	for record in records:
		if record.get("gameTurn", -1) >= 0:
			state["turn"] = record["gameTurn"]
		if record.get("record") != "transition":
			continue
		if record.get("state") == "PLAYING" and record.get("reason") == "LOAD_GAME_NATIVE_READY":
			state["loaded"] = True
		if record.get("reason") == "AUTOPLAY_STARTED":
			state["started"] = record
		if record.get("reason") == "AUTOPLAY_ENDED":
			state["ended"] = record
		if record.get("buttonPopupAwaitingInteraction"):
			state["lastPopup"] = {k: record.get(k) for k in ("buttonPopupType", "buttonPopupTypeId", "buttonPopupFocusedUtc", "gameTurn")}
	return state


def request_error(launched, run_id):
	# <!-- custom: PythonErr.log is shared by every client, so count only an error naming this run's RunId: another client's bad request once marked a normal run REQUEST_FAILED. See KI#1081. (Claude Code Opus 5.5) -->
	return any("[SASAutoplay RunId=%s]" % run_id in line for line in python_errors(launched))


def wait_for_outcome(pid, launched, args, run_id):
	deadline = time.monotonic() + args.timeout_minutes * 60
	start_deadline = time.monotonic() + args.start_minutes * 60
	last_size = -1
	last_progress = time.monotonic()
	history = None
	state = summarize_transitions([])
	while True:
		time.sleep(2)
		alive = desktop_windows.process_alive(pid)
		if history is None:
			history = find_history(pid, launched)
		if history is not None:
			size = history.stat().st_size
			if size != last_size:
				last_size = size
				last_progress = time.monotonic()
				state = summarize_transitions(read_records(history))
				if args.verbose:
					print("  turn=%d loaded=%d autoplay=%s" % (state["turn"], state["loaded"], "ENDED" if state["ended"] else ("ON" if state["started"] else "-")), flush=True)
		if state["ended"] is not None:
			cause = state["ended"].get("autoplayEndCause")
			return (COMPLETED if cause == "SCHEDULED" else ENDED_EARLY), state, history
		if not alive:
			return EXITED, state, history
		observation = read_exit_observation(pid, launched)
		if observation and observation.get("failureDialog"):
			return FAILURE_DIALOG, state, history
		# <!-- custom: SASAutoplayRequest.py now rejects a bad request before arming any turns, so autoplay never starts and the run used to wait out --start-minutes as NOT_STARTED, as Codex's 2026-11-10 review found; stop as soon as the request's error appears. (Claude Code Opus 5.5) -->
		if state["started"] is None and request_error(launched, run_id):
			return REQUEST_FAILED, state, history
		if state["started"] is None and time.monotonic() > start_deadline:
			return NOT_STARTED, state, history
		if state["started"] is not None and time.monotonic() - last_progress > args.stall_minutes * 60:
			return STALLED, state, history
		if time.monotonic() > deadline:
			return TIMED_OUT, state, history


def close_civ4(pid, wait_seconds=90):
	# <!-- custom: Ask politely first; force only if the window does not close, so logs are flushed by Civ4's own shutdown. (Claude Code Opus 5.5) -->
	if desktop_windows.request_close(pid):
		end = time.monotonic() + wait_seconds
		while time.monotonic() < end:
			if not desktop_windows.process_alive(pid):
				return "CLOSED"
			time.sleep(1)
	if not desktop_windows.process_alive(pid):
		return "CLOSED"
	os.system("taskkill /PID %d /F >NUL 2>&1" % pid)
	return "KILLED"


def main():
	parser = argparse.ArgumentParser(description="Launch Civ4 into a save, run AI Auto Play for N turns, report the outcome and exit.")
	parser.add_argument("save", type=Path, nargs="?", help="the .CivBeyondSwordSave to load; it is only read. Omit it with --new-game")
	parser.add_argument("--new-game", action="store_true", help="start a new game with QuickStart instead of loading a save; the base INI's [GAME] settings apply unless overridden below")
	parser.add_argument("--map", help="map script name without .py, e.g. Pangaea")
	parser.add_argument("--world-size", help="e.g. WORLDSIZE_STANDARD")
	parser.add_argument("--speed", help="e.g. GAMESPEED_NORMAL")
	parser.add_argument("--handicap", help="e.g. HANDICAP_NOBLE")
	parser.add_argument("--era", help="e.g. ERA_ANCIENT")
	parser.add_argument("--climate", help="e.g. CLIMATE_TEMPERATE")
	parser.add_argument("--sea-level", help="e.g. SEALEVEL_MEDIUM")
	parser.add_argument("--fixed-seeds", action="store_true", help="set SyncRandSeed and MapRandSeed to 1 for a repeatable new game")
	parser.add_argument("--leaders", help="comma-separated leader types for the civ slots in order, '-' keeping a random one, e.g. LEADER_ALEXANDER,-,LEADER_MANSA_MUSA (needs an SGR199+ DLL)")
	parser.add_argument("--turns", type=int, required=True, help="AI Auto Play turns; counts the loaded turn, so 5 from T0 plays T0-T4")
	# <!-- custom: Debug Mode seems to change the AI's game: from one save, runs with and without it diverged by T84 while same-mode pairs matched.
	# Offered for watching, not for comparisons. See KI#1080. (Claude Code Opus 5.5) -->
	parser.add_argument("--debug-mode", action="store_true", help="turn on Debug Mode (whole map visible) before autoplay starts; it seems to change the game, so leave it off for comparisons (KI#1080)")
	parser.add_argument("--keep-open", action="store_true", help="leave Civ4 running after the outcome instead of closing it")
	parser.add_argument("--multiple", action="store_true", help="allow other Civ4 clients to be running and pass Civ4's 'multiple' argument")
	parser.add_argument("--timeout-minutes", type=float, default=240)
	parser.add_argument("--stall-minutes", type=float, default=15, help="no turn progress for this long while autoplaying counts as STALLED")
	parser.add_argument("--start-minutes", type=float, default=5, help="autoplay must start within this long after launch")
	parser.add_argument("--base-ini", type=Path, default=USER_DIR / "CivilizationIV.ini")
	parser.add_argument("--civ4-dir", type=Path, default=desktop_windows.DEFAULT_CIV4_DIR)
	parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="directory for JSON reports")
	parser.add_argument("--screenshot-root", type=Path, default=DEFAULT_SCREENSHOT_ROOT, help="directory for optional final PNGs")
	parser.add_argument("--no-screenshot", action="store_true", help="skip the optional final window capture")
	parser.add_argument("--verbose", action="store_true")
	args = parser.parse_args()

	game_settings = {}
	if args.new_game:
		if args.save is not None:
			sys.exit("pass either a save or --new-game, not both")
		save = None
		game_settings["QuickStart"] = "1"
		for key, value in (("Map", args.map), ("WorldSize", args.world_size), ("GameSpeed", args.speed), ("QuickHandicap", args.handicap), ("Era", args.era), ("Climate", args.climate), ("SeaLevel", args.sea_level)):
			if value:
				game_settings[key] = value
		if args.fixed_seeds:
			game_settings["SyncRandSeed"] = "1"
			game_settings["MapRandSeed"] = "1"
	else:
		if args.save is None:
			sys.exit("pass a save, or --new-game")
		if args.leaders:
			sys.exit("--leaders applies to --new-game only; a save already has its leaders")
		save = args.save.resolve()
		if not save.is_file():
			sys.exit("save not found: %s" % save)
		mod_path = save_mod_folder(save)
		if mod_path.strip("\\").lower() != ("Mods\\%s" % MOD_FOLDER).lower():
			sys.exit("%s was saved with mod %r, not Mods\\%s" % (save.name, mod_path, MOD_FOLDER))
		# <!-- custom: QuickStart would start a new game instead of loading the save. (Claude Code Opus 5.5) -->
		game_settings["QuickStart"] = "0"
		# <!-- custom: The save brings its own map, but Civ4 checks the INI's last map script at startup: the user's C2C_Arboria from Caveman2Cosmos raised "Map script not found" in an assertion-enabled DLL. (Claude Code Opus 5.5) -->
		game_settings["Map"] = "Pangaea"
	if args.turns <= 0:
		sys.exit("--turns must be positive")
	running = desktop_windows.civ4_processes()
	if running and not args.multiple:
		sys.exit("Civ4 is already running (%s); close it or pass --multiple" % ", ".join(str(pid) for pid, _ in running))

	launched = utc_now()
	run_id = "%s_%d" % (stamp(launched), os.getpid())
	args.output_root.mkdir(parents=True, exist_ok=True)
	ini_name = "SASAutoplay_%s.ini" % run_id
	ini_path = args.civ4_dir / ini_name
	write_request_ini(args.base_ini, ini_path, args.turns, args.debug_mode, run_id, "Autoplay", game_settings, args.leaders)
	if save is None:
		arguments = "ini=%s" % ini_name
	else:
		# <!-- custom: /FXSLOAD must come first and be quoted: placed after ini= or unquoted, Civ4 opened at the main menu. (Claude Code Opus 5.5) -->
		arguments = '/FXSLOAD="%s" ini=%s' % (save, ini_name)
	if args.multiple:
		arguments += " multiple"
	pid = None
	closed = "LEFT_OPEN"
	try:
		pid = desktop_windows.launch_detached(arguments, args.civ4_dir)
		print("launched pid %d: %s" % (pid, arguments), flush=True)

		outcome, state, history = wait_for_outcome(pid, launched, args, run_id)
		finished = utc_now()
		screenshot = None
		if not args.no_screenshot and desktop_windows.process_alive(pid):
			try:
				# <!-- custom: Use capture UTC and the Civ4 PID so screenshots from parallel runs can share one sortable folder. (GPT-6.1-Sol) -->
				screenshot_name = "SASAutoplay_%s_%d_final.png" % (stamp(utc_now()), pid)
				screenshot_path = args.screenshot_root / screenshot_name
				screenshot = str(desktop_windows.screenshot(pid, screenshot_path)[0])
			except Exception as error:  # <!-- custom: a screenshot is evidence, not a requirement (Claude Code Opus 5.5) -->
				screenshot = "failed: %s" % error
	finally:
		# <!-- custom: A failed log read or Ctrl+C used to skip shutdown and leave the request INI behind.
		# Close only the client this runner launched.
		# Keep its INI if the user asked to leave that client open. (GPT-6.1-Sol) -->
		if pid is None or not args.keep_open:
			try:
				if pid is not None:
					closed = close_civ4(pid) if desktop_windows.process_alive(pid) else "ALREADY_EXITED"
			finally:
				# <!-- custom: Civ4 also leaves a .bak copy of the INI it was started with; 56 of them had piled up in the game folder by 2026-11-12. (Claude code Opus 5.5) -->
				for leftover in (ini_path, ini_path.with_name(ini_path.name + ".bak")):
					try:
						leftover.unlink()
					except OSError:
						pass
	time.sleep(2)

	errors = python_errors(launched)
	if outcome == COMPLETED and request_error(launched, run_id):
		outcome = REQUEST_FAILED
	ended = state["ended"] or {}
	game_records = newer_files(LOGS_DIR, "SASGameRecord_*.log", launched)
	summary = {
		"outcome": outcome,
		"pid": pid,
		"save": str(save) if save else None,
		"newGameSettings": game_settings if args.new_game else None,
		"requestedTurns": args.turns,
		"debugMode": args.debug_mode,
		"startTurn": (state["started"] or {}).get("gameTurn"),
		"endTurn": ended.get("gameTurn"),
		"lastTurnSeen": state["turn"],
		"autoplayEndCause": ended.get("autoplayEndCause"),
		"autoplaySeconds": (ended.get("previousDurationMilliseconds", -1) / 1000.0) if ended else None,
		"launchedUtc": stamp(launched),
		"finishedUtc": stamp(finished),
		"wallSeconds": round((finished - launched).total_seconds(), 1),
		"civ4": closed,
		"exitObservation": {k: (read_exit_observation(pid, launched) or {}).get(k) for k in ("outcome", "exitCode", "failureDialog")},
		"lastAwaitedPopup": state["lastPopup"],
		"runtimeHistory": str(history) if history else None,
		"gameRecord": own_game_record(game_records, run_id, pid),
		"gameRecordsSinceLaunch": game_records,
		"newSaves": newer_files(USER_DIR / "Saves", "*.CivBeyondSwordSave", launched),
		"pythonErrors": errors,
		"screenshot": screenshot,
	}
	if args.multiple:
		summary["note"] = "Other clients may have written some gameRecordsSinceLaunch and newSaves; gameRecord is this run's own."
	# <!-- custom: Publish the run-specific summary only after its contents are complete, so readers see a complete report when its final filename appears. (GPT-6.1-Sol) -->
	summary_path = args.output_root / ("SASAutoplay_%s.json" % run_id)
	summary_temp = summary_path.with_suffix(".tmp")
	summary_text = json.dumps(summary, indent=2)
	summary_temp.write_text(summary_text, encoding="utf-8")
	summary_temp.replace(summary_path)
	print(summary_text)
	print("summary: %s" % summary_path)
	# <!-- custom: Tidies the folders this runner fills, Logs and the autoplay screenshots, once its own client is closed: a folder over 1,000 entries keeps its newest 1,000 and moves the rest into an old_<UTC> subfolder.
	# The user asked on 2026-11-12 for upkeep that agents need not remember, as Logs had grown to 5,363 files; archive_crowded does nothing while any Civ4 runs, such as a client left open with --keep-open. (Claude code Opus 5.5) -->
	try:
		archive_old_files.archive_crowded()
	except OSError as error:
		print("folder upkeep skipped: %s" % error)
	sys.exit(0 if outcome == COMPLETED else 1)


if __name__ == "__main__":
	main()

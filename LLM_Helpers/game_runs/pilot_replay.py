#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Replays a list of pilot commands against a save and compares the replies with the last accepted run, so a DLL rebuild or a SASPilotCommands.py edit that changes a command's answer shows up as a diff instead of in the middle of a playthrough.
# By 2026-11-13 the command file had grown to 1,800 lines and the Debug-opt DLL had been rebuilt about ten times in one day, each round checked only by hand. See "Replaying commands" in README_Pilot.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, json the sequence and baselines, sys the exit code, Path the files; pilot is the client whose start, request and close this reuses. (Claude code Opus 5.5) -->
import argparse
import json
import re
import sys
import time
from pathlib import Path

import pilot

# <!-- custom: Keys whose values change from run to run without the command having changed: timings and the reply's size. (Claude code Opus 5.5) -->
# <!-- custom: "conversation", 'diplo''s count of conversations since Civ4 started, depends on what the client did before the sequence loaded its save: 21 and 22 in a reused client against no field in the baselines (2026-11-13). (Claude code Opus 5.5) -->
VOLATILE_KEYS = ("roundTripMs", "gameMs", "tick", "replyBytes", "iniFile", "conversation")
LOGS_DIR = Path(pilot.MAILBOX_ROOT).parent / "Logs"


def load_sequence(path):
	# <!-- custom: Called scenarios until 2026-11-13; Civ4 already uses "scenario" for its scenario maps and "replay" for Hall of Fame replays, so these became command sequences, in pilot_sequences/ (the user and Codex's naming discussion). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: A sequence is JSON: {"save": file name in Saves/single or a full path, "steps": [{"cmd": ..., "args": {...}, "ignore": [keys]}]}. A step's "ignore" lists result keys left out of the comparison for that step only.
	# "sleep" waits that many seconds before the step, for what the game does on later frames, such as the screen 'contact' opens; "from" fills arguments from earlier results of this run, such as {"screen": "steps[8].result.screen"} for 'reply'.
	# "afterTurn" waits until the game is past that turn and waits for orders, as the client's 'endturn' does, e.g. "steps[21].result.gameTurn" after an 'endturn'. (Claude code Opus 5.5) -->
	sequence = json.loads(Path(path).read_text(encoding="utf-8"))
	if not sequence.get("steps"):
		raise pilot.PilotError("%s has no steps" % path)
	return sequence


def save_path(sequence):
	return pilot.resolve_save(sequence["save"])


def strip(value, ignore):
	if isinstance(value, dict):
		result = dict((key, strip(item, ignore)) for (key, item) in value.items() if key not in VOLATILE_KEYS and key not in ignore)
		# <!-- custom: A held popup's ID is never reused within a process, so replaying on the same client gave 3, then 5, for the same chooser (2026-11-13). Compare only that it is held; unit and city IDs, which a save fixes, are still compared. (Claude code Opus 5.5) -->
		if str(result.get("type", "")).startswith("BUTTONPOPUP_") and isinstance(result.get("id"), int) and result["id"] >= 0:
			result["id"] = "held"
		return result
	if isinstance(value, list):
		return [strip(item, ignore) for item in value]
	return value


def differences(old, new, path, out):
	# <!-- custom: Lists each differing path, such as steps[3].result.units[0].moves, rather than one whole-reply mismatch, so the change can be read at a glance. (Claude code Opus 5.5) -->
	if isinstance(old, dict) and isinstance(new, dict):
		for key in sorted(set(old) | set(new)):
			if key not in new:
				out.append("%s.%s: removed" % (path, key))
			elif key not in old:
				out.append("%s.%s: added = %s" % (path, key, short(new[key])))
			else:
				differences(old[key], new[key], "%s.%s" % (path, key), out)
	elif isinstance(old, list) and isinstance(new, list):
		for i in range(max(len(old), len(new))):
			if i >= len(new):
				out.append("%s[%d]: removed" % (path, i))
			elif i >= len(old):
				out.append("%s[%d]: added = %s" % (path, i, short(new[i])))
			else:
				differences(old[i], new[i], "%s[%d]" % (path, i), out)
	# <!-- custom: Python counts true equal to 1, so a reply turning a flag into a number passed unseen (Codex's review); a bool against a non-bool is a difference. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	elif old != new or isinstance(old, bool) != isinstance(new, bool):
		out.append("%s: %s -> %s" % (path, short(old), short(new)))


def short(value):
	text = json.dumps(value, ensure_ascii=False)
	if len(text) > 120:
		return text[:117] + "..."
	return text


def lookup(results, path):
	# <!-- custom: Reads "steps[8].result.screen" from this run's raw replies; a missing part raises, so a sequence that refers to a failed step stops there. (Claude code Opus 5.5) -->
	match = re.match(r"steps\[(\d+)\]\.(.+)$", path)
	if match is None:
		raise pilot.PilotError("cannot read %r: expected steps[N].key..." % path)
	value = results[int(match.group(1))]
	for part in re.findall(r"[^.\[\]]+|\[\d+\]", match.group(2)):
		value = value[int(part[1:-1])] if part.startswith("[") else value[part]
	return value


def run_steps(pid, sequence, timeout):
	results = []
	raw = []
	for step in sequence["steps"]:
		if step.get("sleep"):
			time.sleep(float(step["sleep"]))
		if step.get("afterTurn"):
			pilot.wait_for_turn(pid, 600.0, after_turn=lookup(raw, step["afterTurn"]))
		command_args = dict(step.get("args") or {})
		for (name, path) in (step.get("from") or {}).items():
			command_args[name] = lookup(raw, path)
		reply = pilot.request(pid, step["cmd"], command_args, timeout)
		raw.append(reply)
		# <!-- custom: A failed command is recorded by its error line, not its traceback, whose line numbers move with every edit of the command file. (Claude code Opus 5.5) -->
		entry = {"cmd": step["cmd"], "args": step.get("args") or {}, "ok": bool(reply.get("ok"))}
		if entry["ok"]:
			entry["result"] = strip(reply.get("result"), step.get("ignore") or ())
		else:
			# <!-- custom: The stale read token in "what read 9 showed" differed on every run although the refusal was the same (trade-table sequence, 2026-11-13), so a "from"-filled 'screen' is shown as <screen> there.
			# Only in the phrase that names it: replacing every equal number would also have hidden "65 gold" when the token was 65 (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			szError = reply.get("error") or ""
			if "screen" in (step.get("from") or {}):
				szError = re.sub(r"\bread %d\b" % int(command_args["screen"]), "read <screen>", szError)
			entry["error"] = szError
		results.append(entry)
	return results


def main():
	parser = argparse.ArgumentParser(description="Replay pilot commands against a save and compare the replies with the accepted baseline. Example: pilot_replay.py pilot_sequences/fogplay_t115_core.json")
	parser.add_argument("sequence", help="the sequence JSON file")
	parser.add_argument("--baseline", help="baseline file (default Logs/SASPilotReplay_<sequence>.json)")
	parser.add_argument("--accept", action="store_true", help="write this run as the new baseline instead of comparing")
	parser.add_argument("--pid", type=int, help="use this running piloted client instead of starting one; it loads the save first")
	parser.add_argument("--keep", action="store_true", help="leave the client the script started running")
	parser.add_argument("--timeout", type=float, default=60.0, help="seconds to wait for each reply")
	args = parser.parse_args()
	sequence = load_sequence(args.sequence)
	save = save_path(sequence)
	baseline = Path(args.baseline) if args.baseline else LOGS_DIR / ("SASPilotReplay_%s.json" % Path(args.sequence).stem)
	started = False
	if args.pid is None:
		# <!-- custom: The same start the CLI uses, so the client gets the per-run INI and the save's mod check. (Claude code Opus 5.5) -->
		options = argparse.Namespace(save=str(save), timeout=600.0, multiple=False, map=None, world_size=None, speed=None, handicap=None, fixed_seeds=False)
		pid = pilot.start(options)["pid"]
		started = True
	else:
		pid = args.pid
		pilot.load_game(pid, save)
	try:
		results = run_steps(pid, sequence, args.timeout)
	finally:
		if started and not args.keep:
			pilot.close(pid)
	run = {"sequence": str(args.sequence), "save": str(save), "steps": results}
	# <!-- custom: A step marked expectError that succeeds fails the run too: it first only excused a failure, so a refusal that stopped working could be accepted into a baseline (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	failed = [i for (i, entry) in enumerate(results) if entry["ok"] == bool(sequence["steps"][i].get("expectError"))]
	for i in failed:
		print("step %d %s: %s" % (i, results[i]["cmd"], results[i].get("error") or "succeeded but expectError is set"), file=sys.stderr)
	# <!-- custom: "expect" states the value a step must give, the expression's for 'py', so a first run can verify a fix rather than only record it: the queued-build sequence's last check could return false and still pass as a successful command (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	for (i, step) in enumerate(sequence["steps"]):
		if "expect" not in step or not results[i]["ok"]:
			continue
		value = results[i].get("result")
		if step["cmd"] == "py" and isinstance(value, dict):
			value = value.get("result")
		mismatch = []
		differences(step["expect"], value, "expected", mismatch)
		if mismatch:
			failed.append(i)
			print("step %d %s: %s" % (i, step["cmd"], "; ".join(mismatch)), file=sys.stderr)
	# <!-- custom: The first run of the free-tech sequence wrote its baseline from three failed steps, as the commands ran on the game being left (2026-11-13); a first run with unexpected failures now writes nothing unless --accept. (Claude code Opus 5.5) -->
	if args.accept or (not baseline.is_file() and not failed):
		baseline.write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding="utf-8")
		print("wrote baseline %s (%d steps)" % (baseline, len(results)))
		return 1 if failed else 0
	if not baseline.is_file():
		print("no baseline written: %d step(s) failed; fix them or pass --accept" % len(failed))
		return 1
	old = json.loads(baseline.read_text(encoding="utf-8"))
	out = []
	differences(old["steps"], results, "steps", out)
	for line in out:
		print(line)
	print("%d step(s), %d difference(s) from %s" % (len(results), len(out), baseline))
	return 1 if (out or failed) else 0


if __name__ == "__main__":
	try:
		sys.exit(main())
	except pilot.PilotError as error:
		print("error: %s" % error, file=sys.stderr)
		sys.exit(2)

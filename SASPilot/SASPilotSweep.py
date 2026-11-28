#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Run SASPilot's read commands over every unit and city of a game and list the ones that fail, as a regression check after a DLL or command change.
# On 2026-11-20 'unit' raised "unidentifiable C++ exception" for units in cities on a turn-402 save: it asks the game about every mission with no target, which a player's clicks never do, and an inherited airlift check read past the map (KI#1091.3).
# The check that found it, and confirmed the fix on all 108 units, was a shell loop typed by hand twice; the user asked for it to become a script. (Claude code Opus 5.5) -->

import argparse
import sys

# <!-- custom: SASPilotClient, as saspilot, for the requests, logged as any SASPilotClient.py command is. (Claude code Opus 5.5) -->
import SASPilotClient as saspilot
from SASPilotClient import PilotError, pick_pid

# <!-- custom: Each sweep: the command listing the things, the key holding them in its reply, and the command run on each with its argument. (Claude code Opus 5.5) -->
SWEEPS = {"unit": ("units", "units", "unit"), "city": ("cities", "cities", "city")}


def listed(pid, command, key, player):
	# <!-- custom: An unexpected reply stops the sweep rather than counting as zero things checked (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	result = saspilot.call(pid, command, {"player": player})
	if isinstance(result, dict):
		result = result.get(key)
	if not isinstance(result, list) or [item for item in result if not isinstance(item, dict) or "id" not in item]:
		raise PilotError(("'%s' did not return a list of things with IDs: %r" % (command, result))[:300])
	return [item["id"] for item in result]


def main():
	parser = argparse.ArgumentParser(description="Run SASPilot's unit and city commands over every unit and city of a running game and list the failures, such as a C++ exception. Example: python SASPilot/SASPilotSweep.py; --commands unit; --player 3 under the all role.")
	parser.add_argument("--pid", type=int, help="the Civ4 client; default the only one")
	parser.add_argument("--commands", default="unit,city", help="comma-separated, from: %s" % ", ".join(sorted(SWEEPS)))
	parser.add_argument("--player", type=int, help="another player's units and cities, under the all role; default ours")
	args = parser.parse_args()
	pid = pick_pid(args.pid)
	names = [part.strip() for part in args.commands.split(",") if part.strip()]
	if not names:
		sys.exit("--commands names no sweep; choose from %s" % ", ".join(sorted(SWEEPS)))
	for name in names:
		if name not in SWEEPS:
			sys.exit("no sweep for %s; choose from %s" % (name, ", ".join(sorted(SWEEPS))))
	# <!-- custom: The player is fixed at the start, so every request asks about the same one, and the fog mode and role are printed: with fog on, another player's units and cities are listed and read only as far as our team sees them, which a clean sweep would hide (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	player = args.player
	if player is None:
		player = saspilot.call(pid, "ping").get("activePlayer")
	fog = saspilot.call(pid, "fog").get("fog")
	role = saspilot.call(pid, "role").get("role")
	print("player %s, fog %s, role %s" % (player, "on" if fog else "off", role))
	failures = []
	for name in names:
		(listCommand, key, argument) = SWEEPS[name]
		ids = listed(pid, listCommand, key, player)
		failed = 0
		for item in ids:
			request = {argument: item, "player": player}
			reply = saspilot.request(pid, name, request)
			if not reply.get("ok"):
				failed += 1
				failures.append("%s %s=%s: %s" % (name, argument, item, str(reply.get("error")).splitlines()[0]))
		print("%s: %d checked, %d failed" % (name, len(ids), failed))
	for line in failures:
		print("  " + line)
	return 1 if failures else 0


if __name__ == "__main__":
	try:
		sys.exit(main())
	except PilotError as error:
		sys.exit(str(error))

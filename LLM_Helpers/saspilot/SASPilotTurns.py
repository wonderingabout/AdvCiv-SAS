# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: End turns until something needs the agent, handling only routine steps, as the islands replay (2026-11-15) kept rewriting the same shell loop: end the turn, read 'todo', steer idle exploring boats, print the reminders worth reading.
# A loop that stopped only on idle cities, units, popups and research ended the turn six times against Pericles' first-contact screen, so it stops on 'todo's blocking flag, which counts the diplomacy screen.
# Order within a turn, the user's rule (2026-11-15): move the scouts before trading, as a rival met this turn changes what a tech is worth (one more buyer, or a monopoly lost); trade after the moves unless an AI asks first.
# Routine steps only: an idle boat (one with no orders that is not working a plot) takes 'seareach's recommended unknown coast, as the user asked that scouting hunt unexplored coast first; a first-contact greeting is answered with peace only with --peace-on-contact.
# Every other stop is left to the agent, with the reason printed. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads options, sys reports errors; SASPilotClient sends the requests, logged as its own are. (Claude code Opus 5.5) -->
import argparse
import sys

from SASPilotClient import PilotError, pick_pid, request

PID = None
DEFAULT_CHECKS = "cities,rivalMoods,sharedBonuses,staleMarks,waterScouting,unimproved,idleImprovements"


def pilot(command, **args):
	reply = request(PID, command, args)
	if not reply["ok"]:
		raise PilotError("%s: %s" % (command, reply["error"]))
	return reply["result"]


# <!-- custom: reject_stale_offer, scout_step_by_step and answer_contact went missing when steer_boats was removed: the cut ran from steer_boats to refuse_recommendations, so main() called three undefined names until Ruff's F821 caught it. (Claude code Opus 5.5) -->
def reject_stale_offer(todo):
	# <!-- custom: An AI offer in which everything we would get is something we already have: at turns 74 and 76 of the islands replay (2026-11-15) Pericles and Suleiman offered the very techs we had just bought from them with 'propose' that turn.
	# Such an offer gives nothing, so it is rejected; any other offer is left to the agent.
	# Returns whether it rejected. (Claude code Opus 5.5) -->
	diplomacy = todo.get("diplomacy")
	if not diplomacy or diplomacy.get("aiComment") != "AI_DIPLOCOMMENT_OFFER_DEAL":
		return False
	screen = pilot("diplo")
	theirs = screen.get("theyOffer") or []
	if not theirs or [item for item in theirs if item["item"] != "TRADE_TECHNOLOGIES"]:
		return False
	ours = pilot("py", code="[t for t in %r if gc.getTeam(gc.getPlayer(gc.getGame().getActivePlayer()).getTeam()).isHasTech(gc.getInfoTypeForString(t))]" % [item["what"] for item in theirs])["result"]
	if len(ours) != len(theirs):
		return False
	for reply in screen["replies"]:
		if reply["comment"] == "USER_DIPLOCOMMENT_REJECT_OFFER":
			after = pilot("reply", n=reply["n"], screen=screen["screen"])
			print("  rejected %s's offer of %s, which we already have" % (diplomacy["whoName"], ", ".join(ours)))
			for closing in after.get("replies", []):
				if closing["comment"] == "USER_DIPLOCOMMENT_EXIT":
					pilot("reply", n=closing["n"], screen=after["screen"])
			return True
	return False


def scout_step_by_step(explorers):
	# <!-- custom: One plot at a time, the user's rule (2026-11-15): as on land, each step reveals coast that may change the way, so a target set once (the first version moved each idle explorer to 'seareach's recommendation and let it sail) went round Suleiman's island by the north, into the ice, before the next look.
	# Each explorer, every turn: ask 'seareach', take one 'step' toward its recommendation, ask again, until its moves are spent. (Claude code Opus 5.5) -->
	for iUnit in explorers:
		for i in range(6):
			unit = pilot("unit", unit=iUnit)
			# <!-- custom: Not while a move is still under way: the second step of a turn was refused ("cannot start MISSION_MOVE_TO now ... whose current mission is MISSION_MOVE_TO") and ended the run. (Claude code Opus 5.5) -->
			if unit["movesLeft"] <= 0 or unit.get("missions"):
				break
			reach = pilot("seareach", unit=iUnit)
			recommend = reach.get("recommend")
			if not recommend:
				print("  boat %d: no reachable unknown coast; left for the agent" % iUnit)
				break
			try:
				step = pilot("step", unit=iUnit, x=recommend["x"], y=recommend["y"])
			except PilotError as error:
				print("  boat %d: step refused (%s); left for the next turn" % (iUnit, error))
				break
			print("  boat %d -> %d,%d, toward %d,%d (%s), %d newly revealed%s" % (iUnit, step["x"], step["y"], recommend["x"], recommend["y"], recommend["direction"], step["newlyRevealed"], step["foreignNear"] and ", foreign units near" or ""))


def answer_contact(todo):
	# <!-- custom: A first-contact greeting answered with peace, the choice the replay made both times; any other diplomacy screen is left to the agent.
	# Returns whether it answered. (Claude code Opus 5.5) -->
	diplomacy = todo.get("diplomacy")
	if not diplomacy or diplomacy.get("aiComment") != "AI_DIPLOCOMMENT_FIRST_CONTACT":
		return False
	screen = pilot("diplo")
	for reply in screen["replies"]:
		if reply["comment"] == "USER_DIPLOCOMMENT_PEACE":
			after = pilot("reply", n=reply["n"], screen=screen["screen"])
			print("  first contact with %s: peace" % diplomacy["whoName"])
			for closing in after.get("replies", []):
				if closing["comment"] == "USER_DIPLOCOMMENT_EXIT":
					pilot("reply", n=closing["n"], screen=after["screen"])
			return True
	return False


def refuse_recommendations(todo):
	# <!-- custom: The advisor's production recommendation (BUTTONPOPUP_PYTHON with ACCEPT_RECOMMENDATION and REFUSE_RECOMMENDATION) would replace the city's queue; the replay refused it at turn 71 both runs, a Library for Amsterdam.
	# Refused only with --refuse-recommendations; returns whether every held popup was one. (Claude code Opus 5.5) -->
	bAll = True
	for popup in todo.get("heldPopups") or []:
		if "REFUSE_RECOMMENDATION" in popup["buttons"]:
			pilot("answer", id=popup["id"], button="REFUSE_RECOMMENDATION")
			print("  refused the advisor's %s for %s" % (popup.get("about", {}).get("build"), popup.get("about", {}).get("city")))
		else:
			bAll = False
	return bAll


def report(checks, seen):
	# <!-- custom: Only what is new since the previous turn: the first run printed every unimproved resource and the turn's messages again each turn, burying the one new line.
	# seen holds what was printed. (Claude code Opus 5.5) -->
	for entry in pilot("reminders")["reminders"]:
		if entry["check"] in checks:
			szLine = "[%s] %s" % (entry["check"], entry["text"][:220])
			if szLine not in seen:
				seen.add(szLine)
				print("  " + szLine)
	for message in pilot("messages"):
		szLine = "(turn %d) %s" % (message["turn"], message["text"][:160])
		if szLine not in seen:
			seen.add(szLine)
			print("  " + szLine)


def main():
	# <!-- custom: The examples live in --help rather than the header comment, where the comment reflow joined the two command lines into one sentence. (Claude code Opus 5.5) -->
	parser = argparse.ArgumentParser(description="End turns until something needs the agent, handling only routine steps.", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="examples:\n  python LLM_Helpers/saspilot/SASPilotTurns.py --turns 10 --peace-on-contact --explorers 49155,73733\n  python LLM_Helpers/saspilot/SASPilotTurns.py --turns 5 --checks cities,rivalMoods,sharedBonuses")
	parser.add_argument("--turns", type=int, default=5, help="turns to end at most")
	parser.add_argument("--peace-on-contact", action="store_true", help="answer a first-contact greeting with peace")
	parser.add_argument("--refuse-recommendations", action="store_true", help="refuse the advisor's production recommendation popups, which would replace a city's queue")
	parser.add_argument("--explorers", default="", help="IDs of the ships that explore, comma-separated; only these are sent to 'seareach's recommended unknown coast when idle")
	parser.add_argument("--checks", default=DEFAULT_CHECKS, help="reminder checks to print after each turn, comma-separated")
	parser.add_argument("--pid", type=int, help="Civ4 client PID")
	args = parser.parse_args()
	global PID
	checks = args.checks.split(",")
	seen = set()
	explorers = [int(x) for x in args.explorers.split(",") if x.strip()]
	try:
		PID = pick_pid(args.pid)
		for i in range(args.turns):
			todo = pilot("todo")
			if todo["blocking"]:
				if args.peace_on_contact and answer_contact(todo):
					todo = pilot("todo")
				if reject_stale_offer(todo):
					todo = pilot("todo")
				if args.refuse_recommendations and todo.get("heldPopups") and refuse_recommendations(todo):
					todo = pilot("todo")
				if todo["blocking"] and todo["idleUnits"] and not todo["idleCities"] and not todo["needsResearch"] and not todo.get("heldPopups") and not todo.get("diplomacy"):
					# <!-- custom: Idle explorers scout step by step too: the idle case first sent the whole path to 'seareach's recommendation at once. (Claude code Opus 5.5) -->
					if not [unit for unit in todo["idleUnits"] if unit["id"] not in explorers]:
						scout_step_by_step(explorers)
						todo = pilot("todo")
			if todo["blocking"]:
				reasons = [name for name in ("idleCities", "idleUnits", "needsResearch", "heldPopups", "diplomacy", "freeTechOwed") if todo.get(name)]
				print("turn %d (%d): stopped for %s" % (todo["turn"], todo["year"], ", ".join(reasons)))
				return 0
			if explorers:
				scout_step_by_step(explorers)
				todo = pilot("todo")
				if todo["blocking"]:
					continue
			iBefore = todo["turn"]
			# <!-- custom: The turn number from endturn's own reply: a 'todo' read right after it once still showed the old turn, and the next end of turn then ended two at once (77 to 79). (Claude code Opus 5.5) -->
			ended = pilot("endturn")
			todo = pilot("todo")
			todo["turn"] = ended.get("gameTurn", todo["turn"])
			# <!-- custom: The turn is reported only when it advanced: a diplomacy screen opening during the end of turn left it at 69, and the first run printed turn 69 twice before stopping. (Claude code Opus 5.5) -->
			if todo["turn"] != iBefore:
				print("turn %d (%d)" % (todo["turn"], todo["year"]))
			report(checks, seen)
	except (OSError, PilotError) as error:
		print("SASPilotTurns: %s" % error, file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

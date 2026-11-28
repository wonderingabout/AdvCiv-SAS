#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Walk one city's controls through the UI as a player does, checking each step against the commands that give the same facts: open the city screen, list its build buttons, press one, read the queue back, close the screen.
# Written on 2026-11-28 as the first audit that acts, after the tab audit: the tab audit showed every screen opens and reads, but not that an agent can go from "this city needs a Worker" to a queued Worker by the UI alone.
# A lasting check to run again after a UI or command change, as SASPilotTabAudit.py is, whose name it follows; first named SASPilotCityRoute.py, renamed the same day as "route" means a road or a trade route in Civ4 (the user's remark).
# A plain press first looked like it replaced the queue (Aachen, Worker to Settler), then put the new item first and kept the queue (Vienna, before its Stealth Bomber): K-Mod's CvGame::cityPushOrder replaces the current order only while no production is invested in it, and otherwise inserts the new one first so the hammers are kept.
# So the audit reports the production before the press beside both queues, and takes the pressed order out again unless --keep. (Claude code Opus 5.5) -->

# <!-- custom: argparse and sys for the command line, json for --out, re strips tags from the queue table's text. (Claude code Opus 5.5) -->
import argparse
import json
import re
import sys

# <!-- custom: SASPilotClient, as saspilot, for the requests, logged as any SASPilotClient.py command is. (Claude code Opus 5.5) -->
import SASPilotClient as saspilot
from SASPilotClient import PilotError, pick_pid

# <!-- custom: The city screen's build buttons, one multi-list of the main interface; 'uiitems' marks each with the order it gives, which replaced this file's own list of the four order widgets (2026-11-28). See KI#1110.2. (Claude code Opus 5.5) -->
BUILD_LIST = "BottomButtonList"
# <!-- custom: The city screen's production queue, drawn by CvMainInterface as a table, one row per order with its turns. (Claude code Opus 5.5) -->
QUEUE_TABLE = "SelectedCityText"


def plain(text):
	# <!-- custom: Strips font tags, as SASPilotTabAudit.py's plain does. (Claude code Opus 5.5) -->
	return re.sub(r"<[^>]*>", "", str(text)).strip()


class CityScreenAudit:
	def __init__(self, pid):
		self.pid = pid
		self.steps = []

	def call(self, command, **arguments):
		reply = saspilot.request(self.pid, command, arguments)
		if not reply.get("ok"):
			raise PilotError("%s %s: %s" % (command, arguments, str(reply.get("error")).splitlines()[0]))
		return reply.get("result")

	def step(self, name, problem, **facts):
		entry = {"step": name, "ok": problem is None}
		if problem is not None:
			entry["problem"] = problem
		entry.update(facts)
		self.steps.append(entry)
		return entry

	def pick_city(self, szCity):
		cities = self.call("cities")
		if not cities:
			raise PilotError("the active player has no city")
		if szCity is None:
			return cities[0]
		for city in cities:
			if str(city["id"]) == szCity or city["name"] == szCity:
				return city
		raise PilotError("no city %s; ours: %s" % (szCity, ", ".join([city["name"] for city in cities])))

	def run(self, szCity, szItem, bKeep):
		state = self.call("uistate")
		if state["openScreens"] or state["cityScreen"] or state["bugOptions"] or state.get("diplomacy"):
			raise PilotError("start the city screen audit from the map with no screen open")
		city = self.pick_city(szCity)
		before = self.call("city", city=city["id"])
		pressedItem = None
		# <!-- custom: A lost reply to the opening uiselect may still have opened the screen, so it is closed then too (Codex's fourth review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		try:
			opened = self.call("uiselect", city=city["id"])
		except Exception as error:
			self.step("open", "uiselect failed: %s" % error, city=city["name"])
			self.close_screen()
			return {"city": city["name"], "steps": self.steps, "ok": False}
		entry = self.step("open", None if opened.get("cityScreen") and opened.get("selected") == city["name"] else "uiselect did not open %s's screen" % city["name"], city=city["name"], selected=opened.get("selected"))
		# <!-- custom: Stop before pressing on the wrong city's screen, closing whatever opened; the first version noted the problem and went on to the press (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if not entry["ok"]:
			self.close_screen()
			return {"city": city["name"], "steps": self.steps, "ok": False}
		# <!-- custom: The screen it opened is closed on every path: the first run that refused an unavailable item (BUILDING_PYRAMID in Mainz, 2026-11-28) left the city screen open. (Claude code Opus 5.5) -->
		try:
			self.call("uimain")
			buttons = [item for item in self.call("uiitems", widget=BUILD_LIST, screen="MAIN_INTERFACE").get("items", []) if item.get("order") is not None]
			# <!-- custom: A button the screen greys out is a choice the city has not got, so only enabled ones are compared with the 'city' command's options. (Claude code Opus 5.5) -->
			shown = set([item["about"] for item in buttons if not item.get("disabled")])
			options = before["options"]
			offered = set(list(options.get("units", {}).keys()) + list(options.get("buildings", {}).keys()) + list(options.get("projects", {}).keys()) + list(options.get("processes", [])))
			problem = None
			if shown != offered:
				problem = "the city screen's build buttons and the 'city' options differ"
			self.step("buttons", problem, enabled=len(shown), disabled=len(buttons) - len(shown), onlyOnScreen=sorted(shown - offered), onlyInOptions=sorted(offered - shown))
			if szItem is None:
				# <!-- custom: Default: the first enabled button not already first in the queue, so the press changes something the read-back can see. (Claude code Opus 5.5) -->
				current = before["queue"][:1]
				candidates = [item["about"] for item in buttons if not item.get("disabled") and [item["about"]] != current]
				if not candidates:
					raise PilotError("%s offers nothing to press" % city["name"])
				szItem = candidates[0]
			if szItem not in shown:
				raise PilotError("%s is not an enabled build button of %s" % (szItem, city["name"]))
			# <!-- custom: A press whose reply is lost may still have happened, so the queue is read and reconciled either way (Codex's second review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			pressError = None
			pressedItem = szItem
			try:
				self.call("uipress", widget=BUILD_LIST, about=szItem, screen="MAIN_INTERFACE")
			except PilotError as error:
				pressError = str(error)
			# <!-- custom: Read again once if the first read fails: the press has happened, so giving up here would leave the changed queue in place without the restore (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			try:
				after = self.call("city", city=city["id"])
			except PilotError:
				after = self.call("city", city=city["id"])
			problem = None
			if pressError is not None:
				problem = "uipress failed: %s" % pressError
			elif after["queue"][:1] != [szItem]:
				problem = "the queue starts with %s, not %s" % (after["queue"][:1], szItem)
			self.step("press", problem, item=szItem, productionBefore=before["production"], queueBefore=before["queue"], queueAfter=after["queue"], turnsLeft=after["productionTurnsLeft"])
			# <!-- custom: The queue as the screen shows it, SelectedCityText's rows such as "Aqueduct (3)", one per order, each checked against the name of the 'city' queue's order at its place.
			# The table was first taken for an EXE-drawn list that SASPilot could not read (2026-11-28), until CvMainInterface's WIDGET_HELP_SELECTED rows pointed to it; comparing only the number of rows passed stale rows of the same length (Codex's second review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			self.call("uimain")
			rows = [plain(row[0]) + " " + plain(row[1]) for row in (self.call("uiread", widget=QUEUE_TABLE, screen="MAIN_INTERFACE").get("rows") or [])]
			names = [self.order_name(szOrder) for szOrder in after["queue"]]
			problem = None
			if len(rows) != len(names):
				problem = "the screen lists %d orders, 'city' %d" % (len(rows), len(names))
			else:
				mismatched = [row for (row, szName) in zip(rows, names) if szName is not None and row.find(szName) < 0]
				if mismatched:
					problem = "screen rows not in the 'city' queue's order: %s" % mismatched
			self.step("queue", problem, shown=rows, unchecked=[row for (row, szName) in zip(rows, names) if szName is None])
		finally:
			# <!-- custom: The undo runs in the cleanup, on a fresh read of the queue, so a failed read of the screen or a 'pedia' name after the press still undoes it (Codex's third review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			# <!-- custom: A failed undo is its own step and the close still runs: in one cleanup, a failed queue read, dequeue or produce skipped the close and hid the first failure (Codex's fourth review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			try:
				if pressedItem is not None and not bKeep:
					try:
						self.restore(city, before["queue"], self.call("city", city=city["id"])["queue"], pressedItem)
					except Exception as error:
						self.step("restore", "the undo failed: %s; check the queue in the window" % error)
			finally:
				self.close_screen()
		return {"city": city["name"], "steps": self.steps, "ok": all([entry["ok"] for entry in self.steps])}

	def close_screen(self):
		try:
			closed = self.call("uiselect", close=1)
		except Exception as error:
			self.step("close", "uiselect close=1 failed: %s; close the city screen in the window" % error)
			return
		self.step("close", None if not closed.get("cityScreen") else "the city screen is still open", cityScreen=closed.get("cityScreen"))

	def order_name(self, szOrder):
		# <!-- custom: An order's name as the queue table writes it, from 'pedia' for units, buildings and projects; a process has no Sevopedia kind, and 'py' is refused in the play role the audit runs in, so None, and its row is listed as unchecked. (Claude code Opus 5.5) -->
		if szOrder.startswith("PROCESS_"):
			return None
		return self.call("pedia", type=szOrder)["name"]

	def restore(self, city, queue, pressed, szItem):
		# <!-- custom: The pressed order is taken out with 'dequeue index=0', which leaves the other orders as they were, repeat flags included, and empties a queue that was empty.
		# The first version rebuilt the queue from type names with 'produce', which loses such flags while reporting success, and could not empty a queue (Codex's review, 2026-11-28).
		# Only a change the audit can name is undone, an insert before the old queue or a replacement of its head: the second version dequeued whatever was first, so an unchanged queue lost its own head (Codex's second review).
		# A replaced head, which had no production in it, is put back by type, as no command restores its flags; the step says so. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		# <!-- custom: An unchanged queue is left alone first: pressing the item already first, with nothing invested, leaves the queue as it was, which also matches the replacement test, and undoing it lost that head's repeat flag (Codex's third review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if pressed == queue:
			self.step("restore", None, queue=pressed, note="the queue was unchanged, so nothing was undone")
			return
		inserted = pressed[:1] == [szItem] and pressed[1:] == queue
		replaced = not inserted and pressed[:1] == [szItem] and len(queue) > 0 and pressed[1:] == queue[1:]
		if not inserted and not replaced:
			self.step("restore", "the queue changed in a way the audit did not make, so it was left as is", queue=pressed)
			return
		self.call("dequeue", city=city["id"], index=0)
		note = None
		if replaced:
			self.call("produce", city=city["id"], item=queue[0], first=1)
			note = "the press replaced %s, put back by type" % queue[0]
		now = self.call("city", city=city["id"])["queue"]
		self.step("restore", None if now == queue else "the queue is %s, not %s" % (now, queue), queue=now, note=note)

def summary(report):
	lines = ["%s: %s" % (report["city"], "OK" if report["ok"] else "PROBLEMS")]
	for entry in report["steps"]:
		facts = ", ".join(["%s=%s" % (key, entry[key]) for key in entry if key not in ("step", "ok", "problem")])
		lines.append("  %-8s %s%s" % (entry["step"], "ok" if entry["ok"] else "PROBLEM " + entry["problem"], facts and "  (%s)" % facts or ""))
	return "\n".join(lines)


def main():
	parser = argparse.ArgumentParser(description="Walk one city's controls through the UI, as a player does: open its screen, list its build buttons against the 'city' command's options, press one, read the queue back, take it out again and close the screen. Start from the map with no screen open.")
	parser.add_argument("--pid", type=int, help="the Civ4 client; default the only one")
	parser.add_argument("--city", help="city name or ID; default the first of 'cities'")
	parser.add_argument("--item", help="the build button to press, by XML type such as UNIT_WORKER; default the first enabled one not already first in the queue")
	parser.add_argument("--keep", action="store_true", help="leave the pressed item queued instead of taking it out again")
	parser.add_argument("--out", help="also write the report as JSON to this file")
	args = parser.parse_args()
	pid = pick_pid(args.pid)
	try:
		report = CityScreenAudit(pid).run(args.city, args.item, args.keep)
	except PilotError as error:
		parser.exit(1, "%s\n" % error)
	print(summary(report))
	if args.out:
		with open(args.out, "w", encoding="utf-8") as handle:
			json.dump(report, handle, ensure_ascii=False, indent=1)
	return 0 if report["ok"] else 1


if __name__ == "__main__":
	sys.exit(main())

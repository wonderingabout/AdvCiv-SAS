#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Open every advisor tab by its key in CvScreenEnums.ADVISOR_TABS and list what it shows (tables, list boxes and text widgets) beside the command that gives the same facts without the screen.
# Written for the 2026-11-22 audit of advisor coverage, which first ran as a scratchpad script; kept so a later UI or command change can be audited again (the user's request).
# It answers two questions at once: where reading the UI falls short (a table read back with 0 rows while the screen shows content), and which tabs have no command yet. See KI#1110. (Claude code Opus 5.5) -->

# <!-- custom: argparse and sys for the command line, json for --out, re strips tags from widget text. (Claude code Opus 5.5) -->
import argparse
import json
import re
import sys

# <!-- custom: SASPilotClient, as saspilot, for the requests, logged as any SASPilotClient.py command is. (Claude code Opus 5.5) -->
import SASPilotClient as saspilot
from SASPilotClient import PilotError, pick_pid


def plain(text):
	return re.sub(r"<[^>]*>", "", str(text)).strip()


class Audit:
	def __init__(self, pid):
		self.pid = pid

	def call(self, command, **arguments):
		reply = saspilot.request(self.pid, command, arguments)
		if not reply.get("ok"):
			raise PilotError("%s %s: %s" % (command, arguments, str(reply.get("error")).splitlines()[0]))
		return reply.get("result")

	def tab(self, advisor, row):
		self.call("uiopen", name=advisor, tab=row["key"])
		tables = []
		lists = []
		texts = []
		for widget in self.call("uiwidgets").get("widgets", []):
			if widget.get("hidden"):
				continue
			method = widget.get("method", "")
			if "Table" in method:
				read = self.call("uiread", widget=widget["name"])
				rows = read.get("rows") or []
				tables.append({"widget": widget["name"], "rows": len(rows), "columns": read.get("columns"), "sample": [plain(cell) for cell in (rows[0] if rows else [])]})
			elif "ListBox" in method:
				# <!-- custom: List boxes report their entries through uiitems.
				# The first restored audit treated them as tables and reported every trade list as empty. (GPT-6.2-Sol) -->
				items = self.call("uiitems", widget=widget["name"]).get("items") or []
				sample = plain(items[0].get("text") or items[0].get("about") or "") if items else ""
				lists.append({"widget": widget["name"], "items": len(items), "sample": sample})
			elif widget.get("text"):
				texts.append(plain(widget["text"]))
		return {"tables": tables, "lists": lists, "texts": [text for text in texts if text]}

	def run(self, advisors):
		# <!-- custom: Cleanup closes the advisor the audit opened.
		# Require a clear map so that it cannot also close a screen the player left open. (GPT-6.2-Sol) -->
		state = self.call("uistate")
		if state["openScreens"] or state["cityScreen"] or state["bugOptions"] or state.get("diplomacy"):
			raise PilotError("start the tab audit from the map with no screen open")
		listing = self.call("uitabs", all=1)["advisors"]
		report = []
		for advisor in listing:
			if advisors and advisor["advisor"] not in advisors:
				continue
			for row in advisor["tabs"]:
				entry = {"advisor": advisor["advisor"], "tab": row["key"], "label": row["label"], "command": row["command"], "note": row.get("note")}
				if row.get("option"):
					entry["option"] = row["option"]
				# <!-- custom: List hidden tabs without opening them, including SAS tabs replaced by a BUG advisor. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
				if not row.get("shown", True):
					entry["skipped"] = "hidden without %s" % row["option"] if row.get("option") else "hidden by BUG advisor option"
					report.append(entry)
					continue
				try:
					entry.update(self.tab(advisor["advisor"], row))
				except PilotError as error:
					entry["error"] = str(error)
				finally:
					self.call("closescreens")
				report.append(entry)
		return report


def summary(report):
	lines = []
	for entry in report:
		if entry.get("error"):
			state = "ERROR " + entry["error"]
		elif entry.get("skipped"):
			state = "skipped: " + entry["skipped"]
		else:
			empty = [table["widget"] for table in entry["tables"] if table["rows"] == 0]
			empty.extend(item["widget"] for item in entry["lists"] if item["items"] == 0)
			state = "tables %d, lists %d, texts %d%s" % (len(entry["tables"]), len(entry["lists"]), len(entry["texts"]), " (empty: %s)" % ", ".join(empty) if empty else "")
		command = entry["command"] or "NO COMMAND%s" % (entry.get("note") and " (%s)" % entry["note"] or "")
		lines.append("%-17s %-15s %-14s %s" % (entry["advisor"], entry["tab"], command, state))
	return "\n".join(lines)


def main():
	parser = argparse.ArgumentParser(description="Open every advisor tab of CvScreenEnums.ADVISOR_TABS by key, list its tables, list boxes and texts beside the command that gives its facts, and show where the UI or the commands fall short. Start from the map with no screen open.")
	parser.add_argument("--pid", type=int, help="the Civ4 client; default the only one")
	parser.add_argument("--advisors", default="", help="comma-separated advisor short names; default all")
	parser.add_argument("--out", help="also write the full report as JSON to this file")
	args = parser.parse_args()
	pid = pick_pid(args.pid)
	advisors = [name for name in args.advisors.split(",") if name]
	try:
		report = Audit(pid).run(advisors)
	except PilotError as error:
		parser.exit(1, "%s\n" % error)
	print(summary(report))
	if args.out:
		with open(args.out, "w", encoding="utf-8") as handle:
			json.dump(report, handle, ensure_ascii=False, indent=1)
	return 1 if any(entry.get("error") for entry in report) else 0


if __name__ == "__main__":
	sys.exit(main())

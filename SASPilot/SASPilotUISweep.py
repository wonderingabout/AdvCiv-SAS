#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Open every advisor through SASPilotUI, visit each of its footer tabs and list what went wrong, as a read-only regression check of the screens after a Python or DLL change.
# Listed with Codex (GPT-6.2-Sol) on 2026-11-20 as the next step after SASPilotSweep.py: Python errors, a tab that does not become active, widgets left over from another tab, an Exit that fails or a screen that differs after a close and reopen, and typed widgets with no hover text.
# Only navigation is pressed, including Sevopedia table cells with recorded page links.
# Drop-downs and game-changing buttons are out of scope, and an unexpected popup or the diplomacy screen stops the sweep. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: argparse and sys for the command line, re strips tags from a widget's text, time for the run's length, Counter counts the widgets two visits show, and Path finds SASMagicNumbers.py. (Claude code Opus 5.5) -->
import argparse
import re
import sys
import time
from collections import Counter
from pathlib import Path

# <!-- custom: SASPilotClient, as saspilot, for the requests, logged as any SASPilotClient.py command is. (Claude code Opus 5.5) -->
import SASPilotClient as saspilot
from SASPilotClient import PilotError, pick_pid
# <!-- custom: desktop_windows is no longer imported: --dismiss, its only use here, was removed on 2026-11-27. (Claude code Opus 5.5) -->

# <!-- custom: The screens a player opens from the window, by 'uiopen''s short names; the Sevopedia browses by category rather than footer tabs, so it is left to a sweep of its own. (Claude code Opus 5.5) -->
SCREENS = ("tech", "policy", "religion", "corporation", "foreigntrade", "foreigndiplomacy", "domestic", "military", "espionage", "info", "world", "victory", "halloffame", "pedia")
# <!-- custom: Each screen 'uiopen' must open, so a screen that opens another fails; Religion, Corporation and Espionage open the advisor SAS merged them into (Claude code Opus 5.5 + GPT-6.2-Sol).
# Until 2026-11-22 this also held the fewest footer tabs each showed, counted by hand on the turn-402 save, as the tabs come from the recorder under test and cannot vouch for themselves (Codex's review); the drawn tabs are now compared with CvScreenEnums.ADVISOR_TABS, read through 'uitabs all=1', an independent source the screens draw from. See KI#1110. (Claude code Opus 5.5) -->
EXPECTED = {"tech": "TECH_CHOOSER", "policy": "POLICY_ADVISOR_SCREEN", "religion": "POLICY_ADVISOR_SCREEN", "corporation": "POLICY_ADVISOR_SCREEN", "foreigntrade": "FOREIGN_ADVISOR", "foreigndiplomacy": "FOREIGN_DIPLOMACY_ADVISOR", "domestic": "DOMESTIC_ADVISOR", "military": "MILITARY_ADVISOR", "espionage": "FOREIGN_DIPLOMACY_ADVISOR", "info": "INFO_SCREEN", "world": "WORLD_ADVISOR", "victory": "VICTORY_SCREEN", "halloffame": "HALL_OF_FAME", "pedia": "PEDIA_MAIN"}
# <!-- custom: The registry advisor whose tabs each shortcut into a merged advisor shows. (Claude code Opus 5.5) -->
TAB_ADVISOR = {"religion": "policy", "corporation": "policy", "espionage": "foreigndiplomacy"}
# <!-- custom: The tab a shortcut into a merged advisor must open on, by its place among the tabs, the same in every language: Religion and Corporation open the Policy Advisor's second and third, Espionage the Foreign Diplomacy Advisor's fourth (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
EXPECTED_TAB = {"religion": 1, "corporation": 2, "espionage": 3}
# <!-- custom: Sevopedia categories whose entries play something when pressed, so only the category is opened; named by their screen, not their English label (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
PEDIA_NO_ITEMS = ("PEDIA_MOVIES", "PEDIA_MUSIC")
def magicNumber(szName):
	# <!-- custom: A number from SASMagicNumbers.py, read as text: importing it here would write a __pycache__ folder under Assets/Python, and any file written there while Civ4 runs risks the game (see AGENTS.md's runtime safety). (Claude code Opus 5.5) -->
	text = (Path(__file__).resolve().parents[1] / "Assets" / "Python" / "SASMagicNumbers.py").read_text(encoding="utf-8")
	match = re.search(r"^%s\s*=\s*(\d+)" % szName, text, re.MULTILINE)
	if match is None:
		raise SystemExit("%s not found in SASMagicNumbers.py" % szName)
	return int(match.group(1))


# <!-- custom: The Sevopedia's EXPAND buttons, WIDGET_PYTHON with these as data1: the history panel's and the content panel's. (Claude code Opus 5.5) -->
EXPAND_DATA1 = (magicNumber("SAS_MAGIC_PEDIA_PYTHON_HISTORY_EXPAND"), magicNumber("SAS_MAGIC_PEDIA_PYTHON_CONTENT_EXPAND"))


# <!-- custom: Widgets whose hover is empty by design: WIDGET_GENERAL has none of its own, and the Exit's is the EXE's; the Foreign Advisor's tab links (WIDGET_FOREIGN_ADVISOR) have none, and AdvCiv switched off the unit count's as noninformative (advc.086, CvDLLWidgetData::parseFinanceNumUnits), both empty in the first run (2026-11-20).
# Domestic and foreign trade are empty only without trade routes, so they stay notes. (Claude code Opus 5.5) -->
NO_HOVER = ("WIDGET_GENERAL", "WIDGET_CLOSE_SCREEN", "WIDGET_FOREIGN_ADVISOR", "WIDGET_HELP_FINANCE_NUM_UNITS")


class Stop(Exception):
	pass


def plain(text):
	# <!-- custom: A widget's text without its font and color tags, such as <font=4>EXIT</font>. (Claude code Opus 5.5) -->
	return re.sub(r"<[^>]*>", "", text or "").strip().upper()


# <!-- custom: Identify links before pressing so subheadings and spacers do not consume the per-category page limit. (GPT-6.2-Sol) -->
def pediaEntries(table):
	rows = table["rows"]
	return [(cell, rows[cell["row"]][0].strip()) for cell in table["cells"] if cell["column"] == 0 and (cell["widgetType"] or "").startswith("WIDGET_PEDIA_JUMP_")]


def pediaLinkKey(cell):
	return (cell["widgetType"], cell["data1"], cell["data2"])


class Sweep(object):
	# <!-- custom: Was (pid, hover, dismiss=False); dismiss went with --dismiss on 2026-11-27. (Claude code Opus 5.5) -->
	def __init__(self, pid, hover):
		self.pid = pid
		self.hover = hover
		self.problems = []
		self.notes = []
		self.scrolled = 0
		self.pages = 0
		self.searched = 0
		self.expanded = 0

	def registryTabs(self):
		# <!-- custom: Each advisor's shown tab labels from the registry, read once per sweep. (Claude code Opus 5.5) -->
		if getattr(self, "_registryTabs", None) is None:
			self._registryTabs = {}
			for advisor in self.call("uitabs", all=1)["advisors"]:
				self._registryTabs[advisor["advisor"]] = [tab["label"] for tab in advisor["tabs"] if tab.get("shown", True)]
		return self._registryTabs

	def call(self, command, **arguments):
		reply = saspilot.request(self.pid, command, arguments)
		if not reply.get("ok"):
			raise PilotError("%s %s: %s" % (command, arguments, str(reply.get("error")).splitlines()[0]))
		return reply.get("result")

	# <!-- custom: Was (clear=True); only the removed --dismiss path cleared the errors, so it now always reads without clearing (2026-11-27). (Claude code Opus 5.5) -->
	def pythonErrors(self):
		# <!-- custom: This client's own Python error output, from SASPilot's 'pyerrors'.
		# The first version read PythonErr*.log, but that file is one for every client (KI#1081), and on 2026-11-20 a Civ4 stuck while exiting kept it locked, so no later client's traceback reached it: a probe error never showed, and the clean runs before it had checked nothing. (Claude code Opus 5.5) -->
		reply = self.call("pyerrors", clear=0, lines=400)
		if not reply.get("writes"):
			return ([], 0)
		return (reply.get("lines") or [], reply["writes"])

	def check(self, where):
		# <!-- custom: After each press: a popup or the diplomacy screen is a modal the sweep did not expect, so it stops rather than press under it (Codex's advice); a new Python error stops it too, since 2026-11-27, when it no longer goes on after one. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		# <!-- custom: A Python error stops the sweep too: with HidePythonExceptions 0, as SASPilot recommends, each error line opens an EXE dialog in the window, which Python cannot see or close, and a 120-line test write left 120 of them (2026-11-20). (Claude code Opus 5.5) -->
		# <!-- custom: --dismiss, which closed those dialogs by their OK through desktop_windows.py and went on, was removed on 2026-11-27: testing it for main found its pixel match one pixel off and its two-look check never agreeing, as the see-through dialog shows the animated map, so it clicked nothing. (Claude code Opus 5.5) -->
		self.modals(where)
		self.errors(where)

	def errors(self, where):
		# <!-- custom: Read without clearing, so a run that stops leaves the errors for the next one to see; the first version cleared on every read (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		(lines, iWrites) = self.pythonErrors()
		if not iWrites:
			return
		szLast = "-"
		if lines:
			szLast = lines[-1][:300]
		raise Stop("%s: %d Python error writes, the last: %s; stopped; with HidePythonExceptions 0 their dialogs are open in the window too, and pyerrors clear=1 empties the record for a rerun" % (where, iWrites, szLast))

	def modals(self, where):
		popups = self.call("popups").get("popups") or []
		if popups:
			raise Stop("%s: a popup appeared (%s); stopped" % (where, ", ".join([str(popup.get("type")) for popup in popups])))
		state = self.call("uistate")
		if state.get("diplomacy"):
			raise Stop("%s: the diplomacy screen opened; stopped" % where)
		# <!-- custom: BUG's options dialog is modal too, and not one of the open screens (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if state.get("bugOptions"):
			raise Stop("%s: BUG's options dialog is open; stopped" % where)

	def shown(self):
		widgets = self.call("uiwidgets").get("widgets") or []
		return dict((widget["name"], widget) for widget in widgets)

	def hovers(self, where, widgets):
		iDone = 0
		for widget in widgets.values():
			if iDone >= self.hover:
				break
			if widget.get("widgetType") in NO_HOVER or "widgetType" not in widget:
				continue
			iDone += 1
			text = self.call("uihover", widget=widget["name"])
			if not (text or {}).get("help"):
				self.notes.append("%s: %s (%s) has no hover text" % (where, widget["name"], widget.get("widgetType")))

	def closeScreen(self, name, widgets):
		# <!-- custom: The Policy Advisor's Exit is a WIDGET_GENERAL button its own code handles, which becomes REVOLUTION once a civic is changed, so a button other than WIDGET_CLOSE_SCREEN is pressed only while it reads EXIT (2026-11-20). (Claude code Opus 5.5) -->
		exits = [widget["name"] for widget in widgets.values() if widget.get("widgetType") == "WIDGET_CLOSE_SCREEN" or (widget.get("widgetType") == "WIDGET_GENERAL" and plain(widget.get("text")) == "EXIT")]
		if not exits:
			raise Stop("%s: no Exit widget recorded, so it cannot be closed as a player would; stopped" % name)
		self.call("uipress", widget=exits[0])
		state = self.call("uistate")
		if state.get("openScreens"):
			self.problems.append("%s: still open after its Exit" % name)
		# <!-- custom: Closing a screen must leave the main interface active, as an agent's test loop once hid it with the screens (2026-11-20). (Claude code Opus 5.5) -->
		if not state.get("mainInterfaceActive"):
			self.problems.append("%s: the main interface is inactive after its Exit" % name)

	def opened(self, name):
		reply = self.call("uiopen", name=name)
		if reply.get("screen") != EXPECTED[name]:
			raise Stop("%s: opened %s, expected %s; stopped" % (name, reply.get("screen"), EXPECTED[name]))

	def pedia(self, dry, iItems):
		# <!-- custom: The Sevopedia browses by category, a list box ('uiitems' lists its entries by name), and each category's entries are a table read with 'uiread': each category is pressed, then its first non-blank entries, each drawing its page.
		# A page counts only once 'uistate' shows the Sevopedia moved to another page, and a category once it shows that category: the first version counted every press that did not fail (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.opened("pedia")
		self.check("pedia")
		categories = [(item["text"], item.get("category")) for item in self.call("uiitems", widget="PediaMainCategoryList").get("items") or []]
		print("pedia: %d categories" % len(categories))
		search = None
		if not categories:
			self.problems.append("pedia: no categories recorded")
		pages = []
		if dry:
			print("  " + ", ".join([text for (text, szCategory) in categories]))
			self.closeScreen("pedia", self.shown())
			return
		for (category, szCategory) in categories:
			where = "pedia/%s" % category
			self.call("uipress", widget="PediaMainCategoryList", about=category)
			self.check(where)
			shown = (self.call("uistate").get("pedia") or {}).get("category")
			if shown != szCategory:
				self.problems.append("%s: pressed, but the Sevopedia shows %s, not %s" % (where, shown, szCategory))
				continue
			if szCategory in PEDIA_NO_ITEMS:
				continue
			widgets = self.shown()
			# <!-- custom: The index, the hints, the trees and the charts (Eras, Handicaps and the like, a table of their own) draw a page with no entry list; on the turn-402 test save, 8 of the 36 categories. (Claude code Opus 5.5) -->
			if "PediaMainItemList" not in widgets:
				pages.append(category)
				continue
			table = self.call("uiread", widget="PediaMainItemList", cells=1)
			entries = pediaEntries(table)
			if table["rows"] and not table["cells"]:
				self.problems.append("%s: item list has rows but no recorded cell actions" % where)
			if search is None and len(entries) >= 5:
				for _, szText in reversed(entries):
					szQuery = szText[:4].lower()
					if re.match(r"^[a-z]{4}$", szQuery) and any(szQuery not in label.lower() for _, label in entries):
						search = (category, table, szQuery)
						break
			if iItems >= 0:
				entries = entries[:iItems]
			bCheckedExpand = False
			for cell, szText in entries:
				pressed = self.call("uipress", widget="PediaMainItemList", row=cell["row"], column=cell["column"])
				self.check("%s/%s" % (where, szText))
				if (pressed.get("widget"), pressed.get("data1"), pressed.get("data2")) != pediaLinkKey(cell):
					self.problems.append("%s/%s: cell action changed before the press" % (where, szText))
					continue
				after = self.call("uistate").get("pedia") or {}
				# <!-- custom: Category and item together, as item numbers repeat across categories (Codex's review).
				# The category must be the swept one: on the turn-402 save all 943 linked entries, of 23 link widgets, stayed in their category; a first version also took the category the widget names, which let CIV match PEDIA_CIVICS. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
				if after.get("item") != pressed.get("data1") or after.get("category") != szCategory:
					self.problems.append("%s/%s: pressed %s %s, but the Sevopedia shows %s" % (where, szText.strip(), pressed.get("widget"), pressed.get("data1"), after))
					continue
				self.pages += 1
				if not bCheckedExpand:
					bCheckedExpand = True
					self.expand("%s/%s" % (where, szText.strip()))
				# <!-- custom: Back to the category for its next entry, as a page replaces the entry list. (Claude code Opus 5.5) -->
				if "PediaMainItemList" not in self.shown():
					self.call("uipress", widget="PediaMainCategoryList", about=category)
		if pages:
			self.notes.append("pedia: a page with no entry list for %s" % ", ".join(pages))
		if search is not None:
			self.search(*search)
		else:
			self.notes.append("pedia: no category had an ASCII prefix that could narrow five or more linked entries")
		self.closeScreen("pedia", self.shown())

	def expand(self, where):
		# <!-- custom: Each EXPAND of the page: the history one opened a full panel of 27 widgets with a CLOSE button of the same data1 on Saladin's page (2026-11-20); pressing that button again must bring the page back as it was.
		# Done on each category's first page. (Claude code Opus 5.5) -->
		# <!-- custom: Checked by the button itself and the page: its data2 switches between EXPAND and CLOSE and back, and the Sevopedia stays on the same page, as a widget count alone could change on an unrelated redraw (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		page = self.call("uistate").get("pedia")
		widgets = self.shown()
		for iData1 in EXPAND_DATA1:
			buttons = [widget for widget in widgets.values() if widget.get("widgetType") == "WIDGET_PYTHON" and widget.get("data1") == iData1]
			if not buttons:
				continue
			if len(buttons) != 1 or buttons[0].get("data2") != 1:
				self.problems.append("%s: expected one EXPAND (%d) with data2=1" % (where, iData1))
				return
			self.call("uipress", widget=buttons[0]["name"])
			self.check("%s expanded" % where)
			back = [widget for widget in self.shown().values() if widget.get("widgetType") == "WIDGET_PYTHON" and widget.get("data1") == iData1]
			if len(back) != 1 or back[0].get("data2") != 0 or self.call("uistate").get("pedia") != page:
				self.problems.append("%s: EXPAND (%d) did not switch to its CLOSE on the same page" % (where, iData1))
				return
			self.call("uipress", widget=back[0]["name"])
			self.check("%s collapsed" % where)
			widgets = self.shown()
			again = [widget for widget in widgets.values() if widget.get("widgetType") == "WIDGET_PYTHON" and widget.get("data1") == iData1]
			if len(again) != 1 or again[0].get("data2") != 1 or self.call("uistate").get("pedia") != page:
				self.problems.append("%s: CLOSE (%d) did not bring EXPAND back on the same page" % (where, iData1))
				return
			self.expanded += 1

	def search(self, category, table, szQuery):
		# <!-- custom: Compare the ordered page links after typing, as headings can remain in a filtered list without matching the query.
		# Backspace must restore both the table text and the links. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		where = "pedia/%s search" % category
		expected = [pediaLinkKey(cell) for cell, label in pediaEntries(table) if szQuery in label.lower()]
		self.call("uipress", widget="PediaMainCategoryList", about=category)
		self.call("uitype", text=szQuery)
		self.check(where)
		filtered = self.call("uiread", widget="PediaMainItemList", cells=1)
		found = [pediaLinkKey(cell) for cell, _ in pediaEntries(filtered)]
		if found != expected:
			self.problems.append("%s: typing %s returned %d links, expected %d in the original order" % (where, szQuery, len(found), len(expected)))
		self.call("uitype", keys=",".join(["BACKSPACE"] * len(szQuery)))
		self.check(where + " cleared")
		again = self.call("uiread", widget="PediaMainItemList", cells=1)
		if again["rows"] != table["rows"] or again["cells"] != table["cells"]:
			self.problems.append("%s: Backspace did not restore the original rows and cell actions" % where)
		elif found == expected:
			self.searched += 1

	def screen(self, name, dry):
		self.opened(name)
		self.check(name)
		tabs = self.call("uitabs").get("tabs") or []
		print("%s: %s" % (name, ", ".join([tab["label"] for tab in tabs]) or "no footer tabs"))
		expected = self.registryTabs().get(TAB_ADVISOR.get(name, name), [])
		if [tab["label"] for tab in tabs] != expected:
			self.problems.append("%s: footer tabs %s, CvScreenEnums.ADVISOR_TABS has %s" % (name, [tab["label"] for tab in tabs], expected))
		if name in EXPECTED_TAB:
			active = [i for i in range(len(tabs)) if tabs[i]["active"]]
			if active != [EXPECTED_TAB[name]]:
				self.problems.append("%s: opened on tab %s, expected tab %d" % (name, [tabs[i]["label"] for i in active], EXPECTED_TAB[name] + 1))
		if dry:
			self.closeScreen(name, self.shown())
			return
		start = [tab["label"] for tab in tabs if tab["active"]]
		first = self.shown()
		self.hovers(name, first)
		self.scroll(name)
		for tab in tabs:
			if tab["active"]:
				continue
			where = "%s/%s" % (name, tab["label"])
			self.pressTab(name, tab["label"])
			self.hovers(where, self.shown())
			self.scroll(where)
		# <!-- custom: Back to the first tab: it should show what it showed at first; a widget only one visit shows was left behind by another tab or lost. (Claude code Opus 5.5) -->
		if start and len(tabs) > 1:
			self.pressTab(name, start[0])
			self.compare("%s/%s" % (name, start[0]), first, self.shown())
		final = self.shown()
		self.closeScreen(name, final)
		self.check("%s closed" % name)
		# <!-- custom: Reopened: the same tabs, and the active tab presses again. (Claude code Opus 5.5) -->
		self.opened(name)
		self.check("%s reopened" % name)
		tabsAgain = self.call("uitabs").get("tabs") or []
		if [tab["label"] for tab in tabsAgain] != [tab["label"] for tab in tabs]:
			self.problems.append("%s reopened: tabs %s, were %s" % (name, [tab["label"] for tab in tabsAgain], [tab["label"] for tab in tabs]))
		others = [tab for tab in tabsAgain if not tab["active"]]
		if others:
			self.pressTab("%s reopened" % name, others[0]["label"])
		self.closeScreen(name, self.shown())

	def scroll(self, where):
		# <!-- custom: A list with scroll arrows ('uiscroll', such as the Foreign Advisor's Bonuses grid) is scrolled to its bottom and back to its top: each end should hide its own arrows, as at the start of the list (the user asked for these arrows, 2026-11-20). (Claude code Opus 5.5) -->
		arrows = self.call("uiscroll").get("arrows") or []
		if "bottom" not in arrows:
			return
		self.scrolled += 1
		after = self.call("uiscroll", dir="bottom").get("arrows") or []
		self.check("%s scrolled to the bottom" % where)
		if "bottom" in after or "top" not in after:
			self.problems.append("%s: scrolled to the bottom, the arrows shown are %s" % (where, after))
			return
		after = self.call("uiscroll", dir="top").get("arrows") or []
		self.check("%s scrolled to the top" % where)
		if after != arrows:
			self.problems.append("%s: back at the top, the arrows shown are %s, were %s" % (where, after, arrows))

	def pressTab(self, name, label):
		# <!-- custom: The tab is looked up by its label just before the press: the Foreign Advisor names its widgets with a running counter, so a tab named ForeignAdvisorWidget539 at the first draw was ForeignAdvisorWidget48 after one press, and the first run of this sweep pressed a name that no longer existed (2026-11-20). (Claude code Opus 5.5) -->
		where = "%s/%s" % (name, label)
		matches = [tab for tab in self.call("uitabs").get("tabs") or [] if tab["label"] == label]
		if len(matches) != 1:
			self.problems.append("%s: %d tabs have this label" % (where, len(matches)))
			return
		self.call("uipress", widget=matches[0]["widget"])
		self.check(where)
		active = [tab["label"] for tab in self.call("uitabs").get("tabs") or [] if tab["active"]]
		if active != [label]:
			self.problems.append("%s: pressed, but the active tab is %s" % (where, active))

	def compare(self, where, before, after):
		# <!-- custom: Compared by name without a trailing number, widget type and text, counted, for the same reason as pressTab: a counter-named widget is another name on each draw. (Claude code Opus 5.5) -->
		def counted(widgets):
			result = Counter()
			for widget in widgets.values():
				result[(re.sub(r"\d+$", "", widget["name"]), widget.get("widgetType"), plain(widget.get("text")))] += 1
			return result
		(old, new) = (counted(before), counted(after))
		gone = sorted((old - new).elements())
		added = sorted((new - old).elements())
		if gone:
			self.problems.append("%s: %d widgets missing on the second visit, such as %s" % (where, len(gone), "; ".join([" ".join([str(part) for part in key]) for key in gone[:4]])))
		# <!-- custom: Added widgets are notes: a screen may create one on its first visit to another tab and keep it, such as the Military Advisor's minimap panel, covered by the Summary tab's content, and the Victory screen's spaceship button (2026-11-20); a missing one stays a problem. (Claude code Opus 5.5) -->
		if added:
			self.notes.append("%s: %d widgets only on the second visit, such as %s" % (where, len(added), "; ".join([" ".join([str(part) for part in key]) for key in added[:4]])))


def main():
	parser = argparse.ArgumentParser(description="Open each advisor through SASPilotUI, visit its footer tabs, close and reopen it, and list Python errors, tabs that do not switch, widgets left over between tabs and typed widgets with no hover. Presses only screens and their footer tabs; a popup stops it. Example: python SASPilot/SASPilotUISweep.py; --screens military,domestic; --dry-run.")
	parser.add_argument("--pid", type=int, help="the Civ4 client; default the only one")
	parser.add_argument("--screens", default=",".join(SCREENS), help="comma-separated, from: %s" % ", ".join(SCREENS))
	parser.add_argument("--hover", type=int, default=10, help="typed widgets to hover per tab (default 10; 0 for none)")
	parser.add_argument("--dry-run", action="store_true", help="open each screen and list its tabs, or the Sevopedia's categories, pressing no tab or category")
	parser.add_argument("--pedia-items", default="3", help="Sevopedia entries to open per category (default 3; all for every one)")
	args = parser.parse_args()
	pid = pick_pid(args.pid)
	names = [part.strip() for part in args.screens.split(",") if part.strip()]
	if not names:
		sys.exit("--screens names no screen; choose from %s" % ", ".join(SCREENS))
	for name in names:
		if name not in SCREENS:
			sys.exit("%s is not in the sweep's list; choose from %s" % (name, ", ".join(SCREENS)))
	iItems = -1
	if args.pedia_items != "all":
		iItems = int(args.pedia_items)
	sweep = Sweep(pid, args.hover)
	if sweep.call("uistate").get("openScreens"):
		sys.exit("a screen is open; close it first, so the sweep starts from the map")
	# <!-- custom: Checked before the first screen too, or an inactive main interface would be reported after every Exit, as if each screen had caused it (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not sweep.call("uistate").get("mainInterfaceActive"):
		sys.exit("the main interface is inactive before the sweep; load the game again so the sweep starts from it")
	# <!-- custom: Errors from before the start are looked at, not cleared unseen: in a 2026-11-20 test of the since removed --dismiss, an error came just before the start, its dialog stayed open and the sweep pressed on under it (2026-11-20).
	# They go through the same check as the sweep's, as Sweep.errors says. (Claude code Opus 5.5) -->
	try:
		sweep.check("before the start")
	except Stop as stop:
		sys.exit(str(stop))
	started = time.time()
	try:
		# <!-- custom: A command that fails, such as a press whose screen code raised, is a problem of that screen; the sweep closes it as a player would and goes on: the first full run ended at the Info Screen's Timeline NameError and skipped the last three screens (2026-11-20). See KI#1101. (Claude code Opus 5.5) -->
		for name in names:
			try:
				if name == "pedia":
					sweep.pedia(args.dry_run, iItems)
				else:
					sweep.screen(name, args.dry_run)
			except PilotError as error:
				sweep.problems.append("%s: %s" % (name, error))
				# <!-- custom: The modals are checked before the Exit is pressed to recover (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
				sweep.check("%s after the failure" % name)
				if sweep.call("uistate").get("openScreens"):
					sweep.closeScreen(name, sweep.shown())
	except Stop as stop:
		sweep.problems.append(str(stop))
	print("%d screens in %.1f s, %d lists scrolled, %d Sevopedia pages, %d expanded and back, %d searches: %d problems, %d notes" % (len(names), time.time() - started, sweep.scrolled, sweep.pages, sweep.expanded, sweep.searched, len(sweep.problems), len(sweep.notes)))
	for line in sweep.problems:
		print("  problem: " + line)
	for line in sweep.notes:
		print("  note: " + line)
	return 1 if sweep.problems else 0


if __name__ == "__main__":
	try:
		sys.exit(main())
	except PilotError as error:
		sys.exit(str(error))

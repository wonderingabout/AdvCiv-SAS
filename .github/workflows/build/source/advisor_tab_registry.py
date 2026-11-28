#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the advisors' footer tabs come from CvScreenEnums.ADVISOR_TABS, and that registry agrees with the game's hotkeys, text and SASPilot's command map.

# <!-- custom: Until 2026-11-22 each tabbed advisor kept its own tab list in its own shape (ID lists, text keys built at draw time, two key sets in the Foreign Advisor, a Rise and Fall tab added in the Victory screen), so code that needed every tab had to open each screen, and agents guessed tab numbers (the user's request for a central home).
# This check keeps the registry the one source:
# - every screen calling drawAdvisorFooterTabs reads it (getAdvisorTab...), and no screen sets PAGE_NAME_LIST from a literal list;
# - each advisor's hotkey comment matches its control's HotKey in CIV4ControlInfos.xml;
# - each label text key exists in SAS text or the inherited text list;
# - advisor names and tab keys are unique;
# - SASPilotUI's _TAB_COMMANDS has exactly the registry's advisor/tab keys, so a new tab cannot go unmapped. See KI#1110. (Claude code Opus 5.5) -->
# <!-- custom: argparse for --help, ast to parse the registry and _TAB_COMMANDS as Python without running them, StringIO to feed tokenize, re for the screens' calls, sys for the exit code. (Claude code Opus 5.5) -->
import argparse
import ast
from io import StringIO
import re
import sys
# <!-- custom: tokenize to skip comments when looking for a screen's calls, ElementTree for CIV4ControlInfos.xml and the text files, Path for the repository's files. (Claude code Opus 5.5) -->
import tokenize
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENUMS = Path("Assets/Python/Screens/CvScreenEnums.py")
PYTHON = Path("Assets/Python")
CONTROLS = Path("Assets/XML/Units/CIV4ControlInfos.xml")
TEXT = Path("Assets/XML/Text")
INHERITED = Path("_0_Legacy/Docs/Manifests/xml_sas_text_inherited_hashes.tsv")
SASPILOT_UI = Path("SASPilot/game/SASPilotUI.py")
# <!-- custom: The folder whose files' cmd_ functions are SASPilot's commands, so each _TAB_COMMANDS command can be checked to exist.
# All of SASPilot/game since 2026-11-28, when SASPilotCatalog.py took the first commands out of SASPilotCommands.py by topic: a list of files would need each new one added. (Claude code Opus 5.5) -->
SASPILOT_GAME = Path("SASPilot/game")
DLL = Path("CvGameCoreDLL")
# <!-- custom: The Info page numbers the DLL passes to showInfoScreen, with the tab each means: CvDLLWidgetData.cpp opens Score with py.showInfoScreen(1).
# Codex's review noted that native callers pass numbers, so reordering the registry would open another tab; a number the DLL passes that is not listed here fails too, until its tab is named. See KI#1110. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
DLL_INFO_PAGES = {1: "SCORE"}


def parse_registry(text: str) -> tuple[list[dict], list[str]]:
	# <!-- custom: The ADVISOR_TABS entries from CvScreenEnums.py's source, each with its hotkey comment from the entry's first line; Python 3's ast reads this Python 2 file, as it has no Python 2-only syntax. See KI#1110. (Claude code Opus 5.5) -->
	problems = []
	tree = ast.parse(text)
	lines = text.splitlines()
	node = None
	for statement in tree.body:
		if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ADVISOR_TABS" for target in statement.targets):
			node = statement.value
	if not isinstance(node, ast.Tuple):
		return ([], ["ADVISOR_TABS is not a tuple in %s" % ENUMS])
	advisors = []
	for item in node.elts:
		if not isinstance(item, ast.Tuple) or len(item.elts) != 4:
			problems.append("line %d: an advisor is (name, screen ID, control, tabs)" % item.lineno)
			continue
		(name, screen, control, tabs) = item.elts
		if not isinstance(tabs, ast.Tuple):
			problems.append("line %d: advisor tabs must be a tuple" % tabs.lineno)
			continue
		match = re.search(r"#\s*(?:<!-- custom:\s*)?(F\d+)\b", lines[item.lineno - 1])
		advisor = {"name": ast.literal_eval(name), "control": ast.literal_eval(control), "hotkey": match and match.group(1), "line": item.lineno, "tabs": []}
		for tab in tabs.elts:
			if not isinstance(tab, ast.Tuple) or len(tab.elts) != 3:
				problems.append("line %d: a tab is (key, text key, game option or None)" % tab.lineno)
				continue
			try:
				(key, text_key, option) = [ast.literal_eval(part) for part in tab.elts]
			except ValueError:
				problems.append("line %d: tab fields must be literal values" % tab.lineno)
				continue
			if not isinstance(key, str) or not isinstance(text_key, str) or (option is not None and not isinstance(option, str)):
				problems.append("line %d: a tab needs string keys and a string option or None" % tab.lineno)
				continue
			advisor["tabs"].append({"key": key, "text": text_key, "option": option, "line": tab.lineno})
		advisors.append(advisor)
	return (advisors, problems)


def control_hotkeys(xml_text: str) -> dict[str, str]:
	# <!-- custom: Civ4's XML declares a default namespace, so tags are matched by their local name; the first version looked for plain "ControlInfo" and found none. (Claude code Opus 5.5) -->
	hotkeys = {}
	for info in ET.fromstring(xml_text).iter():
		if info.tag.rsplit("}", 1)[-1] != "ControlInfo":
			continue
		fields = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in info}
		key = fields.get("HotKey", "")
		hotkeys[fields.get("Type")] = key[3:] if key.startswith("KB_") else key
	return hotkeys


def text_keys(root: Path) -> set[str]:
	keys = set()
	for path in sorted((root / TEXT).glob("*.xml")):
		keys.update(re.findall(r"<Tag>([^<]+)</Tag>", path.read_text(encoding="utf-8", errors="replace")))
	for line in (root / INHERITED).read_text(encoding="utf-8").splitlines()[1:]:
		keys.add(line.split("\t", 1)[0])
	return keys


def check_registry(advisors: list[dict], hotkeys: dict[str, str], known_text: set[str]) -> list[str]:
	problems = []
	names = [advisor["name"] for advisor in advisors]
	for name in sorted(set(names)):
		if names.count(name) > 1:
			problems.append("advisor %s is listed %d times" % (name, names.count(name)))
	for advisor in advisors:
		where = "%s:%d %s" % (ENUMS, advisor["line"], advisor["name"])
		if advisor["control"] not in hotkeys:
			problems.append("%s: no %s in %s" % (where, advisor["control"], CONTROLS))
		elif advisor["hotkey"] != hotkeys[advisor["control"]]:
			problems.append("%s: hotkey comment says %s, %s has %s" % (where, advisor["hotkey"] or "nothing", advisor["control"], hotkeys[advisor["control"]] or "none"))
		keys = [tab["key"] for tab in advisor["tabs"]]
		for key in sorted(set(keys)):
			if keys.count(key) > 1:
				problems.append("%s: tab %s is listed %d times" % (where, key, keys.count(key)))
		for tab in advisor["tabs"]:
			if tab["text"] not in known_text:
				problems.append("%s:%d: text key %s is in no SAS text file nor the inherited list" % (ENUMS, tab["line"], tab["text"]))
	return problems


def check_screens(texts: dict[str, str]) -> list[str]:
	problems = []
	for name, text in sorted(texts.items()):
		if name.endswith("SASUtils.py") or "drawAdvisorFooterTab" not in text:
			continue
		# <!-- custom: Tokenize Python 2 source so comments and quoted examples cannot satisfy the check, and a list spanning several lines is still checked. See KI#1110. (GPT-6.2-Sol) -->
		tokens = [token for token in tokenize.generate_tokens(StringIO(text).readline) if token.type not in (tokenize.COMMENT, tokenize.NL)]
		calls = {token.string for token, following in zip(tokens, tokens[1:]) if token.type == tokenize.NAME and following.string == "("}
		if not calls.intersection({"drawAdvisorFooterTabs", "drawAdvisorFooterTabRows"}):
			continue
		if not calls.intersection({"getAdvisorTabs", "getAdvisorTabKeys", "getAdvisorTabTextKeys", "getAdvisorTabIndex", "getAdvisorTabLabels", "getAdvisorTabLabel"}):
			problems.append("%s draws footer tabs without reading CvScreenEnums.ADVISOR_TABS" % name)
		for index, token in enumerate(tokens):
			if token.string != "PAGE_NAME_LIST":
				continue
			following = [part.string for part in tokens[index + 1:index + 7]]
			if following[:3] == ["[", ":", "]"]:
				following = following[3:]
			if len(following) >= 3 and following[:2] == ["=", "["] and following[2] != "]":
				problems.append("%s:%d sets PAGE_NAME_LIST from a literal list; add the tab to CvScreenEnums.ADVISOR_TABS instead" % (name, token.start[0]))
	return problems


def command_names(texts: list[str]) -> set[str]:
	return {name for text in texts for name in re.findall(r"^def cmd_(\w+)\(", text, re.MULTILINE)}


def check_commands(advisors: list[dict], ui_text: str, commands: set[str] | None = None) -> list[str]:
	# <!-- custom: With commands, each entry's value is checked too: a command that exists, or None with a note on what covers part of it.
	# Keys alone were checked first, so "battlez" for "battles" passed and 'uitabs all=1' advertised a command that does not exist (Codex's review, 2026-11-27). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: Parse just this dictionary so another mapping cannot satisfy it and Python cannot silently collapse duplicate keys before they are checked. (GPT-6.2-Sol) -->
	match = re.search(r"^_TAB_COMMANDS[ \t]*=[ \t]*(\{.*?\})[ \t]*$", ui_text, re.MULTILINE | re.DOTALL)
	if match is None:
		return ["%s: missing _TAB_COMMANDS dictionary" % SASPILOT_UI]
	try:
		mapping = ast.parse(match.group(1), mode="eval").body
	except SyntaxError:
		return ["%s: invalid _TAB_COMMANDS dictionary" % SASPILOT_UI]
	if not isinstance(mapping, ast.Dict):
		return ["%s: _TAB_COMMANDS must be a dictionary" % SASPILOT_UI]
	mapped = set()
	problems = []
	for key in mapping.keys:
		if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
			problems.append("%s: _TAB_COMMANDS requires literal string keys" % SASPILOT_UI)
			continue
		if key.value in mapped:
			problems.append("%s: duplicate _TAB_COMMANDS entry %s" % (SASPILOT_UI, key.value))
		mapped.add(key.value)
	for (key, value) in zip(mapping.keys, mapping.values):
		if commands is None or not isinstance(key, ast.Constant):
			continue
		try:
			entry = ast.literal_eval(value)
		except ValueError:
			entry = None
		if not (isinstance(entry, tuple) and len(entry) == 2 and (entry[1] is None or isinstance(entry[1], str))):
			problems.append("%s: _TAB_COMMANDS entry %s must be (command, note)" % (SASPILOT_UI, key.value))
		elif entry[0] is None and not entry[1]:
			problems.append("%s: _TAB_COMMANDS entry %s has no command, so it needs a note on what covers part of it" % (SASPILOT_UI, key.value))
		elif entry[0] is not None and entry[0] not in commands:
			problems.append("%s: _TAB_COMMANDS entry %s names %r, which is no SASPilot command" % (SASPILOT_UI, key.value, entry[0]))
	registry = {"%s/%s" % (advisor["name"], tab["key"]) for advisor in advisors for tab in advisor["tabs"]}
	problems += ["%s: registry tab %s has no _TAB_COMMANDS entry (its command, or None with a note)" % (SASPILOT_UI, key) for key in sorted(registry - mapped)]
	problems += ["%s: _TAB_COMMANDS entry %s is not in the registry" % (SASPILOT_UI, key) for key in sorted(mapped - registry)]
	return problems


def check_dll_info_pages(advisors: list[dict], cpp_texts: dict[str, str]) -> list[str]:
	problems = []
	info = [advisor for advisor in advisors if advisor["name"] == "info"]
	keys = [tab["key"] for tab in info[0]["tabs"]] if info else []
	for name, text in sorted(cpp_texts.items()):
		for match in re.finditer(r"showInfoScreen\(\s*(\d+)\s*\)", text):
			number = int(match.group(1))
			line = text.count("\n", 0, match.start()) + 1
			if number not in DLL_INFO_PAGES:
				problems.append("%s:%d passes Info page %d, which DLL_INFO_PAGES does not name; add the tab it means" % (name, line, number))
			elif number >= len(keys) or keys[number] != DLL_INFO_PAGES[number]:
				problems.append("%s:%d opens Info page %d, meant as %s, but the registry has %s there" % (name, line, number, DLL_INFO_PAGES[number], keys[number] if number < len(keys) else "no tab"))
	return problems


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.parse_args()
	(advisors, problems) = parse_registry((ROOT / ENUMS).read_text(encoding="utf-8"))
	problems += check_registry(advisors, control_hotkeys((ROOT / CONTROLS).read_text(encoding="utf-8")), text_keys(ROOT))
	screens = {str(path.relative_to(ROOT)).replace("\\", "/"): path.read_text(encoding="utf-8", errors="replace") for path in sorted((ROOT / PYTHON).rglob("*.py"))}
	problems += check_screens(screens)
	problems += check_commands(advisors, (ROOT / SASPILOT_UI).read_text(encoding="utf-8"), command_names([path.read_text(encoding="utf-8") for path in sorted((ROOT / SASPILOT_GAME).glob("*.py"))]))
	problems += check_dll_info_pages(advisors, {str(path.relative_to(ROOT)).replace("\\", "/"): path.read_text(encoding="utf-8", errors="replace") for path in sorted((ROOT / DLL).glob("*.cpp"))})
	if problems:
		print("FAIL advisor tab registry:")
		for problem in problems:
			print("  " + problem)
		return 1
	print("PASS advisor tab registry (%d advisors, %d tabs)" % (len(advisors), sum(len(advisor["tabs"]) for advisor in advisors)))
	return 0


if __name__ == "__main__":
	sys.exit(main())

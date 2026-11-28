#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the Sevopedia's item kinds come from CvScreenEnums.PEDIA_ITEM_KINDS, and every Sevopedia page an entry point jumps to by item has a row there.

# <!-- custom: Until 2026-11-28 two lists named the Sevopedia's item kinds, SevoPediaMain's SAS_linkMatchDefs and SASPilotCommands' _PEDIA_KINDS, and each lacked kinds the other had; neither had votes or event triggers, though CvScreensInterface has pediaJumpToVote and pediaJumpToEventTrigger.
# This check keeps the table the one source:
# - each row is (prefix, count method, info method, category, landing categories, link-matched), with SevoScreenEnums categories that exist and the row's category among its landing ones;
# - each pediaJumpTo* entry point's Sevopedia category is a row's category, unless JUMPS_WITHOUT_ROW says why it has none;
# - the two consumers assign their list from PEDIA_ITEM_KINDS rather than writing one. See KI#1110.2. (Claude code Opus 5.5) -->
# <!-- custom: argparse for --help, ast to read the table as Python without running it, re for the entry points, sys for the exit code, Path for the files. (Claude code Opus 5.5) -->
import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENUMS = Path("Assets/Python/Screens/CvScreenEnums.py")
SCREENS_INTERFACE = Path("Assets/Python/EntryPoints/CvScreensInterface.py")
# <!-- custom: Each file reading the table, with the name it assigns from it. (Claude code Opus 5.5) -->
CONSUMERS = ((Path("Assets/Python/Contrib/Sevopedia/SevoPediaMain.py"), "self.SAS_linkMatchDefs"), (Path("SASPilot/game/SASPilotCatalog.py"), "_PEDIA_KINDS"))
# <!-- custom: Entry points whose item is not an index into one XML table, with why. (Claude code Opus 5.5) -->
JUMPS_WITHOUT_ROW = {"PEDIA_GAME_SPEED_CHART": "pediaJumpToGameSpeed's item packs a speed and a culture level, which SevoPediaGameSpeedChart unpacks"}


def sevo_categories(tree: ast.Module) -> set[str]:
	for statement in tree.body:
		if isinstance(statement, ast.ClassDef) and statement.name == "SevoScreenEnums":
			return {target.id for item in statement.body if isinstance(item, ast.Assign) for target in item.targets if isinstance(target, ast.Name)}
	return set()


def category_name(node: ast.AST) -> str | None:
	if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "SevoScreenEnums":
		return node.attr
	return None


def parse_kinds(text: str) -> tuple[list[dict], list[str]]:
	tree = ast.parse(text)
	categories = sevo_categories(tree)
	node = None
	for statement in tree.body:
		if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "PEDIA_ITEM_KINDS" for target in statement.targets):
			node = statement.value
	if not isinstance(node, ast.Tuple):
		return ([], ["PEDIA_ITEM_KINDS is not a tuple in %s" % ENUMS])
	kinds = []
	problems = []
	for row in node.elts:
		if not isinstance(row, ast.Tuple) or len(row.elts) != 6:
			problems.append("line %d: a kind is (prefix, count method, info method, category, landing categories, link-matched)" % row.lineno)
			continue
		(prefix, count, info, category, landing, link) = row.elts
		strings = [element.value if isinstance(element, ast.Constant) and isinstance(element.value, str) else None for element in (prefix, count, info)]
		if None in strings or not strings[0].endswith("_") or not strings[1].startswith("getNum") or not strings[2].startswith("get"):
			problems.append("line %d: prefix, count and info method must be strings such as \"UNIT_\", \"getNumUnitInfos\", \"getUnitInfo\"" % row.lineno)
			continue
		if not isinstance(link, ast.Constant) or not isinstance(link.value, bool):
			problems.append("line %d: link-matched must be True or False" % row.lineno)
		if not isinstance(landing, ast.Tuple):
			problems.append("line %d: landing categories must be a tuple" % row.lineno)
			continue
		landing_names = [category_name(element) for element in landing.elts]
		category_value = None if isinstance(category, ast.Constant) and category.value is None else category_name(category)
		for name in [category_value] + landing_names:
			if name is not None and name not in categories:
				problems.append("line %d: SevoScreenEnums has no %s" % (row.lineno, name))
		if None in landing_names:
			problems.append("line %d: landing categories must be SevoScreenEnums names" % row.lineno)
		if category_value is None and not (isinstance(category, ast.Constant) and category.value is None):
			problems.append("line %d: the category must be a SevoScreenEnums name or None" % row.lineno)
		elif category_value is None and landing_names:
			problems.append("line %d: a kind without a page has no landing categories" % row.lineno)
		elif category_value is not None and category_value not in landing_names:
			problems.append("line %d: %s must be among its own landing categories" % (row.lineno, category_value))
		kinds.append({"prefix": strings[0], "count": strings[1], "info": strings[2], "category": category_value, "line": row.lineno})
	pairs = [(kind["count"], kind["info"]) for kind in kinds]
	problems += ["%s: %s is listed twice" % (ENUMS, "/".join(pair)) for pair in sorted(set(pair for pair in pairs if pairs.count(pair) > 1))]
	return (kinds, problems)


def check_jumps(kinds: list[dict], text: str) -> list[str]:
	# <!-- custom: The Sevopedia branch of each pediaJumpTo* function, such as pediaMainScreen.pediaJump(SevoScreenEnums.PEDIA_UNITS, ...). (Claude code Opus 5.5) -->
	rows = {kind["category"] for kind in kinds}
	problems = []
	for match in re.finditer(r"^def (pediaJumpTo\w+)\(.*?(?=^def |\Z)", text, re.M | re.S):
		# <!-- custom: \s* lets a call split over lines match too (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		for jump in re.finditer(r"pediaJump\(\s*SevoScreenEnums\.(PEDIA_\w+)", match.group(0)):
			category = jump.group(1)
			if category not in rows and category not in JUMPS_WITHOUT_ROW:
				problems.append("%s: %s jumps to %s, which no PEDIA_ITEM_KINDS row has; add its row, or name it in JUMPS_WITHOUT_ROW with why" % (SCREENS_INTERFACE, match.group(1), category))
	return problems


def check_consumers(texts: dict[str, tuple[str, str]]) -> list[str]:
	problems = []
	for path, (name, text) in sorted(texts.items()):
		# <!-- custom: Comments are cut first, as "# PEDIA_ITEM_KINDS" after a list of its own passed (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		assignments = [line.split("#")[0] for line in text.splitlines() if re.match(r"\s*%s\s*=" % re.escape(name), line)]
		if not assignments:
			problems.append("%s: %s is not assigned; this check names it in CONSUMERS" % (path, name))
		problems += ["%s: %s must come from PEDIA_ITEM_KINDS, not a list of its own: %s" % (path, name, line.strip()[:80]) for line in assignments if "PEDIA_ITEM_KINDS" not in line]
	return problems


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.parse_args()
	(kinds, problems) = parse_kinds((ROOT / ENUMS).read_text(encoding="utf-8"))
	problems += check_jumps(kinds, (ROOT / SCREENS_INTERFACE).read_text(encoding="utf-8"))
	problems += check_consumers({str(path): (name, (ROOT / path).read_text(encoding="utf-8")) for (path, name) in CONSUMERS})
	if problems:
		print("FAIL Sevopedia item kinds:")
		for problem in problems:
			print("  " + problem)
		return 1
	print("PASS Sevopedia item kinds (%d kinds, %d with a page)" % (len(kinds), len([kind for kind in kinds if kind["category"] is not None])))
	return 0


if __name__ == "__main__":
	sys.exit(main())

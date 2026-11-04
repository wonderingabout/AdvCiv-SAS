#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: XML lists whose file order players see follow the order players expect.
# Leaders and civilizations follow the alphabetical order of their shown English names; civics (within each category) and religions follow the tech-tree column of their required tech.

# <!-- custom: argparse/pathlib/re/sys drive the CLI and XML scan; the sibling inherited-text module supplies GameText parsing and the committed inherited names. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys

# <!-- custom: Shared repo-root resolution, as in the sibling XML checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root
from xml_sas_text_inherited import NAMES, TEXT_DIR, display_text, read_names, text_entries


# <!-- custom: The Custom Game leader list follows this file's order, not the names: a test with LEADER_CHINESE_LEADER moved showed Mao Zedong between Lincoln and Louis XIV.
# The order must therefore follow the shown name, which can differ from the Type (Mao Zedong is LEADER_CHINESE_LEADER, Roosevelt is LEADER_FRANKLIN_ROOSEVELT). (Claude code Opus 5.5) -->
LEADER_INFOS = "Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml"
LEADER_NOT_IN_LIST = {"LEADER_BARBARIAN", "LEADER_DEFAULTS"}
LEADER_RE = re.compile(r"<Type>\s*(LEADER_\w+)\s*</Type>\s*<Description>\s*(\w+)\s*</Description>")
# <!-- custom: 2026-11-04 screenshots showed two civilization lists: Custom Game lists short names in this file's order ("The USA" came first, before "Arabia"), while Play Now sorts full names itself ("United States of America" near the end).
# So civilizations follow their short names; CIVILIZATION_AMERICA ("United States", renamed from "The USA" the same day) therefore sits under U. Minor and Barbarian civilizations are not in the list and stay last. See KI#1073. (Claude code Opus 5.5) -->
CIV_INFOS = "Assets/XML/Civilizations/CIV4CivilizationInfos.xml"
CIV_NOT_IN_LIST = {"CIVILIZATION_BARBARIAN", "CIVILIZATION_MINOR"}
CIV_RE = re.compile(r"<Type>\s*(CIVILIZATION_\w+)\s*</Type>\s*<Description>\s*\w+\s*</Description>\s*<ShortDescription>\s*(\w+)\s*</ShortDescription>")
# <!-- custom: The Policy Advisor and the Sevopedia (_sevopedia_main_groupings.py) show each civic category in this file's order, which SAS sorted by unlock order ("Civics order aligned to tech pace" in the Main Changes Guide).
# Later tech moves broke it unnoticed: Vassalage moved from Feudalism to Philosophy (Long_Comments_XML.txt #6) and so unlocked before Bureaucracy, and Theocracy (Monotheism) unlocked before Pacifism (Medicine).
# Civics without a required tech count as column 0, and equal columns may keep any order. See KI#1073. (Claude code Opus 5.5) -->
CIVIC_INFOS = "Assets/XML/GameInfo/CIV4CivicInfos.xml"
TECH_INFOS = "Assets/XML/Technologies/CIV4TechInfos.xml"
# <!-- custom: The Sevopedia groups religions by era and keeps this file's order within each era (SevoPediaMain.getReligionList), so religions follow the tech-tree column of their founding tech too.
# They were already in order when this was added; the check keeps them so. See KI#1073. (Claude code Opus 5.5) -->
RELIGION_INFOS = "Assets/XML/GameInfo/CIV4ReligionInfo.xml"
# <!-- custom: True Starts is not checked: CIV4TruLeaderInfos.xml is looked up by <LeaderType> and its order is not shown in game.
# It keeps base AdvCiv's TRU_RAMESSES before TRU_RAGNAR, the reverse of the leader file. (Claude code Opus 5.5) -->


def mod_names(repo_root: Path) -> dict[str, str]:
	names = {}
	for path in sorted((repo_root / TEXT_DIR).glob("*.xml")):
		for tag, english, _line in text_entries(path.read_bytes()):
			names.setdefault(tag, display_text(english))
	return names


def check_names(repo_root: Path, rel_path: str, pattern: re.Pattern, skipped: set[str], names: dict[str, str]) -> list[str]:
	data = (repo_root / rel_path).read_text(encoding="utf-8", errors="replace")
	entries = []
	failures = []
	for match in pattern.finditer(data):
		info_type, key = match.groups()
		if info_type in skipped:
			continue
		if key not in names:
			failures.append(f"{rel_path}: {info_type} uses {key}, but neither mod GameText nor the inherited names list defines it; regenerate the list with xml_sas_text_inherited.py --write")
			continue
		entries.append((names[key], info_type, data.count("\n", 0, match.start()) + 1))
	for previous, current in zip(entries, entries[1:]):
		if previous[0].casefold() > current[0].casefold():
			failures.append(f"{rel_path}:{current[2]}: {current[1]} (\"{current[0]}\") is listed after {previous[1]} (\"{previous[0]}\"); reorder to follow the alphabetical order of the shown names")
	return failures


def first(pattern: str, text: str) -> str | None:
	match = re.search(pattern, text)
	return match.group(1) if match else None


def check_tech_order(repo_root: Path, rel_path: str, info_tag: str, group_tag: str | None) -> list[str]:
	techs = (repo_root / TECH_INFOS).read_text(encoding="utf-8", errors="replace")
	columns = {first(r"<Type>\s*(\w+)\s*</Type>", block): int(first(r"<iGridX>\s*(-?\d+)\s*</iGridX>", block)) for block in re.findall(r"<TechInfo>(.*?)</TechInfo>", techs, re.S)}
	data = (repo_root / rel_path).read_text(encoding="utf-8", errors="replace")
	last: dict[str, tuple[str, str, int]] = {}
	failures = []
	for match in re.finditer("<" + info_tag + ">(.*?)</" + info_tag + ">", data, re.S):
		block = match.group(1)
		info_type = first(r"<Type>\s*(\w+)\s*</Type>", block)
		group = first("<" + group_tag + r">\s*(\w+)\s*</" + group_tag + ">", block) if group_tag else "all"
		tech = first(r"<TechPrereq>\s*(\w+)\s*</TechPrereq>", block) or "NONE"
		column = columns.get(tech, 0)
		previous = last.get(group)
		if previous is not None and previous[2] > column:
			line = data.count("\n", 0, match.start()) + 1
			where = f" in {group}" if group_tag else ""
			failures.append(f"{rel_path}:{line}: {info_type} ({tech}, column {column}) is listed after {previous[0]} ({previous[1]}, column {previous[2]}){where}; reorder by the tech column of each required tech")
		last[group] = (info_type, tech, column)
	return failures


def check(repo_root: Path) -> list[str]:
	names = read_names(NAMES)
	names.update(mod_names(repo_root))
	failures = check_names(repo_root, LEADER_INFOS, LEADER_RE, LEADER_NOT_IN_LIST, names)
	failures += check_names(repo_root, CIV_INFOS, CIV_RE, CIV_NOT_IN_LIST, names)
	failures += check_tech_order(repo_root, CIVIC_INFOS, "CivicInfo", "CivicOptionType")
	failures += check_tech_order(repo_root, RELIGION_INFOS, "ReligionInfo", None)
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that XML lists whose file order players see follow the expected order.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL XML display order")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS XML display order")
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: XML lists whose file order players see follow the order players expect.
# Leaders and civilizations follow the alphabetical order of their shown English names, and civics (within each category) the tech-tree column of their required tech.
# Religions keep the historical order their GameFont glyphs follow, and missionaries, religion buildings, executives and corporation headquarters follow their religion or corporation.

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
# <!-- custom: The Sevopedia groups religions by era and keeps this file's order within each era (SevoPediaMain.getReligionList).
# The first version of this check also required the tech-tree column order of their founding techs, but SAS chose the order on 2025-05-22 as historical founding order (BtS starts with Judaism), and both GameFont files match it.
# A tech move could then have demanded reordering religions and moving their glyphs, so on 2026-11-05 the tech rule was dropped; the fixed GameFont order below keeps the historical order. See KI#1073. (Claude code Opus 5.5) -->
RELIGION_INFOS = "Assets/XML/GameInfo/CIV4ReligionInfo.xml"
# <!-- custom: The DLL (CvGameTextMgr.cpp) gives each religion and corporation its GameFont icon, then its holy-city or headquarters icon, in XML order.
# Reordering religions therefore needs the glyphs in Assets/Res/Fonts/GameFont.tga and GameFont_75.tga moved to match, or icons get swapped; CI cannot read which picture sits in a .tga slot, so it compares against this order, read from both fonts' editor previews on 2026-11-05.
# SAS does not ship CIV4CorporationInfo.xml, so the game uses BtS's fixed CORPORATION_1 to 7 order; if SAS ever ships it, the same rule applies. (Claude code Opus 5.5) -->
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
GAMEFONT_RELIGION_ORDER = ("RELIGION_PAGANISM", "RELIGION_HINDUISM", "RELIGION_JUDAISM", "RELIGION_TAOISM", "RELIGION_BUDDHISM", "RELIGION_CHRISTIANITY", "RELIGION_ISLAM")
CORPORATION_INFOS = "Assets/XML/GameInfo/CIV4CorporationInfo.xml"
GAMEFONT_CORPORATION_ORDER = tuple(f"CORPORATION_{number}" for number in range(1, 8))
UNIT_INFOS = "Assets/XML/Units/CIV4UnitInfos.xml"
BUILDING_INFOS = "Assets/XML/Buildings/CIV4BuildingInfos.xml"
# <!-- custom: Missionaries and religion buildings, and executives and corporation headquarters, are kept in the order of their religion or corporation, so religion N's assets sit in position N of each file.
# No known screen breaks if they drift, but a matching layout makes each family easy to find and review; they were already in order when this was added. (Claude code Opus 5.5) -->
LINKED_ASSET_GROUPS = ((UNIT_INFOS, "UnitInfo", "PrereqReligion", GAMEFONT_RELIGION_ORDER), (BUILDING_INFOS, "BuildingInfo", "PrereqReligion", GAMEFONT_RELIGION_ORDER), (UNIT_INFOS, "UnitInfo", "PrereqCorporation", GAMEFONT_CORPORATION_ORDER), (BUILDING_INFOS, "BuildingInfo", "FoundsCorporation", GAMEFONT_CORPORATION_ORDER))
# <!-- custom: True Starts is not checked: CIV4TruLeaderInfos.xml is looked up by <LeaderType> and its order is not shown in game.
# Its base AdvCiv TRU_RAMESSES before TRU_RAGNAR, the reverse of the leader file, was swapped by hand on 2026-11-04 for tidiness. See KI#1073.2. (Claude code Opus 5.5) -->


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


def info_types(data: str, info_tag: str) -> list[str]:
	return [first(r"<Type>\s*(\w+)\s*</Type>", block) for block in re.findall("<" + info_tag + ">(.*?)</" + info_tag + ">", data, re.S)]


def check_gamefont_order(repo_root: Path) -> list[str]:
	failures = []
	for rel_path, info_tag, expected in ((RELIGION_INFOS, "ReligionInfo", GAMEFONT_RELIGION_ORDER), (CORPORATION_INFOS, "CorporationInfo", GAMEFONT_CORPORATION_ORDER)):
		path = repo_root / rel_path
		if not path.exists():
			continue
		found = tuple(info_types(COMMENT_RE.sub("", path.read_text(encoding="utf-8", errors="replace")), info_tag))
		if found != expected:
			failures.append(f"{rel_path}: order {', '.join(found)} differs from the GameFont glyph order {', '.join(expected)}; move the glyphs in Assets/Res/Fonts/GameFont.tga and GameFont_75.tga to match, then update the order in xml_display_order.py")
	return failures


def check_linked_asset_order(repo_root: Path) -> list[str]:
	failures = []
	for rel_path, info_tag, link_tag, order in LINKED_ASSET_GROUPS:
		data = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), (repo_root / rel_path).read_text(encoding="utf-8", errors="replace"))
		previous = None
		for match in re.finditer("<" + info_tag + ">(.*?)</" + info_tag + ">", data, re.S):
			link = first("<" + link_tag + r">\s*(\w+)\s*</" + link_tag + ">", match.group(1))
			if link is None or link == "NONE":
				continue
			info_type = first(r"<Type>\s*(\w+)\s*</Type>", match.group(1))
			if link not in order:
				failures.append(f"{rel_path}: {info_type} has {link_tag} {link}, which is not in the expected order list")
				continue
			if previous is not None and order.index(link) < order.index(previous[1]):
				line = data.count("\n", 0, match.start()) + 1
				failures.append(f"{rel_path}:{line}: {info_type} ({link}) is listed after {previous[0]} ({previous[1]}); keep these assets in the order of their religions or corporations")
			previous = (info_type, link)
	return failures


def check(repo_root: Path) -> list[str]:
	names = read_names(NAMES)
	names.update(mod_names(repo_root))
	failures = check_names(repo_root, LEADER_INFOS, LEADER_RE, LEADER_NOT_IN_LIST, names)
	failures += check_names(repo_root, CIV_INFOS, CIV_RE, CIV_NOT_IN_LIST, names)
	failures += check_tech_order(repo_root, CIVIC_INFOS, "CivicInfo", "CivicOptionType")
	failures += check_gamefont_order(repo_root)
	failures += check_linked_asset_order(repo_root)
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

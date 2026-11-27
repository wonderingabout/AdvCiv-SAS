#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Some XML type lists are also written out by hand as a DLL enum in CvEnums.h, such as ANIMATIONPATH_* in Civ4AnimationPathInfos.xml and ATTITUDE_* in CIV4AttitudeInfos.xml, and the DLL indexes the XML's rows by that enum, so both must list the same types in the same order.
# Until SAS carried these files (KI#1104.3), the XML side sat in the base game, where no check could see it; a type added, removed or moved on one side only would shift every later row onto the wrong enum value without any load error.
# Codex's review (GPT-6.2-Sol) suggested the animation paths' order; the same holds for the other hand-written enums whose XML SAS now carries, so one table covers them all. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: pathlib locates the files, argparse takes the repository root, re reads the enum blocks, sys loads the shared helpers, and ElementTree reads the XML types. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default and namespace-free tag names, as the other XML checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name


ENUMS = Path("CvGameCoreDLL/CvEnums.h")
GLOBAL_TYPES = Path("Assets/XML/GlobalTypes.xml")
# <!-- custom: Each hand-written enum and where its XML types are: an info file and the element holding each <Type>, or a list in GlobalTypes.xml.
# The DO(...) enums of CvEnumMacros.h, such as EntityEvent or PlayerColor, are not here: the DLL sizes them from the XML at load, so their order cannot drift. (Claude code Opus 5.5) -->
PAIRS = (
	("AnimationPath", "Assets/XML/Units/Civ4AnimationPathInfos.xml", "AnimationPath"),
	("Attitude", "Assets/XML/BasicInfos/CIV4AttitudeInfos.xml", "AttitudeInfo"),
	("Domain", "Assets/XML/BasicInfos/CIV4DomainInfos.xml", "DomainInfo"),
	("Calendar", "Assets/XML/BasicInfos/CIV4CalendarInfos.xml", "CalendarInfo"),
	("ForceControl", "Assets/XML/GameInfo/CIV4ForceControlInfos.xml", "ForceControlInfo"),
	("Automate", GLOBAL_TYPES, "AutomateTypes"),
	("Direction", GLOBAL_TYPES, "DirectionTypes"),
	("Function", GLOBAL_TYPES, "FunctionTypes"),
	# <!-- custom: The rest, found by a scan of every ENUM_START block against the repository's XML types: hand-written enums whose XML SAS carried before KI#1104.3 but no check compared. (Claude code Opus 5.5) -->
	("InterfaceMode", "Assets/XML/Interface/CIV4InterfaceModeInfos.xml", "InterfaceModeInfo"),
	("CityTab", "Assets/XML/BasicInfos/CIV4CityTabInfos.xml", "CityTabInfo"),
	("Yield", "Assets/XML/Terrain/CIV4YieldInfos.xml", "YieldInfo"),
	("Commerce", "Assets/XML/GameInfo/CIV4CommerceInfo.xml", "CommerceInfo"),
	("GameOption", "Assets/XML/GameInfo/CIV4GameOptionInfos.xml", "GameOptionInfo"),
	("MultiplayerOption", "Assets/XML/GameInfo/CIV4MPOptionInfos.xml", "MPOptionInfo"),
	("PlayerOption", "Assets/XML/GameInfo/CIV4PlayerOptionInfos.xml", "PlayerOptionInfo"),
	("GraphicOption", "Assets/XML/GameInfo/CIV4GraphicOptionInfos.xml", "GraphicOptionInfo"),
	("Denial", "Assets/XML/BasicInfos/CIV4DenialInfos.xml", "DenialInfo"),
	("UnitAI", "Assets/XML/BasicInfos/CIV4UnitAIInfos.xml", "UnitAIInfo"),
	("Mission", "Assets/XML/Units/CIV4MissionInfos.xml", "MissionInfo"),
	("Command", "Assets/XML/Units/CIV4CommandInfos.xml", "CommandInfo"),
	("Control", "Assets/XML/Units/CIV4ControlInfos.xml", "ControlInfo"),
	("Memory", "Assets/XML/BasicInfos/CIV4MemoryInfos.xml", "MemoryInfo"),
	("CitySize", GLOBAL_TYPES, "CitySizeTypes"),
	("Contact", GLOBAL_TYPES, "ContactTypes"),
	("DiplomacyPower", GLOBAL_TYPES, "DiplomacyPowerTypes"),
)
# <!-- custom: Enum values with no XML row, inherited as they are: BtS's FunctionTypes has FUNC_STEPKEY, which its GlobalTypes.xml never listed; a value after the XML's last row shifts no row, so it is allowed here by name. (Claude code Opus 5.5) -->
ENUM_ONLY = {"Function": ("FUNC_STEPKEY",)}


def enum_members(text: str, name: str) -> list[str] | None:
	# <!-- custom: Comments are removed before the block is found, so neither a commented-out value nor a comment naming ENUM_END, which cut the block short in the second version, counts (Codex's review, GPT-6.2-Sol). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	text = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", text, flags=re.S))
	match = re.search(r"ENUM_START\(%s,\s*\w+\)(.*?)ENUM_END" % name, text, re.S)
	if match is None:
		return None
	members = []
	directive = None
	for raw in match.group(1).splitlines():
		line = raw.strip()
		if not line:
			continue
		# <!-- custom: A preprocessor line such as #if 0 before a row would make the rows depend on the build, which a name list cannot follow, so it fails (Codex's review); one guarding only the count, as DirectionTypes' #ifdef _USRDLL does, ends the rows anyway. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if line.startswith("#"):
			directive = directive or line
			continue
		for part in line.split(","):
			member, equals, value = part.partition("=")
			member = member.strip()
			if not member:
				continue
			# <!-- custom: NUM_ENUM_TYPES(...) ends the rows; what follows, such as DirectionTypes' masks, is no row. (Claude code Opus 5.5) -->
			if member.startswith("NUM_ENUM_TYPES"):
				return members
			# <!-- custom: The NONE value set to -1 comes before the rows; any other explicit value would shift the rows' indices while the names still compared in order, which Codex's review (GPT-6.2-Sol) reproduced with ANIMATIONPATH_IDLE = 4 passing, so it is returned as an error. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			if equals:
				if value.strip() == "-1" and not members:
					continue
				# <!-- custom: A value equal to the member's position shifts nothing: AdvCiv's GameOptionTypes pins GAMEOPTION_ADVANCED_START = 0, GAMEOPTION_LEAD_ANY_CIV = 7 and others where they already sit. (Claude code Opus 5.5) -->
				if value.strip() != str(len(members)):
					raise ValueError("%s = %s: an explicit value inside a row-indexed enum, at position %d" % (member, value.strip(), len(members)))
			if directive:
				raise ValueError("%s: a preprocessor line before the row %s" % (directive, member))
			members.append(member)
	return members


def xml_types(repo_root: Path, rel: Path | str, element: str) -> list[str]:
	root = ET.parse(repo_root / rel).getroot()
	if Path(rel) == GLOBAL_TYPES:
		for node in root:
			if local_name(node.tag) == element:
				return [(child.text or "").strip() for child in node]
		return []
	# <!-- custom: Rows are read as the DLL's loader reads them: from the first <element>, every sibling in order, whatever its tag, as SetGlobalClassInfo steps with NextSibling.
	# Vanilla's CIV4GraphicOptionInfos.xml, copied by BtS and SAS, wraps its third row, GRAPHICOPTION_CITY_DETAIL, in <PlayerOptionInfo>; the game loads it as the third graphic option, while reading <GraphicOptionInfo> rows only had it missing. (Claude code Opus 5.5) -->
	parents = {child: parent for parent in root.iter() for child in parent}
	first = next((node for node in root.iter() if local_name(node.tag) == element), None)
	if first is None:
		return []
	siblings = list(parents[first])
	types = []
	# <!-- custom: From the first <element> forward, as the loader steps; the first version took the earlier siblings too, which Codex's review (GPT-6.2-Sol) reproduced passing a file whose first row was under the wrong tag, which the DLL skips.
	# A later row without a <Type> is reported as such, as the loader would count it. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for row in siblings[siblings.index(first):]:
		row_types = [(child.text or "").strip() for child in row if local_name(child.tag) == "Type"]
		types.append(row_types[0] if len(row_types) == 1 else "<row %s without one Type>" % local_name(row.tag))
	return types


def check(repo_root: Path) -> list[str]:
	text = (repo_root / ENUMS).read_text(encoding="latin-1")
	failures = []
	for name, rel, element in PAIRS:
		if not (repo_root / rel).is_file():
			failures.append(f"{rel}: missing; {name}Types in {ENUMS} is checked against it")
			continue
		try:
			members = enum_members(text, name)
		except ValueError as error:
			failures.append(f"{ENUMS}: {name}Types: {error}")
			continue
		if members is None:
			failures.append(f"{ENUMS}: no ENUM_START({name}, ...) block")
			continue
		types = xml_types(repo_root, rel, element)
		if not types:
			failures.append(f"{rel}: no {element} types found")
			continue
		extra = [member for member in members[len(types):] if member not in ENUM_ONLY.get(name, ())]
		for index, xml_type in enumerate(types):
			enum_type = members[index] if index < len(members) else "nothing"
			if xml_type != enum_type:
				failures.append(f"{rel}: row {index} is {xml_type}, but {name}Types in {ENUMS} has {enum_type} there; both must list the same types in the same order")
				break
		if extra:
			failures.append(f"{ENUMS}: {name}Types has {', '.join(extra)} after the last row of {rel}")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that the DLL's hand-written enums list the same types, in the same order, as the XML they index.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL DLL enum and XML order")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS DLL enum and XML order: {len(PAIRS)} enum(s) match their XML types")
	return 0


if __name__ == "__main__":
	sys.exit(main())

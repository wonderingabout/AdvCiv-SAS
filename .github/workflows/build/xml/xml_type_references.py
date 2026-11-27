#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Each tag below names a type another XML file defines, such as a unit's <FormationType> or a civilization's <DefaultPlayerColor>; the name must be one that file defines.
# Until SAS carried the defining files (KI#1104.3), they sat in the base game, out of reach of any check, so a misspelt reference, such as FORMATION_TYPE_RANGE for FORMATION_TYPE_RANGED, could only show in game, if at all.
# Codex's review (GPT-6.2-Sol) suggested checking the formation and animation chain; the other references to the carried files are checked the same way. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: pathlib locates the files, argparse takes the repository root, sys loads the shared helpers, and ElementTree reads the references and the types. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default and namespace-free tag names, as the other XML checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name


XML = Path("Assets/XML")
GLOBAL_TYPES = "GlobalTypes.xml"
# <!-- custom: (files holding the reference, or None for every XML file outside Text, the tag, the defining file, and the element whose <Type> it defines, or for GlobalTypes.xml the list; FORMATION_TYPE_* names are the <FormationType> of formation rows, which repeat, not a <Type>). (Claude code Opus 5.5) -->
RULES = (
	(("Units/CIV4UnitInfos.xml",), "FormationType", "Units/CIV4FormationInfos.xml", "UnitFormation/FormationType"),
	(("Units/CIV4FormationInfos.xml",), "EventType", "Units/Civ4EntityEventInfos.xml", "EntityEventInfo"),
	(None, "EntityEvent", "Units/Civ4EntityEventInfos.xml", "EntityEventInfo"),
	# <!-- custom: Missions name theirs in <EntityEventType>, which the first version missed, as Codex's review (GPT-6.2-Sol) reproduced with a misspelt sleep mission that passed. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	(("Units/CIV4MissionInfos.xml",), "EntityEventType", "Units/Civ4EntityEventInfos.xml", "EntityEventInfo"),
	(("Units/Civ4EntityEventInfos.xml",), "AnimationPathType", "Units/Civ4AnimationPathInfos.xml", "AnimationPath"),
	(("Units/Civ4AnimationPathInfos.xml",), "Category", "Units/Civ4AnimationInfos.xml", "AnimationCategory"),
	(("Units/Civ4AnimationInfos.xml",), "DefaultTo", "Units/Civ4AnimationInfos.xml", "AnimationCategory"),
	(("Units/Civ4AnimationPathInfos.xml",), "Operator", GLOBAL_TYPES, "AnimationOperatorTypes"),
	(("Civilizations/CIV4CivilizationInfos.xml",), "DefaultPlayerColor", "Interface/CIV4PlayerColorInfos.xml", "PlayerColorInfo"),
	(("Interface/CIV4PlayerColorInfos.xml",), "ColorTypePrimary", "Interface/CIV4ColorVals.xml", "ColorVal"),
	(("Interface/CIV4PlayerColorInfos.xml",), "ColorTypeSecondary", "Interface/CIV4ColorVals.xml", "ColorVal"),
	(("Interface/CIV4PlayerColorInfos.xml",), "TextColorType", "Interface/CIV4ColorVals.xml", "ColorVal"),
	(None, "Advisor", "Interface/CIV4AdvisorInfos.xml", "AdvisorInfo"),
	(("Terrain/CIV4TerrainInfos.xml",), "ArtDefineTag", "Art/CIV4ArtDefines_Terrain.xml", "TerrainArtInfo"),
)
# <!-- custom: Values meaning no reference, as the XML writes them. (Claude code Opus 5.5) -->
EMPTY = ("", "NONE")


def defined(repo_root: Path, rel: str, element: str, cache: dict) -> set[str]:
	key = (rel, element)
	if key not in cache:
		root = ET.parse(repo_root / XML / rel).getroot()
		names = set()
		if rel == GLOBAL_TYPES:
			names = {(child.text or "").strip() for node in root if local_name(node.tag) == element for child in node}
		elif "/" in element:
			row, field = element.split("/")
			names = {(child.text or "").strip() for node in root.iter() if local_name(node.tag) == row for child in node if local_name(child.tag) == field}
		else:
			names = {(child.text or "").strip() for node in root.iter() if local_name(node.tag) == element for child in node if local_name(child.tag) == "Type"}
		cache[key] = names
	return cache[key]


def source_files(repo_root: Path, sources) -> list[Path]:
	if sources is not None:
		return [repo_root / XML / rel for rel in sources]
	return sorted(path for path in (repo_root / XML).rglob("*.xml") if "Text" not in path.relative_to(repo_root / XML).parts)


def check(repo_root: Path) -> tuple[list[str], int]:
	failures = []
	checked = 0
	cache: dict = {}
	parsed: dict = {}
	for sources, tag, rel, element in RULES:
		if not (repo_root / XML / rel).is_file():
			failures.append(f"{XML / rel}: missing; <{tag}> references are checked against it")
			continue
		names = defined(repo_root, rel, element, cache)
		if not names:
			failures.append(f"{XML / rel}: defines no {element} types; <{tag}> references are checked against them")
			continue
		before = checked
		for path in source_files(repo_root, sources):
			if not path.is_file():
				failures.append(f"{path.relative_to(repo_root)}: missing")
				continue
			if path not in parsed:
				try:
					parsed[path] = ET.parse(path).getroot()
				except ET.ParseError:
					# <!-- custom: A file that does not parse is xml_comments.py's and the game's to report; this check only reads references. (Claude code Opus 5.5) -->
					parsed[path] = None
			root = parsed[path]
			if root is None:
				continue
			for node in root.iter():
				if local_name(node.tag) != tag:
					continue
				value = (node.text or "").strip()
				if value in EMPTY:
					continue
				checked += 1
				if value not in names:
					failures.append(f"{path.relative_to(repo_root)}: <{tag}>{value}</{tag}> is not defined in {XML / rel}")
		# <!-- custom: A rule that finds no reference at all checks nothing, as after a tag rename, so it fails rather than passing silently. (Claude code Opus 5.5) -->
		if checked == before:
			failures.append(f"no <{tag}> reference found for the rule against {XML / rel}; update RULES if the tag moved")
	return failures, checked


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that XML references to types defined in another XML file, such as formation types, entity events, player colors and advisors, name a type that file defines.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()
	failures, checked = check(args.repo_root)
	if failures:
		print("FAIL XML type references")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS XML type references: {checked} reference(s) across {len(RULES)} rule(s) name a defined type")
	return 0


if __name__ == "__main__":
	sys.exit(main())

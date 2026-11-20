#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: Barbarian balance values that must stay above every other player's.
#
# <!-- custom: Two Barbarian values define their role, and a retune could silently reach another player's value:
# - the Barbarian Worker's iWorkRate is its main reason to stay civ-specific (Barbarian Workers often die in cities at war and compensate a later start), so it must stay strictly faster than every other land Worker, including civ-specific ones;
# - the Barbarian leader's iBuildUnitProb keeps Barbarians focused on military pressure, so it must stay strictly higher than every other leader's.
# Workers are land units whose DefaultUnitAI is UNITAI_WORKER; Barbarian assets are found through the CIVILIZATION_BARBARIAN civilization's Units and Leaders lists.
# CIVILIZATION_BARBARIAN is named directly because the BARBARIAN_CIVILIZATION define lives in the inherited base GlobalDefines, which is not in the repository. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

# <!-- custom: Resolve the shared XML helpers from this subject subfolder, as the other build/xml checks do. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


BARBARIAN_CIVILIZATION = "CIVILIZATION_BARBARIAN"
CIVILIZATIONS_PATH = Path("Assets/XML/Civilizations/CIV4CivilizationInfos.xml")
UNITS_PATH = Path("Assets/XML/Units/CIV4UnitInfos.xml")
LEADERS_PATH = Path("Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml")


def infos_by_type(repo_root: Path, path: Path, info_tag: str) -> dict[str, ET.Element]:
	result: dict[str, ET.Element] = {}
	for node in ET.parse(repo_root / path).getroot().iter():
		if local_name(node.tag) == info_tag:
			info_type = child_text_by_local_name(node, "Type")
			if info_type is not None:
				result[info_type] = node
	return result


def barbarian_children(repo_root: Path, parent_tag: str, child_tag: str, value_tag: str) -> set[str]:
	for civ in ET.parse(repo_root / CIVILIZATIONS_PATH).getroot().iter():
		if local_name(civ.tag) != "CivilizationInfo" or child_text_by_local_name(civ, "Type") != BARBARIAN_CIVILIZATION:
			continue
		values = set()
		for parent in civ:
			if local_name(parent.tag) != parent_tag:
				continue
			for child in parent:
				if local_name(child.tag) == child_tag:
					value = (child_text_by_local_name(child, value_tag) or "").strip()
					if value and value != "NONE":
						values.add(value)
		return values
	raise RuntimeError(f"{CIVILIZATIONS_PATH}: {BARBARIAN_CIVILIZATION} is missing")


def read_int(node: ET.Element, tag: str) -> int:
	value = child_text_by_local_name(node, tag)
	if value is None or value.strip() == "":
		raise RuntimeError(f"{child_text_by_local_name(node, 'Type')} has no {tag}")
	return int(value)


def strictly_highest(kind: str, value_tag: str, barbarian: list[str], others: list[str], infos: dict[str, ET.Element]) -> list[str]:
	failures = []
	for barbarian_type in barbarian:
		barbarian_value = read_int(infos[barbarian_type], value_tag)
		for other_type in others:
			other_value = read_int(infos[other_type], value_tag)
			if barbarian_value <= other_value:
				failures.append(f"{BARBARIAN_CIVILIZATION}: {kind} {barbarian_type} {value_tag} {barbarian_value} is not higher than {other_type} {value_tag} {other_value}")
	return failures


def is_land_worker(unit: ET.Element) -> bool:
	return child_text_by_local_name(unit, "DefaultUnitAI") == "UNITAI_WORKER" and child_text_by_local_name(unit, "Domain") == "DOMAIN_LAND"


def audit_barbarian_workers(repo_root: Path) -> tuple[list[str], int]:
	units = infos_by_type(repo_root, UNITS_PATH, "UnitInfo")
	barbarian_types = barbarian_children(repo_root, "Units", "Unit", "UnitType")
	barbarian = sorted(t for t in barbarian_types if t in units and is_land_worker(units[t]))
	others = sorted(t for t, unit in units.items() if t not in barbarian_types and is_land_worker(unit))
	return strictly_highest("Worker", "iWorkRate", barbarian, others, units), len(barbarian)


def audit_barbarian_leaders(repo_root: Path) -> tuple[list[str], int]:
	leaders = infos_by_type(repo_root, LEADERS_PATH, "LeaderHeadInfo")
	barbarian_types = barbarian_children(repo_root, "Leaders", "Leader", "LeaderName")
	missing = sorted(barbarian_types - leaders.keys())
	if missing:
		return [f"{BARBARIAN_CIVILIZATION}: leader {name} has no LeaderHeadInfo" for name in missing], 0
	barbarian = sorted(barbarian_types)
	others = sorted(t for t in leaders if t not in barbarian_types)
	return strictly_highest("leader", "iBuildUnitProb", barbarian, others, leaders), len(barbarian)


def main() -> int:
	parser = argparse.ArgumentParser(description="Fail if Barbarian Worker work rate or Barbarian leader unit probability is not strictly above every other player's.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	worker_failures, workers = audit_barbarian_workers(args.repo_root)
	leader_failures, leaders = audit_barbarian_leaders(args.repo_root)
	failures = worker_failures + leader_failures
	if failures:
		print("FAIL Barbarian balance check")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS Barbarian balance check: {workers} Barbarian Worker(s) faster than every other Worker; {leaders} Barbarian leader(s) with a higher iBuildUnitProb than every other leader.")
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: True Starts companion coverage and reference integrity.
# <!-- custom: True Starts builds the Random-civilization candidate pool exclusively from TruCivInfo,
# and calcFitness dereferences fixed civilizations through the same mapping. Require every playable or
# AI-playable civilization to have exactly one TruCivInfo. TruLeaderInfo is runtime-optional, but SAS
# treats one row per leader belonging to a playable civilization as the maintained completeness policy
# so new leaders do not silently lose contemporaneity/bias data. TruBonusInfo is intentionally sparse;
# missing rows mean no True Starts resource bias, so validate supplied rows rather than requiring one
# for every BonusInfo. See KI#936. (ChatGPT-5.6-Sol) -->

from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the XML checks' repository lookup and namespace-aware element helpers so True Starts reads the same XML format as the other checks. (GPT-6.1-Sol) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


CIVILIZATION_INFOS = Path("Assets/XML/Civilizations/CIV4CivilizationInfos.xml")
LEADER_INFOS = Path("Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml")
BONUS_INFOS = Path("Assets/XML/Terrain/CIV4BonusInfos.xml")
TRU_CIV_INFOS = Path("Assets/XML/TrueStarts/CIV4TruCivInfos.xml")
TRU_LEADER_INFOS = Path("Assets/XML/TrueStarts/CIV4TruLeaderInfos.xml")
TRU_BONUS_INFOS = Path("Assets/XML/TrueStarts/CIV4TruBonusInfos.xml")


def parse(path: Path) -> ET.ElementTree:
	return ET.parse(path)


def info_nodes(repo_root: Path, relative_path: Path, tag_name: str):
	for node in parse(repo_root / relative_path).getroot().iter():
		if local_name(node.tag) == tag_name:
			yield node


def info_types(repo_root: Path, relative_path: Path, tag_name: str) -> set[str]:
	return {
		value
		for node in info_nodes(repo_root, relative_path, tag_name)
		for value in [child_text_by_local_name(node, "Type")]
		if value is not None
	}


def mapped_targets(repo_root: Path, relative_path: Path, info_tag: str, target_tag: str) -> tuple[dict[str, list[str]], list[str]]:
	by_target: dict[str, list[str]] = {}
	failures: list[str] = []
	seen_types: set[str] = set()
	for node in info_nodes(repo_root, relative_path, info_tag):
		info_type = child_text_by_local_name(node, "Type")
		target = child_text_by_local_name(node, target_tag)
		if not info_type:
			failures.append(f"{relative_path}: {info_tag} missing Type")
			continue
		if info_type in seen_types:
			failures.append(f"{relative_path}: duplicate {info_tag} Type {info_type}")
		seen_types.add(info_type)
		if not target:
			failures.append(f"{relative_path}: {info_type} missing {target_tag}")
			continue
		by_target.setdefault(target, []).append(info_type)
	return by_target, failures


def playable_civs_and_leaders(repo_root: Path) -> tuple[set[str], set[str]]:
	playable_civs: set[str] = set()
	leaders: set[str] = set()
	for node in info_nodes(repo_root, CIVILIZATION_INFOS, "CivilizationInfo"):
		civ_type = child_text_by_local_name(node, "Type")
		if not civ_type:
			continue
		is_playable = child_text_by_local_name(node, "bPlayable") == "1"
		is_ai_playable = child_text_by_local_name(node, "bAIPlayable") == "1"
		if not (is_playable or is_ai_playable):
			continue
		playable_civs.add(civ_type)
		for child in node.iter():
			if local_name(child.tag) == "LeaderName" and (child.text or "").strip():
				leaders.add((child.text or "").strip())
	return playable_civs, leaders


def check(repo_root: Path) -> list[str]:
	failures: list[str] = []
	civilization_types = info_types(repo_root, CIVILIZATION_INFOS, "CivilizationInfo")
	leader_types = info_types(repo_root, LEADER_INFOS, "LeaderHeadInfo")
	bonus_types = info_types(repo_root, BONUS_INFOS, "BonusInfo")
	playable_civs, playable_leaders = playable_civs_and_leaders(repo_root)

	tru_civs, mapping_failures = mapped_targets(repo_root, TRU_CIV_INFOS, "TruCivInfo", "CivilizationType")
	failures.extend(mapping_failures)
	tru_leaders, mapping_failures = mapped_targets(repo_root, TRU_LEADER_INFOS, "TruLeaderInfo", "LeaderType")
	failures.extend(mapping_failures)
	tru_bonuses, mapping_failures = mapped_targets(repo_root, TRU_BONUS_INFOS, "TruBonusInfo", "BonusType")
	failures.extend(mapping_failures)

	for target, rows in sorted(tru_civs.items()):
		if target not in civilization_types:
			failures.append(f"{TRU_CIV_INFOS}: {rows[0]} references missing civilization {target}")
		if len(rows) != 1:
			failures.append(f"{TRU_CIV_INFOS}: civilization {target} has {len(rows)} TruCivInfo rows: {', '.join(rows)}")
	for civ_type in sorted(playable_civs):
		if civ_type not in tru_civs:
			failures.append(f"{TRU_CIV_INFOS}: playable civilization {civ_type} has no TruCivInfo")

	for target, rows in sorted(tru_leaders.items()):
		if target not in leader_types:
			failures.append(f"{TRU_LEADER_INFOS}: {rows[0]} references missing leader {target}")
		if len(rows) != 1:
			failures.append(f"{TRU_LEADER_INFOS}: leader {target} has {len(rows)} TruLeaderInfo rows: {', '.join(rows)}")
	for leader_type in sorted(playable_leaders):
		if leader_type not in tru_leaders:
			failures.append(f"{TRU_LEADER_INFOS}: playable-civilization leader {leader_type} has no TruLeaderInfo")

	for target, rows in sorted(tru_bonuses.items()):
		if target not in bonus_types:
			failures.append(f"{TRU_BONUS_INFOS}: {rows[0]} references missing bonus {target}")
		if len(rows) != 1:
			failures.append(f"{TRU_BONUS_INFOS}: bonus {target} has {len(rows)} TruBonusInfo rows: {', '.join(rows)}")

	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check True Starts companion coverage and reference integrity.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL True Starts coverage")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS True Starts coverage")
	return 0


if __name__ == "__main__":
	sys.exit(main())

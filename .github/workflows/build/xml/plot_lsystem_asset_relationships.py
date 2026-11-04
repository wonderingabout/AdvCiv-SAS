#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: active PlotLSystem rules that constrain both an Improvement and a Bonus must use a relationship present in CIV4ImprovementInfos.xml.
# An ArtRef requiring an Improvement must also be reachable: a node reached only by improvement-constrained productions cannot place art for another improvement.

# <!-- custom: argparse/pathlib/sys drive the CLI and shared-helper path; ElementTree reads the PlotLSystem, BonusInfo and ImprovementInfo XML. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

# <!-- custom: Resolve repository/shared-helper paths from this subject subfolder after the workflow-tool reorganization. (ChatGPT-5.6-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


PLOT_LSYSTEM_REL_PATH = Path("Assets/XML/Buildings/CIV4PlotLSystem.xml")
BONUS_INFOS_REL_PATH = Path("Assets/XML/Terrain/CIV4BonusInfos.xml")
IMPROVEMENT_INFOS_REL_PATH = Path("Assets/XML/Terrain/CIV4ImprovementInfos.xml")
SPECIAL_BONUS_SELECTORS = {"BONUS_ALL", "NO_BONUS"}
SPECIAL_IMPROVEMENT_SELECTORS = {"IMPROVEMENT_ALL", "NO_IMPROVEMENT"}


def parse_xml(path: Path) -> ET.ElementTree:
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	return ET.parse(path)


def read_types(repo_root: Path, rel_path: Path, info_tag: str) -> set[str]:
	tree = parse_xml(repo_root / rel_path)
	return {
		info_type
		for node in tree.getroot().iter()
		if local_name(node.tag) == info_tag
		for info_type in [child_text_by_local_name(node, "Type")]
		if info_type is not None
	}


def read_improvement_bonus_relationships(repo_root: Path) -> dict[str, set[str]]:
	tree = parse_xml(repo_root / IMPROVEMENT_INFOS_REL_PATH)
	relationships: dict[str, set[str]] = {}

	for node in tree.getroot().iter():
		if local_name(node.tag) != "ImprovementInfo":
			continue
		improvement_type = child_text_by_local_name(node, "Type")
		if improvement_type is None:
			continue
		bonuses: set[str] = set()
		for child in node.iter():
			if local_name(child.tag) != "BonusTypeStruct":
				continue
			bonus_type = child_text_by_local_name(child, "BonusType")
			if bonus_type:
				bonuses.add(bonus_type)
		relationships[improvement_type] = bonuses

	return relationships


def selector_values(text: str | None, prefix: str, special_values: set[str]) -> set[str]:
	values: set[str] = set()
	for raw_value in (text or "").split(","):
		value = raw_value.strip()
		if not value or value.startswith("!"):
			continue
		if value in special_values:
			continue
		if value.startswith(prefix):
			values.add(value)
	return values


def check(repo_root: Path) -> list[str]:
	active_bonuses = read_types(repo_root, BONUS_INFOS_REL_PATH, "BonusInfo")
	active_improvements = read_types(repo_root, IMPROVEMENT_INFOS_REL_PATH, "ImprovementInfo")
	relationships = read_improvement_bonus_relationships(repo_root)
	tree = parse_xml(repo_root / PLOT_LSYSTEM_REL_PATH)
	failures: list[str] = []

	for index, production in enumerate((node for node in tree.getroot().iter() if local_name(node.tag) == "LProduction"), start=1):
		bonus_values: set[str] = set()
		improvement_values: set[str] = set()
		for child in production:
			if local_name(child.tag) != "Attribute":
				continue
			attribute_class = child.attrib.get("Class")
			if attribute_class == "Bonus":
				bonus_values.update(selector_values(child.text, "BONUS_", SPECIAL_BONUS_SELECTORS))
			elif attribute_class == "Improvement":
				improvement_values.update(selector_values(child.text, "IMPROVEMENT_", SPECIAL_IMPROVEMENT_SELECTORS))

		# <!-- custom: CIV4PlotLSystem.xml retains some unused BtS graphical definitions (for example Cotton/Olives/Tobacco).
		# Only active SAS BonusInfo/ImprovementInfo pairs are gameplay relationships, so ignore selectors for assets absent from the current XML set. (ChatGPT-5.6-Sol) -->
		active_rule_bonuses = sorted(bonus_values & active_bonuses)
		active_rule_improvements = sorted(improvement_values & active_improvements)
		for improvement_type in active_rule_improvements:
			for bonus_type in active_rule_bonuses:
				if bonus_type not in relationships.get(improvement_type, set()):
					name = production.attrib.get("Name") or production.attrib.get("From") or f"LProduction #{index}"
					failures.append(f"{PLOT_LSYSTEM_REL_PATH.as_posix()}: {name}: {improvement_type} + {bonus_type} is not a current ImprovementInfos bonus relationship")

	failures.extend(check_unreachable_art(tree))
	return failures


# <!-- custom: Fixing the Grapes productions from Farm to Plantation left BLeaf_4x3, reached only by them, with a goal ArtRef still requiring Farm, so it could never be placed; the pair check above cannot see this.
# A node's improvements are the union of its incoming productions' positive selectors; any unconstrained or IMPROVEMENT_ALL production makes the node unrestricted.
# BtS's own file has no such ArtRef. See KI#1074. (Claude code Opus 5.5) -->
def check_unreachable_art(tree: ET.ElementTree) -> list[str]:
	incoming: dict[str, set[str] | None] = {}
	for production in (node for node in tree.getroot().iter() if local_name(node.tag) == "LProduction"):
		improvements: set[str] | None = None
		for child in production:
			if local_name(child.tag) == "Attribute" and child.attrib.get("Class") == "Improvement" and "IMPROVEMENT_ALL" not in (child.text or ""):
				improvements = selector_values(child.text, "IMPROVEMENT_", set()) | ({"NO_IMPROVEMENT"} if "NO_IMPROVEMENT" in (child.text or "") else set())
		for target in (child.attrib.get("Name") for child in production if local_name(child.tag) == "To"):
			if improvements is None or incoming.get(target, set()) is None:
				incoming[target] = None
			else:
				incoming[target] = incoming.get(target, set()) | improvements
	failures: list[str] = []
	for node in (node for node in tree.getroot().iter() if local_name(node.tag) == "LNode"):
		reached = incoming.get(node.attrib.get("Name"))
		if reached is None:
			continue
		for art in (child for child in node if local_name(child.tag) == "ArtRef"):
			for attribute in (child for child in art if local_name(child.tag) == "Attribute" and child.attrib.get("Class") == "Improvement"):
				required = selector_values(attribute.text, "IMPROVEMENT_", {"IMPROVEMENT_ALL", "NO_IMPROVEMENT"})
				if required and "IMPROVEMENT_ALL" not in (attribute.text or "") and not required & reached:
					failures.append(f"{PLOT_LSYSTEM_REL_PATH.as_posix()}: {node.attrib.get('Name')}: ArtRef {art.attrib.get('Name')} requires {', '.join(sorted(required))}, but only productions for {', '.join(sorted(reached))} reach this node")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check active PlotLSystem Bonus/Improvement rule pairs against CIV4ImprovementInfos.xml.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	try:
		failures = check(args.repo_root)
	except (RuntimeError, ET.ParseError) as exc:
		print("FAIL PlotLSystem asset relationships")
		print(f"  - {exc}")
		return 1

	if failures:
		print("FAIL PlotLSystem asset relationships")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS PlotLSystem asset relationships")
	return 0


if __name__ == "__main__":
	sys.exit(main())

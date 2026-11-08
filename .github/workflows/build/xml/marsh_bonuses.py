#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Marsh lies on flat Grassland, and Civ4 places a bonus under a feature only when the bonus lists that feature, so every new Grassland bonus needs a Marsh decision that is easy to forget.
# Fail when a flat-Grassland bonus neither allows Marsh nor has a recorded reason below, or when a recorded reason no longer applies.
# Only Marsh is covered: the inherited Forest, Jungle and other feature bonus lists were already settled by BtS and AdvCiv, while Marsh is new and sits on Grassland, the terrain with the most bonuses. (Claude code Opus 5.5) -->

# <!-- custom: argparse exposes the repository option, pathlib/sys locate the shared XML helpers, and ElementTree reads the bonus XML. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the shared repository-root and namespace-agnostic XML readers from lib/xml_defines.py. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


BONUS_INFOS_REL_PATH = Path("Assets/XML/Terrain/CIV4BonusInfos.xml")
MARSH = "FEATURE_MARSH"
GRASS = "TERRAIN_GRASS"

# <!-- custom: Flat-Grassland bonuses deliberately kept off Marsh.
# Marsh bonuses are wetland bonuses that still fit the reclaimed Grassland after draining. (Claude code Opus 5.5) -->
EXCLUDED = {
	"BONUS_CORN": "maize is a dryland crop needing well-drained soil",
	"BONUS_HORSE": "horses avoid soft wet ground, like the wheeled units Marsh blocks",
	"BONUS_COPPER": "a mined mineral, not a wetland bonus",
	"BONUS_IRON": "a mined mineral, not a wetland bonus; bog iron could justify it later",
	"BONUS_URANIUM": "a mined mineral, not a wetland bonus",
}


def flagged(node, list_tag: str, type_tag: str, flag_tag: str) -> set[str]:
	found = set()
	for child in node:
		if local_name(child.tag) != list_tag:
			continue
		for entry in child:
			if child_text_by_local_name(entry, flag_tag) == "1":
				found.add(child_text_by_local_name(entry, type_tag))
	return found


def read_bonuses(repo_root: Path) -> dict[str, dict]:
	path = repo_root / BONUS_INFOS_REL_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	bonuses = {}
	for node in ET.parse(path).getroot().iter():
		if local_name(node.tag) != "BonusInfo":
			continue
		bonuses[child_text_by_local_name(node, "Type")] = {
			"flatGrass": child_text_by_local_name(node, "bFlatlands") == "1" and GRASS in flagged(node, "TerrainBooleans", "TerrainType", "bTerrain"),
			"marsh": MARSH in flagged(node, "FeatureBooleans", "FeatureType", "bFeature"),
			"featureGrass": GRASS in flagged(node, "FeatureTerrainBooleans", "TerrainType", "bFeatureTerrain"),
		}
	return bonuses


def check_marsh_bonuses(bonuses: dict[str, dict], excluded: dict[str, str]) -> list[str]:
	failures = []
	for bonus_type, info in sorted(bonuses.items()):
		if info["marsh"] and not info["featureGrass"]:
			failures.append(f"{bonus_type}: allows {MARSH} but not {GRASS} in FeatureTerrainBooleans, so it can never be placed on Marsh")
		if info["marsh"] and bonus_type in excluded:
			failures.append(f"{bonus_type}: allows {MARSH} but is still recorded as excluded ({excluded[bonus_type]}); remove the exclusion")
		if info["flatGrass"] and not info["marsh"] and bonus_type not in excluded:
			failures.append(f"{bonus_type}: can appear on flat Grassland but has no {MARSH} decision; allow it in FeatureBooleans or record why not in EXCLUDED")
	for bonus_type in sorted(excluded):
		if bonus_type not in bonuses:
			failures.append(f"{bonus_type}: recorded as excluded but no longer exists")
		elif not bonuses[bonus_type]["flatGrass"]:
			failures.append(f"{bonus_type}: recorded as excluded but can no longer appear on flat Grassland; remove the exclusion")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that every flat-Grassland bonus has a recorded Marsh decision.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing this script")
	args = parser.parse_args()

	try:
		failures = check_marsh_bonuses(read_bonuses(args.repo_root), EXCLUDED)
	except RuntimeError as exc:
		failures = [str(exc)]

	if failures:
		print("FAIL Marsh bonus decisions")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS Marsh bonus decisions")
	return 0


if __name__ == "__main__":
	sys.exit(main())

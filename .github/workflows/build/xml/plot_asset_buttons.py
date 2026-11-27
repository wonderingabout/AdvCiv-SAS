#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The new Peat Works first reused Quarry's button, and Drain Marsh at first reused the Marsh feature's, so the Sevopedia showed two different assets with one picture; both were caught only by eye.
# Fail when a feature, bonus, improvement, route or build shares its button with another of these, except an improvement or route with the builds that create it, as BtS does. (Claude code Opus 5.5) -->

# <!-- custom: argparse exposes the repository option, collections groups assets by button, pathlib/sys locate the shared XML helpers, and ElementTree reads the XML. (Claude code Opus 5.5) -->
from collections import defaultdict
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the shared repository-root and namespace-agnostic XML readers from lib/xml_defines.py. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


# <!-- custom: Each source is (info file, info tag, art file, art tag); no art file means the info holds its own Button, as routes and builds do. (Claude code Opus 5.5) -->
SOURCES = (
	("Assets/XML/Terrain/CIV4FeatureInfos.xml", "FeatureInfo", "Assets/XML/Art/CIV4ArtDefines_Feature.xml", "FeatureArtInfo"),
	("Assets/XML/Terrain/CIV4BonusInfos.xml", "BonusInfo", "Assets/XML/Art/CIV4ArtDefines_Bonus.xml", "BonusArtInfo"),
	("Assets/XML/Terrain/CIV4ImprovementInfos.xml", "ImprovementInfo", "Assets/XML/Art/CIV4ArtDefines_Improvement.xml", "ImprovementArtInfo"),
	("Assets/XML/Misc/CIV4RouteInfos.xml", "RouteInfo", None, None),
	("Assets/XML/Units/CIV4BuildInfos.xml", "BuildInfo", None, None),
)
# <!-- custom: Inherited BtS graphical-only improvements that both use the atlas's empty -1,-1 cell; the game never shows them as choices. (Claude code Opus 5.5) -->
SHARED_ALLOWED = {frozenset(("IMPROVEMENT_LAND_WORKED", "IMPROVEMENT_WATER_WORKED"))}


def nodes(repo_root: Path, rel_path: str, tag: str):
	path = repo_root / rel_path
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	return [node for node in ET.parse(path).getroot().iter() if local_name(node.tag) == tag]


def read_assets(repo_root: Path) -> tuple[dict[str, str], dict[str, str]]:
	# <!-- custom: Returns each asset's button, and each build's improvement or route, so an improvement may share its button only with the builds that create it. (Claude code Opus 5.5) -->
	buttons, creates = {}, {}
	for info_path, info_tag, art_path, art_tag in SOURCES:
		art = {}
		if art_path:
			art = {child_text_by_local_name(node, "Type"): child_text_by_local_name(node, "Button") for node in nodes(repo_root, art_path, art_tag)}
		for node in nodes(repo_root, info_path, info_tag):
			asset = child_text_by_local_name(node, "Type")
			buttons[asset] = art.get(child_text_by_local_name(node, "ArtDefineTag"), "") if art_path else child_text_by_local_name(node, "Button")
			if info_tag == "BuildInfo":
				for field in ("ImprovementType", "RouteType"):
					target = child_text_by_local_name(node, field)
					if target and target != "NONE":
						creates[asset] = target
	return buttons, creates


def check_plot_asset_buttons(buttons: dict[str, str], creates: dict[str, str]) -> list[str]:
	users = defaultdict(list)
	for asset, button in buttons.items():
		if button:
			users[button.strip().lower()].append(asset)
	failures = []
	for button, assets in sorted(users.items()):
		if len(assets) < 2 or frozenset(assets) in SHARED_ALLOWED:
			continue
		products = set(asset for asset in assets if not asset.startswith("BUILD_"))
		if len(products) == 1 and all(creates.get(asset) in products for asset in assets if asset.startswith("BUILD_")):
			continue
		failures.append(f"{', '.join(sorted(assets))} share the button {button}; give each its own, unless only an improvement or route and the builds that create it share one")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that plot assets do not borrow each other's buttons.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing this script")
	args = parser.parse_args()

	try:
		failures = check_plot_asset_buttons(*read_assets(args.repo_root))
	except RuntimeError as exc:
		failures = [str(exc)]

	if failures:
		print("FAIL Plot asset buttons")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS Plot asset buttons")
	return 0


if __name__ == "__main__":
	sys.exit(main())

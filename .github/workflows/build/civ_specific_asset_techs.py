#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Build check: civilization-specific assets should not be pushed to a later
# starting tech column or an earlier obsolete tech column than the generic asset
# they replace.
#
# <!-- custom: Same-column tech variation is allowed. For example, a unique
# building or unit using a parallel tech at the same iGridX can be useful flavor.
# Requiring a later iGridX prereq tech is likely to be clunky because the
# replacement can arrive after the generic asset slot it is meant to replace.
# Obsoleting earlier is likewise suspicious because the civ-specific asset can
# disappear before the generic asset would. (ChatGPT-5.5) -->

from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


TECH_INFOS_REL_PATH = Path("Assets/XML/Technologies/CIV4TechInfos.xml")

NONE_VALUES = {
	"",
	"NONE",
	"NO_TECH",
	"TECH_NONE",
	"NO_BUILDING",
	"NO_UNIT",
}

ASSET_GROUPS = (
	{
		"name": "building",
		"asset_infos_path": Path("Assets/XML/Buildings/CIV4BuildingInfos.xml"),
		"class_infos_path": Path("Assets/XML/Buildings/CIV4BuildingClassInfos.xml"),
		"asset_info_tag": "BuildingInfo",
		"class_info_tag": "BuildingClassInfo",
		"asset_type_tag": "Type",
		"asset_class_tag": "BuildingClass",
		"default_asset_tag": "DefaultBuilding",
	},
	{
		"name": "unit",
		"asset_infos_path": Path("Assets/XML/Units/CIV4UnitInfos.xml"),
		"class_infos_path": Path("Assets/XML/Units/CIV4UnitClassInfos.xml"),
		"asset_info_tag": "UnitInfo",
		"class_info_tag": "UnitClassInfo",
		"asset_type_tag": "Type",
		"asset_class_tag": "Class",
		"default_asset_tag": "DefaultUnit",
	},
)

# Keep empty by default. Add only narrow, documented exceptions if a later-prereq
# or earlier-obsolete replacement is truly intentional.
ALLOWED_CIV_SPECIFIC_ASSET_TECH_EXCEPTIONS: dict[str, str] = {
}


def normalize_none(value: str | None) -> str:
	if value is None:
		return "NONE"
	value = value.strip()
	if value in NONE_VALUES:
		return "NONE"
	return value


def parse_xml(path: Path) -> ET.ElementTree:
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	return ET.parse(path)


def read_class_defaults(repo_root: Path, group: dict[str, object]) -> dict[str, str]:
	path = repo_root / group["class_infos_path"]
	tree = parse_xml(path)
	default_by_class: dict[str, str] = {}

	for node in tree.getroot().iter():
		if local_name(node.tag) != group["class_info_tag"]:
			continue

		asset_class = child_text_by_local_name(node, "Type")
		default_asset = normalize_none(child_text_by_local_name(node, group["default_asset_tag"]))
		if asset_class is None:
			continue
		default_by_class[asset_class] = default_asset

	return default_by_class


def read_assets(repo_root: Path, group: dict[str, object]) -> dict[str, dict[str, str]]:
	path = repo_root / group["asset_infos_path"]
	tree = parse_xml(path)
	assets: dict[str, dict[str, str]] = {}

	for node in tree.getroot().iter():
		if local_name(node.tag) != group["asset_info_tag"]:
			continue

		asset_type = child_text_by_local_name(node, group["asset_type_tag"])
		if asset_type is None:
			continue

		asset_class = child_text_by_local_name(node, group["asset_class_tag"])
		prereq_tech = normalize_none(child_text_by_local_name(node, "PrereqTech"))
		obsolete_tech = normalize_none(child_text_by_local_name(node, "ObsoleteTech"))

		assets[asset_type] = {
			"class": asset_class or "NONE",
			"prereq_tech": prereq_tech,
			"obsolete_tech": obsolete_tech,
		}

	return assets


def read_tech_grid_positions(repo_root: Path) -> dict[str, tuple[int, int]]:
	path = repo_root / TECH_INFOS_REL_PATH
	tree = parse_xml(path)
	tech_grid_by_type: dict[str, tuple[int, int]] = {}

	for node in tree.getroot().iter():
		if local_name(node.tag) != "TechInfo":
			continue

		tech_type = child_text_by_local_name(node, "Type")
		if tech_type is None:
			continue

		grid_x_text = child_text_by_local_name(node, "iGridX")
		grid_y_text = child_text_by_local_name(node, "iGridY")
		try:
			grid_x = int(grid_x_text or "-1")
			grid_y = int(grid_y_text or "-1")
		except ValueError as exc:
			raise RuntimeError(f"{TECH_INFOS_REL_PATH}: {tech_type} has invalid iGridX/iGridY: {grid_x_text!r}/{grid_y_text!r}") from exc

		tech_grid_by_type[tech_type] = (grid_x, grid_y)

	return tech_grid_by_type


def tech_label(tech_type: str, tech_grid_by_type: dict[str, tuple[int, int]]) -> str:
	if tech_type == "NONE":
		return "NONE"
	if tech_type not in tech_grid_by_type:
		return f"{tech_type} (missing grid)"
	grid_x, grid_y = tech_grid_by_type[tech_type]
	return f"{tech_type} (GridX={grid_x}, GridY={grid_y})"


def check_prereq_tech(
	asset_type: str,
	asset_class: str,
	group_name: str,
	default_asset: str,
	replacement_tech: str,
	default_tech: str,
	tech_grid_by_type: dict[str, tuple[int, int]],
) -> list[str]:
	failures: list[str] = []

	if replacement_tech == "NONE":
		return failures

	if default_tech == "NONE":
		failures.append(
			f"{asset_type}: {group_name} class {asset_class} replacement requires {tech_label(replacement_tech, tech_grid_by_type)}, "
			f"but default {default_asset} has no PrereqTech"
		)
		return failures

	if replacement_tech not in tech_grid_by_type:
		failures.append(f"{asset_type}: replacement PrereqTech {replacement_tech} is missing from TechInfos")
		return failures
	if default_tech not in tech_grid_by_type:
		failures.append(f"{asset_type}: default {default_asset} PrereqTech {default_tech} is missing from TechInfos")
		return failures

	replacement_grid_x, replacement_grid_y = tech_grid_by_type[replacement_tech]
	default_grid_x, default_grid_y = tech_grid_by_type[default_tech]

	if replacement_grid_x > default_grid_x:
		failures.append(
			f"{asset_type}: {group_name} class {asset_class} replacement uses later PrereqTech column than default {default_asset}: "
			f"{replacement_tech} (GridX={replacement_grid_x}, GridY={replacement_grid_y}) after "
			f"{default_tech} (GridX={default_grid_x}, GridY={default_grid_y})"
		)

	return failures


def check_obsolete_tech(
	asset_type: str,
	asset_class: str,
	group_name: str,
	default_asset: str,
	replacement_tech: str,
	default_tech: str,
	tech_grid_by_type: dict[str, tuple[int, int]],
) -> list[str]:
	failures: list[str] = []

	if replacement_tech == "NONE":
		return failures

	if default_tech == "NONE":
		failures.append(
			f"{asset_type}: {group_name} class {asset_class} replacement obsoletes at {tech_label(replacement_tech, tech_grid_by_type)}, "
			f"but default {default_asset} has no ObsoleteTech"
		)
		return failures

	if replacement_tech not in tech_grid_by_type:
		failures.append(f"{asset_type}: replacement ObsoleteTech {replacement_tech} is missing from TechInfos")
		return failures
	if default_tech not in tech_grid_by_type:
		failures.append(f"{asset_type}: default {default_asset} ObsoleteTech {default_tech} is missing from TechInfos")
		return failures

	replacement_grid_x, replacement_grid_y = tech_grid_by_type[replacement_tech]
	default_grid_x, default_grid_y = tech_grid_by_type[default_tech]

	if replacement_grid_x < default_grid_x:
		failures.append(
			f"{asset_type}: {group_name} class {asset_class} replacement uses earlier ObsoleteTech column than default {default_asset}: "
			f"{replacement_tech} (GridX={replacement_grid_x}, GridY={replacement_grid_y}) before "
			f"{default_tech} (GridX={default_grid_x}, GridY={default_grid_y})"
		)

	return failures


def check_asset_group(repo_root: Path, group: dict[str, object], tech_grid_by_type: dict[str, tuple[int, int]]) -> list[str]:
	default_by_class = read_class_defaults(repo_root, group)
	assets = read_assets(repo_root, group)
	failures: list[str] = []
	group_name = group["name"]

	for asset_type in sorted(assets):
		asset = assets[asset_type]
		asset_class = asset["class"]
		if asset_class == "NONE":
			continue

		default_asset = default_by_class.get(asset_class, "NONE")
		if default_asset == "NONE":
			continue
		if asset_type == default_asset:
			continue
		if default_asset not in assets:
			failures.append(f"{asset_type}: {group_name} class {asset_class} default asset {default_asset} is missing from asset infos")
			continue

		if asset_type in ALLOWED_CIV_SPECIFIC_ASSET_TECH_EXCEPTIONS:
			continue

		default = assets[default_asset]

		failures.extend(
			check_prereq_tech(
				asset_type,
				asset_class,
				group_name,
				default_asset,
				asset["prereq_tech"],
				default["prereq_tech"],
				tech_grid_by_type,
			)
		)

		failures.extend(
			check_obsolete_tech(
				asset_type,
				asset_class,
				group_name,
				default_asset,
				asset["obsolete_tech"],
				default["obsolete_tech"],
				tech_grid_by_type,
			)
		)

	return failures


def check_asset_techs(repo_root: Path) -> list[str]:
	tech_grid_by_type = read_tech_grid_positions(repo_root)
	failures: list[str] = []

	for group in ASSET_GROUPS:
		failures.extend(check_asset_group(repo_root, group, tech_grid_by_type))

	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check civilization-specific building/unit asset techs are not later/earlier than their generic asset's tech columns.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	try:
		failures = check_asset_techs(args.repo_root)
	except RuntimeError as exc:
		print("FAIL civ-specific asset tech timing")
		print(f"  - {exc}")
		return 1

	if failures:
		print("FAIL civ-specific asset tech timing")
		for failure in failures:
			print(f"  - {failure}")
		print("  - Same-GridX parallel tech variation is allowed.")
		print("  - PrereqTech fails only when a replacement starts later than its generic asset.")
		print("  - ObsoleteTech fails only when a replacement obsoletes earlier than its generic asset.")
		return 1

	print("PASS civ-specific asset tech timing")
	return 0


if __name__ == "__main__":
	sys.exit(main())

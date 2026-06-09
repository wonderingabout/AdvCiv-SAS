#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Build check: SAS_MAGIC_WORLDSIZE_* constants must match CIV4WorldInfo.xml order.

from pathlib import Path
import argparse
import ast
import re
import sys
import xml.etree.ElementTree as ET


MAGIC_NUMBERS_RELATIVE_PATH = Path("Assets/Python/SASMagicNumbers.py")
WORLD_INFO_RELATIVE_PATH = Path("Assets/XML/GameInfo/CIV4WorldInfo.xml")
WORLDSIZE_PREFIX = "SAS_MAGIC_WORLDSIZE_"
LARGEST_CONSTANT = "SAS_MAGIC_WORLDSIZE_LARGEST"


def get_default_repo_root() -> Path:
	return Path(__file__).resolve().parents[3]


def local_name(tag: str) -> str:
	return tag.rsplit("}", 1)[-1]


def child_text_by_local_name(node: ET.Element, child_name: str) -> str | None:
	for child in list(node):
		if local_name(child.tag) == child_name:
			return (child.text or "").strip()
	return None


def read_worldinfo_types(repo_root: Path) -> list[str]:
	path = repo_root / WORLD_INFO_RELATIVE_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")

	tree = ET.parse(path)
	world_types: list[str] = []

	for node in tree.getroot().iter():
		if local_name(node.tag) != "WorldInfo":
			continue

		type_text = child_text_by_local_name(node, "Type")
		if not type_text:
			world_types.append("<missing Type>")
			continue
		world_types.append(type_text)

	return world_types


def read_worldsize_magic_constants(repo_root: Path) -> tuple[dict[str, int], dict[str, str]]:
	path = repo_root / MAGIC_NUMBERS_RELATIVE_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")

	tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
	int_constants: dict[str, int] = {}
	alias_constants: dict[str, str] = {}

	for node in tree.body:
		if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
			continue

		name = node.targets[0].id
		if not name.startswith(WORLDSIZE_PREFIX):
			continue

		if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
			int_constants[name] = node.value.value
		elif isinstance(node.value, ast.Name):
			alias_constants[name] = node.value.id
		else:
			raise RuntimeError(f"{MAGIC_NUMBERS_RELATIVE_PATH}: unsupported world-size constant assignment for {name}")

	return int_constants, alias_constants


def expected_magic_name(world_type: str) -> str:
	if not re.fullmatch(r"WORLDSIZE_[A-Z0-9_]+", world_type):
		return f"<invalid world type: {world_type}>"
	return "SAS_MAGIC_" + world_type


def check_worldsizes(repo_root: Path) -> list[str]:
	failures: list[str] = []

	world_types = read_worldinfo_types(repo_root)
	expected_by_name = {expected_magic_name(world_type): index for index, world_type in enumerate(world_types)}
	int_constants, alias_constants = read_worldsize_magic_constants(repo_root)

	if len(set(world_types)) != len(world_types):
		seen: set[str] = set()
		duplicates: list[str] = []
		for world_type in world_types:
			if world_type in seen and world_type not in duplicates:
				duplicates.append(world_type)
			seen.add(world_type)
		failures.append(f"{WORLD_INFO_RELATIVE_PATH}: duplicate world-size Type entries: {', '.join(duplicates)}")

	for name in sorted(expected_by_name):
		expected = expected_by_name[name]
		if name not in int_constants:
			failures.append(f"{MAGIC_NUMBERS_RELATIVE_PATH}: missing {name} = {expected}")
			continue

		actual = int_constants[name]
		if actual != expected:
			failures.append(f"{MAGIC_NUMBERS_RELATIVE_PATH}: {name} expected {expected} from XML order, found {actual}")

	extra_names = sorted(name for name in int_constants if name not in expected_by_name)
	for name in extra_names:
		failures.append(f"{MAGIC_NUMBERS_RELATIVE_PATH}: extra numeric world-size constant {name} = {int_constants[name]} not present in {WORLD_INFO_RELATIVE_PATH}")

	if not world_types:
		failures.append(f"{WORLD_INFO_RELATIVE_PATH}: no WorldInfo entries found")
	else:
		expected_largest_target = expected_magic_name(world_types[-1])
		actual_largest_target = alias_constants.get(LARGEST_CONSTANT)
		if actual_largest_target != expected_largest_target:
			failures.append(f"{MAGIC_NUMBERS_RELATIVE_PATH}: {LARGEST_CONSTANT} should alias {expected_largest_target}, found {actual_largest_target or '<missing>'}")

	for name in sorted(alias_constants):
		if name != LARGEST_CONSTANT:
			failures.append(f"{MAGIC_NUMBERS_RELATIVE_PATH}: unexpected world-size alias {name} = {alias_constants[name]}")

	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that AdvCiv-SAS world-size magic constants match CIV4WorldInfo.xml order.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	failures = check_worldsizes(args.repo_root)

	if failures:
		print("FAIL world-size magic constants")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS world-size magic constants")
	return 0


if __name__ == "__main__":
	sys.exit(main())

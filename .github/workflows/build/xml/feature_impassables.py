#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Adding Marsh meant adding it to every unit that already blocked Jungle and Forest, and the Cannon line had been left without either.
# Fail when units block different feature sets, so a new impassable feature or a new wheeled unit cannot be applied to only some of them. (Claude code Opus 5.5) -->

# <!-- custom: argparse exposes the repository option, collections counts the feature sets, pathlib/sys locate the shared XML helpers, and ElementTree reads the unit XML. (Claude code Opus 5.5) -->
from collections import Counter
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the shared repository-root and namespace-agnostic XML readers from lib/xml_defines.py. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


UNIT_INFOS_REL_PATH = Path("Assets/XML/Units/CIV4UnitInfos.xml")


def read_impassables(repo_root: Path) -> dict[str, frozenset[str]]:
	path = repo_root / UNIT_INFOS_REL_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	units: dict[str, frozenset[str]] = {}
	for node in ET.parse(path).getroot().iter():
		if local_name(node.tag) != "UnitInfo":
			continue
		features = set()
		for entry in node.iter():
			if local_name(entry.tag) == "FeatureImpassable" and child_text_by_local_name(entry, "bFeatureImpassable") == "1":
				features.add(child_text_by_local_name(entry, "FeatureType"))
		if features:
			units[child_text_by_local_name(node, "Type")] = frozenset(features)
	return units


def check_impassables(units: dict[str, frozenset[str]]) -> list[str]:
	if not units:
		return []
	shared, _count = Counter(units.values()).most_common(1)[0]
	failures = []
	for unit_type, features in sorted(units.items()):
		if features != shared:
			missing = ", ".join(sorted(shared - features)) or "-"
			extra = ", ".join(sorted(features - shared)) or "-"
			failures.append(f"{unit_type}: blocks {', '.join(sorted(features))}; missing {missing}, extra {extra} compared with the shared set {', '.join(sorted(shared))}")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that every unit with FeatureImpassables blocks the same features.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing this script")
	args = parser.parse_args()

	try:
		failures = check_impassables(read_impassables(args.repo_root))
	except RuntimeError as exc:
		failures = [str(exc)]

	if failures:
		print("FAIL consistent feature impassables")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS consistent feature impassables")
	return 0


if __name__ == "__main__":
	sys.exit(main())

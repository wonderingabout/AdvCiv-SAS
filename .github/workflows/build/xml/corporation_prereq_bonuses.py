#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Peat was first added to Mining Inc as its 6th input.
# The game counted all 6, because AdvCiv stores the list in a vector, but Python reads at most NUM_CORPORATION_PREREQ_BONUSES (5 in BtS's GlobalDefines.xml), so the Sevopedia showed only 5 and debug builds assert while loading.
# Fail when a corporation lists more inputs than that limit, or the same input twice. See KI#1079. (Claude code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: argparse exposes the repository option, pathlib/sys locate the shared XML helpers, and ElementTree reads the corporation and define XML. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the shared repository-root and namespace-agnostic XML readers from lib/xml_defines.py. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


CORPORATION_INFOS_REL_PATH = Path("Assets/XML/GameInfo/CIV4CorporationInfo.xml")
SAS_DEFINES_REL_PATH = Path("Assets/XML/GlobalDefines_advciv_sas.xml")
LIMIT_DEFINE = "NUM_CORPORATION_PREREQ_BONUSES"
# <!-- custom: BtS's own GlobalDefines.xml is outside the repository, so its value is recorded here; a SAS override of the define replaces it. (Claude code Opus 5.5) -->
BTS_LIMIT = 5


def read_limit(repo_root: Path) -> int:
	path = repo_root / SAS_DEFINES_REL_PATH
	if path.exists():
		for node in ET.parse(path).getroot().iter():
			if local_name(node.tag) == "Define" and child_text_by_local_name(node, "DefineName") == LIMIT_DEFINE:
				return int(child_text_by_local_name(node, "iDefineIntVal"))
	return BTS_LIMIT


def read_corporations(repo_root: Path) -> dict[str, list[str]]:
	path = repo_root / CORPORATION_INFOS_REL_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	corporations = {}
	for node in ET.parse(path).getroot().iter():
		if local_name(node.tag) != "CorporationInfo":
			continue
		inputs = []
		for child in node:
			if local_name(child.tag) == "PrereqBonuses":
				inputs = [(entry.text or "").strip() for entry in child if local_name(entry.tag) == "BonusType"]
		corporations[child_text_by_local_name(node, "Type")] = inputs
	return corporations


def check_corporation_inputs(corporations: dict[str, list[str]], limit: int) -> list[str]:
	failures = []
	for corporation, inputs in sorted(corporations.items()):
		if len(inputs) > limit:
			failures.append(f"{corporation}: {len(inputs)} PrereqBonuses ({', '.join(inputs)}) exceed {LIMIT_DEFINE} = {limit}; Python and the Sevopedia would show only the first {limit}")
		duplicates = sorted(set(bonus for bonus in inputs if inputs.count(bonus) > 1))
		if duplicates:
			failures.append(f"{corporation}: lists {', '.join(duplicates)} more than once in PrereqBonuses")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that every corporation's inputs fit NUM_CORPORATION_PREREQ_BONUSES.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing this script")
	args = parser.parse_args()

	try:
		failures = check_corporation_inputs(read_corporations(args.repo_root), read_limit(args.repo_root))
	except RuntimeError as exc:
		failures = [str(exc)]

	if failures:
		print("FAIL Corporation input limit")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS Corporation input limit")
	return 0


if __name__ == "__main__":
	sys.exit(main())

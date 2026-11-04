#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: XML lists whose file order players see follow the alphabetical order of their shown English names.
# Currently checks leaders in CIV4LeaderHeadInfos.xml.

# <!-- custom: argparse/pathlib/re/sys drive the CLI and XML scan; the sibling inherited-text module supplies GameText parsing and the committed inherited names. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys

# <!-- custom: Shared repo-root resolution, as in the sibling XML checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root
from xml_sas_text_inherited import NAMES, TEXT_DIR, display_text, read_names, text_entries


# <!-- custom: The Custom Game leader list follows this file's order, not the names: a test with LEADER_CHINESE_LEADER moved showed Mao Zedong between Lincoln and Louis XIV.
# The order must therefore follow the shown name, which can differ from the Type (Mao Zedong is LEADER_CHINESE_LEADER, Roosevelt is LEADER_FRANKLIN_ROOSEVELT). (Claude code Opus 5.5) -->
LEADER_INFOS = "Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml"
NOT_IN_LIST = {"LEADER_BARBARIAN", "LEADER_DEFAULTS"}
LEADER_RE = re.compile(r"<Type>\s*(LEADER_\w+)\s*</Type>\s*<Description>\s*(\w+)\s*</Description>")
# <!-- custom: Civilizations are not checked yet.
# 2026-11-04 screenshots showed Custom Game lists their short names in CIV4CivilizationInfos.xml order ("The USA" first, before "Arabia"), while Play Now sorts full names itself ("United States of America" near the end); the current file is not in short-name order.
# True Starts is not checked: CIV4TruLeaderInfos.xml is looked up by <LeaderType> and its order is not shown in game.
# It keeps base AdvCiv's TRU_RAMESSES before TRU_RAGNAR, the reverse of the leader file. (Claude code Opus 5.5) -->


def mod_names(repo_root: Path) -> dict[str, str]:
	names = {}
	for path in sorted((repo_root / TEXT_DIR).glob("*.xml")):
		for tag, english, _line in text_entries(path.read_bytes()):
			names.setdefault(tag, display_text(english))
	return names


def check(repo_root: Path) -> list[str]:
	names = read_names(NAMES)
	names.update(mod_names(repo_root))
	data = (repo_root / LEADER_INFOS).read_text(encoding="utf-8", errors="replace")
	leaders = []
	failures = []
	for match in LEADER_RE.finditer(data):
		leader, key = match.groups()
		if leader in NOT_IN_LIST:
			continue
		if key not in names:
			failures.append(f"{LEADER_INFOS}: {leader} uses {key}, but neither mod GameText nor the inherited names list defines it; regenerate the list with xml_sas_text_inherited.py --write")
			continue
		leaders.append((names[key], leader, data.count("\n", 0, match.start()) + 1))
	for previous, current in zip(leaders, leaders[1:]):
		if previous[0].casefold() > current[0].casefold():
			failures.append(f"{LEADER_INFOS}:{current[2]}: {current[1]} (\"{current[0]}\") is listed after {previous[1]} (\"{previous[0]}\"); reorder so the leaders follow the alphabetical order of their shown names")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that XML lists whose file order players see follow the alphabetical order of their shown English names.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL XML display order")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS XML display order")
	return 0


if __name__ == "__main__":
	sys.exit(main())

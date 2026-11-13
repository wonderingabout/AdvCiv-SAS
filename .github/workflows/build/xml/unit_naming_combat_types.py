#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: BUG's Unit Naming options cover exactly the unit combat types in XML, in the config and its options tab, each with its option texts.

# <!-- custom: Unit Naming looks up the option Combat_<type> for each unit it names, and BUG raises ConfigError for an option it does not know.
# SAS split UNITCOMBAT_MELEE into MELEE_POLEARM and MELEE_SHOCK and added options for its archer and mounted splits but not these, so with Unit Naming on every Spearman or Swordsman raised "Option UnitNaming__Combat_MELEE_SHOCK not found", reproduced through SASPilot on 2026-11-13.
# The options' texts are built from the option ID, TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_<TYPE>_TEXT and _HOVER, so sas_text_references.py treats them as a dynamic family and cannot check them; this check does. See KI#1087. (Claude code Opus 5.5) -->
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
UNIT_COMBAT_INFOS = Path("Assets/XML/BasicInfos/CIV4UnitCombatInfos.xml")
CONFIG = Path("Assets/Config/Unit Naming.xml")
TAB = Path("Assets/Python/BUG/Tabs/BugUnitNameOptionsTab.py")
TEXT_GLOB = "Assets/XML/Text/*.xml"
# <!-- custom: Combat_None names units without a combat type (UnitNameEventManager.getUnitCombat returns "UNITCOMBAT_None"), so it has no XML entry. (Claude code Opus 5.5) -->
NO_COMBAT = "None"
COMMENT = re.compile(r"<!--.*?-->", re.S)
TYPE = re.compile(r"<Type>\s*UNITCOMBAT_([A-Z0-9_]+)\s*</Type>")
CONFIG_OPTION = re.compile(r'<option\s+id="Combat_([A-Za-z0-9_]+)"')
TAB_OPTION = re.compile(r'^[^#\n]*"UnitNaming__Combat_([A-Za-z0-9_]+)"', re.M)
TAG = re.compile(r"<Tag>\s*(TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_[A-Z0-9_]+)\s*</Tag>")


def read(path: Path) -> str:
	return path.read_bytes().decode("latin-1")


def check(types: set[str], config: list[str], tab: list[str], tags: set[str]) -> list[str]:
	failures = []
	expected = types | {NO_COMBAT}
	for where, options in ((CONFIG.as_posix(), config), (TAB.as_posix(), tab)):
		for name in sorted(expected - set(options)):
			failures.append(f"{where}: no Combat_{name} option for UNITCOMBAT_{name}; Unit Naming raises ConfigError for each such unit")
		for name in sorted(set(options) - expected):
			failures.append(f"{where}: Combat_{name} names no unit combat type in {UNIT_COMBAT_INFOS.as_posix()}")
		for name in sorted({name for name in options if options.count(name) > 1}):
			failures.append(f"{where}: Combat_{name} is listed more than once")
	for name in sorted(set(config) & expected):
		for suffix in ("TEXT", "HOVER"):
			key = f"TXT_KEY_BUG_OPT_UNITNAMING__COMBAT_{name.upper()}_{suffix}"
			if key not in tags:
				failures.append(f"{key}: no text, so the Unit Naming options tab shows the key itself")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that BUG's Unit Naming options match the unit combat types.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	root = args.repo_root
	types = set(TYPE.findall(COMMENT.sub("", read(root / UNIT_COMBAT_INFOS))))
	config = CONFIG_OPTION.findall(COMMENT.sub("", read(root / CONFIG)))
	tab = TAB_OPTION.findall(read(root / TAB))
	tags = set()
	for path in root.glob(TEXT_GLOB):
		tags.update(TAG.findall(COMMENT.sub("", read(path))))
	failures = check(types, config, tab, tags)
	if failures:
		print("FAIL Unit Naming combat types")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS Unit Naming combat types (%d types)" % len(types))
	return 0


if __name__ == "__main__":
	sys.exit(main())

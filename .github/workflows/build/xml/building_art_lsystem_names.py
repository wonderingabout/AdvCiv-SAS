#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every building art <LSystem> name has a placement rule in the city L-system the game loads.

# <!-- custom: argparse/pathlib/re/sys drive the CLI and the art define scan. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys

# <!-- custom: Shared repo-root resolution, as in the sibling XML checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


BUILDING_ART = Path("Assets/XML/Art/CIV4ArtDefines_Building.xml")
SAS_CITY_LSYSTEM = Path("Assets/XML/Buildings/CIV4CityLSystem.xml")
# <!-- custom: The Chieftain's Hall art came from Realism Invictus with LSYSTEM_VIKING_TEMPLE, which only RI's own CIV4CityLSystem.xml defines, so SAS city layouts had no rule for it. See KI#1074.
# SAS uses the BtS city L-system, which GitHub does not have, so --write stores its building:LSYSTEM_* names from a local Civ4 install, as xml_sas_text_inherited.py does for inherited text.
# Plain names, not hashes: they are bare identifiers, and failures should name the valid choices.
# If SAS ever ships its own CIV4CityLSystem.xml, the check reads that file instead. (Claude code Opus 5.5) -->
BTS_NAMES = Path(__file__).with_name("building_art_lsystem_names_bts.tsv")
BTS_CITY_LSYSTEM = Path("Beyond the Sword/Assets/XML/Buildings/CIV4CityLSystem.xml")
NAMES_HEADER = "name"
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def lsystem_names(path: Path) -> frozenset[str]:
	data = COMMENT_RE.sub("", path.read_text(encoding="utf-8", errors="replace"))
	return frozenset(re.findall(r'<ArtRef Name="building:([^"]+)"', data))


def city_lsystem_names(repo_root: Path) -> frozenset[str]:
	if (repo_root / SAS_CITY_LSYSTEM).exists():
		return lsystem_names(repo_root / SAS_CITY_LSYSTEM)
	lines = BTS_NAMES.read_text(encoding="utf-8").splitlines()
	if not lines or lines[0] != NAMES_HEADER:
		raise SystemExit(f"{BTS_NAMES}: first line must be the header {NAMES_HEADER!r}; regenerate with --write")
	return frozenset(line for line in lines[1:] if line)


def write_names(civ4_root: Path) -> int:
	path = civ4_root / BTS_CITY_LSYSTEM
	if not path.exists():
		raise SystemExit(f"missing {path}; pass the Civ4 install root with --civ4-root")
	names = sorted(lsystem_names(path))
	BTS_NAMES.write_text("\n".join([NAMES_HEADER] + names) + "\n", encoding="utf-8", newline="\n")
	print(f"wrote {len(names)} BtS city L-system names to {BTS_NAMES}")
	return 0


def check(repo_root: Path) -> list[str]:
	names = city_lsystem_names(repo_root)
	raw = (repo_root / BUILDING_ART).read_text(encoding="utf-8", errors="replace")
	data = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), raw)
	failures = []
	for match in re.finditer(r"<Type>(\w+)</Type>\s*<LSystem>([^<]*)</LSystem>", data):
		art_type, lsystem = match.groups()
		if lsystem not in names:
			line = data.count("\n", 0, match.start()) + 1
			failures.append(f"{BUILDING_ART.as_posix()}:{line}: {art_type} uses {lsystem}, which the city L-system does not define; use one of its building:LSYSTEM_* names")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that building art LSystem names exist in the city L-system.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	parser.add_argument("--write", action="store_true", help="regenerate the BtS name list (local only: needs a Civ4 BtS install)")
	parser.add_argument("--civ4-root", type=Path, help="Civ4 install root containing Beyond the Sword/ (for --write)")
	args = parser.parse_args()
	if args.write:
		if args.civ4_root is None:
			parser.error("--write needs --civ4-root")
		return write_names(args.civ4_root)
	failures = check(args.repo_root)
	if failures:
		print("FAIL building art LSystem names")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS building art LSystem names")
	return 0


if __name__ == "__main__":
	sys.exit(main())

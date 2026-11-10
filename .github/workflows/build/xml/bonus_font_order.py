#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A bonus's GameFont icon is the glyph at its art's <FontButtonIndex>, not its place in CIV4BonusInfos.xml, so the game works in any order.
# But on 2026-11-08 the XML listed Camel before Peat while their glyphs were the other way round, and the art file had kept BtS's grouping, so the three read differently.
# SAS now keeps the Nth BonusInfo on glyph N and the art file sorted by glyph; fail when either drifts, or when two art entries share a glyph. (Claude code Opus 5.5) -->

# <!-- custom: argparse exposes the repository option, pathlib/sys locate the shared XML helpers, and ElementTree reads the bonus and art XML. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the shared repository-root and namespace-agnostic XML readers from lib/xml_defines.py. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


BONUS_INFOS_REL_PATH = Path("Assets/XML/Terrain/CIV4BonusInfos.xml")
BONUS_ART_REL_PATH = Path("Assets/XML/Art/CIV4ArtDefines_Bonus.xml")


def parse(path: Path):
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	return ET.parse(path).getroot()


def read_bonuses(repo_root: Path) -> list[tuple[str, str]]:
	return [(child_text_by_local_name(node, "Type"), child_text_by_local_name(node, "ArtDefineTag")) for node in parse(repo_root / BONUS_INFOS_REL_PATH).iter() if local_name(node.tag) == "BonusInfo"]


def read_art(repo_root: Path) -> list[tuple[str, int]]:
	return [(child_text_by_local_name(node, "Type"), int(child_text_by_local_name(node, "FontButtonIndex"))) for node in parse(repo_root / BONUS_ART_REL_PATH).iter() if local_name(node.tag) == "BonusArtInfo"]


def check_bonus_font_order(bonuses: list[tuple[str, str]], art: list[tuple[str, int]]) -> list[str]:
	failures = []
	index_by_art = dict(art)
	for position, (bonus_type, art_type) in enumerate(bonuses):
		if art_type not in index_by_art:
			failures.append(f"{bonus_type}: ArtDefineTag {art_type} has no BonusArtInfo")
		elif index_by_art[art_type] != position:
			failures.append(f"{bonus_type}: BonusInfo {position} uses glyph {index_by_art[art_type]}; keep the Nth BonusInfo on glyph N, moving the glyphs in both GameFont .tga files with LLM_Helpers/art_viewing/gamefont_tga.py if needed")
	seen = {}
	for art_type, index in art:
		if index in seen:
			failures.append(f"{art_type}: FontButtonIndex {index} is already used by {seen[index]}")
		seen[index] = art_type
	indexes = [index for _, index in art]
	if indexes != sorted(indexes):
		failures.append(f"{BONUS_ART_REL_PATH}: BonusArtInfo entries are not sorted by FontButtonIndex ({indexes})")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that bonuses and their art follow GameFont glyph order.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing this script")
	args = parser.parse_args()

	try:
		failures = check_bonus_font_order(read_bonuses(args.repo_root), read_art(args.repo_root))
	except RuntimeError as exc:
		failures = [str(exc)]

	if failures:
		print("FAIL Bonus glyph order")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS Bonus glyph order")
	return 0


if __name__ == "__main__":
	sys.exit(main())

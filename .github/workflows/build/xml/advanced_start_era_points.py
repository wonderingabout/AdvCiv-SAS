#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: SAS flattened era cost percentages to 100 without rescaling iAdvancedStartPoints, so a Modern start kept AdvCiv's 7500 points but bought about 30% less.
# Fail when an era's points drift from AdvCiv's buying power at the current SAS cost percentages, so a later cost or points change has to be deliberate. (Claude code Opus 5.5) -->

# <!-- custom: argparse exposes the repository option, pathlib/sys locate the shared XML helpers, and ElementTree reads the era XML. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: Reuse the shared repository-root and namespace-agnostic XML readers from lib/xml_defines.py. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name, child_text_by_local_name


ERA_INFOS_REL_PATH = Path("Assets/XML/GameInfo/CIV4EraInfos.xml")
COST_PERCENT_TAGS = ("iTrainPercent", "iConstructPercent", "iGrowthPercent")
TOLERANCE_PERCENT = 10

# <!-- custom: Pinned from base AdvCiv 1.14's CIV4EraInfos.xml because CI has no AdvCiv install: iAdvancedStartPoints, then the percentage shared by its three COST_PERCENT_TAGS. (Claude code Opus 5.5) -->
ADVCIV_ERA_BASELINE: dict[str, tuple[int, int]] = {
	"ERA_ANCIENT": (400, 100),
	"ERA_CLASSICAL": (1600, 100),
	"ERA_MEDIEVAL": (2400, 100),
	"ERA_RENAISSANCE": (3600, 90),
	"ERA_INDUSTRIAL": (5500, 80),
	"ERA_MODERN": (7500, 70),
	"ERA_FUTURE": (9500, 60),
}


def read_eras(repo_root: Path) -> dict[str, tuple[int, float]]:
	path = repo_root / ERA_INFOS_REL_PATH
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")
	eras: dict[str, tuple[int, float]] = {}
	for node in ET.parse(path).getroot().iter():
		if local_name(node.tag) != "EraInfo":
			continue
		era_type = child_text_by_local_name(node, "Type")
		try:
			points = int(child_text_by_local_name(node, "iAdvancedStartPoints"))
			percents = [int(child_text_by_local_name(node, tag)) for tag in COST_PERCENT_TAGS]
		except (TypeError, ValueError) as exc:
			raise RuntimeError(f"{era_type}: missing or invalid Advanced Start or cost percentage value") from exc
		eras[era_type] = (points, sum(percents) / len(percents))
	return eras


def check_era_points(eras: dict[str, tuple[int, float]]) -> list[str]:
	failures = []
	for era_type in sorted(set(ADVCIV_ERA_BASELINE) - set(eras)):
		failures.append(f"{era_type}: in the AdvCiv baseline but missing from {ERA_INFOS_REL_PATH.name}")
	for era_type, (points, cost_percent) in eras.items():
		baseline = ADVCIV_ERA_BASELINE.get(era_type)
		if baseline is None:
			failures.append(f"{era_type}: has no AdvCiv baseline; add one to ADVCIV_ERA_BASELINE")
			continue
		expected = baseline[0] * cost_percent / baseline[1]
		if abs(points - expected) * 100 > expected * TOLERANCE_PERCENT:
			failures.append(f"{era_type}: iAdvancedStartPoints={points} is more than {TOLERANCE_PERCENT}% from the AdvCiv equivalent {expected:.0f} (AdvCiv {baseline[0]} points at cost {baseline[1]}%, SAS cost {cost_percent:g}%)")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check Advanced Start points against AdvCiv's buying power per start era.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing this script")
	args = parser.parse_args()

	try:
		failures = check_era_points(read_eras(args.repo_root))
	except RuntimeError as exc:
		failures = [str(exc)]

	if failures:
		print("FAIL Advanced Start era points")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS Advanced Start era points")
	return 0


if __name__ == "__main__":
	sys.exit(main())

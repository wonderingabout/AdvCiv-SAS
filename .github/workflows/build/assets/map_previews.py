#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every map script shown in Simple Game has a World Picker preview, and every SAS preview file exists.

# <!-- custom: A script shown in Simple Game without a WorldPickerInfo entry gets the dark default globe; on 2026-11-12, 14 of the 38 shown scripts had none, which nothing had flagged.
# This check fails until each has a preview, made with LLM_Helpers/game_runs/map_preview_dds.py, or is listed below with the reason it keeps the default globe. See KI#1082. (Claude code Opus 5.5) -->
# <!-- custom: importlib loads the shared Simple Game classifier from LLM_Helpers. (Claude code Opus 5.5) -->
import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

# <!-- custom: The classifier and the default-globe list live in LLM_Helpers/game_runs/simple_game_scripts.py, which ships in GitHub ZIPs unlike .github/, so the preview helper and the UI map generator can use them there; this check loads that file. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_SPEC = importlib.util.spec_from_file_location("simple_game_scripts", ROOT / "LLM_Helpers" / "game_runs" / "simple_game_scripts.py")
if _SPEC is None or _SPEC.loader is None:
	raise SystemExit("cannot load LLM_Helpers/game_runs/simple_game_scripts.py")
simple_game_scripts = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(simple_game_scripts)
DEFAULT_GLOBE_ON_PURPOSE = simple_game_scripts.DEFAULT_GLOBE_ON_PURPOSE
shown_scripts = simple_game_scripts.shown_scripts


def check(root: Path) -> list[str]:
	failures = []
	picker = (root / "Assets" / "XML" / "Interface" / "CIV4WorldPickerInfos.xml").read_text(encoding="utf-8")
	entries = set(re.findall(r"<MapName>([^<]+)</MapName>", picker))
	for script in shown_scripts(root / "PrivateMaps"):
		if script in DEFAULT_GLOBE_ON_PURPOSE:
			if script in entries:
				failures.append("%s has a World Picker entry but is listed in DEFAULT_GLOBE_ON_PURPOSE; remove it from the list" % script)
			continue
		if script not in entries:
			failures.append("%s is shown in Simple Game but has no World Picker preview, so it shows the dark default globe; make one with: python LLM_Helpers/game_runs/map_preview_dds.py %s --variants 3, then --pick N" % (script, script))
	for path in re.findall(r"<WaterLevelDecalPath>(Art/AdvCiv_SAS/[^<]+)</WaterLevelDecalPath>", picker):
		if not (root / "Assets" / path).is_file():
			failures.append("CIV4WorldPickerInfos.xml names %s, which does not exist under Assets/" % path)
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that every map script shown in Simple Game has a World Picker preview.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL Simple Game map previews")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS Simple Game map previews")
	return 0


if __name__ == "__main__":
	sys.exit(main())

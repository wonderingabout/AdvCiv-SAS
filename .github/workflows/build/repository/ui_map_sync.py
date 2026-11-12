#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: civ4_ui_map.json is exactly what make_civ4_ui_map.py generates.

# <!-- custom: The UI map's JSON is generated from make_civ4_ui_map.py, but on 2026-11-12 an agent edited the JSON directly, so a rerun of the generator would have silently dropped a day of WorldBuilder mapping, as Codex's review found.
# The generator also derives the Simple Game map list from the map scripts, so adding, removing or hiding a script changes the JSON too; this check fails until the JSON is regenerated, and the generator itself fails when more scripts are shown than fit without a scrollbar. (Claude code Opus 5.5) -->
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that civ4_ui_map.json matches what make_civ4_ui_map.py generates.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	folder = args.repo_root / "LLM_Helpers" / "game_runs" / "ui_maps"
	with tempfile.TemporaryDirectory() as tmp:
		generated = Path(tmp) / "civ4_ui_map.json"
		result = subprocess.run([sys.executable, str(folder / "make_civ4_ui_map.py"), str(generated)], capture_output=True, text=True)
		if result.returncode != 0:
			print("FAIL UI map sync")
			print("  - make_civ4_ui_map.py failed: %s" % (result.stderr.strip() or result.stdout.strip()))
			return 1
		if generated.read_bytes() != (folder / "civ4_ui_map.json").read_bytes():
			print("FAIL UI map sync")
			print("  - civ4_ui_map.json differs from what make_civ4_ui_map.py generates: edit the generator, never the JSON, and rerun it; a map script added, removed or hidden from Simple Game also changes it")
			return 1
	print("PASS UI map sync")
	return 0


if __name__ == "__main__":
	sys.exit(main())

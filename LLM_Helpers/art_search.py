#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Finds a kind of terrain or feature across every installed mod and draws them side by side, each on a plot through its own mod's art, labelled with the mod.
# Designing the Marsh feature meant searching mods for marshes, swamps and wetlands by hand and comparing them from screenshots; this does that search and comparison in one command, for any pattern.
# See README_Art_Tools.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; concurrent.futures renders in parallel; os counts processors; pathlib finds the mods; re matches the Types. (Claude code Opus 5.5) -->
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
# <!-- custom: subprocess and sys run nif_preview.py for each match. (Claude code Opus 5.5) -->
import subprocess
import sys

# <!-- custom: civ4_assets reads each mod's XML as the game layers it; plot_scene gives the labelled sheet layout and the plot preview's water test. (Claude code Opus 5.5) -->
from civ4_assets import Civ4Assets, DEFAULT_ROOT, default_cache
import plot_scene

# <!-- custom: Pillow reads the rendered plots; fail with the install command if it is missing. (Claude code Opus 5.5) -->
try:
	from PIL import Image
except ImportError:
	raise SystemExit("Pillow is required: py -m pip install pillow")

KINDS = {"feature": ("featureinfos", "FeatureInfo"), "terrain": ("terraininfos", "TerrainInfo")}


def installed_mods(root=DEFAULT_ROOT):
	folder = Path(root) / "Beyond the Sword" / "Mods"
	return sorted(path.name for path in folder.iterdir() if (path / "Assets").is_dir())


def matches(pattern, kinds, mods):
	# <!-- custom: Every Type matching pattern in each mod, skipping entries a mod inherits unchanged from the base game, so the base game's own are listed once, under BtS. (Claude code Opus 5.5) -->
	base = Civ4Assets(None)
	base_infos = {kind: base.infos("Terrain", *KINDS[kind]) for kind in kinds}
	found = [("BtS", kind, info_type) for kind in kinds for info_type in base_infos[kind] if re.search(pattern, info_type, re.IGNORECASE)]
	for mod in mods:
		try:
			assets = Civ4Assets(mod)
			for kind in kinds:
				for info_type, body in assets.infos("Terrain", *KINDS[kind]).items():
					if re.search(pattern, info_type, re.IGNORECASE) and base_infos[kind].get(info_type) != body:
						found.append((mod, kind, info_type))
		except (SystemExit, OSError, ValueError) as exc:
			print("skipped %s: %s" % (mod, exc), file=sys.stderr)
	return found


def render(match, scratch, size):
	# <!-- custom: A feature stands on the first terrain its XML allows, as plot_scene's defaults choose; a terrain is drawn flat.
	# A failed render is reported with its error and left off the sheet rather than failing the search, as some mods' XML or art does not load. (Claude code Opus 5.5) -->
	mod, kind, info_type = match
	out = scratch / ("%s_%s.png" % (re.sub(r"\W+", "_", mod), info_type))
	command = [sys.executable, str(Path(__file__).with_name("nif_preview.py")), info_type, str(out), "--size", str(size)]
	command += ["--mod", mod]
	result = subprocess.run(command, capture_output=True, text=True, errors="replace")
	error = None if result.returncode == 0 else ((result.stderr.strip() or result.stdout.strip()).splitlines() or ["failed"])[-1]
	return out, error


def main():
	parser = argparse.ArgumentParser(description="Find terrains or features whose Type matches a pattern in every installed mod and draw them on plots, as one sheet labelled with each mod.")
	parser.add_argument("pattern", help="regular expression matched against Types, such as 'MARSH|SWAMP|WETLAND|BOG'")
	parser.add_argument("out", help="PNG sheet to write")
	parser.add_argument("--kind", choices=("feature", "terrain", "both"), default="both")
	parser.add_argument("--mods", nargs="*", help="mod folder names to search; all installed mods by default")
	parser.add_argument("--exclude", nargs="*", default=[], help="mod folder names to leave out of the search")
	parser.add_argument("--size", type=int, default=220)
	parser.add_argument("--columns", type=int, default=5)
	parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
	parser.add_argument("--list", action="store_true", help="list the matches without rendering")
	args = parser.parse_args()
	kinds = ("feature", "terrain") if args.kind == "both" else (args.kind,)
	found = matches(args.pattern, kinds, [mod for mod in args.mods or installed_mods() if mod not in args.exclude])
	if not found:
		raise SystemExit("no %s matches %s" % (" or ".join(kinds), args.pattern))
	for mod, kind, info_type in found:
		print("%s: %s %s" % (mod, kind, info_type))
	if args.list:
		return
	scratch = default_cache("art_search")
	scratch.mkdir(parents=True, exist_ok=True)
	with ThreadPoolExecutor(args.jobs) as pool:
		results = list(pool.map(lambda match: render(match, scratch, args.size), found))
	pictures = []
	for (mod, kind, info_type), (out, error) in zip(found, results):
		if error:
			print("not drawn: %s %s: %s" % (mod, info_type, error), file=sys.stderr)
			continue
		pictures.append(("%s: %s %s" % (mod, info_type.split("_", 1)[1].lower(), kind), Image.open(out).convert("RGB")))
	if not pictures:
		raise SystemExit("none of the matches could be drawn")
	plot_scene.labelled_sheet(pictures, args.columns, args.out)
	print("wrote %s: %d of %d matches" % (args.out, len(pictures), len(found)))


if __name__ == "__main__":
	main()

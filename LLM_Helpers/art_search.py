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
# <!-- custom: hashlib and Counter find and count the mods that share one model file. (Claude code Opus 5.5) -->
from collections import Counter
import hashlib
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

KINDS = {"feature": ("Terrain", "featureinfos", "FeatureInfo"), "terrain": ("Terrain", "terraininfos", "TerrainInfo"), "building": ("Buildings", "buildinginfos", "BuildingInfo"), "unit": ("Units", "unitinfos", "UnitInfo")}


def installed_mods(root=DEFAULT_ROOT):
	folder = Path(root) / "Beyond the Sword" / "Mods"
	return sorted(path.name for path in folder.iterdir() if (path / "Assets").is_dir())


def art_facts(assets, kind):
	# <!-- custom: A building's or unit's art define and era by its Type; terrains and features have neither. (Claude code Opus 5.5) -->
	if kind not in ("building", "unit"):
		return {}
	records = assets.buildings() if kind == "building" else assets.units()
	prefix = "BUILDING_" if kind == "building" else "UNIT_"
	return {info_type: (art, records[art]["Era"]) for info_type, art in assets.type_art.items() if info_type.startswith(prefix)}


def art_file(assets, art):
	fields = assets.art_defines(art).get(art, {})
	return next((fields[key].replace("\\", "/").lower() for key in ("NIF", "SHADERNIF", "KFM") if fields.get(key)), None)


def art_digest(assets, art):
	found = art_file(assets, art)
	data = assets.locate(found)[1] if found else None
	return hashlib.sha1(data).hexdigest() if data else None


# <!-- custom: Added era, which keeps only buildings and units of those eras, and all_copies: without it a building or unit whose model file another mod already showed is counted rather than drawn, since a first hunt for future buildings gave 41 pictures of which most were the same Arcology and Cloning Factory from a dozen mods built on the same base. (Claude code Opus 5.5) -->
def matches(pattern, kinds, mods, era=None, all_copies=False):
	# <!-- custom: Every Type matching pattern in each mod, skipping entries a mod inherits unchanged from the base game, so the base game's own are listed once, under BtS.
	# A mod's buildings and units are nearly all edited copies of the base game's, so those are skipped when their art file is the base game's: the search is for art. (Claude code Opus 5.5) -->
	base = Civ4Assets(None)
	base_infos = {kind: base.infos(KINDS[kind][0], *KINDS[kind][1:]) for kind in kinds}
	base_facts = {kind: art_facts(base, kind) for kind in kinds}

	def wanted(facts, info_type):
		return not era or (info_type in facts and facts[info_type][1] is not None and any(word.strip().lower() in facts[info_type][1].lower() for word in era.split(",")))

	found = [("BtS", kind, info_type) for kind in kinds for info_type in base_infos[kind] if re.search(pattern, info_type, re.IGNORECASE) and wanted(base_facts[kind], info_type)]
	first_with, copies = {}, Counter()
	for mod in mods:
		try:
			assets = Civ4Assets(mod)
			for kind in kinds:
				facts = art_facts(assets, kind)
				for info_type, body in assets.infos(KINDS[kind][0], *KINDS[kind][1:]).items():
					if not re.search(pattern, info_type, re.IGNORECASE) or base_infos[kind].get(info_type) == body or not wanted(facts, info_type):
						continue
					if info_type in facts and info_type in base_facts[kind] and art_file(assets, facts[info_type][0]) == art_file(base, base_facts[kind][info_type][0]):
						continue
					digest = art_digest(assets, facts[info_type][0]) if info_type in facts and not all_copies else None
					if digest in first_with:
						copies[first_with[digest]] += 1
						continue
					if digest:
						first_with[digest] = (mod, kind, info_type)
					found.append((mod, kind, info_type))
		except (SystemExit, OSError, ValueError) as exc:
			print("skipped %s: %s" % (mod, exc), file=sys.stderr)
	return found, copies


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
	parser = argparse.ArgumentParser(description="Find terrains, features, buildings or units whose Type matches a pattern in every installed mod and draw them on plots, as one sheet labelled with each mod.")
	parser.add_argument("pattern", help="regular expression matched against Types, such as 'MARSH|SWAMP|WETLAND|BOG'")
	parser.add_argument("out", help="PNG sheet to write")
	parser.add_argument("--kind", choices=("feature", "terrain", "both", "building", "unit"), default="both", help="both is features and terrains")
	parser.add_argument("--era", help="buildings and units only: eras of the prerequisite tech to keep, such as ancient,classical")
	parser.add_argument("--mods", nargs="*", help="mod folder names to search; all installed mods by default")
	parser.add_argument("--exclude", nargs="*", default=[], help="mod folder names to leave out of the search")
	parser.add_argument("--size", type=int, default=220)
	parser.add_argument("--columns", type=int, default=5)
	parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
	parser.add_argument("--list", action="store_true", help="list the matches without rendering")
	parser.add_argument("--all-copies", action="store_true", help="draw a building or unit again in each mod that uses the same model file")
	args = parser.parse_args()
	kinds = ("feature", "terrain") if args.kind == "both" else (args.kind,)
	if args.era and args.kind not in ("building", "unit"):
		parser.error("--era requires --kind building or unit")
	found, copies = matches(args.pattern, kinds, [mod for mod in args.mods or installed_mods() if mod not in args.exclude], args.era, args.all_copies)
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
	# <!-- custom: The mod in brackets only when the sheet holds two or more mods, and the kind only when it holds two kinds. (Claude code Opus 5.5) -->
	several_mods = len({mod for mod, _, _ in found}) > 1
	for (mod, kind, info_type), (out, error) in zip(found, results):
		if error:
			print("not drawn: %s %s: %s" % (mod, info_type, error), file=sys.stderr)
			continue
		label = info_type.split("_", 1)[1].lower() + (" " + kind if len(kinds) > 1 else "") + (" (%s%s)" % (mod, " +%d" % copies[(mod, kind, info_type)] if copies[(mod, kind, info_type)] else "") if several_mods else "")
		pictures.append((label, Image.open(out).convert("RGB")))
	if not pictures:
		raise SystemExit("none of the matches could be drawn")
	plot_scene.labelled_sheet(pictures, args.columns, args.out)
	print("wrote %s: %d of %d matches" % (args.out, len(pictures), len(found)))


if __name__ == "__main__":
	main()

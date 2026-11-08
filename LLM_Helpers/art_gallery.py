#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Browsing a mod's art one preview at a time is slow: CIV Gold alone has 287 leader art defines.
# This renders every art define matching a pattern through nif_preview.py --mod, filtered by a unit's domain, unit combat or era, keeps each picture as its own PNG for Windows thumbnails, and lays them out on numbered grid sheets.
# See README_Art_Tools.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options; concurrent.futures and subprocess run previews in parallel, os counting processors; pathlib and sys find the helpers; civ4_assets lists the art defines and unit facts; Pillow builds the sheets. (Claude code Opus 5.5) -->
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys

from civ4_assets import Civ4Assets

# <!-- custom: Pillow builds the sheets; fail with the install command if it is missing. (Claude code Opus 5.5) -->
try:
	from PIL import Image, ImageDraw
except ImportError:
	raise SystemExit("Pillow is required: py -m pip install pillow")

HERE = Path(__file__).resolve().parent


def matches(value, wanted):
	# <!-- custom: A filter such as "medieval,renaissance" matches an era, domain or unit combat containing any of its words, ignoring case. (Claude code Opus 5.5) -->
	return not wanted or (value is not None and any(word.strip().lower() in value.lower() for word in wanted.split(",")))


def render(item, args):
	art_type, out = item
	command = [sys.executable, str(HERE / "nif_preview.py"), art_type, str(out), "--mod", args.mod, "--size", str(args.size)]
	if args.clip:
		command += ["--clip", args.clip, "--frames", str(args.frames)]
	result = subprocess.run(command, capture_output=True, text=True, errors="replace")
	if result.returncode != 0 or not out.exists():
		return art_type, (result.stderr.strip() or result.stdout.strip()).splitlines()[-1:] or ["no output"]
	return art_type, None


def sheet(cells, path, args, facts):
	columns = args.columns
	label_height = 28 if args.labels else 0
	# <!-- custom: Cells take the tallest picture's shape, so portrait leaders and 4:3 unit scenes both fill them. (Claude code Opus 5.5) -->
	width = args.size
	height = max(int(width * Image.open(picture).size[1] / Image.open(picture).size[0]) for _, picture in cells)
	characters = max(8, width // 7)
	rows = (len(cells) + columns - 1) // columns
	canvas = Image.new("RGB", (columns * width, rows * (height + label_height)), (24, 24, 24))
	draw = ImageDraw.Draw(canvas)
	for k, (art_type, picture) in enumerate(cells):
		x, y = (k % columns) * width, (k // columns) * (height + label_height)
		image = Image.open(picture).convert("RGB")
		image.thumbnail((width, height))
		canvas.paste(image, (x + (width - image.size[0]) // 2, y + (height - image.size[1]) // 2))
		if args.labels:
			# <!-- custom: Labels go in a strip under each picture rather than over it, so they never hide the art. (Claude code Opus 5.5) -->
			fact = facts.get(art_type)
			lines = [art_type.replace("ART_DEF_", "")[:characters]]
			if fact is not None:
				lines.append(" ".join(value.split("_", 1)[-1] for value in (fact["Domain"], fact["Era"], fact["Combat"]) if value and value != "NONE")[:characters])
			draw.text((x + 4, y + height + 2), "\n".join(lines), fill=(230, 230, 230))
	canvas.save(path)


def main():
	parser = argparse.ArgumentParser(description="Render a mod's leaders or units in bulk and lay them out on grid sheets.")
	parser.add_argument("out", type=Path, help="folder for the pictures and sheets")
	parser.add_argument("--mod", required=True, help="mod folder name under Beyond the Sword/Mods, or bts for the base game")
	parser.add_argument("--pattern", default="ART_DEF_LEADER_*", help="art define pattern, such as ART_DEF_UNIT_* (default: leaders)")
	parser.add_argument("--domain", help="units only: domains to keep, such as land or sea,air")
	parser.add_argument("--combat", help="units only: unit combats to keep, such as melee,mounted")
	parser.add_argument("--era", help="units only: eras of the unit's prerequisite tech to keep, such as ancient,classical")
	parser.add_argument("--limit", type=int, help="render at most this many")
	parser.add_argument("--clip", help="also render this clip as a GIF per entry, such as greeting or idle; the sheet shows each GIF's first frame")
	parser.add_argument("--frames", type=int, default=16, help="GIF frames with --clip")
	parser.add_argument("--size", type=int, default=180, help="picture width")
	parser.add_argument("--columns", type=int, default=5)
	parser.add_argument("--per-sheet", type=int, default=20, help="pictures per grid sheet")
	parser.add_argument("--labels", action="store_true", help="write each define's name, and a unit's domain, era and unit combat, under its picture")
	parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2), help="previews rendered at once")
	args = parser.parse_args()
	assets = Civ4Assets(args.mod)
	facts = assets.units()
	defines = assets.art_defines(args.pattern)
	selected = []
	for art_type in sorted(defines):
		fields = defines[art_type]
		if not any(fields.get(key) for key in ("KFM", "NIF", "NoShaderNIF", "SHADERNIF")):
			continue
		if args.domain or args.combat or args.era:
			fact = facts.get(art_type)
			if fact is None or not (matches(fact["Domain"], args.domain) and matches(fact["Combat"], args.combat) and matches(fact["Era"], args.era)):
				continue
		selected.append(art_type)
	if args.limit:
		selected = selected[:args.limit]
	if not selected:
		raise SystemExit("no art define of %s matches" % args.mod)
	args.out.mkdir(parents=True, exist_ok=True)
	suffix = ".gif" if args.clip else ".png"
	items = [(art_type, (args.out / (art_type.replace("ART_DEF_", "").lower() + suffix)).resolve()) for art_type in selected]
	print("rendering %d of %s's art defines into %s" % (len(items), args.mod, args.out.resolve()))
	with ThreadPoolExecutor(args.jobs) as pool:
		results = list(pool.map(lambda item: render(item, args), items))
	failed = {art_type: error for art_type, error in results if error}
	for art_type, error in failed.items():
		print("  %s failed: %s" % (art_type, error[0][:160]))
	cells = [(art_type, out) for art_type, out in items if art_type not in failed]
	for number, start in enumerate(range(0, len(cells), args.per_sheet), 1):
		path = args.out / ("sheet_%02d.png" % number)
		sheet(cells[start:start + args.per_sheet], path, args, facts)
		print("wrote %s" % path.resolve())
	print("%d rendered, %d failed" % (len(cells), len(failed)))


if __name__ == "__main__":
	sys.exit(main())

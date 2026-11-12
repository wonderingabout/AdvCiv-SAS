#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Agents' image readers open PNG/JPG, not the .dds and .tga art Civ4 uses, so this helper uses Pillow to put art side by side in one labelled PNG.
# On 2026-11-08 a contact sheet of Caveman2Cosmos's peat art chose Peat Works' button, after it had shipped with Quarry's. See README_Art_Tools.md. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the items and options; io wraps archived bytes for Pillow; os/pathlib resolve paths case-insensitively; fpk_tool reads Civ4's packed .FPK art; PIL (Pillow) reads .dds/.tga and draws the sheet. (Claude code Opus 5.5) -->
import argparse
import io
import os
from pathlib import Path

# <!-- custom: fpk_tool, beside this script, reads BtS's packed .FPK art without extracting it. (Claude code Opus 5.5) -->
from fpk_tool import FpkArchive

# <!-- custom: Pillow opens .dds/.tga and draws the sheet; fail with the install command if it is missing. (Claude code Opus 5.5) -->
try:
	from PIL import Image, ImageDraw
except ImportError:
	raise SystemExit("Pillow is required: py -m pip install pillow")


# <!-- custom: Helpers now sit in LLM_Helpers folders named by job, so find the repo root from the LLM_Helpers folder instead of a fixed parent depth. (Claude code Opus 5.5) -->
MOD_ROOT = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent
CIV4_ROOT = MOD_ROOT.parents[2]
LLM_EXTRACTED = Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "mod_repos"
# <!-- custom: Searched in this order, like the game: the mod, then BtS, Warlords and the original game, loose files before packed ones; extracted mods last. (Claude code Opus 5.5) -->
DEFAULT_ROOTS = (MOD_ROOT / "Assets", MOD_ROOT, CIV4_ROOT / "Beyond the Sword" / "Assets", CIV4_ROOT / "Warlords" / "Assets", CIV4_ROOT / "Assets", LLM_EXTRACTED / "c2cmerged", LLM_EXTRACTED / "history_rewritten", LLM_EXTRACTED / "Realism" / "Assets")
DEFAULT_FPKS = tuple(sorted((CIV4_ROOT / "Beyond the Sword" / "Assets").glob("*.FPK"))) + tuple(sorted((CIV4_ROOT / "Warlords" / "Assets").glob("*.FPK"))) + tuple(sorted((CIV4_ROOT / "Assets").glob("*.FPK")))
# <!-- custom: Atlas cells are 64 pixels and the XML's column,row are 1-based: on 2026-11-08 cell 2,9 of Actions_Builds_LeaderHeads_Specialists_Atlas.dds matched BtS's standalone BuildQuarry.dds, the closest of all its cells. (Claude code Opus 5.5) -->
ATLAS_CELL = 64


def find_loose(relative, roots):
	# <!-- custom: XML paths are case-insensitive on Windows and the extracted mods use lower case, so match each part case-insensitively. (Claude code Opus 5.5) -->
	if Path(relative).is_file():
		return Path(relative)
	parts = [p for p in relative.replace("\\", "/").split("/") if p]
	for root in roots:
		current = root
		for part in parts:
			if current is None or not current.is_dir():
				current = None
				break
			match = [entry for entry in os.listdir(current) if entry.lower() == part.lower()]
			current = current / match[0] if match else None
		if current is not None and current.is_file():
			return current
	return None


def load(relative, roots, archives):
	path = find_loose(relative, roots)
	if path is not None:
		return str(path), Image.open(path)
	for archive in archives:
		data = archive.read(relative.lstrip("/\\"))
		if data is not None:
			return "%s in %s" % (relative, archive.path.name), Image.open(io.BytesIO(data))
	return None, None


def resolve(item, roots, archives):
	# <!-- custom: An XML button string is either a path or ",standalone.dds,atlas.dds,column,row"; use the standalone file if found, else cut the cell out of the atlas. (Claude code Opus 5.5) -->
	if not item.startswith(","):
		source, image = load(item, roots, archives)
		return (Path(item).name, source, image) if image is not None else (None, "not found", None)
	_, standalone, atlas, column, row = item.split(",")[:5]
	source, image = load(standalone, roots, archives)
	if image is not None:
		return Path(standalone).name, source, image
	source, image = load(atlas, roots, archives)
	if image is None:
		return None, "neither its standalone file nor its atlas was found", None
	x, y = (int(column) - 1) * ATLAS_CELL, (int(row) - 1) * ATLAS_CELL
	return "%s %s,%s" % (Path(atlas).name, column, row), source, image.crop((x, y, x + ATLAS_CELL, y + ATLAS_CELL))


def main():
	parser = argparse.ArgumentParser(description="Put Civ4 art (.dds, .tga, .png) side by side in one labelled PNG.")
	parser.add_argument("items", nargs="+", help="file paths or XML <Button> strings")
	parser.add_argument("--out", required=True)
	parser.add_argument("--size", type=int, default=128, help="cell size in pixels")
	parser.add_argument("--root", action="append", type=Path, help="extra folder to search, before the defaults")
	parser.add_argument("--fpk", action="append", type=Path, help="extra .FPK archive to search, before the defaults")
	args = parser.parse_args()
	roots = tuple(args.root or ()) + DEFAULT_ROOTS
	archives = [FpkArchive(path) for path in tuple(args.fpk or ()) + DEFAULT_FPKS]
	cells = []
	for item in args.items:
		label, source, image = resolve(item, roots, archives)
		if image is None:
			print("skipped %s: %s" % (item, source))
			continue
		print("%s: %s %dx%d %s" % (source, image.format, image.size[0], image.size[1], image.mode))
		image = image.convert("RGBA")
		# <!-- custom: thumbnail() only shrinks, which left 64-pixel buttons small in the first sheet; scale to the cell both ways, keeping the aspect ratio. (Claude code Opus 5.5) -->
		scale = float(args.size) / max(image.size)
		image = image.resize((max(1, int(image.size[0] * scale)), max(1, int(image.size[1] * scale))), Image.LANCZOS)
		cells.append((label, image))
	if not cells:
		raise SystemExit("nothing to draw")
	sheet = Image.new("RGB", ((args.size + 8) * len(cells), args.size + 28), (60, 60, 60))
	draw = ImageDraw.Draw(sheet)
	for k, (label, image) in enumerate(cells):
		x = 4 + (args.size + 8) * k
		sheet.paste(image, (x, 4), image)
		draw.text((x, args.size + 8), label[:args.size // 6], fill=(230, 230, 230))
	sheet.save(args.out)
	print("wrote %s with %d image(s)" % (args.out, len(cells)))


if __name__ == "__main__":
	main()

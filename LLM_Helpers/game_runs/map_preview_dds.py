# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Makes the Simple Game preview of a map script: starts a QuickStart game on it at turn 0, before any city exists, reveals the map with Debug Mode, and turns the minimap into the 336 x 256 DXT1 FLAT_<Script>.dds that the World Picker shows.
# The camera frame drawn on the minimap is removed by taking three captures with the camera in different places and keeping the median of each pixel, which replaces the user's earlier Paint.NET retouching (README "New .dds for mapscripts in Simple Game"). (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, os, re and time for the run and the logs, subprocess for the Recycle Bin. (Claude code Opus 5.5) -->
import argparse
import os
import re
import subprocess
import time
# <!-- custom: ElementTree checks the World Picker XML before writing it, Path handles files; Pillow handles the images; desktop_windows drives Civ4 and run_autoplay writes the per-run INI and closes the client. (Claude code Opus 5.5) -->
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

import desktop_windows as d
import run_autoplay
# <!-- custom: simple_game_scripts, beside this helper, says which scripts Simple Game lists; the CI check and the UI map generator share it, so the three cannot disagree.
# A first version loaded it from the CI check under .github/, which GitHub ZIPs leave out (GPT-6.1-Sol). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
import simple_game_scripts as sgs

REPO = Path(__file__).resolve().parents[2]
MAPS_ART = REPO / "Assets" / "Art" / "AdvCiv_SAS" / "Maps"
PRIVATE_MAPS = REPO / "PrivateMaps"
WORLD_PICKER = REPO / "Assets" / "XML" / "Interface" / "CIV4WorldPickerInfos.xml"
# <!-- custom: The minimap's map image in a 1926 x 1120 window (1920 x 1080 client), measured on 2026-11-12 from its edge pixels; black letterbox bands inside it are trimmed. (Claude code Opus 5.5) -->
MINIMAP = (1716, 960, 1919, 1109)
# <!-- custom: The run's INI asks for that client size, and the window is checked before any click: the first version inherited the user's resolution, so on another window size its fixed points would have clicked and sampled the game map instead of the minimap. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
SCREEN = (1920, 1080)
WINDOW = (1926, 1120)
# <!-- custom: The existing previews hold the map in about 250 x 154 pixels centred in 336 x 256, with transparent bands around it. (Claude code Opus 5.5) -->
CANVAS = (336, 256)
BOX = (250, 154)
# <!-- custom: Minimap points clicked to move the camera, as fractions of the map image; three far-apart places put the camera frame on different pixels each time. (Claude code Opus 5.5) -->
CAMERA_POINTS = ((0.2, 0.25), (0.8, 0.3), (0.5, 0.8))


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Make the World Picker preview FLAT_<Script>.dds of map scripts from their minimap at turn 0.")
	parser.add_argument("scripts", nargs="*", help="Map script names without .py, such as Arboria")
	parser.add_argument("--missing", action="store_true", help="Make previews for every script shown in Simple Game that has no World Picker entry")
	parser.add_argument("--list-missing", action="store_true", help="Only list those scripts")
	parser.add_argument("--all", action="store_true", help="Every script shown in Simple Game, except those keeping the default globe on purpose")
	parser.add_argument("--handmade", action="store_true", help="Every script whose preview was made by hand before this tool, to redo it in the same format")
	parser.add_argument("--chooser", default="the user", help="With --pick: who chose the variant, such as 'Claude code Opus 5.5' (default: the user)")
	parser.add_argument("--world-size", default="WORLDSIZE_STANDARD")
	parser.add_argument("--work", type=Path, required=False, help="Folder for the captures and PNGs (default: a folder in the scratch outputs)")
	parser.add_argument("--variants", type=int, default=1, help="Make this many previews from freshly generated maps, numbered, with a sheet to compare them; install one afterwards with --pick")
	parser.add_argument("--pick", type=int, help="Install variant N made earlier with --variants, without starting Civ4")
	parser.add_argument("--reason", help="With --pick: why this variant was chosen, kept in the entry's comment as the chooser's taste")
	parser.add_argument("--no-dds", action="store_true", help="Write only the PNG, for a look before replacing anything")
	parser.add_argument("--no-xml", action="store_true", help="Do not add a World Picker entry")
	parser.add_argument("--keep-open", action="store_true", help="Leave the last client running, to inspect it")
	return parser.parse_args()


def simple_game_scripts() -> list[str]:
	return sgs.shown_scripts(PRIVATE_MAPS)


def picker_maps() -> set[str]:
	return set(re.findall(r"<MapName>([^<]+)</MapName>", WORLD_PICKER.read_text(encoding="utf-8")))


def shot(pid: int, path: Path) -> Image.Image:
	d.screenshot(pid, path)
	return Image.open(path).convert("RGB")


def wait_for_map(pid: int, work: Path, timeout: float = 240) -> None:
	# <!-- custom: The game is ready once the minimap shows something and stops changing between two captures; at turn 0 it is mostly black until Debug Mode reveals the map. (Claude code Opus 5.5) -->
	end = time.monotonic() + timeout
	previous = None
	size = None
	while time.monotonic() < end:
		time.sleep(3)
		if not d.process_alive(pid):
			raise SystemExit("Civ4 exited while loading")
		hwnd = d.find_window(pid)
		if not hwnd:
			continue
		left, top, right, bottom = d.window_rect(hwnd)
		size = (right - left, bottom - top)
		# <!-- custom: The window starts small and grows while loading, so wait for the measured size; only a timeout reports the size it kept. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if size != WINDOW:
			continue
		try:
			area = shot(pid, work / "loading.png").crop(MINIMAP)
		except Exception:
			continue
		if ImageStat.Stat(area.convert("L")).stddev[0] > 20 and previous is not None and ImageStat.Stat(ImageChops.difference(area, previous).convert("L")).mean[0] < 2:
			return
		previous = area
	if size != WINDOW:
		raise SystemExit("the window stayed %s, not the %dx%d that MINIMAP was measured in; re-measure MINIMAP for this size" % ("%dx%d" % size if size else "unfound", WINDOW[0], WINDOW[1]))
	raise SystemExit("the map did not appear within %d s" % timeout)


def map_size(pid: int) -> tuple[int, int] | None:
	# <!-- custom: The plot grid's width and height from this client's SASGameRecord (map=WxH), when the record is enabled; the minimap is then resized to that shape in case it stretches a map to its box. (Claude code Opus 5.5) -->
	for path in sorted((run_autoplay.USER_DIR / "Logs").glob("SASGameRecord_*_%d_*.log" % pid), key=lambda p: p.stat().st_mtime, reverse=True):
		match = re.search(r"GAME_RECORD_GAME_SETTINGS .*? map=(\d+)x(\d+)", path.read_text(encoding="utf-8", errors="replace"))
		if match:
			return int(match.group(1)), int(match.group(2))
	return None


def capture(pid: int, script: str, work: Path) -> Image.Image:
	d.key(pid, "ctrl+z")
	time.sleep(3)
	left, top, right, bottom = MINIMAP
	captures = []
	for i, (fx, fy) in enumerate(CAMERA_POINTS):
		d.click(pid, int(left + fx * (right - left)), int(top + fy * (bottom - top)))
		time.sleep(2.5)
		# <!-- custom: A volley of quick shots at each place, as the user suggested: the selected unit's minimap dot blinks, so some shots miss it. (Claude code Opus 5.5) -->
		for j in range(3):
			captures.append(shot(pid, work / ("%s_camera%d_%d.png" % (script, i + 1, j + 1))).crop(MINIMAP))
			time.sleep(0.4)
	return merge(captures)


def merge(captures: list[Image.Image]) -> Image.Image:
	# <!-- custom: Per-pixel median of all captures: the camera frame covers a pixel only in the shots from one camera place, and the blinking unit dot only in some shots. (Claude code Opus 5.5) -->
	bands = []
	for band in range(3):
		channels = [c.getchannel(band).tobytes() for c in captures]
		bands.append(Image.frombytes("L", captures[0].size, bytes(sorted(values)[len(values) // 2] for values in zip(*channels))))
	merged = Image.merge("RGB", bands)
	# <!-- custom: Turn-0 units are white dots that stay put, so the median keeps them; near-white pixels take their neighbourhood's median instead.
	# Ice is bluish and stays. (Claude code Opus 5.5) -->
	smoothed = merged.filter(ImageFilter.MedianFilter(5))
	white = Image.merge("RGB", [merged.getchannel(i).point([255 if v > 235 else 0 for v in range(256)]) for i in range(3)])
	mask = ImageChops.multiply(ImageChops.multiply(white.getchannel(0), white.getchannel(1)), white.getchannel(2)).filter(ImageFilter.MaxFilter(3))
	merged = Image.composite(smoothed, merged, mask)
	# <!-- custom: The minimap letterboxes a map whose shape differs from its box, and a thin silver panel edge sits at its left, beyond the black band; on Arboria (40 x 40) a plain bounding box kept both.
	# Keep the widest run of rows and columns that are mostly not black. (Claude code Opus 5.5) -->
	gray = merged.convert("L").point([255 if v > 8 else 0 for v in range(256)])
	cols = [gray.crop((x, 0, x + 1, gray.height)).histogram()[255] > gray.height / 2 for x in range(gray.width)]
	rows = [gray.crop((0, y, gray.width, y + 1)).histogram()[255] > gray.width / 2 for y in range(gray.height)]
	(x0, x1), (y0, y1) = longest_run(cols), longest_run(rows)
	# <!-- custom: One pixel more on each side: the first batch kept thin edge lines on Tectonics and Planet_Generator_0_68 (2026-11-12). (Claude code Opus 5.5) -->
	return merged.crop((x0 + 1, y0 + 1, x1 - 1, y1 - 1))


def longest_run(flags: list[bool]) -> tuple[int, int]:
	best, start = (0, len(flags)), None
	best_len = -1
	for i, flag in enumerate(flags + [False]):
		if flag and start is None:
			start = i
		elif not flag and start is not None:
			if i - start > best_len:
				best, best_len = (start, i), i - start
			start = None
	return best


def to_preview(image: Image.Image, size: tuple[int, int] | None) -> Image.Image:
	aspect = (size[0] / size[1]) if size else (image.width / image.height)
	width, height = BOX
	if width / height > aspect:
		width = round(height * aspect)
	else:
		height = round(width / aspect)
	canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
	canvas.paste(image.resize((width, height), Image.Resampling.LANCZOS).convert("RGBA"), ((CANVAS[0] - width) // 2, (CANVAS[1] - height) // 2))
	return canvas


def picker_entry_update(script: str, note: str) -> tuple[str, str | None, bool]:
	# <!-- custom: A new entry copies Boreal's, the pattern every SAS preview uses: GlobeFLAT.nif with the .dds as its one water-level decal. (Claude code Opus 5.5) -->
	# <!-- custom: Read and write without newline translation: the file uses CRLF, and a text-mode read had turned it into LF on the first run. (Claude code Opus 5.5) -->
	with open(WORLD_PICKER, encoding="utf-8", newline="") as handle:
		text = handle.read()
	# <!-- custom: Each entry says where its preview came from, so a reader knows it was generated and how it was chosen. (Claude code Opus 5.5) -->
	newline = "\r\n" if "\r\n" in text else "\n"
	comment = "\t\t<!-- custom: Preview made by LLM_Helpers/game_runs/map_preview_dds.py from the minimap at turn 0 on %s; %s. See KI#1082. (Claude code Opus 5.5) -->%s" % (time.strftime("%Y-%m-%d"), note, newline)
	decal = "Art/AdvCiv_SAS/Maps/%s/FLAT_%s.dds" % (script, script)
	existing = re.search(r"(\t\t<!-- custom: Preview made[^\n]*\n)?(\t\t<WorldPickerInfo>\s*<MapName>%s</MapName>.*?</WorldPickerInfo>\r?\n)" % re.escape(script), text, re.S)
	old_decal = None
	if existing:
		# <!-- custom: Redoing an existing preview, such as the 18 the user made by hand, replaces its provenance comment and points its decal at the standard FLAT_<Script>.dds, so every SAS preview ends up in one format (user's request, 2026-11-12). (Claude code Opus 5.5) -->
		decal_match = re.search(r"<WaterLevelDecalPath>([^<]+)</WaterLevelDecalPath>", existing.group(2))
		if not decal_match or not decal_match.group(1).startswith("Art/AdvCiv_SAS/"):
			raise SystemExit("%s's World Picker entry is not a SAS preview entry; leaving it alone" % script)
		old_decal = decal_match.group(1) if decal_match.group(1) != decal else None
		entry = existing.group(2).replace(decal_match.group(1), decal)
		updated = text[:existing.start()] + comment + entry + text[existing.end():]
	else:
		match = re.search(r"(\t\t<WorldPickerInfo>\s*<MapName>Boreal</MapName>.*?</WorldPickerInfo>\r?\n)", text, re.S)
		if not match:
			raise SystemExit("Boreal's World Picker entry not found to copy")
		entry = match.group(1).replace("<MapName>Boreal</MapName>", "<MapName>%s</MapName>" % script).replace("Art/AdvCiv_SAS/Maps/Boreal/FLAT_Boreal.dds", decal)
		closing = text.rindex("\t</WorldPickerInfos>")
		updated = text[:closing] + comment + entry + text[closing:]
	# <!-- custom: Codex reproduced a --reason containing "--" writing an XML comment that is invalid and breaks the whole file, so the new text is parsed before it replaces the file. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	try:
		ET.fromstring(updated.encode("utf-8"))
	except ET.ParseError as error:
		raise SystemExit("the new World Picker entry would make invalid XML (%s); the file is unchanged" % error)
	return updated, old_decal, bool(existing)


def sas_owned_or_missing(script: str, text: str) -> bool:
	# <!-- custom: --all selected inherited BtS entries such as Pangaea and Great_Plains, whose previews the installer then refused (GPT-6.1-Sol).
	# It now takes only scripts with no entry or a SAS entry, the ones this tool can write. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	entry = re.search(r"<WorldPickerInfo>\s*<MapName>%s</MapName>.*?</WorldPickerInfo>" % re.escape(script), text, re.S)
	return not entry or "<WaterLevelDecalPath>Art/AdvCiv_SAS/" in entry.group(0)


def recycle(path: Path) -> None:
	# <!-- custom: An old preview whose name differs from FLAT_<Script>.dds, such as Equal_Islands' _SAS48 file, goes to the Recycle Bin rather than being deleted for good, as AGENTS.md asks. (Claude code Opus 5.5) -->
	command = "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('%s', 'OnlyErrorDialogs', 'SendToRecycleBin')" % str(path).replace("'", "''")
	subprocess.run(["powershell", "-NoProfile", "-Command", command], check=True)
	print("  sent the old", path.name, "to the Recycle Bin")


def install(script: str, preview: Image.Image, args: argparse.Namespace, note: str) -> None:
	# <!-- custom: Game XML and art are not edited while any Civ4 runs, as AGENTS.md's runtime-safety rule asks; --pick and a kept-open client had skipped the launch-time check (GPT-6.1-Sol). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if d.civ4_processes():
		raise SystemExit("Civ4 is running: close it before installing %s's preview, which edits game XML and art" % script)
	# <!-- custom: The XML is built and checked before the DDS is written: Codex found an invalid --reason left the XML intact but had already overwritten the DDS. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	update = None if args.no_xml else picker_entry_update(script, note)
	out = MAPS_ART / script / ("FLAT_%s.dds" % script)
	out.parent.mkdir(parents=True, exist_ok=True)
	preview.save(out, "DDS", pixel_format="DXT1")
	print("  wrote", out)
	if update:
		updated, old_decal, existed = update
		with open(WORLD_PICKER, "w", encoding="utf-8", newline="") as handle:
			handle.write(updated)
		print("  %s the World Picker entry" % ("updated" if existed else "added"))
		if old_decal and (REPO / "Assets" / old_decal).is_file():
			recycle(REPO / "Assets" / old_decal)


def make_preview(script: str, args: argparse.Namespace, png: Path, last: bool) -> Image.Image:
	ini_name = "SASPreview_%s_%d.ini" % (time.strftime("%Y%m%dT%H%M%S"), os.getpid())
	ini_path = d.DEFAULT_CIV4_DIR / ini_name
	# <!-- custom: No [SASAutoplay] request, so the game waits at turn 0 with no city on the map. (Claude code Opus 5.5) -->
	run_autoplay.write_request_ini(run_autoplay.USER_DIR / "CivilizationIV.ini", ini_path, None, False, "-", "Preview", {"QuickStart": "1", "Map": script, "WorldSize": args.world_size, "ScreenWidth": str(SCREEN[0]), "ScreenHeight": str(SCREEN[1])})
	# <!-- custom: The launch is inside the try, with pid set only once it succeeds, so a launch that raises still removes the INI (GPT-6.1-Sol). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	pid = None
	succeeded = False
	try:
		pid = d.launch_detached("ini=%s" % ini_name)
		wait_for_map(pid, args.work)
		image = capture(pid, script, args.work)
		size = map_size(pid)
		preview = to_preview(image, size)
		preview.save(png)
		print("%s: map %s, minimap %dx%d -> %s" % (script, "%dx%d" % size if size else "size unknown", image.width, image.height, png))
		succeeded = True
		return preview
	finally:
		# <!-- custom: --keep-open applied to every client, although its help promises only the last one; a failed run is always closed, so its client and INI are never left behind. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if args.keep_open and last and succeeded:
			print("  left open: pid %d; per-run INI %s (delete it and its .bak after closing)" % (pid, ini_path))
		else:
			try:
				if pid is not None:
					run_autoplay.close_civ4(pid)
			finally:
				# <!-- custom: Civ4 leaves a .bak copy beside the INI it was started with. (Claude code Opus 5.5) -->
				for leftover in (ini_path, ini_path.with_name(ini_path.name + ".bak")):
					leftover.unlink(missing_ok=True)


def variant_sheet(script: str, pngs: list[Path], out: Path) -> None:
	# <!-- custom: The variants side by side, numbered as --pick expects, on a grey background so the transparent bands show. (Claude code Opus 5.5) -->
	columns = min(3, len(pngs))
	rows = (len(pngs) + columns - 1) // columns
	sheet = Image.new("RGB", (CANVAS[0] * columns, (CANVAS[1] + 20) * rows), (60, 60, 60))
	draw = ImageDraw.Draw(sheet)
	for i, png in enumerate(pngs):
		x, y = (i % columns) * CANVAS[0], (i // columns) * (CANVAS[1] + 20)
		tile = Image.new("RGBA", CANVAS, (60, 60, 60, 255))
		tile.alpha_composite(Image.open(png).convert("RGBA"))
		sheet.paste(tile.convert("RGB"), (x, y + 20))
		draw.text((x + 6, y + 4), "%s %d" % (script, i + 1), fill="yellow")
	sheet.save(out)
	print("compare:", out)


def main() -> int:
	args = parse_args()
	missing = [s for s in simple_game_scripts() if s not in picker_maps() and s not in sgs.DEFAULT_GLOBE_ON_PURPOSE]
	if args.list_missing:
		print("\n".join(missing))
		return 0
	# <!-- custom: --all and --handmade let one run redo every preview or only the old hand-made ones, besides naming a few scripts (user's request, 2026-11-12). (Claude code Opus 5.5) -->
	if args.all:
		picker_text = WORLD_PICKER.read_text(encoding="utf-8")
		scripts = [s for s in simple_game_scripts() if s not in sgs.DEFAULT_GLOBE_ON_PURPOSE and sas_owned_or_missing(s, picker_text)]
	elif args.handmade:
		scripts = re.findall(r"made by hand[^\n]*\n\s*<WorldPickerInfo>\s*<MapName>([^<]+)</MapName>", WORLD_PICKER.read_text(encoding="utf-8"))
	elif args.missing:
		scripts = missing
	else:
		scripts = args.scripts
	if not scripts:
		raise SystemExit("name scripts, or pass --missing, --all or --handmade")
	args.work = args.work or (REPO / "LLM_Helpers" / "outputs" / "map_previews")
	args.work.mkdir(parents=True, exist_ok=True)
	if args.pick:
		# <!-- custom: Installs a variant made earlier, without starting Civ4. (Claude code Opus 5.5) -->
		for script in scripts:
			png = args.work / ("FLAT_%s_%d.png" % (script, args.pick))
			if not png.is_file():
				raise SystemExit("no %s; make variants first with --variants" % png)
			print("%s: installing variant %d" % (script, args.pick))
			install(script, Image.open(png).convert("RGBA"), args, "variant %d of %d, chosen by %s, whose reason, a matter of taste: %s" % (args.pick, len(list(args.work.glob("FLAT_%s_*.png" % script))), args.chooser, args.reason or "no reason given"))
		return 0
	if d.civ4_processes():
		raise SystemExit("Civ4 is already running: close it first; each preview needs a fresh game")
	if args.keep_open and args.variants <= 1 and not args.no_dds:
		raise SystemExit("--keep-open would leave the client running while the preview is installed; add --no-dds, or use --variants and install with --pick after closing it")
	for index, script in enumerate(scripts):
		last_script = index == len(scripts) - 1
		if args.variants > 1:
			# <!-- custom: Each launch generates a new map, so several variants let the user choose the best-looking one (user's request, 2026-11-12). (Claude code Opus 5.5) -->
			pngs = [args.work / ("FLAT_%s_%d.png" % (script, k)) for k in range(1, args.variants + 1)]
			for k, png in enumerate(pngs):
				make_preview(script, args, png, last_script and k == len(pngs) - 1)
			variant_sheet(script, pngs, args.work / ("%s_variants.png" % script))
			print("  choose one with: map_preview_dds.py %s --pick N" % script)
		else:
			preview = make_preview(script, args, args.work / ("FLAT_%s.png" % script), last_script)
			if not args.no_dds:
				install(script, preview, args, "a single run, not chosen among variants")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

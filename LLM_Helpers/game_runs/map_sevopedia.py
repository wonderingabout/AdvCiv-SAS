#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Maps the Sevopedia page of each category: where its panels and EXPAND buttons are, so an agent can click into a page without reading a full screenshot first.
# On 2026-11-11 the user asked for this map; reading 36 full screenshots by eye would have been slow and costly, so this clicks each category point from civ4_points.json, finds the panels by their colour and the EXPAND buttons by their look, and writes the positions to civ4_sevopedia_map.json.
# Panels are a greyish purple, about (110-122, 100-115, 102-118), while the parchment around them is brownish with clearly less blue, such as (145, 124, 102); the rule below keeps the first and drops the second. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; json reads the points and writes the map, and re keeps its number lists on one line; tempfile holds screenshots; time waits for pages; sys and pathlib handle exits and paths. (Claude Code Opus 5.5) -->
import argparse
import json
import re
import sys
import tempfile
import time
from pathlib import Path

# <!-- custom: numpy and scipy find the panel regions and match the EXPAND template; PIL reads screenshots and draws the overlays. (Claude Code Opus 5.5) -->
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, signal

# <!-- custom: desktop_windows, beside this script, clicks, hovers and screenshots the Civ4 window. (Claude Code Opus 5.5) -->
import desktop_windows

HERE = Path(__file__).resolve().parent
POINTS_FILE = HERE / "ui_maps" / "civ4_points.json"
MAP_FILE = HERE / "ui_maps" / "civ4_sevopedia_map.json"
TEMPLATE_FILE = HERE / "ui_maps" / "civ4_expand_button.png"
# <!-- custom: The page area between the title bar and the bottom buttons, right of the category list, at 1920x1080 windowed. (Claude Code Opus 5.5) -->
CONTENT = (180, 45, 1926, 1075)
# <!-- custom: An idle spot on the bottom bar, so the pointer leaves no tooltip over the page in the screenshot. (Claude Code Opus 5.5) -->
IDLE_POINT = (1500, 1100)
ENTRY_LIST_RIGHT = 380


def capture(pid):
	path = Path(tempfile.gettempdir()) / "map_sevopedia_shot.png"
	desktop_windows.screenshot(pid, path)
	return Image.open(path).convert("RGB")


def find_panels(image):
	a = np.asarray(image).astype(int)
	r, g, b = a[..., 0], a[..., 1], a[..., 2]
	mask = (b - r > -14) & (r > 70) & (r < 170) & (np.abs(r - g) < 20)
	left, top, right, bottom = CONTENT
	region = np.zeros_like(mask)
	region[top:bottom, left:right] = True
	mask &= region
	# <!-- custom: Closing fills the holes that text and icons leave inside a panel, so each panel becomes one region. (Claude Code Opus 5.5) -->
	mask = ndimage.binary_closing(mask, structure=np.ones((9, 9)))
	labels, _count = ndimage.label(mask)
	panels = []
	for found in ndimage.find_objects(labels):
		y, x = found
		width, height = x.stop - x.start, y.stop - y.start
		if width < 40 or height < 30:
			continue
		# <!-- custom: A real panel fills most of its bounding box; scattered pixels in the model view or the parchment do not. (Claude Code Opus 5.5) -->
		if mask[found].mean() < 0.6:
			continue
		# <!-- custom: The first full run also counted the highlighted entry at the top of the entry list as a panel on six pages; that list column ends near x 370, so a box entirely inside it is dropped. (Claude Code Opus 5.5) -->
		if x.stop <= ENTRY_LIST_RIGHT:
			continue
		panels.append([int(x.start), int(y.start), int(x.stop), int(y.stop)])
	return sorted(panels, key=lambda box: (box[1] // 20, box[0]))


def find_expand(image, template):
	# <!-- custom: Normalized cross-correlation of the grey screenshot with the template; matches above 0.8 count, keeping the best one within each button-sized neighbourhood. (Claude Code Opus 5.5) -->
	f = np.asarray(image.convert("L")).astype(float)
	t = np.asarray(template.convert("L")).astype(float)
	t = t - t.mean()
	th, tw = t.shape
	num = signal.fftconvolve(f, t[::-1, ::-1], mode="valid")
	window_sum = signal.fftconvolve(f, np.ones(t.shape), mode="valid")
	window_sq = signal.fftconvolve(f * f, np.ones(t.shape), mode="valid")
	variance = np.maximum(window_sq - window_sum ** 2 / t.size, 1e-6)
	score = num / (np.sqrt(variance) * np.sqrt((t * t).sum()))
	peaks = (score > 0.8) & (score == ndimage.maximum_filter(score, size=(th, tw)))
	return [[int(x + tw // 2), int(y + th // 2)] for y, x in zip(*np.nonzero(peaks))]


def overlay(image, panels, buttons, path):
	draw = ImageDraw.Draw(image)
	for number, box in enumerate(panels, 1):
		draw.rectangle(box, outline=(255, 0, 0), width=3)
		draw.text((box[0] + 6, box[1] + 4), str(number), fill=(255, 255, 0))
	for x, y in buttons:
		draw.rectangle((x - 55, y - 12, x + 55, y + 12), outline=(0, 255, 0), width=3)
	image.resize((image.width // 2, image.height // 2)).save(path)


def main():
	parser = argparse.ArgumentParser(description="Click each Sevopedia category and record where its page's panels and EXPAND buttons are.")
	parser.add_argument("--pid", type=int, required=True, help="the Civ4 process, with the Sevopedia open at 1920x1080 windowed")
	parser.add_argument("--categories", nargs="*", help="category point names such as pedia_units; default all")
	parser.add_argument("--overlays", type=Path, help="folder for pictures of each page with its found panels numbered")
	parser.add_argument("--wait", type=float, default=2.5, help="seconds for a page to draw after a click")
	args = parser.parse_args()

	layout = json.loads(POINTS_FILE.read_text(encoding="utf-8"))["layouts"]["1080p-windowed"]
	names = args.categories or [name for name in layout["points"] if name.startswith("pedia_") and "category list" in layout["points"][name]["note"]]
	template = Image.open(TEMPLATE_FILE)
	data = json.loads(MAP_FILE.read_text(encoding="utf-8")) if MAP_FILE.is_file() else {}
	pages = data.setdefault("pages", {})
	if args.overlays:
		args.overlays.mkdir(parents=True, exist_ok=True)
	for name in names:
		# <!-- custom: The first trial run found "it4s brittl" in the Sevopedia's search box, filtering the entry list empty: the user's typing had landed in Civ4 after a click brought it forward.
		# So wait until the user has been idle before each click. (Claude Code Opus 5.5) -->
		if not desktop_windows.wait_for_idle_user(3.0, 120):
			sys.exit("the user kept typing or moving the mouse; stopped before %s" % name)
		before = capture(args.pid)
		x, y = layout["points"][name]["xy"]
		desktop_windows.click(args.pid, x, y)
		time.sleep(args.wait)
		desktop_windows.hover(args.pid, *IDLE_POINT)
		time.sleep(0.5)
		image = capture(args.pid)
		# <!-- custom: A click while another window was in front was once lost, as it only brought Civ4 forward; click again when the page did not change. (Claude Code Opus 5.5) -->
		if np.array_equal(np.asarray(before), np.asarray(image)):
			desktop_windows.click(args.pid, x, y)
			time.sleep(args.wait)
			desktop_windows.hover(args.pid, *IDLE_POINT)
			time.sleep(0.5)
			image = capture(args.pid)
		panels = find_panels(image)
		buttons = find_expand(image, template)
		pages[name] = {"panels": panels, "expand": buttons, "measured": time.strftime("%Y-%m-%d")}
		print("%s: %d panels, %d EXPAND" % (name, len(panels), len(buttons)))
		if args.overlays:
			overlay(image, panels, buttons, args.overlays / ("%s.png" % name))
	MAP_FILE.write_text(compact_json(data), encoding="utf-8", newline="\n")
	print("wrote %s" % MAP_FILE)


def compact_json(data):
	# <!-- custom: indent=1 put each number of a box on its own line, six lines per panel; on Codex's suggestion (2026-11-11), number-only lists go back on one line, so each box or button reads as one line, as in the other maps. (Claude Code Opus 5.5) -->
	text = json.dumps(data, indent=1, ensure_ascii=False)
	# <!-- custom: Match only actual multiline arrays.
	# Bracketed numbers inside JSON strings, such as "[1,2]", are data and must keep their original spacing. (GPT-6.1-Sol) -->
	return re.sub(r"\[\n +(-?\d+(?:,\n +-?\d+)*)\n +\]", lambda match: "[" + ", ".join(part.strip() for part in match.group(1).split(",")) + "]", text) + "\n"


if __name__ == "__main__":
	sys.exit(main())

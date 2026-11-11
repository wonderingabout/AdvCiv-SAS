#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Hovers a list of window points in turn and captures the area around each, then lays the captures out on sheets, so an agent can name many unlabelled buttons from their tooltips in a few reads.
# Written on 2026-11-11 to map Civ4's in-game interface, whose icon buttons carry no text; hovering moves only the pointer and needs no click, so nothing in the game changes. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; json reads named points; tempfile holds screenshots; time waits for tooltips; sys and pathlib handle exits and paths; PIL crops and lays out the captures. (Claude Code Opus 5.5) -->
import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageDraw

# <!-- custom: desktop_windows, beside this script, waits for the user, hovers and screenshots the window. (Claude Code Opus 5.5) -->
import desktop_windows


def parse_point(text):
	# <!-- custom: A point is LABEL=X,Y, so the sheet can name each capture. (Claude Code Opus 5.5) -->
	label, _, xy = text.partition("=")
	x, y = (int(v) for v in xy.split(","))
	return label, x, y


def main():
	parser = argparse.ArgumentParser(description="Hover window points in turn and save sheets of what appears around each, such as tooltips.")
	parser.add_argument("--pid", type=int, required=True)
	parser.add_argument("points", nargs="+", help="LABEL=X,Y window-relative points")
	parser.add_argument("--out", type=Path, required=True, help="folder for the sheets")
	parser.add_argument("--radius", type=int, nargs=2, default=(420, 300), metavar=("DX", "DY"), help="capture this far around each point")
	parser.add_argument("--wait", type=float, default=1.2, help="seconds for a tooltip to appear")
	parser.add_argument("--per-sheet", type=int, default=6)
	parser.add_argument("--scale", type=float, default=0.6)
	parser.add_argument("--area", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="capture this fixed window area instead of around each point; Civ4's main screen shows help text at the bottom left, so use 0 420 960 960 there")
	parser.add_argument("--front", action="store_true", help="bring the window to the front first; Civ4 showed no tooltips while another window was in front")
	args = parser.parse_args()

	if args.front:
		# <!-- custom: The first run on Civ4's main screen captured no tooltip at all while the Claude app was in front; Civ4, like its sound, reacts only while it is the foreground window.
		# This takes the focus from the user, so the idle wait comes first. (Claude Code Opus 5.5) -->
		desktop_windows.wait_for_idle_user(3.0, 120)
		desktop_windows.make_dpi_aware()
		desktop_windows.bring_to_front(desktop_windows.find_window(args.pid), args.pid)
		time.sleep(0.8)

	args.out.mkdir(parents=True, exist_ok=True)
	shot = Path(tempfile.gettempdir()) / "hover_tooltips_shot.png"
	captures = []
	for text in args.points:
		label, x, y = parse_point(text)
		if not desktop_windows.wait_for_idle_user(2.0, 120):
			sys.exit("the user kept typing or moving the mouse; stopped before %s" % label)
		desktop_windows.hover(args.pid, x, y)
		time.sleep(args.wait)
		desktop_windows.screenshot(args.pid, shot)
		image = Image.open(shot).convert("RGB")
		# <!-- custom: Civ4's main screen draws help text in a fixed spot above the unit panel, growing upwards, not next to the pointer: hovering the first advisor button showed "Domestic Advisor <F1>" near (100, 910).
		# So a fixed area can be captured instead of the pointer's surroundings. (Claude Code Opus 5.5) -->
		if args.area:
			box = tuple(args.area)
		else:
			dx, dy = args.radius
			box = (max(0, x - dx), max(0, y - dy), min(image.width, x + dx), min(image.height, y + dy))
		crop = image.crop(box)
		draw = ImageDraw.Draw(crop)
		if box[0] <= x < box[2] and box[1] <= y < box[3]:
			draw.ellipse((x - box[0] - 5, y - box[1] - 5, x - box[0] + 5, y - box[1] + 5), outline=(255, 0, 255), width=2)
		crop = crop.resize((int(crop.width * args.scale), int(crop.height * args.scale)))
		captures.append((label, crop))
	for start in range(0, len(captures), args.per_sheet):
		group = captures[start:start + args.per_sheet]
		width = max(c.width for _, c in group)
		height = max(c.height for _, c in group)
		cols = min(3, len(group))
		rows = (len(group) + cols - 1) // cols
		sheet = Image.new("RGB", (cols * (width + 8), rows * (height + 20)), "white")
		draw = ImageDraw.Draw(sheet)
		for i, (label, crop) in enumerate(group):
			px, py = (i % cols) * (width + 8), (i // cols) * (height + 20)
			draw.text((px + 2, py + 2), label, fill=(0, 0, 0))
			sheet.paste(crop, (px, py + 18))
		path = args.out / ("sheet_%02d.png" % (start // args.per_sheet + 1))
		sheet.save(path)
		print("wrote %s: %s" % (path, ", ".join(label for label, _ in group)))


if __name__ == "__main__":
	main()

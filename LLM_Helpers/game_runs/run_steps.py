#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Runs a list of UI steps on a window (click, key, hover, type, scroll, wait), capturing it after each and laying the captures out on one labelled sheet, so a sequence can be checked in a single image read.
# During the 2026-11-11/12 Civ4 mapping the agent kept writing this loop inline; one batch waited for the user to be idle only once, and its later clicks hit the main map after the user moved the mouse, so this waits before every step. (Claude Code Opus 5.5) -->

# <!-- custom: argparse parses the options, math validates durations and time paces the steps.
# pathlib and tempfile handle capture and output paths, PIL draws the sheet, and desktop_windows sends input and captures the window. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
import argparse
import math
import tempfile
import time
from pathlib import Path

# <!-- custom: Pillow opens the individual captures and draws the labelled sheet. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
from PIL import Image, ImageDraw

import desktop_windows as d


def parse_step(text):
	# <!-- custom: Validate the whole batch before sending input.
	# An unknown click flag must fail instead of turning a planned modifier click into a plain click. (GPT-6.1-Sol) -->
	kind, separator, rest = text.partition(":")
	if not separator or not rest:
		raise ValueError("expected KIND:ARGUMENTS")
	if kind == "click":
		x, y, *flags = rest.split(",")
		if len(flags) != len(set(flags)) or any(flag != "double" and flag not in d.MODIFIER_VKS for flag in flags):
			raise ValueError("expected distinct ctrl, shift, alt or double flags")
		modifiers = tuple(d.MODIFIER_VKS[flag] for flag in flags if flag != "double")
		return kind, (int(x), int(y), modifiers, "double" in flags)
	if kind == "key":
		d.parse_key(rest)
		return kind, (rest,)
	if kind == "hover":
		x, y = rest.split(",")
		return kind, (int(x), int(y))
	if kind == "scroll":
		x, y, clicks = rest.split(",")
		return kind, (int(x), int(y), int(clicks))
	if kind == "type":
		return kind, (rest,)
	if kind == "wait":
		seconds = float(rest)
		if not math.isfinite(seconds) or seconds < 0:
			raise ValueError("wait requires a finite non-negative duration")
		return kind, (seconds,)
	raise ValueError("unknown step kind %r" % kind)


def run(pid, kind, values):
	if kind == "click":
		d.click(pid, *values)
	elif kind == "key":
		d.key(pid, *values, hold=0.5)
	elif kind == "hover":
		d.hover(pid, *values)
	elif kind == "type":
		d.type_text(pid, *values)
	elif kind == "scroll":
		d.scroll(pid, *values)
	elif kind == "wait":
		time.sleep(*values)


def write_sheet(shots, columns, output):
	# <!-- custom: Size the grid from every capture because a window can resize between steps.
	# Draw each label in its own strip so a long label cannot overwrite its neighbour. (GPT-6.1-Sol) -->
	sizes = []
	for _, path in shots:
		with Image.open(path) as image:
			sizes.append(image.size)
	width = max(240, max(w for w, _ in sizes))
	height = max(h for _, h in sizes)
	label_height = 20
	columns = min(columns, len(shots))
	rows = (len(shots) + columns - 1) // columns
	with Image.new("RGB", (width * columns, (height + label_height) * rows), "white") as sheet:
		for index, (label, path) in enumerate(shots):
			x = index % columns * width
			y = index // columns * (height + label_height)
			with Image.new("RGB", (width, label_height), "white") as strip:
				ImageDraw.Draw(strip).text((3, 3), label, fill="red")
				sheet.paste(strip, (x, y))
			with Image.open(path) as image:
				sheet.paste(image, (x, y + label_height))
		sheet.save(output, format="PNG")


def main():
	parser = argparse.ArgumentParser(description="Run UI steps on a window, waiting for the user to be idle before each, and save one sheet of a capture after each step.")
	parser.add_argument("--pid", type=int, required=True)
	parser.add_argument("--out", type=Path, required=True, help="sheet PNG to write")
	parser.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="capture only this window-relative area")
	parser.add_argument("--scale", type=float, default=0.4)
	parser.add_argument("--settle", type=float, default=1.2, help="seconds to wait after a step before capturing")
	parser.add_argument("--park", type=int, nargs=2, metavar=("X", "Y"), help="optional pointer position before capturing clicks, keys, text or scrolling")
	parser.add_argument("--columns", type=int, default=3)
	parser.add_argument("--idle-seconds", type=float, default=3.0)
	parser.add_argument("steps", nargs="+", help="click:X,Y[,ctrl|shift|alt|double], key:NAME, hover:X,Y, type:TEXT, scroll:X,Y,CLICKS, wait:SECONDS")
	args = parser.parse_args()
	if args.pid < 1 or args.columns < 1:
		parser.error("--pid and --columns must be positive")
	if not 0 < args.scale <= 1:
		parser.error("--scale must be greater than zero and at most one")
	if any(not math.isfinite(value) or value < 0 for value in (args.settle, args.idle_seconds)):
		parser.error("--settle and --idle-seconds must be finite and non-negative")
	if args.crop:
		left, top, right, bottom = args.crop
		if not (0 <= left < right and 0 <= top < bottom):
			parser.error("--crop must have non-negative coordinates and positive dimensions")
	steps = []
	for text in args.steps:
		try:
			steps.append(parse_step(text))
		except (ValueError, KeyError) as exc:
			parser.error("invalid step %r: %s" % (text, exc))
	args.out.parent.mkdir(parents=True, exist_ok=True)
	if args.out.is_dir():
		parser.error("--out names a directory")
	# <!-- custom: Keep intermediate captures in a temporary directory so a run only writes its requested sheet and cannot replace neighbouring PNGs. (GPT-6.1-Sol) -->
	with tempfile.TemporaryDirectory(prefix="sas_ui_steps_") as folder:
		shots = []
		for index, (kind, values) in enumerate(steps, start=1):
			if not d.wait_for_idle_user(args.idle_seconds, 300):
				parser.exit(1, "the user stayed active; stopped before step %d\n" % index)
			run(args.pid, kind, values)
			time.sleep(args.settle)
			# <!-- custom: Parking also moves the real pointer, so it is opt-in and waits again if requested.
			# Keep a hover's tooltip in its own capture. (GPT-6.1-Sol) -->
			if args.park and kind not in ("hover", "wait") and d.wait_for_idle_user(args.idle_seconds, 300):
				d.hover(args.pid, *args.park)
				time.sleep(0.3)
			path = Path(folder) / ("%02d.png" % index)
			d.screenshot(args.pid, path, "window", args.crop, args.scale)
			shots.append(("%d %s" % (index, args.steps[index - 1]), path))
		write_sheet(shots, args.columns, args.out)
	print("wrote %s: %d steps" % (args.out, len(shots)))


if __name__ == "__main__":
	main()

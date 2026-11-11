#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Clicks named Civ4 points from civ4_points.json one after another and reports how much of the window changed after each, so a point list can be re-checked after a resolution or UI change.
# Written on 2026-11-11 when the Sevopedia's bottom bar was still untested; checking by hand meant a screenshot and a look per button. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; tempfile holds screenshots; time waits for the game; sys and pathlib handle exits and paths; numpy compares screenshots; PIL reads and shrinks them. (Claude Code Opus 5.5) -->
import argparse
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

# <!-- custom: desktop_windows, beside this script, waits for the user to be idle, clicks named points and screenshots the window. (Claude Code Opus 5.5) -->
import desktop_windows

IDLE_POINT = (1500, 1100)


def capture(pid):
	path = Path(tempfile.gettempdir()) / "check_points_shot.png"
	desktop_windows.screenshot(pid, path)
	return Image.open(path).convert("RGB")


def main():
	parser = argparse.ArgumentParser(description="Click named Civ4 points in order and report how much of the window changed after each.")
	parser.add_argument("--pid", type=int, required=True)
	parser.add_argument("points", nargs="+", help="point names from civ4_points.json, clicked in this order")
	parser.add_argument("--wait", type=float, default=2.0, help="seconds for the game to react to a click")
	parser.add_argument("--pictures", type=Path, help="folder for a small picture of the window after each click")
	args = parser.parse_args()

	if args.pictures:
		args.pictures.mkdir(parents=True, exist_ok=True)
	for step, name in enumerate(args.points, 1):
		# <!-- custom: The user's typing landed in the Sevopedia's search box once a click brought Civ4 forward, so wait until they have been idle; simulated clicks count as input too, so this only guards the moment before each click. (Claude Code Opus 5.5) -->
		if not desktop_windows.wait_for_idle_user(3.0, 120):
			sys.exit("the user kept typing or moving the mouse; stopped before %s" % name)
		before = np.asarray(capture(args.pid)).astype(int)
		x, y = desktop_windows.named_point(args.pid, name)
		desktop_windows.click(args.pid, x, y)
		time.sleep(args.wait)
		desktop_windows.hover(args.pid, *IDLE_POINT)
		time.sleep(0.5)
		image = capture(args.pid)
		after = np.asarray(image).astype(int)
		if before.shape != after.shape:
			print("%d %s: the window changed size to %dx%d" % (step, name, image.width, image.height))
		else:
			changed = (np.abs(before - after).sum(axis=2) > 30).mean() * 100
			print("%d %s: %.1f%% of the window changed" % (step, name, changed))
		if args.pictures:
			image.resize((image.width // 4, image.height // 4)).save(args.pictures / ("%02d_%s.png" % (step, name)))


if __name__ == "__main__":
	main()

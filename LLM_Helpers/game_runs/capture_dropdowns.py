#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Opens each dropdown of a Civ4 screen, captures its list page by page while scrolling it with the wheel, and closes it again without choosing anything, so an agent can read every option of the Custom Game screen from pictures.
# On 2026-11-11 a click on a dropdown's header opened its list below it, and a second click on the header closed it with the value unchanged; this script relies on that, and checks the header looks the same afterwards, so a changed setting is reported rather than missed. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; json reads the screen map; time waits for the game; sys and pathlib handle exits and paths; numpy compares pictures; PIL crops and saves them. (Claude Code Opus 5.5) -->
import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

# <!-- custom: desktop_windows, beside this script, waits for the user, clicks, scrolls and screenshots the Civ4 window. (Claude Code Opus 5.5) -->
import desktop_windows

UI_MAP = Path(__file__).resolve().parent / "ui_maps" / "civ4_ui_map.json"
IDLE_POINT = (1500, 1100)


def capture(pid, box):
	path = Path(tempfile.gettempdir()) / "capture_dropdowns_shot.png"
	desktop_windows.screenshot(pid, path, crop=box)
	return Image.open(path).convert("RGB")


def main():
	parser = argparse.ArgumentParser(description="Open each dropdown listed for a screen in civ4_ui_map.json, capture its whole list while scrolling, and close it unchanged.")
	parser.add_argument("--pid", type=int, required=True)
	parser.add_argument("--screen", default="custom_game", help="screen in civ4_ui_map.json whose 'dropdowns' to capture")
	parser.add_argument("--only", nargs="*", help="dropdown names to capture; default all")
	parser.add_argument("--out", type=Path, required=True, help="folder for the pictures")
	parser.add_argument("--max-pages", type=int, default=20)
	args = parser.parse_args()

	screen = json.loads(UI_MAP.read_text(encoding="utf-8"))["screens"][args.screen]
	args.out.mkdir(parents=True, exist_ok=True)
	for name, dropdown in screen["dropdowns"].items():
		if args.only and name not in args.only:
			continue
		x, y = dropdown["xy"]
		left, right = dropdown["span"]
		header = (left, y - 14, right, y + 14)
		# <!-- custom: The list opened below the header for the Size dropdown; capturing 520 px above and below also covers a list that opens upwards near the bottom of the window. (Claude Code Opus 5.5) -->
		area = (left, max(40, y - 520), right, min(1110, y + 520))
		if not desktop_windows.wait_for_idle_user(3.0, 120):
			sys.exit("the user kept typing or moving the mouse; stopped before %s" % name)
		header_before = np.asarray(capture(args.pid, header)).astype(int)
		desktop_windows.click(args.pid, x, y)
		time.sleep(1.5)
		pages = []
		for page in range(1, args.max_pages + 1):
			image = capture(args.pid, area)
			if pages and np.array_equal(np.asarray(image), np.asarray(pages[-1])):
				break
			pages.append(image)
			image.save(args.out / ("%s_%02d.png" % (name, page)))
			desktop_windows.scroll(args.pid, x, min(1100, y + 120), -3)
			time.sleep(0.8)
		desktop_windows.click(args.pid, x, y)
		time.sleep(1.5)
		desktop_windows.hover(args.pid, *IDLE_POINT)
		time.sleep(0.5)
		header_after = np.asarray(capture(args.pid, header)).astype(int)
		# <!-- custom: The first full run warned on all six settings although none had changed: a clicked header stays lit, which shifts its colours.
		# Comparing only its dark text pixels ignores that tint but still sees a different value. (Claude Code Opus 5.5) -->
		text_before = header_before.sum(axis=2) < 240
		text_after = header_after.sum(axis=2) < 240
		same = (text_before != text_after).mean() < 0.01
		print("%s: %d page(s)%s" % (name, len(pages), "" if same else "; WARNING: the header changed, so the value may have changed"))


if __name__ == "__main__":
	main()

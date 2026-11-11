#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Chooses an item in a Civ4 dropdown by its name, using the item lists and list layout recorded in civ4_ui_map.json, so an agent can set up a custom game without reading the list each time.
# Written on 2026-11-11 to compare map scripts' own options on the Custom Game screen; the list layout came from capture_dropdowns.py: 10 items visible, about 26 px apart, the first 35 px below the header, and 3 wheel clicks scroll by 9 items. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; json reads the screen map; time waits for the game; sys, tempfile and pathlib handle exits and files; numpy compares the header before and after. (Claude Code Opus 5.5) -->
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
VISIBLE = 10
STEP = 26
FIRST = 35
PAGE = 9


def header_text(pid, dropdown):
	x, y = dropdown["xy"]
	left, right = dropdown["span"]
	path = Path(tempfile.gettempdir()) / "set_dropdown_header.png"
	desktop_windows.screenshot(pid, path, crop=(left, y - 14, right, y + 14))
	return np.asarray(Image.open(path).convert("RGB")).astype(int).sum(axis=2) < 240


def choose(pid, dropdown, item):
	items = dropdown["items"]
	if item not in items:
		sys.exit("%r is not in this dropdown; known: %s" % (item, ", ".join(items)))
	index = items.index(item)
	x, y = dropdown["xy"]
	# <!-- custom: The list's top item after k pages is 9k, but the last page stops at the end of the list, so the top can be no later than len - 10. (Claude Code Opus 5.5) -->
	last_top = max(0, len(items) - VISIBLE)
	pages = 0
	while min(PAGE * pages, last_top) + VISIBLE - 1 < index:
		pages += 1
	top = min(PAGE * pages, last_top)
	before = header_text(pid, dropdown)
	desktop_windows.click(pid, x, y)
	time.sleep(1.2)
	# <!-- custom: A dropdown opens scrolled to its current item, so counting pages from the top picked Shuffle instead of SAS_Longworld while Earth2 was selected; scrolling the list fully up first makes the count start at item 0. (Claude Code Opus 5.5) -->
	desktop_windows.scroll(pid, x, y + 120, 30)
	time.sleep(0.6)
	for _ in range(pages):
		desktop_windows.scroll(pid, x, y + 120, -3)
		time.sleep(0.6)
	desktop_windows.click(pid, x, y + FIRST + STEP * (index - top))
	time.sleep(2.0)
	desktop_windows.hover(pid, 1500, 1100)
	time.sleep(0.5)
	return (before != header_text(pid, dropdown)).mean() > 0.01


def main():
	parser = argparse.ArgumentParser(description="Choose an item by name in a dropdown recorded in civ4_ui_map.json.")
	parser.add_argument("--pid", type=int, required=True)
	parser.add_argument("--screen", default="custom_game")
	parser.add_argument("dropdown", help="such as map, size or row1_leader")
	parser.add_argument("item", help="the item's name exactly as listed, such as Pangaea")
	args = parser.parse_args()
	ui_map = json.loads(UI_MAP.read_text(encoding="utf-8"))
	dropdown = ui_map["screens"][args.screen]["dropdowns"][args.dropdown]
	if not desktop_windows.wait_for_idle_user(3.0, 120):
		sys.exit("the user kept typing or moving the mouse; nothing chosen")
	# <!-- custom: The row coordinates were measured at one outer window size, and a changed header alone cannot identify the resulting selection. (GPT-6.1-Sol) -->
	desktop_windows.make_dpi_aware()
	hwnd = desktop_windows.find_window(args.pid)
	if hwnd is None:
		sys.exit("no visible window for process %d" % args.pid)
	left, top, right, bottom = desktop_windows.window_rect(hwnd)
	size = (right - left, bottom - top)
	expected = tuple(ui_map["window"])
	if size != expected:
		sys.exit("dropdown map needs a %dx%d window; target is %dx%d" % (expected + size))
	changed = choose(args.pid, dropdown, args.item)
	print("clicked the mapped row for %s in %s; header %s. Verify the displayed item." %
		(args.item, args.dropdown, "changed" if changed else "did not change"))


if __name__ == "__main__":
	main()

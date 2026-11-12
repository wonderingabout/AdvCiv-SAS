# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Starts a QuickStart game at turn 0 with a chosen map script, world size and game options, through a per-run copy of the INI, and leaves it open for an agent to drive; the user's CivilizationIV.ini and Custom Game choices stay untouched.
# Written on 2026-11-12 to map WorldBuilder on a 48-player SAS48 map and the Advanced Start screen, which need a fresh game with settings the autoplay runner does not set. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, os, re and time for the run, Path for files. (Claude code Opus 5.5) -->
import argparse
import os
import re
import time
from pathlib import Path

# <!-- custom: Pillow compares captures; desktop_windows launches and drives Civ4, run_autoplay writes the INI copy. (Claude code Opus 5.5) -->
from PIL import Image, ImageChops, ImageStat

import desktop_windows as d
import run_autoplay

REPO = Path(__file__).resolve().parents[2]
GAME_OPTIONS_XML = REPO / "Assets" / "XML" / "GameInfo" / "CIV4GameOptionInfos.xml"


def game_options(base: str, names: list[str]) -> str:
	# <!-- custom: The INI's GameOptions holds one digit per option in CIV4GameOptionInfos.xml order, so GAMEOPTION_ADVANCED_START, the first, is its first digit. (Claude code Opus 5.5) -->
	order = re.findall(r"<Type>(GAMEOPTION_[A-Z0-9_]+)</Type>", GAME_OPTIONS_XML.read_text(encoding="utf-8"))
	digits = list(base.ljust(len(order), "0"))
	for name in names:
		if name not in order:
			raise SystemExit("unknown game option %s" % name)
		digits[order.index(name)] = "1"
	return "".join(digits)


def wait_until_settled(pid: int, timeout: float = 600) -> None:
	# <!-- custom: Ready once the window is full size and two captures 3 s apart barely differ, at least 15 s after launch; a minimap test would not do, as Advanced Start starts with an almost empty one. (Claude code Opus 5.5) -->
	scratch = REPO / "LLM_Helpers" / "outputs"
	scratch.mkdir(parents=True, exist_ok=True)
	time.sleep(15)
	end = time.monotonic() + timeout
	previous = None
	while time.monotonic() < end:
		time.sleep(3)
		if not d.process_alive(pid):
			raise SystemExit("Civ4 exited while loading")
		hwnd = d.find_window(pid)
		if not hwnd:
			continue
		left, top, right, bottom = d.window_rect(hwnd)
		if right - left < 1000:
			continue
		d.screenshot(pid, scratch / ("start_game_%d.png" % pid))
		image = Image.open(scratch / ("start_game_%d.png" % pid)).convert("L").resize((240, 140))
		if previous is not None and ImageStat.Stat(ImageChops.difference(image, previous)).mean[0] < 1.5:
			(scratch / ("start_game_%d.png" % pid)).unlink(missing_ok=True)
			return
		previous = image
	raise SystemExit("the game did not settle within %d s" % timeout)


def start(script: str, world_size: str, options: list[str], debug_mode: bool, ini_prefix: str = "SASStart") -> tuple[int, Path]:
	base_ini = run_autoplay.USER_DIR / "CivilizationIV.ini"
	current = re.search(r"(?mi)^\s*GameOptions\s*=\s*(\d+)", base_ini.read_bytes().decode("latin-1"))
	settings = {"QuickStart": "1", "Map": script, "WorldSize": world_size}
	if options:
		settings["GameOptions"] = game_options(current.group(1) if current else "", options)
	ini_name = "%s_%s_%d.ini" % (ini_prefix, time.strftime("%Y%m%dT%H%M%S"), os.getpid())
	ini_path = d.DEFAULT_CIV4_DIR / ini_name
	# <!-- custom: No [SASAutoplay] request, so the game waits at turn 0. (Claude code Opus 5.5) -->
	run_autoplay.write_request_ini(base_ini, ini_path, None, False, "-", "Agent", settings)
	# <!-- custom: Codex simulated a timeout here, which left the client running and its INI behind; a failed start now closes this run's own client and removes its INI and .bak before the error goes on.
	# The launch itself sits inside the try too, with pid set only once it succeeds: Codex then made launch_detached raise, and the INI stayed behind. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	pid = None
	try:
		pid = d.launch_detached("ini=%s" % ini_name)
		wait_until_settled(pid)
		if debug_mode:
			d.key(pid, "ctrl+z")
			time.sleep(3)
	except BaseException:
		try:
			if pid is not None and d.process_alive(pid):
				run_autoplay.close_civ4(pid)
		finally:
			for leftover in (ini_path, ini_path.with_name(ini_path.name + ".bak")):
				leftover.unlink(missing_ok=True)
		raise
	return pid, ini_path


def main() -> int:
	parser = argparse.ArgumentParser(description="Start a QuickStart game at turn 0 with a map script, world size and game options, and leave it open.")
	parser.add_argument("--map", default="Pangaea")
	parser.add_argument("--world-size", default="WORLDSIZE_STANDARD")
	parser.add_argument("--option", action="append", default=[], help="Turn on a game option by type, such as GAMEOPTION_ADVANCED_START; repeatable")
	parser.add_argument("--debug-mode", action="store_true", help="Press Ctrl+Z once the game is up, to reveal the map")
	args = parser.parse_args()
	if d.civ4_processes():
		raise SystemExit("Civ4 is already running: drive it with --pid in the other tools, or close it first")
	pid, ini_path = start(args.map, args.world_size, args.option, args.debug_mode)
	print("pid %d; per-run INI %s (delete it, and its .bak, after closing the game)" % (pid, ini_path))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Starts a QuickStart game at turn 0 with a chosen map script, world size and game options, through a per-run copy of the INI, and leaves it open for an agent to drive; the user's CivilizationIV.ini and Custom Game choices stay untouched.
# Written on 2026-11-12 to map WorldBuilder on a 48-player SAS48 map and the Advanced Start screen, which need a fresh game with settings the autoplay runner does not set. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, os, re and time for the run, Path for files; json reads the runtime status that confirms a --load. (Claude code Opus 5.5) -->
import argparse
import json
import os
import re
import time
from pathlib import Path

# <!-- custom: Pillow compares captures; desktop_windows launches and drives Civ4, run_autoplay writes the INI copy. (Claude code Opus 5.5) -->
from PIL import Image, ImageChops, ImageStat

# <!-- custom: desktop_windows moved to LLM_Helpers/desktop on 2026-11-15, as it drives any app's windows, not only Civ4's, so its folder joins the import path. (Claude code Opus 5.5) -->
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
import desktop_windows as d
import run_autoplay

REPO = Path(__file__).resolve().parents[2]
# <!-- custom: game_options moved to run_autoplay.py on 2026-11-19, so its --option for autoplayed games shares this one copy. (Claude code Opus 5.5) -->
game_options = run_autoplay.game_options


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


# <!-- custom: Gained mod, AdvCiv-SAS by default so earlier callers start the same game, to start another mod such as base AdvCiv and compare a screen with SAS's (2026-11-23). See KI#1107. (Claude code Opus 5.5) -->
# <!-- custom: Gained size, None by default so earlier callers keep the profile's resolution, to start a game at a chosen resolution (2026-11-24). See KI#123.4. (Claude code Opus 5.5) -->
def start(script: str, world_size: str, options: list[str], debug_mode: bool, ini_prefix: str = "SASStart", era: str | None = None, mod: str = "AdvCiv-SAS", size: str | None = None) -> tuple[int, Path]:
	base_ini = run_autoplay.USER_DIR / "CivilizationIV.ini"
	current = re.search(r"(?mi)^\s*GameOptions\s*=\s*(\d+)", base_ini.read_bytes().decode("latin-1"))
	settings = {"QuickStart": "1", "Map": script, "WorldSize": world_size}
	# <!-- custom: The INI's QuickStart section takes Era like Map and WorldSize; added on 2026-11-19 for a later-era sample of the scoreboard and advisors, as older late-game saves no longer loaded. (Claude code Opus 5.5) -->
	if era:
		settings["Era"] = era
	# <!-- custom: Added on 2026-11-24 to compare a game started at one resolution with one switched to it during play, as map_preview_dds.py sets its size. See KI#123.4. (Claude code Opus 5.5) -->
	if size:
		width, height = size.lower().split("x")
		settings["ScreenWidth"] = str(int(width))
		settings["ScreenHeight"] = str(int(height))
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
		# <!-- custom: mod= picks the mod, as for a save; added on 2026-11-23 to start base AdvCiv and compare a screen with SAS's, the game font display.
		# Quoted whole, as capture_screens.py does, since --list-mods shows names with spaces such as "AdvCiv Plus" (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		pid = d.launch_detached('ini=%s "mod=\\%s"' % (ini_name, mod))
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


# <!-- custom: Gained mod, AdvCiv-SAS by default, as start did, for a save of another mod (2026-11-23). See KI#1107. (Claude code Opus 5.5) -->
def load(save: Path, debug_mode: bool, mod: str = "AdvCiv-SAS") -> int:
	# <!-- custom: Loads a save into AdvCiv-SAS and leaves it open, with no autoplay, so a fix can be checked on the very position a bug was seen in; run_autoplay.py --turns 1 would play that turn first.
	# Written on 2026-11-22 to check KI#11.3 on the user's turn-22 save, after a hand-typed launch failed: "mod=\AdvCiv-SAS" passed through python -c in Bash lost its backslash (Win32_Process.Create failed: 9), the pitfall AGENTS.md describes, so the arguments are built here.
	# /FXSLOAD comes first and quoted, as run_autoplay.py found; mod= names the mod, as the save alone does not pick it. (Claude code Opus 5.5) -->
	# <!-- custom: Resolved first, as Civ4 starts in the game folder: a relative path that existed here would load nothing there (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	save = save.resolve()
	if not save.is_file():
		raise SystemExit("no save at %s" % save)
	pid = d.launch_detached('/FXSLOAD="%s" "mod=\\%s"' % (save, mod))
	try:
		wait_until_settled(pid)
		# <!-- custom: A settled window can also be the main menu or an error dialog, so the load is confirmed from this process's own runtime status when SAS_RUNTIME_STATUS_ON writes one (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		statuses = sorted(run_autoplay.USER_DIR.joinpath("Logs").glob("SASRuntimeStatus_*_%d.json" % pid))
		if statuses:
			status = json.loads(statuses[-1].read_text(encoding="utf-8"))
			if status.get("sessionKind") != "LOAD_GAME" or status.get("gameState") != "PLAYING":
				raise RuntimeError("Civ4 settled without a loaded game: sessionKind=%s gameState=%s" % (status.get("sessionKind"), status.get("gameState")))
		else:
			print("warning: no runtime status for pid %d (SAS_RUNTIME_STATUS_ON is off), so the load was not confirmed; check the window" % pid)
		if debug_mode:
			d.key(pid, "ctrl+z")
			time.sleep(3)
	except BaseException:
		if d.process_alive(pid):
			run_autoplay.close_civ4(pid)
		raise
	return pid


def main() -> int:
	parser = argparse.ArgumentParser(description="Start a QuickStart game at turn 0 with a map script, world size and game options, or load a save, and leave it open.")
	parser.add_argument("--load", type=Path, metavar="SAVE", help="load this .CivBeyondSwordSave instead of starting a game; --debug-mode still applies, the other options do not")
	parser.add_argument("--map", default="Pangaea")
	parser.add_argument("--world-size", default="WORLDSIZE_STANDARD")
	parser.add_argument("--option", action="append", default=[], help="Turn on a game option by type, such as GAMEOPTION_ADVANCED_START; repeatable")
	parser.add_argument("--debug-mode", action="store_true", help="Press Ctrl+Z once the game is up, to reveal the map")
	parser.add_argument("--era", help="Starting era by type, such as ERA_INDUSTRIAL; the INI's own by default")
	parser.add_argument("--mod", default="AdvCiv-SAS", help="Mod folder name, such as AdvCiv for base AdvCiv to compare a screen; AdvCiv-SAS by default")
	parser.add_argument("--size", metavar="WxH", help="Start at this resolution, such as 1920x1080, through the run's INI copy; the profile's own by default")
	parser.add_argument("--list-mods", action="store_true", help="list the installed mods' folder names, for --mod, and exit")
	args = parser.parse_args()
	# <!-- custom: The mod folders hold archives and backups beside the mods, so only folders with an Assets folder are listed, the ones Civ4 can load (the user's idea, 2026-11-23).
	# Read from the Civ4 install that launch_detached starts, not the repository's parent, which is elsewhere in a worktree (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if args.list_mods:
		for folder in sorted((d.DEFAULT_CIV4_DIR / "Mods").iterdir(), key=lambda p: p.name.lower()):
			if (folder / "Assets").is_dir():
				print(folder.name)
		return 0
	if d.civ4_processes():
		raise SystemExit("Civ4 is already running: drive it with --pid in the other tools, or close it first")
	if args.load:
		print("pid %d; loaded %s" % (load(args.load, args.debug_mode, args.mod), args.load))
		return 0
	pid, ini_path = start(args.map, args.world_size, args.option, args.debug_mode, era=args.era, mod=args.mod, size=args.size)
	print("pid %d; per-run INI %s (delete it, and its .bak, after closing the game)" % (pid, ini_path))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

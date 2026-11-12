# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Launches Civ4 into a mod, optionally at another resolution or in fullscreen, runs named-point or x,y clicks and saves screenshots where asked, then closes its own client; its settings go into a per-run INI, never the user's. Grew out of the 2026-11-12 setup-screen tests (KI#1082), whose one-off scripts each redid the same launch, INI and cleanup steps. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, os for the run's PID, re to edit the INI copy, subprocess to call desktop_windows.py, sys for the exit code. (Claude code Opus 5.5) -->
import argparse
import os
import re
import subprocess
import sys
# <!-- custom: time paces the steps, Path finds files; desktop_windows provides launching and window lookups. (Claude code Opus 5.5) -->
import time
from pathlib import Path

import desktop_windows as d

INI = Path.home() / "Documents" / "My Games" / "beyond the sword" / "CivilizationIV.ini"
TOOL = str(Path(__file__).with_name("desktop_windows.py"))


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Launch Civ4 into a mod, run clicks and capture screens, then close it; the user's INI is not changed.", epilog="Steps: point:SCREEN.CONTROL, click:X,Y, hover:X,Y and drag:X1,Y1,X2,Y2 (window-relative physical pixels, as in screenshots), key:NAME such as ctrl+w, shot:NAME, wait:SECONDS. Example: point:main_menu.single_player point:single_player.simple_game shot:maps")
	parser.add_argument("--out", required=True, help="Folder for the screenshots, saved as NAME.png")
	parser.add_argument("--mod", default="AdvCiv-SAS", help="Mod folder name (default AdvCiv-SAS)")
	parser.add_argument("--size", metavar="WxH", help="Set ScreenWidth and ScreenHeight in this run's copy of CivilizationIV.ini, such as 2560x1380")
	parser.add_argument("--fullscreen", action="store_true", help="Set FullScreen = 1 in this run's INI; it switches the monitor's mode")
	parser.add_argument("--multiple", action="store_true", help="Start as an extra client with Civ4's multiple option, beside one already running")
	parser.add_argument("--maximize", type=int, metavar="MONITOR", help="Fit the window to this monitor's work area before the steps, so a window as large as the screen clears the taskbar")
	parser.add_argument("--pid", type=int, help="Drive this running client instead of starting one, such as the user's idle window; it is left open, and the INI options do not apply")
	parser.add_argument("--keep-open", action="store_true", help="Leave this run's client open after the steps, to continue with --pid; a failed run is still closed")
	parser.add_argument("--settle", type=float, default=3.0, help="Seconds to wait after each click (default 3)")
	parser.add_argument("steps", nargs="+")
	return parser.parse_args()


def set_ini(text: bytes, key: str, value: str) -> bytes:
	text, count = re.subn((r"(?mi)^(%s\s*=\s*)\S+" % key).encode(), lambda m: m.group(1) + value.encode(), text)
	if count != 1:
		raise SystemExit("CivilizationIV.ini has %d '%s' lines, expected 1" % (count, key))
	return text


def tool(*args: str) -> None:
	result = subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True)
	if result.returncode:
		raise RuntimeError("desktop_windows.py %s failed: %s" % (" ".join(args), result.stderr.strip().splitlines()[-1:]))


def run_steps(pid: int, args: argparse.Namespace, out: Path) -> None:
	for step in args.steps:
		kind, _, value = step.partition(":")
		if kind == "point":
			tool("click", "--pid", str(pid), "--idle-seconds", "2", "--point", value)
			time.sleep(args.settle)
		elif kind == "click":
			x, y = value.split(",")
			tool("click", "--pid", str(pid), "--idle-seconds", "2", x, y)
			time.sleep(args.settle)
		elif kind == "hover":
			x, y = value.split(",")
			tool("hover", "--pid", str(pid), x, y)
			time.sleep(args.settle)
		elif kind == "drag":
			# <!-- custom: Added on 2026-11-12 to enlarge WorldBuilder's mode panels by their bottom-right grip, so their lists show without scrolling. (Claude code Opus 5.5) -->
			x1, y1, x2, y2 = value.split(",")
			tool("drag", "--pid", str(pid), "--idle-seconds", "2", x1, y1, x2, y2)
			time.sleep(args.settle)
		elif kind == "key":
			tool("key", "--pid", str(pid), value)
			time.sleep(args.settle)
		elif kind == "shot":
			tool("screenshot", "--pid", str(pid), "--out", str(out / (value + ".png")))
			print("saved", out / (value + ".png"))
		elif kind == "wait":
			time.sleep(float(value))
		else:
			raise SystemExit("unknown step: %s" % step)


def main() -> int:
	args = parse_args()
	out = Path(args.out)
	out.mkdir(parents=True, exist_ok=True)
	if args.pid:
		# <!-- custom: The user allows driving their idle window instead of starting another client (2026-11-12); it is theirs, so it is left open and its INI untouched. (Claude code Opus 5.5) -->
		if args.size or args.fullscreen or args.multiple:
			raise SystemExit("--size, --fullscreen and --multiple apply only to a client this script starts, not to --pid")
		if args.pid not in [p for p, _ in d.civ4_processes()]:
			raise SystemExit("no Civ4 process %d" % args.pid)
		if args.maximize:
			tool("move", "--pid", str(args.pid), "--monitor", str(args.maximize), "full")
			time.sleep(4)
		run_steps(args.pid, args, out)
		return 0
	if d.civ4_processes() and not args.multiple:
		raise SystemExit("Civ4 is already running: drive it with --pid, as AGENTS.md asks, or close it first; --multiple starts a second client only when two are needed")
	# <!-- custom: The run's settings go into its own copy of the INI, passed with ini= as run_autoplay.py does, so the user's CivilizationIV.ini is never written.
	# The first version edited the user's INI and restored it afterwards, but a failure while closing could skip the restore, and with --multiple it rewrote the INI of a client already running. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	text = INI.read_bytes()
	if args.size:
		width, height = args.size.lower().split("x")
		text = set_ini(set_ini(text, "screenwidth", width), "screenheight", height)
	text = set_ini(text, "fullscreen", "1" if args.fullscreen else "0")
	ini_path = Path(d.DEFAULT_CIV4_DIR) / ("SASCapture_%s_%d.ini" % (time.strftime("%Y%m%dT%H%M%S"), os.getpid()))
	ini_path.write_bytes(text)
	pid = None
	succeeded = False
	try:
		pid = d.launch_detached('"mod=\\%s" ini=%s%s' % (args.mod, ini_path.name, " multiple" if args.multiple else ""))
		for _ in range(120):
			time.sleep(1)
			hwnd = d.find_window(pid)
			if hwnd:
				left, top, right, bottom = d.window_rect(hwnd)
				if right - left > 1000:
					break
		time.sleep(12)
		if args.maximize:
			tool("move", "--pid", str(pid), "--monitor", str(args.maximize), "full")
			time.sleep(4)
		run_steps(pid, args, out)
		succeeded = True
	finally:
		# <!-- custom: --keep-open leaves a successful run's client and INI for later steps with --pid, such as at 1440p and 4K, where the named points do not fit and positions are read off each screenshot in turn (2026-11-12).
		# A first version returned from inside this finally block, which can swallow an exception and which newer Python versions warn about; the branch now skips the cleanup instead. (Claude code Opus 5.5) -->
		keep = args.keep_open and succeeded
		if keep:
			print("left open: pid %d; per-run INI %s (delete it and its .bak after closing)" % (pid, ini_path))
		try:
			if pid and not keep:
				subprocess.run([sys.executable, TOOL, "close", "--pid", str(pid)], capture_output=True)
				for _ in range(20):
					time.sleep(1)
					if pid not in [p for p, _ in d.civ4_processes()]:
						break
				else:
					# <!-- custom: A 1920x1080 fullscreen client ignored the close request while still responding (2026-11-12), so stop this run's own process. (Claude code Opus 5.5) -->
					subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Id %d -Force" % pid])
		finally:
			# <!-- custom: Civ4 also leaves a .bak copy of the INI it was started with. (Claude code Opus 5.5) -->
			for leftover in (ini_path, ini_path.with_name(ini_path.name + ".bak")):
				if not keep:
					leftover.unlink(missing_ok=True)
	print("Civ4 clients still running:", [p for p, _ in d.civ4_processes()])
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Retakes the docs' screenshots listed in doc_screenshots.json: one Civ4 client per save role, each screen opened and each tab pressed by name through SASPilot, then Civ4's own Print Screen through SASPilotClient.py shot, written over the image in _1_AdvCiv-SAS/Images.
# Written on 2026-11-21 after the 31 advisor screenshots were retaken by hand-written scripts when the commerce sliders' default background changed; the user asked for the list and the runner so the next retake is one command. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, fnmatch for --only, json for the list and the replies, subprocess to call SASPilotClient.py, time to let a screen draw. (Claude code Opus 5.5) -->
import argparse
import fnmatch
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLIENT = REPO / "SASPilot" / "SASPilotClient.py"
LIST = Path(__file__).resolve().parent / "doc_screenshots.json"
# <!-- custom: desktop_windows moves the real pointer for a hover: SASPilot's uihover reads a tooltip's text, but only a pointer over the widget makes the game draw it, and the Relations tab's attitude breakdown is part of what its screenshot shows (the user, 2026-11-21). (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
import desktop_windows
IMAGES = REPO / "_1_AdvCiv-SAS" / "Images"


def pilot(*args: str, timeout: float = 120.0) -> dict:
	result = subprocess.run([sys.executable, str(CLIENT), "--compact"] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
	lines = [line for line in result.stdout.splitlines() if line.startswith("{") or line.startswith("[")]
	if result.returncode != 0 or not lines:
		raise RuntimeError("SASPilotClient.py %s failed: %s" % (" ".join(args), (result.stderr or result.stdout).strip()[-600:]))
	return json.loads(lines[-1])


# <!-- custom: A save can open on an AI's diplomacy screen, such as Ewuare asking us to convert, which blocks the advisors: answer it as a player who declines, then leave (2026-11-21). (Claude code Opus 5.5) -->
def clear_diplomacy() -> None:
	for _ in range(8):
		screen = pilot("diplo")
		if not screen.get("open"):
			return
		comments = [reply["comment"] for reply in screen.get("replies", [])]
		pick = [c for c in comments if c.endswith("NO_CONVERT")] or [c for c in comments if c.endswith("EXIT")] or [c for c in comments if "NEVERMIND" in c] or comments
		pilot("reply", "screen=%s" % screen["screen"], "comment=%s" % pick[0])
	raise RuntimeError("a diplomacy screen stayed open after 8 replies")


def open_screens() -> list:
	return pilot("uistate").get("openScreens", [])


def cursor_pos() -> tuple:
	point = desktop_windows.wt.POINT()
	desktop_windows.USER32.GetCursorPos(desktop_windows.ctypes.byref(point))
	return point.x, point.y


# <!-- custom: One shot, refused when a person used the mouse meanwhile: the user moving it during the first run clicked a city open, so two shots showed its city screen's panels instead of the map (2026-11-21).
# It waits until nobody has touched the keyboard or mouse for 2 seconds, puts the pointer on the shot's hover point or, without one, in the title bar where it draws no tooltip, takes the shot, then checks that the pointer has not moved and that only this screen is open, without a city screen.
# Returns False to have it taken again. (Claude code Opus 5.5) -->
def take_shot(pid: int, shot: dict) -> bool:
	desktop_windows.wait_for_idle_user(2.0, 600.0)
	pilot("uiopen", "name=%s" % shot["open"])
	time.sleep(1.0)
	screen = open_screens()
	if len(screen) != 1:
		raise RuntimeError("%s: expected one open screen after uiopen %s, found %s" % (shot["image"], shot["open"], screen))
	try:
		for text in shot.get("press", []):
			pilot("uipress", "text=%s" % text, "screen=%s" % screen[0])
			time.sleep(1.0)
		# <!-- custom: Bring the window forward before placing the pointer: shot's Print Screen otherwise did it by clicking the title bar at 640, 12, which moved the pointer and failed the check below on every attempt. (Claude code Opus 5.5) -->
		desktop_windows.bring_to_front(desktop_windows.find_window(pid), pid)
		if shot.get("hover"):
			dx, dy = desktop_windows.client_offset(pid)
			expected = desktop_windows.hover(pid, shot["hover"][0] + dx, shot["hover"][1] + dy)
			time.sleep(1.5)
		else:
			expected = desktop_windows.hover(pid, 200, 10)
		reply = pilot("shot", "out=%s" % (IMAGES / shot["image"]))
		state = pilot("uistate")
		cursor = cursor_pos()
		ok = cursor == tuple(expected) and state.get("openScreens") == screen and not state.get("cityScreen")
		if not ok:
			print("  %s: pointer %s (put at %s), open screens %s (expected %s), city screen %s" % (shot["image"], cursor, tuple(expected), state.get("openScreens"), screen, state.get("cityScreen")))
		if ok:
			print("  %s <- %s" % (shot["image"], Path(reply["shot"]).name))
		for text in shot.get("undo", []):
			pilot("uipress", "text=%s" % text, "screen=%s" % screen[0])
			time.sleep(0.5)
	finally:
		desktop_windows.hover(pid, 200, 10)
		if screen[0] in open_screens():
			pilot("uipress", "text=exit", "screen=%s" % screen[0])
			time.sleep(0.5)
		if pilot("uistate").get("cityScreen"):
			pilot("uiselect", "close=1")
	return ok


def run_save(role: str, save: dict, shots: list, resolution: list, dry_run: bool) -> list:
	done = []
	print("save %s: %s, %d shot(s)" % (role, save["file"], len(shots)))
	if dry_run:
		return [shot["image"] for shot in shots]
	# <!-- custom: Close a client left from an earlier run; with none running, close reports an error, which is fine here. (Claude code Opus 5.5) -->
	try:
		pilot("close", timeout=60.0)
	except RuntimeError:
		pass
	pilot("--resolution", str(resolution[0]), str(resolution[1]), "--save", save["file"], "start", timeout=600.0)
	clear_diplomacy()
	pid = pilot("list")[0]
	for shot in shots:
		for attempt in range(3):
			if take_shot(pid, shot):
				done.append(shot["image"])
				break
			print("  %s: the mouse moved or the screen changed during the shot; taking it again" % shot["image"])
		else:
			raise RuntimeError("%s: the mouse kept moving or the screen kept changing during 3 attempts" % shot["image"])
	errors = pilot("pyerrors")
	if errors.get("lines"):
		raise RuntimeError("Python errors while shooting on %s: %s" % (role, errors["lines"][:5]))
	pilot("close", timeout=60.0)
	return done


def main() -> int:
	parser = argparse.ArgumentParser(description="Retake the docs' screenshots listed in doc_screenshots.json with Civ4's own Print Screen, one client per save role. Images are overwritten in place; review them with git diff before staging.")
	parser.add_argument("--only", help="only images whose name matches this pattern, such as '*military*'")
	parser.add_argument("--save", help="only this save role, such as t201")
	parser.add_argument("--list", action="store_true", help="print the list, with what it does not cover yet, and exit")
	parser.add_argument("--dry-run", action="store_true", help="say which shots would be taken on which save, without starting Civ4")
	args = parser.parse_args()
	data = json.loads(LIST.read_text(encoding="utf-8"))
	shots = [s for s in data["shots"] if (not args.only or fnmatch.fnmatch(s["image"], args.only)) and (not args.save or s["save"] == args.save)]
	if args.list:
		for shot in shots:
			print("%-6s %-18s %-44s %s" % (shot["save"], shot["open"], shot["image"], " > ".join(shot.get("press", []))))
			print("       shows %s" % shot.get("shows", "?"))
		print("\nnot covered yet:")
		for line in data.get("notCovered", []):
			print("- " + line)
		return 0
	missing = [role for role in set(s["save"] for s in shots) if role not in data["saves"]]
	if missing:
		raise SystemExit("unknown save role(s): %s" % ", ".join(missing))
	done = []
	for role in data["saves"]:
		group = [s for s in shots if s["save"] == role]
		if group:
			done += run_save(role, data["saves"][role], group, data["resolution"], args.dry_run)
	print("%d screenshot(s) %s" % (len(done), "planned" if args.dry_run else "retaken"))
	return 0


if __name__ == "__main__":
	sys.exit(main())

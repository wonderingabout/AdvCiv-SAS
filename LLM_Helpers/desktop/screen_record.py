# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Records one monitor's work area (the taskbar left out) with ffmpeg while an optional command runs, then saves the frames that changed as PNGs an agent can read.
# Written on 2026-11-19: Civ4 flashed "Load Error: Failed to uncompress game data" for a fraction of a second before quitting on an old save; window polling missed it, as Civ4 draws its popups inside its game window, while a recording showed it. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, subprocess for ffmpeg and the command, time to let the recording start first. (Claude code Opus 5.5) -->
import argparse
import subprocess
import sys
import time
from pathlib import Path

# <!-- custom: desktop_windows, beside this script, gives each monitor's work area, the screen minus the taskbar. (Claude code Opus 5.5) -->
from desktop_windows import monitors


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Record a monitor's work area (no taskbar) with ffmpeg, optionally while running a command, then save the changed frames as PNGs.")
	parser.add_argument("--out", type=Path, required=True, help="Folder for record.mp4 and frame_NNN.png")
	parser.add_argument("--monitor", type=int, default=1, help="Monitor to record, 1 the leftmost (default 1)")
	parser.add_argument("--seconds", type=float, default=15.0, help="Recording length (default 15)")
	parser.add_argument("--fps", type=int, default=20, help="Frames per second (default 20; a popup shown for 0.1 s needs 10 or more)")
	parser.add_argument("--scene", type=float, default=0.02, help="ffmpeg scene-change score above which a frame is saved (default 0.02; lower saves more)")
	parser.add_argument("--lead", type=float, default=1.5, help="Seconds of recording before the command starts (default 1.5)")
	parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run once recording has started, after --")
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	areas = monitors()
	if not 1 <= args.monitor <= len(areas):
		sys.exit("monitor %d not found; there are %d" % (args.monitor, len(areas)))
	left, top, right, bottom = areas[args.monitor - 1]
	args.out.mkdir(parents=True, exist_ok=True)
	video = args.out / "record.mp4"
	# <!-- custom: gdigrab needs even sizes for libx264's yuv420p, so an odd work area loses its last pixel. (Claude code Opus 5.5) -->
	width = (right - left) // 2 * 2
	height = (bottom - top) // 2 * 2
	recorder = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "gdigrab", "-framerate", str(args.fps), "-offset_x", str(left), "-offset_y", str(top), "-video_size", "%dx%d" % (width, height), "-t", str(args.seconds), "-i", "desktop", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(video)])
	command = args.command[1:] if args.command[:1] == ["--"] else args.command
	if command:
		time.sleep(args.lead)
		subprocess.run(command)
	recorder.wait()
	if recorder.returncode != 0:
		sys.exit("ffmpeg failed with code %d" % recorder.returncode)
	for old in args.out.glob("frame_*.png"):
		old.unlink()
	subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(video), "-vf", "select='gt(scene,%s)'" % args.scene, "-vsync", "vfr", str(args.out / "frame_%03d.png")], check=True)
	frames = sorted(args.out.glob("frame_*.png"))
	print("recorded %s (%dx%d at %d,%d, %s s); %d changed frames saved in %s" % (video.name, width, height, left, top, args.seconds, len(frames), args.out))
	return 0


if __name__ == "__main__":
	sys.exit(main())

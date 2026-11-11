#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: An agent cannot listen, but it can record what the computer's speakers play and measure it: whether the game makes sound, how loud, and when it starts or stops.
# On 2026-11-11 this was first done by hand with ffmpeg and a numpy loop, and the user asked for it to become a helper, since such checks get repeated.
# ffmpeg records through the "virtual-audio-capturer" DirectShow device, which captures the sound output on the development machine. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; subprocess runs ffmpeg; tempfile holds the recording; wave and numpy measure it; sys and pathlib handle exits and paths. (Claude Code Opus 5.5) -->
import argparse
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

DEVICE = "virtual-audio-capturer"
# <!-- custom: Digital silence measured about -91 dB through this device on 2026-11-11; the quiet Sevopedia music measured about -45 dB, so -80 dB separates them with room to spare. (Claude Code Opus 5.5) -->
SILENCE_DB = -80.0


def record(seconds, out_path):
	command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "dshow", "-i", "audio=%s" % DEVICE, "-t", str(seconds), str(out_path)]
	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode != 0 or not Path(out_path).is_file():
		sys.exit("ffmpeg could not record from %s: %s" % (DEVICE, result.stderr.strip()))


def levels(path, step_seconds):
	# <!-- custom: Loudness of each step as RMS in dB of full scale, plus the overall mean and peak; a small floor avoids log(0) on digital silence. (Claude Code Opus 5.5) -->
	with wave.open(str(path)) as stream:
		rate = stream.getframerate()
		channels = stream.getnchannels()
		data = np.frombuffer(stream.readframes(stream.getnframes()), dtype=np.int16).reshape(-1, channels).astype(float) / 32768
	step = max(1, int(rate * step_seconds))
	rows = []
	for start in range(0, len(data), step):
		chunk = data[start:start + step]
		rows.append((start / rate, 20 * np.log10(np.sqrt((chunk ** 2).mean()) + 1e-9)))
	mean_db = 20 * np.log10(np.sqrt((data ** 2).mean()) + 1e-9)
	peak_db = 20 * np.log10(np.abs(data).max() + 1e-9)
	return rows, mean_db, peak_db


def main():
	parser = argparse.ArgumentParser(description="Record the computer's sound output for a few seconds and report how loud it was over time.")
	parser.add_argument("--seconds", type=float, default=6.0)
	parser.add_argument("--step", type=float, default=0.25, help="seconds per loudness row")
	parser.add_argument("--wav", type=Path, help="keep the recording here instead of a temporary file")
	parser.add_argument("--wave-png", type=Path, help="also draw a waveform picture here")
	parser.add_argument("--front", type=int, metavar="PID", help="bring this process's window to the front first; Civ4 plays sound only while it is in front")
	args = parser.parse_args()

	if args.front:
		# <!-- custom: On 2026-11-11 Civ4 measured -42 dB in front and silence with the Volume Mixer in front, and the user confirmed it goes quiet whenever they click away.
		# Bringing it forward takes the focus from the user, so only do it when they are not typing. (Claude Code Opus 5.5) -->
		# <!-- custom: desktop_windows, beside this script, finds the window and brings it to the front. (Claude Code Opus 5.5) -->
		import desktop_windows
		desktop_windows.make_dpi_aware()
		hwnd = desktop_windows.find_window(args.front)
		if hwnd is None:
			sys.exit("no window for process %d" % args.front)
		desktop_windows.bring_to_front(hwnd, args.front)
	wav_path = args.wav or Path(tempfile.gettempdir()) / "sound_check.wav"
	record(args.seconds, wav_path)
	rows, mean_db, peak_db = levels(wav_path, args.step)
	for seconds, db in rows:
		print("%5.2fs %6.1f dB %s" % (seconds, db, "#" * max(0, int((db + 80) / 2))))
	print("mean %.1f dB, peak %.1f dB" % (mean_db, peak_db))
	if args.wave_png:
		subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav_path), "-filter_complex", "showwavespic=s=1200x200", "-frames:v", "1", str(args.wave_png)], check=True)
		print("waveform: %s" % args.wave_png)
	if peak_db < SILENCE_DB:
		# <!-- custom: On 2026-11-11 silence came from Civ4 not being in front or Civ4 muted in the Volume Mixer, where the user keeps it muted.
		# The user also mentions a Windows glitch, not met that day, that leaves an app silent although the mixer shows it unmuted, until its slider is moved down and back up. (Claude Code Opus 5.5) -->
		print("silence: is the game in front (--front PID)? Civ4 is quiet in the background. Is it muted in the Volume Mixer (sndvol.exe)? If it shows unmuted yet stays silent, move its volume slider down and back up")
		sys.exit(1)


if __name__ == "__main__":
	main()

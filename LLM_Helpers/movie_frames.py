#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Agents cannot watch videos or hear sound, only see images, so this turns a Civ4 movie (Bink .bik, or anything ffmpeg reads) into a contact sheet of evenly spaced frames, and its audio into a waveform picture with loudness figures.
# ffmpeg decodes Bink video and audio; it was already installed through winget on 2026-11-08.
# See README_Art_Tools.md. (Claude code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: argparse parses the options; glob/os/shutil find ffmpeg; math rejects a non-finite --start or --duration; re reads its loudness report; subprocess runs it; tempfile holds the frames; PIL (Pillow) builds the sheet. (Claude code Opus 5.5) -->
import argparse
import glob
import math
import os
import re
import shutil
import subprocess
import tempfile

# <!-- custom: Pillow assembles the sheet; fail with the install command if it is missing. (Claude code Opus 5.5) -->
try:
	from PIL import Image, ImageDraw
except ImportError:
	raise SystemExit("Pillow is required: py -m pip install pillow")


def find_tool(name):
	# <!-- custom: winget installs ffmpeg under its package folder without always adding it to this shell's PATH, so look there too. (Claude code Opus 5.5) -->
	found = shutil.which(name)
	if found:
		return found
	pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "*FFmpeg*", "*", "bin", name + ".exe")
	matches = sorted(glob.glob(pattern))
	if not matches:
		raise SystemExit("%s not found; install it with: winget install Gyan.FFmpeg" % name)
	return matches[-1]


def duration_of(ffprobe, path):
	output = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True).stdout
	return float(output.strip())


# <!-- custom: Use the first audio track for both the waveform and loudness so movie and audio-only previews measure the same stream. (GPT-6.1-Sol) -->
def render_audio(ffmpeg, source, target):
	subprocess.run([ffmpeg, "-v", "error", "-y", "-i", source, "-filter_complex", "[0:a:0]showwavespic=s=1024x200:split_channels=1[wave]", "-map", "[wave]", "-frames:v", "1", target], check=True)
	report = subprocess.run([ffmpeg, "-hide_banner", "-i", source, "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
	levels = dict(re.findall(r"(mean_volume|max_volume): (-?[\d.]+) dB", report))
	print("wrote %s; audio mean %s dB, peak %s dB" % (target, levels.get("mean_volume", "?"), levels.get("max_volume", "?")))


def main():
	parser = argparse.ArgumentParser(description="Preview a Civ4 movie as a contact sheet, looping GIF or audio waveform.")
	parser.add_argument("movie")
	parser.add_argument("out", help="PNG contact sheet, looping GIF, MP4 video with sound, or waveform with --audio-only")
	parser.add_argument("--frames", type=int, default=6)
	parser.add_argument("--width", type=int, default=320, help="width of each frame")
	parser.add_argument("--start", help="GIF or MP4 start, in seconds or as a percentage of the movie such as 25%% (default: 0)")
	parser.add_argument("--duration", help="GIF or MP4 length, in seconds or as a percentage of the movie such as 10%% (default: through the end)")
	parser.add_argument("--fps", type=int, help="GIF frames per second (default: 12)")
	audio = parser.add_mutually_exclusive_group()
	audio.add_argument("--audio", help="also write the audio's waveform as this PNG and print its loudness")
	audio.add_argument("--audio-only", action="store_true", help="write a waveform and print loudness without sampling video")
	args = parser.parse_args()
	is_gif = args.out.lower().endswith(".gif") and not args.audio_only
	is_video = args.out.lower().endswith(".mp4") and not args.audio_only
	if not (is_gif or is_video) and any(value is not None for value in (args.start, args.duration)):
		parser.error("--start and --duration require GIF or MP4 output")
	if not is_gif and args.fps is not None:
		parser.error("--fps requires GIF output")
	for option in ("start", "duration"):
		value = getattr(args, option)
		if value is not None:
			try:
				setattr(args, option, (float(value[:-1]), "%") if value.endswith("%") else (float(value), "s"))
			except ValueError:
				parser.error("--%s takes seconds or a percentage, such as 12.5 or 25%%" % option)
	if args.start is not None and (not math.isfinite(args.start[0]) or args.start[0] < 0):
		parser.error("--start must be finite and nonnegative")
	if args.duration is not None and (not math.isfinite(args.duration[0]) or args.duration[0] <= 0):
		parser.error("--duration must be finite and positive")
	if args.fps is not None and not 1 <= args.fps <= 50:
		parser.error("--fps must be between 1 and 50")
	if args.width < 1:
		parser.error("--width must be positive")
	ffmpeg = find_tool("ffmpeg")
	if args.audio_only:
		render_audio(ffmpeg, args.movie, args.out)
		return
	length = duration_of(find_tool("ffprobe"), args.movie)
	# <!-- custom: A percentage is of the whole movie, so --start 50% --duration 10% picks the same slice of a 20-second and a 3-minute movie. (Claude code Opus 5.5) -->
	for option in ("start", "duration"):
		value = getattr(args, option)
		if value is not None:
			setattr(args, option, value[0] * length / 100 if value[1] == "%" else value[0])
	if is_video:
		# <!-- custom: A GIF has no sound, and a .bik opens only in players that decode Bink, so write H.264 video with AAC sound, which VLC, browsers and Windows' own player open.
		# Keep such videos of the game's movies outside the repository, as they copy Firaxis's work in full. (Claude code Opus 5.5) -->
		start = args.start or 0
		if start >= length:
			parser.error("--start must be before the end of the movie")
		duration = min(args.duration or length, length - start)
		subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", str(start), "-i", args.movie, "-t", str(duration), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", args.out], check=True)
		print("wrote %s: %.2f to %.2f s with sound" % (args.out, start, start + duration))
		return
	if is_gif:
		start = args.start or 0
		if start >= length:
			parser.error("--start must be before the end of the movie")
		duration = min(args.duration or length, length - start)
		# <!-- custom: Trim before building the palette so its colors are chosen from the excerpt itself. (GPT-6.1-Sol) -->
		filters = "[0:v]trim=duration=%s,setpts=PTS-STARTPTS,fps=%d,scale=%d:-1:flags=lanczos,split[v][p];[p]palettegen[palette];[v][palette]paletteuse[gif]" % (duration, args.fps or 12, args.width)
		subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", str(start), "-i", args.movie, "-filter_complex", filters, "-map", "[gif]", "-loop", "0", args.out], check=True)
		print("wrote %s: %.2f to %.2f s" % (args.out, start, start + duration))
		if args.audio:
			render_audio(ffmpeg, args.movie, args.audio)
		return
	times = [length * (k + 0.5) / args.frames for k in range(args.frames)]
	frames = []
	with tempfile.TemporaryDirectory() as folder:
		for k, at in enumerate(times):
			target = os.path.join(folder, "%02d.png" % k)
			subprocess.run([ffmpeg, "-v", "error", "-ss", "%.3f" % at, "-i", args.movie, "-frames:v", "1", "-vf", "scale=%d:-1" % args.width, target], check=True)
			frames.append(Image.open(target).convert("RGB"))
	height = frames[0].size[1]
	sheet = Image.new("RGB", ((args.width + 8) * len(frames) - 8, height + 20), (30, 30, 30))
	draw = ImageDraw.Draw(sheet)
	for k, (frame, at) in enumerate(zip(frames, times)):
		sheet.paste(frame, (k * (args.width + 8), 0))
		draw.text((k * (args.width + 8) + 4, height + 4), "%.1f s" % at, fill=(230, 230, 230))
	sheet.save(args.out)
	print("wrote %s: %d frames of %.2f s" % (args.out, len(frames), length))
	if args.audio:
		render_audio(ffmpeg, args.movie, args.audio)


if __name__ == "__main__":
	main()

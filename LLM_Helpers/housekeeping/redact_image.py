#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Screenshots kept in the repo can show details the user would rather not publish, such as the monitor's brand and model in the Volume Mixer's title on 2026-11-11.
# This covers chosen rectangles of an image, by default with the colour around each one, so the cover blends into the window instead of leaving a black bar. (Claude Code Opus 5.5) -->

# <!-- custom: argparse reads the options; collections counts border colours; pathlib handles paths; PIL edits the image. (Claude Code Opus 5.5) -->
import argparse
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw


def border_colour(image, box):
	# <!-- custom: The most common colour on the rectangle's edge, usually the window background around the hidden text. (Claude Code Opus 5.5) -->
	left, top, right, bottom = box
	pixels = [image.getpixel((x, y)) for x in range(left, right) for y in (top, bottom - 1)]
	pixels += [image.getpixel((x, y)) for y in range(top, bottom) for x in (left, right - 1)]
	return Counter(pixels).most_common(1)[0][0]


def redact(path, boxes, out_path=None, colour=None):
	image = Image.open(path).convert("RGB")
	draw = ImageDraw.Draw(image)
	for box in boxes:
		left, top, right, bottom = box
		if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
			raise SystemExit("rectangle %s lies outside the %dx%d image" % (box, image.width, image.height))
		draw.rectangle((left, top, right - 1, bottom - 1), fill=colour or border_colour(image, box))
	target = out_path or path
	image.save(target)
	return target


def main():
	parser = argparse.ArgumentParser(description="Cover rectangles of an image, such as personal details in a screenshot, with the surrounding colour.")
	parser.add_argument("image", type=Path)
	parser.add_argument("--box", type=int, nargs=4, action="append", required=True, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="pixel rectangle to cover; repeat for several")
	parser.add_argument("--out", type=Path, help="write here instead of overwriting the image")
	parser.add_argument("--colour", help="fill colour such as #ffffff instead of the surrounding colour")
	args = parser.parse_args()
	print("covered %d rectangle(s) in %s" % (len(args.box), redact(args.image, [tuple(box) for box in args.box], args.out, args.colour)))


if __name__ == "__main__":
	main()

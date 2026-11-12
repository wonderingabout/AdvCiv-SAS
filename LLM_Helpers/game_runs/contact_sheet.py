# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Puts the same regions of several screenshots side by side on one labelled sheet, so an agent reads a whole capture series in one image instead of opening each full-size PNG.
# Written on 2026-11-12 while mapping WorldBuilder, after the same crop-and-tile code had been retyped for each round of captures. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, Path for files; Pillow crops, scales and labels the images. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Tile the same regions of several screenshots into one labelled sheet.", epilog="Example: contact_sheet.py --out sheet.png --region 0,30,760,560 --region 1500,30,1926,300 --columns 3 a.png b.png c.png")
	parser.add_argument("--out", required=True, help="Sheet PNG to write")
	parser.add_argument("--region", action="append", default=[], metavar="L,T,R,B", help="Window region to keep from each image, placed left to right; repeatable; default the whole image")
	parser.add_argument("--columns", type=int, default=3, help="Tiles per row (default 3)")
	parser.add_argument("--black-to-white", type=int, metavar="MAX", help="Paint pixels whose channels are all at most MAX (such as 12) white, to show black empty space apart from dark content")
	parser.add_argument("--scale", type=float, default=1.0, help="Scale each tile, such as 0.5 for a long series")
	parser.add_argument("images", nargs="+", help="Screenshots; each tile is labelled with its file name")
	return parser.parse_args()


def tile(path: Path, regions: list[tuple[int, int, int, int]], scale: float, black_max: int | None = None) -> Image.Image:
	image = Image.open(path).convert("RGB")
	# <!-- custom: The world-picker globe draws its own black background inside a black panel, so the globe's real size could not be judged on 2026-11-12; the user suggested painting the black white, which shows the content's outline. (Claude code Opus 5.5) -->
	if black_max is not None:
		r, g, b = image.split()
		dark = [Image.eval(c, lambda v, m=black_max: 255 if v <= m else 0) for c in (r, g, b)]
		mask = ImageChops.multiply(ImageChops.multiply(dark[0], dark[1]), dark[2])
		image = Image.composite(Image.new("RGB", image.size, (255, 255, 255)), image, mask)
	parts = [image.crop(region) for region in regions] or [image]
	label_height = 18
	out = Image.new("RGB", (sum(p.width for p in parts), max(p.height for p in parts) + label_height), "black")
	x = 0
	for part in parts:
		out.paste(part, (x, label_height))
		x += part.width
	ImageDraw.Draw(out).text((4, 3), path.stem, fill="yellow")
	if scale != 1.0:
		out = out.resize((max(1, int(out.width * scale)), max(1, int(out.height * scale))))
	return out


def main() -> int:
	args = parse_args()
	regions: list[tuple[int, int, int, int]] = []
	for r in args.region:
		values = [int(v) for v in r.split(",")]
		if len(values) != 4:
			raise SystemExit("--region needs L,T,R,B")
		regions.append((values[0], values[1], values[2], values[3]))
	tiles = [tile(Path(p), regions, args.scale, args.black_to_white) for p in args.images]
	width = max(t.width for t in tiles)
	height = max(t.height for t in tiles)
	rows = (len(tiles) + args.columns - 1) // args.columns
	sheet = Image.new("RGB", (width * min(args.columns, len(tiles)), height * rows), (40, 40, 40))
	for i, t in enumerate(tiles):
		sheet.paste(t, ((i % args.columns) * width, (i // args.columns) * height))
	sheet.save(args.out)
	print("wrote %s (%dx%d, %d tiles)" % (args.out, sheet.width, sheet.height, len(tiles)))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

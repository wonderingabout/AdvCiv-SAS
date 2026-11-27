#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Agents' image readers open PNG/JPG but not Civ4's GameFont .tga files, and none of the local Pythons had Pillow, so on 2026-11-07/08 this pure-Python helper let an agent see and edit the fonts.
# A script reads the .tga only as numbers; the agent sees glyphs once preview has turned a region into an enlarged PNG for its image reader.
# preview renders a region enlarged as PNG for the image reader; grid finds the magenta glyph grid; move copies glyph cells between slots or from another font, such as base AdvCiv's in Git history.
# It handles only the uncompressed 32-bit TGAs Game Font Editor writes, and fails loudly on anything else.
# See README_Art_Tools.md. (Claude code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: argparse parses the subcommands; struct reads the TGA header and writes the PNG chunks; zlib compresses the PNG data. (Claude code Opus 5.5) -->
import argparse
import struct
import zlib


class Tga:
	def __init__(self, path):
		self.data = bytearray(open(path, "rb").read())
		d = self.data
		if d[0] != 0 or d[1] != 0 or d[2] != 2 or d[16] != 32:
			raise SystemExit("%s: expected an uncompressed 32-bit TGA without ID or color map (type=%d bpp=%d)" % (path, d[2], d[16]))
		self.width, self.height = struct.unpack("<HH", d[12:16])
		# <!-- custom: Bit 5 of the descriptor marks top-down rows; Game Font Editor writes bottom-up ones, so y is flipped. (Claude code Opus 5.5) -->
		self.top_down = bool(d[17] & 0x20)

	def offset(self, x, y):
		row = y if self.top_down else self.height - 1 - y
		return 18 + (row * self.width + x) * 4

	def rgba(self, x, y):
		i = self.offset(x, y)
		b, g, r, a = self.data[i:i + 4]
		return r, g, b, a

	def is_grid(self, x, y):
		r, g, b, _ = self.rgba(x, y)
		return (r, g, b) == (255, 0, 255)

	def cell(self, box):
		x0, x1, y0, y1 = box
		return [bytes(self.data[self.offset(x0, y):self.offset(x1, y)]) for y in range(y0, y1)]

	def put(self, box, rows):
		x0, x1, y0, y1 = box
		for k, y in enumerate(range(y0, y1)):
			self.data[self.offset(x0, y):self.offset(x1, y)] = rows[k]


def write_png(path, tga, box, zoom, background=(200, 200, 200)):
	x0, y0, x1, y1 = box
	raw = bytearray()
	for y in range(y0, y1):
		line = bytearray()
		for x in range(x0, x1):
			r, g, b, a = tga.rgba(x, y)
			if (r, g, b) == (255, 0, 255):
				pixel = (r, g, b)
			else:
				# <!-- custom: Blend glyphs over grey by their alpha, as the game does over its interface, so faint edges stay visible. (Claude code Opus 5.5) -->
				pixel = tuple((v * a + background[i] * (255 - a)) // 255 for i, v in enumerate((r, g, b)))
			line += bytes(pixel) * zoom
		for _ in range(zoom):
			raw += b"\x00" + line

	def chunk(tag, payload):
		return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff)
	header = struct.pack(">IIBBBBB", (x1 - x0) * zoom, (y1 - y0) * zoom, 8, 2, 0, 0, 0)
	open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


def cmd_preview(args):
	tga = Tga(args.tga)
	box = args.box or (0, 0, tga.width, tga.height)
	write_png(args.out, tga, box, args.zoom)
	print("wrote %s (%dx%d, box %s, zoom %d)" % (args.out, tga.width, tga.height, tuple(box), args.zoom))


def cmd_grid(args):
	tga = Tga(args.tga)
	print("size %dx%d, %s" % (tga.width, tga.height, "top-down" if tga.top_down else "bottom-up"))
	if args.band is None:
		lines = [y for y in range(tga.height) if sum(1 for x in range(tga.width) if tga.is_grid(x, y)) > tga.width // 2]
		print("horizontal grid lines:", lines)
		return
	y0, y1 = args.band
	# <!-- custom: Glyphs can cover parts of a vertical grid line, so only empty cells show complete lines; read the column pitch from those. (Claude code Opus 5.5) -->
	lines = [x for x in range(tga.width) if all(tga.is_grid(x, y) for y in range(y0 + 1, y1))]
	print("complete vertical grid lines in band %d-%d:" % (y0, y1), lines)


# <!-- custom: Row height and column pitch are separate inputs: the first draft derived the pitch as row height + 1, which fit GameFont.tga (rows 21, columns 22) but cut GameFont_75.tga's cells short, where both are 17.
# The preview showed the wrong cells before any font was replaced; measure both with grid. (Claude code Opus 5.5) -->
def slot_box(slot, row_tops, row_height, col_pitch, per_row):
	row, col = divmod(slot, per_row)
	if row >= len(row_tops):
		raise SystemExit("slot %d needs row %d, but only %d row tops were given" % (slot, row, len(row_tops)))
	return col * col_pitch, col * col_pitch + col_pitch - 1, row_tops[row] + 1, row_tops[row] + row_height


def cmd_move(args):
	target = Tga(args.tga)
	others = {}
	pending = []
	# <!-- custom: Read every source before writing any target, so a swap such as 32=34 34=32 copies the original glyphs. (Claude code Opus 5.5) -->
	for spec in args.set:
		dst, src = spec.split("=")
		if ":" in src:
			path, src_slot = src.rsplit(":", 1)
			if path not in others:
				others[path] = Tga(path)
			source = others[path]
			if (source.width, source.height) != (target.width, target.height):
				raise SystemExit("%s is %dx%d, unlike the target's %dx%d" % (path, source.width, source.height, target.width, target.height))
		else:
			source, src_slot = target, src
		box = slot_box(int(src_slot), args.row_tops, args.row_height, args.col_pitch, args.per_row)
		pending.append((slot_box(int(dst), args.row_tops, args.row_height, args.col_pitch, args.per_row), source.cell(box)))
	for box, rows in pending:
		target.put(box, rows)
	open(args.out, "wb").write(bytes(target.data))
	print("wrote %s with %d glyph cell(s) moved" % (args.out, len(pending)))


def main():
	parser = argparse.ArgumentParser(description="View and rearrange Civ4 GameFont .tga glyphs without an image library.")
	sub = parser.add_subparsers(dest="command", required=True)
	p = sub.add_parser("preview", help="render a region, enlarged, as a PNG an image reader can open")
	p.add_argument("tga")
	p.add_argument("out")
	p.add_argument("--box", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"), help="region in top-down pixels; default the whole font")
	p.add_argument("--zoom", type=int, default=3)
	p.set_defaults(func=cmd_preview)
	p = sub.add_parser("grid", help="list the magenta grid lines, to find row tops and the column pitch")
	p.add_argument("tga")
	p.add_argument("--band", type=int, nargs=2, metavar=("Y0", "Y1"), help="list vertical lines between two horizontal grid lines")
	p.set_defaults(func=cmd_grid)
	p = sub.add_parser("move", help="copy glyph cells to other slots, from this font or another")
	p.add_argument("tga")
	p.add_argument("--row-tops", type=int, nargs="+", required=True, help="the grid line above each row of this glyph group, top-down")
	p.add_argument("--row-height", type=int, required=True, help="distance between those horizontal grid lines")
	p.add_argument("--col-pitch", type=int, required=True, help="distance between vertical grid lines")
	p.add_argument("--per-row", type=int, default=25)
	p.add_argument("--set", action="append", required=True, metavar="DST=SRC", help="slot DST takes slot SRC, or OTHER.tga:SRC from another font; repeat as needed")
	p.add_argument("--out", required=True)
	p.set_defaults(func=cmd_move)
	args = parser.parse_args()
	args.func(args)


if __name__ == "__main__":
	main()

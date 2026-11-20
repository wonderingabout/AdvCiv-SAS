#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: PakBuild and Dragon UnPACKer open Civ4's packed .FPK art, but only through their windows, so an agent could not read BtS's own buttons and models.
# On 2026-11-08 the format proved simple enough to read directly: a header, then per file its name (each byte shifted by +1), padding to 4 bytes, a timestamp, size and offset, with the data stored as is.
# Checked on BtS's Art0.FPK (7583 files) and the Final Frontier STArt3.FPK (802): every offset starts at a valid file header, and the last file ends at the end of the archive.
# See README_Art_Tools.md. (Claude code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: argparse parses the subcommands, fnmatch filters names, pathlib/struct read the archive, and sys reports errors. (Claude code Opus 5.5) -->
import argparse
import fnmatch
from pathlib import Path
import struct
import sys


class FpkArchive:
	def __init__(self, path):
		self.path = Path(path)
		self.file = open(self.path, "rb")
		version, magic = struct.unpack("<I4s", self.file.read(8))
		if magic != b"FPK_":
			raise SystemExit("%s: not an FPK archive (magic %r)" % (self.path, magic))
		# <!-- custom: One flag byte follows the magic; both archives checked had 1 and version 4. (Claude code Opus 5.5) -->
		self.file.read(1)
		count, = struct.unpack("<I", self.file.read(4))
		self.entries = {}
		for _ in range(count):
			length, = struct.unpack("<I", self.file.read(4))
			name = bytes(b - 1 for b in self.file.read(length)).decode("latin-1").replace("\\", "/")
			self.file.read((-length) % 4)
			_timestamp, size, offset = struct.unpack("<QII", self.file.read(16))
			self.entries[name.lower()] = (name, size, offset)

	def names(self, pattern="*"):
		return sorted(name for name, _, _ in self.entries.values() if fnmatch.fnmatch(name.lower(), pattern.lower()))

	def read(self, name):
		entry = self.entries.get(name.replace("\\", "/").lower())
		if entry is None:
			return None
		_, size, offset = entry
		self.file.seek(offset)
		return self.file.read(size)


def main():
	parser = argparse.ArgumentParser(description="List or extract files from Civ4 .FPK archives.")
	sub = parser.add_subparsers(dest="command", required=True)
	p = sub.add_parser("list", help="list files, optionally matching a pattern such as '*atlas*'")
	p.add_argument("fpk")
	p.add_argument("pattern", nargs="?", default="*")
	p = sub.add_parser("extract", help="extract matching files under OUT, keeping their folders")
	p.add_argument("fpk")
	p.add_argument("out", type=Path)
	p.add_argument("pattern", nargs="?", default="*")
	args = parser.parse_args()
	archive = FpkArchive(args.fpk)
	names = archive.names(args.pattern)
	if args.command == "list":
		for name in names:
			print("%10d  %s" % (archive.entries[name.lower()][1], name))
		print("%d of %d file(s)" % (len(names), len(archive.entries)))
		return
	for name in names:
		target = args.out / name
		target.parent.mkdir(parents=True, exist_ok=True)
		target.write_bytes(archive.read(name))
	print("extracted %d file(s) to %s" % (len(names), args.out))


if __name__ == "__main__":
	sys.exit(main())

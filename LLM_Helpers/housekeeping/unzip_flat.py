#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A Known Issue's Drive folder downloads as a ZIP whose folder inside carries the KI's whole title, such as KI#11's 268-character one, so with C:\Users\PC\Downloads in front its paths pass Windows' 260-character limit and 7-Zip could not extract them (the user, 2026-11-23).
# Downloading the files one by one was the user's workaround; reading the members straight from the ZIP needs neither, so this writes each file under its own name into one short folder, as KI#11.3's screenshots were read that day.
# Two members with the same file name, from different subfolders, stop it before anything is written, as does a file already in the folder, so nothing is overwritten. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, pathlib names the files, sys reports a stop, zipfile reads the archive. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import sys
import zipfile

RESERVED = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % n for n in range(1, 10)} | {"LPT%d" % n for n in range(1, 10)}

def main():
	parser = argparse.ArgumentParser(description="Extract a ZIP's files under their own names into one folder, leaving out its folders, for ZIPs whose long folder names pass Windows' path limit.")
	parser.add_argument("zip", type=Path)
	parser.add_argument("--out", type=Path, help="the folder to write into (default: beside the ZIP, named after it)")
	args = parser.parse_args()
	out = args.out or args.zip.with_suffix("")
	with zipfile.ZipFile(args.zip) as archive:
		members = [info for info in archive.infolist() if not info.is_dir()]
		names = [Path(info.filename).name for info in members]
		# <!-- custom: Names are compared as Windows does, ignoring case: Codex's review extracted a/Shot.JPG and b/shot.jpg, and the second overwrote the first with exit code 0 (2026-11-23).
		# Windows' reserved device names, such as CON or NUL.txt, cannot be files there, so they stop it too, and each file is created exclusively, so nothing is ever overwritten. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		folded = [name.casefold() for name in names]
		clashes = sorted({name for name, key in zip(names, folded) if folded.count(key) > 1})
		reserved = sorted(name for name in names if name.split(".")[0].upper().rstrip(" ") in RESERVED)
		existing = sorted(name for name in names if (out / name).exists())
		if clashes or reserved or existing:
			sys.exit("nothing written: %s" % "; ".join(filter(None, ["same name in several folders: " + ", ".join(clashes) if clashes else "", "reserved by Windows: " + ", ".join(reserved) if reserved else "", "already in %s: %s" % (out, ", ".join(existing)) if existing else ""])))
		out.mkdir(parents=True, exist_ok=True)
		for info, name in zip(members, names):
			with open(out / name, "xb") as stream:
				stream.write(archive.read(info))
			print("%s\t%d bytes" % (name, info.file_size))
	print("%d file(s) in %s" % (len(members), out))
	return 0


if __name__ == "__main__":
	sys.exit(main())

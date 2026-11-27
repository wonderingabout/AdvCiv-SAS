#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Reports which Civ4 binaries hold a name, such as a Python function the engine may call, as a string of its own: NUL-terminated ASCII or UTF-16, with the strings beside it for context, and where the DLL source quotes it.
# Written on 2026-11-26 from the one-off searches that settled which carried entry-point functions the engine calls by name (KI#1104): the Pitboss EXE held every PbMain callback but sendEmail, which the DLL calls, while ProcessEvent was in no binary.
# It reads the installed files as they are, decompiling nothing: the Steam EXE's code is encrypted on disk, but its strings are not, so it sits with the audits rather than in exe_analysis/, whose helpers decrypt and decompile the EXE (the user asked, 2026-11-26).
# Zero hits means no stored literal of that name in these files, not that the engine never calls it, as a name can be built at run time; a short or common name, such as run, can match an unrelated string, which the context shows. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import argparse
# <!-- custom: re finds the strings, pathlib the files and sys the exit code. (Claude code Opus 5.5) -->
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BTS = REPO.parents[1]
DEFAULT_FILES = (BTS / "Civ4BeyondSword.exe", BTS / "Civ4BeyondSword_PitBoss.exe", BTS / "Assets" / "CvGameCoreDLL.dll")
STRING_RUN = re.compile(rb"[\x20-\x7e]{2,}")


def ascii_hits(data, name):
	# <!-- custom: The name as a whole C string: ended by a NUL and not preceded by a printable character, so callbackName does not match inside refreshCallbackNames, while one at the file's start or after other binary data still counts.
	# A first version required a NUL before it too and missed those, as Codex's review (GPT-6.2-Sol) noted (2026-11-26). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return [match.start() for match in re.finditer(rb"(?<![\x20-\x7e])" + re.escape(name.encode("ascii")) + rb"\x00", data)]


def wide_hits(data, name):
	# <!-- custom: The same rule for a UTF-16 string: a first version counted the bare UTF-16 bytes, so CallbackName matched inside a wide refreshCallbackNames (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return len(re.findall(rb"(?<![\x20-\x7e]\x00)" + re.escape(name.encode("utf-16-le")) + rb"\x00\x00", data))


def neighbours(data, offset, count=3):
	before = [match.group().decode("ascii") for match in STRING_RUN.finditer(data[max(0, offset - 160):offset])][-count:]
	after = [match.group().decode("ascii") for match in STRING_RUN.finditer(data[offset:offset + 160])][:count + 1]
	return " | ".join(before + ["[" + after[0] + "]"] + after[1:]) if after else ""


def source_quotes(name):
	pattern = '"' + name + '"'
	found = []
	for path in sorted((REPO / "CvGameCoreDLL").glob("*.[ch]*")):
		for number, line in enumerate(path.read_text(encoding="latin-1").splitlines(), 1):
			if pattern in line:
				found.append("%s:%d" % (path.relative_to(REPO).as_posix(), number))
	return found


def main():
	parser = argparse.ArgumentParser(description="Report which Civ4 binaries hold each name as a string of its own, and where the DLL source quotes it.")
	parser.add_argument("names", nargs="+")
	parser.add_argument("--file", action="append", type=Path, help="a binary to search instead of the two BtS EXEs and BtS's DLL; repeatable")
	parser.add_argument("--context", action="store_true", help="show the strings beside each first hit")
	args = parser.parse_args()
	files = args.file or list(DEFAULT_FILES)
	datas = {}
	for path in files:
		if not path.is_file():
			raise SystemExit("%s: not found" % path)
		datas[path] = path.read_bytes()
	for name in args.names:
		print(name)
		for path, data in datas.items():
			hits = ascii_hits(data, name)
			wide = wide_hits(data, name)
			line = "  %s: %d ASCII, %d UTF-16" % (path.name, len(hits), wide)
			if args.context and hits:
				line += "  " + neighbours(data, hits[0])
			print(line)
		quotes = source_quotes(name)
		print("  DLL source: %s" % (", ".join(quotes) if quotes else "not quoted"))
	return 0


if __name__ == "__main__":
	sys.exit(main())

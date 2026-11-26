#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every custom comment in Python and C++ closes before code or the next custom comment.
# <!-- custom: A custom note in # or // lines ends at its closing marker; one left open reads as part of the next note, so its credit and its end go missing unseen.
# On 2026-11-26 a scripted edit of SASCurrentDefines.py removed the line closing one, and the next note's closing marker then closed both, so the reflow helper saw one valid block; the user asked for a check. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds Python files to tokenize, pathlib walks the folders, sys reports the result and tokenize finds Python's comments. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root


SCAN = ((Path("Assets/Python"), ".py"), (Path("PrivateMaps"), ".py"), (Path("CvGameCoreDLL"), ".cpp"), (Path("CvGameCoreDLL"), ".h"), (Path("CvGameCoreDLL"), ".inl"), (Path(".github"), ".py"), (Path("LLM_Helpers"), ".py"), (Path("tests"), ".py"))
OPEN = "<!-- custom:"
CLOSE = "-->"


def read_text(path):
	data = path.read_bytes()
	try:
		return data.decode("utf-8")
	except UnicodeDecodeError:
		return data.decode("latin-1")


def python_comments(text):
	# <!-- custom: [(line, comment text, whole line is a comment)] from tokenize, so a marker inside any string, a triple-quoted one included, is no comment; Codex's review (GPT-6.2-Sol) reproduced the first version's line scan taking one in a docstring for a note. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	lines = text.split("\n")
	result = []
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		if token.type == tokenize.COMMENT:
			row, col = token.start
			result.append((row, token.string, not lines[row - 1][:col].strip()))
	return result


def cpp_comments(text):
	# <!-- custom: [(line, comment text, whole line is a comment, ends a block comment)] for // comments and each line's part of a /* */ block, outside strings. (Claude code Opus 5.5) -->
	result = []
	in_block = False
	for number, line in enumerate(text.split("\n"), 1):
		index = 0
		quote = None
		segment_start = 0 if in_block else None
		code_before = False
		while index < len(line):
			if in_block:
				end = line.find("*/", index)
				if end == -1:
					result.append((number, line[index:], not code_before, False))
					index = len(line)
					break
				result.append((number, line[index:end], not code_before, True))
				in_block = False
				index = end + 2
				continue
			char = line[index]
			if quote:
				if char == "\\":
					index += 2
					continue
				if char == quote:
					quote = None
			elif char in "\"'":
				quote = char
				code_before = True
			elif line.startswith("//", index):
				result.append((number, line[index:], not code_before, False))
				break
			elif line.startswith("/*", index):
				in_block = True
				index += 2
				continue
			elif not char.isspace():
				code_before = True
			index += 1
	return result


def unclosed(text, python):
	# <!-- custom: Yields (opened line, reason) for each custom note not closed before code, before the next note opens, before its block comment ends or before the end of the file; a note continues only over lines that are wholly comments.
	# Markers are read in order within a line, so a second note opened before the first closes fails, which the first version missed, as did a note left open inside /* */ (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	text = text.replace("\r\n", "\n")
	comments = python_comments(text) if python else cpp_comments(text)
	by_line = {}
	for entry in comments:
		by_line.setdefault(entry[0], []).append(entry)
	total = text.count("\n") + 1
	opened = None
	for number in range(1, total + 1):
		entries = by_line.get(number, [])
		if opened is not None and not (entries and entries[0][2]):
			yield opened, "not closed before code at line %d" % number
			opened = None
		for entry in entries:
			body = entry[1]
			index = 0
			while True:
				next_open = body.find(OPEN, index)
				next_close = body.find(CLOSE, index)
				if opened is not None:
					if next_open != -1 and (next_close == -1 or next_open < next_close):
						yield opened, "not closed before another custom comment opens at line %d" % number
						opened = number
						index = next_open + len(OPEN)
						continue
					if next_close == -1:
						break
					opened = None
					index = next_close + len(CLOSE)
					continue
				if next_open == -1:
					break
				opened = number
				index = next_open + len(OPEN)
			if opened is not None and not python and entry[3]:
				yield opened, "not closed before its block comment ends at line %d" % number
				opened = None
	if opened is not None:
		yield opened, "not closed before the end of the file"


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that every custom comment in Python and C++ closes with --> before code or the next custom comment.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for folder, suffix in SCAN:
		root = args.repo_root / folder
		if not root.is_dir():
			continue
		for path in sorted(root.rglob("*" + suffix)):
			if "temp_files" in path.parts or "outputs" in path.parts or "context" in path.parts:
				continue
			count += 1
			for line, reason in unclosed(read_text(path), suffix == ".py"):
				errors.append("%s:%d: custom comment %s" % (path.relative_to(args.repo_root).as_posix(), line, reason))
	print("%s custom comments closed (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

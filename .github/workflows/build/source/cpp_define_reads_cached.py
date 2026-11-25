#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the DLL reads each SAS define by name once, not on every call.
# <!-- custom: GC.getDefineINT("SAS_X") looks the name up in a string map each time, so a read on a recurring path belongs in a function-local static const or AdvCiv's enum-backed CvGlobals cache, as AGENTS.md's caching rules say.
# A read that runs once or rarely anyway, such as a lazy setting cache or an EXE patch at startup, says so in its function with a ci_define_uncached: comment; an existing reason needs only that prefix.
# A first draft took "Not cached:", then define-uncached:, but the user found both too generic: such words can appear in any prose, so an unrelated comment in the same function could exempt a recurring read unnoticed, and a grep would mix exemptions with ordinary comments; the ci_ prefix, as in the [ci_update_dll] commit marker, names a token only this check reads.
# The 2026-11-25 audit found one recurring case among 545 reads: SAS_logFirstCityShadowScoutEntry read SAS_1ST_CITY_SCOUT_FOG_END_REF_PLOT_MULT for each frontier plot, while the gameplay path beside it already kept it in a static. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, pathlib walks the folders, re finds the reads and sys reports the result. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root
# <!-- custom: The marker's one spelling, kept in lib/ci_markers.py with the other CI markers. (Claude code Opus 5.5) -->
from ci_markers import DEFINE_UNCACHED as MARKER


SOURCE_DIR = Path("CvGameCoreDLL")
SOURCE_SUFFIXES = (".cpp", ".h", ".inl")
READ = re.compile(r'\bgetDefine(?:INT|BOOL|FLOAT|STRING)\s*\(\s*"(\w+)"')
# <!-- custom: String contents are blanked to x before this matches, so extern "C" reads as extern "x"; the first version wanted "C" and gave two functions inside an extern "C" block one region, as Codex reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
CONTAINER_HEAD = re.compile(r'(^|[\s;}])(namespace|class|struct|union|enum)\b[^;]*$|extern\s+"\w*"\s*$')
LOOP_HEAD = re.compile(r'^\s*(for|while|do)\b')


def blank_source(text):
	# <!-- custom: Returns three copies of the file with the same length, so offsets match: code with comments blanked; the same with string contents and preprocessor lines blanked too, so braces or semicolons there count for nothing; and the comments alone, where the marker counts.
	# Codex's review (GPT-6.2-Sol) reproduced a marker inside a string, log("ci_define_uncached: ..."), exempting a read, and a #if line before a static hiding the static; a line splice inside a call hid the read, so a backslash before a newline now reads as a space. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	code = list(text)
	bare = list(text)
	comments = [c if c == "\n" else " " for c in text]
	i = 0
	n = len(text)
	line_start = True
	while i < n:
		c = text[i]
		if c == "\\" and i + 1 < n and text[i + 1] == "\n":
			code[i] = bare[i] = " "
			i += 1
		elif text.startswith("//", i):
			j = text.find("\n", i)
			j = n if j < 0 else j
			for k in range(i, j):
				comments[k] = text[k]
				code[k] = bare[k] = " "
			i = j
		elif text.startswith("/*", i):
			j = text.find("*/", i + 2)
			j = n if j < 0 else j + 2
			for k in range(i, j):
				if text[k] != "\n":
					comments[k] = text[k]
					code[k] = bare[k] = " "
			i = j
		elif c == "#" and line_start:
			j = i
			while j < n and not (text[j] == "\n" and text[j - 1] != "\\"):
				j += 1
			for k in range(i, j):
				if text[k] != "\n":
					bare[k] = " "
			i = j
		elif c == '"' or c == "'":
			j = i + 1
			while j < n and text[j] != c and text[j] != "\n":
				j += 2 if text[j] == "\\" else 1
			for k in range(i + 1, min(j, n)):
				bare[k] = "x"
			i = j + 1
		else:
			i += 1
		if 0 < i < n:
			line_start = text[i - 1] == "\n" or (line_start and text[i - 1] in " \t")
	return "".join(code), "".join(bare), "".join(comments)


def statement_start(bare, pos):
	# <!-- custom: Walks back from the read to the start of its statement, through enclosing calls and brace initializers, as in static const int ai[] = { GC.getDefineINT("SAS_A"), ... }.
	# A first version counted every } as nesting, so the } closing the block before static const bool bSAS_SCRAP_ON = ... in CvUnit.cpp carried the walk past its statement start; a } outside brackets now ends the walk, unless a comma follows it, as after the initializer in static int a[] = {0}, b = ..., Codex's other reproduction. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	depth = 0
	i = pos - 1
	while i >= 0:
		c = bare[i]
		if c in ")]":
			depth += 1
		elif c in "([":
			depth -= 1 if depth > 0 else 0
		elif c == "}" and depth == 0:
			if not bare[i + 1:i + 200].lstrip().startswith(","):
				break
			depth += 1
		elif c == "{":
			if depth > 0:
				depth -= 1
			else:
				before = bare[:i].rstrip()
				if not before or before[-1] not in "=,{(":
					break
		elif c == ";" and depth == 0:
			break
		i -= 1
	return i + 1


def blocks(bare):
	# <!-- custom: Each brace block as (kind, region start, open, close); a function's region starts after the previous statement at the enclosing level, so it covers the comments and signature above the body.
	# Namespaces, classes, structs and extern "C" blocks are containers; any other brace opened in one, or at file level, starts a function, such as SelfMod's inline methods, and braces inside a function are loops or other blocks. (Claude code Opus 5.5) -->
	found = []
	stack = []
	boundary = 0
	for i, c in enumerate(bare):
		if c == "{":
			in_function = any(kind == "function" for kind, _, _ in stack)
			if in_function:
				# <!-- custom: The same walk as a statement's, as a first version cut the head at the last ; and so read for (int i = 0; i < n; i++) { as " i++)", missing the loop. (Claude code Opus 5.5) -->
				head = bare[statement_start(bare, i):i]
				kind = "loop" if LOOP_HEAD.match(head) else "block"
			else:
				head = bare[boundary:i]
				if CONTAINER_HEAD.search(head.strip()) or head.rstrip().endswith("="):
					kind = "container"
				else:
					kind = "function"
			stack.append((kind, boundary, i))
			if kind == "container":
				boundary = i + 1
		elif c == "}" and stack:
			kind, start, opened = stack.pop()
			found.append((kind, start, opened, i))
			if not any(k == "function" for k, _, _ in stack):
				boundary = i + 1
		elif c == ";" and not any(k == "function" for k, _, _ in stack):
			boundary = i + 1
	return found


def uncached_reads(text, sas_only=True):
	# <!-- custom: The marker covers the reads after it in its function, but not a read inside a loop unless the marker sits inside that loop too: an annotation for a cold read at the top of a function no longer exempts a hot read in a loop below it, as Codex's review pointed out.
	# A function called on a hot path with no loop of its own is still covered by its marker, so the comment must be true, which review checks. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	code, bare, comments = blank_source(text)
	found = blocks(bare)
	hits = []
	for match in READ.finditer(code):
		name = match.group(1)
		if sas_only and not name.startswith("SAS_"):
			continue
		pos = match.start()
		start = statement_start(bare, pos)
		# <!-- custom: const static is the same cache as static const; Codex's second review found CvPlayerAI.cpp's const static reads counted as uncached by --all-defines. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if re.match(r"\s*(const\s+)?static\b", bare[start:pos]):
			continue
		functions = [b for b in found if b[0] == "function" and b[1] <= pos <= b[3]]
		if functions:
			scope = functions[-1][1]
			loops = [b[2] for b in found if b[0] == "loop" and b[2] <= pos <= b[3]]
			if loops:
				scope = max(scope, max(loops))
			if LOOP_HEAD.match(bare[start:pos]):
				scope = max(scope, start)
			if MARKER in comments[scope:pos]:
				continue
		hits.append((text.count("\n", 0, pos) + 1, name))
	return hits


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that the DLL keeps each SAS define it reads by name in a cache, or says why it reads it once.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	parser.add_argument("--all-defines", action="store_true", help="report inherited defines too (not checked by CI)")
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for path in sorted((args.repo_root / SOURCE_DIR).rglob("*")):
		if path.suffix not in SOURCE_SUFFIXES or "temp_files" in path.parts:
			continue
		count += 1
		text = path.read_bytes().decode("latin-1")
		for line, name in uncached_reads(text, not args.all_defines):
			errors.append("%s:%d: %s is read by name outside a static; cache it, or say why it runs once or rarely with a %s comment in the function" % (path.relative_to(args.repo_root).as_posix(), line, name, MARKER))
	print("%s DLL define reads cached (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

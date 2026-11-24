#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python does not store an attribute twice in a row with nothing able to read the first value.
# <!-- custom: A second `self.X = ...` that overwrites the first before anything reads it leaves a value a reader takes for live, such as SevoPediaTerrain's H_RELEVANT_UNITS, written twice from the same sum, or CvForeignAdvisor's X_LINK = 50 then 0.
# Within one block at one indentation, the first store is dead when no line between names X, calls a method on self, passes self on or aliases it (which may read it), or leaves early through return, break, continue, raise or yield.
# A first scan without those exits found 26 pairs, of which 13 were reads through such a call or an early return; of the other 13, five were fixed and eight are empty list resets, accepted below (2026-11-24). See KI#1098.3. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, pathlib walks the folders, re reads the lines, sys reports the result and tokenize tells code from comments and strings. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import re
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root


SCAN_RELATIVE_DIRS = (Path("Assets/Python"), Path("PrivateMaps"))
STORE = re.compile(r"^(\s*)self\.(\w+)\s*=(?!=)")
# <!-- custom: What may read the pending value without naming it: a method on self, self passed on or aliased, such as helper(self) or alias = self, or leaving the block early.
# The argument pattern first took any "(self", so a bracketed sum such as (self.H_MAP_MINIMAP_MAX * iGridW) hid CvMilitaryAdvisor's dead X_TEXT; bare self must now stand alone between separators.
# Codex (GPT-6.2-Sol) reproduced the alias case, alias = self; self.X = 1; read(alias); self.X = 2, flagged though read can see 1. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
SELF_CALL = re.compile(r"\bself\s*\.\s*\w+\s*\(|(^|[=(,\[{:])\s*self\s*($|[,)\]}])")
# <!-- custom: Once bare self escapes into a name or a call, any later call may read through it, so the rest of that function is left unchecked. (Claude code Opus 5.5) -->
SELF_BARE = re.compile(r"(^|[=(,\[{:])\s*self\s*($|[,)\]}])")
EARLY_EXIT = re.compile(r"^\s*(return|break|continue|raise|yield)\b")
# <!-- custom: An empty list reset such as `self.plotTypes = [] # reinit the array for each pass` right before the store that fills it misleads no reader about a live value; eight inherited map-generation lines use it, so it is accepted rather than edited out of their files.
# A first version also accepted None, "", () and {}, which no case needed and which could hide a real slip, as Codex's review pointed out. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
EMPTY_RESET = re.compile(r"^\s*\[\]\s*$")
TRY_START = re.compile(r"^\s*try\s*:")
TRY_CONTINUATION = re.compile(r"^\s*(except\b|else\s*:|finally\s*:)")


def read_text(path):
	data = path.read_bytes()
	try:
		return data.decode("utf-8")
	except UnicodeDecodeError:
		return data.decode("latin-1")


def code_lines(text):
	# <!-- custom: Each line's code with comments dropped and each string's content replaced by "", so a name or # inside a string or comment is neither a read nor a cut, and the lines inside a triple-quoted string read as empty.
	# A first version split each line at #, so self.X = 1; helper("#", self); self.X = 2 lost the self passed on and was flagged, as Codex reproduced, as were two stores inside a docstring. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	lines = text.split("\n")
	pieces = {}
	try:
		for token in tokenize.generate_tokens(io.StringIO(text).readline):
			if token.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
				continue
			row, col = token.start
			value = '""' if token.type == tokenize.STRING else token.string
			pieces.setdefault(row, []).append((col, token.end[1] if token.end[0] == row else col + len(value), value))
	except (tokenize.TokenError, IndentationError, SyntaxError):
		# <!-- custom: A file tokenize cannot read keeps the simpler cut at #, which is right for nearly every line. (Claude code Opus 5.5) -->
		return [line.split("#", 1)[0].rstrip() for line in lines]
	out = []
	for row, line in enumerate(lines, 1):
		parts = pieces.get(row)
		if not parts:
			out.append("")
			continue
		text_out = line[:parts[0][0]]
		previous_end = parts[0][0]
		for start, end, value in parts:
			text_out += line[previous_end:start] if start >= previous_end else " "
			text_out += value
			previous_end = end
		out.append(text_out.rstrip())
	return out


def dead_stores(text):
	hits = []
	pending = {}
	try_indents = []
	self_escaped = False
	for number, code in enumerate(code_lines(text), 1):
		stripped = code.strip()
		if not stripped:
			continue
		indent = len(code) - len(code.lstrip())
		if stripped.startswith("def "):
			self_escaped = False
		elif SELF_BARE.search(code):
			self_escaped = True
		for name in list(pending):
			if indent < pending[name][0]:
				del pending[name]
		# <!-- custom: A store inside a try block is never pending: a finally or except can read the first value when the second store raises, as in Codex's try: self.X = 1; self.X = risky() / finally: print(self.X). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		while try_indents and indent <= try_indents[-1] and not (indent == try_indents[-1] and TRY_CONTINUATION.match(code)):
			try_indents.pop()
		if TRY_START.match(code):
			try_indents.append(indent)
			pending.clear()
			continue
		in_try = bool(try_indents) or self_escaped
		if stripped.startswith(("def ", "class ")) or EARLY_EXIT.match(code) or SELF_CALL.search(code):
			match = STORE.match(code)
			pending.clear()
			# <!-- custom: A store whose own right side calls a method, as in self.X = self.getNextWidgetName(), still starts a pending value. (Claude code Opus 5.5) -->
			if match and not in_try and not stripped.startswith(("def ", "class ")):
				pending[match.group(2)] = (len(match.group(1)), number, bool(EMPTY_RESET.match(code[match.end():])))
			continue
		match = STORE.match(code)
		if match:
			name = match.group(2)
			rest = code[match.end():]
			if name in pending and pending[name][0] == len(match.group(1)) and not pending[name][2] and not re.search(r"\b%s\b" % name, rest):
				hits.append((pending[name][1], number, name))
			for other in list(pending):
				if other != name and re.search(r"\b%s\b" % other, code):
					del pending[other]
			if in_try:
				pending.pop(name, None)
			else:
				pending[name] = (len(match.group(1)), number, bool(EMPTY_RESET.match(rest)))
			continue
		for name in list(pending):
			if re.search(r"\b%s\b" % name, code):
				del pending[name]
	return hits


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that runtime Python does not overwrite a self attribute before anything can read it.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for relative in SCAN_RELATIVE_DIRS:
		for path in sorted((args.repo_root / relative).rglob("*.py")):
			count += 1
			for first, second, name in dead_stores(read_text(path)):
				errors.append("%s:%d: self.%s is stored again on line %d before anything can read it; remove the first store or say why it stays" % (path.relative_to(args.repo_root).as_posix(), first, name, second))
	print("%s Python dead stores (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

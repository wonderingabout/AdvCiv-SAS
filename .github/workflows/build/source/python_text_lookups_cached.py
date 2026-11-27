#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: Python looks a fixed text key up once, not at each pass of a loop.
# <!-- custom: getText("TXT_KEY_X", ()) cost about 0.8 microseconds a call in game, measured on 2026-11-27, against about 0.02 for a kept local or attribute, so a fixed key looked up inside a for or while body is read again at each pass for the same text.
# The text counterpart of KI#128.8's define reads in loops: run repo-wide first, it found 93 such lookups, now read once before their loop; a fixed lookup outside any loop runs once per call, about 0.08 ms for 100, so it is left alone.
# A lookup with arguments, about 3.6 microseconds, builds a new text each time, so it is not checked; nor are getText in a list comprehension, which this check does not see, nor a while's condition. See KI#128.10. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, pathlib walks the folders, sys reports the result and tokenize tells blocks, strings and comments apart. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root


# <!-- custom: The folders the game runs Python from, from lib/runtime_python.py, so runtime Python elsewhere, such as SASPilot's game files on its branch, is covered once it is listed there, while code that only documents, such as the collapsed 1.12 main interface in the docs examples, is not. (Claude code Opus 5.5) -->
from runtime_python import RUNTIME_PYTHON_DIRS


def read_text(path):
	data = path.read_bytes()
	try:
		return data.decode("utf-8")
	except UnicodeDecodeError:
		return data.decode("latin-1")


SKIPPED = (tokenize.NL, tokenize.COMMENT)


def significant(tokens, index, count):
	# <!-- custom: The next count tokens after index, skipping line breaks and comments inside brackets, so getText(\n"TXT_KEY_X", ()) is seen too. (Claude code Opus 5.5) -->
	found = []
	for token in tokens[index + 1:]:
		if token.type in SKIPPED:
			continue
		found.append(token)
		if len(found) == count:
			break
	return found


def fixed_key(tokens, index):
	# <!-- custom: The key when the getText at index takes a literal TXT_KEY and an empty tuple, getText("TXT_KEY_X", ()), else None. (Claude code Opus 5.5) -->
	following = significant(tokens, index, 6)
	strings = [token.string for token in following]
	if len(following) < 6 or strings[0] != "(" or following[1].type != tokenize.STRING:
		return None
	key = following[1].string.lstrip("uU").strip("\"'")
	if not key.startswith("TXT_KEY_") or strings[2:] != [",", "(", ")", ")"]:
		return None
	return key


def loop_lookups(text):
	# <!-- custom: Yields (line, key) for each fixed-key getText inside the body of a for or while loop, at module level or in a function.
	# A loop's header runs once, so a lookup in for x in getText(...) is not in the loop; the body opens with the INDENT after a header ending in a colon. (Claude code Opus 5.5) -->
	tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
	stack = []
	statement = []
	last_statement = []
	found = []
	for index, token in enumerate(tokens):
		kind = token.type
		if kind in SKIPPED:
			continue
		if kind == tokenize.INDENT:
			header = last_statement[0].string if last_statement else ""
			stack.append(header)
			continue
		if kind == tokenize.DEDENT:
			stack.pop()
			continue
		if kind in (tokenize.NEWLINE, tokenize.ENDMARKER):
			last_statement = statement
			statement = []
			continue
		statement.append(token)
		if kind != tokenize.NAME or token.string != "getText":
			continue
		key = fixed_key(tokens, index)
		if key is None:
			continue
		# <!-- custom: Only the blocks inside the innermost def count: a loop around a def runs the def statement, not its body. (Claude code Opus 5.5) -->
		inner = stack
		for position in range(len(stack) - 1, -1, -1):
			if stack[position] in ("def", "class"):
				inner = stack[position + 1:]
				break
		# <!-- custom: A one-line def's body runs when it is called, not at each pass of a loop around it, as Codex's review (GPT-6.2-Sol) reproduced with def f(): return getText(...) inside a loop. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if statement[0].string == "def":
			continue
		# <!-- custom: A one-line loop, for x in y: getText(...), has no INDENT, so its statement's own head counts too, when the lookup comes after the colon that ends the header outside brackets.
		# The first draft took any colon before it, so for x in {1: getText(...)}: was flagged though its iterable runs once, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		one_line = False
		if statement[0].string in ("for", "while"):
			depth = 0
			for part in statement[:-1]:
				if part.string in "([{":
					depth += 1
				elif part.string in ")]}":
					depth -= 1
				elif depth == 0 and part.string == ":":
					one_line = True
					break
		if any(header in ("for", "while") for header in inner) or one_line:
			found.append((token.start[0], key))
	return found


def python_files(repo_root):
	for folder in RUNTIME_PYTHON_DIRS:
		for path in sorted((repo_root / folder).rglob("*.py")):
			yield path, path.relative_to(repo_root).as_posix()


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that Python looks a fixed text key up once, not at each pass of a loop.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for path, rel in python_files(args.repo_root):
		count += 1
		try:
			lookups = loop_lookups(read_text(path))
		except (tokenize.TokenError, IndentationError, SyntaxError) as error:
			errors.append("%s: could not be tokenized (%s), so its text lookups were not checked" % (rel, error))
			continue
		for line, key in lookups:
			errors.append("%s:%d: %s is looked up at each pass of a loop; look it up once before the loop, or keep it, as its text does not change between passes (see KI#128.10)" % (rel, line, key))
	print("%s Python fixed text lookups outside loops (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python keeps each define it reads by name in a cache, or says why it cannot.
# <!-- custom: The Python counterpart of cpp_define_reads_cached.py: gc.getDefineINT("X") crosses into the DLL and looks the name up each time, 279 ns a read in game against 167 ns through SASCurrentDefines, so a read belongs in a cache, and one that cannot use it says why in its function with a ci_define_uncached: comment, so the choice is visible rather than remembered.
# A cache here is SASCurrentDefines, an attribute (self.x = ...), a name the function declares global, or a read under a lazy guard on one of them, such as if self.x is None or if getattr(self, "x", None) is None; a guard on a parameter, such as if fracXExp is None, falls back to the define at each call, so it is no cache.
# Run repo-wide first on 2026-11-26, it found 97 reads by name outside a cache in 54 functions, 49 of SAS defines and 48 of inherited ones; five ran in a loop, once per leader or tech, and are now read once before it.
# The first draft let each say why it ran once or rarely, but the user found once per deal, hotkey, map or popup still worth the measured saving, so all go through SASCurrentDefines but one, a river define map scripts set themselves.
# Inherited code is checked too, as in C++. See KI#128.9. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, keyword tells Python's keywords from names, pathlib walks the folders, sys reports the result and tokenize tells functions, statements and comments apart. (Claude code Opus 5.5) -->
import argparse
import io
import keyword
from pathlib import Path
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root
# <!-- custom: The marker's one spelling, shared with the C++ check, so one grep finds the exemptions of both. (Claude code Opus 5.5) -->
from ci_markers import DEFINE_UNCACHED as MARKER


SCAN_RELATIVE_DIRS = (Path("Assets/Python"), Path("PrivateMaps"))
READERS = ("getDefineINT", "getDefineFLOAT", "getDefineSTRING", "getDefineBOOL")


def read_text(path):
	data = path.read_bytes()
	try:
		return data.decode("utf-8")
	except UnicodeDecodeError:
		return data.decode("latin-1")


class Block:
	def __init__(self, header, function):
		self.header = header
		self.function = function
		self.globals = set()
		self.marked = False
		self.reads = []
		self.loop = bool(header) and header[0].string in ("for", "while")
		self.indent = 0


SKIPPED = (tokenize.NL, tokenize.COMMENT)


def significant(tokens, index, count):
	# <!-- custom: The next count tokens after index, skipping line breaks and comments inside brackets: gc.getDefineINT(\n"X") was missed, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	found = []
	for token in tokens[index + 1:]:
		if token.type in SKIPPED:
			continue
		found.append(token)
		if len(found) == count:
			break
	return found


def cache_target(tokens, function):
	# <!-- custom: True when tokens name a cache that outlives the call: an attribute of self, getattr(self, "x", None), or a name the function declares global. (Claude code Opus 5.5) -->
	strings = [token.string for token in tokens]
	# <!-- custom: Names and dots alternate, so "self .
	# ready and value", where and and value are name tokens too, is no attribute. (Claude code Opus 5.5) -->
	if len(strings) >= 3 and len(strings) % 2 == 1 and strings[0] == "self" and all(strings[i] == "." for i in range(1, len(strings), 2)) and all(tokens[i].type == tokenize.NAME and not keyword.iskeyword(strings[i]) for i in range(0, len(strings), 2)):
		return True
	if len(strings) == 8 and strings[:4] == ["getattr", "(", "self", ","] and tokens[4].type == tokenize.STRING and strings[5:] == [",", "None", ")"]:
		return True
	return len(strings) == 1 and strings[0] in function.globals


# <!-- custom: A heuristic: the read under the guard is not tied to filling that cache, so if self.x is None: return gc.getDefineINT("X") passes though it reads at each call, as Codex's review (GPT-6.2-Sol) found.
# Tying it would reject the valid pattern of getGGBarTextMode, which reads into a local, checks it and only then stores it; review such a guard by eye. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def lazy_guard(header, function):
	# <!-- custom: An "if <cache> is None:" header, the cache being one cache_target accepts: the read under it runs once, to fill that cache.
	# The first draft accepted any if holding self and is None, so if self.ready and value is None passed, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if len(header) < 5 or header[0].string not in ("if", "elif") or header[-1].string != ":":
		return False
	if [token.string for token in header[-3:-1]] != ["is", "None"]:
		return False
	return cache_target(header[1:-3], function)


def colon_split(statement):
	# <!-- custom: The position of the first colon outside brackets, which ends a one-line if's condition. (Claude code Opus 5.5) -->
	depth = 0
	for index, token in enumerate(statement):
		if token.string in "([{":
			depth += 1
		elif token.string in ")]}":
			depth -= 1
		elif depth == 0 and token.string == ":":
			return index
	return None


def stores_once(statement, function, inner):
	# <!-- custom: True when the statement fills a cache that is set once: in __init__, outside any loop, or under a lazy guard, a block's or a one-line if's.
	# The first draft took any store into an attribute of self or a global as a cache, so self.x = gc.getDefineINT("X") in a method called at each draw, or inside a loop, passed while it read at each call, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if any(lazy_guard(block.header, function) for block in inner[1:]):
		return True
	if statement and statement[0].string in ("if", "elif"):
		colon = colon_split(statement)
		if colon is not None and lazy_guard(statement[:colon + 1], function):
			return True
	if function.function != "__init__" or any(block.loop for block in inner[1:]):
		return False
	depth = 0
	for index, token in enumerate(statement):
		if token.string in "([{":
			depth += 1
		elif token.string in ")]}":
			depth -= 1
		elif depth == 0 and token.type == tokenize.OP and token.string == "=":
			return cache_target(statement[:index], function)
	return False


def uncached_reads(text):
	# <!-- custom: Yields (line, define, function) for each literal read by name inside a function, outside any cache, whose function has no marker comment.
	# A read inside a for or while body runs at each pass, so, as in the C++ check, only a marker inside its innermost loop covers it; a read in a for's own header, such as range(gc.getDefineINT("MAX_TRADE_ROUTES")), runs once and follows the function's marker, while a while's condition runs at each test, so it belongs to that loop.
	# Reads at module level or in a class body run at import, which python_define_reads_import.py rejects, so they are left to it; reads through a variable name, as SASCurrentDefines and the overrides bridge make, are the caches themselves. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
	stack = []
	statement = []
	last_statement = []
	pending_marker = False
	pending_column = 0
	pending_while = []
	found = []

	def function_of(blocks):
		for block in reversed(blocks):
			if block.function:
				return block
		return None

	def mark(column):
		owner = function_of(stack)
		if owner is not None:
			for inner in stack[stack.index(owner):]:
				if inner.indent <= column:
					inner.marked = True

	def close(block):
		if block.function:
			for line, name, loop in block.reads:
				if not (loop or block).marked:
					found.append((line, name, block.function))

	for index, token in enumerate(tokens):
		kind = token.type
		if kind == tokenize.COMMENT:
			if MARKER in token.string:
				# <!-- custom: A comment between a block's header, a def's or a loop's, and its first statement comes before the INDENT that opens the body, so it is held for that body; the first draft credited it to the enclosing function, so a marker just inside a loop did not cover it. (Claude code Opus 5.5) -->
				if last_statement and last_statement[-1].string == ":" and not statement:
					pending_marker = True
					pending_column = token.start[1]
				elif statement and statement[0].string == "def":
					pending_marker = True
					pending_column = token.start[1]
				else:
					# <!-- custom: The comment marks its function and every block between them whose body it sits in, so it covers a loop only when it sits inside that loop.
					# Its column decides, not the stack: a comment line before a dedent comes before the DEDENT tokens, so the first draft credited a function-level reason after a loop to that loop, as a test caught. (Claude code Opus 5.5) -->
					mark(token.start[1])
			continue
		if kind == tokenize.NL:
			continue
		if kind == tokenize.INDENT:
			header = last_statement
			name = header[1].string if len(header) > 1 and header[0].string == "def" else None
			block = Block(header, name)
			block.indent = token.end[1]
			stack.append(block)
			for read in pending_while:
				read[2] = block
			pending_while = []
			if pending_marker:
				mark(pending_column)
			pending_marker = False
			continue
		if kind == tokenize.DEDENT:
			close(stack.pop())
			continue
		if kind in (tokenize.NEWLINE, tokenize.ENDMARKER):
			if statement and statement[0].string == "global":
				block = function_of(stack)
				if block is not None:
					block.globals.update(t.string for t in statement[1:] if t.type == tokenize.NAME)
			# <!-- custom: A one-line def keeps its body on its own line, with no INDENT, so its reads are judged here, its marker being a comment on that line. (Claude code Opus 5.5) -->
			if statement and statement[0].string == "def":
				one_line = Block(statement, statement[1].string)
				body = False
				depth = 0
				for position, part in enumerate(statement):
					if part.string in "([{":
						depth += 1
					elif part.string in ")]}":
						depth -= 1
					elif depth == 0 and part.string == ":":
						body = True
					elif body and part.string in READERS:
						following = significant(statement, position, 2)
						if len(following) == 2 and following[0].string == "(" and following[1].type == tokenize.STRING:
							one_line.reads.append((part.start[0], following[1].string.strip("\"'"), None))
				one_line.marked = pending_marker
				if one_line.reads:
					close(one_line)
					pending_marker = False
			last_statement = statement
			statement = []
			continue
		statement.append(token)
		if kind == tokenize.NAME and token.string in READERS:
			following = significant(tokens, index, 2)
			if len(following) < 2 or following[0].string != "(" or following[1].type != tokenize.STRING:
				continue
			block = function_of(stack)
			if block is None or statement[0].string == "def":
				continue
			inner = stack[stack.index(block):]
			if stores_once(statement, block, inner):
				continue
			loops = [b for b in inner[1:] if b.loop]
			read = [token.start[0], following[1].string.strip("\"'"), loops and loops[-1] or None]
			if statement[0].string == "while":
				pending_while.append(read)
			block.reads.append(read)
	while stack:
		close(stack.pop())
	return sorted(found)


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that runtime Python keeps each define it reads by name in a cache, or says why it cannot.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for relative in SCAN_RELATIVE_DIRS:
		for path in sorted((args.repo_root / relative).rglob("*.py")):
			count += 1
			rel = path.relative_to(args.repo_root).as_posix()
			try:
				reads = uncached_reads(read_text(path))
			except (tokenize.TokenError, IndentationError, SyntaxError) as error:
				errors.append("%s: could not be tokenized (%s), so its define reads were not checked" % (rel, error))
				continue
			for line, name, function in reads:
				errors.append("%s:%d: %s is read by name at each call of %s(); read it through SASCurrentDefines, or keep it in an attribute or a lazy global; a define other code sets during play, which SASCurrentDefines would miss, says so with a %s comment in the function" % (rel, line, name, function, MARKER))
	print("%s Python define reads cached (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

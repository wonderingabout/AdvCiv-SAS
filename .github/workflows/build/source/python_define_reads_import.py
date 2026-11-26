#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python reads no GlobalDefine while its module is imported.
# <!-- custom: A define read at module level, or in a class body, runs once at import and keeps that value for the session, so a live override never reaches it; AGENTS.md prefers reading after setup, lazily, as early reads were linked to instability in KI#128.
# The 2026-11-26 inventory found 16 such reads, 15 SAS switches in the Sevopedia and BUG's PEACE_TREATY_LENGTH in MoreCiv4lerts.py, all now read at use; this check keeps new ones out, repo-wide. See KI#128.6. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, pathlib walks the folders, sys reports the result and tokenize tells function bodies from module code. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root


SCAN_RELATIVE_DIRS = (Path("Assets/Python"), Path("PrivateMaps"))
READERS = ("getDefineINT", "getDefineFLOAT", "getDefineSTRING", "getDefineBOOL")
# <!-- custom: SASCurrentDefines read at import would cache as early, so its getters count too, after their module name. (Claude code Opus 5.5) -->
CURRENT_READERS = ("getInt", "getFloat", "getString")
SKIPPED = (tokenize.NL, tokenize.COMMENT)


def read_text(path):
	data = path.read_bytes()
	try:
		return data.decode("utf-8")
	except UnicodeDecodeError:
		return data.decode("latin-1")


def import_time_reads(text):
	# <!-- custom: Tokens rather than indentation decide scope: a def's signature can span several lines with comments at another indent, as CvMapGeneratorUtil's __init__ signatures do, which misled the first line-based audit.
	# Each INDENT opens the block of the statement before it, a def, a class or anything else; a read counts only when no def body encloses it, a one-line def or a lambda body included. (Claude code Opus 5.5) -->
	# <!-- custom: A def's header and a lambda's arguments run where they stand: the first version treated the whole line as a function, so def f(x=gc.getDefineINT("X")), lambda x=gc.getDefineINT("X"): x and (lambda: None, gc.getDefineINT("X")) passed, as Codex reproduced.
	# So a def's body starts at the colon closing its header, and a lambda's body runs from its colon to the comma or bracket closing it at its own depth. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	stack = []
	head = None
	last_head = None
	depth = 0
	header_depth = None
	body_line = False
	lambdas = []
	reader = None
	previous = []
	hits = []
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		kind = token.type
		if kind in SKIPPED:
			continue
		if kind == tokenize.INDENT:
			stack.append(last_head)
			continue
		if kind == tokenize.DEDENT:
			stack.pop()
			continue
		if kind == tokenize.NEWLINE:
			last_head = head
			head = None
			header_depth = None
			body_line = False
			lambdas = []
			reader = None
			continue
		if head is None:
			head = token.string if kind == tokenize.NAME and token.string in ("def", "class") else "other"
		in_function = body_line or [entry for entry in lambdas if entry[1]]
		if reader is not None and kind == tokenize.OP and token.string == "(":
			if "def" not in stack and not in_function:
				hits.append((reader.start[0], reader.string))
		reader = None
		if kind == tokenize.OP:
			if token.string in "([{":
				depth += 1
			elif token.string in ")]}":
				depth -= 1
				lambdas = [entry for entry in lambdas if entry[0] <= depth]
			elif token.string == ":":
				if header_depth == depth:
					header_depth = None
					body_line = True
				elif lambdas and lambdas[-1][0] == depth and not lambdas[-1][1]:
					lambdas[-1][1] = True
			elif token.string == ",":
				lambdas = [entry for entry in lambdas if not (entry[1] and entry[0] == depth)]
		if kind == tokenize.NAME:
			if token.string == "def":
				header_depth = depth
			elif token.string == "lambda":
				lambdas.append([depth, False])
			elif token.string in READERS or (token.string in CURRENT_READERS and previous[-2:] == ["SASCurrentDefines", "."]):
				reader = token
		previous = (previous + [token.string])[-2:]
	return hits


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that runtime Python reads no GlobalDefine at import.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for relative in SCAN_RELATIVE_DIRS:
		for path in sorted((args.repo_root / relative).rglob("*.py")):
			count += 1
			rel = path.relative_to(args.repo_root).as_posix()
			try:
				hits = import_time_reads(read_text(path))
			except (tokenize.TokenError, IndentationError, SyntaxError) as error:
				errors.append("%s: could not be tokenized (%s), so its define reads were not checked" % (rel, error))
				continue
			for line, name in hits:
				errors.append("%s:%d: %s runs at import, so its value is kept for the session and an override never reaches it; read it at use, through SASCurrentDefines for a SAS define" % (rel, line, name))
	print("%s Python define reads at import (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: a runtime Python module marked pure holds plain values only.
# <!-- custom: A module whose comment carries ci_pure_module: may hold, at top level, only comments and names bound to plain values, numbers, strings, booleans, None or tuples, lists and dicts of them, and nothing else: no import, call, def, class or computed value.
# So any module can import it at any time, early in startup, from a map script or from another leaf module, with no load-order or circular-import risk, as SASMagicNumbers.py's header has asked since 2026-06; until this check, only that comment kept it so.
# Added on 2026-11-27 with SASSessionTunables.py, the home of the settings only Python reads, which the user wanted kept pure like SASMagicNumbers.py, with a check so it stays so. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, ast reads each module's top-level statements, io and tokenize find the marker in comments only, pathlib walks the folders and sys reports the result. (Claude code Opus 5.5) -->
import argparse
import ast
import io
from pathlib import Path
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root
# <!-- custom: The folders the game runs Python from, and the marker's one spelling. (Claude code Opus 5.5) -->
from runtime_python import RUNTIME_PYTHON_DIRS
from ci_markers import PURE_MODULE


def marked(text):
	# <!-- custom: True when a comment, not a string, carries the marker. (Claude code Opus 5.5) -->
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		if token.type == tokenize.COMMENT and PURE_MODULE in token.string:
			return True
	return False


def plain(node):
	# <!-- custom: True for the values the rule promises: a number, a string, True, False or None, a minus sign before a number, and tuples, lists and dicts of them.
	# The first draft used ast.literal_eval, which also let a set and a complex number through and raised on a dict with a list key, as Codex's review (GPT-6.2-Sol) reproduced; the Python 2.4 compile checks the syntax itself. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if isinstance(node, ast.Constant):
		return isinstance(node.value, (int, float, str, bool, type(None))) and not isinstance(node.value, complex)
	if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
		return isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, (int, float)) and not isinstance(node.operand.value, bool)
	if isinstance(node, (ast.Tuple, ast.List)):
		return all(plain(element) for element in node.elts)
	if isinstance(node, ast.Dict):
		return all(key is not None and hashable(key) for key in node.keys) and all(plain(value) for value in node.values)
	return False


def hashable(node):
	# <!-- custom: A dict key must be a plain scalar or a tuple of such keys: {{}: 1} and {([],): 1} passed the second draft and raise TypeError when run, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if isinstance(node, ast.Tuple):
		return all(hashable(element) for element in node.elts)
	return plain(node) and not isinstance(node, (ast.List, ast.Dict))


def impure_statements(text):
	# <!-- custom: (line, what) for each top-level statement other than names bound to a plain value.
	# Python 3's ast reads these modules, as plain values parse alike in Python 2.4; a module it cannot parse fails, as a pure module has no Python 2 syntax to need.
	# Annotated and augmented assignments are refused too; header comments do a docstring's job. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	found = []
	for node in ast.parse(text).body:
		if isinstance(node, ast.Assign) and all(isinstance(target, ast.Name) for target in node.targets):
			if not plain(node.value):
				found.append((node.lineno, "a value that is not plain"))
			continue
		found.append((node.lineno, "a %s statement" % type(node).__name__.lower()))
	return found


def read_text(path):
	return path.read_bytes().decode("utf-8-sig")


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that runtime Python modules marked pure hold plain values only.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	pure = []
	for folder in RUNTIME_PYTHON_DIRS:
		for path in sorted((args.repo_root / folder).rglob("*.py")):
			rel = path.relative_to(args.repo_root).as_posix()
			text = read_text(path)
			try:
				if not marked(text):
					continue
			except (tokenize.TokenError, IndentationError, SyntaxError):
				continue
			pure.append(rel)
			try:
				statements = impure_statements(text)
			except SyntaxError as error:
				errors.append("%s: marked %s but could not be parsed (%s)" % (rel, PURE_MODULE, error))
				continue
			for line, what in statements:
				errors.append("%s:%d: marked %s but holds %s; a pure module holds plain values only, so move it to a module that may import and compute" % (rel, line, PURE_MODULE, what))
	print("%s Python pure modules (%d marked: %s)" % ("FAIL" if errors else "PASS", len(pure), ", ".join(pure) or "none"))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every CI marker is spelled once, in lib/ci_markers.py, and listed in the workflows README.
# <!-- custom: A marker, in a commit message such as [ci_update_dll] or in a source comment such as ci_define_uncached:, turns a check's failure into a handled exception, so a reader must be able to find what each one means and which check reads it.
# The user asked for this on 2026-11-25, when ci_define_uncached: joined two older comment tokens that each check had spelled in its own file and that no README section listed.
# Each marker in lib/ci_markers.py must have a row in a README table under a "CI markers" section, and no workflow script may spell a marker in its code, so a new marker can only come in through that file; comments and docstrings may name one. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, ast finds each script's string constants and docstrings, pathlib walks the folders, re finds marker-shaped strings and sys reports the result. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import argparse
import ast
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The markers themselves and the shared repository-root default. (Claude code Opus 5.5) -->
import ci_markers
from xml_defines import get_default_repo_root


README = Path(".github/workflows/README.md")
SCRIPT_DIRS = (Path(".github/workflows/build"), Path(".github/workflows/lib"))
MARKER_FILE = Path(".github/workflows/lib/ci_markers.py")
# <!-- custom: The marker shapes in use: a bracketed [ci_x] in a commit message, and a word ending in a colon, such as ci_define_uncached:, in a comment. (Claude code Opus 5.5) -->
MARKER_SHAPE = re.compile(r"\[ci_[a-z_]+\]|\bci_[a-z_]+:")
SECTION = re.compile(r"^## CI markers\b.*?(?=^## |\Z)", re.M | re.S)


def markers():
	return dict((name, value) for name, value in vars(ci_markers).items() if name.isupper() and isinstance(value, str))


def listed_markers(readme_text):
	listed = set()
	for section in SECTION.findall(readme_text):
		listed.update(re.findall(r"^\| `([^`]+)` \|", section, re.M))
	return listed


def code_strings(text):
	# <!-- custom: Each string constant in the script's syntax tree, docstrings left out as prose.
	# A first version read tokens and skipped any string alone on its line as a docstring, so Codex's second review (GPT-6.2-Sol) reproduced a marker alone on a line inside a call's brackets passing, "[ci_" "new_marker]" passing as two literals, and a real docstring with a comment after it failing; the tree joins adjacent literals and knows which strings are docstrings. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	try:
		tree = ast.parse(text)
	except SyntaxError:
		return
	docstrings = set()
	for node in ast.walk(tree):
		if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
			first = node.body[0]
			if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
				docstrings.add(id(first.value))
	for node in ast.walk(tree):
		if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
			yield node.lineno, node.value


def problems(repo_root):
	errors = []
	values = markers()
	listed = listed_markers((repo_root / README).read_text(encoding="utf-8"))
	for name, value in sorted(values.items()):
		if value not in listed:
			errors.append("%s: %s = %r has no row in a README \"CI markers\" table" % (MARKER_FILE.as_posix(), name, value))
	for value in sorted(listed - set(values.values())):
		errors.append("%s: %r is listed but not defined in %s" % (README.as_posix(), value, MARKER_FILE.as_posix()))
	for folder in SCRIPT_DIRS:
		for path in sorted((repo_root / folder).rglob("*.py")):
			relative = path.relative_to(repo_root)
			if relative == MARKER_FILE:
				continue
			for line, string in code_strings(path.read_text(encoding="utf-8", errors="replace")):
				spelled = [value for value in values.values() if value in string] or MARKER_SHAPE.findall(string)
				for value in sorted(set(spelled)):
					errors.append("%s:%d: %s is spelled here; import it from %s instead" % (relative.as_posix(), line, value, MARKER_FILE.as_posix()))
	return errors


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that every CI marker is spelled once in lib/ci_markers.py and listed in the workflows README.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = problems(args.repo_root)
	print("%s CI markers listed (%d markers)" % ("FAIL" if errors else "PASS", len(markers())))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: game Python lives where the runtime Python checks look.
# <!-- custom: Fails on a Python file that imports CvPythonExtensions, the engine module only the game provides, outside the folders and files lib/runtime_python.py lists, as such game Python would escape every runtime Python check at once, from the Python 2.4 compile to the define and text caching checks.
# That happened before the list existed: SASPilot's game files sat in LLM_Helpers/saspilot, which one check scanned and the others did not (2026-11-27).
# The import is a one-way signal, as Codex's review (GPT-6.2-Sol) put it: a loader can run a payload that uses the engine without importing it, so loaders such as SASPilot.py should point at listed paths too. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, pathlib builds the paths, subprocess asks Git for the files, sys reports the result and tokenize keeps comments and strings out. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import subprocess
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root
# <!-- custom: The runtime folders and files, and the reference copies to skip, from their one home. (Claude code Opus 5.5) -->
from runtime_python import REFERENCE_PYTHON_PREFIXES, RUNTIME_PYTHON_DIRS, RUNTIME_PYTHON_FILES

ENGINE = "CvPythonExtensions"


COMPOUND = ("if", "elif", "else", "try", "except", "finally", "for", "while", "with", "def", "class")


def simple_statements(line):
	# <!-- custom: Splits a logical line into its simple statements: at a semicolon outside brackets, and after the colon that ends a one-line compound header, so x = 1; import ... and if enabled: from ... import * are seen, which the first draft missed, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	parts = []
	current = []
	depth = 0
	for token in line:
		if token.string in "([{":
			depth += 1
		elif token.string in ")]}":
			depth -= 1
		if depth == 0 and token.type == tokenize.OP and token.string == ";":
			parts.append(current)
			current = []
			continue
		if depth == 0 and token.type == tokenize.OP and token.string == ":" and current and current[0].string in COMPOUND:
			current = []
			continue
		current.append(token)
	parts.append(current)
	return [part for part in parts if part]


def names_engine(statement):
	# <!-- custom: True when an import statement names CvPythonExtensions in a module position: each clause of import a.b as c, d up to its "as", or the module of from X import ...; the first draft matched any later name, so import os as CvPythonExtensions counted, as Codex's review reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	strings = [token.string for token in statement]
	if strings[0] == "from":
		module = []
		for part in strings[1:]:
			if part == "import":
				break
			module.append(part)
		return "".join(module) == ENGINE or "".join(module).startswith(ENGINE + ".")
	if strings[0] != "import":
		return False
	clause = []
	for part in strings[1:] + [","]:
		if part == ",":
			module = "".join(clause[:clause.index("as")] if "as" in clause else clause)
			if module == ENGINE or module.startswith(ENGINE + "."):
				return True
			clause = []
		elif part not in ("(", ")"):
			clause.append(part)
	return False


def imports_engine(text):
	# <!-- custom: The lines of the import statements that name CvPythonExtensions as their module, read from tokens, so a mention in a comment or a string, as the CI stubs' sys.modules["CvPythonExtensions"] makes, does not count. (Claude code Opus 5.5) -->
	found = []
	line = []
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		if token.type in (tokenize.NEWLINE, tokenize.ENDMARKER):
			for statement in simple_statements(line):
				if names_engine(statement):
					found.append(statement[0].start[0])
			line = []
			continue
		if token.type in (tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT):
			continue
		line.append(token)
	return found


def is_runtime(rel):
	return rel in RUNTIME_PYTHON_FILES or any(rel.startswith(folder + "/") for folder in RUNTIME_PYTHON_DIRS)


def candidates(repo_root):
	# <!-- custom: The files Git tracks, plus new ones it does not ignore, so a local .venv, node_modules or ignored scratch such as LLM_Helpers/outputs is never walked, as Codex's review (GPT-6.2-Sol) advised; the first draft walked every folder and filtered afterwards. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.py"], cwd=repo_root, capture_output=True, check=True).stdout.decode("utf-8")
	for rel in sorted(set(part for part in listed.split("\0") if part)):
		if rel.startswith(REFERENCE_PYTHON_PREFIXES) or is_runtime(rel) or not (repo_root / rel).is_file():
			continue
		yield repo_root / rel, rel


def read_text(path):
	# <!-- custom: utf-8-sig drops a UTF-8 BOM, which otherwise stuck to a first-line import and hid it, as Codex's review reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	data = path.read_bytes()
	try:
		return data.decode("utf-8-sig")
	except UnicodeDecodeError:
		return data.decode("latin-1")


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that game Python lives in the folders and files lib/runtime_python.py lists.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for path, rel in candidates(args.repo_root):
		count += 1
		try:
			lines = imports_engine(read_text(path))
		except (tokenize.TokenError, IndentationError, SyntaxError) as error:
			errors.append("%s: could not be tokenized (%s), so its imports were not checked" % (rel, error))
			continue
		for line in lines:
			errors.append("%s:%d: imports %s, which suggests code meant to run in the game, but lib/runtime_python.py does not list it, so no runtime Python check scans it; move it, list its folder, or list the file with its reason" % (rel, line, ENGINE))
	print("%s Python runtime placement (%d files outside the runtime folders)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

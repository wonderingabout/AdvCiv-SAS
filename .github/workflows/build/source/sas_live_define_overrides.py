#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the shipped SASLiveDefineOverrides.txt only overrides integer SAS defines with their own XML values, and its defines are read where an override reaches.
# <!-- custom: SASLiveDefineOverrides/SASLiveDefineOverrides.txt overrides SAS defines while Civ4 runs, on top of GlobalDefines_advciv_sas.xml, so a mistake there shows only in game: a name that is no XML integer define is rejected, and a define kept in a static or an attribute ignores its override.
# The shipped file may carry lines as a demonstration, as the user wants, but each must equal its XML value, so the game plays the same with the overrides on or off and the XML stays the one shipped value. See KI#128.5. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io and tokenize find Python comments, pathlib walks the folders, re finds the reads and sys reports the result. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import re
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default and the index reader the other shipped-default checks use for --staged, as local overrides usually stay unstaged. (Claude code Opus 5.5) -->
from xml_defines import add_staged_argument, get_default_repo_root
# <!-- custom: The game's own parser, the XML's integer defines and the NoEntry rules. (Claude code Opus 5.5) -->
# <!-- custom: ALLOWED_RELATIVE and read_allowed read SASLiveDefineOverridesAllowed.txt, the list of live defines. See KI#128.7. (Claude code Opus 5.5) -->
from sas_live_define_overrides_file import ALLOWED_RELATIVE, VALUES_RELATIVE, XML_RELATIVE, RepoSource, development_values, read_allowed, read_no_entry, read_values, xml_values
# <!-- custom: The C++ comment blanker the define-cache check uses, which keeps string contents, where the names are. (Claude code Opus 5.5) -->
from cpp_define_reads_cached import blank_source


# <!-- custom: The folders the game runs Python from come from lib/runtime_python.py, one list for every runtime Python check, so a new one is added once (2026-11-27). (Claude code Opus 5.5) -->
from runtime_python import RUNTIME_PYTHON_DIRS
PYTHON_ROOTS = RUNTIME_PYTHON_DIRS


def python_files(source: RepoSource):
	for top in PYTHON_ROOTS:
		for relative in source.files(top, (".py",)):
			yield relative


def blank_python_comments(text: str) -> str:
	# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced a commented-out read failing; comments are blanked first, keeping offsets.
	# A file the tokenizer rejects is scanned as is. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	lines = text.splitlines(keepends=True)
	try:
		for token in tokenize.generate_tokens(io.StringIO(text).readline):
			if token.type == tokenize.COMMENT:
				row, col = token.start
				line = lines[row - 1]
				lines[row - 1] = line[:col] + " " * (token.end[1] - col) + line[token.end[1]:]
	except (tokenize.TokenError, IndentationError, SyntaxError):
		return text
	return "".join(lines)


def line_of(text: str, offset: int) -> int:
	return text.count("\n", 0, offset) + 1


def problems(repo_root: Path, values: dict[str, object], xml_values: dict[str, tuple[str, object]], source: RepoSource | None = None) -> list[str]:
	source = source or RepoSource(repo_root)
	found = []
	no_entry = read_no_entry(repo_root, source=source)
	no_entry_names = set(name for name, _ in no_entry)
	dev_values = development_values(source)
	# <!-- custom: The allowed list says what the mod supports live, and the shipped file shows each of those defines at its XML value, so whoever opens it sees every live define; a define in neither file is refused in game. See KI#128.7. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	allowed = [name for name, _ in read_allowed(repo_root, source=source)]
	for name in allowed:
		if name not in xml_values:
			found.append(f"{name}: in {ALLOWED_RELATIVE} but no define in {XML_RELATIVE}")
		if name in no_entry_names:
			found.append(f"{name}: in both {ALLOWED_RELATIVE} and SASLiveDefineOverridesNoEntry.txt; a define is either supported live or never overridden")
		if name not in values:
			found.append(f"{name}: in {ALLOWED_RELATIVE} but has no shipped line in {VALUES_RELATIVE}; ship it at its XML value, so the file shows every live define")
	for name in values:
		if name not in allowed:
			found.append(f"{name}: has a shipped line but is not in {ALLOWED_RELATIVE}, so the game refuses it; list it there once its readers follow an override, or drop the line")
	names = sorted(set(values) | set(name for name in allowed if name in xml_values))
	for name in sorted(values):
		if values[name] != xml_values[name][1]:
			found.append(f"{name}: {values[name]!r} in the shipped overrides but {xml_values[name][1]!r} in {XML_RELATIVE}; a shipped override equals its XML value, so the game is the same with the overrides on or off")
		for listed, reason in no_entry:
			if name == listed:
				found.append(f"{name}: no override may name it, as SASLiveDefineOverridesNoEntry.txt says: {reason}")
				break
		# <!-- custom: A line wins over the XML, so a shipped line naming a define the toggle switches there would silently undo the toggle; such defines stay XML-only.
		# The user settled on 2026-11-26 that the shipped file lists the defines changed during a session, such as BBAI's categories, and not those set once. See KI#128.5. (Claude code Opus 5.5) -->
		if name in dev_values:
			found.append(f"{name}: toggle_dev_diagnostics.py switches it in {XML_RELATIVE}, where a shipped override would silently undo the toggle; leave it out of the shipped overrides")
	if not names:
		return found

	# <!-- custom: An override reaches a reader that asks for the define at each use; one kept in a module global or a self.
	# attribute keeps the XML value, so it is caught here.
	# A read through a name in a variable, as SASTextScale's, is not seen, so such a helper clears its own cache when the bridge's change count moves. (Claude code Opus 5.5) -->
	alternatives = "|".join(re.escape(name) for name in names)
	kept_python = re.compile(r"^(?:self\.\w+|[A-Za-z_]\w*)\s*=[^\n]*?\bgetDefine(?:INT|BOOL|FLOAT|STRING)\s*\(\s*[\"'](" + alternatives + r")[\"']", re.M)
	kept_attribute = re.compile(r"^[ \t]+self\.\w+\s*=[^\n]*?\bgetDefine(?:INT|BOOL|FLOAT|STRING)\s*\(\s*[\"'](" + alternatives + r")[\"']", re.M)
	for rel in python_files(source):
		text = blank_python_comments(source.read(rel))
		for pattern in (kept_python, kept_attribute):
			for match in pattern.finditer(text):
				found.append(f"{rel}:{line_of(text, match.start())}: {match.group(1)} is kept in a module global or attribute, so its override never reaches this reader; read it at each use")

	# <!-- custom: A static keeps the first value, whether read by name or through the enum cache; a read at each use, by name or as GC.getDefineINT(CvGlobals::NAME), sees each setDefineINT. (Claude code Opus 5.5) -->
	kept_static = re.compile(r"\bstatic\b[^;{}]*?(?:CvGlobals::|getDefine(?:INT|BOOL|FLOAT|STRING)\s*\(\s*\")(" + alternatives + r")\b")
	for rel in source.files("CvGameCoreDLL", (".cpp", ".h", ".inl"), recursive=False):
		code = blank_source(source.read(rel, "latin-1"))[0]
		for match in kept_static.finditer(code):
			found.append(f"{rel}:{line_of(code, match.start())}: {match.group(1)} is kept in a static, which keeps the first value; read GC.getDefineINT(CvGlobals::{match.group(1)}) at each use")
	return found


def comment_lines(text: str) -> list[int]:
	# <!-- custom: SASLiveDefineOverrides.txt holds values only, as the user decided on 2026-11-25: Civ4 rereads it during play, and each define's comment stays in the XML.
	# The bridge still skips a comment line, so this rule lives in CI. See KI#128.5. (Claude code Opus 5.5) -->
	return [number for number, line in enumerate(text.splitlines(), 1) if line.strip().startswith("#")]


def main(argv=None) -> int:
	parser = argparse.ArgumentParser(description="Check that the shipped SASLiveDefineOverrides.txt only overrides SAS defines with their own XML values, read where an override reaches.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	add_staged_argument(parser)
	args = parser.parse_args(argv)
	source = RepoSource(args.repo_root, args.staged)
	if args.staged:
		# <!-- custom: A file not yet in the index ships no overrides in the commit being checked, so it counts as empty; the first --staged run failed on such a file with "exists on disk, but not in the index" (2026-11-26). (Claude code Opus 5.5) -->
		text = source.read(VALUES_RELATIVE) if source.exists(VALUES_RELATIVE) else ""
	else:
		text = source.read(VALUES_RELATIVE)
	xml_text = source.read(XML_RELATIVE)
	try:
		values = read_values(args.repo_root, text, xml_text, source)
	except ValueError as error:
		print(f"FAIL SASLiveDefineOverrides: the file is rejected by the game's parser: {error}")
		return 1
	found = problems(args.repo_root, values, xml_values(args.repo_root, xml_text, source), source)
	for number in comment_lines(text):
		found.append(f"{VALUES_RELATIVE}:{number}: a comment line; SASLiveDefineOverrides.txt holds values only, and each define's comment stays in {XML_RELATIVE}")
	if found:
		print("FAIL SASLiveDefineOverrides")
		for item in found:
			print(f"  - {item}")
		return 1
	print(f"PASS SASLiveDefineOverrides: {len(values)} override(s), each equal to its XML value and read where an override reaches")
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Shared XML define helpers for GitHub workflow checks.
#
# This module runs outside Civ4, through GitHub Actions or a local Python 3 command.
# It does not need Civ4 Python 2.4 compatibility.

from pathlib import Path
import argparse
# <!-- custom: ast reads SASSessionTunables.py's literal values without importing it. (Claude code Opus 5.5) -->
import ast
# <!-- custom: subprocess reads the staged GlobalDefines blob for --staged default checks. (Claude code Opus 5.5) -->
import subprocess
import sys
import xml.etree.ElementTree as ET


def get_default_repo_root() -> Path:
	return Path(__file__).resolve().parents[3]


def local_name(tag: str) -> str:
	return tag.rsplit("}", 1)[-1]


def child_text_by_local_name(node: ET.Element, child_name: str) -> str | None:
	for child in list(node):
		if local_name(child.tag) == child_name:
			return (child.text or "").strip()
	return None


# <!-- custom: Development diagnostics are usually left enabled but unstaged, so local working-tree runs of the shipped-default checks failed although the commit candidate was clean.
# staged=True reads every checked file from the index, the same content GitHub checks after commit; unstaged companions fail rather than mixing sources, and outside a Git checkout it fails loudly instead of falling back to the working tree. (Claude code Opus 5.5) -->
def add_staged_argument(parser: argparse.ArgumentParser) -> None:
	parser.add_argument("--staged", action="store_true", help="check the staged (index) commit candidate instead of the working tree, ignoring unstaged development values")


def read_staged_bytes(repo_root: Path, relative: str) -> bytes:
	result = subprocess.run(["git", "show", ":" + relative], cwd=repo_root, capture_output=True)
	if result.returncode:
		raise RuntimeError(f"cannot read staged {relative}: {result.stderr.decode('utf-8', 'replace').strip()}")
	return result.stdout


# <!-- custom: Added staged so callers can parse the index blob for --staged; the default still reads the working tree. (Claude code Opus 5.5) -->
# <!-- custom: session_names adds those settings from SASSessionTunables.py, for a check of a shipped value that moved there, such as aip.py's SAS_SEVO_LEADER_AI_ON; each check names its own, and a named one must be an integer in that file.
# Any name in both files fails, whatever its type, so neither can hide the other; checks of the XML itself, such as define_int_bounds.py, name none and read the XML alone.
# The first version, include_session_tunables, merged every integer of the file and compared integers only, so a Python value could satisfy a check of an XML define, as Codex's review (GPT-6.2-Sol) found. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def read_global_define_ints(repo_root: Path, staged: bool = False, session_names: tuple[str, ...] = ()) -> dict[str, int]:
	relative = "Assets/XML/GlobalDefines_advciv_sas.xml"
	if staged:
		root = ET.fromstring(read_staged_bytes(repo_root, relative))
	else:
		path = repo_root / relative
		if not path.exists():
			raise RuntimeError(f"missing file: {path}")
		root = ET.parse(path).getroot()
	defines: dict[str, int] = {}

	for define in root.iter():
		if local_name(define.tag) != "Define":
			continue

		name = child_text_by_local_name(define, "DefineName")
		value_text = child_text_by_local_name(define, "iDefineIntVal")
		if name is None or value_text is None:
			continue

		try:
			defines[name] = int(value_text)
		except ValueError as exc:
			raise RuntimeError(f"{name} has non-int iDefineIntVal: {value_text!r}") from exc

	# <!-- custom: A revision without SASSessionTunables.py, such as a commit before the move, keeps these settings in the XML, read above; --staged met that case while the file was still untracked. (Claude code Opus 5.5) -->
	tunables = read_session_tunables(repo_root, staged) if session_names else None
	if tunables is not None:
		xml_names = {child_text_by_local_name(define, "DefineName") for define in root.iter() if local_name(define.tag) == "Define"}
		both = sorted(name for name in tunables if name in xml_names)
		if both:
			raise RuntimeError(f"in both GlobalDefines_advciv_sas.xml and SASSessionTunables.py, keep each in one: {', '.join(both)}")
		for name in session_names:
			value = tunables.get(name)
			if type(value) is not int:
				raise RuntimeError(f"{name}: expected an integer in SASSessionTunables.py, found {value!r}")
			defines[name] = value
	return defines


# <!-- custom: The settings only Python reads, which moved from GlobalDefines_advciv_sas.xml to Assets/Python/SASSessionTunables.py with their define names, read without importing the module: it holds plain values only, as python_pure_modules.py checks, so each top-level assignment is a literal.
# detail_manager.py first failed with "SAS_BILLBOARD_SCALE_PCT_FONT_2: missing define" after the move, as it read the XML alone. (Claude code Opus 5.5) -->
# <!-- custom: staged reads the index blob, as for the XML; a revision without the file, before the move, gives None, which callers tell apart from an empty file. (Claude code Opus 5.5) -->
def read_session_tunables(repo_root: Path, staged: bool = False) -> dict[str, object] | None:
	relative = "Assets/Python/SASSessionTunables.py"
	if staged:
		listed = subprocess.run(["git", "ls-files", "--error-unmatch", "--", relative], cwd=repo_root, capture_output=True)
		if listed.returncode:
			return None
		text = read_staged_bytes(repo_root, relative).decode("utf-8")
	else:
		path = repo_root / relative
		if not path.exists():
			return None
		text = path.read_text(encoding="utf-8")
	values: dict[str, object] = {}
	for node in ast.parse(text).body:
		if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
			values[node.targets[0].id] = ast.literal_eval(node.value)
	return values


def read_global_define_texts(repo_root: Path) -> dict[str, str]:
	path = repo_root / "Assets" / "XML" / "GlobalDefines_advciv_sas.xml"
	if not path.exists():
		raise RuntimeError(f"missing file: {path}")

	tree = ET.parse(path)
	defines: dict[str, str] = {}

	for define in tree.getroot().iter():
		if local_name(define.tag) != "Define":
			continue

		name = child_text_by_local_name(define, "DefineName")
		value_text = child_text_by_local_name(define, "DefineTextVal")
		if name is None or value_text is None:
			continue

		defines[name] = value_text

	return defines


def require_int_values(defines: dict[str, int], expected_by_name: dict[str, int]) -> list[str]:
	failures: list[str] = []

	for name, expected in sorted(expected_by_name.items()):
		if name not in defines:
			failures.append(f"{name}: missing define")
			continue

		actual = defines[name]
		if actual != expected:
			failures.append(f"{name}: expected {expected}, found {actual}")

	return failures


# <!-- custom: session_names added: the expected settings that moved to SASSessionTunables.py, passed to read_global_define_ints; the default keeps reading the XML alone. See KI#128.11. (Claude code Opus 5.5) -->
def run_global_define_check(title: str, expected_by_name: dict[str, int], description: str, session_names: tuple[str, ...] = ()) -> int:
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	# <!-- custom: session_names, the caller's settings that moved to SASSessionTunables.py, such as advisor_defaults.py's SAS_MILIT_UI_BATTLE_XY_ON. (Claude code Opus 5.5) -->
	defines = read_global_define_ints(args.repo_root, session_names=session_names)
	failures = require_int_values(defines, expected_by_name)

	if failures:
		print(f"FAIL {title}")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print(f"PASS {title}")
	return 0


# <!-- custom: session_names added, passed on to run_global_define_check. See KI#128.11. (Claude code Opus 5.5) -->
def main_from_expected_values(title: str, expected_by_name: dict[str, int], description: str, session_names: tuple[str, ...] = ()) -> None:
	sys.exit(run_global_define_check(title, expected_by_name, description, session_names))

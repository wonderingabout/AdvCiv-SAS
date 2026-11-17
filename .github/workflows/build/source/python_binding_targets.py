#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A Python binding must point at its own target, not a neighbour's: vanilla Civ IV bound TASK_CONSCRIPT to TASK_HURRY (KI#1090), three more enum names copied the line above (KI#1090.2), and three EventTrigger getters pointed at other getters (KI#122).
# Three exact rules, so deliberate renames pass: an enum binding .value("NAME", VALUE) fails when NAME is itself an enumerator of the DLL's headers but VALUE is another;
# a method binding .def("name", &Class::target) fails when Class declares its own name() and target is neither name nor its py/py_ wrapper;
# and inside python::class_<Owner>, a .def fails when it points at a class that is neither Owner nor one of its bases, as KI#122's getNumUnits pointed CvEventInfo at CvEventTriggerInfo.
# Comments are ignored in the bindings and the headers, as AdvCiv retires methods by commenting their declarations out. See KI#1090.2. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options, pathlib finds the files, re reads the bindings and declarations, sys reports the result. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
DLL = Path("CvGameCoreDLL")
VALUE = re.compile(r'\.value\(\s*"(\w+)"\s*,\s*(?:\w+::)?(\w+)\s*\)')
DEF = re.compile(r'\.def\(\s*"(\w+)"\s*,\s*&\s*(\w+)::(\w+)')
CLASS = re.compile(r"\bclass\s+(?:DllExport\s+)?(\w+)\b[^;{]*\{")
BASES = re.compile(r"\b(?:class|struct)\s+(?:DllExport\s+)?(\w+)\s*:\s*([^{;]+)\{")
OWNER = re.compile(r"class_\s*<\s*(\w+)")
# <!-- custom: An enumerator line, in a plain enum or between AdvCiv's ENUM_START and ENUM_END macros, which an enum { } pattern missed, TASK_CONSCRIPT among them. (Claude code Opus 5.5) -->
ENUMERATOR = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*(?:=[^,\n]*)?,?\s*$", re.MULTILINE)


def without_comments(text):
	# <!-- custom: Blanks // and /* */ comments outside string and character literals, keeping line breaks so line numbers still match. (Claude code Opus 5.5) -->
	out = []
	i = 0
	n = len(text)
	while i < n:
		c = text[i]
		if c in "\"'":
			j = i + 1
			while j < n and text[j] != c:
				j += 2 if text[j] == "\\" else 1
			out.append(text[i:j + 1])
			i = j + 1
		elif text.startswith("//", i):
			j = text.find("\n", i)
			i = n if j < 0 else j
		elif text.startswith("/*", i):
			j = text.find("*/", i + 2)
			j = n if j < 0 else j + 2
			out.append("\n" * text.count("\n", i, j))
			i = j
		else:
			out.append(c)
			i += 1
	return "".join(out)


def is_wrapper(name, target):
	# <!-- custom: py_getX and pyGetX are this codebase's Python wrappers for getX, bound under getX's own name. (Claude code Opus 5.5) -->
	lowered = target.lower()
	for prefix in ("py_", "py"):
		if lowered.startswith(prefix) and lowered[len(prefix):] == name.lower():
			return True
	return False


def header_facts(root):
	enumerators = set()
	classes = {}
	bases = {}
	for path in sorted((root / DLL).glob("*.h")):
		text = without_comments(path.read_text(encoding="utf-8", errors="replace"))
		enumerators.update(ENUMERATOR.findall(text))
		for match in CLASS.finditer(text):
			end = text.find("\n};", match.end())
			classes[match.group(1)] = classes.get(match.group(1), "") + text[match.end():end]
		for match in BASES.finditer(text):
			bases.setdefault(match.group(1), set()).update(re.findall(r"\w+", match.group(2)))
	return enumerators, classes, bases


def ancestors(name, bases, seen=None):
	seen = set() if seen is None else seen
	for base in bases.get(name, ()):
		if base not in seen:
			seen.add(base)
			ancestors(base, bases, seen)
	return seen


def binding_errors(path, relative, enumerators, classes, bases):
	text = without_comments(path.read_text(encoding="utf-8", errors="replace"))
	errors = []
	owners = [(match.start(), match.group(1)) for match in OWNER.finditer(text)]
	for match in DEF.finditer(text):
		owner = None
		for start, name in owners:
			if start < match.start():
				owner = name
		target = match.group(2)
		if owner and target != owner and target not in ancestors(owner, bases):
			errors.append("%s:%d: %s in %s's bindings points at %s::%s, a class that is neither %s nor one of its bases" % (relative, text.count("\n", 0, match.start()) + 1, match.group(1), owner, target, match.group(3), owner))
	for match in VALUE.finditer(text):
		name, value = match.groups()
		if name != value and name in enumerators:
			errors.append("%s:%d: enum name %s is bound to %s, though %s is an enumerator of its own" % (relative, text.count("\n", 0, match.start()) + 1, name, value, name))
	for match in DEF.finditer(text):
		name, cls, target = match.groups()
		if name == target or is_wrapper(name, target) or cls not in classes:
			continue
		if re.search(r"[\s\*&]" + re.escape(name) + r"\s*\(", classes[cls]):
			errors.append("%s:%d: %s is bound to %s::%s, though %s declares its own %s()" % (relative, text.count("\n", 0, match.start()) + 1, name, cls, target, cls, name))
	return errors


def main():
	parser = argparse.ArgumentParser(description="Check that Python bindings point at their own enumerator or method, not a neighbour's.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	enumerators, classes, bases = header_facts(args.repo_root)
	paths = sorted((args.repo_root / DLL).glob("Cy*Interface*.cpp"))
	errors = [error for path in paths for error in binding_errors(path, path.relative_to(args.repo_root).as_posix(), enumerators, classes, bases)]
	if errors:
		print("FAIL Python binding targets")
		for error in errors:
			print("  - " + error)
		return 1
	print("PASS Python binding targets (%d binding files, %d enumerators)" % (len(paths), len(enumerators)))
	return 0


if __name__ == "__main__":
	sys.exit(main())

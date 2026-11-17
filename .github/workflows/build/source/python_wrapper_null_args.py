#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A Python wrapper must pass Python's None on as NULL wherever the native function it calls takes NULL: vanilla Civ IV's wrappers dereferenced such arguments, so None raised "unidentifiable C++ exception" instead of meaning no plot or no attacker.
# KI#1091 (five CyUnit combat wrappers and pushMission) was found that way, and a scan for the pattern found ten more (KI#1091.2).
# The rule: in a Cy*.cpp wrapper, an argument written p->getX() fails when the native function's parameter at that position defaults to NULL in the DLL's headers. See KI#1091.2. (Claude code Opus 5.5) -->

# <!-- custom: argparse parses the options, pathlib finds the files, re reads the wrappers and declarations, sys reports the result. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import sys

# <!-- custom: python_binding_targets supplies without_comments, the binding check's comment stripper, so both checks read C++ the same way. (Claude code Opus 5.5) -->
from python_binding_targets import without_comments

ROOT = Path(__file__).resolve().parents[4]
DLL = Path("CvGameCoreDLL")
DECLARATION = re.compile(r"\b(\w+)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*(?:const\s*)?[;{]")
WRAPPER = re.compile(r"\n[\w:<>\*& ]+?\b(Cy\w+)::(\w+)\(([^)]*)\)\s*\{(.*?)\n\}", re.S)
POINTER_PARAMETER = re.compile(r"\bCy\w+\s*\*\s*(\w+)")
CALL = re.compile(r"->\s*(\w+)\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)")


def split_arguments(text):
	arguments, depth, current = [], 0, ""
	for c in text:
		depth += c == "("
		depth -= c == ")"
		if c == "," and depth == 0:
			arguments.append(current.strip())
			current = ""
		else:
			current += c
	if current.strip():
		arguments.append(current.strip())
	return arguments


def null_defaults(root):
	# <!-- custom: Function name -> one set of NULL-defaulted parameter positions per overload. (Claude code Opus 5.5) -->
	defaults = {}
	for path in sorted((root / DLL).glob("*.h")):
		text = without_comments(path.read_text(encoding="utf-8", errors="replace"))
		for match in DECLARATION.finditer(text):
			positions = {i for i, p in enumerate(match.group(2).split(",")) if re.search(r"=\s*NULL\b", p)}
			if positions:
				defaults.setdefault(match.group(1), []).append(positions)
	return defaults


def wrapper_errors(text, relative, defaults):
	errors = []
	text = without_comments(text)
	for wrapper in WRAPPER.finditer(text):
		names = POINTER_PARAMETER.findall(wrapper.group(3))
		for call in CALL.finditer(wrapper.group(4)):
			for position, argument in enumerate(split_arguments(call.group(2))):
				name = next((n for n in names if re.match(r"^%s\s*->" % n, argument)), None)
				if name and any(position in overload for overload in defaults.get(call.group(1), [])):
					line = text.count("\n", 0, wrapper.start()) + 2
					errors.append("%s:%d: %s::%s dereferences %s, while %s takes NULL there; pass Python's None on as (%s == NULL ? NULL : %s)" % (relative, line, wrapper.group(1), wrapper.group(2), name, call.group(1), name, argument))
	return errors


def main():
	parser = argparse.ArgumentParser(description="Fail when a Cy*.cpp Python wrapper dereferences an argument its native function accepts as NULL.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	defaults = null_defaults(args.repo_root)
	paths = sorted((args.repo_root / DLL).glob("Cy*.cpp"))
	errors = [error for path in paths for error in wrapper_errors(path.read_text(encoding="utf-8", errors="replace"), path.relative_to(args.repo_root).as_posix(), defaults)]
	for error in errors:
		print("FAIL " + error)
	if errors:
		return 1
	print("PASS Python wrapper NULL arguments (%d wrapper files)" % len(paths))
	return 0


if __name__ == "__main__":
	sys.exit(main())

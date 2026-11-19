#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the DLL source must not bring back the non-standard C++ that AdvCiv's advc.cppstd removed.
# <!-- custom: VC2003 accepts these forms, so the DLL builds and plays the same; a standard-conforming compiler such as Clang rejects them or leaves their behavior undefined.
# AdvCiv's 616238930 (2026-10-12) rewrote them in the BtS code it inherited, and the AdvCiv 1.14 merge brought that in, leaving none in SAS; this check keeps new SAS code, such as the SASPilot or save-transplant work, from adding them back. See KI#1099. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import re
import subprocess
import sys

# <!-- custom: cpp_lex masks comments and literals so a question mark or backslash inside them is not read as code; xml_defines gives the repository root. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from cpp_lex import mask_cpp
from xml_defines import get_default_repo_root


CPP_SUFFIXES = (".cpp", ".h", ".hpp", ".inl")
# <!-- custom: A void function's body, up to its opening brace; the parameter list may hold one level of nested parentheses, as default arguments such as (int)0 do. (Claude code Opus 5.5) -->
VOID_FUNCTION = re.compile(r"(?:^|[\n;}])[ \t]*(?:template\s*<[^>]*>\s*)?(?:(?:static|inline|virtual|__forceinline|friend)\s+)*void\s+([\w:~]+)\s*\((?:[^()]|\([^()]*\))*\)\s*(?:const\s*)?\{")
RETURN_VALUE = re.compile(r"\breturn\b(?=\s*[^\s;])")
INCLUDE_BACKSLASH = re.compile(r'^[ \t]*#[ \t]*include[ \t]*"[^"\n]*\\[^"\n]*"', re.M)
# <!-- custom: BtS read printf-style arguments as (char*)(&format+1), assuming they follow the last named one on the stack; va_start is the standard way. (Claude code Opus 5.5) -->
VARARGS_ADDRESS = re.compile(r"\(\s*char\s*\*\s*\)\s*\(\s*&\s*\w+\s*\+\s*1\s*\)")


def tracked_sources(repo_root):
	output = subprocess.run(["git", "-C", str(repo_root), "ls-files", "CvGameCoreDLL"], capture_output=True, text=True, check=True).stdout
	return [repo_root / name for name in output.splitlines() if name.lower().endswith(CPP_SUFFIXES)]


def line_of(text, position):
	return text.count("\n", 0, position) + 1


def body_end(masked, start):
	depth = 1
	index = start
	while index < len(masked) and depth:
		if masked[index] == "{":
			depth += 1
		elif masked[index] == "}":
			depth -= 1
		index += 1
	return index


def top_level_question(expression):
	# <!-- custom: Only a question mark outside parentheses makes the returned value itself a conditional; one inside a call's arguments, as in CySelectionGroup::pushMission's last two arguments, is an ordinary argument. (Claude code Opus 5.5) -->
	depth = 0
	for character in expression:
		if character in "([{":
			depth += 1
		elif character in ")]}":
			depth -= 1
		elif character == "?" and depth == 0:
			return True
	return False


def file_problems(relative, text):
	masked = mask_cpp(text)
	problems = []
	for function in VOID_FUNCTION.finditer(masked):
		start = function.end()
		body = masked[start:body_end(masked, start)]
		for statement in RETURN_VALUE.finditer(body):
			expression = body[statement.end():body.find(";", statement.end())]
			# <!-- custom: return f(); is valid in a void function when f returns void, so only a conditional is reported; standard C++ requires both branches of ?: to be void once one is, and BtS's return m_pPlayer ? m_pPlayer->disbandUnit(bAnnounce) : NULL; paired a void call with NULL. (Claude code Opus 5.5) -->
			if top_level_question(expression):
				problems.append("%s:%d: void function %s returns a ?: expression; use if/else, as AdvCiv's advc.cppstd does (KI#1099)" % (relative, line_of(text, start + statement.start()), function.group(1)))
	for include in INCLUDE_BACKSLASH.finditer(text):
		problems.append("%s:%d: #include path holds a backslash; write the header's own name with forward slashes, as AdvCiv's advc.cppstd does for CvReplayMessage.h (KI#1099)" % (relative, line_of(text, include.start())))
	for varargs in VARARGS_ADDRESS.finditer(masked):
		problems.append("%s:%d: reads varargs through the address after a named parameter; use va_list with va_start and va_end, as AdvCiv's advc.cppstd does in CvXMLLoadUtility.cpp (KI#1099)" % (relative, line_of(text, varargs.start())))
	return problems


def find_problems(repo_root):
	problems = []
	for path in tracked_sources(repo_root):
		if path.is_file():
			problems.extend(file_problems(path.relative_to(repo_root).as_posix(), path.read_text(encoding="latin-1")))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that the DLL source does not bring back the non-standard C++ that AdvCiv's advc.cppstd removed.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve())
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL C++ standard conformance (%d)" % len(problems))
		return 1
	print("PASS C++ standard conformance")
	return 0


if __name__ == "__main__":
	sys.exit(main())

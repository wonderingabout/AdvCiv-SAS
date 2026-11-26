#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: the base-game entry points SAS carries keep the functions the engine calls by name.
# <!-- custom: Nothing in SAS calls these functions, so a cleanup or rename would look safe and pass every other check, while the game or Pitboss would fail only on reaching the call.
# Each name below was found in the engine on 2026-11-26: as a string in Civ4BeyondSword.exe or Civ4BeyondSword_PitBoss.exe, or in the DLL's CvPythonCaller.cpp.
# The EXE registers every module in EntryPoints and every map script as an "EntryPoint module", so being registered does not show which functions it calls; CvMapScriptInterface.py's stubs are left out, as the map generator calls the active map script's functions, not these.
# Codex proposed checking a curated callback list on 2026-11-23, when the carry was decided. See KI#1104. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

from pathlib import Path
import argparse
import io
import sys
import tokenize

# <!-- custom: io and tokenize read the Python files' tokens; xml_defines from the workflows' lib/ gives the repository root, as the other build checks find it. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


MAIN_EXE = "Civ4BeyondSword.exe"
PITBOSS_EXE = "Civ4BeyondSword_PitBoss.exe"
# <!-- custom: Found in no engine file on 2026-11-26, so not listed: CvUnitControlInterface's ProcessEvent, CvDebugInterface's parseText and CvTranslator's printOutText, kept as copied. (Claude code Opus 5.5) -->
CALLBACKS = {
	"Assets/Python/EntryPoints/PbMain.py": {
		"create": PITBOSS_EXE,
		"run": PITBOSS_EXE,
		"update": PITBOSS_EXE,
		"patchAvailable": PITBOSS_EXE,
		"patchProgress": PITBOSS_EXE,
		"patchDownloadComplete": PITBOSS_EXE,
		"appUpToDate": PITBOSS_EXE,
		"refreshRow": PITBOSS_EXE,
		"refreshCustomMapOptions": PITBOSS_EXE,
		"refreshAdvancedStartPoints": PITBOSS_EXE,
		"getMessageOfTheDay": PITBOSS_EXE,
		"addChatMessage": PITBOSS_EXE,
		"displayMessageBox": PITBOSS_EXE,
		"sendEmail": "the DLL's CvPythonCaller::sendEmailReminder",
	},
	"Assets/Python/EntryPoints/CvTranslator.py": {
		"finishText": MAIN_EXE + " and " + PITBOSS_EXE,
	},
	"Assets/Python/EntryPoints/CvDebugInterface.py": {
		"toggleDebugMode": MAIN_EXE + " and " + PITBOSS_EXE,
	},
}


def defined_functions(text):
	# <!-- custom: Reads tokens, so only a def at column 0 counts and one inside a string or comment does not: a first, line-based version took a def in a triple-quoted string for a real one, as Codex's review reproduced (2026-11-26). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	names = set()
	tokens = [token for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type not in (tokenize.NL, tokenize.COMMENT)]
	for (token, following) in zip(tokens, tokens[1:]):
		if token.type == tokenize.NAME and token.string == "def" and token.start[1] == 0 and following.type == tokenize.NAME:
			names.add(following.string)
	return names


def find_problems(repo_root):
	problems = []
	for relative, callbacks in sorted(CALLBACKS.items()):
		path = repo_root / relative
		if not path.is_file():
			problems.append("%s: missing; the engine loads it by name, so carry it back or drop its entry here" % relative)
			continue
		defined = defined_functions(path.read_text(encoding="latin-1"))
		for name, caller in sorted(callbacks.items()):
			if name not in defined:
				problems.append("%s: no top-level def %s, which %s calls by name; keep it, or drop the entry if the engine no longer calls it (KI#1104)" % (relative, name, caller))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that the carried base-game entry points keep the functions the engine calls by name.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve())
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL Python engine callbacks (%d)" % len(problems))
		return 1
	print("PASS Python engine callbacks (%d functions in %d files)" % (sum(len(names) for names in CALLBACKS.values()), len(CALLBACKS)))
	return 0


if __name__ == "__main__":
	sys.exit(main())

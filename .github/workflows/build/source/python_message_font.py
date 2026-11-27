#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python adds on-screen messages through SASTextScale.
# <!-- custom: Fails on a call to addMessage or addImmediateMessage on anything but SASTextScale, outside SASTextScale.py itself, and on addCombatMessage outside CvUtil.addCombatMessageScaled.
# CvDLLInterfaceIFaceBase::addMessage wraps every message the DLL adds in the label font, but CyInterface()'s calls go to the EXE directly, so at an upscaled label size MoreCiv4lerts' "Cyrus will export Iron" sat small under the DLL's larger "Global Warming strikes near ..." in the user's screenshot.
# SASTextScale.addMessage and SASTextScale.addImmediateMessage, added for this, apply the same wrap; run repo-wide first, the check found 43 direct calls in 14 files, all now routed through them. See KI#117.2. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, pathlib walks the folders, sys reports the result and tokenize keeps comments and strings out. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root
# <!-- custom: The folders the game runs Python from. (Claude code Opus 5.5) -->
from runtime_python import RUNTIME_PYTHON_DIRS

METHODS = ("addMessage", "addImmediateMessage", "addCombatMessage")
HELPER = "Assets/Python/SASTextScale.py"
# <!-- custom: The forwarding functions, the only places allowed to call the engine's message methods: SASTextScale's addMessage and addImmediateMessage, and CvUtil.addCombatMessageScaled, which fixed Combat Log lines the same way earlier.
# The first draft exempted whole files, so a direct call anywhere in CvUtil.py passed, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
ALLOWED = {
	(HELPER, "addMessage"): "addMessage",
	(HELPER, "addImmediateMessage"): "addImmediateMessage",
	("Assets/Python/CvUtil.py", "addCombatMessageScaled"): "addCombatMessage",
}
SKIPPED = (tokenize.COMMENT, tokenize.NL)


def interface_names(tokens):
	# <!-- custom: Names the file binds to CyInterface(), such as BugUtil's interface = CyInterface(), whose message calls count as engine calls too. (Claude code Opus 5.5) -->
	names = set()
	for index in range(len(tokens) - 4):
		# <!-- custom: Not an attribute, as self.ui = CyInterface() made a bare ui elsewhere count, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if tokens[index].type == tokenize.NAME and (index == 0 or tokens[index - 1].string != ".") and [token.string for token in tokens[index + 1:index + 5]] == ["=", "CyInterface", "(", ")"]:
			names.add(tokens[index].string)
	return names


def direct_calls(text, rel=""):
	# <!-- custom: (line, method) for each engine message call outside its forwarding function, a call whose receiver is CyInterface() or a name bound to it, read from tokens so comments and strings do not count.
	# Heuristic: the first draft flagged any .addMessage(, so an unrelated inbox.addMessage(record) failed, as Codex's review reproduced; a receiver passed in from elsewhere is not seen. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	tokens = [token for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type not in SKIPPED]
	names = interface_names(tokens)
	found = []
	stack = []
	last = []
	statement = []
	for index, token in enumerate(tokens):
		if token.type == tokenize.INDENT:
			stack.append(last[1].string if len(last) > 1 and last[0].string == "def" else None)
			continue
		if token.type == tokenize.DEDENT:
			stack.pop()
			continue
		if token.type in (tokenize.NEWLINE, tokenize.ENDMARKER):
			last = statement
			statement = []
			continue
		statement.append(token)
		if token.type != tokenize.NAME or token.string not in METHODS or index < 2 or index + 1 >= len(tokens):
			continue
		if tokens[index - 1].string != "." or tokens[index + 1].string != "(":
			continue
		receiver = tokens[index - 2]
		engine = receiver.string in names or (receiver.string == ")" and index >= 4 and tokens[index - 3].string == "(" and tokens[index - 4].string == "CyInterface")
		if not engine:
			continue
		function = next((name for name in reversed(stack) if name), None)
		if ALLOWED.get((rel, function)) == token.string:
			continue
		found.append((token.start[0], token.string))
	return found


def read_text(path):
	return path.read_bytes().decode("utf-8-sig", errors="replace")


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that runtime Python adds on-screen messages through SASTextScale.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	for folder in RUNTIME_PYTHON_DIRS:
		for path in sorted((args.repo_root / folder).rglob("*.py")):
			rel = path.relative_to(args.repo_root).as_posix()
			count += 1
			try:
				calls = direct_calls(read_text(path), rel)
			except (tokenize.TokenError, IndentationError, SyntaxError) as error:
				errors.append("%s: could not be tokenized (%s), so its messages were not checked" % (rel, error))
				continue
			for line, method in calls:
				errors.append("%s:%d: calls %s directly, so its text keeps the stock size while the DLL's messages use the label font; call %s instead (see KI#117.2)" % (rel, line, method, "CvUtil.addCombatMessageScaled" if method == "addCombatMessage" else "SASTextScale." + method))
	print("%s Python messages use the label font (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

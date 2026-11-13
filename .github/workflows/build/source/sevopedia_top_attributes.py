#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every self.top.X a Sevopedia page reads is defined on the SevoPediaMain instance.

# <!-- custom: Each Sevopedia page reaches the main screen through self.top. On 2026-10-20 the Sevopedia colors moved from SevoPediaMain attributes into SASVisuals.Color, but SevoPediaIndex.py kept reading self.top.COLOR_HIGHLIGHT_TEXT.
# Python only fails when that line runs, here on Down in the Index after a search, so no compile check or load caught it until a SASPilot UI demo did on 2026-11-13. See KI#1086.
# Names count as defined when SevoPediaMain.py assigns self.X, defines def X or a class attribute X, or a page assigns self.top.X; an audit then found no read of a BtS CvPediaScreen member, so that base class, which CI cannot see, needs no exception list. (Claude code Opus 5.5) -->
import argparse
import io
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SEVOPEDIA = Path("Assets/Python/Contrib/Sevopedia")
MAIN = "SevoPediaMain.py"
LINE_STARTS = (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)


def code_tokens(text: str) -> list[tokenize.TokenInfo]:
	# <!-- custom: The first draft cut comments by hand and matched regexes on the rest, so a string holding "self.top.X" counted as a read, and an escaped quote could make a trailing comment count too (Codex's review).
	# Python 3's tokenizer reads Civ4's Python 2 files well enough to tell code from strings and comments, even where its parser cannot compile them; a file it cannot read fails the check rather than passing unread. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	return [token for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type not in (tokenize.COMMENT, tokenize.NL)]


def attribute_uses(tokens: list[tokenize.TokenInfo], chain: tuple[str, ...]) -> list[tuple[int, str, bool]]:
	# <!-- custom: (line, X, assigned) for each chain + "." + X, e.g. self.top.X; "assigned" when a plain "=" follows, not "==". (Claude code Opus 5.5) -->
	found = []
	size = 2 * len(chain)
	for i in range(len(tokens) - size):
		window = tokens[i:i + size + 1]
		names = [token.string for token in window[0:size:2]]
		dots = [token.string for token in window[1:size:2]]
		if names != list(chain) or dots != ["."] * len(chain) or window[size].type != tokenize.NAME:
			continue
		if i > 0 and tokens[i - 1].string == ".":
			continue
		following = tokens[i + size + 1].string if i + size + 1 < len(tokens) else ""
		found.append((window[size].start[0], window[size].string, following == "="))
	return found


def main_definitions(tokens: list[tokenize.TokenInfo]) -> set[str]:
	defined = {name for _line, name, assigned in attribute_uses(tokens, ("self",)) if assigned}
	for i, token in enumerate(tokens[:-1]):
		if token.string == "def" and tokens[i + 1].type == tokenize.NAME:
			defined.add(tokens[i + 1].string)
		# <!-- custom: A class attribute: a name at the class body's indentation, first on its logical line, followed by "=". (Claude code Opus 5.5) -->
		elif token.type == tokenize.NAME and token.start[1] == 1 and (i == 0 or tokens[i - 1].type in LINE_STARTS) and tokens[i + 1].string == "=":
			defined.add(token.string)
	return defined


def check(texts: dict[str, str]) -> list[str]:
	tokens = {name: code_tokens(text) for name, text in texts.items()}
	defined = main_definitions(tokens[MAIN])
	reads = []
	for name in sorted(tokens):
		for line, attribute, assigned in attribute_uses(tokens[name], ("self", "top")):
			if assigned:
				defined.add(attribute)
			else:
				reads.append((name, line, attribute))
	return ["%s:%d: self.top.%s is not defined by %s or assigned by any page" % (name, line, attribute, MAIN) for name, line, attribute in reads if attribute not in defined]


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that every self.top.X a Sevopedia page reads is defined on SevoPediaMain.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	folder = args.repo_root / SEVOPEDIA
	texts = {path.name: path.read_bytes().decode("utf-8", errors="replace") for path in folder.glob("*.py")}
	if MAIN not in texts:
		print("FAIL Sevopedia self.top attributes")
		print("  - %s not found" % (SEVOPEDIA / MAIN).as_posix())
		return 1
	failures = check(texts)
	if failures:
		print("FAIL Sevopedia self.top attributes")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS Sevopedia self.top attributes (%d pages)" % len(texts))
	return 0


if __name__ == "__main__":
	sys.exit(main())

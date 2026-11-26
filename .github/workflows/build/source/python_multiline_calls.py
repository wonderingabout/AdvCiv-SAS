#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python writes a call on one line, not one argument per line.
# <!-- custom: One line per call greps, compares and lints better (AGENTS.md); hand sweeps had no guard, so the KI#1104 copies brought 18 back and 7 SAS calls such as a, b = f( slipped past collapse_multiline_calls.py.
# Tables, conditions, multi-line strings and calls with a comment inside, such as AdvCiv's # <advc.092> markers, stay multi-line; --fix collapses what this flags. See KI#21.7. (Claude code Opus 5.5) -->

# <!-- custom: pathlib walks the folders, argparse reads the options, io feeds each file to tokenize. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import io
# <!-- custom: keyword tells names from keywords, re finds commented-out calls and splits lines, sys reports the result, tokenize splits each file into statements. (Claude code Opus 5.5) -->
import keyword
import re
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root


SCAN_RELATIVE_DIRS = (Path("Assets/Python"), Path("PrivateMaps"))
ASSIGNMENT_OPS = {"=", "+=", "-=", "*=", "/=", "%=", "|=", "&=", "^=", "<<=", ">>=", "**=", "//="}
OPENERS = {"(": ")", "[": "]", "{": "}"}
# <!-- custom: AdvCiv's tags such as "advc.092", "<advc.092>" or "advc.002b:", and SAS's custom notes. (Claude code Opus 5.5) -->
PROVENANCE_MARKER = re.compile(r"\badvc\.\w|<!-- custom:")
LINE_DIRECTIVE = re.compile(r"#\s*(noqa|type:|pylint:|pyright:|fmt:|ruff:|pragma)", re.IGNORECASE)


def source_lines(text, keepends=False):
	# <!-- custom: Splits on "\n" only: str.splitlines() also breaks on characters such as U+0085, which a Windows-1252 ellipsis byte becomes when a legacy file is read as Latin-1, and the line numbers would then drift from tokenize's (found by Codex, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	lines = [line for line in re.split(r"(?<=\n)", text) if line]
	if keepends:
		return lines
	return [line.rstrip("\r\n") for line in lines]


def logical_statements(text):
	statement = []
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		if token.type in (tokenize.ENDMARKER,):
			continue
		if not statement and token.type in (tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT):
			continue
		statement.append(token)
		if token.type == tokenize.NEWLINE:
			yield statement
			statement = []


def is_call_like(code):
	# <!-- custom: code: the statement's tokens without NL/NEWLINE. A call is NAME(.NAME)* "(" at the start, after "return"/"yield", or after an assignment such as "x =", "x +=" or "a, b =". (Claude code Opus 5.5) -->
	opener = next((i for i, token in enumerate(code) if token.string == "("), None)
	if opener is None or opener == 0 or code[opener - 1].type != tokenize.NAME or keyword.iskeyword(code[opener - 1].string):
		return False, None
	i = opener - 1
	while i >= 2 and code[i - 1].string == "." and code[i - 2].type == tokenize.NAME:
		i -= 2
	prefix = code[:i]
	if not prefix:
		return True, opener
	if len(prefix) == 1 and prefix[0].string in ("return", "yield"):
		return True, opener
	if prefix[-1].string in ASSIGNMENT_OPS and all(token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING) or token.string in (".", ",", "[", "]") for token in prefix[:-1]):
		return True, opener
	return False, None


def closer_line(code, opener):
	depth = 0
	for token in code[opener:]:
		if token.string in OPENERS:
			depth += 1
		elif token.string in (")", "]", "}"):
			depth -= 1
			if depth == 0:
				return token.start[0]
	return code[-1].start[0]


def has_multiline_table(code, opener):
	# <!-- custom: A literal that spans lines is a table when it is a dict, or a list or tuple whose elements start with another literal (rows); a tuple of calls or names, such as getText's argument tuple, is not. (Claude code Opus 5.5) -->
	stack = []
	for i in range(opener + 1, len(code)):
		token = code[i]
		if token.string in OPENERS:
			previous = code[i - 1]
			is_literal = token.string == "{" or not (previous.type == tokenize.NAME and not keyword.iskeyword(previous.string) or previous.string in (")", "]"))
			if stack and stack[-1]["literal"] and previous.string in (",", "(", "[") and is_literal:
				stack[-1]["rows"] = True
			stack.append({"char": token.string, "line": token.start[0], "literal": is_literal, "rows": False})
		elif token.string in (")", "]", "}") and stack:
			entry = stack.pop()
			if entry["literal"] and token.start[0] != entry["line"] and (entry["char"] == "{" or entry["rows"]):
				return True
	return False


def flagged_ranges(text):
	lines = source_lines(text)
	ranges = []
	for statement in logical_statements(text):
		start, end = statement[0].start[0], statement[-1].start[0]
		if end <= start:
			continue
		# <!-- custom: A comment inside keeps the statement multi-line only when it is a provenance marker, such as AdvCiv's "# <advc.092>" around the arguments it changed, or a SAS custom note; other comments move above the collapsed line, as the movie screens' "#self.EXIT_TEXT," did (2026-11-22). See KI#21.7. (Claude code Opus 5.5) -->
		comments = [token.string for token in statement if token.type == tokenize.COMMENT]
		# <!-- custom: Codex's review (2026-11-22): a bare "advc" or "custom" word in prose such as "# AdvCiv compatibility" exempted a call, so only the marker syntax counts; and a line-scoped directive such as "# noqa: F821" must stay on its line, as moving it re-enabled the warning it silenced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if any(PROVENANCE_MARKER.search(comment) or LINE_DIRECTIVE.search(comment) for comment in comments):
			continue
		if any(token.type == tokenize.STRING and token.start[0] != token.end[0] for token in statement):
			continue
		if any(lines[number - 1].rstrip().endswith("\\") for number in range(start, end)):
			continue
		code = [token for token in statement if token.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT)]
		if is_wrapped_flat_literal(code):
			ranges.append((start, end))
			continue
		call_like, opener = is_call_like(code)
		# <!-- custom: The call itself must span lines: in "x = f() if (a or" + "b) else c" only the condition does (found by Codex, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if not call_like or closer_line(code, opener) == code[opener].start[0] or has_multiline_table(code, opener):
			continue
		ranges.append((start, end))
	return ranges


def is_wrapped_flat_literal(code):
	# <!-- custom: A list or tuple of plain values assigned over several lines, wrapped at an arbitrary point, as CvDebugInfoScreen.py's 14 CivInfoItems strings were over two lines (2026-11-22).
	# One item per line stays allowed, as in SASGameRecordSettings.py's key lists, which AGENTS.md counts among the uniform listings that read better that way. See KI#21.7. (Claude code Opus 5.5) -->
	equals = next((i for i, token in enumerate(code) if token.string in ASSIGNMENT_OPS), None)
	if equals is None or equals + 2 >= len(code) or code[equals + 1].string not in ("[", "(") or code[-1].string != OPENERS[code[equals + 1].string]:
		return False
	if not all(token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING) or token.string in (".", ",") for token in code[:equals]):
		return False
	inner = code[equals + 2:-1]
	# <!-- custom: Keywords are not plain values: Codex's "[a and b, c," + "d]" was flagged as a flat list (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not inner or not all((token.type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING) and (not keyword.iskeyword(token.string) or token.string in ("None", "True", "False"))) or token.string in (",", ".", "-") for token in inner):
		return False
	if code[equals + 1].start[0] == code[-1].start[0]:
		return False
	item_lines = [inner[0].start[0]] + [inner[i + 1].start[0] for i, token in enumerate(inner[:-1]) if token.string == ","]
	return len(set(item_lines)) < len(item_lines)


def significant_tokens(text, comments=True):
	skipped = (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER) + (() if comments else (tokenize.COMMENT,))
	return [(token.type, token.string) for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type not in skipped]


def comment_only_lines(text):
	# <!-- custom: Line numbers holding nothing but a comment, from tokenize, so a "#" inside a string, such as a triple-quoted text containing "#f(", is never taken for disabled code (found by Codex, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return set(token.start[0] for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type == tokenize.COMMENT and not token.line[:token.start[1]].strip())


COMMENTED_CALL_START = re.compile(r"^\s*#\s*(?:(?:return|yield)\s+|[\w.\[\], ]+?\s*(?:[-+*/%|&^]|<<|>>|\*\*|//)?=\s*)?[A-Za-z_][\w.]*\s*\(")
COMMENTED_RUN_MAX_LINES = 20
QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'")


def bracket_depth(text):
	text = QUOTED.sub("", text)
	return sum(text.count(c) for c in "([{") - sum(text.count(c) for c in ")]}")


def comment_code(line):
	return line.split("#", 1)[1].strip()


def commented_ranges(text):
	# <!-- custom: Commented-out calls count too, as searches find them like live code: CvDebugInfoScreen.py's disabled screen.addPanel( spanned 5 comment lines.
	# A run of comment lines is judged by uncommenting it and applying the same rule, so prose comments that merely contain a parenthesis are left alone. (Claude code Opus 5.5) -->
	lines = source_lines(text)
	comments = comment_only_lines(text)
	# <!-- custom: Lines inside a multi-line custom note are prose or quotes, not disabled code: SevoPediaReligion.py quotes base AdvCiv's addMultiListControlGFC call over four lines, which must stay as quoted.
	# Before calls with a comment inside were flagged, that quote's own "# numLists, ..." comment hid it (2026-11-22). (Claude code Opus 5.5) -->
	# <!-- custom: The skip ends with the note's comment block, so an unclosed note no longer hides disabled calls further down the file (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: The comments under a --fix note moved out of a call unchanged, so they are not disabled code either: Codex's "# g(" and "# 1)", moved from one call, were merged into "# g(1)" by the next pass, under a note saying they moved unchanged (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: Only as many lines as the note says moved are skipped, so a disabled call added right below them is still found (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	inside_note = False
	moved_left = 0
	previous = None
	for number in sorted(comments):
		line = lines[number - 1]
		if previous is not None and number != previous + 1:
			inside_note = False
			moved_left = 0
		previous = number
		if inside_note:
			comments.discard(number)
			inside_note = "-->" not in line
		elif moved_left:
			comments.discard(number)
			moved_left -= 1
		elif line.strip().startswith(HOIST_NOTE_START):
			comments.discard(number)
			count = HOIST_NOTE_COUNT.search(line)
			moved_left = int(count.group(1)) if count else 1
			inside_note = "-->" not in line
		elif "<!-- custom:" in line and "-->" not in line:
			inside_note = True
	ranges = []
	i = 0
	while i < len(lines):
		if i + 1 in comments and COMMENTED_CALL_START.match(lines[i]) and bracket_depth(comment_code(lines[i])) > 0:
			code = [comment_code(lines[i])]
			j = i
			while bracket_depth(" ".join(code)) > 0 and j + 2 in comments and j - i + 1 < COMMENTED_RUN_MAX_LINES:
				j += 1
				code.append(comment_code(lines[j]))
			# <!-- custom: The uncommented text must also compile, which tells a disabled call from prose such as "getCount() returns the number of trades (one per deal, ...". (Claude code Opus 5.5) -->
			# <!-- custom: A disabled call with its own inner comment, such as "# 1, # note", stays as it is: joined, the note would swallow the rest of the call, and --fix crashed on it (Codex's review, 2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			if any("#" in QUOTED.sub("", part) for part in code):
				i = j + 1
				continue
			try:
				is_call = bracket_depth(" ".join(code)) == 0 and flagged_ranges("\n".join(code) + "\n") == [(1, len(code))]
				if is_call:
					# <!-- custom: Compiled as a function body, so a disabled "return f(" compiles too. (Claude code Opus 5.5) -->
					compile("def _():\n" + "".join("\t" + part + "\n" for part in code), "<commented-out call>", "exec")
			except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
				is_call = False
			if is_call:
				ranges.append((i + 1, j + 1))
			i = j + 1
		else:
			i += 1
	return ranges


def join_parts(parts):
	body = ""
	for part in parts:
		if not body or body.endswith(("(", "[", "{")) or part.startswith((")", "]", "}", ",")):
			body += part
		else:
			body += " " + part
	return body


def line_comments(text):
	# <!-- custom: Each line's trailing comment, from tokenize: the column it starts at and its text, so --fix can cut it off the code and move it above. (Claude code Opus 5.5) -->
	return dict((token.start[0], (token.start[1], token.string)) for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type == tokenize.COMMENT)


# <!-- custom: A moved comment alone above a call looked like a stray line: the movie screens' "#self.EXIT_TEXT," read as a fragment once off its argument (the user, 2026-11-22).
# So --fix writes a credited custom note above the moved comments, saying where they came from. See KI#21.7. (Claude code Opus 5.5) -->
HOIST_NOTE_START = "# <!-- custom: Collapsed onto one line by python_multiline_calls.py --fix;"
HOIST_NOTE_COUNT = re.compile(r"the (\d+) comments below")


def hoist_note(count, credit):
	if count == 1:
		moved = "the comment below sat inside the brackets and moved above unchanged"
	else:
		moved = "the %d comments below sat inside the brackets and moved above unchanged, in order" % count
	return "%s %s. See KI#21.7. (%s) -->" % (HOIST_NOTE_START, moved, credit)


def collapse(text, ranges, commented=False, credit=None):
	# <!-- custom: Joins each range's stripped lines, with no space after an opener or before a closer or comma; the file's line ending and the first line's indentation, or its "#" prefix for a commented-out call, stay.
	# A comment inside a live statement moves, unchanged and in order, onto its own line above the collapsed one, under a note credited to the --credit model; without --credit, a call that needs one raises ValueError. (Claude code Opus 5.5) -->
	newline = "\r\n" if "\r\n" in text else "\n"
	lines = source_lines(text, keepends=True)
	comments = {} if commented else line_comments(text)
	for start, end in reversed(ranges):
		first = lines[start - 1]
		if commented:
			prefix = first[:len(first) - len(first.split("#", 1)[1].lstrip())]
			body = join_parts([comment_code(line) for line in lines[start - 1:end]])
			lines[start - 1:end] = [prefix + body + newline]
			continue
		prefix = first[:len(first) - len(first.lstrip(" \t"))]
		hoisted = []
		parts = []
		trailing = ""
		for number in range(start, end + 1):
			line = lines[number - 1].rstrip("\r\n")
			if number in comments:
				column, comment = comments[number]
				# <!-- custom: A comment after the closing bracket, on the statement's last line, stays at the end of the collapsed line, as Codex suggested (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
				if number == end:
					trailing = " " + comment
				else:
					hoisted.append(prefix + comment + newline)
				line = line[:column]
			if line.strip():
				parts.append(line.strip())
		if hoisted:
			# <!-- custom: Codex's review (2026-11-22): a blank credit wrote an empty attribution, so it is refused like a missing one, as are a line break or "-->", which would break the note. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			if not credit or not credit.strip() or "\n" in credit or "\r" in credit or "-->" in credit:
				raise ValueError("line %d: a comment inside moves above the call, under a credited note; pass --credit with your model name, such as --credit \"Claude code Opus 5.5\"" % start)
			hoisted.insert(0, prefix + hoist_note(len(hoisted), credit) + newline)
		lines[start - 1:end] = hoisted + [prefix + join_parts(parts) + trailing + newline]
	return "".join(lines)


def commented_code_tokens(text, ranges):
	return [significant_tokens("\n".join(comment_code(line) for line in source_lines(text)[start - 1:end]) + "\n") for start, end in ranges]


# <!-- custom: credit added, the --credit model passed on to collapse() for the note above moved comments. (Claude code Opus 5.5) -->
def file_errors(path, relative, fix=False, credit=None):
	raw = path.read_bytes()
	# <!-- custom: Some inherited files are Windows-1252, not UTF-8; --fix writes each file back in the encoding it was read with. (Claude code Opus 5.5) -->
	encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
	try:
		text = raw.decode(encoding)
	except UnicodeDecodeError:
		encoding = "latin-1"
		text = raw.decode(encoding)
	try:
		ranges = flagged_ranges(text)
	except (tokenize.TokenError, IndentationError) as exc:
		return ["%s: could not split into statements (%s)" % (relative, exc)]
	disabled = commented_ranges(text)
	if fix and (ranges or disabled):
		try:
			fixed = collapse(text, ranges, credit=credit)
		except ValueError as exc:
			return ["%s: %s" % (relative, exc)]
		# <!-- custom: Moving a comment changes the token order, so the code is compared without comments, and the comments as a sorted list, so none is lost or changed; the notes --fix adds are left out of that list. (Claude code Opus 5.5) -->
		def comment_list(source):
			return sorted(value[1] for value in line_comments(source).values() if not value[1].startswith(HOIST_NOTE_START))
		if significant_tokens(fixed, comments=False) != significant_tokens(text, comments=False) or comment_list(fixed) != comment_list(text):
			return ["%s: --fix would change the code, not only its layout; collapse it by hand" % relative]
		disabled = commented_ranges(fixed)
		before = commented_code_tokens(fixed, disabled)
		fixed = collapse(fixed, disabled, commented=True)
		removed = 0
		after = []
		for start, end in disabled:
			after.append(significant_tokens(comment_code(source_lines(fixed)[start - 1 - removed]) + "\n"))
			removed += end - start
		if before != after or significant_tokens(fixed, comments=False) != significant_tokens(text, comments=False):
			return ["%s: --fix would change a commented-out call, not only its layout; collapse it by hand" % relative]
		# <!-- custom: A credit with a character the file's encoding lacks, such as an em dash in a Windows-1252 file, crashed --fix (Codex's review, 2026-11-22); it is now reported for that file, which stays unchanged. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		try:
			data = fixed.encode(encoding)
		except UnicodeEncodeError as exc:
			return ["%s: --fix cannot write the file back as %s (%s); use a --credit it can hold" % (relative, encoding, exc)]
		path.write_bytes(data)
		print("FIXED %s: %d call(s), %d commented-out" % (relative, len(ranges), len(disabled)))
		return []
	errors = ["%s:%d: call or flat list spans lines %d-%d - put it on one line, any comment inside on its own line above, or run this check with --fix (AGENTS.md, Code layout and collapsing)" % (relative, start, start, end) for start, end in ranges]
	errors += ["%s:%d: commented-out call spans lines %d-%d - put it on one line, or run this check with --fix" % (relative, start, start, end) for start, end in disabled]
	return errors


# <!-- custom: credit added, passed on to file_errors(). (Claude code Opus 5.5) -->
def find_problems(repo_root, fix=False, credit=None):
	problems = []
	for relative in SCAN_RELATIVE_DIRS:
		folder = repo_root / relative
		if not folder.is_dir():
			continue
		for path in sorted(folder.rglob("*.py")):
			problems.extend(file_errors(path, path.relative_to(repo_root).as_posix(), fix, credit))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that runtime Python writes each call on one line.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	parser.add_argument("--fix", action="store_true", help="collapse the flagged calls in place; review the diff, and check that Civ4 is not running first")
	parser.add_argument("--credit", help="with --fix, the model credit for the note written above comments moved out of a call, such as \"Claude code Opus 5.5\"")
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve(), args.fix, args.credit)
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL python multi-line calls (%d)" % len(problems))
		return 1
	print("PASS python multi-line calls")
	return 0


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python aligns a table of two or more columns with tabs, and leaves one space between code tokens elsewhere.
# <!-- custom: Inspired by CvDebugInfoScreen.py's dispatch table, which vanilla Civ4 lined up with tabs, such as 'DESC':\t"Team Relations", \t\t\t'DATA':, while SAS's own Sevopedia charts used runs of spaces that drifted out of line with each rename, such as SevoPediaWorldSizeChart.py's "W/H Ratio*", a few spaces short of its column.
# That dispatch table has only one column to align, so this rule single-spaces it; the Sevopedia charts are the tab tables to follow.
# Like a formatter's check, a line fails when it differs from the layout --fix gives: a table with two or more columns to align on 4-column tab stops, as .editorconfig sets, each one tab past its widest entry, and one space everywhere else, so stray double spaces and one-column alignment such as "WORLDSIZE_ARENA:  1," become one space.
# Commented-out code follows the same layout; prose comments, the gap before a trailing comment, strings and indentation are left alone. See KI#21.8. (Claude code Opus 5.5) -->

# <!-- custom: pathlib walks the folders, argparse reads the options, io feeds each file to tokenize, ast tells commented-out code from prose that happens to parse. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import ast
import io
# <!-- custom: re splits lines, sys reports the result, tokenize finds the gaps between code tokens outside strings and comments, warnings quiets compile() on old commented-out strings. (Claude code Opus 5.5) -->
import re
import sys
import tokenize
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root


# <!-- custom: The folders the game runs Python from come from lib/runtime_python.py, one list for every runtime Python check, so a new one is added once (2026-11-27). (Claude code Opus 5.5) -->
from runtime_python import RUNTIME_PYTHON_DIRS
SCAN_RELATIVE_DIRS = tuple(Path(folder) for folder in RUNTIME_PYTHON_DIRS)
TAB_WIDTH = 4
MIN_ALIGNED_COLUMNS = 2
OPENERS = ("(", "[", "{")
CLOSERS = (")", "]", "}")
# <!-- custom: A comment-only line: its indentation, "#" and at most one space form the prefix kept as is, and the rest is the commented-out text. (Claude code Opus 5.5) -->
COMMENTED_LINE = re.compile(r"^([ \t]*# ?)(.*)$")
ASSIGNMENTS = {"=", "+=", "-=", "*=", "/=", "%=", "|=", "&=", "^=", "<<=", ">>=", "**=", "//="}
SKIPPED_TYPES = (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER, tokenize.COMMENT)


def source_lines(text):
	# <!-- custom: Splits on "\n" only, as python_multiline_calls.py does: str.splitlines() also breaks on U+0085, which a Windows-1252 ellipsis byte becomes when read as Latin-1, so line numbers would drift from tokenize's. (Claude code Opus 5.5) -->
	return [line for line in re.split(r"(?<=\n)", text) if line]


def bad_gap(gap):
	return "  " in gap or ("\t" in gap and " " in gap)


def line_gaps(text):
	# <!-- custom: For each line, every boundary between two code tokens that start and end on it, as (start, end, separator) with character offsets, even where no space sits between them; a row holding the end of a multi-line string is marked unsafe, since its first segment does not start at the line's indentation.
	# separator: where a table's columns meet, after a "," or ":" or touching an "=" or augmented assignment, as the separator and its bracket depth from the line's start, or None.
	# Codex's review (2026-11-23) paired left = foo(a, b) with right = bar[long_key: very_long], as both held two separators: a call's comma and a slice's colon. Rows now share columns only when their separators match in kind and depth. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	gaps, unsafe = {}, set()
	previous = None
	depth = 0
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		if token.type in SKIPPED_TYPES:
			if token.type == tokenize.COMMENT:
				previous = None
			continue
		if token.start[0] != token.end[0]:
			unsafe.add(token.end[0])
		if previous is None or previous.end[0] != token.start[0]:
			depth = 0
		if previous is not None and previous.end[0] == token.start[0]:
			separator = None
			if previous.string in (",", ":") or previous.string in ASSIGNMENTS:
				separator = (previous.string, depth)
			elif token.string in ASSIGNMENTS:
				separator = (token.string, depth)
			gaps.setdefault(token.start[0], []).append((previous.end[1], token.start[1], separator))
		if token.string in OPENERS:
			depth += 1
		elif token.string in CLOSERS:
			depth -= 1
		previous = token
	return gaps, unsafe


def visual_width(text, column=0):
	for char in text:
		column = (column // TAB_WIDTH + 1) * TAB_WIDTH if char == "\t" else column + 1
	return column


def alignment_gap(line, start, end):
	gap = line[start:end]
	return "\t" in gap or len(gap) >= 2


def column_gaps(line, gaps):
	# <!-- custom: The separator boundaries of a line in order, each with whether it aligns; the n-th one is the same place in every row of a table.
	# The first draft split each line at its own wide gaps only, so SevoPediaWorldSizeChart.py's "Building Class Prereq Mod", whose next column followed after one space, merged two columns and pushed every row's later columns ten tabs out.
	# The second counted every token boundary, so in CvCustomizableDomesticAdvisor.py a row holding CyCity.getCommerceRate where its neighbour held None split the name at its dot; columns now meet only at separators. (Claude code Opus 5.5) -->
	return [alignment_gap(line, start, end) for start, end, separator in gaps if separator]


def separator_kinds(gaps):
	return [separator for _start, _end, separator in gaps if separator]


def relayout(lines, rows):
	# <!-- custom: rows: one block of adjacent lines with as many separators each.
	# A column is the n-th separator wherever any row aligns there; each line splits there into segments, and column j's tab stop is the first one past the widest segment j ends at, so every row reaches it with one tab or more.
	# Other double spaces in the rows become one space. (Claude code Opus 5.5) -->
	columns_at = set()
	for row, gaps in rows:
		columns_at.update(n for n, aligned in enumerate(column_gaps(lines[row - 1], gaps)) if aligned)
	split = {}
	for row, gaps in rows:
		line = lines[row - 1].rstrip("\r\n")
		segments, current, position, n = [], "", 0, 0
		for start, end, separator in gaps:
			current += line[position:start]
			position = end
			if separator and n in columns_at:
				segments.append(current)
				current = ""
			elif bad_gap(line[start:end]):
				current += " "
			else:
				current += line[start:end]
			n += 1 if separator else 0
		segments.append(current + line[position:])
		split[row] = segments
	starts = {row: visual_width(segments[0]) for row, segments in split.items()}
	columns = max(len(segments) for segments in split.values())
	out = {row: segments[0] for row, segments in split.items()}
	aligned = 0
	for j in range(1, columns):
		having = [row for row, segments in split.items() if len(segments) > j]
		# <!-- custom: Where every row's cell before a column ends at the same place, the column lines up anyway, so one space joins it; the map scripts' option dicts, such as Ring.py's `4:  "TXT_KEY_MAP_WORLD_WRAP"` with one-digit keys, had turned into a tab that aligned nothing (the user, 2026-11-22). (Claude code Opus 5.5) -->
		if len(set(starts[row] for row in having)) == 1:
			for row in having:
				out[row] += " " + split[row][j]
				starts[row] = visual_width(split[row][j], starts[row] + 1)
			continue
		stop = (max(starts[row] for row in having) // TAB_WIDTH + 1) * TAB_WIDTH
		aligned += 1
		for row in having:
			column = starts[row]
			tabs = 0
			while column < stop:
				column = (column // TAB_WIDTH + 1) * TAB_WIDTH
				tabs += 1
			out[row] += "\t" * tabs + split[row][j]
			starts[row] = visual_width(split[row][j], stop)
	return out, aligned


def fixed_text(text, gaps, unsafe):
	return commented_code_laid_out(code_laid_out(text, gaps, unsafe))


def commented_code_laid_out(text):
	# <!-- custom: Commented-out code follows the same layout, as searches find it too: CvCustomizableDomesticAdvisor.py keeps the rows advc.004 cut from COLUMNS_LIST, such as # ("GRANK_FOOD", 38, "int", ...), as a disabled table (the user, 2026-11-23).
	# A run of comment lines with one prefix whose text compiles as Python is laid out as a file of its own and gets its prefix back; prose, such as "# advc.004: Cut from the list initializer below", does not compile and stays as written. (Claude code Opus 5.5) -->
	lines = source_lines(text)
	# <!-- custom: Codex's review (2026-11-23) found two ways a string could be taken for commented-out code and changed: a "# x =  y" line inside a live triple-quoted string, which only looks like a comment, and the same line inside a commented-out one, # text = """ to # """.
	# So a line counts only when the tokenizer sees it as a comment on a line of its own, and lines on or between commented-out triple quotes are string text, which stays as written. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	comment_rows = {token.start[0] for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type == tokenize.COMMENT and not token.line[:token.start[1]].strip()}
	in_string = False
	bodies = []
	for row, line in enumerate(lines, 1):
		match = COMMENTED_LINE.match(line.rstrip("\r\n")) if row in comment_rows else None
		quotes = len(re.findall(r"\"\"\"|'''", match.group(2))) if match else 0
		inside = in_string or quotes > 0
		in_string = (in_string != (quotes % 2 == 1)) if match else False
		code = None
		if match and not inside and match.group(2).strip():
			try:
				# <!-- custom: Old commented-out strings such as "\I" are invalid escapes in Python 3, whose compile() then warns on every run. (Claude code Opus 5.5) -->
				with warnings.catch_warnings():
					warnings.simplefilter("ignore")
					tree = ast.parse(match.group(2).strip())
				# <!-- custom: The map scripts' "#   FILE:    Wheel.py" and "#   AUTHOR:  Axius" notices, and AStarTools.py's "#   pUnit           : CyUnit" docs, parse in Python 3 as variable annotations, a syntax Python 2.4 does not have; they are prose, so they stay as written.
				# A dotted name before the colon is a commented-out dict row instead, such as Pangaea.py's "#       WorldSizeTypes.WORLDSIZE_HUGE:      (26,16)". (Claude code Opus 5.5) -->
				if not any(isinstance(node, ast.AnnAssign) and not isinstance(node.target, ast.Attribute) for node in ast.walk(tree)):
					code = match.group(1), match.group(2)
			except (SyntaxError, ValueError):
				pass
		bodies.append(code)
	replaced = {}
	row = 0
	while row < len(lines):
		if bodies[row] is None:
			row += 1
			continue
		run = [row]
		while run[-1] + 1 < len(lines) and bodies[run[-1] + 1] is not None and bodies[run[-1] + 1][0] == bodies[row][0]:
			run.append(run[-1] + 1)
		row = run[-1] + 1
		# <!-- custom: Each body is laid out at the column it really starts at, after its prefix: laid out from column 0, the GRANK rows, which start at column 18 after "\t\t\t\t# ", came out on the wrong tab stops and lost their columns. (Claude code Opus 5.5) -->
		offset = " " * visual_width(bodies[run[0]][0])
		block = "".join(offset + bodies[r][1] + "\n" for r in run)
		try:
			block_gaps, block_unsafe = line_gaps(block)
			laid_out = code_laid_out(block, block_gaps, block_unsafe)
		except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
			continue
		for r, body in zip(run, source_lines(laid_out)):
			ending = lines[r][len(lines[r].rstrip("\r\n")):]
			replaced[r] = bodies[r][0] + body.rstrip("\n")[len(offset):] + ending
	return "".join(replaced.get(row, line) for row, line in enumerate(lines))


def code_laid_out(text, gaps, unsafe):
	lines = source_lines(text)
	flagged = {row for row, row_gaps in gaps.items() for start, end, _ in row_gaps if bad_gap(lines[row - 1][start:end])}
	if flagged & unsafe:
		raise ValueError("line %d ends a multi-line string and has a gap to fix; fix it by hand" % min(flagged & unsafe))
	# <!-- custom: Lines already aligned with tabs are laid out too, so every table in the repository has the same layout: Tectonics.py's xMoves and yMoves rows, two tabs after each "=", were tab-only, so the first sweep skipped them, though their tabs align nothing (the user, 2026-11-22). (Claude code Opus 5.5) -->
	tabbed = {row for row, row_gaps in gaps.items() for start, end, _ in row_gaps if "\t" in lines[row - 1][start:end]} - unsafe

	replaced = {}
	in_table = set()
	for block in tables(lines, gaps, unsafe):
		laid_out, aligned = relayout(lines, [(r, gaps.get(r, [])) for r in block])
		# <!-- custom: Only a table with two or more columns to align keeps tabs, such as the Sevopedia charts or CvCustomizableDomesticAdvisor.py's COLUMNS_LIST: a key-to-value map such as SAS_WorldSizeUtils.py's WorldSizeTypes.WORLDSIZE_ARENA: 1, or an enum or assignment list, gains little from one aligned column, so its rows get one space (the user, 2026-11-23). (Claude code Opus 5.5) -->
		if aligned < MIN_ALIGNED_COLUMNS:
			continue
		in_table.update(block)
		for block_row, content in laid_out.items():
			ending = lines[block_row - 1][len(lines[block_row - 1].rstrip("\r\n")):]
			replaced[block_row] = content + ending
	for row in sorted((flagged | tabbed) - in_table):
		# <!-- custom: A line in no table aligns with nothing, so its double spaces or tabs, such as "x =  y" or GameFontDisplay.py's "%  (iID)", become one space. (Claude code Opus 5.5) -->
		line = lines[row - 1]
		for start, end, _ in reversed(gaps[row]):
			if bad_gap(line[start:end]) or "\t" in line[start:end]:
				line = line[:start] + " " + line[end:]
		replaced[row] = line
	# <!-- custom: A line whose layout changes also drops its trailing spaces and tabs, as git diff --check flagged inherited ones on lines the sweep touched (Codex's review, 2026-11-23); a line opening a multi-line string keeps them, as they belong to the string. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	opens = multiline_starts(text)
	for row, line in list(replaced.items()):
		if line != lines[row - 1] and row not in opens:
			body = line.rstrip("\r\n")
			replaced[row] = body.rstrip(" \t") + line[len(body):]
	return "".join(replaced.get(row, line) for row, line in enumerate(lines, 1))


def multiline_starts(text):
	return {token.start[0] for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.start[0] != token.end[0]}


def tables(lines, gaps, unsafe):
	# <!-- custom: Every table of a file is found up front, from its structure: the first version grew each table from whichever flagged line it met first, judging a neighbour by its current alignment, so after a pass laid a table out its neighbours joined differently, and passes over SevoPediaMain.py's widget IDs flipped between two layouts. (Claude code Opus 5.5) -->
	def columns(row):
		return column_gaps(lines[row - 1], gaps.get(row, ()))

	def indent(row):
		line = lines[row - 1]
		return line[:len(line) - len(line.lstrip(" \t"))]

	def comment_only(row):
		return lines[row - 1].lstrip(" \t").startswith("#")

	# <!-- custom: A run is adjacent lines at the same indentation whose separators match in kind and depth: SevoPediaMain.py's HEAD_TEXT and BACK_TEXT lines sit together but are different calls.
	# A run continues through comment-only lines: CvCustomizableDomesticAdvisor.py's COLUMNS_LIST holds an "# advc.004:" note between rows, and stopping there laid its two halves out on different tab stops. (Claude code Opus 5.5) -->
	runs, current = [], []
	for row in range(1, len(lines) + 1):
		if current and comment_only(row):
			continue
		if row not in unsafe and columns(row) and current and indent(row) == indent(current[0]) and separator_kinds(gaps.get(row, ())) == separator_kinds(gaps.get(current[0], ())):
			current.append(row)
			continue
		if len(current) > 1:
			runs.append(current)
		current = [row] if row not in unsafe and columns(row) else []
	if len(current) > 1:
		runs.append(current)
	# <!-- custom: A table's widest row often has one space before its next column, so it shows no alignment of its own and stays in its run; two such rows in a row end a table, so plain statements beside it stay out.
	# A table needs two rows that align; otherwise its double spaces, such as "x =  y" next to "z = 1", are slips rather than columns.
	# Laid out, every row of a table aligns, so the next pass finds the same tables. (Claude code Opus 5.5) -->
	found = []
	for run in runs:
		segment, plain = [], []
		for row in run + [None]:
			if row is not None and not any(columns(row)):
				plain.append(row)
				continue
			if row is None or len(plain) > 1:
				if len(plain) == 1 and row is None:
					segment.extend(plain)
				if sum(1 for r in segment if any(columns(r))) > 1:
					found.append(segment)
				segment = []
			else:
				segment.extend(plain)
			plain = []
			if row is not None:
				segment.append(row)
	return found


def code_tokens(text):
	# <!-- custom: A comment is compared with its whitespace normalized, as laying out commented-out code changes only its spacing. (Claude code Opus 5.5) -->
	return [" ".join(token.string.split()) if token.type == tokenize.COMMENT else token.string for token in tokenize.generate_tokens(io.StringIO(text).readline) if token.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER)]


def file_errors(path, relative, fix=False):
	raw = path.read_bytes()
	# <!-- custom: Some inherited files are Windows-1252, not UTF-8; --fix writes each file back in the encoding it was read with. (Claude code Opus 5.5) -->
	encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
	try:
		text = raw.decode(encoding)
	except UnicodeDecodeError:
		encoding = "latin-1"
		text = raw.decode(encoding)
	try:
		gaps, unsafe = line_gaps(text)
	except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
		return ["%s: could not split into tokens (%s)" % (relative, exc)]
	# <!-- custom: Like a formatter's check, a line fails when it differs from the layout --fix gives, so a table already aligned with tabs fails too when its stops are not the ones --fix would choose. (Claude code Opus 5.5) -->
	try:
		fixed = fixed_text(text, gaps, unsafe)
	except ValueError as exc:
		return ["%s: %s" % (relative, exc)]
	differing = [row for row, (old, new) in enumerate(zip(source_lines(text), source_lines(fixed)), 1) if old != new]
	if not differing:
		return []
	if fix:
		# <!-- custom: Only whitespace between tokens may change, so the token sequence, comments included, must stay identical. (Claude code Opus 5.5) -->
		if code_tokens(fixed) != code_tokens(text):
			return ["%s: --fix would change the code, not only its layout; fix it by hand" % relative]
		path.write_bytes(fixed.encode(encoding))
		print("FIXED %s: %d line(s)" % (relative, len(differing)))
		return []
	return ["%s:%d: gaps between code tokens differ from the layout --fix gives - align a table's columns with tabs only, one tab past its widest entry, and use one space elsewhere, or run this check with --fix (AGENTS.md, Code layout and collapsing)" % (relative, row) for row in differing]


def find_problems(repo_root, fix=False):
	problems = []
	for relative in SCAN_RELATIVE_DIRS:
		folder = repo_root / relative
		if not folder.is_dir():
			continue
		for path in sorted(folder.rglob("*.py")):
			problems.extend(file_errors(path, path.relative_to(repo_root).as_posix(), fix))
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that runtime Python aligns columns with tabs and leaves one space between code tokens elsewhere.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	parser.add_argument("--fix", action="store_true", help="lay tables out on tab stops and collapse lone double spaces in place; review the diff, and check that Civ4 is not running first")
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve(), args.fix)
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL python aligned columns (%d)" % len(problems))
		return 1
	print("PASS python aligned columns")
	return 0


if __name__ == "__main__":
	sys.exit(main())

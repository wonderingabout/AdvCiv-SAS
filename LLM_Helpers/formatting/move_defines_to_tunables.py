#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Moves SAS defines that only Python reads from GlobalDefines_advciv_sas.xml into Assets/Python/SASSessionTunables.py, and switches their Python reads to the module.
# Written for the move of 2026-11-27, which grew from a 23-define pilot run by two one-off scratch scripts into about 110 defines; kept here so a later family moves the same way rather than by a new script.
# Dry run by default: it prints what it would move, every read it would switch and every mention it cannot switch, such as a name built at runtime ("SAS_X_%d" % i) or one in an error message, which need a hand check; --apply writes.
# It does not decide which defines may move: give it names the readers audit (audit_define_timing.py --readers) lists as read by Python only, minus those SASLiveDefineOverrides.txt may change and those our tooling or CI reads from the XML. (Claude code Opus 5.5) -->

# <!-- custom: pathlib locates the files, argparse takes the names and comments, and ast and html check and decode values. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import ast
import html
# <!-- custom: re matches the reads, sys finds the shared runtime folder list and prints UTF-8, and io and tokenize find the strings and comments a read must not be rewritten in. (Claude code Opus 5.5) -->
import io
import re
import sys
import tokenize

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".github" / "workflows" / "lib"))
from runtime_python import RUNTIME_PYTHON_DIRS

XML_PATH = REPO / "Assets" / "XML" / "GlobalDefines_advciv_sas.xml"
TUNABLES_PATH = REPO / "Assets" / "Python" / "SASSessionTunables.py"
MODULE = "SASSessionTunables"
# <!-- custom: The read forms SAS's runtime Python uses for a define by name; anything else naming a moved define is reported, not rewritten.
# The lookbehind keeps an attribute of another object, such as other.gc.getDefineINT, from matching, which the first version rewrote into other.SASSessionTunables, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
READ_PATTERN = r'(?<![\w.])(?:self\.gc|gc|CyGlobalContext\(\)|SASCurrentDefines)\.get(?:Define)?(?:INT|Int|String)\("%s"\)'
VALUE_PATTERN = re.compile(r"<(iDefineIntVal|DefineTextVal)>(.*?)</\1>$")


def text_spans(text):
	# <!-- custom: The character spans of the file's strings and comments, from Python's own tokenizer, so a lookup inside one, a triple-quoted string spanning lines included, is reported rather than rewritten.
	# The first version scanned each line for quotes and #, which missed multiline strings, as Codex's review (GPT-6.2-Sol) reproduced; a file the tokenizer cannot read raises instead of being guessed at. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	starts = [0]
	for line in text.split("\n"):
		starts.append(starts[-1] + len(line) + 1)
	spans = []
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		if token.type in (tokenize.STRING, tokenize.COMMENT):
			spans.append((starts[token.start[0] - 1] + token.start[1], starts[token.end[0] - 1] + token.end[1]))
	return spans


def in_spans(offset, spans):
	return any(start <= offset < end for start, end in spans)


def read_names(path):
	names = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
	if len(set(names)) != len(names):
		raise SystemExit("duplicate names in %s" % path)
	return names


def collect_blocks(lines, names):
	# <!-- custom: A block is the <Define> and the comment directly above it; a comment separated from it by a blank line stays, as it may head a group. (Claude code Opus 5.5) -->
	blocks = []
	for name in names:
		index = [i for i, line in enumerate(lines) if line.strip() == "<DefineName>%s</DefineName>" % name]
		if len(index) != 1:
			raise SystemExit("%s: found %d times in the XML" % (name, len(index)))
		i = index[0]
		if lines[i - 1].strip() != "<Define>" or lines[i + 2].strip() != "</Define>":
			raise SystemExit("%s: not a three-line <Define> block" % name)
		match = VALUE_PATTERN.match(lines[i + 1].strip())
		if not match:
			raise SystemExit("%s: unexpected value line %r" % (name, lines[i + 1].strip()))
		if match.group(1) == "iDefineIntVal":
			value = "%d" % int(match.group(2))
		else:
			# <!-- custom: Decoded, so an XML entity such as &amp; becomes the character Python should hold, which the first version copied as is (Codex's review, GPT-6.2-Sol). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			value = repr(html.unescape(match.group(2)))
		start = i - 1
		comment = []
		j = start - 1
		if lines[j].rstrip().endswith("-->"):
			while True:
				comment.insert(0, lines[j])
				if "<!--" in lines[j]:
					break
				j -= 1
			start = j
		blocks.append({"start": start, "end": i + 2, "name": name, "value": value, "comment": comment})
	blocks.sort(key=lambda block: block["start"])
	return blocks


def python_text(blocks, lines):
	out = []
	previous_end = None
	for block in blocks:
		if previous_end is not None:
			between = lines[previous_end + 1:block["start"]]
			# <!-- custom: Defines adjacent in the XML stay one blank line apart; anything else between them, another define or a group gap, becomes two, so the XML's groups still show. (Claude code Opus 5.5) -->
			if any(line.strip() for line in between) or len(between) > 1:
				out.append("")
		for line in block["comment"]:
			out.append("# " + line.strip())
		out.append("%s = %s" % (block["name"], block["value"]))
		out.append("")
		previous_end = block["end"]
	return "\n".join(out)


def runtime_python_files():
	for folder in RUNTIME_PYTHON_DIRS:
		for path in sorted((REPO / folder).rglob("*.py")):
			yield path


# <!-- custom: Computes every rewritten file in memory and writes nothing, so main can check the whole run before writing; the first version wrote each file as it went, so a later failure, such as a missing SASSessionTunables.py, left callers rewritten and the XML cut, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def switch_reads(names, import_comment):
	switched = 0
	leftovers = []
	changed = []
	for path in runtime_python_files():
		if path == TUNABLES_PATH:
			continue
		text = path.read_bytes().decode("utf-8")
		newline = "\r\n" if "\r\n" in text else "\n"
		count = 0
		for name in names:
			if name not in text:
				continue
			spans = text_spans(text)
			pieces = []
			last = 0
			for found in re.finditer(READ_PATTERN % name, text):
				if in_spans(found.start(), spans):
					continue
				pieces.append(text[last:found.start()])
				pieces.append("%s.%s" % (MODULE, name))
				last = found.end()
				count += 1
			pieces.append(text[last:])
			text = "".join(pieces)
		for name in names:
			for number, line in enumerate(text.split("\n"), 1):
				if re.search(r"\b%s\b" % name, line) and "%s.%s" % (MODULE, name) not in line:
					leftovers.append("%s:%d: %s" % (path.relative_to(REPO), number, line.strip()[:160]))
		if not count:
			continue
		switched += count
		if not re.search(r"^import %s\b" % MODULE, text, re.M):
			lines = text.split(newline)
			last_import = max(i for i, line in enumerate(lines) if re.match(r"(import|from)\s+\w", line))
			lines[last_import + 1:last_import + 1] = [import_comment, "import " + MODULE]
			text = newline.join(lines)
		print("%s: %d read(s)" % (path.relative_to(REPO), count))
		changed.append((path, text))
	return switched, leftovers, changed


def main(argv):
	parser = argparse.ArgumentParser(description="Move Python-only SAS defines from GlobalDefines_advciv_sas.xml into SASSessionTunables.py and switch their reads.")
	parser.add_argument("names", help="file listing one define name per line")
	parser.add_argument("--heading", required=True, help="comment line written above the moved block, saying what moved and when")
	parser.add_argument("--import-comment", required=True, help="comment line written above each added import")
	parser.add_argument("--apply", action="store_true", help="write the files; without it, only report")
	args = parser.parse_args(argv)
	# <!-- custom: Windows consoles default to cp1252, which cannot print a comment holding a character such as an emoji; the second run stopped on one, so print UTF-8. (Claude code Opus 5.5) -->
	sys.stdout.reconfigure(encoding="utf-8")
	sys.stderr.reconfigure(encoding="utf-8")

	names = read_names(args.names)
	if not TUNABLES_PATH.is_file():
		raise SystemExit("missing %s; create it first, with its header" % TUNABLES_PATH.relative_to(REPO))
	xml = XML_PATH.read_bytes().decode("utf-8")
	if "\r\n" in xml:
		raise SystemExit("the XML has CRLF line endings; expected LF as stored")
	lines = xml.split("\n")
	blocks = collect_blocks(lines, names)
	body = python_text(blocks, lines)
	# <!-- custom: Checked before anything is written: each value must read back as a plain literal and each name appear once as an assignment, so a bad value stops the run instead of reaching the game (Codex's review, GPT-6.2-Sol). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for block in blocks:
		ast.literal_eval(block["value"])
		if len(re.findall(r"^%s = " % block["name"], body, re.M)) != 1:
			raise SystemExit("%s: not exactly one assignment in the generated text" % block["name"])
	compile(body, "SASSessionTunables (generated)", "exec")
	print(body)
	switched, leftovers, changed = switch_reads(names, args.import_comment)
	print("%d define(s), %d read(s) switched" % (len(blocks), switched), file=sys.stderr)
	if leftovers:
		print("mentions left for a hand check:", file=sys.stderr)
		for line in leftovers:
			print("  " + line, file=sys.stderr)
	if args.apply:
		# <!-- custom: Everything is computed and checked above; only now is anything written. (Claude code Opus 5.5) -->
		for path, text in changed:
			path.write_bytes(text.encode("utf-8"))
		remove = set()
		for block in blocks:
			remove.update(range(block["start"], block["end"] + 1))
		kept = "\n".join(line for k, line in enumerate(lines) if k not in remove)
		# <!-- custom: Removing a group whole leaves its separators behind; four or more blank lines collapse into the XML's three-line group gap. (Claude code Opus 5.5) -->
		kept = re.sub(r"\n{5,}", "\n\n\n\n", kept)
		XML_PATH.write_bytes(kept.encode("utf-8"))
		tunables = TUNABLES_PATH.read_bytes().decode("utf-8").rstrip("\n")
		TUNABLES_PATH.write_bytes((tunables + "\n\n\n" + args.heading + "\n" + body).encode("utf-8"))
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))

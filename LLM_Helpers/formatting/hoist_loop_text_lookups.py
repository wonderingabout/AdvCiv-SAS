#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Reads each fixed-key text lookup that python_text_lookups_cached.py finds inside a loop, getText("TXT_KEY_X", ()), once before the outermost loop of its function, as szTextX, and uses that local in the loop.
# Written on 2026-11-27 for the check's first repo-wide run, which found 93 such lookups in 20 files; hoisting each by hand risked a slip in one of them. See KI#128.10.
# Usage from the mod root: python LLM_Helpers/formatting/hoist_loop_text_lookups.py [--dry-run] [FILE ...]; with no file, every file the check reports.
# Review the diff after use: the lookup moves out of any branch it sat in, which only reads the text once even when that branch never runs, and the local's name is checked against the function's other names. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, pathlib finds the files, re finds each lookup on its line and sys loads the check, whose loop_lookups decides what is in a loop. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".github" / "workflows" / "build" / "source"))
sys.path.insert(0, str(ROOT / ".github" / "workflows" / "lib"))
# <!-- custom: The check itself finds the lookups, so the fixer and the check cannot disagree about which ones sit in a loop. (Claude code Opus 5.5) -->
import python_text_lookups_cached as check

COMMENT = "# <!-- custom: Fixed texts read once before the loop rather than at each pass, which cost about 0.8 microseconds a lookup. See KI#128.10. (Claude code Opus 5.5) -->"
LOOP = re.compile(r"^\s*(for|while)\b")
SCOPE = re.compile(r"^\s*(def|class)\b")


def indent_width(line):
	return len(line.expandtabs(4)) - len(line.expandtabs(4).lstrip())


def local_name(key):
	return "szText" + "".join(part.capitalize() for part in key[len("TXT_KEY_"):].split("_"))


def outermost_loop(lines, number):
	# <!-- custom: The line index of the outermost for or while enclosing line number within its def, found by walking up through lines of lower indent; a one-line loop is its own line. (Claude code Opus 5.5) -->
	level = indent_width(lines[number])
	found = number if LOOP.match(lines[number]) else None
	for previous in range(number - 1, -1, -1):
		text = lines[previous]
		if not text.strip() or text.lstrip().startswith("#"):
			continue
		width = indent_width(text)
		if width < level:
			level = width
			if SCOPE.match(text):
				break
			if LOOP.match(text):
				found = previous
	return found


def hoist(path, dry_run):
	data = path.read_bytes().decode("utf-8") if b"\r\n" not in path.read_bytes() else None
	if data is None:
		raise SystemExit("%s has CRLF line endings; this helper writes LF only" % path)
	lines = data.split("\n")
	findings = check.loop_lookups(data)
	inserts = {}
	problems = []
	# <!-- custom: Only a receiver the file binds once at module level, such as localText = CyTranslator(), is safe to read before the loop: Codex's review (GPT-6.2-Sol) ran the first draft on for localText in translators:, and it read localText before the loop bound it. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	stable = set(re.findall(r"^([A-Za-z_]\w*)\s*=\s*CyTranslator\(\)\s*$", data, re.MULTILINE))
	# <!-- custom: Each local name belongs to one key, as TXT_KEY_A_B and TXT_KEY_A__B both make szTextAB, and the first draft let the second overwrite the first, as Codex's review reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	owners = {}
	for line_number, key in findings:
		index = line_number - 1
		pattern = re.compile(r"((?:[A-Za-z_]\w*(?:\(\))?\.)*)getText\(\s*(u?)\"" + re.escape(key) + r"\"\s*,\s*\(\s*\)\s*\)")
		match = pattern.search(lines[index])
		# <!-- custom: A line holding the same key twice, as CvInfoScreen's two "unknown" columns do, has both replaced at its first finding, so its second finding has nothing left to do; the first draft reported it as spanning lines. (Claude code Opus 5.5) -->
		if match is None and re.search(r"\b" + local_name(key) + r"\b", lines[index]):
			continue
		if match is None:
			problems.append("%s:%d: %s spans lines; hoist it by hand" % (path, line_number, key))
			continue
		loop = outermost_loop(lines, index)
		if loop is None:
			problems.append("%s:%d: %s: no loop found above it; hoist it by hand" % (path, line_number, key))
			continue
		receiver = match.group(1).rstrip(".")
		if receiver not in stable:
			problems.append("%s:%d: %s is read through %s, which the file does not bind once at module level as a CyTranslator(); hoist it by hand" % (path, line_number, key, receiver or "a bare name"))
			continue
		name = local_name(key)
		if owners.setdefault(name, key) != key:
			problems.append("%s:%d: %s and %s would both be %s; hoist it by hand" % (path, line_number, owners[name], key, name))
			continue
		if re.search(r"\b" + name + r"\b", data):
			problems.append("%s:%d: %s already exists in the file; hoist it by hand" % (path, line_number, name))
			continue
		entries = inserts.setdefault(loop, {})
		entries.setdefault(key, (name, match.group(0)))
		lines[index] = pattern.sub(name, lines[index])
	for loop in sorted(inserts, reverse=True):
		indent = lines[loop][:len(lines[loop]) - len(lines[loop].lstrip())]
		block = [indent + COMMENT] + [indent + "%s = %s" % (name, expression) for (name, expression) in inserts[loop].values()]
		lines[loop:loop] = block
	if not dry_run and inserts:
		path.write_bytes("\n".join(lines).encode("utf-8"))
	return sum(len(entries) for entries in inserts.values()), problems


def main(argv=None):
	parser = argparse.ArgumentParser(description="Read fixed-key text lookups once before their loop.")
	parser.add_argument("files", nargs="*", type=Path)
	parser.add_argument("--dry-run", action="store_true")
	args = parser.parse_args(argv)
	files = args.files or sorted({path for path, rel in check.python_files(ROOT) if check.loop_lookups(check.read_text(path))})
	all_problems = []
	for path in files:
		count, problems = hoist(path if path.is_absolute() else ROOT / path, args.dry_run)
		all_problems.extend(problems)
		print("%s: %d local(s) %s" % (path, count, "would be added" if args.dry_run else "added"))
	for problem in all_problems:
		print("  - " + problem)
	return bool(all_problems)


if __name__ == "__main__":
	sys.exit(main())

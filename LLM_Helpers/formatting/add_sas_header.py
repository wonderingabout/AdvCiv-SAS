#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# External helper: add the SAS modification header, and optionally a custom note, to inherited Python files after their own notices.
# <!-- custom: A sweep that changes inherited files, such as KI#21.8's spacing pass, makes source_change_provenance.py ask each changed Python or XML file for the SAS header; twelve files needed it, and a scratch script inserting it after the leading notices first doubled their closing "#" line (2026-11-23).
# The header goes after the file's leading comment block, so inherited notices keep their order; --note adds a credited custom note saying what changed and why, as a bare header would leave the change unexplained. See KI#21.8. (Claude code Opus 5.5) -->

# <!-- custom: pathlib reads the files, argparse the options, re the provenance findings, subprocess runs the provenance check, sys the exit status. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
HEADER = [
	"#",
	"# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)",
	"# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)",
]
MARKER = "wonderingabout"
PROVENANCE = Path(".github/workflows/build/source/source_change_provenance.py")
MISSING_HEADER = re.compile(r"^\s*- (\S+\.py):\d+: changed Python/XML file lacks the SAS modification copyright header")


def read(path):
	# <!-- custom: A UTF-8 BOM is kept through utf-8-sig; the first version read it as part of the first line, which then did not start with "#" (Codex's review, 2026-11-23). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	raw = path.read_bytes()
	encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
	try:
		return raw.decode(encoding), encoding
	except UnicodeDecodeError:
		return raw.decode("latin-1"), "latin-1"


def with_header(text, note):
	# <!-- custom: The header's lines take the file's own line ending; the first version wrote LF lines into CRLF files (Codex's review, 2026-11-23). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	ending = "\r" if text.count("\r\n") * 2 > text.count("\n") else ""
	lines = text.split("\n")
	end = 0
	while end < len(lines) and lines[end].startswith("#"):
		end += 1
	if end == 0:
		raise ValueError("no leading comment block of inherited notices; add the header by hand")
	header = list(HEADER)
	# <!-- custom: A notice block that already ends with a bare "#" or "##" line gets no second one, as the first version gave Fractal.py, Pangaea.py and MonkeyTools.py. (Claude code Opus 5.5) -->
	if lines[end - 1].rstrip() in ("#", "##"):
		header = header[1:]
	if note:
		header += ["#", "# " + note]
	return "\n".join(lines[:end] + [line + ending for line in header] + lines[end:])


def provenance_files(base_ref):
	command = [sys.executable, str(PROVENANCE)] + (["--base-ref", base_ref] if base_ref else [])
	output = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True).stdout
	return sorted({match.group(1).replace("\\", "/") for match in map(MISSING_HEADER.match, output.splitlines()) if match})


def main():
	parser = argparse.ArgumentParser(description="Add the SAS modification header, and optionally a custom note, after an inherited Python file's own notices.")
	parser.add_argument("files", nargs="*", type=Path, help="Python files, relative to the repository root")
	parser.add_argument("--from-provenance", action="store_true", help="take the files that source_change_provenance.py reports as lacking the header")
	parser.add_argument("--base-ref", help="with --from-provenance, the base the provenance check compares with, such as HEAD")
	parser.add_argument("--note", help="the custom note's text, such as \"Layout only: ... See KI#21.8.\"; written as <!-- custom: NOTE (CREDIT) -->")
	parser.add_argument("--credit", help="the model credit for --note, such as \"Claude code Opus 5.5\"")
	parser.add_argument("--apply", action="store_true", help="write the files; without it, only list what would change")
	args = parser.parse_args()
	if bool(args.note) != bool(args.credit):
		parser.error("--note and --credit go together, as a custom note carries a model credit")
	if not args.files and not args.from_provenance:
		parser.error("name files or pass --from-provenance")
	files = [path.as_posix() for path in args.files] + (provenance_files(args.base_ref) if args.from_provenance else [])
	if not files:
		print("No file lacks the SAS header.")
		return 0
	note = "<!-- custom: %s (%s) -->" % (args.note, args.credit) if args.note else None
	# <!-- custom: Every file is checked first and written only once all pass, so a failing check leaves nothing half done (AGENTS.md, File management). (Claude code Opus 5.5) -->
	plans, problems = [], []
	for name in files:
		path = REPO_ROOT / name
		text, encoding = read(path)
		if MARKER in text:
			problems.append("%s: already has the SAS header" % name)
			continue
		try:
			plans.append((name, path, with_header(text, note).encode(encoding)))
		except ValueError as exc:
			problems.append("%s: %s" % (name, exc))
		except UnicodeEncodeError as exc:
			problems.append("%s: the note cannot be written as %s (%s)" % (name, encoding, exc))
	for problem in problems:
		print("SKIP " + problem)
	# <!-- custom: With a problem left, --apply writes nothing, as the comment above promises; the first version still wrote the files that passed (Codex's review, 2026-11-23). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if args.apply and problems:
		print("Nothing written: fix or drop the files above first.")
		return 1
	for name, path, data in plans:
		if args.apply:
			path.write_bytes(data)
		print(("ADDED " if args.apply else "WOULD ADD ") + name)
	return 1 if problems else 0


if __name__ == "__main__":
	sys.exit(main())

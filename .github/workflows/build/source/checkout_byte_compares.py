#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: ui_map_sync.py compared a checked-out file with its generator's output as bytes, so on a Windows clone whose checkout writes CRLF it failed on an unchanged file, while GitHub's LF checkout passed (2026-11-16).
# Such a failure shows only locally, so this check makes every byte comparison in the CI build scripts carry a "# bytes-compare: <reason>" note on its line or the line above; text comparisons ignore line endings. (Claude code Opus 5.5) -->
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCAN = Path(".github/workflows/build")
COMPARE = re.compile(r"read_bytes\(\)\s*(?:==|!=)|(?:==|!=)\s*[^#\n]*read_bytes\(\)")
NOTE = "# bytes-compare:"


def file_errors(path, relative):
	lines = path.read_text(encoding="utf-8").splitlines()
	errors = []
	for index, line in enumerate(lines):
		if not COMPARE.search(line.split("#", 1)[0]):
			continue
		if NOTE in line or (index > 0 and NOTE in lines[index - 1]):
			continue
		errors.append("%s:%d: byte comparison without a '%s <reason>' note; compare text (read_text) so CRLF and LF checkouts agree, or say why bytes are needed" % (relative, index + 1, NOTE))
	return errors


def main():
	parser = argparse.ArgumentParser(description="Require a reason for byte comparisons in the CI build scripts.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	files = sorted((args.repo_root / SCAN).rglob("*.py"))
	errors = [error for path in files for error in file_errors(path, path.relative_to(args.repo_root).as_posix())]
	if errors:
		print("FAIL checkout byte comparisons")
		for error in errors:
			print("  - " + error)
		return 1
	print("PASS checkout byte comparisons (%d file(s) checked)" % len(files))
	return 0


if __name__ == "__main__":
	sys.exit(main())

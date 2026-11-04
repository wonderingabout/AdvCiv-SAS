#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: active XML, Python and C++ code does not use XML asset identifiers that SAS retired.

# <!-- custom: argparse/pathlib/re/sys drive the CLI, file scan and table parsing. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys

# <!-- custom: Shared repo-root resolution, as in the sibling XML checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


# <!-- custom: On 2026-11-04 SAS restored the inherited bonus and leader identifiers (for example BONUS_GRAPES back to BONUS_WINE, LEADER_MAO_ZEDONG back to LEADER_CHINESE_LEADER).
# Nothing failed if new code reused a retired spelling, which would silently point at a missing asset.
# The retired names come from the first column of the xml_asset_names.md tables, so the doc stays the single list; "*" there stands for any identifier characters.
# Only code is checked, not comments or docs, which keep the old names as history. (Claude code Opus 5.5) -->
MAP_FILE = Path("_1_AdvCiv-SAS/Docs/Deprecated/xml_asset_names.md")
TABLE_HEADER = "| Retired SAS machine family |"
SOURCE_GLOBS = ("Assets/XML/**/*.xml", "Assets/Config/**/*.xml", "Assets/Python/**/*.py", "PrivateMaps/**/*.py", "CvGameCoreDLL/**/*.cpp", "CvGameCoreDLL/**/*.h")
COMMENT_RES = {
	".xml": re.compile(r"<!--.*?-->", re.S),
	".py": re.compile(r"#[^\n]*"),
	".cpp": re.compile(r"//[^\n]*|/\*.*?\*/", re.S),
	".h": re.compile(r"//[^\n]*|/\*.*?\*/", re.S),
}


def retired_patterns(repo_root: Path) -> list[tuple[str, re.Pattern]]:
	text = (repo_root / MAP_FILE).read_text(encoding="utf-8")
	patterns = []
	in_table = False
	for line in text.splitlines():
		if line.startswith(TABLE_HEADER):
			in_table = True
			continue
		if in_table and line.startswith("| ---"):
			continue
		if in_table and line.startswith("|"):
			first_cell = line.split("|")[1]
			for name in re.findall(r"`([A-Z0-9_*]+)`", first_cell):
				body = re.escape(name).replace(r"\*", "[A-Z0-9_]*")
				patterns.append((name, re.compile(r"(?<![A-Za-z0-9_])" + body + r"(?![A-Za-z0-9_])")))
			continue
		in_table = False
	if not patterns:
		raise SystemExit(f"{MAP_FILE}: no retired names found under a '{TABLE_HEADER}' table")
	return patterns


def check(repo_root: Path) -> list[str]:
	patterns = retired_patterns(repo_root)
	combined = re.compile("|".join(pattern.pattern for _name, pattern in patterns))
	failures = []
	seen = set()
	for glob in SOURCE_GLOBS:
		for path in sorted(repo_root.glob(glob)):
			if path in seen or not path.is_file():
				continue
			seen.add(path)
			raw = path.read_text(encoding="utf-8", errors="replace")
			code = COMMENT_RES[path.suffix.lower()].sub(lambda m: "\n" * m.group(0).count("\n"), raw)
			# <!-- custom: One combined pattern per file keeps the scan fast; the matching retired name is looked up only for hits. (Claude code Opus 5.5) -->
			for match in combined.finditer(code):
				name = next(name for name, pattern in patterns if pattern.fullmatch(match.group(0)))
				line = code.count("\n", 0, match.start()) + 1
				failures.append(f"{path.relative_to(repo_root).as_posix()}:{line}: {match.group(0)} uses the retired SAS name {name}; use the current identifier listed in {MAP_FILE.as_posix()}")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that active code does not use retired SAS XML asset identifiers.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL retired XML asset names")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS retired XML asset names")
	return 0


if __name__ == "__main__":
	sys.exit(main())

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Renames identifiers, such as SAS defines, in every tracked text file at once: C++, XML, map scripts, theme files and docs alike.
# Written on 2026-11-12 for the SAS_EXE_PATCH_* -> SAS_EXE_P_* rename, which touched 14 kinds of file; define renames recur (KI#1001.2, SAS_SCRAP_*), and hand edits miss files or break CRLF. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: argparse for options, re for the identifier boundaries, subprocess for git ls-files, Path for files. (Claude code Opus 5.5) -->
import argparse
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# <!-- custom: Verbatim history keeps the names it was written with: the git logs, archived changelogs, generated corpora, and the deprecated-name table, whose old-name column must stay old (fix its new-name column by hand). (Claude code Opus 5.5) -->
SKIPPED = ("_1_AdvCiv-SAS/Docs/git_logs/", "_1_AdvCiv-SAS/Docs/changelogs_web/", "LLM_Helpers/context/", "_1_AdvCiv-SAS/Docs/Deprecated/")
# <!-- custom: KI#1001.2's byte limit for SAS define names, drawn from AdvCiv. (Claude code Opus 5.5) -->
MAX_DEFINE_BYTES = 42


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Rename identifiers in every tracked text file, keeping line endings and encoding. Dry run unless --write.")
	parser.add_argument("pairs", nargs="+", metavar="OLD=NEW", help="An identifier or prefix and its replacement, such as SAS_EXE_PATCH_=SAS_EXE_P_; the longest OLD wins where several match")
	parser.add_argument("--write", action="store_true", help="Change the files; without it, only list what would change")
	parser.add_argument("--include-history", action="store_true", help="Also rewrite the skipped history folders")
	parser.add_argument("--exclude", action="append", default=[], metavar="PATH", help="Leave this repo-relative file or folder alone, such as a doc that describes the rename itself; repeatable")
	return parser.parse_args()


def tracked_files() -> list[Path]:
	# <!-- custom: Tracked files only, plus untracked ones that git does not ignore, so new uncommitted files are renamed too. (Claude code Opus 5.5) -->
	out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, check=True).stdout
	return [REPO / name for name in sorted(set(out.decode("utf-8").split("\0"))) if name]


def main() -> int:
	args = parse_args()
	pairs = dict(pair.split("=", 1) for pair in args.pairs)
	# <!-- custom: Left boundary only, so a prefix such as SAS_EXE_PATCH_ also renames SAS_EXE_PATCH_ON; longest first, so SAS_EXE_PATCH_SETUP_SCREEN_ beats SAS_EXE_PATCH_. (Claude code Opus 5.5) -->
	olds = sorted(pairs, key=len, reverse=True)
	pattern = re.compile(rb"(?<![A-Za-z0-9_])(" + rb"|".join(re.escape(o.encode()) for o in olds) + rb")")
	changed = {}
	names = set()
	for path in tracked_files():
		rel = path.relative_to(REPO).as_posix()
		if (not args.include_history and rel.startswith(SKIPPED)) or path == Path(__file__).resolve() or any(rel == e.replace("\\", "/").rstrip("/") or rel.startswith(e.replace("\\", "/").rstrip("/") + "/") for e in args.exclude):
			continue
		if not path.is_file():
			continue
		data = path.read_bytes()
		if b"\0" in data[:8192] or not pattern.search(data):
			continue
		new = pattern.sub(lambda m: pairs[m.group(1).decode()].encode(), data)
		changed[rel] = len(pattern.findall(data))
		for match in re.finditer(rb"(?<![A-Za-z0-9_])(" + rb"|".join(re.escape(pairs[o].encode()) for o in olds) + rb")[A-Z0-9_]*", new):
			names.add(match.group(0).decode())
		if args.write:
			path.write_bytes(new)
	for rel, count in changed.items():
		print("%4d  %s" % (count, rel))
	print("%s %d files" % ("changed" if args.write else "would change", len(changed)))
	too_long = sorted(n for n in names if n.startswith("SAS_") and len(n) > MAX_DEFINE_BYTES)
	for name in too_long:
		print("over %d bytes: %s (%d)" % (MAX_DEFINE_BYTES, name, len(name)))
	return 1 if too_long else 0


if __name__ == "__main__":
	raise SystemExit(main())

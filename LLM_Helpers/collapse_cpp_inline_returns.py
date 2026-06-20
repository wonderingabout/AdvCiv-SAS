#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Conservative C++ header cleanup helper.
#
# Collapses simple inline functions whose body is exactly one return statement:
#   T f(...) const
#   {
#       return expr;
#   }
# becomes:
#   T f(...) const { return expr; }
#
# This is intentionally separate from collapse_cpp_signatures.py; it rewrites
# function bodies, not just signatures. Review the diff before committing.

from __future__ import annotations

from pathlib import Path
import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import difflib
import re
import sys

from collapse_cpp_signatures import (
	decode_bytes,
	display_path,
	get_default_repo_root,
	iter_candidate_files,
	split_line_ending,
	stripped_for_length,
)


HEADER_SUFFIXES = {".h", ".hpp", ".inl"}
CONTROL_START_WORDS = {"if", "else", "for", "while", "switch", "catch", "return", "sizeof"}


class Rewrite:
	def __init__(self, start: int, end: int, lines: list[str]):
		self.start = start
		self.end = end
		self.lines = lines


class Stats:
	def __init__(self):
		self.files_scanned = 0
		self.files_changed = 0
		self.functions = 0


def leading_ws(text: str) -> str:
	return text[: len(text) - len(text.lstrip(" \t"))]


def default_diff_file_path(repo_root: Path, timestamp: str) -> Path:
	return repo_root / "LLM_Helpers" / "outputs" / f"collapse_cpp_inline_returns_{timestamp}.diff.txt"


def resolve_output_file_path(repo_root: Path, value: str | None, default_path: Path) -> Path | None:
	if value is None:
		return None
	if value == "auto":
		return default_path
	path = Path(value)
	return path if path.is_absolute() else repo_root / path


def line_comment_index(text: str) -> int:
	in_string = None
	escaped = False
	for index, ch in enumerate(text):
		if in_string is not None:
			if escaped:
				escaped = False
			elif ch == "\\":
				escaped = True
			elif ch == in_string:
				in_string = None
			continue
		if ch in ('"', "'"):
			in_string = ch
			continue
		if ch == "/" and index + 1 < len(text) and text[index + 1] == "/":
			return index
	return -1


def split_tail_comment(text: str) -> tuple[str, str | None]:
	index = line_comment_index(text)
	if index < 0:
		return text.rstrip(), None
	return text[:index].rstrip(), text[index + 2 :].strip()


def signature_start_is_safe(text: str) -> bool:
	stripped = text.strip()
	if not stripped or stripped.startswith(("//", "/*", "*", "#")):
		return False
	if any(stripped.startswith(word + " ") or stripped.startswith(word + "(") for word in CONTROL_START_WORDS):
		return False
	if "(" not in stripped or ")" not in stripped:
		return False
	if stripped.endswith(("{", ";", ":")):
		return False
	prefix = stripped.split("(", 1)[0].strip()
	if not prefix or "=" in prefix or "." in prefix or "->" in prefix:
		return False
	if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", prefix):
		# Constructor/destructor bodies need a separate review pass.
		return False
	return True


def return_line_payload(text: str) -> str | None:
	stripped = text.strip()
	if not stripped.startswith("return ") or not stripped.endswith(";"):
		return None
	if line_comment_index(stripped) >= 0:
		return None
	return stripped


def try_rewrite(bodies: list[str], eols: list[str], index: int, max_line_len: int) -> Rewrite | None:
	if index + 3 >= len(bodies):
		return None
	signature = bodies[index]
	open_brace = bodies[index + 1]
	return_payload = return_line_payload(bodies[index + 2])
	close_brace = bodies[index + 3]
	if return_payload is None:
		return None
	if leading_ws(open_brace) != leading_ws(signature) or open_brace.strip() != "{":
		return None
	if close_brace.strip() != "}":
		return None
	if leading_ws(close_brace) != leading_ws(signature):
		return None
	signature_code, signature_comment = split_tail_comment(signature)
	if not signature_start_is_safe(signature_code):
		return None
	collapsed = signature_code.strip() + " { " + return_payload + " }"
	if signature_comment is not None:
		collapsed += " // " + signature_comment
	if len(stripped_for_length(collapsed)) > max_line_len:
		return None
	return Rewrite(index, index + 3, [leading_ws(signature) + collapsed + eols[index]])


def rewrite_lines(lines: list[str], max_line_len: int) -> tuple[list[str], Stats]:
	bodies: list[str] = []
	eols: list[str] = []
	for line in lines:
		body, eol = split_line_ending(line)
		bodies.append(body)
		eols.append(eol)
	stats = Stats()
	new_lines: list[str] = []
	index = 0
	while index < len(lines):
		rewrite = try_rewrite(bodies, eols, index, max_line_len)
		if rewrite is None:
			new_lines.append(lines[index])
			index += 1
			continue
		new_lines.extend(rewrite.lines)
		stats.functions += 1
		index = rewrite.end + 1
	return new_lines, stats


def process_file(repo_root: Path, path: Path, args: argparse.Namespace, stats: Stats, diff_file) -> bool:
	relative_path = path.relative_to(repo_root)
	if path.suffix.lower() not in HEADER_SUFFIXES:
		return False
	raw = path.read_bytes()
	encoding, text = decode_bytes(raw)
	lines = text.splitlines(keepends=True)
	new_lines, file_stats = rewrite_lines(lines, args.max_line_len)
	stats.files_scanned += 1
	if file_stats.functions == 0:
		return False
	old_text = "".join(lines)
	new_text = "".join(new_lines)
	if old_text == new_text:
		return False
	stats.files_changed += 1
	stats.functions += file_stats.functions
	if diff_file is not None:
		diff_file.writelines(
			difflib.unified_diff(
				lines,
				new_lines,
				fromfile=f"{relative_path.as_posix()} (before)",
				tofile=f"{relative_path.as_posix()} (after)",
				lineterm="\n",
			)
		)
	if args.in_place:
		path.write_text(new_text, encoding=encoding, newline="")
	return True


def parse_args(argv: list[str]) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Collapse simple one-return inline C++ header functions.")
	parser.add_argument("paths", nargs="*", type=Path, help="files or directories to scan; defaults to tracked C/C++ files under CvGameCoreDLL")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	parser.add_argument("--in-place", action="store_true", help="write changes instead of only reporting")
	parser.add_argument("--diff-file", nargs="?", const="auto", default=None, help="write review diff to a file; without a path, writes a timestamped diff under LLM_Helpers/outputs/")
	parser.add_argument("--max-line-len", type=int, default=600)
	return parser.parse_args(argv)


def main(argv: list[str]) -> int:
	args = parse_args(argv)
	repo_root = args.repo_root.resolve()
	timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
	diff_file_path = resolve_output_file_path(repo_root, args.diff_file, default_diff_file_path(repo_root, timestamp))
	if diff_file_path is not None:
		diff_file_path.parent.mkdir(parents=True, exist_ok=True)
	stats = Stats()
	changed: list[Path] = []
	diff_context = diff_file_path.open("w", encoding="utf-8", newline="") if diff_file_path is not None else nullcontext(None)
	with diff_context as diff_file:
		for path in iter_candidate_files(repo_root, args.paths):
			if process_file(repo_root, path, args, stats, diff_file):
				changed.append(path.relative_to(repo_root))
	print(f"Scanned {stats.files_scanned} C/C++ header-like file(s).")
	if changed:
		verb = "Updated" if args.in_place else "Would update"
		print(f"{verb} {len(changed)} file(s): {stats.functions} inline return collapse(s).")
		for path in changed:
			print(f"  - {display_path(repo_root, repo_root / path)}")
		if diff_file_path is not None:
			print(f"Diff file written: {display_path(repo_root, diff_file_path)}")
		if not args.in_place:
			print("Run again with --in-place after reviewing the target list/diff.")
			return 1
	else:
		print("No simple inline return collapses found.")
		if diff_file_path is not None and diff_file_path.exists() and diff_file_path.stat().st_size == 0:
			diff_file_path.unlink()
	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv[1:]))

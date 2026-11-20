# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Git counterpart of svn_history_to_diffs.py: exports another mod's Git history as one greppable diff per commit, plus INDEX.txt and PATH_HISTORY_INDEX.txt in the same format, so SVN and Git histories read alike.
# Our own commit_diffs/ come from make_light_source_zip.py, whose exclusions and history segments are specific to AdvCiv-SAS; this helper is for other repositories, such as Caveman2Cosmos's GitHub clone. (Claude code Opus 5.5) -->
from __future__ import annotations

# <!-- custom: Standard library only, like svn_history_to_diffs.py: argparse for options, fnmatch for --summarize globs, re for email redaction, subprocess to run git. (Claude code Opus 5.5) -->
import argparse
import fnmatch
import re
import subprocess
import sys
# <!-- custom: ThreadPoolExecutor exports commits in parallel; Path handles files. (Claude code Opus 5.5) -->
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_MAX_FILE_PATCH_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_FILE_CHANGED_LINES = 10_000
DEFAULT_MAX_COMMIT_PATCH_BYTES = 16 * 1024 * 1024
# <!-- custom: Same binary list as svn_history_to_diffs.py.
# In a blobless clone, excluding these by name also keeps git from downloading their contents. (Claude code Opus 5.5) -->
BINARY_PATTERNS = ("*.7z", "*.bin", "*.bmp", "*.dds", "*.dll", "*.exe", "*.exp", "*.fpk", "*.gif", "*.ico", "*.idb", "*.ilk", "*.jpg", "*.kf", "*.kfm", "*.lib", "*.ncb", "*.nif", "*.obj", "*.opt", "*.pch", "*.pdb", "*.png", "*.rar", "*.sdf", "*.suo", "*.tga", "*.zip", "*.bik", "*.mp3", "*.wav", "*.ogg")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]*\w")
FIELD_SEP = "\x1f"
RECORD_SEP = "\x1e"


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Export a Git repository's history as one greppable diff per commit, plus INDEX.txt and PATH_HISTORY_INDEX.txt, in the format of svn_history_to_diffs.py.")
	parser.add_argument("--repo", required=True, help="Path of the Git working copy or clone, which may be blobless")
	parser.add_argument("--out", required=True, help="Output folder. Existing commit files are kept, so an interrupted run resumes.")
	parser.add_argument("--label", required=True, help="Short name that prefixes each file, for example C2C")
	parser.add_argument("--rev", default="HEAD", help="Commit whose ancestry is exported (default HEAD)")
	parser.add_argument("--first", type=int, default=1, help="First commit number to export, counting the oldest as 1")
	parser.add_argument("--last", type=int, default=None, help="Last commit number to export (default: the newest)")
	parser.add_argument("--summarize", action="append", default=[], metavar="GLOB", help="Path glob to list without fetching its contents, such as art folders. Repeatable.")
	parser.add_argument("--workers", type=int, default=4, help="Commits rendered in parallel (default 4)")
	parser.add_argument("--newest-first", action="store_true", help="Render the newest commits first")
	parser.add_argument("--max-file-patch-bytes", type=int, default=DEFAULT_MAX_FILE_PATCH_BYTES)
	parser.add_argument("--max-file-changed-lines", type=int, default=DEFAULT_MAX_FILE_CHANGED_LINES)
	parser.add_argument("--max-commit-patch-bytes", type=int, default=DEFAULT_MAX_COMMIT_PATCH_BYTES)
	parser.add_argument("--force", action="store_true", help="Re-render commit files that already exist")
	return parser.parse_args()


def git(repo: Path, *args: str) -> str:
	result = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=off", *args], capture_output=True)
	if result.returncode != 0:
		raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
	return result.stdout.decode("utf-8", "replace")


def redact(text: str) -> str:
	return EMAIL_PATTERN.sub("<email redacted>", text)


def list_commits(repo: Path, rev: str) -> list[dict[str, str]]:
	# <!-- custom: Oldest first, so commit numbers stay stable as new commits arrive; --topo-order keeps every parent before its children. (Claude code Opus 5.5) -->
	fmt = FIELD_SEP.join(("%H", "%P", "%an", "%aI", "%B")) + RECORD_SEP
	raw = git(repo, "log", "--reverse", "--topo-order", f"--format={fmt}", rev)
	commits = []
	for record in raw.split(RECORD_SEP):
		record = record.strip("\n")
		if not record:
			continue
		sha, parents, author, date, message = record.split(FIELD_SEP, 4)
		commits.append({"sha": sha, "parents": parents.split(), "author": author, "date": date, "message": message.strip()})
	return commits


def matches_any(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
	return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path.lower(), pattern.lower()) for pattern in patterns)


def changed_paths(repo: Path, commit: dict) -> list[tuple[str, str]]:
	base = commit["parents"][0] if commit["parents"] else None
	args = ["diff-tree", "--no-commit-id", "-r", "--name-status", "-M", base, commit["sha"]] if base else ["diff-tree", "--no-commit-id", "-r", "--root", "--name-status", "-M", commit["sha"]]
	rows = []
	for line in git(repo, *args).splitlines():
		parts = line.split("\t")
		status = parts[0][0]
		if status == "R" and len(parts) == 3:
			rows.append(("R", f"{parts[2]} (from {parts[1]})"))
		else:
			rows.append((status, parts[-1]))
	return rows


def commit_filename(label: str, number: int, sha: str) -> str:
	return f"{label}_{number:05d}_{sha[:10]}.diff"


def render_commit(repo: Path, number: int, commit: dict, args: argparse.Namespace) -> str:
	paths = changed_paths(repo, commit)
	header = ["# Git commit diff", f"# Source: {args.source}", f"# Commit: {number} ({commit['sha']})", f"# Author: {redact(commit['author'])}", f"# Date: {commit['date']}"]
	body: list[str] = []
	partial = False
	if len(commit["parents"]) > 1:
		body.append("# Merge commit: paths are listed against its first parent, without a patch, since the merged commits carry their own diffs.")
	else:
		remaining = args.max_commit_patch_bytes
		for status, shown in paths:
			path, _, origin = shown.partition(" (from ")
			origin = origin.rstrip(")")
			# <!-- custom: Deletions were listed without their removed lines yet counted as full coverage, losing the deleted code that archaeology often needs; they now render like any other patch. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			if matches_any(path, BINARY_PATTERNS) or matches_any(path, args.summarize):
				note = "Binary file, contents not shown" if matches_any(path, BINARY_PATTERNS) else "Summarized path, contents not fetched"
				body.append(f"Index: {path}\n# {note}\n")
				if not matches_any(path, BINARY_PATTERNS):
					partial = True
				continue
			# <!-- custom: A rename's patch needs both of its paths: limited to the new path alone, git showed an added file and dropped the rename from and rename to lines. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			pathspec = [origin, path] if origin else [path]
			diff_args = ["diff", "--no-color", "-M", commit["parents"][0], commit["sha"], "--", *pathspec] if commit["parents"] else ["show", "--no-color", "--format=", commit["sha"], "--", path]
			patch = git(repo, *diff_args)
			if "Binary files" in patch.split("@@", 1)[0]:
				body.append(f"Index: {path}\n# Binary file, contents not shown\n")
				continue
			changed = sum(1 for line in patch.splitlines() if line[:1] in "+-" and not line.startswith(("+++", "---")))
			size = len(patch.encode("utf-8"))
			if changed > args.max_file_changed_lines or size > args.max_file_patch_bytes or size > remaining:
				body.append(f"Index: {path}\n# Left out: {changed} changed lines, {size} bytes\n")
				partial = True
				continue
			remaining -= size
			body.append(f"Index: {path}\n{redact(patch)}")
	message = "\n".join(f"#   {line}" for line in redact(commit["message"]).splitlines()) or "#   (no message)"
	header += [f"# Coverage: {'partial' if partial else 'full'}", "# Message:", message, f"# Changed paths ({len(paths)}):"]
	header += [f"#   {status} {shown}" for status, shown in paths]
	(args.out / commit_filename(args.label, number, commit["sha"])).write_text("\n".join(header) + "\n\n" + "\n".join(body), encoding="utf-8", newline="\n")
	return "partial" if partial else "full"


def read_coverage(path: Path) -> str:
	with path.open(encoding="utf-8") as handle:
		for line in handle:
			if line.startswith("# Coverage: "):
				return line[len("# Coverage: "):].strip()
	return "unknown"


def write_indexes(repo: Path, numbered: list[tuple[int, dict]], args: argparse.Namespace) -> None:
	span = f"{numbered[0][0]}-{numbered[-1][0]}"
	index = [f"# Git commit diff index for {args.label}", f"# Source: {args.source} ({span} of {args.total} commits, oldest = 1)", "# Generated by LLM_Helpers/code_history/git_history_to_diffs.py.", "# Files are named <label>_<number>_<sha>.diff; coverage is full or partial.", "# Columns: number<TAB>date<TAB>author<TAB>changed-paths<TAB>coverage<TAB>title-preview"]
	history: dict[str, list[str]] = {}
	for number, commit in numbered:
		paths = changed_paths(repo, commit)
		coverage = read_coverage(args.out / commit_filename(args.label, number, commit["sha"]))
		title = redact(commit["message"].splitlines()[0] if commit["message"] else "")[:100]
		index.append(f"{number}\t{commit['date']}\t{redact(commit['author'])}\t{len(paths)}\t{coverage}\t{title}")
		for status, shown in paths:
			path, _, origin = shown.partition(" (from ")
			history.setdefault(path, []).append(f"  {args.label} {number} {status}" + (f" from {origin.rstrip(')')}" if origin else ""))
	(args.out / "INDEX.txt").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
	lines = [f"# Path history for {args.label} ({span})", "# Maps each path to the commits that changed it, newest -> oldest.", "# Rows: <label> <number> <A|M|D|R|C|T> [from <path>]. Follow a 'from' origin to continue a file's history before its rename."]
	for path in sorted(history):
		lines.append(path)
		lines += reversed(history[path])
	(args.out / "PATH_HISTORY_INDEX.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
	args = parse_args()
	repo = Path(args.repo).resolve()
	args.out = Path(args.out)
	args.out.mkdir(parents=True, exist_ok=True)
	# <!-- custom: A repository without an origin remote, such as a local fixture, made git fail here; its own path names the source instead. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	try:
		args.source = git(repo, "remote", "get-url", "origin").strip() or str(repo)
	except RuntimeError:
		args.source = str(repo)
	commits = list_commits(repo, args.rev)
	args.total = len(commits)
	last = args.last or len(commits)
	numbered = [(number, commit) for number, commit in enumerate(commits, 1) if args.first <= number <= last]
	todo = [(n, c) for n, c in numbered if args.force or not (args.out / commit_filename(args.label, n, c["sha"])).exists()]
	if args.newest_first:
		todo.reverse()
	print(f"{args.label}: commits {args.first}-{last} of {len(commits)}, {len(todo)} to render", flush=True)
	failures = []
	with ThreadPoolExecutor(max_workers=args.workers) as pool:
		futures = {pool.submit(render_commit, repo, n, c, args): n for n, c in todo}
		for done, future in enumerate(as_completed(futures), 1):
			try:
				future.result()
			except Exception as error:
				# <!-- custom: Collect every failure and report them all at the end, as the SVN exporter does, so one rerun retries them. (Claude code Opus 5.5) -->
				failures.append((futures[future], str(error)))
			if done % 25 == 0 or done == len(todo):
				print(f"  {done}/{len(todo)} commits, {len(failures)} failed", flush=True)
	if failures:
		for number, error in sorted(failures):
			print(f"FAILED {number}: {error}", file=sys.stderr)
		print("Indexes not written; rerun the same command to retry the failed commits.", file=sys.stderr)
		return 1
	write_indexes(repo, numbered, args)
	print(f"Wrote {len(numbered)} commits and both indexes to {args.out}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

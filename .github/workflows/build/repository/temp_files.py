#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: git must track nothing under CvGameCoreDLL/Project/temp_files, and no repository filter rule may re-include it.
#
# <!-- custom: We suspect fast-compile temp files can produce unreliable DLLs; this check used to fail on every generated target except Debug-opt, whose matching PDB is deliberately retained for crash analysis. See KI#38 and KI#38.2. (ChatGPT-5.5 + GPT-5.5 + GPT-5.6-Sol) -->
# <!-- custom: Since 2026-11-11 build_with_report.ps1 refuses a BUILD while the target folder holds files, so local folders are left alone and only tracked files are checked.
# The tracked zero-byte .gitkeep that kept the folder in fresh clones for this check was dropped the same day: the Makefile creates the folder when missing, and nothing else needed it. (Claude Code Opus 5.5) -->

from pathlib import Path
import argparse
# <!-- custom: subprocess lists the tracked files under temp_files. (Claude Code Opus 5.5) -->
import subprocess
import sys

# <!-- custom: Resolve repository/shared-helper paths from this subject subfolder after the workflow-tool reorganization. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


TEMP_FILES_REL_PATH = Path("CvGameCoreDLL/Project/temp_files")
GIT_FILTER_REL_PATHS = (
	Path(".gitignore"),
	Path(".gitattributes"),
)
ALLOWED_GITIGNORE_RULES = {
	"/cvgamecoredll/project/temp_files/",
}


def active_temp_files_filter_rules(repo_root: Path) -> list[str]:
	# <!-- custom: Codex's review reproduced the check passing in a repository whose .gitignore lacked the temp_files line, so generated targets could flood git status unnoticed; the rule is now required. (Claude Code Opus 5.5 + GPT-6.1-Sol) -->
	failures: list[str] = []
	found_ignore_rule = False

	for rel_path in GIT_FILTER_REL_PATHS:
		path = repo_root / rel_path
		if not path.exists():
			failures.append(f"missing repository filter file: {rel_path.as_posix()}")
			continue
		if not path.is_file():
			failures.append(f"repository filter path is not a file: {rel_path.as_posix()}")
			continue

		for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
			stripped = line.strip()
			if not stripped or stripped.startswith("#"):
				continue
			normalized = stripped.replace("\\", "/").lower()
			if "temp_files" not in normalized:
				continue
			if rel_path == Path(".gitignore") and normalized in ALLOWED_GITIGNORE_RULES:
				found_ignore_rule = True
				continue
			failures.append(f"{rel_path.as_posix()}: line {line_number}: remove active temp_files rule: {stripped}")

	if not found_ignore_rule:
		failures.append(".gitignore: missing the rule /CvGameCoreDLL/Project/temp_files/ that keeps build targets out of git status")
	return failures


# <!-- custom: Was check_temp_files_folder, which also required the folder and its zero-byte .gitkeep; with the marker dropped on 2026-11-11 only the tracked-files part remains, hence the narrower name. (Claude Code Opus 5.5) -->
def tracked_temp_files(repo_root: Path) -> list[str]:
	tracked = subprocess.run(["git", "ls-files", "-z", "--", TEMP_FILES_REL_PATH.as_posix()], cwd=repo_root, capture_output=True, check=True).stdout.decode("utf-8").split("\0")
	unexpected = sorted(path for path in tracked if path)
	if unexpected:
		return ["compiler temp_files content is tracked by git; remove it from the index: " + ", ".join(unexpected)]
	return []


def check_temp_files(repo_root: Path) -> list[str]:
	failures: list[str] = []
	failures.extend(tracked_temp_files(repo_root))
	failures.extend(active_temp_files_filter_rules(repo_root))
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that git tracks nothing under CvGameCoreDLL/Project/temp_files.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	failures = check_temp_files(args.repo_root)

	if failures:
		print("FAIL compiler temp_files hygiene")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS compiler temp_files hygiene")
	print(f"  - git tracks nothing under {TEMP_FILES_REL_PATH.as_posix()}; local build targets are ignored")
	return 0


if __name__ == "__main__":
	sys.exit(main())

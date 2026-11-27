#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The EXE patches guide and its helpers stay in Git and the light-source ZIP for agents, but out of player and GitHub Download ZIP archives, and so do the files that describe them.
# Only the export-ignore lines in .gitattributes keep them out, and deleting one would pass unnoticed, so on 2026-11-12 the user asked for a check that fails when any is missing.
# argparse/sys provide the entry point, pathlib the paths, and subprocess asks Git for the effective export-ignore attribute rather than copying its pattern rules. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Folders end with "/": git check-attr reported ".github" as unspecified but ".github/" as set, because a pattern such as "/.github/" matches directories only.
# git archive still skipped the whole folder. (Claude code Opus 5.5) -->
REQUIRED = (
	".github/",
	"AGENTS.md",
	"LLM_Helpers/exe_analysis/",
	"_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md",
)


def unexcluded(repo, paths):
	result = subprocess.run(["git", "check-attr", "-z", "--stdin", "export-ignore"], cwd=repo, input="".join(path + "\0" for path in paths).encode("utf-8"), stdout=subprocess.PIPE, check=True)
	fields = result.stdout.decode("utf-8").split("\0")
	values = {fields[index]: fields[index + 2] for index in range(0, len(fields) - 1, 3)}
	return [path for path in paths if values.get(path) != "set"]


def check(repo):
	errors = []
	for path in REQUIRED:
		if not (repo / path.rstrip("/")).exists():
			errors.append("%s: missing; update REQUIRED in exe_patches_export_ignore.py if it moved" % path)
	for path in unexcluded(repo, [path for path in REQUIRED if (repo / path.rstrip("/")).exists()]):
		errors.append("%s: not export-ignore in .gitattributes, so it would ship in player and GitHub Download ZIP archives; see the EXE section of .gitattributes" % path)
	return errors


def main():
	parser = argparse.ArgumentParser(description="Require the EXE patches guide, its helpers and the files describing them to stay export-ignore.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	errors = check(args.repo_root)
	print("FAIL EXE patches export-ignore" if errors else "PASS EXE patches export-ignore (%d paths)" % len(REQUIRED))
	for error in errors:
		print("  - " + error)
	return int(bool(errors))


if __name__ == "__main__":
	sys.exit(main())

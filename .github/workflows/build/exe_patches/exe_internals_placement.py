#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: EXE internals stay in the export-ignored EXE patches guide and helpers, out of files that ship to players.

# <!-- custom: The EXE patches guide and LLM_Helpers/exe_analysis/ describe how we read the game's EXE, and stay out of player archives (exe_patches_export_ignore.py); files that ship may describe a patch's effect and link to the guide.
# On 2026-11-12 the user's review found such details had spread into shipping files anyway: a KI paragraph on the globe patch's code cave and "our decrypted EXE copy", and notes in the Game Runs guide and the UI map generator.
# Nothing checked the content, only the export-ignore lines.
# This check fails on those markers in any file that ships, so the details go to the guide instead. (Claude code Opus 5.5) -->
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Words that only describe reading the EXE: its decrypted copy, the Ghidra tool, Ghidra's FUN_ names and the cave idiom of a hook. (Claude code Opus 5.5) -->
MARKERS = re.compile(r"decrypted (?:copy|exe)|\bghidra\b|\bFUN_00[0-9a-f]{6}\b|code cave", re.I)
# <!-- custom: Code addresses in the EXE's range; the DLL source that applies the patches needs them, as AdvCiv's and RI's do. (Claude code Opus 5.5) -->
ADDRESS = re.compile(r"\b0x00[4-9a-fA-F][0-9a-fA-F]{5}\b")
ADDRESS_ALLOWED = ("CvGameCoreDLL/",)
# <!-- custom: Another mod's comment quoted as is in the DLL source, each line starting with "//" then ">", such as RI's own patch notes with Ghidra's FUN_ names: that text is already public in that mod's DLL source, and rewording it to pass would blur whose finding it is.
# See source_change_provenance.py's quoted_source_block. (Claude code Opus 5.5) -->
QUOTE_LINE = re.compile(r"^[ \t]*//[ \t]?>")
# <!-- custom: Inherited files kept verbatim: AdvCiv's manual quotes the addresses of AdvCiv's own patch, already public in every AdvCiv download. (Claude code Opus 5.5) -->
INHERITED = ("_0_Legacy/",)
BINARY_SUFFIXES = {".dll", ".pdb", ".dds", ".tga", ".nif", ".kfm", ".fpk", ".bik", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".wav", ".ogg", ".zip", ".exe", ".civbeyondswordsave", ".civbeyondswordreplay"}


def shipping_files(repo: Path) -> list[str]:
	listed = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=repo, capture_output=True, check=True).stdout.decode("utf-8").split("\0")
	paths = [p for p in listed if p and Path(p).suffix.lower() not in BINARY_SUFFIXES and not p.startswith(INHERITED)]
	result = subprocess.run(["git", "check-attr", "-z", "--stdin", "export-ignore"], cwd=repo, input="".join(p + "\0" for p in paths).encode("utf-8"), capture_output=True, check=True)
	fields = result.stdout.decode("utf-8").split("\0")
	ignored = {fields[i] for i in range(0, len(fields) - 2, 3) if fields[i + 2] == "set"}
	# <!-- custom: A folder pattern such as /.github/ marks the folder, not each file, for check-attr, though git archive skips everything in it; so a file under an export-ignored folder counts as ignored too. (Claude code Opus 5.5) -->
	folders = [p + "/" for p in (".github", "LLM_Helpers/exe_analysis") if subprocess.run(["git", "check-attr", "export-ignore", p + "/"], cwd=repo, capture_output=True, text=True).stdout.strip().endswith(": set")]
	return [p for p in paths if p not in ignored and not p.startswith(tuple(folders))]


def check(repo: Path) -> list[str]:
	failures = []
	for rel in shipping_files(repo):
		path = repo / rel
		if not path.is_file():
			continue
		data = path.read_bytes()
		if b"\0" in data[:8192]:
			continue
		for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
			found = None if rel.startswith(ADDRESS_ALLOWED) and QUOTE_LINE.match(line) else MARKERS.search(line)
			if not found and not rel.startswith(ADDRESS_ALLOWED):
				found = ADDRESS.search(line)
			if found:
				failures.append("%s:%d: '%s' describes the EXE's internals in a file that ships; move the detail to README_EXE_Patches.md and link to it" % (rel, number, found.group(0)))
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that EXE internals stay out of files that ship to players.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	args = parser.parse_args()
	failures = check(args.repo_root)
	print("FAIL EXE internals placement" if failures else "PASS EXE internals placement")
	for failure in failures:
		print("  - " + failure)
	return int(bool(failures))


if __name__ == "__main__":
	sys.exit(main())

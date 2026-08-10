#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: Removed or renamed technologies, assets, and UI features can leave apparently valid TXT_KEY entries behind. Audit every SAS-owned GameText file while explicitly accounting for inherited/EXE references and BUG's dynamically constructed key families; inherited AdvCiv/BUG/BULL files have too much static-analysis noise for a reliable blocking test and remain covered by the broader manual audit. (GPT-5.6-Sol) -->

from pathlib import Path
import argparse
import re
import sys


TARGET_GLOB = "Assets/XML/Text/AdvCiv-SAS*.xml"
REFERENCE_GLOBS = ("Assets/XML/**/*.xml", "Assets/Config/**/*.xml", "Assets/Python/**/*.py", "PrivateMaps/**/*.py", "CvGameCoreDLL/**/*.cpp", "CvGameCoreDLL/**/*.h")
TEXT_BLOCK_RE = re.compile(r"<TEXT>(.*?)</TEXT>", re.DOTALL | re.IGNORECASE)
TAG_DEF_RE = re.compile(r"<Tag>\s*(TXT_KEY_[A-Z0-9_]+)\s*</Tag>", re.IGNORECASE)
TAG_SPAN_RE = re.compile(r"<Tag>.*?</Tag>", re.DOTALL | re.IGNORECASE)
XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CPP_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"(?m)^\s*(?://|#).*$")
TOKEN_RE = re.compile(r"TXT_KEY_[A-Z0-9_]+")
DYNAMIC_PREFIXES = ("TXT_KEY_BUG_OPT_", "TXT_KEY_BUG_OPTLABEL_")
INHERITED_REFERENCE_KEYS = {
	# Confirmed in inherited BTS/vanilla Python or XML; the GitHub checkout contains the mod only.
	"TXT_KEY_FOREIGN_ADVISOR_SURPLUS_RESOURCES",
	"TXT_KEY_FOREIGN_ADVISOR_TRADE_TABLE",
	"TXT_KEY_MAIN_MENU_CIVILOPEDIA",
	"TXT_KEY_MAIN_MENU_PLAY_NOW",
	"TXT_KEY_MAIN_MENU_SELECT_DIFFICULTY_TITLE",
	"TXT_KEY_MAIN_MENU_SELECT_GAME_SPEED_TITLE",
	"TXT_KEY_MAIN_MENU_SELECT_SEALEVEL_TITLE",
	"TXT_KEY_MAIN_MENU_SELECT_WORLD_SETUP",
	"TXT_KEY_MAIN_MENU_SELECT_WORLD_SIZE_TITLE",
	"TXT_KEY_MENU_SEALEVEL",
	"TXT_KEY_MENU_SIZE",
	"TXT_KEY_PEDIA_SCREEN_TOP",
}
EXE_RUNTIME_REFERENCE_KEYS = {
	# No static mod/base/vanilla reference, but changing the High label changed its Custom Game list text in-game; Low uses the matching EXE convention.
	"TXT_KEY_SEALEVEL_HIGH_RECOMMEND",
	"TXT_KEY_SEALEVEL_LOW_RECOMMEND",
}


def read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8", errors="replace")


def collect_definitions(paths: list[Path]) -> set[str]:
	definitions: set[str] = set()
	for path in paths:
		for block in TEXT_BLOCK_RE.findall(XML_COMMENT_RE.sub("", read_text(path))):
			definitions.update(TAG_DEF_RE.findall(block))
	return definitions


def collect_references(repo_root: Path) -> set[str]:
	references: set[str] = set()
	seen: set[Path] = set()
	for pattern in REFERENCE_GLOBS:
		for path in repo_root.glob(pattern):
			resolved = path.resolve()
			if not path.is_file() or resolved in seen:
				continue
			seen.add(resolved)
			text = read_text(path)
			if path.suffix.casefold() == ".xml":
				text = XML_COMMENT_RE.sub("", TAG_SPAN_RE.sub("", text))
			else:
				text = LINE_COMMENT_RE.sub("", CPP_BLOCK_COMMENT_RE.sub("", text))
			references.update(TOKEN_RE.findall(text))
	return references


def check_unused_sas_text(repo_root: Path) -> tuple[list[str], list[str], list[str], list[str], int, int]:
	targets = sorted(path for path in repo_root.glob(TARGET_GLOB) if path.is_file())
	if not targets:
		raise RuntimeError(f"no files match {TARGET_GLOB}")
	definitions = collect_definitions(targets)
	if not definitions:
		raise RuntimeError(f"no TXT_KEY definitions found in {TARGET_GLOB}")
	references = collect_references(repo_root)
	inherited = sorted(definitions & INHERITED_REFERENCE_KEYS)
	exe_runtime = sorted(definitions & EXE_RUNTIME_REFERENCE_KEYS)
	dynamic = sorted(key for key in definitions if key not in references and key.startswith(DYNAMIC_PREFIXES))
	unused = sorted(key for key in definitions if key not in references and key not in INHERITED_REFERENCE_KEYS and key not in EXE_RUNTIME_REFERENCE_KEYS and not key.startswith(DYNAMIC_PREFIXES))
	return unused, inherited, exe_runtime, dynamic, len(definitions), len(targets)


def print_keys(title: str, keys: list[str]) -> None:
	print(f"{title} ({len(keys)}):")
	for key in keys:
		print(f"  - {key}")


def main() -> int:
	parser = argparse.ArgumentParser(description="Reject unused TXT_KEY entries in SAS-owned GameText XML files.")
	parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3], help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	try:
		unused, inherited, exe_runtime, dynamic, definition_count, file_count = check_unused_sas_text(args.repo_root)
	except RuntimeError as exc:
		print("FAIL unused SAS GameText")
		print(f"  - {exc}")
		return 1

	if unused:
		print("FAIL unused SAS GameText")
		for key in unused:
			print(f"  - {key}: defined in {TARGET_GLOB} but not referenced by active mod XML/Config/Python/PrivateMaps/C++")
		return 1

	print(f"PASS unused SAS GameText ({definition_count} referenced or explicitly accepted keys across {file_count} files)")
	print_keys("Confirmed inherited base references absent from the GitHub mod-only checkout", inherited)
	print_keys("Empirically confirmed EXE runtime references with no static mod/base/vanilla reference", exe_runtime)
	print_keys("Recognized dynamically constructed BUG keys", dynamic)
	return 0


if __name__ == "__main__":
	sys.exit(main())

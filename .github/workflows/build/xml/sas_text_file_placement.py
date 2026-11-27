#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: SAS Sevopedia texts sit in their dedicated file and use the _PEDIA name.
# Asset pedia entries (*_PEDIA) belong in AdvCiv-SAS_Sevopedia_Lengthy.xml, even short stubs; concept pages (TXT_KEY_CONCEPT_*_PEDIA) belong in AdvCiv-SAS_Core.xml.
# A SAS text used as an XML <Civilopedia> value must end in _PEDIA, and a SAS _PEDIA text must be used as one. Inherited texts are not checked.

# <!-- custom: argparse/pathlib/re/sys drive the CLI and the text scan. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys

# <!-- custom: Shared repo-root resolution, as in the sibling XML checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


# <!-- custom: The 2026-11-05 City Center work added its two pedia texts to AdvCiv-SAS_main.xml, where the Warrior pedia and a shared Barbarian stub already sat, although AGENTS.md puts pedia texts in Sevopedia Lengthy.
# All four were moved; this check keeps new ones in place. (Claude code Opus 5.5) -->
TEXT_DIR = Path("Assets/XML/Text")
SAS_TEXT_GLOB = "AdvCiv-SAS*.xml"
PEDIA_FILE = "AdvCiv-SAS_Sevopedia_Lengthy.xml"
CONCEPT_FILE = "AdvCiv-SAS_Core.xml"
PEDIA_TAG_RE = re.compile(rb"<Tag>\s*(TXT_KEY_\w+_PEDIA)\s*</Tag>")
COMMENT_RE = re.compile(rb"<!--.*?-->", re.S)
CIVILOPEDIA_RE = re.compile(rb"<Civilopedia>\s*(TXT_KEY_\w+)\s*</Civilopedia>")
TEXT_TAG_RE = re.compile(rb"<Tag>\s*(TXT_KEY_\w+)\s*</Tag>")
# <!-- custom: CONCEPT_BASE_ADVCIV_SOME_CHANGES uses TXT_KEY_BASE_ADVCIV_SOME_CHANGES_PEDIA_SR, after BtS's own TXT_KEY_BTS_RULES_CHANGES_PEDIA_SR concept page, so that suffix counts as a pedia name too. (Claude code Opus 5.5) -->
PEDIA_SUFFIXES = ("_PEDIA", "_PEDIA_SR")


def check(repo_root: Path) -> list[str]:
	failures = []
	for path in sorted((repo_root / TEXT_DIR).glob(SAS_TEXT_GLOB)):
		data = COMMENT_RE.sub(lambda m: b"\n" * m.group(0).count(b"\n"), path.read_bytes())
		for match in PEDIA_TAG_RE.finditer(data):
			tag = match.group(1).decode("ascii")
			expected = CONCEPT_FILE if tag.startswith("TXT_KEY_CONCEPT_") else PEDIA_FILE
			if path.name != expected:
				line = data.count(b"\n", 0, match.start()) + 1
				failures.append(f"{path.relative_to(repo_root).as_posix()}:{line}: {tag} belongs in {TEXT_DIR.as_posix()}/{expected}")
	failures.extend(check_pedia_names(repo_root))
	return failures


def civilopedia_values(repo_root: Path) -> set[str]:
	values = set()
	for path in (repo_root / "Assets/XML").rglob("*.xml"):
		if TEXT_DIR.name in path.relative_to(repo_root).parts:
			continue
		values.update(tag.decode("ascii") for tag in CIVILOPEDIA_RE.findall(COMMENT_RE.sub(b"", path.read_bytes())))
	return values


def check_pedia_names(repo_root: Path) -> list[str]:
	values = civilopedia_values(repo_root)
	failures = []
	for path in sorted((repo_root / TEXT_DIR).glob(SAS_TEXT_GLOB)):
		for tag in sorted(set(match.decode("ascii") for match in TEXT_TAG_RE.findall(COMMENT_RE.sub(b"", path.read_bytes())))):
			named = tag.endswith(PEDIA_SUFFIXES)
			if tag in values and not named:
				failures.append(f"{path.relative_to(repo_root).as_posix()}: {tag} is a <Civilopedia> text but does not end in _PEDIA")
			elif named and tag not in values:
				failures.append(f"{path.relative_to(repo_root).as_posix()}: {tag} ends in _PEDIA but no XML <Civilopedia> field uses it")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that SAS pedia and concept texts sit in their dedicated text files.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	failures = check(args.repo_root)
	if failures:
		print("FAIL SAS text file placement")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS SAS text file placement")
	return 0


if __name__ == "__main__":
	sys.exit(main())

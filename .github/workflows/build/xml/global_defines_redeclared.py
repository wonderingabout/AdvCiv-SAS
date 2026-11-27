#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The carried BtS GlobalDefines.xml leaves out the names a file the DLL loads later declares again, listing each in its header as "NAME = value in BtS, redeclared in FILE" (KI#1104.2).
# This check holds that list true: each listed name must be declared in the named file, as an XML parse finds it, so outside comments, and no longer in the copy.
# Why: the first removal matched names inside comments too, such as GlobalDefinesAlt.xml's commented-out BASE_REVOLT_OCCUPATION_TURNS, and removed six that nothing redeclares, which would have dropped the base revolt duration from 2 turns to 0 and the power health penalties; Codex's review (GPT-6.2-Sol) found it, and a load test could not, as a missing define still loads. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: pathlib locates the files, argparse takes the repository root, re reads the header list, sys loads the shared helpers, and ElementTree parses declarations without comments. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default and namespace-free tag names, as the other XML checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root, local_name


CARRIED = Path("Assets/XML/GlobalDefines.xml")
LOADER = Path("CvGameCoreDLL/CvXMLLoadUtilitySet.cpp")
COUNT = re.compile(r"BtS's declarations of the (\d+) names below were removed")
ENTRY = re.compile(r"^([A-Z][A-Z0-9_-]*) = (.*?) in BtS, redeclared in ([A-Za-z_]+\.xml)(?:;|\.|$)")


def declared(path: Path) -> set[str]:
	root = ET.parse(path).getroot()
	return {node.text.strip() for node in root.iter() if local_name(node.tag) == "DefineName" and node.text and node.text.strip()}


# <!-- custom: The define files the DLL reads after GlobalDefines.xml, in SetGlobalDefines' order, so a redeclaration counts only in a file that loads later; the first version accepted any XML file, such as one the DLL never reads, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def later_files(repo_root: Path) -> list[str]:
	order = re.findall(r'ReadGlobalDefines\("xml\\\\(\w+\.xml)"', (repo_root / LOADER).read_text(encoding="latin-1"))
	if "GlobalDefines.xml" not in order:
		raise SystemExit(f"{LOADER}: no ReadGlobalDefines call for GlobalDefines.xml found")
	return order[order.index("GlobalDefines.xml") + 1:]


def check(repo_root: Path) -> tuple[list[str], int]:
	path = repo_root / CARRIED
	if not path.is_file():
		return [], 0
	text = path.read_text(encoding="utf-8")
	entries = [ENTRY.match(line.strip()) for line in text.splitlines()]
	entries = [match for match in entries if match]
	failures = []
	# <!-- custom: The header states how many names it lists, so a list emptied or cut short by an edit fails rather than passing with nothing to check (Codex's review, GPT-6.2-Sol). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	stated = COUNT.search(text)
	if stated is None or int(stated.group(1)) != len(entries) or not entries:
		failures.append(f"{CARRIED}: the header states {stated.group(1) if stated else 'no'} removed names but lists {len(entries)}")
	loaded_later = later_files(repo_root)
	in_copy = declared(path)
	cache: dict[str, set[str]] = {}
	for match in entries:
		name, file_name = match.group(1), match.group(3)
		if file_name not in loaded_later:
			failures.append(f"{CARRIED}: {name} is listed as redeclared in {file_name}, which the DLL does not load after GlobalDefines.xml")
			continue
		if file_name not in cache:
			other = repo_root / "Assets" / "XML" / file_name
			cache[file_name] = declared(other) if other.is_file() else set()
		if name not in cache[file_name]:
			failures.append(f"{CARRIED}: {name} is listed as redeclared in {file_name}, which does not declare it outside comments; restore BtS's declaration")
		if name in in_copy:
			failures.append(f"{CARRIED}: {name} is listed as removed but is still declared in the copy")
	return failures, len(entries)


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that each name the carried BtS GlobalDefines.xml lists as redeclared is declared in the named file.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()
	failures, count = check(args.repo_root)
	if failures:
		print("FAIL carried GlobalDefines redeclarations")
		for failure in failures:
			print(f"  - {failure}")
		return 1
	print(f"PASS carried GlobalDefines redeclarations: {count} removed name(s), each declared in the file listed")
	return 0


if __name__ == "__main__":
	sys.exit(main())

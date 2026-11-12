#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Resolve repository/shared-helper paths from this subject subfolder after the workflow-tool reorganization. (GPT-6.1-Sol) -->
#
# <!-- custom: Removed or renamed technologies, assets, and UI features can leave apparently valid TXT_KEY entries behind, while renamed SAS assets can reference pedia keys that were never defined.
# Audit every SAS-owned GameText file and SAS-owned asset description while explicitly accounting for inherited/EXE references and BUG's dynamically constructed key families; inherited AdvCiv/BUG/BULL files have too much unused-key static-analysis noise for a reliable blocking test and remain covered by the broader manual audit. (GPT-5.6-Sol) -->

from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET

# <!-- custom: The inherited-text hash manifest lists every GameText tag that BtS/vanilla/base AdvCiv define, which the GitHub mod-only checkout otherwise cannot see. (Claude code Opus 5.5) -->
from xml_sas_text_inherited import MANIFEST, read_manifest


TARGET_GLOB = "Assets/XML/Text/AdvCiv-SAS*.xml"
ALL_TEXT_GLOB = "Assets/XML/Text/*.xml"
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
	"TXT_KEY_MENU_SEALEVEL",
}
EXE_RUNTIME_REFERENCE_KEYS = {
	# No static mod/base/vanilla reference, but changing the High label changed its Custom Game list text in-game; Low uses the matching EXE convention.
	"TXT_KEY_SEALEVEL_HIGH_RECOMMEND",
	"TXT_KEY_SEALEVEL_LOW_RECOMMEND",
	# <!-- custom: The EXE builds the setup screens' titles from these keys, "Select a " plus the option's name, with no reference in any XML, Python or DLL file; dropping the prefix changed the titles in game on 2026-11-12. See KI#1083. (Claude code Opus 5.5) -->
	"TXT_KEY_MAIN_MENU_SELECT_A",
	"TXT_KEY_MAIN_MENU_SELECT_A_CIV",
	"TXT_KEY_MAIN_MENU_SELECT_A_CLIMATE",
	"TXT_KEY_MAIN_MENU_SELECT_A_DIFFICULTY",
	"TXT_KEY_MAIN_MENU_SELECT_A_MAP",
	"TXT_KEY_MAIN_MENU_SELECT_A_SCENARIO",
	"TXT_KEY_MAIN_MENU_SELECT_A_SEALEVEL",
}
INHERITED_PEDIA_REFERENCE_KEYS = {
	# <!-- custom: These descriptions are overridden by SAS, but their Civilopedia text remains inherited from the base game or expansion.
	# The GitHub checkout contains the mod only, so keep the confirmed inherited references explicit. (GPT-5.6-Sol) -->
	"TXT_KEY_BUILDING_EGYPTIAN_OBELISK_PEDIA",
	"TXT_KEY_CIV_AMERICA_PEDIA",
	"TXT_KEY_LEADER_ALEXANDER_PEDIA",
	"TXT_KEY_LEADER_ISABELLA_PEDIA",
	"TXT_KEY_LEADER_JUSTINIAN_PEDIA",
	"TXT_KEY_LEADER_PACAL_PEDIA",
	"TXT_KEY_LEADER_SURYAVARMAN_PEDIA",
}
# <!-- custom: This check covered only TXT_KEY names, so a diplomacy response key that no loaded text defines would pass; the KI#149 _CORRECTED key, defined only in Warlords text, showed how easily such keys get lost.
# Every key CIV4DiplomacyInfos uses must exist in mod GameText or in the inherited-text manifest (base AdvCiv, BtS, Warlords, vanilla), whatever its prefix. See KI#149. (Claude code Opus 5.5) -->
DIPLOMACY_INFOS = "Assets/XML/GameInfo/CIV4DiplomacyInfos.xml"
DIPLOMACY_TEXT_RE = re.compile(r"<Text>\s*([A-Z0-9_]+)\s*</Text>")
ANY_TAG_DEF_RE = re.compile(r"<Tag>\s*([A-Za-z0-9_]+)\s*</Tag>")
PEDIA_INFO_SPECS = (
	("Assets/XML/Buildings/CIV4BuildingInfos.xml", "BuildingInfo"),
	("Assets/XML/Units/CIV4UnitInfos.xml", "UnitInfo"),
	("Assets/XML/Civilizations/CIV4CivilizationInfos.xml", "CivilizationInfo"),
	("Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml", "LeaderHeadInfo"),
)


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


def child_text(node: ET.Element, tag_name: str) -> str:
	for child in node:
		if child.tag.rsplit("}", 1)[-1] == tag_name:
			return (child.text or "").strip()
	return ""


def collect_missing_sas_pedia_references(repo_root: Path, sas_definitions: set[str], all_mod_definitions: set[str]) -> tuple[list[str], list[str]]:
	missing: list[str] = []
	inherited: set[str] = set()
	for rel_path, info_tag in PEDIA_INFO_SPECS:
		path = repo_root / rel_path
		if not path.is_file():
			raise RuntimeError(f"missing file: {path}")
		for node in ET.parse(path).getroot().iter():
			if node.tag.rsplit("}", 1)[-1] != info_tag:
				continue
			description = child_text(node, "Description")
			if description not in sas_definitions:
				continue
			pedia = child_text(node, "Civilopedia")
			if pedia in all_mod_definitions:
				continue
			if pedia in INHERITED_PEDIA_REFERENCE_KEYS:
				inherited.add(pedia)
				continue
			info_type = child_text(node, "Type") or "UNKNOWN_INFO"
			missing.append(f"{info_type}: Civilopedia references {pedia or 'an empty key'}, but no matching mod GameText <Tag> exists")
	return sorted(missing), sorted(inherited)


def collect_missing_diplomacy_text(repo_root: Path) -> list[str]:
	defined = set(read_manifest(MANIFEST))
	for path in repo_root.glob(ALL_TEXT_GLOB):
		for block in TEXT_BLOCK_RE.findall(XML_COMMENT_RE.sub("", read_text(path))):
			defined.update(ANY_TAG_DEF_RE.findall(block))
	text = XML_COMMENT_RE.sub("", read_text(repo_root / DIPLOMACY_INFOS))
	return sorted(set(DIPLOMACY_TEXT_RE.findall(text)) - defined)


# <!-- custom: Accepted inherited keys go stale when SAS stops defining the key (for example after moving identical text back to base AdvCiv on 2026-11-04); fail so the lists stay a record of real exceptions. (Claude code Opus 5.5) -->
def collect_stale_accepted_keys(definitions: set[str], inherited_pedia: list[str]) -> list[str]:
	stale = sorted((INHERITED_REFERENCE_KEYS | EXE_RUNTIME_REFERENCE_KEYS) - definitions)
	stale += sorted(INHERITED_PEDIA_REFERENCE_KEYS - set(inherited_pedia))
	return stale


def check_sas_text_references(repo_root: Path) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], int, int]:
	targets = sorted(path for path in repo_root.glob(TARGET_GLOB) if path.is_file())
	if not targets:
		raise RuntimeError(f"no files match {TARGET_GLOB}")
	definitions = collect_definitions(targets)
	if not definitions:
		raise RuntimeError(f"no TXT_KEY definitions found in {TARGET_GLOB}")
	all_mod_definitions = collect_definitions(sorted(path for path in repo_root.glob(ALL_TEXT_GLOB) if path.is_file()))
	references = collect_references(repo_root)
	inherited = sorted(definitions & INHERITED_REFERENCE_KEYS)
	exe_runtime = sorted(definitions & EXE_RUNTIME_REFERENCE_KEYS)
	dynamic = sorted(key for key in definitions if key not in references and key.startswith(DYNAMIC_PREFIXES))
	unused = sorted(key for key in definitions if key not in references and key not in INHERITED_REFERENCE_KEYS and key not in EXE_RUNTIME_REFERENCE_KEYS and not key.startswith(DYNAMIC_PREFIXES))
	missing_pedia, inherited_pedia = collect_missing_sas_pedia_references(repo_root, definitions, all_mod_definitions)
	missing_pedia += [f"{DIPLOMACY_INFOS} references {key}, but neither mod GameText nor the inherited base AdvCiv/BtS/Warlords/vanilla text defines it" for key in collect_missing_diplomacy_text(repo_root)]
	missing_pedia += [f"{key}: listed as an accepted inherited reference, but no longer needed; remove it from the list" for key in collect_stale_accepted_keys(definitions, inherited_pedia)]
	return unused, missing_pedia, inherited, inherited_pedia, exe_runtime, dynamic, len(definitions), len(targets)


def print_keys(title: str, keys: list[str]) -> None:
	print(f"{title} ({len(keys)}):")
	for key in keys:
		print(f"  - {key}")


def main() -> int:
	parser = argparse.ArgumentParser(description="Reject unused SAS-owned TXT_KEY entries and missing SAS-owned Civilopedia references.")
	parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4], help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	try:
		unused, missing_pedia, inherited, inherited_pedia, exe_runtime, dynamic, definition_count, file_count = check_sas_text_references(args.repo_root)
	except RuntimeError as exc:
		print("FAIL SAS GameText references")
		print(f"  - {exc}")
		return 1

	if unused or missing_pedia:
		print("FAIL SAS GameText references")
		for key in unused:
			print(f"  - {key}: defined in {TARGET_GLOB} but not referenced by active mod XML/Config/Python/PrivateMaps/C++")
		for failure in missing_pedia:
			print(f"  - {failure}")
		return 1

	print(f"PASS SAS GameText references ({definition_count} referenced or explicitly accepted keys across {file_count} files)")
	print_keys("Confirmed inherited base references absent from the GitHub mod-only checkout", inherited)
	print_keys("Confirmed inherited Civilopedia references for SAS-overridden descriptions", inherited_pedia)
	print_keys("Empirically confirmed EXE runtime references with no static mod/base/vanilla reference", exe_runtime)
	print_keys("Recognized dynamically constructed BUG keys", dynamic)
	return 0


if __name__ == "__main__":
	sys.exit(main())

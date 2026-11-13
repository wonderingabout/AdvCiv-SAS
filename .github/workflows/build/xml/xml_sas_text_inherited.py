#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: AdvCiv-SAS GameText XML files hold only text that SAS changed.
# An entry whose English is identical to the inherited text (base AdvCiv, else BtS, else Warlords, else vanilla) is no longer an SAS change.

# <!-- custom: argparse/pathlib/sys drive the CLI and shared-helper path; glob, hashlib and re read GameText entries and hash their English; html decodes entities in stored names; subprocess reads the base AdvCiv snapshot from Git in --write mode only. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import glob
import hashlib
import html
import re
import subprocess
import sys

# <!-- custom: Shared repo-root resolution, as in the sibling XML checks. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


# <!-- custom: The 2026-11-04 cleanup found 25 SAS text entries identical to inherited text, for example TXT_KEY_LEADER_TOKUGAWA (lengthened, then shortened back to AdvCiv's "Tokugawa") and TXT_KEY_TECH_SAILING_QUOTE (back to the vanilla quote after tech remaps).
# GitHub has no BtS/Warlords/vanilla text files, so --write stores one hash per inherited tag from a local Civ4 install; BtS, Warlords and vanilla never change, and the base AdvCiv 1.12 snapshot is a fixed commit. (Claude code Opus 5.5) -->
BASE_ADVCIV_COMMIT = "0d81edb6443827986a2d620a5bf7b4faaaaafe46"
TEXT_DIR = "Assets/XML/Text"
SAS_TEXT_GLOB = "AdvCiv-SAS*.xml"
MANIFEST = Path(__file__).with_name("xml_sas_text_inherited_hashes.tsv")
# <!-- custom: Hashes cannot be read or sorted, so checks that need inherited English (xml_display_order.py) get readable names, limited to the keys they use. (Claude code Opus 5.5) -->
NAMES = Path(__file__).with_name("xml_sas_text_inherited_names.tsv")
NAME_KEY_SOURCES = (("Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml", ("Description",)), ("Assets/XML/Civilizations/CIV4CivilizationInfos.xml", ("Description", "ShortDescription")))
# <!-- custom: The first draft left Warlords out, assuming BtS does not load it.
# It then kept TXT_KEY_CONCEPT_IRRIGATION (Warlords-only) as SAS text, and the AI_DIPLO_DEMAND_TRIBUTE_POWER_STRONGER_MONTEZUMA_1_CORRECTED line that the leader ID restore had deleted was wrongly restored as missing.
# But the game does load Warlords text: neither SAS nor base AdvCiv defines TXT_KEY_CIV_KOREA_DESC, which exists only there, yet Korea shows its name in game, and BtS's own CIV4DiplomacyInfos uses Warlords-only diplomacy keys.
# With Warlords included, both entries proved identical to inherited text and were deleted again. See KI#149. (Claude code Opus 5.5) -->
GAME_LAYERS = (("bts", "Beyond the Sword/Assets/XML/Text"), ("warlords", "Warlords/Assets/XML/Text"), ("vanilla", "Assets/XML/Text"))

TEXT_RE = re.compile(rb"<TEXT\b[^>]*>(.*?)</TEXT>", re.S)
TAG_RE = re.compile(rb"<Tag>\s*([^<\s]+)\s*</Tag>")
ENGLISH_RE = re.compile(rb"<English>(.*?)</English>", re.S)
ENCODING_RE = re.compile(rb"<\?xml[^>]*encoding=[\"']([^\"']+)[\"']")


def decode(data: bytes, raw: bytes) -> str:
	match = ENCODING_RE.search(data[:200])
	encoding = match.group(1).decode("ascii") if match else "utf-8"
	try:
		return raw.decode(encoding)
	except (UnicodeDecodeError, LookupError):
		return raw.decode("cp1252", errors="replace")


# <!-- custom: Strict comparison: only CRLF/LF differs, because Git checkouts may change line endings; a fixed hyphen, quote mark or spacing keeps the entry an SAS change. (Claude code Opus 5.5) -->
def english_hash(text: str) -> str:
	return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()[:16]


def text_entries(data: bytes):
	for match in TEXT_RE.finditer(data):
		tag = TAG_RE.search(match.group(1))
		english = ENGLISH_RE.search(match.group(1))
		if tag and english:
			yield tag.group(1).decode("ascii", errors="replace"), decode(data, english.group(1)), data.count(b"\n", 0, match.start()) + 1


# <!-- custom: Leader and civilization names nest the shown text in <Text> beside <Gender>/<Plural>. (Claude code Opus 5.5) -->
def display_text(english: str) -> str:
	nested = re.search(r"<Text>(.*?)</Text>", english, re.S)
	return html.unescape(nested.group(1) if nested else english).strip()


def name_keys(repo_root: Path) -> set[str]:
	keys = set()
	for rel_path, fields in NAME_KEY_SOURCES:
		data = (repo_root / rel_path).read_text(encoding="utf-8", errors="replace")
		for field in fields:
			keys.update(re.findall("<" + field + r">\s*(TXT_KEY_\w+)\s*</" + field + ">", data))
	return keys


# <!-- custom: The lists began with "#" provenance lines, which Rainbow CSV's CSVLint in VS Code reported as rows with the wrong column count.
# They are now plain TSV with one header row, so table tools read them cleanly; the provenance lives in this script and the workflows README. (Claude code Opus 5.5) -->
NAMES_HEADER = "tag\tsource\tname"
# <!-- custom: "game" is the first BtS, Warlords or vanilla layer defining the tag, or "-". "source" names base AdvCiv first, but SAS loads its own text files, not base AdvCiv's originals, so a tag listed as "advciv" may be defined nowhere the game reads.
# Codex's review of KI#1085's check found that it counted such tags as defined; checks asking what the game can show use game_defined_tags instead. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
MANIFEST_HEADER = "tag\tsource\tsha256\tgame"


def read_rows(path: Path, header: str) -> list[list[str]]:
	lines = path.read_text(encoding="utf-8").splitlines()
	if not lines or lines[0] != header:
		raise SystemExit(f"{path}: first line must be the header {header!r}; regenerate with --write")
	return [line.split("\t") for line in lines[1:] if line]


def read_names(path: Path) -> dict[str, str]:
	return {tag: name for tag, _source, name in read_rows(path, NAMES_HEADER)}


def read_manifest(path: Path) -> dict[str, tuple[str, str]]:
	return {tag: (source, digest) for tag, source, digest, _game in read_rows(path, MANIFEST_HEADER)}


def game_defined_tags(path: Path) -> set[str]:
	return {tag for tag, _source, _digest, game in read_rows(path, MANIFEST_HEADER) if game != "-"}


def write_manifest(repo_root: Path, civ4_root: Path) -> int:
	inherited: dict[str, tuple[str, str]] = {}
	game: dict[str, str] = {}
	names: dict[str, tuple[str, str]] = {}
	wanted = name_keys(repo_root)
	listing = subprocess.run(["git", "-C", str(repo_root), "ls-tree", "--name-only", BASE_ADVCIV_COMMIT, TEXT_DIR + "/"], capture_output=True, text=True, check=True).stdout.split("\n")
	for name in sorted(path for path in listing if path.lower().endswith(".xml")):
		data = subprocess.run(["git", "-C", str(repo_root), "show", BASE_ADVCIV_COMMIT + ":" + name], capture_output=True, check=True).stdout
		for tag, english, _line in text_entries(data):
			inherited.setdefault(tag, ("advciv", english_hash(english)))
			if tag in wanted:
				names.setdefault(tag, ("advciv", display_text(english)))
	for source, folder in GAME_LAYERS:
		files = sorted(glob.glob(str(civ4_root / folder / "*.xml")))
		if not files:
			raise SystemExit(f"no text files under {civ4_root / folder}; pass the Civ4 install root with --civ4-root")
		for path in files:
			for tag, english, _line in text_entries(Path(path).read_bytes()):
				inherited.setdefault(tag, (source, english_hash(english)))
				game.setdefault(tag, source)
				if tag in wanted:
					names.setdefault(tag, (source, display_text(english)))
	# <!-- custom: Hash list: inherited English per GameText tag (base AdvCiv, else BtS, else Warlords, else vanilla), first 16 hex digits of SHA-256.
	# Names list: readable English for the leader/civilization keys only. (Claude code Opus 5.5) -->
	lines = [MANIFEST_HEADER] + [f"{tag}\t{source}\t{digest}\t{game.get(tag, '-')}" for tag, (source, digest) in sorted(inherited.items())]
	MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
	print(f"wrote {len(inherited)} inherited text hashes to {MANIFEST}")
	lines = [NAMES_HEADER] + [f"{tag}\t{source}\t{name}" for tag, (source, name) in sorted(names.items())]
	NAMES.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
	print(f"wrote {len(names)} inherited names to {NAMES}")
	return 0


def check(repo_root: Path) -> list[str]:
	inherited = read_manifest(MANIFEST)
	failures = []
	for path in sorted((repo_root / TEXT_DIR).glob(SAS_TEXT_GLOB)):
		for tag, english, line in text_entries(path.read_bytes()):
			found = inherited.get(tag)
			if found is None or found[1] != english_hash(english):
				continue
			if found[0] == "advciv":
				action = "restore base AdvCiv's original block (with its comments and other languages) in its inherited text file"
			else:
				action = "delete the SAS entry so the " + {"bts": "BtS", "warlords": "Warlords", "vanilla": "vanilla"}[found[0]] + " text applies"
			failures.append(f"{path.relative_to(repo_root).as_posix()}:{line}: {tag} English is identical to the inherited {found[0]} text; {action}")
	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check that AdvCiv-SAS GameText entries still differ from the inherited English text.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	parser.add_argument("--write", action="store_true", help="regenerate the inherited-text hash manifest (local only: needs a Civ4 BtS install)")
	parser.add_argument("--civ4-root", type=Path, help="Civ4 install root containing Assets/ and Beyond the Sword/ (for --write)")
	args = parser.parse_args()
	if args.write:
		if args.civ4_root is None:
			parser.error("--write needs --civ4-root")
		return write_manifest(args.repo_root, args.civ4_root)
	failures = check(args.repo_root)
	if failures:
		print("FAIL SAS text differs from inherited text")
		for failure in failures:
			print("  - " + failure)
		return 1
	print("PASS SAS text differs from inherited text")
	return 0


if __name__ == "__main__":
	sys.exit(main())

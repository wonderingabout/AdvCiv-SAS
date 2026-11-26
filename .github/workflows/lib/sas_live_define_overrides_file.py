#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Shared reader of SASLiveDefineOverrides.txt for workflow checks.
#
# This module runs outside Civ4, through GitHub Actions or a local Python 3 command.

# <!-- custom: pathlib finds the game's own bridge, types builds its module and stubs the two engine modules it imports, sys holds the stubs while it runs. See KI#128.5. (Claude code Opus 5.5) -->
from pathlib import Path
# <!-- custom: re checks the NoEntry file's lines. (Claude code Opus 5.5) -->
import re
# <!-- custom: subprocess reads the index for RepoSource's staged mode. (Claude code Opus 5.5) -->
import subprocess
import sys
import types


VALUES_RELATIVE = "SASLiveDefineOverrides/SASLiveDefineOverrides.txt"
NO_ENTRY_RELATIVE = "SASLiveDefineOverrides/SASLiveDefineOverridesNoEntry.txt"
ALLOWED_RELATIVE = "SASLiveDefineOverrides/SASLiveDefineOverridesAllowed.txt"
BRIDGE_RELATIVE = "Assets/Python/SASLiveDefineOverridesBridge.py"
XML_RELATIVE = "Assets/XML/GlobalDefines_advciv_sas.xml"


class RepoSource:
	# <!-- custom: Reads the repository's files from the working tree, or with staged=True from the index, so a --staged check reads every file it uses from the commit being checked.
	# Codex's review (GPT-6.2-Sol, 2026-11-26) found the first --staged version read the values and the XML from the index but NoEntry, the bridge and the scanned readers from disk, so a staged forbidden line passed once its NoEntry line was removed unstaged, and an unstaged policy change could reject a clean index. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def __init__(self, repo_root: Path, staged: bool = False):
		self.repo_root = repo_root
		self.staged = staged
		self._oids = None
		self._blobs = {}

	def _index(self) -> dict[str, str]:
		# <!-- custom: The index's regular files as path -> blob id, listed once; contents are fetched only for the files a check reads.
		# A first version fetched every blob, art, music and logs included: Codex's review (GPT-6.2-Sol) measured 3,507 entries and 555 MiB for one check of a few hundred text files. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if self._oids is None:
			listing = subprocess.run(["git", "ls-files", "-s", "-z"], cwd=self.repo_root, capture_output=True, check=True).stdout.decode("utf-8")
			oids = {}
			for entry in listing.split("\0"):
				if entry:
					meta, path = entry.split("\t", 1)
					mode, oid = meta.split()[:2]
					# <!-- custom: Regular files only: a gitlink (mode 160000) names a commit, which has no blob to read. (Claude code Opus 5.5) -->
					if mode.startswith("100"):
						oids[path] = oid
			self._oids = oids
		return self._oids

	def _fetch(self, paths: list[str]) -> None:
		# <!-- custom: One git cat-file --batch call for the paths not yet read; each frame's header is checked, as a missing object or another type has no blob body. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		wanted = [path for path in paths if path not in self._blobs]
		if not wanted:
			return
		oids = self._index()
		batch = subprocess.run(["git", "cat-file", "--batch"], cwd=self.repo_root, input="".join(oids[path] + "\n" for path in wanted).encode(), capture_output=True, check=True).stdout
		offset = 0
		for path in wanted:
			header_end = batch.index(b"\n", offset)
			header = batch[offset:header_end].split()
			if len(header) != 3 or header[1] != b"blob":
				raise RuntimeError(f"cannot read staged {path}: git cat-file answered {b' '.join(header).decode('utf-8', 'replace')!r}")
			size = int(header[2])
			self._blobs[path] = batch[header_end + 1:header_end + 1 + size]
			offset = header_end + 1 + size + 1

	def exists(self, relative: str) -> bool:
		if self.staged:
			return relative in self._index()
		return (self.repo_root / relative).is_file()

	def read(self, relative: str, encoding: str = "utf-8") -> str:
		if self.staged:
			if relative not in self._index():
				raise FileNotFoundError(f"{relative} is not in the index")
			self._fetch([relative])
			return self._blobs[relative].decode(encoding, "replace")
		return (self.repo_root / relative).read_text(encoding=encoding, errors="replace")

	def files(self, top: str, suffixes: tuple[str, ...], recursive: bool = True) -> list[str]:
		# <!-- custom: The relative paths under top with one of the suffixes, sorted; recursive=False keeps only top's own files. (Claude code Opus 5.5) -->
		prefix = top.rstrip("/") + "/"
		if self.staged:
			found = [path for path in self._index() if path.startswith(prefix) and (recursive or "/" not in path[len(prefix):])]
		else:
			root = self.repo_root / top
			walk = root.rglob("*") if recursive else root.iterdir()
			found = [path.relative_to(self.repo_root).as_posix() for path in walk if path.is_file()]
		found = sorted(path for path in found if path.lower().endswith(suffixes))
		if self.staged:
			self._fetch(found)
		return found


DEFINE_VALUES_RELATIVE = "LLM_Helpers/diagnostics/define_values.py"


def development_values(source: RepoSource) -> dict[str, int]:
	# <!-- custom: The values toggle_dev_diagnostics.py switches in the XML, read from the same source as the files checked: Codex's review (GPT-6.2-Sol) found --staged imported them from disk, so an unstaged edit of define_values.py could decide whether a staged line passed.
	# The file is plain data, so its text is run in an empty namespace. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	namespace = {}
	exec(compile(source.read(DEFINE_VALUES_RELATIVE), DEFINE_VALUES_RELATIVE, "exec"), namespace)
	return namespace["DEVELOPMENT_VALUES"]


def read_no_entry(repo_root: Path, text: str | None = None, source: RepoSource | None = None) -> list[tuple[str, str]]:
	# <!-- custom: The defines no override may name, as (name, reason) pairs from SASLiveDefineOverridesNoEntry.txt, beside the overrides so whoever opens the folder sees them; the user proposed that file on 2026-11-25, after the rules first sat in CI code.
	# Each line names one define in full: patterns such as SAS_EXE_P_* were allowed at first, but a grep for a define then missed its line, so the user asked on 2026-11-26 for full names, and a "*" is now rejected.
	# Raises ValueError on a line that is not "NAME: reason".
	# text overrides the file, for tests. See KI#128.5. (Claude code Opus 5.5) -->
	return read_named_reasons(repo_root, NO_ENTRY_RELATIVE, text, source)


def read_allowed(repo_root: Path, text: str | None = None, source: RepoSource | None = None) -> list[tuple[str, str]]:
	# <!-- custom: The defines the mod supports live, as (name, reason) pairs from SASLiveDefineOverridesAllowed.txt, in NoEntry's form. See KI#128.7. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return read_named_reasons(repo_root, ALLOWED_RELATIVE, text, source)


def read_named_reasons(repo_root: Path, relative: str, text: str | None = None, source: RepoSource | None = None) -> list[tuple[str, str]]:
	if text is None:
		text = (source or RepoSource(repo_root)).read(relative)
	rules = []
	for number, line in enumerate(text.splitlines(), 1):
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		name, colon, reason = line.partition(":")
		if not colon or not re.fullmatch(r"[A-Z0-9_]+", name.strip()) or not reason.strip():
			raise ValueError(f"{relative} line {number}: expected NAME: reason, one define named in full, got {line!r}")
		rules.append((name.strip(), reason.strip()))
	return rules


def load_bridge(repo_root: Path, source: RepoSource | None = None):
	# <!-- custom: Loads Assets/Python/SASLiveDefineOverridesBridge.py itself, with stand-ins for CvPythonExtensions and SASPythonLogging, so CI parses the file with the game's own parser rather than a copy that could drift from it.
	# The bridge keeps to syntax both Civ4's Python 2.4 and Python 3 accept for this. See KI#128.5. (Claude code Opus 5.5) -->
	saved = {name: sys.modules.get(name) for name in ("CvPythonExtensions", "SASPythonLogging")}
	engine = types.ModuleType("CvPythonExtensions")
	engine.CyGlobalContext = None
	engine.CyInterface = None
	logging = types.ModuleType("SASPythonLogging")
	logging.writeRecord = lambda record, fields="": None
	sys.modules["CvPythonExtensions"] = engine
	sys.modules["SASPythonLogging"] = logging
	try:
		# <!-- custom: Compiled from its text in memory: spec_from_file_location's loader wrote a .pyc into Assets/Python/__pycache__, as Codex's review (GPT-6.2-Sol) reproduced, so CI wrote into the game's folder. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		path = repo_root / BRIDGE_RELATIVE
		module = types.ModuleType("SASLiveDefineOverridesBridge_ci")
		module.__file__ = str(path)
		exec(compile((source or RepoSource(repo_root)).read(BRIDGE_RELATIVE), str(path), "exec"), module.__dict__)
	finally:
		for name, previous in saved.items():
			if previous is None:
				sys.modules.pop(name, None)
			else:
				sys.modules[name] = previous
	return module


def xml_values(repo_root: Path, text: str | None = None, source: RepoSource | None = None) -> dict[str, tuple[str, object]]:
	# <!-- custom: The SAS defines of GlobalDefines_advciv_sas.xml as name -> (kind, value), read with the bridge's own parser, so CI and the game agree on which names may be overridden and with which type.
	# text overrides the file, for tests. (Claude code Opus 5.5) -->
	if text is None:
		text = (source or RepoSource(repo_root)).read(XML_RELATIVE)
	return load_bridge(repo_root, source)._parseXml(text)


def read_values(repo_root: Path, text: str | None = None, xml_text: str | None = None, source: RepoSource | None = None) -> dict[str, object]:
	# <!-- custom: Raises ValueError, as the game rejects the file, for a line it rejects.
	# text and xml_text override the files, for tests or staged content. (Claude code Opus 5.5) -->
	if text is None:
		text = (source or RepoSource(repo_root)).read(VALUES_RELATIVE)
	return load_bridge(repo_root, source)._parse(text, xml_values(repo_root, xml_text, source))

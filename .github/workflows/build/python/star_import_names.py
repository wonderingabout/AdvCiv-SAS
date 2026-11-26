#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: An undefined name in a Civ4 Python file stays dormant until its line runs: PyHelpers' getUnlockedReligionIdxList appended to religionList after creating religionlist, a NameError on any call, from vanilla to SAS until 2026-11-22. See KI#165.2.
# Ruff misses such names in files with "from CvPythonExtensions import *": it cannot know what the star import provides, so it reports F405 "may be undefined" instead of F821, and the Ruff gate ignores F405, as nearly every Civ4 name arrives that way.
# So this resolves each F405 name the way Python would: names the file's star-imported repository modules define, recursively, Python 2 built-ins, class names in the BUG Python API reference, DLL registrations and verified EXE or DLL names; any other name fails. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse reads the CLI, json Ruff's report, pathlib the files and re the definitions; io and tokenize find Python 2 "except X, name:" bindings. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import argparse
import io
import json
from pathlib import Path
import re
# <!-- custom: subprocess runs Ruff, and sys gives its module fallback and the exit code. (Claude code Opus 5.5) -->
import subprocess
import sys
import tokenize

ROOT = Path(__file__).resolve().parents[4]
SCANNED = ("Assets/Python", "PrivateMaps")
API_REFERENCE = "_0_Legacy/Docs/Civ4BUG_Python_API/all_classes_web.txt"
# <!-- custom: Python 2 built-ins Python 3's Ruff does not know.
# A free self still needs a real receiver. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
PYTHON2_BUILTINS = frozenset(("apply", "basestring", "buffer", "cmp", "coerce", "execfile", "file", "intern", "long", "raw_input", "reduce", "unichr", "unicode", "xrange"))
# <!-- custom: CvPythonExtensions names the BUG Python API reference lacks, each checked to exist in the engine; add one here only after checking it, as a typo added here would hide the next religionList. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
ENGINE_NAMES = frozenset((
	"AreaBorderLayers", "CivilopediaPageTypes", "CommandTypes", "ControlTypes",
	"DiplomacyPowerTypes", "FeatTypes", "FontSymbols", "GameOptionTypes",
	"GameStateTypes", "GlobeLayerTypes", "GraphicOptionTypes", "HitTestTypes",
	"InfoBarTypes", "InputTypes", "MissionAITypes", "MissionTypes",
	"MouseFlags", "MultiplayerOptionTypes", "NiTextOut", "NotifyCode",
	"PlotLandscapeLayers", "PlotStyles", "PollutionTypes", "ReplayMessageTypes",
	"SASAutoPlayEndCause", "TaskTypes", "TradeableItems", "WorldBuilderPopupTypes",
	"addWBAdvancedStartControlTabs", "addWBPlayerControlTabs", "cyIntRange", "cyUpdatePlotIndicatorSize",
	"destroyWBDiplomacyCtrl", "getASBuilding", "getASImprovement", "getASRoute",
	"getASUnit", "getAlarmHourLeft", "getAlarmMinLeft", "getChtLvl",
	"getClockText", "getEspionageModifier", "getWBSaveExtension", "getWBToolAdvancedStartTabCtrl",
	"getWBToolDiplomacyTabCtrl", "getWBToolEditTabCtrl", "getWBToolNormalMapTabCtrl", "getWBToolNormalPlayerTabCtrl",
	"initWBDiplomacyCtrl", "initWBToolAdvancedStartControl", "initWBToolEditCtrl", "initWBToolEditCtrlTab",
	"initWBToolPlayerControl", "isAlarmOn", "isLimitedUnitClass", "isLimitedWonderClass",
	"isMouseOverGameSurface", "isNationalWonderClass", "isTeamProject", "isTeamWonderClass",
	"isTechRequiredForBuilding", "isTechRequiredForProject", "isTechRequiredForUnit", "isWorldProject",
	"isWorldWonderClass", "plotCity", "plotDirection", "plotDistance",
	"plotXY", "refreshWBEditCtrlCorporationButtons", "refreshWBEditCtrlReligionButtons", "saveDiplomacySettings",
	"setDiplomacySettings", "setFocusToCVG", "setNoIntroMovie", "setWBInitialCtrlTabPlacement",
	"shuffleList", "toggleAlarm",
	# <!-- custom: CyPitboss, the Pitboss server's Python class, is defined by Civ4BeyondSword_PitBoss.exe, which holds the name 74 times; PbAdmin.py and PbWizard.py, carried on 2026-11-26, use it. See KI#1104. (Claude code Opus 5.5) -->
	"CyPitboss",
))
# <!-- custom: The BUG reference documents class headings and method signatures.
# Only headings can supply a module-level name.
# The DLL registrations supply enums and other exported names that may appear only in the reference's signatures. (GPT-6.2-Sol) -->
API_CLASS = re.compile(r"^(?:class )?([A-Z][A-Za-z_0-9]+)(?: - not in SDK)?[ 	]*$", re.M)
DLL_EXPORT = re.compile(r'python::(?:def|(?:class_|enum_)<[^>]+>(?:\s+\w+)?)\s*\(\s*"([A-Za-z_]\w*)"')
LEGACY_EXCEPT = re.compile(r"^([ \t]*)except[ \t]+(?:[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\([^:\r\n]+\))[ \t]*,[ \t]*([A-Za-z_]\w*)[ \t]*:")


def engine_exports(repo):
	reference = (repo / API_REFERENCE).read_text(encoding="utf-8", errors="replace")
	names = set(API_CLASS.findall(reference)) | ENGINE_NAMES | {"true", "false"}
	dll = repo / "CvGameCoreDLL"
	for path in (*dll.glob("Cy*.cpp"), dll / "CvDLLPython.cpp"):
		if path.is_file():
			names.update(DLL_EXPORT.findall(path.read_text(encoding="utf-8", errors="replace")))
	return names


def legacy_exception_bindings(text):
	# <!-- custom: Civ4 still binds the target in except Error, name.
	# Ruff reads it as an undefined name.
	# Limit the exception to the binding and its handler suite, so an unrelated reference elsewhere can still fail. (GPT-6.2-Sol) -->
	lines = text.split("\n")
	bindings = {}
	try:
		tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
	except (tokenize.TokenError, IndentationError):
		return bindings
	for index, token in enumerate(tokens):
		if token.type != tokenize.NAME or token.string != "except":
			continue
		row, column = token.start
		match = LEGACY_EXCEPT.match(lines[row - 1])
		if not match or len(match.group(1)) != column:
			continue
		end = row
		index += 1
		while index < len(tokens) and tokens[index].type != tokenize.NEWLINE:
			end = tokens[index].end[0]
			index += 1
		index += 1
		while index < len(tokens) and tokens[index].type in (tokenize.COMMENT, tokenize.NL):
			index += 1
		if index < len(tokens) and tokens[index].type == tokenize.INDENT:
			depth = 1
			for item in tokens[index + 1:]:
				depth += (item.type == tokenize.INDENT) - (item.type == tokenize.DEDENT)
				if depth == 0:
					end = item.start[0] - 1
					break
		bindings.setdefault(match.group(2), []).append((row, end))
	return bindings


F405 = re.compile(r"`([^`]+)` may be undefined")
STAR = re.compile(r"^\s*from\s+([\w.]+)\s+import\s+\*", re.M)
TOP_LEVEL = re.compile(r"^(?:def|class)\s+([A-Za-z_]\w*)|^([A-Za-z_][\w,\s]*?)=(?!=)|^import\s+([\w.]+)(?:\s+as\s+(\w+))?|^from\s+[\w.]+\s+import\s+(?!\*)(.+)$|^from\s+([\w.]+)\s+import\s+\*", re.M)


class Resolver:
	# <!-- custom: Each repository module's top-level names, with those of the modules it star-imports in turn, as Python makes them available to a file that star-imports it. (Claude code Opus 5.5) -->
	def __init__(self, repo):
		self.modules = {}
		for base in SCANNED:
			for path in sorted((repo / base).rglob("*.py")):
				self.modules.setdefault(path.stem, path)
		self.cache = {"CvPythonExtensions": engine_exports(repo)}

	def exports(self, name, seen=()):
		if name in self.cache:
			return self.cache[name]
		if name not in self.modules or name in seen:
			return set()
		names = set()
		for match in TOP_LEVEL.finditer(self.modules[name].read_text(encoding="utf-8", errors="replace")):
			definition, assigned, imported, alias, imported_names, star = match.groups()
			if definition:
				names.add(definition)
			elif assigned:
				names.update(re.findall(r"[A-Za-z_]\w*", assigned))
			elif imported:
				names.add(alias or imported.split(".")[0])
			elif imported_names:
				names.update(re.findall(r"[A-Za-z_]\w*", imported_names.split("#")[0]))
			elif star:
				names |= self.exports(star, seen + (name,))
		self.cache[name] = names
		return names

	def provided(self, path):
		names = set()
		for star in STAR.findall(path.read_text(encoding="utf-8", errors="replace")):
			names |= self.exports(star)
		return names


def ruff_report(repo):
	command = ["check", *SCANNED, "--isolated", "--no-cache", "--config", "builtins = ['unicode']", "--select", "F405", "--output-format", "json", "--exit-zero"]
	for ruff in (["ruff"], [sys.executable, "-m", "ruff"]):
		try:
			return json.loads(subprocess.run(ruff + command, cwd=repo, capture_output=True, text=True, check=True).stdout)
		except (OSError, subprocess.CalledProcessError, ValueError):
			continue
	raise RuntimeError("cannot run Ruff; install it, as python-ruff.yml does")


def problems(repo, report):
	resolver = Resolver(repo)
	provided = {}
	legacy = {}
	found = []
	for entry in report:
		match = F405.search(entry.get("message", ""))
		if not match:
			continue
		name = match.group(1)
		path = Path(entry["filename"])
		path = path if path.is_absolute() else repo / path
		if path not in provided:
			provided[path] = resolver.provided(path)
			legacy[path] = legacy_exception_bindings(path.read_text(encoding="utf-8", errors="replace"))
		row = entry["location"]["row"]
		if name in provided[path] or name in PYTHON2_BUILTINS or any(start <= row <= end for start, end in legacy[path].get(name, ())):
			continue
		found.append("%s:%d: %s is defined by none of the file's star imports, Python 2 built-ins or legacy exception bindings" % (path.relative_to(repo).as_posix(), row, name))
	return sorted(found)


def main():
	parser = argparse.ArgumentParser(description="Fail on names hidden from Ruff by a star import that nothing defines, such as KI#165.2's religionList.")
	parser.add_argument("--repo-root", type=Path, default=ROOT)
	parser.add_argument("--ruff-json", type=Path, help="a saved Ruff F405 JSON report, instead of running Ruff")
	args = parser.parse_args()
	repo = args.repo_root.resolve()
	try:
		report = json.loads(args.ruff_json.read_text(encoding="utf-8")) if args.ruff_json else ruff_report(repo)
		found = problems(repo, report)
	except (RuntimeError, OSError, ValueError, KeyError) as exc:
		print("FAIL star-import names setup: %s" % exc)
		return 1
	for problem in found:
		print("FAIL " + problem)
	if found:
		print("FAIL star-import names (%d)" % len(found))
		return 1
	print("PASS star-import names")
	return 0


if __name__ == "__main__":
	sys.exit(main())

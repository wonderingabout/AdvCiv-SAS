#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Report-only audit: when each SAS define of GlobalDefines_advciv_sas.xml takes effect, from how its readers read it.
# Written on 2026-11-26 to decide which defines SASLiveDefineOverrides.txt may override and which belong in SASLiveDefineOverridesNoEntry.txt, rather than guessing per family.
# A reader that asks at each use follows an override; one that keeps the value, in a DLL static or member, a Python module variable, an __init__ attribute or a lazy cache, does not; one that runs only while loading or setting up takes effect at startup.
# Heuristic and text-based: a name built at runtime, such as "SAS_X_FONT_%d" % i, shows as unread, and a reader inside a helper called only at load shows as at use.
# Check each verdict before acting on it. See KI#128.5. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, collections groups readers, pathlib walks the folders, re finds names and functions, io and tokenize blank Python comments, sys reaches the CI comment blanker. (Claude code Opus 5.5) -->
import argparse
from collections import defaultdict
from pathlib import Path
import re
import io
# <!-- custom: sys puts the CI build and lib folders on the path for their comment blankers. (Claude code Opus 5.5) -->
import sys
import tokenize

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".github" / "workflows" / "build" / "source"))
sys.path.insert(0, str(REPO / ".github" / "workflows" / "lib"))
# <!-- custom: The C++ comment blanker the define-cache CI check uses, so a name in a comment is no reader. (Claude code Opus 5.5) -->
from cpp_define_reads_cached import blank_source

# <!-- custom: Inherited defines are audited too since 2026-11-26, as the user asked: the Python define inventory covers every define Python reads, SAS and inherited, and the C++ check already covered both (KI#128.4).
# The files and their order come from CvXMLLoadUtility::SetGlobalDefines, so the list cannot drift from what the DLL loads; each is read from the mod if it has a copy, else from BtS's Assets/XML, two folders up, and skipped when absent, as on a machine without the game.
# A define read only by the EXE, as some BtS ones are, shows as unread here. (Claude code Opus 5.5) -->
LOADER = REPO / "CvGameCoreDLL" / "CvXMLLoadUtilitySet.cpp"
BTS_XML = REPO.parents[1] / "Assets" / "XML"
# <!-- custom: A hyphen too, as AdvCiv's THRESH-BAD-FEAT-PER-CITY, which the DLL reads, has them; the first version skipped it and counted 1,447 defines instead of 1,448, as Codex's review (GPT-6.2-Sol) found. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
DEFINE = re.compile(r"<DefineName>\s*([A-Z][A-Z0-9_-]*)\s*</DefineName>\s*<(iDefineIntVal|fDefineFloatVal|DefineTextVal)>")
KINDS = {"iDefineIntVal": "int", "fDefineFloatVal": "float", "DefineTextVal": "string"}
NAME = r"[A-Z][A-Z0-9_]+"
# <!-- custom: A name read in quotes may hold a hyphen, as THRESH-BAD-FEAT-PER-CITY does, while an identifier such as CvGlobals::NAME cannot, so the quoted searches use their own pattern; with NAME alone, that define still showed as unread, as Codex's review (GPT-6.2-Sol) found. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
QUOTED_NAME = r"[A-Z][A-Z0-9_-]+"
# <!-- custom: Function names that run while loading XML, a save or a map, or setting up a session: a define read only there takes effect at startup. (Claude code Opus 5.5) -->
# <!-- custom: A word must end where the name's next word starts, so "readiness" is no "read": Codex's review (GPT-6.2-Sol) reproduced it counted as setup. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
LOAD_NAMES = re.compile(r"(^|_|::)([Ii]nit|[Cc]ache|[Ll]oad|[Rr]ead|[Ss]etGlobal|[Cc]onfigure|[Ss]etup|preGameStart|beforeGeneration|[Gg]enerate|addRivers|onGameLoad|onGameStart)(?=[A-Z_0-9]|$)|initialize|::Cv\w+$")
CPP_FUNCTION = re.compile(r"^[A-Za-z_][\w:<>,\s\*&~]*?\b([\w]+(?:::[~\w]+)?)\s*\([^;]*$")
PY_DEF = re.compile(r"^(\s*)def\s+(\w+)\s*\(")
PY_CLASS = re.compile(r"^(\s*)class\s+(\w+)")


def define_files():
	# <!-- custom: The GlobalDefines files in the DLL's load order, each with the path read, the mod's copy first. (Claude code Opus 5.5) -->
	order = re.findall(r'ReadGlobalDefines\("xml\\\\(\w+\.xml)"', LOADER.read_text(encoding="latin-1"))
	files = []
	for file_name in order:
		for folder in (REPO / "Assets" / "XML", BTS_XML):
			if (folder / file_name).is_file():
				files.append((file_name, folder / file_name))
				break
	return files


def read_defines(scope="all"):
	# <!-- custom: Each define as name -> (kind, origin), the origin being the first file of the load order to define it, so "SAS" for GlobalDefines_advciv_sas.xml's own and the file's name for an inherited one. (Claude code Opus 5.5) -->
	names = {}
	for file_name, path in define_files():
		text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8", errors="replace"), flags=re.S)
		for name, tag in DEFINE.findall(text):
			if name not in names:
				names[name] = (KINDS[tag], "SAS" if file_name == "GlobalDefines_advciv_sas.xml" else file_name)
	if scope == "sas":
		return {name: value for name, value in names.items() if value[1] == "SAS"}
	if scope == "inherited":
		return {name: value for name, value in names.items() if value[1] != "SAS"}
	return names


def cpp_line_kind(line, previous, function):
	# <!-- custom: How one C++ line uses a value: kept in a static, member or global, read in a load or setup function, or read at use. (Claude code Opus 5.5) -->
	# <!-- custom: previous holds the statement's earlier lines, so a static whose read is wrapped onto a later line is caught, which Codex's review (GPT-6.2-Sol) reproduced as at use. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: The third pattern takes an initializer brace, as in CvCityAI.cpp's static const int aiSASMinOffensiveProductionCapacityPercent[] = { ...
	# }, whose seven reads, one per line, the first version reported as read at use, so 21 production defines looked live; Codex's review (GPT-6.2-Sol) caught it on 2026-11-26. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if re.search(r"\bstatic\b", line) or re.search(r"\bstatic\b[^;{}]*$", previous) or re.search(r"\bstatic\b[^;{}]*=\s*\{[^;}]*$", previous):
		return "kept: static"
	if re.search(r"\b(?:g_|m_|s_)\w+\s*=", line) or re.search(r"\bg[A-Z]\w*\s*=(?!=)", line) or re.search(r"\bg[A-Z]\w*\[[^\]]*\]\s*=(?!=)", line):
		return "kept: member or global"
	if LOAD_NAMES.search(function):
		return "load or setup"
	return "at use"


def cpp_lines():
	# <!-- custom: Every C++ line with its file, number, enclosing function and the line before, comments blanked. (Claude code Opus 5.5) -->
	rows = []
	for path in sorted((REPO / "CvGameCoreDLL").iterdir()):
		if path.suffix.lower() not in (".cpp", ".h", ".inl"):
			continue
		lines = blank_source(path.read_text(encoding="latin-1"))[0].split("\n")
		function = "-"
		for number, line in enumerate(lines, 1):
			# <!-- custom: A closing brace at column 0 ends the function, so a table after it, such as BBAILog.cpp's aSASBBAILogCategories, is at file scope rather than inside the function before it, as the first run had it. (Claude code Opus 5.5) -->
			if line.startswith("}"):
				function = "-"
			elif line[:1].isalpha() and not line.rstrip().endswith(";") and "(" in line:
				match = CPP_FUNCTION.match(line)
				if match:
					function = match.group(1)
			statement = []
			back = number - 2
			while back >= 0 and len(statement) < 12 and not re.search(r"[;{}]\s*$", lines[back]):
				statement.insert(0, lines[back])
				back -= 1
			# <!-- custom: A line ending in an initializer's "= {" starts the same statement, so it is kept: the walk stopped there, and at six lines, so CvCityAI.cpp's seven-element static arrays of production defines read as at use (2026-11-26). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			if back >= 0 and len(statement) < 12 and re.search(r"=\s*\{\s*$", lines[back]):
				statement.insert(0, lines[back])
			rows.append((path.name, number, function, line, " ".join(statement)))
	return rows


def call_index(rows):
	# <!-- custom: Each called name with the lines that call it, built once: searching every line for each reader's callers took 85 seconds a run. (Claude code Opus 5.5) -->
	index = defaultdict(list)
	call = re.compile(r"\b(\w+)\s*\(")
	for row in rows:
		for match in call.finditer(row[3]):
			index[match.group(1)].append(row)
	return index


def cpp_readers(names, rows):
	readers = defaultdict(list)
	index = call_index(rows)
	pattern = re.compile(r"(?:\"(" + QUOTED_NAME + r")\"|CvGlobals::(" + NAME + r")|\bDO\((" + NAME + r")\))")
	for file_name, number, function, line, previous in rows:
		for match in pattern.finditer(line):
			name = match.group(1) or match.group(2) or match.group(3)
			if name not in names:
				continue
			if match.group(3):
				how = "enum list"
			elif function == "-" and "getDefine" not in line:
				how = "table: check by hand"
			elif function == "-":
				how = "scope unknown: check by hand"
			else:
				how = cpp_line_kind(line, previous, function)
				# <!-- custom: A read at use inside a helper, such as BBAILog's getClampedSASBBAILogLevel, is only as live as the helper's callers: when every call keeps the result or runs at load, so does the read.
				# The first run called BBAI's category levels ready, while BBAILog.cpp fills their globals once at load, as Codex's review (GPT-6.2-Sol) had found. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
				if how == "at use":
					short = function.split("::")[-1]
					calls = [cpp_line_kind(c_line, c_prev, c_function) for c_file, c_number, c_function, c_line, c_prev in index.get(short, []) if c_function != function]
					if calls and all(kind != "at use" for kind in calls):
						kinds = sorted(set(calls))
						how = kinds[0] if len(kinds) == 1 else "kept: " + ", ".join(kinds)
						how = how + " (through " + short + ")"
			readers[name].append(("C++", f"CvGameCoreDLL/{file_name}:{number}", function, how))
	return readers


def built_name_readers(names, readers, rows):
	# <!-- custom: A name built at runtime, such as "SAS_BILLBOARD_SCALE_PCT_FONT_%d" % i, has no literal reader; a literal prefix of an unread name, ending in "_", stands in for it, with the same classification. (Claude code Opus 5.5) -->
	unread = [name for name in names if not readers.get(name)]
	prefix_pattern = re.compile(r"[\"'](SAS_[A-Z0-9_]*_)[\"'%]")
	py_rows = []
	for top in ("Assets/Python", "PrivateMaps"):
		for path in sorted((REPO / top).rglob("*.py")):
			rel = path.relative_to(REPO).as_posix()
			for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
				if not line.strip().startswith("#"):
					py_rows.append((rel, number, line))
	for rel, number, line in py_rows:
		for match in prefix_pattern.finditer(line.split("#", 1)[0]):
			for name in unread:
				if name.startswith(match.group(1)):
					readers[name].append(("Python", f"{rel}:{number}", "-", "built name: check by hand"))
	for file_name, number, function, line, previous in rows:
		for match in prefix_pattern.finditer(line):
			for name in unread:
				if name.startswith(match.group(1)):
					readers[name].append(("C++", f"CvGameCoreDLL/{file_name}:{number}", function, "built name: " + cpp_line_kind(line, previous, function)))
	return readers


def python_readers(names, readers):
	pattern = re.compile(r"[\"'](" + QUOTED_NAME + r")[\"']")
	for top in ("Assets/Python", "PrivateMaps"):
		for path in sorted((REPO / top).rglob("*.py")):
			rel = path.relative_to(REPO).as_posix()
			source = path.read_text(encoding="utf-8", errors="replace")
			lines = source.split("\n")
			# <!-- custom: Comments are blanked by token position, so a "#" inside a string does not cut a read short, as splitting on "#" did; a file the tokenizer rejects keeps that split. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			blanked = list(lines)
			# <!-- custom: A line that starts inside open brackets continues a statement, so its indent says nothing about scope.
			# CvMapGeneratorUtil's __init__ signatures span several lines with AdvCiv's "# </advc.137>" among them; popping the def there labelled 14 reads in their bodies import-time. (Claude code Opus 5.5) -->
			continued = set()
			try:
				depth = 0
				seen = set()
				for token in tokenize.generate_tokens(io.StringIO(source).readline):
					if token.type == tokenize.COMMENT:
						row, col = token.start
						blanked[row - 1] = blanked[row - 1][:col]
					if token.start[0] not in seen:
						seen.add(token.start[0])
						if depth > 0:
							continued.add(token.start[0])
					if token.type == tokenize.OP:
						if token.string in "([{":
							depth += 1
						elif token.string in ")]}":
							depth -= 1
			except (tokenize.TokenError, IndentationError, SyntaxError):
				blanked = [line.split("#", 1)[0] for line in lines]
			stack = []
			for number, line in enumerate(lines, 1):
				stripped = line.strip()
				if not stripped or stripped.startswith("#"):
					continue
				def_line = False
				if number not in continued:
					indent = len(line) - len(line.lstrip())
					while stack and stack[-1][0] >= indent:
						stack.pop()
					head = PY_DEF.match(line)
					# <!-- custom: A read on a def's own line was skipped; it may be a default argument, run at import, or a one-line body, run at each call, so it is scanned and left to read by hand, as Codex's review (GPT-6.2-Sol) found. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
					if head:
						stack.append((len(head.group(1)), head.group(2), "def"))
						def_line = True
					head = PY_CLASS.match(line)
					if head:
						stack.append((len(head.group(1)), head.group(2), "class"))
						continue
				code = blanked[number - 1]
				for match in pattern.finditer(code):
					name = match.group(1)
					if name not in names:
						continue
					defs = [entry[1] for entry in stack if entry[2] == "def"]
					function = defs and defs[-1] or "<module>"
					before = "\n".join(lines[max(0, number - 4):number - 1])
					if "SASCurrentDefines." in code or "_DynamicFontTag(" in code or "_getSASUIFontSize(" in code:
						how = "at use: shared cache"
					# <!-- custom: A bare name kept in a constant, as SASDefineGuard's SAS_LAUNCH_GUARD_TEST_INT_DEFINE = "SAS_LAUNCH_GUARD_TEST_INT", reads nothing; the read is where the constant is used. (Claude code Opus 5.5) -->
					elif re.match(r"\s*\w+\s*=\s*[\"']\w+[\"']\s*$", code):
						continue
					elif def_line:
						how = "scope unknown: def line"
					elif not defs:
						how = "kept: import"
					elif function == "__init__":
						how = "kept: __init__"
					elif re.match(r"\s*self\.\w+\s*=", code):
						how = "kept: attribute"
					elif "is None" in before or re.match(r"\s*global\b", before.split("\n")[-1] if before else ""):
						how = "kept: lazy"
					elif rel.startswith("PrivateMaps") or LOAD_NAMES.search(function):
						how = "load or setup"
					else:
						how = "at use"
					readers[name].append(("Python", f"{rel}:{number}", function, how))
	return readers


def verdict(entries):
	if not entries:
		return "unread"
	hows = set(how for _, _, _, how in entries if how != "enum list")
	if not hows:
		return "unread"
	if any(how.startswith("built name") or how.startswith("table") or how.startswith("scope unknown") for how in hows):
		return "by hand"
	# <!-- custom: Was "ready": Codex's review (GPT-6.2-Sol) pointed out that a read fresh each time its function runs may sit in a function that runs only during setup, such as the main menu's music pool, so no cache detected is all this can say. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if hows <= {"at use", "at use: shared cache"}:
		return "no cache detected"
	if hows <= {"load or setup"}:
		return "startup"
	if any(how.startswith("kept") for how in hows):
		return "kept"
	return "mixed"


def family(name):
	parts = name.split("_")
	return "_".join(parts[:3]) if len(parts) > 3 else name


def reader_side(entries):
	# <!-- custom: Who reads a define in source: the DLL, Python, both, or none.
	# A define in AdvCiv's GlobalDefines enum list counts for the DLL, which caches it and reads it as GC.getDefineINT(CvGlobals::X): the first run set those mentions aside, so COMBAT_DAMAGE showed as read by nobody. (Claude code Opus 5.5) -->
	langs = set(lang for lang, _, _, how in entries)
	if langs == {"C++", "Python"}:
		return "both"
	if langs == {"C++"}:
		return "DLL"
	if langs == {"Python"}:
		return "Python"
	return "none"


def exe_hits(names):
	# <!-- custom: For each name, the binaries among BtS's two EXEs whose strings hold it, through audit_engine_names.py's matching, so a define only the EXE reads, as many of BtS's are, is told from a dead one; empty when the game is not installed. (Claude code Opus 5.5) -->
	sys.path.insert(0, str(REPO / "LLM_Helpers" / "audits"))
	import audit_engine_names as engine
	found = defaultdict(list)
	# <!-- custom: The binaries actually searched, which the report names, so a missing EXE does not pass for "Python only", as Codex's review (GPT-6.2-Sol) asked. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	found["__searched__"] = []
	for path in engine.DEFAULT_FILES[:2]:
		if not path.is_file():
			continue
		found["__searched__"].append(path.name)
		data = path.read_bytes()
		for name in names:
			if engine.ascii_hits(data, name) or engine.wide_hits(data, name):
				found[name].append(path.name)
	return found


def cpp_prefix_names(names, rows):
	# <!-- custom: The names a C++ line could build at runtime from a literal prefix ending in "_", as built_name_readers matches, but for every name: that function looks only at names no literal reads, so a literal Python read hid a DLL reader building the name from a prefix, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	prefix_pattern = re.compile(r"[\"'](SAS_[A-Z0-9_]*_)[\"'%]")
	found = set()
	for _, _, _, line, _ in rows:
		for match in prefix_pattern.finditer(line):
			found.update(name for name in names if name.startswith(match.group(1)))
	return found


def readers_report(names, readers, rows, scope, out_path):
	# <!-- custom: Written for the user's question of which defines could leave GlobalDefines for a central Python settings file: a define only Python reads, with no live override, needs no XML, while one the DLL or the EXE reads must stay. (Claude code Opus 5.5) -->
	sides = dict((name, reader_side(readers.get(name, []))) for name in names)
	# <!-- custom: Every name is searched in the EXEs and against C++ prefixes, not only the unread ones: the first version did so for names no source read, so FIELD_OF_VIEW, which Python and both EXEs read, looked Python-only, as Codex's review reproduced.
	# A define Python and the EXE read shows as Python+EXE, and one Python reads by literal while the DLL may build its name shows as both, so the Python-only column holds just the defines nothing else reads. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	exe = exe_hits(list(names))
	searched = exe.pop("__searched__")
	built = cpp_prefix_names(names, rows)
	for name in names:
		if sides[name] == "Python" and name in built:
			sides[name] = "both"
		if name in exe:
			sides[name] = {"none": "EXE", "Python": "Python+EXE"}.get(sides[name], sides[name])
	columns = ("DLL", "Python", "both", "Python+EXE", "EXE", "none")
	origins = defaultdict(lambda: defaultdict(int))
	for name in names:
		origins[names[name][1]][sides[name]] += 1
	out = ["# Define readers", "", f"Generated by `LLM_Helpers/audits/audit_define_timing.py --readers --scope {scope}`; heuristic and text-based, see its header.", "",
		"- DLL, Python, both: who reads the define by its literal name in source; a name built at runtime counts for the side that builds it.",
		"- Python+EXE: Python reads it and BtS's EXE or Pitboss EXE holds the name, so it stays in the XML.",
		"- EXE: no reader in source, but BtS's EXE or Pitboss EXE holds the name, so the engine likely reads it.",
		"- none: no reader in source and not in the EXEs: likely dead, or read under a name this audit cannot see.", "",
		"EXEs searched: " + (", ".join(searched) or "none found, so EXE readers are unknown and Python-only defines may still be read by the engine"), "",
		"| Origin | " + " | ".join(columns) + " |", "| --- | " + " | ".join("---" for _ in columns) + " |"]
	for origin in sorted(origins):
		out.append(f"| {origin} | " + " | ".join(str(origins[origin][side]) for side in columns) + " |")
	for side, title in (("Python", "Python only, by origin and family"), ("EXE", "Read by the EXE only"), ("none", "No reader found")):
		out += ["", f"## {title}", ""]
		groups = defaultdict(list)
		for name in sorted(names):
			if sides[name] == side:
				groups[(names[name][1], family(name))].append(name)
		for (origin, fam), members in sorted(groups.items()):
			out.append(f"- {origin}, `{fam}` ({len(members)}): " + ", ".join(f"`{member}`" for member in members))
	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_bytes("\n".join(out).encode("utf-8"))
	totals = defaultdict(int)
	for side in sides.values():
		totals[side] += 1
	print(" ".join(f"{side}={totals[side]}" for side in columns) + f" of {len(names)}; wrote {out_path}")
	return 0


def main(argv=None):
	parser = argparse.ArgumentParser(description="Report when each GlobalDefines define, SAS or inherited, takes effect, from how its readers read it, to choose overridable and NoEntry defines and audit caching.")
	parser.add_argument("--define", help="show the readers of one define")
	parser.add_argument("--scope", choices=("all", "sas", "inherited"), default="all", help="which defines to report: SAS ones (GlobalDefines_advciv_sas.xml), inherited ones, or both")
	parser.add_argument("--readers", action="store_true", help="report who reads each define, the DLL, Python, both, the EXE or nobody, to LLM_Helpers/outputs/define_readers.md")
	parser.add_argument("--out", type=Path, default=None)
	args = parser.parse_args(argv)
	names = read_defines(args.scope)
	rows = cpp_lines()
	readers = built_name_readers(names, python_readers(names, cpp_readers(names, rows)), rows)
	if args.readers:
		return readers_report(names, readers, rows, args.scope, args.out or REPO / "LLM_Helpers" / "outputs" / "define_readers.md")
	args.out = args.out or REPO / "LLM_Helpers" / "outputs" / "define_timing.md"
	if args.define:
		for row in readers.get(args.define, []):
			print("  ".join(row))
		print(f"{args.define}: {verdict(readers.get(args.define, []))}")
		return 0
	counts = defaultdict(int)
	families = defaultdict(lambda: defaultdict(list))
	origins = defaultdict(lambda: defaultdict(int))
	for name in sorted(names):
		v = verdict(readers.get(name, []))
		counts[v] += 1
		families[family(name)][v].append(name)
		origins[names[name][1]][v] += 1
	out = ["# Define timing", "", f"Generated by `LLM_Helpers/audits/audit_define_timing.py --scope {args.scope}`; heuristic, see its header.", "",
		"- no cache detected: every reader asks each time its code runs; that code may still run only during setup, so check before relying on an override.",
		"- kept: a reader keeps the value (static, member, import, `__init__`, attribute or lazy cache), so it needs work first.",
		"- startup: read only while loading or setting up: NoEntry candidates.",
		"- mixed: some readers at load, others at use.",
		"- by hand: read under a name built at runtime from a prefix, or listed in a table another function reads; check by hand.",
		"- unread: no literal reader found.", "",
		"| Verdict | Count |", "| --- | --- |"]
	out += [f"| {v} | {counts[v]} |" for v in ("no cache detected", "kept", "startup", "mixed", "by hand", "unread")]
	out += ["", "## By origin", "", "The file of the DLL's load order that first defines it; SAS is GlobalDefines_advciv_sas.xml.", "", "| Origin | no cache | kept | startup | mixed | by hand | unread |", "| --- | --- | --- | --- | --- | --- | --- |"]
	for origin in sorted(origins):
		out.append(f"| {origin} | " + " | ".join(str(origins[origin][v]) for v in ("no cache detected", "kept", "startup", "mixed", "by hand", "unread")) + " |")
	out += ["", "## By family", "", "| Family | no cache | kept | startup | mixed | by hand | unread |", "| --- | --- | --- | --- | --- | --- | --- |"]
	for fam in sorted(families):
		row = families[fam]
		out.append(f"| {fam} | " + " | ".join(str(len(row[v])) for v in ("no cache detected", "kept", "startup", "mixed", "by hand", "unread")) + " |")
	out += ["", "## Defines", ""]
	for name in sorted(names):
		entries = readers.get(name, [])
		out.append(f"### {name} ({names[name][0]}, {names[name][1]}): {verdict(entries)}")
		out.append("")
		for lang, where, function, how in entries:
			out.append(f"- {lang} `{where}` in `{function}`: {how}")
		out.append("")
	args.out.parent.mkdir(parents=True, exist_ok=True)
	args.out.write_bytes("\n".join(out).encode("utf-8"))
	print(" ".join(f"{v}={counts[v]}" for v in ("no cache detected", "kept", "startup", "mixed", "by hand", "unread")) + f" of {len(names)}; wrote {args.out}")
	return 0


if __name__ == "__main__":
	sys.exit(main())

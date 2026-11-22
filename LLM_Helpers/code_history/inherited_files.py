#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Lists which Python, XML and C++ files SAS carries and which it still takes from the base game, with the matching source layers, content comparisons, static Python importers, and the first and last indexed commits for the matching repo paths.
# Reviews kept asking which file actually runs and when a copy entered the lineage (Codex and the user, 2026-11-22), for example WorldBuilder, whose two screens SAS never copied; the judgment parts live in _1_AdvCiv-SAS/Docs/Source_Analysis/inherited_files_audit.md. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: argparse reads the options; collections counts the summary; importlib loads the CI check's layers and matching, so the layer paths and load-order rule have one home; pathlib walks the trees; sys reports errors. (Claude code Opus 5.5) -->
import argparse
import csv
from io import BytesIO
# <!-- custom: datetime timestamps the inventory report. (Claude code Opus 5.5) -->
from datetime import datetime, timezone
from collections import Counter, defaultdict
import importlib.util
from pathlib import Path
import re
# <!-- custom: subprocess reads Git path operations, dates and titles for --inventory. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import subprocess
import sys

REPO = next(path for path in Path(__file__).resolve().parents if path.name == "LLM_Helpers").parent
_SPEC = importlib.util.spec_from_file_location("inherited_files_check", REPO / ".github/workflows/build/source/inherited_files.py")
check = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(check)
PATH_HISTORY = REPO / "LLM_Helpers" / "context" / "commit_diffs" / "PATH_HISTORY_INDEX.txt"
COLUMNS = ("file", "runs", "earliestBase", "layers", "vsBts", "vsAdvCiv", "importedBy", "historyPath", "first", "last")


def path_history():
	# <!-- custom: PATH_HISTORY_INDEX lists, per path, the commits touching it newest first, as "<segment> <practical> <sha>".
	# It is generated with the light-source ZIP or refresh_commit_diffs.py, so commits after its last refresh are missing; the summary prints its newest commit. (Claude code Opus 5.5) -->
	history = {}
	newest = None
	current = None
	if PATH_HISTORY.is_file():
		for line in PATH_HISTORY.read_text(encoding="utf-8", errors="replace").splitlines():
			if not line or line.startswith("#"):
				continue
			if not line.startswith("  "):
				current = line.strip().lower()
				history.setdefault(current, [])
				continue
			history[current].append(line.strip())
			# <!-- custom: Better BTS AI rows give r<revision> in place of a practical count, so only SAS-branch rows date the index. (Claude code Opus 5.5) -->
			fields = line.split()
			if fields[0] == "SASBranch" and (newest is None or int(fields[1]) > int(newest.split()[1])):
				newest = line.strip()
	return (history, newest)


def upstream_hashes(area, commit, paths):
	# <!-- custom: Read upstream blobs in one Git call.
	# Compare their bytes with the SAS checkout using the same text and binary rules as the BtS comparison. (GPT-6.2-Sol) -->
	if not paths:
		return {}
	queries = "".join("%s:%s\n" % (commit, path) for path in paths).encode("utf-8")
	output = subprocess.run(["git", "cat-file", "--batch"], cwd=REPO, input=queries, capture_output=True, check=True).stdout
	stream = BytesIO(output)
	hashes = {}
	for path in paths:
		_, kind, size = stream.readline().split()
		if kind != b"blob":
			raise ValueError("expected upstream file at " + path)
		hashes[path] = check.asset_bytes_hash(area, stream.read(int(size)))
		if stream.read(1) != b"\n":
			raise ValueError("incomplete upstream file record for " + path)
	return hashes


def rows_for(area, civ4_root, upstream_ref):
	(_, subdir, suffixes) = [entry for entry in check.AREAS if entry[0] == area][0]
	by_name = area == "python"
	layers = check.comparison_sources(area, subdir, suffixes, civ4_root)
	layer_files = [(name, check.area_files(root, suffixes, by_name)) for (name, root) in layers]
	commit, upstream = check.upstream_paths(upstream_ref)
	advciv = check.upstream_files(upstream, area, subdir, suffixes)
	sas = check.sas_files(area, subdir, suffixes)
	advciv_hashes = upstream_hashes(area, commit, [advciv[key] for key in sorted(sas.keys() & advciv.keys())])
	imports = check.python_importers(sas) if by_name else {}
	(history, _) = path_history()
	keys = set(sas) | set(advciv)
	for (_, files) in layer_files:
		keys.update(files)
	rows = []
	for key in sorted(keys):
		present = [name for (name, files) in layer_files if key in files]
		bts_path = dict(layer_files)["bts"].get(key)
		sas_path = sas.get(key)
		advciv_path = advciv.get(key)
		row = {"file": key, "earliestBase": present[0] if present else "-", "layers": ",".join(present) or "-"}
		if sas_path is not None:
			row["runs"] = "sas"
		elif area == "cpp":
			row["runs"] = "not built"
		elif present:
			# <!-- custom: For inherited assets, report the newest matching copy.
			# The audit describes where runtime evidence confirms that candidate. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			row["runs"] = present[-1]
		else:
			row["runs"] = "advciv only"
		if sas_path is not None:
			sas_hash = check.asset_hash(area, sas_path)
			if bts_path is not None:
				row["vsBts"] = "same" if sas_hash == check.asset_hash(area, bts_path) else "changed"
			if advciv_path is not None:
				row["vsAdvCiv"] = "same" if sas_hash == advciv_hashes[advciv_path] else "changed"
		else:
			if bts_path is not None:
				row["vsBts"] = "no SAS copy"
			if advciv_path is not None:
				row["vsAdvCiv"] = "no SAS copy"
		if by_name:
			row["importedBy"] = ",".join(sorted(imports.get(key[:-3], ()))) or "-"
		# <!-- custom: A deleted override can have history even when the inventory now resolves to a base copy.
		# For example, AdvCiv added and removed CvWBInterface at the same relative path BtS uses.
		# Show each matching path separately so changes at different paths do not imply a verified rename. (GPT-6.2-Sol) -->
		paths = {Path(subdir) / files[key].relative_to(root) for (name, root), (_, files) in zip(layers, layer_files) if key in files}
		if advciv_path is not None:
			paths.add(Path(advciv_path))
		if sas_path is not None:
			paths.add(sas_path.relative_to(REPO))
		matching = sorted({path.as_posix().lower() for path in paths} & history.keys())
		if matching:
			for path in matching:
				commits = history[path]
				rows.append(dict(row, historyPath=path, first=commits[-1], last=commits[0]))
		else:
			rows.append(row)
	return rows


# <!-- custom: The first K-Mod source and asset imports, verified by their Git subjects.
# The two preceding SVN records have no files in the audited trees. (GPT-6.2-Sol) -->
KMOD_INITIAL_IMPORTS = {"2414225e64", "593c549b51"}
INVENTORY_COLUMNS = ("kind", "path", "layers", "advcivEvents", "sas", "ourEvents")
LAYER_NAMES = {"vanilla": "vanilla", "warlords": "Warlords", "bts": "BtS", "advciv": "Base AdvCiv"}


def git_path_changes():
	# <!-- custom: Git supplies the real path operations in topological order.
	# The exported path index only lists touches, and practical numbers from different segments cannot establish when a path was added, deleted or renamed.
	# Skip synthetic repetitions from merge diffs. (GPT-6.2-Sol) -->
	output = subprocess.run(["git", "log", "--full-history", "--topo-order", "--no-merges", "--abbrev=10", "--format=%x1e%h%x1f%as%x1f%s", "--name-status", "-M", "-z", "--", *(":(icase)" + subdir for _, subdir, _ in check.AREAS)], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
	return parse_path_changes(output)


def parse_path_changes(output):
	changes = []
	for record in output.split("\x1e")[1:]:
		header, *fields = record.rstrip("\0").split("\0")
		sha, date, title = header.split("\x1f", 2)
		names = iter(fields)
		for status in names:
			code = status.strip()[0]
			path = next(names)
			if code in ("R", "C"):
				destination = next(names)
				if code == "R" and path.lower() != destination.lower():
					changes.append((path, "renamed to", destination, sha, date, title))
				changes.append((destination, "renamed from" if code == "R" else "copied from", path, sha, date, title))
			else:
				action = {"A": "added", "D": "deleted"}.get(code, "changed")
				changes.append((path, action, None, sha, date, title))
	return changes


def describe(change, show_path):
	path, action, other, sha, date, title = change
	location = " " + other if other else ""
	if show_path:
		preposition = " at " if other is None else (" to " if action.endswith("from") else " from ")
		location += preposition + path
	# <!-- custom: Date, SHA and title, no practical number: the same practical number names different commits in different segments.
	# A draft dropped SHAs too, as a rewrite of our history changes SAS's, but the user wanted each event to lead straight to its commit (2026-11-22); after a squash, rebase or amend, rerun --inventory, which CI cannot notice without the full history. (Claude code Opus 5.5) -->
	return "%s %s (%s%s): %s" % (date, sha, action, location, title)


def inventory_rows(area, subdir, tsv_rows, by_path, by_module, importers):
	rows = []
	sas = check.sas_files(area, subdir, [entry for entry in check.AREAS if entry[0] == area][0][2])
	for row in tsv_rows:
		if row["area"] != area:
			continue
		layers = row["layers"].split(",")
		base = [LAYER_NAMES[name] for name in layers if name != "advciv"]
		carries = check.sas_carries(row, sas)
		advciv = "advciv" in layers
		# <!-- custom: Whether SAS has the file, not how its content differs: the audit is about files added, removed or renamed against base AdvCiv and the base game (the user, 2026-11-22), and content changes are ordinary work.
		# SAS's own path is given only where it differs from the inherited one, such as SAS's Assets/Res/Cursors/ against the base game's Assets/res/, so a path is not repeated. (Claude code Opus 5.5) -->
		own = sas[row["file"]].relative_to(REPO).as_posix() if carries else "-"
		if carries:
			state = "kept" if own == row["path"] else "kept at " + own
		elif area == "cpp":
			state = "no SAS source at this path"
		elif not base:
			state = "absent"
		elif area == "python":
			# <!-- custom: Imported or not, without a count: a count would change with every new import of PyHelpers, while a module starting or stopping to be used is the decision worth reviewing. (Claude code Opus 5.5) -->
			state = "%s copy, %s" % (base[-1], check.IMPORTED if importers.get(row["file"][:-3]) else check.NOT_IMPORTED)
		else:
			state = "%s copy available" % base[-1]
		changes = by_module.get(row["file"], []) if area == "python" else by_path.get(row["path"].lower(), [])
		decision = "extra" if carries and not advciv else ("absent" if not carries and advciv else "")
		rows.append((decision, row, state, file_events(changes, by_module=area == "python"), changes))
	return rows


def upstream_shas(ref):
	output = subprocess.run(["git", "rev-list", "--abbrev-commit", "--abbrev=10", ref], cwd=REPO, capture_output=True, text=True, check=True).stdout
	return set(output.split())


def first_clause(title):
	# <!-- custom: Prefer a real clause boundary.
	# Skip abbreviation periods and keep the full subject in the report when a long clause needs a second cut. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	abbreviation = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf|no|fig|dr|mr|mrs|ms|prof)$", re.IGNORECASE)
	for match in re.finditer(r"\.\s+|;\s+|\s+[-–—]\s+", title):
		separator = match.group()
		if separator.startswith(".") and abbreviation.search(title[:match.start()]):
			continue
		title = title[:match.start()].rstrip(" .,;:")
		break
	if len(title) > 160:
		comma = title.rfind(", ", 60, 161)
		space = title.rfind(" ", 0, 161)
		stop = comma if comma != -1 else (space if space != -1 else 160)
		title = title[:stop].rstrip(" .,;:") + " (full title in the report)"
	# <!-- custom: Strip markup from subjects so a cutoff cannot leave a broken emphasis, code span or reference link in the generated Markdown. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	return title.replace("*", "").replace(chr(96), "").replace("_", "\\_").replace("[", "(").replace("]", ")").replace("|", "/")


def same_module_move(change):
	path, action, other, _, _, _ = change
	return action == "renamed to" and other.lower().startswith("assets/python/") and Path(other).name.lower() == Path(path).name.lower()


def sas_file_changes(changes, upstream, *, by_module=False):
	return [change for change in reversed(changes) if change[1] != "changed" and change[3] not in upstream and not (by_module and same_module_move(change))]


def taken_and_dropped(changes):
	# <!-- custom: A departure alone can be the removal of a file inherited before SAS.
	# Require a SAS-side arrival followed by a departure for the "dropped again" list. (GPT-6.2-Sol) -->
	arrived = False
	for _, action, _, _, _, _ in changes:
		if action in ("added", "renamed from", "copied from"):
			arrived = True
		elif arrived and action in ("deleted", "renamed to"):
			return True
	return False


def sas_side_events(changes, *, by_module=False):
	events = []
	show_path = by_module and len({change[0].lower() for change in changes}) > 1
	for path, action, other, sha, date, title in changes:
		location = " " + chr(96) + other + chr(96) if other else ""
		if show_path:
			preposition = " at " if other is None else (" to " if action.endswith("from") else " from ")
			location += preposition + chr(96) + path + chr(96)
		events.append(("%s " + chr(96) + "%s" + chr(96) + ", %s%s: %s") % (date, sha, action, location, first_clause(title)))
	return "; ".join(events) or "no SAS-side file event found"


def file_events(changes, *, by_module=False):
	# <!-- custom: Only file-level events, oldest first: added, removed, added again, renamed or moved, such as CIV4CityLSystem.xml added on 2025-05-07 and removed on 2026-01-30.
	# A draft showed each file's latest change and SAS commit count, but those were content edits such as renaming Rice or a religion, noise for what SAS takes and leaves (the user, 2026-11-22). (Claude code Opus 5.5) -->
	events = []
	# <!-- custom: A same-name Python move has an outgoing and incoming record in the same basename group.
	# Show the incoming event once, with both paths.
	# Same-name adds or deletions at different paths remain distinct. (GPT-6.2-Sol) -->
	show_path = by_module and len({change[0].lower() for change in changes}) > 1
	for change in reversed(changes):
		path, action, other, sha, date, _ = change
		if action == "changed":
			continue
		if by_module and same_module_move(change):
			continue
		if action == "added" and sha in KMOD_INITIAL_IMPORTS and not show_path:
			events.append("came with K-Mod, %s %s" % (date, sha))
		else:
			events.append(describe(change, show_path))
	return "; ".join(events) or "-"


def folder_tree(files_by):
	# <!-- custom: The whole inherited layout as nested bullets, a folder then its files then its subfolders, each file marked as carried by SAS or not, with the layer it comes from.
	# Earlier versions gave each folder counts, then counts by layer, then only the uncarried files grouped by layer; the user found the names clearer than the counts, and with every file in a proper tree the counts add nothing (2026-11-22). (Claude code Opus 5.5) -->
	# <!-- custom: Folders merge case-insensitively, as Windows does: the base game ships Assets/res and Assets/res/cursors where AdvCiv has Assets/Res and Cursors, and the first tree showed each spelling as its own folder, with children under the wrong one.
	# Each shows its most common spelling. (Claude code Opus 5.5) -->
	spellings = {}
	direct = {}
	for (folder, files) in files_by.items():
		parts = folder.split("/")
		for depth in range(1, len(parts) + 1):
			node = tuple(part.lower() for part in parts[:depth])
			spellings.setdefault(node, Counter())[parts[depth - 1]] += len(files)
			direct.setdefault(node, [])
		direct[tuple(part.lower() for part in parts)].extend(files)
	lines = []
	for node in sorted(direct):
		indent = "  " * (len(node) - 1)
		lines.append("%s- `%s/`" % (indent, spellings[node].most_common(1)[0][0]))
		for (name, provider, carries) in sorted(direct[node], key=lambda item: item[0].lower()):
			if carries:
				status = "filename kept by SAS, also in %s" % ("base AdvCiv" if provider == "Base AdvCiv" else provider)
			elif provider == "Base AdvCiv":
				status = "base AdvCiv filename absent from SAS (see the list above)"
			else:
				status = "from %s, not in SAS" % provider
			lines.append("%s  - `%s`: %s" % (indent, name, status))
	return lines


# <!-- custom: upstream_ref is new: write_inventory read the CI check's fixed "1.14" default, so --upstream-ref was ignored here, which Codex found in review; main now passes the resolved ref (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def write_inventory(upstream_ref):
	by_path = defaultdict(list)
	by_module = defaultdict(list)
	for change in git_path_changes():
		path = change[0].lower()
		by_path[path].append(change)
		if path.startswith("assets/python/"):
			by_module[path.rsplit("/", 1)[-1]].append(change)
	sas_python = check.sas_files("python", "Assets/Python", (".py",))
	importers = check.python_importers(sas_python)
	tsv_rows = check.read_tsv()
	titles = {"python": "Python", "xml": "XML", "cpp": "C++", "res": "res", "config": "Config"}
	by_area = [(area, subdir, inventory_rows(area, subdir, tsv_rows, by_path, by_module, importers)) for (area, subdir, _) in check.AREAS]
	# <!-- custom: The full per-file list is a report, written to the Git-ignored LLM_Helpers/outputs, timestamped, sorted by path so folders group as in a tree view, for grepping and for agents.
	# As a Markdown table of 924 rows it was hard to read, and as a tracked TSV it would churn with every SAS file change and every history rewrite (the user, 2026-11-22).
	# New SAS files are listed too, so one grep finds any file. (Claude code Opus 5.5) -->
	entries = []
	for (area, subdir, rows) in by_area:
		for (decision, row, state, events, _) in rows:
			entries.append(("inherited", row["path"], row["layers"], row["advcivEvents"], state, events))
	for (area, subdir, suffixes) in check.AREAS:
		for path in check.new_sas_files(area, subdir, suffixes, tsv_rows):
			name = path.relative_to(REPO).as_posix()
			entries.append(("new", name, "-", "-", "kept", file_events(by_path.get(name.lower(), []))))
	entries.sort(key=lambda entry: entry[1].lower())
	report = REPO / "LLM_Helpers" / "outputs" / ("inherited_files_inventory_%s.tsv" % datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
	report.parent.mkdir(exist_ok=True)
	with report.open("w", encoding="utf-8", newline="") as stream:
		writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
		writer.writerow(INVENTORY_COLUMNS)
		writer.writerows(entries)
	(imported, problems) = check.inherited_imports(tsv_rows)
	for problem in problems:
		print("warning: " + problem)
	# <!-- custom: The readable part goes into the audit between markers, below its hand-written reasons, as history_lineage_tables.py does for its guide; a separate inventory file beside it was confusing (the user, 2026-11-22).
	# Everything in it changes only with an inherited-file decision, which CI's fingerprints catch.
	# A per-commit log of file events was dropped: it listed our history, which the user did not want there, went stale on a squash without CI noticing, and the report holds each file's events. (Claude code Opus 5.5) -->
	block = [check.GENERATED_START] + check.audit_markers(tsv_rows, imported) + [""]
	block.append("Generated by [`inherited_files.py`](/LLM_Helpers/README.md#inherited_filespy) `--inventory`. The same run writes every inherited and new SAS file, its layers, its file events in base AdvCiv's history and in ours, and SAS's status to a timestamped `inherited_files_inventory_<UTC>.tsv` in the Git-ignored `LLM_Helpers/outputs/`.")
	block.append("")
	# <!-- custom: The inherited modules SAS imports without carrying a copy, each with the file that runs: part of how far SAS integrates what it inherits, which CI fingerprints.
	# A bare lower-case module name hid where it sits (the user, 2026-11-22). (Claude code Opus 5.5) -->
	where = {row["file"][:-3]: check.base_game_path(row) for row in tsv_rows if row["area"] == "python" and check.in_base_game(row)}
	# <!-- custom: One bullet per module, in path order: as one inline list of 18 paths it ran to a single unreadable line (the user, 2026-11-22). (Claude code Opus 5.5) -->
	# <!-- custom: "imported by SAS's Python files, inherited importers included", not "SAS imports": every importer was an inherited file SAS kept, and the old heading read as if SAS had chosen them (the user, 2026-11-22). (Claude code Opus 5.5) -->
	block += ["Base-game Python modules imported by SAS's Python files, inherited importers included, without a module of the same name in SAS:", ""] + ["- `%s`" % path for path in sorted((where[module] for module in imported), key=str.lower)]
	block.append("")
	# <!-- custom: Per provider, the newest layer holding the file, so each file counts once and the table answers what each layer gives SAS and what SAS does not carry (the user, 2026-11-22). (Claude code Opus 5.5) -->
	providers = {}
	# <!-- custom: Each inherited file by its folder, with its source layer and whether SAS carries it, for the tree below; the layer tells apart files SAS never needed to copy, such as the base game's text files, which Civ4 loads from every layer together, from base AdvCiv files SAS removed or renamed (the user, 2026-11-22). (Claude code Opus 5.5) -->
	files_by = {}
	for (area, subdir, rows) in by_area:
		for (decision, row, state, _, _) in rows:
			carries = state.startswith("kept")
			provider = LAYER_NAMES[row["layers"].split(",")[-1]]
			(folder, name) = row["path"].rsplit("/", 1)
			counts = providers.setdefault(provider, [0, 0, 0])
			counts[0] += 1
			counts[1 if carries else 2] += 1
			files_by.setdefault(folder, []).append((name, provider, carries))
	block += ["### Counts", "", "Each inherited file counts once, under the newest layer that provides it.", "", "| Provider | Files | Filename kept by SAS | Not in SAS |", "| --- | --- | --- | --- |"]
	for provider in ("vanilla", "Warlords", "BtS", "Base AdvCiv"):
		if provider in providers:
			block.append("| %s | %d | %d | %d |" % ((provider,) + tuple(providers[provider])))
	block += ["", "| Area | Inherited files | Filename kept by SAS | SAS overrides absent from base AdvCiv | Base AdvCiv files absent from SAS |", "| --- | --- | --- | --- | --- |"]
	for (area, subdir, rows) in by_area:
		block.append("| %s | %d | %d | %d | %d |" % (titles[area], len(rows), len([1 for row in rows if row[2].startswith("kept")]), len([1 for row in rows if row[0] == "extra"]), len([1 for row in rows if row[0] == "absent"])))
	# <!-- custom: The files SAS decided about, generated one full path per bullet with the events on SAS's side of history: a hand-kept list drifted from Git, and bare names hid where a file sits (the user, 2026-11-22).
	# Files SAS took in and dropped again get their own list, such as Assets/XML/Buildings/CIV4CityLSystem.xml, which neither of the other two would show. (Claude code Opus 5.5) -->
	upstream = upstream_shas(upstream_ref)
	selections = {heading: [] for heading in (check.TAKEN_IN_HEADING, check.DROPPED_HEADING, check.REMOVED_HEADING)}
	for area, subdir, rows in by_area:
		for decision, row, state, _, changes in rows:
			by_module = area == "python"
			events = sas_file_changes(changes, upstream, by_module=by_module)
			if decision == "extra":
				heading = check.TAKEN_IN_HEADING
			elif decision == "absent":
				heading = check.REMOVED_HEADING
			elif not state.startswith("kept") and taken_and_dropped(events):
				heading = check.DROPPED_HEADING
			else:
				continue
			selections[heading].append((row["path"], sas_side_events(events, by_module=by_module)))
	lists = (
		(check.TAKEN_IN_HEADING, "Base-game filenames that SAS keeps and base AdvCiv lacks."),
		(check.DROPPED_HEADING, "Base-game filenames absent from both SAS and base AdvCiv for which Git records a SAS-side arrival followed by a departure."),
		(check.REMOVED_HEADING, "Base AdvCiv filenames absent from SAS. The list shows the SAS-side deletion or rename where Git records one."),
	)
	for heading, intro in lists:
		block += ["", "### " + heading, "", intro, ""]
		block += ["- `%s`: %s" % (path, events) for path, events in sorted(selections[heading], key=lambda item: item[0].lower())]
	block += ["", "### By folder", "", "Every inherited file in its folder, with its comparison layer and whether SAS keeps the filename. The file's contents may have changed or come from another mod.", ""]
	block += folder_tree(files_by)
	block += ["", check.GENERATED_END]
	text = check.AUDIT.read_text(encoding="utf-8")
	try:
		start, end = check.generated_bounds(text)
	except ValueError as error:
		raise SystemExit(str(error)) from error
	check.AUDIT.write_text(text[:start] + "\n".join(block) + text[end:], encoding="utf-8", newline="\n")
	print("wrote %s and the generated part of %s" % (report.relative_to(REPO).as_posix(), check.AUDIT.relative_to(REPO).as_posix()))


LOGS = Path.home() / "Documents" / "My Games" / "beyond the sword" / "Logs"
LOG_LINE = re.compile(r"^(load_module |EntryPoint module:)\s*([A-Za-z0-9_]+)")


def loaded_modules(log_dir):
	# <!-- custom: Which modules Civ4 reported loading in every PythonDbg*.log under log_dir, archived ones included, lower-cased.
	# Lower case because Civ4 imports by name without case: the first comparison, case-sensitive, missed CvUNVictoryScreen, which the logs name CvUnVictoryScreen; Codex caught it (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	loaded, entry_points, logs = set(), set(), sorted(log_dir.rglob("PythonDbg*.log"))
	for log in logs:
		for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
			match = LOG_LINE.match(line)
			if match:
				(loaded if match.group(1).startswith("load") else entry_points).add(match.group(2).lower())
	return loaded, entry_points, logs


def report_loaded(log_dir):
	# <!-- custom: Sorts the base-game Python modules SAS has no copy of by what the logs show: loaded, registered only as an entry point, or not observed.
	# Registered entry points such as CvTranslator never print load_module, so "not observed" is not proof of non-use (Codex, 2026-11-22). See KI#1104. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	loaded, entry_points, logs = loaded_modules(log_dir)
	if not logs:
		raise SystemExit("no PythonDbg*.log under %s" % log_dir)
	tsv_rows = check.read_tsv()
	sas = {path.stem.lower() for path in (REPO / "Assets" / "Python").rglob("*.py")}
	missing = sorted((row for row in tsv_rows if row["area"] == "python" and check.in_base_game(row) and row["file"][:-3] not in sas), key=lambda row: row["path"].lower())
	print("%d PythonDbg logs under %s" % (len(logs), log_dir))
	for label, test in (("loaded", lambda key: key in loaded), ("entry point only", lambda key: key not in loaded and key in entry_points), ("not observed", lambda key: key not in loaded and key not in entry_points)):
		rows = [row for row in missing if test(row["file"][:-3])]
		print("\n%s (%d):" % (label, len(rows)))
		for row in rows:
			print("  %s\t%s" % (check.base_game_path(row), next(name for name in reversed(row["layers"].split(",")) if name in check.BASE_TREES)))
	return 0


LAYER_FOLDERS = {"vanilla": "", "warlords": "Warlords/", "bts": "Beyond the Sword/"}
# <!-- custom: The copy comment names the layer as well as the full path: a path under the install root alone did not say whether vanilla, Warlords or BtS shipped the file (the user, 2026-11-22). (Claude code Opus 5.5) -->
COPY_LAYER_NAMES = {"vanilla": "vanilla Civ4", "warlords": "Warlords", "bts": "BtS"}


def shipped_by(layers):
	if len(layers) == 1:
		return "only %s ships it" % COPY_LAYER_NAMES[layers[0]]
	return "the newest of the %s and %s copies" % (", ".join(COPY_LAYER_NAMES[name] for name in layers[:-1]), COPY_LAYER_NAMES[layers[-1]])


def take_in(paths, civ4_root):
	# <!-- custom: Copies base-game Python files SAS uses into SAS, from the newest layer providing each, adding only the SAS header after Firaxis's notice and a comment naming the source; from then on each is an ordinary SAS file.
	# Written for KI#1104's first copies (2026-11-22), so the next file SAS starts using comes in the same way; Codex checked each of those copies against its source. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	rows = {row["path"].lower(): row for row in check.read_tsv() if row["area"] == "python" and check.in_base_game(row)}
	for path in paths:
		row = rows.get(path.replace("\\", "/").lower())
		if row is None:
			raise SystemExit("%s: not a base-game Python file in inherited_files.tsv" % path)
		layers = [name for name in row["layers"].split(",") if name in LAYER_FOLDERS]
		layer = layers[-1]
		rel = check.base_game_path(row)
		source = LAYER_FOLDERS[layer] + rel
		target = REPO / rel
		if target.exists():
			raise SystemExit("%s: already in SAS" % rel)
		lines = (civ4_root / source).read_bytes().decode("ascii").replace("\r\n", "\n").split("\n")
		if "Copyright Firaxis Games" not in lines[1]:
			raise SystemExit("%s: no Firaxis notice on line 2; add the header by hand" % source)
		header = ["#", "# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)", "# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)", "#", "# <!-- custom: Copied from %s's %s (%s), the copy SAS ran before (%s). See KI#1104. (model credit) -->" % (COPY_LAYER_NAMES[layer], (civ4_root / source).resolve(), shipped_by(layers), datetime.now().strftime("%Y-%m-%d"))]
		target.parent.mkdir(parents=True, exist_ok=True)
		target.write_bytes("\n".join(lines[:2] + header + lines[2:]).encode("ascii"))
		print("copied %s -> %s; put your model credit in its comment" % (source, rel))
	return 0


def main():
	parser = argparse.ArgumentParser(description="List which inherited Python, XML or C++ filenames SAS keeps or still takes from the base game, with their lineage.")
	parser.add_argument("area", nargs="?", choices=[entry[0] for entry in check.AREAS])
	# <!-- custom: The user asked for every inherited file, base AdvCiv's included, with when and why SAS took or skipped it, not only SAS's copies (2026-11-22); --inventory writes that table from the CI tsv and our history. (Claude code Opus 5.5) -->
	parser.add_argument("--inventory", action="store_true", help="write the TSV report and refresh the audit summary")
	parser.add_argument("--runs", help="filter by matching source layer: sas, bts, warlords, vanilla, 'not built' (C++) or 'advciv only'")
	parser.add_argument("--civ4-root", type=Path, default=check.DEFAULT_CIV4_ROOT, help="install root containing Assets and Beyond the Sword")
	parser.add_argument("--upstream-ref", help="upstream AdvCiv commit or ref (default: the release SAS last merged)")
	parser.add_argument("--grep", help="only files whose name contains this text (case-insensitive)")
	parser.add_argument("--summary", action="store_true", help="print counts instead of rows")
	parser.add_argument("--loaded", nargs="?", const=LOGS, type=Path, metavar="LOG_DIR", help="compare the base-game Python files SAS lacks with the modules PythonDbg logs show loading (default: Civ4's Logs folder)")
	parser.add_argument("--take-in", nargs="+", metavar="PATH", help="copy these base-game Python files, such as Assets/Python/Screens/CvScreen.py, into SAS with a source comment")
	args = parser.parse_args()
	if args.loaded:
		return report_loaded(args.loaded)
	if args.take_in:
		return take_in(args.take_in, args.civ4_root)
	# <!-- custom: --upstream-ref applies to --inventory too; it was ignored there, which Codex found in review (2026-11-22). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	upstream_ref = check.merged_release_or_exit(REPO, args.upstream_ref)
	if args.inventory:
		write_inventory(upstream_ref)
		return 0
	if args.area is None:
		parser.error("give an area or --inventory")
	rows = rows_for(args.area, args.civ4_root, upstream_ref)
	if args.runs:
		rows = [row for row in rows if row["runs"] == args.runs]
	if args.grep:
		rows = [row for row in rows if args.grep.lower() in row["file"]]
	if args.summary:
		print("commit history index newest: %s" % (path_history()[1] or "missing, run LLM_Helpers/packaging/refresh_commit_diffs.py"))
		by_file = {row["file"]: (row["runs"], row.get("vsBts", "-")) for row in rows}
		for ((runs, vs_bts), count) in sorted(Counter(by_file.values()).items()):
			print("runs=%s vsBts=%s: %d" % (runs, vs_bts, count))
		return 0
	print("\t".join(COLUMNS))
	for row in rows:
		print("\t".join(row.get(column, "-") for column in COLUMNS))
	return 0


if __name__ == "__main__":
	sys.exit(main())

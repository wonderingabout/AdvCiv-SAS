#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASSaveTransplanter: recreates the turn-0 world of a save that the current build can no longer load, as a new save written by the current build.
# The build that wrote the save loads it and writes its world as WorldBuilder text (type names, not XML indexes), SASSaveTransplanterWorld.py checks those names against the current XML, and the current build loads that text as a scenario and saves normally.
# No binary field crosses versions.
# See README_SASSaveTransplanter.md. (Claude code Fable 5.2) -->

# <!-- custom: argparse reads the commands; collections counts mods and plot differences; json reads facts and writes reports; re finds leftover mod-folder names in a mod copy; shutil copies a source build; struct reads and rewrites the save header; subprocess runs SASSaveTransplanterWorld.py; uuid names SASPilot session. (Claude code Fable 5.2) -->
import argparse
import collections
import datetime
import json
import os
import re
import shutil
import struct
# <!-- custom: datetime, os and time stamp run files and wait with deadlines; sys extends the import path for the helpers below; Path builds the run and save paths. (Claude code Opus 5.5) -->
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "game_runs"))
sys.path.insert(0, str(HERE.parent / "desktop"))
sys.path.insert(0, str(HERE.parent / "saspilot"))
# <!-- custom: run_autoplay writes the per-run INI and closes Civ4, desktop_windows launches and clicks, SASPilotClient talks to the current build. (Claude code Fable 5.2) -->
import desktop_windows
import run_autoplay
import SASPilotClient

MODS_DIR = run_autoplay.REPO_ROOT.parent
BTS_DIR = MODS_DIR.parent
CIV4_DIR = BTS_DIR.parent
SAVE_EXT = ".CivBeyondSwordSave"
WB_EXT = ".CivBeyondSwordWBSave"
EXPORTER = "SASSaveTransplanterExport"
# <!-- custom: Written into every folder install_mod_copy creates; only a folder holding it may be reused or given the export hook. (Claude code Fable 5.2) -->
MOD_COPY_MARK = "SASModCopy.json"
# <!-- custom: The scenario setup screens' OK button as PrintWindow shows it, 120 x 36 pixels around the click point, taken at the window size beside it.
# A mean colour difference above 4 of 255 per channel counts as another picture: measured 2026-11-16, the first screen's "OK >" differed from the reference by 0.79, the other two by 0, and the black loading screen by 71. (Claude code Fable 5.2) -->
SETUP_OK_MAX_DIFFERENCE = 4.0
# <!-- custom: The reference pictures were beside this script; on 2026-11-16 the user asked for them in the Images folder, where other pictures that helpers read and write already live, such as the art-tool samples in Images/LLM. (Claude code Opus 5.5) -->
SETUP_OK_DIR = run_autoplay.REPO_ROOT / "_1_AdvCiv-SAS" / "Images" / "LLM" / "sassavetransplanter"
HOOK_MARK = "# SASSaveTransplanter hook"
HOOK = "\n\n%s: writes the loaded game's world out once; added to this copy by SASSaveTransplanter.py.\nimport %s\n_sasSaveTransplanterInnerOnEvent = onEvent\ndef onEvent(argsList):\n\t%s.onEvent(argsList)\n\treturn _sasSaveTransplanterInnerOnEvent(argsList)\n" % (HOOK_MARK, EXPORTER, EXPORTER)


def utc_stamp():
	return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_header(path):
	# <!-- custom: A save starts with a 4-byte version, a 4-byte length and the mod path; further fields follow, and the checksum that ends the file does not cover the mod path (c4lib's checksum.cpp lists what it covers).
	# So a copy can name another mod folder with no checksum repair. (Claude code Fable 5.2) -->
	data = Path(path).read_bytes()
	if len(data) < 8:
		raise ValueError("%s does not look like a Civ4 save (%d bytes)" % (path, len(data)))
	version, length = struct.unpack_from("<ii", data, 0)
	if length < 0 or length > 260 or len(data) < 8 + length:
		raise ValueError("%s does not look like a Civ4 save (mod path length %d)" % (path, length))
	return data, version, data[8:8 + length].decode("latin-1")


def copy_with_mod_path(save, out, mod_path):
	# <!-- custom: Was out.write_bytes: Codex (GPT-6.1-Sol)'s 2026-11-16 review made the input and the "_copy" path one file and the original save was rewritten in place.
	# Mode "xb" only creates, so the copy can never be an existing file, the input and its hard links included. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	data, version, old = read_header(save)
	encoded = mod_path.encode("latin-1")
	with open(out, "xb") as handle:
		handle.write(struct.pack("<ii", version, len(encoded)) + encoded + data[8 + len(old.encode("latin-1")):])
	return old


def command_inventory(args):
	# <!-- custom: The Saves folders hold other mods' saves too (Caveman2Cosmos, base AdvCiv), and every mod names them "PC BC-<year>", so the header's mod path is read before anything is assigned to a build. (Claude code Fable 5.2) -->
	mods = collections.Counter()
	rows = []
	for root in args.folders:
		for save in sorted(Path(root).rglob("*" + SAVE_EXT)):
			try:
				mod = read_header(save)[2] or "(no mod)"
			except (ValueError, OSError) as error:
				mod = "(unreadable: %s)" % error
			mods[mod] += 1
			rows.append({"save": str(save), "mod": mod, "bytes": save.stat().st_size, "modifiedUtc": datetime.datetime.fromtimestamp(save.stat().st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
	for mod, count in mods.most_common():
		print("%6d  %s" % (count, mod))
	if args.report:
		args.report.write_text(json.dumps({"mods": dict(mods), "saves": rows}, indent=1), encoding="utf-8")
		print("wrote %s" % args.report)
	return 0


def install_mod_copy(tree, name, dry_run=False):
	# <!-- custom: Installs an extracted release under Mods with another folder name, so it runs beside the current mod: for a transplant's source build, or to launch an old build for a bisect.
	# The release tree stays as it was.
	# Was part of install_build, which accepted any existing folder under Mods: Codex (GPT-6.1-Sol)'s 2026-11-16 review noted that --build AdvCiv would have patched a real AdvCiv installation.
	# A copy now carries MOD_COPY_MARK, and a folder without it is refused. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	if Path(name).name != name or name in ("", ".", ".."):
		raise SystemExit("%r is not a folder name" % name)
	target = MODS_DIR / name
	if target.resolve() == run_autoplay.REPO_ROOT.resolve():
		raise SystemExit("the copy must not be the current mod folder")
	if target.exists():
		mark = target / MOD_COPY_MARK
		if not mark.is_file():
			raise SystemExit("%s exists and was not made by this tool (no %s); choose another folder name" % (target, MOD_COPY_MARK))
		made = json.loads(mark.read_text(encoding="utf-8"))
		if tree is not None and Path(made["sourceTree"]).resolve() != Path(tree).resolve():
			raise SystemExit("%s holds a copy of %s, not of %s; choose another folder name" % (target, made["sourceTree"], tree))
		return made
	if tree is None:
		raise SystemExit("%s does not exist; pass --release-tree with an extracted release to install it" % target)
	tree = Path(tree).resolve()
	inis = list(tree.glob("*.ini"))
	if len(inis) != 1:
		raise SystemExit("%s: expected one mod .ini, found %d" % (tree, len(inis)))
	original = inis[0].stem
	# <!-- custom: The first 4986 launch from the folder AdvCiv-SAS-4986 stopped on AdvCiv's "Invalid path to UI theme" dialog (advc.002b): the theme's path names the mod folder once in CIV4ArtDefines_Misc.xml (DEFAULT_THEME_NAME) and twice in Resource/Civ4.thm.
	# Renaming those three made the copy start; this is all AdvCiv-SAS 4986 needs to run under another folder name. (Claude code Fable 5.2) -->
	rewrites = (("Assets/XML/Art/CIV4ArtDefines_Misc.xml", "Mods/%s/Resource/Civ4.thm" % original, "Mods/%s/Resource/Civ4.thm" % name), ("Resource/Civ4.thm", "Mods\\%s\\Resource" % original, "Mods\\%s\\Resource" % name))
	made = {"format": "SASModCopy", "sourceTree": str(tree), "originalName": original, "name": name, "createdUtc": utc_stamp(), "ini": name + ".ini", "rewritten": [], "otherReferences": []}
	if dry_run:
		made["dryRun"] = True
		for relative, old, _new in rewrites:
			if (tree / relative).is_file() and old.encode("latin-1") in (tree / relative).read_bytes():
				made["rewritten"].append(relative)
		return made
	for part in ("Assets", "PrivateMaps", "Resource", "Settings"):
		if (tree / part).is_dir():
			shutil.copytree(tree / part, target / part)
	# <!-- custom: Civ4 reads the mod's settings from <folder name>.ini. (Claude code Fable 5.2) -->
	shutil.copyfile(inis[0], target / (name + ".ini"))
	for relative, old, new in rewrites:
		themed = target / relative
		if themed.is_file():
			content = themed.read_bytes()
			if old.encode("latin-1") in content:
				themed.write_bytes(content.replace(old.encode("latin-1"), new.encode("latin-1")))
				made["rewritten"].append(relative)
	# <!-- custom: Another mod may name its folder in further files, so whatever still names the old folder is listed for inspection, not rewritten: only the three theme paths were tested. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	pattern = re.compile(("Mods[/\\\\]%s(?![\\w.-])" % re.escape(original)).encode("latin-1"), re.IGNORECASE)
	for path in sorted(target.rglob("*")):
		if path.is_file() and path.suffix.lower() in (".xml", ".py", ".ini", ".thm", ".txt") and pattern.search(path.read_bytes()):
			made["otherReferences"].append(str(path.relative_to(target)))
	(target / MOD_COPY_MARK).write_text(json.dumps(made, indent=1), encoding="utf-8")
	print("copied %s to %s" % (tree, target))
	return made


def install_build(tree, name):
	# <!-- custom: A transplant's source build: a mod copy plus the export hook.
	# Refuses while Civ4 runs, before anything is written, as the running client could be that copy. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	refuse_running_civ4()
	install_mod_copy(tree, name)
	target = MODS_DIR / name
	entry = target / "Assets" / "Python" / "EntryPoints" / "CvEventInterface.py"
	text = entry.read_bytes().decode("latin-1")
	if HOOK_MARK not in text:
		entry.write_bytes((text + HOOK.replace("\n", "\r\n")).encode("latin-1"))
	shutil.copyfile(HERE / (EXPORTER + ".py"), entry.parent / (EXPORTER + ".py"))
	return target


def write_ini(prefix, mod_folder, extra_lines=None):
	ini_name = "%s_%s_%d.ini" % (prefix, time.strftime("%Y%m%dT%H%M%S"), os.getpid())
	ini_path = desktop_windows.DEFAULT_CIV4_DIR / ini_name
	# <!-- custom: QuickStart would start a new game instead of loading; Map names a script every build has, as run_autoplay.py does. (Claude code Fable 5.2) -->
	run_autoplay.write_request_ini(run_autoplay.USER_DIR / "CivilizationIV.ini", ini_path, None, False, "-", "Transplant", {"QuickStart": "0", "Map": "Pangaea", "Mod": "Mods\\%s" % mod_folder}, extra_lines=extra_lines)
	return ini_name, ini_path


def remove_ini(ini_path):
	for leftover in (ini_path, ini_path.with_name(ini_path.name + ".bak")):
		try:
			leftover.unlink()
		except OSError:
			pass


def write_request(build, values):
	# <!-- custom: What the hook in a mod copy is to do on its next launch, as a Python module of plain values beside CvEventInterface.py.
	# "%a" keeps it ASCII; a human name with other letters would not compare equal in the hook, which was not tried. (Claude code Fable 5.2) -->
	path = MODS_DIR / build / "Assets" / "Python" / "EntryPoints" / "SASSaveTransplanterRequest.py"
	path.write_text("".join("%s = %a\n" % item for item in sorted(values.items())), encoding="ascii")
	return path


def remove_request(path):
	# <!-- custom: Removed once Civ4 has closed, so the copy holds no armed request; see the hook's onEvent. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	for leftover in (path, path.with_suffix(".pyc")):
		try:
			leftover.unlink()
		except OSError:
			pass


def refuse_running_civ4():
	running = desktop_windows.civ4_processes()
	if running:
		raise SystemExit("Civ4 is already running (%s); close it first" % ", ".join(str(pid) for pid, _ in running))


def exporter_import():
	# <!-- custom: reload, as a SASPilot session may have imported an older copy of the exporter. (Claude code Fable 5.2) -->
	return "import sys\nif %r not in sys.path:\n\tsys.path.insert(0, %r)\nimport %s\nreload(%s)\n" % (str(HERE), str(HERE), EXPORTER, EXPORTER)


def exporter_code(prefix, probe):
	# <!-- custom: Python for SASPilot's 'py': runs this folder's exporter inside the current build, where no hook is installed. (Claude code Fable 5.2) -->
	return exporter_import() + "result = %s.export(%r, %r)\n" % (EXPORTER, str(prefix), probe)


def export_world_current(save, prefix, timeout):
	# <!-- custom: A save the current build still loads needs no source copy or hook: SASPilot loads it and runs the same exporter.
	# This is the control run, and the way to keep a test start as text before a later commit breaks its save. (Claude code Fable 5.2) -->
	refuse_running_civ4()
	prefix = Path(prefix)
	prefix.parent.mkdir(parents=True, exist_ok=True)
	completed = subprocess.run([sys.executable, str(HERE.parent / "saspilot" / "SASPilotClient.py"), "--timeout", str(timeout), "--save", str(save), "start"], capture_output=True, text=True)
	if completed.returncode != 0:
		raise SystemExit("SASPilot could not load %s: %s" % (save, completed.stderr[-2000:]))
	pid = json.loads(completed.stdout)["pid"]
	reply = SASPilotClient.call(pid, "py", {"code": exporter_code(prefix, True)}, 300.0)
	outcome = SASPilotClient.close(pid)["civ4"]
	if reply.get("result"):
		raise SystemExit("the export failed in the current build: %s" % reply.get("result"))
	return {"sourceSave": str(save), "sourceBuild": run_autoplay.MOD_FOLDER, "wbSave": str(prefix) + WB_EXT, "facts": str(prefix) + ".facts.json", "civ4": outcome}


def export_world(build, save, prefix, timeout):
	if build == run_autoplay.MOD_FOLDER:
		return export_world_current(save, prefix, timeout)
	install_build(None, build)
	# <!-- custom: Loads a copy of the save in the source build and waits for the hook's .done file.
	# The original save is only read. (Claude code Fable 5.2) -->
	refuse_running_civ4()
	build_dir = MODS_DIR / build
	prefix = Path(prefix)
	prefix.parent.mkdir(parents=True, exist_ok=True)
	for suffix in (WB_EXT, ".facts.json", ".done"):
		leftover = Path(str(prefix) + suffix)
		if leftover.exists():
			leftover.unlink()
	# <!-- custom: Was "<prefix>_copy", kept afterwards; a name of its own per run cannot meet an earlier copy, and the copy is removed once the source build has closed. (Claude code Fable 5.2) -->
	save_copy = Path("%s_copy_%s_%d%s" % (prefix, utc_stamp(), os.getpid(), SAVE_EXT))
	old_mod = copy_with_mod_path(save, save_copy, "Mods\\%s\\" % build)
	request = write_request(build, {"MODE": "export", "OUT_PREFIX": str(prefix)})
	ini_name, ini_path = write_ini("SASSaveTransplanter", build)
	pid = desktop_windows.launch_detached('/FXSLOAD="%s" ini=%s' % (save_copy, ini_name))
	print("source build %s: launched pid %d" % (build, pid), flush=True)
	done = Path(str(prefix) + ".done")
	deadline = time.monotonic() + timeout
	try:
		while not done.exists():
			if not desktop_windows.process_alive(pid):
				raise SystemExit("the source build exited before exporting; see PythonErr.log")
			if time.monotonic() > deadline:
				raise SystemExit("no export within %g s; Civ4 %d left open for inspection (a dialog may be waiting)" % (timeout, pid))
			time.sleep(1)
		time.sleep(1)
	except SystemExit:
		if not desktop_windows.process_alive(pid):
			remove_ini(ini_path)
			remove_request(request)
		raise
	outcome = run_autoplay.close_civ4(pid)
	remove_ini(ini_path)
	remove_request(request)
	save_copy.unlink()
	status = done.read_text(encoding="latin-1")
	if not status.startswith("SUCCEEDED"):
		raise SystemExit("the source build's export failed:\n%s" % status)
	return {"sourceSave": str(save), "sourceSaveModPath": old_mod, "sourceBuild": build, "wbSave": str(prefix) + WB_EXT, "facts": str(prefix) + ".facts.json", "civ4": outcome}


def setup_ok_button(pid, crop_path):
	# <!-- custom: Where the setup screens' OK is, and whether it is on screen now, by comparing the window's picture there with the reference pictures in SETUP_OK_DIR (setup_ok_button_1926x1120.png).
	# Was a blind click every 2 s; Codex (GPT-6.1-Sol)'s 2026-11-16 review noted that a slow start, a dialog or another layout would send that click to some other Civ4 control.
	# PrintWindow reads the window without bringing it forward. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	# <!-- custom: Pillow compares the two pictures; imported here so the other commands work without it. (Claude code Fable 5.2) -->
	from PIL import Image, ImageChops, ImageStat
	hwnd = desktop_windows.find_window(pid)
	if not hwnd:
		return None, None
	left, top, right, bottom = desktop_windows.window_rect(hwnd)
	size = (right - left, bottom - top)
	# <!-- custom: OK sits 70 px left of and 26 px above the window's bottom-right corner at 1926 x 1120; measured 2026-11-16. (Claude code Fable 5.2) -->
	point = (size[0] - 70, size[1] - 26)
	if point[0] < 60 or point[1] < 18:
		return None, None
	image = desktop_windows.print_window_image(hwnd).crop((point[0] - 60, point[1] - 18, point[0] + 60, point[1] + 18))
	if crop_path is not None:
		crop_path.parent.mkdir(parents=True, exist_ok=True)
		image.save(crop_path)
	# <!-- custom: One reference per look of the button at that window size; a build with another theme gets its own file next to the first.
	# With no reference for the window's size the answer is False and nothing is clicked: the second version still clicked then, which Codex (GPT-6.1-Sol)'s second review flagged. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	for reference in sorted(SETUP_OK_DIR.glob("setup_ok_button*_%dx%d.png" % size)):
		difference = ImageStat.Stat(ImageChops.difference(image, Image.open(reference).convert("RGB"))).mean
		if sum(difference) / 3.0 <= SETUP_OK_MAX_DIFFERENCE:
			return point, True
	return point, False


def click_setup_screens(pid, finished, deadline, prefix):
	# <!-- custom: Civ4 opens a scenario with three setup screens (Civilization, Your Details, Game Snapshot), each with OK at the bottom right and the file's own values preselected, so OK is clicked, whenever it is seen, until finished() says the game has started. (Claude code Fable 5.2) -->
	clicks = 0
	unrecognized = 0
	next_click = time.monotonic() + 20
	while not finished():
		if not desktop_windows.process_alive(pid):
			raise SystemExit("Civ4 exited while loading the WorldBuilder file; see PythonErr.log")
		if time.monotonic() > deadline:
			raise SystemExit("no game after %d OK clicks; Civ4 %d left open for inspection" % (clicks, pid))
		# <!-- custom: A click gives Civ4 the keyboard, and the Your Details screen then takes what the user types elsewhere (see the name check in import_world), so it waits until nobody has typed or moved the mouse for 1.5 s, as agent_message.py's pastes do. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		if time.monotonic() >= next_click and desktop_windows.user_idle_seconds() >= 1.5:
			point, seen = setup_ok_button(pid, Path("%s_setup_ok/%02d.png" % (prefix, clicks + unrecognized)))
			if seen:
				desktop_windows.click(pid, point[0], point[1])
				clicks += 1
				# <!-- custom: The pointer leaves the button, whose highlighted look would not match the reference on the next screen. (Claude code Fable 5.2) -->
				desktop_windows.hover(pid, point[0], point[1] - 200)
			elif point is not None:
				unrecognized += 1
				if unrecognized == 30:
					print("no setup screen recognized for a minute; if one is waiting, click its OK by hand. The pictures taken at the button are in %s_setup_ok; one of them can become a reference, setup_ok_button_<name>_<width>x<height>.png in %s" % (prefix, SETUP_OK_DIR), flush=True)
			# <!-- custom: Was 6 s between clicks; 2 s leaves the Leader Name box open for less stray typing. (Claude code Fable 5.2) -->
			next_click = time.monotonic() + 2
		time.sleep(0.5)
	return clicks


def human_problem(human, name, slot):
	# <!-- custom: The Your Details screen's Leader Name box has the keyboard while the setup screens are up: during the second 4986 run the user was typing elsewhere and two letters landed in it, so the human "PC" came out as "PCdo", and "PCor" on the next run.
	# No Python call sets a player's name, so a changed name is reported and the transplant command imports again, up to three times; nothing is saved for a failed attempt, whose save used to stay at the normal output path.
	# The slot is checked too, as names can repeat (Codex (GPT-6.1-Sol)'s reviews). (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	if human is None:
		return None
	if (human.get("name") is not None and name != human["name"]) or slot != human["slot"]:
		return {"source": human, "destination": {"name": name, "slot": slot}}
	return None


def import_world_hook(build, wb, prefix, timeout, keep_techs=None, seeds=None, human=None, map_update=None):
	# <!-- custom: The import for a receiving build without SASPilot: a mod copy whose hook does the work in the game (the exporter's finishImport).
	# The user asked whether a current world could go into base AdvCiv or an older AdvCiv-SAS. (Claude code Fable 5.2) -->
	install_build(None, build)
	prefix = Path(prefix)
	for suffix in (".import.done", ".import.json", "_reexport" + WB_EXT, "_reexport.facts.json", "_reexport.done"):
		leftover = Path(str(prefix) + suffix)
		if leftover.exists():
			leftover.unlink()
	save = Path(str(prefix) + "_T0" + SAVE_EXT)
	request = write_request(build, {"MODE": "import", "OUT_PREFIX": str(prefix), "SAVE_PATH": str(save), "KEEP_GRANTS": keep_techs, "SEEDS": seeds, "MAP_UPDATE": map_update, "HUMAN_NAME": human and human.get("name"), "HUMAN_SLOT": human and human["slot"]})
	ini_name, ini_path = write_ini("SASSaveTransplanter", build)
	pid = desktop_windows.launch_detached('/FXSLOAD="%s" ini=%s' % (wb, ini_name))
	print("receiving build %s: launched pid %d on %s" % (build, pid, wb), flush=True)
	done = Path(str(prefix) + ".import.done")
	try:
		clicks = click_setup_screens(pid, done.exists, time.monotonic() + timeout, prefix)
		time.sleep(1)
	except SystemExit:
		if not desktop_windows.process_alive(pid):
			remove_ini(ini_path)
			remove_request(request)
		raise
	outcome = run_autoplay.close_civ4(pid)
	remove_ini(ini_path)
	remove_request(request)
	result = json.loads(Path(str(prefix) + ".import.json").read_text(encoding="ascii"))
	if result.get("error"):
		raise SystemExit("the import failed in %s:\n%s" % (build, result["error"]))
	result.update({"setupOkClicks": clicks, "civ4": outcome, "reexportWbSave": str(prefix) + "_reexport" + WB_EXT, "reexportFacts": str(prefix) + "_reexport.facts.json"})
	problem = human_problem(human, result.get("humanName"), result.get("activePlayer"))
	if problem:
		result["humanChanged"] = problem
	return result


def import_world(wb, prefix, timeout, keep_open=False, keep_techs=None, seeds=None, human=None, map_update=None):
	# <!-- custom: Starts the current build on the WorldBuilder file, clicks through the setup screens until SASPilot answers from inside the game, and does the rest through SASPilot. (Claude code Fable 5.2) -->
	refuse_running_civ4()
	prefix = Path(prefix)
	session = uuid.uuid4().hex
	ini_name, ini_path = write_ini("SASPilot", run_autoplay.MOD_FOLDER, extra_lines=["[SASPilot]", "On = 1", "Session = %s" % session])
	pid = desktop_windows.launch_detached('/FXSLOAD="%s" ini=%s' % (wb, ini_name))
	print("current build: launched pid %d on %s" % (pid, wb), flush=True)
	hello = SASPilotClient.MAILBOX_ROOT / str(pid) / "hello.json"
	deadline = time.monotonic() + timeout
	clicks = click_setup_screens(pid, lambda: SASPilotClient._hello_session(hello) == session, deadline, prefix)
	state = SASPilotClient.wait_for_turn(pid, max(30.0, deadline - time.monotonic()))
	result = {"setupOkClicks": clicks, "pid": pid, "state": state}
	if human is not None:
		found = SASPilotClient.call(pid, "py", {"code": "[gc.getPlayer(game.getActivePlayer()).getName(), game.getActivePlayer()]"}, 60.0).get("result")
		problem = human_problem(human, found[0], found[1])
		if problem:
			result["humanChanged"] = problem
			result["civ4"] = SASPilotClient.close(pid)["civ4"]
			return result
	if keep_techs is not None:
		# <!-- custom: --free-grants source: remove the techs and promotions the scenario start added beyond the source's own. (Claude code Fable 5.2) -->
		code = exporter_import() + "result = %s.keepSourceGrants(%r, %r)\n" % (EXPORTER, keep_techs[0], keep_techs[1])
		result["grantsRemovedAfterLoad"] = SASPilotClient.call(pid, "py", {"code": code}, 120.0).get("result")
	if seeds is not None:
		# <!-- custom: --seeds source: both generators continue from the source game's states, so the same transplant always gives the same game.
		# Whether that game then matches the source's own continuation is a separate question; see README_SASSaveTransplanter.md. (Claude code Fable 5.2) -->
		code = "game.getSorenRand().init(%d)\ngame.getMapRand().init(%d)\nresult = [game.getSorenRand().getSeed(), game.getMapRand().getSeed()]\n" % (seeds[0], seeds[1])
		result["seedsSet"] = SASPilotClient.call(pid, "py", {"code": code}, 120.0).get("result")
	if map_update is not None:
		code = exporter_import() + "result = %s.updateMap(%r, %r)\n" % (EXPORTER, map_update[0], map_update[1])
		result["mapUpdate"] = SASPilotClient.call(pid, "py", {"code": code}, 300.0).get("result")
		if not isinstance(result["mapUpdate"], dict):
			result["civ4"] = SASPilotClient.close(pid)["civ4"]
			raise SystemExit("the map update failed in the current build:\n%s" % (result["mapUpdate"],))
	reply = SASPilotClient.call(pid, "py", {"code": exporter_code(str(prefix) + "_reexport", False)}, 300.0)
	if reply.get("result"):
		raise SystemExit("the re-export failed in the current build:\n%s" % reply.get("result"))
	save = Path(str(prefix) + "_T0" + SAVE_EXT)
	SASPilotClient.call(pid, "save", {"path": str(save), "overwrite": True}, 120.0)
	result.update({"save": str(save), "reexportWbSave": str(prefix) + "_reexport" + WB_EXT, "reexportFacts": str(prefix) + "_reexport.facts.json"})
	if not keep_open:
		result["civ4"] = SASPilotClient.close(pid)["civ4"]
	return result


def compare_facts(source_path, destination_path):
	# <!-- custom: The WorldBuilder comparison only sees what that format holds.
	# The facts files add what each build computed from it: yields under its own rules, area sizes, who is human, each player's units.
	# Differences here are expected across versions (a terrain's yield changed) and are listed, not failed: they say what the new rules made of the old world. (Claude code Fable 5.2) -->
	source = json.loads(Path(source_path).read_text(encoding="ascii"))
	destination = json.loads(Path(destination_path).read_text(encoding="ascii"))
	report = {"game": {}, "players": [], "plotColumnsChanged": {}, "plotExamples": []}
	for key in sorted(set(source.get("game", {})) | set(destination.get("game", {}))):
		before, after = source.get("game", {}).get(key), destination.get("game", {}).get(key)
		if before != after:
			report["game"][key] = {"source": before, "destination": after}
	by_id = dict((player["id"], player) for player in destination.get("players", []))
	for player in source.get("players", []):
		other = by_id.pop(player["id"], None)
		if other is None:
			report["players"].append({"id": player["id"], "missingInDestination": True})
			continue
		changed = dict((key, {"source": player.get(key), "destination": other.get(key)}) for key in sorted(set(player) | set(other)) if player.get(key) != other.get(key))
		if changed:
			report["players"].append({"id": player["id"], "changed": changed})
	for player_id in sorted(by_id):
		report["players"].append({"id": player_id, "missingInSource": True})
	columns = source.get("plotColumns", [])
	if columns != destination.get("plotColumns"):
		report["plotColumnsDiffer"] = True
		return report
	plots = dict(((row[0], row[1]), row) for row in destination.get("plots", []))
	changed = collections.Counter()
	transitions = collections.Counter()
	for row in source.get("plots", []):
		other = plots.get((row[0], row[1]))
		if other is None:
			changed["(missing plot)"] += 1
			continue
		for index, name in enumerate(columns):
			if row[index] != other[index]:
				changed[name] += 1
				if name in ("food", "production", "commerce"):
					transitions["%s %s/%s/%s: %s %s -> %s" % (row[columns.index("terrain")], row[columns.index("feature")], row[columns.index("bonus")], row[columns.index("improvement")], name, row[index], other[index])] += 1
				elif len(report["plotExamples"]) < 40:
					report["plotExamples"].append({"x": row[0], "y": row[1], "column": name, "source": row[index], "destination": other[index]})
	report["plotColumnsChanged"] = dict(changed)
	report["plotCount"] = {"source": len(source.get("plots", [])), "destination": len(destination.get("plots", []))}
	report["yieldChangesByPlotKind"] = dict(transitions.most_common())
	return report


def read_facts(path):
	return json.loads(Path(path).read_text(encoding="ascii"))


def team_blocks(lines):
	# <!-- custom: Yields (first, last) line indexes of each BeginTeam..EndTeam block, in team order. (Claude code Fable 5.2) -->
	start = None
	for index, line in enumerate(lines):
		if line.strip() == "BeginTeam":
			start = index
		elif line.strip() == "EndTeam" and start is not None:
			yield start, index
			start = None


def drop_source_free_techs(wb_path, facts):
	# <!-- custom: A scenario start gives each team the techs in the file plus the free techs of its members' civilizations under the loading build's XML.
	# The first 4986 transplant therefore gave Benin Mysticism and Fishing (4986) plus Pottery (current), a start neither build would deal.
	# So the techs that were the source build's civilization free techs leave the file, the current build adds its own, and techs from another origin, such as a handicap's AI techs, stay.
	# --techs source keeps the file as it is and removes the added ones after the load instead. (Claude code Fable 5.2) -->
	free = collections.defaultdict(set)
	for player in facts.get("players", []):
		free[player["team"]].update(player.get("civFreeTechs", []))
	lines = Path(wb_path).read_text(encoding="latin-1").splitlines(True)
	dropped = {}
	remove = set()
	for start, end in team_blocks(lines):
		team = None
		for index in range(start, end):
			text = lines[index].strip()
			if text.startswith("TeamID="):
				team = int(text.split("=", 1)[1])
			elif text.startswith("Tech=") and team is not None and text.split("=", 1)[1] in free.get(team, ()):
				remove.add(index)
				dropped.setdefault(str(team), []).append(text.split("=", 1)[1])
	Path(wb_path).write_bytes("".join(line for index, line in enumerate(lines) if index not in remove).encode("latin-1"))
	return dropped


def drop_source_free_promotions(wb_path, facts):
	# <!-- custom: The same for promotions: those the source build gave a unit for free, by its type or its leader's traits, leave the file, and the current build gives its own when it creates the unit.
	# Earned promotions stay. (Claude code Fable 5.2) -->
	free = dict((player["id"], player.get("freePromotionsByUnit", {})) for player in facts.get("players", []))
	lines = Path(wb_path).read_text(encoding="latin-1").splitlines(True)
	dropped = collections.Counter()
	remove = set()
	unit_free = None
	owner = None
	for index, line in enumerate(lines):
		text = line.strip()
		if text.startswith("UnitType="):
			fields = dict(part.strip().split("=", 1) for part in text.split(","))
			owner = int(fields["UnitOwner"])
			unit_free = set(free.get(owner, {}).get(fields["UnitType"], []))
		elif text == "EndUnit":
			unit_free = None
		elif text.startswith("PromotionType=") and unit_free is not None and text.split("=", 1)[1] in unit_free:
			remove.add(index)
			dropped["player %d %s" % (owner, text.split("=", 1)[1])] += 1
	Path(wb_path).write_bytes("".join(line for index, line in enumerate(lines) if index not in remove).encode("latin-1"))
	return dict(dropped)


def explain_units(source, destination, policy, renames):
	# <!-- custom: Says for each player whether every unit is where it was with the promotions the policy predicts; unit types are compared after the renames, as the source facts hold the old names. (Claude code Fable 5.2) -->
	rows = []
	after = dict((player["id"], player) for player in destination.get("players", []))
	for player in source.get("players", []):
		other = after.get(player["id"])
		if other is None:
			continue
		old_free = player.get("freePromotionsByUnit", {})
		expected = []
		for unit in player.get("units", []):
			unit_type = renames.get(unit[2], unit[2])
			promotions = set(unit[6])
			if policy == "current":
				promotions -= set(old_free.get(unit[2], []))
			expected.append([unit[0], unit[1], unit_type, sorted(promotions)])
		# <!-- custom: Under "current" the receiving build's own free promotions are not predicted, only listed: its facts are taken from the game that gets saved, where no probe unit may be created.
		# A unit matches when it stands where it stood with at least the promotions it should keep. (Claude code Fable 5.2) -->
		found = [[unit[0], unit[1], unit[2], sorted(unit[6])] for unit in other.get("units", [])]
		left = list(found)
		unexpected = []
		added = collections.Counter()
		for unit in expected:
			match = None
			for candidate in left:
				if candidate[:3] == unit[:3] and (candidate[3] == unit[3] or (policy == "current" and set(unit[3]) <= set(candidate[3]))):
					match = candidate
					break
			if match is None:
				unexpected.append({"missing": unit})
			else:
				left.remove(match)
				for name in set(match[3]) - set(unit[3]):
					added["%s %s" % (unit[2], name)] += 1
		unexpected += [{"extra": unit} for unit in left]
		rows.append({"id": player["id"], "units": len(found), "asExpected": not unexpected, "unexpected": unexpected, "promotionsAddedByCurrentRules": dict(added)})
	return rows


def explain_plots(source, destination, renames, update):
	# <!-- custom: Every plot must be as it was, except for renamed types and, in the "update" variant, the feature and bonus the map update reported for that very plot; was a set of added type names valid on any plot that held none, so a new type could have appeared where the update never put it. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	columns = source.get("plotColumns", [])
	kept = [columns.index(name) for name in ("plotType", "terrain", "improvement", "route", "river", "areaTiles", "startingPlot")]
	feature, bonus = columns.index("feature"), columns.index("bonus")
	after = dict(((row[0], row[1]), row) for row in destination.get("plots", []))
	announced = dict(((change[0], change[1]), {feature: change[5], bonus: change[7]}) for change in (update or {}).get("changes", []))
	unexpected = []
	counts = collections.Counter()
	for row in source.get("plots", []):
		other = after.get((row[0], row[1]))
		problem = other is None or any(row[index] != other[index] for index in kept)
		if not problem:
			for index in (feature, bonus):
				before = renames.get(row[index], row[index])
				if before != other[index]:
					if announced.get((row[0], row[1]), {}).get(index) == other[index]:
						counts[other[index]] += 1
					else:
						problem = True
		if problem and len(unexpected) < 40:
			unexpected.append({"source": row, "destination": other})
		elif problem:
			counts["(further unexpected plots)"] += 1
	return {"asExpected": not unexpected, "plots": len(after), "updatedPlotsByType": dict(counts), "unexpected": unexpected}


def judge_map_update(update, facts, out_path):
	# <!-- custom: Checks what the map update reported against what it is allowed to do: put a new feature type on a plot without one and a new bonus type on a plot without one, nothing else.
	# Writes those plots' expected WorldBuilder lines for SASSaveTransplanterWorld.py compare --allowed-plot-changes, which then compares every plot in full.
	# The first version waived every "plot payload" difference of the WorldBuilder comparison whenever the smaller facts comparison passed, so a changed river direction on a plot that stayed a river plot would have passed (Codex (GPT-6.1-Sol)'s 2026-11-16 review). (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	new_features, new_bonuses = set(update.get("newFeatureTypes", [])), set(update.get("newBonusTypes", []))
	allowed = {}
	unexpected = []
	for x, y, feature_before, variety_before, bonus_before, feature_after, variety_after, bonus_after in update.get("changes", []):
		added = []
		fine = True
		if (feature_before, variety_before) != (feature_after, variety_after):
			fine = feature_before is None and feature_after in new_features
			added.append("FeatureType=%s,FeatureVariety=%d" % (feature_after, variety_after))
		if bonus_before != bonus_after:
			fine = fine and bonus_before is None and bonus_after in new_bonuses
			added.append("BonusType=%s" % bonus_after)
		if fine:
			allowed["%d,%d" % (x, y)] = {"removed": [], "added": added}
		else:
			unexpected.append([x, y, feature_before, variety_before, bonus_before, feature_after, variety_after, bonus_after])
	out_path.write_text(json.dumps(allowed, indent=1), encoding="utf-8")
	# <!-- custom: A map-wide count can look fine while one start gets most of the new resources (Codex (GPT-6.1-Sol)), so the additions inside each start's 21 city plots are listed per player. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	game = facts.get("game", {})
	width, height = game.get("gridWidth", 0), game.get("gridHeight", 0)
	near = []
	for player in facts.get("players", []):
		start = player.get("startingPlot")
		if not start:
			continue
		found = collections.Counter()
		for change in update.get("changes", []):
			dx, dy = abs(change[0] - start[0]), abs(change[1] - start[1])
			if game.get("wrapX") and width:
				dx = min(dx, width - dx)
			if game.get("wrapY") and height:
				dy = min(dy, height - dy)
			if dx <= 2 and dy <= 2 and dx + dy < 4:
				for before, after in ((change[2], change[5]), (change[4], change[7])):
					if after is not None and after != before:
						found[after] += 1
		near.append({"id": player["id"], "civilization": player.get("civilization"), "start": start, "addedInCityPlots": dict(found)})
	return {"asExpected": not unexpected, "unexpected": unexpected[:40], "allowedPlotChanges": str(out_path), "plotsChanged": len(update.get("changes", [])), "nearStarts": near}


def map_script_overrides(name):
	# <!-- custom: The map update uses the current build's general placement: the Marsh fractal and the DLL's bonus placement.
	# A map script can replace either on a new map (addFeatures, addBonuses, addBonusType), and whether the source's script did is not carried over, so the report says which of them the script of that name defines today. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	for folder in (run_autoplay.REPO_ROOT / "PrivateMaps", BTS_DIR / "PublicMaps", BTS_DIR / "PrivateMaps", CIV4_DIR / "PublicMaps"):
		script = folder / (str(name) + ".py")
		if script.is_file():
			text = script.read_text(encoding="latin-1")
			return {"script": name, "file": str(script), "defines": [callback for callback in ("addFeatures", "addBonuses", "addBonusType") if re.search(r"^def %s\b" % callback, text, re.MULTILINE)]}
	return {"script": name, "file": None, "defines": []}


def audit_map_types(source, destination, renames):
	# <!-- custom: Which plot-content types the current build has that the source build lacked, per kind.
	# Features and bonuses are placed by the "update" variant; a new terrain, improvement or route is only listed, as nothing says which existing plots should change (the user's question, 2026-11-16). (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	audit = {}
	for kind in ("terrainTypes", "featureTypes", "bonusTypes", "improvementTypes", "routeTypes"):
		before = source.get("game", {}).get(kind)
		after = destination.get("game", {}).get(kind)
		if before is None or after is None:
			audit[kind] = {"unknown": True}
			continue
		before = set(renames.get(name, name) for name in before)
		audit[kind] = {"newInCurrentBuild": sorted(set(after) - before), "goneFromCurrentBuild": sorted(before - set(after))}
	return audit


def require_free_promotion_probes(facts):
	# <!-- custom: --free-grants current removes each unit's source-build free promotions, which the export finds with probe units.
	# A failed probe used to count as "no free promotions", so an old free promotion would have stayed on the unit and passed (Codex (GPT-6.1-Sol)'s 2026-11-16 review); now the run stops. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	lacking = []
	for player in facts.get("players", []):
		probed = player.get("freePromotionsByUnit")
		for unit_type in sorted(set(unit[2] for unit in player.get("units", []))):
			if probed is None or unit_type not in probed:
				lacking.append("player %d %s" % (player["id"], unit_type))
		if "units" not in player:
			lacking.append("player %d (no unit list)" % player["id"])
	if lacking:
		raise SystemExit("the source build did not report free promotions for: %s; see \"missing\" in source.facts.json, or use --free-grants source" % ", ".join(lacking))


def restrict_human(wb_path, slot):
	# <!-- custom: The scenario's Civilization screen preselects the first playable slot, and the unattended import only clicks OK.
	# For a source whose human was another slot, every other slot is marked unplayable so that the list holds only that one; the AIs still play their slots. (Claude code Fable 5.2) -->
	lines = Path(wb_path).read_text(encoding="latin-1").splitlines(True)
	player = -1
	changed = 0
	for index, line in enumerate(lines):
		if line.strip() == "BeginPlayer":
			player += 1
		elif line.strip() == "PlayableCiv=1" and player != slot:
			lines[index] = line.replace("PlayableCiv=1", "PlayableCiv=0")
			changed += 1
	Path(wb_path).write_bytes("".join(lines).encode("latin-1"))
	return changed


def explain_techs(source, destination, policy):
	# <!-- custom: Says for each player whether its turn-0 techs are what the chosen policy predicts, so a tech difference in the facts comparison is either explained here or a real finding. (Claude code Fable 5.2) -->
	rows = []
	after = dict((player["id"], player) for player in destination.get("players", []))
	# <!-- custom: Techs belong to teams: a team has the free techs of all its members' civilizations.
	# Was each player's own civilization only, which Codex (GPT-6.1-Sol)'s 2026-11-16 review showed failing both players of a correct two-player team. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	old_free, new_free = collections.defaultdict(set), collections.defaultdict(set)
	for player in source.get("players", []):
		old_free[player.get("team")].update(player.get("civFreeTechs", []))
	for player in destination.get("players", []):
		new_free[player.get("team")].update(player.get("civFreeTechs", []))
	for player in source.get("players", []):
		other = after.get(player["id"])
		if other is None:
			continue
		before = set(player.get("techs", []))
		if policy == "current":
			expected = (before - old_free[player.get("team")]) | new_free[other.get("team")]
		else:
			expected = before
		found = set(other.get("techs", []))
		rows.append({"id": player["id"], "civilization": player.get("civilization"), "source": sorted(before), "destination": sorted(found), "asExpected": expected == found, "unexpected": sorted(found ^ expected)})
	return rows


def run_helper(arguments):
	completed = subprocess.run([sys.executable, str(HERE / "SASSaveTransplanterWorld.py")] + [str(a) for a in arguments], capture_output=True, text=True)
	print(completed.stdout, end="")
	if completed.stderr:
		print(completed.stderr, end="", file=sys.stderr)
	return completed.returncode


def xml_roots(build):
	# <!-- custom: Low to high load precedence, as SASSaveTransplanterWorld.py asks: Civ4, Warlords, BtS, then the receiving mod. (Claude code Fable 5.2) -->
	return [CIV4_DIR / "Assets" / "XML", CIV4_DIR / "Warlords" / "Assets" / "XML", BTS_DIR / "Assets" / "XML", MODS_DIR / build / "Assets" / "XML"]


def check_outputs(save, out, variants, overwrite):
	# <!-- custom: Before anything is launched: the final save was still written with overwrite, so transplanting an earlier run's preserve_T0 into the same folder would have replaced the input before any check (Codex (GPT-6.1-Sol)'s second review).
	# The input may not be one of this run's saves, hard links included, and an earlier run's save is only replaced with --overwrite. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	for name in variants:
		planned = out / (name + "_T0" + SAVE_EXT)
		if planned.exists():
			if os.path.samefile(planned, save):
				raise SystemExit("the input save %s is where this run would write its result; choose another --out" % save)
			if not overwrite:
				raise SystemExit("%s exists from an earlier run; pass --overwrite to replace it, or choose another --out" % planned)


def rename_facts(facts, renames, drops):
	# <!-- custom: The source facts with every type name as the receiving build knows it, and the types of the mapping's "drop" list taken out, as drop_types takes them out of the WorldBuilder file. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	def deep(value):
		if isinstance(value, str):
			return renames.get(value, value)
		if isinstance(value, list):
			return [deep(item) for item in value]
		if isinstance(value, dict):
			return dict((deep(key), deep(item)) for key, item in value.items())
		return value

	facts = deep(facts)
	if drops:
		columns = facts.get("plotColumns", [])
		for row in facts.get("plots", []):
			for name in ("feature", "bonus", "improvement", "route"):
				if row[columns.index(name)] in drops:
					row[columns.index(name)] = None
		for player in facts.get("players", []):
			for key in ("techs", "civFreeTechs"):
				if key in player:
					player[key] = [name for name in player[key] if name not in drops]
			for unit in player.get("units", []):
				unit[6] = [name for name in unit[6] if name not in drops]
			for unit_type in player.get("freePromotionsByUnit", {}):
				player["freePromotionsByUnit"][unit_type] = [name for name in player["freePromotionsByUnit"][unit_type] if name not in drops]
		for key in ("featureTypes", "bonusTypes", "terrainTypes", "improvementTypes", "routeTypes"):
			if key in facts.get("game", {}):
				facts["game"][key] = [name for name in facts["game"][key] if name not in drops]
	return facts


def drop_types(wb_in, wb_out, drops):
	# <!-- custom: For a receiving build that lacks some of the source's types, such as base AdvCiv without Marsh, Peat and Camel: the mapping file's "drop" list names types whose plot feature, bonus, improvement or route, unit promotion or team tech line is left out, each counted in the report.
	# A type used anywhere else, such as a civic or a leader, cannot be dropped and still needs a mapping. (Claude code Fable 5.2) -->
	dropped = collections.Counter()
	kept = []
	for line in Path(wb_in).read_text(encoding="latin-1").splitlines(True):
		key, _, rest = line.strip().partition("=")
		value = rest.split(",")[0].strip()
		if key in ("BonusType", "FeatureType", "ImprovementType", "RouteType", "PromotionType", "Tech") and value in drops:
			dropped[value] += 1
		else:
			kept.append(line)
	Path(wb_out).write_bytes("".join(kept).encode("latin-1"))
	return dict(dropped)


def named_blocks(lines, name):
	# <!-- custom: (first, last) line indexes of each Begin<name>..End<name> block, in order. (Claude code Fable 5.2) -->
	start = None
	for index, line in enumerate(lines):
		if line.strip() == "Begin" + name:
			start = index
		elif line.strip() == "End" + name and start is not None:
			yield start, index
			start = None


def trim_unused_slots(wb_path):
	# <!-- custom: Current AdvCiv-SAS writes 48 team and 48 player blocks, base AdvCiv has 18 slots.
	# A reader pads a file with fewer blocks (advc.056), so the unused blocks after the last used one are cut; a used slot is never moved, as Codex (GPT-6.1-Sol) advised, and anything that names a cut slot stops the run. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	lines = Path(wb_path).read_text(encoding="latin-1").splitlines(True)
	teams, players = list(named_blocks(lines, "Team")), list(named_blocks(lines, "Player"))

	def values(block, key):
		return [line.strip().split("=", 1)[1] for line in lines[block[0]:block[1]] if line.strip().startswith(key + "=")]

	used_players = [index for index, block in enumerate(players) if any(value != "NONE" for value in values(block, "LeaderType") + values(block, "CivType"))]
	keep_players = max(used_players) + 1 if used_players else 0
	keep_teams = max([int(value) for index in used_players for value in values(players[index], "Team")] + [-1]) + 1
	problems = []
	for index, block in enumerate(teams[keep_teams:]):
		if values(block, "Tech"):
			problems.append("team block %d has techs" % (keep_teams + index))
	for line in lines:
		text = line.strip()
		for key, limit in (("UnitOwner", keep_players), ("CityOwner", keep_players)):
			for part in text.split(","):
				if part.strip().startswith(key + "=") and int(part.split("=", 1)[1]) >= limit:
					problems.append(text)
		if text.startswith("TeamReveal=") and any(int(value) >= keep_teams for value in text.split("=", 1)[1].split(",") if value.strip()):
			problems.append(text)
	if problems:
		raise SystemExit("unused player slots cannot be trimmed, as the file names slots beyond the last used one: %s" % "; ".join(problems[:10]))
	cut = set()
	for start, end in teams[keep_teams:] + players[keep_players:]:
		cut.update(range(start, end + 1))
	Path(wb_path).write_bytes("".join(line for index, line in enumerate(lines) if index not in cut).encode("latin-1"))
	return {"teamBlocks": [len(teams), keep_teams], "playerBlocks": [len(players), keep_players]}


def command_export(args):
	if args.build != run_autoplay.MOD_FOLDER:
		install_build(args.release_tree, args.build)
	print(json.dumps(export_world(args.build, args.save.resolve(), args.prefix.resolve(), args.timeout), indent=1))
	return 0


def command_import(args):
	print(json.dumps(import_world(args.wb.resolve(), args.prefix.resolve(), args.timeout, args.keep_open), indent=1))
	return 0


def command_facts(args):
	report = compare_facts(args.source, args.destination)
	text = json.dumps(report, indent=1)
	if args.report:
		args.report.write_text(text, encoding="utf-8")
	print(text)
	return 0


def finish_variant(args, out, name, candidate_wb, source_facts, renames, keep, seeds, human, map_update):
	# <!-- custom: One receiving game: import, save, re-export and judge.
	# The user suggested making both worlds by default, the one kept as it was and the one with the current build's new map content, since which is wanted depends on the test; each is a variant with its own save and its own verdict. (Claude code Fable 5.2) -->
	steps = {}
	for attempt in range(3):
		if args.destination == run_autoplay.MOD_FOLDER:
			steps["import"] = import_world(candidate_wb, out / name, args.timeout, keep_techs=keep, seeds=seeds, human=human, map_update=map_update)
		else:
			steps["import"] = import_world_hook(args.destination, candidate_wb, out / name, args.timeout, keep_techs=keep, seeds=seeds, human=human, map_update=map_update)
		steps["import"]["attempt"] = attempt + 1
		if "humanChanged" not in steps["import"]:
			break
		print("the human's name or slot changed during setup (%r); importing again" % (steps["import"]["humanChanged"],), flush=True)
	if "humanChanged" in steps["import"]:
		# <!-- custom: Nothing was saved for this variant; see human_problem. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		steps["outcome"] = "FAILED"
		return 4, steps
	compare = ["compare", candidate_wb, out / (name + "_reexport" + WB_EXT), "--report", out / (name + ".roundtrip.json")] + (["--ignore-free-grants"] if args.free_grants == "current" else [])
	update = steps["import"].get("mapUpdate")
	if update is not None:
		steps["mapUpdate"] = judge_map_update(update, source_facts, out / (name + ".allowed_plot_changes.json"))
		steps["mapUpdate"]["mapScript"] = map_script_overrides(source_facts.get("game", {}).get("mapScript"))
		compare += ["--allowed-plot-changes", steps["mapUpdate"]["allowedPlotChanges"]]
	code = run_helper(compare)
	steps["worldBuilderCompare"] = {"exitCode": code, "report": str(out / (name + ".roundtrip.json"))}
	destination_facts = read_facts(out / (name + "_reexport.facts.json"))
	steps["factsCompare"] = compare_facts(out / "source.facts.json", out / (name + "_reexport.facts.json"))
	steps["mapTypes"] = audit_map_types(source_facts, destination_facts, renames)
	steps["techs"] = {"policy": args.free_grants, "players": explain_techs(source_facts, destination_facts, args.free_grants)}
	steps["plots"] = explain_plots(source_facts, destination_facts, renames, update)
	steps["units"] = {"policy": args.free_grants, "players": explain_units(source_facts, destination_facts, args.free_grants, renames)}
	# <!-- custom: A variant succeeds only if the world came back as it went in, apart from what the map update announced, and every player's techs and units are what the policy predicts. (Claude code Fable 5.2) -->
	if not steps["plots"]["asExpected"] or not all(row["asExpected"] for step in ("techs", "units") for row in steps[step]["players"]) or (update is not None and not steps["mapUpdate"]["asExpected"]):
		code = code or 3
	if args.verify_load:
		# <!-- custom: The new save is loaded once more by the receiving build and exported again, and that world must equal the one exported before saving: Codex (GPT-6.1-Sol) suggested reopening the save before calling it good. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		export_world(args.destination, out / (name + "_T0" + SAVE_EXT), out / (name + "_loadcheck"), args.timeout)
		load_code = run_helper(["compare", out / (name + "_reexport" + WB_EXT), out / (name + "_loadcheck" + WB_EXT), "--ignore-player-names", "--report", out / (name + ".loadcheck.json")])
		steps["loadCheck"] = {"exitCode": load_code, "report": str(out / (name + ".loadcheck.json"))}
		code = code or load_code
	steps["outcome"] = code == 0 and "SUCCEEDED" or "DIFFERENCES"
	return code, steps


def command_transplant(args):
	out = args.out.resolve()
	out.mkdir(parents=True, exist_ok=True)
	report = {"format": "SASSaveTransplanterReport", "formatVersion": 2, "startedUtc": utc_stamp(), "steps": {}, "variants": {}}
	variants = [name for name in ("preserve", "update") if args.map_variants in ("both", name)]
	check_outputs(args.save.resolve(), out, variants, args.overwrite)
	if args.build != run_autoplay.MOD_FOLDER:
		install_build(args.release_tree, args.build)
	if args.destination != run_autoplay.MOD_FOLDER:
		install_build(args.destination_release_tree, args.destination)
	report["steps"]["export"] = export_world(args.build, args.save.resolve(), out / "source", args.timeout)
	source_wb = out / ("source" + WB_EXT)
	candidate_wb = out / ("transplant" + WB_EXT)
	mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8")) if args.mapping else {}
	renames, drops = mapping.get("types", {}), set(mapping.get("drop", []))
	if drops:
		report["steps"]["typesDropped"] = drop_types(source_wb, out / ("source_dropped" + WB_EXT), drops)
		source_wb = out / ("source_dropped" + WB_EXT)
	arguments = ["transplant", source_wb, "--output", candidate_wb, "--overwrite", "--report", out / "transplant.types.json", "--source-build", args.build, "--destination-build", args.destination_label or args.destination]
	for root in xml_roots(args.destination):
		arguments += ["--dest-xml-root", root]
	if args.mapping:
		arguments += ["--mapping", args.mapping]
	code = run_helper(arguments)
	report["steps"]["typeCheck"] = {"exitCode": code, "report": str(out / "transplant.types.json")}
	if code == 0:
		# <!-- custom: The facts are read in the receiving build's names.
		# They used to keep the source's names while the WorldBuilder file had the new ones, with a rename applied here and there; Codex (GPT-6.1-Sol)'s second review showed both free-grant removals then finding nothing for a renamed unit, tech or promotion. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		source_facts = rename_facts(read_facts(out / "source.facts.json"), renames, drops)
		if args.destination != run_autoplay.MOD_FOLDER:
			report["steps"]["unusedSlotsTrimmed"] = trim_unused_slots(candidate_wb)
		keep = None
		if args.free_grants == "current":
			require_free_promotion_probes(source_facts)
			report["steps"]["sourceFreeTechsDropped"] = drop_source_free_techs(candidate_wb, source_facts)
			report["steps"]["sourceFreePromotionsDropped"] = drop_source_free_promotions(candidate_wb, source_facts)
		else:
			techs = collections.defaultdict(set)
			for player in source_facts.get("players", []):
				techs[player["team"]].update(player.get("techs", []))
			keep = (dict((team, sorted(names)) for team, names in techs.items()), dict((player["id"], [[unit[0], unit[1], renames.get(unit[2], unit[2]), unit[6]] for unit in player.get("units", [])]) for player in source_facts.get("players", [])))
		seeds = None
		game_facts = source_facts.get("game", {})
		if args.seeds == "source" and "syncRandSeed" in game_facts and "mapRandSeed" in game_facts:
			seeds = (game_facts["syncRandSeed"], game_facts["mapRandSeed"])
		human = game_facts.get("activePlayer", 0)
		if args.human_slot is not None:
			human = args.human_slot
		if human != min([player["id"] for player in source_facts.get("players", [])] or [0]):
			report["steps"]["humanSlot"] = {"slot": human, "otherSlotsMadeUnplayable": restrict_human(candidate_wb, human)}
		human_name = None
		for player in source_facts.get("players", []):
			if player["id"] == human and player.get("human"):
				human_name = player.get("name")
		human = {"slot": human, "name": human_name}
		source_types = ([renames.get(name, name) for name in game_facts.get("featureTypes", [])], [renames.get(name, name) for name in game_facts.get("bonusTypes", [])])
		# <!-- custom: "preserve" is the world as it was and "update" the one where the current build also placed its new feature and bonus types; the save of each is <name>_T0.CivBeyondSwordSave.
		# Were "transplant" and "transplant_new_content" under --new-content keep/add: the user found "content" vague, as it could mean units, and Codex (GPT-6.1-Sol) proposed naming what each choice produces. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		for name, map_update in (("preserve", None), ("update", source_types)):
			if name not in variants:
				continue
			variant_code, report["variants"][name] = finish_variant(args, out, name, candidate_wb, source_facts, renames, keep, seeds, human, map_update)
			code = code or variant_code
	report["outcome"] = code == 0 and "SUCCEEDED" or "DIFFERENCES"
	report["endedUtc"] = utc_stamp()
	(out / "transplant.report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
	for name in sorted(report["variants"]):
		variant = report["variants"][name]
		update = variant["import"].get("mapUpdate") or {}
		print("%s: %s; save %s%s" % (name, variant["outcome"], variant["import"].get("save"), update and "; added %s, not placed %s" % (update.get("counts"), update.get("notPlaced")) or ""))
	print("wrote %s" % (out / "transplant.report.json"))
	return code


def main():
	parser = argparse.ArgumentParser(description="Recreate an old save's turn-0 world as a new save of the current build.")
	commands = parser.add_subparsers(dest="command", required=True)
	inventory = commands.add_parser("inventory", help="count saves by the mod folder their header names")
	inventory.add_argument("folders", nargs="+", type=Path)
	inventory.add_argument("--report", type=Path, help="write every save's mod, size and time as JSON")
	inventory.set_defaults(run=command_inventory)
	export = commands.add_parser("export", help="load a save in the build that wrote it and write its world as WorldBuilder text plus facts")
	transplant = commands.add_parser("transplant", help="export, check type names, import into the current build, save and compare")
	for sub in (export, transplant):
		sub.add_argument("save", type=Path, help="the old save; it is only read")
		sub.add_argument("--build", required=True, help="the source build's folder name under Mods, e.g. AdvCiv-SAS-4986")
		sub.add_argument("--release-tree", type=Path, help="an extracted release to install as --build when that folder does not exist yet")
		sub.add_argument("--timeout", type=float, default=600.0)
	export.add_argument("--prefix", type=Path, required=True, help="output path without extension")
	export.set_defaults(run=command_export)
	transplant.add_argument("--out", type=Path, required=True, help="output folder")
	transplant.add_argument("--mapping", type=Path, help="JSON old-type to new-type mapping for SASSaveTransplanterWorld.py")
	transplant.add_argument("--destination-label", help="the receiving build's name in the reports; default --destination")
	transplant.add_argument("--destination", default=run_autoplay.MOD_FOLDER, help="the receiving build's folder name under Mods; default the current mod. Another build must be a copy made by install-mod-copy, and its import runs through the hook, without SASPilot")
	transplant.add_argument("--destination-release-tree", type=Path, help="an extracted release or a mod folder to install as --destination when that folder does not exist yet")
	transplant.add_argument("--overwrite", action="store_true", help="replace the saves an earlier run left in --out")
	transplant.add_argument("--no-verify-load", dest="verify_load", action="store_false", help="skip loading each new save once more in the receiving build and comparing its world again")
	transplant.add_argument("--free-grants", choices=("current", "source"), default="current", help="current: civilizations' free techs and units' free promotions come from the current build's rules in place of the source build's; source: exactly the source's techs and promotions")
	transplant.add_argument("--map-variants", choices=("both", "preserve", "update"), default="both", help="preserve: the map exactly as it was; update: the current build also places the map feature and resource types the source build did not have, such as Marsh, Peat and Camel, on plots that hold none; both: one save of each. Renamed types are mapped either way")
	transplant.add_argument("--seeds", choices=("source", "new"), default="source", help="source: the random generators continue from the source game's states; new: the states the scenario start drew")
	transplant.add_argument("--human-slot", type=int, help="the player slot the human takes; default the source save's active player")
	transplant.set_defaults(run=command_transplant)
	importer = commands.add_parser("import", help="start the current build on a WorldBuilder file, save it and re-export it")
	importer.add_argument("wb", type=Path)
	importer.add_argument("--prefix", type=Path, required=True)
	importer.add_argument("--timeout", type=float, default=600.0)
	importer.add_argument("--keep-open", action="store_true")
	importer.set_defaults(run=command_import)
	# <!-- custom: The mod copy alone, without the export hook: Codex (GPT-6.1-Sol) proposed it so that an old build can also be installed for a manual bisect, with one implementation. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	mod_copy = commands.add_parser("install-mod-copy", help="install an extracted release under Mods with another folder name, to run it beside the current mod")
	mod_copy.add_argument("release_tree", type=Path, help="the extracted release; it is only read")
	mod_copy.add_argument("name", help="the copy's folder name under Mods, e.g. AdvCiv-SAS-4986")
	mod_copy.add_argument("--dry-run", action="store_true", help="say what would be copied and rewritten, and write nothing")
	mod_copy.set_defaults(run=lambda args: print(json.dumps(install_mod_copy(args.release_tree, args.name, args.dry_run), indent=1)) or 0)
	facts = commands.add_parser("facts", help="compare two facts files")
	facts.add_argument("source", type=Path)
	facts.add_argument("destination", type=Path)
	facts.add_argument("--report", type=Path)
	facts.set_defaults(run=command_facts)
	args = parser.parse_args()
	return args.run(args)


if __name__ == "__main__":
	sys.exit(main())

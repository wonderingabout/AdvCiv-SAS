#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build the DLL through build_with_report.ps1, install it into Assets, or syntax-check C++ files with VC2003's cl.exe /Zs, from any shell.

# <!-- custom: build_with_report.ps1 needs the Visual C++ 2010 environment from vcvars32.bat, which an agent's shell lacks: started bare, a build failed within 4 s on 2026-11-13 with cmd's "not recognized as a command" and no compiler line.
# Agents therefore wrote a one-off .bat into their session scratchpad each time (build_debugopt.bat, build_release.bat, zs.bat), which the next session could not see; this helper replaces them.
# The build runs under cmd.exe, as Git Bash's PATH would put Unix find ahead of the one the Makefile's FIND step expects. (Claude code Opus 5.5) -->
import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROJECT = REPO / "CvGameCoreDLL" / "Project"
SOURCE = REPO / "CvGameCoreDLL"
VCVARS = Path(r"C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\vcvars32.bat")
TOOLKIT = Path(r"C:\Program Files (x86)\Civ4SDK\Microsoft Visual C++ Toolkit 2003")
PSDK = Path(r"C:\Program Files (x86)\Civ4SDK\WindowsSDK")
LIBS = Path(r"C:\Program Files (x86)\Civ4Libs")
CONFIGURATIONS = ("Debug-opt", "Release", "Assert-fast", "Debug")
# <!-- custom: The same defines and include paths a scratchpad zs.bat used for the Release-like translation units; /Zs checks syntax and types without writing objects or touching the installed DLL. (Claude code Opus 5.5) -->
SYNTAX_FLAGS = ["/nologo", "/Zs", "/MD", "/GR", "/EHsc", "/DWIN32", "/D_WINDOWS", "/D_USRDLL", "/DNDEBUG", "/DSAS_DLL_BUILD_CONFIGURATION=3"]
SYNTAX_INCLUDES = [SOURCE, TOOLKIT / "include", PSDK / "Include", PSDK / "Include" / "mfc", LIBS / "Boost-1.32.0" / "include", LIBS / "Python24" / "include"]


def windows_path(path: str) -> str:
	# <!-- custom: Running cmd.exe was not enough: it inherits Git Bash's PATH, so on 2026-11-13 the Makefile's "FIND /C /V" ran C:\Program Files\Git\usr\bin\find.exe, which treated its arguments as folders and crawled all of C: ("FIND: '/C/$Recycle.Bin/...': Permission denied") while nmake waited; the build sat at RUNNING for minutes with no compiler process.
	# So Git's tools leave the PATH and System32 comes first, where Windows' find.exe and the rest of cmd's tools live. See KI#38.7. (Claude code Opus 5.5) -->
	system32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")
	kept = [entry for entry in path.split(os.pathsep) if entry and "\\git\\" not in entry.lower().replace("/", "\\") + "\\"]
	return os.pathsep.join([system32] + kept)


def run_in_vc_environment(command: str, cwd: Path) -> int:
	if not VCVARS.is_file():
		sys.exit("vcvars32.bat not found at %s" % VCVARS)
	environment = dict(os.environ)
	environment["PATH"] = windows_path(environment.get("PATH", ""))
	# <!-- custom: One cmd.exe line, so the environment vcvars32 sets is still there for the command after it. (Claude code Opus 5.5) -->
	line = 'call "%s" >nul && %s' % (VCVARS, command)
	return subprocess.call(line, cwd=str(cwd), shell=True, env=environment)


def build(configuration: str, request: str) -> int:
	command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\build_with_report.ps1 -Configuration %s -Request %s" % (configuration, request)
	return run_in_vc_environment(command, PROJECT)


INSTALLED = REPO / "Assets" / "CvGameCoreDLL.dll"
DESKTOP_WINDOWS = REPO / "LLM_Helpers" / "desktop" / "desktop_windows.py"


def running_mod_clients() -> list[str]:
	# <!-- custom: Civ4 clients running this mod, as "PID commandline" lines; another mod's client loads its own DLL, so it does not count.
	# The first version looked for "AdvCiv-SAS" in the command line and missed the SASPilot client it was tested on, whose mod is named only in its ini= file, so it replaced the DLL under the running game (2026-11-20); desktop_windows.client_mod reads both. (Claude code Opus 5.5) -->
	sys.path.insert(0, str(DESKTOP_WINDOWS.parent))
	import desktop_windows
	return ["%d %s" % (pid, cmd) for (pid, cmd) in desktop_windows.civ4_processes() if desktop_windows.process_alive(pid) and desktop_windows.client_mod(cmd).lower() == "advciv-sas"]


def sha256(path: Path) -> str:
	import hashlib
	return hashlib.sha256(path.read_bytes()).hexdigest()


def install(configuration: str, close: bool) -> int:
	# <!-- custom: Each DLL test on 2026-11-20 took the same steps by hand: close the test Civ4, copy the new DLL into Assets, start the game again.
	# Once a Civ4 that had exited but still showed in the process list (pid 32660) kept the old DLL open, so the copy failed with "Device or resource busy" until the old file was moved aside.
	# Only the DLL is copied: its .build.json joins it only for a shipped Release update (AGENTS.md, DLL compilation). (Claude code Opus 5.5) -->
	built = PROJECT / configuration / "CvGameCoreDLL.dll"
	if not built.is_file():
		print("no built DLL at %s; run build first" % built)
		return 1
	# <!-- custom: Only the DLL its own report calls a successful build of this configuration, with the same hash: the folder can hold a DLL from a failed or older build (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	import json
	report_path = PROJECT / configuration / "CvGameCoreDLL.dll.build.json"
	report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
	expected = str((report.get("dllAfter") or {}).get("sha256", "")).lower()
	if report.get("status") != "SUCCEEDED" or report.get("configuration") != configuration or expected != sha256(built):
		print("%s's build report does not show a successful %s build of this DLL (status %s, configuration %s, report's hash %s, DLL's %s); build again" % (built, configuration, report.get("status"), report.get("configuration"), expected[:12] or "none", sha256(built)[:12]))
		return 1
	clients = running_mod_clients()
	if clients and close:
		subprocess.call([sys.executable, str(DESKTOP_WINDOWS), "close", "--mod", "AdvCiv-SAS", "--wait", "30", "--force"])
		clients = running_mod_clients()
	# <!-- custom: Refused whenever a client is left, closed or not: the first version went on after --close without looking again (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if clients:
		print("Civ4 runs with this mod and has the DLL loaded; close it%s:\n  %s" % ("" if close else ", or pass --close", "\n  ".join(clients)))
		return 1
	# <!-- custom: Written beside the installed DLL and checked first, then swapped in by a rename, so a failed write never leaves Assets with half a DLL or none (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	staged = INSTALLED.with_name(INSTALLED.name + ".new")
	staged.write_bytes(built.read_bytes())
	if sha256(staged) != sha256(built):
		staged.unlink()
		print("the copy to %s differs from %s" % (staged, built))
		return 1
	try:
		os.replace(staged, INSTALLED)
	except PermissionError:
		# <!-- custom: Windows refuses to overwrite a DLL any process has loaded, which is a surer sign than the mod name: a command line names the mod asked for, not the DLL loaded (Codex's review).
		# So a lock with any Civ4 still alive is refused; only with none alive, as with pid 32660, is the locked file renamed, which Windows allows, to the temp folder, and put back if the swap still fails. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		sys.path.insert(0, str(DESKTOP_WINDOWS.parent))
		import desktop_windows
		alive = [pid for (pid, _) in desktop_windows.civ4_processes() if desktop_windows.process_alive(pid)]
		if alive:
			staged.unlink()
			print("%s is in use and Civ4 processes still run (%s); close them first" % (INSTALLED, ", ".join([str(pid) for pid in alive])))
			return 1
		# <!-- custom: tempfile for the folder the locked DLL moves to, and time for its name, needed only on this path. (Claude code Opus 5.5) -->
		import tempfile
		import time
		aside = Path(tempfile.gettempdir()) / "AdvCiv-SAS_locked_dlls" / ("CvGameCoreDLL_%s.dll" % time.strftime("%Y%m%dT%H%M%S"))
		aside.parent.mkdir(parents=True, exist_ok=True)
		os.replace(INSTALLED, aside)
		try:
			os.replace(staged, INSTALLED)
		except OSError:
			os.replace(aside, INSTALLED)
			raise
		print("the installed DLL was locked by a Civ4 that has exited; moved it to %s" % aside)
	print("installed %s DLL (%s) to %s" % (configuration, sha256(built)[:12], INSTALLED))
	return 0


def generated_header_folders() -> list[Path]:
	# <!-- custom: CvGameCoreUtils.cpp includes SASBuildProvenance.generated.h, which only a build writes into temp_files/<target>, so on 2026-11-19 its /Zs check failed with C1083 while the other files passed.
	# Use the newest such header; its values do not matter for a syntax check. (Claude code Opus 5.5) -->
	headers = sorted((PROJECT / "temp_files").glob("*/SASBuildProvenance.generated.h"), key=lambda path: path.stat().st_mtime, reverse=True)
	return [headers[0].parent] if headers else []


def syntax(files: list[str]) -> int:
	failures = 0
	includes = " ".join('/I"%s"' % path for path in SYNTAX_INCLUDES + generated_header_folders())
	for name in files:
		path = Path(name)
		if not path.is_absolute():
			path = SOURCE / path if (SOURCE / path).is_file() else Path.cwd() / path
		if not path.is_file():
			print("not found: %s" % name)
			failures += 1
			continue
		command = '"%s" %s %s "%s"' % (TOOLKIT / "bin" / "cl.exe", " ".join(SYNTAX_FLAGS), includes, path)
		code = run_in_vc_environment(command, SOURCE)
		print("%s %s" % ("OK" if code == 0 else "FAILED", path.name))
		failures += code != 0
	return 1 if failures else 0


def main() -> int:
	parser = argparse.ArgumentParser(description="Build the AdvCiv-SAS DLL through build_with_report.ps1, install it into Assets, or check C++ files with cl.exe /Zs, with the Visual C++ environment set up. Examples: build_dll.py build; build_dll.py build --install --close; build_dll.py install; build_dll.py build --configuration Release; build_dll.py syntax CvGameInterface.cpp CyGame.cpp")
	sub = parser.add_subparsers(dest="action", required=True)
	build_parser = sub.add_parser("build", help="run build_with_report.ps1 (REBUILD by default, which cleans temp_files/<target> first)")
	build_parser.add_argument("--configuration", choices=CONFIGURATIONS, default="Debug-opt")
	build_parser.add_argument("--request", choices=("REBUILD", "BUILD", "CLEAN"), default="REBUILD")
	build_parser.add_argument("--install", action="store_true", help="install the DLL into Assets after a successful build")
	build_parser.add_argument("--close", action="store_true", help="with --install, close this mod's Civ4 clients first")
	install_parser = sub.add_parser("install", help="copy the built DLL into Assets for a local test; refuses while this mod's Civ4 runs unless --close")
	install_parser.add_argument("--configuration", choices=CONFIGURATIONS, default="Debug-opt")
	install_parser.add_argument("--close", action="store_true", help="close this mod's Civ4 clients first")
	syntax_parser = sub.add_parser("syntax", help="cl.exe /Zs on C++ files, by name in CvGameCoreDLL or by path; no objects, no DLL")
	syntax_parser.add_argument("files", nargs="+")
	args = parser.parse_args()
	if args.action == "build":
		if args.install and args.request == "CLEAN":
			parser.error("--install needs a build; CLEAN only removes one")
		code = build(args.configuration, args.request)
		if code == 0 and args.install:
			return install(args.configuration, args.close)
		return code
	if args.action == "install":
		return install(args.configuration, args.close)
	return syntax(args.files)


if __name__ == "__main__":
	sys.exit(main())

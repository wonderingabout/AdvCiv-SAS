#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build the DLL through build_with_report.ps1, or syntax-check C++ files with VC2003's cl.exe /Zs, from any shell.

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


def syntax(files: list[str]) -> int:
	failures = 0
	includes = " ".join('/I"%s"' % path for path in SYNTAX_INCLUDES)
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
	parser = argparse.ArgumentParser(description="Build the AdvCiv-SAS DLL through build_with_report.ps1, or check C++ files with cl.exe /Zs, with the Visual C++ environment set up. Examples: build_dll.py build; build_dll.py build --configuration Release; build_dll.py syntax CvGameInterface.cpp CyGame.cpp")
	sub = parser.add_subparsers(dest="action", required=True)
	build_parser = sub.add_parser("build", help="run build_with_report.ps1 (REBUILD by default, which cleans temp_files/<target> first)")
	build_parser.add_argument("--configuration", choices=CONFIGURATIONS, default="Debug-opt")
	build_parser.add_argument("--request", choices=("REBUILD", "BUILD", "CLEAN"), default="REBUILD")
	syntax_parser = sub.add_parser("syntax", help="cl.exe /Zs on C++ files, by name in CvGameCoreDLL or by path; no objects, no DLL")
	syntax_parser.add_argument("files", nargs="+")
	args = parser.parse_args()
	if args.action == "build":
		return build(args.configuration, args.request)
	return syntax(args.files)


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Describes EXE addresses with headless Ghidra: the containing function, the instructions around each address and the decompiled function, written as one text file an agent can read.
# It runs ghidra_scripts/DescribeAddresses.java on the project dump_exe_image.py's copy was imported into, read-only and without re-analysis, so a run takes seconds after Ghidra starts. (Claude code Opus 5.5) -->
import argparse
# <!-- custom: os for the environment, subprocess to run Ghidra, sys for exit codes, tempfile for the address list and script copy, and Path for files. (Claude code Opus 5.5) -->
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GHIDRA_DIR = Path(r"C:\Tools\ghidra_12.2_PUBLIC")
JDK_ROOT = Path(r"C:\Program Files\Eclipse Adoptium")
ANALYSIS_DIR = Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "exe_analysis"
PROJECT_NAME = "Civ4BtS"
PROGRAM_NAME = "Civ4BeyondSword_decrypted.exe"


def find_jdk():
	# <!-- custom: Ghidra 12.2 needs Java 25, while an older Amazon Corretto JDK 21 comes first on PATH, so JAVA_HOME is set to the newest Temurin 25+ explicitly. (Claude code Opus 5.5) -->
	candidates = sorted(path for path in JDK_ROOT.glob("jdk-*") if path.name.split("-")[1].split(".")[0].isdigit() and int(path.name.split("-")[1].split(".")[0]) >= 25)
	if not candidates:
		sys.exit("no JDK 25 or later under %s; install it with: winget install EclipseAdoptium.Temurin.25.JDK" % JDK_ROOT)
	return candidates[-1]


def main():
	parser = argparse.ArgumentParser(description="Describe Civ4BeyondSword.exe addresses with headless Ghidra.")
	parser.add_argument("addresses", nargs="*", help="addresses such as 0x0057C9EB, optionally with a label after a colon: 0x0057C9EB:popup_margin")
	parser.add_argument("--file", type=Path, help="tab-separated file of address and label, one per line; # starts a comment")
	parser.add_argument("--out", type=Path, default=ANALYSIS_DIR / "describe_exe_sites.txt")
	parser.add_argument("--max-chars", type=int, default=6000, help="cut each decompiled function after this many characters")
	args = parser.parse_args()

	rows = []
	if args.file:
		rows.extend(args.file.read_text(encoding="utf-8").splitlines())
	for item in args.addresses:
		address, _, label = item.partition(":")
		rows.append("%s\t%s" % (address, label))
	if not [row for row in rows if row.strip() and not row.startswith("#")]:
		sys.exit("no addresses given")
	if not (ANALYSIS_DIR / "ghidra" / (PROJECT_NAME + ".gpr")).exists():
		sys.exit("no Ghidra project at %s; create it as described under dump_exe_image.py in LLM_Helpers/README.md" % (ANALYSIS_DIR / "ghidra"))

	with tempfile.TemporaryDirectory() as temporary:
		address_file = Path(temporary) / "addresses.tsv"
		address_file.write_text("\n".join(rows) + "\n", encoding="utf-8")
		args.out.parent.mkdir(parents=True, exist_ok=True)
		java_home = find_jdk()
		env = dict(os.environ, JAVA_HOME=str(java_home), PATH=str(java_home / "bin") + os.pathsep + os.environ.get("PATH", ""))
		# <!-- custom: analyzeHeadless.bat failed with "\Steam\steamapps\common\Sid était inattendu" when given the repository's script folder: cmd cannot parse "(x86)" and "Sid Meier's" in a batch argument, so the script is copied next to the address list first. (Claude code Opus 5.5) -->
		script_dir = Path(temporary)
		(script_dir / "DescribeAddresses.java").write_bytes((Path(__file__).resolve().parent / "ghidra_scripts" / "DescribeAddresses.java").read_bytes())
		command = [str(GHIDRA_DIR / "support" / "analyzeHeadless.bat"), str(ANALYSIS_DIR / "ghidra"), PROJECT_NAME, "-process", PROGRAM_NAME, "-readOnly", "-noanalysis", "-scriptPath", str(script_dir), "-postScript", "DescribeAddresses.java", str(address_file), str(args.out.resolve()), str(args.max_chars)]
		# <!-- custom: analyzeHeadless.bat ends with "pause" on errors; empty stdin lets that pause return instead of hanging the run. (Claude code Opus 5.5) -->
		result = subprocess.run(command, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, errors="replace")
	if result.returncode != 0 or not args.out.exists():
		sys.stderr.write(result.stdout[-4000:] + result.stderr[-2000:])
		sys.exit("Ghidra failed (exit %d)" % result.returncode)
	print("wrote %s" % args.out)
	return 0


if __name__ == "__main__":
	sys.exit(main())

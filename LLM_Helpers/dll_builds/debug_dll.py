#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Look inside the game DLL with WinDbg's console debugger, CDB: list the Civ4 processes, check which of their threads are hidden from debuggers, print a running game's stacks, save a full dump of it, or analyze a crash dump.

# <!-- custom: On 2026-11-18 the DLL Debugging Guide's recipes were PowerShell blocks, and its tests ran from scratchpad scripts the next session could not see.
# This keeps the recipes that every debugging session needs in one place; the one-off breakpoint experiments stay in Downloads/AdvCiv-SAS_LLM/debugger_trials/.
# See README_DLL_Debugging.md for what works on the Steam game and why breakpoints on the main thread end it. (Claude code Opus 5.5) -->
# <!-- custom: argparse reads the subcommands; ctypes queries threads and processes through the Windows API; json reads PowerShell's process list. (Claude code Opus 5.5) -->
import argparse
import ctypes
import json
# <!-- custom: os and pathlib handle paths; subprocess runs CDB and PowerShell; sys gives the exit and the running Python; wintypes gives the Windows API's types. (Claude code Opus 5.5) -->
import os
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEBUG_OPT_SYMBOLS = REPO / "CvGameCoreDLL" / "Project" / "temp_files" / "Debug-opt"
CDB = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "cdbX86.exe"

TH32CS_SNAPTHREAD = 0x00000004
THREAD_QUERY_INFORMATION = 0x0040
THREAD_HIDE_FROM_DEBUGGER = 0x11


class THREADENTRY32(ctypes.Structure):
	_fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ThreadID", wintypes.DWORD), ("th32OwnerProcessID", wintypes.DWORD), ("tpBasePri", wintypes.LONG), ("tpDeltaPri", wintypes.LONG), ("dwFlags", wintypes.DWORD)]


def civ4_processes():
	command = "Get-CimInstance Win32_Process -Filter \"Name='Civ4BeyondSword.exe'\" | Select-Object ProcessId, @{n='Started';e={$_.CreationDate.ToString('s')}}, CommandLine | ConvertTo-Json -Compress"
	output = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True).stdout.strip()
	if not output:
		return []
	rows = json.loads(output)
	return rows if isinstance(rows, list) else [rows]


def cdb_path():
	if not CDB.exists():
		sys.exit("cdbX86.exe not found at %s; install WinDbg from the Microsoft Store" % CDB)
	return str(CDB)


def thread_ids(pid):
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
	entry = THREADENTRY32()
	entry.dwSize = ctypes.sizeof(THREADENTRY32)
	ids = []
	ok = kernel32.Thread32First(snapshot, ctypes.byref(entry))
	while ok:
		if entry.th32OwnerProcessID == pid:
			ids.append(entry.th32ThreadID)
		ok = kernel32.Thread32Next(snapshot, ctypes.byref(entry))
	kernel32.CloseHandle(snapshot)
	return ids


def thread_states(pid):
	# <!-- custom: Codex's review of the guide's first PowerShell version found it printed only hidden threads and dropped failed queries, so an empty answer could not be told from a query that never ran.
	# Each thread therefore reports HIDDEN, not hidden or UNKNOWN, and the main thread is the one created first, as Civ4's main thread was in every check of 2026-11-18. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	ntdll = ctypes.WinDLL("ntdll")
	kernel32.OpenThread.restype = wintypes.HANDLE
	rows = []
	for tid in thread_ids(pid):
		handle = kernel32.OpenThread(THREAD_QUERY_INFORMATION, False, tid)
		if not handle:
			rows.append((tid, None, "UNKNOWN (cannot open, error %d)" % ctypes.get_last_error()))
			continue
		created = wintypes.FILETIME()
		unused = (wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME())
		kernel32.GetThreadTimes(handle, ctypes.byref(created), ctypes.byref(unused[0]), ctypes.byref(unused[1]), ctypes.byref(unused[2]))
		start = (created.dwHighDateTime << 32) | created.dwLowDateTime
		hidden = ctypes.c_ubyte(0)
		returned = wintypes.ULONG(0)
		status = ntdll.NtQueryInformationThread(handle, THREAD_HIDE_FROM_DEBUGGER, ctypes.byref(hidden), 1, ctypes.byref(returned)) & 0xFFFFFFFF
		kernel32.CloseHandle(handle)
		if status != 0:
			rows.append((tid, start, "UNKNOWN (status 0x%08X)" % status))
		else:
			rows.append((tid, start, "HIDDEN" if hidden.value else "not hidden"))
	return rows


def command_list(args):
	processes = civ4_processes()
	if not processes:
		print("no Civ4BeyondSword.exe running")
	for row in processes:
		print("%s  started %s  %s" % (row["ProcessId"], row["Started"], row["CommandLine"]))


def command_threads(args):
	rows = thread_states(args.pid)
	if not rows:
		sys.exit("no threads found for process %d" % args.pid)
	known = [row for row in rows if row[1] is not None]
	main_tid = min(known, key=lambda row: row[1])[0] if known else None
	for tid, start, state in rows:
		print("thread %d%s: %s" % (tid, " (main)" if tid == main_tid else "", state))
	unknown = [row for row in rows if row[2].startswith("UNKNOWN")]
	hidden = [row for row in rows if row[2] == "HIDDEN"]
	print("%d threads: %d hidden, %d unknown" % (len(rows), len(hidden), len(unknown)))
	if unknown:
		print("some queries failed, so this does not show that no thread is hidden")
	sys.exit(1 if unknown else 0)


def run_cdb(arguments, log):
	# <!-- custom: Live sessions attach with -pd and end with qd: on 2026-11-18 stopping CDB ended the game it was attached to, while -pd, which Codex's review proposed, left it running even after q. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	log.parent.mkdir(parents=True, exist_ok=True)
	command = [cdb_path()] + arguments + ["-logo", str(log)]
	result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	print("log: %s" % log)
	return result.returncode


# <!-- custom: Codex's 2026-11-18 review found the commands trusted files rather than CDB: with an earlier dump already at --out, a failed .dump still printed "full dump", so an old dump could pass as the new game's evidence.
# Each command now checks CDB's exit code and its own output, and dump refuses an existing file. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
def same_path(first, second):
	first, second = Path(first), Path(second)
	if first.exists() and second.exists():
		return os.path.samefile(first, second)
	return first.resolve() == second.resolve()


def chosen_out(out):
	# <!-- custom: A --out the caller names must not exist yet: the session log replaces any file there, so naming an existing file, such as the dump itself, would delete it; Codex's re-check reproduced analyze --out <the dump> erasing the dump (2026-11-18).
	# Default logs in TEMP or beside the dump are the helper's own and may be replaced. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if out and Path(out).exists():
		sys.exit("%s already exists; give a new file name for the session log" % out)
	return out


def cdb_or_fail(arguments, log, protect=()):
	for kept in protect:
		if same_path(log, kept):
			sys.exit("the session log %s would replace %s; choose another --out" % (log, kept))
	if log.exists():
		log.unlink()
	code = run_cdb(arguments, log)
	if code != 0 or not log.exists():
		sys.exit("CDB failed (exit code %d); see %s" % (code, log))
	return log.read_text(encoding="utf-8", errors="replace")


def command_snapshot(args):
	stacks = "~* kb %d" % args.frames if args.all else "~0 kb %d" % args.frames
	log = Path(chosen_out(args.out) or os.path.join(os.environ.get("TEMP", "."), "civ4_stack_%d.txt" % args.pid))
	text = cdb_or_fail(["-pd", "-p", str(args.pid), "-c", "%s; qd" % stacks], log)
	marker = text.find("> " + stacks)
	if marker < 0:
		sys.exit("CDB did not run the stack command; see %s" % log)
	print(text[marker:])


def command_dump(args):
	out = Path(args.out).resolve()
	if out.exists():
		sys.exit("%s already exists; give a new file name, so an earlier dump cannot pass as this one" % out)
	# <!-- custom: The log was out.with_suffix(".txt"), so dump --out live.txt gave the log and the dump one file name (Codex's re-check); the log now appends to the whole name. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	log = out.with_name(out.name + ".log.txt")
	text = cdb_or_fail(["-pd", "-p", str(args.pid), "-c", ".dump /ma \"%s\"; qd" % out], log, protect=(out,))
	if not out.exists() or out.stat().st_size == 0 or "Dump successfully written" not in text:
		sys.exit("no dump written; see %s" % log)
	print("full dump: %s (%.1f MB)" % (out, out.stat().st_size / 1048576.0))


def command_analyze(args):
	dump = Path(args.dump).resolve()
	if args.symbols:
		symbols = Path(args.symbols)
	elif (dump.parent / "CvGameCoreDLL.pdb").exists():
		symbols = dump.parent
	else:
		symbols = DEBUG_OPT_SYMBOLS
	if not dump.is_file():
		sys.exit("no such dump: %s" % dump)
	log = Path(chosen_out(args.out) or dump.with_name(dump.stem + "_analysis.txt"))
	# <!-- custom: lmvm comes after the first kb: run before it on 2026-11-18, it printed only "(deferred)", as CDB loads the DLL's symbols on first use. (Claude code Opus 5.5) -->
	text = cdb_or_fail(["-z", str(dump), "-y", "%s;srv*" % symbols, "-c", ".ecxr; kb %d; lmvm CvGameCoreDLL; !analyze -v; q" % args.frames], log, protect=(dump,))
	if "ChildEBP" not in text:
		sys.exit("CDB printed no stack; see %s" % log)
	print("symbols: %s" % symbols)
	# <!-- custom: A dump copied away from its PDB fell back on 2026-11-18 to the current Debug-opt PDB, from another build; CDB rejected it and printed CvGameCoreDLL+8ae475 with no names, which is easy to miss in the output. (Claude code Opus 5.5) -->
	if "CvGameCoreDLL" in text and "private pdb symbols" not in text:
		print("WARNING: no matching PDB loaded for CvGameCoreDLL, so its frames have no names; pass --symbols with the folder holding that build's PDB")
	# <!-- custom: !analyze -v repeats the kb stack in its STACK_TEXT, so each line prints once. (Claude code Opus 5.5) -->
	printed = set()
	for line in text.splitlines():
		if line in printed:
			continue
		if line.startswith(("ChildEBP", "EXCEPTION_CODE_STR", "FAULTING_SOURCE_FILE", "FAULTING_SOURCE_LINE_NUMBER", "SYMBOL_NAME", "FAILURE_BUCKET_ID")) or " CvGameCoreDLL!" in line or "pdb symbols" in line:
			print(line)
			printed.add(line)


EXIT_CODE_NAMES = {0x4000001F: "STATUS_WX86_BREAKPOINT", 0x4000001E: "STATUS_WX86_SINGLE_STEP", 0xC0000005: "access violation"}


def command_breaktest(args):
	# <!-- custom: The tests behind the DLL Debugging Guide answered one question by hand, whether a breakpoint stops the game on this EXE: on the Steam EXE one in CvGame::update ended it with 0x4000001F (main thread hidden), while one on an EXE worker thread stopped (tests 10 and 13).
	# This asks it again in one command, for example on a GOG copy or a later Steam build.
	# A breakpoint that ends the game ends it, so run it on a throwaway game. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: signal holds off Ctrl+C during the cleanup below; time paces the wait for a hit. (Claude code Opus 5.5) -->
	import signal
	import time
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	kernel32.OpenProcess.restype = wintypes.HANDLE
	# <!-- custom: PROCESS_QUERY_LIMITED_INFORMATION, to read the exit code if the game ends. (Claude code Opus 5.5) -->
	process = kernel32.OpenProcess(0x1000, False, args.pid)
	if not process:
		sys.exit("cannot open process %d" % args.pid)
	target = args.address or args.function
	action = '".echo SAS_BREAK_HIT; r eip; kb 8; bc *; qd"'
	command = ("~0s; ba e1 %s %s" if args.hardware else "bp /1 %s %s") % (target, action)
	log = Path(chosen_out(args.out) or os.path.join(os.environ.get("TEMP", "."), "civ4_breaktest_%d.txt" % args.pid))
	if log.exists():
		log.unlink()
	exit_code = wintypes.DWORD(259)

	def game_alive():
		kernel32.GetExitCodeProcess(process, ctypes.byref(exit_code))
		return exit_code.value == 259

	def log_text():
		return log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""

	debugger = None
	verdict = None
	clean = False
	try:
		# <!-- custom: CDB gets a console of its own, hidden, so the cleanup below can send it Ctrl+C, which CDB takes as a break-in request, as Codex's interrupt.py did in its trials. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		hidden = subprocess.STARTUPINFO()
		hidden.dwFlags = subprocess.STARTF_USESHOWWINDOW
		hidden.wShowWindow = 0
		debugger = subprocess.Popen([cdb_path(), "-pd", "-p", str(args.pid), "-y", str(DEBUG_OPT_SYMBOLS), "-logo", str(log)], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_CONSOLE, startupinfo=hidden)
		debugger.stdin.write((command + "\ng\n").encode("ascii"))
		debugger.stdin.flush()
		end = time.monotonic() + args.seconds
		while time.monotonic() < end and verdict is None:
			time.sleep(0.5)
			if "\nSAS_BREAK_HIT" in log_text():
				verdict = "STOPPED"
			elif not game_alive():
				verdict = "EXITED"
		# <!-- custom: A hit runs bc *; qd itself, so STOPPED is reported only once CDB has exited and the game still runs, not from the echo alone (Codex's review, 2026-11-18). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if verdict == "STOPPED":
			try:
				debugger.wait(15)
				clean = game_alive()
			except subprocess.TimeoutExpired:
				pass
		elif verdict == "EXITED":
			clean = True
	except KeyboardInterrupt:
		# <!-- custom: Ctrl+C on the helper: the cleanup below still runs, and the result is reported like the others instead of as a traceback. (Claude code Opus 5.5) -->
		verdict = "INTERRUPTED"
	finally:
		# <!-- custom: Codex's review found that a timeout or Ctrl+C killed CDB with the breakpoint still written in the game, or skipped cleanup entirely.
		# Whatever happened, CDB is now interrupted, told bc *; qd, and must exit within 15 s while the game runs on; otherwise the game is reported unsafe to keep using.
		# The first cleanup broke in with DebugBreakProcess, which returned success, yet CDB recorded no break, did not exit, and a fresh CDB then read cc (int 3) at CvGame::doTurn: the breakpoint stayed in the game, and only the UNSAFE report caught it (2026-11-18).
		# A console Ctrl+C is what makes CDB break in. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		# <!-- custom: Codex's re-check found that a second Ctrl+C during this cleanup escaped it, skipping the kill and the handle close and leaving CDB attached with the breakpoint armed.
		# Ctrl+C is therefore ignored for the bounded cleanup and restored after it, and the nested finally always reaps CDB and closes the handles. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
		try:
			if debugger is not None and debugger.poll() is None and game_alive() and not clean:
				try:
					subprocess.run([sys.executable, __file__, "_interrupt", str(debugger.pid)], timeout=15, check=True)
					time.sleep(1)
					debugger.stdin.write(b".echo SAS_CLEANUP; bc *; qd\n")
					debugger.stdin.flush()
					debugger.wait(15)
					clean = game_alive() and "\nSAS_CLEANUP" in log_text()
				except (OSError, subprocess.SubprocessError):
					clean = False
		finally:
			try:
				if debugger is not None:
					if debugger.poll() is None:
						clean = clean and verdict == "EXITED"
						debugger.kill()
						try:
							debugger.wait(5)
						except subprocess.TimeoutExpired:
							pass
					try:
						debugger.stdin.close()
					except OSError:
						pass
			finally:
				kernel32.CloseHandle(process)
				signal.signal(signal.SIGINT, previous_handler)
	print("breakpoint: %s" % command)
	if verdict == "STOPPED":
		print("STOPPED: the breakpoint stopped the game; breakpoints work there" + ("; CDB then cleared it and detached" if clean else ""))
	elif verdict == "EXITED":
		print("GAME EXITED with 0x%08X (%s) and no stop: the breakpoint was not reported to the debugger" % (exit_code.value, EXIT_CODE_NAMES.get(exit_code.value, "unknown")))
	elif verdict == "INTERRUPTED":
		print("INTERRUPTED by Ctrl+C before a result" + ("; CDB broke in, cleared the breakpoint and detached" if clean else ""))
	else:
		print("NO HIT within %d s: the code did not run, or the breakpoint was never armed" % args.seconds + ("; CDB broke in, cleared it and detached" if clean else ""))
	print("log: %s" % log)
	if verdict == "STOPPED":
		text = log_text()
		hit = text.rfind("\nSAS_BREAK_HIT")
		print(text[hit + 1:hit + 1200])
	if not clean:
		sys.exit("UNSAFE: cleanup could not be confirmed, so process %d may still hold the breakpoint or a debugger; close that game" % args.pid)


def send_ctrl_c(console_pid):
	# <!-- custom: Codex's interrupt.py from its 2026-11-18 trials, as a helper step.
	# It runs as its own short process: attaching to CDB's console detaches the caller's own, and the Ctrl+C reaches every process on that console, so this one ignores it first. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	import time
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	kernel32.FreeConsole()
	if not kernel32.AttachConsole(console_pid):
		raise ctypes.WinError(ctypes.get_last_error())
	kernel32.SetConsoleCtrlHandler(None, True)
	if not kernel32.GenerateConsoleCtrlEvent(0, 0):
		raise ctypes.WinError(ctypes.get_last_error())
	time.sleep(0.3)
	kernel32.FreeConsole()


def main():
	if len(sys.argv) == 3 and sys.argv[1] == "_interrupt":
		send_ctrl_c(int(sys.argv[2]))
		return
	parser = argparse.ArgumentParser(description="Look inside the game DLL with CDB: processes, hidden threads, live stacks, full dumps and crash-dump analysis.")
	sub = parser.add_subparsers(dest="command", required=True)
	sub.add_parser("list", help="list running Civ4 processes with their start time and command line, to pick a --pid")
	threads = sub.add_parser("threads", help="report each thread of a process as HIDDEN, not hidden or UNKNOWN to debuggers")
	threads.add_argument("--pid", type=int, required=True)
	snapshot = sub.add_parser("snapshot", help="attach, print the main thread's stack (or every thread's) and detach, leaving the game running")
	snapshot.add_argument("--pid", type=int, required=True)
	snapshot.add_argument("--all", action="store_true", help="every thread, not only the main one")
	snapshot.add_argument("--frames", type=int, default=12)
	snapshot.add_argument("--out", help="session log; default civ4_stack_<pid>.txt in TEMP")
	dump = sub.add_parser("dump", help="attach, write a full dump of the running game and detach, leaving it running")
	dump.add_argument("--pid", type=int, required=True)
	dump.add_argument("--out", required=True, help="dump file; a game's full dump runs to gigabytes, so write it where it will be deleted or kept on purpose")
	analyze = sub.add_parser("analyze", help="read a crash dump: crashing context, stack, symbol check and !analyze -v")
	analyze.add_argument("dump")
	analyze.add_argument("--symbols", help="folder with the matching PDB; default the dump's folder if it holds one, else temp_files/Debug-opt")
	analyze.add_argument("--frames", type=int, default=12)
	analyze.add_argument("--out", help="session log; default <dump>_analysis.txt beside the dump")
	breaktest = sub.add_parser("breaktest", help="set one breakpoint and report whether it stopped the game, ended it (with its exit code) or never fired; run on a throwaway game")
	breaktest.add_argument("--pid", type=int, required=True)
	where = breaktest.add_mutually_exclusive_group(required=True)
	where.add_argument("--function", help="for example CvGameCoreDLL!CvGame::update, which runs every frame on the main thread")
	where.add_argument("--address", help="a code address, for example one from a worker thread's stack in a snapshot --all")
	breaktest.add_argument("--hardware", action="store_true", help="a hardware execution breakpoint (ba e1), set from the main thread, instead of a software one (bp)")
	breaktest.add_argument("--seconds", type=int, default=10)
	breaktest.add_argument("--out", help="session log; default civ4_breaktest_<pid>.txt in TEMP")
	args = parser.parse_args()
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")
	{"list": command_list, "threads": command_threads, "snapshot": command_snapshot, "dump": command_dump, "analyze": command_analyze, "breaktest": command_breaktest}[args.command](args)


if __name__ == "__main__":
	main()

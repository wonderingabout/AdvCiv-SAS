#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Writes a decrypted, read-only copy of Civ4BeyondSword.exe for Ghidra.
# The Steam EXE is wrapped by Steam's DRM (SteamStub, the .bind section): its .text code is encrypted on disk, so on 2026-11-12 Realism Invictus's Steam patch address 0x00601EEC held other bytes than its expected PUSH 0x00C4C678.
# The wrapper decrypts .text in memory at startup, so this launches Civ4 without a mod, waits until .text in memory differs from the file, copies the whole image and closes the game it started.
# Copying that early, before any mod DLL loads, keeps runtime EXE patches such as SelfMod.cpp's out of the copy. (Claude code Opus 5.5) -->
import argparse
# <!-- custom: ctypes reads the other process's memory, hashlib reports hashes, struct parses the PE headers, sys and time for exit codes and polling, and Path for files. (Claude code Opus 5.5) -->
import ctypes
import hashlib
import importlib.util
import struct
import sys
import time
from pathlib import Path

# <!-- custom: desktop_windows supplies the default Civ4 folder, the running-client list and a detached launch, so this helper starts the game the same way run_autoplay.py does.
# It is loaded from its file with importlib; a sys.path entry and a late import needed an unexplained noqa (2026-11-12). (Claude code Opus 5.5) -->
_DESKTOP_WINDOWS_SPEC = importlib.util.spec_from_file_location("desktop_windows", Path(__file__).resolve().parent.parent / "game_runs" / "desktop_windows.py")
if _DESKTOP_WINDOWS_SPEC is None or _DESKTOP_WINDOWS_SPEC.loader is None:
	raise SystemExit("cannot load LLM_Helpers/game_runs/desktop_windows.py")
desktop_windows = importlib.util.module_from_spec(_DESKTOP_WINDOWS_SPEC)
_DESKTOP_WINDOWS_SPEC.loader.exec_module(desktop_windows)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PAGE = 0x1000
DEFAULT_OUT = Path.home() / "Downloads" / "AdvCiv-SAS_LLM" / "exe_analysis" / "Civ4BeyondSword_decrypted.exe"
# <!-- custom: Bytes Realism Invictus's SelfMod.cpp expects before patching, from its comments: "V2 (Steam / beta Steam): PUSH 0x00C4C678 at 0x00601EEC".
# A match shows the copy holds the same decrypted code RI patches. (Claude code Opus 5.5) -->
CHECKS = {"RI Steam V2 PUSH 0x00C4C678": (0x00601EEC, bytes.fromhex("6878c6c400"))}


def parse_pe(data):
	pe = struct.unpack_from("<I", data, 0x3C)[0]
	count = struct.unpack_from("<H", data, pe + 6)[0]
	optional_size = struct.unpack_from("<H", data, pe + 20)[0]
	optional = pe + 24
	image_base, section_alignment = struct.unpack_from("<II", data, optional + 28)
	size_of_image = struct.unpack_from("<I", data, optional + 56)[0]
	sections = []
	for index in range(count):
		offset = optional + optional_size + 40 * index
		name = data[offset:offset + 8].rstrip(b"\0").decode("latin1")
		virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, offset + 8)
		sections.append({"name": name, "header": offset, "va": virtual_address, "vsize": virtual_size, "raw": raw_offset, "rsize": raw_size})
	return {"base": image_base, "alignment": section_alignment, "size": size_of_image, "optional": optional, "sections": sections}


def read_memory(handle, address, size):
	# <!-- custom: Reads page by page so one unreadable page becomes zeros instead of failing the whole copy; returns the bytes and the unreadable page count. (Claude code Opus 5.5) -->
	result = bytearray(size)
	unreadable = 0
	for start in range(0, size, PAGE):
		length = min(PAGE, size - start)
		buffer = ctypes.create_string_buffer(length)
		read = ctypes.c_size_t(0)
		if ctypes.windll.kernel32.ReadProcessMemory(handle, ctypes.c_void_p(address + start), buffer, length, ctypes.byref(read)) and read.value == length:
			result[start:start + length] = buffer.raw
		else:
			unreadable += 1
	return bytes(result), unreadable


def main():
	parser = argparse.ArgumentParser(description="Copy the decrypted Civ4BeyondSword.exe image out of memory for Ghidra. Launches Civ4 without a mod and closes it afterwards, unless --pid names a running client.")
	parser.add_argument("--pid", type=int, help="read this running Civ4 instead of launching one; it is left running, and any runtime EXE patches it already applied are copied too")
	parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
	parser.add_argument("--civ4-dir", type=Path, default=desktop_windows.DEFAULT_CIV4_DIR)
	parser.add_argument("--timeout", type=float, default=120, help="seconds to wait for the code to be decrypted")
	args = parser.parse_args()

	disk = (args.civ4_dir / desktop_windows.EXE_NAME).read_bytes()
	pe = parse_pe(disk)
	text = next(section for section in pe["sections"] if section["name"] == ".text")
	disk_text = disk[text["raw"]:text["raw"] + min(PAGE, text["rsize"])]

	launched = args.pid is None
	if launched:
		if desktop_windows.civ4_processes():
			sys.exit("Civ4 is already running; pass --pid to read it, or close it first")
		# <!-- custom: "multiple" only stops Civ4 refusing to start beside another client. No mod= argument is passed, though CivilizationIV.ini can still name a mod; the copy is taken as soon as .text is decrypted, before the game loads any DLL. (Claude code Opus 5.5) -->
		pid = desktop_windows.launch_detached("multiple", args.civ4_dir)
		print("launched Civ4, pid %d" % pid)
	else:
		pid = args.pid
	handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
	if not handle:
		sys.exit("cannot open process %d (error %d)" % (pid, ctypes.windll.kernel32.GetLastError()))
	try:
		# <!-- custom: Reads at the EXE's preferred base 0x400000; the MZ check below fails loudly if Windows ever loads it elsewhere. (Claude code Opus 5.5) -->
		deadline = time.time() + args.timeout
		while True:
			first, _ = read_memory(handle, pe["base"] + text["va"], len(disk_text))
			if first != disk_text and any(first):
				break
			if time.time() > deadline:
				sys.exit(".text in memory still matches the file after %d seconds: not decrypted, or not a SteamStub EXE" % args.timeout)
			time.sleep(0.2)
		# <!-- custom: The first page changing does not prove the wrapper finished the rest of .text, so copy until two reads half a second apart are identical. (Claude code Opus 5.5) -->
		image, unreadable = read_memory(handle, pe["base"], pe["size"])
		while True:
			time.sleep(0.5)
			again, unreadable = read_memory(handle, pe["base"], pe["size"])
			if again[text["va"]:text["va"] + text["vsize"]] == image[text["va"]:text["va"] + text["vsize"]]:
				break
			if time.time() > deadline:
				sys.exit(".text kept changing for %d seconds" % args.timeout)
			image = again
	finally:
		ctypes.windll.kernel32.CloseHandle(handle)
		if launched:
			desktop_windows.subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
			print("closed Civ4")
	if image[:2] != b"MZ":
		sys.exit("no MZ header at 0x%08X; the EXE did not load at its preferred base" % pe["base"])

	# <!-- custom: Rewrite the section table so each section's file offset equals its memory address; Ghidra then loads the copy exactly as the game saw it in memory. (Claude code Opus 5.5) -->
	out = bytearray(image)
	for section in pe["sections"]:
		size = (max(section["vsize"], 1) + pe["alignment"] - 1) // pe["alignment"] * pe["alignment"]
		struct.pack_into("<II", out, section["header"] + 16, size, section["va"])
	struct.pack_into("<I", out, pe["optional"] + 36, pe["alignment"])
	args.out.parent.mkdir(parents=True, exist_ok=True)
	args.out.write_bytes(bytes(out))

	print("wrote %s (%d bytes, %d unreadable pages left as zeros)" % (args.out, len(out), unreadable))
	text_bytes = image[text["va"]:text["va"] + text["vsize"]]
	print(".text sha256 %s" % hashlib.sha256(text_bytes).hexdigest())
	failed = 0
	for label, (address, expected) in CHECKS.items():
		found = image[address - pe["base"]:address - pe["base"] + len(expected)]
		ok = found == expected
		failed += not ok
		print("%s at 0x%08X: %s (%s)" % (label, address, "match" if ok else "MISMATCH", found.hex(" ")))
	return 1 if failed else 0


if __name__ == "__main__":
	sys.exit(main())

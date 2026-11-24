# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Report-only audit of Civ4 Python screens whose __init__ sets layout attributes that a later method sets again, such as BtS's W_SCREEN = 1024 placeholder before a runtime layout reads the resolution.
# Written on 2026-11-24 for KI#1098.3, when several screens turned out to carry such dead placeholders and values derived from them; it lists, per class, the __init__ attributes another method reassigns and the ones no code in the same file reads. (Claude code Opus 5.5) -->
# <!-- custom: Usage: python LLM_Helpers/audits/audit_screen_init_layout.py [files or folders], Assets/Python by default; --only-resolution keeps classes that read getXResolution/getYResolution somewhere, and --all-names adds lower-case state attributes, usually meant to start in __init__ and change later.
# Heuristic and text-based: it does not follow inheritance, getattr or reads from other modules, such as self.top.X in Sevopedia pages, so check each hit before removing anything. (Claude code Opus 5.5) -->

# <!-- custom: argparse for the options, os to walk folders, re for the class, def and self.X patterns, sys for the exit code. (Claude code Opus 5.5) -->
import argparse
import os
import re
import sys

CLASS_RE = re.compile(r"^class\s+(\w+)")
DEF_RE = re.compile(r"^(\t| {4})def\s+(\w+)\s*\(")
MULTI_ASSIGN_RE = re.compile(r"^\s*((?:self\.[A-Za-z_]\w*\s*,\s*)+self\.[A-Za-z_]\w*)\s*=(?!=)")
READ_RE = re.compile(r"self\.([A-Za-z_]\w*)")
UPPER_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def strip_comment(line):
	# <!-- custom: Drops a trailing # comment, ignoring # inside simple quotes; good enough for an advisory report. (Claude code Opus 5.5) -->
	out = []
	quote = None
	for ch in line:
		if quote:
			out.append(ch)
			if ch == quote:
				quote = None
		elif ch in "\"'":
			quote = ch
			out.append(ch)
		elif ch == "#":
			break
		else:
			out.append(ch)
	return "".join(out)


def scan_file(path):
	with open(path, encoding="latin-1") as handle:
		lines = handle.read().splitlines()
	classes = {}
	current_class = None
	current_def = None
	for raw in lines:
		match = CLASS_RE.match(raw)
		if match:
			current_class = match.group(1)
			classes[current_class] = {"assign": {}, "reads": {}, "resolution": False}
			current_def = None
			continue
		if current_class is None:
			continue
		match = DEF_RE.match(raw)
		if match:
			current_def = match.group(2)
			continue
		# <!-- custom: A comment at column 0 still belongs to the class, as Python reads it; only code there ends the class.
		# Codex's review found the earlier scan stopping at such a comment. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if raw.lstrip().startswith("#"):
			continue
		if raw and not raw[0].isspace():
			current_class = None
			continue
		line = strip_comment(raw)
		if not line.strip():
			continue
		info = classes[current_class]
		if "getXResolution" in line or "getYResolution" in line:
			info["resolution"] = True
		assigned = set()
		multi = MULTI_ASSIGN_RE.match(line)
		if multi:
			for name in re.findall(r"self\.([A-Za-z_]\w*)", multi.group(1)):
				assigned.add(name)
		else:
			match = re.match(r"^\s*self\.([A-Za-z_]\w*)\s*=(?!=)", line)
			if match:
				assigned.add(match.group(1))
		for name in assigned:
			info["assign"].setdefault(name, set()).add(current_def)
		rhs = line.split("=", 1)[1] if assigned else line
		for name in READ_RE.findall(rhs):
			info["reads"].setdefault(name, set()).add(current_def)
	return classes


def report(path, only_resolution, all_names):
	found = False
	for class_name, info in sorted(scan_file(path).items()):
		if only_resolution and not info["resolution"]:
			continue
		reassigned = []
		unread = []
		for name, defs in sorted(info["assign"].items()):
			if "__init__" not in defs:
				continue
			# <!-- custom: Upper-case names are the screens' layout constants, such as W_SCREEN or X_EXIT; state such as bPlaying or iPage is meant to be set in __init__ and changed later. (Claude code Opus 5.5) -->
			if not all_names and not UPPER_RE.match(name):
				continue
			others = sorted(d for d in defs if d and d != "__init__")
			if others:
				reassigned.append("%s (also in %s)" % (name, ", ".join(others)))
			if name not in info["reads"]:
				unread.append(name)
		if not reassigned and not unread:
			continue
		if not found:
			print("== %s" % path)
			found = True
		print("  class %s%s" % (class_name, " [reads resolution]" if info["resolution"] else ""))
		if reassigned:
			print("    set in __init__ and again later: " + "; ".join(reassigned))
		if unread:
			print("    set in __init__, no read found in this file: " + ", ".join(unread))


def iter_paths(targets):
	for target in targets:
		if os.path.isdir(target):
			for root, _dirs, files in os.walk(target):
				for name in sorted(files):
					if name.endswith(".py"):
						yield os.path.join(root, name)
		else:
			yield target


def main():
	parser = argparse.ArgumentParser(description="Report Civ4 screen attributes set in __init__ and set again later, or not read in their own file.")
	parser.add_argument("paths", nargs="*", default=["Assets/Python"])
	parser.add_argument("--only-resolution", action="store_true", help="only classes that read the resolution somewhere")
	parser.add_argument("--all-names", action="store_true", help="also report lower-case state attributes, not only upper-case layout constants")
	args = parser.parse_args()
	for path in iter_paths(args.paths):
		report(path, args.only_resolution, args.all_names)
	return 0


if __name__ == "__main__":
	sys.exit(main())

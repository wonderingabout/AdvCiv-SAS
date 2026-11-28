#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Moves a group of top-level functions and constants out of a large Python module into a sibling module that reaches the rest as <prefix>.<name>, and checks that nothing was lost, as SASPilotCommands.py was split into SASPilotCatalog.py, SASPilotDiplomacy.py and SASPilotCities.py on 2026-11-28.
# Three steps, run in order:
# - graph: from the commands named, the helpers only they use (the group to move), the names they share with the rest (left in place, reached through the prefix) and the moved names the rest still calls.
# - move: moves the group verbatim, each definition with the comments directly above it and, for a command, its help line wherever it is, adding the prefix to the shared names; writes the new module under its header.
# - check: compares the module before with the two files after, line for line once the prefix is removed, and lists names the new module uses but neither defines nor imports.
# Written as scratchpad scripts during that split and kept here, as the next split needs them again (AGENTS.md). Where it tripped: the first name check counted only definitions and plain imports, so a name the old module had from `from SASUtils import getInfoTypeOrFail` reached the game unresolved and 'trainable' raised NameError; it now counts from-imports and classes too. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the steps; json the move's config; re finds definitions, names and string literals. (Claude code Opus 5.5) -->
import argparse
import json
import re
import sys
# <!-- custom: Counter compares the lines before and after a move; Path reads and writes the files. (Claude code Opus 5.5) -->
from collections import Counter
from pathlib import Path


def read(path):
	return Path(path).read_text(encoding="utf-8")


def top_level(text):
	# <!-- custom: Each top-level def, class or NAME = assignment, with its line range up to the next one, comment lines left out of the body. (Claude code Opus 5.5) -->
	lines = text.split("\n")
	starts = []
	for i, line in enumerate(lines):
		match = re.match(r"(?:def|class) (\w+)\b", line) or re.match(r"(\w+) = ", line)
		if match:
			starts.append((i, match.group(1)))
	result = {}
	for k, (i, name) in enumerate(starts):
		end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
		result[name] = (i, end, "\n".join(l for l in lines[i:end] if not l.strip().startswith("#")))
	return result


# <!-- custom: Python code split into string literals, comments and the rest, so names are changed only in code: the first version rewrote them inside strings too, return shared, "contains shared" becoming "contains old.shared", and 'check', which stripped the prefix everywhere, passed it (Codex reproduced it, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_TOKENS = re.compile(r'''(?P<string>[uUbBrR]{0,2}(?:"""(?:\\.|[^\\])*?"""|\'\'\'(?:\\.|[^\\])*?\'\'\'|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'))|(?P<comment>#[^\n]*)''')


def in_code(text, change):
	# <!-- custom: Applies change to the parts of text outside string literals and comments. (Claude code Opus 5.5) -->
	parts = []
	last = 0
	for match in _TOKENS.finditer(text):
		parts.append(change(text[last:match.start()]))
		parts.append(match.group(0))
		last = match.end()
	parts.append(change(text[last:]))
	return "".join(parts)


def strip_literals(text):
	# <!-- custom: The text with string literals emptied and comments removed, so a name is found only in code. (Claude code Opus 5.5) -->
	parts = []
	last = 0
	for match in _TOKENS.finditer(text):
		parts.append(text[last:match.start()])
		parts.append('""' if match.group("string") else "")
		last = match.end()
	parts.append(text[last:])
	return "".join(parts)


def qualify(code, name, prefix):
	# <!-- custom: Adds the prefix to name where it is a bare name, not an attribute: a name after a dot is someone's attribute even with spaces between the two, which the first pattern, looking only at the character before, qualified too (Codex reproduced it, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def replace(match):
		if code[:match.start()].rstrip().endswith("."):
			return match.group(0)
		return prefix + "." + name
	return re.sub(r"(?<![\w])" + re.escape(name) + r"\b", replace, code)


def imported_names(text):
	names = set(re.findall(r"^import (\w+)", text, re.M))
	for group in re.findall(r"^from [\w.]+ import ([\w, ]+)$", text, re.M):
		names.update(name.strip() for name in group.split(","))
	return names


def graph(text, commands, prefix, own, external=None):
	defs = top_level(text)
	names = set(defs)
	uses = dict((name, set(n for n in re.findall(r"(?<![\w.\"'])([A-Za-z_]\w*)", body) if n in names and n != name)) for (name, (i, end, body)) in defs.items())
	users = dict((name, set(user for user in names if name in uses[user])) for name in names)
	# <!-- custom: Names other files reach through the prefix count as used outside the group, so they stay: the map's first graph would have moved _yields, which SASPilotCities.py, split out before it, calls as saspilot._yields (2026-11-28). (Claude code Opus 5.5) -->
	for (name, files) in (external or {}).items():
		if name in users:
			users[name] = users[name] | set(files)
	group = set(prefix + command for command in commands)
	missing = [name for name in group if name not in defs]
	if missing:
		raise SystemExit("not found: %s" % ", ".join(missing))
	changed = True
	while changed:
		changed = False
		for name in list(group):
			for dep in uses[name]:
				if dep not in group and not dep.startswith(prefix) and users[dep] <= group | set([dep]):
					group.add(dep)
					changed = True
	# <!-- custom: Less the names the new module defines itself, such as gc and _HELP: the first version listed them as shared, so a move would have reached them through the prefix. (Claude code Opus 5.5) -->
	shared = sorted(set(dep for name in group for dep in uses[name] if dep not in group and dep not in own))
	outside = dict((name, sorted(u for u in users[name] if u not in group)) for name in group if users[name] - group)
	return (sorted(group, key=lambda n: defs[n][0]), shared, outside, defs)


def cmd_graph(args):
	text = read(args.file)
	external = {}
	for sibling in sorted(Path(args.file).parent.glob("*.py")):
		if sibling.resolve() == Path(args.file).resolve():
			continue
		for name in set(re.findall(r"(?<![\w.])" + re.escape(args.prefix) + r"\.(\w+)", strip_literals(read(sibling)))):
			external.setdefault(name, []).append(sibling.name)
	(group, shared, outside, defs) = graph(text, args.commands.split(","), args.command_prefix, set(args.own.split(",")), external)
	print("move %d definitions:" % len(group))
	for name in group:
		print("  %5d %s" % (defs[name][0] + 1, name))
	print("shared, left in place and reached through the prefix: %s" % ", ".join(shared))
	print("moved names the rest still calls: %s" % (json.dumps(outside) if outside else "none"))
	print("For 'move', a JSON config: {\"module\": \"...\", \"move\": %s, \"shared\": %s, \"header\": \"...\"}" % (json.dumps(group), json.dumps(shared)))


def cmd_move(args):
	config = json.loads(read(args.config))
	path = Path(args.file)
	text = path.read_text(encoding="utf-8")
	lines = text.split("\n")
	units = []
	for name in config["move"]:
		pattern = re.compile(r"^(?:def %s\(|class %s\b|%s = )" % ((re.escape(name),) * 3))
		starts = [i for (i, line) in enumerate(lines) if pattern.match(line)]
		if len(starts) != 1:
			raise SystemExit("%s: %d definitions" % (name, len(starts)))
		start = starts[0]
		# <!-- custom: Comments and decorators directly above go with the definition: a decorator left behind applied itself to the next function, and both checks passed (Codex reproduced it, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		while start > 0 and (lines[start - 1].startswith("#") or lines[start - 1].startswith("@")):
			start -= 1
		end = starts[0] + 1
		while end < len(lines) and (lines[end] == "" or lines[end][:1] in ("\t", " ", ")", "}", "]")):
			end += 1
		while lines[end - 1] == "":
			end -= 1
		units.append((start, end, name))
		if name.startswith(args.command_prefix):
			key = args.help_dict + '["%s"]' % name[len(args.command_prefix):]
			helps = [i for (i, line) in enumerate(lines) if re.match(re.escape(key) + r" ?=", line)]
			if len(helps) > 1:
				raise SystemExit("%s: %d help lines" % (key, len(helps)))
			if helps:
				units.append((helps[0], helps[0] + 1, "help " + name))
	units.sort()
	for k in range(len(units) - 1):
		if units[k][1] > units[k + 1][0]:
			raise SystemExit("overlapping parts: %s and %s" % (units[k][2], units[k + 1][2]))
	helps = dict((name[5:], "\n".join(lines[a:b])) for (a, b, name) in units if name.startswith("help "))
	pieces = []
	for (a, b, name) in units:
		if name.startswith("help "):
			continue
		if name in helps:
			pieces.append(helps[name])
		pieces.append("\n".join(lines[a:b]))
	moved = "\n\n\n".join(pieces) + "\n"
	# <!-- custom: A shared name the moved code also binds locally, as a parameter, an assignment, a loop or an except target, is refused, as adding the prefix there gives def cmd_b(old.shared) or rebinds the old module's name (Codex reproduced the parameter case, 2026-11-28).
	# Found by the target Python's own parser, which marks every binding: the first check matched text one line at a time, so a target spread over several lines, such as a tuple, passed, and the move then changed game state (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	bound = bound_names(args.python, moved, config["shared"])
	if bound:
		raise SystemExit("the moved code binds shared names locally: %s; rename them there first" % ", ".join(bound))
	for name in config["shared"]:
		moved = in_code(moved, lambda code: qualify(code, name, args.prefix))
	taken = set()
	for (a, b, name) in units:
		taken.update(range(a, b))
	kept = re.sub(r"\n{4,}", "\n\n\n", "\n".join(line for (i, line) in enumerate(lines) if i not in taken))
	# <!-- custom: The config's module is a bare name, such as SASPilotMap, written beside the old file; a path, as first given for SASPilotExpansion (2026-11-28), failed in pathlib with "Invalid name 'SASPilot/game/SASPilotExpansion.py.py'", so it is named plainly now. (Claude code Opus 5.5) -->
	if "/" in config["module"] or "\\" in config["module"] or config["module"].endswith(".py"):
		raise SystemExit("module %r: give the bare module name, such as SASPilotMap; it is written beside %s" % (config["module"], path.name))
	target = path.with_name(config["module"] + ".py")
	if target.exists():
		raise SystemExit("%s exists" % target)
	# <!-- custom: Both results are compiled before either is written, with the Python that runs them (--python, by default Civ4's 2.4 where installed), so a move that breaks the syntax writes nothing. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	compile_check(args.python, [config["header"] + moved, kept])
	if args.dry_run:
		print("would move %d parts, %d lines, to %s" % (len(units), len(taken), target))
		return
	target.write_text(config["header"] + moved, encoding="utf-8", newline="\n")
	path.write_bytes(kept.encode("utf-8"))
	print("moved %d parts, %d lines, to %s" % (len(units), len(taken), target))


# <!-- custom: Run by Python 2.4, the game's: the names bound in a source file, by its own parser's AST, whose assignment, loop, except and comprehension targets are AssName nodes and whose function and lambda parameters are argnames. (Claude code Opus 5.5) -->
_BOUND_NAMES_24 = """
import compiler, sys
def walk(node, names):
	if isinstance(node, compiler.ast.AssName):
		names[node.name] = 1
	if isinstance(node, compiler.ast.Function) or isinstance(node, compiler.ast.Lambda):
		for arg in compiler.ast.flatten(node.argnames):
			names[arg] = 1
	if isinstance(node, compiler.ast.Global):
		for name in node.names:
			names[name] = 1
	if isinstance(node, compiler.ast.Import) or isinstance(node, compiler.ast.From):
		for (name, alias) in node.names:
			names[alias or name.split(".")[0]] = 1
	for child in node.getChildNodes():
		walk(child, names)
names = {}
tree = compiler.parseFile(sys.argv[1])
for statement in tree.node.nodes:
	if isinstance(statement, compiler.ast.Function):
		walk(statement, names)
	else:
		for child in statement.getChildNodes():
			walk(child, names)
print " ".join(names.keys())
"""


def run_python(python, script, text):
	# <!-- custom: subprocess runs the target Python on a temporary copy of the text, which tempfile makes. (Claude code Opus 5.5) -->
	import subprocess
	import tempfile
	with tempfile.NamedTemporaryFile("wb", suffix=".py", delete=False) as handle:
		handle.write(text.encode("utf-8"))
	try:
		return subprocess.run([python, "-c", script, handle.name], capture_output=True, text=True)
	finally:
		Path(handle.name).unlink()


def bound_names(python, text, shared):
	# <!-- custom: The shared names the text binds; the module-level definitions moved with it are not bindings of a shared name, as shared names are by definition left in place.
	# Without Python 2.4, Python 3's ast, which cannot read Python 2-only syntax such as print statements. (Claude code Opus 5.5) -->
	if python and Path(python).exists():
		result = run_python(python, _BOUND_NAMES_24, text)
		if result.returncode:
			raise SystemExit("the moved code does not parse with %s: %s" % (python, (result.stderr.strip().splitlines() or ["?"])[-1]))
		names = set(result.stdout.split())
	else:
		# <!-- custom: ast, Python 3's parser, only when the target's Python is not installed. (Claude code Opus 5.5) -->
		import ast
		names = set()
		for node in ast.walk(ast.parse(text)):
			if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
				names.add(node.id)
			elif isinstance(node, ast.arg):
				names.add(node.arg)
	return sorted(name for name in shared if name in names)


def compile_check(python, texts):
	# <!-- custom: With the target's compile(), not only its parser: compiler.parseFile, the first check, accepts a top-level return, which Python 2.4's compile() rejects (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not python or not Path(python).exists():
		for text in texts:
			try:
				compile(text, "<split>", "exec")
			except SyntaxError as error:
				raise SystemExit("the result does not compile: %s (checked with this Python; pass --python for the target's)" % error)
		return
	for text in texts:
		result = run_python(python, "import sys; compile(open(sys.argv[1], 'rU').read() + '\\n', sys.argv[1], 'exec')", text)
		if result.returncode:
			raise SystemExit("the result does not compile with %s: %s" % (python, (result.stderr.strip().splitlines() or ["?"])[-1]))


def cmd_check(args):
	before = read(args.before)
	after = read(args.file)
	module = read(args.module)
	prefix = re.compile(r"(?<![\w.])" + re.escape(args.prefix) + r"\.")
	body = in_code(module, lambda code: prefix.sub("", code))
	lines_before = Counter(line for line in before.split("\n") if line.strip())
	lines_after = Counter(line for line in (after + "\n" + body).split("\n") if line.strip())
	missing = lines_before - lines_after
	extra = lines_after - lines_before
	print("lines missing %d, extra %d (the new module's header and imports count as extra)" % (sum(missing.values()), sum(extra.values())))
	for line in list(missing)[:10]:
		print("  - " + line[:120])
	code = "\n".join(line for line in module.split("\n") if not line.strip().startswith("#"))
	code = re.sub(r'"(\\.|[^"\\])*"', '""', code)
	code = re.sub(r"'(\\.|[^'\\])*'", "''", code)
	used = set(re.findall(r"(?<![\w.])([A-Za-z_]\w*)", code))
	defined = set(top_level(module)) | imported_names(module)
	rest = set(top_level(after)) | imported_names(after)
	unresolved = sorted(name for name in used - defined if name in rest)
	print("names the new module uses from the old one without the prefix: %s" % (", ".join(unresolved) or "none"))
	return 1 if missing or unresolved else 0


def main():
	parser = argparse.ArgumentParser(description="Split a group of commands and their helpers out of a large Python module into a sibling module.")
	parser.add_argument("--command-prefix", default="cmd_", help="the prefix of command functions, default cmd_")
	sub = parser.add_subparsers(dest="step", required=True)
	step = sub.add_parser("graph", help="list the group to move from the commands named, and what it shares")
	step.add_argument("file")
	step.add_argument("commands", help="comma-separated command names without the prefix, e.g. city,produce")
	step.add_argument("--own", default="gc,_HELP", help="names the new module defines itself, default gc,_HELP")
	step.add_argument("--prefix", default="saspilot", help="the name the other files in the folder reach this module by; their references keep a helper in place, default saspilot")
	step = sub.add_parser("move", help="move the group of a JSON config ('graph' prints one) into a new module")
	step.add_argument("file")
	step.add_argument("config")
	step.add_argument("--prefix", default="saspilot", help="the name the new module reaches the old one by, default saspilot")
	step.add_argument("--help-dict", default="_HELP", help="the dict holding each command's help, default _HELP")
	step.add_argument("--dry-run", action="store_true")
	step.add_argument("--python", default="C:/Python24/python.exe", help="the Python that compiles the results, default Civ4's 2.4 at C:/Python24; without it, this one")
	step = sub.add_parser("check", help="compare a copy of the module before the move with the two files after")
	step.add_argument("before")
	step.add_argument("file")
	step.add_argument("module")
	step.add_argument("--prefix", default="saspilot")
	args = parser.parse_args()
	if args.step == "graph":
		cmd_graph(args)
	elif args.step == "move":
		cmd_move(args)
	else:
		sys.exit(cmd_check(args))


if __name__ == "__main__":
	main()

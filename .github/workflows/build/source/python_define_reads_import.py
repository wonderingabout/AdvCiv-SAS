#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: runtime Python reads no GlobalDefine while its module is imported.
# <!-- custom: A define read at module level, or in a class body, runs once at import and keeps that value for the session, so a live override never reaches it; AGENTS.md prefers reading after setup, lazily, as early reads were linked to instability in KI#128.
# The 2026-11-26 inventory found 16 such reads, 15 SAS switches in the Sevopedia and BUG's PEACE_TREATY_LENGTH in MoreCiv4lerts.py, all now read at use; this check keeps new ones out, repo-wide. See KI#128.6. (Claude code Opus 5.5) -->

# <!-- custom: argparse reads the options, io feeds each file to tokenize, pathlib walks the folders, sys reports the result and tokenize tells function bodies from module code. (Claude code Opus 5.5) -->
import argparse
import io
from pathlib import Path
# <!-- custom: re finds module-level constructions, class methods, and the define reads and method calls in them. (Claude code Opus 5.5) -->
import re
import sys
import tokenize

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

# <!-- custom: The shared repository-root default, as the other source checks use. (Claude code Opus 5.5) -->
from xml_defines import get_default_repo_root
# <!-- custom: The ci_import_call: marker, which exempts a module-level call whose define reads cannot run at import. (Claude code Opus 5.5) -->
from ci_markers import IMPORT_CALL


SCAN_RELATIVE_DIRS = (Path("Assets/Python"), Path("PrivateMaps"))
READERS = ("getDefineINT", "getDefineFLOAT", "getDefineSTRING", "getDefineBOOL")
# <!-- custom: SASCurrentDefines read at import would cache as early, so its getters count too, after their module name. (Claude code Opus 5.5) -->
CURRENT_READERS = ("getInt", "getFloat", "getString")
SKIPPED = (tokenize.NL, tokenize.COMMENT)


def read_text(path):
	data = path.read_bytes()
	try:
		return data.decode("utf-8")
	except UnicodeDecodeError:
		return data.decode("latin-1")


def import_time_reads(text):
	# <!-- custom: Tokens rather than indentation decide scope: a def's signature can span several lines with comments at another indent, as CvMapGeneratorUtil's __init__ signatures do, which misled the first line-based audit.
	# Each INDENT opens the block of the statement before it, a def, a class or anything else; a read counts only when no def body encloses it, a one-line def or a lambda body included. (Claude code Opus 5.5) -->
	# <!-- custom: A def's header and a lambda's arguments run where they stand: the first version treated the whole line as a function, so def f(x=gc.getDefineINT("X")), lambda x=gc.getDefineINT("X"): x and (lambda: None, gc.getDefineINT("X")) passed, as Codex reproduced.
	# So a def's body starts at the colon closing its header, and a lambda's body runs from its colon to the comma or bracket closing it at its own depth. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	stack = []
	head = None
	last_head = None
	depth = 0
	header_depth = None
	body_line = False
	lambdas = []
	reader = None
	previous = []
	hits = []
	for token in tokenize.generate_tokens(io.StringIO(text).readline):
		kind = token.type
		if kind in SKIPPED:
			continue
		if kind == tokenize.INDENT:
			stack.append(last_head)
			continue
		if kind == tokenize.DEDENT:
			stack.pop()
			continue
		if kind == tokenize.NEWLINE:
			last_head = head
			head = None
			header_depth = None
			body_line = False
			lambdas = []
			reader = None
			continue
		if head is None:
			head = token.string if kind == tokenize.NAME and token.string in ("def", "class") else "other"
		in_function = body_line or [entry for entry in lambdas if entry[1]]
		if reader is not None and kind == tokenize.OP and token.string == "(":
			if "def" not in stack and not in_function:
				hits.append((reader.start[0], reader.string))
		reader = None
		if kind == tokenize.OP:
			if token.string in "([{":
				depth += 1
			elif token.string in ")]}":
				depth -= 1
				lambdas = [entry for entry in lambdas if entry[0] <= depth]
			elif token.string == ":":
				if header_depth == depth:
					header_depth = None
					body_line = True
				elif lambdas and lambdas[-1][0] == depth and not lambdas[-1][1]:
					lambdas[-1][1] = True
			elif token.string == ",":
				lambdas = [entry for entry in lambdas if not (entry[1] and entry[0] == depth)]
		if kind == tokenize.NAME:
			if token.string == "def":
				header_depth = depth
			elif token.string == "lambda":
				lambdas.append([depth, False])
			elif token.string in READERS or (token.string in CURRENT_READERS and previous[-2:] == ["SASCurrentDefines", "."]):
				reader = token
		previous = (previous + [token.string])[-2:]
	return hits


# <!-- custom: Code a module runs at import also runs what it calls: an object built at module level, such as CvScreensInterface's mainInterface = CvMainInterface.CvMainInterface(), runs its __init__, and a function called there runs its body, so a define read in them runs at import too, which the token scan above cannot see.
# KI#128.6 left these out, counting 51 SAS and 4 inherited __init__ reads. Run on 2026-11-26 on that commit's tree and today's, this pass found none in the paths it follows: those reads sit in classes built later, mostly Sevopedia pages built on first opening.
# Its only finds were two reads behind CvEventInterface's initAfterReload(), which runs them only once BugInit.init() succeeds, not on the normal first import, so that call carries the ci_import_call: marker. See KI#128.6. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
READ_CALL = re.compile(r"\b(?:getDefine(?:INT|FLOAT|STRING|BOOL)|SASCurrentDefines\s*\.\s*get(?:Int|Float|String))\s*\(")
CALL = re.compile(r"(?<![\w.])((?:[A-Za-z_]\w*\s*\.\s*)*)([A-Za-z_]\w*)\s*\(")


class Module:
	# <!-- custom: One file's code as Python tokens: each line's code with strings emptied and comments dropped, its def and class blocks with their line ranges, and the names it imports.
	# Built from tokens rather than line patterns: Codex's review (GPT-6.2-Sol) reproduced a line-based first version following self.later() from a comment and giving a decorator's lambda to the method before it (2026-11-26). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def __init__(self, path, text):
		self.path = path
		self.code = {}
		self.comments = {}
		self.blocks = []
		self.parse(text)
		self.top = dict(((block["name"], block) for block in self.blocks if block["parent"] is None))
		self.imported, self.star, self.aliases = {}, [], {}
		for line in text.split("\n"):
			match = re.match(r"\s*from\s+([\w.]+)\s+import\s+(.+)", line)
			if match and match.group(2).strip() == "*":
				self.star.append(match.group(1).split(".")[-1].lower())
			elif match:
				for item in match.group(2).replace("(", "").replace(")", "").split(","):
					parts = item.split()
					if parts:
						self.imported[parts[-1]] = (match.group(1).split(".")[-1].lower(), parts[0])
			match = re.match(r"\s*import\s+(.+)", line)
			if match:
				for item in match.group(1).split(","):
					parts = item.split()
					if parts:
						self.aliases[parts[-1]] = parts[0].split(".")[-1].lower()

	def parse(self, text):
		stack, header, pending, depth, level, start = [], None, None, 0, 0, True
		for token in tokenize.generate_tokens(io.StringIO(text).readline):
			kind, line = token.type, token.start[0]
			if kind == tokenize.INDENT:
				level += 1
				if pending is not None:
					pending["level"] = level
					stack.append(pending)
					pending = None
				continue
			if kind == tokenize.DEDENT:
				level -= 1
				while stack and stack[-1]["level"] > level:
					stack.pop()["end"] = line - 1
				continue
			if kind == tokenize.NEWLINE:
				if header is not None and header["inline"]:
					header["end"] = line
				elif header is not None:
					pending = header
				header, start = None, True
				continue
			if kind == tokenize.COMMENT:
				self.comments[line] = token.string
				continue
			if kind in (tokenize.NL, tokenize.ENDMARKER):
				continue
			self.code.setdefault(line, []).append('""' if kind == tokenize.STRING else token.string)
			if start and kind == tokenize.NAME and token.string in ("def", "class"):
				header = {"kind": token.string, "name": None, "start": line, "end": line, "parent": stack[-1] if stack else None, "bases": [], "colon": False, "inline": False}
				self.blocks.append(header)
			elif header is not None and header["name"] is None and kind == tokenize.NAME:
				header["name"] = token.string
			elif header is not None and not header["colon"]:
				if token.string in ("(", "[", "{"):
					depth += 1
					if header["kind"] == "class" and depth == 1:
						header["bases"].append("")
				elif token.string in (")", "]", "}"):
					depth -= 1
				elif token.string == ":" and depth == 0:
					header["colon"] = True
				elif header["kind"] == "class" and depth == 1 and token.string == ",":
					header["bases"].append("")
				elif header["kind"] == "class" and depth == 1:
					# <!-- custom: A base keeps its dotted name, such as a.Base, which a first version split into a and Base, so class C(a.Base) lost its base (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
					header["bases"][-1] += token.string
			elif header is not None:
				header["inline"] = True
			start = False
		for block in stack:
			block["end"] = max(self.code) if self.code else block["start"]

	def lines(self, block):
		# <!-- custom: A block's own lines as token lists, without those of the defs nested in it, which run only when called; None gives the module's code outside every def, class bodies included, as they run at import. (Claude code Opus 5.5) -->
		inner = [other for other in self.blocks if other["kind"] == "def" and other is not block and (block is None or (other["start"] > block["start"] and other["end"] <= block["end"]))]
		numbers = sorted(self.code) if block is None else [number for number in sorted(self.code) if block["start"] <= number <= block["end"]]
		kept = []
		for number in numbers:
			nested = [other for other in inner if other["start"] <= number <= other["end"]]
			# <!-- custom: A nested def's own header line stays, as its default arguments run when the enclosing code does. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			if not nested or [other for other in nested if other["start"] == number] or (block is not None and number == block["start"]):
				kept.append((number, self.code[number]))
		return kept

	def exempt(self, number):
		# <!-- custom: Whether a comment on line number, or the comment-only lines just above it, carries the ci_import_call: marker with a reason after it.
		# Comments come from the tokens, so the token in a string does not count, as Codex's review found of a first version reading raw text (2026-11-26). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		def marked(text):
			if IMPORT_CALL not in text:
				return False
			reason = text.split(IMPORT_CALL, 1)[1].replace("-->", "").strip()
			return bool(re.sub(r"\([^)]*\)\s*$", "", reason).strip())
		if marked(self.comments.get(number, "")):
			return True
		index = number - 1
		while index > 0 and index in self.comments and index not in self.code:
			if marked(self.comments[index]):
				return True
			index -= 1
		return False

	def method(self, cls, name):
		return next((block for block in self.blocks if block["parent"] is cls and block["name"] == name), None)


def eager_code(tokens, own_header):
	# <!-- custom: The part of a line that runs when the code around it runs, joined for the call pattern.
	# A def or class header runs only its default arguments or bases, while own_header, the followed block's own header, runs only a one-line body after its colon; a lambda's body runs only when called, but its default arguments now.
	# A first version did the reverse for both, missing def f(x=read()) and following f = lambda: read(), as Codex's review reproduced (2026-11-26). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if tokens and tokens[0] in ("def", "class"):
		depth, colon = 0, len(tokens)
		for (index, token) in enumerate(tokens):
			if token in ("(", "[", "{"):
				depth += 1
			elif token in (")", "]", "}"):
				depth -= 1
			elif token == ":" and depth == 0:
				colon = index
				break
		tokens = tokens[colon + 1:] if own_header else tokens[2:colon]
	kept, skipping, depth = [], None, 0
	for token in tokens:
		if token in ("(", "[", "{"):
			depth += 1
		elif token in (")", "]", "}"):
			depth -= 1
			if skipping is not None and depth < skipping[0]:
				skipping = None
		if skipping is not None:
			if skipping[1] and token == ":" and depth == skipping[0]:
				skipping = (skipping[0], False)
			elif not skipping[1] and token == "," and depth == skipping[0]:
				skipping = None
			elif skipping[1]:
				kept.append(token)
			continue
		if token == "lambda":
			skipping = (depth, True)
			continue
		kept.append(token)
	return " ".join(kept)


def constructed_at_import_reads(texts):
	# <!-- custom: texts maps each scanned file's path to its text.
	# Returns (path, line, callable, origin path, origin line) for each define read in code that module-level code calls, directly or through other calls, so at import.
	# From each module's code outside its defs it follows the classes it builds, into __init__ along the base classes, and the functions it calls; in them, calls through self, resolved from the class actually built so an override wins, by a dotted name such as a.Base.__init__(self), or by a name the file defines or imports; transitively, objects built inside followed code included.
	# A name is found in its own file, or where the file imports it from, by name, alias or *; a call it cannot resolve, such as an engine method, is not followed, and a call whose reads depend on a run-time test is followed whatever the test. See KI#128.6. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	modules = {}
	for (path, text) in texts.items():
		# <!-- custom: A file the token scan above could not tokenize is reported there already; skipping it here keeps that report from being lost to a second TokenError (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		try:
			modules[path] = Module(path, text)
		except (tokenize.TokenError, IndentationError, SyntaxError):
			continue
	by_name = {}
	for path in sorted(modules):
		by_name.setdefault(path.stem.lower(), modules[path])

	def chain_method(module, cls, name, seen=None):
		seen = seen or set()
		if (module.path, cls["start"]) in seen:
			return None
		seen.add((module.path, cls["start"]))
		found = module.method(cls, name)
		if found is not None:
			return (module, found)
		for base in cls["bases"]:
			target = resolve(module, [part for part in base.split(".") if part], None)
			if target is not None and target[1]["kind"] == "class":
				result = chain_method(target[0], target[1], name, seen)
				if result is not None:
					return result
		return None

	def resolve(module, parts, self_class):
		# <!-- custom: Resolves a dotted name, such as Base, a.Base or a.Base.__init__, to (module, block): a module alias leads into that module, a class into its methods along its bases, and self into the class actually built. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if not parts:
			return None
		if parts[0] == "self":
			return chain_method(self_class[0], self_class[1], parts[1]) if self_class is not None and len(parts) == 2 else None
		current = None
		if module.top.get(parts[0]) is not None:
			current = (module, module.top[parts[0]])
		elif parts[0] in module.imported:
			(source, original) = module.imported[parts[0]]
			other = by_name.get(source)
			current = (other, other.top[original]) if other is not None and other.top.get(original) is not None else None
		elif parts[0] in module.aliases:
			current = (by_name.get(module.aliases[parts[0]]), None)
		else:
			current = next(((by_name[source], by_name[source].top[parts[0]]) for source in module.star if source in by_name and by_name[source].top.get(parts[0]) is not None), None)
		for part in parts[1:]:
			if current is None or current[0] is None:
				return None
			if current[1] is None:
				current = (current[0], current[0].top[part]) if current[0].top.get(part) is not None else None
			elif current[1]["kind"] == "class":
				current = chain_method(current[0], current[1], part)
			else:
				return None
		return current if current is not None and current[1] is not None else None

	def callees(module, block, tokens, number, self_class):
		code = eager_code(tokens, block is not None and number == block["start"])
		for (chain, name) in CALL.findall(code):
			parts = [part.strip() for part in chain.split(".") if part.strip()] + [name]
			found = resolve(module, parts, self_class)
			if found is None:
				continue
			if found[1]["kind"] == "class":
				# <!-- custom: Building a class runs its __init__, found along its bases, with self being the class built, so a base's self.read() finds the subclass's override (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
				built = found
				found = chain_method(found[0], found[1], "__init__")
				if found is not None:
					yield (found, built)
			else:
				yield (found, self_class if parts[0] == "self" or len(parts) > 1 and found[1]["parent"] is not None else None)

	hits, seen = [], set()
	for path in sorted(modules):
		module = modules[path]
		pending = []
		for (number, tokens) in module.lines(None):
			if module.exempt(number):
				continue
			pending.extend((target, self_class, (path, number)) for (target, self_class) in callees(module, None, tokens, number, None))
		while pending:
			((target, block), self_class, origin) = pending.pop()
			key = (target.path, block["start"], None if self_class is None else (self_class[0].path, self_class[1]["start"]))
			if key in seen:
				continue
			seen.add(key)
			name = block["name"] if block["parent"] is None else block["parent"]["name"] + "." + block["name"]
			for (number, tokens) in target.lines(block):
				if READ_CALL.search(eager_code(tokens, number == block["start"])):
					hits.append((target.path, number, name, origin[0], origin[1]))
				pending.extend((found, context, origin) for (found, context) in callees(target, block, tokens, number, self_class))
	return sorted(set(hits))


def main(argv=None):
	parser = argparse.ArgumentParser(description="Check that runtime Python reads no GlobalDefine at import.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args(argv)
	errors = []
	count = 0
	texts = {}
	for relative in SCAN_RELATIVE_DIRS:
		for path in sorted((args.repo_root / relative).rglob("*.py")):
			count += 1
			rel = path.relative_to(args.repo_root).as_posix()
			texts[path] = read_text(path)
			try:
				hits = import_time_reads(texts[path])
			except (tokenize.TokenError, IndentationError, SyntaxError) as error:
				errors.append("%s: could not be tokenized (%s), so its define reads were not checked" % (rel, error))
				continue
			for line, name in hits:
				errors.append("%s:%d: %s runs at import, so its value is kept for the session and an override never reaches it; read it at use, through SASCurrentDefines for a SAS define" % (rel, line, name))
	for (target, line, name, origin, origin_line) in constructed_at_import_reads(texts):
		errors.append("%s:%d: a define read in %s, which runs at import, reached from module-level code at %s:%d; read it at use, through SASCurrentDefines for a SAS define (KI#128.6)" % (target.relative_to(args.repo_root).as_posix(), line, name, origin.relative_to(args.repo_root).as_posix(), origin_line))
	print("%s Python define reads at import (%d files)" % ("FAIL" if errors else "PASS", count))
	for error in errors:
		print("  - " + error)
	return bool(errors)


if __name__ == "__main__":
	sys.exit(main())

#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Share the JSON layout used by the UI maps, saved window positions, and console replies.
# Formatting just "usage" in app_layouts.json leaves the composer layouts in their compact table-like form. (GPT-6.1-Sol) -->
import argparse
import json
import re
import sys
from pathlib import Path


def unique_object(pairs):
	result = {}
	for key, value in pairs:
		if key in result:
			raise ValueError(f"duplicate JSON key: {key!r}")
		result[key] = value
	return result


def _inline_json(value, indent, inline_width, level, sort_keys):
	# <!-- custom: An array or object whose compact form fits inline_width (counting its indentation) stays on one line; larger ones open one member per line.
	# Added for SASPilotConsole.py --pretty, where a 'workers' reply's plot rows each fit on a line (2026-11-14). (Claude code Opus 5.5) -->
	compact = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=sort_keys, separators=(", ", ": "))
	if not isinstance(value, (dict, list)) or len(compact) + level * indent <= inline_width or not value:
		return compact
	pad = " " * (indent * (level + 1))
	if isinstance(value, dict):
		items = sorted(value.items()) if sort_keys else value.items()
		members = ["%s%s: %s" % (pad, json.dumps(key, ensure_ascii=False), _inline_json(member, indent, inline_width, level + 1, sort_keys)) for key, member in items]
		return "{\n" + ",\n".join(members) + "\n" + " " * (indent * level) + "}"
	members = [pad + _inline_json(member, indent, inline_width, level + 1, sort_keys) for member in value]
	return "[\n" + ",\n".join(members) + "\n" + " " * (indent * level) + "]"


def format_json(value, indent, inline_width=0, *, sort_keys=False):
	if inline_width > 0:
		return _inline_json(value, indent, inline_width, 0, sort_keys)
	text = json.dumps(value, indent=indent, ensure_ascii=False, allow_nan=False, sort_keys=sort_keys)
	# <!-- custom: JSON escapes newlines inside strings, so this only matches actual arrays.
	# Keep one coordinate or crop rectangle per line, as in map_sevopedia.py. (GPT-6.1-Sol) -->
	return re.sub(r"\[\n +(-?\d+(?:,\n +-?\d+)*)\n *\]",
		lambda match: "[" + re.sub(r"\n +", " ", match[1]) + "]", text)


def format_document(text, section, indent):
	decoder = json.JSONDecoder(object_pairs_hook=unique_object)
	document = decoder.decode(text)
	newline = "\r\n" if "\r\n" in text else "\n"
	if section is None:
		return (format_json(document, indent) + "\n").replace("\n", newline)
	if not isinstance(document, dict) or section not in document:
		raise ValueError(f"no top-level member named {section!r}")

	# <!-- custom: Walk JSON token boundaries so a key repeated inside a nested object or a string cannot be mistaken for the selected top-level member. (GPT-6.1-Sol) -->
	whitespace = re.compile(r"[ \t\r\n]*")
	position = whitespace.match(text).end() + 1
	while True:
		key_start = whitespace.match(text, position).end()
		key, key_end = decoder.raw_decode(text, key_start)
		after_colon = text.index(":", key_end) + 1
		value_start = whitespace.match(text, after_colon).end()
		value, value_end = decoder.raw_decode(text, value_start)
		if key == section:
			line_prefix = text[text.rfind("\n", 0, key_start) + 1:key_start]
			padding = re.match(r"[ \t]*", line_prefix)[0]
			replacement = format_json(value, indent).replace("\n", newline + padding)
			return text[:value_start] + replacement + text[value_end:]
		position = text.index(",", value_end) + 1


def main():
	parser = argparse.ArgumentParser(description="Format JSON for review, keeping integer arrays inline.")
	parser.add_argument("path", type=Path)
	parser.add_argument("--section", help="Only format this top-level member")
	parser.add_argument("--indent", type=int, choices=range(1, 9), default=2, metavar="1-8")
	mode = parser.add_mutually_exclusive_group()
	mode.add_argument("--in-place", action="store_true", help="Write to the input file instead of stdout")
	mode.add_argument("--check", action="store_true", help="Fail if the input needs formatting")
	args = parser.parse_args()
	try:
		original = args.path.read_bytes()
		formatted = format_document(original.decode("utf-8"), args.section, args.indent)
		output = formatted.encode("utf-8")
		if args.check:
			if output != original:
				parser.error(f"{args.path} needs formatting. Rerun this command with --in-place in place of --check.")
		elif args.in_place:
			if output != original:
				args.path.write_bytes(output)
		else:
			sys.stdout.buffer.write(output)
	except (OSError, ValueError) as error:
		parser.error(str(error))


if __name__ == "__main__":
	main()

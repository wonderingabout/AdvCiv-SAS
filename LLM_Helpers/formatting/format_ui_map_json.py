#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Expand a UI map or one of its top-level sections for review.
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


def format_json(value, indent):
	text = json.dumps(value, indent=indent, ensure_ascii=False, allow_nan=False)
	# <!-- custom: JSON escapes newlines inside strings, so this only matches actual arrays.
	# Keep one coordinate or crop rectangle per line, as in map_sevopedia.py. (GPT-6.1-Sol) -->
	return re.sub(r"\[\n +(-?\d+(?:,\n +-?\d+)*)\n +\]",
		lambda match: "[" + re.sub(r"\n +", " ", match[1]) + "]", text)


def format_document(text, section, indent):
	decoder = json.JSONDecoder(object_pairs_hook=unique_object)
	document = decoder.decode(text)
	newline = "\r\n" if "\r\n" in text else "\n"
	if section is None:
		return (format_json(document, indent) + "\n").replace("\n", newline)
	if not isinstance(document, dict) or section not in document:
		raise ValueError(f"no top-level member named {section!r}")

	# <!-- custom: Walk JSON token boundaries so a key repeated inside a nested object
	# or a string cannot be mistaken for the selected top-level member. (GPT-6.1-Sol) -->
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
	parser = argparse.ArgumentParser(description="Format JSON for UI-map review, keeping integer arrays inline.")
	parser.add_argument("path", type=Path)
	parser.add_argument("--section", help="Only format this top-level member")
	parser.add_argument("--indent", type=int, choices=range(1, 9), default=2, metavar="1-8")
	parser.add_argument("--in-place", action="store_true", help="Write to the input file instead of stdout")
	args = parser.parse_args()
	try:
		original = args.path.read_bytes()
		formatted = format_document(original.decode("utf-8"), args.section, args.indent)
		output = formatted.encode("utf-8")
		if args.in_place:
			if output != original:
				args.path.write_bytes(output)
		else:
			sys.stdout.buffer.write(output)
	except (OSError, ValueError) as error:
		parser.error(str(error))


if __name__ == "__main__":
	main()

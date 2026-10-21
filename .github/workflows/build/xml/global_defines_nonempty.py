#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: GlobalDefines XML entries should have a non-empty name and exactly one non-empty value.

from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

# <!-- custom: Resolve repository/shared-helper paths from this subject subfolder after the workflow-tool reorganization. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root, local_name, child_text_by_local_name

# <!-- custom: Share shipped-file discovery with the loader-capacity check so callback and modular defines participate in the same uniqueness check as root GlobalDefines. (GPT-6.1-Sol) -->
from global_define_lengths import loaded_define_paths


# <!-- custom: Civ4 usually stores boolean defines as integer 0/1 values, but keep this here so a future schema/helper variant fails cleanly instead of looking value-less. (ChatGPT-5.5) -->
VALUE_FIELD_NAMES = ("iDefineIntVal", "fDefineFloatVal", "DefineTextVal", "bDefineBoolVal")


def direct_child_values_by_local_name(node: ET.Element, child_name: str) -> list[str]:
	values: list[str] = []

	for child in list(node):
		if local_name(child.tag) != child_name:
			continue

		values.append((child.text or "").strip())

	return values


# <!-- custom: Share declaration locations across files to catch renamed SAS keys colliding with another shipped setting, not just duplicates inside one XML file.
# Keep the optional standalone-file call; report both locations even when values match, since a repeated key hides independent settings behind load order. (GPT-6.1-Sol) -->
def check_global_defines_file(relative_path: Path, absolute_path: Path, seen_names: dict[str, tuple[Path, int]] | None = None) -> list[str]:
	failures: list[str] = []

	try:
		tree = ET.parse(absolute_path)
	except ET.ParseError as exc:
		return [f"{relative_path}: XML parse error: {exc}"]

	define_nodes = [node for node in tree.getroot().iter() if local_name(node.tag) == "Define"]
	if not define_nodes:
		failures.append(f"{relative_path}: no <Define> entries found")
		return failures

	if seen_names is None:
		seen_names = {}

	for index, define in enumerate(define_nodes, 1):
		name = child_text_by_local_name(define, "DefineName")
		label = name or f"<Define> #{index}"

		if not name:
			failures.append(f"{relative_path}: <Define> #{index} has empty or missing <DefineName>")
		else:
			previous = seen_names.get(name)
			if previous is not None:
				previous_path, previous_index = previous
				failures.append(f"{relative_path}: <Define> #{index}: {name} duplicate <DefineName>; first declared in {previous_path}: <Define> #{previous_index}")
			else:
				seen_names[name] = (relative_path, index)

		present_value_fields: list[str] = []
		nonempty_value_fields: list[str] = []
		empty_value_fields: list[str] = []

		for field_name in VALUE_FIELD_NAMES:
			for value in direct_child_values_by_local_name(define, field_name):
				present_value_fields.append(field_name)
				if value:
					nonempty_value_fields.append(field_name)
				else:
					empty_value_fields.append(field_name)

		if not present_value_fields:
			failures.append(f"{relative_path}: {label} has no recognized define value field")
		elif empty_value_fields:
			failures.append(f"{relative_path}: {label} has empty value field(s): {', '.join(empty_value_fields)}")
		elif len(nonempty_value_fields) > 1:
			failures.append(f"{relative_path}: {label} has more than one non-empty value field: {', '.join(nonempty_value_fields)}")

	return failures


def check_global_defines_nonempty(repo_root: Path) -> list[str]:
	failures: list[str] = []
	paths = loaded_define_paths(repo_root)

	if not paths:
		return ["no shipped GlobalDefines/PythonCallbackDefines XML files found"]

	seen_names: dict[str, tuple[Path, int]] = {}
	for path in paths:
		failures.extend(check_global_defines_file(path.relative_to(repo_root), path, seen_names))

	return failures


def main() -> int:
	parser = argparse.ArgumentParser(description="Check shipped GlobalDefines/PythonCallbackDefines for non-empty entries and globally unique names.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root(), help="repository root; defaults to the root containing .github/")
	args = parser.parse_args()

	failures = check_global_defines_nonempty(args.repo_root)

	if failures:
		print("FAIL GlobalDefines content/uniqueness")
		for failure in failures:
			print(f"  - {failure}")
		return 1

	print("PASS GlobalDefines content/uniqueness")
	return 0


if __name__ == "__main__":
	sys.exit(main())

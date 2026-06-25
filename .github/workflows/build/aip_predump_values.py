#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: Build-check helper: compare LeaderHeadInfo AIP predump values against a lightweight Python mirror of CvLeaderHeadInfo XML defaults plus UWAI::applyPersonalityWeight.
# This is intentionally a separate script from build/aip.py so the always-on AIP release-safety check can stay lightweight while this deeper effective-value mirror can validate committed predump values.
# Direct scalar/simple-array values are checked here, and derived contact/memory aggregate values reuse the same pre-normalization AIP helper logic as the in-game Sevopedia AIP cache. UnitAIWeightModifiers and ImprovementWeightModifiers are not checked because they are not currently displayed/predumped. (ChatGPT-5.5) -->

from __future__ import annotations

import argparse
import ast
import datetime as _datetime
import math
import re
import sys
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

PREDUMP_RELATIVE_PATH = Path("Assets/Python/Contrib/Sevopedia/SevoPediaLeaderCachePredumped.py")
LEADER_XML_RELATIVE_PATH = Path("Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml")
UWAI_DEFINE_NAME = "UWAI_PERSONALITY_PERCENT"
DEFAULTS_LEADER_TYPE = "LEADER_DEFAULTS"
AIP_EXCLUDED_LEADER_TYPES: Tuple[str, ...] = ()

# <!-- custom: Shared AIP enum/type lists, direct field specs, XML array specs, and aggregate key-family metadata are imported from ai_utils_shared_with_civ4.py in configure_shared_aip_constants(). Keeping them shared avoids drifting copies of getter fields, CONTACT_*, MEMORY_*, attitude indexes, and iAggregated* metadata. (ChatGPT-5.5) -->

ATTITUDE_TO_INDEX: Dict[str, int] = {}
FLAVOR_TYPES: Tuple[str, ...] = ()
NO_WAR_ATTITUDE_TYPES: Tuple[str, ...] = ()
CONTACT_TYPES: Tuple[str, ...] = ()
MEMORY_TYPES: Tuple[str, ...] = ()
DIRECT_INT_FIELDS: Tuple[Tuple[str, str, int], ...] = ()
ATTITUDE_THRESHOLD_FIELDS: Tuple[Tuple[str, str, int], ...] = ()
EXTRA_UWAI_ONLY_INT_FIELDS: Tuple[Tuple[str, str, int], ...] = ()
ALL_INT_FIELDS: Tuple[Tuple[str, str, int], ...] = ()
DISPLAY_ARRAY_FIELD_SPECS: Tuple[Tuple[str, str, str, Tuple[str, ...], str], ...] = ()
HIDDEN_ARRAY_FIELD_SPECS: Tuple[Tuple[str, str, str, Tuple[str, ...], str], ...] = ()
ARRAY_FIELD_SPECS: Tuple[Tuple[str, str, str, Tuple[str, ...], str], ...] = ()

RAW_INT_RE = re.compile(r"\((-?\d+)\)")


@dataclass
class LeaderRecord:
	index: int
	type: str
	values: Dict[str, int]


@dataclass
class ComparisonResult:
	leader_index: int
	leader_type: str
	getter_key: str
	expected: int
	actual: Optional[int]
	status: str


def find_repo_root(start: Path) -> Path:
	current = start.resolve()
	for candidate in (current,) + tuple(current.parents):
		if (candidate / "Assets").is_dir() and (candidate / "CvGameCoreDLL").is_dir():
			return candidate
	raise RuntimeError("Could not locate repo root containing Assets/ and CvGameCoreDLL/.")


def strip_xml_namespaces(root: ET.Element) -> None:
	for elem in root.iter():
		if "}" in elem.tag:
			elem.tag = elem.tag.split("}", 1)[1]


def child_text(elem: ET.Element, tag: str) -> Optional[str]:
	child = elem.find(tag)
	if child is None or child.text is None:
		return None
	text = child.text.strip()
	return text if text != "" else None


def parse_int(text: str, path: Path, leader_type: str, tag: str) -> int:
	try:
		return int(text)
	except ValueError as exc:
		raise ValueError(f"{path}: leader {leader_type}: tag {tag} expected int, got {text!r}") from exc


def get_pascal_case_suffix(xml_type: str) -> str:
	# Mirrors the AIP helper convention: FLAVOR_MILITARY -> Military,
	# ATTITUDE_FURIOUS -> Furious.
	parts = [part for part in xml_type.split("_") if part]
	if len(parts) > 1:
		parts = parts[1:]
	return "".join(part[:1] + part[1:].lower() for part in parts)


def array_value_key(key_prefix: str, xml_type: str) -> str:
	return "%s%s" % (key_prefix, get_pascal_case_suffix(xml_type))


def displayed_value_keys(shared_helpers: Any) -> Tuple[str, ...]:
	array_keys: List[str] = []
	for _root_tag, _key_tag, _value_tag, type_names, key_prefix in DISPLAY_ARRAY_FIELD_SPECS:
		for type_name in type_names:
			array_keys.append(array_value_key(key_prefix, type_name))
	# <!-- custom: displayed aggregate keys are shared with the in-game AIP helper layer, so the workflow checker does not duplicate which synthetic contact/memory fields are predumped. (ChatGPT-5.5) -->
	aggregate_keys = shared_helpers.get_aip_displayed_aggregate_value_keys()
	return (
		tuple(getter for getter, _tag, _default in DIRECT_INT_FIELDS)
		+ tuple(getter for getter, _tag, _default in ATTITUDE_THRESHOLD_FIELDS)
		+ tuple(array_keys)
		+ tuple(aggregate_keys)
	)


def uwai_primitive_value_keys() -> Tuple[str, ...]:
	array_keys: List[str] = []
	for _root_tag, _key_tag, _value_tag, type_names, key_prefix in ARRAY_FIELD_SPECS:
		for type_name in type_names:
			array_keys.append(array_value_key(key_prefix, type_name))
	return (
		tuple(getter for getter, _tag, _default in ALL_INT_FIELDS)
		+ tuple(getter for getter, _tag, _default in ATTITUDE_THRESHOLD_FIELDS)
		+ tuple(array_keys)
	)


def constructor_defaults() -> Dict[str, int]:
	values: Dict[str, int] = {}
	for getter, _tag, _explicit_default in ALL_INT_FIELDS:
		values[getter] = 0
	for getter, _tag, constructor_default in ATTITUDE_THRESHOLD_FIELDS:
		values[getter] = constructor_default
	for _root_tag, _key_tag, _value_tag, type_names, key_prefix in ARRAY_FIELD_SPECS:
		for type_name in type_names:
			values[array_value_key(key_prefix, type_name)] = 0
	return values


def read_array_fields(values: Dict[str, int], leader_elem: ET.Element, xml_path: Path, leader_type: str) -> None:
	for root_tag, key_tag, value_tag, type_names, key_prefix in ARRAY_FIELD_SPECS:
		known_types = set(type_names)
		root = leader_elem.find(root_tag)
		if root is None:
			continue
		for item in list(root):
			type_name = child_text(item, key_tag)
			value_text = child_text(item, value_tag)
			if type_name is None or value_text is None:
				continue
			if type_name not in known_types:
				raise ValueError(f"{xml_path}: leader {leader_type}: tag {root_tag}/{key_tag} unknown type {type_name!r}")
			values[array_value_key(key_prefix, type_name)] = parse_int(value_text, xml_path, leader_type, value_tag)


def read_leader_record(base_values: Dict[str, int], leader_elem: ET.Element, xml_path: Path) -> Tuple[str, Dict[str, int]]:
	leader_type = child_text(leader_elem, "Type")
	if leader_type is None:
		raise ValueError(f"{xml_path}: LeaderHeadInfo without <Type>")
	values = deepcopy(base_values)

	for getter, tag, explicit_default in ALL_INT_FIELDS:
		text = child_text(leader_elem, tag)
		if text is not None:
			values[getter] = parse_int(text, xml_path, leader_type, tag)
		else:
			# Mirrors CvLeaderHeadInfo::GetChildXmlValByName: if the copied value is
			# non-zero, it becomes the missing-tag default; otherwise use the explicit
			# default argument from CvLeaderHeadInfo::read.
			values[getter] = values[getter] if values[getter] != 0 else explicit_default

	for getter, tag, _constructor_default in ATTITUDE_THRESHOLD_FIELDS:
		text = child_text(leader_elem, tag)
		if text is None:
			continue
		if text not in ATTITUDE_TO_INDEX:
			raise ValueError(f"{xml_path}: leader {leader_type}: tag {tag} unknown attitude value {text!r}")
		values[getter] = ATTITUDE_TO_INDEX[text]

	read_array_fields(values, leader_elem, xml_path, leader_type)

	return leader_type, values


def read_leaders_from_xml(repo_root: Path) -> List[LeaderRecord]:
	xml_path = repo_root / LEADER_XML_RELATIVE_PATH
	root = ET.parse(str(xml_path)).getroot()
	strip_xml_namespaces(root)
	infos = root.findall("./LeaderHeadInfos/LeaderHeadInfo")
	if not infos:
		raise ValueError(f"{xml_path}: no LeaderHeadInfo entries found")

	leaders: List[LeaderRecord] = []
	defaults_template: Optional[Dict[str, int]] = None
	for info in infos:
		base = constructor_defaults() if defaults_template is None else deepcopy(defaults_template)
		leader_type, values = read_leader_record(base, info, xml_path)
		if leader_type == DEFAULTS_LEADER_TYPE:
			defaults_template = values
			continue
		leaders.append(LeaderRecord(index=len(leaders), type=leader_type, values=values))
	return leaders


def read_global_define_int(repo_root: Path, define_name: str) -> int:
	for path in sorted((repo_root / "Assets" / "XML").rglob("*.xml")):
		try:
			root = ET.parse(str(path)).getroot()
		except ET.ParseError:
			continue
		strip_xml_namespaces(root)
		for define in root.findall(".//Define"):
			name = child_text(define, "DefineName")
			if name != define_name:
				continue
			text = child_text(define, "iDefineIntVal")
			if text is None:
				raise ValueError(f"{path}: {define_name} missing iDefineIntVal")
			return parse_int(text, path, define_name, "iDefineIntVal")
	raise ValueError(f"Could not find {define_name} under Assets/XML")


def median_fraction(values: List[int]) -> Fraction:
	ordered = sorted(values)
	mid = len(ordered) // 2
	if len(ordered) % 2:
		return Fraction(ordered[mid], 1)
	return Fraction(ordered[mid - 1] + ordered[mid], 2)


def round_cpp_scaled(value: Fraction) -> int:
	# Mirrors ScaledNum::round for signed values: add +/- 0.5, then truncate
	# toward zero. For exact Fractions, floor/ceil express that behavior cleanly.
	if value >= 0:
		return math.floor(value + Fraction(1, 2))
	return math.ceil(value - Fraction(1, 2))


def apply_uwai_personality_weight(leaders: List[LeaderRecord], weight: int) -> None:
	if weight == 100:
		return
	personality_leaders = [leader for leader in leaders if leader.type not in AIP_EXCLUDED_LEADER_TYPES]
	if not personality_leaders:
		return
	for getter_key in uwai_primitive_value_keys():
		median = median_fraction([leader.values[getter_key] for leader in personality_leaders])
		for leader in personality_leaders:
			old_value = leader.values[getter_key]
			new_value = (median * (100 - weight) + old_value * weight) / 100
			leader.values[getter_key] = round_cpp_scaled(new_value)


def import_aip_shared_helpers(repo_root: Path) -> Any:
	sevopedia_path = repo_root / "Assets" / "Python" / "Contrib" / "Sevopedia"
	sevopedia_path_text = str(sevopedia_path)
	if sevopedia_path_text not in sys.path:
		sys.path.insert(0, sevopedia_path_text)
	import ai_utils_shared_with_civ4  # pylint: disable=import-error,import-outside-toplevel
	return ai_utils_shared_with_civ4


def configure_shared_aip_constants(shared_helpers: Any) -> None:
	# <!-- custom: Keep enum/type lists, direct getter metadata, Civ4 attitude-index mapping, XML array specs, and aggregate key-family metadata shared with the runtime AIP helpers. (ChatGPT-5.5) -->
	global AIP_EXCLUDED_LEADER_TYPES, ATTITUDE_TO_INDEX, FLAVOR_TYPES, NO_WAR_ATTITUDE_TYPES, CONTACT_TYPES, MEMORY_TYPES
	global DIRECT_INT_FIELDS, ATTITUDE_THRESHOLD_FIELDS, EXTRA_UWAI_ONLY_INT_FIELDS, ALL_INT_FIELDS
	global DISPLAY_ARRAY_FIELD_SPECS, HIDDEN_ARRAY_FIELD_SPECS, ARRAY_FIELD_SPECS
	AIP_EXCLUDED_LEADER_TYPES = tuple(shared_helpers.get_aip_excluded_leader_types())
	ATTITUDE_TO_INDEX = shared_helpers.get_aip_attitude_type_to_index()
	FLAVOR_TYPES = tuple(shared_helpers.get_aip_flavor_types_assessed())
	NO_WAR_ATTITUDE_TYPES = tuple(shared_helpers.get_aip_no_war_attitude_types_assessed())
	CONTACT_TYPES = tuple(shared_helpers.get_aip_contact_types_assessed())
	MEMORY_TYPES = tuple(shared_helpers.get_aip_memory_types_assessed())
	DIRECT_INT_FIELDS = tuple((getter, xml_tag, xml_default) for getter, xml_tag, xml_default, _label, _invert in shared_helpers.get_aip_direct_int_field_specs())
	ATTITUDE_THRESHOLD_FIELDS = tuple((getter, xml_tag, xml_default) for getter, xml_tag, xml_default, _label, _invert in shared_helpers.get_aip_attitude_threshold_field_specs())
	EXTRA_UWAI_ONLY_INT_FIELDS = tuple(shared_helpers.get_aip_extra_uwai_only_int_field_specs())
	ALL_INT_FIELDS = DIRECT_INT_FIELDS + EXTRA_UWAI_ONLY_INT_FIELDS
	DISPLAY_ARRAY_FIELD_SPECS = tuple(shared_helpers.get_aip_display_array_field_specs())
	HIDDEN_ARRAY_FIELD_SPECS = tuple(shared_helpers.get_aip_hidden_array_field_specs())
	ARRAY_FIELD_SPECS = tuple(shared_helpers.get_aip_array_field_specs())


def add_shared_aggregate_display_values_to_leaders(leaders: List[LeaderRecord], shared_helpers: Any) -> None:
	personality_leaders = [leader for leader in leaders if leader.type not in AIP_EXCLUDED_LEADER_TYPES]
	leaders_by_index = {leader.index: leader for leader in personality_leaders}
	non_excluded_leader_indexes = tuple(leaders_by_index.keys())

	def get_contact_rand(iLeader: int, iContact: int) -> int:
		return leaders_by_index[iLeader].values[array_value_key("iContactRand", CONTACT_TYPES[iContact])]

	def get_contact_delay(iLeader: int, iContact: int) -> int:
		return leaders_by_index[iLeader].values[array_value_key("iContactDelay", CONTACT_TYPES[iContact])]

	def get_memory_type(iMemoryIndex: int) -> str:
		return MEMORY_TYPES[iMemoryIndex]

	def get_memory_attitude_percent(iLeader: int, iMemoryIndex: int) -> int:
		return leaders_by_index[iLeader].values[array_value_key("iMemoryAttitudePercent", MEMORY_TYPES[iMemoryIndex])]

	def get_memory_decay_rand(iLeader: int, iMemoryIndex: int) -> int:
		return leaders_by_index[iLeader].values[array_value_key("iMemoryDecay", MEMORY_TYPES[iMemoryIndex])]

	# <!-- custom: The shared helper creates AIP synthetic display values from XML+UWAI raw inputs. For example, it normalizes iAggregatedRawContactProbReligionPressure into iAggregatedContactProbReligionPressure, and iAggregatedRawPositiveMemoryTradedTechToUsAffection into iAggregatedPositiveMemoryTradedTechToUsAffection. The checker supplies XML+UWAI values as a provider, while Sevopedia supplies gc/DLL values. (ChatGPT-5.5) -->
	display_values = shared_helpers.compute_leaders_info_aip_aggregate_display_values(non_excluded_leader_indexes, CONTACT_TYPES, get_contact_rand, get_contact_delay, get_memory_type, get_memory_attitude_percent, get_memory_decay_rand, False, False)
	for leader in personality_leaders:
		leader.values.update(display_values[leader.index])


def read_predump_cache(repo_root: Path) -> Dict[int, Dict[str, Tuple[Any, ...]]]:
	path = repo_root / PREDUMP_RELATIVE_PATH
	module_ast = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
	for node in module_ast.body:
		if isinstance(node, ast.Assign):
			for target in node.targets:
				if isinstance(target, ast.Name) and target.id == "LEADERS_INFO_CACHED":
					value = ast.literal_eval(node.value)
					if not isinstance(value, dict):
						raise ValueError(f"{path}: LEADERS_INFO_CACHED is not a dict")
					return value
	raise ValueError(f"{path}: could not find LEADERS_INFO_CACHED assignment")


def extract_raw_label_value(entry: Tuple[Any, ...]) -> Optional[int]:
	if not entry or not isinstance(entry[0], str):
		return None
	match = RAW_INT_RE.search(entry[0])
	if match is None:
		return None
	return int(match.group(1))


def compare_values(leaders: List[LeaderRecord], predump: Dict[int, Dict[str, Tuple[Any, ...]]], shared_helpers: Any) -> List[ComparisonResult]:
	results: List[ComparisonResult] = []
	for leader in leaders:
		if leader.type in AIP_EXCLUDED_LEADER_TYPES:
			continue
		leader_cache = predump.get(leader.index)
		if leader_cache is None:
			for getter_key in displayed_value_keys(shared_helpers):
				results.append(ComparisonResult(leader.index, leader.type, getter_key, leader.values[getter_key], None, "missing-leader"))
			continue
		for getter_key in displayed_value_keys(shared_helpers):
			entry = leader_cache.get(getter_key)
			if entry is None:
				results.append(ComparisonResult(leader.index, leader.type, getter_key, leader.values[getter_key], None, "missing-field"))
				continue
			if getter_key.startswith("iAggregated"):
				actual = entry[1] if len(entry) > 1 and isinstance(entry[1], int) else None
				if actual is None:
					results.append(ComparisonResult(leader.index, leader.type, getter_key, leader.values[getter_key], None, "unparsed-value"))
					continue
			else:
				actual = extract_raw_label_value(entry)
				if actual is None:
					results.append(ComparisonResult(leader.index, leader.type, getter_key, leader.values[getter_key], None, "unparsed-label"))
					continue
			status = "match" if actual == leader.values[getter_key] else "mismatch"
			results.append(ComparisonResult(leader.index, leader.type, getter_key, leader.values[getter_key], actual, status))
	return results


def normalize_markdown_lines(lines: List[str]) -> List[str]:
	normalized: List[str] = []
	previous_blank = False
	for line in lines:
		is_blank = line.strip() == ""
		if is_blank and previous_blank:
			continue
		normalized.append(line)
		previous_blank = is_blank
	while normalized and normalized[-1].strip() == "":
		normalized.pop()
	return normalized


def write_markdown_report(path: Path, repo_root: Path, leaders: List[LeaderRecord], weight: int, results: List[ComparisonResult], max_mismatches: int) -> None:
	compared = len(results)
	matches = sum(1 for result in results if result.status == "match")
	mismatches = [result for result in results if result.status == "mismatch"]
	missing = [result for result in results if result.status != "match" and result.status != "mismatch"]

	lines: List[str] = []
	lines.append("# Leader AIP predump effective-value check")
	lines.append("")
	lines.append("Current direct-value plus shared derived-aggregate comparison between `CIV4LeaderHeadInfos.xml` and `SevoPediaLeaderCachePredumped.py`.")
	lines.append("")
	lines.append("This helper mirrors the narrow DLL path needed for effective AIP values checked by this script:")
	lines.append("")
	lines.append("- `LEADER_DEFAULTS` copy behavior from `CvXMLLoadUtility::SetGlobalClassInfo`.")
	lines.append("- `CvLeaderHeadInfo::GetChildXmlValByName` missing-tag behavior.")
	lines.append("- `UWAI::applyPersonalityWeight` for scalar primitive fields and checked primitive array/list fields.")
	lines.append("- Shared AIP contact/memory aggregate helpers for derived pre-normalization fields.")
	lines.append("")
	lines.append("Unit AI modifiers and improvement modifiers are intentionally not checked yet because they are not currently displayed/predumped by the AIP panel.")
	lines.append("")
	lines.append("## Summary")
	lines.append("")
	lines.append(f"- Repo root: `{repo_root}`")
	lines.append(f"- Leaders parsed, excluding `{DEFAULTS_LEADER_TYPE}`: {len(leaders)}")
	lines.append(f"- UWAI personality percent: {weight}")
	lines.append(f"- Effective-value entries compared: {compared}")
	lines.append(f"- Matches: {matches}")
	lines.append(f"- Mismatches: {len(mismatches)}")
	lines.append(f"- Missing/unparsed entries: {len(missing)}")
	lines.append("")
	if mismatches:
		lines.append("## Mismatches")
		lines.append("")
		lines.append("| Leader | Getter | Expected from XML+UWAI | Predump raw label |")
		lines.append("|---|---|---:|---:|")
		for result in mismatches[:max_mismatches]:
			lines.append(f"| {result.leader_index}: `{result.leader_type}` | `{result.getter_key}` | {result.expected} | {result.actual} |")
		if len(mismatches) > max_mismatches:
			lines.append("")
			lines.append(f"_Only first {max_mismatches} mismatches shown._")
		lines.append("")
	if missing:
		lines.append("## Missing or unparsed entries")
		lines.append("")
		lines.append("| Leader | Getter | Expected | Status |")
		lines.append("|---|---|---:|---|")
		for result in missing[:max_mismatches]:
			lines.append(f"| {result.leader_index}: `{result.leader_type}` | `{result.getter_key}` | {result.expected} | {result.status} |")
		if len(missing) > max_mismatches:
			lines.append("")
			lines.append(f"_Only first {max_mismatches} missing/unparsed entries shown._")
		lines.append("")
	if not mismatches and not missing:
		lines.append("## Result")
		lines.append("")
		lines.append("All checked direct values and derived aggregate values match the committed predump.")
		lines.append("")
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text("\n".join(normalize_markdown_lines(lines)) + "\n", encoding="utf-8", newline="\n")


def default_output_path(repo_root: Path) -> Path:
	timestamp = _datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
	return repo_root / "LLM_Helpers" / "outputs" / f"leader_aip_predump_values_{timestamp}.md"


def main() -> int:
	parser = argparse.ArgumentParser(description="Compare LeaderHeadInfo AIP predump values against XML+UWAI-emulated effective values.")
	parser.add_argument("--repo-root", type=Path, default=None, help="repository root; defaults to the current tree containing Assets/ and CvGameCoreDLL/")
	parser.add_argument("--output", type=Path, default=None, help="Markdown report path; defaults to LLM_Helpers/outputs/leader_aip_predump_values_<timestamp>.md")
	parser.add_argument("--max-mismatches", type=int, default=120, help="maximum mismatch rows to include in each report section")
	parser.add_argument("--no-uwai", action="store_true", help="debug mode: do not apply UWAI_PERSONALITY_PERCENT before comparing")
	parser.add_argument("--allow-mismatch", action="store_true", help="debug mode: return exit code 0 even when mismatches or missing/unparsed entries are found")
	args = parser.parse_args()

	repo_root = find_repo_root(args.repo_root or Path.cwd())
	shared_helpers = import_aip_shared_helpers(repo_root)
	configure_shared_aip_constants(shared_helpers)
	leaders = read_leaders_from_xml(repo_root)
	weight = read_global_define_int(repo_root, UWAI_DEFINE_NAME)
	if args.no_uwai:
		weight = 100
	else:
		apply_uwai_personality_weight(leaders, weight)
	add_shared_aggregate_display_values_to_leaders(leaders, shared_helpers)
	predump = read_predump_cache(repo_root)
	results = compare_values(leaders, predump, shared_helpers)
	mismatch_count = sum(1 for result in results if result.status == "mismatch")
	missing_count = sum(1 for result in results if result.status != "match" and result.status != "mismatch")
	output_path = args.output or default_output_path(repo_root)
	write_markdown_report(output_path, repo_root, leaders, weight, results, args.max_mismatches)

	print("Leader AIP predump effective-value check")
	print(f"  compared: {len(results)}")
	print(f"  mismatches: {mismatch_count}")
	print(f"  missing/unparsed: {missing_count}")
	print(f"  report: {output_path}")
	if not args.allow_mismatch and (mismatch_count or missing_count):
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())

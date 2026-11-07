#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Audit military-unit continuity across the technology tree.
# The fatal invariant is intentionally narrow: once a playable civilization has at least one unconstrained military unit in a land/sea/air domain, acquiring a reachable combination of technologies in the next technology-tree column must not reduce that domain to zero unconstrained military units.
# "Unconstrained" means trainable from technology alone: no strategic Bonus, religion/corporation/building prerequisite, and no finite UnitClass instance cap.
# Pure exploration units are excluded by role (UNITAI_EXPLORE*) rather than by unit type, so Scout/Explorer/Airship/Recon Drone do not hide a military gap.
# A secondary, non-fatal report lists direct upgrade transitions whose successor adds technology or other conditions not guaranteed when the source obsoletes.
# Those are review candidates, not automatically defects. See KI#537.2. (ChatGPT-5.6-Sol + Claude code Opus 5.5) -->

# <!-- custom: argparse exposes the CLI, itertools enumerates same-column technology combinations, sys returns the exit code, ElementTree reads the XML and defaultdict groups techs and report rows. (ChatGPT-5.6-Sol + Claude code Opus 5.5) -->
import argparse
import itertools
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
# <!-- custom: dataclass holds the parsed records, lru_cache memoizes guaranteed prerequisites and pathlib locates the repository. (ChatGPT-5.6-Sol + Claude code Opus 5.5) -->
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

MOD_ROOT = Path(__file__).resolve().parent.parent
UNIT_INFOS = MOD_ROOT / "Assets/XML/Units/CIV4UnitInfos.xml"
UNIT_CLASS_INFOS = MOD_ROOT / "Assets/XML/Units/CIV4UnitClassInfos.xml"
TECH_INFOS = MOD_ROOT / "Assets/XML/Technologies/CIV4TechInfos.xml"
CIV_INFOS = MOD_ROOT / "Assets/XML/Civilizations/CIV4CivilizationInfos.xml"

UNIT_NS = {"x": "x-schema:CIV4UnitSchema.xml"}
TECH_NS = {"x": "x-schema:CIV4TechnologiesSchema.xml"}
CIV_NS = {"x": "x-schema:CIV4CivilizationsSchema.xml"}
TRACKED_DOMAINS = ("DOMAIN_LAND", "DOMAIN_SEA", "DOMAIN_AIR")


@dataclass(frozen=True)
class Tech:
	type: str
	grid_x: int
	and_prereqs: tuple[str, ...]
	or_prereqs: tuple[str, ...]


@dataclass(frozen=True)
class UnitClass:
	type: str
	default_unit: str
	max_global: int
	max_team: int
	max_player: int

	@property
	def unlimited(self) -> bool:
		return self.max_global < 0 and self.max_team < 0 and self.max_player < 0


@dataclass(frozen=True)
class Unit:
	type: str
	unit_class: str
	domain: str
	default_ai: str
	enabled_ais: tuple[str, ...]
	military_production: bool
	cost: int
	prereq_techs: frozenset[str]
	obsolete_tech: str | None
	primary_bonus: str | None
	or_bonuses: tuple[str, ...]
	prereq_religion: str | None
	state_religion: str | None
	prereq_corporation: str | None
	prereq_building: str | None
	upgrade_classes: tuple[str, ...]

	@property
	def exploration_only(self) -> bool:
		# <!-- custom: Role-based rather than unit-type-based: this catches the current Scout, Explorer, Airship and Robotic Recon Drone without naming any of them. (ChatGPT-5.6-Sol + Claude code Opus 5.5) -->
		if not self.default_ai.startswith("UNITAI_EXPLORE"):
			return False
		return not self.enabled_ais or all(ai.startswith("UNITAI_EXPLORE") for ai in self.enabled_ais)

	@property
	def military(self) -> bool:
		return self.military_production and not self.exploration_only

	@property
	def unconstrained(self) -> bool:
		return (
			not self.primary_bonus
			and not self.or_bonuses
			and not self.prereq_religion
			and not self.state_religion
			and not self.prereq_corporation
			and not self.prereq_building
		)


@dataclass(frozen=True)
class Civ:
	type: str
	unit_overrides: dict[str, str]


def _text(node, tag, ns):
	value = node.findtext("x:" + tag, namespaces=ns)
	return value if value and value != "NONE" else None


def _texts(node, path, ns):
	return tuple(e.text for e in node.findall(path, ns) if e.text and e.text != "NONE")


def _int(node, tag, ns, default=0):
	value = node.findtext("x:" + tag, namespaces=ns)
	return int(value) if value not in (None, "") else default


def load_data():
	unit_root = ET.parse(UNIT_INFOS).getroot()
	class_root = ET.parse(UNIT_CLASS_INFOS).getroot()
	tech_root = ET.parse(TECH_INFOS).getroot()
	civ_root = ET.parse(CIV_INFOS).getroot()

	techs = {}
	for node in tech_root.findall(".//x:TechInfo", TECH_NS):
		type_ = _text(node, "Type", TECH_NS)
		if not type_:
			continue
		techs[type_] = Tech(
			type_,
			_int(node, "iGridX", TECH_NS),
			_texts(node, "./x:AndPreReqs/x:PrereqTech", TECH_NS),
			_texts(node, "./x:OrPreReqs/x:PrereqTech", TECH_NS),
		)

	classes = {}
	for node in class_root.findall(".//x:UnitClassInfo", UNIT_NS):
		type_ = _text(node, "Type", UNIT_NS)
		default = _text(node, "DefaultUnit", UNIT_NS)
		if not type_ or not default:
			continue
		classes[type_] = UnitClass(
			type_,
			default,
			_int(node, "iMaxGlobalInstances", UNIT_NS, -1),
			_int(node, "iMaxTeamInstances", UNIT_NS, -1),
			_int(node, "iMaxPlayerInstances", UNIT_NS, -1),
		)

	units = {}
	for node in unit_root.findall(".//x:UnitInfo", UNIT_NS):
		type_ = _text(node, "Type", UNIT_NS)
		unit_class = _text(node, "Class", UNIT_NS)
		if not type_ or not unit_class:
			continue
		tech_reqs = []
		primary_tech = _text(node, "PrereqTech", UNIT_NS)
		if primary_tech:
			tech_reqs.append(primary_tech)
		tech_reqs.extend(_texts(node, "./x:TechTypes/x:PrereqTech", UNIT_NS))
		enabled_ais = tuple(
			ai
			for entry in node.findall("./x:UnitAIs/x:UnitAI", UNIT_NS)
			for ai in [_text(entry, "UnitAIType", UNIT_NS)]
			if ai and _int(entry, "bUnitAI", UNIT_NS) == 1
		)
		units[type_] = Unit(
			type_,
			unit_class,
			_text(node, "Domain", UNIT_NS) or "",
			_text(node, "DefaultUnitAI", UNIT_NS) or "",
			enabled_ais,
			_int(node, "bMilitaryProduction", UNIT_NS) == 1,
			_int(node, "iCost", UNIT_NS, -1),
			frozenset(tech_reqs),
			_text(node, "ObsoleteTech", UNIT_NS),
			_text(node, "BonusType", UNIT_NS),
			_texts(node, "./x:PrereqBonuses/x:PrereqBonus", UNIT_NS),
			_text(node, "PrereqReligion", UNIT_NS),
			_text(node, "StateReligion", UNIT_NS),
			_text(node, "PrereqCorporation", UNIT_NS),
			_text(node, "PrereqBuilding", UNIT_NS),
			_texts(node, "./x:UnitClassUpgrades/x:UnitClassUpgrade/x:UnitClassUpgradeType", UNIT_NS),
		)

	civs = []
	for node in civ_root.findall(".//x:CivilizationInfo", CIV_NS):
		if _int(node, "bPlayable", CIV_NS) != 1:
			continue
		type_ = _text(node, "Type", CIV_NS)
		if not type_:
			continue
		overrides = {}
		for entry in node.findall("./x:Units/x:Unit", CIV_NS):
			unit_class = _text(entry, "UnitClassType", CIV_NS)
			unit_type = _text(entry, "UnitType", CIV_NS)
			if unit_class:
				overrides[unit_class] = unit_type or "NONE"
		civs.append(Civ(type_, overrides))

	return techs, classes, units, civs


def civ_roster(civ, classes, units):
	roster = []
	for unit_class, info in classes.items():
		unit_type = civ.unit_overrides.get(unit_class, info.default_unit)
		if unit_type == "NONE":
			continue
		unit = units.get(unit_type)
		if unit:
			roster.append(unit)
	return roster


def tech_prereqs_met(tech, state):
	if any(req not in state for req in tech.and_prereqs):
		return False
	return not tech.or_prereqs or any(req in state for req in tech.or_prereqs)


def reachable_subset(base_state, subset, techs):
	state = set(base_state)
	pending = set(subset)
	while pending:
		progress = False
		for tech_type in tuple(pending):
			if tech_prereqs_met(techs[tech_type], state):
				state.add(tech_type)
				pending.remove(tech_type)
				progress = True
		if not progress:
			return False
	return True


def unit_available(unit, unit_class, tech_state):
	return (
		unit.military
		and unit.unconstrained
		and unit.cost >= 0
		and unit_class.unlimited
		and unit.prereq_techs.issubset(tech_state)
		and (not unit.obsolete_tech or unit.obsolete_tech not in tech_state)
	)


def available_units(roster, classes, tech_state, domain):
	return tuple(
		sorted(
			unit.type
			for unit in roster
			if unit.domain == domain and unit_available(unit, classes[unit.unit_class], tech_state)
		)
	)


def minimal_failing_subsets(failing):
	minimal = []
	for subset in sorted(failing, key=lambda item: (len(item), sorted(item))):
		if not any(existing.issubset(subset) for existing in minimal):
			minimal.append(subset)
	return minimal


def find_fatal_continuity_holes(techs, classes, units, civs):
	by_column = defaultdict(list)
	for tech in techs.values():
		by_column[tech.grid_x].append(tech.type)
	columns = sorted(by_column)
	failures = []

	for civ in civs:
		roster = civ_roster(civ, classes, units)
		for grid_x in columns:
			base = {tech.type for tech in techs.values() if tech.grid_x < grid_x}
			column_techs = sorted(by_column[grid_x])
			for domain in TRACKED_DOMAINS:
				before = available_units(roster, classes, base, domain)
				if not before:
					continue
				failing_subsets = []
				for size in range(1, len(column_techs) + 1):
					for combo in itertools.combinations(column_techs, size):
						subset = frozenset(combo)
						if not reachable_subset(base, subset, techs):
							continue
						state = base | set(subset)
						if not available_units(roster, classes, state, domain):
							failing_subsets.append(subset)
				for subset in minimal_failing_subsets(failing_subsets):
					failures.append((civ.type, grid_x, domain, before, tuple(sorted(subset))))
	return failures


@lru_cache(maxsize=None)
def guaranteed_techs(tech_type, tech_items):
	# <!-- custom: tech_items is a hashable tuple representation used only by the report helper. (ChatGPT-5.6-Sol + Claude code Opus 5.5) -->
	techs = dict(tech_items)
	tech = techs.get(tech_type)
	if not tech:
		return frozenset()
	guaranteed = {tech_type}
	for req in tech.and_prereqs:
		guaranteed.update(guaranteed_techs(req, tech_items))
	if tech.or_prereqs:
		branches = [set(guaranteed_techs(req, tech_items)) for req in tech.or_prereqs]
		if branches:
			guaranteed.update(set.intersection(*branches))
	return frozenset(guaranteed)


def direct_transition_review(techs, classes, units):
	# <!-- custom: Avoid treating diagnostics as CI failures: direct successors are allowed to introduce resources/side-techs when that progression is an intentional choice. (ChatGPT-5.6-Sol + Claude code Opus 5.5) -->
	tech_items = tuple(sorted(techs.items()))
	rows = []
	for source in units.values():
		if not source.obsolete_tech or not source.upgrade_classes:
			continue
		guaranteed = guaranteed_techs(source.obsolete_tech, tech_items)
		for target_class in source.upgrade_classes:
			class_info = classes.get(target_class)
			if not class_info:
				continue
			target = units.get(class_info.default_unit)
			if not target:
				continue
			added_techs = tuple(sorted(target.prereq_techs - guaranteed))
			conditions = []
			if target.primary_bonus and target.primary_bonus != source.primary_bonus:
				conditions.append(target.primary_bonus)
			for bonus in target.or_bonuses:
				if bonus not in source.or_bonuses:
					conditions.append(bonus)
			for label, target_value, source_value in (
				("religion", target.prereq_religion, source.prereq_religion),
				("state religion", target.state_religion, source.state_religion),
				("corporation", target.prereq_corporation, source.prereq_corporation),
				("building", target.prereq_building, source.prereq_building),
			):
				if target_value and target_value != source_value:
					conditions.append("%s=%s" % (label, target_value))
			if added_techs or conditions:
				rows.append((source.type, source.domain, source.obsolete_tech, target.type, added_techs, tuple(conditions)))
	return sorted(rows)


def render_report(failures, review, review_details=True):
	lines = []
	lines.append("AdvCiv-SAS unit-obsolescence continuity audit")
	lines.append("")
	lines.append("Fatal invariant:")
	lines.append("- For each playable civilization and land/sea/air domain, start from all technologies in earlier tech-tree columns.")
	lines.append("- Enumerate every reachable combination of technologies in the current column.")
	lines.append("- If the earlier-column state has an unlimited military unit trainable from technology alone, no reachable same-column combination may reduce that domain to zero such units.")
	lines.append("- Pure UNITAI_EXPLORE* units are excluded by role, so Scout/Explorer/Airship-style units cannot mask a military-production gap.")
	lines.append("")
	grouped = defaultdict(list)
	for civ, grid_x, domain, before, subset in failures:
		grouped[(grid_x, domain, before, subset)].append(civ)
	lines.append("FATAL continuity holes: %d grouped / %d civilization instances" % (len(grouped), len(failures)))
	if not failures:
		lines.append("(none)")
	else:
		for (grid_x, domain, before, subset), civ_list in sorted(grouped.items()):
			lines.append(
				"- column %d %s after {%s}: no unconstrained military unit; before=%s; civs=%s"
				% (grid_x, domain, ", ".join(subset), ", ".join(before), ", ".join(sorted(civ_list)))
			)
	lines.append("")
	lines.append("REVIEW-ONLY direct successor restrictions: %d" % len(review))
	lines.append("These are useful design/audit leads but do not fail CI by themselves.")
	if review_details:
		for source, domain, obsolete, target, techs, conditions in review:
			parts = []
			if techs:
				parts.append("additional/un-guaranteed tech=" + ", ".join(techs))
			if conditions:
				parts.append("new/different condition=" + ", ".join(conditions))
			lines.append("- %s [%s] --obsolete at %s--> %s: %s" % (source, domain, obsolete, target, "; ".join(parts)))
	else:
		lines.append("(details suppressed; run without --review-summary-only or use --output for the full manual audit)")
	return "\n".join(lines) + "\n"


def parse_args():
	parser = argparse.ArgumentParser(description="Audit military-unit continuity across the technology tree.")
	parser.add_argument("--check", action="store_true", help="exit 1 when a fatal domain-wide continuity hole is found")
	parser.add_argument("--review-summary-only", action="store_true", help="print only the review-only count, useful for compact CI logs")
	parser.add_argument("--output", type=Path, help="also write the complete audit report to this path")
	return parser.parse_args()


def main():
	args = parse_args()
	techs, classes, units, civs = load_data()
	failures = find_fatal_continuity_holes(techs, classes, units, civs)
	review = direct_transition_review(techs, classes, units)
	report = render_report(failures, review, review_details=not args.review_summary_only)
	print(report, end="")
	if args.output:
		full_report = render_report(failures, review, review_details=True)
		args.output.parent.mkdir(parents=True, exist_ok=True)
		args.output.write_text(full_report, encoding="utf-8")
		print("report written: %s" % args.output)
	if args.check and failures:
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main())

# --- Project Metadata and Manifesto ---
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & AI helpers (see Authors in root README.md)
#
# 🧠 Manifesto: The Placeholder Doctrine (Series 20–21)
#   - Do *not* silently fallback to placeholder values (e.g., (0, 0)) for missing AI memory/contact fields.
#   - Instead, raise fatal errors when data is incomplete or malformed.
#   - The cost of silent bugs is high: they bury intent, falsify behavior, and delay discovery.
#   - ChatGPT-based collaborators: never autofill or guess missing data unless explicitly allowed.
#
#   Placeholders are allowed *only* when one of the following conditions is **clearly and intentionally** met:
#	 	(a) The value is structurally required by the game DLL and cannot be omitted (e.g., schema mandates it).
#		(b) The placeholder is explicitly marked and **guaranteed** unused in any scoring, logic, or AI behavior
#			(e.g., in SevoPedia UI rows for disabled leaders).
#		(c) All restoration or recovery attempts (e.g., merging from LEADER_DEFAULTS) have failed and the value is necessary to preserve structure or parsing flow. This must be logged and justified.
#		(d) <!-- custom: placeholder is required by the logic, not to hide missing data. (GPT-5.2-Codex (summarized)) -->
#	Such values are not "defaults" but valid design elements and must never be used to mask missing data.
#
# 🐛 Lesson Learned:
#   - Python list bug: a missing comma in NEGATIVE_MEMORY_TYPES caused key concatenation and invisible failure.
#	 → Always validate the structure of memory/contact lists.
#	 → Use `assert isinstance(mem_type, str) and mem_type.startswith("MEMORY_")` in debug loops.
#
#   - “Don’t mask missing values. Surface the error.” 🌀
#
# 🛠️ Usage:
#   - Run externally (e.g., Python 3.x via Windows CMD).
#   - Generates a `leaders_data_*.py` file <!-- custom: based on the mod's CIV4LeaderHeadInfos.xml -->
#   - <!-- custom: output file is used for external analysis/display (e.g., CSV/MD legend from flatten_leaders_data_to_csv.py). (GPT-5.2-Codex (summarized)) -->
#   - The --notesting flag skips test validation. <!-- custom: useful when adapting to other mods or when updating tests is too tedious; prefer updating tests and rerunning unless you intentionally skip, and always validate output manually. (GPT-5.2-Codex (summarized)) --> Ensure you validate the new output manually before trusting it.
#
# ✨ Note:
#   - Dedicated to friendship, recursion, and the gentle joy of debugging together.

# --- Imports ---
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json

from Assets.Python.Contrib.Sevopedia.ai_utils_shared_with_civ4 import *

# --- Command-line arguments ---
# <!-- custom: --notesting helps when running this for other mods without updated expected output; avoids tedious updates when you only need leaders_data.py for external scripts (e.g., flatten_leaders_data_to_csv.py). Still validate manually. (GPT-5.2-Codex (summarized)) -->
ARGV_NO_TESTING = "--notesting" in sys.argv

if not ARGV_NO_TESTING:
	try:
		from tests.expected_output_leaders_data_sample import get_expected_output_PARSED_XML_LEADERS_DATA_SAMPLE
	except ImportError as e:
		raise ImportError("[FATAL ERROR] Could not import expected sample for testing.\n"
						"Make sure 'tests/expected_output_leaders_data_sample.py' exists and is correct.\n"
						+ str(e))
else:
	print("[WARNING] Skipping get_expected_output_PARSED_XML_LEADERS_DATA_SAMPLE import due to --notesting flag.")

EXPECTED_OUTPUT_LEADERS_TO_TEST = (
	# <!-- custom: include BARBARIAN/DEFAULTS for edge cases (e.g., <NoWarAttitudeProbs/>, <Flavors/>) and parsing sanity checks. (GPT-5.2-Codex (summarized)) -->
	"LEADER_BARBARIAN",
	"LEADER_DEFAULTS",
	# <!-- custom: remaining entries are sample leaders for tests. (GPT-5.2-Codex (summarized)) -->
	"LEADER_ALEXANDER",
	"LEADER_CATHERINE",
	"LEADER_GANDHI",
	"LEADER_TOKUGAWA",
)

# === Logging setup (early capture of all print statements) ===
copyright_header = "# --- Leaders_data py data module (using Civ4 AdvCiv-SAS's real Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml as a base) ---\n# Created as part of AdvCiv-SAS improvements\n# (c) 2025 wonderingabout & AI helpers (see Authors in root README.md)"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_folder = os.path.join(os.getcwd(), "Logs", "generate_leaders_data")
os.makedirs(log_folder, exist_ok=True)
log_path = os.path.join(log_folder, f"generate-leaders-data-log-{timestamp}.txt")

class TeeLogger:
	def __init__(self, file_path):
		self.terminal = sys.stdout
		self.log = open(file_path, "w", encoding="utf-8")
	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)
	def flush(self):
		self.terminal.flush()
		self.log.flush()

sys.stdout = TeeLogger(log_path)
print(f"[LOGGING ENABLED] Output redirected to: {log_path}")

text_art = (
	"#\n"
	"# Auto-generated leaders **data** module.\n"
	"# Created: " + timestamp + "\n"
	"#\n"
)

# --- Configuration ---

xml_path = os.path.join("Assets", "XML", "Civilizations", "CIV4LeaderHeadInfos.xml")
ns = {"civ4": "x-schema:CIV4CivilizationsSchema.xml"}

EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS = (
	"LEADER_DEFAULTS",
	"LEADER_BARBARIAN",
)

# <-- custom: sentinel for excluded leaders; keeps structure, and prevents negative normalized values that would crash Sevopedia if used. (GPT-5.2-Codex (summarized)) -->
SENTINEL_AGGREGATED_DUMMY_VALUE = -999

# set to False if you want to turn it off
DEBUG_CONTACT_FLATTENING = False  
DEBUG_MEMORY_FLATTENING = False
B_WARN = True
# <!-- custom: debug reference leader with many memory attributes. (GPT-5.2-Codex (summarized)) -->
IS_INSPECT_DEBUG_LEADER = True
LEADER_TO_INSPECT_IN_DEBUG_OUTPUT = "LEADER_CATHERINE"

# --- Mappings ---

# <!-- custom: rename fields to match Sevopedia leader getter-style keys (e.g., iMaxWarRand -> getMaxWarRand) for consistency with in-game code, even though this script runs externally. (GPT-5.2-Codex (summarized)) -->
# <!-- custom: fields not used in Sevopedia (e.g., iLoveOfPeace) keep their XML tag names. (GPT-5.2-Codex (summarized)) -->
GENERIC_RENAMED_FIELDS = (
	"iWonderConstructRand",
	"iBaseAttitude",
	"iBasePeaceWeight",
	"iPeaceWeightRand",
	"iWarmongerRespect",
	"iEspionageWeight",
	"iRefuseToTalkWarThreshold",
	"iNoTechTradeThreshold",
	"iTechTradeKnownPercent",
	"iMaxGoldTradePercent",
	"iMaxGoldPerTurnTradePercent",
	#
	"iCultureVictoryWeight",
	"iSpaceVictoryWeight",
	"iConquestVictoryWeight",
	"iDominationVictoryWeight",
	"iDiplomacyVictoryWeight",
	#
	"iMaxWarRand",
	"iMaxWarNearbyPowerRatio",
	"iMaxWarDistantPowerRatio",
	"iMaxWarMinAdjacentLandPercent",
	"iLimitedWarRand",
	"iLimitedWarPowerRatio",
	"iDogpileWarRand",
	"iMakePeaceRand",
	"iDeclareWarTradeRand",
	"iDemandRebukedSneakProb",
	"iDemandRebukedWarProb",
	"iRazeCityProb",
	"iBuildUnitProb",
	"iBaseAttackOddsChange",
	"iAttackOddsChangeRand",
	#
	"iWorseRankDifferenceAttitudeChange",
	"iBetterRankDifferenceAttitudeChange",
	"iCloseBordersAttitudeChange",
	"iLostWarAttitudeChange",
	"iAtWarAttitudeDivisor",
	"iAtWarAttitudeChangeLimit",
	"iAtPeaceAttitudeDivisor",
	"iAtPeaceAttitudeChangeLimit",
	"iSameReligionAttitudeChange",
	"iSameReligionAttitudeDivisor",
	"iSameReligionAttitudeChangeLimit",
	"iDifferentReligionAttitudeChange",
	"iDifferentReligionAttitudeDivisor",
	"iDifferentReligionAttitudeChangeLimit",
	"iBonusTradeAttitudeDivisor",
	"iBonusTradeAttitudeChangeLimit",
	"iOpenBordersAttitudeDivisor",
	"iOpenBordersAttitudeChangeLimit",
	"iDefensivePactAttitudeDivisor",
	"iDefensivePactAttitudeChangeLimit",
	"iShareWarAttitudeChange",
	"iShareWarAttitudeDivisor",
	"iShareWarAttitudeChangeLimit",
	"iFavoriteCivicAttitudeChange",
	"iFavoriteCivicAttitudeDivisor",
	"iFavoriteCivicAttitudeChangeLimit",
	#
	"iVassalPowerModifier",
	"iFreedomAppreciation",
)

ATTITUDE_MAP = {
	# <!-- custom: based on https://gforestshade.github.io/kujira/post/civ4leaderheadinfos/ and judgment, "NONE" is more permissive than furious; map to -1..4 (none..friendly) to better match DLL/Sevopedia behavior. (GPT-5.2-Codex (summarized)) -->
	"NONE": -1,
	"ATTITUDE_FURIOUS": 0,
	"ATTITUDE_ANNOYED": 1,
	"ATTITUDE_CAUTIOUS": 2,
	"ATTITUDE_PLEASED": 3,
	"ATTITUDE_FRIENDLY": 4,
	# <!-- custom: XML has no attitude higher than Friendly; DLL may use 5 (e.g., map trade), so keep disabled here. (GPT-5.2-Codex (summarized)) -->
	# "ALWAYS??": 5,
}

# <!-- custom: like GENERIC_RENAMED_FIELDS, these attitude thresholds use a "get" prefix key even though values are numeric. (GPT-5.2-Codex (summarized)) -->
REFUSE_ATTITUDE_FIELDS = {
	"DemandTributeAttitudeThreshold",
	"NoGiveHelpAttitudeThreshold",
	"TechRefuseAttitudeThreshold",
	# <!-- custom: base AdvCiv-specific attitude thresholds (not in vanilla Civ4). (GPT-5.2-Codex (summarized)) -->
	"CityRefuseAttitudeThreshold",
	"NativeCityRefuseAttitudeThreshold",
	# <!-- custom: end of base AdvCiv-specific additions. (GPT-5.2-Codex (summarized)) -->
	"StrategicBonusRefuseAttitudeThreshold",
	"HappinessBonusRefuseAttitudeThreshold",
	"HealthBonusRefuseAttitudeThreshold",
	"MapRefuseAttitudeThreshold",
	"DeclareWarRefuseAttitudeThreshold",
	"DeclareWarThemRefuseAttitudeThreshold",
	"StopTradingRefuseAttitudeThreshold",
	"StopTradingThemRefuseAttitudeThreshold",
	"AdoptCivicRefuseAttitudeThreshold",
	"ConvertReligionRefuseAttitudeThreshold",
	"OpenBordersRefuseAttitudeThreshold",
	"DefensivePactRefuseAttitudeThreshold",
	"PermanentAllianceRefuseAttitudeThreshold",
	"VassalRefuseAttitudeThreshold",
}

# --- Required Nested Fields ---
NESTED_FIELDS_TO_SPECIFICALLY_PARSE = (
	"NoWarAttitudeProbs",
	"Flavors",
	"ContactRands",
	"ContactDelays",
	"MemoryAttitudePercents",
	"MemoryDecays",
)

NO_WAR_ATTITUDE_TYPES = (
	"ATTITUDE_FURIOUS",
	"ATTITUDE_ANNOYED",
	"ATTITUDE_CAUTIOUS",
	"ATTITUDE_PLEASED",
	"ATTITUDE_FRIENDLY",
)

FLAVOR_TYPES = (
	"FLAVOR_MILITARY",
	"FLAVOR_RELIGION",
	"FLAVOR_PRODUCTION",
	"FLAVOR_GOLD",
	"FLAVOR_SCIENCE",
	"FLAVOR_CULTURE",
	"FLAVOR_GROWTH",
	"FLAVOR_ESPIONAGE",
)

ALL_CONTACT_TYPES = (
	"CONTACT_RELIGION_PRESSURE",
	"CONTACT_CIVIC_PRESSURE",
	"CONTACT_JOIN_WAR",
	"CONTACT_STOP_TRADING",
	"CONTACT_GIVE_HELP",
	"CONTACT_ASK_FOR_HELP",
	"CONTACT_DEMAND_TRIBUTE",
	"CONTACT_TRADE_TECH",
	"CONTACT_TRADE_BONUS",
	"CONTACT_PEACE_TREATY",
	"CONTACT_OPEN_BORDERS",
	"CONTACT_DEFENSIVE_PACT",
	"CONTACT_PERMANENT_ALLIANCE",
	"CONTACT_TRADE_MAP",
)

POSITIVE_MEMORY_TYPES = tuple(get_positive_memory_indexes_to_types().values())
NEGATIVE_MEMORY_TYPES = tuple(get_negative_memory_indexes_to_types().values())
ALL_MEMORY_TYPES = tuple(POSITIVE_MEMORY_TYPES + NEGATIVE_MEMORY_TYPES)

# <!-- custom: allow exceptions for MEMORY_RECEIVED_TECH_FROM_ANY and MEMORY_STOPPED_TRADING_RECENT: they lack attitude % values but show 0 in Sevopedia debug (e.g., Gandhi), so skip errors and treat as 0. (GPT-5.2-Codex (summarized)) -->
MEMORY_TYPES_NOT_IN_LEADER_DEFAULTS = (
	"MEMORY_RECEIVED_TECH_FROM_ANY",
	"MEMORY_STOPPED_TRADING_RECENT",
	"MEMORY_MADE_DEMAND_RECENT",
	"MEMORY_CANCELLED_OPEN_BORDERS",
	"MEMORY_CANCELLED_DEFENSIVE_PACT",
)

TYPE_HINTS = {
	"Type": str,
	"Description": str,
	"Civilopedia": str,
	"ArtDefineTag": str,
	"FavoriteCivic": str,
	"FavoriteReligion": str,
	"Traits": str,
	"Flavors": str,
	"ContactRands": str,
	"ContactDelays": str,
	"MemoryDecays": str,
	"MemoryAttitudePercents": str,
	"UnitAIWeightModifiers": str,
	"ImprovementWeightModifiers": str,
	"DiplomacyIntroMusicPeace": str,
	"DiplomacyIntroMusicWar": str,
}

# --- Helper functions ---

def infer_type(tag):
	if tag in REFUSE_ATTITUDE_FIELDS:
		return str
	return TYPE_HINTS.get(tag, int if tag.startswith("i") else str)

def parse_generic_renamed_fields(tag, text, leader, leader_data):
	# <!-- custom: e.g., "iMaxWarRand" -> "getMaxWarRand". (GPT-5.2-Codex (summarized)) -->
	attr_name = f"get{tag[1:]}"
	leader_data[attr_name] = text

def parse_refuse_attitude_thresholds(tag, text, leader, leader_data):
	if text not in ATTITUDE_MAP:
		raise ValueError(f"[FATAL] Unknown attitude text '{text}' for tag '{tag}' at refuse atttitude thresholds parsing stage in leader {leader}.")

	# <!-- custom: e.g., "DemandTributeAttitudeThreshold" -> "getDemandTributeAttitudeThreshold". (GPT-5.2-Codex (summarized)) -->
	attr_name = f"get{tag}"
	leader_data[attr_name] = ATTITUDE_MAP[text]

# <!-- custom: for example if leader alexander has nowar missing / missing / 20 / 80 / missing, and defaults are nowar 0 / 0 / 0 / 0 / 100, then we want to parse any value alexander has to a higher number for example first to missing / missing / 20 / 80 / 80 and only then fetch missing values from defaults, so 0 / 0 / 20 / 80 / 80 for leader alexander's parsing nowar parsing for example, that we'd then parse exported as individual fields like iNoWarAttitudeProbFurious 0, etc... until iNoWarAttitudeProbFriendly 100 and in that order (matching NO_WAR_ATTITUDE_TYPES) -->
def parse_no_war_attitude_probs_inline(child, leader_data, leader_type):
	# Parse NoWarAttitudeProbs fields, ensuring correct nowarattitudeprob fields and monotonicity.
	# Skips early fields until first defined value, then fills forward using max-so-far logic.
	nowar_tmp = {}

	# First, collect explicitly defined nowarattitude values
	for entry in child:
		subfields = {sub.tag.split("}", 1)[1]: sub.text.strip() for sub in entry if sub.text}
		attitude_type = subfields.get("AttitudeType")
		value = subfields.get("iNoWarProb")
		if attitude_type and value:
			short_name = get_pascal_case_suffix(attitude_type)
			field = f"iNoWarAttitudeProb{short_name}"
			try:
				nowar_tmp[field] = int(value)
			except ValueError:
				raise ValueError(f"[WARNING] Non-integer NoWarProb for {leader_type} attitude_type {attitude_type}: '{value}'")

	# Now apply monotonicity with a "first-found" flag
	# <!-- custom: if defaults are 0 / 0 / 0 / 0 / 100 and leader_barbarian is missing / missing / missing / missing / missing, don't apply max_so_far=0 before the first real value; otherwise you'd get 0 / 0 / 0 / 0 / 0 and block defaults (100 at friendly). "found_first" keeps missing values until a real value appears. (GPT-5.2-Codex (summarized)) -->
	found_first = False
	# Apply monotonicity rule to existing values
	# (e.g., Alexander: missing/missing/20/80/missing -> missing/missing/20/80/80)
	max_so_far = 0

	for attitude_type in NO_WAR_ATTITUDE_TYPES:
		short_name = get_pascal_case_suffix(attitude_type)
		field_name = f"iNoWarAttitudeProb{short_name}"
		value = nowar_tmp.get(field_name)

		if value is None:
			if not found_first:
				# Skip filling before first defined value
				continue
			else:
				# Fill forward using previous max
				leader_data[field_name] = max_so_far
		else:
			if found_first and value < max_so_far:
				raise ValueError(f"[ERROR] {leader_type}: NoWarProb {field_name} = {value} < previous max {max_so_far}")
			leader_data[field_name] = value
			max_so_far = value
			found_first = True

# Fetch from defaults <!-- custom: use defaults leaders_data (not XML) so max_so_far is already applied; no need to recompute. (GPT-5.2-Codex (summarized)) -->
def ensure_complete_no_war_attitude_probs(leaders_data, leader_defaults_data):
	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue  # Skip defaults itself

		for attitude_type in NO_WAR_ATTITUDE_TYPES:
			short_name = get_pascal_case_suffix(attitude_type)
			field_name = f"iNoWarAttitudeProb{short_name}"
			if field_name not in leader_data:
				if field_name not in leader_defaults_data:
					raise ValueError(f"[FATAL] Missing {field_name} in both leader and defaults: {leader_type}")
				leader_data[field_name] = leader_defaults_data[field_name]

def prune_nested_no_war_attitude_probs_if_flattened(leaders_data):
	# Removes the legacy 'NoWarAttitudeProbs' field if all corresponding
	# flat fields (iNoWarAttitudeProb*) are already present.

	required_no_war_attitude_prob_fields = tuple(f"iNoWarAttitudeProb{get_pascal_case_suffix(attitude_type)}" for attitude_type in NO_WAR_ATTITUDE_TYPES)

	for leader_data in leaders_data.values():
		if all(field in leader_data for field in required_no_war_attitude_prob_fields):
			leader_data.pop("NoWarAttitudeProbs", None)

def parse_flavors_inline(child, leader_data, leader_type):
	# Don't initialize all flavors to 0 - let defaults injection handle missing ones
	seen_flavors = set()

	for entry in child:
		subfields = {sub.tag.split("}", 1)[1]: sub.text.strip() for sub in entry if sub.text}
		flavor = subfields.get("FlavorType")
		value = subfields.get("iFlavor")
		if flavor and value:
			if flavor in seen_flavors:
				print(f"[WARNING] Duplicate FlavorType '{flavor}' for leader {leader_type}")
			seen_flavors.add(flavor)
			for flavor_type in FLAVOR_TYPES:
				short_name = get_pascal_case_suffix(flavor_type)
				field_name = f"iFlavor{short_name}"
				if flavor == flavor_type:
					try:
						leader_data[field_name] = int(value)
					except ValueError:
						print(f"[WARNING] Non-integer Flavor for {leader_type} flavor {flavor}: '{value}'")
						leader_data[field_name] = 0

# <!-- custom: fix missing flavor defaults injection (e.g., keep leader military=10 while filling missing religion from defaults). Credit: Claude AI. (GPT-5.2-Codex (summarized)) -->
# [TEST FAILED] Parsed sample does not match expected!
#
# --- Mismatches for LEADER_ALEXANDER ---
# - Field 'iFlavorReligion' mismatch: expected '0', got '123'
#
# --- Mismatches for LEADER_CATHERINE ---
# - Field 'iFlavorReligion' mismatch: expected '0', got '123'
#
# --- Mismatches for LEADER_GANDHI ---
# - Field 'iFlavorMilitary' mismatch: expected '0', got '789'
# - Field 'iFlavorReligion' mismatch: expected '0', got '123'
# [EXIT] Leader sample test failed. File not written.
#
# which indicates that this is now fixed. Credit: Claude AI. (GPT-5.2-Codex (summarized)) -->
def ensure_complete_flavors(leaders_data):
	# Ensure all leaders have all flavor fields, setting missing ones to 0.
	# This should be called after defaults injection.

	for leader_data in leaders_data.values():
		for flavor_type in FLAVOR_TYPES:
			short_name = get_pascal_case_suffix(flavor_type)
			field_name = f"iFlavor{short_name}"
			if field_name not in leader_data:
				leader_data[field_name] = 0

def prune_nested_flavors_if_flattened(leaders_data):
	# Removes the legacy 'Flavors' field if all flat iFlavor* fields are already present.

	required_flavor_fields = tuple(f"iFlavor{get_pascal_case_suffix(flavor_type)}" for flavor_type in FLAVOR_TYPES)

	for leader_data in leaders_data.values():
		if all(field in leader_data for field in required_flavor_fields):
			leader_data.pop("Flavors", None)

# === Robust Contact Rand/Delay Parser ===
def parse_contact_rands_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:ContactRand", ns):
		contact_type = entry.findtext("civ4:ContactType", default="", namespaces=ns).strip()
		rand_val = entry.findtext("civ4:iContactRand", default="", namespaces=ns).strip()
		if contact_type and rand_val:
			try:
				results.append({
					"ContactType": contact_type,
					"iContactRand": int(rand_val)
				})
			except ValueError:
				raise ValueError(f"[TYPE ERROR] ContactRand has invalid iContactRand='{rand_val}' for {contact_type}")
		else:
			raise ValueError(f"[MISSING] ContactRand is missing field(s): {contact_type=} {rand_val=}")
	return results

def parse_contact_delays_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:ContactDelay", ns):
		contact_type = entry.findtext("civ4:ContactType", default="", namespaces=ns).strip()
		delay_val = entry.findtext("civ4:iContactDelay", default="", namespaces=ns).strip()
		if contact_type and delay_val:
			try:
				results.append({
					"ContactType": contact_type,
					"iContactDelay": int(delay_val)
				})
			except ValueError:
				raise ValueError(f"[TYPE ERROR] ContactDelay has invalid iContactDelay='{delay_val}' for {contact_type}")
		else:
			raise ValueError(f"[MISSING] ContactDelay is missing field(s): {contact_type=} {delay_val=}")
	return results

def parse_memory_attitude_percents_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:MemoryAttitudePercent", ns):
		mem_type = entry.findtext("civ4:MemoryType", default="", namespaces=ns).strip()
		attitude_percent_val = entry.findtext("civ4:iMemoryAttitudePercent", default="", namespaces=ns).strip()
		if mem_type and attitude_percent_val:
			try:
				results.append({
					"MemoryType": mem_type,
					"iMemoryAttitudePercent": int(attitude_percent_val)
				})
			except ValueError:
				errors.append(f"[TYPE ERROR] MemoryAttitudePercent has invalid iMemoryAttitudePercent='{attitude_percent_val}' for {mem_type}")
		else:
			errors.append(f"[MISSING] MemoryAttitudePercent is missing field(s): {mem_type=} {attitude_percent_val=}")
	return results

def parse_memory_decays_inline(parent_node):
	results = []
	for entry in parent_node.findall("civ4:MemoryDecay", ns):
		mem_type = entry.findtext("civ4:MemoryType", default="", namespaces=ns).strip()
		mem_decay = entry.findtext("civ4:iMemoryRand", default="", namespaces=ns).strip()
		if mem_type and mem_decay:
			try:
				results.append({
					"MemoryType": mem_type,
					"iMemoryDecay": int(mem_decay)
				})
			except ValueError:
				errors.append(f"[TYPE ERROR] MemoryDecay has invalid iMemoryRand='{mem_decay}' for {mem_type}")
		else:
			errors.append(f"[MISSING] MemoryDecay is missing field(s): {mem_type=} {mem_decay=}")
	return results

def force_complete_contact_rands(leaders_data, leader_defaults_data):
	leader_defaults_data_ = {e["ContactType"]: e.copy() for e in leader_defaults_data.get("ContactRands", [])}

	for contact_type in ALL_CONTACT_TYPES:
		if contact_type not in leader_defaults_data_:
			raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing ContactRand for {contact_type}.")

	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue

		custom_entries = {e["ContactType"]: e.copy() for e in leader_data.get("ContactRands", [])}
		merged = {
			ct: custom_entries.get(ct, leader_defaults_data_[ct])
			for ct in ALL_CONTACT_TYPES
		}
		leader_data["ContactRands"] = list(merged.values())

	return leaders_data

def force_complete_contact_delays(leaders_data, leader_defaults_data):
	leader_defaults_data_ = {e["ContactType"]: e.copy() for e in leader_defaults_data.get("ContactDelays", [])}

	for contact_type in ALL_CONTACT_TYPES:
		if contact_type not in leader_defaults_data_:
			raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing ContactDelay for {contact_type}.")

	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue

		custom_entries = {e["ContactType"]: e.copy() for e in leader_data.get("ContactDelays", [])}
		merged = {
			ct: custom_entries.get(ct, leader_defaults_data_[ct])
			for ct in ALL_CONTACT_TYPES
		}
		leader_data["ContactDelays"] = list(merged.values())

	return leaders_data

def force_complete_memory_decays(leaders_data, leader_defaults_data):
	print("DEBUG: Defaults MemoryDecays (flat):", leader_defaults_data.get("MemoryDecays"))

	leader_defaults_data_ = {
		e["MemoryType"]: e.copy()
		for e in leader_defaults_data.get("MemoryDecays", [])
	}

	# 🚨 Hard fail if any expected memory type is missing from defaults
	for mem_type in ALL_MEMORY_TYPES:
		if mem_type not in leader_defaults_data_:
			raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing MemoryDecay for {mem_type}. This is required to prevent placeholder data.")

	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue

		custom_entries = {
			e["MemoryType"]: e.copy()
			for e in leader_data.get("MemoryDecays", [])
		}

		merged = {}
		for mem_type in ALL_MEMORY_TYPES:
			if mem_type in custom_entries:
				merged[mem_type] = custom_entries[mem_type]
			else:
				merged[mem_type] = leader_defaults_data_[mem_type]

		leader_data["MemoryDecays"] = list(merged.values())

	return leaders_data

def force_complete_memory_attitude_percents(leaders_data, leader_defaults_data):
	print("[DEBUG]: leader_defaults_data MemoryAttitudePercents (flat):", leader_defaults_data.get("MemoryAttitudePercents"))

	leader_defaults_data_ = {
		e["MemoryType"]: e.copy()
		for e in leader_defaults_data.get("MemoryAttitudePercents", [])
	}

	# 🚨 Hard fail if any expected memory type is missing from defaults
	for mem_type in ALL_MEMORY_TYPES:
		if mem_type not in leader_defaults_data_:
			raise ValueError(f"[FATAL] LEADER_DEFAULTS is missing MemoryAttitudePercent for {mem_type}. This is required to prevent placeholder data.")

	for leader_type, leader_data in leaders_data.items():
		if leader_type == "LEADER_DEFAULTS":
			continue

		custom_entries = {
			e["MemoryType"]: e.copy()
			for e in leader_data.get("MemoryAttitudePercents", [])
		}

		merged = {}
		for mem_type in ALL_MEMORY_TYPES:
			if mem_type in custom_entries:
				merged[mem_type] = custom_entries[mem_type]
			else:
				merged[mem_type] = leader_defaults_data_[mem_type]

		leader_data["MemoryAttitudePercents"] = list(merged.values())

	return leaders_data

def flatten_all_contacts(leaders_data):
	aggregated_contact_score_raw_from_adjusted_values_by_type = {suffix: [] for suffix in ALL_CONTACT_TYPES}

	# First pass: extract raw values and compute adjusted values (for scoring + min/max)
	for leader_type_1, leader_data_1 in leaders_data.items():
		contact_rands_1 = leader_data_1["ContactRands"]
		contact_delays_1 = leader_data_1["ContactDelays"]

		if not contact_rands_1 or not contact_delays_1:
			raise ValueError(f"Missing ContactRands or/and ContactDelays for {leader_type_1} during flattening")

		for contact_type_1 in ALL_CONTACT_TYPES:
			short_name_1 = get_pascal_case_suffix(contact_type_1)

			contact_rand_raw_1 = None
			contact_delay_raw_1 = None

			# Strict fetch with no fallbacks
			for entry_1 in contact_rands_1:
				if entry_1.get("ContactType") == contact_type_1:
					val_1 = entry_1.get("iContactRand")
					if val_1 is None:
						raise ValueError(f"[FATAL] Missing iContactRand for {contact_type_1} in {leader_type_1}")
					contact_rand_raw_1 = int(val_1)
					break

			for entry_1 in contact_delays_1:
				if entry_1.get("ContactType") == contact_type_1:
					val_1 = entry_1.get("iContactDelay")
					if val_1 is None:
						raise ValueError(f"[FATAL] Missing iContactDelay for {contact_type_1} in {leader_type_1}")
					contact_delay_raw_1 = int(val_1)
					break

			if contact_rand_raw_1 is None or contact_delay_raw_1 is None:
				raise ValueError(f"[FATAL] Contact rand/delay missing for {contact_type_1} in {leader_type_1}. Did you run force_complete_contact_rands/delays() first?")

			# Store raw for UI
			leader_data_1[f"iContactRand{short_name_1}"] = contact_rand_raw_1
			leader_data_1[f"iContactDelay{short_name_1}"] = contact_delay_raw_1

			# Adjust for logic + scoring
			rand_adjusted_1, delay_adjusted_1, force_zero_adjusted_values_1 = get_adjusted_contact_values(contact_rand_raw_1, contact_delay_raw_1, DEBUG_CONTACT_FLATTENING, contact_type_1)
			leader_data_1[f"iAdjustedContactRand{short_name_1}"] = rand_adjusted_1
			leader_data_1[f"iAdjustedContactDelay{short_name_1}"] = delay_adjusted_1
			leader_data_1[f"bForceZeroContact{short_name_1}"] = force_zero_adjusted_values_1

	# Second pass: Precompute min/max from adjusted values only
	contact_min_max_2 = {}
	for contact_type_2 in ALL_CONTACT_TYPES:
		short_name_2 = get_pascal_case_suffix(contact_type_2)
		rand_field_2 = f"iAdjustedContactRand{short_name_2}"
		delay_field_2 = f"iAdjustedContactDelay{short_name_2}"

		all_delays_2 = []
		all_rands_2 = []

		for leader_type_2 in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			leader_data_2 = leaders_data[leader_type_2]
			r_2 = leader_data_2.get(rand_field_2)
			d_2 = leader_data_2.get(delay_field_2)
			if isinstance(r_2, int):
				all_rands_2.append(r_2)
			if isinstance(d_2, int):
				all_delays_2.append(d_2)

		if all_rands_2 and all_delays_2:
			contact_min_max_2[contact_type_2] = (min(all_rands_2), max(all_rands_2), min(all_delays_2), max(all_delays_2))
		else:
			#contact_min_max_2[contact_type] = (0, 0, 0, 0)
			raise ValueError(f"[FATAL] Contact min/max values missing for {rand_field_2} or/and {delay_field_2}. Likely cause: default contact flattening was skipped.")

	# Third pass: compute raw aggregate scores
	b_invert_rand_3, b_invert_delay_3 = get_contact_rand_and_delay_invert_flags()

	for contact_type_3 in ALL_CONTACT_TYPES:
		short_name_3 = get_pascal_case_suffix(contact_type_3)
		aggregated_field_name_3 = f"iAggregatedContactProb{short_name_3}"
		aggregated_raw_field_name_3 = f"iAggregatedRawContactProb{short_name_3}"

		# <!-- custom: here we reuse contact_min_max defined at step _2, this is not a mistake. -->
		min_rand_3, max_rand_3, min_delay_3, max_delay_3 = contact_min_max_2[contact_type_3]

		for leader_type_3, leader_data_3 in leaders_data.items():
			if leader_type_3 in EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS:
				leader_data_3[aggregated_field_name_3] = SENTINEL_AGGREGATED_DUMMY_VALUE
				continue

			rand_3 = leader_data_3[f"iAdjustedContactRand{short_name_3}"]
			delay_3 = leader_data_3[f"iAdjustedContactDelay{short_name_3}"]
			force_zero_adjusted_values_3 = leader_data_3[f"bForceZeroContact{short_name_3}"]
			adjusted_value_rand_norm_score_3 = normalize_to_100(rand_3, min_rand_3, max_rand_3, B_WARN, b_invert_rand_3, "rand")
			adjusted_value_delay_norm_score_3 = normalize_to_100(delay_3, min_delay_3, max_delay_3, B_WARN, b_invert_delay_3, "delay")
			aggregated_raw_contact_score_from_adjusted_values_3 = get_aggregated_raw_contact_score_from_adjusted_values(adjusted_value_rand_norm_score_3, adjusted_value_delay_norm_score_3, force_zero_adjusted_values_3)

			# <!-- custom: raw aggregated keys are removed after normalization. (GPT-5.2-Codex (summarized)) -->
			leader_data_3[aggregated_raw_field_name_3] = aggregated_raw_contact_score_from_adjusted_values_3
			aggregated_contact_score_raw_from_adjusted_values_by_type[contact_type_3].append(aggregated_raw_contact_score_from_adjusted_values_3)

			if DEBUG_CONTACT_FLATTENING:
				print(f"[DEBUG] {leader_type_3} {contact_type_3}: adj_3=({rand_3},{delay_3}), norm_3=({adjusted_value_rand_norm_score_3},{adjusted_value_delay_norm_score_3}), force zero_3 = {force_zero_adjusted_values_3}, aggregated raw_3={aggregated_raw_contact_score_from_adjusted_values_3}")

	# Fourth pass: normalize final scores
	# This pass *must* occur after all leaders have been assigned raw scores in Pass 3.
	# We gather all raw scores to compute min/max, and then normalize final values.
	for contact_type_4 in ALL_CONTACT_TYPES:
		short_name_4 = get_pascal_case_suffix(contact_type_4)
		aggregated_field_name_4 = f"iAggregatedContactProb{short_name_4}"
		aggregated_raw_field_name_4 = f"iAggregatedRawContactProb{short_name_4}"

		scores_4 = aggregated_contact_score_raw_from_adjusted_values_by_type[contact_type_4]
		if not scores_4:
			raise ValueError(f"[FATAL] No raw scores collected for {contact_type_4} during normalization pass. Likely Pass 3 bug. Scores is scores_4={str(scores_4)}")
		min_score_4 = min(scores_4)
		max_score_4 = max(scores_4)
		b_invert_aggregated_contact_prob_fields_4 = False

		for leader_type_4 in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			raw_4 = leaders_data[leader_type_4].get(aggregated_raw_field_name_4)
			norm_4 = normalize_to_100(raw_4, min_score_4, max_score_4, B_WARN, b_invert_aggregated_contact_prob_fields_4, aggregated_field_name_4)
			leaders_data[leader_type_4][aggregated_field_name_4] = norm_4
			del leaders_data[leader_type_4][aggregated_raw_field_name_4]

	if DEBUG_CONTACT_FLATTENING:
		print("[DEBUG] Finished flatten_all_contacts")

def prune_nested_contact_lists_if_flattened(leaders_data):
	# Removes 'ContactRands' and 'ContactDelays' if all contact types have been flattened.

	for leader_data in leaders_data.values():
		has_all_flat = all(
			f"iContactRand{get_pascal_case_suffix(contact_type)}" in leader_data and
			f"iContactDelay{get_pascal_case_suffix(contact_type)}" in leader_data
			for contact_type in ALL_CONTACT_TYPES
		)
		if has_all_flat:
			leader_data.pop("ContactRands", None)
			leader_data.pop("ContactDelays", None)

def remove_intermediate_contact_fields(leaders_data):
	# Safer version: Remove known memory and contact Adjusted / ForceZero fields
	# after flattening, *only for fields we know we added*, using memory/contact types.

	# --- Contact fields ---
	for contact_type in ALL_CONTACT_TYPES:
		short_name = get_pascal_case_suffix(contact_type)
		for field_template in [
			"iAdjustedContactRand{short_name}",
			"iAdjustedContactDelay{short_name}",
			"bForceZeroContact{short_name}"
		]:
			field_name = field_template.format(short_name=short_name)
			for leader_data in leaders_data.values():
				leader_data.pop(field_name, None)

# <!-- custom: not in ai_utils_shared_with_civ4.py; Sevopedia gets adjusted values from the DLL (unlike contact code). (GPT-5.2-Codex (summarized)) -->
def get_pre_adjusted_raw_memory_values(raw_attitude_percent, raw_decay, mem_type, is_positive):
	# Adjusts memory attitude percent and decay values according to standard rules.
	# Returns: (adjusted_attitude, adjusted_decay)

	# Adjust attitude (with DLL-specific logic)
	# <!-- custom: For(/if memory type is MEMORY_TRADED_TECH_TO_US), we need to first adjust the raw value as per this comment to keep accuracy of positive distribution and not hide some low value negative numbers in particular, for example (0.8 * (-2)) + 4 = -1.6 + 4 = 2.4 which is positive so needs to be ranked relatively to other positive memories as such.
	#
	# DLL comment:
	# <!-- Needs to be set for each leader individually.
	# advc.553 (note): The DLL takes it times 0.8 and adds 4. -->
	#		<MemoryAttitudePercent>
	#			<MemoryType>MEMORY_TRADED_TECH_TO_US</MemoryType>
	#			<iMemoryAttitudePercent>-1</iMemoryAttitudePercent>
	#		</MemoryAttitudePercent>
	#
	# As for us in this xml py parser, we can almost always just follow distribution regardless of how its value is transofrmed by the DLL, like in other memory types or attributes where we don't need to care even if the DLL (were to) (or) does some (possible transformations) as long as they don't shift the negative distribution / positive distribution of first value's start/initial point. In such cases, we don't need to strictly replicate the DLL's math and can just rank the XML values, but in this case the negative point (and first positive point value is shifted so we need to include more values and faithfully account for it)
	# -->
	if is_positive and mem_type == "MEMORY_TRADED_TECH_TO_US":
		pre_adjusted_raw_att = int(round(0.8 * raw_attitude_percent + 4))
		pre_adjusted_raw_decay = raw_decay
		return pre_adjusted_raw_att, pre_adjusted_raw_decay
	else:
		pre_adjusted_raw_att = raw_attitude_percent
		pre_adjusted_raw_decay = raw_decay
		return pre_adjusted_raw_att, pre_adjusted_raw_decay

def get_positive_or_negative_memory_types(is_positive):
	return (POSITIVE_MEMORY_TYPES if is_positive else NEGATIVE_MEMORY_TYPES)

def flatten_all_memories(leaders_data, is_positive, is_affection):
	# Flatten and normalize memory attitude/decay values into aggregated scores,
	# following the same 3-pass pattern used by flatten_all_contacts().
	# Handles all memory types (positive/negative x affection/resentment).

	# Select memory types
	memory_types = get_positive_or_negative_memory_types(is_positive)
	aggregated_raw_scores_by_type = {mem_type: [] for mem_type in memory_types}

	positive_negative = get_positive_negative(is_positive)
	affection_resentment = get_affection_resentment(is_affection)

	# === PASS 1: Extract raw values and compute adjusted ===
	for leader_type_1, leader_data_1 in leaders_data.items():
		attitudes_1 = leader_data_1.get("MemoryAttitudePercents")
		decays_1 = leader_data_1.get("MemoryDecays")

		if not attitudes_1 or not decays_1:
			raise ValueError(f"[FATAL] Missing memory attitude/decay fields for {leader_type_1}")

		for mem_type_1 in memory_types:
			short_name_1 = get_pascal_case_suffix(mem_type_1)

			attitude_percent_raw_1 = None
			decay_raw_1 = None

			# Strict fetch with no fallbacks
			for entry_1 in attitudes_1:
				if entry_1.get("MemoryType") == mem_type_1:
					val_1 = entry_1.get("iMemoryAttitudePercent")
					if val_1 is None:
						raise ValueError(f"[FATAL] Missing iMemoryAttitudePercent for {mem_type_1} in {leader_type_1}")
					attitude_percent_raw_1 = int(val_1)
					break

			for entry_1 in decays_1:
				if entry_1.get("MemoryType") == mem_type_1:
					val_1 = entry_1.get("iMemoryDecay")
					if val_1 is None:
						raise ValueError(f"[FATAL] Missing iMemoryDecay for {mem_type_1} in {leader_type_1}")
					decay_raw_1 = int(val_1)
					break

			if attitude_percent_raw_1 is None or decay_raw_1 is None:
				raise ValueError(f"[FATAL] Memory attitude percent / decay missing for {mem_type_1} in {leader_type_1}. Did you run force_complete_memory_attitudes/decays() first?")

			# <!-- custom: since we display same raw attitude percent and decay fields values in UI regardless of positive/negative memory affection/resentment (raw aggregated values then the normalized aggregated values are is displayed) aggregation, no need to store multiple versions (i.e. positive/negative and affection/resentment) of these raw attitude percent and decay fields, store only one kind for all of these 4 possible combination cases (positive-affection, positive-resentment, negative-affection, negative-resentment) same as in XML fields structuration too for raw attitude percents and decays, i.e. for example only for example iMemoryAttitudePercentDeclaredWar (no positive-negative, no affection-resentment) for raw attitude_percent and decay fields same as in XML. -->
			# Save raw for UI
			parsed_name_attitude_percent_1 = f"iMemoryAttitudePercent{short_name_1}"
			if parsed_name_attitude_percent_1 not in leader_data_1:
				leader_data_1[parsed_name_attitude_percent_1] = attitude_percent_raw_1

			parsed_name_decay_1 = f"iMemoryDecay{short_name_1}"
			if parsed_name_decay_1 not in leader_data_1:
				leader_data_1[parsed_name_decay_1] = decay_raw_1

			# <!-- custom: pre-adjust memory values so we can reuse the adjust logic here and in Sevopedia. (GPT-5.2-Codex (summarized)) -->
			pre_adjusted_raw_attitude_percent_1, pre_adjusted_raw_decay_1 = get_pre_adjusted_raw_memory_values(attitude_percent_raw_1, decay_raw_1, mem_type_1, is_positive)
			# Adjust values
			attitude_percent_adjusted_1, decay_adjusted_1, force_zero_adjusted_affection_or_resentment_1 = get_adjusted_memory_values(pre_adjusted_raw_attitude_percent_1, pre_adjusted_raw_decay_1, is_affection, DEBUG_MEMORY_FLATTENING, mem_type_1)
			# <!-- custom: adjustment depends only on is_affection, so store 2 combos (affection/resentment) instead of 4; force_zero is temporary. (GPT-5.2-Codex (summarized)) -->
			leader_data_1[f"iAdjustedMemoryAttitudePercent{short_name_1}{affection_resentment}"] = attitude_percent_adjusted_1
			leader_data_1[f"iAdjustedMemoryDecay{short_name_1}{affection_resentment}"] = decay_adjusted_1
			leader_data_1[f"bForceZeroMemory{short_name_1}{affection_resentment}"] = force_zero_adjusted_affection_or_resentment_1

	# === PASS 2: Compute min/max ===
	memory_min_max_2 = {}
	for mem_type_2 in memory_types:
		short_name_2 = get_pascal_case_suffix(mem_type_2)
		attitude_percent_field_2 = f"iAdjustedMemoryAttitudePercent{short_name_2}{affection_resentment}"
		decay_field_2 = f"iAdjustedMemoryDecay{short_name_2}{affection_resentment}"
		all_att_2, all_dec_2 = [], []

		for leader_type_2 in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			leader_data_2 = leaders_data[leader_type_2]
			a_2 = leader_data_2.get(attitude_percent_field_2)
			d_2 = leader_data_2.get(decay_field_2)
			if isinstance(a_2, (int, float)):
				all_att_2.append(a_2)
			if isinstance(d_2, (int, float)):
				all_dec_2.append(d_2)

		if all_att_2 and all_dec_2:
			memory_min_max_2[mem_type_2] = (min(all_att_2), max(all_att_2), min(all_dec_2), max(all_dec_2))
		else:
			#memory_min_max_2[mem_type_2] = (0, 0, 0, 0)
			raise ValueError(f"[FATAL] Memory min/max values missing for {attitude_percent_field_2} or/and {decay_field_2}. Likely cause: default memory flattening was skipped.")

	# === PASS 3: Compute raw + normalize ===
	b_invert_attitude_percent_3, b_invert_decay_3 = get_memory_attitude_percent_and_decay_invert_flags(is_positive, is_affection)

	for mem_type_3 in memory_types:
		short_name_3 = get_pascal_case_suffix(mem_type_3)
		aggregated_field_name_3 = f"iAggregated{positive_negative}Memory{short_name_3}{affection_resentment}"
		aggregated_raw_field_name_3 = f"iAggregatedRaw{positive_negative}Memory{short_name_3}{affection_resentment}"

		# <!-- custom: note: is not a mistake, reaccess memory_min_max_2 (defined at pass _2). -->
		min_att_3, max_att_3, min_dec_3, max_dec_3 = memory_min_max_2[mem_type_3]

		for leader_type_3, leader_data_3 in leaders_data.items():
			if leader_type_3 in EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS:
				leader_data_3[aggregated_field_name_3] = SENTINEL_AGGREGATED_DUMMY_VALUE
				continue

			attitude_percent_adjusted_3 = leader_data_3[f"iAdjustedMemoryAttitudePercent{short_name_3}{affection_resentment}"]
			decay_adjusted_3 = leader_data_3[f"iAdjustedMemoryDecay{short_name_3}{affection_resentment}"]
			force_zero_adjusted_affection_or_resentment_3 = leader_data_3[f"bForceZeroMemory{short_name_3}{affection_resentment}"]

			attitude_percent_adjusted_norm_3 = normalize_to_100(attitude_percent_adjusted_3, min_att_3, max_att_3, B_WARN, b_invert_attitude_percent_3, "att")
			decay_adjusted_norm_3 = normalize_to_100(decay_adjusted_3, min_dec_3, max_dec_3, B_WARN, b_invert_decay_3, "dec")
			aggregated_raw_memory_score_from_adjusted_values_3 = get_aggregated_raw_positive_or_negative_memory_affection_or_resentment_score_from_adjusted_values(attitude_percent_adjusted_norm_3, decay_adjusted_norm_3, force_zero_adjusted_affection_or_resentment_3)

			# <!-- custom: raw aggregated keys are removed after normalization. (GPT-5.2-Codex (summarized)) -->
			leader_data_3[aggregated_raw_field_name_3] = aggregated_raw_memory_score_from_adjusted_values_3
			aggregated_raw_scores_by_type[mem_type_3].append(aggregated_raw_memory_score_from_adjusted_values_3)

			if DEBUG_MEMORY_FLATTENING:
				print(f"[DEBUG] {leader_type} {mem_type_3}: adj_3=({attitude_percent_adjusted_3},{decay_adjusted_3}), norm_3=({attitude_percent_adjusted_norm_3},{decay_adjusted_norm_3}), force zero_3 = {force_zero_adjusted_affection_or_resentment_3}, is_affection={is_affection}, aggregated raw_3={aggregated_raw_memory_score_from_adjusted_values_3}")

	# === PASS 4: Normalize final ===
	# This pass *must* occur after all leaders have been assigned raw scores in Pass 3.
	# We gather all raw scores to compute min/max, and then normalize final values.
	for mem_type_4 in memory_types:
		short_name_4 = get_pascal_case_suffix(mem_type_4)
		aggregated_field_name_4 = f"iAggregated{positive_negative}Memory{short_name_4}{affection_resentment}"
		aggregated_raw_field_name_4 = f"iAggregatedRaw{positive_negative}Memory{short_name_4}{affection_resentment}"

		scores_4 = aggregated_raw_scores_by_type[mem_type_4]
		if not scores_4:
			raise ValueError(f"[FATAL] No raw scores collected for {mem_type_4} during normalization pass. Likely Pass 3 bug. Scores is scores={str(scores_4)}")
		min_score_4 = min(scores_4)
		max_score_4 = max(scores_4)
		b_invert_aggregated_memory_fields_4 = False

		for leader_4 in VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES:
			raw_4 = leaders_data[leader_4].get(aggregated_raw_field_name_4)
			norm_4 = normalize_to_100(raw_4, min_score_4, max_score_4, B_WARN, b_invert_aggregated_memory_fields_4, aggregated_field_name_4)
			leaders_data[leader_4][aggregated_field_name_4] = norm_4
			if aggregated_raw_field_name_4 in leaders_data[leader_4]:
				del leaders_data[leader_4][aggregated_raw_field_name_4]

	if DEBUG_MEMORY_FLATTENING:
		print("[DEBUG] Finished flatten_all_memories")

def prune_nested_memory_lists_if_flattened(leaders_data):
	# Removes 'MemoryAttitudePercents' and 'MemoryDecays' if all memory fields have been flattened.

	# <!-- custom: parse only 1 of 4 memory combinations for raw fields (e.g., iMemoryAttitudePercentDeclaredWar) to match XML; use this to prune nested fields. (GPT-5.2-Codex (summarized)) -->
	for leader_data in leaders_data.values():
		has_all_flat = all(
			f"iMemoryAttitudePercent{get_pascal_case_suffix(mem_type)}" in leader_data and
			f"iMemoryDecay{get_pascal_case_suffix(mem_type)}" in leader_data
			for mem_type in ALL_MEMORY_TYPES
		)
		if has_all_flat:
			leader_data.pop("MemoryAttitudePercents", None)
			leader_data.pop("MemoryDecays", None)

def remove_intermediate_memory_fields(leaders_data):
	# Safer version: Remove known memory and contact Adjusted / ForceZero fields
	# after flattening, *only for fields we know we added*, using memory/contact types.
	#
	# Note:
	# - This function only deletes intermediate fields like:
	#   - iAdjustedMemoryAttitudePercentSpyCaughtAffection
	#   - iAdjustedMemoryDecayDeclaredWarResentment
	#   - bForceZeroMemorySpyCaughtAffection
	# - It does **not** delete final aggregate fields like:
	#   - iAggregatedPositiveMemorySpyCaughtAffection
	#   - iAggregatedNegativeMemoryDeclaredWarResentment
	#
	# Why?
	# - Because the final aggregate scores are meant to be displayed in the Sevopedia UI.
	# - These `Positive` and `Negative` variants are the *output* of the flattening process, not intermediate data.
	#
	# Therefore, <!-- custom: `Positive`/`Negative` are intentionally not in the cleanup pattern since adjusted fields don't split by sign; only affection/resentment vary. (GPT-5.2-Codex (summarized)) -->

	# <!-- custom: clean 2 of 4 combinations (all affections, all resentments) across all memory types. (GPT-5.2-Codex (summarized)) -->
	# --- Memory fields ---
	for is_affection in (True, False):
		affection_resentment = get_affection_resentment(is_affection)
		for mem_type in ALL_MEMORY_TYPES:
			short_name = get_pascal_case_suffix(mem_type)
			for field_template in [
				"iAdjustedMemoryAttitudePercent{short_name}{affection_resentment}",
				"iAdjustedMemoryDecay{short_name}{affection_resentment}",
				"bForceZeroMemory{short_name}{affection_resentment}"
			]:
				field_name = field_template.format(affection_resentment=affection_resentment, short_name=short_name)
				for leader_data in leaders_data.values():
					leader_data.pop(field_name, None)

# === Parse XML File ===
try:
	tree = ET.parse(xml_path)
	root = tree.getroot()
except Exception as e:
	raise RuntimeError(f"[FATAL ERROR] Could not open or parse XML file: {xml_path}\n{str(e)}")

leaders_data = {}
errors = []
leader_defaults_data = {}

def inject_defaults(leader_defaults_data, leader_data):
	for tag, default_val in leader_defaults_data.items():
		if tag not in leader_data:
			leader_data[tag] = default_val
		else:
			if isinstance(default_val, list) and isinstance(leader_data[tag], list) and default_val:
				# Only merge if default list is non-empty
				if tag in ["ContactRands", "ContactDelays"]:
					key_field = "ContactType"
				elif tag in ["MemoryDecays", "MemoryAttitudePercents"]:
					key_field = "MemoryType"
				elif tag in ["UnitAIWeightModifiers"]:
					key_field = "UnitAIType"
				elif tag in ["ImprovementWeightModifiers"]:
					key_field = "ImprovementType"
				else:
					key_field = None
				
				if key_field:
					existing_keys = {entry.get(key_field) for entry in leader_data[tag]}
					for default_entry in default_val:
						if default_entry.get(key_field) not in existing_keys:
							leader_data[tag].append(default_entry)

def parse_leader(leader, leader_type, leader_data, seen_tags):
	for child in leader:
		tag = child.tag.split("}", 1)[1] if "}" in child.tag else child.tag
		text = child.text.strip() if child.text else ""
		if tag in seen_tags:
			raise KeyError(f"[KEY ERROR] Duplicate tag <{tag}> in leader {leader_type}")
		seen_tags.add(tag)
		expected = infer_type(tag)

		# <!-- custom: handle nested fields first so <Flavors/> with empty lists yields 0s instead of skipping; avoids treating nested fields as scalar. Credit: ChatGPT. (GPT-5.2-Codex (summarized)) -->
		# --- always handle known nested tags first — even if empty
		if tag == "NoWarAttitudeProbs":
			parse_no_war_attitude_probs_inline(child, leader_data, leader_type)
		elif tag == "Flavors":
			parse_flavors_inline(child, leader_data, leader_type)
		elif tag == "ContactRands":
			leader_data["ContactRands"] = parse_contact_rands_inline(child)
		elif tag == "ContactDelays":
			leader_data["ContactDelays"] = parse_contact_delays_inline(child)
		elif tag == "MemoryAttitudePercents":
			leader_data["MemoryAttitudePercents"] = parse_memory_attitude_percents_inline(child)
		elif tag == "MemoryDecays":
			leader_data["MemoryDecays"] = parse_memory_decays_inline(child)

		# <!-- custom: after nested fields, handle scalar fields. (GPT-5.2-Codex (summarized)) -->
		elif len(child) == 0:
			if tag in GENERIC_RENAMED_FIELDS:
				parse_generic_renamed_fields(tag, text, leader, leader_data)
			elif tag in REFUSE_ATTITUDE_FIELDS:
				parse_refuse_attitude_thresholds(tag, text, leader, leader_data)
			elif expected is int:
				try:
					leader_data[tag] = int(text)
				except ValueError:
					errors.append(f"[TYPE ERROR] Leader {leader_type}: Expected int for <{tag}>, got '{text}'")
					leader_data[tag] = text
			elif expected is str:
				if text.isdigit():
					errors.append(f"[TYPE WARNING] Leader {leader_type}: Expected string for <{tag}>, got numeric '{text}'")
				leader_data[tag] = text

		# <!-- custom: other nested fields (e.g., <Traits>, <UnitAIWeightModifiers>) are parsed as JSON-like objects; not used in the AI panel. (GPT-5.2-Codex (summarized)) -->
		# These are allowed and will be treated as list-of-dicts if present
		else:
			sub_entries = [
				{sub.tag.split("}", 1)[1]: sub.text.strip() for sub in subentry if sub.text} for subentry in child
			]
			leader_data[tag] = sub_entries

	for required_tag in NESTED_FIELDS_TO_SPECIFICALLY_PARSE:
		if required_tag not in seen_tags:
			raise ValueError(f"[FATAL] Missing required nested tag <{required_tag}> in leader {leader_type}. Expected at least <{required_tag}/>.")

# <!-- custom: before parsing any leader is done, make sure our normalize_to_100 shifting works as expected -->
test_expected_shifting_pre_normalize_to_100()

# <!-- custom: leader_defaults_data block (highlighted by ChatGPT). (GPT-5.2-Codex (summarized)) -->
# 1. Parse LEADER_DEFAULTS (this fills leader_defaults_data)
for leader in root.findall(".//civ4:LeaderHeadInfo", ns):
	type_tag = leader.find("civ4:Type", ns)
	if type_tag is None or type_tag.text != "LEADER_DEFAULTS":
		continue
	
	leader_type = type_tag.text
	seen_tags_leader_defaults = set()

	parse_leader(leader, leader_type, leader_defaults_data, seen_tags_leader_defaults)

if "LEADER_DEFAULTS" in leader_defaults_data:
	raise ValueError("[INFO] Nested defaults ['LEADER_DEFAULTS']")

# 2. Inject missing memory attitude percent (AFTER parsing)
if "MemoryAttitudePercents" not in leader_defaults_data:
	leader_defaults_data["MemoryAttitudePercents"] = []

existing_attitudes = {
	entry.get("MemoryType")
	for entry in leader_defaults_data["MemoryAttitudePercents"]
	if isinstance(entry, dict)
}

for mem_type in MEMORY_TYPES_NOT_IN_LEADER_DEFAULTS:
	if mem_type not in existing_attitudes:
		print(f"[INFO] Missing memory attitude percent's memory type {mem_type} in LEADER_DEFAULTS, injecting attitude=0 for {mem_type} as seems to be the case already ingame in leader info's gc in debug output.")
		leader_defaults_data["MemoryAttitudePercents"].append({
			"MemoryType": mem_type,
			"iMemoryAttitudePercent": 0
		})

# <!-- custom: handle missing memoryDecays by injecting 0 (matches LEADER_DEFAULTS behavior); suggestion from ChatGPT. (GPT-5.2-Codex (summarized)) -->
if "MemoryDecays" not in leader_defaults_data:
	leader_defaults_data["MemoryDecays"] = []

existing_decays = {
	entry.get("MemoryType")
	for entry in leader_defaults_data["MemoryDecays"]
	if isinstance(entry, dict)
}

for mem_type in MEMORY_TYPES_NOT_IN_LEADER_DEFAULTS:
	if mem_type not in existing_decays:
		print(f"[INFO] Missing memory decay memory type {mem_type} in LEADER_DEFAULTS, injecting decay=0 for {mem_type} as seems to be the case already ingame in leader info's gc in debug output at least for the few missing memory attitude percent fields in LEADER_DEFAULTS 's XML that display as existing and 0 in sevopedia leader's gc ingame in debug output, so handle any potential memory decay missing in LEADER_DEFAULTS similarly hopefully accurate enough too i mean at least if not simply accurate but anyways etc.")
		leader_defaults_data["MemoryDecays"].append({
			"MemoryType": mem_type,
			"iMemoryDecayRand": 0
		})

# <!-- custom: leader_data block (highlighted by ChatGPT). (GPT-5.2-Codex (summarized)) -->
for leader in root.findall(".//civ4:LeaderHeadInfo", ns):
	type_tag = leader.find("civ4:Type", ns)
	if type_tag is None or not type_tag.text:
		continue

	leader_type = type_tag.text
	leader_data = {}
	seen_tags_leader = set()

	parse_leader(leader, leader_type, leader_data, seen_tags_leader)
	inject_defaults(leader_defaults_data, leader_data)

	# Save leader
	leaders_data[leader_type] = leader_data

# === After parsing all leaders ===
# --- Create a list of valid leaders (exclude dummy leaders for aggregated attributes) ---
VALID_LEADERS_FOR_AGGREGATED_ATTRIBUTES = [
	k for k in leaders_data
	if k not in EXCLUDED_LEADER_TYPES_FROM_CALCULATIONS
]

if IS_INSPECT_DEBUG_LEADER:
	print("1 - Before any force_complete functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
print("DEBUG DEFAULT MemoryDecays:", leader_defaults_data.get("MemoryDecays"))
print("DEBUG Catherine MemoryDecays:", leaders_data["LEADER_CATHERINE"]["MemoryDecays"])
# After parsing all leaders and injecting defaults
# --- Ensure nested defaults are complete only now ---
print("DEFAULTS FINAL at step 1:", leader_defaults_data)
ensure_complete_no_war_attitude_probs(leaders_data, leader_defaults_data)
ensure_complete_flavors(leaders_data)
force_complete_contact_rands(leaders_data, leader_defaults_data)
force_complete_contact_delays(leaders_data, leader_defaults_data)
force_complete_memory_decays(leaders_data, leader_defaults_data)
force_complete_memory_attitude_percents(leaders_data, leader_defaults_data)

if IS_INSPECT_DEBUG_LEADER:
	print("2 - Before any flatten_all functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
# --- Now flatten all contacts nicely <!-- custom: then prune list too anwyays etc --> ---
flatten_all_contacts(leaders_data)
# --- Add Positive <!-- custom: and negative --> Memory Affection <!-- custom: and resentment aggregates --> ---
for is_positive in (True, False):
	for is_affection in (True, False):
		flatten_all_memories(leaders_data, is_positive, is_affection)

# === Final Cleanup ===

if IS_INSPECT_DEBUG_LEADER:
	print("3 - Before any prune_nested functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
prune_nested_no_war_attitude_probs_if_flattened(leaders_data)
prune_nested_flavors_if_flattened(leaders_data)
prune_nested_contact_lists_if_flattened(leaders_data)
prune_nested_memory_lists_if_flattened(leaders_data)

# <!-- custom: run cleanup only after all parsing so intermediate data isn't needed elsewhere. Credit: ChatGPT. (GPT-5.2-Codex (summarized)) -->
# --- Cleanup remaining unused legacy fields if not already done ---
if IS_INSPECT_DEBUG_LEADER:
	print("4 - Before any remove_intermediate functions: Leader %s's leaders_data: %s" % (LEADER_TO_INSPECT_IN_DEBUG_OUTPUT, str(leaders_data[LEADER_TO_INSPECT_IN_DEBUG_OUTPUT])))
remove_intermediate_contact_fields(leaders_data)
remove_intermediate_memory_fields(leaders_data)

if not ARGV_NO_TESTING:
	def check_errors_and_tests():
		if errors:
			print("[VALIDATION ERRORS FOUND]")
			for e in errors:
				print(e)
			raise SystemExit("[EXIT] Leader data validation failed.")

		if not leaders_data:
			raise ValueError("[FATAL ERROR] Parsed 0 leaders. Check XML structure or namespace.")

		# --- Test parsed output against expected sample ---

		expected_sample = get_expected_output_PARSED_XML_LEADERS_DATA_SAMPLE()

		parsed_sample = {k: v for k, v in leaders_data.items() if k in EXPECTED_OUTPUT_LEADERS_TO_TEST}

		def compare_leaders(expected, actual):
			grouped_mismatches = {}  # leader -> list of mismatches

			for leader, expected_data in expected.items():
				actual_data = actual.get(leader)
				if actual_data is None:
					grouped_mismatches.setdefault(leader, []).append(f"[{leader}] Leader is missing in parsed data.")
					continue

				# Check for field mismatches
				for key, expected_value in expected_data.items():
					actual_value = actual_data.get(key, "<MISSING>")
					if actual_value != expected_value:
						grouped_mismatches.setdefault(leader, []).append(f"Field '{key}' mismatch: expected '{expected_value}', got '{actual_value}'")

				# Check for unexpected extra fields
				for key in actual_data.keys():
					if key not in expected_data:
						grouped_mismatches.setdefault(leader, []).append(f"Unexpected extra field '{key}' present in parsed data (value: '{actual_data[key]}')")

			return grouped_mismatches

		grouped_mismatches = compare_leaders(expected_sample, parsed_sample)

		if grouped_mismatches:
			print("[TEST FAILED] Parsed sample does not match expected!")

			for leader, problems in grouped_mismatches.items():
				print(f"\n--- Mismatches for {leader} ---")
				for issue in problems:
					print(f"- {issue}")

			raise SystemExit("[EXIT] Leader sample test failed. File not written.")
		else:
			print("[TEST PASSED] Parsed sample matches expected sample!")

	# <!-- custom: tip: use --notesting to generate output faster, then update expected output; be careful, it's easy to miss mismatches?verify thoroughly. (GPT-5.2-Codex (summarized)) -->
	check_errors_and_tests()

else:
	print("[WARNING] Skipping leaders_data testing due to --notesting flag.")

# --- Output to file ---
def output_to_file():
	output_path = f"leaders_data_{timestamp}.py"
	with open(output_path, "w", encoding="utf-8") as f:
		f.write(f"{copyright_header}\n\n")
		f.write(text_art.format(timestamp=timestamp))
		f.write("\n\nPARSED_XML_LEADERS_DATA = ")
		f.write(json.dumps(leaders_data, indent=4, ensure_ascii=False))
	print(f"[SUCCESS] Leaders data written to: {output_path}")
	print(f"[LOGGING COMPLETE] Log file saved in: {log_path}")

output_to_file()
